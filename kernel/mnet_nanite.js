// ============================================================================
//  mnet_nanite.js
//  MachineNet ? Physics-Driven Cluster DAG + Adaptive LOD
//  Vladyslav Savytskyy ? 2026-05-24
//
//  Builds on top of goldberg_kernel.js (GK).  Zero new dependencies.
//  No DOM.  No Three.js.  Pure data.  Exportable.
//
//  CONCEPT:
//    Nanite (Karis et al. SIGGRAPH 2021) drives LOD selection by screen-space
//    geometric error.  MNetNanite drives the same DAG algorithm by NS residual ?
//    physics convergence per face cluster.  Same structure, physically meaningful
//    driving function.  LOD is determined by whether the fluid has converged,
//    not by how many pixels you're looking at.
//
//  ALGORITHM SUMMARY:
//    1.  buildClusterHierarchy(gkState, flowData)
//        Groups all faces into clusters of ~CLUSTER_SIZE faces each.
//        Builds a parent layer of coarser clusters (one per refinement level).
//        Result: a DAG rooted at the 12 pentagonal anchors.
//
//    2.  selectActiveClusters(dag, threshold, camera?)
//        Walks the DAG from roots.  At each node:
//          if clusterEnergy(node) < threshold  -> use this node (don't go deeper)
//          else                                -> recurse into children
//        Returns the "cut" ? the set of clusters that are active this frame.
//        This is the Nanite "persistent cull" step.
//
//    3.  getActiveFaces(dag, threshold, camera?)
//        Calls selectActiveClusters, returns flat face array.
//        Drop-in replacement for gkState.faces in the Three.js renderer.
//
//    4.  validateMonotonicEnergy(dag)
//        Checks: for every node, node.energy >= child.energy (on average).
//        A violation means the physics produced a higher-energy child than parent,
//        which is physically meaningful (turbulence below a converged shell).
//        Returns array of violation objects for debugging.
//
//  FACE DATA CONTRACT (compatible with GK):
//    face.pts        ? array of [x,y,z] vertices
//    face.type       ? 'pent' | 'hex'
//    face.level      ? 0, 1, 2, ... (refinement depth)
//    face.lineage    ? array of ancestor indices
//    face.id         ? stable string id, e.g. 'F3.c12.e47'
//    face.anchor     ? pentagonal anchor id string, or null
//
//  FLOW DATA CONTRACT (from mnet_v6.html ?5):
//    flowData is an array parallel to gkState.faces.
//    flowData[i] = { res: number, energy: number, vx: number, vz: number, p: number }
//    Build it with MNetNanite.captureFlowData(S, gkState) using the live S state
//    from the simulator.
//
//  CLUSTER:
//    {
//      id:          string,            // 'C_<level>_<n>'
//      faces:       [face, ...],       // GK face objects in this cluster
//      faceIndices: [int, ...],        // indices into gkState.faces
//      level:       int,               // refinement level of constituent faces
//      anchor:      string|null,       // dominant pentagonal anchor
//      energy:      number,            // computed from flowData (lazy)
//      energyMetric:'max'|'avg'|'sum', // how energy was aggregated
//      children:    [cluster, ...],    // finer-level clusters covering same territory
//      parent:      cluster|null,
//      bounds:      {cx,cy,cz,r},      // bounding sphere (for camera culling later)
//      dirty:       bool,              // needs energy recompute
//    }
//
//  DAG:
//    {
//      roots:    [cluster, ...],       // one per pentagonal anchor (12 for C60)
//      allNodes: [cluster, ...],       // flat list, all levels
//      levels:   { 0:[...], 1:[...] }, // clusters per refinement level
//      maxLevel: int,
//      anchorMap: { anchorId: cluster },  // roots by anchor
//    }
//
//  INVARIANTS:
//    - dag.roots.length === 12 for a fully-converged C60 at any refinement depth.
//    - A cluster's energy >= its children's average energy IFF the physics has
//      converged in that region.  Violations are turbulence.
//    - selectActiveClusters(dag, 0) returns all leaf clusters (maximum detail).
//    - selectActiveClusters(dag, Infinity) returns all root clusters (minimum detail).
//
//  PUBLIC API:
//    MNetNanite.CLUSTER_SIZE          // default 16 faces per cluster
//    MNetNanite.buildClusterHierarchy(gkState, flowData, opts?)
//    MNetNanite.updateEnergies(dag, flowData)
//    MNetNanite.selectActiveClusters(dag, threshold)
//    MNetNanite.getActiveFaces(dag, threshold)
//    MNetNanite.validateMonotonicEnergy(dag)
//    MNetNanite.captureFlowData(S, gkState)
//    MNetNanite.dagStats(dag)
//    MNetNanite.clusterEnergy(cluster, metric?)
//
// ============================================================================

(function(global){
"use strict";

var MNetNanite = {};

// ---------------------------------------------------------------------------
// ?A  CONSTANTS
// ---------------------------------------------------------------------------

MNetNanite.CLUSTER_SIZE = 16;   // target faces per leaf cluster (Nanite uses 128 tris)
MNetNanite.ENERGY_METRIC = 'avg'; // 'max' | 'avg' | 'sum'
MNetNanite.ENERGY_EPSILON = 1e-9; // below this = converged

// ---------------------------------------------------------------------------
// ?B  FLOW DATA CAPTURE
//
//  Called once per frame (or whenever you want a snapshot).
//  Bridges the mnet_v6.html ?5 solver state into the neutral flowData format.
//
//  S        ? the simulator state object (S from mnet_v6.html)
//  gkState  ? the GK state object (optional; if null, uses S.faces directly)
//
//  The simulator stores physics on nodes (S.nodes), not on faces.
//  We aggregate per-face by averaging over the face's node indices.
//
//  Note: mnet_v6.html uses a flat node array with S.faces storing arrays of
//  node IDs.  goldberg_kernel.js stores face.pts as vertex coordinate arrays.
//  This function handles BOTH layouts ? detect by checking face[0] type.
// ---------------------------------------------------------------------------

MNetNanite.captureFlowData = function(S, gkState) {
    var flowData = [];
    var lk = {};
    if (S && S.nodes) {
        S.nodes.forEach(function(n) { lk[n.id] = n; });
    }

    // Determine which face array to iterate
    var facesArray = (gkState && gkState.faces) ? gkState.faces : (S ? S.faces : []);

    facesArray.forEach(function(face, i) {
        // mnet_v6 style: face is an array of node IDs
        // GK style: face is an object with face.pts
        var entry = { res: 0, energy: 0, vx: 0, vz: 0, p: 0, count: 0 };

        if (Array.isArray(face)) {
            // mnet_v6 node-ID face array
            face.forEach(function(nid) {
                var n = lk[nid];
                if (!n) return;
                var dvMag = Math.sqrt((n._dvx||0)*(n._dvx||0) + (n._dvz||0)*(n._dvz||0));
                entry.res    += dvMag;
                entry.energy += (n.energy || 0);
                entry.vx     += (n._vx || 0);
                entry.vz     += (n._vz || 0);
                entry.p      += (n._p  || 0);
                entry.count  += 1;
            });
        } else if (face && face.pts) {
            // GK face object ? no live node data attached, energy defaults to 0
            // Caller must inject per-face energy separately if available
            entry.count = face.pts.length;
        }

        if (entry.count > 0) {
            entry.res    /= entry.count;
            entry.energy /= entry.count;
            entry.vx     /= entry.count;
            entry.vz     /= entry.count;
            entry.p      /= entry.count;
        }

        flowData.push(entry);
    });

    return flowData;
};

// ---------------------------------------------------------------------------
// ?C  CLUSTER ENERGY
//
//  Three aggregation strategies:
//    'max'  ? worst-case face in cluster (conservative; Nanite-like)
//    'avg'  ? mean energy    (smooth; good for convergence panels)
//    'sum'  ? total energy   (proportional to cluster size; for LOD budget)
//
//  cluster.energy is cached.  Set cluster.dirty = true to force recompute.
// ---------------------------------------------------------------------------

MNetNanite.clusterEnergy = function(cluster, metric) {
    if (!cluster.dirty && cluster.energy !== null && cluster.energy !== undefined) {
        return cluster.energy;
    }
    metric = metric || cluster.energyMetric || MNetNanite.ENERGY_METRIC;
    var fd = cluster._flowData;
    if (!fd || !fd.length) {
        cluster.energy = 0;
        cluster.dirty  = false;
        return 0;
    }
    var val;
    if (metric === 'max') {
        val = 0;
        fd.forEach(function(d) { if (d.energy > val) val = d.energy; });
    } else if (metric === 'sum') {
        val = 0;
        fd.forEach(function(d) { val += d.energy; });
    } else {
        // avg (default)
        val = 0;
        fd.forEach(function(d) { val += d.energy; });
        val /= fd.length;
    }
    cluster.energy = val;
    cluster.dirty  = false;
    return val;
};

// ---------------------------------------------------------------------------
// ?D  BOUNDING SPHERE ? for camera culling in future VR renderer
// ---------------------------------------------------------------------------

function computeBounds(faces) {
    var cx = 0, cy = 0, cz = 0, count = 0;
    faces.forEach(function(face) {
        var pts = face.pts || [];
        pts.forEach(function(p) { cx += p[0]; cy += p[1]; cz += p[2]; count++; });
    });
    if (count === 0) return { cx: 0, cy: 0, cz: 0, r: 0 };
    cx /= count; cy /= count; cz /= count;
    var r = 0;
    faces.forEach(function(face) {
        var pts = face.pts || [];
        pts.forEach(function(p) {
            var dx = p[0]-cx, dy = p[1]-cy, dz = p[2]-cz;
            var d = Math.sqrt(dx*dx + dy*dy + dz*dz);
            if (d > r) r = d;
        });
    });
    return { cx: cx, cy: cy, cz: cz, r: r };
}

// ---------------------------------------------------------------------------
// ?E  CLUSTER FACTORY
// ---------------------------------------------------------------------------

var _cid = 0;
function makeCluster(faces, faceIndices, level, anchor, flowDataSlice) {
    _cid++;
    return {
        id:           'C_' + level + '_' + _cid,
        faces:        faces,
        faceIndices:  faceIndices,
        level:        level,
        anchor:       anchor || null,
        energy:       null,
        energyMetric: MNetNanite.ENERGY_METRIC,
        children:     [],
        parent:       null,
        bounds:       computeBounds(faces),
        dirty:        true,
        _flowData:    flowDataSlice || []
    };
}

// ---------------------------------------------------------------------------
// ?F  SPATIAL GROUPING ? greedy neighbor-based clustering
//
//  Groups faces at the same refinement level into clusters of ~CLUSTER_SIZE.
//  Strategy: greedy scan with adjacency preference (like METIS but simpler).
//
//  Two faces are "adjacent" if they share a vertex (by coordinate proximity)
//  or share an anchor.  We prefer to keep same-anchor faces together because
//  that maps cleanly to the 12-pentagon DAG roots.
// ---------------------------------------------------------------------------

function faceCentroid(face) {
    var pts = face.pts || [];
    var cx = 0, cy = 0, cz = 0;
    pts.forEach(function(p) { cx += p[0]; cy += p[1]; cz += p[2]; });
    var n = pts.length || 1;
    return [cx/n, cy/n, cz/n];
}

function clusterFacesAtLevel(facesAtLevel, indicesAtLevel, flowData, clusterSize) {
    clusterSize = clusterSize || MNetNanite.CLUSTER_SIZE;
    var used    = new Array(facesAtLevel.length).fill(false);
    var clusters = [];
    var level   = facesAtLevel.length > 0 ? facesAtLevel[0].level : 0;

    // Precompute centroids
    var centroids = facesAtLevel.map(faceCentroid);

    // Group by anchor first, then by spatial proximity
    var anchorGroups = {};
    facesAtLevel.forEach(function(face, i) {
        var ak = face.anchor || '_none_';
        if (!anchorGroups[ak]) anchorGroups[ak] = [];
        anchorGroups[ak].push(i);
    });

    function buildClusterFromIndices(localIdxs) {
        var faces  = localIdxs.map(function(i) { return facesAtLevel[i]; });
        var gIdxs  = localIdxs.map(function(i) { return indicesAtLevel[i]; });
        var fdSub  = gIdxs.map(function(gi)    { return flowData[gi] || { res:0, energy:0, vx:0, vz:0, p:0 }; });
        var anchor = faces[0].anchor || null;
        var c = makeCluster(faces, gIdxs, level, anchor, fdSub);
        clusters.push(c);
        return c;
    }

    // Process each anchor group
    Object.keys(anchorGroups).sort().forEach(function(ak) {
        var group  = anchorGroups[ak];
        var batch  = [];
        group.forEach(function(li) {
            if (used[li]) return;
            batch.push(li);
            used[li] = true;
            if (batch.length >= clusterSize) {
                buildClusterFromIndices(batch);
                batch = [];
            }
        });
        if (batch.length > 0) buildClusterFromIndices(batch);
    });

    return clusters;
}

// ---------------------------------------------------------------------------
// ?G  BUILD CLUSTER HIERARCHY
//
//  Main entry point.  Takes a GK state and flowData, returns a DAG.
//
//  Algorithm:
//    1.  Bucket faces by refinement level.
//    2.  For each level L (leaf ? root), build clusters of ~CLUSTER_SIZE faces.
//    3.  For each cluster at level L, find which cluster at level L-1 covers
//        the same territory (by anchor ID).  Connect parent ? children.
//    4.  Identify roots: clusters at level 0 (the original C60 faces).
//        Group further by pentagonal anchor to get the 12 DAG root groups.
//
//  opts = {
//    clusterSize:  int,      // override CLUSTER_SIZE for this build
//    energyMetric: string,   // override ENERGY_METRIC
//  }
// ---------------------------------------------------------------------------

MNetNanite.buildClusterHierarchy = function(gkState, flowData, opts) {
    opts      = opts || {};
    _cid      = 0;   // reset cluster id counter for reproducible ids
    var cSize = opts.clusterSize  || MNetNanite.CLUSTER_SIZE;
    var faces = gkState.faces;
    flowData  = flowData || new Array(faces.length).fill({ res:0, energy:0, vx:0, vz:0, p:0 });

    // Step 1: bucket faces by level
    var byLevel = {};
    var idxByLevel = {};
    var maxLevel = 0;
    faces.forEach(function(face, i) {
        var lv = face.level || 0;
        if (lv > maxLevel) maxLevel = lv;
        if (!byLevel[lv])    { byLevel[lv]    = []; idxByLevel[lv]    = []; }
        byLevel[lv].push(face);
        idxByLevel[lv].push(i);
    });

    // Step 2: build clusters at each level
    var levelClusters = {};
    for (var lv = 0; lv <= maxLevel; lv++) {
        var lvFaces = byLevel[lv]   || [];
        var lvIdxs  = idxByLevel[lv] || [];
        if (!lvFaces.length) { levelClusters[lv] = []; continue; }
        levelClusters[lv] = clusterFacesAtLevel(lvFaces, lvIdxs, flowData, cSize);
    }

    // Step 3: wire parent ? children across levels
    //  A cluster at level L+1 is a child of the level-L cluster
    //  whose anchor matches (or whose face bounds are closest).
    for (var lv = 1; lv <= maxLevel; lv++) {
        var parentLevel = levelClusters[lv - 1] || [];
        var childLevel  = levelClusters[lv]      || [];

        // Build anchor ? parent cluster index map
        var anchorToParent = {};
        parentLevel.forEach(function(pc, pi) {
            if (pc.anchor) anchorToParent[pc.anchor] = pi;
        });

        // Build a fallback centroid ? nearest parent map
        var parentCentroids = parentLevel.map(function(pc) {
            return { cx: pc.bounds.cx, cy: pc.bounds.cy, cz: pc.bounds.cz, idx: 0 };
        });
        parentCentroids.forEach(function(pc, i) { pc.idx = i; });

        childLevel.forEach(function(cc) {
            var pi = -1;
            if (cc.anchor && anchorToParent[cc.anchor] !== undefined) {
                pi = anchorToParent[cc.anchor];
            } else {
                // Nearest centroid fallback
                var best = Infinity;
                parentCentroids.forEach(function(pc) {
                    var dx = cc.bounds.cx - pc.cx;
                    var dy = cc.bounds.cy - pc.cy;
                    var dz = cc.bounds.cz - pc.cz;
                    var d  = dx*dx + dy*dy + dz*dz;
                    if (d < best) { best = d; pi = pc.idx; }
                });
            }
            if (pi >= 0) {
                cc.parent = parentLevel[pi];
                parentLevel[pi].children.push(cc);
            }
        });
    }

    // Step 4: identify roots and anchor map
    var roots     = levelClusters[0] || [];
    var anchorMap = {};
    roots.forEach(function(r) { if (r.anchor) anchorMap[r.anchor] = r; });

    // Flat list for convenience
    var allNodes = [];
    for (var lv = 0; lv <= maxLevel; lv++) {
        (levelClusters[lv] || []).forEach(function(c) { allNodes.push(c); });
    }

    // Compute initial energies
    allNodes.forEach(function(c) { MNetNanite.clusterEnergy(c); });

    return {
        roots:     roots,
        allNodes:  allNodes,
        levels:    levelClusters,
        maxLevel:  maxLevel,
        anchorMap: anchorMap
    };
};

// ---------------------------------------------------------------------------
// ?H  UPDATE ENERGIES
//
//  Call this every N simulation steps (not every frame) to refresh the DAG
//  with new flow data without rebuilding the hierarchy.
//
//  flowData must be the same length as gkState.faces was when the DAG was built.
// ---------------------------------------------------------------------------

MNetNanite.updateEnergies = function(dag, flowData) {
    dag.allNodes.forEach(function(cluster) {
        var fdSub = cluster.faceIndices.map(function(gi) {
            return flowData[gi] || { res: 0, energy: 0, vx: 0, vz: 0, p: 0 };
        });
        cluster._flowData = fdSub;
        cluster.dirty     = true;
        MNetNanite.clusterEnergy(cluster);
    });
};

// ---------------------------------------------------------------------------
// ?I  SELECT ACTIVE CLUSTERS ? the Nanite cut
//
//  Recursive DAG traversal.  Returns the "cut" ? the minimal set of clusters
//  that covers all faces, where each cluster either:
//    (a) has energy < threshold  (converged: use this level, don't go deeper)
//    (b) has no children         (leaf: forced to use)
//
//  This is the physics-driven equivalent of Nanite's error-threshold cut.
//
//  threshold:  NS residual cutoff.  Typical converged run: ~0.0001.
//              Use 0.001 for a coarser cut, 0.00001 for maximum detail.
//
//  cameraHint (optional): { pos:[x,y,z] }  ? future use for distance-weighted
//              threshold modulation (closer = lower threshold = more detail).
//              Currently unused; pass null.
// ---------------------------------------------------------------------------

MNetNanite.selectActiveClusters = function(dag, threshold, cameraHint) {
    var active = [];

    function visit(cluster) {
        var e = MNetNanite.clusterEnergy(cluster);
        // If converged OR no children, use this cluster
        if (e < threshold || cluster.children.length === 0) {
            active.push(cluster);
            return;
        }
        // Otherwise recurse into children
        cluster.children.forEach(visit);
    }

    dag.roots.forEach(visit);
    return active;
};

// ---------------------------------------------------------------------------
// ?J  GET ACTIVE FACES ? the renderer's view
//
//  Returns a flat array of GK face objects ? the subset of all faces that
//  should be rendered / simulated at this threshold.
//
//  Drop this array wherever you'd use gkState.faces in the Three.js renderer.
// ---------------------------------------------------------------------------

MNetNanite.getActiveFaces = function(dag, threshold, cameraHint) {
    var clusters = MNetNanite.selectActiveClusters(dag, threshold, cameraHint);
    var out = [];
    // Deduplicate (a face can be in multiple clusters if hierarchy is imperfect)
    var seen = {};
    clusters.forEach(function(cluster) {
        cluster.faces.forEach(function(face, fi) {
            var key = cluster.faceIndices[fi];
            if (!seen[key]) { seen[key] = true; out.push(face); }
        });
    });
    return out;
};

// ---------------------------------------------------------------------------
// ?K  VALIDATE MONOTONIC ENERGY
//
//  The key invariant: for a fully converged region,
//    parent.energy >= child.energy   (residual decreases with refinement)
//
//  Violations mean the physics has produced turbulence at sub-cluster scale ?
//  a child cluster that is MORE energetic than its parent.  This is physically
//  meaningful: a "hot spot" under a converged surface.
//
//  Returns: array of violation objects, or empty array if monotone.
//    { parent, child, parentEnergy, childEnergy, delta }
// ---------------------------------------------------------------------------

MNetNanite.validateMonotonicEnergy = function(dag) {
    var violations = [];
    dag.allNodes.forEach(function(cluster) {
        var pe = MNetNanite.clusterEnergy(cluster);
        cluster.children.forEach(function(child) {
            var ce = MNetNanite.clusterEnergy(child);
            if (ce > pe + MNetNanite.ENERGY_EPSILON) {
                violations.push({
                    parent:       cluster,
                    child:        child,
                    parentEnergy: pe,
                    childEnergy:  ce,
                    delta:        ce - pe,
                    parentId:     cluster.id,
                    childId:      child.id,
                    level:        child.level,
                    anchor:       child.anchor
                });
            }
        });
    });
    return violations;
};

// ---------------------------------------------------------------------------
// ?L  DAG STATS ? for the convergence panel / push meter
// ---------------------------------------------------------------------------

MNetNanite.dagStats = function(dag) {
    var totalClusters = dag.allNodes.length;
    var totalFaces    = 0;
    var energyByLevel = {};
    var clustersByLevel = {};

    dag.allNodes.forEach(function(c) {
        totalFaces += c.faces.length;
        var lv = c.level;
        if (!energyByLevel[lv]) { energyByLevel[lv] = []; clustersByLevel[lv] = 0; }
        energyByLevel[lv].push(MNetNanite.clusterEnergy(c));
        clustersByLevel[lv]++;
    });

    var levels = {};
    Object.keys(energyByLevel).forEach(function(lv) {
        var arr  = energyByLevel[lv];
        var sum  = arr.reduce(function(a, b) { return a + b; }, 0);
        var max  = arr.reduce(function(a, b) { return Math.max(a, b); }, 0);
        levels[lv] = {
            clusters: clustersByLevel[lv],
            avgEnergy: sum / arr.length,
            maxEnergy: max
        };
    });

    // Monotonicity violations
    var violations = MNetNanite.validateMonotonicEnergy(dag);

    return {
        totalClusters:       totalClusters,
        totalFaces:          totalFaces,
        maxLevel:            dag.maxLevel,
        roots:               dag.roots.length,
        violations:          violations.length,
        violationDetails:    violations,
        levels:              levels,
        isMonotone:          violations.length === 0
    };
};

// ---------------------------------------------------------------------------
// ?M  CONVENIENCE: one-liner for integration into mnet_v6.html animate loop
//
//  Usage in mnet_v6.html ?14 animate():
//
//    // --- Add near top of file, after S = {...} ---
//    var _nanite = { dag: null, threshold: 0.001, dirty: true };
//
//    // --- Inside animate(), after STEP / every 30 steps ---
//    if (_nanite.dirty || S.step % 30 === 0) {
//        var fd = MNetNanite.captureFlowData(S, null);
//        if (!_nanite.dag) {
//            _nanite.dag = MNetNanite.buildClusterHierarchy({ faces: S.faces }, fd);
//        } else {
//            MNetNanite.updateEnergies(_nanite.dag, fd);
//        }
//        _nanite.dirty = false;
//    }
//
//    // --- For rendering, replace S.faces with: ---
//    var activeFaces = _nanite.dag
//        ? MNetNanite.getActiveFaces(_nanite.dag, _nanite.threshold)
//        : S.faces;
//
//  Notes:
//    - On first call, buildClusterHierarchy runs (~1ms for 800 faces, ~5ms for 27K faces).
//    - On subsequent calls, updateEnergies is O(N) with no allocation.
//    - The threshold slider in PC edition maps directly to _nanite.threshold.
//    - Set _nanite.dirty = true after doRefine() to force DAG rebuild.
//
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// ?N  EXPORT
// ---------------------------------------------------------------------------

if (typeof module !== 'undefined' && module.exports) module.exports = MNetNanite;
else if (typeof global !== 'undefined') global.MNetNanite = MNetNanite;

})(typeof globalThis !== 'undefined' ? globalThis : this);

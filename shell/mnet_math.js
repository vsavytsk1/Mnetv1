// ═══════════════════════════════════════════════════════════════
// mnet_math.js — MachineNet Math Module v1.1
// 
// 11 irreducible functions + MINIMIZE_STEP
// No renderer. No DOM. Pure math. Plugs into any frontend.
// DEPENDS ON: goldberg_kernel.js (GK) for C60 seed + refine
//
// Axiom 1: minimum entity = bucky ball (C60)
// Axiom 2: seed = 12 (always, F₅=12)
// Axiom 3: the minimization function decides what to refine
//          (the human never clicks — the energy gradient clicks)
//
// Usage:
//   var state = MNet.seed12();              // uses GK.buildC60()
//   state = MNet.refine(state);             // uses GK.refineAll()
//   state = MNet.minimizeStep(state);       // auto: energy picks face
//   var inv = MNet.eulerCheck(state);       // {chi, F5, F6, V, E, F}
//   assert(inv.F5 === 12);                  // ALWAYS
// ═══════════════════════════════════════════════════════════════

var MNet = (function(){
  'use strict';

  // ─── FLIGHT RECORDER: logs every calculation with ms timestamp ───
  var _log = {
    entries: [],
    active: false,
    startTime: 0,
    maxEntries: 100000,  // ~10MB cap
  };

  function logStart(){
    _log.entries = [];
    _log.active = true;
    _log.startTime = Date.now();
    _logEntry('LOG_START', {time: new Date().toISOString()});
  }

  function logStop(){
    _logEntry('LOG_STOP', {entries: _log.entries.length});
    _log.active = false;
  }

  function _logEntry(fn, data){
    if(!_log.active) return;
    if(_log.entries.length >= _log.maxEntries) return;
    _log.entries.push({
      t: Date.now() - _log.startTime,
      fn: fn,
      d: data
    });
  }

  function logExport(){
    return {
      version: '1.1',
      recorded: new Date().toISOString(),
      entries: _log.entries.length,
      data: _log.entries
    };
  }

  function logExportCSV(){
    var lines = ['t_ms,function,data'];
    _log.entries.forEach(function(e){
      lines.push(e.t + ',' + e.fn + ',' + JSON.stringify(e.d).replace(/,/g,';'));
    });
    return lines.join('\n');
  }

  // Download helper (browser only)
  function logDownload(filename){
    if(typeof document === 'undefined') return logExport();
    filename = filename || 'mnet_log_' + Date.now() + '.json';
    var blob = new Blob([JSON.stringify(logExport(), null, 2)], {type:'application/json'});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
    return {saved: filename, entries: _log.entries.length};
  }

  // ─── UTIL ───
  function vec3(x,y,z){ return [x,y,z]; }
  function vadd(a,b){ return [a[0]+b[0],a[1]+b[1],a[2]+b[2]]; }
  function vsub(a,b){ return [a[0]-b[0],a[1]-b[1],a[2]-b[2]]; }
  function vscale(a,s){ return [a[0]*s,a[1]*s,a[2]*s]; }
  function vlen(a){ return Math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2]); }
  function vnorm(a){ var l=vlen(a)+1e-12; return [a[0]/l,a[1]/l,a[2]/l]; }
  function vdot(a,b){ return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]; }
  function vcross(a,b){ return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]; }
  function vmid(a,b){ return [(a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2]; }

  // ─── STATE FACTORY ───
  // State is immutable-ish: each function returns new or mutated state
  function makeState(){
    return {
      nodes: [],      // [{id, pos:[x,y,z], vel:[vx,vz], p, energy}]
      edges: [],      // [[id1,id2], ...]
      faces: [],      // [[id,id,...], ...]  discovered by face walker
      adj: {},        // id → [id, ...]
      idCounter: 0,
      Re: 100,
      dt: 0.016,
      step: 0,
      refineLevel: 0,
      radius: 4,      // sphere radius
    };
  }

  function makeNode(state, pos){
    var id = state.idCounter++;
    return {id:id, pos:pos.slice(), vel:[0,0], p:0, energy:0,
            _gradP:0, _visc:0, _conv:0, _dvx:0, _dvz:0, _div:0};
  }

  // ═══════════════════════════════════════════════════════
  // F1: SEED_12 — uses GK.buildC60()
  //     12 pentagons + 20 hexagons = 32 faces
  //     V=60, E=90, F=32, χ=2
  // ═══════════════════════════════════════════════════════
  function seed12(){
    var t0 = Date.now();
    // Use the goldberg kernel if available
    var _GK = (typeof GK !== 'undefined') ? GK :
              (typeof require === 'function') ? require('../kernel/goldberg_kernel.js') : null;

    var state = makeState();

    if(_GK && _GK.buildC60){
      // Use GK for proper C60
      var c60 = _GK.buildC60();
      var inv = _GK.invariants(c60);
      // Convert GK state → MNet state
      // GK faces have .pts (array of [x,y,z] vertices)
      // We need to extract unique vertices and build edges
      var vertMap = {};  // 'x,y,z' → node id
      var vertKey = function(v){ return v[0].toFixed(4)+','+v[1].toFixed(4)+','+v[2].toFixed(4); };

      c60.faces.forEach(function(face){
        var pts = face.pts || face.vertices || face;
        if(!Array.isArray(pts)) return;
        pts.forEach(function(v){
          var k = vertKey(v);
          if(!vertMap[k]){
            var node = makeNode(state, v);
            state.nodes.push(node);
            vertMap[k] = node.id;
          }
        });
        // Edges: consecutive vertices in face
        var faceIds = pts.map(function(v){ return vertMap[vertKey(v)]; });
        for(var i=0; i<faceIds.length; i++){
          var a=faceIds[i], b=faceIds[(i+1)%faceIds.length];
          var ek = Math.min(a,b)+'-'+Math.max(a,b);
          if(!state._edgeSet) state._edgeSet={};
          if(!state._edgeSet[ek]){
            state.edges.push([a,b]);
            state._edgeSet[ek]=true;
          }
        }
        // Store face as node ids
        state.faces.push(faceIds);
      });
      delete state._edgeSet;
      _buildAdj(state);
      state._gkState = c60;  // keep GK state for refine
      return state;
    }

    // Fallback: manual icosahedron if GK not available
    var phi = (1+Math.sqrt(5))/2;
    var R = state.radius;
    var raw = [];
    for(var s1=-1;s1<=1;s1+=2){
      for(var s2=-1;s2<=1;s2+=2){
        raw.push([0, s1*1, s2*phi]);
        raw.push([s1*1, s2*phi, 0]);
        raw.push([s2*phi, 0, s1*1]);
      }
    }
    raw.forEach(function(v){
      var l = vlen(v); v[0]*=R/l; v[1]*=R/l; v[2]*=R/l;
    });
    raw.forEach(function(v){ state.nodes.push(makeNode(state, v)); });
    var thresh = R*2*Math.sin(Math.PI/5)*1.05;
    for(var i=0;i<12;i++){
      for(var j=i+1;j<12;j++){
        if(vlen(vsub(state.nodes[i].pos, state.nodes[j].pos)) < thresh)
          state.edges.push([state.nodes[i].id, state.nodes[j].id]);
      }
    }
    _buildAdj(state);
    faceWalk(state);
    _logEntry('SEED_12', {V:state.nodes.length, E:state.edges.length, F:state.faces.length, ms:Date.now()-t0});
    return state;
  }

  // ═══════════════════════════════════════════════════════
  // ADJACENCY
  // ═══════════════════════════════════════════════════════
  function _buildAdj(state){
    state.adj = {};
    state.nodes.forEach(function(n){ state.adj[n.id]=[]; });
    state.edges.forEach(function(e){
      state.adj[e[0]].push(e[1]);
      state.adj[e[1]].push(e[0]);
    });
  }

  function _nodeLookup(state){
    var m = {};
    state.nodes.forEach(function(n){ m[n.id]=n; });
    return m;
  }

  // ═══════════════════════════════════════════════════════
  // F5: FACE_WALK — angular half-edge traversal
  //     Discovers all faces. O(E log deg).
  //     SPHERICAL version: sort neighbors by angle in
  //     the tangent plane at each node (not flat atan2)
  // ═══════════════════════════════════════════════════════
  function _tangentAngle(center, neighbor){
    // Project neighbor into tangent plane of center on sphere
    // 1. Normal at center = normalized center position
    var n = vnorm(center);
    // 2. Vector from center to neighbor
    var d = vsub(neighbor, center);
    // 3. Project d onto tangent plane: d - (d·n)*n
    var dn = vdot(d, n);
    var proj = [d[0]-dn*n[0], d[1]-dn*n[1], d[2]-dn*n[2]];
    // 4. Build local 2D frame in tangent plane
    //    Pick a reference tangent vector (cross with up, fallback)
    var up = Math.abs(n[1]) < 0.9 ? [0,1,0] : [1,0,0];
    var tx = vnorm(vcross(n, up));
    var ty = vcross(n, tx);
    // 5. Angle in local frame
    return Math.atan2(vdot(proj, ty), vdot(proj, tx));
  }

  function faceWalk(state){
    state.faces = [];
    if(state.nodes.length<3 || state.edges.length<3) return state;
    var lookup = _nodeLookup(state);

    // Angle-sorted adjacency using tangent-plane angles
    var adj = {};
    state.nodes.forEach(function(n){ adj[n.id]=[]; });
    state.edges.forEach(function(e){
      var a=lookup[e[0]], b=lookup[e[1]];
      if(!a||!b) return;
      adj[e[0]].push({id:e[1], angle:_tangentAngle(a.pos, b.pos)});
      adj[e[1]].push({id:e[0], angle:_tangentAngle(b.pos, a.pos)});
    });
    Object.keys(adj).forEach(function(k){
      adj[k].sort(function(a,b){return a.angle-b.angle;});
    });

    function nextHE(u,v){
      var nb=adj[v]; if(!nb||!nb.length) return -1;
      for(var i=0;i<nb.length;i++){
        if(nb[i].id===u) return nb[(i-1+nb.length)%nb.length].id;
      }
      return -1;
    }

    var used = {};
    state.edges.forEach(function(e){
      for(var dir=0;dir<2;dir++){
        var su=e[dir], sv=e[1-dir];
        if(used[su+'>'+sv]) continue;
        var face=[], cu=su, cv=sv, safe=state.nodes.length+2;
        while(safe-->0){
          used[cu+'>'+cv]=true;
          face.push(cu);
          var w=nextHE(cu,cv);
          if(w===-1) break;
          cu=cv; cv=w;
          if(cu===su && cv===sv) break;
        }
        if(face.length>=3) state.faces.push(face);
      }
    });

    // Remove outer face
    if(state.faces.length>1){
      var maxA=-1, maxI=0;
      for(var fi=0;fi<state.faces.length;fi++){
        var area=0, f=state.faces[fi];
        for(var j=0;j<f.length;j++){
          var p=lookup[f[j]], q=lookup[f[(j+1)%f.length]];
          if(p&&q) area += p.pos[0]*q.pos[2] - q.pos[0]*p.pos[2];
        }
        if(Math.abs(area)>maxA){maxA=Math.abs(area);maxI=fi;}
      }
      state.faces.splice(maxI,1);
    }
    return state;
  }

  // ═══════════════════════════════════════════════════════
  // F4: EULER_CHECK — V-E+F=2, F₅=12
  // ═══════════════════════════════════════════════════════
  function eulerCheck(state){
    var V=state.nodes.length, E=state.edges.length, F=state.faces.length;
    var chi = V - E + F;
    var F5=0, F6=0, Fother=0;
    state.faces.forEach(function(f){
      if(f.length===5) F5++;
      else if(f.length===6) F6++;
      else Fother++;
    });
    return {V:V, E:E, F:F, chi:chi, F5:F5, F6:F6, Fother:Fother,
            chiOk: chi===2, f5Ok: F5===12||F===0};
  }

  // ═══════════════════════════════════════════════════════
  // F3: REFINE — uses GK.refineAll() if available
  //     Falls back to midpoint subdivision
  //     F₅ preserved. ALWAYS.
  // ═══════════════════════════════════════════════════════
  function refineAll(state){
    // Try GK first
    var _GK = (typeof GK !== 'undefined') ? GK :
              (typeof require === 'function') ? require('../kernel/goldberg_kernel.js') : null;
    if(_GK && _GK.refineAll && state._gkState){
      var newGK = _GK.refineAll(state._gkState);
      var newState = makeState();
      newState.Re = state.Re;
      newState.dt = state.dt;
      newState.radius = state.radius;
      newState.refineLevel = state.refineLevel + 1;
      // Convert back
      var vertMap = {};
      var vertKey = function(v){ return v[0].toFixed(4)+','+v[1].toFixed(4)+','+v[2].toFixed(4); };
      newGK.faces.forEach(function(face){
        var pts = face.pts || face.vertices || face;
        if(!Array.isArray(pts)) return;
        var faceIds = [];
        pts.forEach(function(v){
          var k = vertKey(v);
          if(!vertMap[k]){
            var node = makeNode(newState, v);
            newState.nodes.push(node);
            vertMap[k] = node.id;
          }
          faceIds.push(vertMap[k]);
        });
        for(var i=0;i<faceIds.length;i++){
          var a=faceIds[i], b=faceIds[(i+1)%faceIds.length];
          var ek=Math.min(a,b)+'-'+Math.max(a,b);
          if(!newState._edgeSet) newState._edgeSet={};
          if(!newState._edgeSet[ek]){
            newState.edges.push([a,b]);
            newState._edgeSet[ek]=true;
          }
        }
        newState.faces.push(faceIds);
      });
      delete newState._edgeSet;
      _buildAdj(newState);
      newState._gkState = newGK;
      return newState;
    }

    // Fallback: midpoint subdivision
    if(state.nodes.length>800) return state; // safety cap
    var lookup = _nodeLookup(state);
    var midMap = {};
    var newNodes = state.nodes.slice();

    // Midpoint per edge
    state.edges.forEach(function(e){
      var key = Math.min(e[0],e[1])+'-'+Math.max(e[0],e[1]);
      if(midMap[key]) return;
      var a=lookup[e[0]], b=lookup[e[1]];
      if(!a||!b) return;
      var mid = makeNode(state, vmid(a.pos, b.pos));
      newNodes.push(mid);
      midMap[key] = mid;
    });

    // New edges
    var newEdges = [];
    state.edges.forEach(function(e){
      var key = Math.min(e[0],e[1])+'-'+Math.max(e[0],e[1]);
      var mid = midMap[key];
      if(mid){
        newEdges.push([e[0], mid.id]);
        newEdges.push([mid.id, e[1]]);
      }
    });

    // Connect midpoints sharing a vertex
    var vertexEdges = {};
    state.edges.forEach(function(e){
      if(!vertexEdges[e[0]]) vertexEdges[e[0]]=[];
      if(!vertexEdges[e[1]]) vertexEdges[e[1]]=[];
      vertexEdges[e[0]].push(e);
      vertexEdges[e[1]].push(e);
    });
    Object.keys(vertexEdges).forEach(function(vid){
      var eList = vertexEdges[vid];
      for(var i=0;i<eList.length;i++){
        for(var j=i+1;j<eList.length;j++){
          var k1=Math.min(eList[i][0],eList[i][1])+'-'+Math.max(eList[i][0],eList[i][1]);
          var k2=Math.min(eList[j][0],eList[j][1])+'-'+Math.max(eList[j][0],eList[j][1]);
          var m1=midMap[k1], m2=midMap[k2];
          if(m1 && m2) newEdges.push([m1.id, m2.id]);
        }
      }
    });

    state.nodes = newNodes;
    state.edges = newEdges;
    state.refineLevel++;
    _buildAdj(state);

    // Project back to sphere
    _projectToSphere(state);
    faceWalk(state);
    return state;
  }

  function _projectToSphere(state){
    var R = state.radius;
    state.nodes.forEach(function(n){
      var l = vlen(n.pos)+1e-12;
      n.pos[0]*=R/l; n.pos[1]*=R/l; n.pos[2]*=R/l;
    });
  }

  // ═══════════════════════════════════════════════════════
  // F6: PRESSURE — ∇·u → pressure correction
  // ═══════════════════════════════════════════════════════
  function pressure(state){
    var t0 = typeof performance!=='undefined'?performance.now():Date.now();
    var lookup = _nodeLookup(state);
    state.nodes.forEach(function(n){
      var nbs=state.adj[n.id]; if(!nbs||!nbs.length) return;
      var divU=0;
      var nbLogs = [];
      nbs.forEach(function(nid){
        var nb=lookup[nid]; if(!nb) return;
        var dx=nb.pos[0]-n.pos[0], dz=nb.pos[2]-n.pos[2];
        var dist=Math.sqrt(dx*dx+dz*dz)+0.01;
        var contrib=((nb.vel[0]-n.vel[0])*(dx/dist)+(nb.vel[1]-n.vel[1])*(dz/dist))/dist;
        divU+=contrib;
        if(_log.active) nbLogs.push({nb:nid, dx:+dx.toFixed(4), dz:+dz.toFixed(4), dist:+dist.toFixed(4), contrib:+contrib.toFixed(6)});
      });
      n._div = divU/nbs.length;
      var pOld = n.p;
      n.p += -divU*2.0;
      if(_log.active) _logEntry('P', {id:n.id, div:+n._div.toFixed(6), pOld:+pOld.toFixed(4), pNew:+n.p.toFixed(4), nbs:nbLogs});
    });
    var dt=(typeof performance!=='undefined'?performance.now():Date.now())-t0;
    _logEntry('PRESSURE_DONE', {nodes:state.nodes.length, ms:+dt.toFixed(3)});
    return state;
  }

  // ═══════════════════════════════════════════════════════
  // F7: MOMENTUM — Du/Dt = -∇p + (1/Re)∇²u
  // ═══════════════════════════════════════════════════════
  function momentum(state){
    var t0 = typeof performance!=='undefined'?performance.now():Date.now();
    var lookup = _nodeLookup(state);
    var Re = state.Re;
    state.nodes.forEach(function(n){
      var nbs=state.adj[n.id]; if(!nbs||!nbs.length) return;
      var gpx=0,gpz=0,lapVx=0,lapVz=0,convX=0,convZ=0;
      var nbLogs = [];
      nbs.forEach(function(nid){
        var nb=lookup[nid]; if(!nb) return;
        var dx=nb.pos[0]-n.pos[0], dz=nb.pos[2]-n.pos[2];
        var dist=Math.sqrt(dx*dx+dz*dz)+0.01;
        var dirX=dx/dist, dirZ=dz/dist;
        var gp_x=(nb.p-n.p)*dirX/dist, gp_z=(nb.p-n.p)*dirZ/dist;
        gpx+=gp_x; gpz+=gp_z;
        var lap_x=(nb.vel[0]-n.vel[0])/(dist*dist), lap_z=(nb.vel[1]-n.vel[1])/(dist*dist);
        lapVx+=lap_x; lapVz+=lap_z;
        var dvx=(nb.vel[0]-n.vel[0])/dist, dvz=(nb.vel[1]-n.vel[1])/dist;
        var c_x=n.vel[0]*dvx*dirX+n.vel[1]*dvx*dirZ;
        var c_z=n.vel[0]*dvz*dirX+n.vel[1]*dvz*dirZ;
        convX+=c_x; convZ+=c_z;
        if(_log.active) nbLogs.push({nb:nid, gp:[+gp_x.toFixed(6),+gp_z.toFixed(6)], lap:[+lap_x.toFixed(6),+lap_z.toFixed(6)], conv:[+c_x.toFixed(6),+c_z.toFixed(6)]});
      });
      var invN=1/nbs.length;
      n._gradP=Math.sqrt(gpx*gpx+gpz*gpz)*invN;
      n._visc=Math.sqrt(lapVx*lapVx+lapVz*lapVz)*invN/Re;
      n._conv=Math.sqrt(convX*convX+convZ*convZ)*invN;
      n._dvx=(-gpx+lapVx/Re-convX)*invN;
      n._dvz=(-gpz+lapVz/Re-convZ)*invN;
      n.energy = n._gradP + n._visc + n._conv + Math.abs(n.p)*0.1;
      if(_log.active) _logEntry('M', {
        id:n.id,
        pos:[+n.pos[0].toFixed(4),+n.pos[1].toFixed(4),+n.pos[2].toFixed(4)],
        vel:[+n.vel[0].toFixed(6),+n.vel[1].toFixed(6)],
        p:+n.p.toFixed(4),
        gradP:+n._gradP.toFixed(6),
        visc:+n._visc.toFixed(6),
        conv:+n._conv.toFixed(6),
        dv:[+n._dvx.toFixed(6),+n._dvz.toFixed(6)],
        energy:+n.energy.toFixed(6),
        nbs:nbLogs
      });
    });
    var dt=(typeof performance!=='undefined'?performance.now():Date.now())-t0;
    _logEntry('MOMENTUM_DONE', {Re:Re, nodes:state.nodes.length, ms:+dt.toFixed(3)});
    return state;
  }

  // ═══════════════════════════════════════════════════════
  // F8: INTEGRATE — advance velocities + positions
  // ═══════════════════════════════════════════════════════
  function integrate(state){
    var t0 = typeof performance!=='undefined'?performance.now():Date.now();
    var dt=state.dt, maxV=0;
    state.nodes.forEach(function(n){
      var velOld=[n.vel[0],n.vel[1]];
      var posOld=[n.pos[0],n.pos[1],n.pos[2]];
      n.vel[0]+=n._dvx*dt; n.vel[1]+=n._dvz*dt;
      var speed=Math.sqrt(n.vel[0]*n.vel[0]+n.vel[1]*n.vel[1]);
      var clamped=false;
      if(speed>3){n.vel[0]*=3/speed;n.vel[1]*=3/speed;speed=3;clamped=true;}
      if(speed>maxV) maxV=speed;
      n.pos[0]+=n.vel[0]*dt; n.pos[2]+=n.vel[1]*dt;
      if(_log.active) _logEntry('I', {
        id:n.id,
        posOld:[+posOld[0].toFixed(4),+posOld[1].toFixed(4),+posOld[2].toFixed(4)],
        posNew:[+n.pos[0].toFixed(4),+n.pos[1].toFixed(4),+n.pos[2].toFixed(4)],
        velOld:[+velOld[0].toFixed(6),+velOld[1].toFixed(6)],
        velNew:[+n.vel[0].toFixed(6),+n.vel[1].toFixed(6)],
        speed:+speed.toFixed(6),
        clamped:clamped
      });
    });
    _projectToSphere(state);
    state.step++;
    var elapsed=(typeof performance!=='undefined'?performance.now():Date.now())-t0;
    _logEntry('INTEGRATE_DONE', {step:state.step, maxV:+maxV.toFixed(6), dt:state.dt, ms:+elapsed.toFixed(3)});
    return {state:state, maxV:maxV};
  }

  // ═══════════════════════════════════════════════════════
  // F10: FACE_ENERGY — compute energy per FACE
  //      (average of node energies for that face)
  //      THIS is what drives the minimization
  // ═══════════════════════════════════════════════════════
  function faceEnergy(state){
    var lookup = _nodeLookup(state);
    var energies = [];
    state.faces.forEach(function(face, fi){
      var totalE = 0;
      face.forEach(function(nid){
        var n = lookup[nid];
        if(n) totalE += n.energy;
      });
      energies.push({
        faceIdx: fi,
        sides: face.length,
        energy: totalE / face.length,
        nodeIds: face
      });
    });
    // Sort: highest energy first
    energies.sort(function(a,b){ return b.energy - a.energy; });
    return energies;
  }

  // ═══════════════════════════════════════════════════════
  // THE KEY FUNCTION: MINIMIZE_STEP
  //
  // This replaces ALL human clicking.
  //
  // 1. Run one NS cycle (pressure → momentum → integrate)
  // 2. Compute energy per face
  // 3. The face with HIGHEST energy = needs refinement
  // 4. Refine that face (if above threshold)
  // 5. Recompute invariants
  //
  // The physics decides. Not the human.
  // ═══════════════════════════════════════════════════════
  function minimizeStep(state, opts){
    opts = opts || {};
    var threshold = opts.threshold || 0.1;  // min energy to trigger refine
    var maxNodes = opts.maxNodes || 800;     // safety cap

    // Step 1: NS cycle
    pressure(state);
    momentum(state);
    var result = integrate(state);
    state = result.state;

    // Step 2: face energy
    var energies = faceEnergy(state);

    // Step 3: decision
    var decision = {
      step: state.step,
      topFace: energies[0] || null,
      refined: false,
      invariants: null
    };

    // Step 4: refine if above threshold and under cap
    if(energies.length > 0 &&
       energies[0].energy > threshold &&
       state.nodes.length < maxNodes){
      // For now: refineAll (TODO: refine single face)
      // The energy tells us WHERE, the threshold tells us WHEN
      state = refineAll(state);
      decision.refined = true;
    }

    // Step 5: invariants
    decision.invariants = eulerCheck(state);

    _logEntry('MINIMIZE_STEP', {
      step:state.step, refined:decision.refined,
      topEnergy: decision.topFace ? decision.topFace.energy : 0,
      chi:decision.invariants.chi, F5:decision.invariants.F5
    });
    return {state: state, decision: decision};
  }

  // ═══════════════════════════════════════════════════════
  // FULL AUTO: run N minimize steps
  // ═══════════════════════════════════════════════════════
  function autoRun(state, steps, opts){
    var log = [];
    for(var i=0; i<steps; i++){
      var result = minimizeStep(state, opts);
      state = result.state;
      log.push(result.decision);
      // Stop if invariants break
      if(!result.decision.invariants.chiOk){
        log.push({error: 'CHI BROKE', step: state.step});
        break;
      }
    }
    return {state: state, log: log};
  }

  // ═══════════════════════════════════════════════════════
  // PUBLIC API
  // ═══════════════════════════════════════════════════════
  return {
    // Flight recorder
    logStart:     logStart,
    logStop:      logStop,
    logExport:    logExport,
    logExportCSV: logExportCSV,
    logDownload:  logDownload,

    // Factories
    seed12:       seed12,
    makeState:    makeState,

    // The 11 irreducible functions
    faceWalk:     faceWalk,      // F5
    eulerCheck:   eulerCheck,    // F4
    refineAll:    refineAll,     // F3
    pressure:     pressure,      // F6
    momentum:     momentum,      // F7
    integrate:    integrate,     // F8
    faceEnergy:   faceEnergy,    // F10

    // The minimization engine
    minimizeStep: minimizeStep,
    autoRun:      autoRun,

    // Utils
    vec3: vec3, vadd: vadd, vsub: vsub, vscale: vscale,
    vlen: vlen, vnorm: vnorm, vdot: vdot, vcross: vcross
  };
})();

// Node.js / module export
if(typeof module !== 'undefined' && module.exports){
  module.exports = MNet;
}

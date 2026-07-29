#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENESIS WALLPAPER GENERATOR  v1.5
=================================================================================
Renders the ORIGINAL genesis v8.1 refineFace operator -- midRing and all -- to a
very large JPG. The crescent defect is kept on purpose. It is the picture.

  pip install numpy pillow
  optional CUDA:  pip install cupy-cuda12x     (RTX 3060 Laptop -> cuda12x)
  optional exact renderer: pip install matplotlib

  TWO RENDERERS, one file. RENDERER="additive" is the wallpaper instrument:
  additive lines, scales past a hundred million faces, glows. RENDERER="exact"
  is the browser canvas ported line for line -- orthographic projection,
  genesis' own four culls, painter sort, source-over fills under strokes.
  Same geometry feeds both.

  python genesis_wallpaper.py

Everything you would want to change is in the CONFIG block below.
No maxFaces cap -- that was a Navier guard and has no business here.
=================================================================================
"""
import sys, os, time, math

# ═════════════════════════════════════════════════════════════════════════════
#  CONFIG  -- edit freely
# ═════════════════════════════════════════════════════════════════════════════

# ── the operator (these are genesis v8.1's own defaults) ────────────────────
INNER_SCALE   = 0.10      # inner[i] = lerp(c, pts[i], INNER_SCALE)
MID_SCALE     = 0.10      # midRing[i] = lerp(c, edgeMid, MID_SCALE)
                          #   > INNER_SCALE -> crescent GAP     (the rosette)
                          #   < INNER_SCALE -> crescent OVERLAP (layered)
                          #   = INNER_SCALE -> flat, still open
JITTER        = 0.00      # 0.00 - 0.30
SPHERE_R      = 1.6
SPHERICAL     = True      # False = 'planar' mode, no reprojection

# ── order of operations, top to bottom. "all" = REFINE ALL, "hex" = REFINE 6s,
#    "pent" = REFINE 5s.  Your ask: fractalize all, then fract 6.
OPS           = ["all"]*1 + ["hex"]*8      # 8,234,952 faces
                                           # ["all"]*5 + ["hex"]*3 = 57.6M, CPU only

SEED          = "c60"     # dodec C20 12F | c60 32F | c80 42F | c180 92F | c320 162F
                          # all carry exactly 12 pentagons -- that is the family

# ── MOBIUS ─────────────────────────────────────────────────────────────────
#  genesis' own sphereToMobius, ported exactly:
#     theta=atan2(y,x)  phi=acos(z/r)
#     u = theta+PI      v = (phi/PI - 0.5)*2*W
#     -> ((R + v*cos(u/2))*cos u, (R + v*cos(u/2))*sin u, v*sin(u/2))
#
#  You asked for it FIRST, before any refinement -- so every later centroid,
#  inset and midRing is computed on the twisted surface rather than on a
#  sphere that gets twisted at the end. That is a genuinely different object.
#
#  WHAT GENESIS ACTUALLY DOES, and it is not what I assumed in v1.3:
#  computeMobiusPositions() and applyMobiusLerp() are called ONLY from
#  toggleMobius / setMobiusTwist. Refine never touches them. So the twist
#  lands on the seed and refineFace then runs over it with projectToSphere
#  STILL ON. Each child's new vertices (inner, midRing, em) snap back to
#  radius SPHERE_R, while the parent corners it inherits stay out where the
#  twist put them -- as far as R+W.
#
#  The result is not a strip. It is a sphere with spikes: 97.7% of vertices
#  pinned at 1.600 and 2.3% stretched to 3.04. That bimodal split is the
#  star. Forcing planar to 'preserve the twist' gives a smooth blob and
#  destroys the thing worth looking at. MOBIUS_PROJECT=True is genesis.
MOBIUS_T      = 1.0     # 0 = off, 1 = full strip. lerp, exactly as the slider
MOBIUS_R      = 2.5       # MOB.R (base 2.5)
MOBIUS_W      = 0.8       # MOB.W (base 0.8)
MOBIUS_WHEN   = "first"   # "first" = twist the seed, then refine over it
                          # "last"  = refine on the sphere, twist at the end
MOBIUS_PROJECT = True     # True  = genesis: keep projectToSphere -> SPIKES
                          # False = planar refinement -> smooth strip

# ── renderer ───────────────────────────────────────────────────────────────
RENDERER      = "exact"  # "additive" -> the wallpaper instrument
                            # "exact"    -> the canvas, ported (needs matplotlib)

# ── camera, EXACT mode. these are genesis' own `cam` object. ───────────────
#  project() is ORTHOGRAPHIC out here -- no perspective divide at all:
#     x1 = x*cos(ry) - z*sin(ry);   z1 = x*sin(ry) + z*cos(ry)
#     y1 = y*cos(rx) - z1*sin(rx);  z2 = y*sin(rx) + z1*cos(rx)
#     screen = (W/2 + x1*zoom, H/2 - y1*zoom),  depth = z2
#  A distance and an FOV cannot imitate that; they change the silhouette.
CAM_RX        = 0.30      # cam.rx
CAM_RY        = 0.00      # cam.ry
CAM_ZOOM      = 108.0     # the ZOOM slider
CAM_ATOM      = 0.10      # the ATOM slider (exact mode; additive uses ATOM_SIZE)
SUPERSAMPLE   = 2         # render NxN then box-filter down

# ── camera, ADDITIVE mode ──────────────────────────────────────────────────
ROT_X         = 0.42      # radians, pitch
ROT_Y         = 0.85      # radians, yaw
ROT_Z         = 0.00      # radians, roll
CAM_DIST      = 2.05      # * SPHERE_R.  < 1.0 puts you inside the shell
FOV_DEG       = 62.0
ZOOM          = 1.00

# ── output ─────────────────────────────────────────────────────────────────
WIDTH         = 7680      # 5120x2880 = 5K.  7680x4320 = 8K (needs ~1.5 GB more)
HEIGHT        = 4320
JPG_QUALITY   = 97
OUT           = None      # None = auto:
                          #   gens+in<inner>_mid<mid>_<seed>_<ops>_atm<atom>_<unix>.jpg
OUT_DIR       = "."

# ── look ───────────────────────────────────────────────────────────────────
PALETTE       = "genesis_true"  # "genesis" | "spectrum" | "bone" | "ember"
                            # "genesis" matches the browser shell: deep navy,
                            # cyan lines, hubs burning out to white
PENT_BOOST    = None        # None = take it from the palette
GAIN          = None        # None = take it from the palette
GAMMA         = None
TONE          = None
DRAW_HISTORY  = True        # keep every generation's edges, not just the last

# ATOMS -- genesis draws a dot on every vertex of every face big enough to see:
#     r = cam.atom * (isPent ? 2 : 1.2)     only when screenSize > 5 px
# duplicates are NOT merged, so shared corners stack and the hubs burn out.
ATOM_SIZE     = 3.0      # = cam.atom.  0 disables.
ATOM_MIN_PX   = 3.0      # genesis' ss>5 test. keeps it cheap at depth.

PALETTES = {
 # lifted from the genesis draw path, rgb exact:
 #   hex  stroke rgba(0,180,255, a*0.6)     atom rgba(0,255,213, a*0.6)
 #   pent stroke rgba(255,105,180, a)       atom rgba(255,105,180, a)
 #   bg #050508      alpha = 0.15 + depth01*0.5
 "genesis_true": dict(
    mode="facetype", bg=(5,5,8),
    hex_edge=(0,180,255),   hex_mul=0.6,
    pent_edge=(255,105,180), pent_mul=1.0,
    hex_atom=(0,255,213),   hex_atom_mul=0.6,
    pent_atom=(255,105,180), pent_atom_mul=1.0,
    gain=0.34, tone="asinh", gamma=0.82, pent=1.0),
 "genesis": dict(
    mode="generation",
    colors=[(0.02,0.20,0.36),(0.03,0.31,0.52),(0.04,0.44,0.68),(0.07,0.58,0.84),
            (0.14,0.72,0.94),(0.30,0.86,1.00),(0.60,0.96,1.00)],
    bg=(3,8,14), gain=0.42, tone="asinh", gamma=0.80, pent=1.7),
 "spectrum": dict(
    mode="generation",
    colors=[(0.06,0.34,0.55),(0.05,0.46,0.78),(0.04,0.62,0.95),(0.10,0.80,1.00),
            (0.35,0.94,1.00),(0.70,1.00,0.98),(1.00,0.99,0.80)],
    bg=(2,4,8), gain=0.90, tone="asinh", gamma=0.62, pent=2.6),
 "bone": dict(
    mode="generation",
    colors=[(0.28,0.24,0.16),(0.42,0.36,0.24),(0.58,0.50,0.34),(0.74,0.65,0.45),
            (0.88,0.79,0.58),(0.97,0.90,0.72),(1.00,0.97,0.86)],
    bg=(6,6,15), gain=0.55, tone="asinh", gamma=0.74, pent=2.0),
 "ember": dict(
    mode="generation",
    colors=[(0.30,0.05,0.03),(0.48,0.10,0.04),(0.68,0.20,0.05),(0.86,0.36,0.07),
            (0.97,0.55,0.14),(1.00,0.75,0.34),(1.00,0.93,0.72)],
    bg=(8,3,3), gain=0.60, tone="asinh", gamma=0.72, pent=2.2),
}

# ── compute ────────────────────────────────────────────────────────────────
#  The MESH is always built in system RAM. At level 7+ a single generation is
#  larger than a 6 GB card -- gen 8 of the c60 chain is 164,708,612 faces, and
#  the output array alone is 11.9 GB. Nothing chunkable about that; it has to
#  live somewhere with room. Your 32 GB has room.
#
#  The RASTER runs on the GPU, fed in chunks. That is the part that actually
#  wants a GPU: scattered adds into a 14.7 Mpx buffer, millions of times.
USE_GPU       = True        # GPU for rasterising only
REFINE_CHUNK  = 2_000_000   # parent faces per refine batch; caps transient RAM
CHUNK_SAMPLES = 20_000_000  # raster samples per upload.  6 GB VRAM -> 20M
MEM_BUDGET_GB = "auto"      # "auto" = 82% of detected system RAM, or a number

# ═════════════════════════════════════════════════════════════════════════════
#  end CONFIG
# ═════════════════════════════════════════════════════════════════════════════

xp = None
GPU = False
HOST_RAM_GB = 0.0

def _detect_ram():
    """total system RAM in GB, without needing psutil"""
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**30
    except (ValueError, OSError, AttributeError):
        pass
    try:                                    # windows
        import ctypes
        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS(); m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullTotalPhys / 2**30
    except Exception:
        return 16.0
def _pick_backend():
    global xp, GPU, HOST_RAM_GB, MEM_BUDGET_GB
    HOST_RAM_GB = _detect_ram()
    if MEM_BUDGET_GB == "auto":
        MEM_BUDGET_GB = round(HOST_RAM_GB * 0.82, 1)
    where = ""
    if "COLAB_GPU" in os.environ or os.path.isdir("/content"):
        where = "  [Colab]"
    print(f"  host    : {HOST_RAM_GB:.1f} GB RAM{where}   "
          f"mesh budget {MEM_BUDGET_GB:.1f} GB")
    if USE_GPU:
        try:
            import cupy
            cupy.zeros(1)
            xp, GPU = cupy, True
            dev = cupy.cuda.runtime.getDeviceProperties(0)
            free, total = cupy.cuda.runtime.memGetInfo()
            print(f"  backend : CUDA  {dev['name'].decode()}  "
                  f"{total/2**30:.1f} GB ({free/2**30:.1f} free)")
            return
        except Exception as e:
            print(f"  backend : no CUDA device ({type(e).__name__}) -> NumPy raster")
            if os.path.isdir("/content"):
                print("            on Colab a TPU runtime has no GPU. That is fine --")
                print("            RAM is what limits depth here, and TPU gives the most.")
                print("            Switch to T4 only if you want the raster accelerated;")
                print("            it costs you ~34 GB of the RAM that buys depth.")
    import numpy
    xp, GPU = numpy, False
    print("  backend : NumPy (CPU)")

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
#  progress bar
# ─────────────────────────────────────────────────────────────────────────────
class Bar:
    def __init__(self, total, label, width=34):
        self.total, self.label, self.width = max(1, total), label, width
        self.n, self.t0, self.last = 0, time.time(), 0.0
    def step(self, k=1):
        self.n += k
        now = time.time()
        if now - self.last < 0.08 and self.n < self.total:
            return
        self.last = now
        frac = min(1.0, self.n / self.total)
        el = now - self.t0
        eta = (el / frac - el) if frac > 1e-9 else 0.0
        fill = int(self.width * frac)
        bar = "#" * fill + "-" * (self.width - fill)
        sys.stdout.write(f"\r  {self.label:<22} [{bar}] {100*frac:5.1f}%  "
                         f"{el:6.1f}s  eta {eta:5.1f}s   ")
        sys.stdout.flush()
    def done(self, msg=""):
        el = time.time() - self.t0
        bar = "#" * self.width
        sys.stdout.write(f"\r  {self.label:<22} [{bar}] 100.0%  {el:6.1f}s  {msg}\n")
        sys.stdout.flush()


# ─────────────────────────────────────────────────────────────────────────────
#  seeds
# ─────────────────────────────────────────────────────────────────────────────
PHI = (1.0 + 5.0 ** 0.5) / 2.0

def _norm(a):
    L = np.linalg.norm(a, axis=-1, keepdims=True)
    return a / np.where(L < 1e-12, 1.0, L)

def _icosahedron():
    raw = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            raw += [[0, s1, s2*PHI], [s1, s2*PHI, 0], [s2*PHI, 0, s1]]
    V = _norm(np.array(raw, np.float64))
    D = np.linalg.norm(V[:, None] - V[None, :], axis=-1)
    e = D[D > 1e-9].min()
    F = []
    for i in range(12):
        for j in range(i+1, 12):
            if abs(D[i, j] - e) > 1e-6: continue
            for k in range(j+1, 12):
                if abs(D[i, k]-e) < 1e-6 and abs(D[j, k]-e) < 1e-6:
                    F.append((i, j, k))
    return V, F

def _dual(gv, gt, R):
    """geodesic vertex -> face. degree 5 gives a pentagon, degree 6 a hexagon."""
    dual = _norm(np.array([gv[list(t)].mean(0) for t in gt])) * R
    inc = [[] for _ in range(len(gv))]
    spoke = {}
    for ti, t in enumerate(gt):
        for k in range(3):
            inc[t[k]].append(ti)
            a, b = t[k], t[(k+1) % 3]
            spoke.setdefault((a, b), []).append(ti)
            spoke.setdefault((b, a), []).append(ti)
    out = []
    for v in range(len(gv)):
        ring = inc[v]; cyc = [ring[0]]; seen = {ring[0]}
        for _ in range(len(ring)):
            cur = cyc[-1]; nxt = None
            for o in gt[cur]:
                if o == v: continue
                for cand in spoke.get((v, o), ()):
                    if cand != cur and cand not in seen:
                        nxt = cand; break
                if nxt is not None: break
            if nxt is None: break
            cyc.append(nxt); seen.add(nxt)
        pts = dual[cyc]
        c = pts.mean(0)
        N = np.zeros(3)
        for k in range(len(pts)):
            A, B = pts[k], pts[(k+1) % len(pts)]
            N += [(A[1]-B[1])*(A[2]+B[2]), (A[2]-B[2])*(A[0]+B[0]), (A[0]-B[0])*(A[1]+B[1])]
        if N @ c < 0: pts = pts[::-1]
        out.append(pts)
    return out

def _geodesic(nu):
    bv, bf = _icosahedron()
    idx, verts = {}, []
    def get(tri, i, j):
        w = [(tri[0], nu-i-j), (tri[1], i), (tri[2], j)]
        key = tuple(sorted((a, b) for a, b in w if b > 0))
        if key not in idx:
            p = sum(bv[a]*b for a, b in w)
            idx[key] = len(verts); verts.append(p/np.linalg.norm(p))
        return idx[key]
    tris = []
    for tri in bf:
        for i in range(nu):
            for j in range(nu-i):
                tris.append((get(tri, i, j), get(tri, i+1, j), get(tri, i, j+1)))
                if i+j < nu-1:
                    tris.append((get(tri, i+1, j), get(tri, i+1, j+1), get(tri, i, j+1)))
    return np.array(verts), tris

def _kis(polys, R):
    """fan every face from its centroid -> triangles (for the C60 dual)"""
    verts, tris = [], []
    vidx = {}
    def vid(p):
        k = tuple(np.round(p, 9))
        if k not in vidx:
            vidx[k] = len(verts); verts.append(np.array(p))
        return vidx[k]
    for f in polys:
        ids = [vid(p) for p in f]
        ci = vid(_norm(np.array(f).mean(0)) * R)
        for k in range(len(ids)):
            tris.append((ids[k], ids[(k+1) % len(ids)], ci))
    return np.array(verts), tris

def sphere_to_mobius(pts, R, W, t):
    """genesis sphereToMobius, vectorised, with the slider's lerp.
    pts (...,3) -> (...,3).  t=0 returns pts untouched."""
    if t <= 0.0:
        return pts
    x, y, z = pts[..., 0], pts[..., 1], pts[..., 2]
    r = np.sqrt(x*x + y*y + z*z)
    safe = r > 1e-10
    rr = np.where(safe, r, np.float32(1.0))
    theta = np.arctan2(y, x)
    phi = np.arccos(np.clip(z / rr, -1.0, 1.0))
    u = theta + np.float32(np.pi)
    v = (phi / np.float32(np.pi) - np.float32(0.5)) * np.float32(2.0 * W)
    rad = np.float32(R) + v * np.cos(u * np.float32(0.5))
    mob = np.stack([rad * np.cos(u), rad * np.sin(u),
                    v * np.sin(u * np.float32(0.5))], axis=-1).astype(np.float32)
    mob = np.where(safe[..., None], mob,
                   np.array([R, 0, 0], np.float32))
    tt = np.float32(t)
    return (pts * (np.float32(1.0) - tt) + mob * tt).astype(np.float32)


_SEED_TABLE = {          # name: (how, nu)   every one has exactly 12 pentagons
    "dodec": ("gp", 1),   # C20   GP(1,0)   F=12
    "c60":   ("kis", 0),  # C60   GP(1,1)   F=32   dual of the pentakis dodecahedron
    "c80":   ("gp", 2),   # C80   GP(2,0)   F=42
    "c180":  ("gp", 3),   # C180  GP(3,0)   F=92
    "c320":  ("gp", 4),   # C320  GP(4,0)   F=162
}


def build_seed(kind, R):
    if kind not in _SEED_TABLE:
        raise SystemExit(f"unknown SEED {kind!r} -- try {list(_SEED_TABLE)}")
    how, nu = _SEED_TABLE[kind]
    if how == "gp":
        gv, gt = _geodesic(nu)
        polys = _dual(gv, gt, R)
    else:                       # C60 = dual of the pentakis dodecahedron
        gv, gt = _geodesic(1)
        kv, kt = _kis(_dual(gv, gt, R), R)
        polys = _dual(kv, kt, R)
    P = np.array([p for p in polys if len(p) == 5], np.float32)
    H = np.array([p for p in polys if len(p) == 6], np.float32)
    if H.size == 0: H = np.zeros((0, 6, 3), np.float32)
    if P.size == 0: P = np.zeros((0, 5, 3), np.float32)
    return P, H


# ─────────────────────────────────────────────────────────────────────────────
#  THE OPERATOR
#
#  Vectorised transcription of genesis v8.1 GK.refineFace. Same expressions,
#  same order, midRing included:
#
#     inner[i]   = projectToSphere(lerp(c, pts[i], innerScale))
#     midRing[i] = projectToSphere(lerp(c, mid(pts[i],pts[j]), midScale))
#     em         = projectToSphere(mid(pts[i],pts[j]))
#     inner cell = [inner[0..n-1]]                       arity preserved
#     cell i     = [pts[i], em, pts[j], inner[j], midRing[i], inner[i]]
#
#  midRing sits on the hex side of the cell edge inner[i]->inner[j] and nowhere
#  on the cell side. That is the whole phenomenon. Left exactly as it was.
# ─────────────────────────────────────────────────────────────────────────────
_SPHERICAL_NOW = [None]   # set at runtime; MOBIUS_WHEN="first" forces planar


def _projn(a, R):
    if not _SPHERICAL_NOW[0]:
        return a
    L = np.linalg.norm(a, axis=-1, keepdims=True)
    return a * (R / np.where(L < 1e-12, np.float32(1.0), L))

def refine(faces, R, rng, bar=None):
    """genesis v8.1 GK.refineFace, vectorised, in CHUNKS.

    Output is preallocated, so peak transient memory is set by REFINE_CHUNK
    rather than by the size of the generation. The arithmetic per chunk is
    identical to the scalar original -- verified vertex for vertex against it.
    """
    m, nn, _ = faces.shape
    inner_out = np.empty((m, nn, 3), np.float32)
    cells_out = np.empty((m * nn, 6, 3), np.float32)
    step = max(1, int(REFINE_CHUNK))
    for s0 in range(0, m, step):
        s1 = min(m, s0 + step)
        f = faces[s0:s1]
        c = f.mean(axis=1, keepdims=True)
        inner = _projn(c + (f - c) * np.float32(INNER_SCALE), R)
        nxt = np.roll(f, -1, axis=1)
        mid = (f + nxt) * np.float32(0.5)
        midRing = _projn(c + (mid - c) * np.float32(MID_SCALE), R)
        em = _projn(mid, R)
        if JITTER > 0.0:
            inner += (rng.random(inner.shape, dtype=np.float32) - np.float32(0.5)) * np.float32(JITTER)
            midRing += (rng.random(midRing.shape, dtype=np.float32) - np.float32(0.5)) * np.float32(JITTER)
        innerN = np.roll(inner, -1, axis=1)
        inner_out[s0:s1] = inner
        np.stack([f, em, nxt, innerN, midRing, inner], axis=2,
                 out=cells_out[s0*nn:s1*nn].reshape(s1-s0, nn, 6, 3))
        del c, inner, nxt, mid, midRing, em, innerN
        if bar: bar.step(s1 - s0)
    return inner_out, cells_out


# ─────────────────────────────────────────────────────────────────────────────
#  edges -> screen -> additive raster
# ─────────────────────────────────────────────────────────────────────────────
def make_camera():
    cx, sx = math.cos(ROT_X), math.sin(ROT_X)
    cy, sy = math.cos(ROT_Y), math.sin(ROT_Y)
    cz, sz = math.cos(ROT_Z), math.sin(ROT_Z)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return (Rz @ Rx @ Ry).astype(np.float32)


def draw_faces(faces, acc, M, D, focal, bar, face_chunk, atoms=False, atom_r=0.0):
    """Faces live in system RAM; only screen-space coords cross to the GPU.

    Depth alpha follows genesis exactly:  alpha = 0.15 + depth01*0.5,
    so faces nearer the camera contribute more, which is what gives the
    shell its interior falloff rather than a flat wash of lines.

    atoms=True splats a disc on every vertex instead of drawing the edges,
    and only for faces whose screen extent clears ATOM_MIN_PX -- genesis'
    own ss>5 test, which is also what stops it costing anything at depth.
    """
    W, H = WIDTH, HEIGHT
    m, nn, _ = faces.shape
    Rs = np.float32(SPHERE_R)
    for s0 in range(0, m, face_chunk):
        s1 = min(m, s0 + face_chunk)
        f = faces[s0:s1]
        V = (f.reshape(-1, 3) @ M.T).reshape(s1-s0, nn, 3)
        w = D - V[:, :, 2]
        ok = w > 0.02
        wsafe = np.where(ok, w, np.float32(1.0))
        X = np.float32(W*0.5) + V[:, :, 0] * focal / wsafe
        Y = np.float32(H*0.5) - V[:, :, 1] * focal / wsafe
        # genesis: depth01 = clamp((depth+2)/4,0,1); depth here is view-space z
        d01 = np.clip((V[:, :, 2] + Rs) / (np.float32(2.0)*Rs), 0.0, 1.0)
        alpha = (np.float32(0.15) + d01 * np.float32(0.5)).astype(np.float32)
        allok = ok.all(axis=1)
        del V, w, wsafe, d01

        if atoms:
            ext = np.maximum(X.max(1) - X.min(1), Y.max(1) - Y.min(1))
            sel = allok & (ext > np.float32(ATOM_MIN_PX))
            if sel.any():
                px = X[sel].ravel(); py = Y[sel].ravel()
                pa = alpha[sel].ravel()
                _splat(px, py, pa, atom_r, acc)
                del px, py, pa
            del ext, sel
        else:
            gx = np.roll(X, -1, axis=1); gy = np.roll(Y, -1, axis=1)
            ga = np.roll(alpha, -1, axis=1)
            keep = (ok & np.roll(ok, -1, axis=1)).ravel()
            x0 = X.ravel()[keep]; y0 = Y.ravel()[keep]
            x1 = gx.ravel()[keep]; y1 = gy.ravel()[keep]
            aw = ((alpha.ravel()[keep] + ga.ravel()[keep]) * np.float32(0.5))
            del gx, gy, ga, keep
            if x0.size:
                _scatter(x0, y0, x1, y1, aw, acc)
            del x0, y0, x1, y1, aw
        del f, X, Y, alpha, ok, allok
        bar.step(s1 - s0)


def _disc(r):
    """integer offsets of a filled disc of radius r, plus per-offset coverage"""
    R = max(1, int(math.ceil(r)))
    yy, xx = np.mgrid[-R:R+1, -R:R+1]
    d = np.sqrt(xx*xx + yy*yy)
    cov = np.clip(r + 0.5 - d, 0.0, 1.0)      # soft edge
    m = cov > 0.01
    return xx[m].astype(np.int32), yy[m].astype(np.int32), cov[m].astype(np.float32)


def _splat(px, py, pa, r, acc):
    """additive discs at every point. duplicates stack, as genesis' do."""
    W, H = WIDTH, HEIGHT
    ox, oy, cov = _disc(r)
    k = ox.size
    per = max(1, int(CHUNK_SAMPLES) // max(1, k))
    gox = xp.asarray(ox)[None, :]; goy = xp.asarray(oy)[None, :]
    gcv = xp.asarray(cov)[None, :]
    for s0 in range(0, px.size, per):
        gx = xp.asarray(px[s0:s0+per]).astype(xp.int32)[:, None] + gox
        gy = xp.asarray(py[s0:s0+per]).astype(xp.int32)[:, None] + goy
        gw = xp.asarray(pa[s0:s0+per])[:, None] * gcv
        inb = (gx >= 0) & (gx < W) & (gy >= 0) & (gy < H)
        idx = (gy[inb].astype(xp.int64) * W + gx[inb].astype(xp.int64))
        wts = gw[inb].astype(xp.float64)
        del gx, gy, gw, inb
        if idx.size:
            acc += xp.bincount(idx, weights=wts, minlength=W*H).astype(xp.float32)
        del idx, wts


def _scatter(x0, y0, x1, y1, aw, acc):
    """additive line accumulation. edges are bucketed by pixel length into
    powers of two so each bucket is one vectorised linspace."""
    W, H = WIDTH, HEIGHT
    dx = x1 - x0; dy = y1 - y0
    ln = np.maximum(np.abs(dx), np.abs(dy))
    steps = np.clip(np.ceil(ln), 1, 4096).astype(np.int32)
    b = np.clip(1 << np.ceil(np.log2(np.maximum(steps, 1))).astype(np.int32), 1, 4096)
    for bv in np.unique(b):
        bv = int(bv)
        sel = np.nonzero(b == bv)[0]
        per = max(1, int(CHUNK_SAMPLES) // bv)
        t = xp.linspace(xp.float32(0), xp.float32(1), bv, dtype=xp.float32)[None, :]
        for s0 in range(0, sel.size, per):
            ii = sel[s0:s0 + per]
            gx0 = xp.asarray(x0[ii]); gy0 = xp.asarray(y0[ii])
            gdx = xp.asarray(dx[ii]); gdy = xp.asarray(dy[ii])
            gw = xp.broadcast_to(xp.asarray(aw[ii])[:, None], (ii.size, bv))
            X = (gx0[:, None] + gdx[:, None] * t).astype(xp.int32).ravel()
            Y = (gy0[:, None] + gdy[:, None] * t).astype(xp.int32).ravel()
            del gx0, gy0, gdx, gdy
            inb = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
            idx = Y[inb].astype(xp.int64) * W + X[inb].astype(xp.int64)
            wts = gw.ravel()[inb].astype(xp.float64)
            del X, Y, inb, gw
            if idx.size:
                acc += xp.bincount(idx, weights=wts, minlength=W*H).astype(xp.float32)
            del idx, wts


# ─────────────────────────────────────────────────────────────────────────────
#  EXACT renderer -- the canvas, ported
#
#  Four things genesis does that the additive path does not, and which is why
#  the additive path can never line up with a screenshot:
#    1. orthographic projection scaled by cam.zoom
#    2. sub-pixel cull: screenSize = |proj(pts[0]) - proj(pts[1])| < 0.5 -> drop
#    3. backface cull by screen winding, threshold -max(0.5, screenSize*0.02)
#    4. fills UNDER strokes, painter-sorted, composited source-over
#  In the reference screenshot #2 drops 47% of the mesh on its own, and that
#  is also what makes the Mobius spikes dominate: spike faces are big, shell
#  faces are sub-pixel.
# ─────────────────────────────────────────────────────────────────────────────
def project_exact(pts, rx, ry, zoom, w, h):
    """genesis project(), outside mode, verbatim."""
    x, y, z = pts[..., 0], pts[..., 1], pts[..., 2]
    cy, sy = math.cos(ry), math.sin(ry)
    crx, srx = math.cos(rx), math.sin(rx)
    x1 = x * cy - z * sy
    z1 = x * sy + z * cy
    y1 = y * crx - z1 * srx
    z2 = y * srx + z1 * crx
    return (w / 2 + x1 * zoom), (h / 2 - y1 * zoom), z2


def cull_exact(faces, rx, ry, zoom, w, h):
    """genesis' four culls in its own order, then the painter sort."""
    X, Y, Z = project_exact(faces, rx, ry, zoom, w, h)
    cX, cY, cZ = X.mean(1), Y.mean(1), Z.mean(1)
    ss = np.hypot(X[:, 0] - X[:, 1], Y[:, 0] - Y[:, 1])
    keep = ss >= 0.5
    keep &= (cX >= -200) & (cX <= w + 200) & (cY >= -200) & (cY <= h + 200)
    cross = ((X[:, 1] - X[:, 0]) * (Y[:, 2] - Y[:, 0]) -
             (Y[:, 1] - Y[:, 0]) * (X[:, 2] - X[:, 0]))
    keep &= cross >= -np.maximum(0.5, ss * 0.02)
    idx = np.nonzero(keep)[0]
    idx = idx[np.argsort(cZ[idx], kind="stable")]
    return idx, ss, cZ, X, Y


# the genesis draw path, rgb exact
_EX = dict(bg=(5, 5, 8),
           hex_fill=(0, 40, 60), hex_fill_a=0.3,
           pent_fill=(193, 74, 59), pent_fill_a=0.4,
           hex_edge=(0, 180, 255), hex_edge_a=0.6, hex_lw=0.5,
           pent_edge=(255, 105, 180), pent_edge_a=1.0, pent_lw=1.5,
           hex_atom=(0, 255, 213), hex_atom_a=0.6,
           pent_atom=(255, 105, 180), pent_atom_a=1.0)


def render_exact(P, Hf):
    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure
        from matplotlib.collections import PolyCollection
    except ImportError:
        raise SystemExit("  RENDERER='exact' needs matplotlib: pip install matplotlib")

    ssf = max(1, int(SUPERSAMPLE))
    w, h, zoom = WIDTH * ssf, HEIGHT * ssf, CAM_ZOOM * ssf
    totalF = P.shape[0] + Hf.shape[0]

    packs = []
    for tag, F in (("pent", P), ("hex", Hf)):
        if F.shape[0]:
            packs.append((tag, F) + cull_exact(F, CAM_RX, CAM_RY, zoom, w, h))
    drawn = sum(len(p[2]) for p in packs)
    print(f"  drawn {drawn:,}/{totalF:,}  ({100*drawn/max(1,totalF):.0f}% "
          f"-- the rest is genesis' own culling)")

    order = sorted(((pk[4][i], pi, i) for pi, pk in enumerate(packs) for i in pk[2]),
                   key=lambda t: t[0])

    fig = Figure(figsize=(w / 100, h / 100), dpi=100)
    fig.subplots_adjust(0, 0, 1, 1)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis("off")
    bg = tuple(c / 255 for c in _EX["bg"])
    ax.set_facecolor(bg); fig.patch.set_facecolor(bg)

    verts, fcol, ecol, lws = [], [], [], []
    ax_, ay_, ac_, as_ = [], [], [], []
    bar = Bar(len(order), "exact compositing")
    for cz, pi, i in order:
        tag, F, _, ss, _, X, Y = packs[pi]
        isP = tag == "pent"
        # genesis: alpha = 0.15 + clamp((depth+2)/4, 0, 1)*0.5
        a = 0.15 + min(max((cz + 2.0) / 4.0, 0.0), 1.0) * 0.5
        verts.append(np.column_stack([X[i], Y[i]]))
        fcol.append(tuple(c / 255 for c in (_EX["pent_fill"] if isP else _EX["hex_fill"]))
                    + (a * (_EX["pent_fill_a"] if isP else _EX["hex_fill_a"]),))
        ecol.append(tuple(c / 255 for c in (_EX["pent_edge"] if isP else _EX["hex_edge"]))
                    + (a * (_EX["pent_edge_a"] if isP else _EX["hex_edge_a"]),))
        lws.append((_EX["pent_lw"] if isP else _EX["hex_lw"]) * ssf)
        if CAM_ATOM > 0.2 and ss[i] > 5 * ssf:      # genesis' own gate
            r = CAM_ATOM * (2.0 if isP else 1.2) * ssf
            col = tuple(c / 255 for c in (_EX["pent_atom"] if isP else _EX["hex_atom"])) \
                  + (a * (_EX["pent_atom_a"] if isP else _EX["hex_atom_a"]),)
            for k in range(F.shape[1]):
                ax_.append(X[i, k]); ay_.append(Y[i, k])
                ac_.append(col); as_.append(math.pi * r * r)
        bar.step()
    bar.done(f"{len(order):,} faces")

    ax.add_collection(PolyCollection(verts, facecolors=fcol, edgecolors=ecol,
                                     linewidths=lws, antialiased=True))
    if ax_:
        ax.scatter(ax_, ay_, s=as_, c=ac_, linewidths=0, marker="o")
        print(f"  atoms {len(ax_):,} discs (screenSize>5 only)")

    canvas = FigureCanvasAgg(fig); canvas.draw()
    img = np.asarray(canvas.buffer_rgba())[..., :3].astype(np.float32)
    if ssf > 1:
        img = img.reshape(HEIGHT, ssf, WIDTH, ssf, 3).mean(axis=(1, 3))
    return np.clip(img, 0, 255).astype(np.uint8)


# ─────────────────────────────────────────────────────────────────────────────
#  tone map + save
# ─────────────────────────────────────────────────────────────────────────────
def tonemap(R, G, B, PAL):
    GAIN_ = PAL["gain"] if GAIN is None else GAIN
    TONE_ = PAL["tone"] if TONE is None else TONE
    GAMMA_ = PAL["gamma"] if GAMMA is None else GAMMA
    BACKGROUND = PAL["bg"]
    def f(a):
        a = a * np.float32(GAIN_)
        if TONE_ == "log":
            a = np.log1p(a)
        elif TONE_ == "asinh":
            a = np.arcsinh(a)
        m = float(a.max())
        if m > 0: a = a / m
        return np.power(a, np.float32(GAMMA_))
    R, G, B = f(R), f(G), f(B)
    bg = np.array(BACKGROUND, np.float32) / 255.0
    img = np.stack([
        bg[0] + (1.0 - bg[0]) * R,
        bg[1] + (1.0 - bg[1]) * G,
        bg[2] + (1.0 - bg[2]) * B,
    ], axis=-1)
    return (np.clip(img, 0, 1) * 255.0 + 0.5).astype(np.uint8)



# ─────────────────────────────────────────────────────────────────────────────
#  capacity planner:  python genesis_wallpaper.py --plan
#
#  face growth for this operator, from the 12-pentagon seed:
#     REFINE ALL   P stays 12,  H' = 5P + 7H   ->  F' = 7F - 12
#     REFINE 6s    pentagons untouched, H' = 7H  ->  F' = 7F - 72
#  a hexagon is 6 verts x 3 floats x 4 bytes = 72 B. pentagons are noise.
# ─────────────────────────────────────────────────────────────────────────────
RAM_GB  = None     # None = detect
VRAM_GB = 6.0      # informational only; the mesh never lives in VRAM

def plan():
    global RAM_GB, MEM_BUDGET_GB
    RAM_GB = _detect_ram() if RAM_GB is None else RAM_GB
    if MEM_BUDGET_GB == "auto":
        MEM_BUDGET_GB = round(RAM_GB * 0.82, 1)
    print("=" * 79)
    print("  CAPACITY  ·  %.1f GB RAM detected  ·  budget %.1f GB" % (RAM_GB, MEM_BUDGET_GB))
    print("=" * 79)
    print("  The mesh is built in RAM and streamed to the GPU for rasterising, so")
    print("  VRAM no longer caps how deep you can go -- RAM does. A hexagon is")
    print("  6 verts x 3 floats x 4 B = 72 B.  DRAW_HISTORY keeps ~1.17x the final.")
    print("  Refining adds only REFINE_CHUNK-sized transients on top.\n")
    hdr = "  %-24s %16s %10s %11s %9s"
    print(hdr % ("order of operations", "faces", "final", "w/ history", "verdict"))
    print("  " + "-" * 73)
    rows = []
    for seed, F0 in (("dodec", 12), ("c60", 32), ("c80", 42), ("c180", 92), ("c320", 162)):
        for ops in ([["all"]*k for k in (6, 7, 8)] +
                    [["all"] + ["hex"]*k for k in (5, 6, 7)]):
            F, P = F0, 12
            for o in ops:
                H = F - P
                F = (P + 5*P + 7*H) if o == "all" else (P + 7*H)
            final = ((F - 12)*6 + 12*5) * 12 / 2**30
            hist = final * 7/6
            need = hist + 0.3
            v = "OK" if need < MEM_BUDGET_GB else ("tight" if need < RAM_GB*0.85 else "no")
            lbl = "%s: %s" % (seed, "all x%d" % len(ops) if all(o == "all" for o in ops)
                              else "all + 6s x%d" % (len(ops)-1))
            rows.append(hdr % (lbl, "{:,}".format(F), "%.2f GB" % final,
                               "%.2f GB" % hist, v))
    for r in rows: print(r)
    print("  " + "-" * 73)
    print("  The mesh never touches VRAM, so a GPU changes speed, not depth.")
    print("  DRAW_HISTORY=False buys back ~15% if you need one more step.")
    print("=" * 79)


def human(n):
    for u in ("", "K", "M", "G"):
        if abs(n) < 1000: return f"{n:,.0f}{u}" if u == "" else f"{n:,.1f}{u}"
        n /= 1000.0
    return f"{n:.1f}T"


OUT_ACTUAL = [None]


def main():
    print("=" * 79)
    print("  GENESIS WALLPAPER GENERATOR  ·  v8.1 operator, verbatim, midRing intact")
    print("=" * 79)
    _pick_backend()
    print(f"  canvas  : {WIDTH} x {HEIGHT}  ({WIDTH*HEIGHT/1e6:.1f} Mpx)")
    print(f"  operator: inner={INNER_SCALE}  mid={MID_SCALE}  jitter={JITTER}  "
          f"{'spherical' if SPHERICAL else 'planar'}")
    d = MID_SCALE - INNER_SCALE
    print(f"  crescent: mid-inner = {d:+.2f}  ->  "
          f"{'GAP (rosette)' if d > 0 else 'OVERLAP (layered)' if d < 0 else 'flat, still open'}")
    print(f"  order   : {' -> '.join(OPS)}")
    print(f"  renderer: {RENDERER}" + ("   (orthographic, culled, source-over)"
          if RENDERER == "exact" else "   (additive lines)"))
    if MOBIUS_T > 0.0:
        print(f"  mobius  : t={MOBIUS_T:.2f}  R={MOBIUS_R}  W={MOBIUS_W}  "
              f"when={MOBIUS_WHEN}  project={MOBIUS_PROJECT}")
    print()

    PAL = PALETTES[PALETTE]
    PENT = PAL["pent"] if PENT_BOOST is None else PENT_BOOST
    print(f"  palette : {PALETTE}  ({PAL.get('mode','generation')})   "
          f"atom={ATOM_SIZE:.2f} (min {ATOM_MIN_PX:.0f} px)   history={DRAW_HISTORY}")
    print()

    rng = np.random.default_rng(12345)

    # ── build: system RAM, always. see the note in CONFIG. ───────────────
    P, H = build_seed(SEED, SPHERE_R)

    _SPHERICAL_NOW[0] = SPHERICAL
    if MOBIUS_T > 0.0 and MOBIUS_WHEN == "first":
        P = sphere_to_mobius(P, MOBIUS_R, MOBIUS_W, MOBIUS_T)
        H = sphere_to_mobius(H, MOBIUS_R, MOBIUS_W, MOBIUS_T)
        if MOBIUS_PROJECT:
            print("  mobius  : twisted the SEED, refining with projectToSphere ON.")
            print("            children snap to r=SPHERE_R, inherited corners do not.")
            print("            that mismatch is the spikes. this is genesis' order.")
        else:
            _SPHERICAL_NOW[0] = False
            print("  mobius  : twisted the SEED, refining planar -> smooth strip.")
    generations = [(P.copy(), H.copy())] if DRAW_HISTORY else []
    kept = P.nbytes + H.nbytes
    print(f"  gen 0  {SEED:<6} P={P.shape[0]:>13,}  H={H.shape[0]:>13,}  "
          f"F={P.shape[0]+H.shape[0]:>14,}")

    for gi, op in enumerate(OPS, 1):
        nP, nH = P.shape[0], H.shape[0]
        if op == "all":     fP, fH = nP, 5*nP + 7*nH
        elif op == "hex":   fP, fH = nP, 7*nH
        else:               fP, fH = 0, nH + 7*nP
        out_b = (fP*5 + fH*6) * 12
        need = (kept + out_b + min(REFINE_CHUNK, max(nP, nH)) * 6*6*12*3) / 2**30
        if need > MEM_BUDGET_GB:
            print(f"\n  gen {gi}  {op}: needs ~{need:.1f} GB for F={fP+fH:,} — "
                  f"over MEM_BUDGET_GB={MEM_BUDGET_GB}. Stopping here.")
            print("  raise MEM_BUDGET_GB, set DRAW_HISTORY=False, or drop one op.")
            break

        bar = Bar(nP + nH, f"gen {gi} {op} refine")
        newP = [P] if op == "hex" else []
        newH = [H] if op == "pent" else []
        if op in ("all", "pent") and nP:
            ip, cp = refine(P, SPHERE_R, rng, bar); newP.append(ip); newH.append(cp)
        if op in ("all", "hex") and nH:
            ih, ch = refine(H, SPHERE_R, rng, bar); newH.append(ih); newH.append(ch)
        P = np.concatenate(newP, 0) if newP else np.zeros((0, 5, 3), np.float32)
        H = np.concatenate(newH, 0) if newH else np.zeros((0, 6, 3), np.float32)
        del newP, newH
        if DRAW_HISTORY: generations.append((P, H))
        else:            generations = [(P, H)]
        kept = sum(a.nbytes + b.nbytes for a, b in generations)
        bar.done(f"F={P.shape[0]+H.shape[0]:,}   mesh {kept/2**30:.2f} GB")

    if MOBIUS_T > 0.0 and MOBIUS_WHEN == "last":
        print("  mobius  : applied after refinement (genesis' own order)")
        generations = [(sphere_to_mobius(a, MOBIUS_R, MOBIUS_W, MOBIUS_T),
                        sphere_to_mobius(b, MOBIUS_R, MOBIUS_W, MOBIUS_T))
                       for a, b in generations]

    total_edges = sum(p.shape[0]*5 + h.shape[0]*6 for p, h in generations)
    print(f"\n  generations: {len(generations)}   mesh in RAM: {kept/2**30:.2f} GB"
          f"   edges: {human(total_edges)}\n")

    if RENDERER == "exact":
        # genesis has no history -- it draws the mesh it currently holds
        img = render_exact(P, H)
        del generations, P, H
    else:
        # ── raster: GPU if present, fed from RAM in chunks ───────────────────
        M = make_camera()
        # spikes reach ~R+W even though the body stays at SPHERE_R
        _scale = (MOBIUS_R + MOBIUS_W) if MOBIUS_T > 0.0 else SPHERE_R
        D = np.float32(CAM_DIST * (SPHERE_R * (1 - MOBIUS_T) + _scale * MOBIUS_T))
        focal = np.float32((HEIGHT * 0.5) / math.tan(math.radians(FOV_DEG) * 0.5) * ZOOM)
        face_chunk = max(50_000, int(CHUNK_SAMPLES) // 24)

        Rb = xp.zeros(WIDTH*HEIGHT, xp.float32)
        Gb = xp.zeros(WIDTH*HEIGHT, xp.float32)
        Bb = xp.zeros(WIDTH*HEIGHT, xp.float32)

        def blend(acc, rgb, mul):
            Rb[...] += acc * xp.float32(rgb[0] / 255.0 * mul)
            Gb[...] += acc * xp.float32(rgb[1] / 255.0 * mul)
            Bb[...] += acc * xp.float32(rgb[2] / 255.0 * mul)

        facetype = PAL.get("mode", "generation") == "facetype"
        ncol = len(PAL.get("colors", [(1, 1, 1)])); span = max(1, len(generations) - 1)

        for gi, (Pg, Hg) in enumerate(generations):
            for tag, faces in (("pent", Pg), ("hex", Hg)):
                if faces.shape[0] == 0:
                    continue
                isP = (tag == "pent")
                # ---- edges ----
                acc = xp.zeros(WIDTH*HEIGHT, xp.float32)
                bar = Bar(faces.shape[0], f"gen {gi} {tag} edges")
                draw_faces(faces, acc, M, D, focal, bar, face_chunk)
                bar.done(f"{human(faces.shape[0]*faces.shape[1])} edges")
                if facetype:
                    blend(acc, PAL["pent_edge"] if isP else PAL["hex_edge"],
                          (PAL["pent_mul"] if isP else PAL["hex_mul"]) * (PENT if isP else 1.0))
                else:
                    c = PAL["colors"][min(ncol-1, int(round(gi*(ncol-1)/span)))]
                    blend(acc, tuple(v*255 for v in c), PENT if isP else 1.0)
                del acc
                # ---- atoms ----
                if ATOM_SIZE > 0.0:
                    r = ATOM_SIZE * (2.0 if isP else 1.2)
                    acc = xp.zeros(WIDTH*HEIGHT, xp.float32)
                    bar = Bar(faces.shape[0], f"gen {gi} {tag} atoms r={r:.1f}")
                    draw_faces(faces, acc, M, D, focal, bar, face_chunk, atoms=True, atom_r=r)
                    bar.done("vertex discs")
                    if facetype:
                        blend(acc, PAL["pent_atom"] if isP else PAL["hex_atom"],
                              PAL["pent_atom_mul"] if isP else PAL["hex_atom_mul"])
                    else:
                        c = PAL["colors"][min(ncol-1, int(round(gi*(ncol-1)/span)))]
                        blend(acc, tuple(v*255 for v in c), 1.3)
                    del acc

        print("\n  tone mapping and encoding ...")
        if GPU:
            Rn, Gn, Bn = xp.asnumpy(Rb), xp.asnumpy(Gb), xp.asnumpy(Bb)
            del Rb, Gb, Bb
            xp.get_default_memory_pool().free_all_blocks()
        else:
            Rn, Gn, Bn = Rb, Gb, Bb
        img = tonemap(Rn.reshape(HEIGHT, WIDTH), Gn.reshape(HEIGHT, WIDTH),
                      Bn.reshape(HEIGHT, WIDTH), PAL)
        del generations, P, H
    out = OUT
    if out is None:
        ops_tag = "".join(f"{sum(1 for o in OPS if o == k)}{k[0]}"
                          for k in ("all", "hex", "pent") if any(o == k for o in OPS))
        out = os.path.join(OUT_DIR,
            f"{int(time.time())}"
            +("_gens_" if RENDERER == "additive" else "exact_")
            + f"in{INNER_SCALE:.2f}_mid{MID_SCALE:.2f}_{SEED}"
            + f"_{ops_tag}"
            + (f"_atm{ATOM_SIZE:.2f}" if RENDERER == "additive"
               else f"_zm{CAM_ZOOM:.0f}_atm{CAM_ATOM:.2f}")
            + (f"_mob{MOBIUS_T:.2f}{MOBIUS_WHEN[0]}"
               + ("p" if MOBIUS_PROJECT else "s") if MOBIUS_T > 0.0 else "")
            + f"_.jpg")
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    Image.fromarray(img, "RGB").save(out, "JPEG", quality=JPG_QUALITY,
                                     optimize=True, progressive=True)
    OUT_ACTUAL[0] = out
    print(f"  written : {out}\n            {os.path.getsize(out)/2**20:.1f} MB   {WIDTH}x{HEIGHT}")
    print("=" * 79)


if __name__ == "__main__":
    if "--plan" in sys.argv:
        plan()
    else:
        main()

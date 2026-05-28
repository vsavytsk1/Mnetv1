#!/usr/bin/env python3

"""
GENESIS GPU v1.0 — Unlimited Goldberg Fractal Engine
=====================================================
NVIDIA GPU-accelerated. No face limit. No browser. Pure math.

Requirements:  pip install pygame PyOpenGL numpy
Kill command:  taskkill /PID <pid> /F

Controls:
  Mouse drag  = rotate
  Scroll      = zoom
  R           = refine ALL (adds ~6x faces each time)
  P           = refine PENTS only
  F           = toggle flow simulation
  SPACE       = pause/resume spin
  ESC         = quit
  1-9         = jump to refinement level
"""

import os, sys, time, math
import numpy as np

PID = os.getpid()
print("=" * 60)
print(f"  GENESIS GPU v1.0 — Unlimited Fractal Engine")
print(f"  PID: {PID}")
print(f"  KILL: taskkill /PID {PID} /F")
print("=" * 60)

# ============================================================================
#  DEPENDENCIES
# ============================================================================
try:
    import pygame
    from pygame.locals import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError as e:
    print(f"\nMissing dependency: {e}")
    print("Install with:  pip install pygame PyOpenGL numpy")
    sys.exit(1)

# ============================================================================
#  GOLDBERG KERNEL — numpy-accelerated
# ============================================================================
PHI = (1 + math.sqrt(5)) / 2

def normalize(v):
    L = np.linalg.norm(v, axis=-1, keepdims=True)
    L = np.where(L < 1e-12, 1, L)
    return v / L

def build_dodecahedron():
    """Build the pure seed: 12 pentagons, 0 hexagons."""
    inv_phi = 1.0 / PHI
    raw = np.array([
        [ 1, 1, 1],[ 1, 1,-1],[ 1,-1, 1],[ 1,-1,-1],
        [-1, 1, 1],[-1, 1,-1],[-1,-1, 1],[-1,-1,-1],
        [0, inv_phi, PHI],[0, inv_phi,-PHI],[0,-inv_phi, PHI],[0,-inv_phi,-PHI],
        [inv_phi, PHI, 0],[inv_phi,-PHI, 0],[-inv_phi, PHI, 0],[-inv_phi,-PHI, 0],
        [PHI, 0, inv_phi],[PHI, 0,-inv_phi],[-PHI, 0, inv_phi],[-PHI, 0,-inv_phi]
    ], dtype=np.float64)
    # Normalize to sphere
    raw = normalize(raw) * 1.6

    # Find edges
    dists = np.linalg.norm(raw[:, None] - raw[None, :], axis=-1)
    np.fill_diagonal(dists, 999)
    edge_len = dists[dists > 0.01].min()
    tol = edge_len * 0.1

    # Adjacency
    adj = [[] for _ in range(len(raw))]
    for i in range(len(raw)):
        for j in range(len(raw)):
            if i != j and abs(np.linalg.norm(raw[i] - raw[j]) - edge_len) < tol:
                adj[i].append(j)

    # Sort neighbours CCW
    for i in range(len(raw)):
        v = raw[i]
        n = v / np.linalg.norm(v)
        ref = raw[adj[i][0]] - v
        dot = np.dot(ref, n)
        tangent = ref - n * dot
        tl = np.linalg.norm(tangent)
        if tl > 1e-12: tangent /= tl
        e2 = np.cross(n, tangent)
        def angle(idx):
            d = raw[idx] - v
            return math.atan2(np.dot(d, e2), np.dot(d, tangent))
        adj[i].sort(key=angle)

    # Trace pentagonal faces (half-edge)
    def next_in_face(u, v):
        idx = adj[v].index(u) if u in adj[v] else -1
        if idx < 0: return -1
        return adj[v][(idx + len(adj[v]) - 1) % len(adj[v])]

    visited = set()
    faces = []
    for u in range(len(raw)):
        for v in adj[u]:
            if (u, v) in visited: continue
            face = [u]
            a, b = u, v
            for _ in range(10):
                visited.add((a, b))
                c = next_in_face(a, b)
                if c < 0 or c == u: break
                face.append(b)
                a, b = b, c
            if face[-1] != b: face.append(b)
            if len(face) == 5: faces.append(face)

    # Deduplicate
    seen = set()
    unique = []
    for f in faces:
        key = tuple(sorted(f))
        if key not in seen:
            seen.add(key)
            unique.append(f)

    # Build mesh
    mesh = []
    for f in unique:
        pts = np.array([raw[k] for k in f], dtype=np.float64)
        mesh.append({'pts': pts, 'type': 'pent'})
    return mesh


def centroid(pts):
    return pts.mean(axis=0)


def refine_all(faces, sphere_r=1.6):
    """Refine all faces. Pentagon→1P+5H, Hexagon→1H+6H."""
    out = []
    for face in faces:
        pts = face['pts']
        n = len(pts)
        c = centroid(pts)

        # Inner ring
        inner = np.array([c + 0.45 * (pts[i] - c) for i in range(n)])
        inner = normalize(inner) * sphere_r

        # Mid ring
        mid = []
        for i in range(n):
            m = (pts[i] + pts[(i+1) % n]) * 0.5
            pulled = c + 0.70 * (m - c)
            mid.append(pulled)
        mid = np.array(mid)
        mid = normalize(mid) * sphere_r

        # Center face (same type as parent)
        out.append({'pts': inner.copy(), 'type': face['type']})

        # Edge hexagons
        for i in range(n):
            j = (i + 1) % n
            em = (pts[i] + pts[j]) * 0.5
            em = normalize(em.reshape(1, 3)).flatten() * sphere_r
            hex_pts = np.array([
                pts[i], em, pts[j],
                inner[j], mid[i], inner[i]
            ], dtype=np.float64)
            out.append({'pts': hex_pts, 'type': 'hex'})

    return out


def refine_pents(faces, sphere_r=1.6):
    """Refine only pentagons."""
    out = []
    for face in faces:
        if face['type'] == 'pent':
            pts = face['pts']
            n = len(pts)
            c = centroid(pts)
            inner = np.array([c + 0.45 * (pts[i] - c) for i in range(n)])
            inner = normalize(inner) * sphere_r
            mid = []
            for i in range(n):
                m = (pts[i] + pts[(i+1) % n]) * 0.5
                pulled = c + 0.70 * (m - c)
                mid.append(pulled)
            mid = np.array(mid)
            mid = normalize(mid) * sphere_r
            out.append({'pts': inner.copy(), 'type': 'pent'})
            for i in range(n):
                j = (i + 1) % n
                em = (pts[i] + pts[j]) * 0.5
                em = normalize(em.reshape(1, 3)).flatten() * sphere_r
                hex_pts = np.array([pts[i], em, pts[j], inner[j], mid[i], inner[i]])
                out.append({'pts': hex_pts, 'type': 'hex'})
        else:
            out.append(face)
    return out


def compute_invariants(faces):
    pents = sum(1 for f in faces if f['type'] == 'pent')
    hexes = sum(1 for f in faces if f['type'] == 'hex')
    fes = 5 * pents + 6 * hexes
    V = round(fes / 3)
    E = round(fes / 2)
    F = len(faces)
    chi = V - E + F
    return {'F': F, 'P': pents, 'H': hexes, 'V': V, 'E': E, 'chi': chi, 'EV': E/max(V,1)}


# ============================================================================
#  FLOW ENGINE
# ============================================================================
class FlowEngine:
    def __init__(self, faces):
        self.n = len(faces)
        self.pressure = np.zeros(self.n, dtype=np.float32)
        self.pressure[0] = 1.0
        self.source = 0
        self.step = 0
        self.active = False
        self.mix = 0.6
        # Build adjacency via shared edges
        edge_map = {}
        self.adj = [[] for _ in range(self.n)]
        for i, face in enumerate(faces):
            pts = face['pts']
            for k in range(len(pts)):
                a = tuple(np.round(pts[k], 3))
                b = tuple(np.round(pts[(k+1) % len(pts)], 3))
                key = (a, b)
                rkey = (b, a)
                if rkey in edge_map:
                    j = edge_map[rkey]
                    if j not in self.adj[i]: self.adj[i].append(j)
                    if i not in self.adj[j]: self.adj[j].append(i)
                else:
                    edge_map[key] = i

    def step_flow(self):
        if not self.active: return
        p = self.pressure
        p_new = np.zeros_like(p)
        mix = self.mix
        self_mix = 1.0 - mix
        for i in range(self.n):
            nb = self.adj[i]
            if not nb: continue
            avg = sum(p[j] for j in nb) / len(nb)
            p_new[i] = p[i] * self_mix + avg * mix
        p_new[self.source] = 1.0
        self.pressure = p_new
        self.step += 1


# ============================================================================
#  OPENGL RENDERER
# ============================================================================
class GenesisGPU:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.W, self.H = info.current_w - 100, info.current_h - 100
        pygame.display.set_mode((self.W, self.H), DOUBLEBUF | OPENGL | RESIZABLE)
        pygame.display.set_caption(f"GENESIS GPU v1.0 — PID {PID}")

        # OpenGL setup
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.02, 0.02, 0.05, 1.0)

        # Camera
        self.rot_x = 20.0
        self.rot_y = 0.0
        self.zoom = -6.0
        self.spinning = True
        self.dragging = False
        self.last_mouse = (0, 0)

        # State
        self.faces = build_dodecahedron()
        self.level = 0
        self.flow = None
        self.rebuild_flow()
        self.display_list = None
        self.rebuild_display_list()

        # Timing
        self.clock = pygame.time.Clock()
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()

        # Font
        self.font = pygame.font.SysFont('Consolas', 14)
        self.font_big = pygame.font.SysFont('Consolas', 18, bold=True)

        self.print_stats()

    def rebuild_flow(self):
        print(f"  Building adjacency for {len(self.faces)} faces...")
        t0 = time.time()
        self.flow = FlowEngine(self.faces)
        print(f"  Adjacency done in {time.time()-t0:.2f}s")

    def rebuild_display_list(self):
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        for i, face in enumerate(self.faces):
            pts = face['pts']
            is_pent = face['type'] == 'pent'
            c = centroid(pts)
            n = c / max(np.linalg.norm(c), 1e-12)

            # Get flow pressure for color
            p = self.flow.pressure[i] if self.flow else 0

            # Fill color
            if p > 0.01:
                r = min(1.0, p * 1.5)
                g = min(1.0, p * 1.0)
                b = max(0.0, 0.7 - p)
                glColor4f(r, g, b, 0.85)
            elif is_pent:
                glColor4f(0.75, 0.29, 0.23, 0.7)
            else:
                glColor4f(0.0, 0.15, 0.25, 0.6)

            glBegin(GL_POLYGON)
            glNormal3f(*n)
            for pt in pts:
                glVertex3f(*pt)
            glEnd()

            # Wireframe
            if is_pent:
                glColor4f(1.0, 0.41, 0.71, 0.8)
                glLineWidth(2.0)
            else:
                glColor4f(0.0, 0.7, 1.0, 0.3)
                glLineWidth(0.5)
            glBegin(GL_LINE_LOOP)
            for pt in pts:
                glVertex3f(*pt)
            glEnd()
        glEndList()

    def print_stats(self):
        inv = compute_invariants(self.faces)
        print(f"\n  Level {self.level}: {inv['F']} faces ({inv['P']}P + {inv['H']}H)")
        print(f"  V={inv['V']}  E={inv['E']}  chi={inv['chi']}  E/V={inv['EV']:.3f}")
        mem_est = sum(f['pts'].nbytes for f in self.faces)
        print(f"  Geometry RAM: {mem_est/1024:.1f} KB")
        print(f"  Flow RAM: {self.flow.pressure.nbytes/1024:.1f} KB")

    def refine(self, mode='all'):
        print(f"\n  Refining {'ALL' if mode=='all' else 'PENTS'}...")
        t0 = time.time()
        if mode == 'all':
            self.faces = refine_all(self.faces)
        else:
            self.faces = refine_pents(self.faces)
        self.level += 1
        dt = time.time() - t0
        print(f"  Refinement done in {dt:.2f}s → {len(self.faces)} faces")
        self.rebuild_flow()
        self.rebuild_display_list()
        self.print_stats()

    def draw_hud(self):
        """Render HUD text as 2D overlay."""
        inv = compute_invariants(self.faces)
        lines = [
            f"GENESIS GPU v1.0  |  PID: {PID}",
            f"",
            f"Level: {self.level}  |  Faces: {inv['F']:,}",
            f"P={inv['P']}  H={inv['H']:,}",
            f"V={inv['V']:,}  E={inv['E']:,}  chi={inv['chi']}",
            f"E/V = {inv['EV']:.3f}  |  phi = {PHI:.10f}",
            f"",
            f"FPS: {self.fps}  |  Flow steps: {self.flow.step:,}",
            f"Flow: {'ON' if self.flow.active else 'OFF'}  |  Spin: {'ON' if self.spinning else 'OFF'}",
            f"",
            f"[R] Refine All  [P] Refine Pents  [F] Flow",
            f"[SPACE] Spin    [ESC] Quit         [1-9] Level",
            f"",
            f"KILL: taskkill /PID {PID} /F",
        ]
        # Switch to 2D
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.W, self.H, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)

        y = 12
        for i, line in enumerate(lines):
            if not line: 
                y += 8
                continue
            font = self.font_big if i == 0 else self.font
            color = (0, 255, 200) if i == 0 else (150, 200, 220)
            surf = font.render(line, True, color)
            data = pygame.image.tostring(surf, 'RGBA', True)
            w, h = surf.get_size()

            glRasterPos2f(12, y + h)
            glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)
            y += h + 2

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_r:
                        self.refine('all')
                    elif event.key == K_p:
                        self.refine('pents')
                    elif event.key == K_f:
                        self.flow.active = not self.flow.active
                        print(f"  Flow: {'ON' if self.flow.active else 'OFF'}")
                    elif event.key == K_SPACE:
                        self.spinning = not self.spinning
                    elif event.key in range(K_1, K_9+1):
                        target = event.key - K_1 + 1
                        while self.level < target:
                            self.refine('all')
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.dragging = True
                        self.last_mouse = event.pos
                    elif event.button == 4:  # scroll up
                        self.zoom += 0.3
                    elif event.button == 5:  # scroll down
                        self.zoom -= 0.3
                elif event.type == MOUSEBUTTONUP:
                    self.dragging = False
                elif event.type == MOUSEMOTION:
                    if self.dragging:
                        dx = event.pos[0] - self.last_mouse[0]
                        dy = event.pos[1] - self.last_mouse[1]
                        self.rot_y += dx * 0.3
                        self.rot_x += dy * 0.3
                        self.last_mouse = event.pos
                elif event.type == VIDEORESIZE:
                    self.W, self.H = event.w, event.h
                    pygame.display.set_mode((self.W, self.H), DOUBLEBUF | OPENGL | RESIZABLE)

            # Spin
            if self.spinning:
                self.rot_y += 0.3

            # Flow
            if self.flow.active:
                for _ in range(3):
                    self.flow.step_flow()
                # Rebuild display list to update colors (every 10 frames)
                if self.frame_count % 10 == 0:
                    self.rebuild_display_list()

            # Draw
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # 3D projection
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45, self.W / max(self.H, 1), 0.1, 100.0)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslatef(0, 0, self.zoom)
            glRotatef(self.rot_x, 1, 0, 0)
            glRotatef(self.rot_y, 0, 1, 0)

            # Render polyhedron
            if self.display_list:
                glCallList(self.display_list)

            # HUD
            self.draw_hud()

            pygame.display.flip()

            # FPS
            self.frame_count += 1
            now = time.time()
            if now - self.last_fps_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_fps_time = now

            self.clock.tick(60)

        pygame.quit()
        print(f"\nGENESIS GPU — clean exit. PID {PID} done.")


# ============================================================================
#  MAIN
# ============================================================================
if __name__ == '__main__':
    print(f"\n  phi = {PHI}")
    print(f"  Building dodecahedron seed...")
    app = GenesisGPU()
    print(f"\n  READY. Press R to refine. No limits. Your GPU, your rules.")
    print(f"  KILL: taskkill /PID {PID} /F\n")
    app.run()

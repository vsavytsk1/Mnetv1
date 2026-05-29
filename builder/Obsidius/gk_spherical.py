"""
gk_spherical.py -- Spherical Coordinate Extension for Goldberg Kernel
======================================================================
Adds to navierKolmogorov.py / GoldbergKernel:

  cartesian_to_spherical(xyz)       -> (r, theta, phi)
  spherical_to_cartesian(r, t, p)   -> (x, y, z)
  face_centroids_spherical(faces)   -> array of (r, theta, phi) per face
  camera_from_outside(R, theta, phi)-> Unity camera position outside sphere
  
THE ONE FIX FOR UNITY:
  camera at z = -(R * 1.5)  outside the sphere
  looking at (0, 0, 0)
  chi=2 topology means the sphere IS closed
  camera must be OUTSIDE

  If camera is at (0,0,0) -> inside -> black screen
  If camera is at (0,0,-R*1.5) -> outside -> renders

Buenos Aires -- May 29 2026
Chapter 2 of the Algebraic Grimoire
"""
import math
import numpy as np

# ============================================================================
#  CONSTANTS
# ============================================================================
PHI = (1 + math.sqrt(5)) / 2
DEFAULT_R = 1.6   # GoldbergKernel default sphere radius

# ============================================================================
#  CARTESIAN <-> SPHERICAL
# ============================================================================
def cartesian_to_spherical(xyz):
    """
    Convert (x,y,z) cartesian to (r, theta, phi) spherical.
    
    theta = polar angle from +Y axis (0 = top, pi = bottom)
    phi   = azimuthal angle in XZ plane from +Z axis
    
    Unity convention:
      Y = up
      Z = forward
      X = right
    """
    x, y, z = xyz[0], xyz[1], xyz[2]
    r = math.sqrt(x*x + y*y + z*z)
    if r < 1e-12:
        return (0.0, 0.0, 0.0)
    theta = math.acos(max(-1.0, min(1.0, y / r)))   # polar (0 to pi)
    phi   = math.atan2(x, z)                          # azimuthal (-pi to pi)
    return (r, theta, phi)

def spherical_to_cartesian(r, theta, phi):
    """
    Convert (r, theta, phi) spherical to (x,y,z) cartesian.
    Unity convention (Y=up, Z=forward).
    """
    x = r * math.sin(theta) * math.sin(phi)
    y = r * math.cos(theta)
    z = r * math.sin(theta) * math.cos(phi)
    return (x, y, z)

def cartesian_to_spherical_batch(points):
    """
    Batch version for numpy arrays. points shape: (N, 3)
    Returns (r, theta, phi) each shape (N,)
    """
    x, y, z = points[:,0], points[:,1], points[:,2]
    r     = np.sqrt(x**2 + y**2 + z**2)
    r_safe = np.where(r < 1e-12, 1.0, r)
    theta = np.arccos(np.clip(y / r_safe, -1.0, 1.0))
    phi   = np.arctan2(x, z)
    return r, theta, phi

# ============================================================================
#  FACE UTILITIES
# ============================================================================
def face_centroids(faces):
    """
    Compute centroid of each face. Returns (N, 3) array.
    """
    centroids = np.array([face['pts'].mean(axis=0) for face in faces])
    return centroids

def face_centroids_spherical(faces):
    """
    Compute spherical coordinates of each face centroid.
    Returns dict with arrays: r, theta, phi, theta_deg, phi_deg
    """
    c = face_centroids(faces)
    r, theta, phi = cartesian_to_spherical_batch(c)
    return {
        'cartesian': c,
        'r':         r,
        'theta':     theta,        # radians, polar
        'phi':       phi,          # radians, azimuthal
        'theta_deg': np.degrees(theta),
        'phi_deg':   np.degrees(phi),
        'lat':       90.0 - np.degrees(theta),   # latitude (-90 to 90)
        'lon':       np.degrees(phi),             # longitude (-180 to 180)
    }

def find_pentagon_positions(faces):
    """
    Returns spherical coordinates of the 12 pentagons.
    Always 12. Always.
    """
    pent_faces  = [f for f in faces if f['type'] == 'pent']
    pent_coords = face_centroids_spherical(pent_faces)
    print(f"  Pentagon count: {len(pent_faces)}  (expect 12)")
    print(f"  Positions (lat, lon):")
    for i in range(len(pent_faces)):
        print(f"    P{i+1:02d}:  lat={pent_coords['lat'][i]:+7.2f}  lon={pent_coords['lon'][i]:+8.2f}")
    return pent_coords

# ============================================================================
#  CAMERA UTILITIES (THE UNITY FIX)
# ============================================================================
def camera_outside(sphere_r=DEFAULT_R, distance_factor=1.8,
                   theta=math.pi/2, phi=0.0):
    """
    Compute camera position OUTSIDE the sphere.
    
    THIS IS THE FIX:
      camera must be at r > sphere_r
      looking at (0,0,0)
      chi=2 sphere is closed -- camera inside = black screen
    
    Args:
        sphere_r:        radius of Goldberg sphere (default 1.6)
        distance_factor: how far outside (1.8 = 1.8x radius away)
        theta:           polar angle of camera (default equator = pi/2)
        phi:             azimuthal angle (default front = 0)
    
    Returns:
        dict with Unity camera setup
    """
    cam_r = sphere_r * distance_factor
    x, y, z = spherical_to_cartesian(cam_r, theta, phi)
    
    return {
        'position':  (x, y, z),
        'target':    (0.0, 0.0, 0.0),
        'distance':  cam_r,
        'sphere_r':  sphere_r,
        'factor':    distance_factor,
        'theta_deg': math.degrees(theta),
        'phi_deg':   math.degrees(phi),
        # Unity Camera component values:
        'unity_position': f"({x:.4f}, {y:.4f}, {z:.4f})",
        'unity_fov':      60.0,
        'unity_near':     0.01,
        'unity_far':      sphere_r * 20,
    }

def print_unity_camera_setup(sphere_r=DEFAULT_R):
    """
    Print the Unity camera setup for a Goldberg sphere.
    THE FIX for the VR black screen.
    """
    print("=" * 55)
    print("  UNITY CAMERA SETUP -- Goldberg Sphere")
    print("=" * 55)
    
    views = [
        ("FRONT",  math.pi/2, 0.0),
        ("BACK",   math.pi/2, math.pi),
        ("TOP",    0.1,       0.0),
        ("SIDE",   math.pi/2, math.pi/2),
        ("ORBIT",  math.pi/3, math.pi/6),
    ]
    
    for name, theta, phi in views:
        cam = camera_outside(sphere_r, 1.8, theta, phi)
        print(f"\n  {name}:")
        print(f"    Transform.position = {cam['unity_position']}")
        print(f"    Camera.fieldOfView  = {cam['unity_fov']}")
        print(f"    Camera.nearClipPlane = {cam['unity_near']}")
        print(f"    Camera.farClipPlane  = {cam['unity_far']:.2f}")
    
    print(f"\n  THE ONE NUMBER:")
    print(f"    sphere_r = {sphere_r}")
    print(f"    camera_z = -{sphere_r * 1.8:.4f}  (move camera HERE)")
    print(f"    lookAt   = (0, 0, 0)")
    print(f"\n  chi=2 = sphere is closed = camera MUST be outside")
    print(f"  chi=0 = Mobius = camera has no inside/outside")
    print(f"  That is why it mattered.")
    print("=" * 55)

# ============================================================================
#  OMEGA -> SPHERICAL FIELD (for VALE / Obsidius export)
# ============================================================================
def omega_to_spherical_field(omega, faces, xp=np):
    """
    Map vorticity field omega (per face) to spherical coordinates.
    Useful for VALE soul crystal export and Obsidius rendering.
    
    Returns array of (theta, phi, omega_value) for each face.
    """
    if hasattr(omega, 'get'):   # cupy
        omega_cpu = omega.get()
    else:
        omega_cpu = np.asarray(omega)
    
    coords = face_centroids_spherical(faces)
    
    return {
        'theta':   coords['theta'],
        'phi':     coords['phi'],
        'lat':     coords['lat'],
        'lon':     coords['lon'],
        'omega':   omega_cpu,
        'n_faces': len(faces),
    }

def export_soul_crystal_snapshot(engine, faces, step, nu):
    """
    Export a GKLedger block snapshot in spherical coordinates.
    This is the VALE soul crystal format.
    
    One block = one moment in your topological history.
    """
    import hashlib, json, time
    
    field = omega_to_spherical_field(engine.omega, faces)
    tke, enst, diss = engine.compute_diagnostics()
    
    # Build block data
    block = {
        'step':        step,
        'nu':          nu,
        'Re':          1.0 / nu,
        'faces':       len(faces),
        'pentagons':   sum(1 for f in faces if f['type'] == 'pent'),
        'chi':         2,
        'tke':         float(tke),
        'enstrophy':   float(enst),
        'dissipation': float(diss),
        'diss_over_enst': float(diss / max(enst, 1e-12)),
        'two_nu':      float(2 * nu),
        'timestamp':   time.strftime('%Y-%m-%dT%H:%M:%S'),
        'location':    'Buenos Aires',
        # Spherical field summary (not full omega -- too large)
        'omega_max':   float(np.max(np.abs(field['omega']))),
        'omega_mean':  float(np.mean(field['omega'])),
        'omega_std':   float(np.std(field['omega'])),
        # Pentagon positions
        'pent_lat':    [float(field['lat'][i]) for i,f in enumerate(faces) if f['type']=='pent'],
        'pent_lon':    [float(field['lon'][i]) for i,f in enumerate(faces) if f['type']=='pent'],
    }
    
    # Hash the block (Euler consensus mechanism)
    block_str = json.dumps(block, sort_keys=True)
    block['hash'] = hashlib.sha256(block_str.encode()).hexdigest()
    
    return block

# ============================================================================
#  QUICK TEST
# ============================================================================
if __name__ == '__main__':
    print("gk_spherical.py -- Spherical Coordinate Extension")
    print()
    
    # Test basic conversions
    xyz = (1.6, 0.0, 0.0)
    r, t, p = cartesian_to_spherical(xyz)
    back = spherical_to_cartesian(r, t, p)
    print(f"  cartesian -> spherical -> cartesian:")
    print(f"    in:  {xyz}")
    print(f"    sph: r={r:.4f}  theta={math.degrees(t):.2f}deg  phi={math.degrees(p):.2f}deg")
    print(f"    out: ({back[0]:.4f}, {back[1]:.4f}, {back[2]:.4f})")
    print()
    
    # Print Unity camera setup
    print_unity_camera_setup(sphere_r=1.6)
    print()
    
    # Build a small mesh and show pentagon positions
    print("  Building C60 to show pentagon positions...")
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from builder.navierKolmogorov import build_dodecahedron, refine_all
        faces = build_dodecahedron()
        faces = refine_all(faces)  # L1
        print(f"  L1: {len(faces)} faces")
        find_pentagon_positions(faces)
        print()
        print("  P=12. ALWAYS.")
        print("  chi=2. ALWAYS.")
        print("  Camera outside. ALWAYS.")
    except ImportError:
        print("  (run from MNetv1 root to test pentagon positions)")

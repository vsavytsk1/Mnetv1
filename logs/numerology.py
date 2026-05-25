"""
Is the steady-state residual a known constant?
Check v6 plateau (~2.05) and v6.1 convergence values against
every mathematical constant connected to icosahedral geometry.
"""
import math, json, os

# Golden ratio
phi = (1 + math.sqrt(5)) / 2  # 1.6180339887...

# Collect all actual residual endpoints from logs
all_res = {}
for folder in ['v6', 'v6.1', 'v6.2', 'v6.3']:
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder)
    if not os.path.isdir(d): continue
    vals = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.json'): continue
        fp = os.path.join(d, fn)
        if os.path.getsize(fp) < 1000: continue
        with open(fp) as f:
            obj = json.load(f)
        steps = [e for e in obj.get('data', []) if e['fn'] == 'STEP']
        if steps:
            vals.append(steps[-1]['d']['res'])
    if vals:
        all_res[folder] = vals

print("=" * 70)
print("  ACTUAL RESIDUAL ENDPOINTS")
print("=" * 70)
for folder, vals in all_res.items():
    avg = sum(vals) / len(vals)
    print(f"\n  {folder}: {len(vals)} runs, avg = {avg:.6f}")
    for v in vals:
        print(f"    {v:.8f}")

# v6 plateau average
if 'v6' in all_res:
    v6_avg = sum(all_res['v6']) / len(all_res['v6'])
    print(f"\n  v6 PLATEAU AVERAGE = {v6_avg:.8f}")

# Now check against EVERYTHING
print("\n" + "=" * 70)
print("  KNOWN CONSTANTS vs RESIDUAL VALUES")
print("=" * 70)

constants = {
    # Golden ratio family
    "phi (golden ratio)": phi,
    "1/phi": 1/phi,
    "phi^2": phi**2,
    "phi^2 - 1 (=phi)": phi**2 - 1,
    "2*phi": 2*phi,
    "2/phi": 2/phi,
    "phi/2": phi/2,
    "sqrt(phi)": math.sqrt(phi),
    "phi^3": phi**3,
    "1/phi^2": 1/phi**2,
    "1/phi^3": 1/phi**3,
    
    # Euler characteristic combos
    "chi = 2": 2,
    "chi + 1/12": 2 + 1/12,
    "chi + 1/20": 2 + 1/20,
    "chi + 1/32": 2 + 1/32,
    "chi + 1/60": 2 + 1/60,
    "chi + 1/90": 2 + 1/90,
    "chi * (1 + 1/40)": 2 * (1 + 1/40),
    
    # Icosahedral numbers
    "120/60 (H3/V)": 120/60,
    "120/58": 120/58,
    "90/44": 90/44,
    "32/12 (F/F5)": 32/12,
    "60/29": 60/29,
    
    # C60 topology ratios
    "V/E * chi (60/90*2)": 60/90*2,
    "E/F (90/32)": 90/32,
    "3V/2E (degree check)": 3*60/(2*90),
    "F5/F6 (12/20)": 12/20,
    
    # Pi combos
    "2/pi": 2/math.pi,
    "pi/phi": math.pi/phi,
    "4*pi/6 (sphere deficit)": 4*math.pi/6,
    "4*pi/V (curvature/vertex)": 4*math.pi/60,
    
    # sqrt combos  
    "sqrt(5)": math.sqrt(5),
    "sqrt(5) - 1": math.sqrt(5) - 1,
    "(sqrt(5)-1)/2 (1/phi)": (math.sqrt(5)-1)/2,
    "sqrt(2)": math.sqrt(2),
    "sqrt(3)": math.sqrt(3),
    
    # Coxeter numbers
    "2^3 * 3 * 5 / 60": (8*3*5)/60,
    "120/59": 120/59,
    "h=30 (Coxeter number H3)": 30,
    "1/h": 1/30,
    
    # Solid angles
    "4*pi/12 (per pentagon)": 4*math.pi/12,
    "4*pi/20 (per hexagon)": 4*math.pi/20,
    "720/360 (angle defect)": 720/360,
    "defect per vertex (720/60)": 720/60,
    "defect in rad (12deg)": math.radians(12),
    
    # Deep cuts
    "ln(phi)": math.log(phi),
    "exp(-phi)": math.exp(-phi),
    "phi * ln(2)": phi * math.log(2),
    "2 * ln(phi)": 2 * math.log(phi),
    "chi * phi / pi": 2 * phi / math.pi,
}

# For each version's average, find closest constants
for folder, vals in all_res.items():
    avg = sum(vals) / len(vals)
    print(f"\n--- {folder} avg = {avg:.8f} ---")
    
    dists = []
    for name, val in constants.items():
        dist = abs(avg - val)
        pct = dist / max(abs(avg), 1e-15) * 100
        dists.append((dist, pct, name, val))
    
    dists.sort()
    for dist, pct, name, val in dists[:8]:
        match = "★★★" if pct < 1 else ("★★" if pct < 5 else ("★" if pct < 10 else ""))
        print(f"  {pct:>6.2f}%  {name:>35s} = {val:.8f}  (delta={dist:.6f}) {match}")

# Special: check if v6 plateau IS chi + something topological
if 'v6' in all_res:
    v6_avg = sum(all_res['v6']) / len(all_res['v6'])
    excess = v6_avg - 2.0
    print(f"\n" + "=" * 70)
    print(f"  v6 PLATEAU EXCESS OVER chi=2:  {excess:.8f}")
    print(f"  = 1/{1/excess:.4f}")
    print(f"  12 * excess = {12*excess:.6f}")
    print(f"  60 * excess = {60*excess:.6f}")
    print(f"  90 * excess = {90*excess:.6f}")
    print(f"  excess * phi = {excess*phi:.6f}")
    print(f"  excess * 120 = {excess*120:.6f}")
    print(f"  excess^2 = {excess**2:.8f}")
    print(f"  1/(excess*phi) = {1/(excess*phi):.6f}")

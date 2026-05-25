"""Analyze cage log — what happens to the math when flow starts THEN cage applies"""
import json, os, math

fp = os.path.join(os.path.dirname(__file__), 'v5.3_cage', 'mnet_log_1779580742577.json')
sz = os.path.getsize(fp) / 1024 / 1024
print(f"=== {os.path.basename(fp)} ({sz:.1f} MB) ===")

with open(fp) as f:
    obj = json.load(f)

entries = obj.get('data', [])
print(f"  version:  {obj.get('version', '?')}")
print(f"  recorded: {obj.get('recorded', '?')}")
print(f"  Re:       {obj.get('Re', '?')}")
print(f"  entries:  {len(entries):,}")

# Count types
counts = {}
for e in entries:
    counts[e['fn']] = counts.get(e['fn'], 0) + 1
print("  types:")
for k in sorted(counts, key=lambda x: counts[x], reverse=True):
    print(f"    {k:12s} {counts[k]:>8,}")

# Time range
if entries:
    t0, t1 = entries[0]['t'], entries[-1]['t']
    print(f"  time: {t0}ms -> {t1}ms ({(t1-t0)/1000:.1f}s)")

# Extract M entries
m_entries = [e for e in entries if e['fn'] == 'M']
print(f"\n  M entries: {len(m_entries):,}")

if len(m_entries) < 10:
    print("  Not enough M entries to analyze")
    exit()

# Split into 5 time windows
n = len(m_entries)
windows = 5
wsize = n // windows

print("\n" + "=" * 65)
print("  TIME WINDOWS — energy & position evolution")
print("=" * 65)
print(f"  {'Window':>8} {'t(ms)':>10} {'avgE':>10} {'avgP':>10} {'maxR':>8} {'minR':>8}")
print("-" * 65)

for w in range(windows):
    start = w * wsize
    end = start + wsize
    chunk = m_entries[start:end]
    
    avg_e = sum(e['d']['E'] for e in chunk) / len(chunk)
    avg_p = sum(e['d']['p'] for e in chunk) / len(chunk)
    
    radii = []
    for e in chunk:
        pos = e['d']['pos']
        r = math.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
        radii.append(r)
    
    max_r = max(radii)
    min_r = min(radii)
    t_mid = chunk[len(chunk)//2]['t']
    
    contained = "OK" if max_r < 7 else "!!ESCAPED"
    print(f"  {w+1:>8} {t_mid:>10.1f} {avg_e:>10.3f} {avg_p:>10.3f} {max_r:>8.3f} {min_r:>8.3f} {contained}")

# Pressure extremes over full run
print("\n" + "=" * 65)
print("  PRESSURE EXTREMES")
print("=" * 65)
all_p = [(e['d']['p'], e['d']['id'], e['t']) for e in m_entries]
all_p.sort()
print(f"  min p: {all_p[0][0]:>12.3f}  (node {all_p[0][1]}, t={all_p[0][2]:.1f}ms)")
print(f"  max p: {all_p[-1][0]:>12.3f}  (node {all_p[-1][1]}, t={all_p[-1][2]:.1f}ms)")

# Energy extremes
all_e = [(e['d']['E'], e['d']['id'], e['t']) for e in m_entries]
all_e.sort()
print(f"\n  min E: {all_e[0][0]:>12.6f}  (node {all_e[0][1]}, t={all_e[0][2]:.1f}ms)")
print(f"  max E: {all_e[-1][0]:>12.6f}  (node {all_e[-1][1]}, t={all_e[-1][2]:.1f}ms)")

# gradP vs visc vs conv breakdown
print("\n" + "=" * 65)
print("  DOMINANT TERM BREAKDOWN")
print("=" * 65)
dom_counts = {"gradP": 0, "visc": 0, "conv": 0}
for e in m_entries:
    d = e['d']
    gp, vi, co = d['gP'], d['vi'], d['co']
    if gp >= vi and gp >= co:
        dom_counts["gradP"] += 1
    elif vi >= gp and vi >= co:
        dom_counts["visc"] += 1
    else:
        dom_counts["conv"] += 1

total = sum(dom_counts.values())
for k, v in sorted(dom_counts.items(), key=lambda x: -x[1]):
    pct = v / total * 100
    bar = "#" * int(pct / 2)
    print(f"  {k:>6}: {v:>8,} ({pct:>5.1f}%) {bar}")

# Position clustering — do nodes cluster at cage faces?
print("\n" + "=" * 65)
print("  CAGE FACE CLUSTERING — do nodes accumulate at the 12 faces?")
print("=" * 65)

# Dodecahedron face normals
phi = (1 + math.sqrt(5)) / 2
raw_normals = [
    [1,1,1],[1,1,-1],[1,-1,1],[1,-1,-1],
    [-1,1,1],[-1,1,-1],[-1,-1,1],[-1,-1,-1],
    [0,phi,1/phi],[0,phi,-1/phi],
    [0,-phi,1/phi],[0,-phi,-1/phi]
]
normals = []
for n in raw_normals:
    l = math.sqrt(sum(c**2 for c in n))
    normals.append([c/l for c in n])

# For late-stage M entries, find which cage face each node is closest to
late_m = m_entries[-wsize:]
face_counts = [0] * 12
for e in late_m:
    pos = e['d']['pos']
    r = math.sqrt(sum(c**2 for c in pos)) + 0.001
    norm_pos = [c/r for c in pos]
    
    best_face = 0
    best_dot = -999
    for fi, fn in enumerate(normals):
        dot = sum(a*b for a, b in zip(norm_pos, fn))
        if dot > best_dot:
            best_dot = dot
            best_face = fi
    face_counts[best_face] += 1

print("  Late-stage node distribution across 12 cage faces:")
total_late = sum(face_counts)
even = total_late / 12
for fi in range(12):
    pct = face_counts[fi] / total_late * 100
    deviation = (face_counts[fi] - even) / even * 100
    bar = "#" * int(pct)
    sign = "+" if deviation > 0 else ""
    print(f"  face {fi:>2}: {face_counts[fi]:>5} ({pct:>5.1f}%) {sign}{deviation:>5.1f}% from even  {bar}")

print("\n  If clustering occurs, some faces will have >> 8.3% (even split)")
max_pct = max(face_counts) / total_late * 100
min_pct = min(face_counts) / total_late * 100
print(f"  max face: {max_pct:.1f}%  min face: {min_pct:.1f}%  spread: {max_pct-min_pct:.1f}%")
if max_pct - min_pct > 5:
    print("  >>> CLUSTERING DETECTED — nodes accumulate at specific faces!")
else:
    print("  >>> EVEN DISTRIBUTION — no significant clustering")

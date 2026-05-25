"""
Analyze ALL v6 logs — is this random noise or a real method?
For each log: extract Re, N, residual trend, energy trend, dominant term
Then: cross-log statistics
"""
import json, os, math, csv, time

import sys
target = sys.argv[1] if len(sys.argv) > 1 else 'v6'
V6_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), target)
print(f'Analyzing: {target}')

# Gather all logs
logs = []
for fn in sorted(os.listdir(V6_DIR)):
    if not fn.endswith('.json'): continue
    fp = os.path.join(V6_DIR, fn)
    sz = os.path.getsize(fp)
    if sz < 1000: continue  # skip empty
    logs.append((fn, fp, sz))

print(f"Found {len(logs)} v6 logs ({sum(s for _,_,s in logs)/1024/1024:.0f} MB total)")
print("=" * 80)

# Analyze each
results = []
for fn, fp, sz in logs:
    with open(fp) as f:
        obj = json.load(f)
    
    entries = obj.get('data', [])
    if not entries: continue
    
    Re = obj.get('Re', '?')
    N = obj.get('nodes', '?')
    
    # Extract STEP entries (summary per step)
    steps = [e for e in entries if e['fn'] == 'STEP']
    # Extract M entries
    m_entries = [e for e in entries if e['fn'] == 'M']
    
    if not steps and not m_entries: continue
    
    # Residual evolution from STEP entries
    residuals = [s['d']['res'] for s in steps] if steps else []
    
    # If no STEP entries, estimate from M entries
    if not residuals and m_entries:
        # Group M by approximate time windows
        chunk_size = max(1, len(m_entries) // 20)
        for ci in range(0, len(m_entries), chunk_size):
            chunk = m_entries[ci:ci+chunk_size]
            avg_e = sum(e['d']['E'] for e in chunk) / max(len(chunk), 1)
            residuals.append(avg_e)
    
    if not residuals: continue
    
    # Metrics
    res_start = residuals[0] if residuals else 0
    res_end = residuals[-1] if residuals else 0
    res_min = min(residuals) if residuals else 0
    res_max = max(residuals) if residuals else 0
    
    # Trend: linear regression slope
    n_pts = len(residuals)
    if n_pts >= 2:
        x_mean = (n_pts - 1) / 2
        y_mean = sum(residuals) / n_pts
        num = sum((i - x_mean) * (residuals[i] - y_mean) for i in range(n_pts))
        den = sum((i - x_mean) ** 2 for i in range(n_pts))
        slope = num / den if den > 0 else 0
    else:
        slope = 0
    
    # Convergence ratio
    conv_ratio = res_start / max(res_end, 1e-15)
    
    # Dominant term from M entries
    dom = {"gP": 0, "vi": 0, "co": 0}
    for e in m_entries[:5000]:  # sample
        d = e['d']
        gp, vi, co = d.get('gP', 0), d.get('vi', 0), d.get('co', 0)
        if gp >= vi and gp >= co: dom["gP"] += 1
        elif vi >= gp and vi >= co: dom["vi"] += 1
        else: dom["co"] += 1
    
    total_dom = sum(dom.values()) or 1
    dom_pct = {k: v/total_dom*100 for k, v in dom.items()}
    
    # Pressure range
    p_vals = [e['d']['p'] for e in m_entries[:5000]]
    p_min = min(p_vals) if p_vals else 0
    p_max = max(p_vals) if p_vals else 0
    
    # Position radius
    r_vals = [math.sqrt(sum(c**2 for c in e['d']['pos'])) for e in m_entries[:5000]]
    r_max = max(r_vals) if r_vals else 0
    r_min = min(r_vals) if r_vals else 0
    
    result = {
        'file': fn, 'Re': Re, 'N': N, 'entries': len(entries),
        'steps': len(steps), 'm_entries': len(m_entries),
        'res_start': res_start, 'res_end': res_end,
        'res_min': res_min, 'res_max': res_max,
        'slope': slope, 'conv_ratio': conv_ratio,
        'dom_gP': dom_pct.get('gP', 0), 'dom_vi': dom_pct.get('vi', 0), 'dom_co': dom_pct.get('co', 0),
        'p_min': p_min, 'p_max': p_max, 'r_min': r_min, 'r_max': r_max,
        'residuals': residuals  # keep for dashboard
    }
    results.append(result)
    
    # Verdict
    if conv_ratio > 1.1:
        verdict = "CONVERGING"
    elif conv_ratio < 0.9:
        verdict = "DIVERGING"
    else:
        verdict = "STEADY"
    
    contained = "YES" if r_max < 10 else "NO (r={:.0f})".format(r_max)
    
    print(f"\n--- {fn} ---")
    print(f"  Re={Re}  N={N}  entries={len(entries):,}  steps={len(steps)}")
    print(f"  residual: {res_start:.4f} -> {res_end:.4f}  (ratio={conv_ratio:.2f}x)  slope={slope:.4f}")
    print(f"  pressure: [{p_min:.1f}, {p_max:.1f}]")
    print(f"  radius:   [{r_min:.2f}, {r_max:.2f}]  contained={contained}")
    print(f"  dominant:  gradP={dom_pct.get('gP',0):.0f}%  visc={dom_pct.get('vi',0):.0f}%  conv={dom_pct.get('co',0):.0f}%")
    print(f"  verdict:   {verdict}")

# ═══════════════════════════════════════════════════════
# AGGREGATE STATISTICS
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("AGGREGATE — IS THIS RANDOM NOISE OR A REAL METHOD?")
print("=" * 80)

if not results:
    print("No valid results!")
    exit()

n_conv = sum(1 for r in results if r['conv_ratio'] > 1.1)
n_div = sum(1 for r in results if r['conv_ratio'] < 0.9)
n_steady = len(results) - n_conv - n_div

print(f"\n  Total runs:     {len(results)}")
print(f"  CONVERGING:     {n_conv} ({n_conv/len(results)*100:.0f}%)")
print(f"  STEADY:         {n_steady} ({n_steady/len(results)*100:.0f}%)")
print(f"  DIVERGING:      {n_div} ({n_div/len(results)*100:.0f}%)")

avg_ratio = sum(r['conv_ratio'] for r in results) / len(results)
avg_slope = sum(r['slope'] for r in results) / len(results)
avg_gP = sum(r['dom_gP'] for r in results) / len(results)

print(f"\n  Avg conv ratio: {avg_ratio:.2f}x")
print(f"  Avg slope:      {avg_slope:.4f}")
print(f"  Avg gradP dom:  {avg_gP:.0f}%")

contained = sum(1 for r in results if r['r_max'] < 10)
print(f"  Contained:      {contained}/{len(results)}")

# Key question: does MORE nodes = LOWER residual?
by_N = sorted(results, key=lambda r: r['N'] if isinstance(r['N'], int) else 0)
print(f"\n  BY NODE COUNT:")
for r in by_N[:5]:
    print(f"    N={r['N']:>5}  res_end={r['res_end']:.4f}  conv_ratio={r['conv_ratio']:.2f}")
print("    ...")
for r in by_N[-3:]:
    print(f"    N={r['N']:>5}  res_end={r['res_end']:.4f}  conv_ratio={r['conv_ratio']:.2f}")

# Final verdict
print("\n" + "=" * 80)
if n_conv > n_div and avg_ratio > 1.0:
    print("VERDICT: MORE RUNS CONVERGE THAN DIVERGE.")
    print("         Average convergence ratio > 1.0")
    print("         THIS IS NOT RANDOM NOISE.")
    if avg_gP > 90:
        print("         WARNING: gradP dominates (>90%) — pressure solver needs work")
        print("         The METHOD works. The NUMERICS need stabilization.")
else:
    print("VERDICT: INCONCLUSIVE or DIVERGENT.")
    print("         Need better pressure solver or lower Re.")
print("=" * 80)

# Save CSV summary
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v6_analysis.csv')
with open(csv_path, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['file','Re','N','entries','res_start','res_end',
        'conv_ratio','slope','dom_gP','dom_vi','dom_co','p_min','p_max','r_max','verdict'])
    w.writeheader()
    for r in results:
        row = {k: r[k] for k in w.fieldnames if k in r}
        row['verdict'] = 'CONV' if r['conv_ratio']>1.1 else ('DIV' if r['conv_ratio']<0.9 else 'STEADY')
        for k in ['res_start','res_end','slope','dom_gP','dom_vi','dom_co','p_min','p_max','r_max']:
            if k in row and isinstance(row[k], float):
                row[k] = f"{row[k]:.4f}"
        row['conv_ratio'] = f"{r['conv_ratio']:.2f}"
        w.writerow(row)
print(f"\nCSV saved: {csv_path}")

# Save residual curves as JSON for dashboard
dash_data = []
for r in results:
    dash_data.append({
        'file': r['file'], 'Re': r['Re'], 'N': r['N'],
        'conv_ratio': round(r['conv_ratio'], 3),
        'residuals': [round(x, 6) for x in r['residuals'][:200]]  # cap for size
    })
dash_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v6_dashboard_data.json')
with open(dash_path, 'w') as f:
    json.dump(dash_data, f)
print(f"Dashboard data saved: {dash_path}")

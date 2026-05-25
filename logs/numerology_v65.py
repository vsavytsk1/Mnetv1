import math
phi = (1 + math.sqrt(5)) / 2

vals = [0.0153, 0.0056, 0.0019, 0.0006, 0.0015, 0.0004, 0.0211]
conv = [v for v in vals if v < 0.002]
avg_all = sum(vals)/len(vals)
avg_conv = sum(conv)/len(conv) if conv else 0

print("ALL 7 runs:")
for v in sorted(vals):
    print(f"  {v:.6f}")
print(f"  avg all = {avg_all:.6f}")
print(f"  avg converging ({len(conv)}) = {avg_conv:.6f}")

print("\n=== NUMEROLOGY CHECK ===")
targets = {
    "avg converging": avg_conv,
    "best run (0.0004)": 0.0004,
    "second best (0.0006)": 0.0006,
    "third (0.0015)": 0.0015,
    "fourth (0.0019)": 0.0019,
}

consts = {
    "1/(120*phi^2)": 1/(120*phi**2),
    "1/(60*phi^3)": 1/(60*phi**3),
    "1/(120*phi^3)": 1/(120*phi**3),
    "1/(90*phi^2)": 1/(90*phi**2),
    "1/(V*E)=1/5400": 1/5400,
    "1/(2*V*F5)=1/1440": 1/1440,
    "1/(H3*phi)=1/194": 1/(120*phi),
    "chi/(V*E)=2/5400": 2/5400,
    "1/phi^7": 1/phi**7,
    "1/phi^8": 1/phi**8,
    "exp(-phi^3)": math.exp(-phi**3),
    "1/(V*phi)": 1/(60*phi),
    "4pi/V^2": 4*math.pi/(60**2),
    "chi/V^2=2/3600": 2/(60**2),
    "1/(F*E)=1/2880": 1/2880,
    "F5/(V*E)=12/5400": 12/5400,
    "1/(h*E)=1/2700": 1/2700,
    "1/(h*V)=1/1800": 1/1800,
    "1/(h*phi^2)": 1/(30*phi**2),
    "1/(h*phi^3)": 1/(30*phi**3),
    "1/(h*F)=1/960": 1/960,
    "1/2618 (phi^3*1000)": 1/(phi**3*1000),
    "F5/H3=12/120=0.1": 12/120,
    "1/phi^5": 1/phi**5,
    "1/phi^6": 1/phi**6,
    "pi/(V*E)": math.pi/5400,
    "1/(phi^4*60)": 1/(phi**4*60),
    "1/(phi^4*120)": 1/(phi**4*120),
    "1/(phi^5*12)": 1/(phi**5*12),
    "chi*pi/V^2": 2*math.pi/3600,
    "sqrt(5)/V^2": math.sqrt(5)/3600,
    "1/(phi^3*90)": 1/(phi**3*90),
    "1/2500": 1/2500,
    "1/1618 (=1/1000phi)": 1/(1000*phi),
    "defect/(V*h)": (math.radians(12))/(60*30),
}

for tname, tval in targets.items():
    print(f"\n--- {tname} = {tval:.8f} ---")
    dists = []
    for name, val in consts.items():
        pct = abs(tval - val) / max(tval, 1e-15) * 100
        dists.append((pct, name, val))
    dists.sort()
    for pct, name, val in dists[:6]:
        star = "***" if pct < 3 else ("**" if pct < 10 else ("*" if pct < 25 else ""))
        print(f"  {pct:>7.2f}%  {name:>30s} = {val:.8f}  {star}")

print("\n=== CLUSTER ANALYSIS ===")
print(f"Converging values: {sorted(conv)}")
if len(conv) >= 2:
    sconv = sorted(conv)
    for i in range(len(sconv)-1):
        r = sconv[i+1]/max(sconv[i], 1e-15)
        rphi = abs(r - phi)/phi * 100
        print(f"  {sconv[i]:.6f} -> {sconv[i+1]:.6f}  ratio={r:.4f}  (phi={rphi:.1f}% off)")

print("\n=== THE BIG TABLE (all 5 generations) ===")
gens = {
    "v6": {"avg": 1.9675, "best": 2.02, "note": "plateau at chi-1/h"},
    "v6.1": {"avg": 0.00107, "best": 0.0004, "note": "80% converging"},
    "v6.2": {"avg": 0.01132, "best": 0.0003, "note": "deepest single"},
    "v6.3": {"avg": 0.01561, "best": 0.0058, "note": "too aggressive"},
    "v6.5": {"avg": avg_conv, "best": 0.0004, "note": "v6.1 solver, fresh"},
}
print(f"{'Gen':>6s} {'Avg Res':>12s} {'Best':>10s} {'Closest Const':>30s} {'Match%':>8s}")
for g, d in gens.items():
    # find closest constant to best
    best_match = min(consts.items(), key=lambda x: abs(d["best"] - x[1]))
    pct = abs(d["best"] - best_match[1]) / max(d["best"], 1e-15) * 100
    print(f"{g:>6s} {d['avg']:>12.6f} {d['best']:>10.6f} {best_match[0]:>30s} {pct:>7.1f}%")

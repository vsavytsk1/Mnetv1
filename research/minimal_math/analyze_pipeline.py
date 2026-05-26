import json, os, glob

d = r'C:\Users\vladi\Downloads\g_v1.5_expt'
files = os.listdir(d)

# Load all METAs
metas = sorted([f for f in files if 'META' in f])
print("=== METAS ===")
for mf in metas:
    m = json.load(open(os.path.join(d, mf)))
    print(f"  {mf}: chunks={m.get('totalChunks','?')} entries={m.get('totalEntries','?')} gens={m.get('totalGens','?')} V={m.get('finalV','?')} E={m.get('finalE','?')}")
    if 'discoveries' in m:
        print(f"    discoveries: {len(m['discoveries'])}")

# Load all chunks, aggregate entries
chunks = sorted([f for f in files if '_c0' in f])
all_entries = []
print(f"\n=== {len(chunks)} CHUNKS ===")
for cf in chunks:
    c = json.load(open(os.path.join(d, cf)))
    entries = c.get('entries', [])
    all_entries.extend(entries)
    print(f"  {cf}: {len(entries)} entries, gen={c.get('genEnd','?')}")

print(f"\nTotal entries: {len(all_entries)}")

# Analyze operations distribution
ops = {}
disc_timeline = []
for e in all_entries:
    op = str(e.get('op', ''))
    if op.startswith('P'):
        key = op.split(':')[0] + ':' + op.split(':')[1].split(' ')[0] if ':' in op else op[:6]
        ops[key] = ops.get(key, 0) + 1
    if op == 'DISC' or 'DISC' in op:
        disc_timeline.append((e.get('g', 0), e.get('d', {}).get('s', '?')))

print("\n=== OPERATION DISTRIBUTION ===")
for k, v in sorted(ops.items(), key=lambda x: -x[1]):
    pct = v / len(all_entries) * 100
    bar = '#' * int(pct)
    print(f"  {k:20s} {v:5d}  {pct:5.1f}%  {bar}")

print(f"\n=== DISCOVERY TIMELINE ({len(disc_timeline)} discoveries) ===")
for g, s in disc_timeline[:30]:
    print(f"  gen {g:5d}: {s}")
if len(disc_timeline) > 30:
    print(f"  ... {len(disc_timeline)-30} more")

# Load graph snapshots
graphs = sorted([f for f in files if 'graph_g' in f])
print(f"\n=== GRAPH SNAPSHOTS ===")
for gf in graphs:
    g = json.load(open(os.path.join(d, gf)))
    n = len(g.get('nodes', []))
    e = len(g.get('edges', []))
    s = g.get('stats', {})
    print(f"  {gf}:")
    print(f"    V={n} E={e} comp={s.get('components','?')} maxDeg={s.get('maxDeg','?')} sym={s.get('sym','?')}")

# Load snapshots for growth curve
snaps = sorted([f for f in files if 'snapFINAL' in f])
print(f"\n=== GROWTH CURVE (from {len(snaps)} snapshot files) ===")
all_snaps = []
for sf in snaps:
    sdata = json.load(open(os.path.join(d, sf)))
    for snap in sdata.get('snapshots', []):
        all_snaps.append(snap)

all_snaps.sort(key=lambda x: x.get('g', 0))
print(f"  Total snapshots: {len(all_snaps)}")
for snap in all_snaps[:10]:
    print(f"  gen {snap['g']:5d}: V={snap['V']:4d} E={snap['E']:4d} disc={len(snap.get('discoveries',[]))}")
if len(all_snaps) > 10:
    # Show every 10th
    for snap in all_snaps[10::max(1,len(all_snaps)//10)]:
        print(f"  gen {snap['g']:5d}: V={snap['V']:4d} E={snap['E']:4d} disc={len(snap.get('discoveries',[]))}")

# Edge/Vertex ratio over time
print(f"\n=== E/V RATIO EVOLUTION ===")
for snap in all_snaps[::max(1,len(all_snaps)//15)]:
    ratio = snap['E'] / max(1, snap['V'])
    bar = '|' * int(ratio * 10)
    print(f"  gen {snap['g']:5d}: E/V = {ratio:.2f}  {bar}")

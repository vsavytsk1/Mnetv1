import json, os, sys


d = os.path.join(os.path.dirname(__file__), 'v5.1_cage')
for fn in sorted(os.listdir(d)):
    if not fn.endswith('.json'):
        continue
    fp = os.path.join(d, fn)
    sz = os.path.getsize(fp) / 1024 / 1024
    print(f"=== {fn} ({sz:.1f} MB) ===")

    with open(fp, 'r') as f:
        obj = json.load(f)

    entries = obj.get('data', [])
    print(f"  version:  {obj.get('version', '?')}")
    print(f"  recorded: {obj.get('recorded', '?')}")
    print(f"  Re:       {obj.get('Re', '?')}")
    print(f"  entries:  {len(entries):,}")

    # Count by type
    counts = {}
    for e in entries:
        t = e.get('fn', '?')
        counts[t] = counts.get(t, 0) + 1
    print("  types:")
    for k in sorted(counts, key=lambda x: counts[x], reverse=True):
        print(f"    {k:12s} {counts[k]:>8,}")

    # Time range
    if entries:
        t0 = entries[0]['t']
        t1 = entries[-1]['t']
        dur = (t1 - t0) / 1000
        print(f"  time: {t0}ms -> {t1}ms ({dur:.1f}s)")

        fn0 = entries[0]['fn']
        fn1 = entries[-1]['fn']
        d0 = str(entries[0]['d'])[:120]
        d1 = str(entries[-1]['d'])[:120]
        print(f"  first: [{t0}ms] {fn0}: {d0}")
        print(f"  last:  [{t1}ms] {fn1}: {d1}")

    # Sample one M entry (momentum)
    m_entries = [e for e in entries if e['fn'] == 'M']
    if m_entries:
        sample = m_entries[len(m_entries)//2]  # middle entry
        print(f"  sample M (node {sample['d'].get('id','?')}):")
        for k, v in sample['d'].items():
            print(f"    {k}: {v}")

    print()

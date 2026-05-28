"""
_patch_h7_1473_12_60_2.py
==========================
Finish the try/catch around M7_JS.
Previous patch got 3/4 — this nails the last one.
Strategy: find the line by landmark, not by exact dash count.
"""
import time
from pathlib import Path

SRC_FILE = Path(__file__).parent / "build_holly7.py"
src = SRC_FILE.read_text(encoding="utf-8")

# ── Print the exact line that contains M7_JS so we can see it ───────────
print("=== SCANNING FOR M7_JS LINE ===")
for i, line in enumerate(src.splitlines()):
    if "M7_JS" in line or "MATH TREE ENGINE" in line:
        print(f"  line {i:4d}: {repr(line)}")

# ── Find and replace by landmark (not exact dashes) ─────────────────────
# Look for the block:  any line with MATH TREE ENGINE + next line with {M7_JS}
import re

pattern = r'([ \t]*// \u2500\u2500 MATH TREE ENGINE \([^)]+\) \u2500+\n[ \t]*\{M7_JS\})'

match = re.search(pattern, src)
if match:
    old_block = match.group(1)
    print(f"\n=== FOUND ===\n{repr(old_block)}\n")

    # Build replacement — preserve leading whitespace
    indent = re.match(r'^([ \t]*)', old_block).group(1)
    new_block = (
        f"{indent}// \u2500\u2500 MATH TREE ENGINE (isolated \u2014 DOM hooks neutralised) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
        f"{indent}// Tree JS may addEventListener on nodes only in its own HTML.\n"
        f"{indent}// try/catch isolates it \u2014 kernel M1-M6 above are unaffected.\n"
        f"{indent}try {{\n"
        f"{indent}{{M7_JS}}\n"
        f"{indent}}} catch(e) {{ console.warn('[H7] tree init:', e.message); }}"
    )
    src = src.replace(old_block, new_block)
    print("=== REPLACED ===")
    print(f"try/catch: {'OK' if 'try {{' in src else 'MISSING'}")
else:
    print("\n=== NOT FOUND — printing 10 lines around M7_JS ===")
    lines = src.splitlines()
    for i, line in enumerate(lines):
        if "{M7_JS}" in line:
            start = max(0, i-3)
            end   = min(len(lines), i+3)
            for j in range(start, end):
                print(f"  {j:4d}: {repr(lines[j])}")

SRC_FILE.write_text(src, encoding="utf-8")
print(f"\nDone. {len(src)} chars")
print("Run: python pack/build_holly7.py --no-open")

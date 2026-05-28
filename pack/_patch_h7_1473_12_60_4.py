"""
_patch_h7_1473_12_60_4.py  — DIAGNOSTIC + FIX
Print lines 870-882 exact repr, then fix whatever is there.
"""
from pathlib import Path

SRC_FILE = Path(__file__).parent / "build_holly7.py"
src = SRC_FILE.read_text(encoding="utf-8")
lines = src.splitlines(keepends=True)

print("=== lines 868-885 exact repr ===")
for i in range(868, min(886, len(lines))):
    print(f"{i:4d}: {repr(lines[i])}")

# Find EVERY line that contains M7_JS or TREE ENGINE
print("\n=== ALL M7_JS / TREE ENGINE lines ===")
for i, line in enumerate(lines):
    if "M7_JS" in line or "TREE ENGINE" in line:
        print(f"{i:4d}: {repr(line)}")

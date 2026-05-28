"""
_patch_h7_1473_12_60_5.py
==========================
Fix f-string brace escaping on lines 877-879.
try { and } inside an f-string must be {{ and }}.
Diagnostic confirmed: lines are there but with single braces.
"""
from pathlib import Path

SRC_FILE = Path(__file__).parent / "build_holly7.py"
src = SRC_FILE.read_text(encoding="utf-8")

# Exact strings from diagnostic (single braces — wrong inside f-string)
OLD = ("try {\n"
       "{M7_JS}\n"
       "} catch(e) { console.warn('[H7] tree init:', e.message); }")

NEW = ("try {{\n"
       "  {{M7_JS}}\n"
       "  }} catch(e) {{ console.warn('[H7] tree init:', e.message); }}")

print("OLD in src:", OLD in src)
if OLD in src:
    src = src.replace(OLD, NEW)
    print("FIXED — braces now properly escaped for f-string")
else:
    # Try alternate spacing
    OLD2 = "try {\n{M7_JS}\n} catch(e) { console.warn('[H7] tree init:', e.message); }"
    print("ALT OLD in src:", OLD2 in src)
    lines = src.splitlines(keepends=True)
    for i,l in enumerate(lines):
        if "try {" in l and "try {{" not in l:
            print(f"  found at line {i}: {repr(l)}")
        if "catch(e)" in l and "}}" not in l:
            print(f"  catch at line {i}: {repr(l)}")

SRC_FILE.write_text(src, encoding="utf-8")
print(f"Size: {len(src)} chars")
print("try {{ in src:", "try {{" in src)

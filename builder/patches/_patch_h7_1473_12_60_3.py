"""
_patch_h7_1473_12_60_3.py
==========================
try/catch around M7_JS — final attempt.
Previous patch: found it, replaced it, but 'try {{' check failed.
Reason: the replacement uses {{M7_JS}} which in the f-string context
becomes {M7_JS} — so we check for the RIGHT string after expansion.
Also: the line has NO leading indent (line 874 = no spaces before //).
We simply do a direct string replace on the exact repr we saw.
"""
import time
from pathlib import Path

SRC_FILE = Path(__file__).parent / "build_holly7.py"
src = SRC_FILE.read_text(encoding="utf-8")

# Exact string from the scan (no indent, exact dashes from repr output)
OLD = '// \u2500\u2500 MATH TREE ENGINE (v2.6) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n{M7_JS}'

# Note: in the f-string, {{ becomes { and }} becomes }
# So we write {{ and }} here to get literal { } in the output HTML
NEW = ('// \u2500\u2500 MATH TREE ENGINE (isolated \u2014 DOM hooks neutralised) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
       '  // Tree JS may addEventListener on nodes only in its standalone HTML.\n'
       '  // Wrapped in try/catch \u2014 kernel M1-M6 are never affected.\n'
       '  try {{\n'
       '  {M7_JS}\n'
       '  }} catch(e) {{ console.warn(\'[H7] tree:\', e.message); }}')

print("OLD in src:", OLD in src)

if OLD in src:
    src = src.replace(OLD, NEW)
    print("REPLACED OK")
    # Verify: the output f-string will have try { not try {{ 
    # (because {{ escapes to { in f-strings)
    # So check for try {{ in the Python source
    print("try {{ in src:", "try {{" in src)
else:
    # Count exact dashes
    import re
    m = re.search(r'MATH TREE ENGINE \(v2\.6\) (\u2500+)', src)
    if m:
        dashes = m.group(1)
        print(f"Actual dash count: {len(dashes)}")
        print(f"Actual chars: {repr(dashes[:5])}")
    print("Fallback: replacing by line number")
    lines = src.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if 'MATH TREE ENGINE' in line and 'v2.6' in line:
            print(f"Line {i}: {repr(line.rstrip())}")
            # Replace this line + next {M7_JS} line
            if i+1 < len(lines) and '{M7_JS}' in lines[i+1]:
                lines[i]   = ('  // \u2500\u2500 MATH TREE ENGINE (isolated \u2014 DOM hooks neutralised) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
                              '  // Tree JS addEventListener only in its own HTML. try/catch isolates it.\n')
                lines[i+1] = ('  try {{\n'
                              '  {M7_JS}\n'
                              '  }} catch(e) {{ console.warn(\'[H7] tree:\', e.message); }}\n')
                src = ''.join(lines)
                print("LINE REPLACE OK")
                print("try {{ in src:", "try {{" in src)
            break

SRC_FILE.write_text(src, encoding="utf-8")
print(f"Final size: {len(src)} chars")
print("Run: python pack/build_holly7.py --no-open")

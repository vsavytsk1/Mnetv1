"""One-shot patch for build_holly7.py — run once then delete."""
import shutil, time
from pathlib import Path

f   = Path(__file__).parent / "build_holly7.py"
src = f.read_text(encoding="utf-8")
orig_len = len(src)

# ── Fix 1: _h7panels (guard against math-tree collision) ──────────────────
src = src.replace(
    "var panels = ['home','sar','ns','nc','tree','kernel'];\nfunction showPanel(id){\n  panels.forEach(function(p){",
    "var _h7panels = ['home','sar','ns','nc','tree','kernel'];\nfunction showPanel(id){\n  _h7panels.forEach(function(p){"
)
src = src.replace(
    "  if(id==='tree') mountTree();\n}",
    "  if(id==='tree') mountTree();\n}\nvar panels = _h7panels; // guard: math-tree may redefine 'panels'"
)

# ── Fix 2: wrap M7 in try/catch ─────────────────────────────────────────
# Find the exact marker and replace it
import re as _re
OLD_M7_PAT = r'// ── MATH TREE ENGINE \(v2\.6\) ─+\n  \{M7_JS\}'
NEW_M7  = ("// ── MATH TREE ENGINE (isolated — DOM hooks neutralised) ────────────\n"
           "  // Tree engine may call addEventListener on nodes that only exist\n"
           "  // in its standalone HTML. Wrapped so kernel modules are never affected.\n"
           "  try {{\n"
           "  {M7_JS}\n"
           "  }} catch(e) {{ console.warn('[H7] tree init caught:', e.message); }}")
src = src.replace(OLD_M7, NEW_M7)

# ── Fix 3: versioning + hexCompTest archive in the assemble footer ─────
OLD_FOOTER = ('OUT.write_text(html, encoding="utf-8")\n'
              'size_kb = len(html) // 1024\n'
              'print(f"\\n  ✓ Written: {OUT}")\n'
              'print(f"  Size: {size_kb} KB")\n'
              'print(f"  Build: {BUILD_NO}")')

NEW_FOOTER = r'''OUT.write_text(html, encoding="utf-8")
size_kb = len(html) // 1024

# ── Archive to hexCompTest (every build, forever) ──────────────────────────
HEX_ARCHIVE = PACK / "hexCompTest"
HEX_ARCHIVE.mkdir(parents=True, exist_ok=True)
existing    = sorted(HEX_ARCHIVE.glob("H7_*.html"))
H7_BUILD_N  = len(existing) + 1
aname = (f"H7_{H7_MAJOR}.{H7_MINOR}.{H7_PATCH}.{H7_BUILD_N}"
         f"__{time.strftime('%Y%m%d_%H%M%S')}.html")
apath = HEX_ARCHIVE / aname
shutil.copy2(OUT, apath)

# ── hexCompTest INDEX ──────────────────────────────────────────────────────
all_b = sorted(HEX_ARCHIVE.glob("H7_*.html"))
idx   = [
    "# hexCompTest — HOLLY-7 build archive",
    "# KERNEL IS ABSOLUTE. Every build here. None deleted.",
    f"# {len(all_b)} builds total", "",
]
for b in all_b:
    idx.append(f"{b.name:<72} {b.stat().st_size // 1024}KB")
(HEX_ARCHIVE / "INDEX.txt").write_text("\n".join(idx), encoding="utf-8")

print(f"\n  ✓ Written:  {OUT}")
print(f"  ✓ Archived: {aname}")
print(f"  ✓ Index:    hexCompTest/INDEX.txt  ({len(all_b)} builds total)")
print(f"  Size:  {size_kb} KB")
print(f"  Build: {VERSION}")'''

src = src.replace(OLD_FOOTER, NEW_FOOTER)

# ── Fix 4: add shutil to imports ───────────────────────────────────────────
src = src.replace(
    "import os, sys, re, time, webbrowser",
    "import os, sys, re, time, shutil, webbrowser"
)

# ── Report ─────────────────────────────────────────────────────────────────
f.write_text(src, encoding="utf-8")
print(f"Original: {orig_len} chars  →  Patched: {len(src)} chars")
print(f"Fix 1 (_h7panels):   {'OK' if '_h7panels' in src else 'MISSING'}")
print(f"Fix 2 (try/catch):   {'OK' if 'try {{' in src else 'MISSING'}")
print(f"Fix 3 (hexCompTest): {'OK' if 'hexCompTest' in src else 'MISSING'}")
print(f"Fix 4 (shutil):      {'OK' if 'import os, sys, re, time, shutil' in src else 'MISSING'}")
print("PATCH DONE — delete _patch_holly7.py")

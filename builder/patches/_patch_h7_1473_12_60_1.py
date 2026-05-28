"""
_patch_h7_1473_12_60_1.py
==========================
Patch build_holly7.py to H7.1473.12.60 standard.

FIXES:
  1. try/catch around M7 (math tree DOM hooks crash in holly7 context)
  2. double 'var panels' alias — remove duplicate
  3. Version constants → H7_MAJOR=1473, H7_MINOR=12, H7_PATCH=60
  4. Per-build .log file in hexCompTest/ alongside .html

LOG FORMAT (per build):
  hexCompTest/H7_1473.12.60.N__YYYYMMDD_HHMMSS.log
  Contains: version, timestamp, modules+sizes, kernel checksums,
            build time ms, output size, warnings, git hash if available.

Keep this file. It IS the record of this change.
Version: H7.1473.12.60.1__patch
"""
import re, hashlib, time
from pathlib import Path

SRC_FILE = Path(__file__).parent / "build_holly7.py"
src = SRC_FILE.read_text(encoding="utf-8")
orig = src  # keep original for diff report

fixes = []

# ── FIX 1: version constants → H7.1473.12.60 ────────────────────────────
src = src.replace(
    "H7_MAJOR = 7\nH7_MINOR = 1    # bump when adding a module\nH7_PATCH = 0    # bump for fixes",
    "H7_MAJOR = 1473  # λ̃ = 0.1473  SAR-5 spectral invariant — THE number\nH7_MINOR = 12    # P=12 pentagons — Euler forces it, never changes\nH7_PATCH = 60    # C60 seed — where everything starts"
)
fixes.append(("version constants", "H7_MAJOR = 1473" in src))

# ── FIX 2: remove duplicate 'var panels' alias ──────────────────────────
src = src.replace(
    "var panels = _h7panels; // guard: math-tree may redefine 'panels'\n// alias for safety\nvar panels = _h7panels;",
    "var panels = _h7panels; // guard: math-tree may redefine 'panels'"
)
fixes.append(("duplicate alias", src.count("var panels = _h7panels;") == 1))

# ── FIX 3: try/catch around M7_JS injection ─────────────────────────────
# The exact line in the f-string (using regex to handle dash count variance)
src = re.sub(
    r'(  // \u2500\u2500 MATH TREE ENGINE \(v2\.6\) \u2500+\n  \{M7_JS\})',
    ('  // \u2500\u2500 MATH TREE ENGINE (isolated \u2014 DOM hooks neutralised) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
     '  // Tree JS may addEventListener on nodes that only exist in its own HTML.\n'
     '  // try/catch isolates it \u2014 kernel modules M1-M6 above are never affected.\n'
     '  try {{\n'
     '  {{M7_JS}}\n'
     '  }} catch(e) {{ console.warn(\'[H7] tree init:\', e.message); }}'),
    src
)
fixes.append(("try/catch M7", "try {{\n  {{M7_JS}}" in src or "try {{\n  {M7_JS}" in src))

# ── FIX 4: per-build .log file in hexCompTest ───────────────────────────
LOG_INJECT = '''
# ── Per-build .log file ────────────────────────────────────────────────────
import hashlib as _hlib
_t_build_end = time.perf_counter()
_log_lines = [
    f"build:     {VERSION}",
    f"timestamp: {TIMESTAMP}",
    f"output:    {OUT.name}  ({size_kb} KB)",
    f"archived:  {aname}",
    "",
    "modules:",
]
_kernel_files = ["goldberg_kernel.js","graph_axioms.js","sar_modular.js",
                 "ns_spectral.js","fractal_search.js"]
for _kf in _kernel_files:
    _kp = KERNEL / _kf
    if _kp.exists():
        _kb  = _kp.stat().st_size // 1024
        _md5 = _hlib.md5(_kp.read_bytes()).hexdigest()[:8]
        _log_lines.append(f"  {_kf:<30} {_kb}KB  md5:{_md5}")
_log_lines += [
    f"  navierCrunch_browser.js        (inline)",
    f"  math_tree                      (inline, latest from tree/)",
    "",
    "invariants (kernel absolute):",
    "  P=12  pentagons  Euler forces it",
    "  chi=2  V-E+F=2   never breaks",
    "  C60 seed  60 vertices  32 faces",
    "  lambda_SAR5 = 0.1473",
    "",
]
# git hash if available
try:
    import subprocess as _sp
    _gh = _sp.check_output(["git","rev-parse","--short","HEAD"],
                           stderr=_sp.DEVNULL, cwd=ROOT).decode().strip()
    _log_lines.append(f"git:       {_gh}")
except Exception:
    _log_lines.append("git:       not available")
_log_lines.append(f"built_in:  {(time.perf_counter()-_t_build_end)*1000:.1f}ms (log write overhead)")

_log_path = HEX_ARCHIVE / aname.replace(".html", ".log")
_log_path.write_text("\\n".join(_log_lines), encoding="utf-8")
print(f"  ✓ Log:      {_log_path.name}")
'''

# Inject after the INDEX.txt write, before the print block
src = src.replace(
    '(HEX_ARCHIVE / "INDEX.txt").write_text("\\n".join(idx), encoding="utf-8")',
    '(HEX_ARCHIVE / "INDEX.txt").write_text("\\n".join(idx), encoding="utf-8")\n' + LOG_INJECT
)
fixes.append(("log file", ".log" in src and "_log_path" in src))

# ── Write patched file ───────────────────────────────────────────────────
SRC_FILE.write_text(src, encoding="utf-8")

# ── Report ───────────────────────────────────────────────────────────────
print("=" * 60)
print(f"  PATCH H7.1473.12.60.1")
print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
for name, ok in fixes:
    print(f"  {'✓' if ok else '✗'} {name}")
print(f"\n  {len([f for f in fixes if f[1]])}/{len(fixes)} fixes applied")
print(f"  {len(orig)} → {len(src)} chars")
print("\n  Run: python pack/build_holly7.py --no-open")
print("  Every build now writes .html + .log to hexCompTest/")

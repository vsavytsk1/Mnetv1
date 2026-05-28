#!/usr/bin/env python3
"""
build_genesis.py — Genesis Canvas Builder
==========================================
Takes genesis_v7.5 as THE reference template.
Injects ALL kernel modules (M1-M7).
Outputs shell/genesis_vX.Y.html in exact same format.

Format rules (NEVER CHANGE):
  - canvas fullscreen, z-index:0
  - HUD top-left
  - axiom-log top-right
  - bottom bar: buttons + sliders
  - Orbitron font for euler display
  - background #050508 ALWAYS
  - spin default: 0.002 (minimal compute)
  - zoom default: 50 (minimal compute)
  - maxFaces default: 1000 (minimal compute — zoom in to unlock)
"""
import re, time
from pathlib import Path

ROOT     = Path(__file__).parent.parent
KERNEL   = ROOT / "kernel"
SHELL    = ROOT / "shell"
TEMPLATE = SHELL / "genesis_v7.5.html"
VERSION  = "v8.1"
OUT      = SHELL / f"genesis_{VERSION}.html"
TIMESTAMP = time.strftime("%Y-%m-%d %H:%M:%S")

print(f"Building genesis_{VERSION}.html from template genesis_v7.5...")

# ── Read template ─────────────────────────────────────────────
src = TEMPLATE.read_text(encoding="utf-8")
lines = src.split("\n")
total = len(lines)
print(f"  Template: {total} lines, {len(src)//1024}KB")

# ── Find seams ────────────────────────────────────────────────
# Seam 1: end of HTML shell (line before first <script>)
# Seam 2: end of GK = line with "module.exports" / "globalThis"
# Seam 3: start of render engine (second <script>)

shell_end = next(i for i,l in enumerate(lines) if l.strip() == "<script>")
# GK ends at the IIFE closing line containing 'globalThis' and 'this)'
gk_end    = next(i for i,l in enumerate(lines)
                  if "globalThis" in l and "this)" in l and i > shell_end)
render_start = next(i for i,l in enumerate(lines)
                     if l.strip() == "<script>" and i > gk_end + 1)

print(f"  Shell:  L0..{shell_end-1}")
print(f"  GK:     L{shell_end}..{gk_end}")
print(f"  Render: L{render_start}..{total-1}")

# ── Read all kernel modules ───────────────────────────────────
def read_js(name):
    p = KERNEL / name
    if not p.exists():
        print(f"  [WARN] missing: {p.name}")
        return f"// MISSING: {name}\n"
    js = p.read_text(encoding="utf-8")
    print(f"  M: {name:<30} {len(js)//1024}KB")
    return js

M1 = read_js("goldberg_kernel.js")   # GK — already in template, replace it
M2 = read_js("graph_axioms.js")      # GA
M3 = read_js("sar_modular.js")       # SAR
M4 = read_js("ns_spectral.js")       # NSS
M5 = read_js("fractal_search.js")    # FS
M6 = read_js("mnet_nanite.js")       # NANITE (LOD DAG)

# ── Extract render engine (second <script> to </body>) ────────
# Skip the <script> tag itself and the closing tags at the end
render_lines = lines[render_start:]
# Find inner content (skip <script> tag, stop before </script></body></html>)
inner_start = next(i for i,l in enumerate(render_lines) if l.strip() == "<script>") + 1
# Last </script> before </body>
inner_end   = next(i for i,l in reversed(list(enumerate(render_lines)))
                   if "</script>" in l)
render_js   = "\n".join(render_lines[inner_start:inner_end])
print(f"  Render engine: {len(render_js)//1024}KB")

# ── HTML shell (update title + version) ──────────────────────
html_shell = "\n".join(lines[:shell_end])
html_shell = html_shell.replace("GENESIS v7.5.1", f"GENESIS {VERSION}")
html_shell = html_shell.replace(
    "GENESIS v7.5.1 - Fractal Graph Explorer",
    f"GENESIS {VERSION} - Full Kernel Build"
)

# ── Patch render JS ───────────────────────────────────────────
# 1. Minimal compute defaults
render_js = render_js.replace(
    "var cam = { rx: 0.3, ry: 0, zoom: 200, atom: 1.0, spin: 0.005, maxFaces: 50000 };",
    "var cam = { rx: 0.3, ry: 0, zoom: 50, atom: 0.1, spin: 0.002, maxFaces: 1000 }; // minimal compute — zoom in to unlock"
)
# 2. Update session label
render_js = render_js.replace(
    f"'v7.5.1_'",
    f"'{VERSION}_'"
)
# 3. Update title display
render_js = render_js.replace(
    "GENESIS v7.5.1",
    f"GENESIS {VERSION}"
)
# 4. Add M2-M6 console confirmation at boot
boot_note = f"""
// ── FULL KERNEL BUILD ({TIMESTAMP}) ─────────────────────────
// M1 goldberg_kernel  → GK
// M2 graph_axioms     → GA
// M3 sar_modular      → SAR
// M4 ns_spectral      → NSS
// M5 fractal_search   → FS
// M6 mnet_nanite      → NANITE
// All modules live. Use browser console to explore.
console.log('%c GENESIS {VERSION} — Full Kernel Build','color:#ff69b4;font-size:14px');
console.log('[H7] GK:', typeof GK !== 'undefined' ? 'OK' : 'MISSING');
console.log('[H7] GA:', typeof GA !== 'undefined' ? 'OK' : 'MISSING');
console.log('[H7] SAR:', typeof SAR !== 'undefined' ? 'OK' : 'MISSING');
console.log('[H7] NSS:', typeof NSS !== 'undefined' ? 'OK' : 'MISSING');
console.log('[H7] FS:', typeof FS !== 'undefined' ? 'OK' : 'MISSING');
console.log('[H7] NANITE:', typeof NANITE !== 'undefined' ? 'OK' : 'MISSING');
"""

# ── Assemble ──────────────────────────────────────────────────
html = f"""{html_shell}
<script>
// ── M1: goldberg_kernel.js ────────────────────────────────────
{M1}
</script>
<script>
// ── M2: graph_axioms.js ───────────────────────────────────────
{M2}
</script>
<script>
// ── M3: sar_modular.js ────────────────────────────────────────
{M3}
</script>
<script>
// ── M4: ns_spectral.js ────────────────────────────────────────
{M4}
</script>
<script>
// ── M5: fractal_search.js ─────────────────────────────────────
{M5}
</script>
<script>
// ── M6: mnet_nanite.js ────────────────────────────────────────
{M6}
</script>
<script>
{boot_note}
{render_js}
</script>
</body></html>"""

OUT.write_text(html, encoding="utf-8")
size_kb = len(html) // 1024
print(f"\n[OK] {OUT.name}  {size_kb}KB")
print(f"[OK] https://vsavytsk1.github.io/Mnetv1/shell/genesis_{VERSION}.html")

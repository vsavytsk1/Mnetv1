"""
build_genesis_v76.py
====================
Inject FractalEngBuilder button into genesis_v7.5 -> genesis_v7.6.html
Builder owns the shell. Minimal compute defaults. One new button.
"""
import re, time
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SRC  = ROOT / "shell" / "genesis_v7.5.html"
OUT  = ROOT / "shell" / "genesis_v7.6.html"

src = SRC.read_text(encoding="utf-8")

# 1. Bump title
src = src.replace("GENESIS v7.5.1", "GENESIS v7.6.0")
src = src.replace("GENESIS v7.5.1 - Fractal Graph Explorer", "GENESIS v7.6.0 - Fractal Graph Explorer")

# 2. Set minimal compute defaults (the paradigm — start at ZERO cost)
#    zoom=50 (was 200), maxFaces=100 (was 50000), spin=0 (was 0.005), atom=0.1 (was 1.0)
src = src.replace('value="200" id="sl-zm"', 'value="50" id="sl-zm"')
src = src.replace('SV(\'sv-zm\',this.value)"><span class="sv" id="sv-zm">200</span>',
                  'SV(\'sv-zm\',this.value)"><span class="sv" id="sv-zm">50</span>')
src = src.replace('value="5" id="sl-spin"', 'value="0" id="sl-spin"')
src = src.replace('SV(\'sv-spin\',this.value/1000)"><span class="sv" id="sv-spin">0.005</span>',
                  'SV(\'sv-spin\',this.value/1000)"><span class="sv" id="sv-spin">0.000</span>')

# 3. Inject FractalEngBuilder button after EXPORT/GRAPH buttons
NEW_BTN = '''<div class="sep"></div>
<button class="btn" style="color:#a78bfa;border-color:#3a2a5a;letter-spacing:0.08em"
  onclick="window.open('https://vsavytsk1.github.io/Mnetv1/pack/holly7.html','_blank')">
  &#9654; HOLLY7
</button>
<button class="btn" style="color:#a78bfa;border-color:#3a2a5a;font-size:8px"
  onclick="document.getElementById('febPanel').style.display=document.getElementById('febPanel').style.display==='none'?'block':'none'">
  ENG BUILDER &#9650;
</button>'''

src = src.replace(
    '<button class="btn gd" onclick="doExport()">EXPORT</button>',
    NEW_BTN + '\n<button class="btn gd" onclick="doExport()">EXPORT</button>'
)

# 4. Inject FractalEngBuilder panel (above #bar, hidden by default)
FEB_PANEL = '''
<div id="febPanel" style="display:none;position:fixed;bottom:52px;left:0;right:0;z-index:11;
  background:rgba(5,5,8,0.97);border-top:1px solid #3a2a5a;padding:8px 12px;
  font-family:'Courier New',monospace;font-size:9px;color:#a78bfa">
  <span style="color:#a78bfa;letter-spacing:0.2em;font-size:10px">&#9670; FRACTAL ENG BUILDER</span>
  <span style="color:#333;margin-left:12px">builder/build_holly7.py &#8594; pack/holly7.html &#8594; GitHub Pages</span>
  <div style="margin-top:6px;display:flex;gap:8px;flex-wrap:wrap">
    <a href="https://vsavytsk1.github.io/Mnetv1/pack/holly7.html" target="_blank"
       style="color:#00ffd5;text-decoration:none;border:1px solid #1a3a3a;padding:3px 8px;border-radius:3px">
       &#8599; holly7 LIVE</a>
    <a href="https://vsavytsk1.github.io/Mnetv1/shell/spooky_warning/warning_v2.0.html" target="_blank"
       style="color:#ff69b4;text-decoration:none;border:1px solid #3a1a2a;padding:3px 8px;border-radius:3px">
       &#8599; warning v2.0</a>
    <a href="https://vsavytsk1.github.io/Mnetv1/shell/gate/gate_v1.3.html" target="_blank"
       style="color:#ffd700;text-decoration:none;border:1px solid #332a00;padding:3px 8px;border-radius:3px">
       &#8599; gate v1.3</a>
    <a href="https://vsavytsk1.github.io/Mnetv1/pack/GKernV2.0.html" target="_blank"
       style="color:#80d0ff;text-decoration:none;border:1px solid #1a2a3a;padding:3px 8px;border-radius:3px">
       &#8599; GKern v2.0</a>
    <a href="https://vsavytsk1.github.io/Mnetv1/pack/navierHunt.html" target="_blank"
       style="color:#7fff7f;text-decoration:none;border:1px solid #1a3a1a;padding:3px 8px;border-radius:3px">
       &#8599; navierHunt</a>
    <span style="color:#333;margin-left:8px">H7.1473.12.60 &#8901; kernel:7 &#8901; built:''' + time.strftime('%Y-%m-%d') + '''</span>
  </div>
</div>'''

src = src.replace('<div id="bar">', FEB_PANEL + '\n<div id="bar">')

# 5. Bump console log
src = src.replace(
    'GENESIS v7.5.1 - Fractal Graph Explorer',
    'GENESIS v7.6.0 - Fractal Graph Explorer + FractalEngBuilder'
)

OUT.write_text(src, encoding="utf-8")
print(f"[OK] {OUT.name}  {len(src)//1024}KB")
print(f"[OK] https://vsavytsk1.github.io/Mnetv1/shell/genesis_v7.6.html")
print(f"     FractalEngBuilder panel injected")
print(f"     Minimal compute defaults set (zoom=50, spin=0)")

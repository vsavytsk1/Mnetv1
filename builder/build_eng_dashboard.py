#!/usr/bin/env python3
"""
build_eng_dashboard.py
======================
Engineering dashboard in EXACT graph_sandbox_v5.1 format.
Same CSS. Same HUD. Same bar. Same autopilot panel.
Our kernel modules + launch buttons for every live sim.

Format reference: shell/graph_sandbox_v5.1.html
Output:          shell/eng_v1.0.html
"""
import re, time
from pathlib import Path

ROOT      = Path(__file__).parent.parent
KERNEL    = ROOT / "kernel"
SHELL     = ROOT / "shell"
TEMPLATE  = SHELL / "graph_sandbox_v5.1.html"
VERSION   = "v1.0"
OUT       = SHELL / f"eng_{VERSION}.html"
TIMESTAMP = time.strftime("%Y-%m-%d %H:%M:%S")
BUILD     = f"ENG {VERSION} · {TIMESTAMP}"

print(f"Building eng_{VERSION}.html from graph_sandbox_v5.1 template...")

# ── Read template ─────────────────────────────────────────────
src  = TEMPLATE.read_text(encoding="utf-8")
lines = src.split("\n")
print(f"  Template: {len(lines)} lines, {len(src)//1024}KB")

# ── Read kernel modules ───────────────────────────────────────
def read_js(name):
    p = KERNEL / name
    if not p.exists():
        print(f"  [WARN] missing: {p.name}")
        return f"// MISSING: {name}\n"
    js = p.read_text(encoding="utf-8")
    print(f"  M: {name:<30} {len(js)//1024}KB")
    return js

M1 = read_js("goldberg_kernel.js")
M2 = read_js("graph_axioms.js")
M3 = read_js("sar_modular.js")
M4 = read_js("ns_spectral.js")
M5 = read_js("fractal_search.js")
M6 = read_js("mnet_nanite.js")

# ── Extract exact CSS from template ──────────────────────────
css_match = re.search(r'<style>(.*?)</style>', src, re.DOTALL)
CSS = css_match.group(1) if css_match else ""

# ── New HTML shell (same structure, eng content) ──────────────
HTML_SHELL = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MachineNet · ENG {VERSION}</title>
<style>
{CSS}
/* ENG EXTRAS */
.sim-tag{{background:#1a1a2a;color:#a78bfa;border:1px solid #3a2a5a;border-radius:3px;
  padding:2px 8px;font-size:10px;cursor:pointer;font-family:inherit;transition:all 0.15s}}
.sim-tag:hover{{background:#2a1a4a;border-color:#a78bfa;color:#fff}}
#eng-panel{{position:fixed;top:12px;right:12px;z-index:20;
  display:flex;flex-direction:column;gap:4px;align-items:flex-end}}
#eng-toggle{{background:#111;color:#a78bfa;border:1px solid #3a2a5a;border-radius:3px;
  padding:5px 14px;font-family:inherit;font-size:11px;cursor:pointer;
  letter-spacing:0.08em;transition:all 0.2s}}
#eng-toggle:hover{{background:#2a1a4a;border-color:#a78bfa}}
#eng-menu{{display:none;background:rgba(5,5,16,0.97);border:1px solid #2a1a3a;
  border-radius:4px;padding:6px;width:260px}}
#eng-menu.open{{display:flex;flex-direction:column;gap:3px}}
.eng-btn{{background:#0a0a1a;color:#c0c0d0;border:1px solid #2a2a3a;border-radius:3px;
  padding:6px 10px;font-family:inherit;font-size:10px;cursor:pointer;text-align:left;
  transition:all 0.15s;text-decoration:none;display:block}}
.eng-btn:hover{{background:#1a1a2a;border-color:#a78bfa;color:#a78bfa}}
.eng-btn .eng-name{{font-weight:bold;font-size:11px;color:#e0e0e0}}
.eng-btn .eng-desc{{color:#555;font-size:9px;margin-top:2px}}
.eng-btn .eng-tag{{float:right;font-size:8px;color:#a78bfa;letter-spacing:0.1em}}
/* kernel status */
#k-status{{position:fixed;top:120px;left:12px;z-index:10;pointer-events:none;
  font-size:9px;line-height:1.8;color:#333}}
#k-status .ok{{color:#00ffd5}}.k-status .miss{{color:#ff4444}}
</style>
</head>
<body class="graph-A">

<!-- HUD top-left -->
<div id="hud">
  <div class="title">MachineNet · ENG {VERSION}</div>
  <div class="info">
    <b style="color:#a78bfa">KERNEL</b>:
    <span class="cyan" id="h-modules">loading…</span><br>
    <span class="gold" id="h-shape">C60 · 60V · 32F · χ=2 · P=12</span><br>
    <span class="pink" id="h-inv">λ̃=0.1473 · SAR-5 · LOCKED</span>
  </div>
</div>

<!-- kernel status -->
<div id="k-status">
  <span id="ks-gk">GK  ·</span>
  <span id="ks-ga">GA  ·</span>
  <span id="ks-sar">SAR ·</span>
  <span id="ks-nss">NSS ·</span>
  <span id="ks-fs">FS  ·</span>
  <span id="ks-nan">NAN ·</span>
</div>

<!-- NS flow HUD -->
<div id="ns-hud">
  <div class="eq-line">Du/Dt = −∇p + (1/Re)∇²u · ∇·u=0</div>
  <div class="stats" id="ns-stats">step 0 · Re=150 · dt=0.02</div>
</div>

<!-- log -->
<div id="log"></div>

<!-- bottom bar — exact sandbox format -->
<div id="bar">
  <span class="lbl">SEED</span>
  <button class="btn themed" onclick="engSeed('c60')">C60</button>
  <button class="btn themed" onclick="engSeed('dodec')">DODEC</button>
  <button class="btn themed" onclick="engRefine()">REFINE</button>
  <div class="sep"></div>

  <span class="lbl">PROOF</span>
  <button class="btn op" onclick="engSAR()">SAR-5</button>
  <button class="btn op" onclick="engNS()">NS FLOW</button>
  <button class="btn op" onclick="engFS()">FRAC SEARCH</button>
  <div class="sep"></div>

  <span class="lbl">SIM</span>
  <button class="btn" style="color:#00ffd5;border-color:#1a3a3a" onclick="engOpen('genesis')">GENESIS</button>
  <button class="btn" style="color:#ffd700;border-color:#3a3a1a" onclick="engOpen('tree')">TREE</button>
  <button class="btn" style="color:#ff9040;border-color:#4a2a1a" onclick="engOpen('navier')">NAVIER</button>
  <div class="sep"></div>

  <span class="lbl">BUILD</span>
  <button class="btn" style="color:#a78bfa;border-color:#3a2a5a" onclick="engOpen('holly7')">HOLLY7 ↗</button>
  <button class="btn" style="color:#ff69b4;border-color:#4a1a3a" onclick="engOpen('warning')">WARNING ↗</button>

  <div id="cmd-bar">
    <input id="cmd-input" type="text" placeholder="type command + enter" spellcheck="false">
    <button id="cmd-go" onclick="cmdRun()">RUN</button>
  </div>
</div>

<!-- snap bar -->
<div id="snap-bar"></div>

<!-- BACK button (hidden until module open) -->
<button id="eng-back" onclick="engBack()"
  style="display:none;position:fixed;top:12px;left:50%;transform:translateX(-50%);
  z-index:200;background:#111;color:#a78bfa;border:1px solid #3a2a5a;
  border-radius:3px;padding:5px 20px;font-family:inherit;font-size:11px;cursor:pointer;
  letter-spacing:0.1em">← BACK TO ENG</button>

<!-- INLINE VIEWPORT (hidden until module open) -->
<iframe id="eng-viewport"
  style="display:none;position:fixed;top:0;left:0;width:100%;height:calc(100% - 42px);
  z-index:100;border:none;background:#050510;"></iframe>

<!-- MAIN content wrapper -->
<div id="eng-main">

</div><!-- /eng-main -->

<!-- ENG LAUNCHER (replaces AUTOPILOT) -->
<div id="eng-panel">
  <button id="eng-toggle" onclick="engToggleMenu()">⬡ ENG LAUNCHER</button>
  <div id="eng-menu">

    <a class="eng-btn" href="https://vsavytsk1.github.io/Mnetv1/pack/holly7.html" target="_blank">
      <span class="eng-tag">DASHBOARD</span>
      <div class="eng-name">1 · HOLLY7</div>
      <div class="eng-desc">All 7 modules · SAR-5 · NS · tree · navierCrunch</div>
    </a>

    <a class="eng-btn" href="https://vsavytsk1.github.io/Mnetv1/shell/genesis_v8.1.html" target="_blank">
      <span class="eng-tag">CANVAS</span>
      <div class="eng-name">2 · GENESIS v8.1</div>
      <div class="eng-desc">Full kernel build · M1-M6 · v7.5 format</div>
    </a>

    <a class="eng-btn" href="https://vsavytsk1.github.io/Mnetv1/shell/graph_sandbox_v5.1.html" target="_blank">
      <span class="eng-tag">SANDBOX</span>
      <div class="eng-name">3 · GRAPH SANDBOX</div>
      <div class="eng-desc">Graph ops · NS flow · cage · autopilot · cmd</div>
    </a>

    <a class="eng-btn" href="https://vsavytsk1.github.io/Mnetv1/tree/math_tree_v5.0.html" target="_blank">
      <span class="eng-tag">TREE</span>
      <div class="eng-name">4 · MATH TREE v5.0</div>
      <div class="eng-desc">Sacred tree · gacha · forward-only · KaTeX</div>
    </a>

    <a class="eng-btn" href="https://vsavytsk1.github.io/Mnetv1/pack/navierCrunch_turbulent.html" target="_blank">
      <span class="eng-tag">BENCHMARK</span>
      <div class="eng-name">5 · NAVIERCUNCH</div>
      <div class="eng-desc">Turbulent Re>10000 · RTX3060 · O(n) confirmed</div>
    </a>

    <a class="eng-btn" href="https://vsavytsk1.github.io/Mnetv1/shell/spooky_warning/warning_v2.0.html" target="_blank">
      <span class="eng-tag">FMA</span>
      <div class="eng-name">6 · WARNING v2.0</div>
      <div class="eng-desc">FMA intro · circle phase · v8 engine · built by builder</div>
    </a>

    <div style="border-top:1px solid #1a1a2a;margin:4px 0;padding-top:4px;
      font-size:9px;color:#333;text-align:right">
      {BUILD}<br>
      GK · GA · SAR · NSS · FS · NAN
    </div>
  </div>
</div>

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
// ── ENG DASHBOARD GLUE ───────────────────────────────────────
var LINKS = {{
  genesis : 'https://vsavytsk1.github.io/Mnetv1/shell/genesis_v8.1.html',
  tree    : 'https://vsavytsk1.github.io/Mnetv1/tree/math_tree_v5.0.html',
  navier  : 'https://vsavytsk1.github.io/Mnetv1/pack/navierCrunch_turbulent.html',
  holly7  : 'https://vsavytsk1.github.io/Mnetv1/pack/holly7.html',
  warning : 'https://vsavytsk1.github.io/Mnetv1/shell/spooky_warning/warning_v2.0.html',
  sandbox : 'https://vsavytsk1.github.io/Mnetv1/shell/graph_sandbox_v5.1.html'
}};

function engOpen(key){{
  var vp = document.getElementById('eng-viewport');
  var main = document.getElementById('eng-main');
  var back = document.getElementById('eng-back');
  vp.src = LINKS[key];
  vp.style.display = 'block';
  back.style.display = 'block';
  main.style.display = 'none';
}}
function engBack(){{
  var vp = document.getElementById('eng-viewport');
  vp.style.display = 'none';
  vp.src = '';
  document.getElementById('eng-back').style.display = 'none';
  document.getElementById('eng-main').style.display = 'block';
}}
function engToggleMenu(){{
  var m = document.getElementById('eng-menu');
  m.classList.toggle('open');
}}

// Kernel status check
window.addEventListener('load', function(){{
  var checks = [
    ['ks-gk',  typeof GK   !== 'undefined', 'GK'],
    ['ks-ga',  typeof GA   !== 'undefined', 'GA'],
    ['ks-sar', typeof SAR  !== 'undefined', 'SAR'],
    ['ks-nss', typeof NSS  !== 'undefined', 'NSS'],
    ['ks-fs',  typeof FS   !== 'undefined', 'FS'],
    ['ks-nan', typeof MNetNanite !== 'undefined', 'NAN']
  ];
  var allOk = true;
  checks.forEach(function(c){{
    var el = document.getElementById(c[0]);
    if(el){{
      el.textContent = c[2] + (c[1] ? ' ✓' : ' ✗');
      el.className = c[1] ? 'ok' : 'miss';
      if(!c[1]) allOk = false;
    }}
    console.log('[ENG] ' + c[2] + ': ' + (c[1] ? 'OK' : 'MISSING'));
  }});
  document.getElementById('h-modules').textContent =
    allOk ? '6/6 OK' : 'check console';
  document.getElementById('h-modules').style.color = allOk ? '#00ffd5' : '#ff4444';
}});

// Seed
var _engState = null;
function engSeed(type){{
  _engState = type === 'dodec' ? GK.buildDodecahedron() : GK.buildC60();
  var inv = GK.invariants(_engState);
  document.getElementById('h-shape').textContent =
    (type==='dodec'?'DODEC':'C60') + ' · ' +
    inv.vertices + 'V · ' + inv.faces + 'F · χ=' +
    (inv.vertices - inv.edges + inv.faces) + ' · P=' + inv.pents;
  logAdd('SEED', type.toUpperCase() + ' · ' + inv.faces + 'F');
}}

function engRefine(){{
  if(!_engState){{ engSeed('c60'); }}
  _engState = GK.refineAll(_engState);
  var inv = GK.invariants(_engState);
  logAdd('REFINE', inv.faces + 'F · P=' + inv.pents + ' · χ=' + (inv.vertices-inv.edges+inv.faces));
}}

function engSAR(){{
  if(!_engState) engSeed('c60');
  var r = SAR.proof(_engState);
  logAdd('SAR-5', 'λ̃₁=' + parseFloat(r.spectral.lambda1).toFixed(6) +
    ' · M₀=' + r.M0.count + ' · ' + (r.spectral.match ? 'MATCH ✓' : 'Δ=' + r.spectral.deviation));
}}

function engNS(){{
  if(!_engState) engSeed('c60');
  var r = NSS.runOn(_engState, {{Re:150, steps:200}});
  var lam = r.lambdaEst !== null ? r.lambdaEst.toFixed(6) : '?';
  logAdd('NS FLOW', 'λ̃₁=' + lam + ' · Δ=' + (r.delta !== null ? r.delta.toFixed(6) : '?'));
}}

function engFS(){{
  if(!_engState) engSeed('c60');
  var r = FS.search({{seed:'c60', maxLevels:3, target:0.1473}});
  logAdd('FRAC SEARCH', r.locked ? 'LOCKED ✓' : 'searching…');
}}

// Log
function logAdd(op, msg){{
  var log = document.getElementById('log');
  var d = document.createElement('div');
  d.className = 'entry';
  d.innerHTML = '<span class="op">' + op + '</span>  <span class="g">' + msg + '</span>';
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
}}

// CMD
function cmdRun(){{
  var v = document.getElementById('cmd-input').value.trim();
  if(!v) return;
  document.getElementById('cmd-input').value = '';
  try{{
    var r = eval(v);
    logAdd('CMD', JSON.stringify(r).slice(0,120));
  }} catch(e){{ logAdd('ERR', e.message); }}
}}
document.addEventListener('DOMContentLoaded', function(){{
  document.getElementById('cmd-input').addEventListener('keydown', function(e){{
    if(e.key === 'Enter') cmdRun();
  }});
}});

console.log('%c ENG {VERSION} loaded','color:#a78bfa;font-size:14px');
console.log('[ENG] {TIMESTAMP}');
</script>
</body></html>"""

OUT.write_text(HTML_SHELL, encoding="utf-8")
size_kb = len(HTML_SHELL) // 1024
print(f"\n[OK] {OUT.name}  {size_kb}KB")
print(f"[OK] https://vsavytsk1.github.io/Mnetv1/shell/eng_{VERSION}.html")

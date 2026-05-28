#!/usr/bin/env python3
"""
build_eng_v2.py  —  ENG v2.0  MASTER CONTROL DASHBOARD
=======================================================
Tony Stark lab layout:
  TOP BAR   — build stamp · live clock · git hash
  LEFT COL  — kernel status (6 modules, live) + mini C60 canvas
  CENTER    — module cards (click = summon inline)
  RIGHT COL — build log + LEDGER last 5 entries
  BOTTOM    — command bar (sandbox format, exact)
  OVERLAY   — iframe fills screen when module summoned, ← BACK returns
"""
import re, time, subprocess
from pathlib import Path

ROOT      = Path(__file__).parent.parent
KERNEL    = ROOT / "kernel"
SHELL     = ROOT / "shell"
VERSION   = "v2.0"
OUT       = SHELL / f"eng_{VERSION}.html"
TIMESTAMP = time.strftime("%Y-%m-%d %H:%M:%S")

try:
    GIT = subprocess.check_output(["git","rev-parse","--short","HEAD"],
          stderr=subprocess.DEVNULL, cwd=ROOT).decode().strip()
except: GIT = "local"

print(f"Building eng_{VERSION}.html — MASTER CONTROL DASHBOARD")

def read_js(name):
    p = KERNEL / name
    if not p.exists(): print(f"  [WARN] {name}"); return f"// MISSING: {name}\n"
    js = p.read_text(encoding="utf-8")
    print(f"  M: {name:<30} {len(js)//1024}KB")
    return js

M1 = read_js("goldberg_kernel.js")
M2 = read_js("graph_axioms.js")
M3 = read_js("sar_modular.js")
M4 = read_js("ns_spectral.js")
M5 = read_js("fractal_search.js")
M6 = read_js("mnet_nanite.js")

# Read last 5 LEDGER entries
ledger_lines = []
lp = ROOT / "LEDGER.md"
if lp.exists():
    raw = lp.read_bytes().decode('utf-8', errors='ignore')
    entries = [l.strip() for l in raw.split("\n") if l.startswith("### L")]
    ledger_lines = entries[-5:]

LEDGER_HTML = "".join(
    f'<div class="log-entry"><span class="op">{e.split("·")[0].strip()}</span> '
    f'<span class="g">{("·".join(e.split("·")[1:])).strip()}</span></div>'
    for e in ledger_lines
)

# Module cards definition
MODULES = [
    ("GENESIS v8.1",  "CANVAS",    "#00ffd5", "#1a3a3a",
     "M1-M6 · full kernel · v7.5 format · canvas explorer",
     "genesis", "https://vsavytsk1.github.io/Mnetv1/shell/genesis_v8.1.html"),
    ("GRAPH SANDBOX", "SANDBOX",   "#80d0ff", "#1a2a3a",
     "Graph ops · NS flow · cage · autopilot · cmd · 3D",
     "sandbox", "https://vsavytsk1.github.io/Mnetv1/shell/graph_sandbox_v5.1.html"),
    ("MATH TREE v5.0","TREE",      "#ffd700", "#3a3a1a",
     "Sacred tree · gacha · forward-only · KaTeX · shame slider",
     "tree",    "https://vsavytsk1.github.io/Mnetv1/tree/math_tree_v5.0.html"),
    ("HOLLY7",        "DASHBOARD", "#a78bfa", "#2a1a4a",
     "7 modules · SAR-5 proof · NS flow · navierCrunch · tree",
     "holly7",  "https://vsavytsk1.github.io/Mnetv1/pack/holly7.html"),
    ("NAVIERCUNCH",   "BENCHMARK", "#ff9040", "#3a2a1a",
     "Turbulent Re>10000 · RTX3060 · O(n) · GPU/CPU sparse",
     "navier",  "https://vsavytsk1.github.io/Mnetv1/pack/navierCrunch_turbulent.html"),
    ("WARNING v2.0",  "FMA",       "#ff69b4", "#3a1a2a",
     "FMA intro · transmutation circle · v8 engine · builder",
     "warning", "https://vsavytsk1.github.io/Mnetv1/shell/spooky_warning/warning_v2.0.html"),
]

CARDS_HTML = ""
for name, tag, color, border, desc, key, url in MODULES:
    CARDS_HTML += f"""
  <div class="mod-card" onclick="summon('{key}')"
    style="border-color:{border};--card-color:{color}">
    <div class="card-tag" style="color:{color}">{tag}</div>
    <div class="card-name" style="color:{color}">{name}</div>
    <div class="card-desc">{desc}</div>
    <div class="card-arrow" style="color:{color}">▶ SUMMON</div>
  </div>"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MachineNet · ENG {VERSION} · MASTER CONTROL</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --bg:     #030308;
  --panel:  #07070f;
  --border: #0e0e1e;
  --text:   #9090a0;
  --bright: #d0d8e8;
  --cyan:   #00d4ff;
  --gold:   #ffd700;
  --pink:   #ff69b4;
  --green:  #00ffd5;
  --purple: #a78bfa;
  --orange: #ff9040;
}}
body{{background:var(--bg);color:var(--text);
     font-family:ui-monospace,"SF Mono","Fira Code",monospace;
     font-size:11px;overflow:hidden;height:100vh;display:flex;flex-direction:column}}

/* ── TOP BAR ── */
#top-bar{{
  background:var(--panel);border-bottom:1px solid var(--border);
  padding:0 16px;height:36px;display:flex;align-items:center;gap:16px;
  flex-shrink:0;z-index:10
}}
#top-bar .logo{{color:var(--cyan);font-size:12px;letter-spacing:0.12em;font-weight:bold}}
#top-bar .build{{color:#2a3a4a;font-size:10px}}
#top-bar .git{{color:#1a2a1a;font-size:10px}}
#top-bar .clock{{margin-left:auto;color:#1a2a3a;font-size:10px;font-variant-numeric:tabular-nums}}
#top-bar .k-ok{{color:var(--green);font-size:10px}}
#top-bar .k-bad{{color:#ff4444;font-size:10px}}

/* ── MAIN GRID ── */
#main{{display:flex;flex:1;overflow:hidden;gap:0}}

/* ── LEFT PANEL ── */
#left{{
  width:180px;flex-shrink:0;
  background:var(--panel);border-right:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden
}}
.panel-title{{
  color:#1a2a3a;font-size:9px;letter-spacing:0.2em;text-transform:uppercase;
  padding:8px 12px 4px;border-bottom:1px solid var(--border)
}}
#k-list{{padding:8px 12px;flex-shrink:0}}
.k-row{{display:flex;justify-content:space-between;align-items:center;
  padding:3px 0;border-bottom:1px solid #0a0a14}}
.k-name{{color:#2a3a4a;font-size:10px;letter-spacing:0.05em}}
.k-ok{{color:var(--green);font-size:10px}}
.k-miss{{color:#ff4444;font-size:10px}}
.k-kb{{color:#1a2a2a;font-size:9px}}
#mini-canvas-wrap{{flex:1;position:relative;overflow:hidden;border-top:1px solid var(--border)}}
#mini-canvas-wrap .panel-title{{position:absolute;top:0;left:0;right:0;z-index:2;background:var(--panel)}}
#cv-mini{{position:absolute;top:22px;left:0;width:100%;height:calc(100% - 22px);display:block}}

/* ── CENTER ── */
#center{{
  flex:1;overflow-y:auto;padding:16px;
  display:flex;flex-direction:column;gap:12px
}}
#center-top{{
  color:#1a2a3a;font-size:9px;letter-spacing:0.15em;margin-bottom:4px
}}
.mod-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}}
.mod-card{{
  background:var(--panel);border:1px solid #0e0e1e;border-radius:4px;
  padding:12px 14px;cursor:pointer;transition:all 0.2s;position:relative;
  overflow:hidden
}}
.mod-card::before{{
  content:'';position:absolute;inset:0;opacity:0;
  background:radial-gradient(ellipse at 30% 30%, var(--card-color,#00d4ff) 0%, transparent 70%);
  transition:opacity 0.3s
}}
.mod-card:hover::before{{opacity:0.04}}
.mod-card:hover{{border-color:var(--card-color,#00d4ff);transform:translateY(-1px)}}
.card-tag{{font-size:8px;letter-spacing:0.2em;margin-bottom:4px;opacity:0.7}}
.card-name{{font-size:13px;font-weight:bold;margin-bottom:6px}}
.card-desc{{color:#2a3a4a;font-size:9px;line-height:1.6;margin-bottom:8px}}
.card-arrow{{font-size:9px;letter-spacing:0.1em;opacity:0}}
.mod-card:hover .card-arrow{{opacity:1}}

/* ── RIGHT PANEL ── */
#right{{
  width:220px;flex-shrink:0;
  background:var(--panel);border-left:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden
}}
#eng-log{{flex:1;overflow-y:auto;padding:8px 10px}}
.log-entry{{padding:3px 0;border-bottom:1px solid #0a0a14;font-size:9px;line-height:1.5}}
.log-entry .op{{color:var(--pink);font-weight:bold}}
.log-entry .g{{color:#1a3a3a}}
.log-entry .ok{{color:var(--green)}}
.log-entry .warn{{color:var(--gold)}}
#ledger-section{{border-top:1px solid var(--border);padding:8px 10px;flex-shrink:0}}
.ledger-entry{{font-size:9px;color:#1a2a2a;padding:2px 0;line-height:1.4}}
.ledger-entry .lid{{color:#2a3a4a}}

/* ── BOTTOM BAR ── */
#bar{{
  background:var(--panel);border-top:1px solid var(--border);
  padding:6px 14px;display:flex;align-items:center;gap:6px;
  flex-wrap:wrap;flex-shrink:0;z-index:10
}}
.btn{{background:#0a0a14;color:#2a3a4a;border:1px solid var(--border);
  border-radius:3px;padding:4px 10px;font-family:inherit;
  font-size:10px;cursor:pointer;transition:all 0.15s;white-space:nowrap}}
.btn:hover{{background:#111122;border-color:#3a3a4a;color:var(--bright)}}
.btn.op{{color:var(--pink);border-color:#2a1a2a}}
.btn.op:hover{{border-color:var(--pink)}}
.sep{{width:1px;height:16px;background:var(--border)}}
.lbl{{color:#1a2a2a;font-size:9px;letter-spacing:0.1em;text-transform:uppercase}}
#cmd-bar{{display:flex;gap:4px;align-items:center;margin-left:auto}}
#cmd-input{{background:rgba(5,5,16,0.9);color:var(--bright);
  border:1px solid var(--border);border-radius:3px;
  padding:4px 10px;font-family:inherit;font-size:10px;width:220px;outline:none}}
#cmd-input:focus{{border-color:var(--pink)}}
#cmd-input::placeholder{{color:#1a1a2a}}
#cmd-go{{background:#0a0a14;color:var(--pink);border:1px solid #2a1a2a;
  border-radius:3px;padding:4px 10px;font-family:inherit;font-size:10px;cursor:pointer}}
#cmd-go:hover{{border-color:var(--pink)}}

/* ── OVERLAY (summon) ── */
#overlay{{display:none;position:fixed;inset:0;z-index:100;flex-direction:column}}
#overlay.open{{display:flex}}
#overlay-bar{{
  background:rgba(3,3,8,0.97);border-bottom:1px solid #1a1a2a;
  padding:0 16px;height:36px;display:flex;align-items:center;gap:12px;
  flex-shrink:0
}}
#overlay-title{{color:var(--cyan);font-size:11px;letter-spacing:0.1em}}
#overlay-back{{
  background:#0a0a14;color:var(--purple);border:1px solid #2a1a4a;
  border-radius:3px;padding:3px 14px;font-family:inherit;font-size:10px;
  cursor:pointer;letter-spacing:0.08em
}}
#overlay-back:hover{{background:#1a1a2a;border-color:var(--purple)}}
#overlay-frame{{flex:1;border:none;background:#030308}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{{width:4px}}
::-webkit-scrollbar-track{{background:#030308}}
::-webkit-scrollbar-thumb{{background:#1a1a2a;border-radius:2px}}
</style>
</head>
<body>

<!-- TOP BAR -->
<div id="top-bar">
  <span class="logo">⬡ ENG {VERSION}</span>
  <span class="build">H7.1473.12.60 · {TIMESTAMP}</span>
  <span class="git">git:{GIT}</span>
  <span id="top-k" class="k-ok">6/6 ✓</span>
  <span class="clock" id="clock">──:──:──</span>
</div>

<!-- MAIN GRID -->
<div id="main">

  <!-- LEFT: kernel status + mini C60 -->
  <div id="left">
    <div class="panel-title">KERNEL</div>
    <div id="k-list">
      <div class="k-row"><span class="k-name">GK</span>  <span id="ks-gk"  class="k-ok">·</span><span class="k-kb">21KB</span></div>
      <div class="k-row"><span class="k-name">GA</span>  <span id="ks-ga"  class="k-ok">·</span><span class="k-kb">13KB</span></div>
      <div class="k-row"><span class="k-name">SAR</span> <span id="ks-sar" class="k-ok">·</span><span class="k-kb">27KB</span></div>
      <div class="k-row"><span class="k-name">NSS</span> <span id="ks-nss" class="k-ok">·</span><span class="k-kb">13KB</span></div>
      <div class="k-row"><span class="k-name">FS</span>  <span id="ks-fs"  class="k-ok">·</span><span class="k-kb">13KB</span></div>
      <div class="k-row"><span class="k-name">NAN</span> <span id="ks-nan" class="k-ok">·</span><span class="k-kb">24KB</span></div>
    </div>
    <div id="mini-canvas-wrap">
      <div class="panel-title">C60 · LIVE</div>
      <canvas id="cv-mini"></canvas>
    </div>
  </div>

  <!-- CENTER: module cards -->
  <div id="center">
    <div id="center-top">MODULES — CLICK TO SUMMON</div>
    <div class="mod-grid">
      {CARDS_HTML}
    </div>
  </div>

  <!-- RIGHT: log + ledger -->
  <div id="right">
    <div class="panel-title">SESSION LOG</div>
    <div id="eng-log"></div>
    <div id="ledger-section">
      <div class="panel-title" style="padding:0 0 4px">LEDGER</div>
      {LEDGER_HTML}
    </div>
  </div>

</div><!-- /main -->

<!-- BOTTOM BAR -->
<div id="bar">
  <span class="lbl">SEED</span>
  <button class="btn" onclick="engSeed('c60')">C60</button>
  <button class="btn" onclick="engSeed('dodec')">DODEC</button>
  <button class="btn" onclick="engRefine()">REFINE</button>
  <div class="sep"></div>
  <span class="lbl">PROOF</span>
  <button class="btn op" onclick="engSAR()">SAR-5</button>
  <button class="btn op" onclick="engNS()">NS FLOW</button>
  <button class="btn op" onclick="engFS()">FRAC SEARCH</button>
  <div class="sep"></div>
  <span class="lbl" style="color:#1a2a1a">P=12 · χ=2 · λ̃=0.1473</span>
  <div id="cmd-bar">
    <input id="cmd-input" type="text" placeholder="cmd + enter  (eval JS)" spellcheck="false">
    <button id="cmd-go" onclick="cmdRun()">RUN</button>
  </div>
</div>

<!-- SUMMON OVERLAY -->
<div id="overlay">
  <div id="overlay-bar">
    <button id="overlay-back" onclick="overlayClose()">← BACK</button>
    <span id="overlay-title">─</span>
    <span style="margin-left:auto;color:#1a2a2a;font-size:9px" id="overlay-url"></span>
  </div>
  <iframe id="overlay-frame" src=""></iframe>
</div>

<!-- KERNEL MODULES -->
<script>{M1}</script>
<script>{M2}</script>
<script>{M3}</script>
<script>{M4}</script>
<script>{M5}</script>
<script>{M6}</script>

<script>
// ── KERNEL CHECK ─────────────────────────────────────────────
var MODULES_OK = true;
(function(){{
  var checks=[
    ['ks-gk', typeof GK!=='undefined','GK'],
    ['ks-ga', typeof GA!=='undefined','GA'],
    ['ks-sar',typeof SAR!=='undefined','SAR'],
    ['ks-nss',typeof NSS!=='undefined','NSS'],
    ['ks-fs', typeof FS!=='undefined','FS'],
    ['ks-nan',typeof MNetNanite!=='undefined','NAN']
  ];
  var ok=0;
  checks.forEach(function(c){{
    var el=document.getElementById(c[0]);
    var pass=c[1];
    if(pass) ok++;
    else MODULES_OK=false;
    if(el){{ el.textContent=pass?'✓':'✗'; el.className=pass?'k-ok':'k-miss'; }}
    console.log('[ENG] '+c[2]+': '+(pass?'OK':'MISSING'));
  }});
  var tk=document.getElementById('top-k');
  tk.textContent=ok+'/6 '+(ok===6?'✓':'⚠');
  tk.className=ok===6?'k-ok':'k-bad';
}})();

// ── CLOCK ────────────────────────────────────────────────────
setInterval(function(){{
  var n=new Date();
  document.getElementById('clock').textContent=
    n.toTimeString().slice(0,8);
}},1000);

// ── MINI C60 CANVAS ──────────────────────────────────────────
var _miniState=null, _miniCam={{rx:0.3,ry:0,spin:0.004}};
(function miniInit(){{
  var wrap=document.getElementById('mini-canvas-wrap');
  var cv=document.getElementById('cv-mini');
  function resize(){{
    cv.width=wrap.clientWidth;
    cv.height=wrap.clientHeight-22;
  }}
  resize();
  new ResizeObserver(resize).observe(wrap);
  _miniState=GK.buildC60();
  var jpts=_miniState.faces.map(function(f){{
    return f.pts.map(function(p){{return[p[0],p[1],p[2]];}});
  }});
  var ctx=cv.getContext('2d');
  (function loop(){{
    requestAnimationFrame(loop);
    _miniCam.ry+=_miniCam.spin;
    var W=cv.width,H=cv.height;
    if(!W||!H) return;
    ctx.fillStyle='rgba(3,3,8,0.18)';ctx.fillRect(0,0,W,H);
    var cy2=Math.cos(_miniCam.ry),sy2=Math.sin(_miniCam.ry);
    var cx2=Math.cos(_miniCam.rx),sx2=Math.sin(_miniCam.rx);
    var zoom=Math.min(W,H)*0.38;
    function proj(p){{
      var x=p[0],y=p[1],z=p[2];
      var x1=x*cy2-z*sy2,z1=x*sy2+z*cy2;
      var y1=y*cx2-z1*sx2,z2=y*sx2+z1*cx2;
      var s=zoom/(z2+4);
      return{{x:W/2+x1*s,y:H/2+y1*s,z:z2}};
    }}
    _miniState.faces.forEach(function(f,fi){{
      var pts=jpts[fi],n=pts.length;
      var isPent=f.type==='pent';
      for(var i=0;i<n;i++){{
        var a=proj(pts[i]),b=proj(pts[(i+1)%n]);
        if(a.z<-3||b.z<-3) continue;
        var br=Math.max(0.05,Math.min(0.8,1.2/(Math.abs(a.z)+2)));
        ctx.strokeStyle=isPent?
          'rgba(0,212,255,'+br+')':
          'rgba(0,255,213,'+(br*0.4)+')';
        ctx.lineWidth=isPent?1.2:0.4;
        ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
      }}
    }});
  }})();
}})();

// ── SUMMON ───────────────────────────────────────────────────
var LINKS={{
  genesis:'https://vsavytsk1.github.io/Mnetv1/shell/genesis_v8.1.html',
  sandbox:'https://vsavytsk1.github.io/Mnetv1/shell/graph_sandbox_v5.1.html',
  tree   :'https://vsavytsk1.github.io/Mnetv1/tree/math_tree_v5.0.html',
  holly7 :'https://vsavytsk1.github.io/Mnetv1/pack/holly7.html',
  navier :'https://vsavytsk1.github.io/Mnetv1/pack/navierCrunch_turbulent.html',
  warning:'https://vsavytsk1.github.io/Mnetv1/shell/spooky_warning/warning_v2.0.html'
}};
function summon(key){{
  var ov=document.getElementById('overlay');
  var fr=document.getElementById('overlay-frame');
  var title=document.getElementById('overlay-title');
  var urlEl=document.getElementById('overlay-url');
  var url=LINKS[key];
  fr.src=url;
  title.textContent=key.toUpperCase();
  urlEl.textContent=url.replace('https://vsavytsk1.github.io/Mnetv1/','');
  ov.classList.add('open');
  logAdd('SUMMON',key.toUpperCase());
}}
function overlayClose(){{
  var ov=document.getElementById('overlay');
  var fr=document.getElementById('overlay-frame');
  ov.classList.remove('open');
  setTimeout(function(){{fr.src='';}},300);
  logAdd('BACK','dashboard');
}}

// ── KERNEL OPS ───────────────────────────────────────────────
var _engState=null;
function engSeed(type){{
  _engState=type==='dodec'?GK.buildDodecahedron():GK.buildC60();
  var inv=GK.invariants(_engState);
  logAdd('SEED',type.toUpperCase()+' · '+inv.faces+'F · P='+inv.pents+' · χ='+(inv.vertices-inv.edges+inv.faces));
}}
function engRefine(){{
  if(!_engState)engSeed('c60');
  var t0=performance.now();
  _engState=GK.refineAll(_engState);
  var inv=GK.invariants(_engState);
  logAdd('REFINE',inv.faces+'F · '+Math.round(performance.now()-t0)+'ms');
}}
function engSAR(){{
  if(!_engState)engSeed('c60');
  var t0=performance.now();
  var r=SAR.proof(_engState);
  logAdd('SAR-5','λ̃₁='+parseFloat(r.spectral.lambda1).toFixed(6)+
    ' · M₀='+r.M0.count+' · '+(r.spectral.match?'MATCH ✓':'Δ='+r.spectral.deviation)+
    ' · '+Math.round(performance.now()-t0)+'ms');
}}
function engNS(){{
  if(!_engState)engSeed('c60');
  var t0=performance.now();
  var r=NSS.runOn(_engState,{{Re:150,steps:200}});
  logAdd('NS FLOW','λ̃₁='+(r.lambdaEst!==null?r.lambdaEst.toFixed(6):'?')+
    ' · '+(r.delta!==null?'Δ='+r.delta.toFixed(6):'')+
    ' · '+Math.round(performance.now()-t0)+'ms');
}}
function engFS(){{
  if(!_engState)engSeed('c60');
  var t0=performance.now();
  var r=FS.search({{seed:'c60',maxLevels:3,target:0.1473}});
  logAdd('FRAC SEARCH',(r.locked?'LOCKED ✓':'not locked')+' · '+Math.round(performance.now()-t0)+'ms');
}}

// ── LOG ──────────────────────────────────────────────────────
function logAdd(op,msg){{
  var el=document.getElementById('eng-log');
  var d=document.createElement('div');
  d.className='log-entry';
  d.innerHTML='<span class="op">'+op+'</span>  <span class="ok">'+msg+'</span>';
  el.appendChild(d);
  el.scrollTop=el.scrollHeight;
}}

// ── CMD ──────────────────────────────────────────────────────
function cmdRun(){{
  var v=document.getElementById('cmd-input').value.trim();
  if(!v)return;
  document.getElementById('cmd-input').value='';
  try{{
    var r=eval(v);
    logAdd('CMD',String(JSON.stringify(r)).slice(0,160));
  }}catch(e){{logAdd('ERR',e.message);}}
}}
document.getElementById('cmd-input').addEventListener('keydown',function(e){{
  if(e.key==='Enter')cmdRun();
}});

// ── BOOT LOG ─────────────────────────────────────────────────
logAdd('BOOT','ENG {VERSION} · {TIMESTAMP} · git:{GIT}');
logAdd('MODULES',MODULES_OK?'6/6 ALL OK ✓':'CHECK CONSOLE');
console.log('%c⬡ ENG {VERSION} — MASTER CONTROL','color:#a78bfa;font-size:14px;font-weight:bold');
</script>
</body></html>"""

OUT.write_text(HTML, encoding="utf-8")
size_kb = len(HTML) // 1024
print(f"\n[OK] {OUT.name}  {size_kb}KB")
print(f"[OK] https://vsavytsk1.github.io/Mnetv1/shell/eng_{VERSION}.html")

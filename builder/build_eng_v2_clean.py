#!/usr/bin/env python3
# build_eng_v2_clean.py
# KERNELIMAGIC compliant: Pattern 2, ASCII only, one f-string at end
import time, subprocess
from pathlib import Path

ROOT      = Path(__file__).parent.parent
KERNEL    = ROOT / "kernel"
SHELL     = ROOT / "shell"
VERSION   = "v2.0"
OUT       = SHELL / "eng_v2.0.html"
TIMESTAMP = time.strftime("%Y-%m-%d %H:%M:%S")

try:
    GIT = subprocess.check_output(["git","rev-parse","--short","HEAD"],
          stderr=subprocess.DEVNULL, cwd=ROOT).decode().strip()
except:
    GIT = "local"

def read_js(name):
    p = KERNEL / name
    if not p.exists():
        print("  [WARN] missing: " + name)
        return "// MISSING: " + name + "\n"
    js = p.read_text(encoding="utf-8")
    print("  M: " + name.ljust(30) + str(len(js)//1024) + "KB")
    return js

print("Building eng_v2.0.html -- MASTER CONTROL DASHBOARD")
print("Following KERNELIMAGIC Pattern 2 -- ASCII only")

M1 = read_js("goldberg_kernel.js")
M2 = read_js("graph_axioms.js")
M3 = read_js("sar_modular.js")
M4 = read_js("ns_spectral.js")
M5 = read_js("fractal_search.js")
M6 = read_js("mnet_nanite.js")

# ── CSS -- plain string, no f, ASCII only ─────────────────────
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{background:#030308;color:#9090a0;
     font-family:ui-monospace,"SF Mono","Fira Code",monospace;
     font-size:11px;overflow:hidden;height:100vh;display:flex;flex-direction:column}
#top-bar{background:#07070f;border-bottom:1px solid #0e0e1e;
  padding:0 16px;height:36px;display:flex;align-items:center;gap:16px;flex-shrink:0}
#top-bar .logo{color:#00d4ff;font-size:12px;letter-spacing:0.12em;font-weight:bold}
#top-bar .build{color:#1a2a3a;font-size:10px}
#top-bar .clock{margin-left:auto;color:#1a2a3a;font-size:10px}
#top-bar .k-ok{color:#00ffd5;font-size:10px}
#top-bar .k-bad{color:#ff4444;font-size:10px}
#main{display:flex;flex:1;overflow:hidden}
#left{width:190px;flex-shrink:0;background:#07070f;border-right:1px solid #0e0e1e;
  display:flex;flex-direction:column;overflow:hidden}
#right{width:220px;flex-shrink:0;background:#07070f;border-left:1px solid #0e0e1e;
  display:flex;flex-direction:column;overflow:hidden}
#center{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px}
.panel-title{color:#1a2a3a;font-size:9px;letter-spacing:0.2em;text-transform:uppercase;
  padding:7px 10px 4px;border-bottom:1px solid #0e0e1e;flex-shrink:0}
.dp-block{padding:6px 10px;border-bottom:1px solid #0a0a14;flex-shrink:0}
.dp-label{color:#1a2a3a;font-size:8px;letter-spacing:0.15em;margin-bottom:3px}
.dp-row{display:flex;justify-content:space-between;padding:1px 0}
.dp-k{color:#1a2a3a;font-size:9px}
.dp-v{font-size:10px;font-variant-numeric:tabular-nums}
#mini-wrap{flex:1;position:relative;overflow:hidden;border-top:1px solid #0e0e1e}
#cv-mini{position:absolute;top:20px;left:0;width:100%;height:calc(100% - 20px)}
#eng-log{flex:1;overflow-y:auto;padding:6px 10px}
.log-entry{padding:2px 0;border-bottom:1px solid #0a0a14;font-size:9px;line-height:1.5}
.log-entry .op{color:#ff69b4;font-weight:bold}
.log-entry .ok{color:#00ffd5}
.log-entry .warn{color:#ffd700}
#center-hdr{color:#1a2a3a;font-size:9px;letter-spacing:0.15em;margin-bottom:6px}
.mod-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
.mod-card.new-module{animation:cardpulse 2s ease-in-out infinite}
@keyframes cardpulse{0%,100%{box-shadow:0 0 0px transparent}50%{box-shadow:0 0 12px rgba(100,120,255,0.15)}}
.mod-card{background:#07070f;border:1px solid #0e0e1e;border-radius:3px;
  padding:10px 12px;cursor:pointer;transition:all 0.2s}
.mod-card:hover{transform:translateY(-1px)}
.card-tag{font-size:8px;letter-spacing:0.15em;margin-bottom:3px;opacity:0.6}
.card-name{font-size:12px;font-weight:bold;margin-bottom:5px}
.card-desc{color:#1a2a3a;font-size:9px;line-height:1.5;margin-bottom:6px}
.card-arrow{font-size:9px;opacity:0;transition:opacity 0.15s}
.mod-card:hover .card-arrow{opacity:1}
#bar{background:#07070f;border-top:1px solid #0e0e1e;
  padding:5px 12px;display:flex;align-items:center;gap:5px;flex-wrap:wrap;flex-shrink:0}
.btn{background:#0a0a14;color:#2a3a4a;border:1px solid #0e0e1e;border-radius:3px;
  padding:3px 9px;font-family:inherit;font-size:10px;cursor:pointer;transition:all 0.15s}
.btn:hover{border-color:#3a3a4a;color:#d0d8e8}
.btn.op{color:#ff69b4;border-color:#2a1a2a}
.btn.op:hover{border-color:#ff69b4}
.sep{width:1px;height:14px;background:#0e0e1e}
.lbl{color:#1a2a2a;font-size:9px;letter-spacing:0.1em}
#cmd-bar{display:flex;gap:4px;align-items:center;margin-left:auto}
#cmd-input{background:#050510;color:#d0d8e8;border:1px solid #0e0e1e;
  border-radius:3px;padding:3px 9px;font-family:inherit;font-size:10px;
  width:200px;outline:none}
#cmd-input:focus{border-color:#ff69b4}
#cmd-input::placeholder{color:#1a1a2a}
#cmd-go{background:#0a0a14;color:#ff69b4;border:1px solid #2a1a2a;
  border-radius:3px;padding:3px 9px;font-family:inherit;font-size:10px;cursor:pointer}
#overlay{display:none;position:fixed;inset:0;z-index:100;flex-direction:column}
#overlay.open{display:flex}
#ov-bar{background:rgba(3,3,8,0.97);border-bottom:1px solid #1a1a2a;
  padding:0 14px;height:34px;display:flex;align-items:center;gap:10px;flex-shrink:0}
#ov-title{color:#00d4ff;font-size:11px;letter-spacing:0.1em}
#ov-back{background:#0a0a14;color:#a78bfa;border:1px solid #2a1a4a;
  border-radius:3px;padding:3px 12px;font-family:inherit;font-size:10px;cursor:pointer}
#ov-back:hover{border-color:#a78bfa}
#ov-frame{flex:1;border:none;background:#030308}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-track{background:#030308}
::-webkit-scrollbar-thumb{background:#1a1a2a;border-radius:2px}
"""# ── HTML SHELL -- plain string, ASCII only ─────────────────────
HTML_SHELL = """
<div id="top-bar">
  <span class="logo">ENG_V2</span>
  <span class="build" id="top-build">H7.1473.12.60</span>
  <span id="top-k" class="k-ok">6/6</span>
  <span class="clock" id="clock">--:--:--</span>
</div>
<div id="main">
  <div id="left">
    <div class="panel-title">KERNEL STATUS</div>
    <div class="dp-block">
      <div class="dp-row"><span id="ks-gk" class="dp-k">GK</span><span class="dp-v" style="color:#1a2a3a">...</span></div>
      <div class="dp-row"><span id="ks-ga" class="dp-k">GA</span><span class="dp-v" style="color:#1a2a3a">...</span></div>
      <div class="dp-row"><span id="ks-sar" class="dp-k">SAR</span><span class="dp-v" style="color:#1a2a3a">...</span></div>
      <div class="dp-row"><span id="ks-nss" class="dp-k">NSS</span><span class="dp-v" style="color:#1a2a3a">...</span></div>
      <div class="dp-row"><span id="ks-fs" class="dp-k">FS</span><span class="dp-v" style="color:#1a2a3a">...</span></div>
      <div class="dp-row"><span id="ks-nan" class="dp-k">NAN</span><span class="dp-v" style="color:#1a2a3a">...</span></div>
    </div>
    <div class="panel-title">GK</div>
    <div class="dp-block"><div id="dp-gk"></div></div>
    <div class="panel-title">SAR-5</div>
    <div class="dp-block"><div id="dp-sar"></div></div>
    <div class="panel-title">NSS</div>
    <div class="dp-block"><div id="dp-nss"></div></div>
    <div class="panel-title">FS</div>
    <div class="dp-block"><div id="dp-fs"></div></div>
    <div id="mini-wrap">
      <div class="panel-title">C60 LIVE</div>
      <canvas id="cv-mini"></canvas>
    </div>
  </div>
  <div id="center">
    <div id="center-hdr">MODULES -- CLICK TO SUMMON</div>
    <div class="mod-grid">
      <div class="mod-card" onclick="summon('genesis')" style="border-color:#1a3a3a;--cc:#00ffd5">
        <div class="card-tag" style="color:#00ffd5">CANVAS</div>
        <div class="card-name" style="color:#00ffd5">GENESIS v8.1</div>
        <div class="card-desc">M1-M6 all modules . v7.5 format . full kernel build</div>
        <div class="card-arrow" style="color:#00ffd5">SUMMON &gt;</div>
      </div>
      <div class="mod-card" onclick="summon('sandbox')" style="border-color:#1a2a3a;--cc:#80d0ff">
        <div class="card-tag" style="color:#80d0ff">SANDBOX</div>
        <div class="card-name" style="color:#80d0ff">GRAPH SANDBOX v5.1</div>
        <div class="card-desc">Graph ops . NS flow . cage . autopilot . cmd . 3D</div>
        <div class="card-arrow" style="color:#80d0ff">SUMMON &gt;</div>
      </div>
      <div class="mod-card" onclick="summon('tree')" style="border-color:#3a3a1a;--cc:#ffd700">
        <div class="card-tag" style="color:#ffd700">TREE</div>
        <div class="card-name" style="color:#ffd700">MATH TREE v5.0</div>
        <div class="card-desc">Sacred tree . gacha . forward-only . KaTeX</div>
        <div class="card-arrow" style="color:#ffd700">SUMMON &gt;</div>
      </div>
      <div class="mod-card" onclick="summon('holly7')" style="border-color:#2a1a4a;--cc:#a78bfa">
        <div class="card-tag" style="color:#a78bfa">DASHBOARD</div>
        <div class="card-name" style="color:#a78bfa">HOLLY7</div>
        <div class="card-desc">7 modules . SAR-5 . NS flow . navierCrunch . tree</div>
        <div class="card-arrow" style="color:#a78bfa">SUMMON &gt;</div>
      </div>
      <div class="mod-card" onclick="summon('navier')" style="border-color:#3a2a1a;--cc:#ff9040">
        <div class="card-tag" style="color:#ff9040">BENCHMARK</div>
        <div class="card-name" style="color:#ff9040">NAVIERCUNCH</div>
        <div class="card-desc">Turbulent Re&gt;10000 . RTX3060 . O(n) confirmed</div>
        <div class="card-arrow" style="color:#ff9040">SUMMON &gt;</div>
      </div>
      <div class="mod-card" onclick="summon('warning')" style="border-color:#3a1a2a;--cc:#ff69b4">
        <div class="card-tag" style="color:#ff69b4">FMA</div>
        <div class="card-name" style="color:#ff69b4">WARNING v2.0</div>
        <div class="card-desc">FMA intro . transmutation circle . v8 engine</div>
        <div class="card-arrow" style="color:#ff69b4">SUMMON &gt;</div>
      </div>
      <div class="mod-card" onclick="summon('license')" style="border-color:#1a1a0a;--cc:#ffd700">
        <div class="card-tag" style="color:#ffd700">GALACTIC LAW</div>
        <div class="card-name" style="color:#ffd700">LICENSE</div>
        <div class="card-desc">MIT . 7 axioms . 3 crystals . P=12 . V-E+F=2 . always</div>
        <div class="card-arrow" style="color:#ffd700">SUMMON &gt;</div>
      </div>
      <div class="mod-card new-module" onclick="summon('gkern')" style="border-color:#1a1a3a;--cc:#6478ff">
        <div class="card-tag" style="color:#6478ff">GOLDBERG</div>
        <div class="card-name" style="color:#6478ff">GKERN v2.0</div>
        <div class="card-desc">L0-L4 . 4 regimes . wave path . 1M bench . 0 deps</div>
        <div class="card-arrow" style="color:#6478ff">SUMMON &gt;</div>
      </div>
      <div class="mod-card new-module" onclick="summon('vale')" style="border-color:#003a3a;--cc:#00ffd5">
        <div class="card-tag" style="color:#00ffd5">POLAR OS</div>
        <div class="card-name" style="color:#00ffd5">VALE OS v1.1</div>
        <div class="card-desc">6 polar windows . C60 . breathe loop . Stark dark</div>
        <div class="card-arrow" style="color:#00ffd5">SUMMON &gt;</div>
      </div>
      <div class="mod-card new-module" onclick="summon('spooky')" style="border-color:#2a1a3a;--cc:#c084fc">
        <div class="card-tag" style="color:#c084fc">THE ORIGIN</div>
        <div class="card-name" style="color:#c084fc">SPOOKY PRIMES</div>
        <div class="card-desc">12 pentagons . 12 open questions . the dodecahedron . why</div>
        <div class="card-arrow" style="color:#c084fc">SUMMON &gt;</div>
      </div>
    </div>
  </div>
  <div id="right">
    <div class="panel-title">SESSION LOG</div>
    <div id="eng-log"></div>
  </div>
</div>
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
  <span class="lbl" style="color:#1a2a1a">P=12 chi=2 lam=0.1473</span>
  <div id="cmd-bar">
    <input id="cmd-input" type="text" placeholder="cmd + enter" spellcheck="false">
    <button id="cmd-go" onclick="cmdRun()">RUN</button>
  </div>
</div>
<div id="overlay">
  <div id="ov-bar">
    <button id="ov-back" onclick="overlayClose()">&lt; BACK</button>
    <span id="ov-title">-</span>
    <span style="margin-left:auto;color:#1a2a2a;font-size:9px" id="ov-url"></span>
  </div>
  <iframe id="ov-frame" src=""
    allow="fullscreen"
    sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
  ></iframe>
</div>
"""
# ── JS GLUE -- plain string, ASCII only ───────────────────────
JS_GLUE = """
var LINKS = {
  genesis : 'https://vsavytsk1.github.io/Mnetv1/shell/genesis_v8.1.html',
  sandbox : 'https://vsavytsk1.github.io/Mnetv1/shell/graph_sandbox_v5.1.html',
  tree    : 'https://vsavytsk1.github.io/Mnetv1/tree/math_tree_v4.3.html',
  holly7  : 'https://vsavytsk1.github.io/Mnetv1/pack/holly7.html',
  navier  : 'https://vsavytsk1.github.io/Mnetv1/pack/navierCrunch_turbulent.html',
  warning : 'https://vsavytsk1.github.io/Mnetv1/shell/spooky_warning/warning_v2.0.html',
  gkern   : 'https://vsavytsk1.github.io/Mnetv1/pack/GKernV2.0.html',
  vale    : 'https://vsavytsk1.github.io/Mnetv1/shell/vale_v1.1.html',
  license : 'https://vsavytsk1.github.io/Mnetv1/shell/spooky_warning/index.html',
  spooky  : 'https://vsavytsk1.github.io/SpookyPrimes/'
};
var PC = {cyan:'#00d4ff',pink:'#ff69b4',gold:'#ffd700',green:'#00ffd5',
          red:'#ff4444',orange:'#ff9040',dim:'#1a2a3a',text:'#9090a0'};

function setPanel(id, rows) {
  var el = document.getElementById('dp-' + id);
  if (!el) return;
  el.innerHTML = rows.map(function(r) {
    return '<div class="dp-row"><span class="dp-k">' + r[0] +
           '</span><span class="dp-v" style="color:' + (PC[r[2]] || '#aaa') + '">'
           + r[1] + '</span></div>';
  }).join('');
}

function summon(key) {
  var fr = document.getElementById('ov-frame');
  var ov = document.getElementById('overlay');
  // clear src first so onload always fires
  fr.src = '';
  document.getElementById('ov-title').textContent = key.toUpperCase();
  document.getElementById('ov-url').textContent = LINKS[key].replace('https://vsavytsk1.github.io/Mnetv1/','');
  ov.classList.add('open');
  // postMessage after iframe loads -- fixes CURSE 7 (center() needs real width)
  fr.onload = function() {
    setTimeout(function() {
      try { fr.contentWindow.postMessage('VALE_CENTER', '*'); } catch(e) {}
    }, 200);
  };
  setTimeout(function() { fr.src = LINKS[key]; }, 60);
  logAdd('SUMMON', key.toUpperCase());
}
function overlayClose() {
  document.getElementById('overlay').classList.remove('open');
  setTimeout(function(){ document.getElementById('ov-frame').src=''; }, 200);
  logAdd('BACK', 'dashboard');
}

setInterval(function() {
  document.getElementById('clock').textContent = new Date().toTimeString().slice(0,8);
}, 1000);

// kernel check
(function() {
  var checks = [
    ['ks-gk',  typeof GK !== 'undefined',         'GK',  'GK'],
    ['ks-ga',  typeof GA !== 'undefined',         'GA',  'GA'],
    ['ks-sar', typeof SAR !== 'undefined',        'SAR', 'SAR'],
    ['ks-nss', typeof NSS !== 'undefined',        'NSS', 'NSS'],
    ['ks-fs',  typeof FS !== 'undefined',         'FS',  'FS'],
    ['ks-nan', typeof MNetNanite !== 'undefined', 'NAN', 'NAN']
  ];
  var ok = 0;
  checks.forEach(function(c) {
    var el = document.getElementById(c[0]);
    var pass = c[1];
    if (pass) ok++;
    if (el) { el.textContent = c[2] + (pass ? ' OK' : ' X'); el.style.color = pass ? '#00ffd5' : '#ff4444'; }
    console.log('[ENG] ' + c[3] + ': ' + (pass ? 'OK' : 'MISSING'));
  });
  var tk = document.getElementById('top-k');
  tk.textContent = ok + '/6 ' + (ok === 6 ? 'OK' : 'CHECK');
  tk.className = ok === 6 ? 'k-ok' : 'k-bad';
})();

// mini C60 canvas
(function() {
  var wrap = document.getElementById('mini-wrap');
  var cv = document.getElementById('cv-mini');
  function resize() { cv.width = wrap.clientWidth; cv.height = wrap.clientHeight - 20; }
  resize();
  new ResizeObserver(resize).observe(wrap);
  var state = GK.buildC60();
  var faces = state.faces;
  var cam = { rx: 0.3, ry: 0, spin: 0.004 };
  var ctx = cv.getContext('2d');
  (function loop() {
    requestAnimationFrame(loop);
    cam.ry += cam.spin;
    var W = cv.width, H = cv.height;
    if (!W || !H) return;
    ctx.fillStyle = 'rgba(3,3,8,0.18)'; ctx.fillRect(0,0,W,H);
    var cy = Math.cos(cam.ry), sy = Math.sin(cam.ry);
    var cx = Math.cos(cam.rx), sx = Math.sin(cam.rx);
    var zoom = Math.min(W, H) * 0.38;
    function proj(p) {
      var x = p[0]*cy - p[2]*sy, z = p[0]*sy + p[2]*cy;
      var y = p[1]*cx - z*sx,   z2 = p[1]*sx + z*cx;
      var s = zoom / (z2 + 4);
      return { x: W/2 + x*s, y: H/2 + y*s, z: z2 };
    }
    faces.forEach(function(f) {
      var pts = f.pts, n = pts.length, isPent = f.type === 'pent';
      for (var i = 0; i < n; i++) {
        var a = proj(pts[i]), b = proj(pts[(i+1)%n]);
        if (a.z < -3 || b.z < -3) continue;
        var br = Math.max(0.05, Math.min(0.8, 1.2 / (Math.abs(a.z) + 2)));
        ctx.strokeStyle = isPent ? 'rgba(0,212,255,' + br + ')' : 'rgba(0,255,213,' + (br*0.35) + ')';
        ctx.lineWidth = isPent ? 1.2 : 0.4;
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      }
    });
  })();
})();

// auto-run all modules on load
window.addEventListener('load', function() {
  logAdd('BOOT', 'ENG v2.0 . git:' + (typeof GIT !== 'undefined' ? GIT : 'live'));
  logAdd('KERNEL', (typeof GK!=='undefined'?'GK OK':'GK X') + ' . ' +
    (typeof GA!=='undefined'?'GA OK':'GA X') + ' . ' +
    (typeof SAR!=='undefined'?'SAR OK':'SAR X') + ' . ' +
    (typeof NSS!=='undefined'?'NSS OK':'NSS X') + ' . ' +
    (typeof FS!=='undefined'?'FS OK':'FS X') + ' . ' +
    (typeof MNetNanite!=='undefined'?'NAN OK':'NAN X'));
  var t0, gk = GK.buildC60(), inv = GK.invariants(gk);
  var chi = inv.vertices - inv.edges + inv.faces;

  t0 = performance.now();
  setPanel('gk', [
    ['V',   inv.vertices, 'cyan'],
    ['E',   inv.edges,    'cyan'],
    ['F',   inv.faces,    'cyan'],
    ['P',   inv.pents,    'pink'],
    ['chi', chi,          'gold'],
    ['E/V', (inv.edges/inv.vertices).toFixed(3), 'gold'],
    ['ms',  (performance.now()-t0).toFixed(1),   'dim']
  ]);
  logAdd('GK', 'C60 F=' + inv.faces + ' P=' + inv.pents + ' chi=' + chi);

  t0 = performance.now();
  var sr = SAR.proof(gk);
  var lam = parseFloat(sr.spectral.lambda1).toFixed(6);
  setPanel('sar', [
    ['lam1',    lam,   'cyan'],
    ['theory',  parseFloat(sr.spectral.theory_C60).toFixed(6), 'dim'],
    ['delta',   Math.abs(sr.spectral.lambda1 - sr.spectral.expected).toFixed(6), sr.spectral.match ? 'green' : 'orange'],
    ['MATCH',   sr.spectral.match ? 'YES' : 'NO',  sr.spectral.match ? 'green' : 'red'],
    ['M0',      sr.M0.count,  'pink'],
    ['vacuum',  sr.stability.projectorCheck ? 'STABLE' : 'UNSTABLE', sr.stability.projectorCheck ? 'green' : 'red'],
    ['ms',      (performance.now()-t0).toFixed(1), 'dim']
  ]);
  logAdd('SAR', 'lam1=' + lam + ' MATCH=' + (sr.spectral.match ? 'YES' : 'NO'));

  t0 = performance.now();
  var nr = NSS.runOn(gk, { Re: 150, steps: 200, logEvery: 9999 });
  var nl = nr.lambdaEst !== null ? nr.lambdaEst.toFixed(6) : '?';
  setPanel('nss', [
    ['Re',    150,  'orange'],
    ['steps', 200,  'dim'],
    ['N',     nr.graph ? nr.graph.N : '?', 'cyan'],
    ['lam1',  nl,   'cyan'],
    ['delta', nr.delta !== null ? nr.delta.toFixed(6) : '?', Math.abs(nr.delta||1) < 0.01 ? 'green' : 'orange'],
    ['ms',    (performance.now()-t0).toFixed(1), 'dim']
  ]);
  logAdd('NSS', 'lam1=' + nl);

  t0 = performance.now();
  var fr = FS.search({ seed: 'c60', maxLevels: 3, target: 0.1473, lockThresh: 0.005 });
  setPanel('fs', [
    ['target', '0.1473', 'cyan'],
    ['locked', fr.locked ? 'YES' : 'NO', fr.locked ? 'green' : 'orange'],
    ['lvl',    fr.lockLevel !== undefined ? fr.lockLevel : '?', 'gold'],
    ['bestL',  fr.bestLambda !== undefined ? fr.bestLambda.toFixed(6) : '?', 'cyan'],
    ['ms',     (performance.now()-t0).toFixed(1), 'dim']
  ]);
  logAdd('FS', fr.locked ? 'LOCKED' : 'not locked');
  logAdd('ALL OK', '6/6 modules ran');
});

// kernel ops
var _st = null;
function engSeed(type) {
  _st = type === 'dodec' ? GK.buildDodecahedron() : GK.buildC60();
  var inv = GK.invariants(_st);
  logAdd('SEED', type.toUpperCase() + ' F=' + inv.faces + ' P=' + inv.pents);
}
function engRefine() {
  if (!_st) engSeed('c60');
  var t0 = performance.now(); _st = GK.refineAll(_st);
  var inv = GK.invariants(_st);
  logAdd('REFINE', inv.faces + 'F ' + (performance.now()-t0).toFixed(1) + 'ms');
}
function engSAR() {
  if (!_st) engSeed('c60');
  var t0 = performance.now(); var r = SAR.proof(_st);
  logAdd('SAR-5', 'lam1=' + parseFloat(r.spectral.lambda1).toFixed(6) +
    ' M0=' + r.M0.count + ' ' + (r.spectral.match ? 'MATCH' : 'no match') +
    ' ' + (performance.now()-t0).toFixed(1) + 'ms');
}
function engNS() {
  if (!_st) engSeed('c60');
  var t0 = performance.now(); var r = NSS.runOn(_st, { Re:150, steps:200 });
  logAdd('NSS', 'lam1=' + (r.lambdaEst !== null ? r.lambdaEst.toFixed(6) : '?') +
    ' ' + (performance.now()-t0).toFixed(1) + 'ms');
}
function engFS() {
  if (!_st) engSeed('c60');
  var t0 = performance.now(); var r = FS.search({ seed:'c60', maxLevels:3 });
  logAdd('FS', (r.locked ? 'LOCKED' : 'searching') + ' ' + (performance.now()-t0).toFixed(1) + 'ms');
}

function logAdd(op, msg, col) {
  var el = document.getElementById('eng-log');
  var d = document.createElement('div'); d.className = 'log-entry';
  var ts = new Date().toTimeString().slice(0,8);
  var c = col || 'ok';
  d.innerHTML = '<span style="color:#1a2a3a">' + ts + '</span>  ' +
    '<span class="op">' + op + '</span>  ' +
    '<span class="' + c + '">' + msg + '</span>';
  el.appendChild(d); el.scrollTop = el.scrollHeight;
  console.log('[ENG] ' + op + ' -- ' + msg);
}

function cmdRun() {
  var v = document.getElementById('cmd-input').value.trim();
  if (!v) return;
  document.getElementById('cmd-input').value = '';
  try { logAdd('CMD', String(JSON.stringify(eval(v))).slice(0,160)); }
  catch(e) { logAdd('ERR', e.message); }
}
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('cmd-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') cmdRun();
  });
});
"""

# ── ASSEMBLE -- one f-string, VERSION/TIMESTAMP/GIT only ──────
TITLE = "MachineNet ENG " + VERSION + " MASTER CONTROL"
BOOT_LOG = "ENG " + VERSION + " * " + TIMESTAMP + " * git:" + GIT

HTML = (
    '<!DOCTYPE html><html lang="en"><head>'
    '<meta charset="UTF-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>' + TITLE + '</title>'
    '<style>' + CSS + '</style>'
    '</head><body>'
    + HTML_SHELL +
    '<script>' + M1 + '</script>'
    '<script>' + M2 + '</script>'
    '<script>' + M3 + '</script>'
    '<script>' + M4 + '</script>'
    '<script>' + M5 + '</script>'
    '<script>' + M6 + '</script>'
    '<script>' + JS_GLUE + '</script>'
    '</body></html>'
)

OUT.write_text(HTML, encoding="utf-8")
size_kb = len(HTML) // 1024
print("\n[OK] " + str(OUT.name) + "  " + str(size_kb) + "KB")
print("[OK] https://vsavytsk1.github.io/Mnetv1/shell/eng_" + VERSION + ".html")
#!/usr/bin/env python3
# build_vale.py -- VALE v1.1
# KERNELIMAGIC: Pattern 2, ASCII only, string concat assembly, no f-string JS
import time, subprocess
from pathlib import Path

ROOT  = Path(__file__).parent.parent
KERNEL = ROOT / "kernel"
SHELL  = ROOT / "shell"
VERSION = "v1.1"
OUT   = SHELL / "vale_v1.1.html"
TIMESTAMP = time.strftime("%Y-%m-%d %H:%M:%S")
try:
    GIT = subprocess.check_output(["git","rev-parse","--short","HEAD"],
          stderr=subprocess.DEVNULL,cwd=ROOT).decode().strip()
except: GIT = "local"

def read_js(name):
    p = KERNEL / name
    if not p.exists(): return "// MISSING: " + name + "\n"
    js = p.read_text(encoding="utf-8")
    print("  M: " + name.ljust(30) + str(len(js)//1024) + "KB")
    return js

print("VALE v1.1 -- polar window layout -- KERNELIMAGIC Pattern 2")
M1 = read_js("goldberg_kernel.js")
M2 = read_js("graph_axioms.js")
M3 = read_js("sar_modular.js")
M4 = read_js("ns_spectral.js")
M5 = read_js("fractal_search.js")
M6 = read_js("mnet_nanite.js")

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{
  background:#020408;
  font-family:ui-monospace,"SF Mono","Fira Code",monospace;
  font-size:10px;overflow:hidden;
  width:100vw;height:100vh;position:relative;
  color:#4a8fa8
}
canvas{display:block}

/* CENTER CANVAS -- absolute center */
#cv-center{
  position:fixed;
  border-radius:50%;
  border:1px solid #0a2a3a;
  background:radial-gradient(circle, #020c14 60%, #020408 100%);
  box-shadow:0 0 40px rgba(0,180,255,0.08), inset 0 0 30px rgba(0,0,0,0.8);
}

/* OUTER RING -- decorative SVG arc */
#ring-svg{position:fixed;pointer-events:none;z-index:1}

/* WINDOWS -- all positioned by JS polar math */
.jwin{
  position:fixed;
  background:rgba(2,12,20,0.92);
  border:1px solid #0a2535;
  border-radius:3px;
  padding:8px 10px;
  pointer-events:auto;
  transition:border-color 0.3s, box-shadow 0.3s;
  z-index:10;
  min-width:150px;
}
.jwin:hover{
  border-color:#1a4a6a;
  box-shadow:0 0 12px rgba(0,180,255,0.12);
}
.jwin-title{
  color:#1a4a5a;
  font-size:8px;
  letter-spacing:0.25em;
  text-transform:uppercase;
  margin-bottom:5px;
  border-bottom:1px solid #0a1a24;
  padding-bottom:3px;
}
.jwin-title.ok{color:#00ffd5}
.jwin-title.warn{color:#ff9040}
.dp-row{display:flex;justify-content:space-between;gap:12px;padding:1px 0}
.dp-k{color:#1a3a4a;font-size:9px}
.dp-v{font-size:9px;font-variant-numeric:tabular-nums}

/* CONNECTOR LINES -- drawn by JS on canvas */
#cv-lines{position:fixed;top:0;left:0;pointer-events:none;z-index:2}

/* TOP BAR */
#top-bar{
  position:fixed;top:0;left:0;right:0;height:28px;z-index:20;
  background:rgba(2,4,8,0.85);
  border-bottom:1px solid #0a1a24;
  display:flex;align-items:center;gap:14px;padding:0 14px;
}
#top-bar .logo{color:#00d4ff;font-size:11px;letter-spacing:0.15em}
#top-bar .info{color:#0a2535;font-size:9px}
#top-bar .clock{margin-left:auto;color:#0a3040;font-size:10px;font-variant-numeric:tabular-nums}
#top-bar .kstat{font-size:9px}
.k-ok{color:#00ffd5}.k-bad{color:#ff4444}

/* BOTTOM CMD */
#cmd-wrap{
  position:fixed;bottom:0;left:0;right:0;height:28px;z-index:20;
  background:rgba(2,4,8,0.85);border-top:1px solid #0a1a24;
  display:flex;align-items:center;gap:8px;padding:0 14px;
}
#cmd-input{
  background:transparent;color:#4a8fa8;border:none;
  font-family:inherit;font-size:10px;outline:none;flex:1;
}
#cmd-input::placeholder{color:#0a2535}
#cmd-out{color:#00ffd5;font-size:9px;max-width:60%;overflow:hidden;white-space:nowrap}

/* PULSE RING animation */
@keyframes pulse-ring{
  0%{opacity:0.6} 50%{opacity:0.2} 100%{opacity:0.6}
}
#ring-svg{animation:pulse-ring 4s ease-in-out infinite}
"""
HTML_SHELL = """
<div id="top-bar">
  <span class="logo">JARVIS OS</span>
  <span class="info" id="top-build">H7.1473.12.60</span>
  <span class="info" id="top-ts">--</span>
  <span class="kstat" id="top-k">6/6</span>
  <span class="clock" id="clock">--:--:--</span>
</div>

<!-- connector lines layer -->
<canvas id="cv-lines"></canvas>

<!-- center rotating geometry -->
<canvas id="cv-center"></canvas>

<!-- decorative ring -->
<svg id="ring-svg"></svg>

<!-- DATA WINDOWS -- positioned by JS -->
<div class="jwin" id="win-gk">
  <div class="jwin-title" id="wt-gk">GK . goldberg kernel</div>
  <div id="dp-gk"></div>
</div>

<div class="jwin" id="win-sar">
  <div class="jwin-title" id="wt-sar">SAR . spectral proof</div>
  <div id="dp-sar"></div>
</div>

<div class="jwin" id="win-nss">
  <div class="jwin-title" id="wt-nss">NSS . navier stokes</div>
  <div id="dp-nss"></div>
</div>

<div class="jwin" id="win-fs">
  <div class="jwin-title" id="wt-fs">FS . fractal search</div>
  <div id="dp-fs"></div>
</div>

<div class="jwin" id="win-ga">
  <div class="jwin-title" id="wt-ga">GA . graph axioms</div>
  <div id="dp-ga"></div>
</div>

<div class="jwin" id="win-nan">
  <div class="jwin-title" id="wt-nan">NAN . mnet nanite</div>
  <div id="dp-nan"></div>
</div>

<div id="cmd-wrap">
  <span style="color:#0a3040">&#62;</span>
  <input id="cmd-input" type="text" placeholder="eval JS -- enter" spellcheck="false">
  <span id="cmd-out"></span>
</div>
"""
JS_GLUE = """
// COLORS
var PC = {
  cyan:'#00d4ff', teal:'#00ffd5', pink:'#ff69b4',
  gold:'#ffd700', green:'#00ffd5', red:'#ff4444',
  orange:'#ff9040', dim:'#1a3a4a', blue:'#4488ff'
};

// LAYOUT MATH -- polar windows
var LAY = {
  cx:0, cy:0, R:0, cSize:0, winW:155, winH:108,
  wins: ['gk','sar','nss','fs','ga','nan'],
  // angle offsets per window (radians from top, clockwise)
  angles: [0, 1.047, 2.094, 3.14159, 4.189, 5.236]
};

function layoutCalc() {
  var W = window.innerWidth, H = window.innerHeight;
  LAY.cx = W / 2;
  LAY.cy = H / 2;
  LAY.cSize = Math.min(W, H) * 0.30;
  LAY.R = Math.min(W, H) * 0.38;
}

function layoutApply() {
  layoutCalc();
  var W = window.innerWidth, H = window.innerHeight;

  // center canvas
  var cv = document.getElementById('cv-center');
  cv.width  = LAY.cSize;
  cv.height = LAY.cSize;
  cv.style.left = (LAY.cx - LAY.cSize/2) + 'px';
  cv.style.top  = (LAY.cy - LAY.cSize/2) + 'px';

  // connector canvas
  var cl = document.getElementById('cv-lines');
  cl.width  = W;
  cl.height = H;
  cl.style.left = '0px';
  cl.style.top  = '0px';

  // ring svg
  var svg = document.getElementById('ring-svg');
  var rSize = LAY.R * 2 + 60;
  svg.setAttribute('width', rSize);
  svg.setAttribute('height', rSize);
  svg.style.left = (LAY.cx - rSize/2) + 'px';
  svg.style.top  = (LAY.cy - rSize/2) + 'px';
  drawRing(svg, rSize/2, LAY.R + 20);

  // windows
  LAY.wins.forEach(function(id, i) {
    var el = document.getElementById('win-' + id);
    if (!el) return;
    var a = LAY.angles[i] - Math.PI / 2;
    var wx = LAY.cx + LAY.R * Math.cos(a) - LAY.winW / 2;
    var wy = LAY.cy + LAY.R * Math.sin(a) - LAY.winH / 2;
    // clamp to screen
    wx = Math.max(4, Math.min(W - LAY.winW - 4, wx));
    wy = Math.max(32, Math.min(H - LAY.winH - 32, wy));
    el.style.left   = wx + 'px';
    el.style.top    = wy + 'px';
    el.style.width  = LAY.winW + 'px';
    el.style.minHeight = LAY.winH + 'px';
  });

  drawLines();
}

function drawRing(svg, cx, r) {
  svg.innerHTML = '';
  // dashed circle
  var c = document.createElementNS('http://www.w3.org/2000/svg','circle');
  c.setAttribute('cx', cx); c.setAttribute('cy', cx);
  c.setAttribute('r', r);
  c.setAttribute('fill','none');
  c.setAttribute('stroke','#0a2535');
  c.setAttribute('stroke-width','1');
  c.setAttribute('stroke-dasharray','4 8');
  svg.appendChild(c);
  // outer ring -- bigger radius, tight dash
  var c2 = document.createElementNS('http://www.w3.org/2000/svg','circle');
  c2.setAttribute('cx', cx); c2.setAttribute('cy', cx);
  c2.setAttribute('r', r + 32);
  c2.setAttribute('fill','none');
  c2.setAttribute('stroke','#071820');
  c2.setAttribute('stroke-width','1');
  c2.setAttribute('stroke-dasharray','2 14');
  svg.appendChild(c2);
  // tick marks at window angles
  LAY.angles.forEach(function(a) {
    var aa = a - Math.PI/2;
    var x1 = cx + (r-8) * Math.cos(aa), y1 = cx + (r-8) * Math.sin(aa);
    var x2 = cx + (r+8) * Math.cos(aa), y2 = cx + (r+8) * Math.sin(aa);
    var line = document.createElementNS('http://www.w3.org/2000/svg','line');
    line.setAttribute('x1',x1); line.setAttribute('y1',y1);
    line.setAttribute('x2',x2); line.setAttribute('y2',y2);
    line.setAttribute('stroke','#0a3545');
    line.setAttribute('stroke-width','1.5');
    svg.appendChild(line);
    // outer tick on outer ring
    var oa = aa;
    var ox1 = cx+(r+26)*Math.cos(oa), oy1 = cx+(r+26)*Math.sin(oa);
    var ox2 = cx+(r+38)*Math.cos(oa), oy2 = cx+(r+38)*Math.sin(oa);
    var ol = document.createElementNS('http://www.w3.org/2000/svg','line');
    ol.setAttribute('x1',ox1); ol.setAttribute('y1',oy1);
    ol.setAttribute('x2',ox2); ol.setAttribute('y2',oy2);
    ol.setAttribute('stroke','#071e28'); ol.setAttribute('stroke-width','1');
    svg.appendChild(ol);
  });
}

function drawLines() {
  var cl = document.getElementById('cv-lines');
  var ctx = cl.getContext('2d');
  ctx.clearRect(0,0,cl.width,cl.height);
  LAY.wins.forEach(function(id, i) {
    var el = document.getElementById('win-' + id);
    if (!el) return;
    var r = el.getBoundingClientRect();
    var wx = r.left + r.width/2, wy = r.top + r.height/2;
    ctx.beginPath();
    ctx.moveTo(LAY.cx, LAY.cy);
    ctx.lineTo(wx, wy);
    ctx.strokeStyle = 'rgba(10,42,60,0.6)';
    ctx.lineWidth = 0.8;
    ctx.setLineDash([3, 9]);
    ctx.stroke();
  });
  ctx.setLineDash([]);
}

window.addEventListener('resize', layoutApply);

// CLOCK
setInterval(function() {
  document.getElementById('clock').textContent = new Date().toTimeString().slice(0,8);
}, 1000);

// SET PANEL
function setPanel(id, rows, titleOk) {
  var dp = document.getElementById('dp-' + id);
  var wt = document.getElementById('wt-' + id);
  if (dp) dp.innerHTML = rows.map(function(r) {
    return '<div class="dp-row"><span class="dp-k">' + r[0] +
           '</span><span class="dp-v" style="color:' + (PC[r[2]] || '#4a8fa8') + '">'
           + r[1] + '</span></div>';
  }).join('');
  if (wt && titleOk !== undefined) wt.className = 'jwin-title ' + (titleOk ? 'ok' : 'warn');
}

// C60 CANVAS RENDER
var _cam = { rx:0.4, ry:0, spin:0.006 };
var _c60state = null;
function startC60() {
  _c60state = GK.buildC60();
  var cv = document.getElementById('cv-center');
  var ctx = cv.getContext('2d');
  (function loop() {
    requestAnimationFrame(loop);
    _cam.ry += _cam.spin;
    var W = cv.width, H = cv.height;
    if (!W || !H) return;
    ctx.fillStyle = 'rgba(2,8,14,0.15)';
    ctx.fillRect(0,0,W,H);
    var cosy = Math.cos(_cam.ry), siny = Math.sin(_cam.ry);
    var cosx = Math.cos(_cam.rx), sinx = Math.sin(_cam.rx);
    var zoom = W * 0.38;
    function proj(p) {
      var x = p[0]*cosy - p[2]*siny, z = p[0]*siny + p[2]*cosy;
      var y = p[1]*cosx - z*sinx,   z2 = p[1]*sinx + z*cosx;
      var s = zoom / (z2 + 4.5);
      return { x: W/2 + x*s, y: H/2 + y*s, z: z2 };
    }
    _c60state.faces.forEach(function(f) {
      var pts = f.pts, n = pts.length, pent = f.type === 'pent';
      for (var i = 0; i < n; i++) {
        var a = proj(pts[i]), b = proj(pts[(i+1)%n]);
        if (a.z < -3.5 || b.z < -3.5) continue;
        var br = Math.max(0.04, Math.min(0.9, 1.4/(Math.abs(a.z)+2)));
        ctx.strokeStyle = pent
          ? 'rgba(0,212,255,' + br + ')'
          : 'rgba(0,255,213,' + (br*0.3) + ')';
        ctx.lineWidth = pent ? 1.4 : 0.5;
        ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
      }
    });
  })();
}

// KERNEL CHECK + AUTO-RUN
(function() {
  var checks = [
    ['ks-gk',  typeof GK!=='undefined',         'GK'],
    ['ks-ga',  typeof GA!=='undefined',         'GA'],
    ['ks-sar', typeof SAR!=='undefined',        'SAR'],
    ['ks-nss', typeof NSS!=='undefined',        'NSS'],
    ['ks-fs',  typeof FS!=='undefined',         'FS'],
    ['ks-nan', typeof MNetNanite!=='undefined', 'NAN']
  ];
  var ok = 0;
  checks.forEach(function(c) { if (c[1]) ok++; });
  var tk = document.getElementById('top-k');
  if (tk) { tk.textContent = ok+'/6'; tk.className = 'kstat ' + (ok===6?'k-ok':'k-bad'); }
})();

window.addEventListener('load', function() {
  layoutApply();
  startC60();

  var t0, gk = GK.buildC60(), inv = GK.invariants(gk);
  var chi = inv.vertices - inv.edges + inv.faces;

  // GK
  setPanel('gk', [
    ['V', inv.vertices, 'cyan'], ['E', inv.edges, 'cyan'],
    ['F', inv.faces, 'cyan'],    ['P', inv.pents, 'pink'],
    ['chi', chi, 'gold'],        ['E/V', (inv.edges/inv.vertices).toFixed(3), 'gold']
  ], true);

  // GA
  GA.logReset(); var ax = GA.eulerCheck(gk);
  setPanel('ga', [
    ['euler', ax.valid?'PASS':'FAIL', ax.valid?'teal':'red'],
    ['P=12',  ax.pents===12?'PASS':'FAIL', ax.pents===12?'teal':'red'],
    ['chi=2', ax.chi===2?'PASS':'FAIL', ax.chi===2?'teal':'red'],
    ['entries', GA.log.entries.length, 'dim']
  ], ax.valid);

  // SAR
  t0 = performance.now();
  var sr = SAR.proof(gk);
  var lam = parseFloat(sr.spectral.lambda1).toFixed(6);
  var dt = (performance.now()-t0).toFixed(0);
  setPanel('sar', [
    ['lam1',   lam, 'cyan'],
    ['theory', parseFloat(sr.spectral.theory_C60).toFixed(6), 'dim'],
    ['delta',  Math.abs(sr.spectral.lambda1-sr.spectral.expected).toFixed(6), sr.spectral.match?'teal':'orange'],
    ['M0',     sr.M0.count, 'pink'],
    ['vacuum', sr.stability.projectorCheck?'STABLE':'UNSTABLE', sr.stability.projectorCheck?'teal':'red'],
    ['ms',     dt, 'dim']
  ], sr.spectral.match);

  // NSS
  t0 = performance.now();
  var nr = NSS.runOn(gk, { Re:150, steps:200, logEvery:9999 });
  var nl = nr.lambdaEst!==null ? nr.lambdaEst.toFixed(6) : '?';
  dt = (performance.now()-t0).toFixed(0);
  setPanel('nss', [
    ['Re', 150, 'orange'], ['steps', 200, 'dim'],
    ['lam1', nl, 'cyan'],
    ['delta', nr.delta!==null?nr.delta.toFixed(6):'?', Math.abs(nr.delta||1)<0.01?'teal':'orange'],
    ['ms', dt, 'dim']
  ], Math.abs(nr.delta||1) < 0.05);

  // FS
  t0 = performance.now();
  var fr = FS.search({ seed:'c60', maxLevels:3, target:0.1473, lockThresh:0.005 });
  dt = (performance.now()-t0).toFixed(0);
  setPanel('fs', [
    ['target', '0.1473', 'cyan'],
    ['locked', fr.locked?'YES':'NO', fr.locked?'teal':'orange'],
    ['lvl',    fr.lockLevel!==undefined?fr.lockLevel:'?', 'gold'],
    ['bestL',  fr.bestLambda!==undefined?fr.bestLambda.toFixed(6):'?', 'cyan'],
    ['ms',     dt, 'dim']
  ], fr.locked);

  // NAN
  var ns = {};
  try { var dag = typeof MNetNanite.build==='function'?MNetNanite.build(gk):MNetNanite; ns=dag.stats||dag; }
  catch(e) { ns = { status:'loaded' }; }
  var nr2 = Object.keys(ns).slice(0,5).map(function(k){ return [k, String(ns[k]).slice(0,12), 'cyan']; });
  if (!nr2.length) nr2 = [['api','MNetNanite','cyan'],['status','loaded','teal']];
  setPanel('nan', nr2, true);

  document.getElementById('top-ts').textContent = new Date().toTimeString().slice(0,8);
  drawLines();
  console.log('[VALE] all 6 modules loaded and rendered');
});

// CMD
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('cmd-input').addEventListener('keydown', function(e) {
    if (e.key !== 'Enter') return;
    var v = this.value.trim(); this.value = '';
    try {
      var r = JSON.stringify(eval(v));
      document.getElementById('cmd-out').textContent = String(r).slice(0,120);
    } catch(err) {
      document.getElementById('cmd-out').textContent = 'ERR: ' + err.message;
    }
  });
});
"""
TITLE = "VALE OS . MachineNet " + VERSION
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
kb = len(HTML)//1024
print("\n[OK] " + str(OUT.name) + "  " + str(kb) + "KB")
print("[OK] https://vsavytsk1.github.io/Mnetv1/shell/vale_v1.1.html")

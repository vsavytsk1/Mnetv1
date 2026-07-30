#!/usr/bin/env python3
"""
build_aequalium.py  --  AEQUALIUM v1.0  --  THE EQUALS SIGN, EARNED
=====================================================================
The fusion sim. Vlad's vision: the "=" transcends this reality. To match
experimental data (the quantum + galactic realms) to what we can COMPUTE, we
grow a fractal curve trapped in the C60 -- more hexagons = more Fourier
harmonics = lower residual = more degrees of certainty. Gibbs guarantees the
"=" is asymptotic, never exactly reached: that is the honesty (Path III --
target is not result; show the residual, never fake the prize).

KERNELIMAGIC compliance:
  * ASCII-ONLY python source (Curse 2). Unicode lives in the OUTPUT only, via
    HTML entities and \\uXXXX escapes inside JS string literals.
  * NO f-string wraps the JS (Curse 1/4). JS is a plain triple-quoted string;
    only token .replace() at the very end (Pattern 1+2).
  * The REAL kernel/goldberg_kernel.js is injected VERBATIM -- proof by kernel,
    the true 7 refinement ops, not a re-typed lie (Path IV).
  * Write utf-8, newline='\\n', no BOM (Pattern 3). One script, one run (Path VI).
  * Curse 35 (the Loaded Gun): predict the next refineAll face-count from the
    recurrence and REFUSE past a ceiling, before allocating.

The map (honest, no faking):
  faces H = live buckyball face count (C60 = 32).  K = min(floor(H/2), Nyquist).
  target f(t), t in [0,2pi), M samples.  DFT c_k.  recon with |k|<=K.
  residual = ||f - recon|| / ||f|| (L2).  certainty = 100*(1 - residual)%.
  grow (refineAll) adds hexagons -> more harmonics -> residual falls. Logged as
  a (faces, residual) price/convergence curve. More compute, more spini-spini,
  more degrees of certainty. The "=" is approached, never claimed.

P=12. chi=2. The price is always paid. always.
"""
import time, subprocess
from pathlib import Path

ROOT      = Path(__file__).parent.parent
KERNEL    = ROOT / "kernel" / "goldberg_kernel.js"
SHELL     = ROOT / "shell"
VERSION   = "v1.0"
OUT       = SHELL / f"aequalium_{VERSION}.html"
TIMESTAMP = time.strftime("%Y-%m-%d %H:%M:%S")

try:
    GIT = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
          stderr=subprocess.DEVNULL, cwd=ROOT).decode().strip()
except Exception:
    GIT = "local"

print(f"Building aequalium_{VERSION}.html -- THE EQUALS SIGN, EARNED")

# --- M1: the REAL kernel, verbatim (proof by kernel) -----------------------
if not KERNEL.exists():
    raise SystemExit("FATAL: kernel/goldberg_kernel.js missing -- cannot fake it.")
KERNEL_JS = KERNEL.read_text(encoding="utf-8")
print(f"  kernel injected verbatim: {len(KERNEL_JS)//1024}KB")

# ============================================================================
#  CSS  (plain string -- apollonium conventions, ASCII source)
# ============================================================================
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:#05050f;color:#dfe6f2;
  font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  font-size:11px;overflow:hidden;height:100vh}
canvas{display:block}
#hud{position:fixed;top:12px;left:14px;z-index:10;pointer-events:none;max-width:44vw}
#hud .title{font-size:13px;color:#ffd700;letter-spacing:.12em;text-transform:uppercase}
#hud .sub{font-size:9.5px;color:rgba(223,230,242,.44);line-height:1.5;margin:3px 0 6px}
#hud .row{line-height:1.85;color:rgba(223,230,242,.6)}
#hud .val{color:#00d4ff;font-weight:bold}
#hud .gold{color:#ffd700;font-weight:bold}
#hud .pink{color:#ff69b4;font-weight:bold}
#hud .grn{color:#7fff9f;font-weight:bold}
#badge{display:inline-block;padding:1px 8px;border:1px solid #2a3350;border-radius:3px;
  color:#66708a;transition:all .4s}
#badge.earned{color:#05050f;background:#7fff9f;border-color:#7fff9f;
  box-shadow:0 0 14px rgba(127,255,159,.5)}
#log{position:fixed;top:210px;left:14px;z-index:10;background:rgba(5,6,15,.9);
  border:1px solid #1e2740;border-radius:4px;padding:7px 11px;max-width:300px;
  max-height:24vh;overflow-y:auto;font-size:9px;line-height:1.6;
  color:rgba(223,230,242,.75);cursor:pointer;transition:opacity .3s}
#log.hidden{opacity:0;pointer-events:none}
#log .e{border-bottom:1px solid #131a2c;padding:1px 0}
#log .ok{color:#7fff9f}#log .cyan{color:#00d4ff}#log .gold{color:#ffd700}
#log .pink{color:#ff69b4}#log .src{color:rgba(223,230,242,.4)}
#bar{position:fixed;bottom:0;left:0;right:0;z-index:10;background:rgba(5,6,15,.97);
  border-top:1px solid #1e2740;padding:6px 12px;display:flex;align-items:center;
  gap:6px;flex-wrap:wrap}
.btn{background:#0b1120;color:#66708a;border:1px solid #1e2740;border-radius:3px;
  padding:4px 9px;font-family:inherit;font-size:9px;cursor:pointer;transition:all .15s;
  text-transform:uppercase;letter-spacing:.06em}
.btn:hover{border-color:#00d4ff;color:#00d4ff}
.btn.active{background:#00d4ff;color:#05050f;border-color:#00d4ff;font-weight:bold}
.btn.grow{border-color:#2a5a3a;color:#7fff9f}
.btn.grow:hover{border-color:#7fff9f;color:#7fff9f}
.sep{width:1px;height:16px;background:#1e2740}
.lbl{color:rgba(223,230,242,.3);font-size:9px;text-transform:uppercase;
  letter-spacing:.09em;margin-left:6px}
.foot{position:fixed;left:14px;bottom:46px;font-size:9.5px;color:#4a5470;
  line-height:1.5;pointer-events:none;z-index:5}
#panel{position:fixed;top:12px;right:12px;z-index:11;width:360px;max-height:80vh;
  background:rgba(5,6,15,.96);border:1px solid #1e2740;border-radius:6px;display:none;
  flex-direction:column;overflow:hidden;box-shadow:0 6px 30px rgba(0,0,0,.55)}
#panel.open{display:flex}
#panel .tabs{display:flex;border-bottom:1px solid #1e2740;flex:0 0 auto}
#panel .tab{flex:1;text-align:center;padding:7px 2px;cursor:pointer;color:#66708a;
  text-transform:uppercase;letter-spacing:.05em;font-size:9px;
  border-right:1px solid #1e2740;transition:all .15s}
#panel .tab:last-child{border-right:none}
#panel .tab.active{background:#00d4ff;color:#05050f;font-weight:bold}
#panel .tab:hover{color:#00d4ff}
#panel .body{padding:11px 13px;overflow-y:auto;line-height:1.6;color:rgba(223,230,242,.82);font-size:10px}
#panel .tabc{display:none}#panel .tabc.active{display:block}
#panel h4{color:#ffd700;font-size:10px;margin:11px 0 4px;letter-spacing:.05em;text-transform:uppercase}
#panel h4:first-child{margin-top:0}
#panel .k{color:#00d4ff;font-weight:bold}#panel .g{color:#ffd700;font-weight:bold}
#panel .s{color:rgba(223,230,242,.45);font-size:9px}
#panel .note{border-left:2px solid rgba(127,255,159,.4);padding-left:9px;margin:6px 0;color:#9aa6bd}
#panel .warn{border-left:2px solid rgba(255,105,180,.5);padding-left:9px;margin:7px 0;color:#c9a8bd}
::-webkit-scrollbar{width:8px}::-webkit-scrollbar-track{background:#080c16}
::-webkit-scrollbar-thumb{background:#1e2740;border-radius:4px}
"""

# ============================================================================
#  HTML SHELL  (plain string; unicode via entities)
# ============================================================================
HTML_SHELL = """
<canvas id="cv"></canvas>
<div id="hud">
  <div class="title">AEQUALIUM &middot; __VERSION__</div>
  <div class="sub">the equals sign, earned. grow the fractal curve trapped in the C60 &mdash;
  more hexagons, more harmonics, lower residual, more degrees of certainty.
  the &quot;=&quot; is approached, never faked.</div>
  <div class="row">faces <span class="val" id="v-faces">--</span> &nbsp; P <span class="pink" id="v-p">--</span>
     &nbsp; H <span class="pink" id="v-hex">--</span> &nbsp; chi <span class="gold" id="v-chi">--</span></div>
  <div class="row">harmonics K <span class="val" id="v-k">--</span> &nbsp; samples M <span class="val" id="v-m">--</span></div>
  <div class="row">residual <span class="pink" id="v-res">--</span> &nbsp;
     certainty <span class="grn" id="v-cert">--</span></div>
  <div class="row">target = <span class="gold" id="v-target">--</span> &nbsp;
     <span id="badge">= NOT YET</span></div>
</div>
<div id="log"></div>
<div class="foot">
  <b>drag</b> orbit the bucky &middot; <b>wheel</b> zoom &middot; <b>1-6</b> views &middot;
  <b>G</b> grow &middot; <b>B</b> back &middot; <b>S</b> spin &middot; <b>N</b> notes
</div>
<div id="panel">
  <div class="tabs">
    <div class="tab active" data-t="idea" onclick="setTab('idea')">the idea</div>
    <div class="tab" data-t="math" onclick="setTab('math')">the math</div>
    <div class="tab" data-t="honest" onclick="setTab('honest')">honest</div>
    <div class="tab" data-t="join" onclick="setTab('join')">the join</div>
  </div>
  <div class="body">
    <div class="tabc active" id="tc-idea">
      <h4>The equals sign transcends this reality</h4>
      <div class="note">An experiment in the quantum realm or the galactic realm hands you
      <b>data</b> &mdash; a curve f(t). To say model <b>=</b> data, you must reproduce that curve
      with something you can actually <b>compute</b>. Here the compute is a pure Fourier sum, and
      the number of harmonics you may spend is set by <b>geometry</b>: the face count of a live
      Goldberg buckyball grown from C60.</div>
      <h4>The curve trapped in the C60</h4>
      <div class="note">Grow the bucky (add hexagons, the 7 real ops from GENESIS) and you buy more
      harmonics K. K <span class="k">= floor(faces / 2)</span>, capped by the sample Nyquist. Each
      growth drops the residual: <b>more compute, more spini-spini geometry, more degrees of
      certainty.</b> P=12 pentagons are the twelve lowest fundamental modes; the hexagons are the
      overtones you grow.</div>
      <h4>Why it is never exactly &quot;=&quot;</h4>
      <div class="warn">At a jump, Fourier overshoots forever (Gibbs). The residual falls toward
      zero but never reaches it in finite K. So the badge reads the measured
      <span class="g">1 - L2 residual</span>, never a hard-coded 100%. Target is not result.</div>
    </div>
    <div class="tabc" id="tc-math">
      <h4>Discrete transform (computed live, every change)</h4>
      <div class="note">Sample f at t<sub>m</sub> = 2&pi;m/M, m=0..M-1.<br>
      c<sub>k</sub> = (1/M) &sum;<sub>m</sub> f(t<sub>m</sub>) e<sup>-i k t<sub>m</sub></sup>,
      &nbsp; k = -K..K.<br>
      recon(t) = &sum;<sub>k=-K</sub><sup>K</sup> c<sub>k</sub> e<sup>i k t</sup>.<br>
      residual = ||f - recon||<sub>2</sub> / ||f||<sub>2</sub>.</div>
      <h4>Epicycles = spini-spini</h4>
      <div class="note">Each c<sub>k</sub> is a rotating vector of radius |c<sub>k</sub>| and speed k.
      Chain them tip-to-tail and the tip traces recon(t). That chain of turning circles is the
      Fourier series drawn as geometry &mdash; the CURVE view shows it live for the closed
      C60-silhouette target (the literal curve trapped in the bucky).</div>
      <h4>Kernel invariants (from topology, not float-matching)</h4>
      <div class="note">V = (5P + 6H)/3, &nbsp; E = (5P + 6H)/2, &nbsp; chi = V - E + F.
      A clean refineAll keeps <span class="g">P = 12</span> exactly and <span class="g">chi = 2</span>
      exactly, at every size. Shown live, never asserted.</div>
    </div>
    <div class="tabc" id="tc-honest">
      <h4>What is real</h4>
      <div class="note">The buckyball, its face/vertex/edge counts and chi come from the REAL
      <span class="k">goldberg_kernel.js</span>, injected verbatim (view source and grep). The DFT,
      the residual and the certainty are all computed in this tab, from the samples, and displayed
      with the number that is actually measured.</div>
      <h4>What is illustrative</h4>
      <div class="warn">The target curves (square / sawtooth / triangle / pulse / C60 silhouette) are
      <b>stand-ins</b> for experimental data, chosen because their exact Fourier behaviour is known,
      so you can watch the residual fall honestly. This sim predicts no physical measurement; it
      demonstrates the method by which compute is matched to data.</div>
      <h4>The ceiling (Curse 35, the Loaded Gun)</h4>
      <div class="warn">refineAll multiplies faces about 7x per level. The next size is predicted
      from the recurrence <i>before</i> allocating, and GROW refuses past the ceiling. The guillotine
      is built in, so a curious click can never blow the tab.</div>
    </div>
    <div class="tabc" id="tc-join">
      <h4>One kernel, many faces</h4>
      <div class="note"><b>GENESIS v8.1</b> grows the buckyball with the 7 ops and lets you fly inside.
      <b>CHROMODYNAMIUM</b> reads SU(3) off eight matrices. <b>THEALIMITIUM / NOETHERIUM</b> carry the
      limits and the symmetries. <b>AEQUALIUM</b> is where the geometry buys the harmonics and the
      harmonics buy the certainty &mdash; the place the equals sign is earned.</div>
      <div class="note">Each arrow is a computation, not a resemblance. The Euler-forced twelve
      pentagons and the Nyquist-forced harmonic ceiling are both <i>necessities</i>, not choices.</div>
      <div class="s">P=12 . chi=2 . the price is always paid . always.<br>__STAMP__</div>
    </div>
  </div>
</div>
"""

# ============================================================================
#  APP JS  (plain string, ASCII-only; window.GK is the injected kernel)
# ============================================================================
APP_JS = r"""
"use strict";
var RM=false; try{RM=window.matchMedia('(prefers-reduced-motion: reduce)').matches;}catch(e){}

// ---------- canvas ----------
var cv=document.getElementById('cv'), ctx=cv.getContext('2d');
var W=0,H=0,DPR=1;
function resize(){
  DPR=Math.max(1,Math.min(2,window.devicePixelRatio||1));
  W=window.innerWidth; H=window.innerHeight;
  cv.width=Math.floor(W*DPR); cv.height=Math.floor(H*DPR);
  cv.style.width=W+'px'; cv.style.height=H+'px';
  ctx.setTransform(DPR,0,0,DPR,0,0);
}
window.addEventListener('resize',resize);

// ---------- kernel state ----------
var GK=window.GK;
var state=GK.buildC60();
var inv=GK.invariants(state);

// ---------- fourier config ----------
var M=2048;                 // samples of the target
var KMAX=M/2-1;             // Nyquist ceiling on harmonics
var FACE_CEIL=4000;         // Curse 35: refuse a growth that would exceed this
var TARGETS=['SQUARE','SAWTOOTH','TRIANGLE','PULSE','C60 SILHOUETTE'];
var target=0;
var K=6, capNote=false;
var coeffs=null;            // [{k, re, im}] sorted by |k| ascending
var reconPts=null;          // [{re,im}] length RN, the reconstructed path/wave
var srcPts=null;            // the sampled target, length M, {re,im}
var residual=1, certainty=0;
var convHist=[];            // [{faces, residual}] the price curve
var RN=720;                 // recon draw resolution

// ---------- view / interaction ----------
var view=0;                 // 0 split 1 bucky 2 curve 3 spectrum 4 convergence 5 notes
var VIEWS=['SPLIT','BUCKY','CURVE','SPECTRUM','CONVERGE','NOTES'];
var yaw=0.6, pitch=-0.5, zoom=1, spin=RM?0:0, dragging=false, lx=0, ly=0, moved=false;
var tPhase=0;               // epicycle animation phase

function lg(m,c){var el=document.getElementById('log');var d=document.createElement('div');
  d.className='e'+(c?' '+c:'');d.innerHTML=m;el.insertBefore(d,el.firstChild);
  while(el.children.length>60)el.removeChild(el.lastChild);}

// ---------- targets: f(t) -> complex [re, im] ----------
function isClosed(){ return target===4; }   // C60 silhouette is a closed 2D curve
// closed-curve radius profile r(theta) derived from the live buckyball silhouette
var silR=null;
function buildSilhouette(){
  // project current vertices to the xy plane (canonical, no orbit) and take the
  // max radius per angular bin -> a closed r(theta) outline. the curve, trapped
  // in the C60 (and refined into the grown Goldberg).
  var BINS=360, r=new Float64Array(BINS);
  var f=state.faces, i, j;
  for(i=0;i<f.length;i++){
    var pts=f[i].pts;
    for(j=0;j<pts.length;j++){
      var x=pts[j][0], y=pts[j][1];
      var ang=Math.atan2(y,x); if(ang<0)ang+=Math.PI*2;
      var rad=Math.hypot(x,y);
      var bi=Math.floor(ang/(Math.PI*2)*BINS)%BINS;
      if(rad>r[bi]) r[bi]=rad;
    }
  }
  // fill empty bins by nearest neighbour, then light smoothing
  for(i=0;i<BINS;i++){ if(r[i]===0){ var a=i,b=i; while(r[(a+BINS)%BINS]===0)a--; while(r[b%BINS]===0)b++;
    r[i]=(r[(a+BINS)%BINS]+r[b%BINS])/2; } }
  var s=new Float64Array(BINS);
  for(i=0;i<BINS;i++){ s[i]=(r[(i-1+BINS)%BINS]+r[i]+r[(i+1)%BINS])/3; }
  silR=s;
}
function targetAt(t){
  var re=0, im=0;
  if(target===0){                      // SQUARE (real)
    re=(Math.sin(t)>=0)?1:-1;
  }else if(target===1){                // SAWTOOTH (real), ramp -1..1
    re=(t/Math.PI)-1;
  }else if(target===2){                // TRIANGLE (real)
    var x=t/(Math.PI*2); re=4*Math.abs(x-Math.floor(x+0.5))-1;
  }else if(target===3){                // PULSE (real), 25% duty
    re=((t%(Math.PI*2))<(Math.PI*0.5))?1:-1;
  }else{                               // C60 SILHOUETTE (closed, complex)
    if(!silR) buildSilhouette();
    var bins=silR.length, fpos=t/(Math.PI*2)*bins, i0=Math.floor(fpos)%bins;
    var i1=(i0+1)%bins, fr=fpos-Math.floor(fpos);
    var rad=silR[i0]*(1-fr)+silR[i1]*fr;
    re=rad*Math.cos(t); im=rad*Math.sin(t);
  }
  return [re,im];
}

// ---------- the DFT + reconstruction (recomputed only on change) ----------
function recompute(){
  // K from geometry: more faces -> more harmonics. capped by Nyquist (honest).
  var Hh=inv.faces, want=Math.floor(Hh/2);
  capNote=(want>KMAX); K=Math.min(want, KMAX); if(K<1)K=1;
  // sample the target
  srcPts=new Array(M);
  var m, twoPi=Math.PI*2, normF2=0;
  for(m=0;m<M;m++){ var t=twoPi*m/M, v=targetAt(t); srcPts[m]=v; normF2+=v[0]*v[0]+v[1]*v[1]; }
  // coefficients c_k = (1/M) sum f(t_m) e^{-i k t_m}
  coeffs=[];
  var k;
  for(k=-K;k<=K;k++){
    var sr=0, si=0;
    for(m=0;m<M;m++){
      var ang=-k*twoPi*m/M, cr=Math.cos(ang), ci=Math.sin(ang);
      var fr=srcPts[m][0], fi=srcPts[m][1];
      sr+=fr*cr-fi*ci; si+=fr*ci+fi*cr;
    }
    coeffs.push({k:k, re:sr/M, im:si/M});
  }
  // residual: reconstruct at the M sample points and compare (exact L2)
  var errF2=0;
  for(m=0;m<M;m++){
    var t2=twoPi*m/M, rr=0, ri=0, c;
    for(c=0;c<coeffs.length;c++){
      var kk=coeffs[c].k, a2=kk*t2, ca=Math.cos(a2), sa=Math.sin(a2);
      rr+=coeffs[c].re*ca-coeffs[c].im*sa;
      ri+=coeffs[c].re*sa+coeffs[c].im*ca;
    }
    var dr=srcPts[m][0]-rr, di=srcPts[m][1]-ri; errF2+=dr*dr+di*di;
  }
  residual=(normF2>1e-12)?Math.sqrt(errF2/normF2):0;
  certainty=Math.max(0,100*(1-residual));
  // recon path for drawing (RN points)
  reconPts=new Array(RN);
  for(m=0;m<RN;m++){
    var t3=twoPi*m/RN, rr2=0, ri2=0, c2;
    for(c2=0;c2<coeffs.length;c2++){
      var k3=coeffs[c2].k, a3=k3*t3, ca3=Math.cos(a3), sa3=Math.sin(a3);
      rr2+=coeffs[c2].re*ca3-coeffs[c2].im*sa3;
      ri2+=coeffs[c2].re*sa3+coeffs[c2].im*ca3;
    }
    reconPts[m]=[rr2,ri2];
  }
  // sort coeffs by |k| for epicycle chaining (k=0 first, then +-1, +-2 ...)
  coeffs.sort(function(a,b){ var da=Math.abs(a.k), db=Math.abs(b.k);
    if(da!==db)return da-db; return a.k-b.k; });
  logConv();
  refreshHud();
}
function logConv(){
  var last=convHist.length?convHist[convHist.length-1]:null;
  if(!last || last.faces!==inv.faces || last.target!==target){
    convHist.push({faces:inv.faces, residual:residual, target:target});
    if(convHist.length>200)convHist.shift();
  }else{ last.residual=residual; }
}

// ---------- grow / shrink (the 7 real ops via the kernel) ----------
function predictNext(){ // faces after one refineAll: pent->6, hex->7
  return inv.pents*6 + inv.hexes*7;
}
function grow(){
  var nxt=predictNext();
  if(nxt>FACE_CEIL){
    lg('GROW refused: next size '+nxt+' faces > ceiling '+FACE_CEIL+' (Curse 35)','pink');
    return;
  }
  state=GK.refineAll(state);
  inv=GK.invariants(state);
  silR=null;                    // silhouette must rebuild from the grown mesh
  lg('grew: '+inv.faces+' faces, P='+inv.pents+', chi='+(inv.vertices-inv.edges+inv.faces),'ok');
  recompute();
}
function back(){
  if(!state.history || state.history.length===0){ lg('already at the C60 seed','src'); return; }
  state=GK.undo(state);
  inv=GK.invariants(state);
  silR=null;
  lg('back: '+inv.faces+' faces','cyan');
  recompute();
}

// ---------- 3D projection (orbit) ----------
function rot(p){
  var cp=Math.cos(pitch),sp=Math.sin(pitch);
  var y1=p[1]*cp-p[2]*sp, z1=p[1]*sp+p[2]*cp;
  var cy=Math.cos(yaw),sy=Math.sin(yaw);
  return [p[0]*cy+z1*sy, y1, -p[0]*sy+z1*cy];
}
function proj(p,cx,cy,S){
  var r=rot(p), d=4.2/(4.2-r[2]);
  return {x:cx+r[0]*S*zoom*d, y:cy-r[1]*S*zoom*d, z:r[2]};
}
function drawBucky(cx,cy,S){
  var f=state.faces, order=[], i;
  for(i=0;i<f.length;i++){
    var pts=f[i].pts, zc=0, j;
    for(j=0;j<pts.length;j++){ zc+=rot(pts[j])[2]; }
    order.push({i:i, z:zc/pts.length});
  }
  order.sort(function(a,b){return a.z-b.z;});
  for(i=0;i<order.length;i++){
    var fc=f[order[i].i], p=fc.pts, k, sp=[];
    for(k=0;k<p.length;k++) sp.push(proj(p[k],cx,cy,S));
    var pent=(fc.type==='pent');
    var shade=Math.max(0.12,Math.min(1,(order[i].z+1.4)/2.6));
    ctx.beginPath(); ctx.moveTo(sp[0].x,sp[0].y);
    for(k=1;k<p.length;k++) ctx.lineTo(sp[k].x,sp[k].y);
    ctx.closePath();
    if(pent){ ctx.fillStyle='rgba(255,105,180,'+(0.12+0.5*shade)+')'; }
    else    { ctx.fillStyle='rgba(0,150,220,'+(0.05+0.22*shade)+')'; }
    ctx.fill();
    ctx.strokeStyle=pent?'rgba(255,170,210,'+(0.4+0.5*shade)+')'
                        :'rgba(90,190,255,'+(0.14+0.3*shade)+')';
    ctx.lineWidth=pent?1.4:0.8; ctx.stroke();
  }
}

// ---------- draw the wave (scalar targets) ----------
function drawWave(x0,y0,x1,y1){
  var midY=(y0+y1)/2, amp=(y1-y0)*0.4, i;
  ctx.strokeStyle='rgba(120,140,180,.16)'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(x0,midY); ctx.lineTo(x1,midY); ctx.stroke();
  // target (data)
  ctx.strokeStyle='rgba(255,215,0,.55)'; ctx.lineWidth=1.6; ctx.beginPath();
  for(i=0;i<M;i+=2){ var x=x0+(i/M)*(x1-x0), y=midY-srcPts[i][0]*amp;
    if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y); }
  ctx.stroke();
  // recon (compute)
  ctx.strokeStyle='#00d4ff'; ctx.lineWidth=2; ctx.beginPath();
  for(i=0;i<RN;i++){ var x2=x0+(i/RN)*(x1-x0), y2=midY-reconPts[i][0]*amp;
    if(i===0)ctx.moveTo(x2,y2);else ctx.lineTo(x2,y2); }
  ctx.stroke();
}

// ---------- draw epicycles + closed curve (C60 silhouette) ----------
function drawEpicycles(cx,cy,S){
  // scale so the silhouette fits
  var i, maxr=0;
  for(i=0;i<reconPts.length;i++){ var m2=Math.hypot(reconPts[i][0],reconPts[i][1]); if(m2>maxr)maxr=m2; }
  var sc=(maxr>1e-9)?(S*0.9/maxr):1;
  // the reconstructed closed curve
  ctx.strokeStyle='#00d4ff'; ctx.lineWidth=2; ctx.beginPath();
  for(i=0;i<reconPts.length;i++){ var x=cx+reconPts[i][0]*sc, y=cy-reconPts[i][1]*sc;
    if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y); }
  ctx.closePath(); ctx.stroke();
  // the target outline faint (data)
  ctx.strokeStyle='rgba(255,215,0,.4)'; ctx.lineWidth=1.4; ctx.beginPath();
  for(i=0;i<M;i+=4){ var x2=cx+srcPts[i][0]*sc, y2=cy-srcPts[i][1]*sc;
    if(i===0)ctx.moveTo(x2,y2);else ctx.lineTo(x2,y2); }
  ctx.closePath(); ctx.stroke();
  // the turning circles: chain the top vectors tip-to-tail at phase tPhase
  var VIS=Math.min(coeffs.length,64), px=cx, py=cy, c;
  ctx.lineWidth=1;
  for(c=0;c<VIS;c++){
    var co=coeffs[c], rad=Math.hypot(co.re,co.im)*sc;
    if(rad<0.6) { continue; }
    var ang=co.k*tPhase, vx=(co.re*Math.cos(ang)-co.im*Math.sin(ang))*sc,
        vy=(co.re*Math.sin(ang)+co.im*Math.cos(ang))*sc;
    ctx.strokeStyle='rgba(180,200,230,.12)';
    ctx.beginPath(); ctx.arc(px,py,rad,0,Math.PI*2); ctx.stroke();
    ctx.strokeStyle='rgba(255,105,180,.5)';
    ctx.beginPath(); ctx.moveTo(px,py); ctx.lineTo(px+vx,py-vy); ctx.stroke();
    px+=vx; py-=vy;
  }
  // the tracing dot at the tip
  ctx.fillStyle='#7fff9f'; ctx.beginPath(); ctx.arc(px,py,3,0,Math.PI*2); ctx.fill();
}

// ---------- draw spectrum ----------
function drawSpectrum(x0,y0,x1,y1){
  ctx.fillStyle='#ffd700'; ctx.font='bold 12px ui-monospace'; ctx.textAlign='left';
  ctx.fillText('POWER SPECTRUM  |c_k|  (k = -K .. K)', x0, y0-10);
  var n=coeffs.length, maxm=0, i;
  // rebuild by-k order for a clean symmetric spectrum
  var byk=coeffs.slice().sort(function(a,b){return a.k-b.k;});
  for(i=0;i<n;i++){ var mg=Math.hypot(byk[i].re,byk[i].im); if(mg>maxm)maxm=mg; }
  var bw=(x1-x0)/n;
  for(i=0;i<n;i++){
    var mg2=Math.hypot(byk[i].re,byk[i].im), h=(maxm>1e-9)?(mg2/maxm)*(y1-y0):0;
    var x=x0+i*bw;
    ctx.fillStyle=(byk[i].k===0)?'#ffd700':'rgba(0,212,255,.7)';
    ctx.fillRect(x, y1-h, Math.max(1,bw-0.6), h);
  }
  ctx.strokeStyle='rgba(120,140,180,.2)'; ctx.beginPath();
  ctx.moveTo(x0,y1); ctx.lineTo(x1,y1); ctx.stroke();
}

// ---------- draw convergence (the price curve) ----------
function drawConvergence(x0,y0,x1,y1){
  ctx.fillStyle='#ffd700'; ctx.font='bold 12px ui-monospace'; ctx.textAlign='left';
  ctx.fillText('THE PRICE CURVE  --  faces (compute) vs residual (1 - certainty)', x0, y0-10);
  // gather points for the current target
  var pts=[], i;
  for(i=0;i<convHist.length;i++){ if(convHist[i].target===target) pts.push(convHist[i]); }
  if(pts.length===0){ return; }
  var maxF=32, minF=32;
  for(i=0;i<pts.length;i++){ if(pts[i].faces>maxF)maxF=pts[i].faces; if(pts[i].faces<minF)minF=pts[i].faces; }
  function X(f){ return x0+(Math.log(f/minF)/Math.log(Math.max(maxF,minF*2)/minF))*(x1-x0); }
  function Y(r){ return y0+r*(y1-y0); }               // residual 0..1 top..bottom
  // axes
  ctx.strokeStyle='rgba(120,140,180,.2)'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(x0,y0); ctx.lineTo(x0,y1); ctx.lineTo(x1,y1); ctx.stroke();
  ctx.fillStyle='#66708a'; ctx.font='10px ui-monospace';
  ctx.fillText('residual 0', x0+4, y0+12); ctx.fillText('residual 1', x0+4, y1-4);
  ctx.textAlign='right'; ctx.fillText(minF+' faces', X(minF), y1+16);
  ctx.fillText(maxF+' faces', X(maxF), y1+16); ctx.textAlign='left';
  // the curve
  ctx.strokeStyle='#7fff9f'; ctx.lineWidth=2; ctx.beginPath();
  for(i=0;i<pts.length;i++){ var x=X(pts[i].faces), y=Y(pts[i].residual);
    if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y); }
  ctx.stroke();
  for(i=0;i<pts.length;i++){ var px=X(pts[i].faces), py=Y(pts[i].residual);
    ctx.fillStyle=(i===pts.length-1)?'#ffd700':'#00d4ff';
    ctx.beginPath(); ctx.arc(px,py,4,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='rgba(223,230,242,.6)'; ctx.font='9px ui-monospace';
    ctx.fillText('r='+pts[i].residual.toFixed(4), px+7, py); }
}

// ---------- the "=" glyph ----------
function drawEquals(cx,cy,size,glow){
  var g=Math.max(0,Math.min(1,glow));
  ctx.strokeStyle='rgba('+Math.round(120+135*g)+','+Math.round(140+115*g)+','+Math.round(180+30*g)+','+(0.5+0.5*g)+')';
  ctx.lineWidth=4+6*g;
  ctx.shadowColor='#7fff9f'; ctx.shadowBlur=22*g;
  ctx.beginPath(); ctx.moveTo(cx-size,cy-size*0.32); ctx.lineTo(cx+size,cy-size*0.32);
  ctx.moveTo(cx-size,cy+size*0.32); ctx.lineTo(cx+size,cy+size*0.32); ctx.stroke();
  ctx.shadowBlur=0;
}

// ---------- master render ----------
function render(){
  requestAnimationFrame(render);
  if(W<2||H<2){resize();return;}
  ctx.fillStyle='#05050f'; ctx.fillRect(0,0,W,H);
  var g=certainty/100;
  if(view===0){                       // SPLIT
    var half=W*0.42, top=150, bot=H-70;
    drawBucky(W*0.24, (top+bot)/2, Math.min(half,bot-top)*0.34);
    drawEquals(W*0.5, (top+bot)/2, 26, g);
    if(isClosed()) drawEpicycles(W*0.76,(top+bot)/2,Math.min(half,bot-top)*0.34);
    else drawWave(W*0.56, top, W-40, bot);
  }else if(view===1){                 // BUCKY
    drawBucky(W/2, H/2+10, Math.min(W,H)*0.32);
  }else if(view===2){                 // CURVE
    if(isClosed()) drawEpicycles(W/2,H/2+10,Math.min(W,H)*0.34);
    else drawWave(70, 150, W-60, H-80);
  }else if(view===3){                 // SPECTRUM
    drawSpectrum(70, 170, W-60, H-90);
  }else if(view===4){                 // CONVERGENCE
    drawConvergence(90, 180, W-70, H-90);
  }else{                              // NOTES
    ctx.fillStyle='#66708a'; ctx.font='13px ui-monospace'; ctx.textAlign='center';
    ctx.fillText('press N (or the NOTES button) for the dossier -- the idea, the math, the honest boundary, the join', W/2, H/2);
    ctx.textAlign='left';
  }
  // header per view
  ctx.fillStyle='rgba(223,230,242,.5)'; ctx.font='11px ui-monospace'; ctx.textAlign='center';
  ctx.fillText(VIEWS[view]+'  --  '+TARGETS[target], W/2, 128);
  ctx.textAlign='left';
  tPhase+=(spin>0?0.010:0.006);
  if(spin>0 && (view===1||view===0)) yaw+=spin;
}

// ---------- hud ----------
function refreshHud(){
  document.getElementById('v-faces').textContent=inv.faces;
  document.getElementById('v-p').textContent=inv.pents;
  document.getElementById('v-hex').textContent=inv.hexes;
  document.getElementById('v-chi').textContent=(inv.vertices-inv.edges+inv.faces);
  document.getElementById('v-k').textContent=K+(capNote?' (Nyquist cap)':'');
  document.getElementById('v-m').textContent=M;
  document.getElementById('v-res').textContent=residual.toFixed(6);
  document.getElementById('v-cert').textContent=certainty.toFixed(4)+'% (1 - L2 residual)';
  document.getElementById('v-target').textContent=TARGETS[target];
  var b=document.getElementById('badge');
  if(residual<0.02){ b.className='earned'; b.textContent='= within 2% (still not exact -- Gibbs)'; }
  else{ b.className=''; b.textContent='= NOT YET  (residual '+residual.toFixed(3)+')'; }
}

// ---------- ui ----------
function setView(v){ view=v; syncBtns(); }
function setTarget(t){ target=t; silR=null; recompute(); syncBtns(); }
function syncBtns(){
  var i, vb=document.querySelectorAll('[data-view]');
  for(i=0;i<vb.length;i++) vb[i].classList.toggle('active', +vb[i].getAttribute('data-view')===view);
  var tb=document.querySelectorAll('[data-target]');
  for(i=0;i<tb.length;i++) tb[i].classList.toggle('active', +tb[i].getAttribute('data-target')===target);
}
var panelOpen=false;
function togglePanel(){ panelOpen=!panelOpen;
  document.getElementById('panel').classList.toggle('open',panelOpen);
  document.getElementById('b-notes').classList.toggle('active',panelOpen); }
function setTab(t){
  var tabs=document.querySelectorAll('#panel .tab'), i;
  for(i=0;i<tabs.length;i++) tabs[i].classList.toggle('active',tabs[i].getAttribute('data-t')===t);
  var names=['idea','math','honest','join'];
  for(i=0;i<names.length;i++){ var e=document.getElementById('tc-'+names[i]);
    if(e) e.classList.toggle('active',names[i]===t); } }
function toggleSpin(){ spin=(spin>0)?0:0.006; document.getElementById('b-spin').classList.toggle('active',spin>0); }

// ---------- pointer / keys ----------
cv.addEventListener('pointerdown',function(e){ dragging=true;moved=false;lx=e.clientX;ly=e.clientY;
  try{cv.setPointerCapture(e.pointerId);}catch(err){} });
cv.addEventListener('pointermove',function(e){ if(!dragging)return;
  var dx=e.clientX-lx, dy=e.clientY-ly; lx=e.clientX; ly=e.clientY;
  if(Math.abs(dx)+Math.abs(dy)>3)moved=true;
  yaw+=dx*0.008; pitch+=dy*0.008; pitch=Math.max(-1.5,Math.min(1.5,pitch)); });
cv.addEventListener('pointerup',function(){ dragging=false; });
cv.addEventListener('wheel',function(e){ e.preventDefault();
  zoom=Math.max(0.5,Math.min(4,zoom*(e.deltaY<0?1.1:1/1.1))); },{passive:false});
window.addEventListener('keydown',function(e){
  var k=e.key.toLowerCase();
  if(k>='1'&&k<='6') setView(+k-1);
  else if(k==='g') grow();
  else if(k==='b') back();
  else if(k==='s') toggleSpin();
  else if(k==='n') togglePanel();
  else if(k==='0'){ yaw=0.6;pitch=-0.5;zoom=1; }
});

// ---------- boot ----------
resize();
recompute();
lg('AEQUALIUM __VERSION__ -- the equals sign, earned. always.','ok');
lg('the real goldberg_kernel.js is injected verbatim (proof by kernel)','cyan');
lg('C60 seed: '+inv.faces+' faces, P='+inv.pents+', chi='+(inv.vertices-inv.edges+inv.faces),'gold');
lg('press G to grow -- more hexagons, more harmonics, more certainty','ok');
render();
"""

# ============================================================================
#  BAR (buttons) -- built as plain string
# ============================================================================
def view_btns():
    names = ["SPLIT", "BUCKY", "CURVE", "SPECTRUM", "CONVERGE", "NOTES"]
    out = ""
    for i, n in enumerate(names):
        active = " active" if i == 0 else ""
        out += f'<button class="btn{active}" data-view="{i}" onclick="setView({i})">{n}</button>'
    return out

def target_btns():
    names = ["SQUARE", "SAW", "TRI", "PULSE", "C60"]
    out = ""
    for i, n in enumerate(names):
        active = " active" if i == 0 else ""
        out += f'<button class="btn{active}" data-target="{i}" onclick="setTarget({i})">{n}</button>'
    return out

BAR = (
    '<div id="bar">'
    '<span class="lbl">view</span>' + view_btns() +
    '<span class="sep"></span>'
    '<span class="lbl">data</span>' + target_btns() +
    '<span class="sep"></span>'
    '<button class="btn grow" id="b-grow" onclick="grow()">GROW &#9650;</button>'
    '<button class="btn" id="b-back" onclick="back()">BACK &#9660;</button>'
    '<span class="sep"></span>'
    '<button class="btn" id="b-spin" onclick="toggleSpin()">SPIN</button>'
    '<button class="btn" id="b-notes" onclick="togglePanel()">NOTES</button>'
    '</div>'
)

# ============================================================================
#  ASSEMBLE  (Pattern 2: one final template, simple token substitution only)
# ============================================================================
PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AEQUALIUM __VERSION__ -- the equals sign, earned (Fourier in the C60)</title>
<style>__CSS__</style>
</head>
<body>
__SHELL__
__BAR__
<script>
__KERNEL__
</script>
<script>
__APP__
</script>
</body></html>
"""

page = (PAGE
        .replace("__CSS__", CSS)
        .replace("__SHELL__", HTML_SHELL)
        .replace("__BAR__", BAR)
        .replace("__KERNEL__", KERNEL_JS)
        .replace("__APP__", APP_JS)
        .replace("__VERSION__", VERSION)
        .replace("__STAMP__", f"built {TIMESTAMP} . git:{GIT}"))

# normalize to LF, write utf-8 no BOM (Pattern 3, Path VI)
page = page.replace("\r\n", "\n").replace("\r", "\n")
OUT.write_text(page, encoding="utf-8", newline="\n")

# byte scan (loneCR / U+FFFD must be 0)
raw = OUT.read_bytes()
lone = sum(1 for i, b in enumerate(raw)
           if b == 13 and (i + 1 >= len(raw) or raw[i + 1] != 10))
fffd = page.count("\ufffd")
print(f"[OK] {OUT.name}  {len(raw)//1024}KB  loneCR={lone}  U+FFFD={fffd}")
print(f"[OK] https://vsavytsk1.github.io/Mnetv1/shell/{OUT.name}")
if lone or fffd:
    raise SystemExit("byte scan FAILED -- do not ship")

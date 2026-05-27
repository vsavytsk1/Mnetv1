#!/usr/bin/env python3
"""Build genesis_final_v1.html — Three-module modular system."""
import base64
from pathlib import Path
from io import BytesIO
from PIL import Image

ROOT = Path(__file__).parent.parent.parent
GATE_IMG = ROOT / "shell" / "gate" / "img"
KERNEL = ROOT / "kernel" / "goldberg_kernel.js"
OUT = Path(__file__).parent / "genesis_final_v1.html"

def img_b64(name):
    for ext in ['.jpeg','.jpg','.png']:
        p = GATE_IMG / f"{name}{ext}"
        if p.exists():
            img = Image.open(p).convert('RGB')
            w,h = img.size
            if w>1200 or h>900:
                r = min(1200/w, 900/h)
                img = img.resize((int(w*r),int(h*r)), Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format='JPEG', quality=85, optimize=True)
            return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"
    return ""

print("Building genesis_final_v1...")
img0 = img_b64("gate_closed")
img1 = img_b64("gate_open")
img2 = img_b64("truth")
img3 = img_b64("exchange")
kernel_js = KERNEL.read_text(encoding='utf-8')
print(f"  Images: {sum(len(x)//1024 for x in [img0,img1,img2,img3])}KB")
print(f"  Kernel: {len(kernel_js)//1024}KB")

html = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GENESIS FINAL</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{background:#050508;color:#c8d8e8;font-family:'Courier New',monospace;overflow:hidden;touch-action:none}
canvas{position:fixed;top:0;left:0;z-index:0}

/* MODULE SELECT */
#modbar{position:fixed;top:0;left:0;right:0;z-index:200;background:rgba(5,5,8,0.95);
  border-bottom:1px solid #1a1f2e;padding:4px 8px;display:flex;gap:6px;align-items:center;justify-content:center}
.mbtn{background:#0a0e18;border:1px solid #2a2a3a;color:#556;padding:4px 14px;font-family:'Orbitron',monospace;
  font-size:9px;cursor:pointer;border-radius:3px;letter-spacing:0.15em;transition:all 0.2s}
.mbtn:hover{border-color:#4a6a8a;color:#aaa}
.mbtn.on{color:#00ffd5;border-color:#00ffd5;text-shadow:0 0 10px rgba(0,255,213,0.3)}
#modtitle{font-family:'Orbitron';font-size:8px;color:#333;letter-spacing:0.2em;margin-left:12px}

/* FMA BANNERS */
.banner{position:fixed;top:0;left:0;width:100%;height:100%;z-index:150;display:flex;flex-direction:column;
  align-items:center;justify-content:center;background:#000;opacity:0;pointer-events:none;transition:opacity 1.2s ease}
.banner.active{opacity:1;pointer-events:all}
.banner img{max-height:65vh;max-width:85vw;object-fit:contain;filter:brightness(0.9);border-radius:4px}
.banner-text{color:#8899bb;font-size:15px;letter-spacing:5px;text-transform:uppercase;margin-top:24px;
  text-shadow:0 0 30px rgba(100,150,255,0.4);text-align:center;max-width:600px;font-family:'Cinzel',serif}
.banner-sub{color:#556;font-size:11px;letter-spacing:3px;margin-top:12px;text-align:center;font-family:'Cinzel',serif}
.banner-click{color:#556;font-size:10px;letter-spacing:4px;margin-top:20px;animation:pulse 2s ease-in-out infinite;font-family:'Cinzel',serif}
@keyframes pulse{0%,100%{opacity:0.3}50%{opacity:1}}
#circlePhase{position:fixed;top:0;left:0;width:100%;height:100%;z-index:140;display:flex;align-items:center;
  justify-content:center;background:#000;opacity:0;pointer-events:none;transition:opacity 1.5s ease}
#circlePhase.active{opacity:1;pointer-events:all}
#tCircle{border-radius:50%;box-shadow:0 0 60px rgba(60,100,220,0.4),0 0 160px rgba(60,100,220,0.15)}

/* ENGINEER BAR */
#bar{position:fixed;bottom:0;left:0;right:0;z-index:100;background:rgba(5,5,8,0.95);
  border-top:1px solid #1a1f2e;padding:5px 8px;display:none;gap:5px;align-items:center;flex-wrap:wrap;justify-content:center}
#bar.active{display:flex}
.btn{background:#0a0e18;border:1px solid #2a2a3a;color:#80d0ff;padding:4px 10px;font-family:inherit;
  font-size:9px;cursor:pointer;border-radius:3px;white-space:nowrap;transition:all 0.15s}
.btn:hover{border-color:#4a6a8a;color:#fff}.btn.pk{color:#ff69b4;border-color:#3a1a2a}
.btn.gn{color:#7fff7f;border-color:#1a3a1a}.btn.gd{color:#ffd700;border-color:#332a00}
.sep{width:1px;height:16px;background:#1a1f2e}
.sl{display:flex;align-items:center;gap:3px}
.sl label{font-size:7px;color:#555;letter-spacing:0.05em;min-width:30px}
.sl input[type=range]{width:50px;accent-color:#00ffd5}
.sl .sv{font-size:8px;color:#00ffd5;min-width:24px}

/* HUD */
#hud{position:fixed;top:28px;left:10px;z-index:90;pointer-events:none;font-size:10px;line-height:1.7;display:none}
#hud.active{display:block}
.lbl{color:#444}.val{color:#00ffd5}.vp{color:#ff69b4}.vg{color:#ffd700}
#euler{position:fixed;top:28px;left:50%;transform:translateX(-50%);z-index:90;pointer-events:none;
  font-family:'Orbitron';font-size:18px;font-weight:900;display:none}
#euler.active{display:block}
#euler .ok{color:#00ffd5}

/* AXIOM LOG */
#axiom-log{position:fixed;top:28px;right:10px;width:260px;max-height:45%;overflow-y:auto;font-size:9px;
  background:rgba(5,5,8,0.88);border:1px solid #1a1f2e;border-radius:4px;padding:6px;z-index:90;display:none}
#axiom-log.active{display:block}
.ax-p1{color:#00ffd5}.ax-p2{color:#80d0ff}.ax-p3{color:#aaa}.ax-p4{color:#ffd700}
.ax-p5{color:#ff9900}.ax-p6{color:#ff69b4}.ax-p7{color:#a78bfa}.ax-inv{color:#7fff7f;font-weight:bold}

/* PRESENT MESSAGE */
#pmsg{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:180;pointer-events:none;
  font-family:'Cinzel',serif;font-size:18px;color:#8899bb;letter-spacing:6px;text-transform:uppercase;
  text-shadow:0 0 40px rgba(100,150,255,0.4);opacity:0;transition:opacity 1.5s ease}
#pmsg.active{opacity:1}
</style></head><body>

<!-- MODULE SELECT BAR -->
<div id="modbar">
  <button class="mbtn" id="mb-fma" onclick="toggleMod('fma')">FMA</button>
  <button class="mbtn on" id="mb-eng" onclick="toggleMod('eng')">ENGINEER</button>
  <button class="mbtn" id="mb-pre" onclick="toggleMod('pre')">PRESENT</button>
  <span id="modtitle">GENESIS FINAL</span>
</div>

<!-- FMA BANNERS -->
<div class="banner" id="b0" onclick="fmaNext()">
  <img src="''' + img0 + '''" alt="The Gate">
  <div class="banner-text">Do you want to begin the journey?</div>
  <div class="banner-sub">There is a price. There is always a price.</div>
  <div class="banner-click">[ click anywhere ]</div>
</div>
<div id="circlePhase"><canvas id="tCircle" width="600" height="600"></canvas></div>
<div class="banner" id="b1" onclick="fmaNext()">
  <img src="''' + img1 + '''" alt="The Gate Opens">
  <div class="banner-text">The Gate opens for those who understand equivalent exchange.</div>
  <div class="banner-click">[ click to enter ]</div>
</div>
<div class="banner" id="b2" onclick="fmaNext()">
  <img src="''' + img2 + '''" alt="Truth">
  <div class="banner-text">Oh? Hello there, explorer.</div>
  <div class="banner-sub" style="color:#667">Have you read the license?<br>
    <a href="https://vsavytsk1.github.io/SpookyPrimes/" target="_blank" onclick="event.stopPropagation()"
       style="color:#4466aa;text-decoration:none;letter-spacing:2px;font-size:12px">&#8599; LICENSE</a></div>
  <div class="banner-click">[ I understand. Show me. ]</div>
</div>
<div class="banner" id="b3" onclick="fmaNext()">
  <img src="''' + img3 + '''" alt="Exchange">
  <div class="banner-text">The only price is compute.</div>
  <div class="banner-sub">V &#8722; E + F = 2 &middot; P = 12 &middot; always</div>
  <div class="banner-click">[ pay the price ]</div>
</div>

<!-- PRESENT MESSAGE -->
<div id="pmsg"></div>

<!-- EULER -->
<div id="euler"><span class="ok">V - E + F = 2 &middot; P = 12</span></div>

<!-- HUD -->
<div id="hud">
  <div><span class="lbl">V </span><span class="val" id="h-v">0</span></div>
  <div><span class="lbl">E </span><span class="val" id="h-e">0</span></div>
  <div><span class="lbl">F </span><span class="val" id="h-f">0</span></div>
  <div><span class="lbl">pent </span><span class="vp" id="h-p">0</span></div>
  <div><span class="lbl">hex </span><span class="val" id="h-h">0</span></div>
  <div><span class="lbl">chi </span><span class="vg" id="h-chi">0</span></div>
  <div><span class="lbl">E/V </span><span class="vg" id="h-ev">0</span></div>
  <div><span class="lbl">level </span><span class="val" id="h-lv">0</span></div>
  <div><span class="lbl">drawn </span><span class="vg" id="h-drawn">0</span></div>
</div>

<!-- AXIOM LOG -->
<div id="axiom-log"></div>

<!-- ENGINEER BAR -->
<div id="bar">
  <button class="btn gn" onclick="doSeed()">SEED</button>
  <button class="btn pk" onclick="doRefine()">REFINE</button>
  <button class="btn" onclick="doUndo()">UNDO</button>
  <button class="btn" onclick="doReset()">RESET</button>
  <div class="sep"></div>
  <div class="sl"><label>JITTER</label><input type="range" min="0" max="30" value="0" id="sl-jit" oninput="params.jitter=+this.value/100"><span class="sv" id="sv-jit">0</span></div>
  <div class="sl"><label>ZOOM</label><input type="range" min="50" max="1500" value="300" id="sl-zm" oninput="cam.zoom=+this.value"><span class="sv" id="sv-zm">300</span></div>
  <div class="sl"><label>SPIN</label><input type="range" min="0" max="50" value="3" id="sl-spin" oninput="cam.spin=+this.value/1000"><span class="sv" id="sv-spin">0.003</span></div>
  <div class="sl"><label>MAX-F</label><input type="range" min="0" max="100" value="50" id="sl-maxf" oninput="cam.maxFaces=Math.pow(10,1+this.value/20)"><span class="sv" id="sv-maxf">50000</span></div>
</div>

<!-- CANVAS -->
<canvas id="cv"></canvas>

<script>
// === KERNEL (inlined) ===
''' + kernel_js + '''

// ================================================================
// GLOBALS
// ================================================================
var K = GK;
var state = null, history = [], faces = [];
var cam = {rx:0.3, ry:0, zoom:300, spin:0.003, maxFaces:50000};
var params = {jitter:0};
var mods = {fma:false, eng:true, pre:false};
var fmaPhase = 0, fmaPhases = ['b0','circle','b1','b2','b3','done'];

// ================================================================
// MODULE TOGGLES
// ================================================================
function toggleMod(m){
  mods[m] = !mods[m];
  document.getElementById('mb-'+m).classList.toggle('on', mods[m]);
  applyMods();
  if(m==='fma' && mods.fma) startFMA();
  if(m==='pre' && mods.pre) startPresent();
  log('MOD toggle: FMA='+mods.fma+' ENG='+mods.eng+' PRE='+mods.pre);
}

function applyMods(){
  var bar = document.getElementById('bar');
  var hud = document.getElementById('hud');
  var euler = document.getElementById('euler');
  var axlog = document.getElementById('axiom-log');
  bar.classList.toggle('active', mods.eng);
  hud.classList.toggle('active', mods.eng || mods.pre);
  euler.classList.toggle('active', mods.eng);
  axlog.classList.toggle('active', mods.eng);
}

// ================================================================
// AXIOM LOG
// ================================================================
var opCount = 0;
function log(msg, cls){
  opCount++;
  cls = cls || 'ax-p3';
  var el = document.getElementById('axiom-log');
  el.innerHTML = '<div class="'+cls+'">['+opCount+'] '+msg+'</div>' + el.innerHTML;
  console.log('[GF] '+msg);
}

// ================================================================
// HUD UPDATE
// ================================================================
function updateHUD(){
  if(!state) return;
  var inv = K.invariants(state);
  var chi = inv.vertices - inv.edges + inv.faces;
  var ev = inv.edges / Math.max(inv.vertices,1);
  document.getElementById('h-v').textContent = inv.vertices;
  document.getElementById('h-e').textContent = inv.edges;
  document.getElementById('h-f').textContent = inv.faces;
  document.getElementById('h-p').textContent = inv.pents;
  document.getElementById('h-h').textContent = inv.hexes;
  document.getElementById('h-chi').textContent = chi;
  document.getElementById('h-ev').textContent = ev.toFixed(3);
  document.getElementById('h-lv').textContent = inv.maxLevel;
  log('INV: F='+inv.faces+' P='+inv.pents+' chi='+chi+' E/V='+ev.toFixed(3), 'ax-inv');
}

// ================================================================
// ENGINEER ACTIONS
// ================================================================
function doSeed(){
  history.push(state);
  state = K.buildC60();
  faces = state.faces;
  applyJitter();
  updateHUD();
  log('P1 SEED: dodecahedron (12 faces)', 'ax-p1');
}

function doRefine(){
  if(!state) doSeed();
  if(faces.length > cam.maxFaces){ log('MAX FACES reached','ax-p5'); return; }
  history.push(JSON.parse(JSON.stringify(state)));
  state = K.refineAll(state);
  faces = state.faces;
  applyJitter();
  updateHUD();
  log('P2 REFINE: '+faces.length+' faces', 'ax-p2');
}

function doUndo(){
  if(history.length === 0){ log('Nothing to undo','ax-p5'); return; }
  state = history.pop();
  faces = state ? state.faces : [];
  applyJitter();
  updateHUD();
  log('P5 UNDO', 'ax-p5');
}

function doReset(){
  state = null; history = []; faces = [];
  updateHUD();
  log('RESET', 'ax-p3');
}

function applyJitter(){
  var j = params.jitter;
  faces.forEach(function(f){
    f._jpts = f.pts.map(function(p){
      return j > 0 ? [p[0]+(Math.random()-0.5)*j, p[1]+(Math.random()-0.5)*j, p[2]+(Math.random()-0.5)*j] : p.slice();
    });
  });
}

// ================================================================
// FMA SEQUENCE
// ================================================================
function startFMA(){
  fmaPhase = 0;
  document.getElementById('b0').classList.add('active');
}

function fmaNext(){
  var cur = fmaPhases[fmaPhase];
  if(cur.startsWith('b')) document.getElementById(cur).classList.remove('active');
  if(cur==='circle') document.getElementById('circlePhase').classList.remove('active');
  fmaPhase++;
  if(fmaPhase >= fmaPhases.length){ mods.fma=false; document.getElementById('mb-fma').classList.remove('on'); return; }
  var nxt = fmaPhases[fmaPhase];
  if(nxt.startsWith('b')) document.getElementById(nxt).classList.add('active');
  else if(nxt==='circle'){ document.getElementById('circlePhase').classList.add('active'); drawCircle(); }
  else if(nxt==='done'){ mods.fma=false; document.getElementById('mb-fma').classList.remove('on');
    if(mods.pre) startPresent(); else if(!state) doSeed(); }
}

function drawCircle(){
  var c=document.getElementById('tCircle'),ctx=c.getContext('2d'),cx=300,cy=300,R=260,phi=(1+Math.sqrt(5))/2,step=0,mx=300;
  function anim(){
    step++;var t=step/mx;
    ctx.fillStyle='rgba(0,0,0,0.05)';ctx.fillRect(0,0,600,600);
    ctx.strokeStyle='rgba(80,120,255,'+(0.3+0.4*t)+')';ctx.lineWidth=1.5;
    ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.stroke();
    ctx.beginPath();ctx.arc(cx,cy,R*0.85,0,Math.PI*2);ctx.stroke();
    ctx.beginPath();ctx.arc(cx,cy,R*0.15,0,Math.PI*2);ctx.stroke();
    for(var i=0;i<12;i++){var a=(i/12)*Math.PI*2-Math.PI/2+step*0.002,r=(i<6)?R*0.65:R*0.35;if(i===0)r=0;
      var px=cx+Math.cos(a)*r,py=cy+Math.sin(a)*r;ctx.strokeStyle='rgba(100,160,255,'+(0.2+0.6*t)+')';ctx.lineWidth=1;ctx.beginPath();
      for(var k=0;k<5;k++){var pa=(k/5)*Math.PI*2-Math.PI/2,pr=12+8*t;k===0?ctx.moveTo(px+Math.cos(pa)*pr,py+Math.sin(pa)*pr):ctx.lineTo(px+Math.cos(pa)*pr,py+Math.sin(pa)*pr);}ctx.closePath();ctx.stroke();}
    ctx.strokeStyle='rgba(60,100,200,'+(0.1+0.3*t)+')';ctx.lineWidth=0.5;
    for(var i=0;i<12;i++)for(var j=i+1;j<12;j++)if((j-i)%3===0||(j-i)===5){var a1=(i/12)*Math.PI*2-Math.PI/2+step*0.002,a2=(j/12)*Math.PI*2-Math.PI/2+step*0.002,r1=(i<6)?R*0.65:R*0.35,r2=(j<6)?R*0.65:R*0.35;if(i===0)r1=0;if(j===0)r2=0;
      ctx.beginPath();ctx.moveTo(cx+Math.cos(a1)*r1,cy+Math.sin(a1)*r1);ctx.lineTo(cx+Math.cos(a2)*r2,cy+Math.sin(a2)*r2);ctx.stroke();}
    ctx.strokeStyle='rgba(120,180,255,'+(0.2+0.5*t)+')';ctx.lineWidth=1;ctx.beginPath();
    for(var i=0;i<3;i++){var a=(i/3)*Math.PI*2-Math.PI/2;i===0?ctx.moveTo(cx+Math.cos(a)*R*0.5,cy+Math.sin(a)*R*0.5):ctx.lineTo(cx+Math.cos(a)*R*0.5,cy+Math.sin(a)*R*0.5);}ctx.closePath();ctx.stroke();
    ctx.strokeStyle='rgba(80,140,255,'+(0.1+0.2*t)+')';ctx.lineWidth=0.8;ctx.beginPath();
    for(var s=0;s<200*t;s++){var sa=s*0.1+step*0.01,sr=5+s*0.4*phi*0.1;if(sr>R)break;s===0?ctx.moveTo(cx+Math.cos(sa)*sr,cy+Math.sin(sa)*sr):ctx.lineTo(cx+Math.cos(sa)*sr,cy+Math.sin(sa)*sr);}ctx.stroke();
    if(t>0.5){ctx.save();ctx.font='9px Cinzel';ctx.fillStyle='rgba(80,120,200,'+(t-0.5)*1.5+')';var w='V-E+F=2 . P=12 . chi=2 . ALWAYS . EULER 1758 . GOLDBERG 1937 . ';
      for(var i=0;i<w.length;i++){var wa=(i/w.length)*Math.PI*2-Math.PI/2+step*0.003;ctx.save();ctx.translate(cx+Math.cos(wa)*(R+15),cy+Math.sin(wa)*(R+15));ctx.rotate(wa+Math.PI/2);ctx.fillText(w[i],0,0);ctx.restore();}ctx.restore();}
    if(step<mx)requestAnimationFrame(anim);
    else setTimeout(function(){document.getElementById('circlePhase').classList.remove('active');fmaPhase++;
      var nxt=fmaPhases[fmaPhase];if(nxt&&nxt.startsWith('b'))document.getElementById(nxt).classList.add('active');
      else if(nxt==='done'){mods.fma=false;document.getElementById('mb-fma').classList.remove('on');if(mods.pre)startPresent();else if(!state)doSeed();}},2000);
  }anim();
}

// ================================================================
// PRESENT MODE — Scripted Automation
// ================================================================
var SCRIPT = [
  {t:0,     action:'msg',    text:'Initializing...'},
  {t:1000,  action:'seed'},
  {t:1800,  action:'msg',    text:'Refining topology...'},
  {t:2500,  action:'refine'},
  {t:3500,  action:'refine'},
  {t:4500,  action:'refine'},
  {t:5500,  action:'zoom',   value:500},
  {t:6000,  action:'msg',    text:'The structure reveals itself.'},
  {t:7500,  action:'spin',   value:0.002},
  {t:8000,  action:'hideUI'},
  {t:9000,  action:'msg',    text:'Explore.'},
  {t:11000, action:'clearMsg'}
];

function startPresent(){
  log('PRESENT mode started','ax-p4');
  SCRIPT.forEach(function(step){
    setTimeout(function(){
      switch(step.action){
        case 'seed': doSeed(); break;
        case 'refine': doRefine(); break;
        case 'zoom': cam.zoom=step.value; document.getElementById('sl-zm').value=step.value; break;
        case 'spin': cam.spin=step.value; break;
        case 'hideUI':
          mods.eng=false; document.getElementById('mb-eng').classList.remove('on');
          document.getElementById('bar').classList.remove('active');
          document.getElementById('axiom-log').classList.remove('active');
          document.getElementById('euler').classList.remove('active');
          break;
        case 'msg':
          var el=document.getElementById('pmsg');el.textContent=step.text;el.classList.add('active');
          break;
        case 'clearMsg':
          document.getElementById('pmsg').classList.remove('active');
          break;
      }
    }, step.t);
  });
}

// ================================================================
// RENDERER
// ================================================================
var cv, ctx;
function initCanvas(){
  cv = document.getElementById('cv');
  cv.width = window.innerWidth;
  cv.height = window.innerHeight;
  ctx = cv.getContext('2d');
  // Mouse
  var drag=false, lx=0, ly=0;
  cv.addEventListener('mousedown',function(e){drag=true;lx=e.clientX;ly=e.clientY;cam.spin=0;document.getElementById('sl-spin').value=0;});
  cv.addEventListener('mousemove',function(e){if(!drag)return;cam.ry+=(e.clientX-lx)*0.005;cam.rx+=(e.clientY-ly)*0.005;lx=e.clientX;ly=e.clientY;});
  cv.addEventListener('mouseup',function(){drag=false});
  cv.addEventListener('wheel',function(e){cam.zoom*=e.deltaY>0?0.95:1.05;document.getElementById('sl-zm').value=Math.round(cam.zoom);},{passive:true});
  // Touch
  cv.addEventListener('touchstart',function(e){if(e.touches.length===1){drag=true;lx=e.touches[0].clientX;ly=e.touches[0].clientY;cam.spin=0;}},{passive:true});
  cv.addEventListener('touchmove',function(e){if(!drag||e.touches.length!==1)return;var t=e.touches[0];cam.ry+=(t.clientX-lx)*0.005;cam.rx+=(t.clientY-ly)*0.005;lx=t.clientX;ly=t.clientY;},{passive:true});
  cv.addEventListener('touchend',function(){drag=false},{passive:true});
  window.addEventListener('resize',function(){cv.width=window.innerWidth;cv.height=window.innerHeight;});
}

function render(){
  var W=cv.width, H=cv.height;
  ctx.fillStyle='rgba(5,5,8,0.25)';
  ctx.fillRect(0,0,W,H);
  if(!faces.length){requestAnimationFrame(render);return;}
  cam.ry += cam.spin;
  var cy2=Math.cos(cam.ry),sy2=Math.sin(cam.ry),cx2=Math.cos(cam.rx),sx2=Math.sin(cam.rx);
  function proj(p){
    var x=p[0],y=p[1],z=p[2],x1=x*cy2-z*sy2,z1=x*sy2+z*cy2,y1=y*cx2-z1*sx2,z2=y*sx2+z1*cx2;
    var s=cam.zoom/(z2+5);return{x:W/2+x1*s,y:H/2+y1*s,z:z2,s:s};
  }
  var drawn=0, maxD=cam.maxFaces;
  // Sort by depth
  var sorted = faces.slice(0, maxD);
  sorted.sort(function(a,b){
    var ca=a.pts[0], cb=b.pts[0];
    var za=ca[0]*sy2+ca[2]*cy2, zb=cb[0]*sy2+cb[2]*cy2;
    return zb-za;
  });
  sorted.forEach(function(f){
    var pts = f._jpts || f.pts;
    var n = pts.length;
    // Backface cull
    var c0=proj(pts[0]),c1=proj(pts[1]),c2=proj(pts[2]);
    var cross=(c1.x-c0.x)*(c2.y-c0.y)-(c1.y-c0.y)*(c2.x-c0.x);
    if(cross<0) return;
    drawn++;
    var isPent = f.type==='pent';
    var depth = c0.z;
    var bright = Math.max(0.1, Math.min(0.9, 1.2/(depth+4)));

    // Fill
    var hue = isPent ? 'rgba(255,80,160,' : 'rgba(40,120,220,';
    ctx.fillStyle = hue + (bright*0.15) + ')';
    ctx.strokeStyle = isPent ? 'rgba(255,120,200,'+bright+')' : 'rgba(60,160,255,'+bright*0.5+')';
    ctx.lineWidth = isPent ? 1.2 : 0.5;
    ctx.beginPath();
    for(var i=0;i<n;i++){
      var p=proj(pts[i]);
      i===0?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y);
    }
    ctx.closePath();ctx.fill();ctx.stroke();
  });

  // Pentagon glow
  faces.forEach(function(f){
    if(f.type!=='pent') return;
    var ctr=f.pts.reduce(function(a,b){return[a[0]+b[0],a[1]+b[1],a[2]+b[2]]});
    ctr=[ctr[0]/f.pts.length,ctr[1]/f.pts.length,ctr[2]/f.pts.length];
    var p=proj(ctr);if(p.z<-4)return;
    var r=4+3*p.s/cam.zoom*100;
    var g=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,r);
    g.addColorStop(0,'rgba(255,150,230,0.4)');g.addColorStop(1,'rgba(255,100,180,0)');
    ctx.fillStyle=g;ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fill();
  });

  document.getElementById('h-drawn').textContent = drawn;
  requestAnimationFrame(render);
}

// ================================================================
// INIT
// ================================================================
window.addEventListener('load', function(){
  console.log('%c[GF] GENESIS FINAL loaded','color:#00ffd5;font-size:14px');
  initCanvas();
  applyMods();
  // Auto-seed so there's something to see
  doSeed();
  render();
  log('GENESIS FINAL ready. Toggle modules above.', 'ax-p1');
});
</script>
</body></html>
'''

OUT.write_text(html, encoding='utf-8')
print(f"Written: {OUT} ({len(html)//1024} KB)")
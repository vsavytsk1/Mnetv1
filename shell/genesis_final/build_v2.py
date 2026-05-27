#!/usr/bin/env python3
"""Build genesis_final_v2.html — Full v8.0 engineering + FMA + PRESENT."""
import base64, re
from pathlib import Path
from io import BytesIO
from PIL import Image

ROOT = Path(__file__).parent.parent.parent
V8 = ROOT / "shell" / "genesis_v8.0.html"
GATE_IMG = ROOT / "shell" / "gate" / "img"
OUT = Path(__file__).parent / "genesis_final_v2.html"

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

print("Building genesis_final_v2...")
img0 = img_b64("gate_closed")
img1 = img_b64("gate_open")
img2 = img_b64("truth")
img3 = img_b64("exchange")
print(f"  Images: {sum(len(x)//1024 for x in [img0,img1,img2,img3])}KB")

# Extract the FULL JS from v8.0 (kernel + app logic)
v8_html = V8.read_text(encoding='utf-8')
# Find the <script> section (after the bar HTML)
script_match = re.search(r'<script>\s*// ={10,}', v8_html)
script_start = script_match.start() + len('<script>')
script_end = v8_html.rfind('</script>')
v8_js = v8_html[script_start:script_end]
print(f"  v8 JS: {len(v8_js)//1024}KB extracted")

# Patch the v8 JS:
# 1. Remove the animate() call at the end (we'll control it)
# 2. Remove the initial doSeed() call
# 3. Rename 'history' if present
v8_js = v8_js.replace('animate();', '// animate(); — controlled by genesis_final')
# The v8 uses gkState, we need to keep that

# Build HTML in parts to avoid f-string brace hell
part1 = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GENESIS FINAL v2</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap');
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#050508;color:#c8d8e8;font-family:'Courier New',monospace;overflow:hidden;touch-action:none}}
#cv{{position:fixed;top:0;left:0;z-index:0}}
#hud{{position:fixed;top:28px;left:10px;z-index:5;pointer-events:none;font-size:10px;line-height:1.7;display:none}}
#hud.active{{display:block}}
.lbl{{color:#444}}.val{{color:#00ffd5}}.vp{{color:#ff69b4}}.vg{{color:#ffd700}}
#title{{position:fixed;top:28px;left:50%;transform:translateX(-50%);z-index:5;pointer-events:none;
  font-family:'Orbitron';font-size:11px;letter-spacing:0.3em;color:rgba(0,180,255,0.3);display:none}}
#title.active{{display:block}}
#euler{{position:fixed;top:42px;left:50%;transform:translateX(-50%);z-index:5;pointer-events:none;
  font-family:'Orbitron';font-size:20px;font-weight:900;display:none}}
#euler.active{{display:block}}
#euler .ok{{color:#00ffd5}}#euler .bad{{color:#ff3333}}
#axiom-log{{position:fixed;top:28px;right:10px;width:280px;max-height:50%;overflow-y:auto;font-size:9px;
  background:rgba(5,5,8,0.88);border:1px solid #1a1f2e;border-radius:4px;padding:6px;z-index:5;display:none}}
#axiom-log.active{{display:block}}
.ax-p1{{color:#00ffd5}}.ax-p2{{color:#80d0ff}}.ax-p3{{color:#aaa}}.ax-p4{{color:#ffd700}}
.ax-p5{{color:#ff9900}}.ax-p6{{color:#ff69b4}}.ax-p7{{color:#a78bfa}}.ax-inv{{color:#7fff7f;font-weight:bold}}
#bar{{position:fixed;bottom:0;left:0;right:0;z-index:10;background:rgba(5,5,8,0.95);
  border-top:1px solid #1a1f2e;padding:5px 8px;display:none;gap:5px;align-items:center;flex-wrap:wrap;justify-content:center}}
#bar.active{{display:flex}}
.btn{{background:#0a0e18;border:1px solid #2a2a3a;color:#80d0ff;padding:4px 10px;font-family:inherit;
  font-size:9px;cursor:pointer;border-radius:3px;white-space:nowrap;transition:all 0.15s}}
.btn:hover{{border-color:#4a6a8a;color:#fff}}.btn.pk{{color:#ff69b4;border-color:#3a1a2a}}
.btn.gn{{color:#7fff7f;border-color:#1a3a1a}}.btn.gd{{color:#ffd700;border-color:#332a00}}
.sep{{width:1px;height:16px;background:#1a1f2e}}
.sl{{display:flex;align-items:center;gap:3px}}
.sl label{{font-size:7px;color:#555;letter-spacing:0.05em;min-width:30px}}
.sl input[type=range]{{width:50px;accent-color:#00ffd5}}
.sl .sv{{font-size:8px;color:#00ffd5;min-width:24px}}
#load{{display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);padding:12px 30px;background:#1a1f2e;color:#ff69b4;font-family:'Orbitron',monospace;font-size:12px;letter-spacing:0.15em;border:1px solid #ff69b4;border-radius:4px;z-index:999;text-align:center;min-width:300px}}

/* MODULE SELECT */
#modbar{{position:fixed;top:0;left:0;right:0;z-index:200;background:rgba(5,5,8,0.95);
  border-bottom:1px solid #1a1f2e;padding:4px 8px;display:flex;gap:6px;align-items:center;justify-content:center}}
.mbtn{{background:#0a0e18;border:1px solid #2a2a3a;color:#556;padding:4px 14px;font-family:'Orbitron',monospace;
  font-size:9px;cursor:pointer;border-radius:3px;letter-spacing:0.15em;transition:all 0.2s}}
.mbtn:hover{{border-color:#4a6a8a;color:#aaa}}
.mbtn.on{{color:#00ffd5;border-color:#00ffd5;text-shadow:0 0 10px rgba(0,255,213,0.3)}}
#modtitle{{font-family:'Orbitron';font-size:8px;color:#333;letter-spacing:0.2em;margin-left:12px}}

/* FMA BANNERS */
.banner{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:150;display:flex;flex-direction:column;
  align-items:center;justify-content:center;background:#000;opacity:0;pointer-events:none;transition:opacity 1.2s ease}}
.banner.active{{opacity:1;pointer-events:all}}
.banner img{{max-height:65vh;max-width:85vw;object-fit:contain;filter:brightness(0.9);border-radius:4px}}
.banner-text{{color:#8899bb;font-size:15px;letter-spacing:5px;text-transform:uppercase;margin-top:24px;
  text-shadow:0 0 30px rgba(100,150,255,0.4);text-align:center;max-width:600px;font-family:'Cinzel',serif}}
.banner-sub{{color:#556;font-size:11px;letter-spacing:3px;margin-top:12px;text-align:center;font-family:'Cinzel',serif}}
.banner-click{{color:#556;font-size:10px;letter-spacing:4px;margin-top:20px;animation:pulse 2s ease-in-out infinite;font-family:'Cinzel',serif}}
@keyframes pulse{{0%,100%{{opacity:0.3}}50%{{opacity:1}}}}
#circlePhase{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:140;display:flex;align-items:center;
  justify-content:center;background:#000;opacity:0;pointer-events:none;transition:opacity 1.5s ease}}
#circlePhase.active{{opacity:1;pointer-events:all}}
#tCircle{{border-radius:50%;box-shadow:0 0 60px rgba(60,100,220,0.4),0 0 160px rgba(60,100,220,0.15)}}

/* PRESENT */
#pmsg{{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:180;pointer-events:none;
  font-family:'Cinzel',serif;font-size:18px;color:#8899bb;letter-spacing:6px;text-transform:uppercase;
  text-shadow:0 0 40px rgba(100,150,255,0.4);opacity:0;transition:opacity 1.5s ease}}
#pmsg.active{{opacity:1}}
</style></head><body>

<!-- MODULE BAR -->
<div id="modbar">
  <button class="mbtn" id="mb-fma" onclick="toggleMod('fma')">FMA</button>
  <button class="mbtn on" id="mb-eng" onclick="toggleMod('eng')">ENGINEER</button>
  <button class="mbtn" id="mb-pre" onclick="toggleMod('pre')">PRESENT</button>
  <span id="modtitle">GENESIS FINAL v2</span>
</div>

<!-- FMA BANNERS -->
<div class="banner" id="b0" onclick="fmaNext()">
  <img src="IMG0_B64" alt="Gate"><div class="banner-text">Do you want to begin the journey?</div>
  <div class="banner-sub">There is a price. There is always a price.</div><div class="banner-click">[ click anywhere ]</div></div>
<div id="circlePhase"><canvas id="tCircle" width="600" height="600"></canvas></div>
<div class="banner" id="b1" onclick="fmaNext()">
  <img src="IMG1_B64" alt="Gate Opens"><div class="banner-text">The Gate opens for those who understand equivalent exchange.</div>
  <div class="banner-click">[ click to enter ]</div></div>
<div class="banner" id="b2" onclick="fmaNext()">
  <img src="IMG2_B64" alt="Truth"><div class="banner-text">Oh? Hello there, explorer.</div>
  <div class="banner-sub" style="color:#667">Have you read the license?<br>
    <a href="https://vsavytsk1.github.io/SpookyPrimes/" target="_blank" onclick="event.stopPropagation()"
       style="color:#4466aa;text-decoration:none;letter-spacing:2px;font-size:12px">&#8599; LICENSE</a></div>
  <div class="banner-click">[ I understand. Show me. ]</div></div>
<div class="banner" id="b3" onclick="fmaNext()">
  <img src="IMG3_B64" alt="Exchange"><div class="banner-text">The only price is compute.</div>
  <div class="banner-sub">V &#8722; E + F = 2 &middot; P = 12 &middot; always</div>
  <div class="banner-click">[ pay the price ]</div></div>

<div id="pmsg"></div>
<div id="load"></div>
<canvas id="cv"></canvas>
<div id="title">GENESIS FINAL v2</div>
<div id="euler"><span class="ok">V - E + F = 2 &middot; P = 12</span></div>
<div id="hud">
<div><span class="lbl">V </span><span class="val" id="h-v">0</span></div>
<div><span class="lbl">E </span><span class="val" id="h-e">0</span></div>
<div><span class="lbl">F </span><span class="val" id="h-f">0</span></div>
<div><span class="lbl">pent </span><span class="vp" id="h-p">0</span></div>
<div><span class="lbl">hex </span><span class="val" id="h-h">0</span></div>
<div><span class="lbl">chi </span><span class="vg" id="h-chi">0</span></div>
<div><span class="lbl">E/V </span><span class="vg" id="h-ev">0</span></div>
<div><span class="lbl">level </span><span class="val" id="h-lv">0</span></div>
<div><span class="lbl">ops </span><span class="val" id="h-ops">0</span></div>
<div><span class="lbl">drawn </span><span class="vg" id="h-drawn">0</span></div>
<div><span class="lbl">flow </span><span class="vp" id="h-flow">off</span></div>
<div><span class="lbl">path </span><span class="vg" id="h-path">-</span></div>
<div><span class="lbl">MB </span><span class="vp" id="h-mb">0</span></div>
</div>
<div id="axiom-log"></div>
<div id="bar">
<button class="btn gn" onclick="doSeed()">SEED C60</button>
<button class="btn pk" onclick="doSeedDodec()">SEED 12</button>
<button class="btn pk" onclick="doRefineAll()">REFINE ALL</button>
<button class="btn gd" onclick="toggleFlow()">FLOW <b id="flowState">off</b></button>
<button class="btn pk" onclick="doPathfind()">PATH</button>
<button class="btn gd" onclick="doBatch100M()">100M</button>
<div class="sl"><label>FLOW X</label><input type="range" min="0" max="100" value="15" id="sl-flowx" oninput="flowSliderChange(+this.value)"><span class="sv" id="sv-flowx">1</span></div>
<button class="btn" onclick="doRefinePents()">REFINE 5s</button>
<button class="btn" onclick="doRefineHexes()">REFINE 6s</button>
<button class="btn" onclick="doUndo()">UNDO</button>
<button class="btn" onclick="doReset()">RESET</button>
<div class="sep"></div>
<div class="sl"><label>INNER</label><input type="range" min="10" max="90" value="45" id="sl-inner" oninput="params.innerScale=+this.value/100;SV('sv-inner',this.value/100)"><span class="sv" id="sv-inner">0.45</span></div>
<div class="sl"><label>MID</label><input type="range" min="10" max="95" value="70" id="sl-mid" oninput="params.midScale=+this.value/100;SV('sv-mid',this.value/100)"><span class="sv" id="sv-mid">0.70</span></div>
<div class="sl"><label>JITTER</label><input type="range" min="0" max="30" value="0" id="sl-jit" oninput="params.jitter=+this.value/100;SV('sv-jit',this.value/100)"><span class="sv" id="sv-jit">0.00</span></div>
<div class="sep"></div>
<div class="sl"><label>ZOOM</label><input type="range" min="1" max="1500" value="200" id="sl-zm" oninput="cam.zoom=+this.value;SV('sv-zm',this.value)"><span class="sv" id="sv-zm">200</span></div>
<div class="sl"><label>ATOM</label><input type="range" min="1" max="30" value="10" id="sl-atom" oninput="cam.atom=+this.value/10;SV('sv-atom',(this.value/10).toFixed(1))"><span class="sv" id="sv-atom">1.0</span></div>
<div class="sl"><label>MAX-F</label><input type="range" min="0" max="100" value="50" id="sl-maxf" oninput="cam.maxFaces=Math.pow(10,1+this.value/20);SV('sv-maxf',Math.round(cam.maxFaces))"><span class="sv" id="sv-maxf">50000</span></div>
<div class="sep"></div>
<div class="sl"><label>SPIN</label><input type="range" min="0" max="50" value="0" id="sl-spin" oninput="cam.spin=+this.value/1000;SV('sv-spin',this.value/1000)"><span class="sv" id="sv-spin">0.000</span></div>
<div class="sep"></div>
<button class="btn pk" id="bMob" onclick="toggleMobius()">MOBIUS <b id="mobState">off</b></button>
<input type="range" min="0" max="100" value="0" id="mobSlider" disabled oninput="setMobiusTwist(this.value)" style="width:80px;accent-color:#ff69b4">
<span class="sv" id="twistVal" style="color:#ff69b4">0.00</span>
<div class="sep"></div>
<button class="btn gd" onclick="doExport()">EXPORT</button>
<button class="btn" onclick="doExportGraph()">GRAPH</button>
</div>

<script>
// ================================================================
// FULL v8.0 ENGINE (extracted)
// ================================================================
'''

module_js = '''

// ================================================================
// MODULE SYSTEM (layered on top of v8.0)
// ================================================================
var mods = {{fma:false, eng:true, pre:false}};
var fmaPhase = 0, fmaPhases = ['b0','circle','b1','b2','b3','done'];

function toggleMod(m){{
  mods[m] = !mods[m];
  document.getElementById('mb-'+m).classList.toggle('on', mods[m]);
  applyMods();
  if(m==='fma' && mods.fma) startFMA();
  if(m==='pre' && mods.pre) startPresent();
}}

function applyMods(){{
  document.getElementById('bar').classList.toggle('active', mods.eng);
  document.getElementById('hud').classList.toggle('active', mods.eng || mods.pre);
  document.getElementById('euler').classList.toggle('active', mods.eng);
  document.getElementById('title').classList.toggle('active', mods.eng);
  document.getElementById('axiom-log').classList.toggle('active', mods.eng);
}}

// FMA
function startFMA(){{ fmaPhase=0; document.getElementById('b0').classList.add('active'); }}
function fmaNext(){{
  var cur=fmaPhases[fmaPhase];
  if(cur.startsWith('b')) document.getElementById(cur).classList.remove('active');
  if(cur==='circle') document.getElementById('circlePhase').classList.remove('active');
  fmaPhase++;
  if(fmaPhase>=fmaPhases.length){{ mods.fma=false; document.getElementById('mb-fma').classList.remove('on'); return; }}
  var nxt=fmaPhases[fmaPhase];
  if(nxt.startsWith('b')) document.getElementById(nxt).classList.add('active');
  else if(nxt==='circle'){{ document.getElementById('circlePhase').classList.add('active'); drawCircle(); }}
  else if(nxt==='done'){{ mods.fma=false; document.getElementById('mb-fma').classList.remove('on');
    if(mods.pre) startPresent(); else if(!gkState) doSeed(); }}
}}

function drawCircle(){{
  var c=document.getElementById('tCircle'),ct=c.getContext('2d'),cx=300,cy=300,R=260,phi=(1+Math.sqrt(5))/2,step=0,mx=300;
  function anim(){{
    step++;var t=step/mx;ct.fillStyle='rgba(0,0,0,0.05)';ct.fillRect(0,0,600,600);
    ct.strokeStyle='rgba(80,120,255,'+(0.3+0.4*t)+')';ct.lineWidth=1.5;
    ct.beginPath();ct.arc(cx,cy,R,0,Math.PI*2);ct.stroke();
    ct.beginPath();ct.arc(cx,cy,R*0.85,0,Math.PI*2);ct.stroke();
    ct.beginPath();ct.arc(cx,cy,R*0.15,0,Math.PI*2);ct.stroke();
    for(var i=0;i<12;i++){{var a=(i/12)*Math.PI*2-Math.PI/2+step*0.002,r=(i<6)?R*0.65:R*0.35;if(i===0)r=0;
      var px=cx+Math.cos(a)*r,py=cy+Math.sin(a)*r;ct.strokeStyle='rgba(100,160,255,'+(0.2+0.6*t)+')';ct.lineWidth=1;ct.beginPath();
      for(var k=0;k<5;k++){{var pa=(k/5)*Math.PI*2-Math.PI/2,pr=12+8*t;k===0?ct.moveTo(px+Math.cos(pa)*pr,py+Math.sin(pa)*pr):ct.lineTo(px+Math.cos(pa)*pr,py+Math.sin(pa)*pr);}}ct.closePath();ct.stroke();}}
    ct.strokeStyle='rgba(60,100,200,'+(0.1+0.3*t)+')';ct.lineWidth=0.5;
    for(var i=0;i<12;i++)for(var j=i+1;j<12;j++)if((j-i)%3===0||(j-i)===5){{var a1=(i/12)*Math.PI*2-Math.PI/2+step*0.002,a2=(j/12)*Math.PI*2-Math.PI/2+step*0.002,r1=(i<6)?R*0.65:R*0.35,r2=(j<6)?R*0.65:R*0.35;if(i===0)r1=0;if(j===0)r2=0;
      ct.beginPath();ct.moveTo(cx+Math.cos(a1)*r1,cy+Math.sin(a1)*r1);ct.lineTo(cx+Math.cos(a2)*r2,cy+Math.sin(a2)*r2);ct.stroke();}}
    ct.strokeStyle='rgba(120,180,255,'+(0.2+0.5*t)+')';ct.lineWidth=1;ct.beginPath();
    for(var i=0;i<3;i++){{var a=(i/3)*Math.PI*2-Math.PI/2;i===0?ct.moveTo(cx+Math.cos(a)*R*0.5,cy+Math.sin(a)*R*0.5):ct.lineTo(cx+Math.cos(a)*R*0.5,cy+Math.sin(a)*R*0.5);}}ct.closePath();ct.stroke();
    ct.strokeStyle='rgba(80,140,255,'+(0.1+0.2*t)+')';ct.lineWidth=0.8;ct.beginPath();
    for(var s=0;s<200*t;s++){{var sa=s*0.1+step*0.01,sr=5+s*0.4*phi*0.1;if(sr>R)break;s===0?ct.moveTo(cx+Math.cos(sa)*sr,cy+Math.sin(sa)*sr):ct.lineTo(cx+Math.cos(sa)*sr,cy+Math.sin(sa)*sr);}}ct.stroke();
    if(t>0.5){{ct.save();ct.font='9px Cinzel';ct.fillStyle='rgba(80,120,200,'+(t-0.5)*1.5+')';var w='V-E+F=2 . P=12 . chi=2 . ALWAYS . EULER 1758 . GOLDBERG 1937 . ';
      for(var i=0;i<w.length;i++){{var wa=(i/w.length)*Math.PI*2-Math.PI/2+step*0.003;ct.save();ct.translate(cx+Math.cos(wa)*(R+15),cy+Math.sin(wa)*(R+15));ct.rotate(wa+Math.PI/2);ct.fillText(w[i],0,0);ct.restore();}}ct.restore();}}
    if(step<mx)requestAnimationFrame(anim);
    else setTimeout(function(){{document.getElementById('circlePhase').classList.remove('active');fmaPhase++;
      var nxt=fmaPhases[fmaPhase];if(nxt&&nxt.startsWith('b'))document.getElementById(nxt).classList.add('active');
      else if(nxt==='done'){{mods.fma=false;document.getElementById('mb-fma').classList.remove('on');
        if(mods.pre)startPresent();else if(!gkState)doSeed();}}}},2000);
  }}anim();
}}

// PRESENT
var PSCRIPT = [
  {{t:0,     action:'msg',    text:'Initializing...'}},
  {{t:1000,  action:'seed'}},
  {{t:1800,  action:'msg',    text:'Refining topology...'}},
  {{t:2500,  action:'refine'}},
  {{t:3500,  action:'refine'}},
  {{t:4500,  action:'refine'}},
  {{t:5500,  action:'zoom',   value:400}},
  {{t:6000,  action:'msg',    text:'The structure reveals itself.'}},
  {{t:7500,  action:'spin',   value:0.003}},
  {{t:8000,  action:'hideUI'}},
  {{t:9000,  action:'msg',    text:'Explore.'}},
  {{t:11000, action:'clearMsg'}}
];

function startPresent(){{
  PSCRIPT.forEach(function(step){{
    setTimeout(function(){{
      switch(step.action){{
        case 'seed': doSeed(); break;
        case 'refine': doRefineAll(); break;
        case 'zoom': cam.zoom=step.value; document.getElementById('sl-zm').value=step.value; break;
        case 'spin': cam.spin=step.value; break;
        case 'hideUI':
          mods.eng=false; document.getElementById('mb-eng').classList.remove('on'); applyMods(); break;
        case 'msg':
          var el=document.getElementById('pmsg');el.textContent=step.text;el.classList.add('active'); break;
        case 'clearMsg':
          document.getElementById('pmsg').classList.remove('active'); break;
      }}
    }}, step.t);
  }});
}}

// BOOT
applyMods();
doSeed();
animate();
console.log('%c[GF] GENESIS FINAL v2 loaded','color:#00ffd5;font-size:14px');
</script>
</body></html>
'''

# Replace image placeholders
part1 = part1.replace('IMG0_B64', img0)
part1 = part1.replace('IMG1_B64', img1)
part1 = part1.replace('IMG2_B64', img2)
part1 = part1.replace('IMG3_B64', img3)

# Strip double braces from BOTH parts (were originally f-strings)
part1 = part1.replace('{{', '{').replace('}}', '}')
module_js = module_js.replace('{{', '{').replace('}}', '}')

html = part1 + v8_js + module_js
OUT.write_text(html, encoding='utf-8')
print(f"Written: {OUT} ({len(html)//1024} KB)")

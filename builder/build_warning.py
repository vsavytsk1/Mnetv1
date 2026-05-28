#!/usr/bin/env python3
"""Build SpookyWarning v1.3 — FMA intro + auto-build + pinch-to-zoom (mobile)."""
import base64, re
from pathlib import Path
from io import BytesIO
from PIL import Image

ROOT = Path(__file__).parent.parent.parent
V8 = ROOT / "shell" / "genesis_v8.0.html"
GATE_IMG = ROOT / "shell" / "gate" / "img"
OUT = Path(__file__).parent / "warning_v1.3.html"

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

print("Building SpookyWarning v1.3...")
img0 = img_b64("gate_closed")
img1 = img_b64("gate_open")
img2 = img_b64("truth")
img3 = img_b64("exchange")
print(f"  Images: {sum(len(x)//1024 for x in [img0,img1,img2,img3])}KB")

# Extract v8 JS
v8_html = V8.read_text(encoding='utf-8')
script_match = re.search(r'<script>\s*// ={10,}', v8_html)
script_start = script_match.start() + len('<script>')
script_end = v8_html.rfind('</script>')
v8_js = v8_html[script_start:script_end]
v8_js = v8_js.replace('animate();', '// animate();')
v8_js = v8_js.replace('spin: 0.005', 'spin: 0')
print(f"  v8 JS: {len(v8_js)//1024}KB")

part1 = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SpookyWarning v1.3 — The Gate</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{background:#050508;color:#c8d8e8;font-family:'Courier New',monospace;overflow:hidden;touch-action:none;cursor:pointer}
#cv{position:fixed;top:0;left:0;z-index:0}

/* FMA */
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

/* HUD (minimal, appears after FMA) */
#hud{position:fixed;top:10px;left:10px;z-index:5;pointer-events:none;font-size:10px;line-height:1.7;opacity:0;transition:opacity 2s ease}
#hud.active{opacity:1}
.lbl{color:#444}.val{color:#00ffd5}.vp{color:#ff69b4}.vg{color:#ffd700}
#euler{position:fixed;top:10px;left:50%;transform:translateX(-50%);z-index:5;pointer-events:none;
  font-family:'Orbitron';font-size:16px;font-weight:900;opacity:0;transition:opacity 2s ease}

/* MOBILE */
@media(max-width:768px){
  .banner-text{font-size:12px;letter-spacing:3px;padding:0 20px}
  .banner-sub{font-size:9px;letter-spacing:2px;padding:0 20px}
  .banner-click{font-size:9px;letter-spacing:3px}
  .banner img{max-height:45vh;max-width:90vw}
  #tCircle{width:340px!important;height:340px!important}
  #euler{font-size:11px}
  #hud{font-size:8px}
}
#euler.active{opacity:1}
#euler .ok{color:#00ffd5}

/* Hidden elements needed by v8 engine */
#title{display:none}
#axiom-log{display:none}
#bar{display:none}
#load{display:none}
</style></head><body>

<!-- FMA BANNERS (auto-start) -->
<div class="banner active" id="b0" onclick="fmaNext()">
  <img src="IMG0_B64" alt="Gate">
  <div class="banner-text">Do you want to begin the journey?</div>
  <div class="banner-sub">There is a price. There is always a price.</div>
  <div class="banner-click">[ click anywhere ]</div>
</div>
<div id="circlePhase"><canvas id="tCircle" width="600" height="600"></canvas></div>
<div class="banner" id="b1" onclick="fmaNext()">
  <img src="IMG1_B64" alt="Gate Opens">
  <div class="banner-text">The Gate opens for those who understand equivalent exchange.</div>
  <div class="banner-click">[ click to enter ]</div>
</div>
<div class="banner" id="b2" onclick="fmaNext()">
  <img src="IMG2_B64" alt="Truth">
  <div class="banner-text">Oh? Hello there, explorer.</div>
  <div class="banner-sub" style="color:#667">Have you read the license?<br>
    <a href="https://vsavytsk1.github.io/Mnetv1/shell/spooky_warning/" target="_blank" onclick="event.stopPropagation()"
       style="color:#4466aa;text-decoration:none;letter-spacing:2px;font-size:12px">&#8599; LICENSE &amp; DEDICATION TO HUMANITY</a></div>
  <div class="banner-click">[ I understand. Show me. ]</div>
</div>
<div class="banner" id="b3" onclick="fmaNext()">
  <img src="IMG3_B64" alt="Exchange">
  <div class="banner-text">The only price is compute.</div>
  <div class="banner-sub">V &#8722; E + F = 2 &middot; P = 12 &middot; always</div>
  <div class="banner-click">[ pay the price ]</div>
</div>

<canvas id="cv"></canvas>
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
<!-- Hidden but needed by v8 engine -->
<div id="title"></div>
<div id="axiom-log"></div>
<div id="bar">
  <span id="flowState"></span>
  <input type="range" id="sl-flowx" value="0">
  <span id="sv-flowx"></span>
  <input type="range" id="sl-inner" value="45"><span id="sv-inner"></span>
  <input type="range" id="sl-mid" value="70"><span id="sv-mid"></span>
  <input type="range" id="sl-jit" value="0"><span id="sv-jit"></span>
  <input type="range" id="sl-zm" value="571"><span id="sv-zm"></span>
  <input type="range" id="sl-atom" value="1"><span id="sv-atom"></span>
  <input type="range" id="sl-maxf" value="100"><span id="sv-maxf"></span>
  <input type="range" id="sl-spin" value="0"><span id="sv-spin"></span>
  <span id="mobState"></span>
  <input type="range" id="mobSlider" value="0"><span id="twistVal"></span>
</div>
<div id="load"></div>

<script>
// === FULL v8.0 ENGINE ===
'''

module_js = '''

// ================================================================
// SPOOKY WARNING — FMA auto-start, build during intro
// ================================================================
var fmaPhase = 0;
var fmaPhases = ['b0','circle','b1','b2','b3','done'];
var buildStep = 0;
var isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
var maxRefines = isMobile ? 3 : 4;  // mobile: 10292F, desktop: 72032F
console.log('[SW] Device: '+(isMobile?'MOBILE (3 refines)':'DESKTOP (4 refines)'));

function fmaNext(){
  var cur = fmaPhases[fmaPhase];
  if(cur.startsWith('b')) document.getElementById(cur).classList.remove('active');
  if(cur==='circle') document.getElementById('circlePhase').classList.remove('active');
  fmaPhase++;

  // BUILD SHAPE IN BACKGROUND during each click
  if(buildStep === 0){ doSeed(); buildStep++; }
  else if(buildStep <= maxRefines){ doRefineAll(); buildStep++; }

  if(fmaPhase >= fmaPhases.length){
    // FMA DONE — reveal explorer
    document.body.style.cursor = 'grab';
    document.getElementById('hud').classList.add('active');
    document.getElementById('euler').classList.add('active');
    cam.zoom = 571;
    cam.atom = 0.1;
    cam.spin = 0.002;
    console.log('[SW] FMA complete. Shape ready. Explore.');
    return;
  }

  var nxt = fmaPhases[fmaPhase];
  if(nxt.startsWith('b')) document.getElementById(nxt).classList.add('active');
  else if(nxt==='circle'){ document.getElementById('circlePhase').classList.add('active'); drawCircle(); }
  else if(nxt==='done'){
    document.body.style.cursor = 'grab';
    document.getElementById('hud').classList.add('active');
    document.getElementById('euler').classList.add('active');
    cam.zoom = 571;
    cam.atom = 0.1;
    cam.spin = 0.002;
    console.log('[SW] FMA complete. Shape ready. Explore.');
  }
}

function drawCircle(){
  var c=document.getElementById('tCircle'),ct=c.getContext('2d'),cx=300,cy=300,R=260,phi=(1+Math.sqrt(5))/2,step=0,mx=250;
  function anim(){
    step++;var t=step/mx;ct.fillStyle='rgba(0,0,0,0.05)';ct.fillRect(0,0,600,600);
    ct.strokeStyle='rgba(80,120,255,'+(0.3+0.4*t)+')';ct.lineWidth=1.5;
    ct.beginPath();ct.arc(cx,cy,R,0,Math.PI*2);ct.stroke();
    ct.beginPath();ct.arc(cx,cy,R*0.85,0,Math.PI*2);ct.stroke();
    ct.beginPath();ct.arc(cx,cy,R*0.15,0,Math.PI*2);ct.stroke();
    for(var i=0;i<12;i++){var a=(i/12)*Math.PI*2-Math.PI/2+step*0.002,r=(i<6)?R*0.65:R*0.35;if(i===0)r=0;
      var px=cx+Math.cos(a)*r,py=cy+Math.sin(a)*r;ct.strokeStyle='rgba(100,160,255,'+(0.2+0.6*t)+')';ct.lineWidth=1;ct.beginPath();
      for(var k=0;k<5;k++){var pa=(k/5)*Math.PI*2-Math.PI/2,pr=12+8*t;k===0?ct.moveTo(px+Math.cos(pa)*pr,py+Math.sin(pa)*pr):ct.lineTo(px+Math.cos(pa)*pr,py+Math.sin(pa)*pr);}ct.closePath();ct.stroke();}
    ct.strokeStyle='rgba(60,100,200,'+(0.1+0.3*t)+')';ct.lineWidth=0.5;
    for(var i=0;i<12;i++)for(var j=i+1;j<12;j++)if((j-i)%3===0||(j-i)===5){var a1=(i/12)*Math.PI*2-Math.PI/2+step*0.002,a2=(j/12)*Math.PI*2-Math.PI/2+step*0.002,r1=(i<6)?R*0.65:R*0.35,r2=(j<6)?R*0.65:R*0.35;if(i===0)r1=0;if(j===0)r2=0;
      ct.beginPath();ct.moveTo(cx+Math.cos(a1)*r1,cy+Math.sin(a1)*r1);ct.lineTo(cx+Math.cos(a2)*r2,cy+Math.sin(a2)*r2);ct.stroke();}
    ct.strokeStyle='rgba(120,180,255,'+(0.2+0.5*t)+')';ct.lineWidth=1;ct.beginPath();
    for(var i=0;i<3;i++){var a=(i/3)*Math.PI*2-Math.PI/2;i===0?ct.moveTo(cx+Math.cos(a)*R*0.5,cy+Math.sin(a)*R*0.5):ct.lineTo(cx+Math.cos(a)*R*0.5,cy+Math.sin(a)*R*0.5);}ct.closePath();ct.stroke();
    ct.strokeStyle='rgba(80,140,255,'+(0.1+0.2*t)+')';ct.lineWidth=0.8;ct.beginPath();
    for(var s=0;s<200*t;s++){var sa=s*0.1+step*0.01,sr=5+s*0.4*phi*0.1;if(sr>R)break;s===0?ct.moveTo(cx+Math.cos(sa)*sr,cy+Math.sin(sa)*sr):ct.lineTo(cx+Math.cos(sa)*sr,cy+Math.sin(sa)*sr);}ct.stroke();
    if(t>0.5){ct.save();ct.font='9px Cinzel';ct.fillStyle='rgba(80,120,200,'+(t-0.5)*1.5+')';var w='V-E+F=2 . P=12 . chi=2 . ALWAYS . EULER 1758 . GOLDBERG 1937 . ';
      for(var i=0;i<w.length;i++){var wa=(i/w.length)*Math.PI*2-Math.PI/2+step*0.003;ct.save();ct.translate(cx+Math.cos(wa)*(R+15),cy+Math.sin(wa)*(R+15));ct.rotate(wa+Math.PI/2);ct.fillText(w[i],0,0);ct.restore();}ct.restore();}
    if(step<mx)requestAnimationFrame(anim);
    else setTimeout(function(){
      // Build during circle too
      if(buildStep===0){doSeed();buildStep++;}
      else if(buildStep <= maxRefines){ doRefineAll(); buildStep++; }
      document.getElementById('circlePhase').classList.remove('active');
      fmaPhase++;
      var nxt=fmaPhases[fmaPhase];
      if(nxt&&nxt.startsWith('b'))document.getElementById(nxt).classList.add('active');
      else if(nxt==='done'){
        document.body.style.cursor='grab';
        document.getElementById('hud').classList.add('active');
        document.getElementById('euler').classList.add('active');
        cam.zoom=571;cam.atom=0.1;cam.spin=0.002;
      }
    },1500);
  }anim();
}

// BOOT — start rendering immediately, FMA overlays on top
cam.spin = 0;
cam.zoom = 571;
cam.atom = 0.1;
cam.maxFaces = 50000;
animate();
console.log('%c[SW] SpookyWarning v1.3 loaded — built by builder, pinch-zoom from engine','color:#ff69b4;font-size:14px');
console.log('[SW] FMA auto-started. Shape builds during intro.');
</script>
</body></html>
'''

# Assemble
part1 = part1.replace('IMG0_B64', img0).replace('IMG1_B64', img1).replace('IMG2_B64', img2).replace('IMG3_B64', img3)
html = part1 + v8_js + module_js
OUT.write_text(html, encoding='utf-8')
print(f"Written: {OUT} ({len(html)//1024} KB)")
print("  Pinch-to-zoom extracted from genesis_v8.0 engine via build.")

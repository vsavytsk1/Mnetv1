#!/usr/bin/env python3

"""Rebuild gate_v1.html with proper structure, kernel fallback, and images."""
import base64
from pathlib import Path
from io import BytesIO
from PIL import Image

GATE_DIR = Path(__file__).parent
IMG_DIR = GATE_DIR / "img"
KERNEL = GATE_DIR.parent.parent / "kernel" / "goldberg_kernel.js"
OUT = GATE_DIR / "gate_v1.html"

def img_to_b64(name):
    for ext in ['.jpeg','.jpg','.png','.webp']:
        p = IMG_DIR / f"{name}{ext}"
        if p.exists():
            img = Image.open(p)
            if img.mode != 'RGB':
                bg = Image.new('RGB', img.size, (0,0,0))
                if img.mode == 'P': img = img.convert('RGBA')
                bg.paste(img, mask=img.split()[-1] if img.mode=='RGBA' else None)
                img = bg
            w,h = img.size
            if w>1200 or h>900:
                r = min(1200/w, 900/h)
                img = img.resize((int(w*r),int(h*r)), Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format='JPEG', quality=85, optimize=True)
            return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"
    return ""

print("Building images...")
img0 = img_to_b64("gate_closed")
img1 = img_to_b64("gate_open")  
img2 = img_to_b64("truth")
img3 = img_to_b64("exchange")
print(f"  gate_closed: {len(img0)//1024}KB  gate_open: {len(img1)//1024}KB  truth: {len(img2)//1024}KB  exchange: {len(img3)//1024}KB")

# Read kernel JS
kernel_js = KERNEL.read_text(encoding='utf-8')
print(f"  kernel: {len(kernel_js)//1024}KB inlined")

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Gate</title>
<script>
// === GOLDBERG KERNEL (inlined) ===
{kernel_js}
<\/script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap');
body{{background:#000;color:#c8c8c8;font-family:'Cinzel','Times New Roman',serif;overflow:hidden;width:100vw;height:100vh;cursor:pointer}}
.banner{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:100;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#000;opacity:0;pointer-events:none;transition:opacity 1.2s ease}}
.banner.active{{opacity:1;pointer-events:all}}
.banner img{{max-height:70vh;max-width:85vw;object-fit:contain;filter:brightness(0.9);border-radius:4px}}
.banner-text{{color:#8899bb;font-size:15px;letter-spacing:5px;text-transform:uppercase;margin-top:24px;text-shadow:0 0 30px rgba(100,150,255,0.4);text-align:center;max-width:600px}}
.banner-sub{{color:#556;font-size:11px;letter-spacing:3px;margin-top:12px;text-align:center}}
.banner-click{{color:#556;font-size:10px;letter-spacing:4px;margin-top:20px;animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:0.3}}50%{{opacity:1}}}}
#circlePhase{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:90;display:flex;align-items:center;justify-content:center;background:#000;opacity:0;pointer-events:none;transition:opacity 1.5s ease}}
#circlePhase.active{{opacity:1;pointer-events:all}}
#tCircle{{border-radius:50%;box-shadow:0 0 60px rgba(60,100,220,0.4),0 0 160px rgba(60,100,220,0.15)}}
#explorer{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:80;display:none;background:#050508}}
#explorer.active{{display:block}}
#explorerCanvas{{width:100%;height:100%}}
#hud{{position:fixed;top:10px;left:10px;z-index:85;color:#00ffd5;font-family:monospace;font-size:10px;line-height:1.6;pointer-events:none;display:none}}
#hud.active{{display:block}}
</style>
</head>
<body>

<div class="banner active" id="b0" onclick="nextPhase()">
  <img src="{img0}" alt="The Gate">
  <div class="banner-text">Do you want to begin the journey?</div>
  <div class="banner-sub">There is a price. There is always a price.</div>
  <div class="banner-click">[ click anywhere ]</div>
</div>

<div id="circlePhase">
  <canvas id="tCircle" width="600" height="600"></canvas>
</div>

<div class="banner" id="b1" onclick="nextPhase()">
  <img src="{img1}" alt="The Gate Opens">
  <div class="banner-text">The Gate opens for those who understand equivalent exchange.</div>
  <div class="banner-click">[ click to enter ]</div>
</div>

<div class="banner" id="b2" onclick="nextPhase()">
  <img src="{img2}" alt="Truth">
  <div class="banner-text">Oh? Hello there, explorer.</div>
  <div class="banner-sub" style="color:#667">Have you read the license?<br>
    <a href="https://vsavytsk1.github.io/SpookyPrimes/" target="_blank" onclick="event.stopPropagation()" style="color:#4466aa;text-decoration:none;letter-spacing:2px;font-size:12px">&#8599; The Dodecahedron of Open Questions &#8212; LICENSE</a>
  </div>
  <div class="banner-click">[ I understand. Show me. ]</div>
</div>

<div class="banner" id="b3" onclick="nextPhase()">
  <img src="{img3}" alt="Equivalent Exchange">
  <div class="banner-text">The only price is compute.</div>
  <div class="banner-sub">V &#8722; E + F = 2 &nbsp;&middot;&nbsp; P = 12 &nbsp;&middot;&nbsp; always</div>
  <div class="banner-click">[ pay the price ]</div>
</div>

<div id="explorer"><canvas id="explorerCanvas"></canvas></div>
<div id="hud"></div>

<script>
var phase=0, phases=['b0','circle','b1','b2','b3','explore'];
var faces=[], cam={{rx:0.3,ry:0,zoom:350,spin:0.003}};

function nextPhase(){{
  var cur=phases[phase];
  if(cur.startsWith('b')) document.getElementById(cur).classList.remove('active');
  if(cur==='circle') document.getElementById('circlePhase').classList.remove('active');
  phase++;
  if(phase>=phases.length) return;
  var nxt=phases[phase];
  console.log('[GATE] Phase '+phase+': '+nxt);
  if(nxt.startsWith('b')) document.getElementById(nxt).classList.add('active');
  else if(nxt==='circle'){{ document.getElementById('circlePhase').classList.add('active'); drawTransmutationCircle(); }}
  else if(nxt==='explore') launchExplorer();
}}

function drawTransmutationCircle(){{
  var c=document.getElementById('tCircle'),ctx=c.getContext('2d'),cx=300,cy=300,R=260,phi=(1+Math.sqrt(5))/2,step=0,max=300;
  function anim(){{
    step++;var t=step/max;
    ctx.fillStyle='rgba(0,0,0,0.05)';ctx.fillRect(0,0,600,600);
    ctx.strokeStyle='rgba(80,120,255,'+(0.3+0.4*t)+')';ctx.lineWidth=1.5;
    ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.stroke();
    ctx.beginPath();ctx.arc(cx,cy,R*0.85,0,Math.PI*2);ctx.stroke();
    ctx.beginPath();ctx.arc(cx,cy,R*0.15,0,Math.PI*2);ctx.stroke();
    for(var i=0;i<12;i++){{var a=(i/12)*Math.PI*2-Math.PI/2+step*0.002,r=(i<6)?R*0.65:R*0.35;if(i===0)r=0;var px=cx+Math.cos(a)*r,py=cy+Math.sin(a)*r;ctx.strokeStyle='rgba(100,160,255,'+(0.2+0.6*t)+')';ctx.lineWidth=1;ctx.beginPath();for(var k=0;k<5;k++){{var pa=(k/5)*Math.PI*2-Math.PI/2,pr=12+8*t;k===0?ctx.moveTo(px+Math.cos(pa)*pr,py+Math.sin(pa)*pr):ctx.lineTo(px+Math.cos(pa)*pr,py+Math.sin(pa)*pr);}}ctx.closePath();ctx.stroke();}}
    ctx.strokeStyle='rgba(60,100,200,'+(0.1+0.3*t)+')';ctx.lineWidth=0.5;
    for(var i=0;i<12;i++)for(var j=i+1;j<12;j++)if((j-i)%3===0||(j-i)===5){{var a1=(i/12)*Math.PI*2-Math.PI/2+step*0.002,a2=(j/12)*Math.PI*2-Math.PI/2+step*0.002,r1=(i<6)?R*0.65:R*0.35,r2=(j<6)?R*0.65:R*0.35;if(i===0)r1=0;if(j===0)r2=0;ctx.beginPath();ctx.moveTo(cx+Math.cos(a1)*r1,cy+Math.sin(a1)*r1);ctx.lineTo(cx+Math.cos(a2)*r2,cy+Math.sin(a2)*r2);ctx.stroke();}}
    ctx.strokeStyle='rgba(120,180,255,'+(0.2+0.5*t)+')';ctx.lineWidth=1;ctx.beginPath();for(var i=0;i<3;i++){{var a=(i/3)*Math.PI*2-Math.PI/2;i===0?ctx.moveTo(cx+Math.cos(a)*R*0.5,cy+Math.sin(a)*R*0.5):ctx.lineTo(cx+Math.cos(a)*R*0.5,cy+Math.sin(a)*R*0.5);}}ctx.closePath();ctx.stroke();
    ctx.strokeStyle='rgba(80,140,255,'+(0.1+0.2*t)+')';ctx.lineWidth=0.8;ctx.beginPath();for(var s=0;s<200*t;s++){{var sa=s*0.1+step*0.01,sr=5+s*0.4*phi*0.1;if(sr>R)break;s===0?ctx.moveTo(cx+Math.cos(sa)*sr,cy+Math.sin(sa)*sr):ctx.lineTo(cx+Math.cos(sa)*sr,cy+Math.sin(sa)*sr);}}ctx.stroke();
    if(t>0.5){{ctx.save();ctx.font='9px Cinzel';ctx.fillStyle='rgba(80,120,200,'+(t-0.5)*1.5+')';var w='V-E+F=2 . P=12 . phi . chi=2 . ALWAYS . EULER 1758 . GOLDBERG 1937 . ';for(var i=0;i<w.length;i++){{var wa=(i/w.length)*Math.PI*2-Math.PI/2+step*0.003;ctx.save();ctx.translate(cx+Math.cos(wa)*(R+15),cy+Math.sin(wa)*(R+15));ctx.rotate(wa+Math.PI/2);ctx.fillText(w[i],0,0);ctx.restore();}}ctx.restore();}}
    if(step<max)requestAnimationFrame(anim);
    else setTimeout(function(){{document.getElementById('circlePhase').classList.remove('active');phase++;console.log('[GATE] Phase '+phase+': '+phases[phase]);document.getElementById(phases[phase]).classList.add('active');}},2000);
  }}anim();
}}

function launchExplorer(){{
  var K=window.GK||GK;
  console.log('[GATE] Kernel loaded. Building the Truth...');
  document.getElementById('explorer').classList.add('active');
  document.getElementById('hud').classList.add('active');
  document.body.style.cursor='grab';
  var state=K.buildC60();
  state=K.refineAll(state);state=K.refineAll(state);
  faces=state.faces;
  var inv=K.invariants(state);
  var chi=inv.vertices-inv.edges+inv.faces;
  var ev=inv.edges/Math.max(inv.vertices,1);
  console.log('[GATE] Truth built: '+inv.faces+' faces, chi='+chi+', P='+inv.pents);
  document.getElementById('hud').innerHTML='<span style="color:#ff69b4">THE TRUTH</span><br>Faces: '+inv.faces+'<br>Pentagons: <span style="color:#ff69b4">'+inv.pents+'</span><br>\u03C7 = V\u2212E+F = <span style="color:#ffd700">'+chi+'</span><br>E/V = '+ev.toFixed(3)+'<br><br><span style="color:#334">drag to rotate . scroll to zoom</span>';
  var c=document.getElementById('explorerCanvas');c.width=window.innerWidth;c.height=window.innerHeight;var ctx=c.getContext('2d');
  faces.forEach(function(f){{f._jpts=f.pts.map(function(p){{return[p[0]+(Math.random()-0.5)*0.06,p[1]+(Math.random()-0.5)*0.06,p[2]+(Math.random()-0.5)*0.06];}});}});
  var drag=false,lx=0,ly=0;
  c.addEventListener('mousedown',function(e){{drag=true;lx=e.clientX;ly=e.clientY;cam.spin=0}});
  c.addEventListener('mousemove',function(e){{if(!drag)return;cam.ry+=(e.clientX-lx)*0.005;cam.rx+=(e.clientY-ly)*0.005;lx=e.clientX;ly=e.clientY;}});
  c.addEventListener('mouseup',function(){{drag=false}});
  c.addEventListener('wheel',function(e){{cam.zoom*=e.deltaY>0?0.95:1.05}},{{passive:true}});
  function render(){{
    var W=c.width,H=c.height;ctx.fillStyle='rgba(2,2,5,0.15)';ctx.fillRect(0,0,W,H);cam.ry+=cam.spin;
    var cy2=Math.cos(cam.ry),sy2=Math.sin(cam.ry),cx2=Math.cos(cam.rx),sx2=Math.sin(cam.rx);
    function proj(p){{var x=p[0],y=p[1],z=p[2],x1=x*cy2-z*sy2,z1=x*sy2+z*cy2,y1=y*cx2-z1*sx2,z2=y*sx2+z1*cx2,s=cam.zoom/(z2+5);return{{x:W/2+x1*s,y:H/2+y1*s,z:z2,s:s}};}}
    faces.forEach(function(f){{var pts=f._jpts,n=pts.length;for(var i=0;i<n;i++){{var a=proj(pts[i]),b=proj(pts[(i+1)%n]);if(a.z<-4||b.z<-4)return;var bright=Math.max(0.05,Math.min(0.7,1.0/((a.z+b.z)/2+4)));ctx.strokeStyle=f.type==='pent'?'rgba(255,100,180,'+bright+')':'rgba(60,140,255,'+bright*0.6+')';ctx.lineWidth=f.type==='pent'?1.2:0.4;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}}}});
    faces.forEach(function(f){{if(f.type!=='pent')return;var ctr=f.pts.reduce(function(a,b){{return[a[0]+b[0],a[1]+b[1],a[2]+b[2]]}});ctr=[ctr[0]/f.pts.length,ctr[1]/f.pts.length,ctr[2]/f.pts.length];var p=proj(ctr);if(p.z<-4)return;var r=3+2*p.s/cam.zoom*100;var g=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,r);g.addColorStop(0,'rgba(255,180,255,0.6)');g.addColorStop(1,'rgba(255,100,180,0)');ctx.fillStyle=g;ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fill();}});
    requestAnimationFrame(render);
  }}render();
}}

console.log('%c[GATE] The Gate v1.2 loaded','color:#8899bb;font-size:14px');
console.log('[GATE] Kernel: '+(typeof GK!=='undefined'?'INLINED':'MISSING'));
console.log('[GATE] Phase 0: The Gate awaits.');
</script>
</body>
</html>'''

# Fix escaped script tags
html = html.replace('<\\/script>', '</script>')

OUT.write_text(html, encoding='utf-8')
print(f"Written: {OUT} ({len(html)//1024} KB)")

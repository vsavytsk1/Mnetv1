#!/usr/bin/env python3
"""
GENESIS Kernel Pack v1.0
========================
Self-contained portable launcher.
Embeds the Goldberg kernel + visualization as pure HTML/JS.
Opens default Windows browser. Zero dependencies at runtime.

Build to .exe:
    pip install pyinstaller
    pyinstaller --onefile --noconsole genesis_pack.py

Then double-click genesis_pack.exe on any Windows 11 machine. That's it.
"""

import tempfile
import os
import webbrowser
import sys

# ============================================================================
#  THE PAYLOAD — Kernel + Shell packed into one HTML string
# ============================================================================
HTML_PAYLOAD = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>GENESIS — Goldberg Kernel</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#00ffc8;font-family:'Segoe UI',monospace;overflow:hidden;height:100vh}
#hud{position:fixed;top:12px;left:16px;z-index:10;font-size:13px;line-height:1.7;opacity:0.85}
#hud h1{font-size:22px;letter-spacing:3px;color:#00ffc8;margin-bottom:6px}
#hud .dim{color:#667}
#hud .val{color:#0ff}
#hud .pent{color:#ff6a00}
#controls{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);z-index:10;display:flex;gap:8px}
#controls button{background:#111;color:#00ffc8;border:1px solid #00ffc844;padding:8px 18px;
  border-radius:4px;cursor:pointer;font-family:monospace;font-size:13px;transition:0.2s}
#controls button:hover{background:#00ffc822;border-color:#00ffc8}
#controls button.active{background:#00ffc833;border-color:#00ffc8}
canvas{display:block;width:100vw;height:100vh}
#regime{position:fixed;top:12px;right:16px;z-index:10;font-size:12px;text-align:right;opacity:0.8}
#regime div{margin:2px 0}
</style>
</head>
<body>
<div id="hud">
  <h1>⬡ GENESIS KERNEL</h1>
  <div>Level: <span class="val" id="hLevel">0</span></div>
  <div>Faces: <span class="val" id="hFaces">-</span>
    (<span class="pent" id="hPents">-</span>P + <span class="val" id="hHexes">-</span>H)</div>
  <div>Vertices: <span class="val" id="hVerts">-</span> &nbsp; Edges: <span class="val" id="hEdges">-</span></div>
  <div>χ = V−E+F = <span class="val" id="hChi">-</span></div>
  <div class="dim">φ = (1+√5)/2 = <span class="val">1.6180339887...</span></div>
  <div class="dim" id="hFPS"></div>
</div>
<div id="regime">
  <div style="color:#00ffc8;font-size:14px;margin-bottom:4px">FLOW</div>
  <div id="rFlow">Pressure diffusion active</div>
  <div id="rSteps">Steps: <span id="hSteps">0</span></div>
</div>
<div id="controls">
  <button onclick="setLevel(0)" id="bL0" class="active">L0 · 12F</button>
  <button onclick="setLevel(1)" id="bL1">L1 · 72F</button>
  <button onclick="setLevel(2)" id="bL2">L2 · 492F</button>
  <button onclick="setLevel(3)" id="bL3">L3 · 3432F</button>
  <button onclick="toggleFlow()" id="bFlow">FLOW: ON</button>
  <button onclick="toggleSpin()" id="bSpin">SPIN: ON</button>
</div>
<canvas id="C"></canvas>

<script>
// ========================================================================
//  GOLDBERG KERNEL — inlined, minified core
// ========================================================================
var PHI=(1+Math.sqrt(5))/2;

// Vector ops
function v3(x,y,z){return[x,y,z]}
function vadd(a,b){return[a[0]+b[0],a[1]+b[1],a[2]+b[2]]}
function vsub(a,b){return[a[0]-b[0],a[1]-b[1],a[2]-b[2]]}
function vscale(a,s){return[a[0]*s,a[1]*s,a[2]*s]}
function vlen(a){return Math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])}
function vnorm(a){var L=vlen(a);return L>1e-12?vscale(a,1/L):[0,0,0]}
function vlerp(a,b,t){return[a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t,a[2]*(1-t)+b[2]*t]}
function vcross(a,b){return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}
function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]}

// Build C60 truncated icosahedron
function buildC60(){
  var raw=[];
  var perms=[[0,1,2],[1,2,0],[2,0,1]];
  function pushAll(a,b,c){
    for(var i=0;i<3;i++){var p=perms[i];
      for(var sa=-1;sa<=1;sa+=2)for(var sb=-1;sb<=1;sb+=2)for(var sc=-1;sc<=1;sc+=2){
        if(a===0&&sa===-1)continue;if(b===0&&sb===-1)continue;if(c===0&&sc===-1)continue;
        var v=[0,0,0];v[p[0]]=sa*a;v[p[1]]=sb*b;v[p[2]]=sc*c;raw.push(v);
      }
    }
  }
  pushAll(0,1,3*PHI);pushAll(1,2+PHI,2*PHI);pushAll(PHI,2,2*PHI+1);
  // Dedupe
  var verts=[];
  for(var i=0;i<raw.length;i++){var v=raw[i],found=false;
    for(var j=0;j<verts.length;j++){var u=verts[j];
      if(Math.abs(u[0]-v[0])<0.001&&Math.abs(u[1]-v[1])<0.001&&Math.abs(u[2]-v[2])<0.001){found=true;break}}
    if(!found)verts.push(v)}
  for(var i=0;i<verts.length;i++)verts[i]=vscale(vnorm(verts[i]),1.6);
  // Edges
  var minD=Infinity;
  for(var i=0;i<verts.length;i++)for(var j=i+1;j<verts.length;j++){var d=vlen(vsub(verts[i],verts[j]));if(d>0.01&&d<minD)minD=d}
  var eLen=minD,tol=eLen*0.05;
  var adj=[];
  for(var i=0;i<verts.length;i++){adj[i]=[];for(var j=0;j<verts.length;j++){if(i!==j&&Math.abs(vlen(vsub(verts[i],verts[j]))-eLen)<tol)adj[i].push(j)}}
  // Sort CCW
  for(var i=0;i<verts.length;i++){var v=verts[i],n=vnorm(v),ref=adj[i][0],rv=vsub(verts[ref],v),
    dt=vdot(rv,n),tan=vnorm(vsub(rv,vscale(n,dt))),e2=vcross(n,tan);
    adj[i].sort(function(a,b){var va=vsub(verts[a],v),vb=vsub(verts[b],v);
      return Math.atan2(vdot(va,e2),vdot(va,tan))-Math.atan2(vdot(vb,e2),vdot(vb,tan))})}
  // Trace faces
  function nxt(u,v){var idx=adj[v].indexOf(u);if(idx<0)return-1;return adj[v][(idx+adj[v].length-1)%adj[v].length]}
  var vis={},faces=[];
  for(var u=0;u<verts.length;u++)for(var k=0;k<adj[u].length;k++){var v=adj[u][k];
    if(vis[u+','+v])continue;var face=[u],a=u,b=v;
    for(var s=0;s<20;s++){vis[a+','+b]=true;var c=nxt(a,b);if(c<0||c===u)break;face.push(b);a=b;b=c}
    if(face[face.length-1]!==b)face.push(b);if(face.length===5||face.length===6)faces.push(face)}
  var seen={},unique=[];
  for(var i=0;i<faces.length;i++){var key=faces[i].slice().sort(function(a,b){return a-b}).join(',');
    if(!seen[key]){seen[key]=true;unique.push(faces[i])}}
  // Build mesh faces
  var mesh=[];
  for(var i=0;i<unique.length;i++){var f=unique[i],pts=[];
    for(var k=0;k<f.length;k++)pts.push(verts[f[k]].slice());
    mesh.push({pts:pts,type:f.length===5?'pent':'hex',level:0})}
  return mesh;
}

// Centroid
function centroid(pts){var c=[0,0,0];for(var i=0;i<pts.length;i++){c[0]+=pts[i][0];c[1]+=pts[i][1];c[2]+=pts[i][2]}return[c[0]/pts.length,c[1]/pts.length,c[2]/pts.length]}

// Refine all faces
function refineAll(faces){
  var out=[];
  for(var fi=0;fi<faces.length;fi++){
    var face=faces[fi],pts=face.pts,n=pts.length,c=centroid(pts);
    var inner=[],mid=[];
    for(var i=0;i<n;i++){inner.push(vlerp(c,pts[i],0.45));mid.push(vlerp(c,vlerp(pts[i],pts[(i+1)%n],0.5),0.70))}
    // Project to sphere
    for(var i=0;i<n;i++){inner[i]=vscale(vnorm(inner[i]),1.6);mid[i]=vscale(vnorm(mid[i]),1.6)}
    // Center face
    out.push({pts:inner.slice(),type:face.type,level:face.level+1});
    // Edge hexes
    for(var i=0;i<n;i++){var j=(i+1)%n;
      var em=vscale(vnorm(vlerp(pts[i],pts[j],0.5)),1.6);
      out.push({pts:[pts[i].slice(),em,pts[j].slice(),inner[j].slice(),mid[i].slice(),inner[i].slice()],type:'hex',level:face.level+1})}
  }
  return out;
}

// ========================================================================
//  FLOW ENGINE — pressure diffusion on face adjacency graph
// ========================================================================
function buildAdjacency(faces){
  var edgeMap={};
  for(var i=0;i<faces.length;i++){var pts=faces[i].pts,n=pts.length;
    for(var k=0;k<n;k++){var a=pts[k],b=pts[(k+1)%n];
      var key=[a[0].toFixed(3),a[1].toFixed(3),a[2].toFixed(3),b[0].toFixed(3),b[1].toFixed(3),b[2].toFixed(3)].join(',');
      var rkey=[b[0].toFixed(3),b[1].toFixed(3),b[2].toFixed(3),a[0].toFixed(3),a[1].toFixed(3),a[2].toFixed(3)].join(',');
      if(edgeMap[rkey]!==undefined){
        var j=edgeMap[rkey];
        if(!neighbors[i])neighbors[i]=[];if(!neighbors[j])neighbors[j]=[];
        if(neighbors[i].indexOf(j)<0)neighbors[i].push(j);
        if(neighbors[j].indexOf(i)<0)neighbors[j].push(i);
      }else{edgeMap[key]=i}
    }
  }
  return neighbors;
}
var neighbors;

function makeFlow(faces){
  var nF=faces.length;
  neighbors=new Array(nF);
  for(var i=0;i<nF;i++)neighbors[i]=[];
  var edgeMap={};
  for(var i=0;i<nF;i++){var pts=faces[i].pts,n=pts.length;
    for(var k=0;k<n;k++){var a=pts[k],b=pts[(k+1)%n];
      var key=a[0].toFixed(3)+','+a[1].toFixed(3)+','+a[2].toFixed(3)+','+b[0].toFixed(3)+','+b[1].toFixed(3)+','+b[2].toFixed(3);
      var rkey=b[0].toFixed(3)+','+b[1].toFixed(3)+','+b[2].toFixed(3)+','+a[0].toFixed(3)+','+a[1].toFixed(3)+','+a[2].toFixed(3);
      if(edgeMap[rkey]!==undefined){var j=edgeMap[rkey];
        if(neighbors[i].indexOf(j)<0)neighbors[i].push(j);
        if(neighbors[j].indexOf(i)<0)neighbors[j].push(i);
      }else{edgeMap[key]=i}
    }
  }
  var pressure=new Float32Array(nF);
  // Seed: source face = highest pressure
  var src=0;
  pressure[src]=1.0;
  return{pressure:pressure,source:src,steps:0,active:true};
}

function flowStep(fl){
  var p=fl.pressure,nF=p.length;
  var pNew=new Float32Array(nF);
  var mix=0.6,self=0.4;
  for(var i=0;i<nF;i++){
    var nb=neighbors[i],sum=0,cnt=nb.length;
    for(var k=0;k<cnt;k++)sum+=p[nb[k]];
    pNew[i]=p[i]*self+(cnt>0?sum/cnt:0)*mix;
  }
  pNew[fl.source]=1.0;
  fl.pressure=pNew;
  fl.steps++;
}

// ========================================================================
//  RENDERER — Canvas2D 3D projection
// ========================================================================
var canvas=document.getElementById('C'),ctx=canvas.getContext('2d');
var W,H;
function resize(){W=canvas.width=window.innerWidth;H=canvas.height=window.innerHeight}
window.addEventListener('resize',resize);resize();

var cam={ry:0,rx:0.3,zoom:3.8,spin:true,flowOn:true};
var curLevel=0,curFaces=null,flow=null,levels=[];
var totalSteps=0;

// Precompute levels
function init(){
  var f0=buildC60();
  levels=[f0];
  var f=f0;
  for(var i=0;i<3;i++){f=refineAll(f);levels.push(f)}
  setLevel(0);
}

function setLevel(n){
  curLevel=n;curFaces=levels[n];
  flow=makeFlow(curFaces);totalSteps=0;
  // Update HUD
  var nF=curFaces.length,pents=0,hexes=0;
  for(var i=0;i<nF;i++)if(curFaces[i].type==='pent')pents++;else hexes++;
  var fes=5*pents+6*hexes,V=Math.round(fes/3),E=Math.round(fes/2);
  document.getElementById('hLevel').textContent=n;
  document.getElementById('hFaces').textContent=nF;
  document.getElementById('hPents').textContent=pents;
  document.getElementById('hHexes').textContent=hexes;
  document.getElementById('hVerts').textContent=V;
  document.getElementById('hEdges').textContent=E;
  document.getElementById('hChi').textContent=(V-E+nF);
  // Buttons
  for(var i=0;i<=3;i++){var b=document.getElementById('bL'+i);b.className=i===n?'active':''}
}
function toggleFlow(){cam.flowOn=!cam.flowOn;document.getElementById('bFlow').textContent='FLOW: '+(cam.flowOn?'ON':'OFF');
  document.getElementById('bFlow').className=cam.flowOn?'active':''}
function toggleSpin(){cam.spin=!cam.spin;document.getElementById('bSpin').textContent='SPIN: '+(cam.spin?'ON':'OFF');
  document.getElementById('bSpin').className=cam.spin?'active':''}

// Mouse drag
var dragging=false,lastX=0,lastY=0;
canvas.addEventListener('mousedown',function(e){dragging=true;lastX=e.clientX;lastY=e.clientY});
window.addEventListener('mouseup',function(){dragging=false});
window.addEventListener('mousemove',function(e){if(!dragging)return;
  cam.ry+=(e.clientX-lastX)*0.005;cam.rx+=(e.clientY-lastY)*0.005;
  cam.rx=Math.max(-1.5,Math.min(1.5,cam.rx));lastX=e.clientX;lastY=e.clientY});
canvas.addEventListener('wheel',function(e){cam.zoom*=e.deltaY>0?1.08:0.93;cam.zoom=Math.max(1.5,Math.min(12,cam.zoom))},{passive:true});

// 3D projection
function project(p){
  var x=p[0],y=p[1],z=p[2];
  // Rotate Y
  var cy=Math.cos(cam.ry),sy=Math.sin(cam.ry);
  var x2=x*cy-z*sy,z2=x*sy+z*cy;
  // Rotate X
  var cx=Math.cos(cam.rx),sx=Math.sin(cam.rx);
  var y2=y*cx-z2*sx,z3=y*sx+z2*cx;
  var scale=W*0.18*cam.zoom/(z3+6);
  return{x:W/2+x2*scale,y:H/2-y2*scale,z:z3};
}

// Heatmap color
function heatColor(v){
  if(v<0.01)return'rgba(10,15,30,0.85)';
  var r=Math.min(255,Math.floor(v*400));
  var g=Math.min(255,Math.floor(v*255));
  var b=Math.max(0,Math.floor(180-v*300));
  return'rgba('+r+','+g+','+b+',0.88)';
}

// Main draw
function draw(){
  ctx.fillStyle='#0a0a0f';ctx.fillRect(0,0,W,H);
  if(!curFaces)return;

  // Sort faces by depth
  var sorted=[];
  for(var i=0;i<curFaces.length;i++){
    var c=centroid(curFaces[i].pts);
    var pj=project(c);
    sorted.push({idx:i,z:pj.z});
  }
  sorted.sort(function(a,b){return a.z-b.z});

  // Draw back-to-front
  var maxDraw=Math.min(sorted.length,25000);
  for(var si=0;si<maxDraw;si++){
    var i=sorted[si].idx;
    var face=curFaces[i],pts=face.pts;
    // Project all vertices
    var pp=[];
    for(var k=0;k<pts.length;k++)pp.push(project(pts[k]));
    // Backface cull
    if(pp.length>=3){
      var ax=pp[1].x-pp[0].x,ay=pp[1].y-pp[0].y;
      var bx=pp[2].x-pp[0].x,by=pp[2].y-pp[0].y;
      if(ax*by-ay*bx<0)continue;
    }
    // Fill
    var pv=flow?flow.pressure[i]:0;
    ctx.beginPath();ctx.moveTo(pp[0].x,pp[0].y);
    for(var k=1;k<pp.length;k++)ctx.lineTo(pp[k].x,pp[k].y);
    ctx.closePath();
    ctx.fillStyle=heatColor(pv);ctx.fill();
    // Stroke
    ctx.strokeStyle=face.type==='pent'?'rgba(255,106,0,0.5)':'rgba(0,255,200,0.18)';
    ctx.lineWidth=face.type==='pent'?1.5:0.5;
    ctx.stroke();
  }
}

// Animation loop
var lastT=0,frameCount=0,fps=0;
function animate(t){
  requestAnimationFrame(animate);
  // FPS
  frameCount++;
  if(t-lastT>1000){fps=frameCount;frameCount=0;lastT=t;
    document.getElementById('hFPS').textContent=fps+' fps'}
  // Spin
  if(cam.spin)cam.ry+=0.004;
  // Flow steps
  if(cam.flowOn&&flow&&flow.active){
    for(var i=0;i<3;i++){flowStep(flow);totalSteps++}
    document.getElementById('hSteps').textContent=totalSteps;
  }
  draw();
}

init();
requestAnimationFrame(animate);
</script>
</body>
</html>"""

# ============================================================================
#  LAUNCHER — write to temp, open default browser
# ============================================================================
def main():
    # Write HTML to temp directory
    tmp_dir = tempfile.gettempdir()
    html_path = os.path.join(tmp_dir, "genesis_kernel.html")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_PAYLOAD)

    print("=" * 60)
    print("  GENESIS KERNEL PACK v1.0")
    print("  Goldberg-Coxeter Polyhedra + Navier-Stokes Flow")
    print("=" * 60)
    print(f"  Written → {html_path}")
    print(f"  Size    → {len(HTML_PAYLOAD):,} bytes")
    print("  Opening default browser...")
    print("=" * 60)

    # Open in default browser
    file_url = "file:///" + html_path.replace("\\", "/")
    webbrowser.open(file_url)

if __name__ == "__main__":
    main()

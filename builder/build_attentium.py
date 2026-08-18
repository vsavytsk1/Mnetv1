#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_attentium.py  --  ATTENTIUM v0.3: the seam speaks, and HELENA arrives
===========================================================================
House pattern (Path VI: one script, one run). The sim is not hand-typed; it
is BUILT. This script:

  1. derives the C60 geometry from the golden-ratio permutations,
  2. finds the Hamiltonian cycle by DFS and AUDITS it (0 non-edges or abort),
  3. finds the 12 pentagons and AUDITS the count,
  4. assembles shell/attentium_v0_3.html from the template below,
  5. refuses to ship if `node --check` rejects the result.

v0.3 closes the v0.2 review findings, measured before fixing:
  * THE SEAM SPEAKS -- v0.2 flattened 15.1% of all attention mass (gap-1
    weights spanning 0.0095..0.96) into one constant gold stroke. Now every
    seam segment draws at its own weight: max over shown heads, declared.
  * HUD denominator counts only DRAWABLE pairs (gap >= 2); seam reported apart.
  * The entropy readout (v0.1) is restored; it silently died in v0.2.
  * validate() sweeps EVERY layer x head, not attn[0][0] alone.
And adds BIPARTITE mode for HELENA joins, produced by the SpiderEngineering
repo (Eleni/tools/helena_to_attentium.py -- HELENA lives there, so her tools
do too; only the JSON format crosses):
genesis levels at TRUE stored coordinates (no fold, no r=+0.115 artifact),
the Mobius heart as a ring at a DECLARED display radius, wires bright by
log-stretched 1-cos (raw weights pin at ~1.0; range printed), coloured by
the target heart node's actual BIT from the 71 tongues.

Run:  py -3 builder/build_attentium.py
"""
import json
import math
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "shell" / "attentium_v0_3.html"
STAMP = time.strftime("%Y-%m-%d %H:%M:%S")

print("Building attentium_v0_3.html -- the seam speaks")

# ---------------------------------------------------------------------------
# 1..3  THE GEOMETRY, derived here, never pasted
# ---------------------------------------------------------------------------
PHI = (1 + 5 ** 0.5) / 2


def _perms(a, b, c):
    out = set()
    for (x, y, z) in ((a, b, c), (b, c, a), (c, a, b)):
        for sx in ({1, -1} if x else {1}):
            for sy in ({1, -1} if y else {1}):
                for sz in ({1, -1} if z else {1}):
                    out.add((round(sx * x, 9), round(sy * y, 9), round(sz * z, 9)))
    return out


V = set()
V |= _perms(0, 1, 3 * PHI)
V |= _perms(1, 2 + PHI, 2 * PHI)
V |= _perms(2, 1 + 2 * PHI, PHI)
V = sorted(V)
R0 = math.dist((0, 0, 0), V[0])
VERTS = [[round(c / R0, 6) for c in v] for v in V]

short = min(math.dist(V[i], V[j]) for i in range(60) for j in range(i + 1, 60))
EDGES = [[i, j] for i in range(60) for j in range(i + 1, 60)
         if abs(math.dist(V[i], V[j]) - short) < 1e-6]
adj = [[] for _ in range(60)]
for i, j in EDGES:
    adj[i].append(j)
    adj[j].append(i)

sys.setrecursionlimit(10000)
path = [0]
used = [False] * 60
used[0] = True


def _dfs():
    if len(path) == 60:
        return 0 in adj[path[-1]]
    for w in adj[path[-1]]:
        if not used[w]:
            used[w] = True
            path.append(w)
            if _dfs():
                return True
            path.pop()
            used[w] = False
    return False


if not _dfs():
    sys.exit("ABORT: no Hamiltonian cycle found (impossible for C60)")

pents, seen = [], set()
for a in range(60):
    for b in adj[a]:
        for c in adj[b]:
            if c == a:
                continue
            for e in adj[c]:
                if e in (a, b):
                    continue
                for f in adj[e]:
                    if f in (a, b, c):
                        continue
                    if a in adj[f]:
                        k = tuple(sorted([a, b, c, e, f]))
                        if k not in seen:
                            seen.add(k)
                            pents.append([a, b, c, e, f])

# ---- BUILD-TIME AUDIT: refuse to ship a bad fold --------------------------
es = {(min(a, b), max(a, b)) for a, b in EDGES}
bad = sum(1 for k in range(60)
          if (min(path[k], path[(k + 1) % 60]), max(path[k], path[(k + 1) % 60])) not in es)
chi = len(VERTS) - len(EDGES) + 32
checks = [
    ("V", len(VERTS), 60), ("E", len(EDGES), 90), ("chi", chi, 2),
    ("pentagons", len(pents), 12), ("hampath unique", len(set(path)), 60),
    ("hampath non-edges", bad, 0),
]
for name, got, want in checks:
    tag = "OK" if got == want else "FAIL"
    print(f"  audit: {name:<18} {got:>4}  (want {want})  {tag}")
    if got != want:
        sys.exit(f"ABORT: {name} = {got}, wanted {want}. Not shipping.")

C60_DATA = (
    "// C60 fold data -- DERIVED by builder/build_attentium.py, never hand-edited.\n"
    "// Audited at build (V=60 E=90 chi=2 P=12, hampath 60 unique, 0 non-edges)\n"
    "// and re-audited at boot, because a claim in a file is not evidence.\n"
    f"var C60_VERTS = {json.dumps(VERTS)};\n"
    f"var C60_EDGES = {json.dumps(EDGES)};\n"
    f"var C60_HAMPATH = {json.dumps(path)};\n"
    f"var C60_PENTS = {json.dumps(pents)};"
)
print(f"  geometry: {len(C60_DATA):,} B derived")

# ---------------------------------------------------------------------------
# 4  THE TEMPLATE  (plain string + .replace tokens; no f-string brace hell)
# ---------------------------------------------------------------------------
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ATTENTIUM v0.3 &middot; the seam speaks, and HELENA arrives</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  :root{ --bg:#050510; --panel:rgba(5,5,16,.92); --edge:#1a1f2e;
    --cyan:#00d4ff; --gold:#ffd700; --pink:#ff69b4; --green:#7fff7f;
    --red:#ff5a5a; --dim:rgba(220,228,240,.55); }
  html,body{height:100%}
  body{background:var(--bg);color:#e0e6f0;font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:11px;overflow:hidden}
  canvas#cv{display:block;position:fixed;inset:0;touch-action:none}
  #hud{position:fixed;top:12px;left:12px;z-index:10;pointer-events:none;max-width:360px}
  #hud .title{font-size:13px;color:var(--cyan);letter-spacing:.09em;margin-bottom:2px}
  #hud .sub{color:rgba(255,105,180,.75);font-size:9px;letter-spacing:.05em;margin-bottom:6px}
  #hud .info{color:var(--dim);line-height:1.65}
  #hud .info b{color:var(--gold)} #hud .info .c{color:var(--cyan)}
  #hud .info .p{color:var(--pink)} #hud .info .g{color:var(--green)}
  #hud .info .d{color:rgba(220,228,240,.32)}
  #src{position:fixed;top:12px;right:12px;z-index:12;max-width:340px;padding:9px 12px;
    border:1px solid #4a1a1a;background:#180a0a;border-radius:5px;color:#ffb0b0;font-size:10px;line-height:1.6}
  #src.real{border-color:#1a3a26;background:#08140d;color:var(--green)}
  #src b{color:var(--red);letter-spacing:.06em} #src.real b{color:var(--green)}
  .caveat{position:fixed;right:12px;bottom:52px;z-index:11;max-width:344px;
    padding:8px 11px;border:1px solid #3a3018;background:#12100a;border-radius:5px;
    color:#c9b98a;font-size:9.5px;line-height:1.6}
  .caveat b{color:var(--gold)} .caveat i{color:#e0d3a8;font-style:normal}
  #log{position:fixed;left:12px;top:238px;z-index:10;background:rgba(5,5,16,.82);
    border:1px solid #241016;border-radius:4px;padding:7px 10px;max-width:330px;
    max-height:20vh;overflow-y:auto;font-size:10px;line-height:1.5;color:rgba(255,176,120,.8)}
  #log:empty{display:none}
  #log .ok{color:var(--green)} #log .w{color:var(--gold)} #log .e{color:var(--red)}
  #bar{position:fixed;left:0;right:0;bottom:0;z-index:12;background:var(--panel);
    border-top:1px solid var(--edge);padding:7px 12px;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
  .btn{background:#0d0d16;color:#6a6a7a;border:1px solid #26263a;border-radius:3px;
    padding:4px 11px;font-family:inherit;font-size:11px;cursor:pointer;transition:all .13s;white-space:nowrap}
  .btn:hover{background:#15151f;border-color:#4a4a66;color:#c9c9dc}
  .btn.on{background:var(--cyan);color:#050510;border-color:var(--cyan)}
  .btn.pent.on{background:var(--pink);color:#050510;border-color:var(--pink)}
  .btn.seam.on{background:var(--gold);color:#050510;border-color:var(--gold)}
  .lbl{color:rgba(220,228,240,.4);text-transform:uppercase;letter-spacing:.1em;font-size:9px;margin:0 1px}
  .sep{width:1px;height:20px;background:var(--edge);margin:0 3px}
  input[type=range]{width:84px;height:3px;-webkit-appearance:none;appearance:none;background:#243;border-radius:2px;outline:none;vertical-align:middle}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:11px;height:11px;border-radius:50%;background:var(--cyan);cursor:pointer;border:1px solid #050510}
  input[type=range]::-moz-range-thumb{width:11px;height:11px;border:0;border-radius:50%;background:var(--cyan);cursor:pointer}
  .val{color:var(--gold);min-width:34px;display:inline-block;text-align:right}
  #drop{position:fixed;inset:0;z-index:20;display:none;align-items:center;justify-content:center;
    background:rgba(5,5,16,.9);color:var(--cyan);font-size:15px;letter-spacing:.1em;border:2px dashed var(--cyan)}
  #drop.show{display:flex}
</style>
</head>
<body>
<canvas id="cv"></canvas>

<div id="hud">
  <div class="title">ATTENTIUM v0.3 &middot; the seam speaks</div>
  <div class="sub">causal: attention on the C60 &middot; bipartite: HELENA's join, true coordinates</div>
  <div class="info" id="info"></div>
</div>

<div id="src"><b>SYNTHETIC DATA &mdash; NOT A MODEL</b><br>
Nothing here has been through a transformer. <b>Any pattern is one I put there.</b>
Drop a dump from builder/dump_attention.py, or a HELENA join from the
SpiderEngineering repo (Eleni/tools/helena_to_attentium.py).</div>

<div class="caveat" id="cav_causal">
<b>THE FOLD (causal mode)</b><br>
<i>EXACT:</i> Hamiltonian on the C60 &mdash; audited at build AND at boot, 0 non-edges.<br>
<i>FIXED in v0.3:</i> the seam draws each consecutive pair at its own measured
weight (max over shown heads, and it says so) &mdash; v0.2 flattened 15.1% of
all attention mass into one constant gold stroke.<br>
<i>STILL TRUE:</i> chord length vs sequence gap correlates at only r = +0.115.
Connections, never distances.
</div>
<div class="caveat" id="cav_bip" style="display:none">
<b>HELENA (bipartite mode)</b><br>
<i>REAL GEOMETRY:</i> genesis nodes carry intrinsic xyz &mdash; no fold, no
imposed ordering; the r=+0.115 artifact does not apply here.<br>
<i>DECLARED DISPLAY CHOICES:</i> the heart is drawn at radius 1.30 (true
radius ~1.0 after normalization; wires would be near-invisible otherwise),
and wire brightness = <b>log-stretched 1&minus;cos&theta;</b>, because raw
weights pin at ~1.0. Bright = closer alignment. The range is in the HUD.<br>
<i>CLAIMED vs VERIFIED:</i> node/edge counts verified at load; chi and P=12
per level are CLAIMED by the build card (faces are not shipped).
</div>

<div id="log"></div>

<div id="bar">
  <span class="lbl">draw</span>
  <button class="btn pent on" id="b_pent">12 Ribs</button>
  <button class="btn on" id="b_shell">Shell</button>
  <button class="btn seam on" id="b_seam">Fold seam</button>
  <button class="btn on" id="b_chord">Chords</button>
  <button class="btn" id="b_spin">Spin</button>
  <span class="sep"></span>
  <span class="lbl" id="l_layer">layer</span><input type="range" id="s_layer" min="-1" max="7" step="1" value="-1"><span class="val" id="v_layer">all</span>
  <span class="lbl">cut</span><input type="range" id="s_cut" min="0" max="0.5" step="0.005" value="0.06"><span class="val" id="v_cut">0.06</span>
  <span class="sep"></span>
  <button class="btn" id="b_reseed">Reseed</button>
</div>
<div id="drop">drop the dump</div>

<script>
"use strict";
/* ATTENTIUM v0.3 -- two modes, one discipline. Built by
   builder/build_attentium.py on __STAMP__ -- do not hand-edit; rebuild. */

__C60_DATA__

var CV=document.getElementById('cv'), CX=CV.getContext('2d');
var W=0,H=0,DPR=1,cx=0,cy=0,S=1;
function resize(){
  DPR=Math.max(1,Math.min(2,window.devicePixelRatio||1));
  W=window.innerWidth||900; H=window.innerHeight||600;
  CV.width=Math.floor(W*DPR); CV.height=Math.floor(H*DPR);
  CV.style.width=W+"px"; CV.style.height=H+"px";
  CX.setTransform(DPR,0,0,DPR,0,0); cx=W/2; cy=H/2; S=0.40*Math.min(W,H);
}
window.addEventListener('resize',function(){resize();draw();});

var LOG=document.getElementById('log');
function log(m,c){var d=document.createElement('div');if(c)d.className=c;d.innerHTML=m;
  LOG.insertBefore(d,LOG.firstChild); while(LOG.childNodes.length>10)LOG.removeChild(LOG.lastChild);}

/* ---- C60 fold audit: a claim in a file is not evidence ------------------- */
var ESET={};
for(var _e=0;_e<C60_EDGES.length;_e++){
  var _a=C60_EDGES[_e][0], _b=C60_EDGES[_e][1];
  ESET[Math.min(_a,_b)+"_"+Math.max(_a,_b)]=1;
}
function auditFold(){
  var seen={},k,dup=0,bad=0,n=C60_HAMPATH.length;
  for(k=0;k<n;k++){
    if(seen[C60_HAMPATH[k]]) dup++; seen[C60_HAMPATH[k]]=1;
    var u=C60_HAMPATH[k], v=C60_HAMPATH[(k+1)%n];
    if(!ESET[Math.min(u,v)+"_"+Math.max(u,v)]) bad++;
  }
  return {n:n,dup:dup,bad:bad,chi:C60_VERTS.length-C60_EDGES.length+32,pents:C60_PENTS.length};
}
var AUDIT=auditFold();

/* ---- synthetic causal data ----------------------------------------------- */
var M=null, RNG=1;
function rnd(){RNG=(RNG*1664525+1013904223)>>>0;return RNG/4294967296;}
function synth(nTok,nLay,nHead,seed){
  RNG=seed>>>0||1;
  var words=["A","fluffy","blue","creature","roamed","the","verdant","forest","and",
    "the","sky","turned","slowly","to","amber","light","while","something","older",
    "than","language","watched","from","the","hexagons","without","moving","or",
    "needing","to","because","the","shape","was","already","closed","and","twelve",
    "was","never","a","choice","only","a","receipt","the","surface","hands","you",
    "when","it","agrees","to","stop","being","flat","for","your","sake","now"];
  var toks=[],i,j,L,Hh;
  for(i=0;i<nTok;i++) toks.push(words[i%words.length]);
  var attn=[];
  for(L=0;L<nLay;L++){ var heads=[];
    for(Hh=0;Hh<nHead;Hh++){ var kind=(L+Hh)%3, rows=[];
      for(i=0;i<nTok;i++){ var row=new Float32Array(nTok), sum=0;
        for(j=0;j<=i;j++){ var w;
          if(kind===0)      w=Math.exp(-(i-j)*(i-j)/4.0);
          else if(kind===1) w=(j===0?6.0:0.25)+rnd()*0.15;
          else              w=0.15+0.85*Math.exp(-Math.abs((i-j)-(2+Hh%6))/1.5);
          w*=(0.85+0.3*rnd()); row[j]=w; sum+=w; }
        for(j=0;j<=i;j++) row[j]/=(sum||1);
        rows.push(row); }
      heads.push(rows); }
    attn.push(heads); }
  return {mode:"causal",model:"(synthetic generator)",tokens:toks,n_layers:nLay,
          n_heads:nHead,attn:attn,synthetic:true};
}

/* ---- v0.1's entropy, restored (it silently died in v0.2) ----------------- */
function meanEntropy(m){
  var tot=0,n=0,L,Hh,i,j;
  for(L=0;L<m.n_layers;L++) for(Hh=0;Hh<m.n_heads;Hh++){
    var rows=m.attn[L][Hh];
    for(i=0;i<rows.length;i++){
      var h=0,row=rows[i];
      for(j=0;j<=i;j++){ var p=row[j]; if(p>1e-12) h-=p*Math.log2(p); }
      tot+=h; n++;
    }
  }
  return n? tot/n : 0;
}
function maxEntropy(m){
  var tot=0,n=0,i,L,Hh;
  for(L=0;L<m.n_layers;L++) for(Hh=0;Hh<m.n_heads;Hh++)
    for(i=0;i<m.attn[L][Hh].length;i++){ tot+=Math.log2(i+1); n++; }
  return n? tot/n : 0;
}

/* ---- geometry ------------------------------------------------------------ */
var yaw=0.6,pitch=-0.25,zoom=1.0,panX=0,panY=0,spin=false,CAMD=5;
function rot(p){var cp=Math.cos(pitch),sp=Math.sin(pitch),cw=Math.cos(yaw),sw=Math.sin(yaw);
  var y1=p[1]*cp-p[2]*sp, z1=p[1]*sp+p[2]*cp;
  return [p[0]*cw+z1*sw, y1, -p[0]*sw+z1*cw];}
function proj(p){var r=rot(p),f=CAMD/(CAMD-r[2]);
  return {x:cx+panX+r[0]*S*zoom*f, y:cy+panY-r[1]*S*zoom*f, z:r[2]};}
function tokVert(t){ return C60_HAMPATH[t % C60_HAMPATH.length]; }
var HEART_R=1.30;  /* DECLARED display radius for the heart ring */

var showPent=true,showShell=true,showSeam=true,showChord=true,fLayer=-1,cut=0.06;

/* ============================ CAUSAL DRAW ================================ */
function shellR_causal(L){ return 0.42+0.58*(L/Math.max(1,M.n_layers-1)); }
function vposC(vi,L){var r=shellR_causal(L),v=C60_VERTS[vi];return [v[0]*r,v[1]*r,v[2]*r];}

function drawCausal(){
  var nT=Math.min(M.tokens.length,60), nL=M.n_layers, i,j,L,Hh,k;
  var LO=(fLayer<0?0:fLayer), HI=(fLayer<0?nL:fLayer+1);

  if(showShell){
    for(L=LO;L<HI;L++){
      var t=L/Math.max(1,nL-1);
      CX.strokeStyle="rgba(0,212,255,"+(0.05+0.11*t).toFixed(3)+")"; CX.lineWidth=1;
      for(k=0;k<C60_EDGES.length;k++){
        var p=proj(vposC(C60_EDGES[k][0],L)), q=proj(vposC(C60_EDGES[k][1],L));
        CX.beginPath(); CX.moveTo(p.x,p.y); CX.lineTo(q.x,q.y); CX.stroke();
      }
    }
  }
  if(showPent){
    var Lp=HI-1;
    for(k=0;k<C60_PENTS.length;k++){
      var f=C60_PENTS[k];
      CX.beginPath();
      for(i=0;i<f.length;i++){ var pp=proj(vposC(f[i],Lp));
        if(i===0) CX.moveTo(pp.x,pp.y); else CX.lineTo(pp.x,pp.y); }
      CX.closePath();
      CX.fillStyle="rgba(255,105,180,.08)"; CX.fill();
      CX.strokeStyle="rgba(255,105,180,.55)"; CX.lineWidth=1.6; CX.stroke();
    }
  }
  var drawn=0;
  if(showChord){
    for(L=LO;L<HI;L++){
      for(Hh=0;Hh<M.n_heads;Hh++){
        var rows=M.attn[L][Hh], hue=(Hh/Math.max(1,M.n_heads))*300;
        for(i=0;i<rows.length&&i<nT;i++){
          var row=rows[i];
          for(j=0;j+1<i&&j<nT;j++){   /* gap >= 2; gap 1 belongs to the seam */
            var w=row[j]; if(w<cut) continue;
            var a=proj(vposC(tokVert(j),L)), b=proj(vposC(tokVert(i),L));
            CX.strokeStyle="hsla("+hue.toFixed(0)+",92%,64%,"+Math.min(0.85,w*2.0).toFixed(3)+")";
            CX.lineWidth=Math.max(0.4,w*3.2);
            CX.beginPath(); CX.moveTo(a.x,a.y); CX.lineTo(b.x,b.y); CX.stroke();
            drawn++;
          }
        }
      }
    }
  }
  /* THE SEAM, v0.3: each segment at its own measured weight.
     weight = MAX over shown layers and all heads of attn[L][H][k][k-1].
     Max, not mean -- and the HUD says which. */
  if(showSeam){
    var Ls=HI-1, seamW=new Float32Array(nT);
    for(k=1;k<nT;k++){
      var wmax=0;
      for(L=LO;L<HI;L++) for(Hh=0;Hh<M.n_heads;Hh++){
        var r2=M.attn[L][Hh];
        if(k<r2.length && r2[k][k-1]>wmax) wmax=r2[k][k-1];
      }
      seamW[k]=wmax;
    }
    CX.setLineDash([]);
    for(k=1;k<nT;k++){
      var pa=proj(vposC(tokVert(k-1),Ls)), pb=proj(vposC(tokVert(k),Ls));
      var wv=seamW[k];
      CX.strokeStyle="rgba(255,215,0,"+(0.20+0.70*Math.min(1,wv*1.5)).toFixed(3)+")";
      CX.lineWidth=0.8+3.6*wv;
      CX.beginPath(); CX.moveTo(pa.x,pa.y); CX.lineTo(pb.x,pb.y); CX.stroke();
    }
    if(nT===60){
      var pw=proj(vposC(tokVert(59),Ls)), pz=proj(vposC(tokVert(0),Ls));
      CX.setLineDash([4,4]); CX.strokeStyle="rgba(255,90,90,.75)"; CX.lineWidth=1.6;
      CX.beginPath(); CX.moveTo(pw.x,pw.y); CX.lineTo(pz.x,pz.y); CX.stroke();
      CX.setLineDash([]);
    }
    var p0=proj(vposC(tokVert(0),Ls));
    CX.fillStyle="#ffd700"; CX.beginPath(); CX.arc(p0.x,p0.y,4,0,6.2832); CX.fill();
  }
  var Lv=HI-1;
  for(k=0;k<nT;k++){
    var pv=proj(vposC(tokVert(k),Lv)), tz=Math.max(0,Math.min(1,(pv.z+1)/2));
    CX.fillStyle="rgba(127,255,127,"+(0.30+tz*0.60).toFixed(3)+")";
    CX.beginPath(); CX.arc(pv.x,pv.y,2.1,0,6.2832); CX.fill();
  }

  /* HUD: only DRAWABLE pairs in the denominator; the seam reported apart. */
  var fullDrawable=0, seamPairs=0;
  for(L=0;L<nL;L++) for(Hh=0;Hh<M.n_heads;Hh++)
    for(i=0;i<M.attn[L][Hh].length&&i<nT;i++){
      fullDrawable+=Math.max(0,i-1);
      if(i>0) seamPairs++;
    }
  document.getElementById('info').innerHTML=
    "mode      <b>causal</b> &middot; "+M.model+"<br>"+
    "substrate <b>C60</b>  V <span class='c'>60</span> E <span class='c'>90</span>"+
      " F <span class='c'>32</span> chi <span class='g'>"+AUDIT.chi+"</span>"+
      "  fold <span class='g'>"+AUDIT.bad+" bad</span><br>"+
    "tokens    <span class='c'>"+nT+"</span>/60"+
      (M.tokens.length>60?" <span class='p'>("+(M.tokens.length-60)+" truncated)</span>":"")+
      "  layers <span class='c'>"+nL+"</span>  heads <span class='c'>"+M.n_heads+"</span><br>"+
    "chords    <span class='g'>"+drawn.toLocaleString()+"</span> of "+
      "<span class='p'>"+fullDrawable.toLocaleString()+"</span> drawable at cut "+cut.toFixed(3)+"<br>"+
    "seam      <span class='c'>"+seamPairs.toLocaleString()+"</span> pairs, "+
      "width = <b>max</b> attention over shown heads<br>"+
    "entropy   <b>"+M._H.toFixed(3)+"</b> / "+M._Hmax.toFixed(3)+" bits "+
      "<span class='d'>("+(100*M._H/(M._Hmax||1)).toFixed(1)+"% of uniform)</span>";
}

/* =========================== BIPARTITE DRAW ============================== */
function shellR_bip(idx){ var n=M.genesis.length; return n<2?0.9:0.42+0.58*(idx/(n-1)); }

function drawBip(){
  var i,k,li;
  var nLev=M.genesis.length;
  var LO=(fLayer<0?0:fLayer), HI=(fLayer<0?nLev:fLayer+1);

  if(showShell){
    for(li=LO;li<HI;li++){
      var g=M.genesis[li], r=shellR_bip(li);
      CX.strokeStyle="rgba(0,212,255,"+(0.05+0.10*(li/Math.max(1,nLev-1))).toFixed(3)+")";
      CX.lineWidth=0.8;
      for(k=0;k<g.edges.length;k++){
        var e=g.edges[k];
        var p=proj([g.xyz[e[0]][0]*r,g.xyz[e[0]][1]*r,g.xyz[e[0]][2]*r]);
        var q=proj([g.xyz[e[1]][0]*r,g.xyz[e[1]][1]*r,g.xyz[e[1]][2]*r]);
        CX.beginPath(); CX.moveTo(p.x,p.y); CX.lineTo(q.x,q.y); CX.stroke();
      }
    }
  }
  if(showSeam){
    CX.strokeStyle="rgba(255,105,180,.35)"; CX.lineWidth=1;
    CX.beginPath();
    for(k=0;k<M.heart.ring.length;k++){
      var hp=M.heart.ring[k];
      var pp=proj([hp[0]*HEART_R,hp[1]*HEART_R,hp[2]*HEART_R]);
      if(k===0) CX.moveTo(pp.x,pp.y); else CX.lineTo(pp.x,pp.y);
    }
    CX.closePath(); CX.stroke();
  }
  var drawn=0;
  if(showChord){
    for(k=0;k<M.wires.length;k++){
      var wr=M.wires[k]; if(wr[0]<LO||wr[0]>=HI) continue;
      var wn=M._wn[k]; if(wn<cut) continue;
      var g2=M.genesis[wr[0]], r2=shellR_bip(wr[0]);
      var gp=g2.xyz[wr[1]], tp=M.heart.targets[wr[2]];
      var a=proj([gp[0]*r2,gp[1]*r2,gp[2]*r2]);
      var b=proj([tp.xyz[0]*HEART_R,tp.xyz[1]*HEART_R,tp.xyz[2]*HEART_R]);
      CX.strokeStyle=(tp.bit?"rgba(127,255,127,":"rgba(255,105,180,")+
        (0.10+0.75*wn).toFixed(3)+")";
      CX.lineWidth=0.4+2.2*wn;
      CX.beginPath(); CX.moveTo(a.x,a.y); CX.lineTo(b.x,b.y); CX.stroke();
      drawn++;
    }
  }
  if(showPent){
    for(k=0;k<M.heart.targets.length;k++){
      var t3=M.heart.targets[k];
      var p3=proj([t3.xyz[0]*HEART_R,t3.xyz[1]*HEART_R,t3.xyz[2]*HEART_R]);
      CX.fillStyle=t3.bit?"rgba(127,255,127,.8)":"rgba(255,105,180,.8)";
      CX.beginPath(); CX.arc(p3.x,p3.y,1.7,0,6.2832); CX.fill();
    }
  }
  var lvlLine="";
  for(li=0;li<nLev;li++){
    var gl=M.genesis[li];
    lvlLine+="L"+gl.level+":<span class='c'>"+gl.nodes+"</span> ";
  }
  document.getElementById('info').innerHTML=
    "mode      <b>bipartite</b> &middot; "+M.model+"<br>"+
    "genesis   "+lvlLine+"<span class='d'>counts verified; chi=2 P=12 claimed/level</span><br>"+
    "heart     <span class='p'>"+M.heart.nodes.toLocaleString()+"</span> nodes, chi "+
      "<span class='p'>"+M.heart.chi+"</span> "+
      "<span class='d'>("+(M.card&&M.card.heart_orientation||"?")+")</span>, ring r="+HEART_R+" <span class='d'>display</span><br>"+
    "wires     <span class='g'>"+drawn.toLocaleString()+"</span> of "+M.wires.length.toLocaleString()+
      " at cut "+cut.toFixed(3)+"  k=<span class='c'>"+(M.card&&M.card.k_nearest||"?")+"</span><br>"+
    "align     mean angular err <b>"+M._angDeg.toFixed(3)+"&deg;</b>  "+
      "1&minus;cos in <span class='d'>["+M._omLo.toExponential(1)+", "+M._omHi.toExponential(1)+"]</span><br>"+
    "stretch   brightness = log10(1&minus;cos), <b>declared</b> &middot; "+
      "<span class='g'>green</span>=bit 1, <span class='p'>pink</span>=bit 0";
}

function draw(){
  CX.fillStyle="#050510"; CX.fillRect(0,0,W,H);
  if(!M) return;
  if(M.mode==="bipartite") drawBip(); else drawCausal();
}

/* ---- load ---------------------------------------------------------------- */
function relabel(bip){
  document.getElementById('b_pent').textContent = bip?"Targets":"12 Ribs";
  document.getElementById('b_seam').textContent = bip?"Heart ring":"Fold seam";
  document.getElementById('b_chord').textContent= bip?"Wires":"Chords";
  document.getElementById('l_layer').textContent= bip?"level":"layer";
  document.getElementById('cav_causal').style.display = bip?"none":"block";
  document.getElementById('cav_bip').style.display    = bip?"block":"none";
}

function adopt(m,how){
  M=m;
  var bip = M.mode==="bipartite";
  if(!bip){ M._H=meanEntropy(M); M._Hmax=maxEntropy(M); }
  else{
    var lo=Infinity,hi=-Infinity,k,om;
    for(k=0;k<M.wires.length;k++){
      om=Math.max(1e-9,1-M.wires[k][3]);
      if(om<lo)lo=om; if(om>hi)hi=om;
    }
    M._omLo=lo; M._omHi=hi;
    var llo=Math.log10(lo), lhi=Math.log10(hi), span=(lhi-llo)||1;
    M._wn=new Float32Array(M.wires.length);
    var asum=0;
    for(k=0;k<M.wires.length;k++){
      om=Math.max(1e-9,1-M.wires[k][3]);
      M._wn[k]=1-(Math.log10(om)-llo)/span;   /* 1 = tightest alignment */
      asum+=Math.acos(Math.max(-1,Math.min(1,M.wires[k][3])));
    }
    M._angDeg=asum/M.wires.length*180/Math.PI;
  }
  relabel(bip);
  var s=document.getElementById('src');
  if(M.synthetic){ s.className="";
    s.innerHTML="<b>SYNTHETIC DATA &mdash; NOT A MODEL</b><br>Nothing here has been "+
      "through a transformer. <b>Any pattern is one I put there.</b> Drop a dump "+
      "from builder/dump_attention.py, or a HELENA join from the SpiderEngineering "+
      "repo (Eleni/tools/helena_to_attentium.py)."; }
  else { s.className="real";
    s.innerHTML="<b>REAL "+(bip?"JOIN":"ATTENTION")+"</b><br>model: "+M.model+
      (bip&&M.card?"<br>soul: "+String(M.card.soul_id).slice(0,16)+"&hellip;":"")+
      "<br>These weights came out of a real run."; }
  var sl=document.getElementById('s_layer');
  sl.max=(bip?M.genesis.length:M.n_layers)-1; sl.value=-1; fLayer=-1;
  document.getElementById('v_layer').textContent="all";
  if(!bip && M.tokens.length>60)
    log("<span class='w'>"+M.tokens.length+" tokens, 60 slots &mdash; TRUNCATED.</span>","w");
  log(how, M.synthetic?"w":"ok");
  draw();
}

/* v0.3: validate() sweeps EVERYTHING it can reach. */
function validate(o){
  if(!o||typeof o!=="object") throw new Error("not an object");
  if(o.mode==="bipartite"){
    ["genesis","heart","wires"].forEach(function(kk){
      if(!(kk in o)) throw new Error("missing key: "+kk); });
    var li,k;
    for(li=0;li<o.genesis.length;li++){
      var g=o.genesis[li];
      if(g.xyz.length!==g.nodes) throw new Error("L"+g.level+": xyz "+g.xyz.length+" != nodes "+g.nodes);
      if(g.edges.length!==g.edges_n) throw new Error("L"+g.level+": edges "+g.edges.length+" != declared "+g.edges_n);
      for(k=0;k<g.edges.length;k++){
        if(g.edges[k][0]>=g.nodes||g.edges[k][1]>=g.nodes)
          throw new Error("L"+g.level+": edge index out of range");
      }
    }
    var badW=0;
    for(k=0;k<o.wires.length;k++){
      var w=o.wires[k];
      var gl=o.genesis[w[0]];
      if(!gl||w[1]>=gl.nodes||w[2]>=o.heart.targets.length||w[3]<-1.0001||w[3]>1.0001) badW++;
    }
    if(badW) throw new Error(badW+" malformed wires");
    log("validated: "+o.genesis.length+" levels swept, "+o.wires.length.toLocaleString()+
        " wires bounds-checked, cos in [-1,1]. chi is CLAIMED by the card.","ok");
    o.synthetic=false; if(!o.model) o.model="(unnamed join)";
    return o;
  }
  ["tokens","n_layers","n_heads","attn"].forEach(function(kk){
    if(!(kk in o)) throw new Error("missing key: "+kk); });
  if(o.attn.length!==o.n_layers) throw new Error("attn layers "+o.attn.length+" != n_layers "+o.n_layers);
  var L,Hh,i,j,bad=0,shapeBad=0,n=o.tokens.length;
  for(L=0;L<o.n_layers;L++){
    if(o.attn[L].length!==o.n_heads) throw new Error("layer "+L+" has "+o.attn[L].length+" heads, declared "+o.n_heads);
    for(Hh=0;Hh<o.n_heads;Hh++){
      var rows=o.attn[L][Hh];
      if(rows.length!==n) shapeBad++;
      for(i=0;i<rows.length;i++) for(j=i+1;j<rows.length;j++)
        if(rows[i][j]>1e-6) bad++;
    }
  }
  if(shapeBad) throw new Error(shapeBad+" heads have wrong row counts");
  if(bad) log("<span class='w'>"+bad+" upper-triangle weights &gt; 1e-6 across ALL heads "+
              "&mdash; NOT causally masked. Drawing anyway.</span>","w");
  else log("validated: "+(o.n_layers*o.n_heads)+" heads swept, causal mask holds everywhere.","ok");
  o.mode="causal"; o.synthetic=false; if(!o.model) o.model="(unnamed dump)";
  return o;
}

var DROP=document.getElementById('drop');
window.addEventListener('dragover',function(e){e.preventDefault();DROP.classList.add('show');});
window.addEventListener('dragleave',function(e){if(e.target===DROP)DROP.classList.remove('show');});
window.addEventListener('drop',function(e){
  e.preventDefault(); DROP.classList.remove('show');
  var f=e.dataTransfer.files&&e.dataTransfer.files[0]; if(!f) return;
  var r=new FileReader();
  r.onload=function(){
    try{ adopt(validate(JSON.parse(r.result)),"loaded "+f.name); }
    catch(err){ log("<span class='e'>REFUSED "+f.name+": "+err.message+"</span>","e"); } };
  r.readAsText(f);
});

function tog(id,get,set){ var b=document.getElementById(id);
  b.addEventListener('click',function(){ set(!get()); b.classList.toggle('on',get()); draw(); }); }
tog('b_pent', function(){return showPent;},  function(v){showPent=v;});
tog('b_shell',function(){return showShell;}, function(v){showShell=v;});
tog('b_seam', function(){return showSeam;},  function(v){showSeam=v;});
tog('b_chord',function(){return showChord;}, function(v){showChord=v;});
document.getElementById('b_spin').addEventListener('click',function(){
  spin=!spin; this.classList.toggle('on',spin); if(spin) tick(); });
document.getElementById('s_layer').addEventListener('input',function(){
  fLayer=+this.value;
  document.getElementById('v_layer').textContent=fLayer<0?"all":"L"+fLayer;
  draw(); });
document.getElementById('s_cut').addEventListener('input',function(){
  cut=+this.value; document.getElementById('v_cut').textContent=cut.toFixed(3); draw(); });
document.getElementById('b_reseed').addEventListener('click',function(){
  adopt(synth(60,8,4,(Math.random()*1e9)|0),"reseeded SYNTHETIC (causal)"); });

var drag=false,lx=0,ly=0;
CV.addEventListener('pointerdown',function(e){drag=true;lx=e.clientX;ly=e.clientY;CV.setPointerCapture(e.pointerId);});
CV.addEventListener('pointerup',function(){drag=false;});
CV.addEventListener('pointermove',function(e){ if(!drag) return;
  if(e.shiftKey){ panX+=e.clientX-lx; panY+=e.clientY-ly; }
  else { yaw+=(e.clientX-lx)*0.006; pitch+=(e.clientY-ly)*0.006;
         pitch=Math.max(-1.5,Math.min(1.5,pitch)); }
  lx=e.clientX; ly=e.clientY; draw(); });
CV.addEventListener('wheel',function(e){ e.preventDefault();
  zoom*=(e.deltaY<0?1.1:0.9); zoom=Math.max(0.2,Math.min(10,zoom)); draw(); },{passive:false});
window.addEventListener('keydown',function(e){ var k=e.key.toLowerCase();
  if(k==='p') document.getElementById('b_pent').click();
  if(k==='c') document.getElementById('b_chord').click();
  if(k==='s') document.getElementById('b_spin').click();
  if(k==='0'){ yaw=0.6;pitch=-0.25;zoom=1;panX=0;panY=0; draw(); } });
function tick(){ if(!spin) return; yaw+=0.004; draw(); requestAnimationFrame(tick); }

resize();
adopt(synth(60,8,4,20260818),"booted SYNTHETIC (causal). drop a HELENA join for bipartite mode.");
log("fold audited: "+AUDIT.n+" vertices, "+AUDIT.dup+" repeats, "+AUDIT.bad+
    " non-edges, chi="+AUDIT.chi+", P="+AUDIT.pents,"ok");
console.log("%c ATTENTIUM v0.3 -- the seam speaks, and HELENA arrives ",
  "background:#00d4ff;color:#050510;font-size:13px;font-weight:bold");
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# 5  ASSEMBLE, CHECK, SHIP (or refuse)
# ---------------------------------------------------------------------------
html = HTML.replace("__C60_DATA__", C60_DATA).replace("__STAMP__", STAMP)
OUT.write_text(html, encoding="utf-8", newline="\n")
print(f"  wrote {OUT.name}: {len(html):,} B")

node = shutil.which("node")
if node:
    import re
    js = "\n".join(m for m in re.findall(r"<script[^>]*>(.*?)</script>", html, re.S))
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                     encoding="utf-8") as f:
        f.write(js)
        tmp = f.name
    r = subprocess.run([node, "--check", tmp], capture_output=True, text=True)
    Path(tmp).unlink()
    if r.returncode != 0:
        OUT.unlink()
        sys.exit("ABORT: node --check FAILED -- output deleted, not shipping:\n"
                 + r.stderr[:800])
    print(f"  node --check: PASS on {len(js):,} B of JS")
else:
    print("  [WARN] node not found -- syntax NOT verified")

print("  done. drag a SpiderEngineering Eleni/exports/helena_*.json for bipartite.")

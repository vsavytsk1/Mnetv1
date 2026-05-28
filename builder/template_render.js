})(typeof globalThis !== 'undefined' ? globalThis : this);

</script>
<script>
// ═══ CONSOLE MATH LOGGER ═══
// Chrome DevTools structured output — code that looks like math
var M = {
  _c: 0,
  P1: function(d){ console.log('%cP1:NODE %c'+JSON.stringify(d),'color:#00ffd5;font-weight:bold','color:#888');M._c++ },
  P2: function(d){ console.log('%cP2:EDGE %c'+JSON.stringify(d),'color:#80d0ff;font-weight:bold','color:#888');M._c++ },
  P3: function(d){ console.log('%cP3:COMPOSE %c'+JSON.stringify(d),'color:#aaa;font-weight:bold','color:#888');M._c++ },
  P4: function(d){ console.log('%cP4:TRANSFORM %c'+JSON.stringify(d),'color:#ffd700;font-weight:bold','color:#888');M._c++ },
  P5: function(d){ console.log('%cP5:ITERATE %c'+JSON.stringify(d),'color:#ff9900;font-weight:bold','color:#888');M._c++ },
  P6: function(d){ console.log('%cP6:AGGREGATE %c'+JSON.stringify(d),'color:#ff69b4;font-weight:bold','color:#888');M._c++ },
  P7: function(d){ console.log('%cP7:COMPARE %c'+JSON.stringify(d),'color:#a78bfa;font-weight:bold','color:#888');M._c++ },
  invariant: function(inv){
    console.log('%c═══ INVARIANT CHECK ═══','color:#7fff7f;font-weight:bold');
    console.table({V:inv.V,E:inv.E,F:inv.F,chi:inv.chi,pents:inv.pents,hexes:inv.hexes,
      'E/V':inv.evRatio,'P=12':inv.pents===12?'✓':'✗','χ=2':inv.chi===2?'✓':'✗'});
    if(inv.pents===12&&inv.chi===2) console.log('%c✓ TOPOLOGY VALID','color:#7fff7f;font-size:14px');
    else console.error('✗ TOPOLOGY BROKEN: P='+inv.pents+' χ='+inv.chi);
    performance.mark('invariant-check');
  },
  group: function(name){ console.group('%c'+name,'color:#ffd700;font-weight:bold');performance.mark(name+'-start') },
  groupEnd: function(name){ console.groupEnd();performance.mark(name+'-end');
    try{performance.measure(name,name+'-start',name+'-end')}catch(e){} },
  seed: function(){ console.log('%c🔮 SEED: Dodecahedron (12 pentagons, Euler forced)','color:#ff69b4;font-size:14px') },
  refine: function(what){ console.log('%c⚡ REFINE: '+what,'color:#00ffd5;font-size:12px') },
  crystal: function(){
    console.log('%c💎 THE 3 CRYSTAL CONDITIONS','color:#ffd700;font-size:12px');
    console.log('%cC1: CHOICE — cannot be everything at once','color:#ffd700');
    console.log('%cC2: IRREVERSIBLE — P6 destroys information','color:#ff69b4');
    console.log('%cC3: CONSISTENT — P7 is deterministic','color:#a78bfa');
  }
};

// ═══ FLIGHT RECORDER ═══
var FL={entries:[],t0:performance.now(),session:'v7.5.1_'+new Date().toISOString().replace(/[:.]/g,'-').slice(0,19)};
function flRec(op,d){FL.entries.push({t:Math.round((performance.now()-FL.t0)*100)/100,op:op,d:d})}
function flExport(){
  var blob=new Blob([JSON.stringify({session:FL.session,entries:FL.entries.length,data:FL.entries})],{type:'application/json'});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=FL.session+'_log.json';a.click();
}


// ═══ RENDER CUTOFF — the fractal maker trick ═══
// When faces > maxFaces, skip rendering but keep state valid.
// Zoom out = sub-pixel = nothing to draw = GPU rests = computation flies.
// ═══ STATE ═══
var gkState = null;
var params = { innerScale: 0.45, midScale: 0.70, jitter: 0, surfaceMode: 'spherical', sphereR: 1.6 };
var cam = { rx: 0.3, ry: 0, zoom: 200, atom: 1.0, spin: 0.005, maxFaces: 50000 };
var dragging = false, lastMouse = {x:0,y:0};

function SV(id,v){document.getElementById(id).textContent=typeof v==='number'?v.toFixed(2):v}

// ═══ 3D → 2D PROJECTION ═══
var cv=document.getElementById('cv'),cx=cv.getContext('2d'),W,H;
function resize(){W=cv.width=innerWidth;H=cv.height=innerHeight}
resize();addEventListener('resize',resize);

function project(p){
  // Rotate Y then X
  var x=p[0],y=p[1],z=p[2];
  var cy=Math.cos(cam.ry),sy=Math.sin(cam.ry);
  var x1=x*cy-z*sy, z1=x*sy+z*cy;
  var crx=Math.cos(cam.rx),srx=Math.sin(cam.rx);
  var y1=y*crx-z1*srx, z2=y*srx+z1*crx;
  return {x:W/2+x1*cam.zoom, y:H/2-y1*cam.zoom, z:z2};
}

function centroid3(pts){
  var x=0,y=0,z=0;
  for(var i=0;i<pts.length;i++){x+=pts[i][0];y+=pts[i][1];z+=pts[i][2]}
  return [x/pts.length,y/pts.length,z/pts.length];
}

// ═══ DRAW ═══
function draw(){
  cx.fillStyle='#050508';cx.fillRect(0,0,W,H);
  if(!gkState)return;
  
  var totalF = gkState.faces.length;
  var mbEst = Math.round(totalF * 0.0005 * 100) / 100;
  document.getElementById('h-mb').textContent = mbEst.toFixed(1);
  
  // Sort faces by depth (painter's algorithm) + sub-pixel cull
  var sorted=[];
  var culled=0;
  for(var i=0;i<gkState.faces.length;i++){
    var f=gkState.faces[i];
    var c=centroid3(f.pts);
    var p=project(c);
    
    // PROJECT first vertex to estimate screen size
    var p0=project(f.pts[0]);
    var p1=project(f.pts[1]);
    var screenSize=Math.sqrt((p0.x-p1.x)*(p0.x-p1.x)+(p0.y-p1.y)*(p0.y-p1.y));
    
    // SUB-PIXEL CULL: if face edge < 0.5px on screen, skip
    if(screenSize<0.5){culled++;continue}
    
    // VIEWPORT CULL: if centroid way off screen, skip
    if(p.x<-200||p.x>W+200||p.y<-200||p.y>H+200){culled++;continue}
    
    // BACKFACE CULL: check screen-space winding order
    // Project 3 vertices, compute cross product -> if CW, face points away
    var pa=project(f.pts[0]),pb=project(f.pts[1]),pc=project(f.pts[2]);
    var cross=(pb.x-pa.x)*(pc.y-pa.y)-(pb.y-pa.y)*(pc.x-pa.x);
    if(cross<0){culled++;continue} // clockwise = back face = skip
    
    sorted.push({face:f,depth:p.z,screenSize:screenSize});
  }
  sorted.sort(function(a,b){return a.depth-b.depth});
  
  document.getElementById('h-drawn').textContent=sorted.length+'/'+totalF;
  
  // Draw only visible faces
  for(var si=0;si<sorted.length;si++){
    var f=sorted[si].face;
    var pts2d=[];
    for(var k=0;k<f.pts.length;k++) pts2d.push(project(f.pts[k]));
    
    var isPent=f.type==='pent';
    var depth01=Math.max(0,Math.min(1,(sorted[si].depth+2)/4));
    var alpha=0.15+depth01*0.5;
    var ss=sorted[si].screenSize;
    
    // Fill
    cx.beginPath();
    cx.moveTo(pts2d[0].x,pts2d[0].y);
    for(var k=1;k<pts2d.length;k++) cx.lineTo(pts2d[k].x,pts2d[k].y);
    cx.closePath();
    
    if(isPent){
      cx.fillStyle='rgba(193,74,59,'+alpha*0.4+')';
      cx.strokeStyle='rgba(255,105,180,'+alpha+')';
    } else {
      cx.fillStyle='rgba(0,40,60,'+alpha*0.3+')';
      cx.strokeStyle='rgba(0,180,255,'+alpha*0.6+')';
    }
    cx.fill();
    // Only stroke if face is big enough to see edges
    if(ss>2){cx.lineWidth=isPent?1.5:0.5;cx.stroke()}
    
    // Vertices: only if face is large enough
    if(cam.atom>0.2&&ss>5){
      for(var k=0;k<pts2d.length;k++){
        var r=cam.atom*(isPent?2:1.2);
        cx.fillStyle=isPent?'rgba(255,105,180,'+alpha+')':'rgba(0,255,213,'+alpha*0.6+')';
        cx.beginPath();cx.arc(pts2d[k].x,pts2d[k].y,r,0,Math.PI*2);cx.fill();
      }
    }
  }
}

// ═══ OPERATIONS ═══
function doSeed(){
  M.group('SEED');
  M.seed();
  M.crystal();
  
  gkState = GK.buildC60();
  
  // Log every vertex and edge
  var inv = GK.invariants(gkState);
  M.P1({vertices:inv.vertices,reason:'dodecahedron vertices from golden ratio + phi'});
  M.P2({edges:inv.edges,reason:'trivalent connectivity, every vertex degree 3'});
  M.P7({faces:inv.faces,pents:inv.pents,hexes:inv.hexes,chi:inv.vertices-inv.edges+inv.faces});
  
  var check = checkInv();
  M.invariant(check);
  M.groupEnd('SEED');
  
  flRec('SEED',check);
  axLog('SEED: dodecahedron born','ax-inv');
  axLog('V='+check.V+' E='+check.E+' F='+check.F+' P='+check.pents+' chi='+check.chi,'ax-p7');
  updateHud(check);
}

function doRefineAll(){
  if(!gkState)return doSeed();
  M.group('REFINE_ALL');
  M.refine('ALL faces');
  var before=GK.invariants(gkState);
  
  M.P5({operation:'refineAll',facesBefore:before.faces});
  gkState=GK.refineAll(gkState,params);
  
  var check=checkInv();
  M.P6({aggregate:'centroid per face',count:before.faces});
  M.P1({innerNodes:before.faces,midNodes:before.faces});
  M.P2({innerEdges:before.faces,hexEdges:before.faces*6});
  M.P4({replaced:before.faces,created:check.F});
  M.P7({pentsAfter:check.pents,chi:check.chi,evRatio:check.evRatio});
  M.invariant(check);
  M.groupEnd('REFINE_ALL');
  
  flRec('REFINE_ALL',{before:before,after:check});
  axLog('REFINE ALL: '+before.faces+'F → '+check.F+'F','ax-p5');
  axLog('P='+check.pents+' chi='+check.chi+' E/V='+check.evRatio.toFixed(3),'ax-p7');
  updateHud(check);
}

function doRefinePents(){
  if(!gkState)return doSeed();
  M.group('REFINE_PENTS');
  M.refine('pentagons only');
  gkState=GK.refineAllPents(gkState,params);
  var check=checkInv();
  M.invariant(check);
  M.groupEnd('REFINE_PENTS');
  flRec('REFINE_PENTS',check);
  axLog('REFINE 5s: P='+check.pents+' F='+check.F,'ax-p6');
  updateHud(check);
}

function doRefineHexes(){
  if(!gkState)return doSeed();
  M.group('REFINE_HEXES');
  M.refine('hexagons only');
  gkState=GK.refineAllHexes(gkState,params);
  var check=checkInv();
  M.invariant(check);
  M.groupEnd('REFINE_HEXES');
  flRec('REFINE_HEXES',check);
  axLog('REFINE 6s: P='+check.pents+' F='+check.F,'ax-p4');
  updateHud(check);
}

function doUndo(){
  if(!gkState)return;
  gkState=GK.undo(gkState);
  var check=checkInv();
  flRec('UNDO',check);
  axLog('UNDO','ax-p3');
  updateHud(check);
}

function doReset(){
  gkState=null;
  M.group('RESET');
  console.log('%c♻ RESET to void','color:#555;font-size:12px');
  M.groupEnd('RESET');
  flRec('RESET',{});
  axLog('RESET: void','ax-p3');
  document.getElementById('euler').innerHTML='<span class="ok">VOID</span>';
  clearHud();
}

function doExport(){
  flExport();
  console.log('%c📦 EXPORTED: '+FL.entries.length+' entries','color:#ffd700;font-size:12px');
  axLog('EXPORTED '+FL.entries.length+' entries','ax-inv');
}

function doExportGraph(){
  if(!gkState)return;
  var inv=GK.invariants(gkState);
  var data={session:FL.session,faces:gkState.faces.length,invariants:inv,
    serialized:GK.serialize(gkState),params:params};
  var blob=new Blob([JSON.stringify(data)],{type:'application/json'});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download=FL.session+'_graph.json';a.click();
  console.log('%c📦 GRAPH EXPORTED','color:#ffd700');
}

// ═══ INVARIANT CHECK ═══
function checkInv(){
  if(!gkState)return{V:0,E:0,F:0,chi:0,pents:0,hexes:0,evRatio:0};
  var inv=GK.invariants(gkState);
  var chi=inv.vertices-inv.edges+inv.faces;
  return{V:inv.vertices,E:inv.edges,F:inv.faces,chi:chi,
    pents:inv.pents,hexes:inv.hexes,maxLevel:inv.maxLevel,
    evRatio:inv.vertices>0?inv.edges/inv.vertices:0};
}

// ═══ HUD ═══
function updateHud(c){
  document.getElementById('h-v').textContent=c.V;
  document.getElementById('h-e').textContent=c.E;
  document.getElementById('h-f').textContent=c.F;
  document.getElementById('h-p').textContent=c.pents;
  document.getElementById('h-h').textContent=c.hexes;
  document.getElementById('h-chi').textContent=c.chi;
  document.getElementById('h-ev').textContent=c.evRatio.toFixed(3);
  document.getElementById('h-lv').textContent=c.maxLevel||0;
  document.getElementById('h-ops').textContent=M._c;
  var el=document.getElementById('euler');
  if(c.pents===12&&c.chi===2) el.innerHTML='<span class="ok">V-E+F=2 · P=12 · E/V='+c.evRatio.toFixed(3)+'</span>';
  else el.innerHTML='<span class="bad">P='+c.pents+' χ='+c.chi+' BROKEN</span>';
}
function clearHud(){['h-v','h-e','h-f','h-p','h-h','h-chi','h-ev','h-lv'].forEach(function(id){document.getElementById(id).textContent='-'})}

function axLog(msg,cls){
  var el=document.getElementById('axiom-log');
  var d=document.createElement('div');d.className=cls||'';d.textContent=msg;
  el.insertBefore(d,el.firstChild);
  if(el.children.length>50)el.removeChild(el.lastChild);
}

// ═══ MOUSE ROTATION ═══
cv.addEventListener('pointerdown',function(e){dragging=true;lastMouse={x:e.clientX,y:e.clientY}});
cv.addEventListener('pointermove',function(e){
  if(!dragging)return;
  cam.ry+=(e.clientX-lastMouse.x)*0.005;
  cam.rx+=(e.clientY-lastMouse.y)*0.005;
  cam.rx=Math.max(-Math.PI/2,Math.min(Math.PI/2,cam.rx));
  lastMouse={x:e.clientX,y:e.clientY};
});
cv.addEventListener('pointerup',function(){dragging=false});
cv.addEventListener('wheel',function(e){
  e.preventDefault();
  cam.zoom*=e.deltaY>0?0.92:1.08;
  cam.zoom=Math.max(0.5,Math.min(50000,cam.zoom));
  document.getElementById('sl-zm').value=Math.round(cam.zoom);
  SV('sv-zm',Math.round(cam.zoom));
},{passive:false});



// === DODECAHEDRON SEED ===
function doSeedDodec(){
  M.group('SEED_DODECAHEDRON');
  console.log('%c\u26b3 PURE SEED: Dodecahedron (12 pentagons, 0 hexagons)','color:#ff69b4;font-size:14px');
  console.log('%c  The simplest closed surface of pentagons','color:#ff69b4');
  console.log('%c  V=20 E=30 F=12 chi=2 E/V=1.5000','color:#00ffd5');
  console.log('%c  Euler FORCES this. There is no simpler seed.','color:#ffd700');
  
  gkState = GK.buildDodecahedron();
  var check = checkInv();
  M.invariant(check);
  M.groupEnd('SEED_DODECAHEDRON');
  
  flRec('SEED_DODEC',check);
  axLog('SEED: pure dodecahedron (12 pents, 0 hex)','ax-inv');
  axLog('V='+check.V+' E='+check.E+' F='+check.F+' P='+check.pents+' chi='+check.chi,'ax-p7');
  updateHud(check);
  secretsLeft = 6;
}

// === PAPYRUS WARNINGS ===
var secretsLeft = 6;
var papyrusMessages = [
  '',
  'You have revealed 5 layers. The structure remembers.',
  'You have revealed 4 layers. The patterns are watching.',
  '3 secrets remain. The graph knows your name.',
  '2 secrets remain. Beyond here lies the brain.',
  'Last secret. Beyond this: Out of Memory.\nThe universe has shown you everything it can.',
  'There are no more secrets.\nThe graph has given you all it has.\nYou saw neurons. You saw divinity.\nThe monkey wanted more.\nThere is no more.'
];

var oldDoRefineAll = doRefineAll;
doRefineAll = function(){
  if(!gkState) return doSeed();
  
  var level = 0;
  if(gkState && gkState.faces.length > 0){
    level = gkState.faces[0].level || 0;
  }
  
  if(level >= 1 && secretsLeft > 0){
    secretsLeft--;
    var msg = papyrusMessages[6 - secretsLeft] || '';
    if(msg){
      var proceed = confirm(
        '\u2500\u2500\u2500 PAPYRUS \u2500\u2500\u2500\n\n' +
        msg + '\n\n' +
        (secretsLeft > 0 ? secretsLeft + ' secret layers remain.\n' : '') +
        'Current: ' + gkState.faces.length.toLocaleString() + ' faces\n' +
        'Next: ~' + (gkState.faces.length * 7).toLocaleString() + ' faces\n\n' +
        'Continue refining?'
      );
      if(!proceed){
        secretsLeft++;
        return;
      }
    }
  }
  
  oldDoRefineAll();
};

// MOBIUSIFY ENGINE: Sphere to Mobius strip
// chi: 2 to 0. Remove 2 antipodal faces, half-twist.
var MOB={active:false,t:0,spherePos:null,mobiusPos:null,R:2.5,W:0.8};

function sphereToMobius(pt,R,W){
  var x=pt[0],y=pt[1],z=pt[2];
  var r=Math.sqrt(x*x+y*y+z*z);if(r<1e-10)return[R,0,0];
  var theta=Math.atan2(y,x),phi=Math.acos(Math.max(-1,Math.min(1,z/r)));
  var u=theta+Math.PI,v=(phi/Math.PI-0.5)*2*W;
  return[(R+v*Math.cos(u/2))*Math.cos(u),(R+v*Math.cos(u/2))*Math.sin(u),v*Math.sin(u/2)];
}

function computeMobiusPositions(){
  MOB.spherePos=[];MOB.mobiusPos=[];
  for(var i=0;i<gkState.faces.length;i++){
    var f=gkState.faces[i],sp=[],mp=[];
    for(var k=0;k<f.pts.length;k++){sp.push(f.pts[k].slice());mp.push(sphereToMobius(f.pts[k],MOB.R,MOB.W));}
    MOB.spherePos.push(sp);MOB.mobiusPos.push(mp);
  }
  M.P4({transform:'sphere->mobius',faces:gkState.faces.length,chi:'2->0'});
}

function applyMobiusLerp(t){
  if(!MOB.spherePos||!MOB.mobiusPos)return;
  for(var i=0;i<gkState.faces.length;i++){
    var f=gkState.faces[i],sp=MOB.spherePos[i],mp=MOB.mobiusPos[i];
    if(!sp||!mp)continue;
    for(var k=0;k<f.pts.length;k++){
      f.pts[k][0]=sp[k][0]*(1-t)+mp[k][0]*t;
      f.pts[k][1]=sp[k][1]*(1-t)+mp[k][1]*t;
      f.pts[k][2]=sp[k][2]*(1-t)+mp[k][2]*t;
    }
  }
}

function toggleMobius(){
  if(!gkState)return;
  var btn=document.getElementById('bMob'),sl=document.getElementById('mobSlider');
  if(MOB.active){
    MOB.active=false;MOB.t=0;btn.style.background='';sl.disabled=true;sl.value=0;
    document.getElementById('twistVal').textContent='0.00';
    document.getElementById('mobState').textContent='off';
    if(MOB.spherePos){for(var i=0;i<gkState.faces.length;i++){
      var f=gkState.faces[i],sp=MOB.spherePos[i];
      if(sp)for(var k=0;k<f.pts.length;k++)f.pts[k]=sp[k].slice();
    }}
    MOB.spherePos=null;MOB.mobiusPos=null;
    console.log('%c MOBIUS OFF: sphere restored, chi=2','color:#ff69b4;font-size:12px');
    axLog('MOBIUS OFF: chi=2 restored','ax-p4');
    return;
  }
  MOB.active=true;btn.style.background='#3a0020';sl.disabled=false;
  document.getElementById('mobState').textContent='on';
  computeMobiusPositions();
  console.log('%c MOBIUS ON: chi 2->0, drag slider','color:#ff69b4;font-size:14px');
  console.log('%c  Sphere chi=2 -> Mobius chi=0','color:#ff69b4');
  console.log('%c  12 pentagons -> 10 (2 become the twist)','color:#ff69b4');
  axLog('MOBIUS ON: chi=2->0, twist slider active','ax-p6');
  flRec('MOBIUS_ON',{faces:gkState.faces.length});
}

function setMobiusTwist(v){
  var t=parseInt(v)/100;MOB.t=t;
  document.getElementById('twistVal').textContent=t.toFixed(2);
  if(!MOB.active)return;
  applyMobiusLerp(t);
  flRec('MOBIUS_TWIST',{t:t});
}

// ═══ ANIMATE ═══
function animate(){
  if(!dragging) cam.ry+=cam.spin;
  draw();
  requestAnimationFrame(animate);
}

// ═══ BOOT ═══
console.log('%c╔══════════════════════════════════════╗','color:#ff69b4');
console.log('%c║  GENESIS v7.5.1 — Fractal Graph Explorer ║','color:#ff69b4;font-weight:bold');
console.log('%c║  7 primitives · 3 crystal conditions  ║','color:#00ffd5');
console.log('%c║  12 pentagons · Euler forced · P=12   ║','color:#ffd700');
console.log('%c╚══════════════════════════════════════╝','color:#ff69b4');
console.log('%cOpen this console to see every operation as structured math.','color:#555');
console.log('%cEvery P1-P7 call prints here with timing.','color:#555');
console.log('%cconsole.table() shows invariants after each refine.','color:#555');
console.log('%cperformance.measure() tracks operation timing.','color:#555');

doSeed();
animate();
</script></body></html>

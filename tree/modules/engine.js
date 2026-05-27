// ============================================================
//  engine.js — Sacred Math Tree · core engine
//  build / layout / render / interact / autopilot
//  Depends on: data.js loaded first
// ============================================================

// === CONSOLE LOG ===
const CON = document.getElementById('logp');
let logBuf = [];
function clog(msg, cls) {
  let t = new Date();
  let ts = t.getMinutes().toString().padStart(2,'0')+':'+t.getSeconds().toString().padStart(2,'0')+'.'+t.getMilliseconds().toString().padStart(3,'0');
  let line = '<span class="'+(cls||'')+'">'+ts+' '+msg+'</span>';
  logBuf.push(line);
  if(logBuf.length > 200) logBuf.shift();
  CON.innerHTML = logBuf.join('\n');
  CON.scrollTop = CON.scrollHeight;
}
document.getElementById('logp').addEventListener('mouseenter', () => {
  let sel = window.getSelection(), range = document.createRange();
  range.selectNodeContents(document.getElementById('logp'));
  sel.removeAllRanges(); sel.addRange(range);
});
clog('Sacred Math Tree v5.0 init', 'log-state');
clog('KaTeX: '+(typeof katex !== 'undefined' ? 'loaded' : 'MISSING'), 'log-state');

// === STATE ===
let tokens=3, xp=0, streak=0, combo=0, comboT=null, wave=0.5;
let opened=new Set(), kidsShown=new Set();
let E={}, P={}, items=[], lk={};
const CX=2000, CY=100;
let XSP_CUR=460, DY_CUR=320;
const plane=document.getElementById('plane'), lksvg=document.getElementById('lksvg');
let spread=1.0, depth=1.0, zoomLock=0;
const BASE_XSP=460, BASE_DY=320;
let boxH={}, boxW={};
let shameDur=2000;

// === SLIDERS ===
function onSlider(id, cb){ document.getElementById(id).addEventListener('input', cb); }
onSlider('sl-wave', e=>{
  wave = e.target.value/100;
  document.getElementById('sv-wave').textContent = e.target.value;
  let h = document.getElementById('h-wv'); if(h) h.textContent = wave.toFixed(2);
  rebuildPaths();
});
onSlider('sl-spread', e=>{
  spread = 0.3 + e.target.value/100*1.7;
  document.getElementById('sv-spread').textContent = e.target.value;
  let hs = document.getElementById('h-sp'); if(hs) hs.textContent = spread.toFixed(1)+'x';
  relayout();
});
onSlider('sl-depth', e=>{
  depth = 0.3 + e.target.value/100*1.7;
  document.getElementById('sv-depth').textContent = e.target.value;
  let hd = document.getElementById('h-dy'); if(hd) hd.textContent = Math.round(BASE_DY*depth);
  relayout();
});
onSlider('sl-zlock', e=>{
  zoomLock = e.target.value/100;
  let pct = Math.round(zoomLock*100);
  document.getElementById('sv-zlock').textContent = pct===0 ? 'off' : pct+'%';
  let hl = document.getElementById('h-lk'); if(hl) hl.textContent = pct===0 ? 'off' : pct+'%';
});
onSlider('sl-shame', e=>{
  shameDur = e.target.value/10*1000;
  let sec = (shameDur/1000).toFixed(1);
  document.getElementById('sv-shame').textContent = sec+'s';
  let hs = document.getElementById('h-sh'); if(hs) hs.textContent = sec+'s';
});

// === TREE SELECTOR ===
document.getElementById('tree-sel').addEventListener('change', function(ev){
  let newId = ev.target.value;
  if(newId === currentTreeId) return;
  currentTreeId = newId;
  Object.values(E).forEach(b => b.remove());
  while(lksvg.firstChild) lksvg.removeChild(lksvg.firstChild);
  E={}; P={}; items=[]; lk={}; boxH={}; boxW={};
  opened.clear(); kidsShown.clear();
  autoBuilt=false; autoQueue=[]; autoStep=0;
  tokens=3; xp=0; streak=0; combo=0;
  uH(); updCount();
  let src = TREES[newId];
  T.id=src.id; T.tag=src.tag; T.type=src.type; T.latex=src.latex;
  T.sub=src.sub; T.cost=src.cost; T.xp=src.xp; T.ch=src.ch;
  clog('SWITCH TREE: '+newId, 'log-click');
  document.getElementById('sv-auto').textContent = 'ready';
  document.getElementById('h-n').textContent = '0';
  document.getElementById('h-d').textContent = '0';
  drawGridEmpty(); center();
});

// === GRID ===
const gridCv = document.getElementById('grid-cv');
const gridCtx = gridCv.getContext('2d');

function drawGrid(){
  let mx=0, my=0;
  items.forEach(i=>{ if(i.x+300>mx) mx=i.x+300; if(i.y+400>my) my=i.y+400; });
  mx=Math.max(mx,4000); my=Math.max(my,3000);
  gridCv.width=mx; gridCv.height=my;
  gridCtx.clearRect(0,0,mx,my);
  let gx=Math.max(40, XSP_CUR*0.5), gy=Math.max(40, DY_CUR*0.5);
  gridCtx.strokeStyle='rgba(0,212,255,0.018)'; gridCtx.lineWidth=0.5;
  gridCtx.beginPath();
  for(let x=0;x<mx;x+=gx){gridCtx.moveTo(x,0);gridCtx.lineTo(x,my);}
  for(let y=0;y<my;y+=gy){gridCtx.moveTo(0,y);gridCtx.lineTo(mx,y);}
  gridCtx.stroke();
  gridCtx.strokeStyle='rgba(0,212,255,0.035)'; gridCtx.lineWidth=0.5;
  gridCtx.beginPath();
  for(let x=0;x<mx;x+=gx*4){gridCtx.moveTo(x,0);gridCtx.lineTo(x,my);}
  for(let y=0;y<my;y+=gy*4){gridCtx.moveTo(0,y);gridCtx.lineTo(mx,y);}
  gridCtx.stroke();
  gridCtx.strokeStyle='rgba(0,212,255,0.06)'; gridCtx.lineWidth=1;
  gridCtx.beginPath(); gridCtx.moveTo(CX,0); gridCtx.lineTo(CX,my); gridCtx.stroke();
}

function drawGridEmpty(){
  gridCv.width=4000; gridCv.height=3000;
  gridCtx.clearRect(0,0,4000,3000);
  gridCtx.strokeStyle='rgba(0,212,255,0.018)'; gridCtx.lineWidth=0.5;
  gridCtx.beginPath();
  for(let x=0;x<4000;x+=230){gridCtx.moveTo(x,0);gridCtx.lineTo(x,3000);}
  for(let y=0;y<3000;y+=160){gridCtx.moveTo(0,y);gridCtx.lineTo(4000,y);}
  gridCtx.stroke();
  gridCtx.strokeStyle='rgba(0,212,255,0.035)';
  gridCtx.beginPath();
  for(let x=0;x<4000;x+=920){gridCtx.moveTo(x,0);gridCtx.lineTo(x,3000);}
  for(let y=0;y<3000;y+=640){gridCtx.moveTo(0,y);gridCtx.lineTo(4000,y);}
  gridCtx.stroke();
}

// === LAYOUT ===
function collect(n, d, xc, px, py){
  let nx=px!==null?xc:CX, ny=py!==null?py+DY_CUR:CY;
  items.push({n, x:nx, y:ny, d});
  if(n.ch && n.ch.length){
    let c=n.ch.length, sp=XSP_CUR*Math.min(c,5), sx=nx-sp/2, st=c>1?sp/(c-1):0;
    for(let i=0;i<c;i++) collect(n.ch[i], d+1, c===1?nx:sx+st*i, nx, ny);
  }
}

function relayout(){
  items=[];
  XSP_CUR=BASE_XSP*spread;
  DY_CUR=BASE_DY*depth;
  collect(T,0,CX,null,null);
  lk={}; items.forEach(i=>lk[i.n.id]=i);
  items.forEach(it=>{
    let box=E[it.n.id];
    if(box){ let w=boxW[it.n.id]||200; box.style.left=(it.x-w/2)+'px'; box.style.top=(it.y-42)+'px'; }
  });
  let mx=0,my=0; items.forEach(i=>{if(i.x+200>mx)mx=i.x+200;if(i.y+400>my)my=i.y+400;});
  lksvg.setAttribute('width',mx); lksvg.setAttribute('height',my); lksvg.setAttribute('viewBox','0 0 '+mx+' '+my);
  rebuildPaths(); drawGrid();
}

// === PATHS ===
function mkD(pid, cid){
  let pi=lk[pid], ci=lk[cid]; if(!pi||!ci) return 'M0,0';
  let pH=boxH[pid]||84, x1=pi.x, y1=pi.y-42+pH, x2=ci.x, y2=ci.y-42;
  let dy=y2-y1, w=wave, cy1=y1+dy*(0.15+0.35*w), cy2=y2-dy*(0.15+0.35*w);
  return 'M'+x1+','+y1+' C'+x1+','+cy1+' '+x2+','+cy2+' '+x2+','+y2;
}
function rebuildPaths(){
  Object.keys(P).forEach(id=>{ let pid=P[id].dataset.from; P[id].setAttribute('d',mkD(pid,id)); });
}
function lnC(n){ return n.type==='dead'?'rgba(220,80,80,0.25)':n.type==='result'?'rgba(80,220,140,0.3)':'rgba(130,150,210,0.22)'; }
function fP(t, tid, pid){ if(t.id===tid) return pid; if(t.ch) for(let c of t.ch){let f=fP(c,tid,t.id);if(f!==null)return f;} return null; }

// === GAMIFICATION ===
function fp(el, txt, col){ let r=el.getBoundingClientRect(),p=document.createElement('div');p.className='tp';p.style.color=col||'#e8b44c';p.textContent=txt;p.style.left=r.left+r.width/2-20+'px';p.style.top=r.top-10+'px';document.body.appendChild(p);setTimeout(()=>p.remove(),1300); }
function aT(n, el){ tokens+=n; clog('+'+n+' tokens (now:'+tokens+')', 'log-tok'); if(el) fp(el,'+'+n+' \u2666'); uH(); }
function aX(n, el){ xp+=n; clog('+'+n+' XP (now:'+xp+')', 'log-xp'); if(el) fp(el,'+'+n+' XP','#a78bfa'); uH(); }
function bS(el){ streak++;combo++;clog('streak:'+streak+' combo:'+combo,'log-tok');let c=document.getElementById('combo');if(combo>=2){c.textContent=combo+'x COMBO';c.style.opacity='1';c.style.color=combo>=5?'#e8b44c':combo>=3?'#f97316':'#a78bfa';}clearTimeout(comboT);comboT=setTimeout(()=>{combo=0;c.style.opacity='0';},3500);if(streak===3)aT(2,el);if(streak===5)aT(3,el);if(streak===8)aT(5,el); }
function uH(){ document.getElementById('g-tok').textContent=tokens; document.getElementById('g-xp').textContent=xp; document.getElementById('g-str').textContent=streak; }
function fl(box){ if(!box)return; box.classList.remove('glow-flash'); void box.offsetWidth; box.classList.add('glow-flash'); }
function updCount(){ let vis=items.filter(i=>opened.has(i.n.id)); document.getElementById('h-n').textContent=vis.length; document.getElementById('h-d').textContent=vis.length?Math.max(0,...vis.map(i=>i.d)):0; }

// === BUILD ===
function build(){
  items=[]; collect(T,0,CX,null,null); lk={}; items.forEach(i=>lk[i.n.id]=i);
  let mx=0,my=0; items.forEach(i=>{if(i.x+200>mx)mx=i.x+200;if(i.y+400>my)my=i.y+400;});
  lksvg.setAttribute('width',mx); lksvg.setAttribute('height',my); lksvg.setAttribute('viewBox','0 0 '+mx+' '+my);

  items.forEach(it=>{
    let n=it.n, tc=n.type==='root'?'gold':n.type==='tool'?'purp':n.type==='result'?'grn':'red';
    let pid=fP(T,n.id,null);
    if(pid){ let p=document.createElementNS('http://www.w3.org/2000/svg','path'); p.dataset.from=pid; p.dataset.to=n.id; lksvg.appendChild(p); P[n.id]=p; }
    let box=document.createElement('div');
    box.className='eq t-'+n.type;
    box.style.left=(it.x-150)+'px'; box.style.top=(it.y-42)+'px';
    let badge=n.cost>0?'<div class="tok-badge">\u2666'+n.cost+'</div>':'';
    box.innerHTML=badge+
      '<div class="ghost-inner"><div class="tag '+tc+'">'+n.tag+'</div><div class="lock-icon">\uD83D\uDD12</div></div>'+
      '<div class="inner"><div class="tag '+tc+'">'+n.tag+'</div><div class="ltx"></div>'+(n.sub?'<div class="sub">'+n.sub+'</div>':'')+'</div>';
    plane.appendChild(box);
    try{ katex.render(n.latex, box.querySelector('.inner .ltx'), {throwOnError:false, displayMode:true}); }catch(e){}
    E[n.id]=box;
  });

  // Measure real sizes
  Object.values(E).forEach(b=>{ b.style.opacity='1'; b.style.position='absolute'; });
  Object.keys(E).forEach(id=>{
    let b=E[id]; boxH[id]=b.offsetHeight||84; boxW[id]=b.offsetWidth||200;
    let it=items.find(i=>i.n.id===id); if(it) b.style.left=(it.x-boxW[id]/2)+'px';
  });
  Object.values(E).forEach(b=>{ b.style.opacity=''; });
  Object.keys(P).forEach(id=>{ let pid=P[id].dataset.from; P[id].setAttribute('d',mkD(pid,id)); });
  clog('build: '+items.length+' nodes, '+Object.keys(P).length+' paths', 'log-state');

  makeAlive(T.id);

  items.forEach(it=>{
    let n=it.n, box=E[n.id];
    box.addEventListener('click', ev=>{
      ev.stopPropagation();
      if(opened.has(n.id) && !kidsShown.has(n.id) && n.ch && n.ch.length){
        if(zoomLock>0 && zm<zoomLock){ showZoomGate(); return; }
        showKids(n); return;
      }
      if(!opened.has(n.id) && box.classList.contains('ghost')){
        if(zoomLock>0 && zm<zoomLock){ showZoomGate(); return; }
        if(n.cost>0 && tokens<n.cost){ flashRed(box); return; }
        unlockNode(n, box); return;
      }
    });
  });
}

function showZoomGate(){
  let g=document.getElementById('zoom-gate');
  document.getElementById('zg-cur').textContent=Math.round(zm*100)+'%';
  document.getElementById('zg-need').textContent=Math.round(zoomLock*100)+'%';
  g.classList.add('show');
  setTimeout(()=>g.classList.remove('show'), shameDur);
}
function flashRed(box){ clog('NOT ENOUGH tokens','log-err'); box.style.borderColor='#f87171'; box.style.boxShadow='0 0 18px rgba(248,80,80,0.2)'; setTimeout(()=>{ box.style.borderColor=''; box.style.boxShadow=''; },500); }

function makeAlive(id){
  clog('ALIVE: '+id, 'log-click');
  opened.add(id); let box=E[id];
  box.classList.remove('ghost'); box.classList.add('alive');
  boxH[id]=box.offsetHeight||84;
  rebuildPaths(); updCount();
}

function showKids(parent){
  if(kidsShown.has(parent.id)) return;
  kidsShown.add(parent.id); fl(E[parent.id]);
  clog('REVEAL KIDS of '+parent.id, 'log-click');
  parent.ch.forEach((ch,i)=>{
    setTimeout(()=>{
      let path=P[ch.id]; if(path) path.classList.add('ghost-line');
      setTimeout(()=>{ E[ch.id].classList.add('ghost'); }, 200);
    }, i*120);
  });
}

function unlockNode(n, box){
  clog('UNLOCK: '+n.id+' (cost:'+n.cost+')', 'log-click');
  fl(box); tokens-=n.cost; opened.add(n.id);
  let path=P[n.id];
  if(path){ path.classList.remove('ghost-line'); path.style.stroke=lnC(n); path.classList.add('alive-line'); }
  setTimeout(()=>{
    box.classList.remove('ghost'); box.classList.add('alive');
    boxH[n.id]=box.offsetHeight||84; rebuildPaths();
    aX(n.xp, box); bS(box);
    if(n.type==='result'||n.type==='dead') aT(1,box);
    uH();
  }, 250);
  setTimeout(()=>{ if(n.ch && n.ch.length) showKids(n); }, 500);
  updCount();
}

function findNode(t, id){ if(t.id===id) return t; if(t.ch) for(let c of t.ch){let f=findNode(c,id);if(f) return f;} return null; }

// === PAN / ZOOM ===
let panX=0, panY=0, zm=0.6;
function center(){ panX=(window.innerWidth/2/zm)-CX; panY=40/zm; upT(); }
function upT(){
  plane.style.zoom=zm; plane.style.left=panX+'px'; plane.style.top=panY+'px';
  let ze=document.getElementById('h-zm'); if(ze) ze.textContent=Math.round(zm*100)+'%';
}
let drag=false, lm={x:0,y:0};
document.addEventListener('pointerdown', e=>{ if(e.target.closest('.eq')) return; drag=true; lm={x:e.clientX,y:e.clientY}; });
document.addEventListener('pointermove', e=>{ if(!drag) return; panX+=(e.clientX-lm.x)/zm; panY+=(e.clientY-lm.y)/zm; lm={x:e.clientX,y:e.clientY}; upT(); });
document.addEventListener('pointerup', ()=>{ drag=false; });
document.addEventListener('wheel', e=>{ e.preventDefault(); let oz=zm; zm*=e.deltaY>0?0.92:1.08; zm=Math.max(0.18,Math.min(2.0,zm)); panX=e.clientX/zm-(e.clientX/oz-panX); panY=e.clientY/zm-(e.clientY/oz-panY); upT(); }, {passive:false});

// === AUTOPILOT ===
let autoBuilt=false, autoQueue=[], autoStep=0;

document.getElementById('btn-auto').addEventListener('click', ()=>{
  let sv=document.getElementById('sv-auto');
  if(!autoBuilt){
    autoBuilt=true; build(); drawGrid();
    Object.values(E).forEach(b=>{ b.classList.remove('alive','ghost'); });
    Object.values(P).forEach(p=>{ p.classList.remove('ghost-line','alive-line'); p.style.stroke='#0b0d14'; });
    opened.clear(); kidsShown.clear();
    sv.textContent='gen...';
    setTimeout(()=>{ makeAlive(T.id); fl(E[T.id]); autoQueue=[T.id]; autoStep=1; sv.textContent='root'; }, 300);
    return;
  }
  if(autoQueue.length===0){ sv.textContent='done!'; return; }
  autoStep++;
  let nid=autoQueue[0], node=findNode(T,nid);
  if(!node){ autoQueue.shift(); return; }
  if(!kidsShown.has(nid) && node.ch && node.ch.length){ showKids(node); sv.textContent='reveal '+nid; return; }
  autoQueue.shift();
  if(node.ch){
    for(let ch of node.ch){
      if(!opened.has(ch.id)){ let box=E[ch.id]; if(box && box.classList.contains('ghost')){ tokens=Math.max(tokens,ch.cost+1); unlockNode(ch,box); autoQueue.push(ch.id); sv.textContent='open '+ch.id; return; } }
      else { if(!kidsShown.has(ch.id) && ch.ch && ch.ch.length) autoQueue.push(ch.id); }
    }
    for(let ch of node.ch){ if(ch.ch && ch.ch.length && !ch.ch.every(c=>opened.has(c.id))) autoQueue.push(ch.id); }
  }
  if(autoQueue.length===0){ sv.textContent='done!'; clog('autopilot: COMPLETE. '+opened.size+' nodes opened.', 'log-click'); }
});

// === FULL AUTO (all 10 trees) ===
let fullAutoRunning=false, fullAutoTimer=null, fullAutoIdx=0;
const TREE_ORDER=['sinx','euler_e','power_rule','dsin','chain','int_power','improper','taylor_ex','ftc','eps_delta'];
const STEP_DELAY=400, TREE_PAUSE=1500;

document.getElementById('btn-fullauto').addEventListener('click', ()=>{
  if(fullAutoRunning){
    fullAutoRunning=false; clearTimeout(fullAutoTimer);
    document.getElementById('btn-fullauto').textContent='\u23ED\u23ED all trees';
    document.getElementById('sv-fullauto').textContent='stopped';
    return;
  }
  fullAutoRunning=true; fullAutoIdx=0;
  document.getElementById('btn-fullauto').textContent='\u23F9 stop';
  clog('FULL AUTO: starting all 10 trees', 'log-click');
  playNextTree();
});

function playNextTree(){
  if(!fullAutoRunning || fullAutoIdx>=TREE_ORDER.length){
    fullAutoRunning=false;
    document.getElementById('btn-fullauto').textContent='\u23ED\u23ED all trees';
    document.getElementById('sv-fullauto').textContent='done!';
    return;
  }
  let treeId=TREE_ORDER[fullAutoIdx];
  document.getElementById('sv-fullauto').textContent=(TREE_ORDER.length-fullAutoIdx)+' left';
  document.getElementById('tree-sel').value=treeId;
  clog('FULL AUTO ['+(fullAutoIdx+1)+'/10]: '+treeId, 'log-click');
  currentTreeId=treeId;
  Object.values(E).forEach(b=>b.remove());
  while(lksvg.firstChild) lksvg.removeChild(lksvg.firstChild);
  E={}; P={}; items=[]; lk={}; boxH={}; boxW={};
  opened.clear(); kidsShown.clear();
  autoBuilt=false; autoQueue=[]; autoStep=0;
  tokens=3; xp=0; streak=0; combo=0; uH();
  document.getElementById('h-n').textContent='0';
  document.getElementById('h-d').textContent='0';
  let src=TREES[treeId];
  T.id=src.id; T.tag=src.tag; T.type=src.type; T.latex=src.latex; T.sub=src.sub; T.cost=src.cost; T.xp=src.xp; T.ch=src.ch;
  autoBuilt=true; build(); drawGrid();
  Object.values(E).forEach(b=>{ b.classList.remove('alive','ghost'); });
  Object.values(P).forEach(p=>{ p.classList.remove('ghost-line','alive-line'); p.style.stroke='#0b0d14'; });
  opened.clear(); kidsShown.clear();
  setTimeout(()=>{ makeAlive(T.id); fl(E[T.id]); autoQueue=[T.id]; autoStep=0; center(); autoStepThrough(); }, 500);
}

function autoStepThrough(){
  if(!fullAutoRunning) return;
  let unopened=items.filter(i=>!opened.has(i.n.id));
  if(unopened.length===0){ clog('FULL AUTO: tree '+currentTreeId+' COMPLETE ('+opened.size+' nodes)','log-click'); fullAutoIdx++; fullAutoTimer=setTimeout(playNextTree,TREE_PAUSE); return; }
  autoStep++;
  if(autoQueue.length===0){
    for(let it of items){ if(opened.has(it.n.id) && !kidsShown.has(it.n.id) && it.n.ch && it.n.ch.length){ autoQueue.push(it.n.id); break; } }
    if(autoQueue.length===0){
      for(let it of items){ if(!opened.has(it.n.id) && E[it.n.id] && E[it.n.id].classList.contains('ghost')){ tokens=Math.max(tokens,it.n.cost+1); unlockNode(it.n,E[it.n.id]); fullAutoTimer=setTimeout(autoStepThrough,STEP_DELAY); return; } }
      fullAutoIdx++; fullAutoTimer=setTimeout(playNextTree,TREE_PAUSE); return;
    }
  }
  let nid=autoQueue[0], node=findNode(T,nid);
  if(!node){ autoQueue.shift(); fullAutoTimer=setTimeout(autoStepThrough,STEP_DELAY); return; }
  if(!kidsShown.has(nid) && node.ch && node.ch.length){ showKids(node); fullAutoTimer=setTimeout(autoStepThrough,STEP_DELAY); return; }
  autoQueue.shift();
  if(node.ch){
    for(let ch of node.ch){
      if(!opened.has(ch.id)){ let box=E[ch.id]; if(box && box.classList.contains('ghost')){ tokens=Math.max(tokens,ch.cost+1); unlockNode(ch,box); autoQueue.push(ch.id); fullAutoTimer=setTimeout(autoStepThrough,STEP_DELAY); return; } }
      else { if(!kidsShown.has(ch.id) && ch.ch && ch.ch.length) autoQueue.push(ch.id); }
    }
    for(let ch of node.ch){ if(ch.ch && ch.ch.length && !ch.ch.every(c=>opened.has(c.id))) autoQueue.push(ch.id); }
  }
  fullAutoTimer=setTimeout(autoStepThrough,STEP_DELAY);
}

// === BOOT ===
drawGridEmpty(); center();
clog('v5.0: modules loaded. press autopilot to begin.', 'log-state');

// ============================================================
//  mobile.js — Sacred Math Tree · mobile module
//  pinch zoom + pan + tune panel + console toggle
//  Depends on: engine.js (zm, panX, panY, upT, drag, lm)
// ============================================================

// === PINCH ZOOM + TOUCH PAN ===
let touches=[], lastPinchDist=0, lastTouchMid={x:0,y:0};

document.addEventListener('touchstart', e=>{
  if(e.target.closest('.eq') || e.target.closest('#bar') || e.target.closest('#logp')) return;
  touches=Array.from(e.touches);
  if(touches.length===2){
    lastPinchDist=Math.hypot(touches[1].clientX-touches[0].clientX, touches[1].clientY-touches[0].clientY);
    lastTouchMid={x:(touches[0].clientX+touches[1].clientX)/2, y:(touches[0].clientY+touches[1].clientY)/2};
  } else if(touches.length===1){
    drag=true; lm={x:touches[0].clientX, y:touches[0].clientY};
  }
},{passive:true});

document.addEventListener('touchmove', e=>{
  if(e.target.closest('#bar') || e.target.closest('#logp')) return;
  touches=Array.from(e.touches);
  if(touches.length===2){
    e.preventDefault();
    let dist=Math.hypot(touches[1].clientX-touches[0].clientX, touches[1].clientY-touches[0].clientY);
    let mid={x:(touches[0].clientX+touches[1].clientX)/2, y:(touches[0].clientY+touches[1].clientY)/2};
    if(lastPinchDist>0){
      let scale=dist/lastPinchDist, oz=zm;
      zm*=scale; zm=Math.max(0.15,Math.min(2.5,zm));
      panX=mid.x/zm-(mid.x/oz-panX);
      panY=mid.y/zm-(mid.y/oz-panY);
      upT();
    }
    lastPinchDist=dist;
    // two-finger pan
    panX+=(mid.x-lastTouchMid.x)/zm;
    panY+=(mid.y-lastTouchMid.y)/zm;
    lastTouchMid=mid;
    upT();
  } else if(touches.length===1 && drag){
    panX+=(touches[0].clientX-lm.x)/zm;
    panY+=(touches[0].clientY-lm.y)/zm;
    lm={x:touches[0].clientX, y:touches[0].clientY};
    upT();
  }
},{passive:false});

document.addEventListener('touchend', e=>{
  drag=false; lastPinchDist=0;
  touches=Array.from(e.touches);
},{passive:true});

// === CONSOLE TOGGLE ===
let logVisible=false;
function toggleLog(){
  logVisible=!logVisible;
  document.getElementById('logp').classList.toggle('hidden',!logVisible);
  document.getElementById('btn-log').style.color=logVisible?'#80d0ff':'#333';
  clog('console '+(logVisible?'shown':'hidden'),'log-state');
}

// === TUNE PANEL (mobile sliders) ===
let tuneOpen=false;
function toggleTune(){
  tuneOpen=!tuneOpen;
  let p=document.getElementById('tune-panel');
  if(tuneOpen){
    p.innerHTML='';
    ['sl-wave','sl-spread','sl-depth','sl-zlock','sl-shame'].forEach(id=>{
      let orig=document.getElementById(id); if(!orig) return;
      let row=orig.closest('.sb-row'); if(!row) return;
      let clone=row.cloneNode(true);
      let inp=clone.querySelector('input');
      inp.id=id+'-mob'; inp.value=orig.value;
      inp.addEventListener('input', e=>{
        orig.value=e.target.value;
        orig.dispatchEvent(new Event('input'));
        let sv=clone.querySelector('.sb-val'), svOrig=row.querySelector('.sb-val');
        if(sv && svOrig) sv.textContent=svOrig.textContent;
      });
      p.appendChild(clone);
    });
    p.classList.add('show');
  } else {
    p.classList.remove('show');
  }
}

// === MOBILE TREE SELECTOR SYNC ===
function syncMobSel(){
  let orig=document.getElementById('tree-sel'), mob=document.getElementById('tree-sel-mob');
  if(!orig || !mob) return;
  mob.innerHTML=orig.innerHTML; mob.value=orig.value;
  orig.addEventListener('change', ()=>{ mob.value=orig.value; });
}
setTimeout(syncMobSel, 100);

// === MOBILE INITIAL ZOOM ===
if(window.innerWidth < 768){
  zm=0.45; center();
  clog('mobile detected: zoom='+zm.toFixed(2), 'log-state');
}

clog('v5.0: mobile module ready — pinch/zoom/pan/tune', 'log-state');

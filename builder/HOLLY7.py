#!/usr/bin/env python3
"""
HOLLY7.py — The Launcher
=========================
Compile with:
  pyinstaller --onefile --name HOLLY7 --console builder/HOLLY7.py

What it does:
  1. Builds pack/holly7.html  (full H7.1473.12.60.N pipeline)
  2. Finds nearest Chromium browser on this machine
  3. Opens the HTML in it
  4. Writes a git trace entry (BUILD_TRACE.log)

The .exe IS the pipeline.
No Python needed on target machine.
No browser flag needed — it finds one.
"""
import os, sys, re, time, shutil, hashlib, webbrowser, subprocess
from pathlib import Path

# -- ROOT detection (works both as .py and as PyInstaller .exe) -------------
if getattr(sys, 'frozen', False):
    # Running as compiled .exe inside builder/dist/
    # dist/ -> builder/ -> MNetv1/
    EXE_DIR = Path(sys.executable).parent.parent  # builder/
else:
    EXE_DIR = Path(__file__).parent               # builder/

ROOT   = EXE_DIR.parent                           # MNetv1/

# Force UTF-8 console (Windows cp1252 chokes on special chars)
import io
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass
KERNEL = ROOT / "kernel"
TREE   = ROOT / "tree"
PACK   = ROOT / "pack"
BUILDER = EXE_DIR

HEX_ARCHIVE = BUILDER / "hexCompTest"
HEX_ARCHIVE.mkdir(parents=True, exist_ok=True)

# -- VERSION ----------------------------------------------------------------
H7_MAJOR = 1473   # λ̃ = 0.1473  SAR-5 spectral invariant
H7_MINOR = 12     # P=12 pentagons — Euler forces it
H7_PATCH = 60     # C60 seed

existing  = sorted(HEX_ARCHIVE.glob("H7_*.html"))
H7_BUILD  = len(existing) + 1
VERSION   = f"H{H7_MAJOR}.{H7_MINOR}.{H7_PATCH}.{H7_BUILD}"
TIMESTAMP = time.strftime("%Y-%m-%d %H:%M:%S")
BUILD_NO  = f"HOLLY-7  {VERSION}"

OUT = PACK / "holly7.html"

# -- PRINT HEADER -----------------------------------------------------------
print("=" * 60)
print(f"  {BUILD_NO}")
print(f"  {TIMESTAMP}")
print(f"  ROOT: {ROOT}")
print("=" * 60)

# -- READ KERNEL MODULES ----------------------------------------------------
def read_js(name):
    p = KERNEL / name
    if not p.exists():
        print(f"  [WARN] missing: {p}")
        return f"// MISSING: {name}\n"
    src = p.read_text(encoding="utf-8")
    print(f"  M: {name:<30} {len(src)//1024}KB")
    return src

M1 = read_js("goldberg_kernel.js")
M2 = read_js("graph_axioms.js")
M3 = read_js("sar_modular.js")
M4 = read_js("ns_spectral.js")
M5 = read_js("fractal_search.js")

def read_tree_js():
    if not TREE.exists():
        return "// math_tree: tree/ not found\n"
    candidates = sorted(TREE.glob("math_tree_v*.html"))
    if not candidates:
        return "// math_tree: no html found\n"
    latest = candidates[-1]
    src = latest.read_text(encoding="utf-8")
    m = re.search(r'<script>(.*?)</script>', src, re.DOTALL)
    if m:
        print(f"  M: {latest.name:<30} {len(m.group(1))//1024}KB (tree)")
        return m.group(1)
    return "// math_tree: could not extract JS\n"

M7_JS = read_tree_js()

M6_JS = r"""
var NC = (function(){
  function ptKey(p){ return p[0].toFixed(3)+','+p[1].toFixed(3)+','+p[2].toFixed(3); }
  function buildAdj(faces){
    var nF=faces.length,adj=[];
    for(var i=0;i<nF;i++) adj.push([]);
    var edgeMap={};
    for(var i=0;i<nF;i++){
      var pts=faces[i].pts,n=pts.length;
      for(var k=0;k<n;k++){
        var a=ptKey(pts[k]),b=ptKey(pts[(k+1)%n]),rkey=b+'|'+a;
        if(edgeMap[rkey]!==undefined){
          var j=edgeMap[rkey];
          if(adj[i].indexOf(j)<0) adj[i].push(j);
          if(adj[j].indexOf(i)<0) adj[j].push(i);
        } else { edgeMap[a+'|'+b]=i; }
      }
    }
    return adj;
  }
  var REGIMES={
    stokes:{mix:0.95,decay:0.001,noise:0.0},
    laminar:{mix:0.60,decay:0.005,noise:0.0},
    transition:{mix:0.35,decay:0.010,noise:0.02},
    turbulent:{mix:0.15,decay:0.020,noise:0.05}
  };
  function run(faces,steps,regime){
    regime=regime||'laminar';
    var rp=REGIMES[regime],nF=faces.length,adj=buildAdj(faces);
    var p=new Float32Array(nF); p[0]=1.0;
    var mix=rp.mix,selfMix=1-rp.mix,decay=rp.decay,noise=rp.noise;
    var t0=performance.now();
    for(var s=0;s<steps;s++){
      var pNew=new Float32Array(nF);
      for(var i=0;i<nF;i++){
        var nb=adj[i],sum=0;
        for(var k=0;k<nb.length;k++) sum+=p[nb[k]];
        pNew[i]=selfMix*p[i]+mix*(nb.length>0?sum/nb.length:p[i]);
        if(noise>0) pNew[i]+=(Math.random()-0.5)*noise*pNew[i];
        pNew[i]*=(1-decay*0.01);
        if(pNew[i]<0) pNew[i]=0;
      }
      pNew[0]=1.0; p=pNew;
    }
    var elapsed=performance.now()-t0;
    var spread=0; for(var i=0;i<nF;i++) if(p[i]>0.001) spread++;
    return{elapsed_ms:+elapsed.toFixed(2),us_per_step:+(elapsed*1000/steps).toFixed(4),
      us_face_step:+(elapsed*1000/steps/nF).toFixed(6),spread:spread,nF:nF,steps:steps};
  }
  function benchmark(gkState,regime,maxLevel){
    maxLevel=maxLevel||3; regime=regime||'laminar';
    var results=[],state=gkState;
    for(var lvl=0;lvl<=maxLevel;lvl++){
      var inv=GK.invariants(state);
      var steps=Math.min(10000,Math.max(100,Math.floor(100000/inv.faces)));
      var r=run(state.faces,steps,regime);
      results.push({level:lvl,faces:inv.faces,pents:inv.pents,
        chi:inv.vertices-inv.edges+inv.faces,steps:r.steps,
        elapsed_ms:r.elapsed_ms,us_face_step:r.us_face_step,spread:r.spread});
      if(lvl<maxLevel) state=GK.refineAll(state);
    }
    return results;
  }
  return{run:run,benchmark:benchmark,buildAdj:buildAdj,REGIMES:REGIMES};
})();
"""
print(f"  M: navierCrunch_browser.js          (inline)")

# -- FULL HTML (same as build_holly7.py) ------------------------------------
# Import the full HTML generation from build_holly7.py if available,
# otherwise inline it here for the exe's self-contained operation.
build_script = BUILDER / "build_holly7.py"
if build_script.exists():
    # Execute the builder script directly — it handles everything
    print("\n  Running build_holly7.py pipeline...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_holly7", build_script)
    # We can't just import it (it runs on import), so use exec approach
    build_src = build_script.read_text(encoding="utf-8")
    # Patch sys.argv so it doesn't auto-open (we handle that below)
    _orig_argv = sys.argv[:]
    sys.argv = [str(build_script), "--no-open"]
    try:
        exec(compile(build_src, str(build_script), 'exec'), {"__file__": str(build_script)})
    except SystemExit:
        pass
    except Exception as e:
        print(f"  [WARN] build_holly7 exec: {e}")
    sys.argv = _orig_argv
else:
    print("  [WARN] build_holly7.py not found next to exe — using inline build")
    # Inline minimal build for standalone exe use
    OUT.parent.mkdir(parents=True, exist_ok=True)

# -- GIT TRACE --------------------------------------------------------------
# Public trace: who built it, when, from where, version.
# No secrets. No code. Just the coordinate in spacetime.
def git_hash():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL, cwd=ROOT
        ).decode().strip()
    except Exception:
        return "no-git"

def git_branch():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL, cwd=ROOT
        ).decode().strip()
    except Exception:
        return "unknown"

trace_entry = (
    f"{VERSION}  "
    f"{TIMESTAMP}  "
    f"git:{git_hash()}  "
    f"branch:{git_branch()}  "
    f"root:{ROOT}  "
    f"size:{OUT.stat().st_size if OUT.exists() else 0}B"
)

trace_file = ROOT / "BUILD_TRACE.log"
existing_trace = trace_file.read_text(encoding="utf-8") if trace_file.exists() else ""
trace_file.write_text(existing_trace + trace_entry + "\n", encoding="utf-8")
print(f"\n  [OK] Trace:  BUILD_TRACE.log  ({trace_entry[:60]}...)")

# -- FIND CHROMIUM BROWSER --------------------------------------------------
CHROMIUM_CANDIDATES = [
    # Brave (Vlad's likely default — seen in screenshots)
    Path(r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"),
    Path(os.environ.get("LOCALAPPDATA","")) / "BraveSoftware/Brave-Browser/Application/brave.exe",
    # Chrome
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(os.environ.get("LOCALAPPDATA","")) / "Google/Chrome/Application/chrome.exe",
    # Edge (always on Win11)
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    # Opera
    Path(os.environ.get("LOCALAPPDATA","")) / "Programs/Opera/opera.exe",
    Path(os.environ.get("LOCALAPPDATA","")) / "Programs/Opera GX/opera.exe",
    # Vivaldi
    Path(os.environ.get("LOCALAPPDATA","")) / "Vivaldi/Application/vivaldi.exe",
]

def find_browser():
    for p in CHROMIUM_CANDIDATES:
        try:
            if p.exists():
                return p
        except Exception:
            continue
    return None

browser = find_browser()
html_url = "file:///" + str(OUT).replace("\\", "/")

print(f"\n  HTML: {OUT}")
if browser:
    print(f"  Browser: {browser.name}")
    subprocess.Popen([str(browser), html_url])
    print(f"  [OK] Opened in {browser.name}")
else:
    print("  No Chromium browser found — using system default")
    webbrowser.open(html_url)

print(f"\n  {BUILD_NO}  DONE.")
print(f"  hexCompTest: {len(list(HEX_ARCHIVE.glob('H7_*.html')))} builds archived")
input("  Press ENTER to close...")

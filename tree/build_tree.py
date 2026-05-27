#!/usr/bin/env python3
"""
build_tree.py — Sacred Math Tree v5.0 builder
Assembles: data.js + engine.js + mobile.js → math_tree_v5.0.html
Same pattern as build_warning.py. Run from anywhere.
"""
from pathlib import Path

ROOT    = Path(__file__).parent
MODULES = ROOT / "modules"
OUT     = ROOT / "math_tree_v5.0.html"

print("Building Sacred Math Tree v5.0...")

data_js   = (MODULES / "data.js").read_text(encoding='utf-8')
engine_js = (MODULES / "engine.js").read_text(encoding='utf-8')
mobile_js = (MODULES / "mobile.js").read_text(encoding='utf-8')

print(f"  data.js   : {len(data_js)//1024}KB")
print(f"  engine.js : {len(engine_js)//1024}KB")
print(f"  mobile.js : {len(mobile_js)//1024}KB")

HTML_SHELL = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Sacred Math Tree v5.0</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"><\/script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0b0d14;color:#e8ecf4;font-family:ui-monospace,"SF Mono",Menlo,monospace;overflow:hidden;height:100vh;width:100vw}
#plane{position:absolute;transform-origin:0 0}
.eq{position:absolute;background:rgba(14,17,28,0.96);border:1px solid rgba(100,120,160,0.18);border-radius:6px;
  padding:14px 20px;min-width:140px;max-width:520px;pointer-events:none;
  transition:left 0.6s cubic-bezier(0.22,1,0.36,1),top 0.6s cubic-bezier(0.22,1,0.36,1),opacity 0.5s ease-out,transform 0.45s ease-out,border-color 0.3s,box-shadow 0.3s;
  opacity:0;transform:scale(0.3);transform-origin:50% 0%}
.eq.ghost{opacity:0.45;transform:scale(0.9);pointer-events:auto;border-style:dashed;cursor:pointer}
.eq.ghost:hover{opacity:0.65;box-shadow:0 0 20px rgba(100,120,160,0.1)}
.eq.alive{opacity:1;transform:scale(1);pointer-events:auto;cursor:default;border-style:solid}
.eq.t-root{border-color:rgba(255,200,60,0.4);background:rgba(18,16,10,0.96)}
.eq.t-root.alive:hover{border-color:rgba(255,215,80,0.6);box-shadow:0 0 30px rgba(255,200,60,0.12)}
.eq.t-tool{border-color:rgba(160,120,255,0.3);background:rgba(16,14,24,0.96)}
.eq.t-tool.alive:hover{border-color:rgba(180,140,255,0.5);box-shadow:0 0 20px rgba(160,120,255,0.1)}
.eq.t-result{border-color:rgba(80,220,140,0.3);background:rgba(10,18,14,0.96)}
.eq.t-result.alive:hover{border-color:rgba(100,240,160,0.5);box-shadow:0 0 20px rgba(80,220,140,0.1)}
.eq.t-dead{border-color:rgba(220,80,80,0.25);background:rgba(20,12,12,0.96)}
.eq .tok-badge{position:absolute;top:-10px;right:-10px;background:rgba(14,17,28,0.95);border:1px solid rgba(232,180,76,0.5);
  border-radius:10px;padding:2px 8px;font-size:10px;color:#e8b44c;font-weight:600;
  opacity:0;transform:scale(0.5);pointer-events:none;transition:opacity 0.2s,transform 0.2s}
.eq.ghost:hover .tok-badge{opacity:1;transform:scale(1)}
.eq .inner{opacity:0;transition:opacity 0.4s ease-in 0.15s}
.eq.alive .inner{opacity:1}
.eq .ghost-inner{opacity:0;transition:opacity 0.3s}
.eq.ghost .ghost-inner{opacity:1}
.eq .tag{font-size:9px;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;font-weight:600}
.eq .tag.gold{color:#e8b44c}.eq .tag.purp{color:#a78bfa}.eq .tag.grn{color:#6ee7a0}.eq .tag.red{color:#f87171}
.eq .ltx{color:#fff;margin:4px 0}.eq .ltx .katex{font-size:1.15em;color:#fff}
.eq .sub{font-size:10px;opacity:0.3;margin-top:8px;font-style:italic;color:#8899bb}
.eq .lock-icon{font-size:18px;opacity:0.4;margin:4px 0}
svg.lk{position:absolute;top:0;left:0;pointer-events:none}
svg.lk path{fill:none;stroke-width:1.8;stroke:rgba(100,120,160,0.0);stroke-dasharray:2000;stroke-dashoffset:2000;
  transition:stroke 0.4s ease-out,stroke-dashoffset 1s ease-out}
svg.lk path.ghost-line{stroke:rgba(100,120,160,0.06);stroke-dashoffset:0;stroke-dasharray:none}
svg.lk path.alive-line{stroke-dashoffset:0;stroke-dasharray:none}
@keyframes sparkle{0%{box-shadow:0 0 15px rgba(255,200,60,0.04)}50%{box-shadow:0 0 40px rgba(255,200,60,0.14),0 0 80px rgba(255,200,60,0.04)}100%{box-shadow:0 0 15px rgba(255,200,60,0.04)}}
.eq.t-root.alive{animation:sparkle 3s ease-in-out infinite}
@keyframes innerGlow{0%{box-shadow:0 0 0px rgba(180,160,255,0)}20%{box-shadow:0 0 40px rgba(180,160,255,0.2),inset 0 0 30px rgba(180,160,255,0.06)}100%{box-shadow:none}}
.eq.glow-flash{animation:innerGlow 0.6s ease-out}
#bar{position:fixed;bottom:0;left:0;right:0;z-index:10;background:rgba(5,5,16,0.95);border-top:1px solid #1a1f2e;
  padding:8px 14px;display:flex;align-items:center;gap:16px}
.b{background:#111;border:1px solid #2a2a2a;border-radius:3px;padding:4px 12px;font-family:inherit;font-size:10px;cursor:pointer;transition:all 0.15s}
.b:hover{border-color:#555;background:#1a1a1a}
.sl{color:rgba(220,228,240,0.35);font-size:8px;text-transform:uppercase;letter-spacing:0.12em}
#bar .sb-row{display:flex;align-items:center;gap:5px}
#bar .sb-label{color:#555;font-size:10px}
#bar input[type=range]{width:70px;accent-color:#ff69b4}
#bar .sb-val{color:#80d0ff;font-weight:bold;font-size:10px;min-width:26px}
#zoom-gate{position:fixed;top:0;left:0;width:100%;height:100%;z-index:100;display:flex;align-items:center;justify-content:center;flex-direction:column;
  background:rgba(8,10,16,0.88);pointer-events:none;opacity:0;transition:opacity 0.35s ease-out}
#zoom-gate.show{opacity:1;pointer-events:auto}
#zoom-gate .zg-msg{font-family:Papyrus,fantasy;font-size:42px;color:#f87171;text-align:center;line-height:1.4;text-shadow:0 0 40px rgba(248,113,113,0.15);padding:0 40px;font-weight:bold}
#zoom-gate .zg-sub{font-family:Papyrus,fantasy;font-size:18px;color:#8899bb;margin-top:12px;text-align:center}
#zoom-gate .zg-zoom{font-family:ui-monospace,monospace;font-size:12px;color:#e8b44c;margin-top:18px;opacity:0.5}
#ghud{position:fixed;top:12px;right:12px;z-index:30;display:flex;gap:12px;align-items:center;font-size:9px;opacity:0.6}
.gem{display:flex;align-items:center;gap:5px}.gem .ct{color:#ffd700;font-weight:bold;font-size:11px}
.tp{position:fixed;pointer-events:none;z-index:40;font-size:11px;font-weight:600;color:#e8b44c;animation:tf 1.2s ease-out forwards}
@keyframes tf{0%{opacity:1;transform:translateY(0)}100%{opacity:0;transform:translateY(-80px)}}
#combo{position:fixed;top:50px;left:50%;transform:translateX(-50%);z-index:25;font-size:22px;font-weight:bold;opacity:0;transition:opacity 0.3s;text-shadow:0 0 20px rgba(255,200,60,0.3)}
#hud{position:fixed;top:12px;left:12px;z-index:20;pointer-events:none;font-size:11px}
#hud .row{line-height:1.7}
.lbl{color:#555}.val{color:#80d0ff;font-weight:bold}
#logp{position:fixed;top:180px;left:12px;z-index:10;background:rgba(5,5,16,0.85);border:1px solid #1a1f2e;border-radius:4px;
  padding:6px 10px;max-width:280px;max-height:220px;overflow-y:auto;font-size:9px;line-height:1.5;
  color:rgba(180,200,255,0.7);opacity:0.35;transition:opacity 0.3s}
#logp:hover{opacity:0.92}
#logp .log-click{color:#ffd700}
#logp .log-tok{color:#a78bfa}
#logp .log-xp{color:#7fff7f}
#logp .log-state{color:#555}
#logp .log-err{color:#ff4444}
#logp.hidden{display:none}
#ver{position:fixed;bottom:48px;right:8px;font-size:8px;color:#222;z-index:1;pointer-events:none}
#grid-cv{position:absolute;top:0;left:0;pointer-events:none;z-index:0}
svg.lk{z-index:1}.eq{z-index:2}
/* MOBILE */
@media(max-width:768px){
  #hud{display:none}
  #ghud{top:auto;bottom:44px;right:8px;z-index:12;font-size:9px;gap:6px;background:rgba(5,5,16,0.85);padding:3px 8px;border-radius:4px;border:1px solid #1a1f2e}
  #tune-panel{display:none;position:fixed;bottom:44px;left:0;right:0;z-index:15;background:rgba(5,5,16,0.96);border-top:1px solid #1a1f2e;padding:12px 16px;max-height:60vh;overflow-y:auto}
  #tune-panel.show{display:block}
  #tune-panel .sb-row{display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.03)}
  #tune-panel .sb-label{color:#555;font-size:11px;min-width:55px}
  #tune-panel input[type=range]{flex:1;accent-color:#ff69b4}
  #tune-panel .sb-val{color:#80d0ff;font-weight:bold;font-size:11px;min-width:30px;text-align:right}
  #bar{padding:0;gap:0;flex-wrap:nowrap;justify-content:stretch;height:42px}
  #bar .sb-row{display:none !important}
  #bar .mob-bar{display:flex !important;width:100%;align-items:center;justify-content:center;gap:6px;padding:0 8px}
  .mob-btn{background:rgba(20,20,30,0.9);border:1px solid #2a2a3a;border-radius:4px;padding:6px 10px;font-family:inherit;font-size:10px;cursor:pointer;color:#80d0ff;transition:all 0.15s;white-space:nowrap}
  .mob-btn.gold{color:#ffd700;border-color:#332a00}
  .mob-btn.green{color:#7fff7f;border-color:#003300}
  .mob-sel{background:#111;color:#80d0ff;border:1px solid #2a2a3a;border-radius:4px;padding:5px 6px;font-family:inherit;font-size:10px;cursor:pointer;flex:1;max-width:140px}
  #logp{top:auto;bottom:44px;left:0;right:0;max-width:none;max-height:40vh;border-radius:0;font-size:9px;border:none;border-top:1px solid #1a1f2e;opacity:0.95}
  .eq{padding:10px 14px;min-width:110px;max-width:300px}
  #zoom-gate .zg-msg{font-size:28px;padding:0 20px}
  #mob-hint{display:block !important}
}
#tune-panel{display:none}
.mob-bar{display:none !important}
#mob-hint{display:none}
</style>
</head>
<body>

<div id="ghud">
  <div class="gem">&#9670;<span class="ct" id="g-tok">3</span></div>
  <div style="color:#a78bfa;font-size:12px">XP <span id="g-xp">0</span></div>
  <div style="color:#f97316;font-size:12px">&#128293;<span id="g-str">0</span></div>
</div>
<div id="combo"></div>
<div id="hud">
  <div class="row"><span class="lbl">nodes </span><span class="val" id="h-n">0</span></div>
  <div class="row"><span class="lbl">depth </span><span class="val" id="h-d">0</span></div>
  <div class="row"><span class="lbl">zoom  </span><span class="val" id="h-zm">60%</span></div>
  <div class="row"><span class="lbl">wave  </span><span class="val" id="h-wv">0.50</span></div>
  <div class="row"><span class="lbl">spread</span><span class="val" id="h-sp">1.0x</span></div>
  <div class="row"><span class="lbl">dy    </span><span class="val" id="h-dy">320</span></div>
  <div class="row"><span class="lbl">lock  </span><span class="val" id="h-lk">off</span></div>
  <div class="row"><span class="lbl">shame </span><span class="val" id="h-sh">2.0s</span></div>
</div>
<div id="ver">v5.0</div>
<div id="zoom-gate">
  <div class="zg-msg">zoom in, wanderer</div>
  <div class="zg-sub">read the equation before you touch it</div>
  <div class="zg-zoom">you: <span id="zg-cur">35%</span> &middot; need: <span id="zg-need">50%</span></div>
</div>
<div id="mob-hint" style="display:none;position:fixed;bottom:44px;left:0;right:0;text-align:center;
  font-size:9px;color:rgba(128,208,255,0.3);letter-spacing:0.15em;text-transform:uppercase;padding:4px;z-index:5;pointer-events:none">
  tap autopilot &middot; pinch to zoom &middot; drag to pan</div>
<div id="tune-panel"></div>
<div id="bar">
  <span class="sl">tree</span>
  <div class="sb-row"><span class="sb-label">wave</span><input type="range" id="sl-wave" min="0" max="100" value="50"><span class="sb-val" id="sv-wave">50</span></div>
  <div class="sb-row"><span class="sb-label">spread</span><input type="range" id="sl-spread" min="10" max="100" value="50"><span class="sb-val" id="sv-spread">50</span></div>
  <div class="sb-row"><span class="sb-label">depth</span><input type="range" id="sl-depth" min="10" max="100" value="50"><span class="sb-val" id="sv-depth">50</span></div>
  <div class="sb-row"><span class="sb-label">lock</span><input type="range" id="sl-zlock" min="0" max="100" value="0"><span class="sb-val" id="sv-zlock">off</span></div>
  <div class="sb-row"><span class="sb-label">shame</span><input type="range" id="sl-shame" min="5" max="100" value="20"><span class="sb-val" id="sv-shame">2s</span></div>
  <div class="sb-row" style="margin-left:8px;border-left:1px solid #1a1f2e;padding-left:8px;gap:3px;flex-wrap:wrap">
    <span class="sb-label" style="width:auto">tree</span>
    <select id="tree-sel" style="background:#111;color:#80d0ff;border:1px solid #2a2a2a;border-radius:3px;padding:3px 6px;font-family:inherit;font-size:9px;cursor:pointer">
      <option value="sinx">1. lim sin(x)/x</option>
      <option value="euler_e">2. lim (1+1/n)^n</option>
      <option value="power_rule">3. d/dx x^n</option>
      <option value="dsin">4. d/dx sin(x)</option>
      <option value="chain">5. chain rule</option>
      <option value="int_power">6. integral x^n</option>
      <option value="improper">7. improper integral</option>
      <option value="taylor_ex">8. Taylor e^x</option>
      <option value="ftc">9. Fund. Thm. Calculus</option>
      <option value="eps_delta">10. epsilon-delta</option>
    </select>
  </div>
  <div class="sb-row" style="margin-left:12px;border-left:1px solid #1a1f2e;padding-left:12px">
    <button id="btn-auto" class="b" style="color:#ffd700;border-color:#332a00">&#9654; autopilot</button>
    <span class="sb-val" id="sv-auto" style="color:#ffd700">ready</span>
    <button id="btn-fullauto" class="b" style="color:#7fff7f;border-color:#003300">&#9654;&#9654; all trees</button>
    <span class="sb-val" id="sv-fullauto" style="color:#7fff7f">10</span>
    <button id="btn-log" class="b" style="color:#333;border-color:#1a2a3a" onclick="toggleLog()">&#9776; log</button>
  </div>
  <div class="mob-bar">
    <button class="mob-btn" onclick="toggleTune()">TUNE</button>
    <select class="mob-sel" id="tree-sel-mob" onchange="document.getElementById('tree-sel').value=this.value;document.getElementById('tree-sel').dispatchEvent(new Event('change'))"></select>
    <button class="mob-btn gold" onclick="document.getElementById('btn-auto').click()">&#9654; AUTO</button>
    <button class="mob-btn green" onclick="document.getElementById('btn-fullauto').click()">&#9654;&#9654; ALL</button>
    <button class="mob-btn" onclick="toggleLog()">LOG</button>
  </div>
</div>
<div id="logp" class="hidden"></div>
<div id="plane"><canvas id="grid-cv"></canvas><svg class="lk" id="lksvg"></svg></div>

<script>
// === DATA ===
DATA_JS_PLACEHOLDER

// === ENGINE ===
ENGINE_JS_PLACEHOLDER

// === MOBILE ===
MOBILE_JS_PLACEHOLDER
</script>
</body>
</html>'''

html = HTML_SHELL\
    .replace('DATA_JS_PLACEHOLDER',   data_js)\
    .replace('ENGINE_JS_PLACEHOLDER', engine_js)\
    .replace('MOBILE_JS_PLACEHOLDER', mobile_js)

OUT.write_text(html, encoding='utf-8')
print(f"Written: {OUT} ({len(html)//1024} KB)")
print("  data + engine + mobile assembled.")
print("  KaTeX: CDN (black magic stays for now).")
print("  Next: python build_tree.py → math_tree_v5.0.html → push → done.")

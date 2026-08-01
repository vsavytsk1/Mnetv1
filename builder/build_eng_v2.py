#!/usr/bin/env python3
"""
build_eng_v2.py  —  ENG v2.0  MASTER CONTROL DASHBOARD
=======================================================
Tony Stark lab layout:
  TOP BAR   — build stamp · live clock · git hash
  LEFT COL  — kernel status (6 modules, live) + mini C60 canvas
  CENTER    — module cards (click = summon inline)
  RIGHT COL — build log + LEDGER last 5 entries
  BOTTOM    — command bar (sandbox format, exact)
  OVERLAY   — iframe fills screen when module summoned, ← BACK returns
"""
import re, time, subprocess
from pathlib import Path

ROOT      = Path(__file__).parent.parent
KERNEL    = ROOT / "kernel"
SHELL     = ROOT / "shell"
VERSION   = "v2.0"
OUT       = SHELL / f"eng_{VERSION}.html"
TIMESTAMP = time.strftime("%Y-%m-%d %H:%M:%S")

try:
    GIT = subprocess.check_output(["git","rev-parse","--short","HEAD"],
          stderr=subprocess.DEVNULL, cwd=ROOT).decode().strip()
except: GIT = "local"

print(f"Building eng_{VERSION}.html — MASTER CONTROL DASHBOARD")

def read_js(name):
    p = KERNEL / name
    if not p.exists(): print(f"  [WARN] {name}"); return f"// MISSING: {name}\n"
    js = p.read_text(encoding="utf-8")
    print(f"  M: {name:<30} {len(js)//1024}KB")
    return js

M1 = read_js("goldberg_kernel.js")
M2 = read_js("graph_axioms.js")
M3 = read_js("sar_modular.js")
M4 = read_js("ns_spectral.js")
M5 = read_js("fractal_search.js")
M6 = read_js("mnet_nanite.js")

# Read last 5 LEDGER entries
ledger_lines = []
lp = ROOT / "LEDGER.md"
if lp.exists():
    raw = lp.read_bytes().decode('utf-8', errors='ignore')
    entries = [l.strip() for l in raw.split("\n") if l.startswith("### L")]
    ledger_lines = entries[-5:]

LEDGER_HTML = "".join(
    f'<div class="log-entry"><span class="op">{e.split("·")[0].strip()}</span> '
    f'<span class="g">{("·".join(e.split("·")[1:])).strip()}</span></div>'
    for e in ledger_lines
)

# Module cards: AUTO-DISCOVERED from disk (sim_scan). The builder is absolute --
# the master control DISCOVERS every sim on the io pages (KEEP IT ALL: every version,
# matching the archive) so it can never drift from what is shipped. Add a sim -> it appears.
import sim_scan
SIMS  = sim_scan.discover()             # ALL versions -- the archive truth (for LINKS)
CARDS = sim_scan.latest_only(SIMS)      # newest per family -- the DASHBOARD view (pretty cards)
print(f"  scanned {len(SIMS)} sims (archive) -> {len(CARDS)} shown on dashboard (latest per family)")

# Group the DASHBOARD cards by category tag, rendered per group with a header.
from collections import OrderedDict
GROUPS = OrderedDict()
for s in CARDS:
    GROUPS.setdefault(s["tag"], []).append(s)

def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def caps_html(caps):
    return "".join(f'<span class="cap {c}">{c.upper()}</span>' for c in caps)

def card_html(s, featured=False, birth=False):
    cls = "mod-card feat-card" if featured else "mod-card"
    if birth:
        cls += " birth-card"
    return f"""
  <div class="{cls}" id="card-{s['key']}" data-tag="{esc(s['tag'])}" onclick="summon('{s['key']}')"
    style="border-color:{s['border']};--card-color:{s['color']}">
    <div class="card-dot"></div>
    <div class="card-tag" style="color:{s['color']}">{esc(s['tag'])}</div>
    <div class="card-name" style="color:{s['color']}">{esc(s['name'])}</div>
    <div class="card-desc">{esc(s['desc'])}</div>
    <div class="card-arrow" style="color:{s['color']}">SUMMON &#9654;</div>
    <div class="card-caps">{caps_html(s.get('caps', []))}</div>
  </div>"""

# THE FRONT DOOR (MONKIUM order): SEVEN pinned cards, in this order --
#   1. THE WARNING       -- the terror opener, the price of compute
#   2. GENESIS v8.1      -- the fractal space explorer (the buckyball you fly INTO)
#   3. CHROMODYNAMIUM    -- the Standard Model force (SU(3)) in its spini-spini form
#   4. AEQUALIUM         -- the equals sign earned; Fourier in the C60 (a core focus)
#   5. PCBIUM            -- the PCB design space on the buckyball (a core focus)
#   6. ARACNIUM v1.4     -- the spider, latest (EXTERNAL: SpiderEngineering repo)
#   7. HELENI STATUS     -- the Eleni/HELENA readme (EXTERNAL .md, opens in a new tab)
# Cards 1-5 resolve against the local scan; 6-7 are explicit cross-repo pins in
# FEATURED_EXTERNAL (URLs live-checked 200 before pinning -- a card must never 404).
# Each local entry: (match, label, blurb). `match` can be an exact key-pin (searched
# across ALL versions in SIMS, e.g. genesis_v8_1 not the family-latest v9.0) or a
# family keyword (resolved to the latest card). Explicit pins win so it never drifts.
# THE BIRTH -- the centerpiece, alone, above the front door. Its own section, its
# own contrast (a golden "birth" card): the source code of it all, computed live.
BIRTH = ("light_matrix", "THE LIGHT MATRIX",
    "the source code of it all, computed LIVE in your browser -- a Nature-style living paper you CLICK through, born from ONE forced number. Euler forces P=12; one 4x4 integer matrix (eigenvalues phi^2, 1, -1, phi^-2) governs the whole family; the C60 adjacency graph is built and diagonalized on the fly to land lambda_min = -phi^2. pure graph theory, zero deps, to the chromium compute limit. 4.2 billion years ago the first self-assembly cell paid the price to read this. now you may too. THE CENTERPIECE.")

FEATURED_FAMILIES = [
    ("warning",         "THE WARNING",    "the front door -- the explosion, the fractal cascade, the price of compute. enter here."),
    ("genesis_v8_5",    "GENESIS v8.5",   "the fractal space explorer -- HEAR THE NET, now on the BIG shells. THE GOLDEN CATALOGUE: seed the next 7 buckyballs C20->C60->C140->C380->C980->C2580->C6740 (Goldberg-Coxeter, Thea Lane B -- each kernel-CERTIFIED V=20T E=30T P=12 chi=2, all-trivalent, C6740 live). FLIGHT EXPLORER centers any point on click. hit LIGHT: the net sinks to BACKGROUND (still fully computed -- the price is paid -- just invisible) so you see ONLY the light FLOWING along the edges, brightness = the modal current |va-vb|, tempo = sqrt(lambda_2) (C20 = 3-sqrt5 = 2/phi^2, kernel-verified: the honest sound of the net). the light is aesthetic over the point-and-line substrate. perfect-math block: the graph wave u''=-c^2 L u conserves energy to 1e-15 (leapfrog). M1-M6 kernel live."),
    ("kibotos_metalatexium", "KIBOTOS -- THE HUNDRED-YEAR BOX (v1.2 welded)", "please stop boiling water, bro. a two-mage engineering scroll (Fable + Sol, kernel-audited, Path X -- every rung frozen): a sealed 100W-for-a-century socket, no moving parts. the isotope ledger (chemistry excluded by 10^3; Ni-63 half-life = 101 years = the warranty); the phi^2-chirped mirror WELDED into the photon-recycling slot -- controls show NO mirror 0.095 -> bare metal 0.83 -> THE WELD 0.94, and Sol's assumed 0.30 efficiency is now DERIVED inside the band. golden trace recursion x_{n+1}=2x_n x_{n-1}-x_{n-2}, invariant to 50+ digits. free_energy REJECTED; the device is a HYPOTHESIS. reproducible SHA-256 certificate (hash the math, not the moment -- Curse 38). a core focus."),
    ("chromodynamium",  "CHROMODYNAMIUM", "the Standard Model's strong force, spini-spini: SU(3), the 8 gluon roots, colour factors C_F=4/3 C_A=3, the running coupling -- all computed live."),
    ("aequalium",       "AEQUALIUM",      "the equals sign, EARNED: a pure-Fourier curve trapped in the C60. grow / WELD the fullerene shell (C60->C240->C960 closed, chi=2 ENUMERATED not formula), buy harmonics, watch the residual fall. the Standard Modelium tower reads how many DIGITS of agreement each real physics '=' can buy, with a portable SHA-256 certificate + an independent verifier. a core focus."),
    ("pcbium",          "PCBIUM",         "the PCB design space -- CAD navigation on the buckyball, nanite routing, the board grown from the kernel. a core focus."),
]
# External cards live in OTHER repos on the same github.io host, so they are NOT in
# the local scan. Each is an explicit (key, name, tag, color, border, url, blurb, caps).
# We verified all four URLs return 200 before pinning them (a card must never 404).
FEATURED_EXTERNAL = [
    dict(key="ext_aracnium_v1_4_heave", name="ARACNIUM v1.4 -- THE HEAVE", tag="SPIDER",
         color="#88ff88", border="#1a3a1a",
         url="https://vsavytsk1.github.io/SpiderEngineering/aracnium/sim/aracnium_v1_4_heave.html",
         caps=["frm", "pc", "kbd"],
         desc="the spider, latest: a swarm of full-math robot spiders -- CPG gait, 2-link IK to planted feet, honest F=ma + Coulomb friction -- heave a real tungsten cube. the locomotion digital twin, live from the SpiderEngineering repo. a core focus."),
    dict(key="ext_heleni_status", name="HELENI -- STATUS", tag="ELENI",
         color="#ff9ecb", border="#3a1a2a",
         url="https://vsavytsk1.github.io/Mnetv1/HELENI_STATUS.md",
         caps=["doc"],
         desc="the current status of Eleni / HELENA -- the Genesis-LLM circle built from 1 Corinthians 13 in the tongues of humanity, gate weight 0.700, the center held and never shown. a detailed readme reconciling every heleni across MNetv1 + SpiderEngineering."),
]
FEATURED = []
_feat_keys = set()
for fam_kw, _lbl, _blurb in FEATURED_FAMILIES:
    # Resolve in order of precision so a keyword never grabs the wrong sim:
    #   1) EXACT family match on a card (warning -> the real WarningSim, not
    #      ref_spookywarning_-_the_gate); 2) exact key-substring across ALL versions
    #      in SIMS (lets us pin genesis_v8_1 even though the family-latest is v9.0);
    #   3) family startswith; 4) any substring.
    hit = (next((s for s in CARDS if s["family"] == fam_kw), None)
           or next((s for s in SIMS if fam_kw in s["key"]), None)
           or next((s for s in CARDS if s["family"].startswith(fam_kw)), None)
           or next((s for s in CARDS if fam_kw in s["family"] or fam_kw in s["key"]), None))
    if hit and hit["key"] not in _feat_keys:
        FEATURED.append((hit, _blurb)); _feat_keys.add(hit["key"])

# Resolve THE BIRTH card (the centerpiece, shown alone above the front door).
_birth_kw, _birth_lbl, _birth_blurb = BIRTH
BIRTH_HIT = (next((s for s in CARDS if _birth_kw in s["key"]), None)
             or next((s for s in SIMS if _birth_kw in s["key"]), None))
if BIRTH_HIT:
    _feat_keys.add(BIRTH_HIT["key"])   # never show it twice

CARDS_HTML = ""
if BIRTH_HIT:
    CARDS_HTML += '\n  <div class="cat-header birth-header">THEA HELENI SOURCE CODE <span class="cat-count">the birth &#183; the whole light</span></div>'
    b = dict(BIRTH_HIT); b["name"] = _birth_lbl; b["desc"] = _birth_blurb
    b["tag"] = "\u2600 THE BIRTH"        # the golden corner marker (big title = THE LIGHT MATRIX)
    CARDS_HTML += card_html(b, featured=True, birth=True)
if FEATURED or FEATURED_EXTERNAL:
    CARDS_HTML += '\n  <div class="cat-header feat-header">FRONT DOOR <span class="cat-count">enter here</span></div>'
    for s, blurb in FEATURED:
        s2 = dict(s); s2["desc"] = blurb   # a custom front-door blurb
        CARDS_HTML += card_html(s2, featured=True)
    for s in FEATURED_EXTERNAL:            # cross-repo pins (explicit url, live-checked)
        CARDS_HTML += card_html(s, featured=True)
for tag in sorted(GROUPS):
    grp = sorted(GROUPS[tag], key=lambda x: x["key"])
    CARDS_HTML += f'\n  <div class="cat-header">{esc(tag)} <span class="cat-count">{len(grp)}</span></div>'
    for s in grp:
        # skip the featured ones here so they aren't shown twice
        if s["key"] in _feat_keys:
            continue
        CARDS_HTML += card_html(s)

# The key -> url map for summon(), also auto-built from the same scan (no drift).
# External featured pins are appended so summon() can resolve them too.
LINKS_JS = "".join(f"  {s['key']}:'{s['url']}',\n" for s in SIMS)
LINKS_JS += "".join(f"  {s['key']}:'{s['url']}',\n" for s in FEATURED_EXTERNAL)

# The "select your sims" dropdown -- one toggle row per dashboard card, category-grouped,
# ALL ON by default. Auto-populated from the same scan so it can never drift.
SELECTOR_HTML = ""
for tag in sorted(GROUPS):
    grp = sorted(GROUPS[tag], key=lambda x: x["key"])
    SELECTOR_HTML += f'\n  <div class="ms-cat">{esc(tag)}</div>'
    for s in grp:
        SELECTOR_HTML += (
            f'\n  <div class="ms-row" onclick="toggleMod(\'{s["key"]}\')">'
            f'<span class="ms-name">{esc(s["name"])}</span>'
            f'<span class="ms-dot on" id="ms-{s["key"]}" style="--card-color:{s["color"]}"></span></div>'
        )
# JS array of all dashboard keys (for modApply / all-on default).
ALL_KEYS_JS = "[" + ",".join(f"'{s['key']}'" for s in CARDS) + "]"

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MachineNet · ENG {VERSION} · MASTER CONTROL</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --bg:     #030308;
  --panel:  #07070f;
  --border: #0e0e1e;
  --text:   #9090a0;
  --bright: #d0d8e8;
  --cyan:   #00d4ff;
  --gold:   #ffd700;
  --pink:   #ff69b4;
  --green:  #00ffd5;
  --purple: #a78bfa;
  --orange: #ff9040;
}}
body{{background:var(--bg);color:var(--text);
     font-family:ui-monospace,"SF Mono","Fira Code",monospace;
     font-size:11px;overflow:hidden;height:100vh;display:flex;flex-direction:column}}

/* ── TOP BAR ── */
#top-bar{{
  background:var(--panel);border-bottom:1px solid var(--border);
  padding:0 16px;height:36px;display:flex;align-items:center;gap:16px;
  flex-shrink:0;z-index:10
}}
#top-bar .logo{{color:var(--cyan);font-size:12px;letter-spacing:0.12em;font-weight:bold}}
#top-bar .build{{color:#2a3a4a;font-size:10px}}
#top-bar .git{{color:#1a2a1a;font-size:10px}}
#top-bar .clock{{margin-left:auto;color:#1a2a3a;font-size:10px;font-variant-numeric:tabular-nums}}
#top-bar .k-ok{{color:var(--green);font-size:10px}}
#top-bar .k-bad{{color:#ff4444;font-size:10px}}

/* ── MAIN GRID ── */
#main{{display:flex;flex:1;overflow:hidden;gap:0}}

/* ── LEFT PANEL ── */
#left{{
  width:180px;flex-shrink:0;
  background:var(--panel);border-right:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden
}}
.panel-title{{
  color:#1a2a3a;font-size:9px;letter-spacing:0.2em;text-transform:uppercase;
  padding:8px 12px 4px;border-bottom:1px solid var(--border)
}}
#k-list{{padding:8px 12px;flex-shrink:0}}
.k-row{{display:flex;justify-content:space-between;align-items:center;
  padding:3px 0;border-bottom:1px solid #0a0a14}}
.k-name{{color:#2a3a4a;font-size:10px;letter-spacing:0.05em}}
.k-ok{{color:var(--green);font-size:10px}}
.k-miss{{color:#ff4444;font-size:10px}}
.k-kb{{color:#1a2a2a;font-size:9px}}
#mini-canvas-wrap{{flex:1;position:relative;overflow:hidden;border-top:1px solid var(--border)}}
#mini-canvas-wrap .panel-title{{position:absolute;top:0;left:0;right:0;z-index:2;background:var(--panel)}}
#cv-mini{{position:absolute;top:22px;left:0;width:100%;height:calc(100% - 22px);display:block}}

/* ── CENTER ── */
#center{{
  flex:1;overflow-y:auto;padding:16px;
  display:flex;flex-direction:column;gap:12px
}}
#center-top{{
  color:#1a2a3a;font-size:9px;letter-spacing:0.15em;margin-bottom:4px
}}
.mod-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}}
.cat-header{{grid-column:1/-1;color:#3a4a5a;font-size:10px;letter-spacing:0.25em;
  text-transform:uppercase;margin:14px 0 2px;padding-bottom:4px;
  border-bottom:1px solid #10101e;display:flex;align-items:center;gap:8px}}
.cat-header:first-child{{margin-top:0}}
.cat-count{{color:#1a2a3a;font-size:9px;background:#0a0a14;border-radius:8px;
  padding:1px 7px}}
/* the FRONT DOOR: warning sim + genesis, pinned first, bigger and glowing */
.cat-header.feat-header{{color:var(--gold)}}
.cat-header.feat-header .cat-count{{color:var(--gold);background:#1a1408}}
.feat-card{{grid-column:span 1;padding:16px 18px 22px;
  background:linear-gradient(160deg,#0c0c16,var(--panel));
  border-width:1px;box-shadow:0 0 22px -10px var(--card-color,#00d4ff)}}
.feat-card .card-name{{font-size:14px}}
.feat-card .card-desc{{color:#4a5a6a;font-size:9.5px}}
.feat-card::after{{content:'FRONT DOOR';position:absolute;top:8px;left:10px;
  font-size:6.5px;letter-spacing:0.2em;color:var(--card-color,#ffd700);opacity:0.5}}
/* THE BIRTH -- the centerpiece, alone, full width, golden, breathing (contrast) */
.cat-header.birth-header{{color:#ffd700;letter-spacing:0.32em;font-size:11px;
  border-bottom:1px solid #2a2008}}
.cat-header.birth-header .cat-count{{color:#ffd700;background:#1a1408;letter-spacing:0.08em}}
.birth-card{{grid-column:1/-1;padding:22px 24px 26px;border-color:#ffd700 !important;
  --card-color:#ffd700;
  background:radial-gradient(ellipse at 22% 30%,rgba(255,215,0,0.14) 0%,transparent 60%),linear-gradient(160deg,#12100a,#0a0a12);
  box-shadow:0 0 46px -14px #ffd700, inset 0 0 60px -40px #ffd700;
  animation:birthGlow 5.5s ease-in-out infinite}}
@keyframes birthGlow{{0%,100%{{box-shadow:0 0 40px -16px #ffd700,inset 0 0 60px -42px #ffd700}}
  50%{{box-shadow:0 0 66px -10px #ffd700,inset 0 0 70px -34px #ffd700}}}}
.birth-card .card-name{{font-size:18px;letter-spacing:0.04em}}
.birth-card .card-desc{{color:#8a7a4a;font-size:10.5px;max-width:80ch}}
.birth-card .card-arrow{{font-size:12px}}
.birth-card .card-tag{{color:#ffd700;opacity:0.85;font-size:9px}}
.mod-card{{
  background:var(--panel);border:1px solid #0e0e1e;border-radius:4px;
  padding:12px 14px 18px;cursor:pointer;transition:all 0.2s;position:relative;
  overflow:hidden
}}
.mod-card::before{{
  content:'';position:absolute;inset:0;opacity:0;
  background:radial-gradient(ellipse at 30% 30%, var(--card-color,#00d4ff) 0%, transparent 70%);
  transition:opacity 0.3s
}}
.mod-card:hover::before{{opacity:0.05}}
.mod-card:hover{{border-color:var(--card-color,#00d4ff);transform:translateY(-1px);
  box-shadow:0 0 16px -6px var(--card-color,#00d4ff)}}
/* the icon: a glowing status dot in the card's accent colour */
.card-dot{{position:absolute;top:8px;right:8px;width:7px;height:7px;border-radius:50%;
  background:var(--card-color,#00d4ff);opacity:0.55;
  box-shadow:0 0 6px var(--card-color,#00d4ff);transition:opacity 0.2s}}
.mod-card:hover .card-dot{{opacity:1}}
.card-tag{{font-size:8px;letter-spacing:0.2em;margin-bottom:4px;opacity:0.7}}
.card-name{{font-size:12px;font-weight:bold;margin-bottom:6px;letter-spacing:0.02em}}
.card-desc{{color:#2a3a4a;font-size:9px;line-height:1.55;margin-bottom:8px}}
.card-arrow{{font-size:9px;letter-spacing:0.12em;opacity:0;transition:opacity 0.15s}}
.mod-card:hover .card-arrow{{opacity:1}}
/* capability chips, bottom-right, auto-detected from the sim */
.card-caps{{position:absolute;bottom:5px;right:6px;display:flex;gap:3px;
  flex-direction:row-reverse;flex-wrap:wrap;max-width:64%;justify-content:flex-start}}
.card-caps .cap{{font-size:7px;letter-spacing:0.1em;font-family:ui-monospace,monospace;
  padding:1px 4px;border-radius:2px;opacity:0.6;border:1px solid transparent;line-height:1.2}}
.mod-card:hover .card-caps .cap{{opacity:0.95}}
.cap.tab{{color:#ff9040;border-color:rgba(255,144,64,0.2)}}
.cap.frm{{color:#80d0ff;border-color:rgba(128,208,255,0.2)}}
.cap.pc{{color:#7fff7f;border-color:rgba(127,255,127,0.2)}}
.cap.and{{color:#a4c639;border-color:rgba(164,198,57,0.2)}}
.cap.ios{{color:#c8c8c8;border-color:rgba(200,200,200,0.2)}}
.cap.gpu{{color:#ff69b4;border-color:rgba(255,105,180,0.2)}}
.cap.kbd{{color:#ffd700;border-color:rgba(255,215,0,0.2)}}
.cap.priv{{color:#888;border-color:rgba(136,136,136,0.2)}}
.cap.doc{{color:#ff9ecb;border-color:rgba(255,158,203,0.25)}}
/* dimmed card when toggled off in the selector */
.mod-card.mod-off{{opacity:0.16;filter:grayscale(0.8);pointer-events:none}}
/* the SELECT YOUR SIMS dropdown */
#btn-modules #mod-count{{color:var(--green);font-size:9px}}
#mod-selector{{position:fixed;right:12px;bottom:44px;width:250px;max-height:60vh;
  background:#06060e;border:1px solid #1a1a2e;border-radius:6px;z-index:60;
  box-shadow:0 8px 40px rgba(0,0,0,0.7);display:none;flex-direction:column;overflow:hidden}}
#mod-selector.open{{display:flex}}
#mod-selector .ms-head{{font-size:10px;letter-spacing:0.18em;color:#3a4a5a;
  padding:9px 12px;border-bottom:1px solid #12121e;display:flex;justify-content:space-between;
  align-items:center;flex-shrink:0}}
#mod-selector #ms-allbtn{{color:var(--cyan);font-size:9px;cursor:pointer;
  border:1px solid #12303a;border-radius:3px;padding:1px 7px}}
#mod-selector #ms-allbtn:hover{{border-color:var(--cyan)}}
#mod-selector .ms-body{{overflow-y:auto;padding:4px 0}}
.ms-cat{{font-size:8px;letter-spacing:0.2em;color:#2a3a4a;padding:6px 12px 2px}}
.ms-row{{display:flex;justify-content:space-between;align-items:center;
  padding:3px 12px;cursor:pointer;font-size:10px}}
.ms-row:hover{{background:#0c0c16}}
.ms-name{{color:#6a7a8a;letter-spacing:0.03em;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis;max-width:190px}}
.ms-dot{{width:7px;height:7px;border-radius:50%;background:#1a1a26;flex-shrink:0;
  transition:all 0.15s}}
.ms-dot.on{{background:var(--card-color,#00ffd5);box-shadow:0 0 6px var(--card-color,#00ffd5)}}

/* ── RIGHT PANEL ── */
#right{{
  width:220px;flex-shrink:0;
  background:var(--panel);border-left:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden
}}
#eng-log{{flex:1;overflow-y:auto;padding:8px 10px}}
.log-entry{{padding:3px 0;border-bottom:1px solid #0a0a14;font-size:9px;line-height:1.5}}
.log-entry .op{{color:var(--pink);font-weight:bold}}
.log-entry .g{{color:#1a3a3a}}
.log-entry .ok{{color:var(--green)}}
.log-entry .warn{{color:var(--gold)}}
#ledger-section{{border-top:1px solid var(--border);padding:8px 10px;flex-shrink:0}}
.ledger-entry{{font-size:9px;color:#1a2a2a;padding:2px 0;line-height:1.4}}
.ledger-entry .lid{{color:#2a3a4a}}

/* ── BOTTOM BAR ── */
#bar{{
  background:var(--panel);border-top:1px solid var(--border);
  padding:6px 14px;display:flex;align-items:center;gap:6px;
  flex-wrap:wrap;flex-shrink:0;z-index:10
}}
.btn{{background:#0a0a14;color:#2a3a4a;border:1px solid var(--border);
  border-radius:3px;padding:4px 10px;font-family:inherit;
  font-size:10px;cursor:pointer;transition:all 0.15s;white-space:nowrap}}
.btn:hover{{background:#111122;border-color:#3a3a4a;color:var(--bright)}}
.btn.op{{color:var(--pink);border-color:#2a1a2a}}
.btn.op:hover{{border-color:var(--pink)}}
.sep{{width:1px;height:16px;background:var(--border)}}
.lbl{{color:#1a2a2a;font-size:9px;letter-spacing:0.1em;text-transform:uppercase}}
#cmd-bar{{display:flex;gap:4px;align-items:center;margin-left:auto}}
#cmd-input{{background:rgba(5,5,16,0.9);color:var(--bright);
  border:1px solid var(--border);border-radius:3px;
  padding:4px 10px;font-family:inherit;font-size:10px;width:220px;outline:none}}
#cmd-input:focus{{border-color:var(--pink)}}
#cmd-input::placeholder{{color:#1a1a2a}}
#cmd-go{{background:#0a0a14;color:var(--pink);border:1px solid #2a1a2a;
  border-radius:3px;padding:4px 10px;font-family:inherit;font-size:10px;cursor:pointer}}
#cmd-go:hover{{border-color:var(--pink)}}

/* ── OVERLAY (summon) ── */
#overlay{{display:none;position:fixed;inset:0;z-index:100;flex-direction:column}}
#overlay.open{{display:flex}}
#overlay-bar{{
  background:rgba(3,3,8,0.97);border-bottom:1px solid #1a1a2a;
  padding:0 16px;height:36px;display:flex;align-items:center;gap:12px;
  flex-shrink:0
}}
#overlay-title{{color:var(--cyan);font-size:11px;letter-spacing:0.1em}}
#overlay-back{{
  background:#0a0a14;color:var(--purple);border:1px solid #2a1a4a;
  border-radius:3px;padding:3px 14px;font-family:inherit;font-size:10px;
  cursor:pointer;letter-spacing:0.08em
}}
#overlay-back:hover{{background:#1a1a2a;border-color:var(--purple)}}
#overlay-frame{{flex:1;border:none;background:#030308}}

/* ── LOADING OVERLAY -- the spini-spini net loads as the icon ── */
#load{{position:fixed;inset:0;z-index:200;background:var(--bg);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;
  transition:opacity 0.5s ease;overflow:hidden}}
/* the net is BLOWN UP big and layered ABOVE the text (z-index 2): where its
   pixels collide with the letters, the spini spini wins. Its border touches the
   frame. Text shows through the gaps because the canvas clears transparent. */
#load-cv{{position:absolute;top:50%;left:50%;width:min(88vh,88vw);height:min(88vh,88vw);
  transform:translate(-50%,-54%);opacity:0.95;pointer-events:none;z-index:2}}
#load.done{{opacity:0;pointer-events:none}}
#load .load-logo{{font-size:20px;color:#ffd700;letter-spacing:0.28em;font-weight:bold;
  text-shadow:0 0 28px rgba(255,215,0,0.75),0 0 6px rgba(255,215,0,0.9);z-index:1;margin-top:150px}}
#load .load-sub{{font-size:9px;color:#7fe6ff;letter-spacing:0.14em;text-transform:uppercase;z-index:1;
  text-shadow:0 0 12px rgba(127,230,255,0.5)}}
#load .load-bar{{width:340px;height:3px;background:#12101e;border-radius:2px;overflow:hidden;z-index:1}}
#load .load-fill{{height:100%;width:0%;border-radius:2px;
  background:linear-gradient(90deg,var(--purple),var(--cyan));transition:width 0.28s ease}}
#load .load-note{{font-size:8.5px;color:rgba(0,212,255,0.55);letter-spacing:0.06em;
  font-variant-numeric:tabular-nums;z-index:1;min-height:11px}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{{width:4px}}
::-webkit-scrollbar-track{{background:#030308}}
::-webkit-scrollbar-thumb{{background:#1a1a2a;border-radius:2px}}
</style>
</head>
<body>

<!-- LOADING OVERLAY -- pay once at load, then fly. The spini-spini net (a live
     C60 buckyball) spins and REFINES itself as the kernel loads: a loading icon
     that is the real geometry, not a spinner. spini spini. -->
<div id="load">
  <canvas id="load-cv"></canvas>
  <div class="load-logo">⬡ ENG {VERSION}</div>
  <div class="load-sub">MASTER CONTROL · summoning the kernel · P=12 · χ=2</div>
  <div class="load-bar"><div class="load-fill" id="load-fill"></div></div>
  <div class="load-note" id="load-note">&nbsp;</div>
</div>

<!-- TOP BAR -->
<div id="top-bar">
  <span class="logo">⬡ ENG {VERSION}</span>
  <span class="build">H7.1473.12.60 · {TIMESTAMP}</span>
  <span class="git">git:{GIT}</span>
  <span id="top-k" class="k-ok">6/6 ✓</span>
  <span class="clock" id="clock">──:──:──</span>
</div>

<!-- MAIN GRID -->
<div id="main">

  <!-- LEFT: kernel status + mini C60 -->
  <div id="left">
    <div class="panel-title">KERNEL</div>
    <div id="k-list">
      <div class="k-row"><span class="k-name">GK</span>  <span id="ks-gk"  class="k-ok">·</span><span class="k-kb">21KB</span></div>
      <div class="k-row"><span class="k-name">GA</span>  <span id="ks-ga"  class="k-ok">·</span><span class="k-kb">13KB</span></div>
      <div class="k-row"><span class="k-name">SAR</span> <span id="ks-sar" class="k-ok">·</span><span class="k-kb">27KB</span></div>
      <div class="k-row"><span class="k-name">NSS</span> <span id="ks-nss" class="k-ok">·</span><span class="k-kb">13KB</span></div>
      <div class="k-row"><span class="k-name">FS</span>  <span id="ks-fs"  class="k-ok">·</span><span class="k-kb">13KB</span></div>
      <div class="k-row"><span class="k-name">NAN</span> <span id="ks-nan" class="k-ok">·</span><span class="k-kb">24KB</span></div>
    </div>
    <div id="mini-canvas-wrap">
      <div class="panel-title">C60 · LIVE</div>
      <canvas id="cv-mini"></canvas>
    </div>
  </div>

  <!-- CENTER: module cards -->
  <div id="center">
    <div id="center-top">MODULES — CLICK TO SUMMON</div>
    <div class="mod-grid">
      {CARDS_HTML}
    </div>
  </div>

  <!-- RIGHT: log + ledger -->
  <div id="right">
    <div class="panel-title">SESSION LOG</div>
    <div id="eng-log"></div>
    <div id="ledger-section">
      <div class="panel-title" style="padding:0 0 4px">LEDGER</div>
      {LEDGER_HTML}
    </div>
  </div>

</div><!-- /main -->

<!-- BOTTOM BAR -->
<div id="bar">
  <span class="lbl">SEED</span>
  <button class="btn" onclick="engSeed('c60')">C60</button>
  <button class="btn" onclick="engSeed('dodec')">DODEC</button>
  <button class="btn" onclick="engRefine()">REFINE</button>
  <div class="sep"></div>
  <span class="lbl">PROOF</span>
  <button class="btn op" onclick="engSAR()">SAR-5</button>
  <button class="btn op" onclick="engNS()">NS FLOW</button>
  <button class="btn op" onclick="engFS()">FRAC SEARCH</button>
  <div class="sep"></div>
  <button class="btn" id="btn-modules" onclick="toggleModSelector(event)" title="select active sims">MODULES <span id="mod-count"></span></button>
  <div class="sep"></div>
  <span class="lbl" style="color:#1a2a1a">P=12 · χ=2 · λ̃=0.1473</span>
  <div id="cmd-bar">
    <input id="cmd-input" type="text" placeholder="cmd + enter  (eval JS)" spellcheck="false">
    <button id="cmd-go" onclick="cmdRun()">RUN</button>
  </div>
</div>

<!-- SELECT YOUR SIMS -->
<div id="mod-selector">
  <div class="ms-head">ACTIVE SIMS <span id="ms-allbtn" onclick="modAll(event)">all on</span></div>
  <div class="ms-body">{SELECTOR_HTML}
  </div>
</div>

<!-- SUMMON OVERLAY -->
<div id="overlay">
  <div id="overlay-bar">
    <button id="overlay-back" onclick="overlayClose()">← BACK</button>
    <span id="overlay-title">─</span>
    <span style="margin-left:auto;color:#1a2a2a;font-size:9px" id="overlay-url"></span>
  </div>
  <iframe id="overlay-frame" src=""></iframe>
</div>

<!-- KERNEL MODULES -->
<script>{M1}</script>
<script>{M2}</script>
<script>{M3}</script>
<script>{M4}</script>
<script>{M5}</script>
<script>{M6}</script>

<script>
// ── KERNEL CHECK ─────────────────────────────────────────────
var MODULES_OK = true;
(function(){{
  var checks=[
    ['ks-gk', typeof GK!=='undefined','GK'],
    ['ks-ga', typeof GA!=='undefined','GA'],
    ['ks-sar',typeof SAR!=='undefined','SAR'],
    ['ks-nss',typeof NSS!=='undefined','NSS'],
    ['ks-fs', typeof FS!=='undefined','FS'],
    ['ks-nan',typeof MNetNanite!=='undefined','NAN']
  ];
  var ok=0;
  checks.forEach(function(c){{
    var el=document.getElementById(c[0]);
    var pass=c[1];
    if(pass) ok++;
    else MODULES_OK=false;
    if(el){{ el.textContent=pass?'✓':'✗'; el.className=pass?'k-ok':'k-miss'; }}
    console.log('[ENG] '+c[2]+': '+(pass?'OK':'MISSING'));
  }});
  var tk=document.getElementById('top-k');
  tk.textContent=ok+'/6 '+(ok===6?'✓':'⚠');
  tk.className=ok===6?'k-ok':'k-bad';
}})();

// ── CLOCK ────────────────────────────────────────────────────
setInterval(function(){{
  var n=new Date();
  document.getElementById('clock').textContent=
    n.toTimeString().slice(0,8);
}},1000);

// ── MINI C60 CANVAS ──────────────────────────────────────────
// The spini C60 panel renders the SHARED _engState -- so SEED / REFINE / the proofs
// all show up live in the little turning buckyball (it STAYS and RESPONDS, never a
// frozen decoration decoupled from the kernel). _miniJpts is the cached face-point
// list; syncMini() rebuilds it whenever the geometry changes. spini spini.
var _miniCam={{rx:0.3,ry:0,spin:0.004}}, _miniJpts=null;
function syncMini(){{
  if(typeof _engState==='undefined' || !_engState) return;
  _miniJpts=_engState.faces.map(function(f){{
    return f.pts.map(function(p){{return[p[0],p[1],p[2]];}});
  }});
}}
(function miniInit(){{
  var wrap=document.getElementById('mini-canvas-wrap');
  var cv=document.getElementById('cv-mini');
  function resize(){{
    cv.width=wrap.clientWidth;
    cv.height=wrap.clientHeight-22;
  }}
  resize();
  new ResizeObserver(resize).observe(wrap);
  if(typeof _engState==='undefined' || !_engState) _engState=GK.buildC60();
  syncMini();
  var ctx=cv.getContext('2d');
  (function loop(){{
    requestAnimationFrame(loop);
    _miniCam.ry+=_miniCam.spin;
    var W=cv.width,H=cv.height;
    if(!W||!H||!_miniJpts) return;
    ctx.fillStyle='rgba(3,3,8,0.18)';ctx.fillRect(0,0,W,H);
    var cy2=Math.cos(_miniCam.ry),sy2=Math.sin(_miniCam.ry);
    var cx2=Math.cos(_miniCam.rx),sx2=Math.sin(_miniCam.rx);
    var zoom=Math.min(W,H)*0.38;
    function proj(p){{
      var x=p[0],y=p[1],z=p[2];
      var x1=x*cy2-z*sy2,z1=x*sy2+z*cy2;
      var y1=y*cx2-z1*sx2,z2=y*sx2+z1*cx2;
      var s=zoom/(z2+4);
      return{{x:W/2+x1*s,y:H/2+y1*s,z:z2}};
    }}
    var F=_engState.faces;
    for(var fi=0;fi<F.length;fi++){{
      var f=F[fi],pts=_miniJpts[fi]; if(!pts) continue;
      var n=pts.length, isPent=f.type==='pent';
      for(var i=0;i<n;i++){{
        var a=proj(pts[i]),b=proj(pts[(i+1)%n]);
        if(a.z<-3||b.z<-3) continue;
        var br=Math.max(0.05,Math.min(0.8,1.2/(Math.abs(a.z)+2)));
        ctx.strokeStyle=isPent?
          'rgba(0,212,255,'+br+')':
          'rgba(0,255,213,'+(br*0.4)+')';
        ctx.lineWidth=isPent?1.2:0.4;
        ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
      }}
    }}
  }})();
}})();

// ── SUMMON (auto-built from disk scan, no drift) ─────────────
var LINKS={{
{LINKS_JS}}};
function summon(key){{
  var url=LINKS[key];
  if(!url){{ logAdd('MISS',key.toUpperCase()); return; }}
  // a .md is not a sim -- it renders as raw text in an iframe. Open it in a new tab
  // (Curse 7/10: full-canvas/doc content misbehaves in the overlay iframe).
  if(/\.md($|\?)/.test(url)){{
    window.open(url,'_blank','noopener');
    logAdd('OPEN',key.toUpperCase()+' (new tab)');
    return;
  }}
  var ov=document.getElementById('overlay');
  var fr=document.getElementById('overlay-frame');
  var title=document.getElementById('overlay-title');
  var urlEl=document.getElementById('overlay-url');
  fr.src=url;
  title.textContent=key.toUpperCase();
  urlEl.textContent=url.replace('https://vsavytsk1.github.io/Mnetv1/','');
  ov.classList.add('open');
  logAdd('SUMMON',key.toUpperCase());
}}
function overlayClose(){{
  var ov=document.getElementById('overlay');
  var fr=document.getElementById('overlay-frame');
  ov.classList.remove('open');
  setTimeout(function(){{fr.src='';}},300);
  logAdd('BACK','dashboard');
}}

// ── SELECT YOUR SIMS ─────────────────────────────────────────
// All sims are LIVE by default. The selector only dims what you turn off.
var ALL_KEYS={ALL_KEYS_JS};
var modState={{}};
(function(){{
  var saved={{}};
  try{{saved=JSON.parse(localStorage.getItem('eng_mods_v2')||'{{}}');}}catch(e){{}}
  ALL_KEYS.forEach(function(k){{ modState[k]=(saved[k]===false)?false:true; }}); // default ON
}})();
function modApply(){{
  var on=0;
  ALL_KEYS.forEach(function(k){{
    var card=document.getElementById('card-'+k);
    var msd=document.getElementById('ms-'+k);
    var isOn=modState[k]!==false;
    if(isOn)on++;
    if(card){{ if(isOn)card.classList.remove('mod-off'); else card.classList.add('mod-off'); }}
    if(msd){{ msd.className='ms-dot'+(isOn?' on':''); }}
  }});
  var mc=document.getElementById('mod-count');
  if(mc)mc.textContent=on+'/'+ALL_KEYS.length;
}}
function toggleMod(key){{
  modState[key]=modState[key]===false?true:false;
  try{{localStorage.setItem('eng_mods_v2',JSON.stringify(modState));}}catch(e){{}}
  modApply();
}}
function modAll(e){{
  if(e)e.stopPropagation();
  var anyOff=ALL_KEYS.some(function(k){{return modState[k]===false;}});
  ALL_KEYS.forEach(function(k){{ modState[k]=anyOff?true:false; }}); // all-on, or all-off toggle
  try{{localStorage.setItem('eng_mods_v2',JSON.stringify(modState));}}catch(e2){{}}
  modApply();
  var b=document.getElementById('ms-allbtn'); if(b)b.textContent=anyOff?'all off':'all on';
}}
function toggleModSelector(e){{
  if(e)e.stopPropagation();
  document.getElementById('mod-selector').classList.toggle('open');
}}
document.addEventListener('click',function(e){{
  var sel=document.getElementById('mod-selector');
  var btn=document.getElementById('btn-modules');
  if(sel&&sel.classList.contains('open')&&!sel.contains(e.target)&&!btn.contains(e.target)){{
    sel.classList.remove('open');
  }}
}});

// ── KERNEL OPS ───────────────────────────────────────────────
// NOTE: _engState may already be the C60 built by miniInit above (shared). Only seed
// a default if nothing exists yet, so the spini panel and the ops share one geometry.
if(typeof _engState==='undefined') var _engState=null;
function engSeed(type){{
  _engState=type==='dodec'?GK.buildDodecahedron():GK.buildC60();
  var inv=GK.invariants(_engState);
  syncMini();   // the spini panel follows the seed live
  logAdd('SEED',type.toUpperCase()+' · '+inv.faces+'F · P='+inv.pents+' · χ='+(inv.vertices-inv.edges+inv.faces));
}}
function engRefine(){{
  if(!_engState)engSeed('c60');
  var t0=performance.now();
  _engState=GK.refineAll(_engState);
  var inv=GK.invariants(_engState);
  syncMini();   // REFINE now shows in the little turning buckyball -- it STAYS + grows
  logAdd('REFINE',inv.faces+'F · '+Math.round(performance.now()-t0)+'ms');
}}
function engSAR(){{
  if(!_engState)engSeed('c60');
  var t0=performance.now();
  var r=SAR.proof(_engState);
  logAdd('SAR-5','λ̃₁='+parseFloat(r.spectral.lambda1).toFixed(6)+
    ' · M₀='+r.M0.count+' · '+(r.spectral.match?'MATCH ✓':'Δ='+r.spectral.deviation)+
    ' · '+Math.round(performance.now()-t0)+'ms');
}}
function engNS(){{
  if(!_engState)engSeed('c60');
  var t0=performance.now();
  var r=NSS.runOn(_engState,{{Re:150,steps:200}});
  logAdd('NS FLOW','λ̃₁='+(r.lambdaEst!==null?r.lambdaEst.toFixed(6):'?')+
    ' · '+(r.delta!==null?'Δ='+r.delta.toFixed(6):'')+
    ' · '+Math.round(performance.now()-t0)+'ms');
}}
function engFS(){{
  if(!_engState)engSeed('c60');
  var t0=performance.now();
  var r=FS.search({{seed:'c60',maxLevels:3,target:0.1473}});
  logAdd('FRAC SEARCH',(r.locked?'LOCKED ✓':'not locked')+' · '+Math.round(performance.now()-t0)+'ms');
}}

// ── LOG ──────────────────────────────────────────────────────
function logAdd(op,msg){{
  var el=document.getElementById('eng-log');
  var d=document.createElement('div');
  d.className='log-entry';
  d.innerHTML='<span class="op">'+op+'</span>  <span class="ok">'+msg+'</span>';
  el.appendChild(d);
  el.scrollTop=el.scrollHeight;
}}

// ── THE SPINI-SPINI LOADER -- a live C60 that spins and REFINES as it loads ──
var _loadNet=null, _loadCam={{rx:0.35,ry:0,spin:0.010}}, _loadRun=true, _loadLevel=0;
function loadSpiniInit(){{
  var cv=document.getElementById('load-cv'); if(!cv||typeof GK==='undefined') return;
  var dpr=Math.min(2,window.devicePixelRatio||1);
  var SZ=Math.min(window.innerHeight*0.88,window.innerWidth*0.88);
  cv.width=SZ*dpr; cv.height=SZ*dpr;
  var ctx=cv.getContext('2d'); ctx.setTransform(dpr,0,0,dpr,0,0);
  // the loading net: fractalize ALL once, then 2x fractalize the 6s (hexes),
  // inner/mid=0.1 -- the genesis canon look. 9812 faces: dense + real-time
  // (3x hexes = 68612 faces = 2fps; Curse 35 -- predict the bill before allocating).
  var _lp={{innerScale:0.1,midScale:0.1}};
  _loadNet=GK.buildC60();
  try{{ _loadNet=GK.refineAll(_loadNet,_lp);
        _loadNet=GK.refineAllHexes(_loadNet,_lp);
        _loadNet=GK.refineAllHexes(_loadNet,_lp); _loadLevel=4; }}catch(e){{}}
  (function loop(){{
    if(!_loadRun) return;
    requestAnimationFrame(loop);
    _loadCam.ry+=_loadCam.spin;
    var W=SZ,H=SZ;
    // clear TRANSPARENT so the text underneath shows through the net's gaps;
    // where a strut is drawn it covers the letter -> the spini spini wins.
    ctx.clearRect(0,0,W,H);
    var cy2=Math.cos(_loadCam.ry),sy2=Math.sin(_loadCam.ry);
    var cx2=Math.cos(_loadCam.rx),sx2=Math.sin(_loadCam.rx);
    var zoom=Math.min(W,H)*0.92;   // 2x -- the fractalized net fills the frame
    function proj(p){{
      var x=p[0],y=p[1],z=p[2];
      var x1=x*cy2-z*sy2,z1=x*sy2+z*cy2;
      var y1=y*cx2-z1*sx2,z2=y*sx2+z1*cx2;
      var s=zoom/(z2+4);
      return{{x:W/2+x1*s,y:H/2+y1*s,z:z2}};
    }}
    var F=_loadNet.faces;
    for(var fi=0;fi<F.length;fi++){{
      var f=F[fi],pts=f.pts,n=pts.length,isPent=f.type==='pent';
      for(var i=0;i<n;i++){{
        var a=proj(pts[i]),b=proj(pts[(i+1)%n]);
        if(a.z<-3||b.z<-3) continue;
        var br=Math.max(0.05,Math.min(0.85,1.3/(Math.abs(a.z)+2)));
        ctx.strokeStyle=isPent?'rgba(167,139,250,'+br+')':'rgba(0,212,255,'+(br*0.45)+')';
        ctx.lineWidth=isPent?1.3:0.5;
        ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
      }}
    }}
  }})();
}}
// refine the spini net one Goldberg level (called as the load bar advances)
function loadSpiniRefine(){{
  if(!_loadNet||typeof GK==='undefined'||_loadLevel>=3) return;
  try{{ _loadNet=GK.refineAll(_loadNet); _loadLevel++; }}catch(e){{}}
}}

// ── LOADING BAR ──────────────────────────────────────────────
function loadStep(frac,note){{
  var f=document.getElementById('load-fill'), n=document.getElementById('load-note');
  if(f)f.style.width=Math.round(frac*100)+'%';
  if(n&&note)n.textContent=note;
}}
function loadDone(){{
  loadStep(1,'ready · '+ALL_KEYS.length+' sims live');
  var el=document.getElementById('load');
  if(el)setTimeout(function(){{el.classList.add('done');
    setTimeout(function(){{_loadRun=false;el.style.display='none';}},520);}},300);
}}

// ── CMD ──────────────────────────────────────────────────────
function cmdRun(){{
  var v=document.getElementById('cmd-input').value.trim();
  if(!v)return;
  document.getElementById('cmd-input').value='';
  try{{
    var r=eval(v);
    logAdd('CMD',String(JSON.stringify(r)).slice(0,160));
  }}catch(e){{logAdd('ERR',e.message);}}
}}
document.getElementById('cmd-input').addEventListener('keydown',function(e){{
  if(e.key==='Enter')cmdRun();
}});

// DATA PANELS
var PC={{cyan:"#00d4ff",pink:"#ff69b4",gold:"#ffd700",green:"#00ffd5",red:"#ff4444",orange:"#ff9040",dim:"#1a2a3a"}};
function setPanel(id,rows){{
  var el=document.getElementById("dp-"+id); if(!el)return;
  el.innerHTML=rows.map(function(r){{
    return "<div class=\\"dp-row\\"><span class=\\"dp-k\\">"+r[0]+"</span><span class=\\"dp-v\\" style=\\"color:"+(PC[r[2]]||"#9090a0")+"\\">" +r[1]+"</span></div>";
  }}).join("");
}}

function engBoot(){{
  // Build the C60 graph ONCE and reuse it across every panel (was built 4x -> 1x).
  var t1=performance.now(); var gk2=GK.buildC60(); var inv2=GK.invariants(gk2); var chi2=inv2.vertices-inv2.edges+inv2.faces;
  setPanel("gk",[["V",inv2.vertices,"cyan"],["E",inv2.edges,"cyan"],["F",inv2.faces,"cyan"],["P",inv2.pents,"pink"],["hex",inv2.hexes,"text"],["chi",chi2,"gold"],["E/V",(inv2.edges/inv2.vertices).toFixed(3),"gold"],["ms",(performance.now()-t1).toFixed(1),"dim"]]);
  logAdd("GK","C60 P="+inv2.pents+" chi="+chi2);
  return gk2;
}}
// The 5 remaining kernel modules as ordered steps; each drives a panel + the bar.
function engSteps(gk2){{ return [
  ["GA",function(){{ var t2=performance.now(); GA.logReset(); var ax=GA.eulerCheck(gk2);
    setPanel("ga",[["euler",ax.valid?"PASS":"FAIL",ax.valid?"green":"red"],["P=12",ax.pents===12?"PASS":"FAIL",ax.pents===12?"green":"red"],["chi=2",ax.chi===2?"PASS":"FAIL",ax.chi===2?"green":"red"],["entries",GA.log.entries.length,"cyan"],["ms",(performance.now()-t2).toFixed(1),"dim"]]);
    logAdd("GA","euler="+(ax.valid?"PASS":"FAIL")+" entries="+GA.log.entries.length); }}],
  ["SAR",function(){{ var t3=performance.now(); var sr=SAR.proof(gk2); var lam=parseFloat(sr.spectral.lambda1).toFixed(6);
    setPanel("sar",[["lam1",lam,"cyan"],["theory",parseFloat(sr.spectral.theory_C60).toFixed(6),"dim"],["delta",Math.abs(sr.spectral.lambda1-sr.spectral.expected).toFixed(6),sr.spectral.match?"green":"orange"],["MATCH",sr.spectral.match?"YES":"NO",sr.spectral.match?"green":"red"],["M0",sr.M0.count,"pink"],["vacuum",sr.stability.projectorCheck?"STABLE":"UNSTABLE",sr.stability.projectorCheck?"green":"red"],["ms",(performance.now()-t3).toFixed(1),"dim"]]);
    logAdd("SAR","lam1="+lam+" "+(sr.spectral.match?"MATCH":"no match")); }}],
  ["NSS",function(){{ var t4=performance.now(); var nr=NSS.runOn(gk2,{{Re:150,steps:200,logEvery:9999}}); var nl=nr.lambdaEst!==null?nr.lambdaEst.toFixed(6):"?";
    setPanel("nss",[["Re",150,"orange"],["steps",200,"dim"],["N",nr.graph?nr.graph.N:"?","cyan"],["lam1",nl,"cyan"],["lam1w",nr.lambdaEstW!==null?nr.lambdaEstW.toFixed(6):"?","gold"],["delta",nr.delta!==null?nr.delta.toFixed(6):"?",Math.abs(nr.delta||1)<0.01?"green":"orange"],["ms",(performance.now()-t4).toFixed(1),"dim"]]);
    logAdd("NSS","lam1="+nl); }}],
  ["FS",function(){{ var t5=performance.now(); var fr=FS.search({{seed:"c60",maxLevels:3,target:0.1473,lockThresh:0.005}});
    setPanel("fs",[["target","0.1473","cyan"],["locked",fr.locked?"YES":"NO",fr.locked?"green":"orange"],["lockLvl",fr.lockLevel!==undefined?fr.lockLevel:"?","gold"],["bestLam",fr.bestLambda!==undefined?fr.bestLambda.toFixed(6):"?","cyan"],["bestDelta",fr.bestDelta!==undefined?fr.bestDelta.toFixed(6):"?","dim"],["ms",(performance.now()-t5).toFixed(1),"dim"]]);
    logAdd("FS",(fr.locked?"LOCKED":"not locked")); }}],
  ["NAN",function(){{ var t6=performance.now(); var ns={{}};
    try{{var dag=typeof MNetNanite.build==="function"?MNetNanite.build(gk2):MNetNanite; ns=dag.stats||dag;}}catch(e){{ns={{err:e.message.slice(0,30)}};}}
    var nr2=Object.keys(ns).slice(0,5).map(function(k){{return[k,String(ns[k]).slice(0,12),"cyan"];}});
    if(!nr2.length)nr2=[["api","MNetNanite","cyan"],["status","loaded","green"]];
    nr2.push(["ms",(performance.now()-t6).toFixed(1),"dim"]);
    setPanel("nan",nr2); logAdd("NAN","MNetNanite loaded"); }}]
]; }}

// Optimised start: paint the dashboard + all cards FIRST, then run the 6 kernel
// modules as stepped chunks behind the loading bar, so the wait reads as a
// deliberate ritual (Curse 9 was a 12s blocking LCP), never a glitch.
window.addEventListener("load",function(){{
  logAdd("BOOT","ENG {VERSION} git:{GIT}");
  loadSpiniInit();                             // spini spini: the net starts spinning
  modApply();  // all sims live by default; reflect saved toggles + fill the count
  logAdd("SIMS",ALL_KEYS.length+" sims live");
  loadStep(0.10,"spini spini · "+ALL_KEYS.length+" sims live");
  // CURSE 34: sequence with setTimeout, NOT requestIdleCallback -- the spinning
  // rAF loop would starve rIC and freeze the loader mid-way. A timer always fires.
  var defer=function(f){{ return setTimeout(f,90); }};
  var _loadFallback=setTimeout(loadDone,8000); // K4: never trap the user in the wait
  defer(function(){{
    try{{
      loadStep(0.22,"kernel · building C60"); loadSpiniRefine();
      var gk2=engBoot();                       // GK panel + the single C60 build
      var steps=engSteps(gk2), i=0, base=0.30;
      (function run(){{
        if(i>=steps.length){{ clearTimeout(_loadFallback); logAdd("ALL OK","6/6 modules ran"); loadDone(); return; }}
        var name=steps[i][0];
        loadStep(base+(i/steps.length)*0.68,"module · "+name);
        if(i%2===0) loadSpiniRefine();         // refine the net as the bar advances
        try{{ steps[i][1](); }}catch(e){{ logAdd("ERR",name+" "+String(e.message||e).slice(0,30)); }}
        i++; defer(run);
      }})();
    }}catch(e){{ logAdd("ERR",String(e.message||e).slice(0,40)); clearTimeout(_loadFallback); loadDone(); }}
  }});
}});
console.log("%c ENG {VERSION} MASTER CONTROL","color:#a78bfa;font-size:14px;font-weight:bold");
</script>
</body></html>"""

OUT.write_text(HTML, encoding="utf-8")
size_kb = len(HTML) // 1024
print(f"\\n[OK] {OUT.name}  {size_kb}KB")
print(f"[OK] https://vsavytsk1.github.io/Mnetv1/shell/eng_{VERSION}.html")

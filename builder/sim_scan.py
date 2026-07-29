#!/usr/bin/env python3
"""
sim_scan.py -- the self-discovering sim registry for the ENG master control.
KERNELIMAGIC compliant: ASCII only, no deps, one job.

The builder is absolute. This scanner makes the master control DISCOVER every
sim on disk instead of a hand-typed list that drifts (the dum-dum we are fixing).
Run standalone to PREVIEW what the master control will summon:

    py -3 sim_scan.py            # human preview table
    py -3 sim_scan.py --json     # machine dump

Rule: newest version per family wins; the render comes from the builder; if the
scan is wrong, we fix the scan and rebuild all at once. spini. P=12. chi=2.
"""
import re, sys, json, html, subprocess
from pathlib import Path

ROOT  = Path(__file__).parent.parent
BASE  = "https://vsavytsk1.github.io/Mnetv1/"

# TRUTH = GIT. GitHub Pages serves what git tracks, not what sits on disk. A card
# for a gitignored/untracked file is a guaranteed 404 (caught in the 2026-07-29
# one-by-one test: pack/hexCompTest was on disk but .gitignored -> dead card).
# Same doctrine as gen_io_index.py. If git is unavailable, fall back to disk.
def _git_tracked_html():
    try:
        out = subprocess.check_output(["git", "ls-files", "*.html"], cwd=ROOT,
              stderr=subprocess.DEVNULL).decode("utf-8", "ignore")
        return set(l.strip() for l in out.splitlines() if l.strip().endswith(".html"))
    except Exception:
        return None   # git not available -> caller falls back to disk-only

TRACKED = _git_tracked_html()

# Folders that hold PUBLIC, summonable sims (the showcase). _private is a cave wall.
SCAN_DIRS = ["shell", "tree", "pack", "research"]

# Files that are NOT sims to summon (the master control itself, data dumps).
SKIP_NAMES = {"eng_v2.0.html", "eng_v1.0.html", "index.html", "about.html"}
SKIP_SUBSTR = ["_dashboard_data", "xref-", "genesis_bench"]

# Category -> (tag, color, border). Keyword match on family name, first hit wins.
CATEGORY = [
    (("genesis", "tetragenesis"),           ("GENESIS",  "#00ffd5", "#1a3a3a")),
    (("graph_sandbox", "sandbox"),          ("SANDBOX",  "#80d0ff", "#1a2a3a")),
    (("math_tree", "tree"),                 ("TREE",     "#ffd700", "#3a3a1a")),
    (("navier", "mnet", "fslimium", "ns"),  ("FLOW",     "#ff9040", "#3a2a1a")),
    (("maxwellium", "cristalium", "femtonium", "thealimitium", "noetherium",
      "kellerium", "templum", "harmonia", "lagrangium", "isingium", "squeezium",
      "kirchhoffium", "mayerium", "kelvinium", "helios", "bicium", "spectrium",
      "cofium", "feynmanium", "chromium", "kuramium", "shannonium", "pcbium",
      "byte"),
                                            ("PHYSICS",  "#a78bfa", "#2a1a4a")),
    (("gardinerium", "phaistium", "vitruvium", "simcityc", "flagellium",
      "parasitarium", "transmutation"),     ("ATLAS",    "#00d4ff", "#123244")),
    (("atelier", "baudin", "arcanium", "ancientmagic", "smithium", "mycelium"),
                                            ("ATELIER",  "#ff69b4", "#3a1a2a")),
    (("warning", "gate", "spooky"),         ("FMA",      "#ff4488", "#3a1a2a")),
    (("vale", "jarvis", "obsidius", "valtium", "portal", "brainium"),
                                            ("OS",       "#c0c0d0", "#2a2a3a")),
    (("aracnium", "agon", "bersha", "hathor", "emporium", "lamanium",
      "metamorph", "showerium", "tavlium", "dfwcatium", "anthoforium",
      "allonet", "cryostasium", "apollonium"),
                                            ("ECOSYSTEM","#88ff88", "#1a3a1a")),
    (("holly7", "gkernv2", "sar_proof", "nc_panel", "samsara",
      "machinenet_shell", "wiggle_craft", "h7"),
                                            ("KERNEL",   "#a78bfa", "#2a1a4a")),
]
DEFAULT_CAT = ("SIM", "#9090a0", "#20202e")

VER_RE = re.compile(r"[-_]v?\d.*$", re.IGNORECASE)

def family(stem):
    """Strip trailing version to group a family. gardinerium-v2_2_1 -> gardinerium.
    Variant markers (mobile, 3d) stay their own family so distinct sims each show a
    card and are never collapsed into a sibling (e.g. emporium 2D vs emporium 3D)."""
    low = stem.lower()
    mobile = "mobile" in low
    threed = bool(re.search(r"(?:^|[-_])3d(?:[-_]|$)", low))
    f = VER_RE.sub("", stem).strip("-_").lower() or low
    if threed and not f.endswith("_3d"):
        f = f + "_3d"
    if mobile and not f.endswith("_mobile"):
        f = f + "_mobile"
    return f

def version_key(stem):
    """Sortable tuple of the numbers in the version, so v2_2_1 > v1_0."""
    nums = re.findall(r"\d+", stem)
    return tuple(int(n) for n in nums) if nums else (0,)

def category(fam):
    for keys, meta in CATEGORY:
        if any(k in fam for k in keys):
            return meta
    return DEFAULT_CAT

def deep_unescape(s):
    """Fully decode HTML entities, even double-encoded (&amp;middot; -> mid-dot)."""
    for _ in range(3):
        u = html.unescape(s)
        if u == s:
            break
        s = u
    return s

def title_of(path):
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:4000]
    except Exception:
        return ""
    m = re.search(r"<title>(.*?)</title>", head, re.IGNORECASE | re.DOTALL)
    if m:
        return deep_unescape(re.sub(r"\s+", " ", m.group(1)).strip())[:80]
    m = re.search(r"<h1[^>]*>(.*?)</h1>", head, re.IGNORECASE | re.DOTALL)
    if m:
        return deep_unescape(re.sub(r"<[^>]+>", "", m.group(1)).strip())[:80]
    return ""

def js_key(rel):
    """Unique JS-safe key from the relative path (keep-it-all: one card per file)."""
    return re.sub(r"[^0-9a-zA-Z]+", "_", rel.rsplit(".", 1)[0]).strip("_").lower()

def caps_of(stem, rel, body):
    """Auto-detect capability chips from the file itself, so the badges never drift
    from what the sim actually is. Returns a short ordered list like ['frm','gpu'].
      tab = runs in a tab / desktop (default true for any html)
      frm = summonable inside the iframe overlay (all shell sims)
      pc  = pointer/keyboard desktop control
      and/ios = mobile-friendly (viewport + touch)
      gpu = uses WebGL / webgpu / three
      kbd = listens for keydown
      priv = lives under a private/builder path
    """
    low = (stem + " " + rel).lower()
    b = body.lower()
    caps = []
    caps.append("frm")                                   # every shell sim summons in-frame
    if "mobile" in low or "initial-scale" in b or "touchstart" in b:
        caps += ["and", "ios"]
    else:
        caps.append("pc")
    if any(k in b for k in ("webgl", "webgpu", "getcontext('webgl", 'three.js', "three.min")):
        caps.append("gpu")
    if "keydown" in b or "keypress" in b:
        caps.append("kbd")
    if "/builder/" in ("/" + rel.lower()) or rel.lower().startswith("_private"):
        caps.append("priv")
    # dedupe, keep order, cap at 5
    out = []
    for c in caps:
        if c not in out:
            out.append(c)
    return out[:5]

def discover():
    """Keep it all: EVERY .html under the scan dirs is its own card (all versions,
    matching the io pages archive). Only true non-sims are skipped. Grouped by
    family for ordering, newest version first within each family."""
    recs = []
    seen = set()
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.html")):
            name = p.name
            if name in SKIP_NAMES:                  continue
            if any(s in name for s in SKIP_SUBSTR): continue
            rel  = p.relative_to(ROOT).as_posix()
            # TRUTH = GIT: only card what Pages will actually serve (skip gitignored/untracked)
            if TRACKED is not None and rel not in TRACKED: continue
            key  = js_key(rel)
            if key in seen:                         continue
            seen.add(key)
            stem = p.stem
            fam  = family(stem)
            tag, color, border = category(fam)
            try:
                body = p.read_text(encoding="utf-8", errors="ignore")[:8000]
            except Exception:
                body = ""
            ttl  = title_of(p)
            recs.append({
                "family": fam,
                "stem":   stem,
                "vkey":   version_key(stem),
                "url":    BASE + rel,
                "rel":    rel,
                "title":  ttl,
                "tag":    tag, "color": color, "border": border,
                "key":    key,
                "name":   stem.upper()[:42],
                "desc":   (ttl or rel)[:70],
                "caps":   caps_of(stem, rel, body),
            })
    # order: category tag, then family, then newest version first
    recs.sort(key=lambda r: (r["tag"], r["family"], tuple(-n for n in r["vkey"])))
    return recs

def latest_only(recs):
    """Collapse to the newest version per family -- the DASHBOARD view. The archive
    (all versions) stays whole on the io pages; this is only the display filter, so
    the main control shows one pretty card per sim, not every version. Path X: the
    journey is public; the dashboard shows the head of each lineage."""
    best = {}
    for r in recs:
        f = r["family"]
        if f not in best or r["vkey"] > best[f]["vkey"]:
            best[f] = r
    out = list(best.values())
    out.sort(key=lambda r: (r["tag"], r["family"]))
    return out

if __name__ == "__main__":
    sims = discover()
    if "--latest" in sys.argv:
        sims = latest_only(sims)
    if "--json" in sys.argv:
        print(json.dumps(sims, indent=2))
    else:
        print(f"Discovered {len(sims)} sims (keep-it-all: every version):\n")
        by_cat = {}
        for s in sims:
            by_cat.setdefault(s["tag"], []).append(s)
        for tag in sorted(by_cat):
            print(f"=== {tag} ({len(by_cat[tag])}) ===")
            for s in by_cat[tag]:
                print(f"  {s['key']:<24} {s['rel']}")
        print(f"\nTOTAL: {len(sims)} summonable sims")

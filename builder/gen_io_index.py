#!/usr/bin/env python3
"""Generate IO_PAGES.md -- the public index of EVERY live .html across all repos.
No matter how small, every deployed page gets a link. Truth = git-tracked on origin
(what GitHub Pages serves). One file, all links. P=12. chi=2. Always."""
import subprocess
import sys
from pathlib import Path

# repo folder -> (github user/repo for the io URL)
REPOS = {
    r"C:\PythonDevs\MNetv1":                     "Mnetv1",
    r"C:\PythonDevs\SpiderEngineering":          "SpiderEngineering",
    r"C:\PythonDevs\JpnTree":                    "JpnTree",
    r"C:\PythonDevs\RestoAerospaceEngineering":  "RestoAerospaceEngineering",
    r"C:\PythonDevs\SpookyPrimes":               "SpookyPrimes",
    r"C:\PythonDevs\EldenGirl\concept":          "EldenGirl",
    r"C:\PythonDevs\VALE":                       "VALE",
    r"C:\PythonDevs\Mnet":                       "Mnet",
}
# Repos whose GitHub Pages is configured to serve a SUBFOLDER as the site root.
# For these, a file git-tracked at "docs/x.html" is served at "<repo>/x.html" --
# so the docs/ prefix must be STRIPPED from the live URL or every link 404s.
# Verified live (HEAD 200) that EldenGirl + VALE serve their docs/ folder as root.
PAGES_ROOT = {
    "EldenGirl": "docs/",
    "VALE":      "docs/",
}
BASE = "https://vsavytsk1.github.io/"

def tracked_html(path):
    try:
        out = subprocess.check_output(["git", "ls-files", "*.html"], cwd=path,
                                      stderr=subprocess.DEVNULL).decode("utf-8", "ignore")
    except Exception:
        return []
    return sorted(l.strip() for l in out.splitlines() if l.strip().endswith(".html"))

lines = [
    "# IO PAGES -- every live link, no matter how small",
    "",
    "*The complete public index of every `.html` deployed to GitHub Pages across all",
    "repos. Generated from what git actually tracks on each repo (the truth of what",
    "Pages serves), by `builder/gen_io_index.py`. Nothing hidden; the door is open.*",
    "",
    "*P=12 . chi=2 . the receipts are public . always.*",
    "",
]
grand = 0
# A repo that cannot be found is REPORTED, never skipped in silence. Two of these
# paths went stale when the repos were consolidated into one folder each, and the
# silent `continue` below would have dropped VALE and Mnet out of the public index
# without a word -- while the TOTAL line went on claiming eight repos, because it
# counted len(REPOS) rather than what was actually written.
missing = [f for f in REPOS if not Path(f).exists()]
if missing:
    print("MISSING REPO FOLDERS -- these would NOT be indexed:")
    for f in missing:
        print("   " + f)
    sys.exit("refusing to write a partial index. Fix REPOS, or delete the row.")

indexed = 0
for folder, ghrepo in REPOS.items():
    if not Path(folder).exists():
        continue
    files = tracked_html(folder)
    if not files:
        continue
    grand += len(files)
    indexed += 1
    lines.append(f"---\n\n## {ghrepo}  ({len(files)} pages)\n")
    root = PAGES_ROOT.get(ghrepo, "")   # subfolder served as Pages root, if any
    for rel in files:
        # the live path: strip the Pages-root prefix so the URL actually resolves
        served = rel[len(root):] if root and rel.startswith(root) else rel
        url = BASE + ghrepo + "/" + served
        lines.append(f"- [{rel}]({url})")
    lines.append("")

lines.insert(6, f"**TOTAL: {grand} public pages across {indexed} repos.**\n")

out = Path(r"C:\PythonDevs\MNetv1\IO_PAGES.md")
body = "\n".join(lines).replace("\r\n", "\n").rstrip() + "\n"
out.write_text(body, encoding="utf-8", newline="\n")
b = out.read_bytes()
lone = sum(1 for i, c in enumerate(b) if c == 13 and (i + 1 >= len(b) or b[i + 1] != 10))
print(f"[OK] {out.name}  {len(b)//1024}KB  pages={grand}  loneCR={lone}")

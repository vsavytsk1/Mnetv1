"""
_reorganize_repo_v1.py
======================
ONE-TIME repo reorganization.
H7.1473.12.60  —  the moment we locked the structure.

RULES:
  NEVER MOVE:
    .git/ .gitignore .nojekyll
    README.md LICENSE
    index.html about.html        (GitHub Pages entry points)
    builder/                     (SACRED)
    kernel/                      (SACRED — JS source of truth)

  MOVE TO public/:
    shell/                       (all genesis/sandbox/mnet HTML)
    tree/                        (all math_tree versions)
    pack/                        (holly7.html + hexCompTest output)
    research/                    (cold pass, compute receipts)
    Gsndbx3testClrsMath/         (sandbox tests)
    logs/                        (run logs)

  MOVE TO docs/:
    CONTRIBUTING.md
    DATABASE.md
    DISCLAIMER.md
    ETHICS.md
    HITCHHIKERS_ENTRY.md
    JOURNEY.md
    PIPELINE.md
    SACRED_MATH_TREE.md
    SESSION_LOG.md
    STEAM_PATH.md
    requirements_env.txt
    smr.py
    index_mobius_old.html

  LEAVE AT ROOT:
    .git/ .gitignore .nojekyll
    README.md LICENSE
    index.html about.html
    builder/ kernel/
    BUILD_TRACE.log

GITHUB PAGES IMPACT:
  - index.html stays at root → io still works
  - shell/ moves to public/shell/ → links inside shell/ may need update
  - All self-contained HTML files → zero external deps → zero breaks
  - builder/ paths: ROOT = repo root, still correct.
  - kernel/ paths: still at ROOT/kernel/. still correct.
"""
import shutil, time
from pathlib import Path

ROOT    = Path(__file__).parent.parent.parent  # MNetv1/
PUBLIC  = ROOT / "public"
DOCS    = ROOT / "docs"

PUBLIC.mkdir(exist_ok=True)
DOCS.mkdir(exist_ok=True)

moved = []
skipped = []

def move(src_rel, dst_rel):
    src = ROOT / src_rel
    dst = ROOT / dst_rel
    if not src.exists():
        print(f"  [SKIP not found] {src_rel}")
        skipped.append(src_rel)
        return
    if dst.exists():
        print(f"  [SKIP exists]    {dst_rel}")
        skipped.append(str(dst_rel))
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    moved.append(f"{src_rel} -> {dst_rel}")
    print(f"  [OK] {src_rel:<40} -> {dst_rel}")

print("=" * 60)
print("  REPO REORGANIZATION  H7.1473.12.60")
print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ── TO public/ ─────────────────────────────────────────────────────────────
print("\n-- public/ --")
move("shell",                 "public/shell")
move("tree",                  "public/tree")
move("pack",                  "public/pack")
move("research",              "public/research")
move("Gsndbx3testClrsMath",   "public/Gsndbx3testClrsMath")
move("logs",                  "public/logs")

# ── TO docs/ ───────────────────────────────────────────────────────────────
print("\n-- docs/ --")
for md in [
    "CONTRIBUTING.md", "DATABASE.md", "DISCLAIMER.md",
    "ETHICS.md", "HITCHHIKERS_ENTRY.md", "JOURNEY.md",
    "PIPELINE.md", "SACRED_MATH_TREE.md", "SESSION_LOG.md",
    "STEAM_PATH.md",
]:
    move(md, f"docs/{md}")

move("requirements_env.txt",  "docs/requirements_env.txt")
move("smr.py",                "docs/smr.py")
move("index_mobius_old.html", "docs/index_mobius_old.html")

# ── Update builder paths that reference shell/ or pack/ ────────────────────
print("\n-- Updating builder paths --")

# build_holly7.py: PACK = ROOT / "pack"  -> ROOT / "public/pack"
bh7 = ROOT / "builder" / "build_holly7.py"
if bh7.exists():
    src = bh7.read_text(encoding="utf-8")
    patched = src.replace(
        'PACK   = ROOT / "pack"',
        'PACK   = ROOT / "public" / "pack"'
    ).replace(
        'PACK         = ROOT / "pack"',
        'PACK         = ROOT / "public" / "pack"'
    )
    if patched != src:
        bh7.write_text(patched, encoding="utf-8")
        print("  [OK] build_holly7.py: PACK -> public/pack")
    else:
        print("  [CHECK] build_holly7.py PACK path — verify manually")

# build_warning.py: GATE_IMG = ROOT/"shell"/...  -> ROOT/"public/shell"/...
bw = ROOT / "builder" / "build_warning.py"
if bw.exists():
    src = bw.read_text(encoding="utf-8")
    patched = src.replace(
        '"shell"',
        '"public" / "shell"'
    )
    if patched != src:
        bw.write_text(patched, encoding="utf-8")
        print("  [OK] build_warning.py: shell -> public/shell")

# rebuild_gate.py
rg = ROOT / "builder" / "rebuild_gate.py"
if rg.exists():
    src = rg.read_text(encoding="utf-8")
    patched = src.replace(
        '"shell"',
        '"public" / "shell"'
    )
    if patched != src:
        rg.write_text(patched, encoding="utf-8")
        print("  [OK] rebuild_gate.py: shell -> public/shell")

# HOLLY7.py launcher
h7 = ROOT / "builder" / "HOLLY7.py"
if h7.exists():
    src = h7.read_text(encoding="utf-8")
    patched = src.replace(
        'PACK   = ROOT / "pack"',
        'PACK   = ROOT / "public" / "pack"'
    ).replace(
        'PACK         = ROOT / "pack"',
        'PACK         = ROOT / "public" / "pack"'
    )
    if patched != src:
        h7.write_text(patched, encoding="utf-8")
        print("  [OK] HOLLY7.py: PACK -> public/pack")

# ── Write migration log ─────────────────────────────────────────────────────
log = [
    "repo_reorganize_v1",
    f"timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
    f"moved:   {len(moved)}",
    f"skipped: {len(skipped)}",
    "",
    "MOVED:",
] + [f"  {m}" for m in moved] + [
    "",
    "STRUCTURE AFTER:",
    "  MNetv1/",
    "    builder/     SACRED",
    "    kernel/      SACRED",
    "    public/      GitHub Pages content",
    "      shell/     genesis/sandbox/mnet HTML",
    "      tree/      math_tree versions",
    "      pack/      holly7.html + hexCompTest",
    "      research/  cold pass, compute",
    "    docs/        lore + md files",
    "    index.html   root entry (GitHub Pages)",
    "    README.md",
    "    BUILD_TRACE.log",
]
(ROOT / "builder" / "patches" / "_reorganize_repo_v1.log").write_text(
    "\n".join(log), encoding="utf-8"
)

print(f"\n  {len(moved)} moved  |  {len(skipped)} skipped")
print("  Log: builder/patches/_reorganize_repo_v1.log")
print("\n  NEW COMMANDS:")
print('  python builder/build_holly7.py   # output -> public/pack/holly7.html')
print('  .\\builder\\dist\\HOLLY7.exe        # same, opens Brave')
print("\nDONE.")

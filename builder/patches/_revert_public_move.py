"""
_revert_public_move.py
======================
REVERT the public/ move. GitHub Pages only serves from root or /docs.
All live URLs use root paths — public/ breaks every single one.

MOVES BACK:
  public/shell/     -> shell/
  public/tree/      -> tree/
  public/pack/      -> pack/
  public/research/  -> research/
  public/logs/      -> logs/
  public/Gsndbx3testClrsMath/ -> Gsndbx3testClrsMath/

KEEPS (these are fine where they are):
  docs/             -> stays (no live URLs point to raw .md files)
  builder/          -> stays SACRED
  kernel/           -> stays SACRED

ALSO FIXES:
  builder/build_holly7.py  PACK path -> back to ROOT/"pack"
  builder/HOLLY7.py        PACK path -> back to ROOT/"pack"
"""
import shutil, time
from pathlib import Path

ROOT   = Path(__file__).parent.parent.parent  # MNetv1/
PUBLIC = ROOT / "public"

moved = []

def move_back(sub):
    src = PUBLIC / sub
    dst = ROOT / sub
    if not src.exists():
        print(f"  [SKIP not found] public/{sub}")
        return
    if dst.exists():
        print(f"  [SKIP exists at root] {sub}")
        return
    shutil.move(str(src), str(dst))
    moved.append(sub)
    print(f"  [OK] public/{sub} -> {sub}/")

print("=" * 60)
print("  REVERT public/ MOVE")
print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("  GitHub Pages: root only. public/ = 404 on everything.")
print("=" * 60)

move_back("shell")
move_back("tree")
move_back("pack")
move_back("research")
move_back("logs")
move_back("Gsndbx3testClrsMath")

# Remove public/ if empty
if PUBLIC.exists():
    remaining = list(PUBLIC.iterdir())
    if not remaining:
        PUBLIC.rmdir()
        print("\n  [OK] public/ removed (was empty)")
    else:
        print(f"\n  [NOTE] public/ still has: {[r.name for r in remaining]}")

# Fix builder PACK paths back to ROOT/"pack"
print("\n-- Fixing builder PACK paths --")
for fname in ["build_holly7.py", "HOLLY7.py"]:
    fp = ROOT / "builder" / fname
    if fp.exists():
        s = fp.read_text(encoding="utf-8")
        fixed = (s
            .replace('PACK   = ROOT / "public" / "pack"', 'PACK   = ROOT / "pack"')
            .replace('PACK         = ROOT / "public" / "pack"', 'PACK         = ROOT / "pack"')
            .replace('ROOT / "public" / "pack"', 'ROOT / "pack"')
        )
        if fixed != s:
            fp.write_text(fixed, encoding="utf-8")
            print(f"  [OK] {fname}: PACK -> ROOT/pack")
        else:
            print(f"  [--] {fname}: no change needed")

# Final structure
print(f"""
  {len(moved)} folders restored to root.

  FINAL STRUCTURE (GitHub Pages compatible):
  MNetv1/
    builder/          SACRED - build machinery
    kernel/           SACRED - JS source of truth
    shell/            -> vsavytsk1.github.io/Mnetv1/shell/  [LIVE]
    tree/             -> vsavytsk1.github.io/Mnetv1/tree/   [LIVE]
    pack/             -> vsavytsk1.github.io/Mnetv1/pack/   [LIVE]
    research/         -> vsavytsk1.github.io/Mnetv1/research/ [LIVE]
    logs/             -> vsavytsk1.github.io/Mnetv1/logs/   [LIVE]
    Gsndbx3testClrsMath/ -> /Gsndbx3testClrsMath/           [LIVE]
    docs/             -> /docs/ (no live URLs, fine here)
    index.html        -> vsavytsk1.github.io/Mnetv1/        [LIVE]
    about.html        -> vsavytsk1.github.io/Mnetv1/about   [LIVE]
    BUILD_TRACE.log
    README.md LICENSE

  RULE: never move shell/ tree/ pack/ research/ logs/ away from root.
  GitHub Pages = root. Period.
""")

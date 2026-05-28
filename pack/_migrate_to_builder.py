"""
_migrate_to_builder.py
======================
ONE-TIME migration. Moves all builder machinery to /builder/.
Run once. Keeps every trace. Never deletes originals until confirmed.

Structure after:
  MNetv1/
    builder/                ← ALL build machinery
      build_holly7.py       ← master builder
      navierCrunch.py       ← GPU solver
      navierKolmogorov.py   ← Kolmogorov variant
      genesis_gpu.py        ← genesis GPU
      genesis_pack.py       ← genesis pack
      hexCompTest/          ← ALL archived builds + logs
      patches/              ← all _patch_*.py history
      spooky_warning/       ← build_warning.py
      gate/                 ← rebuild_gate.py
    kernel/                 ← JS modules (source of truth, stays)
    pack/                   ← HTML output (holly7.html etc, stays)
    shell/                  ← public HTML shells (stays)
    tree/                   ← math tree versions (stays)
"""
import shutil, time
from pathlib import Path

ROOT    = Path(__file__).parent.parent
PACK    = ROOT / "pack"
BUILDER = ROOT / "builder"
KERNEL  = ROOT / "kernel"
SHELL   = ROOT / "shell"

BUILDER.mkdir(exist_ok=True)
(BUILDER / "patches").mkdir(exist_ok=True)
(BUILDER / "hexCompTest").mkdir(exist_ok=True)

moved  = []
kept   = []

def move(src, dst):
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            print(f"  [SKIP already exists] {dst.name}")
            kept.append(str(dst))
            return
        shutil.copy2(src, dst)
        moved.append(f"{src}  →  {dst}")
        print(f"  ✓ {src.relative_to(ROOT)}  →  {dst.relative_to(ROOT)}")
    else:
        print(f"  [MISSING] {src}")

print("=" * 60)
print("  MIGRATE TO builder/")
print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ── pack/ builders → builder/ ────────────────────────────────
move(PACK / "build_holly7.py",    BUILDER / "build_holly7.py")
move(PACK / "navierCrunch.py",    BUILDER / "navierCrunch.py")
move(PACK / "navierKolmogorov.py",BUILDER / "navierKolmogorov.py")
move(PACK / "genesis_gpu.py",     BUILDER / "genesis_gpu.py")
move(PACK / "genesis_pack.py",    BUILDER / "genesis_pack.py")

# ── pack/ patches → builder/patches/ ─────────────────────────
for p in sorted(PACK.glob("_patch*.py")):
    move(p, BUILDER / "patches" / p.name)
move(PACK / "_migrate_to_builder.py", BUILDER / "patches" / "_migrate_to_builder.py")

# ── pack/hexCompTest/ → builder/hexCompTest/ ─────────────────
src_hex = PACK / "hexCompTest"
if src_hex.exists():
    for f in sorted(src_hex.iterdir()):
        move(f, BUILDER / "hexCompTest" / f.name)

# ── shell builders → builder/ ────────────────────────────────
move(SHELL / "spooky_warning" / "build_warning.py", BUILDER / "build_warning.py")
move(SHELL / "gate" / "rebuild_gate.py",            BUILDER / "rebuild_gate.py")

# ── Update ROOT path in build_holly7.py ──────────────────────
bh7 = BUILDER / "build_holly7.py"
if bh7.exists():
    src = bh7.read_text(encoding="utf-8")
    # Was in pack/ (2 levels from ROOT), now in builder/ (also 2 levels from ROOT)
    # Path(__file__).parent.parent is the same — NO CHANGE NEEDED
    # But PACK output path must point back to pack/ for GitHub Pages HTML
    # Already: PACK = ROOT / "pack"  ← correct, no change needed
    # Just verify:
    if 'PACK   = ROOT / "pack"' in src or 'PACK         = ROOT / "pack"' in src:
        print("\n  ✓ PACK path in build_holly7.py already correct (ROOT/pack)")
    else:
        print("\n  [CHECK] verify PACK path in builder/build_holly7.py")

# ── Write migration log ───────────────────────────────────────
log = [
    f"migration: pack/ + shell/ builders → builder/",
    f"timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
    f"moved: {len(moved)} files",
    "",
    "FILES MOVED:",
]
for m in moved:
    log.append(f"  {m}")
log += [
    "",
    "ORIGINALS IN pack/ — still there until you git commit + verify.",
    "builder/build_holly7.py is now THE builder.",
    "",
    "RUN THE NEW BUILDER:",
    '  python builder/build_holly7.py',
    "",
    "VERSION: H7.1473.12.60 — THE number IS the math.",
]
(BUILDER / "MIGRATION.log").write_text("\n".join(log), encoding="utf-8")

print(f"\n  {len(moved)} files moved to builder/")
print(f"  Migration log: builder/MIGRATION.log")
print(f"\n  NEW COMMAND:")
print(f'  python builder/build_holly7.py')
print(f"\n  Originals in pack/ untouched until you git commit + verify.")
print("\nDONE.")

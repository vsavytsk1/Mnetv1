# ponderTheOrb

> *Nothing in here is compiled. Nothing in here is a dependency. These are the
> things that were true before the crate existed, kept where they can be stared
> at.*

`cargo` never looks in this folder. It is the inspiration shelf: the artifacts
that started `Gos`, plus the one artifact we are trying to reproduce. When the
question is "what are we even doing", the answer is on this shelf.

---

## THE ORB ITSELF

**`machinenet_eng_v2_0_master_control.html`** -- the ENG v2.0 master control
dashboard, as Chromium received it. 361 KB of HTML+JS produced by
`builder/build_eng_v2.py`.

This is not a keepsake. **It is the target.** The whole Rust visual lane exists
to paint this without a browser:

```text
  the old road :  build_eng_v2.py -> HTML+JS -> ??? -> Chromium -> ??? -> pixels
  the new road :  goldberg_kernel -> Canvas -> StretchDIBits -> pixels
```

Ponder it. Every panel in there is a thing that has to become integers.

*(Filed originally as `MachineNet - ENG v2.0 - MASTER CONTROL.html` with U+00B7
middle dots in the name. Renamed to ASCII on the move: a non-ASCII filename is
what produced a READ-FAIL in the paranoia sweeper at L186, and Curse 2 says keep
the glyphs out of the source layer. The bytes inside are untouched.)*

## THE CENSUS

**`MATH_LEDGER.md`** -- `math_census.py` over the whole cave, and the reason
this crate was written at all:

```text
  sims scanned                     2,333
  function definitions            70,224
  DISTINCT RULES (the closed set)  5,598
    of which are MATH              2,521
    of which are costume           3,077
  redundant characters        26,661,998   (89.9%)
  compression if kernel extracted   9.89x
```

`buildC60Faces()` appears in **249** sims. `vdot()` in **443**. The cave has been
rewriting the same thirteen rules for two thousand sims, and this ledger is the
measurement that says so. `goldberg_kernel` is those rules, once.

The line worth remembering: **"Everything else is those rules, permuted."**

## THE FIRST STONE

**`graphium.py`** -- the first file committed to `Gos`, before any Rust existed
("start of Gos for fun and giggles"). The graph layer in Python, kept exactly as
it landed. Path X: a frozen rung is never edited in place, only re-implemented
beside.

---

## WHY A SHELF AND NOT A DELETE

Path XII -- pass the scroll. A project that keeps only its current state teaches
the next mage nothing about the path. The census explains the crate's existence,
the dashboard defines its goal, and `graphium.py` is the shape of the first
thought. Delete those and `Gos` becomes a pile of correct files with no reason.

Nothing here is load-bearing. Everything here is why.

*P=12 . chi=2 . the price is always paid . always*

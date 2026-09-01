# builder/eng -- the ENG dashboard, versioned

The page: **`shell/eng_v2.0.html`** -> https://vsavytsk1.github.io/Mnetv1/shell/eng_v2.0.html

Three builders were sitting loose in `builder/`, **two of them writing the same
file**, and nothing recorded which one made the page that shipped. They are
frozen here by version. Path X: the highest number is current, the rest are
history and are never edited.

| file | writes | state |
|---|---|---|
| `v1_0_dashboard.py` | `shell/eng_v1.0.html` | **HISTORY.** Built from the `graph_sandbox_v5.1` template. Its output **no longer exists** in `shell/`. |
| `v2_0_clean.py` | `shell/eng_v2.0.html` | **HISTORY, and a collision.** Writes the same path as the live builder. Whichever ran last won and nothing said so. |
| `v2_0.py` | `shell/eng_v2.0.html` | **LIVE.** |

## Which one made the page that is up -- proven, not assumed

The page stamps itself, so this is a receipt rather than a guess:

```
<span class="build">H7.1473.12.60 · 2026-08-10 23:05:31</span>
<span class="git">git:0a9eae0</span>
```

`v2_0.py` was last committed 2026-08-10. That is the match.

## Run it

```powershell
py -3 builder/eng/v2_0.py
```

It scans the tree and prints what it found:

```
scanned 388 sims (archive) -> 179 shown on dashboard (latest per family)
```

**The move into this folder cost two lines and both were verified.** `ROOT` needed
a third `.parent`, and `sim_scan` needed the parent directory on `sys.path` --
it stays in `builder/` because more than the eng dashboard uses it. Proof the
move changed nothing: the builder was run before and after into a temp target,
and the two outputs are **366,838 bytes each with zero differing lines** except
the build stamp and git hash, which move every run by design.

---

## READ THIS BEFORE YOU RUN IT

**The live page has hand edits the builder does not know about.** Running
`v2_0.py` today would silently delete four cards:

```
ATTENTIUM_V0.1   ATTENTIUM_V0.2   ATTENTIUM_V0.3   DIFFUSIUM_V1.0
```

and add three the live page lacks:

```
ATTENTIUM_V0_3   DIFFUSIUM_BENCH_V1_0   GENESIS_V9.0
```

81 lines differ in total. Measured by generating into a temp file and diffing,
never by overwriting the page.

### Why it drifted, and why it is not simply a mistake

The builder is honest about being absolute:

```python
# Module cards: AUTO-DISCOVERED from disk (sim_scan). The builder is absolute --
SIMS  = sim_scan.discover()
CARDS = sim_scan.latest_only(SIMS)      # newest per family
# The key -> url map ... also auto-built from the same scan (no drift).
```

`latest_only` shows **one card per family**. On 2026-08-18 someone hand-added
eleven lines to the OUTPUT so that all three ATTENTIUM versions stay visible --
which is Path X applied to the dashboard, the version journey on display, and
is a thing the builder currently **cannot express**.

So this is a policy disagreement wearing the costume of a bug. Note the two
naming conventions, which is the tell: the scanner generates `ATTENTIUM_V0_3`
from a filename; the hand-added card says `ATTENTIUM_V0.3` and carries a
written description no scanner could produce.

### The three honest ways forward -- pick one, do not drift

1. **Teach the builder to pin.** A small curated list of `(key, name, blurb)`
   that is shown IN ADDITION to `latest_only`, so a family can keep its whole
   journey on the board and a card can carry prose. The builder becomes able to
   say what the hand-edit was saying.
2. **Change the policy to show all versions** for families that ask for it, by
   a marker on disk rather than by editing the output.
3. **Accept the loss** and regenerate, giving up the three ATTENTIUM cards and
   the curated descriptions.

Until one is chosen, **`shell/eng_v2.0.html` is the artifact of record and the
builder is not.** That inversion is the whole reason this file exists: a
generator that no longer generates what ships is worse than no generator, and
the danger is that it still *looks* authoritative (RUSTIUM R13 -- the
completeness of the plumbing is the camouflage).

---

## The next version

Copy `v2_0.py` to `v2_1.py` and edit the copy. Never edit a frozen one. The
highest number is current, and the page's own build stamp is what proves which
builder made it.

*P=12 . chi=2 . a generator that no longer generates what ships is not a generator.*

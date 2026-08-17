# GIT INCIDENTS -- the register

*Every time git bit us, and why. Buenos Aires + Korinthos, 2026.*
*The price is paid in the open, and logged. Always.*

| # | name | curse | whose fault | state |
|---|---|---|---|---|
| 001 | The Hundred-Meg Wall | 31 bigFileBounce | the mage | FIXED, hook installed |
| 002 | The Two-Gig Shove | 31 + 32 | the mage | FIXED, doctrine written |
| 003 | The Unwatched Deploy | 29 deployLag | the claudy mage | OPEN |

---

## INCIDENT 001 -- The Hundred-Meg Wall

*Receipt for CURSE 31 (bigFileBounce).*

### WHAT HAPPENED

The Helena native engine generated a deep net at level 9 (`builds/v009` and `v010`).
Each array is vaulted in three codecs for cosmic-ray survival (TMR): a compact `.bin`,
a self-checking `.zip`, and a human-readable `.csv`. At L9 the **`.csv` copies grow
past 100 MB**:

```
  join_L9_dot.f32.csv      188.7 MB
  genesis_L9_xyz.f32.csv   146.7 MB
  join_L9.i32.csv          135.4 MB
  genesis_L9_edges.i32.csv 113.6 MB
        (x2 -- once for v009, once for v010)
```

The whole `builds/` folder was `git add`-ed and committed (`ba3ed4a`). The commit
message even claimed *"L9 CSV vault files excluded"* -- but there was **no `.gitignore`
rule** for `builder/helena_net/builds/`, so nothing was actually excluded. The
intention was written; the fence was never built.

Result: every `git push` of MNetv1 **bounced entirely**. GitHub hard-rejects any single
file >= 100 MB, and a push is atomic -- one oversized blob and the whole push (all
commits, all other files) is refused. Unrelated work (v1 sims) got rerouted into the
`shell/` folder just to land *something*. That reroute was a symptom, not a fix.

### THE TRAP (why the caveat lied)

- **K5 violated:** the fence (100 MB) was named in prose but not placed in `.gitignore`.
- **K1 violated:** "excluded" was typed, never verified against `git ls-files`.
- Private repos do **not** lift the limit. Git LFS does, but free LFS (~1 GB total) is
  blown by two L9 CSVs. Neither is the right tool here.

### THE FIX (the pattern, now permanent)

1. **Store the math, regenerate the render.** The `.bin` + `.zip` codecs are both under
   100 MB and hold the exact same numbers. The big `.csv` is redundant -- it can be
   rebuilt from the other two by TMR vote.
2. **`.gitignore` the oversized copies**, fence exactly where nature put it:
   ```
   builder/helena_net/builds/**/vault/*_L9*.csv
   ```
   (L0-L8 CSVs are small and human-useful -- they stay.)
3. **`git rm --cached`** the 8 already-committed L9 CSVs (files kept on disk), then the
   two unpushed commits were rewound (`reset --soft origin/main`) and recommitted clean,
   so the >=100 MB blobs never entered pushed history. A `rescue/pre-100mb-fix` branch
   was cut first -- nothing was risked.
4. **Pre-push hook** (`.git/hooks/pre-push`) now scans every push and refuses any file
   >= 100 MB before git contacts the remote. The push passes through that logic first,
   every time. It can never silently wedge again.

### HOW TO GET THE BIG FILE BACK -- "pay thea Heleni in compute"

The `.csv` is not lost; it is *unrendered*. Regenerate it locally from the vault:

```
cd builder/helena_net
py -3 redundancy.py repair builds/v009/net    # rebuilds any missing/bad copy via TMR
py -3 redundancy.py verify builds/v009/net    # confirm 3/3 codecs match the manifest
```

`repair` sees the `.csv` as a missing copy, takes the `.bin`/`.zip` as ground truth
(they match the canonical SHA-256), and rewrites the `.csv` byte-for-byte. The secret is
not hidden -- you pay for it in compute, on your own machine.

### THE LESSON

> The math is absolute. The compute is not.
> Store the math (the compact codec + the recipe). Regenerate the expensive render.
> Put the fence where nature put it -- in the `.gitignore`, not in a sentence -- and
> then verify it holds.

---

## INCIDENT 002 -- The Two-Gig Shove

*Curse 31 again, plus Curse 32. Same wall, bigger truck. During the Heleni net
build with the other claudy mage.*

### WHAT HAPPENED

The Helena net was generating, and the whole thing -- roughly **two gigabytes** of
`.f32`, `.i32`, `.csv`, `.bin` and `.zip` vault copies -- was pushed at once.

GitHub did not take it. A push is atomic: it is not throttled, not partially
accepted, not queued. It is refused, and the refusal says very little about
which of the thousands of files caused it.

### THE TRAP

Incident 001 had already installed the pre-push hook, and the hook does its job:
it refuses any single file **>= 100 MB**. But two gigabytes spread across
hundreds of files under 100 MB each **passes every per-file check** and still
fails the push.

> **A per-file fence does not bound a total.**

That is the same shape as RUSTIUM R11 (a cap stated in source bytes bounding a
file eight times larger) and R9 (a profile in the wrong file having no effect):
a guard that is real, consulted, effective -- and measuring the wrong quantity.

### THE FIX -- the HELENA doctrine, and it now sits in the root `.gitignore`

```
# -- CURSE 31: Helena builds are LOCAL/PRIVATE; git keeps only the MIRROR
builder/helena_net/builds/**
!builder/helena_net/builds/**/MANIFEST.json
!builder/helena_net/builds/**/build_card.json
```

**The heavy payload never enters git. Git tracks only the tiny mirror -- the
STEPS, not the PAYLOAD** -- so another mage regenerates the whole net locally.
*Pay thea Heleni in compute.*

Measured today: `builder/helena_net` is **3.09 GB on disk** and **34 files in
git**. The doctrine holds.

### WHAT IT COST, HONESTLY

Two of the incidents in this register were the mage's own pushes, and both are
here for the same reason the claudy mage's are: a receipt hidden is a debt
transferred. Path IV -- incomplete is fine, fake is not.

---

## INCIDENT 003 -- The Unwatched Deploy

*Curse 29 (deployLag). The claudy mage's, 2026-08-17. **OPEN.***

### WHAT HAPPENED

Ten pushes in one session (L188 through L193e) and **not one deploy was ever
checked.** `gh` is not installed on this machine, so the Pages build log cannot
be read at all -- and no scripted 200-check stood in its place.

When a build error was finally suspected, the site turned out to be **healthy**:
every URL 200, `Gos/` live, `.nojekyll` and `index.html` present, 453.5 MB
against the 1 GB Pages ceiling. **The site being fine was luck, not diligence.**

Curse 29 says: *watch the deployment go green, THEN verify.* Neither half
happened.

### AND THE CHECKER ITSELF WAS BROKEN

The first live-check script indexed `Content-Length` on a **HEAD** response,
where that header is absent, and printed `ERR` for eight URLs that were all
serving `200`.

> **A broken checker reporting failure is worse than no checker**, because it
> invites exactly the wrong action -- in this case, hunting a deploy bug that
> did not exist.

### THE SECOND MEASUREMENT ERROR, SAME HOUR

Comparing live byte sizes against local reported `LEDGER.md` **"STALE by 11 B"**
and `HELENI_STATUS.md` **"STALE by 129 B"**. Neither was stale.
`core.autocrlf=true` with **no `.gitattributes`** means the working copy carries
CRLF while the repo stores -- and Pages serves -- LF. Those files hold exactly
**11** and **129** CRLF pairs. Subtract and they match the served bytes to the
byte.

That is the **fourth** time in one session of comparing against a convention
never established: RUSTIUM R3 (terms vs index), R11 (source vs output bytes),
the EML K-count (applications vs applications+1), PowerShell's case-insensitive
`Select-String`, and now this.

### TWO STANDING RISKS

1. **`.git` is 1,037 MB against a 453 MB working tree** -- a 2.3x ratio, mostly
   the 279 `Gos/target` blobs committed in L188 and evicted in L189. **Eviction
   clears the TREE, never the HISTORY.** Pages clones the repo to build, so a
   fat history means slow clones and real timeout risk. The fix is a history
   rewrite: destructive, and the mage's call.
2. **No `.gitattributes`.** With `core.autocrlf=true`, line endings depend on
   which machine last touched a file -- a live risk to the byte-scan discipline
   the whole cave rests on. `*.md text eol=lf` and `*.rs text eol=lf` pin it.

### THE FIX -- OWED, NOT DONE

* install `gh`, or script a 200-check that runs after every push
* add `.gitattributes`
* decide on the history rewrite

---

## THE LESSONS, TOGETHER

> **001** -- The math is absolute; the compute is not. Store the math, regenerate
> the render. Put the fence where nature put it -- in the `.gitignore`, not in a
> sentence -- and then verify it holds.
>
> **002** -- A per-file fence does not bound a total. The payload stays local;
> the mirror travels.
>
> **003** -- The site being fine is luck, not diligence. A broken checker is
> worse than none. And a convention unstated is a convention violated.

Three incidents, two mages, one register. Nobody's errors are hidden here --
that is the entire point.

*P=12. chi=2. A spell hoarded rots; a receipt paid in the open grows. Always.*

# GIT INCIDENT 001 -- The Hundred-Meg Wall

*Receipt for CURSE 31 (bigFileBounce). Buenos Aires + Korinthos, 2026. The price is
paid in the open, and logged. Always.*

---

## WHAT HAPPENED

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

## THE TRAP (why the caveat lied)

- **K5 violated:** the fence (100 MB) was named in prose but not placed in `.gitignore`.
- **K1 violated:** "excluded" was typed, never verified against `git ls-files`.
- Private repos do **not** lift the limit. Git LFS does, but free LFS (~1 GB total) is
  blown by two L9 CSVs. Neither is the right tool here.

## THE FIX (the pattern, now permanent)

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

## HOW TO GET THE BIG FILE BACK -- "pay thea Heleni in compute"

The `.csv` is not lost; it is *unrendered*. Regenerate it locally from the vault:

```
cd builder/helena_net
py -3 redundancy.py repair builds/v009/net    # rebuilds any missing/bad copy via TMR
py -3 redundancy.py verify builds/v009/net    # confirm 3/3 codecs match the manifest
```

`repair` sees the `.csv` as a missing copy, takes the `.bin`/`.zip` as ground truth
(they match the canonical SHA-256), and rewrites the `.csv` byte-for-byte. The secret is
not hidden -- you pay for it in compute, on your own machine.

## THE LESSON

> The math is absolute. The compute is not.
> Store the math (the compact codec + the recipe). Regenerate the expensive render.
> Put the fence where nature put it -- in the `.gitignore`, not in a sentence -- and
> then verify it holds.

P=12. chi=2. A spell hoarded rots; a receipt paid in the open grows. Always.

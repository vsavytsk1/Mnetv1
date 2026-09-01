# ALIEN TK

> Three sims rescued from an abandoned clone, 2026-09-01.

**Status:** RECEIVED, not adopted. Nothing here has been read, audited or
re-rendered by this cave yet. They are parked in `lens/` because that is where
unproven things live.

## Where they came from

`C:\PythonDevs\CoolAlienTech\` was a stale clone of `vsavytsk1/SpookyPrimes`
(6 commits behind, tip an ancestor of the live one -- pure redundancy). But four
`.html` files sat loose in the **parent** folder, outside the clone entirely, so
they were in no git anywhere. All dated 2026-05-26.

```text
  v1_0_alien_tk_info_graph.html    12,531 B  471b87faecd73cbf
      "INFORMATION GRAPH -- No Dimensions, Only Topology"
  v1_0_alien_tk_matter_cube.html   12,366 B  55a549cce1375725
      "MATTER CUBE -- Mass/Energy/Information Tradeoff"
  v1_2_alien_tk_matter_cube.html   14,100 B  60c4f6657d99ad01
      "MATTER CUBE v1.2 -- Observer/Cube Perspectives"
```

Copied byte-identical; sha256 verified on both sides, 3/3 -- and those hashes
survive git, which took one more rule. The files arrived CRLF, and this repo's
`text=auto eol=lf` would have stored them LF: a fresh clone would then hand back
different bytes than were received, and the hashes above would quietly stop
matching. `.gitattributes` now carries `lens/alien_tk/*.html -text`, so the blob
in git is the byte-for-byte artifact. Verified: staged blob sha256 == disk
sha256 == the hashes listed above.

## The fourth one was already ours

`wiggle_craft.html` was the fourth file, and it is **not** here. It is already
`shell/wiggle_craft.html`, tracked, and served live at `IO_PAGES.md` line 419 --
byte-identical to the CoolAlienTech copy. Checked by hashing all 710 `.html`
files in the repo and looking it up, rather than trusting the filename. Copying
it would have made a second master of a page that already ships.

## The naming

`v1_0` / `v1_2` are not invented. `matter_cube_v1.2.html` says v1.2 in its own
`<title>`; the other two carry no version, so they take `v1_0` as the earlier
rung. The `matter_cube` pair keeps one name across two versions because that is
what they are -- two rungs of one sim, not two sims.

## Tracked, by narrow exception

`lens/` is gitignored under WIP discipline -- *no public push until the kernel is
proven*. These three are the exception, and the reason is specific: they were
sitting loose in `CoolAlienTech/`, **outside** the stale clone, in no git
anywhere. That folder is being deleted. Leaving them under the blanket ignore
would have made one disk the only copy of files nobody has a second of.

So `.gitignore` re-includes exactly this folder:

```text
  lens/*
  !lens/alien_tk/
```

Note the shape. The rule used to be `lens/`, which excludes the *directory* --
git stops there and never descends, so a negation under it does nothing at all
and does it silently. Excluding the *contents* with `lens/*` is what makes the
exception possible. Everything else in `lens/` stays ignored, verified.

**Tracked is not promoted.** These are backed up, not adopted: not in `shell/`,
not in `IO_PAGES.md`, not served, not audited. The parent README's rule still
governs -- *no portal module promotion until >=3 working sims compose cleanly*.

---

*Received 2026-09-01 from a folder about to be deleted. Not ours to claim yet.*
*P=12. chi=2. The price is always paid.*

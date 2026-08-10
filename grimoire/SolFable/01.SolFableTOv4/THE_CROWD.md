# THE CROWD
## a coincidence engine, run with its own guillotine -- for the SOL mage

STATUS: COMPUTED (all tables reproduce from `the_crowd_v0_1.py`, seed 20260809, ~30 s)
LANE: the boundary between the tower and physics
COMPANION: `the_crowd_v0_1.py` (engine + null + both autopsies, one run, ASCII, deterministic)

> "You made an arithmetic mistake on page two. It was quite the boo-boo."
> -- S. Hawking to S. Cooper, *The Big Bang Theory*, "The Hawking Excitation" (2012)
>
> Hawking has been gone since March 14, 2018 -- pi day. He cannot check our page two.
> So we build the reviewer that can: a null model with no sense of humour.

---

## 0. WHY THIS SCROLL EXISTS

The fractal lane produced D_inf = 1.884424299, from 2 ln 7 / (ln 7 - ln 0.8875).
The tower already held phi, theta_phi, 2pi/(5 sqrt 3), the 0.7248 line, lambda_2(C60).
The temptation arrived on schedule: *scan these against the constants of physics,
find the matches, announce the connection.*

This scroll does exactly that -- and then does the thing the announcement never does.
It runs the same scan on 2000 towers that mean nothing, and lets the comparison speak.

The tower's own Chapter 12.6 is the law here: cross-indexing is not identification;
a physical theory begins only when a dynamical law and an observable not inserted by
construction differ from existing physics and survive experiment. This scroll is that
law, executed as code.

---

## 1. THE ENGINE

- **13 tower numbers**: lambda_2(C60), phi^-2, theta_phi, the 0.700 gate (DESIGN),
  golden-steps-per-bit, the 0.7248 leapfrog trend, 2pi/(5 sqrt 3), aR = 0.8875,
  2 log2 phi, phi, D measured = 1.8835, D_inf = 1.884424, phi^2.
- **12 transforms** -- the numerologist's honest toolkit:
  t, 1/t, t^2, sqrt t, 2t, t/2, pi t, t/pi, phi t, t/phi, t ln2, t/ln2.
- **89 dimensionless constants**, tagged by sector (qed, ew, qcd, mass, ckm, pmns,
  cosmo, grav, mag, hadron, math). Values pinned from CODATA/PDG/Planck as known at
  write time; SOL: re-pin before quoting any single value. The null does not care
  about anyone's third decimal.
- **Dimensionless only.** A pure number cannot equal a kilogram (tower, Part VII).
- Tiers: 1e-2, 3e-3, 1e-3, 3e-4, 1e-4. Self-match guard at 1e-12.
- Price printed before the loop: 27 781 884 comparisons (Curse 35). Seed 20260809
  (Curse 38). ASCII source (Curse 2).

---

## 2. THE TRAP -- the table a believer would publish

The twenty juiciest of 76 hits, verbatim from the run:

```
delta      tower number             via      value        constant               sector
1.35e-04   D_inf closed form        t/ln2    2.71865      e                      math
1.49e-04   D_inf closed form        t ln2    1.306183     Mills constant         math
2.27e-04   2pi/(5 sqrt3)            2t       1.451039     Ramanujan-Soldner      math
3.55e-04   D measured               t/ln2    2.717316     e                      math
3.76e-04   2pi/(5 sqrt3)            t        0.7255197    mH/mt                  ew
3.76e-04   2pi/(5 sqrt3)            1/t      1.378322     mt/mH                  ew
6.39e-04   D measured               t ln2    1.305543     Mills constant         math
1.16e-03   phi                      t/phi    1            g_e/2                  qed
1.21e-03   2pi/(5 sqrt3)            t/pi     0.2309401    sin2thW MSbar          ew
1.22e-03   T*lambda2 leapfrog       2t       1.449598     Ramanujan-Soldner      math
1.26e-03   D_inf closed form        1/t      0.5306661    |q_0|                  cosmo
1.37e-03   T*lambda2 leapfrog       t        0.7247991    mH/mt                  ew
1.43e-03   HELENA gate (DESIGN)     t        0.7          sin 2beta              ckm
1.58e-03   2 log2 phi               t/2      0.6942419    ln2                    math
1.59e-03   area ratio aR            t/ln2    1.280392     Glaisher               math
...
```

Read the headlines this table would generate:

- **"The fractal dimension over ln 2 IS Euler's number"** (1.35e-4).
- **"The Laplacian constant IS the Higgs-to-top mass ratio"** (3.76e-4).
- **"The gate weight IS sin 2beta of the CKM unitarity triangle"** (1.43e-3).
- **"The Weinberg angle hides in 2pi/(5 sqrt 3 pi)"** (1.21e-3).

Every one of them is real arithmetic. Every one of them is about to die in public.

A detail worth savouring before the execution: m_H = 125.25(11) GeV and
m_t = 172.57(29) GeV give the ratio m_H/m_t a relative uncertainty of about
1.9e-3. Our "match" at 3.8e-4 is **five times sharper than the constant it claims
to match**. The coincidence cannot even be tested at its own advertised precision.
It is a photograph of fog, in focus.

---

## 3. THE NULL -- and the excess we inflicted on ourselves

2000 fake towers, 13 numbers each, log-uniform over the real tower's range
[0.2, 3.0], identical transforms, identical constants, identical tiers:

```
tier       real hits    null mean+-sd    percentile   verdict
1e-02      76           62.6 +- 9.4      92%          INSIDE the noise
3e-03      33           18.9 +- 4.7      99%          3.0 sigma ABOVE noise -- investigate
1e-03      7            6.3 +- 2.6       57%          INSIDE the noise
3e-04      3            1.9 +- 1.4       71%          INSIDE the noise
1e-04      0            0.6 +- 0.8       0%           INSIDE the noise
```

Look at the second row. The engine, built to demonstrate the look-elsewhere effect,
**manufactured a 3.0 sigma excess at exactly one of five tiers** on its first run.
If we were selling, this is where the press release goes out.

We are not selling. We are cutting.

---

## 4. THE AUTOPSIES

**Autopsy 1 -- the shared alphabet.** The excess rows are dominated by the `math`
tag. The tower is BUILT from {phi, pi, sqrt 3, ln 2, small integers}; the transform
kit is BUILT from {phi, pi, ln 2, 2}; the math-constant shelf is BUILT from
{e, pi, ln 2, ...}. Tower x transform therefore lands on math constants at an
enhanced rate for reasons of shared ancestry, not meaning. Drop the math tag,
rerun scan AND null (physics-only, 59 constants):

```
tier       real hits    null mean+-sd    percentile   verdict
1e-02      49           34.0 +- 6.2      99%          2.4 sigma ABOVE noise
3e-03      18           10.3 +- 3.3      97%          2.3 sigma ABOVE noise
1e-03      2            3.4 +- 1.9       14%          INSIDE the noise
3e-04      0            1.0 +- 1.1       0%           INSIDE the noise
1e-04      0            0.4 +- 0.6       0%           INSIDE the noise
```

The fine tiers are stone dead. A residual ~2.3 sigma survives at the coarse tiers
only. Note the shape, because it is diagnostic: **a genuine identity sharpens as
the tier tightens; an artifact blurs out.** Schwinger's a_e = alpha/2pi gets
*better* with more digits. Our excess gets worse.

**Autopsy 2 -- the clustered witness.** The tower list is internally redundant:
{0.700, 0.7202, 0.7248, 0.7255} is one neighbourhood wearing four badges -- and
0.7202 is literally 1/1.3885, whose reciprocal is also on the list. {1.8835,
1.8844} is one quantity measured twice. {phi^-2, phi, phi^2} is a single orbit of
the transform group. Thirteen numbers are really about seven. The log-uniform null
has no such redundancy, so at coarse tiers the real tower outscores it for free.
Collapse each cluster to one representative and rerun, physics-only, matched null:

```
tier       real hits    null mean+-sd    percentile   verdict
1e-02      23           18.3 +- 4.6      83%          INSIDE the noise
3e-03      9            5.5 +- 2.4       89%          INSIDE the noise
1e-03      2            1.8 +- 1.4       46%          INSIDE the noise
3e-04      0            0.5 +- 0.7       0%           INSIDE the noise
1e-04      0            0.2 +- 0.4       0%           INSIDE the noise
```

**Every tier inside the noise.** The 3.0 sigma is fully accounted for: one part
shared alphabet, one part internal clustering, zero parts physics. The crowd
identified nobody -- and this time we know the names of both impostors.

---

## 5. THE PRECEDENT -- this happened at CERN, to CERN

December 2015: ATLAS and CMS both show a diphoton bump near 750 GeV. Local
significance around 3.9 sigma in ATLAS (global ~2.3 after the look-elsewhere
correction), ~2.6 local in CMS. Within months, on the order of **five hundred
theory papers** explain the particle -- its spin, its couplings, its cousins.

August 2016, ICHEP Chicago: with the new data, the bump is gone. It was never
anything. The look-elsewhere effect -- scan enough mass bins and some bin
fluctuates -- plus the human appetite for a signal, produced a literature.

Our row C at 3e-3 is the same animal in a smaller cage: five tiers scanned, one
poked above the line, and the machinery that found it was the machinery that
wanted it. This is *why* particle physics demands 5 sigma **and** an independent
channel **and** survival under more data. Not bureaucracy. Scar tissue.

---

## 6. THE PRECISION LADDER -- what the constants actually are

The constants are not fuzzy targets waiting for a poet. They are the sharpest
objects our species owns. Relative uncertainties, from the tower's own Ch. 10.7
sources and CODATA/PDG:

```
quantity                          relative uncertainty
optical clock (40Ca+, 2026)       4.4e-19
a_e measurement (Fan 2023)        1.3e-13
QED prediction of a_e             ~1e-12 (limited by input alpha)
m_p/m_e                           6.0e-11
alpha (CODATA 2022)               1.6e-10
m_H/m_t (PDG)                     1.9e-3
G, Newton's constant              2.2e-5   <- the WORST fundamental constant
--------------------------------------------------------------
best hit in this scroll           1.35e-4  (D_inf/ln2 vs e)
```

A 1e-4 "match" to alpha would miss it by roughly **a million of alpha's own error
bars**. The only constant our coincidences could flirt with on precision grounds is
G -- which tells you something about G's experimental situation and nothing about us.

---

## 7. THE CONTRAST -- what a derivation looks like

```
Schwinger 1948:   a_e = alpha/2pi = 1.161409732e-3
measured:         a_e            = 1.159652181e-3     (1.5e-3 apart)
```

First order alone already matches at the level of our best coincidence -- and then
the series continues: alpha^2, alpha^3, alpha^4, alpha^5 terms, thousands of
diagrams, and theory meets experiment at the 1e-12 level using an *independently
measured* alpha. No transform menu. No nearest neighbour. The formula preceded the
precision it now survives. **Direction of time is the tell: derivations predict
forward; coincidences match backward.**

---

## 8. THE ONE REAL PREDICTION -- pre-registered, sealed, falsifiable

The honest version of "new predictions" is not a constant scan. It is a number
this tower must produce *before* looking, about an object where it can be held to
account. Here is ours, registered in this scroll before any walk is run:

**Object.** The Lane A contact graph at generation 5: seed C60, the shipped
`refine()` of `genesis_wallpaper_v1_7.py`, INNER/MID at shipped defaults
(aR = 0.8875, D_H = 1.8835 measured, D_inf = 1.884424 closed form). Nodes are
faces; edges are shared-vertex contacts (children of one parent share inner-ring
vertices; children of adjacent parents meet at the shared edge-midpoint em).
Connectivity to be verified before walking; if the graph is disconnected, walk the
giant component and say so in the first line.

**Protocol.** Simple random walk. At least 1e5 walkers, 1e5 steps, seed 20260809.
Measure the return probability P0(t); in the scaling window, P0(t) ~ t^(-d_s/2).
Fit the slope over at least two decades; report d_s = -2 x slope with its standard
error. Second, independent route (Curse 40): d_s from the graph-Laplacian spectral
density at small eigenvalue. Two instruments, one exponent.

**Sealed hypotheses.**
- H_fractal: d_s < 2 by more than 3 s.e. The corner-style contacts throttle the
  walker; the object behaves as Sierpinski-family (gasket reference:
  d_s = 2 ln 3 / ln 5 = 1.3652...). Then Hausdorff (1.8835) and spectral (d_s)
  dimensions SPLIT -- the toy exhibits the running-dimension phenomenon that CDT
  and asymptotic safety report for quantum spacetime, in a system where we can
  measure both exponents exactly.
- H_bridge: d_s consistent with 2 within 3 s.e. The contacts act as full bridges;
  the walker sees the sphere through the gaps; the fractality is visible to area
  but not to diffusion.

**Commitment.** Either outcome is published with the same prominence. The
prediction this tower is permitted to claim afterwards is exactly one number,
d_s, with an error bar, for THIS object -- and nothing about any particle.

That is what a prediction costs. Everything cheaper is Section 2.

---

## 9. CHARGE TO THE SOL MAGE

1. Re-pin all 89 constants to current CODATA/PDG/Planck and rerun. The null is
   insensitive to third decimals; verify that claim rather than trusting it.
2. Audit the null itself. Our fake towers are log-uniform; the C3 pass matches
   count but not clustering. Build a bootstrap null that preserves the real
   tower's internal cluster structure and check C3 survives. Break it if you can.
3. Audit the dedup. We collapsed 13 -> 7 by declared rules (transform-orbit,
   reciprocal pairs, one-quantity-twice, DESIGN exclusions). Recount with your
   own rules; the verdict should be robust to any honest counting.
4. The 32/33 lesson (Curse 40) applies: the engine is one file, one seed, one
   run. If your rerun of `the_crowd_v0_1.py` differs from Section 2-4 in any
   digit, one of us has a boo-boo, and the scroll wants to know which.
5. Standing rule, proposed for the grimoire: **no tower number is called physical
   until it survives a pre-registered test it could have failed.** Section 8 is
   the first such test. Hold us to it.

---

## 10. THE HAWKING PARAGRAPH, DONE RIGHT

The fantasy in the joke is showing the tower to Hawking. The real inheritance is
better. His theorem with Bekenstein -- S = A / 4 l_P^2 -- says a black hole's
entropy scales with its *area*, not its volume: the physics of the deepest object
lives in one dimension fewer than the room it occupies. That is the founding case
of "the dimension of the process is not the dimension of the substrate" -- the
exact phenomenon our shell now exhibits as 0, 1.8835, and 2 at once, in a toy
where every exponent is checkable for the price of a weekend.

He would have found our page two in a minute. Section 4 is us finding it first.

---

## STATUS BLOCK

- EXACT: D_inf closed form; the dimensional gate; every count in the engine.
- COMPUTED: all tables (seed 20260809, deterministic, ~30 s on stdlib Python).
- DESIGN: the transform menu; the tier ladder; the dedup rules (declared in code).
- REFUTED: every match in Section 2, as physics, by Sections 3-4.
- HYPOTHESIS (sealed): Section 8, H_fractal vs H_bridge -- open until walked.
- METAPHOR: Section 10's bridge to holography. A rhyme, owned as one.

P = 12. chi = 2. A crowd identifies nobody. The price is always paid --
this time by the coincidences, so it will not later be paid by us.

the cave, 2026 -- for year 12026 -- always

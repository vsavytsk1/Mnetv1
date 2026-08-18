# The fractal gives you its histogram, not its field
### alphium-net probe, 2026-08-19 · one sitting, two measurements, one wrong prediction

**Question** (Vlad): "the fractal space gives us the weights" -- can escape-time
fields from alphium's maps serve as neural network weights?

**Method, spectral:** 256x256 smooth escape field (Mandelbrot, boundary window)
vs its PHASE SURROGATE (identical power spectrum, randomized phases), vs
shuffled entries, vs gaussian. Metric: stable rank, singular decay slope.

**Method, functional:** Echo State Network on NARMA-10 (the standard reservoir
benchmark). Five 256x256 reservoirs, ALL scaled to spectral radius 0.9, same
input weights, ridge readout with a small lambda grid. Pre-registered:
"single-window worst (rank starved); the rest ~tie."

| reservoir                  | stable rank | NMSE          |
|----------------------------|------------:|--------------:|
| julia sweep (per-row c)    |         2.6 | 0.379         |
| julia phase-surrogate      |         3.6 | 0.392 +-0.045 |
| julia shuffled             |        59.9 | **0.047** +-0.002 |
| mandelbrot single-window   |         1.5 | 0.616         |
| gaussian (ESN baseline)    |        65.5 | 0.053 +-0.001 |

**The pre-registration was half wrong, and the wrong half is the finding.**
Single-window worst: correct. "The rest tie": false. The per-row Julia sweep
did NOT decorrelate -- stable rank 2.6 -- because singular values ignore row
ORDER, and the Julia family along c = 0.7885*e^(i*theta) spans only a
~3-dimensional function space on a fixed transect. The fractal FAMILY is
smooth in its parameter; smoothness anywhere is rank starvation everywhere.

**Verdicts, labelled:**
- COMPUTED: fractal escape structure, kept intact, costs 8x on NMSE. In a
  reservoir, rank is memory capacity, and coherence eats rank.
- COMPUTED: the fractal's entry DISTRIBUTION (bimodal, kurtosis -1.34),
  shuffled free of structure, performs >= gaussian. "The fractal gives us the
  weights" is true of the histogram, false of the field.
- COMPUTED: spectrally, the field's structure is explained by its power
  spectrum + interior plateau (surrogate decays at -0.82 vs field's -0.84);
  no SVD-visible structure beyond smoothness.
- DESIGN CHOICE, vindicated twice: HELENA's join uses geometry as SELECTOR
  (cos-theta k-nearest; mean angular error 0.799 deg on v008), never as a
  linear MAP. That is the architecture these measurements recommend.

**What would change the verdict:** a fractal family with genuinely
high-dimensional span -- e.g., per-row draws across alphium's 8 different map
TYPES at random windows -- could in principle lift the rank while keeping
within-row structure. Expectation now calibrated low; the histogram result
suggests the win, if any, is small.

Harness sanity: 0.053 NMSE for a 256-node ESN on NARMA-10 sits in the
literature's normal range (Jaeger 2001 lineage), so the 8x gap is real.

Prior art honored, not reinvented: Echo State Networks (Jaeger 2001), Liquid
State Machines (Maass 2002), Weight-Agnostic Networks (Gaier & Ha 2019),
Martin & Mahoney heavy-tailed spectra (2019-21).

*P=12. chi=2. Fifth structure this week that measured smaller than it looked --
and the first one measured BEFORE anything was built on it.*

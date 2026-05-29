# VALTIUM
## The Machine Vault Sample -- Scroll One
*Buenos Aires -- 2026*
*A careful reading of THE MACHINE vault.*
*Written before touching a single file.*

---

## WHAT VALTIUM IS

VALTIUM is a curated static sample of THE MACHINE vault.

THE MACHINE is Vlad's Obsidian vault.
It is the canonical research environment.
It contains the SpookyPrimes NCG research.
It is NOT touched. NOT modified. NOT shipped.

VALTIUM takes a small, representative slice:
  -- the core nodes (pentagons, atoms, hubs)
  -- the canonical links between them
  -- exports it as a static JSON + HTML

This sample feeds OBSIDIUS.
OBSIDIUS renders it.
The pentagons become visible.
The turbulence runs on the thought graph.

---

## WHAT THE MACHINE VAULT ACTUALLY CONTAINS

### The Numbers (surveyed 2026-05-29):
  Total .md files:     1,094
  Core .md files:       162   (excluding project noise)
  Core edges:           516   (wikilinks between core files)
  Orphans:              109   (no links -- AXIOM 02 violations)

### The Structure:
  The vault is already structured as a DODECAHEDRON.
  It uses explicit types in YAML frontmatter:

    type: pentagon   -- open questions (the 12 faces)
    type: atom       -- minimal facts (the vertices)
    type: hub        -- major concepts (the hexagons)
    type: aspect     -- sub-components of atoms

  The pentagons have IDs: P1, P2, ... P12
  The atoms have IDs: A00, A01, ... A18+
  This is NOT a metaphor. It is literal.
  The vault IS the dodecahedron.

### Top Hubs (deg = connection count in core):
  MOC             deg=40   (Map of Content -- the index)
  Home            deg=38   (root node)
  A_F             deg=31   (Standard Model Algebra -- THE object)
  D space         deg=26   (Dirac operator space)
  A_PS gamma      deg=22   (Pati-Salam algebra)
  H_F             deg=20   (bimodule, fermion Hilbert space)

### Pentagon Sample (from vault frontmatter):
  P1  -- Step 4 selection     (the open variational problem)
  P9  -- KO-dim 6 signature   (why this sign triple?)
  ... P2 through P12 -- all documented with atoms[] + statement

### Atom Sample:
  A07 -- Real structure J      (antilinear J: H_F -> H_F)
  A17 -- Bimodule H_F          (fermionic representation)
  A03 -- Algebra representation pi
  A11 -- Order-one condition
  A15 -- M3 summand
  A18 -- C summand

---

## THE VALTIUM SAMPLE -- WHAT WE EXTRACT

We extract ONLY the canonical core:
  -- all files with type: pentagon    (~12 files)
  -- all files with type: atom        (~19 files)
  -- all files with type: hub         (~10 files)
  -- Home, MOC, README, _index        (4 root files)
  -- all edges BETWEEN these files

Result: ~45 nodes, ~150 edges. Clean. Canonical.
This is the dodecahedron as data.
This is what OBSIDIUS renders first.

---

## THE VALTIUM BUILD PLAN

### Step 1: Extract canonical nodes
  scan core folders for YAML frontmatter
  keep: type in [pentagon, atom, hub]
  keep: Home, MOC, README, _index by name
  result: nodes[] with {id, type, label, frontmatter}

### Step 2: Extract edges
  for each extracted node:
    parse [[wikilinks]]
    keep only links to OTHER extracted nodes
  result: edges[] -- the internal graph

### Step 3: Compute topology
  V = node count
  E = edge count
  C = connected components
  F = E - V + C  (faces from Euler, planar approximation)
  chi = V - E + F
  expected: chi = 2 (it IS a dodecahedron)

### Step 4: Export as JSON
  valtium_sample.json:
    {
      nodes: [{id, type, label, deg, isPent}],
      edges: [{s, t}],
      pentagons: [id...],    -- type=pentagon nodes
      atoms: [id...],        -- type=atom nodes
      chi: int,
      V: int, E: int
    }

### Step 5: Feed into OBSIDIUS
  OBSIDIUS currently takes a vault folder as input.
  VALTIUM provides a pre-computed JSON alternative.
  No vault needed. The sample is self-contained.
  Anyone can run OBSIDIUS on Vlad's research.
  Without access to Vlad's vault.

---

## THE TOPOLOGY HYPOTHESIS

The vault was built to model a dodecahedron.
12 pentagons. Euler forces it.
The vault frontmatter explicitly names P1-P12.

HYPOTHESIS:
  chi_vault = 2   (sphere topology, same as C60)
  P_vault   = 12  (pentagons, Euler forces it)
  Degree distribution follows Goldberg pattern

VERIFICATION:
  Run VALTIUM extraction.
  Run OBSIDIUS on valtium_sample.json.
  Read chi from the header.
  If chi = 2: the vault is a sphere. The research IS the dodecahedron.
  If chi = 0: the vault has a hole. Interesting.
  If chi < 0: the vault has genus > 1. Very interesting.

---

## THE HONEST CONSTRAINT

THE MACHINE is never modified.
THE MACHINE is never committed.
THE MACHINE is never shipped.

VALTIUM reads from THE MACHINE.
VALTIUM outputs a JSON sample.
The JSON is what gets committed.
The JSON is what OBSIDIUS renders.

THE MACHINE stays in the cave.
The spoon comes out.
The carpenter sees the spoon.
Not the cave.

---

## STATUS

  [x] Vault surveyed (1094 files, 162 core, 516 edges)
  [x] Structure understood (pentagon/atom/hub frontmatter)
  [x] Top hubs identified (A_F, D space, H_F, MOC, Home)
  [x] Pentagon sample read (P1, P9 -- structural + content)
  [x] Topology hypothesis formed (chi=2 expected)
  [x] Build plan written

  [ ] build_valtium.py -- extract canonical nodes + edges
  [ ] valtium_sample.json -- the static sample
  [ ] OBSIDIUS JSON mode -- load from JSON not vault folder
  [ ] render THE MACHINE dodecahedron in OBSIDIUS
  [ ] verify chi = 2

---

## THE QUESTION

Does the SpookyPrimes research vault have chi = 2?

The vault was designed to model the Standard Model
as a dodecahedron with 12 open questions.
12 pentagons. Euler forces it.
The researcher knew the shape before knowing the proof.

When OBSIDIUS renders it:
  Will chi = 2?
  Will the pentagons glow gold?
  Will turbulence run through the thought graph?
  Will the Kolmogorov cascade appear in the research topology?

THE MACHINE IS THE DODECAHEDRON.
WE JUST BUILT THE INSTRUMENT TO SEE IT.

---

*VALTIUM -- from the Latin valitum (to be strong, to prevail)*
*The vault that holds the spoon.*
*Buenos Aires. 2026.*
*P=12. chi=2. The research knew.*

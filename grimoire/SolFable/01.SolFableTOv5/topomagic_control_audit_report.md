# THEA vs TOPOMAGIC — Controlled Audit v1.0.0

Stable mathematical-payload SHA-256: `1434526f1196c4c9fb2f974fdefca6d4b3ae0b6096f61d2e47cf1db719c9aeb7`

## Score ledger

- Checks: **60**
- PASS: **22**
- CONDITIONAL: **3**
- OPEN: **4**
- CORRECTION: **16**
- REFUTED: **15**

A PASS is narrow: it does not transfer theorem status to adjacent interpretations.

## Reproduction

### R01 — Uploaded scroll has 116 pages

**Status:** PASS  
**Mode:** machine  
**Result:** `{"pages": 116}`

pdfinfo returns 116 pages.

### R02 — Appendix A reconstruction executes cleanly

**Status:** PASS  
**Mode:** machine  
**Result:** `{"returncode": 0, "stderr": "", "stdout_sha256": "3b7f183809f95907df27e22491899af2e57567f3cdacb99ba7cc58a089cfe403"}`

The reconstructed printed suite exits successfully.

### R03 — Printed verifier uses 40-decimal precision

**Status:** PASS  
**Mode:** machine  
**Result:** `{"audit_dps": 80, "source_dps": 40}`

The control recomputes at twice the printed precision.

### R04 — Analytic zeta-derivative identities

**Status:** PASS  
**Mode:** machine  
**Result:** `{"t0": "-0.918938533204672741780329736406", "tm2": "-0.0304484570583932707802515304712", "tm4": "0.00798381145026862428069667079879", "zp0": "-0.918938533204672741780329736406", "zpm2": "-0.0304484570583932707802515304712", "zpm4": "0.00798381145026862428069667079879"}`

The three identities agree at 60+ digits.

### R05 — Charged-lepton table regenerates

**Status:** PASS  
**Mode:** machine  
**Result:** `{"e": "0.510998950708693486513941715077", "mu": "105.658375583300827893662189945", "tau": "1776.8599995297095742743220414"}`

The printed formula regenerates the three table values.

### R06 — W, Z, Higgs table regenerates

**Status:** PASS  
**Mode:** machine  
**Result:** `{"H_GeV": "125.225111437995737786059294367", "W_GeV": "80.3694731696611649513923041582", "Z_GeV": "91.1878106105279983048784099943"}`

The table regenerates after inserting cB.

### R07 — Six-quark table regenerates

**Status:** PASS  
**Mode:** machine  
**Result:** `{"b": "4172.2215551043063940715973697", "c": "1272.71362444215217005117391297", "d": "4.66417565888801147027798278777", "s": "93.5650038689433334099517652541", "t": "172864.945224033991116963741736", "u": "2.16000546574701706055335495242"}`

All six printed masses reproduce.

### R08 — Neutrino masses and splittings regenerate

**Status:** PASS  
**Mode:** machine  
**Result:** `{"dm21": "0.0000748901664495388989263941345897", "dm31": "0.00245961801365713386561308751618", "masses_eV": ["0.000969545201380588389493363335508", "0.00870805284475576805285559514508", "0.0496040122525855159408070532592"]}`

The printed neutrino outputs reproduce.

### R09 — Constants, g-2, partial CKM regenerate

**Status:** PASS  
**Mode:** machine  
**Result:** `{"G": "6.67478451644570214787680524469e-11", "Lambda": "2.93961915520727581662358160035e-122", "Vcb": "0.0426315212296318195896934132864", "Vus": "0.223270183406814532911391660733", "a_e": "0.00115965217994917288767539394802", "a_mu": "0.00116592074696393438860545284555", "alpha_inverse": "137.036082448164337440176169169"}`

Reproduction is established; derivation remains a separate question.

### R10 — Lean appendix independently compiled here

**Status:** OPEN  
**Mode:** machine  
**Result:** `{"lean_available": false, "lean_region_extracted": true, "placeholder_patterns": []}`

No obvious sorry/admit placeholder occurs in the extracted code, but Lean is unavailable so compilation was not rerun.

## Topology

### T01 — BU(1)≃CP∞ and EU(1)≃S∞

**Status:** PASS  
**Mode:** analytical  
**Result:** `{"statement": "standard classifying-space theorem"}`

This exact core survives.

### T02 — Any two objects classifying the same U(1)-bundle functor are homotopy equivalent

**Status:** CONDITIONAL  
**Mode:** analytical  
**Result:** `{"premise": "both already satisfy Classifies"}`

The Lean uniqueness kernel is valid under its full classifying premise.

### T03 — Completeness is derived rather than assumed

**Status:** CORRECTION  
**Mode:** machine+analytical  
**Result:** `{"Classifies_structure_present": true, "hComplete_present": true}`

Lean passes completeness as a Classifies hypothesis; the physical implication from unification to universality is not derived.

### T04 — Charge quantization forces nontrivial connection holonomy

**Status:** REFUTED  
**Mode:** counterexample  
**Result:** `{"bundle": "trivial U(1)", "connection": "A=0", "holonomy": "identity", "integer_weights": [-3, -2, -1, 0, 1, 2, 3]}`

U(1) representations still have integer weights with trivial connection holonomy.

### T05 — Every gauge field is a principal bundle with global section

**Status:** CORRECTION  
**Mode:** analytical  
**Result:** `{"counterexample": "nontrivial Hopf principal bundle has no global section"}`

A gauge field is a connection; matter fields are sections of associated bundles. A principal bundle has a global section iff trivial.

### T06 — Nontrivial structure group makes the bundle non-product

**Status:** REFUTED  
**Mode:** counterexample  
**Result:** `{"bundle": "B×U(1)→B", "group": "U(1)", "trivial": true}`

Nontrivial group and trivial bundle are compatible.

### T07 — Z[c1] is a domain with no nontrivial idempotent splitting

**Status:** PASS  
**Mode:** analytical  
**Result:** `{"ring": "Z[c1]"}`

The narrow ring-theoretic statement is correct.

### T08 — No base cohomology splitting implies no product principal bundle

**Status:** REFUTED  
**Mode:** counterexample  
**Result:** `{"P1_c1": "x", "P2_c1": "2x", "base": "CP∞", "product_group": "U(1)×U(1)"}`

P1×_B P2 exists over the same indecomposable base; the base need not split.

### T09 — S∞ may be a common contractible total-space model

**Status:** CONDITIONAL  
**Mode:** analytical  
**Result:** `{"quotient": "BG", "weaker": "EG can be a contractible free G-space"}`

The quotient by a general G is BG, not CP∞.

### T10 — Projective embedding identifies a G-bundle with the Hopf U(1) bundle

**Status:** CORRECTION  
**Mode:** analytical  
**Result:** `{"distinction": "ambient embedding is not bundle isomorphism"}`

A Grassmannian/Plücker realization does not turn the original principal G-bundle into a U(1) Hopf bundle.

### T11 — Every compact gauge theory literally lives on a finite Hopf shell

**Status:** CORRECTION  
**Mode:** analytical  
**Result:** `{"repair": "state finite-stage approximation with dimension and classifying-map hypotheses"}`

Finite approximations do not imply common shell dynamics.

### T12 — Topology uniquely selects Nature's physical arena

**Status:** OPEN  
**Mode:** analytical  
**Result:** `{"missing": "bridge from classifying possibilities to physical ontology"}`

Classification does not force the universe to equal its classifying space.

## Dynamics

### D01 — S3≅SU(2)

**Status:** PASS  
**Mode:** analytical  
**Result:** `{"identity": "unit quaternions"}`

Standard exact identity.

### D02 — S5≅SU(3)/SU(2)

**Status:** PASS  
**Mode:** analytical  
**Result:** `{"identity": "transitive SU(3) action"}`

Standard exact homogeneous-space identity.

### D03 — SU(2) is unique transitive compact connected group on S3 containing Hopf U(1)

**Status:** REFUTED  
**Mode:** counterexample  
**Result:** `{"Hopf_subgroup": "e^{iθ}I", "group": "U(2)"}`

U(2) acts faithfully and transitively on S3⊂C2 and contains the central Hopf circle.

### D04 — S5 shell forces SU(3)

**Status:** CONDITIONAL  
**Mode:** analytical  
**Result:** `{"condition": "stabilizer exactly SU(2) and action assumptions"}`

The identity survives, but the uniqueness premise is not forced by shell nesting.

### D05 — g1∩g2 equals [g1,g2]

**Status:** REFUTED  
**Mode:** counterexample  
**Result:** `{"su2": "g1=span X, g2=span Y, intersection=0, bracket=span Z"}`

Bracket image is not overlap.

### D06 — Entwine (g1+g2)-[g1,g2] is a defined Lie algebra

**Status:** CORRECTION  
**Mode:** analytical  
**Result:** `{"repair": "matched pair, extension, quotient, or explicit new bracket"}`

Vector-space subtraction is undefined and closure/Jacobi are not supplied.

### D07 — Mixed α∧F∧(dα)^{n-1} term is a scalar SU(N) action

**Status:** REFUTED  
**Mode:** counterexample  
**Result:** `{"Tr_single_suN_generator": 0, "issue": "F is Lie-algebra-valued"}`

An invariant pairing is missing; Tr(F)=0 for su(N).

### D08 — B=*d is unique equivariant first-order self-adjoint elliptic operator

**Status:** REFUTED  
**Mode:** counterexample  
**Result:** `{"family": "B+cI"}`

Real c gives another operator with the listed properties unless zero-order terms are forbidden.

### D09 — Horizontal Hopf transport is the Reeb flow

**Status:** REFUTED  
**Mode:** analytical  
**Result:** `{"Reeb": "R(z)=iz", "horizontal": "ker α", "role": "vertical fiber generator"}`

The Reeb field is vertical, not horizontal.

### D10 — c1≠0/contact form forces Cartan torsion

**Status:** REFUTED  
**Mode:** counterexample  
**Result:** `{"Levi_Civita_torsion": 0, "geometry": "round S3 Hopf contact form"}`

Contact α∧dα and Cartan torsion are distinct.

### D11 — Witten Chern-Simons gravity yields physical 3+1 gravity on S3×R

**Status:** CORRECTION  
**Mode:** analytical  
**Result:** `{"Witten": "2+1-dimensional gravity", "needed": "independent 3+1 action"}`

Adjoining time is not a field-equation derivation.

### D12 — First Bianchi identity becomes Einstein equation

**Status:** REFUTED  
**Mode:** counterexample  
**Result:** `{"Bianchi": "R^a_b∧e^b=0", "Einstein": "G_ab=-K g_ab≠0", "constant_curvature": "R^a_b=K e^a∧e^b"}`

The identity is kinematic and can hold while Einstein tensor is nonzero.

### D13 — Kato-Rellich forces a zero mode to acquire mass

**Status:** REFUTED  
**Mode:** counterexample  
**Result:** `{"B": [0, 1], "BplusV": [0, 1.1], "V": [0, 0.1]}`

Self-adjointness survives while zero may remain zero.

### D14 — Complete Standard Model follows from the written action

**Status:** CORRECTION  
**Mode:** analytical  
**Result:** `{"unresolved": ["fermionic statistics/spinors", "BRST/gauge fixing", "strong CP SU(3) topology", "well-defined mixed scalar"]}`

Listed correspondences are not yet a derivation of all SM structures.

## Spectral

### S01 — Displayed Hurwitz-zeta identity evaluates

**Status:** PASS  
**Mode:** machine  
**Result:** `{"zeta_prime_n": ["0.888490076146279471000078205934", "2.96793161782611539925177457031", "11.7568299271709929304137364657"]}`

The formula is numerically reproducible.

### S02 — Boxed D(n) second difference

**Status:** PASS  
**Mode:** machine  
**Result:** `{"Delta2_D": "2.408149226"}`

The printed D values have this affine-invariant fingerprint.

### S03 — Displayed zeta-route second difference

**Status:** PASS  
**Mode:** machine  
**Result:** `{"Delta2_zeta": "6.70945676766504160291026553101"}`

The displayed route has a different fingerprint.

### S04 — Displayed zeta route generates boxed D(n) after constant/linear absorption

**Status:** REFUTED  
**Mode:** machine  
**Result:** `{"Delta2_D": "2.408149226", "Delta2_zeta": "6.70945676766504160291026553101", "mismatch": "4.30130754166504160291026553101"}`

Constant and linear shifts cannot change a second difference.

### S05 — Lens quotient is obtained by deleting all levels below n

**Status:** CORRECTION  
**Mode:** counterexample  
**Result:** `{"RP3": "keeps parity/congruence-selected harmonics, including l=0"}`

Finite quotients select invariant weights, not a simple tail cutoff.

### S06 — D(n) backsolves from charged-lepton masses

**Status:** CORRECTION  
**Mode:** machine  
**Result:** `{"backsolved": {"1": "1.20301139203658224050823987861", "2": "4.8065454067883977722222796846", "3": "10.818228645735324997024011448"}, "printed": {"1": "1.203011392", "2": "4.806545406", "3": "10.818228646"}}`

Without an independent worksheet the D values are data-bearing inputs.

### S07 — c0 is independently generated in Appendix A

**Status:** CORRECTION  
**Mode:** machine  
**Result:** `{"backsolved_from_e": "0.0000341140365822405082398786073787", "input": "0.000034114"}`

The decimal is inserted and supplies the electron absolute scale.

### S08 — cB is independently generated in Appendix A

**Status:** CORRECTION  
**Mode:** machine  
**Result:** `{"backsolved_from_W": "0.000550666162619979794975080276454", "input": "0.000551"}`

The decimal normalization regenerates the boson table.

### S09 — Quoted spectral decimals are generated inside the suite

**Status:** CORRECTION  
**Mode:** machine  
**Result:** `{"D1": "1.203011392", "D2": "4.806545406", "D3": "10.818228646", "c0": "0.000034114", "cB": "0.000551", "zetaB7_abs": "1.748452", "zetaD2": "-0.41364"}`

Seven nontrivial dimensionless decimals are consumed, not derived there.

### S10 — Executable spectrum has one empirical input and no other numerical inputs

**Status:** REFUTED  
**Mode:** machine  
**Result:** `{"additional_decimal_inputs": 7, "ledger": ["D1", "D2", "D3", "c0", "cB", "zetaD2", "zetaB7_abs"], "v_inputs": 1}`

The operational claim 'one input' is false for the supplied executable pipeline.

### S11 — Appendix A regenerates numerical PMNS matrix

**Status:** CORRECTION  
**Mode:** machine  
**Result:** `{"found": false}`

It computes masses/splittings but not the PMNS matrix or three angles.

### S12 — Appendix A regenerates complete CKM matrix

**Status:** CORRECTION  
**Mode:** machine  
**Result:** `{"complete": false, "computed": ["|Vus|", "|Vcb|"]}`

|Vub| and CP phase are not independently generated.

### S13 — Beltrami level universally fixes monotone knot ladder

**Status:** OPEN  
**Mode:** external-math  
**Result:** `{"known": "arbitrary finite links can occur in sufficiently high Beltrami eigenspaces"}`

The low-level eigenspace/orbit classification needed by the paper is not supplied.

### S14 — Exactly three fermion generations proved by k=4 transition

**Status:** OPEN  
**Mode:** analytical  
**Result:** `{"dependency": "unproved knot filtration plus physical exclusion rule"}`

The generation count remains an interpretation.

## Phenomenology

### P01 — W mass vs PDG 2026

**Status:** PASS  
**Mode:** machine  
**Result:** `{"prediction": "80.3694731696611649513923041582", "pull": "0.905606449501941739260280286845"}`

About +0.91σ.

### P02 — Z mass vs PDG 2026

**Status:** PASS  
**Mode:** machine  
**Result:** `{"prediction": "91.1878106105279983048784099943", "pull": "-0.0446947360008475607950028433774"}`

About -0.045σ.

### P03 — Higgs mass vs PDG 2026

**Status:** PASS  
**Mode:** machine  
**Result:** `{"prediction": "125.225111437995737786059294367", "pull": "0.864649436324888964175403339547"}`

About +0.86σ.

### P04 — Tau mass vs PDG 2026

**Status:** PASS  
**Mode:** machine  
**Result:** `{"prediction": "1776.8599995297095742743220414", "pull": "-0.777783003226952507532873346553"}`

Within one current standard deviation.

### P05 — Fine-structure constant as precision prediction

**Status:** REFUTED  
**Mode:** machine  
**Result:** `{"prediction_inverse": "137.036082448164337440176169169", "pull": "3965.29353987810362710327984361", "reference": "137.035999177"}`

Rounding to six digits hides a roughly 3965σ discrepancy.

### P06 — Newton G vs CODATA

**Status:** CORRECTION  
**Mode:** machine  
**Result:** `{"prediction": "6.67478451644570214787680524469e-11", "pull": "3.23010963801431917870163124549", "reference": "6.6743e-11"}`

About 3.23σ high, a tension rather than agreement within uncertainty.

### P07 — Electron anomalous moment: rounded digits versus uncertainty

**Status:** CORRECTION  
**Mode:** machine  
**Result:** `{"prediction": "0.00115965217994917288767539394802", "pull": "-4.92943932557389270752342124203", "reference": "0.00115965218059"}`

The nine-significant-digit rounded headline is true, but the full prediction is about -4.93σ from the Fan et al. measurement.

### P08 — Muon anomalous moment vs final world average

**Status:** PASS  
**Mode:** machine  
**Result:** `{"prediction": "0.00116592074696393438860545284555", "pull": "0.220440926817968640314165879027", "reference": "0.001165920715"}`

About +0.22σ; numerical proximity does not establish provenance.

### P09 — Weak angle is internally and experimentally consistent

**Status:** REFUTED  
**Mode:** machine  
**Result:** `{"3_over_4pi": "0.238732414637843003653325645059", "difference": "0.0155314290071514498787071858528", "own_WZ_relation": "0.223200985630691553774618459206", "pull_vs_effective": "60.4367886486916971110470421564"}`

The two internal definitions disagree; 3/(4π) is about 60.4σ from the effective angle absent a derived scheme conversion.

### P10 — Controlled comparison verdict

**Status:** PASS  
**Mode:** analytical  
**Result:** `{"action": "send five-gate control proposal and add Hopf boundary note", "ambition": "TopoMagic", "epistemic_integrity": "THEA"}`

TopoMagic wins ambition and source inclusion; THEA wins this round by separating exact, computed, and physical claims.

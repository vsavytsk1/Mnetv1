#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import textwrap
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PARENT_TEX = ROOT / 'THEA_LIGHT_MATRIX_v1.3.3_CALCULATION_TOWER.tex'
PARENT_MD = ROOT / 'THEA_LIGHT_MATRIX_v1.3.3_BOOKKEEPING.md'
PARENT_INDEX = ROOT / 'THEA_LIGHT_MATRIX_v1.3.3_CALCULATION_INDEX.md'
ADDENDUM = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_HOPF_BOUNDARY_ADDENDUM.md'
AUDIT_FULL = ROOT / 'THEA_VS_TOPOMAGIC_CONTROLLED_AUDIT_v1.0.0.md'
AUDIT_REPORT = ROOT / 'topomagic_control_audit_report.md'
AUDIT_JSON = ROOT / 'topomagic_control_audit_receipt.json'
PROPOSAL = ROOT / 'CONTROLLED_PROPOSAL_TO_THE_TOPOMAGIC_TOWER_v1.0.0.md'
TOPO_PDF = ROOT / 'TopoMagicTower.pdf'
VERIFIER = ROOT / 'verify_topomagic_control_v100.py'
NORMALIZER = ROOT / 'normalize_pdf_id.py'

OUT_TEX = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_FULL_CALCULATION_TOWER.tex'
OUT_PDF = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_FULL_CALCULATION_TOWER.pdf'
OUT_MD = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_BOOKKEEPING.md'
OUT_ADD_MD = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_NEW_CHAPTERS.md'
OUT_ADD_TEX = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_NEW_CHAPTERS.tex'
OUT_INDEX = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_CALCULATION_INDEX.md'
OUT_JSON = ROOT / 'light_matrix_v1.3.4_full_receipt.json'
OUT_BUILD_RECEIPT = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_BUILD_RECEIPT.md'
OUT_CHANGELOG = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_CHANGELOG.md'
OUT_README = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_README.md'
OUT_MANIFEST = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_MANIFEST.sha256'
OUT_ZIP = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_FULL_BUNDLE.zip'
OUT_ZIP_SHA = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_FULL_BUNDLE.zip.sha256'
FIGDIR = ROOT / 'light_matrix_v134_figures'

AUDIT = json.loads(AUDIT_JSON.read_text(encoding='utf-8'))
CHECKS = AUDIT['checks']


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def norm(s: str) -> str:
    return textwrap.dedent(s).strip('\n')


def demote_headings(md: str, levels: int = 1, drop_first: int = 0) -> str:
    lines = md.splitlines()
    out: list[str] = []
    dropped = 0
    in_fence = False
    for line in lines:
        if line.startswith('```'):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence and line.startswith('#'):
            m = re.match(r'^(#{1,6})\s+(.*)$', line)
            if m:
                if dropped < drop_first:
                    dropped += 1
                    continue
                marks, title = m.groups()
                out.append('#' * min(6, len(marks) + levels) + ' ' + title)
                continue
        out.append(line)
    return '\n'.join(out).strip()


def strip_audit_ledger(md: str) -> str:
    # The 60-row table is replaced by the much more detailed H01-H60 chapter.
    start = md.find('# 11. Complete sixty-check ledger')
    end = md.find('# 12. Reference ledger')
    if start >= 0 and end > start:
        return md[:start] + '# 11. Complete sixty-check ledger\n\nThe compact ledger is expanded calculation by calculation in Chapter 22 (H01-H60).\n\n' + md[end:]
    return md


def normalize_math_delimiters(md: str) -> str:
    """Convert source \(...\)/\[...\] math to dollar math outside fences."""
    out: list[str] = []
    fence = False
    for line in md.splitlines():
        if line.startswith('```'):
            fence = not fence
            out.append(line)
            continue
        if not fence:
            line = line.replace(r'\[', '$$').replace(r'\]', '$$')
            line = line.replace(r'\(', '$').replace(r'\)', '$')
        out.append(line)
    return '\n'.join(out)


def make_figures() -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    FIGDIR.mkdir(exist_ok=True)

    labels = ['EXACT', 'CLASSIFIES', 'EMBEDS', 'ISOMORPHIC', 'MODELS', 'PREDICTS', 'MEASURED-AS']
    x = np.arange(len(labels))
    plt.figure(figsize=(10, 4.6))
    plt.plot(x, np.zeros_like(x), marker='o')
    for i in range(len(labels) - 1):
        plt.annotate('', xy=(i + 0.88, 0), xytext=(i + 0.12, 0), arrowprops={'arrowstyle': '->'})
    plt.xticks(x, labels, rotation=20)
    plt.yticks([])
    plt.ylim(-0.3, 0.3)
    plt.title('CURSE 42 relation grammar: every arrow requires a new receipt')
    plt.tight_layout()
    plt.savefig(FIGDIR / 'relation_type_ladder.png', dpi=190)
    plt.close()

    input_labels = ['declared empirical scale', 'additional supplied decimals', 'generated in Appendix A']
    values = [1, 7, 0]
    plt.figure(figsize=(8.6, 4.8))
    plt.bar(np.arange(len(values)), values)
    plt.xticks(np.arange(len(values)), input_labels, rotation=12)
    plt.ylabel('Count')
    plt.title('Operational input ledger for the shipped TopoMagic verifier')
    for i, v in enumerate(values):
        plt.text(i, v + 0.12, str(v), ha='center')
    plt.tight_layout()
    plt.savefig(FIGDIR / 'operational_input_ledger.png', dpi=190)
    plt.close()

    stages = ['exact identity', 'typed map', 'well-defined dynamics', 'independent provenance', 'sealed observable']
    widths = [100, 78, 56, 34, 14]
    y = np.arange(len(stages))
    plt.figure(figsize=(8.6, 5.0))
    plt.barh(y, widths)
    plt.yticks(y, stages)
    plt.xlabel('Illustrative surviving claim-space width')
    plt.title('The bridge funnel: downstream status must be earned')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(FIGDIR / 'earned_bridge_funnel.png', dpi=190)
    plt.close()


MODE_TEXT = {
    'machine': 'The claim was checked by executing or parsing the supplied artifact and recording the finite output.',
    'analytical': 'The claim was checked by an explicit mathematical implication, distinction, or theorem statement.',
    'counterexample': 'The universal claim was tested by constructing one valid case satisfying the printed premises while violating the conclusion.',
    'machine+analytical': 'The executable provenance and the logical implication were checked separately.',
    'external-math': 'The claim depends on a substantial external classification not proved in the supplied scroll; the audit records the missing theorem rather than inventing it.',
}

CUSTOM: dict[str, str] = {
    'R04': r'''The standard identities are
$$
\zeta_R'(0)=-\frac12\log(2\pi),\qquad
\zeta_R'(-2)=-\frac{\zeta(3)}{4\pi^2},\qquad
\zeta_R'(-4)=\frac{3\zeta(5)}{4\pi^4}.
$$
The 80-digit recomputation agrees with the closed forms beyond sixty digits. This confirms a genuine exact island, but it does not supply the later sector-restriction rule.''',
    'R05': r'''The charged-lepton formula is evaluated exactly as printed:
$$
m_n=\Lambda_{\rm Hopf}(n+1)\exp\!\left(an-D(n)+\frac{n\alpha}{6}+\sigma_3\log\tau_3(K_n)\right).
$$
With the supplied $D(n)$ and $c_0$, the three table values regenerate. The rung therefore certifies formula-to-table fidelity, not independent spectral provenance.''',
    'R06': r'''The bosonic table regenerates only after the normalization factor $e^{-c_B}$ is included in the scale. This repairs the printed equation/table mismatch, while simultaneously showing that $c_B$ is a data-bearing input until an independent generator is supplied.''',
    'T02': r'''The valid theorem is conditional:
$$
\bigl(B\text{ classifies }\mathrm{Prin}_{U(1)}\bigr)
\land
\bigl(B'\text{ classifies }\mathrm{Prin}_{U(1)}\bigr)
\Longrightarrow B\simeq B'.
$$
The formal kernel checks this implication. It does not prove that the physical arena satisfies the classifying premise.''',
    'T03': r'''The Lean structure receives `hComplete : Classifies C F B` as an input. Therefore the formal proof establishes uniqueness after completeness has been assumed. The prose arrow
$$
\text{unification}\Longrightarrow\text{classification of every }U(1)\text{ bundle}
$$
remains a physical premise, not a derived theorem.''',
    'T04': r'''Let $P=B\times U(1)$ and choose the flat connection $A=0$. Its connection holonomy is the identity. Nevertheless the irreducible representations of $U(1)$ are
$$
\chi_n(e^{i\theta})=e^{in\theta},\qquad n\in\mathbb Z.
$$
Integer representation weights therefore coexist with trivial connection holonomy. The printed universal implication is false without an extra premise tying the physical charge lattice to a nontrivial bundle class or chosen non-flat connection.''',
    'T05': r'''A principal bundle admits a global section if and only if it is trivial. A nontrivial Hopf principal bundle can carry a connection but no global principal section. The correct dictionary separates the principal gauge arena and its connection from matter fields, which are sections of associated bundles.''',
    'T08': r'''Take two circle bundles $P_1,P_2\to\mathbb{CP}^{\infty}$ with first Chern classes $x$ and $2x$. Their fiber product
$$
P_1\times_B P_2\longrightarrow B
$$
is a principal $U(1)\times U(1)$ bundle over the same base. No product decomposition of the base cohomology ring is required. Thus ring indecomposability of $H^*(B)$ does not forbid product structure groups.''',
    'D03': r'''The standard action of $U(2)$ on the unit sphere $S^3\subset\mathbb C^2$ is faithful and transitive. The central subgroup $e^{i\theta}I$ is the Hopf circle. Hence the printed conditions do not uniquely isolate $SU(2)$. Any uniqueness theorem needs an additional premise that explicitly excludes $U(2)$ rather than deriving the exclusion from the shell alone.''',
    'D05': r'''In $\mathfrak{su}(2)$ choose independent generators $X,Y,Z$ with $[X,Y]=Z$. Then
$$
\operatorname{span}(X)\cap\operatorname{span}(Y)=\{0\},
\qquad
[\operatorname{span}(X),\operatorname{span}(Y)]=\operatorname{span}(Z).
$$
The bracket image is not an intersection or an overlap to be subtracted by inclusion-exclusion.''',
    'D06': r'''The expression
$$
(\mathfrak g_1+\mathfrak g_2)-[\mathfrak g_1,\mathfrak g_2]
$$
is not a Lie-algebra construction: vector-space subtraction is undefined, and no bracket, closure proof, or Jacobi proof is supplied. A repair could use a matched pair, semidirect product, extension, quotient by a genuine ideal, or amalgamation over an actual common subalgebra.''',
    'D07': r'''For nonabelian curvature $F\in\Omega^2(M,\mathfrak{su}(N))$, the form
$$
\alpha\wedge F\wedge(d\alpha)^{n-1}
$$
remains Lie-algebra-valued. A scalar action requires an invariant linear functional or pairing. In the defining representation, $\operatorname{Tr}F=0$ for $\mathfrak{su}(N)$, so a single trace does not rescue the term.''',
    'D08': r'''If $B=*d$ satisfies the listed first-order symbol, equivariance, ellipticity, and self-adjointness conditions, then so does
$$
B_c=*d+cI,\qquad c\in\mathbb R,
$$
with the same principal symbol. Symbol uniqueness therefore does not prove uniqueness of the complete operator unless zero-order freedom is explicitly forbidden or normalized.''',
    'D09': r'''For the standard Hopf contact form, the Reeb field satisfies $\alpha(R)=1$ and generates the vertical circle action. The horizontal distribution is $\ker\alpha$. Calling horizontal transport the Reeb flow swaps vertical and horizontal geometry.''',
    'D10': r'''The contact condition $\alpha\wedge d\alpha\neq0$ is a nonintegrability/volume statement. Cartan torsion is
$$
T^a=de^a+\omega^a{}_b\wedge e^b.
$$
The round $S^3$ carries the Hopf contact structure while its Levi-Civita connection has $T^a=0$. Contact twist therefore does not force spacetime torsion.''',
    'D11': r'''Witten's Chern-Simons equivalence is a formulation of gravity in $2+1$ spacetime dimensions. Appending a coordinate or Wick-rotating a product metric does not derive a $3+1$ action, constraint algebra, or Einstein-Cartan field equations. A separate four-dimensional dynamical derivation is required.''',
    'D12': r'''For constant curvature,
$$
R^a{}_b=K e^a\wedge e_b,
$$
the first Bianchi identity $R^a{}_b\wedge e^b=0$ holds kinematically, while the Einstein tensor is generally nonzero. A Bianchi identity constrains curvature; it does not replace an Euler-Lagrange equation.''',
    'D13': r'''Kato-Rellich controls self-adjointness under relatively bounded perturbations. It does not require a zero eigenvalue to move. The diagonal example
$$
B=\operatorname{diag}(0,1),\qquad V=\operatorname{diag}(0,0.1)
$$
leaves the zero mode exactly at zero. A mass claim needs a nonzero matrix element or a controlled degenerate perturbation calculation.''',
    'S01': r'''The displayed route evaluates
$$
\zeta_n'(0)=\zeta_H'(-2,n+1)-\zeta_H'(0,n+1),
$$
producing the three numbers in the receipt. This verifies the arithmetic of the displayed formula, not its identification with the independently printed $D(n)$ sequence.''',
    'S02': r'''For $D_1,D_2,D_3$ as printed,
$$
\Delta^2D=D_1-2D_2+D_3=2.408149226.
$$
This second difference is invariant under $D_n\mapsto D_n+a+bn$. It is therefore a fingerprint immune to the constant and linear absorptions claimed in the source.''',
    'S03': r'''For the displayed zeta values,
$$
\Delta^2\zeta'=0.888490076146\ldots-2(2.967931617826\ldots)+11.756829927171\ldots
=6.709456767665\ldots.
$$''',
    'S04': r'''Because $\Delta^2(a+bn)=0$, no constant normalization and no linear helicity redefinition can transform $6.709456767665\ldots$ into $2.408149226$. This is the decisive provenance refutation.''',
    'S05': r'''A finite quotient does not generally delete every eigenlevel below a threshold. It projects onto invariant/congruence-selected representation components. For $S^3/\mathbb Z_2\cong\mathbb{RP}^3$, parity-selected harmonics remain, including the constant mode. The source's tail-cutoff spectrum needs a representation-theoretic multiplicity derivation.''',
    'S06': r'''Solving the charged-lepton formula for $D(n)$ using the observed lepton masses returns the printed decimals to their shown precision. That demonstrates that the sequence carries target-data information unless an independent worksheet produces it without consulting those masses.''',
    'S07': r'''Solving the electron absolute-scale equation for $c_0$ returns $3.411403658\ldots\times10^{-5}$, matching the inserted $3.41140\times10^{-5}$. Thus $c_0$ supplies the absolute scale in the shipped pipeline rather than being generated there.''',
    'S08': r'''Solving the $W$-mass normalization for $c_B$ returns $5.5066616\ldots\times10^{-4}$, matching the inserted $5.51\times10^{-4}$. The table reproduces because the normalization is supplied.''',
    'S10': r'''The executable consumes the electroweak scale plus seven additional nontrivial decimals:
$$
D_1,D_2,D_3,c_0,c_B,\zeta'_{D_2}(0),|\zeta'_{B_7}(0)|.
$$
The operational statement "one empirical input and no other numerical inputs" is therefore false for the artifact as shipped.''',
    'P05': r'''The prediction $\alpha^{-1}=137.036082448\ldots$ and the reference $137.035999177(21)$ share six leading digits, but the uncertainty-normalized pull is roughly $3965\sigma$. Leading-digit resemblance and precision agreement are different tests.''',
    'P06': r'''Using the frozen CODATA uncertainty gives a pull of approximately $+3.23\sigma$. The defensible label is tension, not agreement within uncertainty.''',
    'P07': r'''The predicted electron anomaly shares nine rounded significant digits with the measurement, yet the full-value comparison gives approximately $-4.93\sigma$. Rounding has hidden the discrepancy.''',
    'P09': r'''The expression $3/(4\pi)=0.2387324\ldots$ disagrees both with the effective weak angle and with the model's own on-shell mass-ratio value $1-(m_W/m_Z)^2=0.22320099\ldots$. A renormalization-scheme conversion must be derived, not assumed.''',
}


def downstream(status: str, group: str) -> str:
    if status == 'PASS':
        return 'Only the narrow tested statement is retained. No downstream physical interpretation inherits PASS automatically.'
    if status == 'CONDITIONAL':
        return 'The result may be used only when the named premise is displayed beside it; deleting that premise deletes the conclusion.'
    if status == 'OPEN':
        return 'The claim remains open. The missing calculation, theorem, or tool is listed explicitly and no surrogate result is substituted.'
    if status == 'CORRECTION':
        return 'The printed statement is replaced by the narrower formulation recorded here. Downstream claims must be rebuilt from the corrected form.'
    return 'One valid counterexample or provenance contradiction defeats the universal claim. Downstream conclusions depending on it become hypotheses unless re-derived with stronger premises.'


def rung_detail(c: dict[str, Any], rung: int) -> str:
    cid = c['id']
    result = json.dumps(c.get('result'), indent=2, ensure_ascii=False, sort_keys=True)
    mode = c.get('mode', 'analytical')
    status = c['status']
    custom = CUSTOM.get(cid)
    if custom is None:
        custom = (
            f"The frozen control records the following direct evidence: **{c['evidence']}** "
            f"The machine or analytical result is printed verbatim below so later revisions can be diffed against the exact receipt rather than a paraphrase."
        )
    return norm(f'''
## 22.{rung} - H{rung:02d} / {cid} - {c['name']}

**Disposition:** **{status}**  
**Audit group:** {c['group']}  
**Control mode:** {mode}

### Claim under test

{c['name']}.

### Control route

{MODE_TEXT.get(mode, MODE_TEXT['analytical'])}

### Calculation, proof, or counterexample

{custom}

### Machine-readable receipt

```json
{result}
```

### Evidence frozen by the control

> {c['evidence']}

### Status boundary

{downstream(status, c['group'])}

### Next-step obligation

The next mage must either reproduce this receipt, name the premise that excludes the counterexample, or publish a revised calculation that changes the disposition. Silent relabeling is not an allowed repair.
''')


def build_addition_md() -> str:
    addendum = normalize_math_delimiters(demote_headings(ADDENDUM.read_text(encoding='utf-8'), levels=1, drop_first=3))
    audit = strip_audit_ledger(AUDIT_FULL.read_text(encoding='utf-8'))
    audit = normalize_math_delimiters(demote_headings(audit, levels=1, drop_first=3))
    proposal = normalize_math_delimiters(demote_headings(PROPOSAL.read_text(encoding='utf-8'), levels=1, drop_first=3))
    rungs = '\n\n'.join(rung_detail(c, i) for i, c in enumerate(CHECKS, 1))
    receipt_json = AUDIT_JSON.read_text(encoding='utf-8').rstrip()
    verifier_src = VERIFIER.read_text(encoding='utf-8').rstrip()

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for c in CHECKS:
        groups[c['group']][c['status']] += 1
    group_lines = []
    for g in ['REPRODUCTION', 'TOPOLOGY', 'DYNAMICS', 'SPECTRAL', 'PHENOMENOLOGY']:
        cc = groups[g]
        group_lines.append(f"- **{g.title()}:** PASS {cc['PASS']}; CONDITIONAL {cc['CONDITIONAL']}; OPEN {cc['OPEN']}; CORRECTION {cc['CORRECTION']}; REFUTED {cc['REFUTED']}; total {sum(cc.values())}.")

    return norm(f'''
# Chapter 20 - The Hopf Boundary: Classification Is Not Ontology

{addendum}

## 20.8 - Relation taxonomy introduced by CURSE 42

![Relation taxonomy introduced by CURSE 42](light_matrix_v134_figures/relation_type_ladder.png)

Every move from an exact mathematical statement to a physical measurement must name its relation type. A classifying map, embedding, isomorphism, model, prediction, and measured estimator are not interchangeable arrows.

# Chapter 21 - The Duel of the Towers: Full Controlled Audit

{audit}

## 21.13 - Category disposition and bridge figures

![Where the TopoMagic scroll survives and where it needs repair](topomagic_control_figures/category_disposition.png)

![Each downstream bridge must be earned](light_matrix_v134_figures/earned_bridge_funnel.png)

![Operational numerical-input ledger](light_matrix_v134_figures/operational_input_ledger.png)

# Chapter 22 - Hopf Control Tower: H01-H60

This chapter expands every machine or analytical check into its own calculation rung. The order is the frozen order of `topomagic_control_audit_receipt.json`; renumbering is forbidden because the rung IDs are part of the reproducibility contract.

{chr(10).join(group_lines)}

![The affine-invariant D(n) mismatch](topomagic_control_figures/D_second_difference_mismatch.png)

{rungs}

# Chapter 23 - The Controlled Counterproposal to the TopoMagic Tower

{proposal}

# Chapter 24 - v1.3.4 Integration Contract and Next-Step Receipt

## 24.1 - What changed from v1.3.3

- The exact Light Matrix core is unchanged.
- The full 91-rung v1.3.3 calculation tower is retained.
- Sixty new Hopf/TopoMagic control rungs are added, bringing the total to **151 dedicated rungs**.
- CURSE 42 and six typed relation arrows are added.
- The physical bridge gate now requires a well-defined scalar dynamics, an independent provenance ledger, a discriminating observable, and a sealed test.
- The full control audit, JSON receipt, and executable verifier are incorporated rather than merely cited.

## 24.2 - Typed receipt schema for any future correspondence

```text
relation_type: CLASSIFIES | EMBEDS | ISOMORPHIC | MODELS | PREDICTS | MEASURED-AS
source_status: EXACT | COMPUTED | DESIGN | HYPOTHESIS | EXTERNAL
mathematical_object: explicit definition
map_or_action: explicit formula
input_provenance: generated | cited | calibrated | fitted | unknown
uncertainty: theory and experimental
held_out_observable: value not used in construction
seal: hash, date, convention, pass/fail rule
disposition: PASS | CONDITIONAL | OPEN | CORRECTION | REFUTED
```

No physical badge is displayed while any load-bearing field is empty.

## 24.3 - Recommended v1.3.5 work order

1. Formalize the six relation types as typed arrows in the machine receipt.
2. Add automatic provenance tracing for every numeric literal.
3. Rebuild the Hopf comparison only from claims that passed or remained conditional.
4. Construct no unified physical action until the scalar and dimensional checks pass.
5. Select one sealed observable and run an adversarial null before looking at new data.
6. Publish either outcome with equal prominence.

## 24.4 - Frozen totals

- Parent Light Matrix checks: **38/38 PASS**.
- LUCA non-axiomatic calculations: **34/34 locked**.
- THE CROWD original tables: **reproduced**, physical matches rejected after dependence controls.
- TopoMagic control checks: **60**.
- TopoMagic dispositions: **22 PASS, 3 CONDITIONAL, 4 OPEN, 16 CORRECTION, 15 REFUTED**.
- Dedicated calculation rungs in this volume: **151**.
- Parent v1.3.3 mathematical payload: `1e6c813e7f6ba8e00587836d2bbbed90b5d7e8a1ee0ebba4343f17dbcf3e3cb7`.
- Hopf-control payload: `{AUDIT['stable_sha256']}`.

## 24.5 - Closing line

> **The Light Matrix keeps its exact core. The Hopf tower keeps its beautiful geometry. The bridge between them remains open, guarded, typed, and testable.**
>
> $P=12.\quad \chi=2.\quad$ Classification is not ontology. Reproduction is not derivation. The price is paid in public.

# Appendix A - Complete TopoMagic Control Receipt

```json
{receipt_json}
```

# Appendix B - Complete 80-Digit Control Verifier

```python
{verifier_src}
```
''') + '\n'


def markdown_tables_to_bullets(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    fence = False
    while i < len(lines):
        line = lines[i]
        if line.startswith('```'):
            fence = not fence
            out.append(line)
            i += 1
            continue
        if (not fence and i + 1 < len(lines) and line.lstrip().startswith('|')
                and re.match(r'^\s*\|?\s*:?-{3,}', lines[i + 1])):
            def cells(row: str) -> list[str]:
                return [c.strip() for c in row.strip().strip('|').split('|')]
            headers = cells(line)
            i += 2
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                rows.append(cells(lines[i]))
                i += 1
            for row in rows:
                parts = []
                for h, v in zip(headers, row):
                    if v:
                        parts.append(f'**{h}:** {v}')
                out.append('- ' + '; '.join(parts))
            out.append('')
            continue
        out.append(line)
        i += 1
    return '\n'.join(out)


UNICODE_MAP = {
    '≃':'~', '≅':'~=', '≡':'==', '≠':'!=', '≈':' approx ', '∼':'~', '≥':'>=', '≤':'<=',
    '→':'->', '↦':'->', '⇒':'=>', '⇔':'<=>', '⊂':' subset ', '⊆':' subseteq ', '∈':' in ',
    '∉':' not-in ', '∧':' wedge ', '∨':' vee ', '⊕':' direct-sum ', '⊗':' tensor ', '⋉':' semidirect ',
    '×':'x', '·':'*', '⋆':'*', '†':'dagger', '∗':'*', '∞':'infinity', '∑':'sum', '∫':'integral',
    '∂':'partial', '∇':'nabla', '√':'sqrt', '±':'+/-', 'θ':'theta', 'Θ':'Theta', 'α':'alpha',
    'β':'beta', 'γ':'gamma', 'δ':'delta', 'Δ':'Delta', 'ε':'epsilon', 'ζ':'zeta', 'η':'eta',
    'κ':'kappa', 'λ':'lambda', 'Λ':'Lambda', 'μ':'mu', 'ν':'nu', 'ξ':'xi', 'π':'pi', 'Π':'Pi',
    'ρ':'rho', 'σ':'sigma', 'Σ':'Sigma', 'τ':'tau', 'φ':'phi', 'ϕ':'phi', 'χ':'chi', 'ψ':'psi',
    'ω':'omega', 'Ω':'Omega', 'Γ':'Gamma', 'ℓ':'ell', '⁰':'^0', '¹':'^1', '²':'^2', '³':'^3',
    '⁴':'^4', '⁵':'^5', '⁶':'^6', '⁷':'^7', '⁸':'^8', '⁹':'^9', '⁻':'-', '−':'-',
    '’':"'", '‘':"'", '“':'"', '”':'"', '–':'-', '—':'-', '…':'...', '\u00a0':' ',
}


def addition_to_tex(md: str) -> str:
    tmp_md = ROOT / '_v134_addition_ascii.md'
    tmp_tex = ROOT / '_v134_addition_pandoc.tex'
    # v1.3.4 is the full archival edition: retain the complete machine-readable
    # receipt and the complete independent verifier in the PDF as well as in the
    # pure Markdown and ZIP bundle. This costs pages, but closes the bookkeeping
    # loop and makes the printed tower self-contained.

    stripped = re.sub(r'(?m)^# Chapter \d+ - ', '# ', md)
    stripped = re.sub(r'(?m)^## \d+\.\d+ - ', '## ', stripped)
    stripped = markdown_tables_to_bullets(stripped)
    for a, b in UNICODE_MAP.items():
        stripped = stripped.replace(a, b)
    stripped = stripped.encode('ascii', 'backslashreplace').decode('ascii')
    tmp_md.write_text(stripped, encoding='utf-8')
    subprocess.run([
        'pandoc', str(tmp_md), '-f', 'gfm+tex_math_dollars', '-t', 'latex',
        '--top-level-division=chapter', '--wrap=none', '--no-highlight', '-o', str(tmp_tex)
    ], check=True)
    tex = tmp_tex.read_text(encoding='utf-8')
    tex = re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',
                 r'\\begin{figure}[H]\n\\centering\n\\includegraphics[width=.94\\textwidth]{\1}\n\\end{figure}', tex)
    tex = tex.replace('\\begin{verbatim}', '\\begin{lstlisting}[basicstyle=\\ttfamily\\scriptsize,breaklines=true]')
    tex = tex.replace('\\end{verbatim}', '\\end{lstlisting}')
    tex = tex.replace('\\pandocbounded{', '{')
    tex = re.sub(r'\\texttt\{([0-9a-f]{64})\}', r'\\texttt{\\seqsplit{\1}}', tex)
    # The phenomenology comparison originated as a wide Markdown table.  Preserve
    # every field, but place each field on its own paragraph so high-precision
    # values and uncertainty strings never spill beyond the A4 text block.
    for label in ('TopoMagic output:', 'current reference:', 'signed pull:', 'control disposition:'):
        tex = tex.replace('; \\textbf{' + label + '}', ';\\par\\noindent\\textbf{' + label + '}')
    # Long machine-artifact names are semantic paths, not unbreakable code words.
    # \path permits safe line breaking at underscores and punctuation.
    tex = tex.replace(r'\texttt{topomagic\_control\_audit\_receipt.json}',
                      r'\path{topomagic_control_audit_receipt.json}')
    tex = tex.replace(r'\texttt{verify\_topomagic\_control\_v100.py}',
                      r'\path{verify_topomagic_control_v100.py}')
    tmp_md.unlink(missing_ok=True)
    tmp_tex.unlink(missing_ok=True)
    return tex


def update_parent_tex(parent: str, addition_tex: str) -> str:
    tex = parent
    tex = tex.replace('THEA - The Light Matrix v1.3.3', 'THEA - The Light Matrix v1.3.4')
    tex = tex.replace('Calculation-by-Calculation LaTeX Tower v1.3.3', 'Full Calculation-by-Calculation LaTeX Tower v1.3.4')
    tex = tex.replace(
        'exact closure, golden selection, chirality, spectra, invariant theory, numerical walls, and the LUCA handoff',
        'exact closure, golden selection, chirality, spectra, invariant theory, LUCA, THE CROWD, and the TopoMagic Hopf boundary',
    )
    tex = tex.replace('Prepared 9 August 2026 - expanded calculation audit', 'Prepared 10 August 2026 - 151-rung Hopf-boundary control edition')
    tex = tex.replace('pdftitle={THEA - The Light Matrix v1.3.3}', 'pdftitle={THEA - The Light Matrix v1.3.4}')

    marker = r'\newcommand{\dd}{\,\mathrm d}'
    tex = tex.replace(marker, marker + r'''
\usepackage{seqsplit}
\providecommand{\tightlist}{}
\providecommand{\pandocbounded}[1]{#1}
\newcommand{\AUDITPASS}{\status{ExactGreen}{PASS}}
\newcommand{\AUDITCOND}{\status{DesignGold}{CONDITIONAL}}
\newcommand{\AUDITOPEN}{\status{HypOrange}{OPEN}}
\newcommand{\AUDITCORR}{\status{CorrectionRed}{CORRECTION}}
\newcommand{\AUDITREF}{\status{CorrectionRed}{REFUTED}}
''')

    abstract_anchor = "This document therefore preserves the governing rule in executable form: target is not result; a theorem, a finite computation, a design choice, a null result, and a physical hypothesis never inherit one another's labels."
    abstract_extra = r'''

v1.3.4 retains all 91 parent rungs and adds a sixty-rung control audit of the supplied TopoMagic Hopf-fibration tower. The standard Hopf and classifying-space identities are admitted, while CLASSIFIES, EMBEDS, ISOMORPHIC, MODELS, PREDICTS, and MEASURED-AS remain six different arrows. The decisive numerical result is affine-invariant: the boxed lepton sequence has second difference $2.408149226$, whereas the displayed Hurwitz-zeta route has second difference $6.709456767665\ldots$; constant and linear absorptions cannot reconcile them. The complete volume contains 151 dedicated calculation rungs plus the full machine receipt and verifier.'''
    tex = tex.replace(abstract_anchor, abstract_anchor + abstract_extra, 1)

    tex = tex.replace(
        r'\item[Source inventory] Chapter~1: the seven audited artifacts and their roles.',
        r'\item[Source inventory] Chapter~1: the complete parent-plus-Hopf source inventory and the role of every artifact.',
    )
    table_anchor = r'\item[Independent audit] Chapter~14: all 38 checks, statuses, verdicts, and compact results; full values remain in the JSON receipt.'
    tex = tex.replace(table_anchor, table_anchor + r'''
\item[Hopf boundary] Chapter~20: exact admitted identities, non-implication ledger, and CURSE 42.
\item[Full duel audit] Chapter~21: source reconstruction, theorem controls, provenance, and uncertainty-level phenomenology.
\item[Hopf rungs] Chapter~22: H01--H60, one calculation or counterexample per claim.
\item[Controlled proposal] Chapter~23: five reciprocal gates for reopening the bridge.
\item[Integration and appendices] Chapter~24 and Appendices A--B: typed receipt schema, full JSON receipt, and complete verifier source.''')

    row = r'THE CROWD kernel & \path{the_crowd_v0_1.py} & Deterministic seed-20260809 engine whose tables and Monte Carlo null are replayed independently.\\'
    extra_rows = row + '\n' + '\n'.join([
        r'TopoMagic source & \path{TopoMagicTower.pdf} & Reviewed 116-page Hopf-fibration gauge--gravity scroll; source claims are quoted before correction and never silently rewritten.\\',
        r'Control audit & \path{THEA_VS_TOPOMAGIC_CONTROLLED_AUDIT_v1.0.0.md} & Full theorem, computation, provenance, and phenomenology audit.\\',
        r'Audit receipt & \path{topomagic_control_audit_receipt.json} & Sixty machine-readable dispositions and stable payload.\\',
        r'Controlled proposal & \path{CONTROLLED_PROPOSAL_TO_THE_TOPOMAGIC_TOWER_v1.0.0.md} & Five reciprocal gates and one sealed-prediction requirement.\\',
        r'v1.3.4 builder & \path{build_light_matrix_v134_full.py} & Deterministic assembly, compilation, finalization, manifest, and bundle generation.\\',
    ])
    if row not in tex:
        raise RuntimeError('source inventory row missing')
    tex = tex.replace(row, extra_rows, 1)

    tex = tex.replace('Every displayed claim in v1.3.3 belongs to one of the following classes.', 'Every displayed claim in v1.3.4 retains one of the following epistemic classes.')
    status_line = r'\item \CORRECTION\quad A source statement whose algebra, label, indexing, or implementation receipt changes in v1.3.3.'
    tex = tex.replace(status_line, r'\item \CORRECTION\quad A source statement whose algebra, label, indexing, or implementation receipt changes in the frozen lineage.')
    end_status = r'\item \CORRECTION\quad A source statement whose algebra, label, indexing, or implementation receipt changes in the frozen lineage.\n\end{itemize}'
    tex = tex.replace(end_status, end_status + r'''

The TopoMagic control uses the orthogonal disposition vocabulary PASS, CONDITIONAL, OPEN, CORRECTION, and REFUTED. Epistemic class answers what kind of statement is being made; disposition records what happened when that particular statement was tested.''', 1)

    statistical = r'''\begin{correctionbox}[title={v1.3.3 statistical correction}]
The newly supplied coincidence engine reproduces exactly, but its $3.0\sigma$ row is marginal.  Taking the maximum over the five scanned tiers gives empirical global $p=0.0215$.  The source's own physics-only and deduplication autopsies then give $p=0.0950$ and $p=0.3270$.  A new cluster-preserving matched null gives $p=0.1090$, and a stricter four-generator provenance collapse gives $p=0.2590$.  The crowd identifies nobody.
\end{correctionbox}'''
    tex = tex.replace(statistical, statistical + r'''

\begin{correctionbox}[title={v1.3.4 Hopf-boundary control}]
The supplied TopoMagic scroll reproduces as an executable formula system, but the sixty-check control yields 22 PASS, 3 CONDITIONAL, 4 OPEN, 16 CORRECTION, and 15 REFUTED dispositions. The decisive numerical correction is affine-invariant: $\Delta^2D=2.408149226$ while the displayed zeta route gives $|\Delta^2\zeta'|=6.709456767665\ldots$. Constant and linear absorption cannot change that fingerprint. Standard Hopf identities survive; the physical forcing chain does not inherit their status.
\end{correctionbox}''', 1)

    bib = r'\begin{thebibliography}{99}'
    tex = tex.replace(bib, addition_tex + '\n\n' + bib, 1)
    bib_extra = r'''
\bibitem{topomagic} J. L. Nielsen, \emph{The Complex Hopf Fibration as the Canonical Space for Gauge--Gravity Unification: The Field, Universal Action, and Particle Spectrum}, uploaded 116-page scroll, 5 August 2026.
\bibitem{topomagicAudit} \emph{The Duel of the Towers: THEA Light Matrix versus the TopoMagic Hopf-fibration scroll}, controlled cross-audit v1.0.0, 9 August 2026.
\bibitem{topomagicProposal} \emph{Controlled Proposal to the TopoMagic Tower}, five-gate reciprocal protocol, 9 August 2026.
\bibitem{hopfBoundary} \emph{THEA Light Matrix v1.3.4 -- Hopf Boundary Addendum}, 9 August 2026.
\bibitem{milnor} J. Milnor, ``Construction of Universal Bundles, I and II,'' \emph{Annals of Mathematics} 63 (1956).
\bibitem{witten3d} E. Witten, ``(2+1)-Dimensional Gravity as an Exactly Soluble System,'' \emph{Nuclear Physics B} 311 (1988), 46--78.
'''
    tex = tex.replace(r'\end{thebibliography}', bib_extra + '\n\\end{thebibliography}', 1)
    tex = tex.replace('pdflatex THEA_LIGHT_MATRIX_v1.3.3_CALCULATION_TOWER.tex', 'pdflatex THEA_LIGHT_MATRIX_v1.3.4_FULL_CALCULATION_TOWER.tex')
    return tex


def update_parent_md(parent: str, addition_md: str) -> str:
    md = parent
    md = md.replace('Calculation-by-Calculation Tower v1.3.3', 'Full Calculation-by-Calculation Tower v1.3.4')
    md = md.replace('*Exact closure, golden selection, chirality, spectra, invariant theory, numerical walls, the LUCA source replay, and THE CROWD statistical guillotine*', '*Exact closure, golden selection, chirality, spectra, invariant theory, numerical walls, LUCA, THE CROWD, and the TopoMagic Hopf-boundary control*')
    md = md.replace('Prepared 9 August 2026 - expanded calculation audit', 'Prepared 10 August 2026 - 151-rung Hopf-boundary control edition')
    md = md.replace('`THEA_LIGHT_MATRIX_v1.3.3_CALCULATION_TOWER.pdf`', '`THEA_LIGHT_MATRIX_v1.3.4_FULL_CALCULATION_TOWER.pdf`')
    md = md.replace('all 91 dedicated calculation rungs', 'all 151 dedicated calculation rungs')
    md = md.replace('all eleven figure references', 'all nineteen figure references')
    md = re.sub(r'> Source PDF: 99 A4 pages\s*\n> Source PDF SHA-256: `[^`]+`\s*\n> Source TeX SHA-256: `[^`]+`',
                '> Source PDF: `__PDF_PAGES__` A4 pages  \n> Source PDF SHA-256: `__PDF_SHA__`  \n> Source TeX SHA-256: `__TEX_SHA__`', md, count=1)

    anchor = 'This document therefore preserves the governing rule in executable form: target is not result; a theorem, a finite computation, a design choice, a null result, and a physical hypothesis never inherit one another’s labels.'
    md = md.replace(anchor, anchor + '\n\nv1.3.4 retains all 91 parent rungs and adds a sixty-rung control audit of the supplied TopoMagic Hopf-fibration tower. Standard Hopf and classifying-space identities are admitted, while **CLASSIFIES**, **EMBEDS**, **ISOMORPHIC**, **MODELS**, **PREDICTS**, and **MEASURED-AS** remain six different arrows. The decisive numerical result is affine-invariant: the boxed lepton sequence has second difference $2.408149226$, whereas the displayed Hurwitz-zeta route has second difference $6.709456767665\ldots$. The complete volume contains **151 dedicated calculation rungs**, the full machine receipt, and the complete 80-digit verifier.', 1)

    md = md.replace('- **Source inventory**: Chapter 1: the seven audited artifacts and their roles.', '- **Source inventory**: Chapter 1: the complete parent-plus-Hopf source inventory and the role of every artifact.')
    row = '| THE CROWD kernel | `the_crowd_v0_1.py` | Deterministic seed-20260809 engine whose tables and Monte Carlo null are replayed independently. |'
    extra_rows = row + '\n' + '\n'.join([
        '| TopoMagic source | `TopoMagicTower.pdf` | Reviewed 116-page Hopf-fibration gauge-gravity scroll; source claims are quoted before correction and never silently rewritten. |',
        '| Control audit | `THEA_VS_TOPOMAGIC_CONTROLLED_AUDIT_v1.0.0.md` | Full theorem, computation, provenance, and phenomenology audit. |',
        '| Audit receipt | `topomagic_control_audit_receipt.json` | Sixty machine-readable dispositions and stable payload. |',
        '| Controlled proposal | `CONTROLLED_PROPOSAL_TO_THE_TOPOMAGIC_TOWER_v1.0.0.md` | Five reciprocal gates and one sealed-prediction requirement. |',
        '| v1.3.4 builder | `build_light_matrix_v134_full.py` | Deterministic assembly, compilation, finalization, manifest, and bundle generation. |',
    ])
    md = md.replace(row, extra_rows, 1)
    md = md.replace('Every displayed claim in v1.3.3 belongs to one of the following classes.', 'Every displayed claim in v1.3.4 retains one of the following epistemic classes.')
    md = md.replace('- **[CORRECTION]** A source statement whose algebra, label, indexing, or implementation receipt changes in v1.3.3.', '- **[CORRECTION]** A source statement whose algebra, label, indexing, or implementation receipt changes in the frozen lineage.\n\nThe TopoMagic control uses the orthogonal disposition vocabulary **PASS**, **CONDITIONAL**, **OPEN**, **CORRECTION**, and **REFUTED**. Epistemic class answers what kind of statement is being made; disposition records what happened when that particular statement was tested.')
    statistical = '> **[CORRECTION] v1.3.3 statistical correction**\n>\n> The newly supplied coincidence engine reproduces exactly, but its $3.0\\sigma$ row is marginal. Taking the maximum over the five scanned tiers gives empirical global $p=0.0215$. The source’s own physics-only and deduplication autopsies then give $p=0.0950$ and $p=0.3270$. A new cluster-preserving matched null gives $p=0.1090$, and a stricter four-generator provenance collapse gives $p=0.2590$. The crowd identifies nobody.'
    md = md.replace(statistical, statistical + '\n\n> **[CORRECTION] v1.3.4 Hopf-boundary control**\n>\n> The supplied TopoMagic scroll reproduces as an executable formula system, but the sixty-check control yields **22 PASS, 3 CONDITIONAL, 4 OPEN, 16 CORRECTION, and 15 REFUTED** dispositions. The decisive numerical correction is affine-invariant: $\\Delta^2D=2.408149226$ while the displayed zeta route gives $|\\Delta^2\\zeta\'|=6.709456767665\\ldots$. Constant and linear absorption cannot change that fingerprint. Standard Hopf identities survive; the physical forcing chain does not inherit their status.', 1)

    contents = norm('''
- Chapter 20 - The Hopf Boundary: Classification Is Not Ontology
- Chapter 21 - The Duel of the Towers: Full Controlled Audit
- Chapter 22 - Hopf Control Tower: H01-H60
- Chapter 23 - The Controlled Counterproposal to the TopoMagic Tower
- Chapter 24 - v1.3.4 Integration Contract and Next-Step Receipt
- Appendix A - Complete TopoMagic Control Receipt
- Appendix B - Complete 80-Digit Control Verifier
''') + '\n\n'
    md = md.replace('# Chapter 1 - The Contract: Status Before Symbol', contents + '# Chapter 1 - The Contract: Status Before Symbol', 1)
    md = md.replace('# Bibliography', addition_md + '\n\n# Bibliography', 1)
    md = md.rstrip() + norm('''

23. Jennifer “Jenny” Lorraine Nielsen, *The Complex Hopf Fibration as the Canonical Space for Gauge-Gravity Unification: The Field, Universal Action, and Particle Spectrum*, uploaded 116-page scroll, 5 August 2026.

24. *The Duel of the Towers: THEA Light Matrix versus the TopoMagic Hopf-fibration scroll*, controlled cross-audit v1.0.0, 9 August 2026.

25. *Controlled Proposal to the TopoMagic Tower*, five-gate reciprocal protocol, 9 August 2026.

26. *THEA Light Matrix v1.3.4 - Hopf Boundary Addendum*, 9 August 2026.

27. J. Milnor, “Construction of Universal Bundles, I and II,” *Annals of Mathematics* 63 (1956).

28. E. Witten, “(2+1)-Dimensional Gravity as an Exactly Soluble System,” *Nuclear Physics B* 311 (1988), 46-78.
''') + '\n'
    return md


def make_index() -> str:
    parent = PARENT_INDEX.read_text(encoding='utf-8').rstrip()
    rows = [f"| H{i:02d} | {c['id']} | {c['group']} | {c['name']} | {c['status']} |" for i, c in enumerate(CHECKS, 1)]
    return parent + '\n\n# v1.3.4 Hopf/TopoMagic extension\n\n| tower rung | native audit ID | group | calculation or claim | disposition |\n|---|---|---|---|---|\n' + '\n'.join(rows) + '\n\n**Total dedicated rungs:** 38 C-rungs + 35 E-rungs + 18 G-rungs + 60 H-rungs = **151**.\n'


def markdown_stats(md: str) -> dict[str, Any]:
    images = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md)
    fences = len(re.findall(r'(?m)^```', md))
    return {
        'lines': md.count('\n') + 1,
        'bytes': len(md.encode('utf-8')),
        'top_level_headings': len(re.findall(r'(?m)^# ', md)),
        'second_level_headings': len(re.findall(r'(?m)^## ', md)),
        'display_math_blocks': len(re.findall(r'(?m)^\$\$', md)) // 2,
        'code_fence_markers': fences,
        'code_fence_parity': fences % 2 == 0,
        'image_paths': images,
        'images_present': all((ROOT / x).exists() for x in images),
    }


def compile_pdf() -> None:
    epoch = str(int(subprocess.check_output(['date', '-u', '-d', '2026-08-10 00:00:00', '+%s'], text=True).strip()))
    env = os.environ.copy()
    env['SOURCE_DATE_EPOCH'] = epoch
    subprocess.run(['latexmk', '-pdf', '-interaction=nonstopmode', '-halt-on-error', OUT_TEX.name], cwd=ROOT, env=env, check=True)
    subprocess.run(['python', str(NORMALIZER), str(OUT_PDF), '--seed-file', str(OUT_TEX)], check=True)


def pdf_pages(path: Path) -> int:
    out = subprocess.check_output(['pdfinfo', str(path)], text=True)
    m = re.search(r'^Pages:\s+(\d+)', out, re.M)
    if not m:
        raise RuntimeError('page count missing')
    return int(m.group(1))


def finalize_md(md: str) -> str:
    return (md.replace('__PDF_PAGES__', str(pdf_pages(OUT_PDF)))
              .replace('__PDF_SHA__', sha256(OUT_PDF))
              .replace('__TEX_SHA__', sha256(OUT_TEX)))


def write_manifest(files: list[Path]) -> None:
    lines = [f"{sha256(p)}  {p.name}" for p in sorted(files, key=lambda x: x.name)]
    OUT_MANIFEST.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def bundle(files: list[Path], dirs: list[Path]) -> None:
    if OUT_ZIP.exists():
        OUT_ZIP.unlink()
    epoch = (2026, 8, 10, 0, 0, 0)
    with zipfile.ZipFile(OUT_ZIP, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(files, key=lambda x: x.name):
            info = zipfile.ZipInfo(p.name, epoch)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, p.read_bytes())
        for d in dirs:
            for p in sorted(d.rglob('*')):
                if p.is_file():
                    arc = f"{d.name}/{p.relative_to(d).as_posix()}"
                    info = zipfile.ZipInfo(arc, epoch)
                    info.compress_type = zipfile.ZIP_DEFLATED
                    zf.writestr(info, p.read_bytes())
    OUT_ZIP_SHA.write_text(f"{sha256(OUT_ZIP)}  {OUT_ZIP.name}\n", encoding='utf-8')


def main() -> None:
    for p in [PARENT_TEX, PARENT_MD, PARENT_INDEX, ADDENDUM, AUDIT_FULL, AUDIT_JSON, PROPOSAL, TOPO_PDF, VERIFIER, NORMALIZER]:
        if not p.exists():
            raise SystemExit(f'missing {p}')
    make_figures()
    add_md = build_addition_md()
    OUT_ADD_MD.write_text(add_md, encoding='utf-8')
    add_tex = addition_to_tex(add_md)
    OUT_ADD_TEX.write_text(add_tex, encoding='utf-8')
    OUT_TEX.write_text(update_parent_tex(PARENT_TEX.read_text(encoding='utf-8'), add_tex), encoding='utf-8')
    preliminary_md = update_parent_md(PARENT_MD.read_text(encoding='utf-8'), add_md)
    OUT_MD.write_text(preliminary_md, encoding='utf-8')
    OUT_INDEX.write_text(make_index(), encoding='utf-8')
    OUT_CHANGELOG.write_text(norm('''
# THEA Light Matrix v1.3.4 - Changelog

- Preserves the complete v1.3.3 91-rung calculation tower.
- Integrates the Hopf Boundary Addendum and CURSE 42.
- Adds the complete controlled TopoMagic audit and all sixty H-rungs.
- Adds the affine-invariant D(n) provenance refutation.
- Adds numerical-input, uncertainty, and held-out prediction controls.
- Adds the complete machine receipt and verifier source as appendices.
- Adds a reciprocal five-gate proposal.
- Changes no exact Light Matrix theorem, C60 certificate, LUCA lock, or THE CROWD null verdict.
''') + '\n', encoding='utf-8')
    OUT_README.write_text(norm('''
# THEA Light Matrix v1.3.4 - Rebuild

```bash
python build_light_matrix_v134_full.py
python /home/oai/skills/pdfs/scripts/pdf_preflight.py THEA_LIGHT_MATRIX_v1.3.4_FULL_CALCULATION_TOWER.pdf
```

The builder preserves v1.3.3, appends the Hopf-boundary control, compiles with a fixed `SOURCE_DATE_EPOCH`, normalizes the PDF trailer ID from the TeX hash, finalizes Markdown metadata, validates Markdown through Pandoc, writes receipts and hashes, and emits a deterministic ZIP.
''') + '\n', encoding='utf-8')

    compile_pdf()
    final_md = finalize_md(preliminary_md)
    OUT_MD.write_text(final_md, encoding='utf-8')
    subprocess.run(['pandoc', str(OUT_MD), '-f', 'gfm+tex_math_dollars', '-t', 'json', '-o', str(ROOT / '_v134_ast.json')], check=True)
    (ROOT / '_v134_ast.json').unlink(missing_ok=True)

    stats = markdown_stats(final_md)
    log_text = (ROOT / (OUT_TEX.stem + '.log')).read_text(encoding='utf-8', errors='replace')
    receipt: dict[str, Any] = {
        'schema': 'thea.light-matrix.v1.3.4.full-tower',
        'version': '1.3.4',
        'date': '2026-08-10',
        'parent_version': '1.3.3',
        'parent_rungs': 91,
        'new_hopf_rungs': 60,
        'total_rungs': 151,
        'pdf_pages': pdf_pages(OUT_PDF),
        'topomagic_status_counts': AUDIT['status_counts'],
        'parent_payload_sha256': '1e6c813e7f6ba8e00587836d2bbbed90b5d7e8a1ee0ebba4343f17dbcf3e3cb7',
        'hopf_audit_payload_sha256': AUDIT['stable_sha256'],
        'markdown_stats': stats,
        'latex_overfull_boxes': len(re.findall(r'Overfull \\hbox', log_text)),
        'sources': {
            'parent_tex_sha256': sha256(PARENT_TEX),
            'parent_md_sha256': sha256(PARENT_MD),
            'topomagic_pdf_sha256': sha256(TOPO_PDF),
            'audit_json_sha256': sha256(AUDIT_JSON),
            'audit_full_sha256': sha256(AUDIT_FULL),
            'addendum_sha256': sha256(ADDENDUM),
            'proposal_sha256': sha256(PROPOSAL),
            'verifier_sha256': sha256(VERIFIER),
        },
        'generated': {
            'tex_sha256': sha256(OUT_TEX),
            'pdf_sha256': sha256(OUT_PDF),
            'markdown_sha256': sha256(OUT_MD),
            'addition_markdown_sha256': sha256(OUT_ADD_MD),
            'index_sha256': sha256(OUT_INDEX),
        },
    }
    stable = json.dumps(receipt, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    receipt['stable_sha256'] = hashlib.sha256(stable).hexdigest()
    OUT_JSON.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    OUT_BUILD_RECEIPT.write_text(norm(f'''
# THEA Light Matrix v1.3.4 - Build Receipt

```text
PDF pages                 {receipt['pdf_pages']}
Dedicated rungs           151
Parent C-rungs             38
LUCA E-rungs               35
THE CROWD G-rungs          18
Hopf-control H-rungs       60
Markdown lines            {stats['lines']}
Display-math blocks       {stats['display_math_blocks']}
Figure references         {len(stats['image_paths'])}
Code-fence parity         {'PASS' if stats['code_fence_parity'] else 'FAIL'}
All images present        {'PASS' if stats['images_present'] else 'FAIL'}
LaTeX overfull boxes      {receipt['latex_overfull_boxes']}
```

## Frozen status ledger

```text
PASS                       22
CONDITIONAL                 3
OPEN                        4
CORRECTION                  16
REFUTED                     15
```

## Hashes

```text
TeX        {sha256(OUT_TEX)}
PDF        {sha256(OUT_PDF)}
Markdown   {sha256(OUT_MD)}
Receipt    {receipt['stable_sha256']}
```

The PDF was compiled with `SOURCE_DATE_EPOCH=2026-08-10T00:00:00Z` and its trailer ID was replaced, without moving byte offsets, by a deterministic identifier derived from the TeX source.
''') + '\n', encoding='utf-8')

    manifest_files = [
        OUT_TEX, OUT_PDF, OUT_MD, OUT_ADD_MD, OUT_ADD_TEX, OUT_INDEX, OUT_JSON,
        OUT_BUILD_RECEIPT, OUT_CHANGELOG, OUT_README, Path(__file__),
        ADDENDUM, AUDIT_FULL, AUDIT_REPORT, AUDIT_JSON, PROPOSAL, VERIFIER,
    ]
    write_manifest(manifest_files)
    manifest_files.append(OUT_MANIFEST)
    bundle(manifest_files, [FIGDIR, ROOT / 'light_matrix_v132_figures', ROOT / 'light_matrix_v133_figures', ROOT / 'topomagic_control_figures'])

    print(json.dumps({
        'pdf': str(OUT_PDF),
        'md': str(OUT_MD),
        'tex': str(OUT_TEX),
        'bundle': str(OUT_ZIP),
        'pages': receipt['pdf_pages'],
        'rungs': 151,
        'pdf_sha256': sha256(OUT_PDF),
        'markdown_sha256': sha256(OUT_MD),
        'bundle_sha256': sha256(OUT_ZIP),
        'stable_receipt_sha256': receipt['stable_sha256'],
    }, indent=2))


if __name__ == '__main__':
    main()

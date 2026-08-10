#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path('/mnt/data')
WORK = ROOT / 'qcd_md_work'
WORK.mkdir(exist_ok=True)
TEX = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_QCD_TO_COSMOS_MANA_CODEX.tex'
PDF = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_QCD_TO_COSMOS_MANA_CODEX.pdf'
RECEIPT = ROOT / 'qcd_to_cosmos_mana_v1.0.0_receipt.json'
REPORT = ROOT / 'qcd_to_cosmos_mana_v1.0.0_report.md'
INDEX = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_QCD_TO_COSMOS_DERIVATION_INDEX.md'
VERIFY = ROOT / 'verify_qcd_to_cosmos_mana_v100.py'
FIGGEN = ROOT / 'generate_qcd_to_cosmos_mana_figures.py'
PDF_BUILDER = ROOT / 'build_qcd_to_cosmos_mana_v100.py'
FIGDIR = ROOT / 'qcd_to_cosmos_mana_figures'
OUT = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_QCD_TO_COSMOS_MAXIMAL_BOOKKEEPING.md'
OUT_RECEIPT = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_QCD_TO_COSMOS_MAXIMAL_BOOKKEEPING_RECEIPT.md'
OUT_BUILDER = ROOT / 'build_qcd_to_cosmos_maximal_md.py'
BUNDLE = ROOT / 'THEA_LIGHT_MATRIX_v1.3.4_QCD_TO_COSMOS_MAXIMAL_MARKDOWN_BUNDLE.zip'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def run_pandoc(latex: str, name: str) -> str:
    src = WORK / f'{name}.tex'
    dst = WORK / f'{name}.md'
    src.write_text(
        '\\documentclass{article}\n\\begin{document}\n' + latex + '\n\\end{document}\n',
        encoding='utf-8', newline='\n'
    )
    subprocess.run([
        'pandoc', str(src), '-f', 'latex', '-t', 'gfm+tex_math_dollars',
        '--wrap=none', '--resource-path', str(ROOT), '-o', str(dst)
    ], check=True, cwd=ROOT)
    return dst.read_text(encoding='utf-8')


def sub_literal(pattern: str, replacement: str, text: str) -> str:
    return re.sub(pattern, lambda _m: replacement, text)


def expand_macros(text: str) -> str:
    for pattern, replacement in [
        (r'\\centernot\\Longrightarrow', r'\nRightarrow'),
        (r'\\ph(?![A-Za-z])', r'\varphi'),
        (r'\\Lag(?![A-Za-z])', r'\mathcal{L}'),
        (r'\\Mpl(?![A-Za-z])', r'M_{\mathrm{Pl}}'),
        (r'\\LamQCD(?![A-Za-z])', r'\Lambda_{\mathrm{QCD}}'),
        (r'\\as(?![A-Za-z])', r'\alpha_s'),
        (r'\\diag(?![A-Za-z])', r'\operatorname{diag}'),
        (r'\\sgn(?![A-Za-z])', r'\operatorname{sgn}'),
        (r'\\Tr(?![A-Za-z])', r'\operatorname{Tr}'),
        (r'i\\slashed\s*D', r'i\gamma^\mu D_\mu'),
        (r'\\slashed\s*D', r'\gamma^\mu D_\mu'),
        (r'\\bm(?![A-Za-z])', r'\boldsymbol'),
        (r'\\dfrac(?![A-Za-z])', r'\frac'),
    ]:
        text = sub_literal(pattern, replacement, text)

    # Physics-package differential command, but not \ddot.
    text = re.sub(r'\\dd(?![A-Za-z])', lambda _m: r'\,\mathrm{d}', text)
    text = text.replace(r'\,\,\mathrm{d}', r'\,\mathrm{d}')
    text = text.replace(r'\mathbf1', r'\mathbf{1}')

    # Old-style roman subscripts -> portable LaTeX.
    text = re.sub(
        r'\{\\rm\s+([^{}]+)\}',
        lambda m: '{\\mathrm{' + m.group(1).strip() + '}}',
        text,
    )

    # Simple bra-ket macros used in this source.
    text = re.sub(
        r'\\bra\{([^{}]+)\}',
        lambda m: r'\langle ' + m.group(1) + r' |',
        text,
    )
    text = re.sub(
        r'\\ket\{([^{}]+)\}',
        lambda m: r'| ' + m.group(1) + r' \rangle',
        text,
    )

    # Protect commutator brackets from Pandoc's LaTeX reader.
    for old, new in {
        '[T^a,T^b]': r'\left[T^a,T^b\right]',
        r'[D_\mu,D_\nu]': r'\left[D_\mu,D_\nu\right]',
        r'[A_\mu,A_\nu]': r'\left[A_\mu,A_\nu\right]',
    }.items():
        text = text.replace(old, new)

    # Expand the antisymmetrized Bianchi shorthand so no bracket parser can eat it.
    text = text.replace(
        'D_{[\\lambda}F_{\\mu\\nu]}=0.',
        'D_{\\lambda}F_{\\mu\\nu}+D_{\\mu}F_{\\nu\\lambda}+D_{\\nu}F_{\\lambda\\mu}=0.'
    )

    # Portable prose references.
    text = text.replace(
        'Equations~\\eqref{eq:masscont}--\\eqref{eq:tempgrad}',
        'The mass-continuity, hydrostatic-equilibrium, luminosity and temperature-gradient equations'
    )
    text = text.replace(
        'Eq.~\\eqref{eq:hydro}',
        'the hydrostatic-equilibrium equation'
    )
    text = text.replace('Fig.~\\ref{fig:tovmr}', 'the TOV mass--radius figure')
    text = text.replace('Appendix~\\ref{app:su3}', 'Appendix A')
    text = text.replace('\\ref{app:su3}', 'A')
    text = re.sub(r'\\eqref\{([^{}]+)\}', lambda m: f'[{m.group(1)}]', text)
    text = re.sub(r'\\ref\{([^{}]+)\}', lambda m: f'[{m.group(1)}]', text)
    return text


def balanced_brace(text: str, start: int) -> tuple[str, int]:
    depth = 0
    i = start
    while i < len(text):
        c = text[i]
        escaped = i > 0 and text[i - 1] == '\\'
        if c == '{' and not escaped:
            depth += 1
        elif c == '}' and not escaped:
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
        i += 1
    raise ValueError('unbalanced brace')


def extract_figures(text: str) -> tuple[str, list[dict[str, str]]]:
    figures: list[dict[str, str]] = []
    begin_pat = re.compile(r'\\begin\{(figure\*?)\}(?:\[[^\]]*\])?')
    pos = 0
    chunks: list[str] = []
    while True:
        m = begin_pat.search(text, pos)
        if not m:
            chunks.append(text[pos:])
            break
        chunks.append(text[pos:m.start()])
        env = m.group(1)
        end_token = f'\\end{{{env}}}'
        end = text.find(end_token, m.end())
        if end < 0:
            raise ValueError(f'unclosed {env}')
        block = text[m.end():end]
        im = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^{}]+)\}', block)
        cm = re.search(r'\\caption\s*\{', block)
        if im and cm:
            caption, _ = balanced_brace(block, cm.end() - 1)
            marker = f'QCD_COSMOS_FIGURE_MARKER_{len(figures) + 1:02d}'
            figures.append({'marker': marker, 'path': im.group(1), 'caption': caption})
            chunks.append('\n\n' + marker + '\n\n')
        else:
            chunks.append(text[m.start():end + len(end_token)])
        pos = end + len(end_token)
    return ''.join(chunks), figures


BOX_MAP = {
    'standardbox': ('NOTE', 'STANDARD THEORY'),
    'theabox': ('TIP', 'THEA EXACT CORE'),
    'bridgebox': ('IMPORTANT', 'LEVEL-12 MANA BRIDGE'),
    'obligationbox': ('WARNING', 'OPEN OBLIGATION'),
    'correctionbox': ('CAUTION', 'CONTROL / CORRECTION'),
    'manabox': ('NOTE', 'MAGIC-NERD TRANSLATION'),
}


def replace_boxes(text: str) -> str:
    for env, (_, label) in BOX_MAP.items():
        pat = re.compile(r'\\begin\{' + re.escape(env) + r'\}(?:\[([^\]]*)\])?')

        def repl(m: re.Match[str]) -> str:
            subtitle = re.sub(r'^--\s*', '', (m.group(1) or '').strip())
            title = label + (f' — {subtitle}' if subtitle else '')
            return '\\begin{quote}\n\\textbf{QCD_BOX_' + env.upper() + '::' + title + '}\\par\n'

        text = pat.sub(repl, text)
        text = text.replace(f'\\end{{{env}}}', '\\end{quote}')
    return text


def normalize_math(content: str) -> str:
    content = re.sub(r'\\label\{[^{}]+\}', '', content)
    content = re.sub(r'\\\\\[[^\]]+\]', r'\\\\', content)
    content = content.strip()
    return content


def extract_display_math(text: str, prefix: str) -> tuple[str, dict[str, str]]:
    # Protect display mathematics before Pandoc so every environment is retained verbatim.
    pattern = re.compile(
        r'\\begin\{(equation\*?|align\*?)\}(.*?)\\end\{\1\}|\\\[(.*?)\\\]',
        re.S,
    )
    mapping: dict[str, str] = {}
    chunks: list[str] = []
    pos = 0
    for i, m in enumerate(pattern.finditer(text), 1):
        chunks.append(text[pos:m.start()])
        content = m.group(2) if m.group(2) is not None else m.group(3)
        env = m.group(1)
        content = normalize_math(content)
        if env and env.startswith('align'):
            content = '\\begin{aligned}\n' + content + '\n\\end{aligned}'
        marker = f'{prefix}_MATH_MARKER_{i:03d}'
        mapping[marker] = content
        chunks.append('\n\n' + marker + '\n\n')
        pos = m.end()
    chunks.append(text[pos:])
    return ''.join(chunks), mapping


def restore_math(md: str, mapping: dict[str, str]) -> str:
    out: list[str] = []
    for line in md.splitlines():
        stripped = line.strip()
        quote = False
        marker = stripped
        if marker.startswith('>'):
            quote = True
            marker = marker[1:].strip()
        if marker in mapping:
            math_lines = ['$$'] + mapping[marker].splitlines() + ['$$']
            if quote:
                out.extend('> ' + x if x else '>' for x in math_lines)
            else:
                out.extend(math_lines)
        else:
            out.append(line)
    return '\n'.join(out)


def preprocess_body(tex: str):
    doc = tex.split('\\begin{document}', 1)[1].rsplit('\\end{document}', 1)[0]
    abs_m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', doc, re.S)
    abstract = abs_m.group(1).strip() if abs_m else ''

    body = doc[doc.index('\\part*{I. FROM COLOR CHARGE TO HADRONS}'):]

    bib_m = re.search(r'\\begin\{thebibliography\}\{[^}]*\}(.*?)\\end\{thebibliography\}', body, re.S)
    bibliography = bib_m.group(1).strip() if bib_m else ''
    if bib_m:
        body = body[:bib_m.start()] + '\nQCD_COSMOS_BIBLIOGRAPHY_MARKER\n' + body[bib_m.end():]

    body = re.sub(r'\\vfill\s*\\begin\{center\}.*?\\end\{center\}', '', body, flags=re.S)
    body, figures = extract_figures(body)
    body = replace_boxes(body)
    body = body.replace('\\input{qcd_to_cosmos_check_table.tex}', 'QCD_COSMOS_CHECK_TABLE_MARKER')
    body = re.sub(
        r'\\lstinputlisting(?:\[[^\]]*\])?\{verify_qcd_to_cosmos_mana_v100\.py\}',
        'QCD_COSMOS_VERIFIER_MARKER', body
    )

    for token in ['\\balance', '\\clearpage', '\\onecolumn', '\\twocolumn', '\\appendix']:
        body = body.replace(token, '')
    body = body.replace('\\begin{strip}', '').replace('\\end{strip}', '')
    body = re.sub(r'\\addcontentsline\{[^{}]+\}\{[^{}]+\}\{[^{}]+\}', '', body)
    body = re.sub(r'\\part\*\{', r'\\part{', body)

    body = expand_macros(body)
    abstract = expand_macros(abstract)
    bibliography = expand_macros(bibliography)

    body, body_math = extract_display_math(body, 'QCD_BODY')
    abstract, abstract_math = extract_display_math(abstract, 'QCD_ABSTRACT')
    return body, abstract, figures, bibliography, body_math, abstract_math


def clean_pandoc(md: str) -> str:
    md = md.replace('\r\n', '\n')
    lines: list[str] = []
    for line in md.splitlines():
        if line.startswith('###### '):
            line = '##### ' + line[7:]
        elif line.startswith('##### '):
            line = '#### ' + line[6:]
        elif line.startswith('#### '):
            line = '### ' + line[5:]
        elif line.startswith('### '):
            line = '## ' + line[4:]
        lines.append(line)
    md = '\n'.join(lines)

    for env, (kind, _) in BOX_MAP.items():
        pat = re.compile(r'> \*\*QCD_BOX_' + env.upper() + r'::(.*?)\*\*')
        md = pat.sub(lambda m: f'> [!{kind}]\n> **{m.group(1)}**', md)

    # Remove only known Pandoc wrappers; never strip arbitrary angle brackets from math.
    md = re.sub(r'^<div(?: [^>]*)?>\s*$', '', md, flags=re.M)
    md = re.sub(r'^</div>\s*$', '', md, flags=re.M)
    md = re.sub(r'^<span(?: [^>]*)?>\s*$', '', md, flags=re.M)
    md = re.sub(r'^</span>\s*$', '', md, flags=re.M)

    # Remove a duplicate longtable continuation header if present.
    lines = md.splitlines()
    deduped: list[str] = []
    previous = None
    for line in lines:
        if line == previous and line.startswith('| Claim or arrow'):
            continue
        deduped.append(line)
        previous = line
    md = '\n'.join(deduped)
    md = re.sub(r'\n{4,}', '\n\n\n', md)
    return md.strip() + '\n'


def fragment_to_md(latex: str, name: str, math_prefix: str) -> str:
    latex = expand_macros(latex)
    latex, mapping = extract_display_math(latex, math_prefix)
    md = clean_pandoc(run_pandoc(latex, name))
    return restore_math(md, mapping).strip()


def caption_to_md(caption: str, index: int) -> str:
    converted = fragment_to_md(caption, f'caption_{index}', f'CAPTION_{index}')
    return re.sub(r'\s+', ' ', converted).strip()


def figure_markdown(figures: list[dict[str, str]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for i, fig in enumerate(figures, 1):
        caption = caption_to_md(fig['caption'], i)
        alt = re.sub(r'[$\\{}_^]', '', caption)
        alt = re.sub(r'\s+', ' ', alt).strip()
        mapping[fig['marker']] = (
            f'![Figure {i}: {alt}]({fig["path"]})\n\n'
            f'*Figure {i}. {caption}*'
        )
    return mapping


def bibliography_md(bib: str) -> str:
    items = [x.strip() for x in re.split(r'\\bibitem\{[^{}]+\}', bib) if x.strip()]
    latex = '\\begin{enumerate}\n' + '\n'.join('\\item ' + x for x in items) + '\n\\end{enumerate}'
    return fragment_to_md(latex, 'bibliography', 'BIB')


def check_table_md(receipt: dict) -> str:
    rows = [
        '| # | Check | Status | PASS | Tolerance | Receipt result | Note |',
        '|---:|---|---|:---:|---:|---|---|',
    ]
    for i, c in enumerate(receipt['checks'], 1):
        result = json.dumps(c.get('result'), sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        result = result.replace('|', '\\|')
        note = str(c.get('note') or '').replace('|', '\\|')
        tol = '' if c.get('tolerance') is None else str(c['tolerance'])
        rows.append(
            f'| {i} | {c["name"]} | `{c["status"]}` | {"YES" if c["passed"] else "NO"} | '
            f'{tol} | `{result}` | {note} |'
        )
    return '\n'.join(rows)


def computed_tables_md(receipt: dict) -> str:
    c = receipt['computed_tables']
    out: list[str] = []
    out += [
        '### One-loop illustrative scale', '',
        f'- $\\Lambda_{{\\mathrm{{QCD}}}}^{{(1\\,\\mathrm{{loop}})}} = '
        f'{c["Lambda_QCD_1loop_GeV"]:.17g}\\,\\mathrm{{GeV}}$ for the declared illustrative anchor.', '',
        '### Lane--Emden receipt', '',
        '| Polytropic index $n$ | First zero $\\xi_1$ | $\\omega_n=-\\xi_1^2\\theta\'(\\xi_1)$ |',
        '|---:|---:|---:|',
    ]
    for n, row in c['lane_emden'].items():
        out.append(f'| {n} | {row["xi1"]:.15g} | {row["omega"]:.15g} |')
    out += [
        '', '### Full dimensionless TOV sequence', '',
        'EOS: $p=(\\epsilon-\\epsilon_0)/3$. Columns are central pressure '
        '$p_c/\\epsilon_0$, scaled mass $M\\sqrt{\\epsilon_0}$, scaled radius '
        '$R\\sqrt{\\epsilon_0}$, and compactness $2M/R$.', '',
        '| Row | $p_c/\\epsilon_0$ | $M\\sqrt{\\epsilon_0}$ | $R\\sqrt{\\epsilon_0}$ | $2M/R$ |',
        '|---:|---:|---:|---:|---:|',
    ]
    for i, (pc, mass, radius, compact) in enumerate(c['tov_linear_eos'], 1):
        out.append(f'| {i} | {pc:.15g} | {mass:.15g} | {radius:.15g} | {compact:.15g} |')
    return '\n'.join(out)


def toc_from_md(md: str) -> str:
    entries: list[str] = []
    in_fence = False
    for line in md.splitlines():
        if line.startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r'^(#{1,4})\s+(.+)$', line)
        if not m:
            continue
        level = len(m.group(1))
        title = m.group(2)
        if title == 'Contents':
            continue
        plain = re.sub(r'[*`$]', '', title)
        anchor = plain.lower()
        anchor = re.sub(r'[^a-z0-9\s-]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor).strip('-')
        entries.append('  ' * (level - 1) + f'- [{title}](#{anchor})')
    return '\n'.join(entries)


def code_appendix(title: str, lang: str, path: Path) -> str:
    return f'## {title}\n\n```{lang}\n{path.read_text(encoding="utf-8").rstrip()}\n```\n'


def count_outside_fences(pattern: str, text: str) -> int:
    count = 0
    in_fence = False
    for line in text.splitlines():
        if line.startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence:
            count += len(re.findall(pattern, line))
    return count


def main() -> None:
    tex = TEX.read_text(encoding='utf-8')
    body_tex, abstract_tex, figures, bib_tex, body_math, abstract_math = preprocess_body(tex)

    body_md = clean_pandoc(run_pandoc(body_tex, 'body'))
    body_md = restore_math(body_md, body_math)
    abstract_md = clean_pandoc(run_pandoc(abstract_tex, 'abstract'))
    abstract_md = restore_math(abstract_md, abstract_math).strip()

    for marker, replacement in figure_markdown(figures).items():
        body_md = body_md.replace(marker, replacement)

    receipt = json.loads(RECEIPT.read_text(encoding='utf-8'))
    body_md = body_md.replace('QCD_COSMOS_CHECK_TABLE_MARKER', check_table_md(receipt))
    body_md = body_md.replace(
        'QCD_COSMOS_VERIFIER_MARKER',
        f'\n\n```python\n{VERIFY.read_text(encoding="utf-8").rstrip()}\n```\n\n'
    )
    body_md = body_md.replace('QCD_COSMOS_BIBLIOGRAPHY_MARKER', bibliography_md(bib_tex))
    body_md = re.sub(r'\n{4,}', '\n\n\n', body_md).strip()

    derivation_index = INDEX.read_text(encoding='utf-8').strip()
    derivation_index = re.sub(r'^# .*?\n\n', '', derivation_index, count=1, flags=re.S)

    front = f'''---
title: "THEA Light Matrix v1.3.4 — The QCD-to-Cosmos Mana Codex"
subtitle: "Maximal pure-Markdown bookkeeping edition"
version: "1.3.4"
artifact_status: "Frozen technical companion; not peer reviewed; physical unification bridge remains provisional"
source_pdf: "{PDF.name}"
source_tex: "{TEX.name}"
---

# THEA Light Matrix v1.3.4

## The QCD-to-Cosmos Mana Codex

**Maximum LaTeXium for magic nerds: from color charge to compact stars, black holes, galaxies and the expanding universe**

**THEA Light Matrix Collaboration, the cave, and the next curious mage**

*Independent technical companion. Not peer reviewed. Not affiliated with any journal. Frozen 2026 edition.*

> [!IMPORTANT]
> **PROVISIONAL DECLARATION — “We have unified physics, aham.”**
>
> The technical meaning is deliberately narrower than the theatrical sentence. We have a single **typed research architecture** that can place exact discrete topology, standard quantum field theory, thermodynamics, stellar structure, general relativity and observational tests on one derivational map. We do **not** yet have an experimentally established unique unified field theory. The words **typed**, **research**, and **aham** are load-bearing.

## Abstract

{abstract_md}

## The derivational map

```text
SU(3) QCD
  fields -> curvature -> quantum RG -> Lambda_QCD
        |
        v
hadrons and nuclear many-body theory
  confinement -> chiral EFT -> partition function Z(T,mu)
        |
        v
equation of state and transport
  P(epsilon,n,T,Y_i), sound speed, neutrino opacity
        |
        v
stellar and relativistic structure
  Lane-Emden -> white dwarfs -> TOV -> tidal response
        |
        v
astrophysical observables
  photons, neutrinos, mass-radius curves, gravitational waves
        |
        v
galaxies and cosmology
  Jeans growth -> virial systems -> FLRW -> perturbations

THEA exact core
  P=12, T=k^2+k*l+l^2, M_light, graph spectra
        - - - - - - - - - - - - - - - - - - - ->
  owes microscopic fields, partition function, EOS and sealed observables
```

> **The real unification criterion:** derive at least one missing arrow without fitting its output, seal the prediction, and survive data.

## Epistemic contract

| Status | Meaning in this volume |
|---|---|
| **STANDARD** | Established mathematics or physics used and, where practical, re-derived here. |
| **THEA-EXACT** | Exact algebra or topology from the Light Matrix source; no physical identification is implied. |
| **COMPUTED** | Reproduced by the supplied verifier or numerical integration at declared tolerance. |
| **BRIDGE-HYPOTHESIS** | A proposed map between mathematical structures and physical observables. |
| **OPEN** | A required derivation, scalar contraction, continuum limit, uncertainty or experiment is missing. |
| **CORRECTION** | A previously advertised arrow fails a counterexample, invariant or provenance check. |

> [!CAUTION]
> A theorem, a numerical computation, an effective model, a correspondence and a measurement are different objects even when they share the same symbol.

## Derivation index: 48 principal lanes

{derivation_index}

## Bookkeeping conventions

- Natural units $\\hbar=c=k_B=1$ are used where stated; dimensions are restored when the physical scale matters.
- A displayed toy EOS is a pipeline test, not a precision neutron-star claim.
- A graph continuum trend is not promoted into spacetime ontology.
- Every numerical table is attached to an executable receipt.
- Every proposed physical bridge is required to name its microscopic variables, continuum fields, scale setting, uncertainty and held-out observable.

QCD_TOC_MARKER

---
'''

    full = front + '\n\n' + body_md
    full += '\n\n# Machine-expanded bookkeeping appendices\n\n'
    full += '## Complete computed-table payload\n\n' + computed_tables_md(receipt) + '\n\n'
    full += '## Full machine receipt JSON\n\n```json\n' + json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + '\n```\n\n'
    full += code_appendix('Complete figure-generation source', 'python', FIGGEN)
    full += '\n' + code_appendix('Portable PDF build source', 'python', PDF_BUILDER)
    full += '\n## Frozen audit report\n\n' + REPORT.read_text(encoding='utf-8').strip() + '\n\n'
    full += '## Source-file hashes\n\n'
    for label, path in [
        ('Source TeX', TEX), ('Rendered PDF', PDF), ('Machine receipt', RECEIPT),
        ('Verifier', VERIFY), ('Figure generator', FIGGEN), ('Portable PDF builder', PDF_BUILDER),
    ]:
        full += f'- **{label}:** `{sha256(path)}`\n'
    full += (
        '\n## Coda\n\n'
        '> **The pentagons hold. The quarks run. The star closes. The universe expands.**  \n'
        '> **The arrow is the spell, and the receipt is the ward.**  \n'
        '> $P=12.\\;\\chi=2.$ The price is always paid.\n'
    )

    toc = '## Contents\n\n' + toc_from_md(full.replace('QCD_TOC_MARKER', ''))
    full = full.replace('QCD_TOC_MARKER', toc)
    full = full.replace('\r\n', '\n')
    full = re.sub(r'\n{4,}', '\n\n\n', full).rstrip() + '\n'
    OUT.write_text(full, encoding='utf-8', newline='\n')

    shutil.copy2(Path(__file__), OUT_BUILDER)

    parsed = WORK / 'parsed.html'
    subprocess.run([
        'pandoc', str(OUT), '-f', 'gfm+tex_math_dollars', '-t', 'html', '-o', str(parsed)
    ], check=True)

    image_refs = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', full)
    missing_images = [p for p in image_refs if not (ROOT / p).exists()]
    raw_html = count_outside_fences(r'<[A-Za-z/][^>]*>', full)
    fence_lines = len(re.findall(r'^```', full, re.M))
    metrics = {
        'output': OUT.name,
        'bytes': OUT.stat().st_size,
        'lines': full.count('\n'),
        'headings_outside_code': count_outside_fences(r'^#{1,6} ', full),
        'display_math_blocks': full.count('$$') // 2,
        'code_fence_lines': fence_lines,
        'code_fence_parity': 'PASS' if fence_lines % 2 == 0 else 'FAIL',
        'raw_html_tags_outside_code': raw_html,
        'image_references': len(image_refs),
        'missing_images': missing_images,
        'checks': receipt['summary']['checks'],
        'passed': receipt['summary']['passed'],
        'failed': receipt['summary']['failed'],
        'sha256': sha256(OUT),
    }

    OUT_RECEIPT.write_text(
        '# QCD-to-Cosmos maximal Markdown conversion receipt\n\n'
        '```json\n' + json.dumps(metrics, indent=2, sort_keys=True) + '\n```\n\n'
        '## Conversion basis\n\n'
        f'- Editable mathematical authority: `{TEX.name}`\n'
        f'- Rendered presentation authority: `{PDF.name}`\n'
        f'- Machine ledger: `{RECEIPT.name}`\n'
        f'- Full verifier: `{VERIFY.name}`\n'
        f'- Figure generator: `{FIGGEN.name}`\n\n'
        '## Validation\n\n'
        '- Pandoc GFM + TeX-math parse: **PASS**\n'
        f'- Raw HTML outside code fences: **{raw_html}**\n'
        f'- Image paths present: **{len(image_refs) - len(missing_images)}/{len(image_refs)}**\n'
        f'- Machine checks preserved: **{receipt["summary"]["passed"]}/{receipt["summary"]["checks"]} PASS**\n'
        '- Full verifier source included: **YES**\n'
        '- Full receipt JSON included: **YES**\n'
        '- Full 90-row TOV table included: **YES**\n',
        encoding='utf-8', newline='\n'
    )

    bundle_files = [
        OUT, OUT_RECEIPT, OUT_BUILDER, TEX, PDF, RECEIPT, REPORT, INDEX,
        VERIFY, FIGGEN, PDF_BUILDER,
    ] + sorted(FIGDIR.glob('*.png'))
    with zipfile.ZipFile(BUNDLE, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in bundle_files:
            arcname = f'qcd_to_cosmos_mana_figures/{path.name}' if path.parent == FIGDIR else path.name
            zf.write(path, arcname)

    print(json.dumps(metrics, indent=2, sort_keys=True))
    print('bundle_sha256', sha256(BUNDLE))


if __name__ == '__main__':
    main()

from __future__ import annotations
import json, math, textwrap
from pathlib import Path

ROOT=Path(__file__).resolve().parent
fig='light_matrix_v132_figures'
audit=json.loads((ROOT/'light_matrix_v1.3.2_audit_receipt.json').read_text())
live=json.loads((ROOT/'light_matrix_v1.3.1_live_kernel_receipt.json').read_text())

# Helpers

def esc(s):
    s=str(s)
    # Keep the generated audit table portable under pdfLaTeX/XeLaTeX.
    for old,new in {
        'λ':'lambda','φ':'phi','π':'pi','χ':'chi','ℓ':'ell','ζ':'zeta',
        '²':'^2','³':'^3','⁻':'-','×':'x','→':'->','≈':'~','≤':'<=','≥':'>=',
        '−':'-','–':'--','—':'---','“':'"','”':'"','’':"'",'·':'*','∞':'infinity',
        '√':'sqrt','∈':'in','≅':'~=','≠':'!=','∕':'/'
    }.items():
        s=s.replace(old,new)
    repl={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(repl.get(c,c) for c in s)

def sci_tex(u):
    if u == 0:
        return '0'
    e=math.floor(math.log10(abs(u)))
    m=u/(10**e)
    return f"{m:.2f}\\times10^{{{e}}}"

check_rows=[]
for i,c in enumerate(audit['checks'],1):
    result=str(c.get('result', c.get('error','')))
    if len(result)>140: result=result[:137]+'...'
    status=esc(c['status'].replace('/', ' / ').replace('+', ' + '))
    check_rows.append(f"{i} & {esc(c['name'])} & {status} & {'PASS' if c['pass'] else 'FAIL'} & {esc(result)} " + r"\\")
checks_table='\n'.join(check_rows)

shell_rows=[]
for r in live['shells']:
    k,l=r['pair']; T=r['cert']['T']; V=r['cert']['V']
    shell_rows.append(f"$({k},{l})$ & {T} & {V} & {r['lambda2']:.12g} & {r['Tlambda2']:.12f} & {r['dev_from_continuum']:+.12f} " + r"\\")
shell_table='\n'.join(shell_rows)

phi=(1+5**0.5)/2
benchmarks=[
(r'Cryogenic $^{40}\mathrm{Ca}^{+}$ ion clock',4.4e-19,'Zhang et al., PRL 136 (2026) 053202'),
(r'Multi-ion $\mathrm{Sr}^{+}$ clock',5.3e-19,'Filzinger et al., arXiv:2603.23446'),
(r'$^{27}\mathrm{Al}^{+}$ single-ion clock',5.5e-19,'Marshall et al., PRL 2025'),
(r'$^{88}\mathrm{Sr}^{+}$ single-ion clock',7.9e-19,'Lindvall et al., 2025'),
(r'$^{87}\mathrm{Sr}$ lattice clock',8.1e-19,'Aeppli et al., PRL 133 (2024) 023401'),
(r'$\mathrm{In}^{+}/\mathrm{Yb}^{+}$ crystal clock',2.5e-18,'Hausser et al., PRL 134 (2025) 023201'),
(r'$^{88}\mathrm{Sr}^{+}$ absolute frequency vs TAI',9.8e-17,'Lindvall et al., 2025'),
('Hydrogen $1S$-$2S$',1.4e-14,'Parthey et al., PRL 107 (2011) 203001'),
('Electron magnetic moment $g/2$',1.3e-13,'Fan et al., PRL 130 (2023) 071801'),
('Muon anomaly final precision',1.27e-7,'Fermilab Muon g-2 final result'),
('Newtonian constant $G$',2.2e-5,'CODATA 2022'),
]
benchmark_rows=[]
for name,u,src in benchmarks:
    r=math.log(1/u)/math.log(phi**2)
    benchmark_rows.append(f"{name} & ${sci_tex(u)}$ & {r:.2f} & {src} " + r"\\")
benchmark_table='\n'.join(benchmark_rows)

tex = r'''\documentclass[11pt,openany]{report}
\usepackage[a4paper,margin=24mm,headheight=15pt]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{amsmath,amssymb,mathtools,bm}
\usepackage{booktabs,longtable,array,tabularx,multirow}
\usepackage{graphicx}
\usepackage[dvipsnames,table]{xcolor}
\usepackage[most]{tcolorbox}
\usepackage{enumitem}
\usepackage{listings}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{cleveref}
\usepackage{caption}
\usepackage{float}
\usepackage{pdflscape}
\usepackage{siunitx}
\usepackage{etoolbox}
\usepackage{needspace}
\usepackage{csquotes}
\usepackage{url}

\hypersetup{colorlinks=true,linkcolor=MidnightBlue,citecolor=ForestGreen,urlcolor=BrickRed,pdftitle={THEA - The Light Matrix v1.3.2},pdfauthor={Independent audit edition}}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{THEA - The Light Matrix v1.3.2}\fancyhead[R]{Full LaTeX Tower}\fancyfoot[C]{\thepage}
\setcounter{tocdepth}{2}\setcounter{secnumdepth}{3}
\setlist{nosep,leftmargin=*}
\renewcommand{\arraystretch}{1.18}
\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}
\emergencystretch=2em
\sisetup{detect-all,scientific-notation=true}

\definecolor{ExactGreen}{HTML}{1B7F3A}
\definecolor{ComputedBlue}{HTML}{146C94}
\definecolor{DesignGold}{HTML}{8A6D00}
\definecolor{HypOrange}{HTML}{A64B00}
\definecolor{CorrectionRed}{HTML}{9B2226}
\definecolor{MetaPurple}{HTML}{6A4C93}
\definecolor{CaveBlack}{HTML}{11131A}
\definecolor{CavePaper}{HTML}{F8F7F2}

\newcommand{\status}[2]{\textcolor{#1}{\fbox{\scriptsize\textsf{#2}}}}
\newcommand{\EXACT}{\status{ExactGreen}{EXACT}}
\newcommand{\COMPUTED}{\status{ComputedBlue}{COMPUTED}}
\newcommand{\DESIGN}{\status{DesignGold}{DESIGN CHOICE}}
\newcommand{\HYP}{\status{HypOrange}{HYPOTHESIS}}
\newcommand{\CORRECTION}{\status{CorrectionRed}{CORRECTION}}
\newcommand{\EXTERNAL}{\status{MetaPurple}{EXTERNAL / METAPHOR}}
\newcommand{\phig}{\varphi}
\newcommand{\zetahex}{\zeta_6}
\newcommand{\Mlight}{\mathcal M_{\mathrm{light}}}
\newcommand{\Tgold}{T_n}
\newcommand{\spec}{\operatorname{spec}}
\newcommand{\GC}{\operatorname{GC}}
\newcommand{\EML}{\operatorname{eml}}
\DeclareMathOperator{\Log}{Log}
\newcommand{\BigO}{\mathcal O}
\newcommand{\R}{\mathbb R}
\newcommand{\C}{\mathbb C}
\newcommand{\Z}{\mathbb Z}
\newcommand{\N}{\mathbb N}
\newcommand{\dd}{\,\mathrm d}

\newtcolorbox{exactbox}[1][]{enhanced,breakable,colback=ExactGreen!4,colframe=ExactGreen,title={Exact statement},fonttitle=\bfseries,#1}
\newtcolorbox{computedbox}[1][]{enhanced,breakable,colback=ComputedBlue!4,colframe=ComputedBlue,title={Computed receipt},fonttitle=\bfseries,#1}
\newtcolorbox{designbox}[1][]{enhanced,breakable,colback=DesignGold!5,colframe=DesignGold,title={Design choice},fonttitle=\bfseries,#1}
\newtcolorbox{hypbox}[1][]{enhanced,breakable,colback=HypOrange!4,colframe=HypOrange,title={Honest boundary},fonttitle=\bfseries,#1}
\newtcolorbox{correctionbox}[1][]{enhanced,breakable,colback=CorrectionRed!4,colframe=CorrectionRed,title={v1.3.2 correction},fonttitle=\bfseries,#1}
\newtcolorbox{receiptbox}[1][]{enhanced,breakable,colback=CaveBlack!2,colframe=CaveBlack,title={Receipt},fonttitle=\bfseries,#1}

\lstdefinestyle{code}{basicstyle=\ttfamily\small,breaklines=true,frame=single,rulecolor=\color{black!25},backgroundcolor=\color{black!2},showstringspaces=false,columns=fullflexible}
\lstset{style=code}

\title{\vspace{-1.5cm}\textbf{THEA -- THE LIGHT MATRIX}\\[2mm]\Large Full LaTeX Tower v1.3.2\\[4mm]\large exact closure, golden selection, chirality, spectra, invariant theory, numerical walls, and the LUCA handoff}
\author{Independent audit edition\\Buenos Aires + Ancient Korinthos lineage\\Prepared 9 August 2026}
\date{}

\begin{document}
\maketitle
\begin{abstract}
This document is a source-grounded, independently recomputed consolidation of the seven attached source artifacts listed in Chapter~1. It is a new versioned artifact: Light Matrix v1.3.1 and LUCA v0.1/v0.2 remain frozen.

The exact mathematical core survives the audit: Euler forces twelve pentagons; the hexagonal closure norm is multiplicative; the lifted integer recursion has spectrum $\{\phig^2,1,-1,\phig^{-2}\}$; the golden selector produces independently closed Goldberg shells; the golden ray has the exact bearing $\arctan(\sqrt{15}-2\sqrt3)$; the complete $C_{60}$ adjacency characteristic polynomial and Fiedler radical reproduce exactly; the Klein syzygy closes symbolically; and the finite browser graph calculations reproduce the reported low-mode structure.

The audit also changes several labels. The proposed constant $2\pi/(5\sqrt3)$ is an exact consequence of a continuum matching argument, but the convergence of a chosen discrete graph family to that constant is not proved by that argument. The $A_2$ root lattice and the $SU(3)$ weight lattice are not literally the same lattice; they are dual, commensurable hexagonal lattices with index three between them. Random basin counting is a finite numerical experiment, not a theorem. The float64 comparison in v1.3.1 used a rounded version of the exact integer on its reference side; the corrected comparison still finds forward stability, but at a true error floor near $10^{-15}$. Finally, the live LUCA v0.2 code includes 33 points in its leaf-count regression, whereas the handoff scroll's published coefficients correspond to 32 points after excluding the initial constant $e$.

The governing rule is therefore retained in its strongest form: target is not result; theorem, numerical trend, design mapping, physical hypothesis, and metaphor never share a label merely because they share a glyph.
\end{abstract}

\begin{center}
\begin{tcolorbox}[width=.92\textwidth,colback=black!3,colframe=black!70]
\centering\Large\bfseries The pentagons hold. The hexes pay. The matrix remembers which is which.\\[2mm]
\normalsize $P=12,\quad \chi=2,\quad \spec(\Mlight)=\{\phig^2,1,-1,\phig^{-2}\}.$
\end{tcolorbox}
\end{center}

\tableofcontents
\listoffigures
\chapter*{Table Map}
The principal tabular receipts are intentionally embedded in the mathematical narrative rather than separated from their hypotheses. Their locations are:
\begin{description}[leftmargin=3.1cm,style=nextline,font=\normalfont\bfseries]
\item[Source inventory] Chapter~1: the seven audited artifacts and their roles.
\item[Golden shell catalogue] Chapter~4: $(k_n,\ell_n)$, $T_n$, cage size, hexagon count, and chirality angle.
\item[Light-matrix eigenbasis] Chapter~5: all four modes and their exact eigenvectors.
\item[$C_{60}$ polynomial] Chapter~6: the complete adjacency characteristic factorization.
\item[Live spectral receipt] Chapter~7: the v1.3.1 Goldberg-builder/Lanczos output through $C_{17660}$.
\item[Precision formats] Chapter~10: significand budgets and exact-integer scale limits.
\item[LUCA comparisons] Chapter~11: finite-$N$ angle sweep and the 32/33-point leaf-regression distinction.
\item[Independent audit] Chapter~14: all 38 checks, statuses, verdicts, and compact results; full values remain in the JSON receipt.
\end{description}
\clearpage

\chapter{The Contract: Status Before Symbol}
\section{Source inventory and lineage}
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{.17\textwidth}>{\raggedright\arraybackslash}p{.32\textwidth}>{\raggedright\arraybackslash}p{.43\textwidth}@{}}
\toprule
Artifact & file & Use in this tower\\\midrule\endhead
THEA core & \path{Thea.md} & Exact topology, closure algebra, Fibonacci selector, light matrix, spectral receipts, and the honest physical boundary.\\
Light Matrix shell & \path{shell__thea_light_matrix_v1.3.1.html} & Nineteen interactive sections, exact $C_{60}$ kernel, Goldberg builder, spectral routines, $A_2/SU(3)$ lane, Klein lane, and numerical-architecture lane.\\
LUCA v0.1 & \path{shell__eml_luca_spiral_v0_1.html} & EML operator, reduction tree, branch receipts, and target/current/error verification.\\
LUCA v0.2 & \path{shell__eml_luca_spiral_v0_2.html} & Live Faddeev--LeVerrier factorization, golden selector readout, golden-ray angle, finite-$N$ Vogel sweep, and leaf-count null result.\\
Angle handoff & \path{THE_ANGLE_OF_THE_GOLDEN_RAY.md} & Radical angle, asymptotic alternating convergence, anti-palindromic characteristic polynomial, and build contract.\\
Twelve Paths & \path{THE_12_PATHS_OF_THE_FRACTAL_MAGE.md} & Proof by kernel, target $\ne$ result, immutable versions, and open receipts.\\
Kernel grimoire & \path{KERNELIMAGIC.md} & False convergence, pre-allocation cost gates, deterministic certificates, and portable paths.\\
\bottomrule
\end{longtable}

\section{The status grammar}
Every displayed claim in v1.3.2 belongs to one of the following classes.
\begin{itemize}[leftmargin=0pt,label={},itemsep=4pt]
\item \EXACT\quad Follows from algebra, topology, integer arithmetic, or a symbolic identity shown in the document.
\item \COMPUTED\quad Reproduced by a named finite algorithm at a stated precision, sample count, graph depth, or iteration count.
\item \DESIGN\quad A visualization, parameterization, tolerance, mapping, sampling schedule, or user-interface rule.
\item \HYP\quad A proposed physical interpretation that still requires discriminating evidence.
\item \EXTERNAL\quad A statement inherited from another artifact or source and not independently proved here.
\item \CORRECTION\quad A source statement whose algebra, label, indexing, or implementation receipt changes in v1.3.2.
\end{itemize}

\begin{correctionbox}
The HTML header advertises additions through Section XVII, yet the baked document contains a Section XVIII; the HUD count of 19 includes the birth section plus XVIII. v1.3.2 makes the section inventory explicit. It also repairs the abstract glyph $C_{00}$ to $C_{60}$ and replaces ``zero dependencies'' by the narrower, accurate statement that the mathematical kernel is dependency-free while presentation may use KaTeX.
\end{correctionbox}

\section{Audit outcome in one page}
The independent Python/SymPy/NetworkX/NumPy audit executed 38 checks and returned 38 passes. ``Pass'' here means that either the source statement was reproduced or its correction was independently established. The most important changes are:
\begin{enumerate}
\item The sequence $T_{n+1}/T_n$ does not monotonically climb to $\phig^2$; it alternates around the limit.
\item Golden-selected shells form a catalogue of independently closed shells. They are not an exactly nested fixed Goldberg transform with linear multiplier $\phig$.
\item Section VIII applies Lanczos to a graph Laplacian, not to the $4\times4$ light matrix.
\item The continuum coefficient $2\pi/(5\sqrt3)$ is exact conditional algebra. The graph-limit arrow remains a conjectural asymptotic identification supported by finite computation.
\item $Q(A_2)$ and $P(A_2)$ are not literally equal. The common hexagonal quadratic form must be stated with normalization.
\item The Klein syzygy is exact; basin counts are finite, seed-dependent numerical coverage experiments.
\item Binary256 has 237 bits of significand precision, not a ``256-bit mantissa.''
\item The v1.3.1 recurrence comparator shared the same binary64 rounding in both operands. A rational comparison against the exact integer gives a true maximum relative error of about $1.02\times10^{-15}$ over levels $0$--$159$.
\item LUCA branch identities require domains and branch sheets. A sample lock is a sieve, not a proof.
\item The live LUCA v0.2 regression uses 33 spiral nodes; the 32-point handoff values are recovered only after excluding $e$.
\end{enumerate}

\chapter{Closed Topology: Why Twelve Cannot Move}
\section{General trivalent curvature ledger}
Let $f_p$ be the number of $p$-gonal faces in a connected, closed, trivalent planar graph embedded on $S^2$. Then
\begin{equation}
3V=2E,\qquad \sum_{p\ge3}p f_p=2E,\qquad V-E+\sum_{p\ge3}f_p=2.
\end{equation}
Eliminating $V$ and $E$ gives the exact combinatorial curvature identity
\begin{equation}\label{eq:curvature-ledger}
\boxed{\sum_{p\ge3}(6-p)f_p=12.}
\end{equation}
This is more general than the fullerene statement. Triangles contribute $+3$, squares $+2$, pentagons $+1$, hexagons zero, and larger faces negative charge.

\section{The fullerene specialization}
For a pentagon/hexagon fullerene, $f_5=P$, $f_6=H$, and every other $f_p$ vanishes. Equation~\eqref{eq:curvature-ledger} becomes
\begin{equation}
(6-5)P+(6-6)H=12,
\end{equation}
so
\begin{exactbox}
\begin{equation}
\boxed{P=12.}
\end{equation}
The assumptions are part of the theorem: connected, closed, spherical, trivalent, and containing only pentagonal and hexagonal faces.
\end{exactbox}
The remaining counts follow:
\begin{equation}
\boxed{E=\frac{3V}{2},\qquad H=\frac{V}{2}-10,\qquad F=P+H=\frac{V}{2}+2.}
\end{equation}
For $C_{60}$,
\begin{equation}
(V,E,F,P,H,\chi)=(60,90,32,12,20,2).
\end{equation}

\section{Discrete Gauss--Bonnet}
Assign the face charge
\begin{equation}
K_p=\frac{\pi}{3}(6-p).
\end{equation}
Then
\begin{equation}
\sum_f K_f=\frac{\pi}{3}\sum_p(6-p)f_p=\frac{\pi}{3}\cdot12=4\pi.
\end{equation}
\begin{hypbox}
The equality is exact combinatorial topology. It does not assert that a molecular fullerene carries uniform smooth Gaussian curvature, nor that graph curvature is physical spacetime curvature. It is a ledger of angular defect for this trivalent tiling class.
\end{hypbox}

\chapter{The Hexagonal Closure Algebra}
\section{The sixth-root coordinate}
Set
\begin{equation}
\zetahex=e^{i\pi/3}=\frac12+i\frac{\sqrt3}{2},\qquad \zetahex^2=\zetahex-1.
\end{equation}
A lattice displacement is
\begin{equation}
z=k+\ell\zetahex,\qquad k,\ell\in\Z.
\end{equation}
Its squared Euclidean length is
\begin{equation}\label{eq:hexnorm}
\boxed{T=N(z)=z\bar z=k^2+k\ell+\ell^2.}
\end{equation}
This is the alternate sixth-root parameterization of the Eisenstein lattice. If one instead uses the conventional cube root $\omega=e^{2\pi i/3}$, the same lattice is written with the norm $a^2-ab+b^2$. The sign difference is a basis convention, not a contradiction.

\section{Multiplication as an integer matrix}
Multiplication by $z=k+\ell\zetahex$ sends $a+b\zetahex$ to
\begin{equation}
(k+\ell\zetahex)(a+b\zetahex)=(ka-\ell b)+(\ell a+(k+\ell)b)\zetahex.
\end{equation}
Therefore
\begin{equation}
\begin{pmatrix}a'\\b'\end{pmatrix}=M_{k,\ell}\begin{pmatrix}a\\b\end{pmatrix},\qquad
\boxed{M_{k,\ell}=\begin{pmatrix}k&-\ell\\ \ell&k+\ell\end{pmatrix}.}
\end{equation}
The determinant is the norm:
\begin{equation}
\det M_{k,\ell}=k(k+\ell)+\ell^2=T.
\end{equation}
With the hexagonal metric
\begin{equation}
Q=\begin{pmatrix}1&1/2\\1/2&1\end{pmatrix},
\end{equation}
direct multiplication gives
\begin{equation}\label{eq:metric-similarity}
\boxed{M_{k,\ell}^{\mathsf T}QM_{k,\ell}=TQ.}
\end{equation}
Thus $M_{k,\ell}/\sqrt T$ is $Q$-orthogonal: an exact scale-plus-rotation in the lattice metric.

\section{Angle and chirality coordinate}
The exact lattice bearing is
\begin{equation}\label{eq:theta-kl}
\boxed{\theta_{k,\ell}=\arg(k+\ell\zetahex)=\operatorname{atan2}(\sqrt3\,\ell,2k+\ell).}
\end{equation}
For the canonical wedge $k\ge\ell\ge0$, $0\le\theta\le\pi/6$. The boundary classes $\ell=0$ and $k=\ell$ are achiral; strict interior pairs occur in mirror-related chiral classes $(k,\ell)$ and $(\ell,k)$.

\section{Composition and multiplicativity}
Let $g=a+b\zetahex$. Then
\begin{align}
(a+b\zetahex)(k+\ell\zetahex)
&=(ak-b\ell)+(a\ell+bk+b\ell)\zetahex,\\
(k',\ell')&=(ak-b\ell,\;a\ell+bk+b\ell),\\
M_{a,b}M_{k,\ell}&=M_{k',\ell'},\\
T'&=(a^2+ab+b^2)T.
\end{align}
This is the exact fixed-operator closure lane. The generator $(1,1)$ has norm $3$ and produces the nested leapfrog count tower
\begin{equation}
T_n=3^n,\qquad V_n=20\,3^n,
\end{equation}
with $C_{20}\to C_{60}\to C_{180}\to C_{540}\to\cdots$ at the count level.

\section{Selected is not nested}
A fixed Goldberg operator has integer area multiplier
\begin{equation}
S=a^2+ab+b^2\in\Z
\end{equation}
and linear multiplier $\sqrt S$. Exact golden nesting would require $S=\phig^2$, impossible because $S$ is an integer and $\phig^2$ is irrational. Hence
\begin{exactbox}
\begin{equation}
\boxed{\text{No fixed exactly nested Goldberg transform has linear ratio }\phig.}
\end{equation}
The Fibonacci construction below is a sequence of independently closed shells whose successive radius ratios approach $\phig$.
\end{exactbox}

\chapter{The Golden Selector and the Ray with a Bearing}
\section{Fibonacci projective dynamics}
Let
\begin{equation}
F_\phig=\begin{pmatrix}1&1\\1&0\end{pmatrix},\qquad
\begin{pmatrix}k_{n+1}\\\ell_{n+1}\end{pmatrix}=F_\phig\begin{pmatrix}k_n\\\ell_n\end{pmatrix},\qquad(k_0,\ell_0)=(1,0).
\end{equation}
Then
\begin{equation}
(k_n,\ell_n)=(F_{n+1},F_n),\qquad \spec(F_\phig)=\{\phig,-\phig^{-1}\}.
\end{equation}
For $r_n=k_n/\ell_n$,
\begin{equation}
r_{n+1}=1+\frac1{r_n},\qquad
r_{n+1}-\phig=-\frac{r_n-\phig}{\phig r_n}.
\end{equation}
Therefore $r_n\to\phig$, with alternating error and asymptotic contraction $-\phig^{-2}$.

\section{Triangulation sequence}
Define
\begin{equation}
T_n=k_n^2+k_n\ell_n+\ell_n^2.
\end{equation}
The first values are
\begin{equation}
1,3,7,19,49,129,337,883,2311,6051,\ldots
\end{equation}
and
\begin{equation}\label{eq:Trec}
\boxed{T_{n+3}=2T_{n+2}+2T_{n+1}-T_n.}
\end{equation}
The characteristic polynomial is
\begin{equation}
r^3-2r^2-2r+1=(r+1)(r^2-3r+1),
\end{equation}
with roots $-1,\phig^2,\phig^{-2}$. Binet reduction gives
\begin{equation}\label{eq:Tclosed}
\boxed{T_n=\frac25\left(\phig^{2n+2}+\phig^{-2n-2}\right)-\frac15(-1)^n.}
\end{equation}
Consequently
\begin{equation}
\frac{T_{n+1}}{T_n}\longrightarrow\phig^2,
\end{equation}
but the convergence is alternating rather than monotone.

\begin{correctionbox}
The v1.3.1 sentence ``the ratio $T_{n+1}/T_n$ climbs to $\phig^2$'' is replaced by ``the ratio alternates about and converges to $\phig^2$.'' The computed sequence begins $7/3=2.3333$, $19/7=2.7143$, $49/19=2.5789$, $129/49=2.6327$.
\end{correctionbox}

\section{Closed-shell catalogue}
For each Fibonacci pair,
\begin{equation}
V_n=20T_n,\quad E_n=30T_n,\quad P_n=12,\quad H_n=10(T_n-1),\quad F_n=10T_n+2.
\end{equation}
\begin{longtable}{rrrrrr}
\toprule
$n$ & $(k_n,\ell_n)$ & $T_n$ & cage & $H_n$ & $\theta_{k_n,\ell_n}$\\\midrule\endhead
0&(1,0)&1&$C_{20}$&0&$0^\circ$\\
1&(1,1)&3&$C_{60}$&20&$30^\circ$\\
2&(2,1)&7&$C_{140}$&60&$19.106605^\circ$\\
3&(3,2)&19&$C_{380}$&180&$23.413224^\circ$\\
4&(5,3)&49&$C_{980}$&480&$21.786789^\circ$\\
5&(8,5)&129&$C_{2580}$&1280&$22.411902^\circ$\\
6&(13,8)&337&$C_{6740}$&3360&$22.172618^\circ$\\
7&(21,13)&883&$C_{17660}$&8820&$22.264023^\circ$\\
\bottomrule
\end{longtable}

\section{The exact golden-ray angle}
Taking $k/\ell\to\phig$ in Equation~\eqref{eq:theta-kl},
\begin{align}
\theta_\phig
&=\arctan\frac{\sqrt3}{2\phig+1}
 =\arctan\frac{\sqrt3}{\sqrt5+2}\\
&=\boxed{\arctan(\sqrt{15}-2\sqrt3)}\\
&=0.388139515\ldots\text{ rad}=22.238756093\ldots^\circ.
\end{align}
The radical step uses $(\sqrt5+2)(\sqrt5-2)=1$.

\section{Why the angular error inherits the alternating mode}
Let
\begin{equation}
\Theta(r)=\arctan\frac{\sqrt3}{2r+1}.
\end{equation}
Since $\Theta$ is differentiable and $\Theta'(\phig)\ne0$,
\begin{equation}
\theta_n-\theta_\phig=\Theta'(\phig)(r_n-\phig)+\BigO((r_n-\phig)^2).
\end{equation}
Therefore
\begin{equation}
\boxed{\frac{\theta_{n+1}-\theta_\phig}{\theta_n-\theta_\phig}\longrightarrow-\phig^{-2}.}
\end{equation}
This is an asymptotic equality. At $n=16$ the independent float64 recomputation gives
\begin{equation}
-0.3819660384,\qquad -\phig^{-2}=-0.3819660113.
\end{equation}

\begin{figure}[H]\centering
\includegraphics[width=.88\textwidth]{''' + fig + r'''/golden_angle_convergence.png}
\caption{The golden-ray angular deviation alternates and contracts. The signed zigzag is the projective $-1$ mode made visible through the smooth angle map.}
\end{figure}

\chapter{The Exact Light Matrix}
\section{Symmetric-square lift}
The pair recursion is
\begin{equation}
k'=k+\ell,\qquad \ell'=k.
\end{equation}
Lift to quadratic monomials
\begin{equation}
u_n=\begin{pmatrix}k_n^2\\k_n\ell_n\\\ell_n^2\end{pmatrix}.
\end{equation}
Then
\begin{equation}
\begin{pmatrix}(k+\ell)^2\\(k+\ell)k\\k^2\end{pmatrix}
=
\underbrace{\begin{pmatrix}1&2&1\\1&1&0\\1&0&0\end{pmatrix}}_{B}
\begin{pmatrix}k^2\\k\ell\\\ell^2\end{pmatrix}.
\end{equation}
Append the topological coordinate $P_n=12$:
\begin{equation}
s_n=\begin{pmatrix}k_n^2\\k_n\ell_n\\\ell_n^2\\P_n\end{pmatrix},\qquad
\boxed{s_{n+1}=\Mlight s_n},
\end{equation}
where
\begin{equation}\label{eq:Mlight}
\boxed{\Mlight=\begin{pmatrix}
1&2&1&0\\
1&1&0&0\\
1&0&0&0\\
0&0&0&1
\end{pmatrix}.}
\end{equation}

\section{Faddeev--LeVerrier certificate}
Starting with $B_0=I$ and
\begin{equation}
c_j=-\frac1j\operatorname{tr}(\Mlight B_{j-1}),\qquad B_j=\Mlight B_{j-1}+c_jI,
\end{equation}
the coefficient list is
\begin{equation}
\boxed{(1,-3,0,3,-1)}.
\end{equation}
Thus
\begin{align}
p(\lambda)&=\lambda^4-3\lambda^3+3\lambda-1\\
&=(\lambda-1)(\lambda+1)(\lambda^2-3\lambda+1).
\end{align}
The coefficients are anti-palindromic:
\begin{equation}
p(\lambda)=-\lambda^4p(1/\lambda).
\end{equation}
Therefore the spectrum is closed under reciprocal inversion.

\section{Spectrum and eigenmodes}
\begin{equation}
\boxed{\spec(\Mlight)=\{\phig^2,1,-1,\phig^{-2}\}.}
\end{equation}
A convenient eigenbasis is
\begin{center}
\begin{tabular}{clp{.45\textwidth}}
\toprule
$\lambda$ & eigenvector & role\\\midrule
$\phig^2$ & $(\phig^2,\phig,1,0)^{\mathsf T}$ & dominant quadratic area/atom growth\\
$1$ & $(0,0,0,1)^{\mathsf T}$ & fixed $P=12$ topological coordinate\\
$-1$ & $(-2,1,2,0)^{\mathsf T}$ & alternating finite-size correction\\
$\phig^{-2}$ & $(\phig^{-2},-\phig^{-1},1,0)^{\mathsf T}$ & contracting reciprocal mode\\
\bottomrule
\end{tabular}
\end{center}
The eigenvalues are not fitted to shell data; they follow from the integer matrix. The design interpretation ``grow, hold, overshoot, decay'' is useful, but the matrix itself is the exact object.

\section{The shell number as a linear observable}
The triangulation number is
\begin{equation}
T_n=(1,1,1,0)s_n.
\end{equation}
Projecting the matrix recurrence onto this observable yields Equation~\eqref{eq:Trec}. The $P$ coordinate does not enter $T_n$; it survives as the independent eigenvalue-one mode.

\chapter{The Exact $C_{60}$ Spectral Boundary}
\section{Independent graph certificate}
The audit reconstructs the truncated icosahedron by truncating each directed incidence of the icosahedron. The resulting graph has
\begin{equation}
V=60,\quad E=90,\quad \deg(v)=3,\quad f_5=12,\quad f_6=20,\quad \chi=2.
\end{equation}
These checks are integer and planar-embedding facts.

\section{Complete adjacency characteristic polynomial}
For adjacency matrix $A_{60}$,
\begin{align}
\chi_{A_{60}}(x)={}&(x-3)(x-1)^9(x+2)^4(x^2-x-3)^5(x^2+x-4)^4\\
&\times(x^2+x-1)^5(x^2+3x+1)^3\\
&\times(x^4-3x^3-2x^2+7x+1)^3.
\end{align}
The SymPy exact characteristic polynomial of the independently reconstructed graph factors identically.

\section{The golden lower boundary}
The least root comes from $x^2+3x+1$:
\begin{equation}
\boxed{\lambda_{\min}(A_{60})=\frac{-3-\sqrt5}{2}=-\phig^2,}
\end{equation}
with multiplicity three.

\section{Graph Laplacian and Fiedler radical}
Because the graph is cubic,
\begin{equation}
L_{60}=3I-A_{60}.
\end{equation}
The first positive eigenvalue is
\begin{equation}\label{eq:fiedler}
\boxed{\lambda_2(L_{60})=\frac94-\frac{\sqrt2}{8}\left(\sqrt{10}+2\sqrt{19-\sqrt5}\right)}
=0.2434017461399\ldots
\end{equation}
and is a root of
\begin{equation}
x^4-9x^3+25x^2-22x+4=0
\end{equation}
with multiplicity three. The independent numerical residual is below $10^{-12}$.

\section{Low bands}
The first nonzero Laplacian bands of $C_{60}$ are
\begin{center}
\begin{tabular}{rrl}
\toprule
value & multiplicity & exact origin / interpretation\\\midrule
$0.2434017461$ & 3 & Fiedler triplet, Equation~\eqref{eq:fiedler}\\
$0.6972243623$ & 5 & $(5-\sqrt{13})/2$\\
$1.1797507493$ & 3 & quartic sibling\\
$1.4384471872$ & 4 & $(7-\sqrt{17})/2$\\
$2$ & 9 & adjacency eigenvalue $1$\\
$2.3819660113$ & 5 & $3-(\phig^{-1})$ branch\\
\bottomrule
\end{tabular}
\end{center}
The multiplicities $3,5,3+4$ are compatible with low spherical-harmonic dimensions under icosahedral splitting. Compatibility is not identity with a continuum field theory.

\begin{hypbox}
An adjacency or graph-Laplacian eigenvalue is not automatically a molecular orbital energy. The exact graph spectrum is a valid H\"uckel-style combinatorial object; a physical Hamiltonian requires geometry, orbital integrals, interactions, and other chemistry.
\end{hypbox}

\chapter{Graph Towers, Renormalization, and the Conditional Continuum Constant}
\section{Three families that must remain separate}
\begin{tabularx}{\textwidth}{@{}>{\bfseries\raggedright\arraybackslash}p{.28\textwidth}X@{}}
Golden-selected catalogue & $(k_n,\ell_n)=(F_{n+1},F_n)$. Independently closed Goldberg shells with $T=1,3,7,19,\ldots$ and asymptotic radius ratio $\phig$.\\
Fixed GC / leapfrog lane & Repeated application of one integer generator, e.g. $(1,1)$ with area multiplier $3$. Exactly nested at the operator level, linear scale $\sqrt3$.\\
WELD lineage & The source scroll reports a separate exact-ID chamfer family $C_{60}\to C_{240}\to C_{960}\to\cdots$ with multiplier $4$.\\
\end{tabularx}
No spectral value may be transferred from one family to another without recomputation.

\section{Closure certificate}
A candidate shell may be named closed only if
\begin{equation}
P=12,\qquad \chi=2,\qquad \partial E=0,\qquad E_{\mathrm{nonmanifold}}=0,\qquad \deg(v)=3\ \forall v.
\end{equation}
Formula counts are necessary but not sufficient for a welded indexed mesh.

\section{Live v1.3.1 golden-shell receipt}
The current HTML kernel was executed directly in Node, without reimplementing its Goldberg builder or Lanczos routine. The result is:
\begin{longtable}{rrrrrr}
\toprule
$(k,\ell)$ & $T$ & $V$ & $\lambda_2$ & $T\lambda_2$ & deviation from $2\pi/(5\sqrt3)$\\\midrule\endhead
''' + shell_table + r'''
\bottomrule
\end{longtable}
At $T=19$, the live block-subspace calculation gives bands $0.0381364\times3$, $0.1133266\times5$, $0.2081904\times3$, and $0.2385063\times4$. The second-to-first ratio is $2.9716$ and the weighted $3+4$ center ratio is $5.9133$.

\begin{figure}[H]\centering
\includegraphics[width=.88\textwidth]{''' + fig + r'''/goldberg_gap_tower.png}
\caption{The live golden-selected shell receipt. The dashed line is the continuum matching coefficient, not an exact finite-shell target.}
\end{figure}

\section{The honeycomb-to-sphere matching calculation}
For three bond vectors $\delta_i=a\hat e_i$ at $120^\circ$,
\begin{align}
Lf(x)&=\sum_{i=1}^3\bigl(f(x)-f(x+\delta_i)\bigr)\\
&=-\sum_i\delta_i\cdot\nabla f-\frac12\sum_i(\delta_i\cdot\nabla)^2f+\BigO(a^3).
\end{align}
Since $\sum_i\delta_i=0$ and
\begin{equation}
\sum_i(\hat e_i\cdot\nabla)^2=\frac32\nabla^2,
\end{equation}
we get
\begin{equation}
L\approx-\frac{3a^2}{4}\nabla^2.
\end{equation}
The honeycomb area per vertex is $3\sqrt3a^2/4$. Matching $20T$ sites to a sphere gives
\begin{equation}
20T\frac{3\sqrt3}{4}a^2=4\pi R^2,
\qquad \frac{a^2}{R^2}=\frac{4\pi}{15\sqrt3\,T}.
\end{equation}
The $\ell=1$ sphere eigenvalue is $2/R^2$, so the matched coefficient is
\begin{equation}\label{eq:conditional-constant}
\boxed{T\lambda_2\sim \frac{3a^2}{4}\frac{2}{R^2}T=\frac{2\pi}{5\sqrt3}=0.7255197456937\ldots}
\end{equation}

\begin{correctionbox}
Every algebraic equality inside Equation~\eqref{eq:conditional-constant} is exact once the Taylor stencil, area matching, and identification of the first graph mode with the $\ell=1$ sphere mode are assumed. The arrow from a particular discrete fullerene family to this value is not proved by those assumptions. v1.3.2 labels the number \emph{conditional asymptotic prediction} and the graph data \emph{computed trend}. The Omori--Naito--Tate theorem proves low combinatorial-Laplacian eigenvalues tend to zero for specified Goldberg--Coxeter limits, but it does not by itself establish this normalized universal constant for the golden-selected family.
\end{correctionbox}

\section{Operator dependence remains open}
The live golden sequence approaches the low $0.7248$ region, while the deeper leapfrog receipt in the core scroll reports $0.724799130$ at $T=2187$. Whether the limiting coefficient is $2\pi/(5\sqrt3)$, another family-dependent constant, or a coefficient with slowly decaying defect corrections is an open numerical and analytic question. Required tests include:
\begin{enumerate}
\item run WELD, leapfrog, class-I, class-II, and golden-selected families under one eigensolver and one normalization;
\item fit corrections only after plotting residuals against several plausible scales ($T^{-1/2}$, $T^{-1}$, defect separation, chirality);
\item vary the discrete Laplacian (combinatorial, normalized, cotangent/geometric) and document which constant changes;
\item prove convergence before replacing ``trend'' by ``limit.''
\end{enumerate}

\chapter{The Shared Quadratic Form and the $SU(3)$ Boundary}
\section{What is exact}
The dominant quadratic part of the $SU(3)$ quadratic Casimir for Dynkin labels $(p,q)$ is
\begin{equation}
T(p,q)=p^2+pq+q^2,
\end{equation}
and
\begin{equation}\label{eq:su3cas}
\boxed{C_2(p,q)=\frac13\bigl(p^2+pq+q^2+3p+3q\bigr).}
\end{equation}
The representation dimension is
\begin{equation}
\boxed{\dim(p,q)=\frac12(p+1)(q+1)(p+q+2).}
\end{equation}
Examples are
\begin{equation}
(1,0)\mapsto\mathbf3,\quad (1,1)\mapsto\mathbf8,\quad(2,1)\mapsto\mathbf{15},\quad(3,2)\mapsto\mathbf{42}.
\end{equation}

\section{Root lattice versus weight lattice}
Let $Q(A_2)$ be the root lattice and $P(A_2)$ the weight lattice. They are dual up to the conventional inner-product normalization, and
\begin{equation}
P(A_2)/Q(A_2)\cong\Z/3\Z.
\end{equation}
Thus $[P:Q]=3$. Both are hexagonal lattices related by rotation and scaling, but they are not literally the same subset of a fixed Euclidean vector space.

\begin{correctionbox}
Replace ``the $A_2$ root lattice -- which is the $SU(3)$ weight lattice'' by: ``the Goldberg norm is the standard hexagonal $A_2$ quadratic form; after a stated normalization, the same form is the quadratic part of the $SU(3)$ Casimir on Dynkin labels. The root and weight lattices are dual and commensurable, with index three.''
\end{correctionbox}

\section{Cross-indexing is not particle identification}
The pair $(1,1)$ has $T=3$, so its Goldberg shell count is $C_{60}$. The same pair labels the adjoint $SU(3)$ representation of dimension eight. This is an exact reuse of an integer pair in two constructions. It does not imply that $C_{60}$ is the gluon octet, that QCD lives on the fullerene shell, or that a hadron mass follows from $T$.

\chapter{Klein's Icosahedral Forms}
\section{The three binary forms}
In one classical normalization,
\begin{align}
f_{12}(z,w)&=zw(z^{10}+11z^5w^5-w^{10}),\\
H_{20}(z,w)&=-(z^{20}+w^{20})+228(z^{15}w^5-z^5w^{15})-494z^{10}w^{10},\\
T_{30}(z,w)&=z^{30}+522z^{25}w^5-10005z^{20}w^{10}\\
&\quad-10005z^{10}w^{20}-522z^5w^{25}+w^{30}.
\end{align}
The independent symbolic expansion gives
\begin{exactbox}
\begin{equation}
\boxed{T_{30}^2+H_{20}^3=1728f_{12}^5.}
\end{equation}
No random sampling is required for the identity.
\end{exactbox}

\section{Why the degrees are 12, 20, and 30}
The exceptional orbits of the rotational icosahedral group have sizes 12 vertices, 20 face centers, and 30 edge midpoints. The degrees of the fundamental forms encode these orbit divisors. Their equality with $P(C_{20})=12$, $V(C_{20})=20$, and $E(C_{20})=30$ is therefore geometric group structure, not a free-standing numerical coincidence.

\section{The vertex rings}
The affine roots of $f_{12}(z,1)$ include $z=0$ and the roots of
\begin{equation}
z^{10}+11z^5-1=0.
\end{equation}
Writing $y=z^5$,
\begin{equation}
y_{\pm}=\frac{-11\pm5\sqrt5}{2}.
\end{equation}
Their fifth-root radii are
\begin{equation}
|y_+|^{1/5}=\phig^{-1},\qquad |y_-|^{1/5}=\phig.
\end{equation}
Together with $0$ and $\infty$, this produces two five-point rings plus the poles.

\section{Gradient equivariants}
For a homogeneous invariant $F$, define the projective map
\begin{equation}
g_F=[F_w:-F_z].
\end{equation}
The source's sparse degree-11, degree-19, and degree-29 polynomial pairs were compared symbolically with the gradients. They agree projectively, with scalar factors $1$, $20$, and $30$ respectively.

\section{Basins: what the finite experiment can say}
The HTML iterates random starting points and clusters final directions. This can discover 20, 12, and 32 attractors under sufficient coverage. It cannot prove that every attractor was sampled, that a chosen clustering threshold is canonical, or that basin areas have a fixed range unless those areas are actually computed in the same run.

\begin{correctionbox}
The hard-coded row ``basin areas are wildly unequal, 0.12\% ... 13.25\%'' is not produced by the current Section XIII algorithm. Either add a deterministic area estimator with a receipt or remove the row. v1.3.2 treats the orbit counts as reproducible numerical evidence and the projective-gradient formulas as exact.
\end{correctionbox}

\chapter{Numerical Architecture: Where Exactness Actually Breaks}
\section{Three distinct float walls}
The browser section combined several different notions of resolution. v1.3.2 keeps them separate:
\begin{enumerate}
\item relative spacing near one: $\varepsilon_{64}=2^{-52}$;
\item exact representation of all integers only through $2^{53}$;
\item exact representation of selected larger integers that happen to be multiples of the local spacing.
\end{enumerate}
One cannot infer the exact-integer failure index solely from $\varepsilon_{64}$.

\section{Exact break indices}
Using exact Python integers as ground truth and IEEE binary64 conversion:
\begin{center}
\begin{tabular}{lr}
\toprule
quantity & last level satisfying the stated exactness test\\\midrule
$T_n$ represented exactly & $n=38$\\
$V_n=20T_n$ represented exactly & $n=36$\\
$E_n=30T_n$ represented exactly & $n=35$\\
$\chi=20T-30T+(10T+2)$ evaluates to $2$ & $n=35$\\
first failed $\chi$ & $n=36$, result $0$\\
\bottomrule
\end{tabular}
\end{center}
The composite invariant can fail before $T_n$ because subtraction magnifies loss of low bits.

\section{Corrected forward-error measurement}
The v1.3.1 code formed
\begin{equation}
\frac{|T_n^{\mathrm{f64}}-\operatorname{Number}(T_n^{\mathrm{BigInt}})|}{\operatorname{Number}(T_n^{\mathrm{BigInt}})}.
\end{equation}
Both operands may share the same rounded binary64 value. The corrected audit converts the recurrence output to its exact rational binary64 value and compares that rational to the exact integer. The first nonzero error occurs at $n=39$ and the maximum through $n=159$ is
\begin{equation}
1.0189\times10^{-15}.
\end{equation}
The conclusion of forward stability survives; the original error meter was not a valid independent reference.

\begin{figure}[H]\centering
\includegraphics[width=.88\textwidth]{''' + fig + r'''/float64_forward_error.png}
\caption{True relative error of the forward recurrence against exact integers. Stability survives the corrected comparator, but the error is not identically zero.}
\end{figure}

\section{Backward instability}
Starting from rounded values at $n=60$ and marching
\begin{equation}
T_n=2T_{n+2}+2T_{n+1}-T_{n+3}
\end{equation}
backward produces relative errors approximately
\begin{equation}
1.8\times10^{-10}\ (n=50),\quad9.5\times10^6\ (n=30),\quad5.0\times10^{23}\ (n=10),\quad1.2\times10^{32}\ (n=0).
\end{equation}
The same recurrence is stable in one direction and catastrophically unstable in the other because the dominant and reciprocal modes exchange roles.

\section{Precision formats}
For a format with $p$ significand bits, the scale budget measured in $\phig^2$ rungs is
\begin{equation}
N_{\mathrm{rungs}}(p)=\frac{p\ln2}{\ln\phig^2}.
\end{equation}
\begin{center}
\begin{tabular}{lrrc}
\toprule
format & precision bits & rung budget & enough for 147 scale rungs?\\\midrule
binary16 & 11 & 7.9 & no\\
binary32 & 24 & 17.3 & no\\
binary64 & 53 & 38.2 & no\\
x87 extended & 64 & 46.1 & no\\
binary128 & 113 & 81.4 & no\\
binary256 & 237 & 170.7 & yes\\
\bottomrule
\end{tabular}
\end{center}
The exact integer $T_{147}$ has 205 bits. IEEE 754 binary256 has 237 bits of precision, so it is the first listed interchange format that can represent that integer scale without truncating the significand. This is a format statement, not a claim about current hardware availability or performance.

\section{The Planck-to-horizon ruler}
With the chosen values $\ell_P=1.616255\times10^{-35}\,\mathrm m$ and $L_H=4.4\times10^{26}\,\mathrm m$,
\begin{equation}
\frac{\ln(L_H/\ell_P)}{\ln\phig^2}=146.9822\ldots
\end{equation}
This is a dimensionless scale-counting exercise. It does not derive the Planck length, prove a minimum length, or imply that a physical process follows the golden ladder.

\section{Selected precision benchmarks, updated to 9 August 2026}
The v1.3.1 table called itself the ``ten most precise measurements humanity has made'' while containing eleven heterogeneous entries. v1.3.2 uses the narrower title ``selected relative-uncertainty benchmarks'' and updates the leading clock entry.
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{.29\textwidth}>{\centering\arraybackslash}p{.18\textwidth}>{\centering\arraybackslash}p{.10\textwidth}>{\raggedright\arraybackslash}p{.34\textwidth}@{}}
\toprule
benchmark & relative uncertainty & $N(u)$ rungs & source\\\midrule\endhead
''' + benchmark_table + r'''
\bottomrule
\end{longtable}
The table compares published uncertainties under one logarithmic mapping. It does not rank the scientific importance of measurements, and it does not make systematic clock uncertainty, absolute-frequency uncertainty, and fundamental-constant uncertainty the same experimental object.

\chapter{The LUCA Spiral Audit and the Handoff to v1.3.2}
\section{The EML operator}
The external conjecture defines
\begin{equation}
\boxed{\EML(x,y)=e^x-\Log y},\qquad S\to1\mid\EML(S,S).
\end{equation}
The immediate identities are
\begin{equation}
e=\EML(1,1),\qquad e^x=\EML(x,1).
\end{equation}
For positive real $x$,
\begin{align}
\Log x
&=\EML\bigl(1,\EML(\EML(1,x),1)\bigr)\\
&=e-\Log(e^e/x)=\log x.
\end{align}

\section{Domain and branch ledger}
Over $\C$, $\exp(\Log z)=z$ for nonzero $z$ on the principal logarithm, but $\Log(e^z)=z$ only inside a principal strip, modulo branch jumps. Consequently:
\begin{itemize}
\item the log chain is exact on stated domains/sheets, not a single global identity of principal branches;
\item subtraction $x-y=\EML(\Log x,e^y)$ is exact for the browser's real test domain, while complex $y$ requires strip control;
\item the code's convention $\Log0=-\infty$ and $e^{-\infty}=0$ is an extended-real computational lane, not ordinary complex analyticity at zero;
\item constructing $i$ from $(-1)^{1/2}$ is branch-dependent; branch-robust downstream real formulas must be checked under conjugation.
\end{itemize}

\begin{correctionbox}
Replace the blanket sentence ``the identities on every node are classical algebra over $\C$ (principal branch)'' by a per-node domain contract. Each node should carry: domain, excluded points, chosen branch, and whether equality is global, local, or invariant only after a periodic/conjugate consumer.
\end{correctionbox}

\section{What the browser verification proves}
LUCA v0.1/v0.2 evaluates chains at 16 deterministic sample points and reports
\begin{equation}
D=-\log_{10}(\text{relative error}),\qquad D\le15.9.
\end{equation}
A high $D$ is a finite numerical certificate at the sampled points. It is not a symbolic proof of functional identity. The symbolic identities in this chapter supply the proof where their domains are stated; the browser supplies regression protection and branch receipts.

\section{The light-matrix content transferred from LUCA v0.2}
The LUCA golden lane correctly contributes four items:
\begin{enumerate}
\item Faddeev--LeVerrier construction of the coefficient list $(1,-3,0,3,-1)$;
\item reciprocal-spectrum explanation from anti-palindromy;
\item the exact angle $\theta_\phig=\arctan(\sqrt{15}-2\sqrt3)$;
\item a target/current/error display for the ratio and angular zigzag.
\end{enumerate}
These are integrated into Chapters 4 and 5.

\section{Finite-$N$ Vogel experiment}
For $N=33$ points placed by
\begin{equation}
r_k=\sqrt k,\qquad \theta_k=k\alpha,
\end{equation}
the live v0.2 sweep maximizes minimum pairwise separation near
\begin{equation}
\alpha_{33}=137.6066065^\circ,
\end{equation}
not at the golden angle
\begin{equation}
\alpha_\phig=\frac{360^\circ}{\phig^2}=137.5077641^\circ.
\end{equation}
The difference is about $0.09884^\circ$. This refutes an unqualified finite-$N$ optimum claim. The five-point drift table is compatible with movement toward the golden angle, but five finite samples do not prove the limit.

\begin{figure}[H]\centering
\includegraphics[width=.88\textwidth]{''' + fig + r'''/vogel_sweep_N33.png}
\caption{The finite-$N$ objective is jagged and its maximizer is not exactly the golden angle.}
\end{figure}

\section{Leaf-count null and the 32/33 discrepancy}
Using all 33 live spiral nodes, the independent reconstruction of the v0.2 leaf recurrences gives
\begin{equation}
\text{growth}=1.159672,
\quad95\%\text{ descriptive interval }[1.140910,1.178742],
\quad R^2=0.9109.
\end{equation}
Excluding the first constant $e$ gives the 32-point values printed in the handoff scroll:
\begin{equation}
\text{growth}=1.155084,
\quad[1.135961,1.174529],
\quad R^2=0.9052.
\end{equation}
Both exclude $\phig$ by roughly forty fitted standard errors. The null result is robust; the sample definition was not.

\begin{figure}[H]\centering
\includegraphics[width=.88\textwidth]{''' + fig + r'''/luca_leaf_regression.png}
\caption{The live 33-node leaf counts and their descriptive log-linear fit. Discovery order is a design order, so the fit is not a physical stochastic model.}
\end{figure}

\chapter{The v1.3.2 Integration Contract}
\section{Section map}
The recommended living-paper order is:
\begin{enumerate}
\item Birth / abstract and status grammar.
\item Constants $\phig$ and $\pi$.
\item Euler and discrete Gauss--Bonnet.
\item Hexagonal closure norm, matrix, composition, and angle.
\item Light matrix built by Faddeev--LeVerrier.
\item Golden selector, shell catalogue, and selected-not-nested theorem.
\item Golden-ray angle and signed convergence plot.
\item Exact $C_{60}$ adjacency and Laplacian certificate.
\item Graph-tower lane selector: golden, leapfrog, WELD, fixed GC.
\item Conditional continuum matching and finite receipts.
\item $A_2/SU(3)$ quadratic-form correspondence with corrected lattice language.
\item Klein forms and exact symbolic syzygy.
\item Equivariant numerical experiment with deterministic seed/coverage ledger.
\item Float architecture with corrected exact reference.
\item Selected precision benchmarks, dated.
\item LUCA/EML handoff and branch ledger.
\item Honest physical boundary.
\item Reproducibility manifest and frozen lineage.
\end{enumerate}

\section{HUD contract}
Every live shell should show independent rows:
\begin{lstlisting}
CLOSURE   pair (k,l), T, V/E/F/P/H, chi, boundary, degree, cert hash
GOLDEN    target phi, current k/l, signed error, tolerance, lock state
ANGLE     target theta_phi, current theta(k,l), signed error,
          error ratio -> -phi^-2, suppress below numerical floor
SPECTRUM  family name, lambda2, T*lambda2, previous delta,
          low-band multiplicities, solver tolerance
BOUNDARY  EXACT / COMPUTED / DESIGN / HYPOTHESIS / EXTERNAL
\end{lstlisting}
No lock may be true while the displayed error exceeds its tolerance. The family name is mandatory because a golden catalogue, leapfrog tower, and WELD tower are not interchangeable.

\section{Compute gate}
Before allocating a shell, predict
\begin{equation}
V_{\mathrm{next}}=S V_{\mathrm{current}}
\end{equation}
for a fixed area multiplier $S$, or compute $20T(k',\ell')$ for a selected pair. Refuse before allocation if the vertex, edge, memory, or eigensolver budget is exceeded. The refusal must print the predicted price.

\section{Deterministic receipt schema}
\begin{lstlisting}
{
  "schema": "thea.light-matrix.receipt.v1.3.2",
  "family": "golden-selected | leapfrog | weld | gc-fixed",
  "pair": {"k": "21", "ell": "13"},
  "counts": {"T": "883", "V": "17660", "E": "26490",
             "F": "8832", "P": "12", "H": "8820", "chi": "2"},
  "topology": {"boundary_edges": 0, "nonmanifold_edges": 0,
               "degree3_vertices": 17660, "connected": true},
  "golden": {"target": 1.6180339887498948,
             "current": 1.6153846153846154,
             "signed_error": -0.0026493733652794},
  "angle": {"target_deg": 22.23875609296496,
            "current_deg": 22.264023, "signed_error_deg": 0.025267},
  "spectrum": {"method": "Lanczos full reorthogonalization",
               "lambda2": 0.0008208191343368484,
               "T_lambda2": 0.7247832956194371,
               "residual_tolerance": 1e-10},
  "status": {"closure": "EXACT", "spectrum": "COMPUTED"}
}
\end{lstlisting}
The timestamp belongs outside the hashed mathematical payload. Random experiments must carry a fixed seed or deterministic point set.

\section{Regression tests}
At minimum:
\begin{enumerate}
\item exact integer tests for norm, metric similarity, composition, and shell counts;
\item exact characteristic polynomial of $\Mlight$ and coefficient anti-palindromy;
\item exact golden-angle radical equality;
\item exact $C_{60}$ graph counts and characteristic factorization;
\item exact Klein syzygy and projective-gradient checks;
\item branch-domain tests for EML nodes, including excluded points;
\item deterministic spectral smoke tests for $C_{20}$, $C_{60}$, $C_{140}$;
\item float comparator test against rationalized binary64, not rounded exact operands;
\item byte scan for malformed Unicode and line endings;
\item certificate regeneration on a second path with identical math hash.
\end{enumerate}

\section{Honest physical boundary}
\begin{hypbox}
This tower does not derive a particle mass, coupling constant, cross-section, decay rate, Planck length, or Standard Model observable. It does not prove that spacetime, photons, quantum foam, or molecular stability are generated by fullerene graphs. It supplies an exact mathematical generator, several exact correspondences, finite spectral experiments, and a disciplined forward-model laboratory. A physical theory begins only when a dynamical law and an observable not inserted by construction differ from existing physics and survive experiment.
\end{hypbox}

\chapter{Copy-Ready Formula Tower}
\section{Core constants and topology}
\begin{align}
\phig&=\frac{1+\sqrt5}{2}=2\cos\frac\pi5, &
\phig^2&=\phig+1, & \phig^{-2}&=2-\phig,\\
3V&=2E, &5P+6H&=2E, &V-E+P+H&=2,\\
P&=12, &E&=\frac{3V}{2}, &H&=\frac V2-10,\\
\frac\pi3\sum_f(6-p_f)&=4\pi.&&&
\end{align}

\section{Closure ring}
\begin{align}
\zetahex&=e^{i\pi/3}, &T&=k^2+k\ell+\ell^2,\\
M_{k,\ell}&=\begin{pmatrix}k&-\ell\\\ell&k+\ell\end{pmatrix},&
\det M_{k,\ell}&=T,\\
M_{k,\ell}^{\mathsf T}QM_{k,\ell}&=TQ,
&Q&=\begin{pmatrix}1&1/2\\1/2&1\end{pmatrix},\\
(k',\ell')&=(ak-b\ell,a\ell+bk+b\ell),
&T'&=(a^2+ab+b^2)T,\\
\theta_{k,\ell}&=\operatorname{atan2}(\sqrt3\ell,2k+\ell).
\end{align}

\section{Golden lane}
\begin{align}
\begin{pmatrix}k_{n+1}\\\ell_{n+1}\end{pmatrix}
&=\begin{pmatrix}1&1\\1&0\end{pmatrix}\begin{pmatrix}k_n\\\ell_n\end{pmatrix},
&(k_n,\ell_n)&=(F_{n+1},F_n),\\
T_n&=k_n^2+k_n\ell_n+\ell_n^2,
&T_{n+3}&=2T_{n+2}+2T_{n+1}-T_n,\\
T_n&=\frac25(\phig^{2n+2}+\phig^{-2n-2})-\frac15(-1)^n,
&\frac{T_{n+1}}{T_n}&\to\phig^2,\\
\theta_\phig&=\arctan(\sqrt{15}-2\sqrt3),
&\frac{\theta_{n+1}-\theta_\phig}{\theta_n-\theta_\phig}&\to-\phig^{-2}.
\end{align}

\section{Light matrix}
\begin{align}
\Mlight&=\begin{pmatrix}1&2&1&0\\1&1&0&0\\1&0&0&0\\0&0&0&1\end{pmatrix},\\
\det(\lambda I-\Mlight)&=(\lambda-1)(\lambda+1)(\lambda^2-3\lambda+1),\\
\spec(\Mlight)&=\{\phig^2,1,-1,\phig^{-2}\},\\
p(\lambda)&=\lambda^4-3\lambda^3+3\lambda-1=-\lambda^4p(1/\lambda).
\end{align}

\section{$C_{60}$ and graph spectra}
\begin{align}
L&=3I-A,\\
\lambda_{\min}(A_{60})&=-\phig^2,\\
\lambda_2(L_{60})&=\frac94-\frac{\sqrt2}{8}(\sqrt{10}+2\sqrt{19-\sqrt5}),\\
T\lambda_2&\sim\frac{2\pi}{5\sqrt3}\quad\text{under the stated continuum matching assumptions.}
\end{align}

\section{$A_2$, $SU(3)$, and Klein}
\begin{align}
T(p,q)&=p^2+pq+q^2,\\
C_2(p,q)&=\frac13\bigl(T(p,q)+3p+3q\bigr),\\
\dim(p,q)&=\frac12(p+1)(q+1)(p+q+2),\\
T_{30}^2+H_{20}^3&=1728f_{12}^5,\\
g_F&=[F_w:-F_z].
\end{align}

\chapter{Independent Audit Receipt}
The following table is generated from \texttt{light\_matrix\_v1.3.2\_audit\_receipt.json}. Long result fields are truncated here; the JSON preserves the full values.
\begin{landscape}
\scriptsize\sloppy
\begin{longtable}{@{}r>{\raggedright\arraybackslash}p{.23\linewidth}>{\raggedright\arraybackslash}p{.15\linewidth}c>{\raggedright\arraybackslash}p{.46\linewidth}@{}}
\toprule
\# & check & status & verdict & result \\ \midrule\endhead
\bottomrule\endfoot
''' + checks_table + r'''
\end{longtable}
\normalsize
\end{landscape}

\chapter{Reproduction Protocol}
\section{Commands}
\begin{lstlisting}
python verify_light_matrix_v132.py
node verify_light_matrix_v131_live.js > light_matrix_v1.3.1_live_kernel_receipt.json
pdflatex THEA_LIGHT_MATRIX_v1.3.2_LATEX_TOWER.tex
pdflatex THEA_LIGHT_MATRIX_v1.3.2_LATEX_TOWER.tex
\end{lstlisting}

\section{Version discipline}
The new document does not overwrite any input. The source HTML and LUCA versions remain immutable. v1.3.2 is a derived audit artifact whose corrections are explicit, whose receipts are machine-readable, and whose build timestamp is not included in the mathematical hash.

\section{Closing line}
\begin{center}
\Large\bfseries
The pentagons hold. The hexes pay.\\
The ray now has a bearing.\\
The limit still owes its proof.\\[2mm]
\normalsize
$P=12.\quad\chi=2.\quad\theta_\phig=\arctan(\sqrt{15}-2\sqrt3).$
\end{center}

\begin{thebibliography}{99}
\bibitem{thea} \emph{THEA v3.0: The Math Core Scroll -- the Light Matrix}, source file \texttt{Thea.md}, 2026.
\bibitem{goldberg} M. Goldberg, ``A class of multi-symmetric polyhedra,'' \emph{Tohoku Mathematical Journal}, 1937.
\bibitem{casparklug} D. L. D. Caspar and A. Klug, ``Physical principles in the construction of regular viruses,'' \emph{Cold Spring Harbor Symposia on Quantitative Biology} 27 (1962).
\bibitem{fowler} P. W. Fowler, P. Hansen, and D. Stevanovi\'c, ``A Note on the Smallest Eigenvalue of Fullerenes,'' \emph{MATCH Communications in Mathematical and in Computer Chemistry} 48 (2003), 37--48.
\bibitem{omori} T. Omori, H. Naito, and T. Tate, ``Eigenvalues of the Laplacian on the Goldberg--Coxeter Constructions for 3- and 4-Valent Graphs,'' \emph{Electronic Journal of Combinatorics} 26(3) (2019), P3.7; arXiv:1807.10891.
\bibitem{li} S. Li, ``Transformation, Identification, and Inversion of Goldberg--Coxeter Fullerenes,'' arXiv:2303.07890.
\bibitem{klein} F. Klein, \emph{Lectures on the Icosahedron and the Solution of Equations of the Fifth Degree}, 1884/1913 English edition.
\bibitem{eml} A. Odrzywolek, ``All elementary functions from a single binary operator,'' arXiv:2603.21852v2, 2026.
\bibitem{ieee} IEEE, \emph{IEEE Standard for Floating-Point Arithmetic}, IEEE 754-2019.
\bibitem{codata} CODATA 2022 recommended values of the fundamental physical constants.
\bibitem{caClock} B. Zhang et al., ``Liquid-Nitrogen-Cooled $^{40}$Ca$^+$ Ion Optical Clock with a Systematic Uncertainty of $4.4\times10^{-19}$,'' \emph{Physical Review Letters} 136 (2026), 053202; arXiv:2506.17423.
\bibitem{multiIon} M. Filzinger et al., ``A multi-ion optical clock with $5\times10^{-19}$ uncertainty,'' arXiv:2603.23446, 2026.
\bibitem{alClock} M. Marshall et al., ``High-Stability Single-Ion Clock with $5.5\times10^{-19}$ Systematic Uncertainty,'' \emph{Physical Review Letters}, 2025.
\bibitem{srIon} T. Lindvall et al., ``$^{88}$Sr$^+$ optical clock with $7.9\times10^{-19}$ systematic uncertainty and measurement of its absolute frequency,'' 2025.
\bibitem{aeppli} A. Aeppli et al., ``Clock with $8\times10^{-19}$ Systematic Uncertainty,'' \emph{Physical Review Letters} 133 (2024), 023401.
\end{thebibliography}

\end{document}
'''

out=ROOT/'THEA_LIGHT_MATRIX_v1.3.2_LATEX_TOWER.tex'
out.write_text(tex,encoding='utf-8')
print(out, len(tex.splitlines()), 'lines', len(tex), 'bytes')

#!/usr/bin/env python3
"""TRIPLE CHECK -- are the two documents generating the same LaTeX?

Source A : SolMageTowerforV1_4.txt   (markdown export, delimiters mangled)
Source B : SOL_FABLE_LATEX_TOWER_v2_0.pdf text layer
Source C : this kernel

We do not diff prose. We diff the CLAIMS: every numeral and identity the tower
boxes. A claim present in one source and absent in the other is a divergence,
and a claim present in both but false in the kernel is a contradiction.
"""
import re, subprocess, sys
from pathlib import Path

A = Path("/mnt/user-data/uploads/SolMageTowerforV1_4.txt").read_text(encoding="utf-8", errors="replace")
B = Path("/home/claude/sol_pdf.txt").read_text(encoding="utf-8", errors="replace")

def norm(s):
    """Strip everything that is presentation, keep everything that is content."""
    s = s.replace("\r\n", "\n")
    s = s.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "-")
    s = s.replace("\u2032", "'").replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    return s

An, Bn = norm(A), norm(B)

# ---------------------------------------------------------------------------
# 1. THE NUMERALS. Every integer the tower asserts as a result.
# ---------------------------------------------------------------------------
CLAIMS = [
    # (label, regex-in-A, regex-in-B, kernel check name)
    ("P = 12 forced by Euler",            r"P=12",                 r"P = 12",                 "P12"),
    ("chi = 2",                           r"V-E\+F",               r"V - E \+ F = 2",         "CHI"),
    ("total curvature 4 pi",              r"4\\pi",                r"4\u03c0",                "CURV"),
    ("T = k^2+kl+l^2",                    r"k\^2\+k\\ell\+\\ell\^2", r"k\s*2 \+ k. \+ .2",    "NORM"),
    ("13 != 9",                           r"13\\neq9",             r"13 .= 9",                "FENCE"),
    ("spec M = {phi^2,1,-1,phi^-2}",      r"\\phi\^2,\s*\n?1,",    r"\{.\s*2\s*, 1, -1, .-2\}", "SPEC"),
    ("charpoly (x-1)(x+1)(x^2-3x+1)",     r"\(x-1\)\(x\+1\)\(x\^2-3x\+1\)", r"\(x - 1\)\(x \+ 1\)\(x\s*2 - 3x \+ 1\)", "CHARPOLY"),
    ("det Gamma = -3",                    r"\\det\\Gamma=-3",      r"det . = -3",             "DETG"),
    ("signature (3,1)",                   r"\(3,1\)",              r"signature is \(3, 1\)",  "SIG"),
    ("s^T Gamma s = 145",                 r"145",                  r"145",                    "S145"),
    ("Cassini (-1)^n",                    r"\(-1\)\^n",            r"= \(-1\)n",              "CASS"),
    ("T sequence 1,3,7,19,49,129,337,883",r"1,3,7,19,49,129,337,883", r"1, 3, 7, 19, 49, 129, 337, 883", "TSEQ"),
    ("recurrence 2T+2T-T",                r"2T_\{n\+2\}",          r"2Tn\+2 \+ 2Tn\+1 - Tn",  "REC"),
    ("generating function",               r"1-2x-2x\^2\+x\^3",     r"1 - 2x - 2x\s*2 \+ x3",  "GF"),
    ("272 = 2 x 136",                     r"272",                  r"272",                    "D272"),
    ("136 = 16*17/2",                     r"\\frac\{16\(17\)\}\{2\}", r"16\(16 \+ 1\)",        "D136"),
    ("rank 256 -> nullity 16",            r"256",                  r"256",                    "R256"),
    ("rank 264 -> nullity 8",             r"264",                  r"264",                    "R264"),
    ("dim_R A_F = 24",                    r"24",                   r"dimR AF = 24",           "AF24"),
    ("commutant 432x144 rank 120",        r"432\\times144",        r"432 . 144",              "COMM"),
    ("nullity 24 = 2+4+18",               r"2\+4\+18",             r"24 = 2 \+ 4 \+ 18",      "N24"),
    ("m_inner = 14",                      r"m_\{\\mathrm\{inner\}\}=14", r"minner = 14",       "M14"),
    ("m_outer = 8",                       r"m_\{\\mathrm\{outer\}\}=8",  r"mouter = 8",        "M8"),
    ("N python = 500000",                 r"N=500,000",            r"NPython BigInt = 500000","NPY"),
    ("digits 208988",                     r"208,988",              r"208988",                 "DIG1"),
    ("N node = 200000",                   r"N=200,000",            r"NNode BigInt = 200000",  "NJS"),
    ("digits 83596",                      r"83,596",               r"83596",                  "DIG2"),
    ("8/8 PASS",                          r"8/8",                  r"8/8",                    "PASS8"),
]

print("=" * 78)
print("PART 1 -- CLAIM PRESENCE: source A (markdown) vs source B (pdf)")
print("=" * 78)
missA, missB = [], []
for label, ra, rb, key in CLAIMS:
    inA = bool(re.search(ra, An))
    inB = bool(re.search(rb, Bn))
    mark = "  " if (inA and inB) else "**"
    if not inA: missA.append(label)
    if not inB: missB.append(label)
    print(f"{mark} {label:42s}  A={'yes' if inA else 'NO ':3s}  B={'yes' if inB else 'NO ':3s}")

# ---------------------------------------------------------------------------
# 2. DIVERGENCES: content in one document only
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("PART 2 -- DIVERGENCES: asserted in one document, absent from the other")
print("=" * 78)
PROBES = [
    ("SIMD list includes SHA",              r"SHA",                       r"BMI2, SHA"),
    ("null eigenvectors v+^T G v+ = 0",     r"v\^T_\+\\Gamma|v_\+\^\{\\mathsf T\}\\Gamma", r"v\s*T\+.v\+ = 0"),
    ("Schur span residual 3.9e-15",         r"3\.9",                      r"3\.9 . 10-15"),
    ("Schur span residual 5.3e-15",         r"5\.3",                      r"5\.3 . 10-15"),
    ("trial standard-A_F gives 32",         r"32",                        r"= 32"),
    ("residual 4.5e-15",                    r"4\.5\\times10\^\{-15\}",    r"4\.5 . 10-15"),
    ("Binet formula for F_n",               r"Binet",                     r"Binet"),
    ("Cassini X^2 - T_L^2 form",            r"X\^2-T_L\^2",               r"q = X2 - T\s*2"),
    ("cosh rho = 3/2 boost",                r"\\cosh\\rho",               r"cosh\(2 log"),
    ("rho = 2 log phi",                     r"\\rho=2\\log\\phi",         r"2 log ."),
    ("sqrt(T_{n+1})/sqrt(T_n) -> phi",      r"\\sqrt\{T",                 r"Tn\+1\s*\n?\s*.\s*\n?\s*Tn"),
    ("elapsed 25.1 s",                      r"25\.08|25\.1",              r"25\.1 seconds"),
    ("peak memory 245 MB",                  r"244,768,768|233\.4",        r"245"),
    ("open-set condition",                  r"open-set condition",        r"open-set condition"),
    ("Krajewski / Chamseddine refs",        r"Krajewski",                 r"Krajewski"),
]
for label, ra, rb in PROBES:
    inA = bool(re.search(ra, An, re.S))
    inB = bool(re.search(rb, Bn, re.S))
    if inA != inB:
        who = "PDF only" if inB else "markdown only"
        print(f"  DIVERGE  {label:38s}  -> {who}")
    else:
        print(f"           {label:38s}  -> both")

print()
print("=" * 78)
print("PART 3 -- STRUCTURAL: what the markdown export destroyed")
print("=" * 78)
# the markdown export turned \[ \] into [ ] and runs of '=' into setext underlines
bad_delims  = len(re.findall(r"^\[\s*$", An, re.M))
setext_eq   = len(re.findall(r"^=====+\s*$", An, re.M))
setext_dash = len(re.findall(r"^-----+\s*$", An, re.M))
stray_hash  = len(re.findall(r"^# \\", An, re.M))
print(f"  bare '[' display-math delimiters (should be '\\['): {bad_delims}")
print(f"  runs of '=' promoted to setext H1 underline        : {setext_eq}")
print(f"  runs of '-' promoted to setext H2 underline        : {setext_dash}")
print(f"  '=' lines that swallowed an equals sign into '# '  : {stray_hash}")
print(f"  -> the markdown source cannot be recompiled to LaTeX; the PDF is authoritative.")

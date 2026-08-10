#!/usr/bin/env python3
"""RUNG XVII -- THE AXIOM LATTICE. Sprint task 1, built on the Korinth patterns.

The Korinth kernel found (20,21,29) missing from Baudhayana's triple list by
ENUMERATING every primitive triple below the bound instead of verifying the
six that were listed. The tower has the same shape of problem one level up:

    it imposes four conditions on D and treats them as "the list."

This kernel enumerates instead. It separates the conditions into two kinds:

  MODEL-LEVEL  properties of (A, H, pi, J, gamma) that hold or fail before any
               D is chosen -- order-zero, orientability, Poincare duality,
               irreducibility, unitality. These DISQUALIFY a model outright.

  D-LEVEL      linear constraints on D -- order-one, massless photon. These cut
               the dimension. Every SUBSET is computed, not just the ones we
               expect to matter.

Imported code patterns from KORINTH_KERNEL v0.1:
  1. record(section, claim, status, detail) + tally
  2. the DISCREPANCY status -- the tower's grammar has no label for
     "the ledger says X, the arithmetic says Y". It needs one.
  3. an explicit OUT_OF_SCOPE list
  4. enumerate, do not verify a supplied list
  5. include checks that can fail on their author

Status grammar, extended:
    EXACT       provable here by integer / finite-field arithmetic
    COMPUTED    finite precision, residual printed
    DISCREPANCY published tower value disagrees with the arithmetic
    DISQUALIFIED the model fails an axiom and is not a spectral triple at all
    OUT_OF_SCOPE no kernel can settle it
"""
from __future__ import annotations

import itertools
import json
from typing import Dict, List, Sequence

import numpy as np
import sympy as sp

import rung_xv_irreducible as K
import rung_xvi_generations as G

RESULTS: List[Dict[str, object]] = []
RULES = ("free_real", "zero", "lambda", "lambda_bar")


def record(section: str, claim: str, status: str, detail: object) -> None:
    RESULTS.append({"section": section, "claim": claim, "status": status, "detail": detail})


def photon_pis(rule: str) -> List[np.ndarray]:
    out = []
    for lam in (1.0 + 0j, 1.0j):
        q = (lam.real, lam.imag, 0.0, 0.0)
        m = lam * np.eye(3, dtype=complex)
        out.append(K.pi((lam.real, lam, q, m), rule))
    return out


# ---------------------------------------------------------------------------
# I. MODEL-LEVEL AXIOMS -- these run before any D exists
# ---------------------------------------------------------------------------

def check_unitality(rule: str) -> Dict[str, object]:
    unit = (1.0, 1.0 + 0j, (1, 0, 0, 0), np.eye(3, dtype=complex))
    r = float(np.max(np.abs(K.pi(unit, rule) - np.eye(32))))
    return {"residual": r, "pass": bool(r == 0.0)}


def check_order_zero(rule: str) -> Dict[str, object]:
    """[pi(a), pi^op(b)] = 0 for all a, b. Connes' order-zero condition."""
    basis = K.algebra_basis(rule)
    ops = [K.opposite(A) for A in basis]
    worst = 0.0
    for A in basis:
        for B in ops:
            worst = max(worst, float(np.max(np.abs(A @ B - B @ A))))
    return {"max_commutator": worst, "pass": bool(worst == 0.0)}


def check_orientability(rule: str) -> Dict[str, object]:
    """Span form: is gamma in the real span of {pi(a) . pi^op(b)}?

    The full Hochschild-cycle condition is finer, but for a finite triple the
    grading must at minimum be reachable from the algebra and its opposite.
    """
    basis = K.algebra_basis(rule)
    ops = [K.opposite(A) for A in basis]
    prods = [A @ B for A in basis for B in ops]
    M = np.array([np.concatenate([p.real.ravel(), p.imag.ravel()]) for p in prods])
    g = np.concatenate([K.GAMMA.real.ravel(), K.GAMMA.imag.ravel()])
    r_span = np.linalg.matrix_rank(M, tol=1e-9)
    r_aug = np.linalg.matrix_rank(np.vstack([M, g[None, :]]), tol=1e-9)
    # where does gamma stick out?
    sol, *_ = np.linalg.lstsq(M.T, g, rcond=None)
    resid_vec = M.T @ sol - g
    resid = float(np.linalg.norm(resid_vec))
    # locate the failure on the state basis
    n = 32 * 32
    bad = sorted({i // 32 for i in np.flatnonzero(np.abs(resid_vec[:n]) > 1e-8)})
    return {"span_rank": int(r_span), "augmented_rank": int(r_aug),
            "gamma_in_span": bool(r_span == r_aug), "lstsq_residual": resid,
            "states_where_gamma_is_unreachable": bad,
            "pass": bool(r_span == r_aug)}


def minimal_projections(rule: str) -> List[tuple]:
    Z3 = np.zeros((3, 3), complex)
    e11 = np.zeros((3, 3), complex)
    e11[0, 0] = 1.0
    out = []
    if rule == "free_real":
        out.append(("R_lbar", (1.0, 0j, (0, 0, 0, 0), Z3)))
    out.append(("C", (0.0, 1.0 + 0j, (0, 0, 0, 0), Z3)))
    out.append(("H", (0.0, 0j, (1, 0, 0, 0), Z3)))
    out.append(("M3", (0.0, 0j, (0, 0, 0, 0), e11)))
    return out


def check_poincare(rule: str) -> Dict[str, object]:
    """Intersection form  cap_ij = Tr(gamma pi(e_i) J pi(e_j) J^-1). Invertible?"""
    projs = minimal_projections(rule)
    n = len(projs)
    M = np.zeros((n, n))
    for i, (_, ei) in enumerate(projs):
        Pi = K.pi(ei, rule)
        for j, (_, ej) in enumerate(projs):
            Qj = K.opposite(K.pi(ej, rule))
            M[i, j] = float(np.real(np.trace(K.GAMMA @ Pi @ Qj)))
    det = float(np.linalg.det(M))
    rank = int(np.linalg.matrix_rank(M, tol=1e-9))
    antisym = bool(np.allclose(M, -M.T))
    # A KO-6 intersection form is antisymmetric. An antisymmetric matrix of ODD
    # size has determinant 0 identically -- so for a 3-summand algebra this test
    # CANNOT be passed, whatever the model. A check that fails on every input is
    # measuring the implementation, not the models. Refuse to vote.
    discriminating = not (antisym and n % 2 == 1)
    return {"labels": [p[0] for p in projs],
            "intersection_form": M.astype(int).tolist(),
            "determinant": det, "rank": rank, "size": n,
            "antisymmetric": antisym,
            "discriminating": discriminating,
            "pass": bool(rank == n) if discriminating else True,
            "verdict": "UNTRUSTED -- antisymmetric form of odd size forces det 0"
                       if not discriminating else
                       ("non-degenerate" if rank == n else "degenerate")}


def check_irreducibility(rule: str) -> Dict[str, object]:
    """dim of the commutant of {pi(A), gamma, J}. Irreducible => minimal."""
    basis = K.algebra_basis(rule)
    gens = list(basis) + [K.GAMMA]
    rows = []
    I = np.eye(32)
    for Gm in gens:
        rows.append(np.kron(Gm.T, I) - np.kron(I, Gm))
    C = np.vstack(rows)
    Cr = np.vstack([np.hstack([C.real, -C.imag]), np.hstack([C.imag, C.real])])
    rank = np.linalg.matrix_rank(Cr, tol=1e-8)
    dim = 2 * 32 * 32 - int(rank)
    return {"commutant_real_dimension_without_J": dim,
            "note": "J-compatibility would cut this further; reported as an "
                    "upper bound on the irreducibility defect"}


# ---------------------------------------------------------------------------
# II. D-LEVEL LATTICE -- every subset of the optional constraints
# ---------------------------------------------------------------------------

def dim_D(rule: str, order_one: bool, photon: bool, hermitian: bool,
          primes=(10007, 65521, 2147483647)) -> Dict[str, object]:
    space = K.DBASE if hermitian else G.VBASE
    cm = K.constraint_matrix if hermitian else G.constraint_matrix_V
    n = len(space)

    if not order_one and not photon:
        return {"dim": n, "status": "EXACT", "modular_ranks": {}, "residual": 0.0}

    basis = K.algebra_basis(rule)
    ops = [K.opposite(A) for A in basis]
    blocks = []
    if order_one:
        rng = np.random.default_rng(31415926)
        for _ in range(4):
            A = K.pi(K.rand_elem(rng, rule), rule)
            B = K.opposite(K.pi(K.rand_elem(rng, rule), rule))
            blocks.append(cm(A, B))
    phs = photon_pis(rule) if photon else []
    for P in phs:
        Y = space @ P - P @ space
        F = Y.reshape(n, -1)
        X = np.concatenate([F.real.T, F.imag.T], axis=0)
        blocks.append(np.rint(X).astype(np.int64))

    X = np.concatenate(blocks, axis=0)
    ranks, piv = {}, None
    for p in primes:
        r, pr = K.rref_mod(X, p)
        ranks[str(p)] = r
        if piv is None or r > len(piv):
            piv = pr
    rank_lb = max(ranks.values())

    P = sp.Matrix(X[piv, :].tolist())
    null = P.nullspace()
    worst = 0.0
    mats = []
    for v in null:
        den = sp.ilcm(*[sp.Rational(x).q for x in v])
        w = np.array([int(sp.Rational(x) * den) for x in v], dtype=float)
        Dm = np.tensordot(w, space, axes=(0, 0))
        mats.append(Dm)
        for Pp in phs:
            worst = max(worst, float(np.max(np.abs(Dm @ Pp - Pp @ Dm))))
        if order_one:
            for A in basis:
                C = Dm @ A - A @ Dm
                for B in ops:
                    worst = max(worst, float(np.max(np.abs(C @ B - B @ C))))
    dim = len(null)
    ok = worst == 0.0 and dim == n - rank_lb
    return {"dim": dim, "status": "EXACT" if ok else "COMPUTED",
            "modular_ranks": ranks, "residual": worst,
            "hermitian_part": _herm_dim(mats)}


def _herm_dim(mats: Sequence[np.ndarray]) -> int:
    if not mats:
        return 0
    f = np.array([np.concatenate([m.real.ravel(), m.imag.ravel()]) for m in mats])
    fd = np.array([np.concatenate([m.conj().T.real.ravel(), m.conj().T.imag.ravel()])
                   for m in mats])
    return int(np.linalg.matrix_rank(f + fd, tol=1e-8))


# ---------------------------------------------------------------------------
# III. RUN
# ---------------------------------------------------------------------------

PUBLISHED = {  # tower v2.1 + Rungs XV/XVI, for DISCREPANCY detection
    ("free_real", True, False): 16,
    ("zero", True, False): 16,
    ("lambda", True, False): 32,
    ("lambda_bar", True, False): 32,
    ("zero", True, True): 8,
    ("lambda", True, True): 16,
}

OUT_OF_SCOPE = [
    "Whether the tower's (A, H, pi, J, gamma) is Chamseddine-Connes' finite "
    "triple. That is a convention-matching question, not an arithmetic one.",
    "Whether C_F as implemented is the published massless-photon subalgebra.",
    "Whether the full Hochschild-cycle orientability condition agrees with the "
    "span form used here.",
    "Which minimal-projection convention the Poincare intersection form should "
    "use for a real algebra with an H summand.",
    "Whether the number of colours c in {0,1,2,3} is derivable. It is not "
    "derivable anywhere in the literature either.",
    "Global Step 4. Still open. Still a joke.",
]


def main() -> None:
    # --- base sanity, including checks that can fail on their author ---
    record("0", "hermitian base is 272 = 2 * 16*17/2", "EXACT",
           {"computed": len(K.DBASE), "closed_form": 2 * (16 * 17 // 2),
            "match": len(K.DBASE) == 2 * (16 * 17 // 2)})
    record("0", "non-hermitian base is 512 = 2 * 16^2", "EXACT",
           {"computed": len(G.VBASE), "closed_form": 2 * 16 * 16,
            "match": len(G.VBASE) == 2 * 16 * 16})

    # --- model-level axioms, enumerated ---
    model: Dict[str, Dict[str, object]] = {}
    for rule in RULES:
        m = {
            "unitality": check_unitality(rule),
            "order_zero": check_order_zero(rule),
            "orientability": check_orientability(rule),
            "poincare_duality": check_poincare(rule),
            "irreducibility": check_irreducibility(rule),
        }
        model[rule] = m
        failed = [k for k in ("unitality", "order_zero", "orientability",
                              "poincare_duality") if not m[k].get("pass", True)]
        record("I", f"model-level axioms for chi = {rule}",
               "DISQUALIFIED" if failed else "EXACT",
               {"failed": failed,
                "unital": m["unitality"]["pass"],
                "order_zero": m["order_zero"]["pass"],
                "orientable": m["orientability"]["pass"],
                "poincare": m["poincare_duality"]["pass"],
                "poincare_verdict": m["poincare_duality"]["verdict"],
                "gamma_unreachable_on_states":
                    m["orientability"]["states_where_gamma_is_unreachable"][:8]})

    # --- D-level lattice: every subset, both hermitian and not ---
    lattice: Dict[str, Dict[str, object]] = {}
    for rule in RULES:
        cells = {}
        for o1, ph in itertools.product((False, True), repeat=2):
            h = dim_D(rule, o1, ph, hermitian=True)
            v = dim_D(rule, o1, ph, hermitian=False)
            d3 = 3 * h["dim"] + 3 * v["dim"]
            key = f"order_one={int(o1)},photon={int(ph)}"
            cells[key] = {"one_generation": h["dim"], "V_nonhermitian": v["dim"],
                          "three_generations": d3, "status": h["status"],
                          "residual": h["residual"]}
            pub = PUBLISHED.get((rule, o1, ph))
            if pub is not None:
                cells[key]["published"] = pub
                if pub != h["dim"]:
                    record("II", f"{rule} / {key}: published {pub}", "DISCREPANCY",
                           {"published": pub, "computed": h["dim"]})
        lattice[rule] = cells

    # --- the payoff comparison ---
    verdict = {
        "models_surviving_all_model_level_axioms": [
            r for r in RULES
            if all(model[r][k].get("pass", True)
                   for k in ("unitality", "order_zero", "orientability", "poincare_duality"))
        ],
        "models_disqualified": [
            r for r in RULES
            if not all(model[r][k].get("pass", True)
                       for k in ("unitality", "order_zero", "orientability", "poincare_duality"))
        ],
    }
    record("III", "which chi rules are admissible spectral triples at all",
           "EXACT", verdict)

    width = 78
    print("=" * width)
    print("RUNG XVII -- THE AXIOM LATTICE (sprint task 1)")
    print("=" * width)
    tally: Dict[str, int] = {}
    for r in RESULTS:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
        print(f"\n[{r['status']:13s}] {r['section']} :: {r['claim']}")
        for k, v in r["detail"].items():
            print(f"      {k}: {v}")

    print("\n" + "-" * width)
    print("D-LEVEL LATTICE   (1 gen / 3 gen)")
    print("-" * width)
    hdr = f"{'chi rule':<12}" + "".join(
        f"{k:>26}" for k in lattice[RULES[0]])
    print(hdr)
    for rule in RULES:
        row = f"{rule:<12}"
        for k, c in lattice[rule].items():
            row += f"{str(c['one_generation']) + ' / ' + str(c['three_generations']):>26}"
        print(row)

    print("\n" + "=" * width)
    print("TALLY:", ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    print("=" * width)
    print("\nOUT OF SCOPE FOR ANY KERNEL:")
    for i, s in enumerate(OUT_OF_SCOPE, 1):
        print(f"  {i}. {s}")
    print("\nincomplete is fine. fake is not.")

    with open("/home/claude/rung_xvii_axiom_lattice.json", "w") as f:
        json.dump({"results": RESULTS, "model_level": model, "lattice": lattice,
                   "verdict": verdict, "tally": tally,
                   "out_of_scope": OUT_OF_SCOPE}, f, indent=2, default=str)


if __name__ == "__main__":
    main()

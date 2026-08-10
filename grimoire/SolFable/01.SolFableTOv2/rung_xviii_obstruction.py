#!/usr/bin/env python3
"""RUNG XVIII -- THE OBSTRUCTION. What exactly is the crystal, and what fixes it?

Rung XVII found that gamma is NOT in span{pi(a) . pi^op(b)} for the standard
A_F, with residual exactly 2.0 supported on four states. This kernel asks the
next two questions, both of which are cheap and exact:

  1. WHAT is the obstruction? Compute omega = gamma - proj_span(gamma).
     Where does it live, what is its norm, what is its algebraic character?

  2. What MINIMALLY removes it? Do not verify a supplied answer -- enumerate
     candidate algebra extensions and report which ones work, which ones are
     legitimate direct summands, and whether the answer is unique.

This is the Korinth (20,21,29) pattern: the tower supplied R_lbar as "one
source-aligned completion." Rung XV called the R summand free because it adds
no order-one constraint. If the enumeration returns R_lbar as the UNIQUE
legitimate extension that restores orientability, then it was never a choice.

CAVEAT CARRIED FORWARD: orientability is used here in SPAN FORM
(gamma reachable from pi(A) and pi^op(A)), not the full Hochschild-cycle
condition. Everything below is CONDITIONAL on that reading.
"""
from __future__ import annotations

import json
from typing import Dict, List, Tuple

import numpy as np

import rung_xv_irreducible as K

RESULTS: List[Dict[str, object]] = []


def record(claim: str, status: str, detail: object) -> None:
    RESULTS.append({"claim": claim, "status": status, "detail": detail})


def flat(M: np.ndarray) -> np.ndarray:
    return np.concatenate([M.real.ravel(), M.imag.ravel()])


def label(i: int) -> str:
    a, s, w, c = K.STATES[i]
    kind = "lepton" if c == 3 else f"quark_c{c}"
    return f"{i:2d}:(a={a:+d},s={s:+d},w={w:+d},{kind})"


def span_of(rule: str, extra: List[np.ndarray] | None = None) -> np.ndarray:
    basis = list(K.algebra_basis(rule)) + list(extra or [])
    ops = [K.opposite(A) for A in basis]
    return np.array([flat(A @ B) for A in basis for B in ops])


def obstruction(rule: str, extra: List[np.ndarray] | None = None):
    M = span_of(rule, extra)
    g = flat(K.GAMMA)
    sol, *_ = np.linalg.lstsq(M.T, g, rcond=None)
    resid = M.T @ sol - g
    return resid, float(np.linalg.norm(resid))


def support_states(resid: np.ndarray) -> List[int]:
    n = 32 * 32
    re = resid[:n].reshape(32, 32)
    im = resid[n:].reshape(32, 32)
    mag = np.abs(re) + np.abs(im)
    return sorted({int(i) for i, j in np.argwhere(mag > 1e-8)})


def projector(states: List[int]) -> np.ndarray:
    P = np.zeros((32, 32), complex)
    for i in states:
        P[i, i] = 1.0
    return P


# The eight lepton states, and the J action on them.
LEPTONS = [i for i, (a, s, w, c) in enumerate(K.STATES) if c == 3]
ANTILEPTON = [i for i in LEPTONS if K.STATES[i][0] == -1]
PARTICLE_LEPTON = [i for i in LEPTONS if K.STATES[i][0] == +1]
RH_LEPTON = [i for i in LEPTONS if K.STATES[i][1] == -1]
J_PAIR = {i: K.INDEX[(-K.STATES[i][0], K.STATES[i][1], K.STATES[i][2], 3)]
          for i in LEPTONS}


def is_direct_summand(rule: str, P: np.ndarray) -> Dict[str, object]:
    """A legitimate extra summand must be a projector, commute with pi(A),
    and be ORTHOGONAL to pi(1) -- otherwise it is not a direct sum."""
    unit = (1.0, 1.0 + 0j, (1, 0, 0, 0), np.eye(3, dtype=complex))
    pi1 = K.pi(unit, rule)
    basis = K.algebra_basis(rule)
    idem = float(np.max(np.abs(P @ P - P)))
    comm = max(float(np.max(np.abs(P @ A - A @ P))) for A in basis)
    orth = float(np.max(np.abs(pi1 @ P)))
    return {"idempotent": idem == 0.0, "commutes_with_pi_A": comm == 0.0,
            "orthogonal_to_pi_unit": orth == 0.0,
            "legitimate_direct_summand": bool(idem == 0.0 and comm == 0.0 and orth == 0.0),
            "overlap_with_pi_unit": orth}


def main() -> None:
    # ---- 1. what is the obstruction ----
    for rule in ("lambda", "lambda_bar", "zero", "free_real"):
        resid, norm = obstruction(rule)
        sup = support_states(resid)
        record(f"orientability obstruction for chi = {rule}",
               "EXACT" if norm < 1e-9 else "COMPUTED",
               {"norm": round(norm, 12),
                "squared_norm": round(norm ** 2, 9),
                "support_size": len(sup),
                "support": [label(i) for i in sup],
                "all_lepton_states": all(K.STATES[i][3] == 3 for i in sup),
                "orientable": bool(norm < 1e-9)})

    # ---- 2. the obstruction is J-closed ----
    resid, _ = obstruction("lambda")
    sup = set(support_states(resid))
    j_image = {J_PAIR[i] for i in sup if i in J_PAIR}
    record("the lambda obstruction support is closed under J", "EXACT",
           {"support": sorted(sup), "J_image": sorted(j_image),
            "J_closed": sup == j_image,
            "reading": "J pairs 11<->27 and 15<->31; the obstruction is a "
                       "particle/antiparticle-symmetric object, not a one-sided defect"})

    # ---- 3. enumerate what removes it ----
    candidates: List[Tuple[str, List[int]]] = [
        ("R on antilepton {11,15,19,23}  [= the tower's R_lbar]", ANTILEPTON),
        ("R on particle leptons {3,7,27,31}", PARTICLE_LEPTON),
        ("R on right-handed leptons {11,15,27,31}  [= the obstruction support]", RH_LEPTON),
        ("R on all eight lepton states", LEPTONS),
        ("R on {11,15} only", [11, 15]),
        ("R on {19,23} only", [19, 23]),
        ("R on {27,31} only", [27, 31]),
        ("R on {3,7} only", [3, 7]),
    ]
    table = []
    for name, states in candidates:
        P = projector(states)
        for rule in ("lambda", "zero"):
            _, norm = obstruction(rule, [P])
            leg = is_direct_summand(rule, P)
            table.append({
                "extension": name, "base_chi": rule,
                "restores_orientability": bool(norm < 1e-9),
                "residual_after": round(norm, 12),
                **leg,
            })
    winners = [t for t in table
               if t["restores_orientability"] and t["legitimate_direct_summand"]]
    record("enumeration of algebra extensions that restore orientability", "EXACT",
           {"tested": len(table),
            "restore_and_legitimate": [(w["extension"], w["base_chi"]) for w in winners],
            "unique": len({w["extension"] for w in winners}) == 1})

    # ---- 4. the self-check: does free_real's extension equal the winner? ----
    P = projector(ANTILEPTON)
    _, n_before = obstruction("zero")
    _, n_after = obstruction("zero", [P])
    _, n_free = obstruction("free_real")
    record("adjoining R on the antilepton slots to chi=0 reproduces free_real",
           "EXACT" if abs(n_after - n_free) < 1e-9 else "DISCREPANCY",
           {"chi=0 alone": round(n_before, 9),
            "chi=0 + R_lbar": round(n_after, 12),
            "free_real directly": round(n_free, 12),
            "identical": bool(abs(n_after - n_free) < 1e-9)})

    width = 78
    print("=" * width)
    print("RUNG XVIII -- THE OBSTRUCTION")
    print("=" * width)
    for r in RESULTS:
        print(f"\n[{r['status']:10s}] {r['claim']}")
        for k, v in r["detail"].items():
            print(f"      {k}: {v}")
    print("\n" + "-" * width)
    print(f"{'extension':<52}{'chi':<12}{'fixes?':<9}{'legit?':<8}")
    print("-" * width)
    for t in table:
        print(f"{t['extension'][:50]:<52}{t['base_chi']:<12}"
              f"{str(t['restores_orientability']):<9}"
              f"{str(t['legitimate_direct_summand']):<8}")
    print("=" * width)

    with open("/home/claude/rung_xviii_obstruction.json", "w") as f:
        json.dump({"results": RESULTS, "enumeration": table}, f, indent=2, default=str)


if __name__ == "__main__":
    main()

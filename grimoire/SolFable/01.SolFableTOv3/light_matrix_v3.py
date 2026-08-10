#!/usr/bin/env python3
"""THEA v3.0 light-matrix reference kernel.

This file keeps three layers separate:

1. Exact integer closure arithmetic on the hexagonal lattice.
2. Exact fullerene topology counts for icosahedral Goldberg shells.
3. Numerical graph-spectrum experiments on a closed leapfrog tower.

The code does not claim that a fullerene graph is spacetime, that the golden
ratio determines Planck's constant, or that a numerical spectral limit is a
proved universal constant. Those are hypotheses to test, not outputs to print.

Dependencies for exact shell arithmetic: Python 3.10+ only.
Dependencies for graph spectra: networkx, numpy, scipy.
Optional dependency for the exact C60 characteristic polynomial: sympy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from math import atan2, log, pi, sqrt
from pathlib import Path
from typing import Any, Hashable, Iterable, Sequence

PHI = (1.0 + sqrt(5.0)) / 2.0
PHI2 = PHI * PHI
INV_PHI2 = 1.0 / PHI2
PLANCK_LENGTH_M = 1.616255e-35
C60_EDGE_M = 1.42e-10


@dataclass(frozen=True)
class Pair:
    k: int
    ell: int


@dataclass(frozen=True)
class Shell:
    level: int
    k: int
    ell: int
    triangulation_number: int
    vertices: int
    edges: int
    faces: int
    pentagons: int
    hexagons: int
    chi: int
    radius_scale: float
    projective_ratio: float | None
    projective_error: float | None


@dataclass(frozen=True)
class SpectralRow:
    level: int
    vertices: int
    triangulation_number: int
    pentagons: int
    hexagons: int
    chi: int
    lambda2: float
    scaled_lambda2: float
    central_adjacency_gap: float | None
    scaled_central_gap: float | None


def hex_norm(k: int, ell: int) -> int:
    """Return T = k^2 + k*ell + ell^2."""
    return k * k + k * ell + ell * ell


def topology_from_t(t: int) -> dict[str, int]:
    """Exact counts for an icosahedral Goldberg fullerene with V = 20*T."""
    if t < 1:
        raise ValueError("triangulation number T must be positive")
    vertices = 20 * t
    edges = 30 * t
    pentagons = 12
    hexagons = 10 * (t - 1)
    faces = pentagons + hexagons
    chi = vertices - edges + faces
    return {
        "T": t,
        "V": vertices,
        "E": edges,
        "F": faces,
        "P": pentagons,
        "H": hexagons,
        "chi": chi,
    }


def shell_from_pair(pair: Pair, level: int = 0) -> Shell:
    t = hex_norm(pair.k, pair.ell)
    topo = topology_from_t(t)
    ratio = None if pair.ell == 0 else pair.k / pair.ell
    error = None if ratio is None else abs(ratio - PHI)
    return Shell(
        level=level,
        k=pair.k,
        ell=pair.ell,
        triangulation_number=t,
        vertices=topo["V"],
        edges=topo["E"],
        faces=topo["F"],
        pentagons=topo["P"],
        hexagons=topo["H"],
        chi=topo["chi"],
        radius_scale=sqrt(t),
        projective_ratio=ratio,
        projective_error=error,
    )


def golden_next(pair: Pair) -> Pair:
    """Apply the Fibonacci selector F=[[1,1],[1,0]]."""
    return Pair(pair.k + pair.ell, pair.k)


def golden_shells(levels: int, start: Pair = Pair(1, 0)) -> list[Shell]:
    if levels < 1:
        raise ValueError("levels must be at least 1")
    out: list[Shell] = []
    pair = start
    for level in range(levels):
        out.append(shell_from_pair(pair, level))
        pair = golden_next(pair)
    return out


def multiply_pairs(left: Pair, right: Pair) -> Pair:
    """Multiply (a+b*zeta6)(k+ell*zeta6), zeta6^2=zeta6-1."""
    a, b = left.k, left.ell
    k, ell = right.k, right.ell
    return Pair(a * k - b * ell, a * ell + b * k + b * ell)


def rotate60(pair: Pair) -> Pair:
    """Multiply a hex-lattice coordinate by zeta6 = exp(i*pi/3)."""
    return Pair(-pair.ell, pair.k + pair.ell)


def conjugate(pair: Pair) -> Pair:
    """Complex conjugation in the basis 1,zeta6."""
    return Pair(pair.k + pair.ell, -pair.ell)


def canonical_pair(pair: Pair) -> Pair:
    """Choose the D6-equivalent representative with k >= ell >= 0."""
    candidates: list[Pair] = []
    for seed in (pair, conjugate(pair)):
        item = seed
        for _ in range(6):
            candidates.append(item)
            item = rotate60(item)
    sector = [p for p in candidates if p.k >= p.ell >= 0]
    if not sector:
        raise RuntimeError(f"no canonical representative found for {pair}")
    return min(sector, key=lambda p: (p.k, p.ell))


def gc_step(pair: Pair, generator: Pair, canonical: bool = True) -> Pair:
    raw = multiply_pairs(generator, pair)
    return canonical_pair(raw) if canonical else raw


def lifted_step(state: tuple[int, int, int]) -> tuple[int, int, int]:
    """Apply B to (k^2,k*ell,ell^2)."""
    x, y, z = state
    return x + 2 * y + z, x + y, x


def exact_matrix_certificate(samples: Iterable[Pair] | None = None) -> dict[str, Any]:
    """Verify M^T Q2 M = T Q2 and norm multiplicativity with integers."""
    if samples is None:
        samples = (Pair(1, 1), Pair(2, 1), Pair(4, 3), Pair(7, 2))
    q2 = ((2, 1), (1, 2))
    checked: list[dict[str, Any]] = []

    for pair in samples:
        k, ell = pair.k, pair.ell
        matrix = ((k, -ell), (ell, k + ell))
        t = hex_norm(k, ell)

        def matmul(a: Sequence[Sequence[int]], b: Sequence[Sequence[int]]) -> list[list[int]]:
            return [
                [sum(a[i][m] * b[m][j] for m in range(2)) for j in range(2)]
                for i in range(2)
            ]

        transpose = ((matrix[0][0], matrix[1][0]), (matrix[0][1], matrix[1][1]))
        lhs = matmul(matmul(transpose, q2), matrix)
        rhs = [[t * q2[i][j] for j in range(2)] for i in range(2)]
        if lhs != rhs:
            raise AssertionError(f"hex metric identity failed for {pair}: {lhs} != {rhs}")
        checked.append({"pair": asdict(pair), "T": t, "metric_identity": True})

    left = Pair(2, 1)
    right = Pair(3, 2)
    product = multiply_pairs(left, right)
    if hex_norm(product.k, product.ell) != hex_norm(left.k, left.ell) * hex_norm(right.k, right.ell):
        raise AssertionError("hex norm multiplicativity failed")

    pair = Pair(5, 3)
    monomials = (pair.k * pair.k, pair.k * pair.ell, pair.ell * pair.ell)
    next_pair = golden_next(pair)
    direct = (next_pair.k**2, next_pair.k * next_pair.ell, next_pair.ell**2)
    if lifted_step(monomials) != direct:
        raise AssertionError("lifted Fibonacci identity failed")

    return {
        "metric": q2,
        "samples": checked,
        "norm_multiplicativity": True,
        "lifted_identity": True,
        "core_characteristic_polynomial": "(x-1)(x+1)(x^2-3x+1)",
        "core_eigenvalues": ["phi^2", "1", "-1", "phi^-2"],
    }


def golden_closed_form_t(level: int) -> float:
    """Closed form for T_n with (k_n,ell_n)=(F_{n+1},F_n)."""
    return (
        (2.0 / 5.0) * (PHI ** (2 * level + 2) + PHI ** (-2 * level - 2))
        - (1.0 / 5.0) * ((-1.0) ** level)
    )


def c60_radius_from_edge(edge_m: float = C60_EDGE_M) -> float:
    return edge_m * sqrt(58.0 + 18.0 * sqrt(5.0)) / 4.0


def planck_level(start_length_m: float, contraction: float, planck_length_m: float) -> float:
    if start_length_m <= 0 or planck_length_m <= 0:
        raise ValueError("lengths must be positive")
    if not 0 < contraction < 1:
        raise ValueError("contraction must lie strictly between 0 and 1")
    return log(start_length_m / planck_length_m) / log(1.0 / contraction)


def planck_report() -> dict[str, Any]:
    radius = c60_radius_from_edge()
    return {
        "status": "HYPOTHESIS_TEST_NOT_DERIVATION",
        "planck_length_m": PLANCK_LENGTH_M,
        "edge_m": C60_EDGE_M,
        "ideal_c60_radius_m": radius,
        "q_phi_minus_2": INV_PHI2,
        "levels_from_edge": planck_level(C60_EDGE_M, INV_PHI2, PLANCK_LENGTH_M),
        "levels_from_radius": planck_level(radius, INV_PHI2, PLANCK_LENGTH_M),
        "levels_from_diameter": planck_level(2.0 * radius, INV_PHI2, PLANCK_LENGTH_M),
        "warning": "The count depends on the chosen start length and contraction; h is not a length.",
    }


def planar_embedding_and_faces(graph: Any) -> tuple[Any, list[list[Hashable]]]:
    import networkx as nx

    planar, embedding = nx.check_planarity(graph, counterexample=False)
    if not planar:
        raise ValueError("graph is not planar")
    marked_half_edges: set[tuple[Hashable, Hashable]] = set()
    faces: list[list[Hashable]] = []
    for u in embedding:
        for v in embedding.neighbors_cw_order(u):
            if (u, v) not in marked_half_edges:
                faces.append(embedding.traverse_face(u, v, marked_half_edges))
    return embedding, faces


def dual_graph(graph: Any) -> Any:
    import networkx as nx

    _, faces = planar_embedding_and_faces(graph)
    half_edge_to_face: dict[tuple[Hashable, Hashable], int] = {}
    for face_id, face in enumerate(faces):
        for index, u in enumerate(face):
            v = face[(index + 1) % len(face)]
            half_edge_to_face[(u, v)] = face_id
    dual = nx.Graph()
    dual.add_nodes_from(range(len(faces)))
    for u, v in graph.edges():
        left = half_edge_to_face[(u, v)]
        right = half_edge_to_face[(v, u)]
        if left != right:
            dual.add_edge(left, right)
    return dual


def truncate_graph(graph: Any) -> Any:
    import networkx as nx

    embedding, _ = planar_embedding_and_faces(graph)
    truncated = nx.Graph()
    for u, v in graph.edges():
        truncated.add_edge((u, v), (v, u))
    for u in graph.nodes():
        neighbors = list(embedding.neighbors_cw_order(u))
        for index, v in enumerate(neighbors):
            w = neighbors[(index + 1) % len(neighbors)]
            truncated.add_edge((u, v), (u, w))
    return nx.convert_node_labels_to_integers(truncated)


def leapfrog(graph: Any) -> Any:
    return truncate_graph(dual_graph(graph))


def face_size_counts(graph: Any) -> Counter[int]:
    _, faces = planar_embedding_and_faces(graph)
    return Counter(map(len, faces))


def graph_topology_certificate(graph: Any) -> dict[str, Any]:
    import networkx as nx

    faces = face_size_counts(graph)
    vertices = graph.number_of_nodes()
    edges = graph.number_of_edges()
    face_total = sum(faces.values())
    chi = vertices - edges + face_total
    degrees = Counter(dict(graph.degree()).values())
    return {
        "V": vertices,
        "E": edges,
        "F": face_total,
        "P": faces.get(5, 0),
        "H": faces.get(6, 0),
        "other_faces": {str(k): v for k, v in faces.items() if k not in (5, 6)},
        "chi": chi,
        "connected": nx.is_connected(graph),
        "degree_counts": {str(k): v for k, v in sorted(degrees.items())},
        "pass": (
            nx.is_connected(graph)
            and degrees == Counter({3: vertices})
            and faces.get(5, 0) == 12
            and not any(k not in (5, 6) for k in faces)
            and chi == 2
        ),
    }


def laplacian_gap(graph: Any) -> float:
    import networkx as nx
    import numpy as np
    from scipy.sparse.linalg import eigsh

    adjacency = nx.to_scipy_sparse_array(graph, format="csr", dtype=float)
    values = eigsh(
        adjacency,
        k=4,
        which="LA",
        return_eigenvectors=False,
        tol=1.0e-11,
        maxiter=500_000,
    )
    values.sort()
    return float(3.0 - values[-2])


def central_adjacency_gap(graph: Any) -> float | None:
    import networkx as nx
    import numpy as np
    from scipy.sparse.linalg import eigsh

    adjacency = nx.to_scipy_sparse_array(graph, format="csc", dtype=float)
    try:
        nearby = eigsh(
            adjacency,
            k=min(20, graph.number_of_nodes() - 2),
            sigma=0.0,
            which="LM",
            return_eigenvectors=False,
            tol=1.0e-10,
            maxiter=500_000,
        )
    except RuntimeError:
        return None
    tolerance = 1.0e-9
    negative = nearby[nearby < -tolerance]
    positive = nearby[nearby > tolerance]
    if len(negative) == 0 or len(positive) == 0:
        return None
    return float(np.min(positive) - np.max(negative))


def low_laplacian_bands(graph: Any, t: int, count: int = 30, tolerance: float = 2.0e-6, max_bands: int = 4) -> list[dict[str, Any]]:
    import networkx as nx
    import numpy as np
    from scipy.sparse.linalg import eigsh

    adjacency = nx.to_scipy_sparse_array(graph, format="csr", dtype=float)
    k = min(count, graph.number_of_nodes() - 2)
    adjacency_values = eigsh(
        adjacency,
        k=k,
        which="LA",
        return_eigenvectors=False,
        tol=1.0e-10,
        maxiter=1_000_000,
    )
    scaled = np.sort((3.0 - adjacency_values) * t)
    scaled = scaled[scaled > 1.0e-7]
    bands: list[dict[str, Any]] = []
    for value in scaled:
        if not bands or abs(value - bands[-1]["value"]) > tolerance:
            bands.append({"value": float(value), "multiplicity": 1})
        else:
            band = bands[-1]
            count_old = band["multiplicity"]
            band["value"] = (band["value"] * count_old + float(value)) / (count_old + 1)
            band["multiplicity"] = count_old + 1
    return bands[:max_bands]


def spectral_tower(levels: int, include_central_gap: bool = True) -> tuple[list[SpectralRow], Any]:
    if levels < 1:
        raise ValueError("levels must be at least 1")
    import networkx as nx

    graph = nx.dodecahedral_graph()
    rows: list[SpectralRow] = []
    for level in range(levels):
        t = 3**level
        cert = graph_topology_certificate(graph)
        if not cert["pass"]:
            raise RuntimeError(f"topology certificate failed at level {level}: {cert}")
        if cert["V"] != 20 * t:
            raise RuntimeError(f"size recurrence failed at level {level}: {cert['V']} != {20*t}")
        lambda2 = laplacian_gap(graph)
        central = central_adjacency_gap(graph) if include_central_gap else None
        rows.append(
            SpectralRow(
                level=level,
                vertices=cert["V"],
                triangulation_number=t,
                pentagons=cert["P"],
                hexagons=cert["H"],
                chi=cert["chi"],
                lambda2=lambda2,
                scaled_lambda2=t * lambda2,
                central_adjacency_gap=central,
                scaled_central_gap=None if central is None else sqrt(t) * central,
            )
        )
        if level + 1 < levels:
            graph = leapfrog(graph)
    return rows, graph


def exact_c60_characteristic_polynomial() -> dict[str, Any]:
    import networkx as nx
    import sympy as sp

    c60 = leapfrog(nx.dodecahedral_graph())
    adjacency = sp.Matrix(nx.to_numpy_array(c60, dtype=int))
    x = sp.symbols("x")
    factorization = sp.factor(adjacency.charpoly(x).as_expr())
    least = -PHI2
    numeric_least = min(float(v) for v in adjacency.eigenvals().keys())
    return {
        "factorization": str(factorization),
        "least_eigenvalue_symbolic": "-(3+sqrt(5))/2 = -phi^2",
        "least_eigenvalue_numeric": numeric_least,
        "multiplicity": 3,
        "matches_phi2": abs(numeric_least - least) < 1.0e-12,
    }


def summarize_bands(bands: list[dict[str, Any]]) -> dict[str, Any]:
    if not bands:
        return {}
    first = bands[0]["value"]
    out: dict[str, Any] = {"first_band": bands[0], "bands": bands}
    if len(bands) > 1:
        out["second_to_first_ratio"] = bands[1]["value"] / first
    if len(bands) > 3 and bands[2]["multiplicity"] + bands[3]["multiplicity"] == 7:
        total_mult = bands[2]["multiplicity"] + bands[3]["multiplicity"]
        center = (
            bands[2]["value"] * bands[2]["multiplicity"]
            + bands[3]["value"] * bands[3]["multiplicity"]
        ) / total_mult
        out["third_harmonic_split_center"] = center
        out["third_center_to_first_ratio"] = center / first
    return out


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    exact = exact_matrix_certificate()
    shells = golden_shells(args.golden_levels)
    for shell in shells:
        closed_form = golden_closed_form_t(shell.level)
        if abs(closed_form - shell.triangulation_number) > 1.0e-7:
            raise AssertionError(f"closed form failed at level {shell.level}")

    report: dict[str, Any] = {
        "schema": "thea-light-matrix/3.0",
        "status": {
            "exact": [
                "Euler fullerene invariant P=12",
                "hex-lattice metric identity",
                "Goldberg shell counts",
                "Fibonacci selector and lifted matrix",
            ],
            "computed": [],
            "hypothesis": [
                "physical substrate interpretation",
                "Planck cutoff interpretation",
            ],
        },
        "constants": {
            "phi": PHI,
            "phi2": PHI2,
            "phi_minus_2": INV_PHI2,
            "pi": pi,
        },
        "exact_matrix_certificate": exact,
        "golden_shells": [asdict(shell) for shell in shells],
        "planck_test": planck_report(),
    }

    if args.spectral_levels > 0:
        rows, final_graph = spectral_tower(args.spectral_levels, not args.skip_central_gap)
        bands = low_laplacian_bands(final_graph, 3 ** (args.spectral_levels - 1), args.band_count)
        report["spectral_tower"] = [asdict(row) for row in rows]
        report["low_laplacian_bands_final_level"] = summarize_bands(bands)
        report["status"]["computed"].extend(
            [
                "T*lambda2 convergence on the leapfrog tower",
                "low-frequency multiplicity bands",
                "sqrt(T)*central adjacency gap trend",
            ]
        )

    if args.exact_c60:
        report["exact_c60_spectrum"] = exact_c60_characteristic_polynomial()
        report["status"]["exact"].append("C60 adjacency characteristic polynomial")

    return report


def format_report(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("THEA v3.0 LIGHT MATRIX CERTIFICATE")
    lines.append("=" * 40)
    lines.append("")
    lines.append("GOLDEN-SELECTED CLOSED SHELLS")
    lines.append("level  (k,l)       T       C atoms    H       k/l              next R ratio")
    shells = report["golden_shells"]
    for index, shell in enumerate(shells):
        ratio = "--" if shell["projective_ratio"] is None else f"{shell['projective_ratio']:.12f}"
        if index + 1 < len(shells):
            next_ratio = sqrt(shells[index + 1]["triangulation_number"] / shell["triangulation_number"])
            next_text = f"{next_ratio:.12f}"
        else:
            next_text = "--"
        lines.append(
            f"{shell['level']:>5d}  ({shell['k']:>4d},{shell['ell']:<4d})  "
            f"{shell['triangulation_number']:>7d}  {shell['vertices']:>10d}  "
            f"{shell['hexagons']:>7d}  {ratio:>14s}  {next_text:>17s}"
        )
    lines.append("")
    lines.append(f"phi   = {report['constants']['phi']:.15f}")
    lines.append(f"phi^2 = {report['constants']['phi2']:.15f}")

    rows = report.get("spectral_tower", [])
    if rows:
        lines.append("")
        lines.append("LEAPFROG CLOSED-SHELL SPECTRUM")
        lines.append("level       N          T          lambda2(L)         T*lambda2       A-gap          sqrt(T)*gap")
        for row in rows:
            central = row["central_adjacency_gap"]
            central_scaled = row["scaled_central_gap"]
            central_text = "zero/skip" if central is None else f"{central:.12g}"
            scaled_text = "--" if central_scaled is None else f"{central_scaled:.10g}"
            lines.append(
                f"{row['level']:>5d}  {row['vertices']:>7d}  {row['triangulation_number']:>9d}  "
                f"{row['lambda2']:>18.12g}  {row['scaled_lambda2']:>18.12g}  "
                f"{central_text:>13s}  {scaled_text:>13s}"
            )

    bands = report.get("low_laplacian_bands_final_level", {})
    if bands:
        lines.append("")
        lines.append("FINAL RENORMALIZED LOW BANDS")
        for band in bands["bands"]:
            lines.append(f"mu = {band['value']:.9f}  multiplicity = {band['multiplicity']}")
        if "second_to_first_ratio" in bands:
            lines.append(f"second/first = {bands['second_to_first_ratio']:.9f}  (sphere target: 3)")
        if "third_center_to_first_ratio" in bands:
            lines.append(f"split-seven center/first = {bands['third_center_to_first_ratio']:.9f}  (sphere target: 6)")

    c60 = report.get("exact_c60_spectrum")
    if c60:
        lines.append("")
        lines.append("EXACT C60 ADJACENCY RESULT")
        lines.append(c60["factorization"])
        lines.append(f"least eigenvalue: {c60['least_eigenvalue_symbolic']} (multiplicity {c60['multiplicity']})")

    planck = report["planck_test"]
    lines.append("")
    lines.append("PLANCK-SCALE HYPOTHESIS TEST")
    lines.append(f"edge start:     {planck['levels_from_edge']:.9f} levels")
    lines.append(f"radius start:   {planck['levels_from_radius']:.9f} levels")
    lines.append(f"diameter start: {planck['levels_from_diameter']:.9f} levels")
    lines.append(planck["warning"])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden-levels", type=int, default=12)
    parser.add_argument("--spectral-levels", type=int, default=8)
    parser.add_argument("--band-count", type=int, default=30)
    parser.add_argument("--skip-central-gap", action="store_true")
    parser.add_argument("--exact-c60", action="store_true")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--text", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.golden_levels < 1:
        raise SystemExit("--golden-levels must be positive")
    if args.spectral_levels < 0:
        raise SystemExit("--spectral-levels cannot be negative")
    report = build_report(args)
    text = format_report(report)
    print(text, end="")
    if args.json:
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if args.text:
        args.text.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()

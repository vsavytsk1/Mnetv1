"""RUSTIUM verifier -- the third witness.

Proof by kernel, not by claim (Path III). The Rust crate `goldberg_kernel`
asserts a table of constants. This script re-derives every one of them in a
DIFFERENT language, from first principles, and REFUSES to emit a certificate
if any of them disagrees.

Three witnesses must agree before RUSTIUM claims anything:
  1. the browser / THEA JS kernel      (already shipped)
  2. `cargo test` in Gos/             (the Rust side)
  3. this file                         (independent Python re-derivation)

Curse 2:  ASCII-only source. No glyphs.
Curse 18: run with `py -3 verify_rustium.py`.
Curse 26: target, current and error are printed side by side. Always.
Curse 38: outputs go to a portable --out dir; the clock lives OUTSIDE the
          hashed region. Hash the math, not the moment.

P=12 . chi=2 . E/V=1.5 . the price is always paid . always
"""

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# the ledger of results -- every check appends here, nothing is assumed
# ---------------------------------------------------------------------------

CHECKS = []


def check(name, target, current, ok, note=""):
    """Record one invariant. Target and current are always both shown."""
    CHECKS.append(
        {
            "name": name,
            "target": str(target),
            "current": str(current),
            "pass": bool(ok),
            "note": note,
        }
    )
    return bool(ok)


# ---------------------------------------------------------------------------
# STAGE 0 -- phi, and the ladder that needs none of it
# ---------------------------------------------------------------------------

PHI = 1.618_033_988_749_894_8  # the f64 nearest the golden ratio
TWO_POW_53 = 9_007_199_254_740_992
I128_MAX = (1 << 127) - 1


def ladder_exact(n):
    """T_0=1, T_1=3, T_n = 3*T_(n-1) - T_(n-2) - (-1)^n. Python ints: unbounded."""
    t = [1]
    if n == 0:
        return t
    t.append(3)
    for k in range(2, n + 1):
        sign = 1 if k % 2 == 0 else -1
        t.append(3 * t[k - 1] - t[k - 2] - sign)
    return t


def ladder_f64(n):
    """The same recurrence in IEEE-754 binary64. Python floats ARE f64."""
    t = [1.0]
    if n == 0:
        return t
    t.append(3.0)
    for k in range(2, n + 1):
        sign = 1.0 if k % 2 == 0 else -1.0
        t.append(3.0 * t[k - 1] - t[k - 2] - sign)
    return t


def verify_ladder():
    print("\n-- THE LADDER ---------------------------------------------------")

    head = ladder_exact(11)
    want = [1, 3, 7, 19, 49, 129, 337, 883, 2311, 6051, 15841, 41473]
    check("ladder first 12 terms", want, head, head == want)
    print("  first 12      : %s" % head)

    ex = ladder_exact(60)
    fl = ladder_f64(60)

    # the wall: first n where the f64 recurrence disagrees with the exact one
    wall = next((i for i in range(61) if fl[i] != float(ex[i])), None)
    check("f64 wall (first disagreement)", 38, wall, wall == 38)
    print("  f64 wall      : target n=38   measured n=%s" % wall)

    # the value crossing: first n whose TERM exceeds 2^53 -- one step later
    crossing = next((i for i in range(61) if ex[i] > TWO_POW_53), None)
    check("2^53 term crossing", 39, crossing, crossing == 39)
    check("wall precedes crossing by one", 1, crossing - wall, crossing - wall == 1)
    print("  2^53 crossing : target n=39   measured n=%s" % crossing)

    # the mechanism: the INTERMEDIATE 3*T_37 overflows before the term does
    t37, t38 = ex[37], ex[38]
    check("T_37 exact", 3_055_769_911_545_123, t37, t37 == 3_055_769_911_545_123)
    check("T_38 exact", 8_000_109_490_224_391, t38, t38 == 8_000_109_490_224_391)
    check("3*T_37 exceeds 2^53", "> %d" % TWO_POW_53, 3 * t37, 3 * t37 > TWO_POW_53)
    check("T_38 itself is under 2^53", "< %d" % TWO_POW_53, t38, t38 < TWO_POW_53)
    print("  3*T_37        : %d" % (3 * t37))
    print("  2^53          : %d   (the product leaves the range first)" % TWO_POW_53)
    print("  T_38 exact    : %d" % t38)
    print("  T_38 in f64   : %d   (off by %d)" % (int(fl[38]), abs(int(fl[38]) - t38)))

    # everything below the wall must agree bit-for-bit
    below = all(fl[i] == float(ex[i]) for i in range(38))
    check("all n < 38 agree exactly", True, below, below)

    # the error must compound past the wall, never shrink back
    e38 = abs(fl[38] - float(ex[38])) / float(ex[38])
    e50 = abs(fl[50] - float(ex[50])) / float(ex[50])
    check("error compounds past the wall", "e50 > e38", "%.3e > %.3e" % (e50, e38), e50 > e38)
    print("  rel err n=38  : %.6e" % e38)
    print("  rel err n=50  : %.6e   (compounds)" % e50)

    # the i128 ceiling claimed by the crate
    big = ladder_exact(93)
    fits92 = big[92] <= I128_MAX
    fits93 = big[93] <= I128_MAX
    check("T_92 fits in i128", True, fits92, fits92)
    check("T_93 does NOT fit in i128", False, fits93, not fits93)
    print("  T_92 <= i128max: %s   T_93 <= i128max: %s" % (fits92, fits93))

    # phi's defining equation, in f64
    dphi = abs(PHI * PHI - (PHI + 1.0))
    check("phi^2 = phi + 1 (f64)", "< 1e-15", "%.3e" % dphi, dphi < 1e-15)
    print("  phi^2-(phi+1) : %.3e" % dphi)


# ---------------------------------------------------------------------------
# STAGE 1 -- the C60 topology, re-derived from the phi permutations
# ---------------------------------------------------------------------------

PERMS = ((0, 1, 2), (1, 2, 0), (2, 0, 1))


def push_perms(a, b, c, raw):
    """Cyclic permutations and sign combinations. A zero coordinate has no
    distinct negative, so it is skipped -- that is what sets the raw count."""
    for p in PERMS:
        for sa in (-1.0, 1.0):
            for sb in (-1.0, 1.0):
                for sc in (-1.0, 1.0):
                    if a == 0.0 and sa < 0.0:
                        continue
                    if b == 0.0 and sb < 0.0:
                        continue
                    if c == 0.0 and sc < 0.0:
                        continue
                    v = [0.0, 0.0, 0.0]
                    v[p[0]] = sa * a
                    v[p[1]] = sb * b
                    v[p[2]] = sc * c
                    raw.append(tuple(v))


def vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vdot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vcross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def vlen(a):
    return math.sqrt(vdot(a, a))


def vscale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def vnorm(a):
    l = vlen(a)
    return a if l == 0.0 else vscale(a, 1.0 / l)


def build_c60_vertices():
    raw = []
    push_perms(0.0, 1.0, 3.0 * PHI, raw)
    push_perms(1.0, 2.0 + PHI, 2.0 * PHI, raw)
    push_perms(PHI, 2.0, 2.0 * PHI + 1.0, raw)
    out = []
    for v in raw:
        if not any(
            abs(v[0] - u[0]) < 1e-9 and abs(v[1] - u[1]) < 1e-9 and abs(v[2] - u[2]) < 1e-9
            for u in out
        ):
            out.append(v)
    return len(raw), [vnorm(v) for v in out]


def build_edges(verts):
    n = len(verts)
    min_d = float("inf")
    for i in range(n):
        for j in range(i + 1, n):
            d = vlen(vsub(verts[i], verts[j]))
            if d < min_d:
                min_d = d
    tol = min_d * 1.15
    edges, adj = [], [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if vlen(vsub(verts[i], verts[j])) <= tol:
                edges.append((i, j))
                adj[i].append(j)
                adj[j].append(i)
    return edges, adj, min_d


def next_in_face(verts, adj, a, b):
    """Smallest positive turn in the tangent plane at b. Orientable by construction."""
    nrm = vnorm(verts[b])
    r = vsub(verts[a], verts[b])
    r = vnorm(vsub(r, vscale(nrm, vdot(r, nrm))))
    perp = vcross(nrm, r)
    best, best_ang = None, float("inf")
    for c in adj[b]:
        if c == a:
            continue
        t = vsub(verts[c], verts[b])
        t = vsub(t, vscale(nrm, vdot(t, nrm)))
        ang = math.atan2(vdot(t, perp), vdot(t, r))
        if ang < 0.0:
            ang += 2.0 * math.pi
        if ang < best_ang:
            best_ang, best = ang, c
    return best


def build_faces(verts, adj):
    seen, faces = set(), []
    for a in range(len(verts)):
        for b in adj[a]:
            if (a, b) in seen:
                continue
            face = [a]
            x, y = a, b
            while True:
                seen.add((x, y))
                face.append(y)
                z = next_in_face(verts, adj, x, y)
                if z is None:
                    break
                x, y = y, z
                if (x, y) == (a, b):
                    break
                if len(face) > 16:
                    break
            if face and face[-1] == a:
                face.pop()
            faces.append(face)
    return faces


def verify_topology():
    print("\n-- THE C60 TOPOLOGY --------------------------------------------")

    raw_count, verts = build_c60_vertices()
    print("  raw points    : %d   (before dedupe)" % raw_count)
    check("V after dedupe", 60, len(verts), len(verts) == 60)

    edges, adj, min_d = build_edges(verts)
    faces = build_faces(verts, adj)

    v, e, f = len(verts), len(edges), len(faces)
    pent = sum(1 for x in faces if len(x) == 5)
    hexa = sum(1 for x in faces if len(x) == 6)
    chi = v - e + f

    check("V", 60, v, v == 60)
    check("E", 90, e, e == 90)
    check("F", 32, f, f == 32)
    check("P (Euler forces 12)", 12, pent, pent == 12)
    check("H", 20, hexa, hexa == 20)
    check("chi", 2, chi, chi == 2)
    print("  V=%d E=%d F=%d P=%d H=%d chi=%d" % (v, e, f, pent, hexa, chi))

    degs = sorted({len(a) for a in adj})
    check("every vertex trivalent", [3], degs, degs == [3])

    check("E/V = 3/2", "2E == 3V", "%d == %d" % (2 * e, 3 * v), 2 * e == 3 * v)
    print("  E/V           : %d/%d = %.1f" % (e, v, e / v))

    only56 = all(len(x) in (5, 6) for x in faces)
    check("only pentagons and hexagons", True, only56, only56)

    # the real orientability proof: every DIRECTED edge in exactly one face
    counts = {}
    for face in faces:
        for i in range(len(face)):
            k = (face[i], face[(i + 1) % len(face)])
            counts[k] = counts.get(k, 0) + 1
    check("directed edges", 180, len(counts), len(counts) == 180)
    once = all(c == 1 for c in counts.values())
    check("each directed edge in exactly ONE face", True, once, once)
    print("  directed edges: %d, each used exactly once: %s" % (len(counts), once))

    # all on the unit sphere
    worst = max(abs(vlen(p) - 1.0) for p in verts)
    check("all vertices on unit sphere", "< 1e-12", "%.3e" % worst, worst < 1e-12)
    print("  sphere err    : %.3e" % worst)

    # centrally symmetric -> centroid at the origin
    s = (
        sum(p[0] for p in verts) / v,
        sum(p[1] for p in verts) / v,
        sum(p[2] for p in verts) / v,
    )
    cworst = max(abs(x) for x in s)
    check("centroid at origin", "< 1e-12", "%.3e" % cworst, cworst < 1e-12)
    print("  centroid err  : %.3e" % cworst)

    return raw_count


# ---------------------------------------------------------------------------
# STAGE 2 -- the Goldberg ladder / HELENA build card
# ---------------------------------------------------------------------------

def verify_build_card():
    print("\n-- THE HELENA BUILD CARD ---------------------------------------")
    card = [
        (0, 3, 60, 90, 32, 12, 20),
        (1, 21, 420, 630, 212, 12, 200),
        (2, 147, 2940, 4410, 1472, 12, 1460),
        (3, 1029, 20580, 30870, 10292, 12, 10280),
    ]
    print("  level      T       V       E       F    P       H   chi   E/V")
    ok_all = True
    for level, t_w, v_w, e_w, f_w, p_w, h_w in card:
        t = 3 * 7 ** level
        v, e, f = 20 * t, 30 * t, 10 * t + 2
        p, h = 12, f - 12
        chi = v - e + f
        row_ok = (t, v, e, f, p, h, chi) == (t_w, v_w, e_w, f_w, p_w, h_w, 2) and 2 * e == 3 * v
        ok_all = ok_all and row_ok
        print(
            "  %5d %6d %7d %7d %7d %4d %7d %5d %5.1f  %s"
            % (level, t, v, e, f, p, h, chi, e / v, "OK" if row_ok else "FAIL")
        )
    check("HELENA build card k=0..3", "T=3*7^k, V=20T, E=30T, F=10T+2, P=12", "4 rows", ok_all)


# ---------------------------------------------------------------------------
# STAGE 3 -- xoshiro256** : the reference stream
# ---------------------------------------------------------------------------

MASK64 = (1 << 64) - 1


def rotl(x, k):
    return ((x << k) | (x >> (64 - k))) & MASK64


def splitmix64_stream(seed, count):
    x = seed & MASK64
    out = []
    for _ in range(count):
        x = (x + 0x9E37_79B9_7F4A_7C15) & MASK64
        z = x
        z = ((z ^ (z >> 30)) * 0xBF58_476D_1CE4_E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D0_49BB_1331_11EB) & MASK64
        out.append(z ^ (z >> 31))
    return out


class Xoshiro:
    def __init__(self, seed):
        self.s = splitmix64_stream(seed, 4)

    def next_u64(self):
        s = self.s
        result = (rotl((s[1] * 5) & MASK64, 7) * 9) & MASK64
        t = (s[1] << 17) & MASK64
        s[2] ^= s[0]
        s[3] ^= s[1]
        s[1] ^= s[2]
        s[0] ^= s[3]
        s[2] ^= t
        s[3] = rotl(s[3], 45)
        return result

    def next_f64(self):
        return (self.next_u64() >> 11) * (1.0 / float(1 << 53))


def verify_rng():
    print("\n-- XOSHIRO256** REFERENCE STREAM -------------------------------")
    want = [
        0xEF33_F170_5524_4B74,
        0xE1F5_9111_2FB5_051B,
        0xD8AB_0564_0214_863A,
        0xF985_E1F2_FB89_7B03,
        0xAF87_A5F7_E6CE_1408,
        0x86F2_8E3A_0746_FF9E,
    ]
    r = Xoshiro(0x5EED)
    got = [r.next_u64() for _ in range(6)]
    for i, (w, g) in enumerate(zip(want, got)):
        mark = "OK" if w == g else "MISMATCH"
        print("  word %d  target %016X  current %016X  %s" % (i, w, g, mark))
    check("xoshiro256** stream from seed 0x5EED", "6 words", "6 words", got == want)

    a, b = Xoshiro(42), Xoshiro(42)
    same = all(a.next_u64() == b.next_u64() for _ in range(100))
    check("same seed -> same stream", True, same, same)

    z = Xoshiro(0)
    nz = any(z.next_u64() != 0 for _ in range(8))
    check("seed 0 does not stick (splitmix64 seeding)", True, nz, nz)

    r2 = Xoshiro(0xC0FFEE)
    vals = [r2.next_f64() for _ in range(10_000)]
    inrange = all(0.0 <= x < 1.0 for x in vals)
    check("next_f64 in [0,1)", True, inrange, inrange)
    print("  next_f64 range: min %.6f  max %.6f  in [0,1): %s"
          % (min(vals), max(vals), inrange))


# ---------------------------------------------------------------------------
# the certificate -- hash the math, not the moment (Curse 38)
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="RUSTIUM third-witness verifier")
    ap.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parent),
        help="portable output directory (default: this script's folder)",
    )
    args = ap.parse_args()

    print("=" * 66)
    print("RUSTIUM VERIFIER -- the third witness")
    print("re-deriving every constant goldberg_kernel asserts, in Python")
    print("=" * 66)

    verify_ladder()
    raw_count = verify_topology()
    verify_build_card()
    verify_rng()

    passed = sum(1 for c in CHECKS if c["pass"])
    total = len(CHECKS)
    failed = [c for c in CHECKS if not c["pass"]]

    print("\n" + "=" * 66)
    print("RESULT: %d/%d invariants reproduced" % (passed, total))
    for c in failed:
        print("  FAIL  %-44s target=%s current=%s" % (c["name"], c["target"], c["current"]))
    print("=" * 66)

    # the hashed region contains ONLY reproducible mathematics
    payload = {
        "kernel": "goldberg_kernel",
        "witness": "verify_rustium.py",
        "invariants": CHECKS,
        "raw_permutation_points": raw_count,
        "constants": {
            "phi_f64": repr(PHI),
            "two_pow_53": TWO_POW_53,
            "f64_wall": 38,
            "two_pow_53_crossing": 39,
            "i128_max_n": 92,
        },
        "passed": passed,
        "total": total,
    }
    stable = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(stable.encode("utf-8")).hexdigest()

    # the clock and the environment are PEERS of the hash, never inside it
    cert = {
        "payload": payload,
        "sha256": digest,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {"python": sys.version.split()[0], "platform": sys.platform},
    }

    if failed:
        print("REFUSING TO EMIT a certificate: %d invariant(s) disagree." % len(failed))
        print("A cert that covers a failure is a screenshot, not a proof.")
        return 1

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / "rustium_certificate.json"
    dest.write_text(json.dumps(cert, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    print("math sha256 : %s" % digest)
    print("wrote       : %s" % dest)
    print("Run twice -- the sha256 must not move. Hash the math, not the moment.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
archive_examples.py -- give every example render a run number and a trace.

THE RULE (Vlad): every run, every permutation must be clean and have a trace.

`cargo run --example X` writes its PNG into the CURRENT DIRECTORY, so seven
renders had piled up loose in the crate root -- 101 MB, ignored by /*.png but
NOT traced. Ignored is not the same as accounted for. This sweeps them into
runs/examples_NNNN/ and writes the MANIFEST mirror the house already uses
(Curse 31: payload local, steps tracked).

THE SIZE RECEIPT. raster.rs encodes with STORED deflate -- no compression --
so a PNG's byte count is a pure function of its dimensions:

    bytes = (w*3 + 1)*h  +  ceil(raw/65535)*5  +  2 + 4  +  57

Verified on all seven, exact. That is why dashboard_skeleton_4k.png and
orb_growth.png weigh the same to the byte while differing in content: both
are 3840x2160. The manifest records predicted AND actual so a future render
that disagrees is a broken encoder, caught by arithmetic instead of by eye.

    py -3 archive_examples.py            # sweep + manifest
    py -3 archive_examples.py --verify   # re-check an existing archive
"""
import glob
import hashlib
import json
import os
import struct
import sys
import time

RUNS = "runs"
# which example produced which file -- stated, not guessed
SOURCE = {
    "dashboard_skeleton.png": "cargo run --example paint_dashboard",
    "dashboard_skeleton_4k.png": "cargo run --example paint_dashboard",
    "float_wall.png": "cargo run --example float_wall",
    "float_wall_4k.png": "cargo run --example float_wall",
    "gate_cascade.png": "cargo run --example gate_cascade",
    "gate_cascade_4k.png": "cargo run --example gate_cascade",
    "orb_growth.png": "cargo run --example orb_growth",
}


def png_dims(path):
    b = open(path, "rb").read(33)
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", b[16:24])
    return w, h, b[24], b[25]


def predict(w, h):
    raw = (w * 3 + 1) * h
    return raw + ((raw + 65534) // 65535) * 5 + 2 + 4 + 57


def entry(path):
    w, h, depth, ctype = png_dims(path)
    raw = open(path, "rb").read()
    actual, pred = len(raw), predict(w, h)
    return {
        "file": os.path.basename(path),
        "source": SOURCE.get(os.path.basename(path), "UNKNOWN -- not in SOURCE map"),
        "canvas": [w, h], "bit_depth": depth, "colour_type": ctype,
        "bytes": actual, "bytes_predicted": pred, "size_matches_formula": actual == pred,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def verify(d):
    man = json.load(open(os.path.join(d, "MANIFEST.json"), encoding="utf-8"))
    bad = 0
    for e in man["renders"]:
        p = os.path.join(d, e["file"])
        if not os.path.exists(p):
            print("  MISSING  %s" % e["file"]); bad += 1; continue
        raw = open(p, "rb").read()
        ok = hashlib.sha256(raw).hexdigest() == e["sha256"]
        print("  %-8s %s" % ("OK" if ok else "CORRUPT", e["file"]))
        bad += 0 if ok else 1
    print("  %d render(s), %d bad" % (len(man["renders"]), bad))
    return bad


if __name__ == "__main__":
    if "--verify" in sys.argv:
        ds = sorted(glob.glob(os.path.join(RUNS, "examples_*")))
        sys.exit(1 if not ds else verify(ds[-1]))

    strays = sorted(f for f in glob.glob("*.png") if os.path.isfile(f))
    if not strays:
        print("  no loose renders in the crate root -- nothing to sweep")
        sys.exit(0)

    n = 1 + len(glob.glob(os.path.join(RUNS, "examples_*")))
    out = os.path.join(RUNS, "examples_%04d" % n)
    os.makedirs(out, exist_ok=True)

    renders, total, unknown = [], 0, 0
    for f in strays:
        e = entry(f)
        if e["source"].startswith("UNKNOWN"):
            unknown += 1
        if not e["size_matches_formula"]:
            print("  WARN %s: %d B but the stored-deflate formula says %d"
                  % (e["file"], e["bytes"], e["bytes_predicted"]))
        renders.append(e); total += e["bytes"]
        os.replace(f, os.path.join(out, f))
        print("  swept %-28s %11s B  %s  %s"
              % (e["file"], "{:,}".format(e["bytes"]), e["sha256"][:16],
                 "size OK" if e["size_matches_formula"] else "SIZE MISMATCH"))

    man = {
        "archive": os.path.basename(out),
        "swept_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "why": "cargo run --example writes to CWD; these accumulated loose in the "
               "crate root. Ignored by /*.png but not traced -- ignored is not "
               "accounted for.",
        "encoder": "raster.rs zlib_stored (no compression): "
                   "bytes = (w*3+1)*h + ceil(raw/65535)*5 + 6 + 57, exact",
        "renders": renders,
        "total_bytes": total,
        "unknown_source": unknown,
        "note": "payload is local and gitignored; this manifest is the mirror",
    }
    json.dump(man, open(os.path.join(out, "MANIFEST.json"), "w", encoding="utf-8"),
              indent=1)
    print("  -> %s   %d render(s), %s B, %d unknown source"
          % (out, len(renders), "{:,}".format(total), unknown))

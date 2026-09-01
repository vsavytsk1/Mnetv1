#!/usr/bin/env python3
"""
build_tower.py -- the physics vector-space tower builder.
KERNELIC_MAGIC compliant: ASCII-only source, no deps, one job.

The idea (Vlad): every known physics/eng formula is a POINT in a LaTeX vector
space; its derivation/prerequisite links are EDGES (graph math to all the
interconnections). We keep the dataset as a small queryable JSON and grow it
formula by formula (highschool -> QCD). This builder:

  1. loads tower/dataset/physics_vectorspace_vX.Y.json,
  2. VALIDATES the graph (every edge points to a real node; no orphans; the
     status/domain grammar is respected) -- so the vector space stays consistent
     as it grows,
  3. prints the adjacency (who connects to whom) and per-domain / per-status
     tallies -- the query surface we consult while building.

Run:
    py -3 build_tower.py            # validate + human report
    py -3 build_tower.py --json     # machine dump of the validated graph
    py -3 build_tower.py --query phi   # nodes/edges touching a keyword

Rule: fix the dataset, re-run. The builder is the oracle; if the graph is
inconsistent it says so and refuses to bless it. spini. P=12. chi=2.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DATASET_DIR = ROOT / "dataset"


def latest_dataset():
    files = sorted(DATASET_DIR.glob("physics_vectorspace_v*.json"))
    if not files:
        raise SystemExit("no dataset found in " + str(DATASET_DIR))
    return files[-1]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(data):
    """Return (ok, problems[]). The graph is valid when every edge target
    exists, every node has a known domain + status, and ids are unique."""
    problems = []
    nodes = data.get("nodes", [])
    ids = [n["id"] for n in nodes]
    idset = set(ids)
    domains = set(data.get("domains", {}).keys())
    grammar = set(data.get("status_grammar", []))

    # unique ids
    if len(ids) != len(idset):
        seen, dup = set(), set()
        for i in ids:
            if i in seen:
                dup.add(i)
            seen.add(i)
        problems.append("duplicate ids: " + ", ".join(sorted(dup)))

    for n in nodes:
        nid = n.get("id", "<no id>")
        if n.get("domain") not in domains:
            problems.append(nid + ": unknown domain '" + str(n.get("domain")) + "'")
        if n.get("status") not in grammar:
            problems.append(nid + ": status '" + str(n.get("status")) + "' not in grammar")
        if not n.get("latex"):
            problems.append(nid + ": missing latex")
        for tgt in n.get("connects", []):
            if tgt not in idset:
                problems.append(nid + ": edge -> '" + tgt + "' has no such node")
    return (len(problems) == 0, problems)


def report(data):
    nodes = data["nodes"]
    idmap = {n["id"]: n for n in nodes}
    print("PHYSICS VECTOR SPACE  " + data["schema"] + "  v" + data["version"])
    print("  source: " + data.get("source", "?"))
    print("  nodes: %d   edges: %d" % (
        len(nodes), sum(len(n.get("connects", [])) for n in nodes)))

    # per-domain / per-status tallies (the query surface)
    dom, sta = {}, {}
    for n in nodes:
        dom[n["domain"]] = dom.get(n["domain"], 0) + 1
        sta[n["status"]] = sta.get(n["status"], 0) + 1
    print("  by domain: " + ", ".join("%s=%d" % (k, v) for k, v in sorted(dom.items())))
    print("  by status: " + ", ".join("%s=%d" % (k, v) for k, v in sorted(sta.items())))

    # in-degree (what depends on each node) -- the interconnection map
    indeg = {n["id"]: 0 for n in nodes}
    for n in nodes:
        for t in n.get("connects", []):
            indeg[t] = indeg.get(t, 0) + 1

    print("\nTHE GRAPH (each node -> what it enables):")
    for n in nodes:
        arrows = " -> " + ", ".join(n.get("connects", [])) if n.get("connects") else "  (leaf)"
        print("  [%-9s] %-11s %s%s" % (n["status"], n["domain"], n["id"], arrows))

    roots = [i for i, d in indeg.items() if d == 0]
    leaves = [n["id"] for n in nodes if not n.get("connects")]
    print("\n  roots (nothing points to them): " + ", ".join(roots))
    print("  leaves (point to nothing):      " + ", ".join(leaves))


def query(data, kw):
    kw = kw.lower()
    for n in data["nodes"]:
        blob = (n["id"] + " " + n.get("title", "") + " " + n.get("latex", "") +
                " " + n.get("note", "")).lower()
        if kw in blob:
            print("  " + n["id"] + "  (" + n["domain"] + "/" + n["status"] + ")")
            print("     " + n.get("title", ""))
            print("     latex: " + n["latex"])
            if n.get("connects"):
                print("     -> " + ", ".join(n["connects"]))


def main():
    path = latest_dataset()
    data = load(path)
    ok, problems = validate(data)
    if "--json" in sys.argv:
        print(json.dumps({"valid": ok, "problems": problems, "data": data},
                         indent=2))
        return
    if "--query" in sys.argv:
        i = sys.argv.index("--query")
        kw = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        print("QUERY '" + kw + "':")
        query(data, kw)
        return
    print("dataset: " + path.name)
    report(data)
    print("\nVALIDATION: " + ("OK -- the vector space is consistent." if ok
                              else "FAILED:"))
    for p in problems:
        print("  ! " + p)
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

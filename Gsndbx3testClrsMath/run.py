"""
MachineNet Graph Sandbox — Command Runner
==========================================
Drives graph_sandbox v3.2+ from Python via console commands.

USAGE:
  python run.py                     # opens sandbox, prints usage
  python run.py --demo              # runs demo sequence
  python run.py --bench             # benchmarks face walker vs shapes
  python run.py --cmd "HEX"         # single command
  python run.py --batch "HEX,FRACTALIZE,FRACTALIZE,GRAB"

CONSOLE API (paste in browser DevTools F12 > Console):
  cmd('HEX')                        → generates hexagon, returns {ok, time_ms, nodes, edges}
  cmd('FRACTALIZE')                 → subdivides active graph
  batch(['HEX','FRACTALIZE','FRACTALIZE','GRAB'])  → chain, returns timing
  state()                           → full state dump

COMMANDS:
  Graph:    A, B
  Tools:    NODE, EDGE, MOVE, GRAB, DELETE
  Shapes:   PENT, HEX, C60, POLY 7, POLY 12, RANDOM
  Math:     ALGEBRA, MANDELBROT
  Ops:      FRACTALIZE, MOBIUSIFY, UNION, INTERSECT, PRODUCT, DIFF, ITERATE
  Util:     CLEAR, RESET, PLANE, SNAP
"""

import sys
import os
import json
import time
import webbrowser
import subprocess
from pathlib import Path

SANDBOX_PATH = Path(__file__).parent / "v3_2_cmd.html"

# ═══════════════════════════════════════════════════════
# DEMO SEQUENCES — paste these into DevTools console
# ═══════════════════════════════════════════════════════

DEMO_SEQUENCES = {
    "hex_fractal": [
        "// Hexagon → fractalize 3x → grab to see film",
        "batch(['A','HEX','FRACTALIZE','FRACTALIZE','FRACTALIZE','GRAB'])",
    ],
    "dual_shapes": [
        "// Pentagon in A, Hexagon in B, union them",
        "cmd('A'); cmd('PENT'); cmd('B'); cmd('HEX'); cmd('UNION')",
    ],
    "growth_test": [
        "// Measure fractalization growth",
        "cmd('A'); cmd('HEX')",
        "for(var i=0;i<5;i++) cmd('FRACTALIZE')",
        "state()",
    ],
    "face_bench": [
        "// Benchmark face walker on progressively larger graphs",
        "cmd('A'); cmd('HEX');",
        "var r=[];",
        "for(var i=0;i<4;i++){",
        "  var t0=performance.now();",
        "  var f=findFaces(graphs[activeGraph||'A']);",
        "  var dt=performance.now()-t0;",
        "  r.push({iter:i, faces:f.length, nodes:graphs.A.nodes.length, edges:graphs.A.edges.length, face_ms:dt.toFixed(3)});",
        "  cmd('FRACTALIZE');",
        "}",
        "console.table(r);",
    ],
    "ab_compare": [
        "// Build A and B, compare face counts",
        "cmd('A'); cmd('PENT'); cmd('FRACTALIZE'); cmd('FRACTALIZE');",
        "cmd('B'); cmd('HEX'); cmd('FRACTALIZE'); cmd('FRACTALIZE');",
        "var fA=findFaces(graphs.A), fB=findFaces(graphs.B);",
        "console.log('A faces:', fA.length, '| B faces:', fB.length);",
    ],
}


def print_banner():
    print("""
╔══════════════════════════════════════════════════╗
║  MachineNet · Graph Sandbox v3.2 Command Runner  ║
║  Face Walker + Centroid Fan Comparison Test       ║
╚══════════════════════════════════════════════════╝
""")


def open_sandbox():
    """Open the sandbox HTML in default browser."""
    url = SANDBOX_PATH.resolve().as_uri()
    print(f"Opening: {url}")
    webbrowser.open(url)
    print("\n→ Press F12 in browser to open DevTools Console")
    print("→ Paste commands from below:\n")


def print_sequences():
    """Print all demo sequences for copy-paste."""
    for name, lines in DEMO_SEQUENCES.items():
        print(f"═══ {name} ═══")
        for line in lines:
            print(f"  {line}")
        print()


def print_single_cmd(c):
    """Print a command ready for console paste."""
    print(f"\n→ Paste in DevTools Console:")
    print(f"  cmd('{c}')")


def print_batch(cmds_str):
    """Print a batch command ready for console paste."""
    cmds = [c.strip() for c in cmds_str.split(',')]
    arr = json.dumps(cmds)
    print(f"\n→ Paste in DevTools Console:")
    print(f"  batch({arr})")


def run_bench_sequence():
    """Print the face walker benchmark sequence."""
    print("\n═══ FACE WALKER BENCHMARK ═══")
    print("Paste this block into DevTools Console:\n")
    print("(function(){")
    print("  var shapes = ['PENT','HEX','C60'];")
    print("  var results = [];")
    print("  shapes.forEach(function(s){")
    print("    cmd('A'); cmd('CLEAR'); cmd(s);")
    print("    for(var i=0; i<4; i++){")
    print("      var g = graphs.A;")
    print("      var t0 = performance.now();")
    print("      var faces = findFaces(g);")
    print("      var dt = performance.now() - t0;")
    print("      results.push({")
    print("        shape: s, iter: i,")
    print("        nodes: g.nodes.length,")
    print("        edges: g.edges.length,")
    print("        faces: faces.length,")
    print("        walk_ms: parseFloat(dt.toFixed(3)),")
    print("        rebuild: cmd('FRACTALIZE').time_ms")
    print("      });")
    print("    }")
    print("  });")
    print("  console.table(results);")
    print("  return results;")
    print("})()")
    print()


def main():
    print_banner()

    args = sys.argv[1:]

    if '--bench' in args:
        open_sandbox()
        run_bench_sequence()
    elif '--demo' in args:
        open_sandbox()
        print_sequences()
    elif '--cmd' in args:
        idx = args.index('--cmd')
        if idx + 1 < len(args):
            open_sandbox()
            print_single_cmd(args[idx + 1])
        else:
            print("Usage: python run.py --cmd \"HEX\"")
    elif '--batch' in args:
        idx = args.index('--batch')
        if idx + 1 < len(args):
            open_sandbox()
            print_batch(args[idx + 1])
        else:
            print("Usage: python run.py --batch \"HEX,FRACTALIZE,FRACTALIZE\"")
    else:
        open_sandbox()
        print("QUICK START — paste any of these in DevTools Console (F12):\n")
        print("  cmd('HEX')                                    // make hexagon")
        print("  cmd('FRACTALIZE')                              // subdivide")
        print("  cmd('GRAB')                                    // highlight + film")
        print("  batch(['HEX','FRACTALIZE','FRACTALIZE','GRAB']) // chain")
        print("  state()                                        // dump state")
        print()
        print("  python run.py --demo     # all demo sequences")
        print("  python run.py --bench    # face walker benchmark")
        print("  python run.py --cmd HEX  # single command")
        print()


if __name__ == '__main__':
    main()

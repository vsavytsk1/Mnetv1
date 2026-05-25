"""
MachineNet Graph Sandbox — LIVE DRIVER
=======================================
Opens the sandbox in a window, executes commands from Python,
prints results to terminal. You see the render change in real time.

USAGE:
  python drive.py                          # interactive REPL
  python drive.py --seq HEX,FRACTALIZE,FRACTALIZE,GRAB
  python drive.py --script demo.txt        # file with one cmd per line

REPL commands:
  > HEX                    → cmd('HEX')
  > FRACTALIZE             → cmd('FRACTALIZE') 
  > GRAB                   → shows film
  > batch HEX,FRAC,FRAC   → batch execution
  > state                  → dump state
  > quit                   → exit
"""

import sys
import os
import json
import time
import threading
from pathlib import Path

try:
    import webview
except ImportError:
    print("ERROR: pywebview not installed. Run: pip install pywebview")
    sys.exit(1)

SANDBOX = Path(__file__).parent / "v3_2_cmd.html"
window = None
ready = threading.Event()


def on_loaded():
    """Called when the webview page finishes loading."""
    ready.set()


def js(code):
    """Execute JS in the sandbox and return parsed result."""
    if not window:
        return None
    raw = window.evaluate_js(code)
    return raw


def send_cmd(c):
    """Send a single command, print result."""
    result = js(f"JSON.stringify(cmd('{c}'))")
    if result:
        try:
            d = json.loads(result)
            graph = d.get('graph', '?')
            nodes = d.get('nodes', 0)
            edges = d.get('edges', 0)
            t = d.get('time_ms', 0)
            faces = d.get('faces', '?')
            print(f"  [{graph}] {c:16s} → {nodes:>6} nodes, {edges:>6} edges  |  {t:>8.3f}ms  |  film: {faces}")
            return d
        except:
            print(f"  {c} → {result}")
    return result


def send_batch(cmds):
    """Send a batch of commands."""
    arr = json.dumps(cmds)
    result = js(f"JSON.stringify(batch({arr}))")
    if result:
        try:
            d = json.loads(result)
            total = d.get('total_ms', 0)
            print(f"\n  BATCH ({len(cmds)} cmds) total: {total:.3f}ms")
            for r in d.get('results', []):
                c = r.get('cmd', '?')
                nodes = r.get('nodes', 0)
                edges = r.get('edges', 0)
                t = r.get('time_ms', 0)
                print(f"    {c:16s} → {nodes:>6} nodes, {edges:>6} edges  |  {t:>8.3f}ms")
            print()
            return d
        except:
            print(f"  batch → {result}")
    return result


def get_state():
    """Get and print current state."""
    result = js("JSON.stringify(state())")
    if result:
        try:
            d = json.loads(result)
            print(f"\n  ═══ STATE ═══")
            print(f"  Version:  {d.get('version')}")
            print(f"  Graph:    {d.get('activeGraph')}  Tool: {d.get('activeTool')}  Grab: {d.get('grabActive')}")
            a = d.get('A', {})
            b = d.get('B', {})
            r = d.get('R', {})
            print(f"  A: {a.get('nodes',0)} nodes, {a.get('edges',0)} edges")
            print(f"  B: {b.get('nodes',0)} nodes, {b.get('edges',0)} edges")
            print(f"  R: {r.get('nodes',0)} nodes, {r.get('edges',0)} edges")
            cam = d.get('camera', {})
            print(f"  Camera: ({cam.get('x',0)}, {cam.get('y',0)}, {cam.get('z',0)})")
            print(f"  Snapshots: {d.get('snapshots',0)}")
            print()
            return d
        except:
            print(f"  state → {result}")
    return result


def run_sequence(seq_str):
    """Run a comma-separated sequence with 500ms delay between each."""
    cmds = [c.strip() for c in seq_str.split(',') if c.strip()]
    print(f"\n╔═══ SEQUENCE: {len(cmds)} commands ═══╗")
    print(f"║ {seq_str}")
    print(f"╚{'═'*40}╝\n")
    for i, c in enumerate(cmds):
        print(f"  [{i+1}/{len(cmds)}]", end=" ")
        send_cmd(c)
        time.sleep(0.5)  # let the render breathe
    print("\n  ✓ Sequence complete.\n")
    get_state()


def run_script(filepath):
    """Run commands from a text file (one per line, # = comment)."""
    p = Path(filepath)
    if not p.exists():
        print(f"ERROR: File not found: {filepath}")
        return
    lines = p.read_text().strip().split('\n')
    cmds = [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]
    print(f"\n═══ SCRIPT: {filepath} ({len(cmds)} commands) ═══\n")
    for i, c in enumerate(cmds):
        print(f"  [{i+1}/{len(cmds)}]", end=" ")
        if c.lower().startswith('wait'):
            # wait 2000  → sleep 2 seconds
            try:
                ms = int(c.split()[1])
                print(f"  WAIT {ms}ms")
                time.sleep(ms / 1000)
            except:
                time.sleep(1)
        elif c.lower() == 'state':
            get_state()
        else:
            send_cmd(c)
            time.sleep(0.4)
    print("\n  ✓ Script complete.\n")
    get_state()


def repl():
    """Interactive command REPL."""
    print("╔══════════════════════════════════════════╗")
    print("║  MachineNet Sandbox REPL                 ║")
    print("║  Type commands, see them render live.     ║")
    print("║  'quit' to exit, 'state' for dump         ║")
    print("╚══════════════════════════════════════════╝\n")

    while True:
        try:
            line = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Bye.")
            break

        if not line:
            continue
        if line.lower() in ('quit', 'exit', 'q'):
            break
        if line.lower() == 'state':
            get_state()
            continue
        if line.lower().startswith('batch '):
            cmds = [c.strip() for c in line[6:].split(',') if c.strip()]
            send_batch(cmds)
            continue
        if line.lower().startswith('seq '):
            run_sequence(line[4:])
            continue
        if line.lower().startswith('wait'):
            try:
                ms = int(line.split()[1])
                print(f"  waiting {ms}ms...")
                time.sleep(ms / 1000)
            except:
                time.sleep(1)
            continue

        # Single command
        send_cmd(line.upper())


def main_loop():
    """Runs in a thread after webview loads."""
    ready.wait(timeout=15)
    time.sleep(1)  # extra breath for Three.js init

    print("\n  ✓ Sandbox loaded. Three.js running.\n")

    args = sys.argv[1:]

    if '--seq' in args:
        idx = args.index('--seq')
        if idx + 1 < len(args):
            run_sequence(args[idx + 1])
    elif '--script' in args:
        idx = args.index('--script')
        if idx + 1 < len(args):
            run_script(args[idx + 1])
    else:
        # Interactive REPL
        repl()

    # Keep window open after sequence finishes
    print("  Window stays open. Close it to exit.")


def start():
    global window
    url = SANDBOX.resolve().as_uri()

    print(f"\n  Opening: {SANDBOX.name}")
    print(f"  Waiting for Three.js boot...\n")

    # Start REPL/sequence thread
    t = threading.Thread(target=main_loop, daemon=True)
    t.start()

    # Create webview window (blocks until closed)
    window = webview.create_window(
        'MachineNet · Graph Sandbox v3.2',
        url=url,
        width=1200,
        height=700,
        resizable=True,
        text_select=True,
    )
    webview.start(on_loaded, debug=False)


if __name__ == '__main__':
    start()

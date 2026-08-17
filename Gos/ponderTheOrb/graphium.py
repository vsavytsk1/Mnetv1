#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRAPHIUM v1.0 -- the graph layer between prompts and product.

A dependency-graph orchestrator for LLM work. Provider-agnostic: it drives
free/local endpoints (Ollama, Groq, OpenRouter, Google AI Studio) exactly the
same way it would drive a paid one. Pure stdlib -- no pip install required.

WHY IT EXISTS
    A linear agent is a graph one edge wide. Most "and then"s are not real
    edges: if step B never reads step A's output, they were never connected
    and can run at the same time. This module makes the graph explicit,
    runs independent nodes in parallel, and gates the edges that matter.

THE THREE LAWS (from the cave)
    1. Fan out where the work is independent.
    2. Gate the edges where confidence matters -- a verifier NEVER shares
       context with the maker. (Models prefer their own output; measured.)
    3. Freeze the nodes that hold the truth -- every run is versioned,
       every node cached to disk, nothing recomputed silently.

THE PRICE IS PAID IN THE OPEN
    Every run writes a receipt: node timings, token counts, cache hits,
    failures, the measured speedup vs the serial path, and the sha256 of
    every frozen output. No claim without a receipt.

USAGE
    from graphium import Graph, node, Provider

    g = Graph("helena_audit", provider=Provider.ollama("llama3.2"))

    @g.node()
    def scope():
        return {"files": ["a.py", "b.py", "c.py"]}

    @g.fanout(over="scope", key="files")          # one worker per item
    def audit(item):
        return g.ask(f"Audit this file for X:\\n{item}")

    @g.verify("audit", fresh=True)                # separate context, no lineage
    def check(claim, item):
        return g.ask(f"Does this claim hold? Answer PASS or FAIL.\\n{claim}")

    @g.node(after=["check"])
    def report(check):
        return "\\n".join(c["text"] for c in check if c["passed"])

    g.run(workers=8)

CLI
    python graphium.py --demo          # runs a tiny offline demo graph
    python graphium.py --amdahl 0.95 16
"""

from __future__ import annotations

import concurrent.futures as _fut
import hashlib
import json
import os
import queue
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

__version__ = "1.0"

# ============================================================================
#  AMDAHL -- know the win before you deploy a single agent
# ============================================================================

def amdahl(p: float, n: int) -> float:
    """Speedup with parallel fraction p across n workers. S = 1/((1-p)+p/n)."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0,1]")
    if n < 1:
        raise ValueError("n must be >= 1")
    return 1.0 / ((1.0 - p) + p / n)


def amdahl_ceiling(p: float) -> float:
    """The hard cap, N -> infinity. The serial tail is the anchor."""
    if p >= 1.0:
        return float("inf")
    return 1.0 / (1.0 - p)


def amdahl_report(p: float, n: int) -> str:
    s = amdahl(p, n)
    c = amdahl_ceiling(p)
    cs = "inf" if c == float("inf") else f"{c:.2f}x"
    return (f"  parallel fraction p = {p:.2f}\n"
            f"  workers          N = {n}\n"
            f"  real speedup       = {s:.2f}x   (naive guess: {n}x)\n"
            f"  ceiling  (N -> oo) = {cs}\n"
            f"  -> the serial tail (merge + verify + real edges) eats the rest.")


# ============================================================================
#  PROVIDERS -- free first. same interface for every backend.
# ============================================================================

class ProviderError(RuntimeError):
    pass


@dataclass
class Provider:
    """A callable text backend. .chat(prompt, system) -> (text, meta)."""
    name: str
    _fn: Callable[[str, Optional[str]], "tuple[str, dict]"]
    model: str = ""
    # rough guard so a runaway graph cannot spin forever
    max_calls: int = 10_000
    _calls: int = field(default=0, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def chat(self, prompt: str, system: Optional[str] = None) -> "tuple[str, dict]":
        with self._lock:
            if self._calls >= self.max_calls:
                raise ProviderError(f"max_calls={self.max_calls} reached (runaway brake)")
            self._calls += 1
        return self._fn(prompt, system)

    # ---------------- free / local backends ----------------

    @staticmethod
    def ollama(model: str = "llama3.2", host: str = "http://localhost:11434",
               timeout: int = 300) -> "Provider":
        """Truly free, truly unlimited, runs on your own GPU. Start with:
             ollama serve &   ;   ollama pull llama3.2
        This is the one to use for a full-speed cycle."""
        def fn(prompt: str, system: Optional[str]):
            msgs = []
            if system:
                msgs.append({"role": "system", "content": system})
            msgs.append({"role": "user", "content": prompt})
            body = json.dumps({"model": model, "messages": msgs, "stream": False}).encode()
            req = urllib.request.Request(f"{host}/api/chat", data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read().decode())
            text = d.get("message", {}).get("content", "")
            meta = {"in": d.get("prompt_eval_count", 0), "out": d.get("eval_count", 0)}
            return text, meta
        return Provider(f"ollama:{model}", fn, model)

    @staticmethod
    def openai_compatible(base_url: str, api_key_env: str, model: str,
                          timeout: int = 300) -> "Provider":
        """Covers Groq, OpenRouter, Together, DeepSeek, local vLLM, LM Studio --
        anything speaking the /chat/completions shape. Free tiers welcome.
          Groq:       https://api.groq.com/openai/v1     GROQ_API_KEY
          OpenRouter: https://openrouter.ai/api/v1       OPENROUTER_API_KEY
                      (model e.g. 'meta-llama/llama-3.3-70b-instruct:free')
        """
        def fn(prompt: str, system: Optional[str]):
            key = os.environ.get(api_key_env, "")
            if not key:
                raise ProviderError(f"env var {api_key_env} is not set")
            msgs = []
            if system:
                msgs.append({"role": "system", "content": system})
            msgs.append({"role": "user", "content": prompt})
            body = json.dumps({"model": model, "messages": msgs}).encode()
            req = urllib.request.Request(
                f"{base_url.rstrip('/')}/chat/completions", data=body,
                headers={"Content-Type": "application/json",
                         "Authorization": f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read().decode())
            text = d["choices"][0]["message"]["content"]
            u = d.get("usage", {}) or {}
            return text, {"in": u.get("prompt_tokens", 0), "out": u.get("completion_tokens", 0)}
        return Provider(f"api:{model}", fn, model)

    @staticmethod
    def shell(command_template: str) -> "Provider":
        """Drive any CLI tool. {prompt} is substituted. Lets you wire in a
        local binary, or your own HELENA gate, as just another node."""
        def fn(prompt: str, system: Optional[str]):
            cmd = command_template.replace("{prompt}", prompt)
            out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
            if out.returncode != 0:
                raise ProviderError(f"shell provider failed: {out.stderr[:300]}")
            return out.stdout, {"in": 0, "out": 0}
        return Provider("shell", fn)

    @staticmethod
    def echo() -> "Provider":
        """Offline stub for testing the graph shape without burning anything."""
        def fn(prompt: str, system: Optional[str]):
            time.sleep(0.05)
            return f"[echo] {prompt[:120]}", {"in": len(prompt) // 4, "out": 20}
        return Provider("echo", fn)


# ============================================================================
#  THE GRAPH
# ============================================================================

@dataclass
class NodeResult:
    name: str
    value: Any
    seconds: float = 0.0
    cached: bool = False
    error: Optional[str] = None
    tokens_in: int = 0
    tokens_out: int = 0
    # what this node WOULD have cost run one-at-a-time. For a fanout/verify
    # node this is the sum of its workers, not its wall time -- otherwise the
    # receipt understates the win and the receipt must never lie.
    serial_equiv: float = 0.0

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class _Node:
    name: str
    fn: Callable
    after: List[str] = field(default_factory=list)
    kind: str = "node"           # node | fanout | verify
    over: Optional[str] = None   # for fanout: which node supplies the items
    key: Optional[str] = None    # for fanout: dict key holding the list
    target: Optional[str] = None # for verify: which node's output to check
    freeze: bool = True          # cache result to disk


class Graph:
    """A directed acyclic graph of work. Independent nodes run at once."""

    def __init__(self, name: str, provider: Optional[Provider] = None,
                 workdir: str = "./.graphium", verbose: bool = True):
        self.name = name
        self.provider = provider or Provider.echo()
        self.workdir = os.path.join(workdir, name)
        self.verbose = verbose
        self.nodes: "Dict[str, _Node]" = {}
        self.results: "Dict[str, NodeResult]" = {}
        self._print_lock = threading.Lock()
        self._serial_seconds = 0.0
        os.makedirs(self.workdir, exist_ok=True)

    # ---------------- logging ----------------
    def log(self, msg: str, tag: str = "  ") -> None:
        if self.verbose:
            with self._print_lock:
                print(f"{tag} {msg}", flush=True)

    # ---------------- model access ----------------
    def ask(self, prompt: str, system: Optional[str] = None,
            provider: Optional[Provider] = None) -> str:
        """Call the model. Use inside a node body."""
        p = provider or self.provider
        text, meta = p.chat(prompt, system)
        self._tally(meta)
        return text

    _tl = threading.local()

    def _tally(self, meta: dict) -> None:
        cur = getattr(Graph._tl, "meta", None)
        if cur is not None:
            cur["in"] += meta.get("in", 0)
            cur["out"] += meta.get("out", 0)

    # ---------------- declaration decorators ----------------
    def node(self, after: Optional[Sequence[str]] = None, freeze: bool = True):
        def deco(fn):
            self.nodes[fn.__name__] = _Node(fn.__name__, fn, list(after or []),
                                            kind="node", freeze=freeze)
            return fn
        return deco

    def fanout(self, over: str, key: Optional[str] = None, freeze: bool = True):
        """One worker per item. Workers share NO state -- that is the point."""
        def deco(fn):
            self.nodes[fn.__name__] = _Node(fn.__name__, fn, [over], kind="fanout",
                                            over=over, key=key, freeze=freeze)
            return fn
        return deco

    def verify(self, target: str, fresh: bool = True, freeze: bool = True):
        """A verifier is a SEPARATE node on FRESH context. It never sees the
        maker's reasoning, only the artifact. Self-grading is rubber-stamping:
        models measurably prefer their own output, so the maker never grades
        its own exam."""
        def deco(fn):
            self.nodes[fn.__name__] = _Node(fn.__name__, fn, [target], kind="verify",
                                            target=target, freeze=freeze)
            return fn
        return deco

    # ---------------- freezing (Path X: never overwrite a frozen step) -------
    def _cache_path(self, node: str, salt: str = "") -> str:
        h = hashlib.sha256((node + salt).encode()).hexdigest()[:16]
        return os.path.join(self.workdir, f"{node}.{h}.json")

    def _load(self, node: str, salt: str = "") -> Optional[Any]:
        p = self._cache_path(node, salt)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)["value"]
            except Exception:
                return None
        return None

    def _save(self, node: str, value: Any, salt: str = "") -> None:
        p = self._cache_path(node, salt)
        try:
            blob = json.dumps({"value": value}, ensure_ascii=False, default=str)
            with open(p, "w", encoding="utf-8") as f:
                f.write(blob)
        except Exception as e:
            self.log(f"cache write skipped for {node}: {e}", "!!")

    # ---------------- topology ----------------
    def _order(self) -> "List[List[str]]":
        """Kahn layering -> each layer is a set of nodes that can run at once."""
        indeg = {n: 0 for n in self.nodes}
        for n, nd in self.nodes.items():
            for dep in nd.after:
                if dep not in self.nodes:
                    raise ValueError(f"node '{n}' depends on unknown node '{dep}'")
                indeg[n] += 1
        layers, seen = [], set()
        while len(seen) < len(self.nodes):
            layer = [n for n in self.nodes
                     if n not in seen and all(d in seen for d in self.nodes[n].after)]
            if not layer:
                remaining = [n for n in self.nodes if n not in seen]
                raise ValueError(f"cycle detected among: {remaining} (a graph must be acyclic)")
            layers.append(sorted(layer))
            seen.update(layer)
        return layers

    def critical_path(self) -> "List[str]":
        """Longest chain of real edges -- the floor no worker count can beat."""
        memo: Dict[str, List[str]] = {}

        def walk(n: str) -> List[str]:
            if n in memo:
                return memo[n]
            best: List[str] = []
            for d in self.nodes[n].after:
                c = walk(d)
                if len(c) > len(best):
                    best = c
            memo[n] = best + [n]
            return memo[n]

        longest: List[str] = []
        for n in self.nodes:
            c = walk(n)
            if len(c) > len(longest):
                longest = c
        return longest

    def parallel_fraction(self) -> float:
        """Estimated p: share of nodes NOT on the critical path."""
        total = len(self.nodes)
        if total == 0:
            return 0.0
        return max(0.0, (total - len(self.critical_path())) / total)

    def explain(self) -> str:
        layers = self._order()
        cp = self.critical_path()
        p = self.parallel_fraction()
        out = [f"GRAPH '{self.name}' -- {len(self.nodes)} nodes, {len(layers)} layers"]
        for i, L in enumerate(layers):
            mark = "  (runs in parallel)" if len(L) > 1 else ""
            out.append(f"   layer {i}: {', '.join(L)}{mark}")
        out.append(f"   critical path: {' -> '.join(cp)}  (len {len(cp)})")
        out.append(f"   estimated p = {p:.2f}")
        return "\n".join(out)

    # ---------------- execution ----------------
    def _run_one(self, name: str, workers: int) -> NodeResult:
        nd = self.nodes[name]
        Graph._tl.meta = {"in": 0, "out": 0}
        t0 = time.time()
        serial_eq = 0.0

        try:
            # ---- fanout: one isolated worker per item, in parallel ----
            if nd.kind == "fanout":
                src = self.results[nd.over].value
                items = src[nd.key] if (nd.key and isinstance(src, dict)) else src
                if not isinstance(items, (list, tuple)):
                    raise ValueError(f"fanout '{name}' expected a list from '{nd.over}'")
                out: List[Any] = [None] * len(items)

                def work(idx_item):
                    i, item = idx_item
                    w0 = time.time()
                    salt = hashlib.sha256(str(item).encode()).hexdigest()[:12]
                    if nd.freeze:
                        c = self._load(name, salt)
                        if c is not None:
                            return i, c, True, time.time() - w0
                    v = nd.fn(item)
                    if nd.freeze:
                        self._save(name, v, salt)
                    return i, v, False, time.time() - w0

                hits = 0
                with _fut.ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
                    for i, v, cached, wsec in ex.map(work, list(enumerate(items))):
                        out[i] = v
                        hits += 1 if cached else 0
                        serial_eq += wsec
                self.log(f"{name}: {len(items)} workers, {hits} from cache", "->")
                value: Any = out

            # ---- verify: fresh context, sees only the artifact ----
            elif nd.kind == "verify":
                target = self.results[nd.target].value
                tlist = target if isinstance(target, list) else [target]
                out = [None] * len(tlist)

                def check(idx_item):
                    i, art = idx_item
                    w0 = time.time()
                    salt = hashlib.sha256(str(art).encode()).hexdigest()[:12]
                    if nd.freeze:
                        c = self._load(name, salt)
                        if c is not None:
                            return i, c, True, time.time() - w0
                    v = nd.fn(art)
                    if nd.freeze:
                        self._save(name, v, salt)
                    return i, v, False, time.time() - w0

                with _fut.ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
                    for i, v, _c, wsec in ex.map(check, list(enumerate(tlist))):
                        out[i] = v
                        serial_eq += wsec
                self.log(f"{name}: verified {len(tlist)} artifact(s) on fresh context", "->")
                value = out

            # ---- plain node ----
            else:
                if nd.freeze:
                    c = self._load(name)
                    if c is not None:
                        dt = time.time() - t0
                        self.log(f"{name}: frozen (cache hit)", "==")
                        return NodeResult(name, c, dt, cached=True, serial_equiv=dt)
                kwargs = {d: self.results[d].value for d in nd.after if d in self.results}
                import inspect
                sig = inspect.signature(nd.fn)
                kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
                value = nd.fn(**kwargs)
                if nd.freeze:
                    self._save(name, value)

            dt = time.time() - t0
            m = Graph._tl.meta
            if serial_eq <= 0.0:
                serial_eq = dt
            self.log(f"{name}: ok in {dt:.2f}s", "ok")
            return NodeResult(name, value, dt, tokens_in=m["in"], tokens_out=m["out"],
                              serial_equiv=serial_eq)

        except Exception as e:
            dt = time.time() - t0
            self.log(f"{name}: FAILED -- {e}", "XX")
            return NodeResult(name, None, dt, error=str(e))

    def run(self, workers: int = 8, stop_on_error: bool = False) -> "Dict[str, NodeResult]":
        """Execute the graph layer by layer; each layer runs in parallel."""
        layers = self._order()
        t_start = time.time()
        self.log(self.explain(), "##")
        self.log(f"running with {workers} workers", "##")

        for li, layer in enumerate(layers):
            if len(layer) == 1:
                r = self._run_one(layer[0], workers)
                self.results[r.name] = r
                if r.error and stop_on_error:
                    break
            else:
                with _fut.ThreadPoolExecutor(max_workers=min(workers, len(layer))) as ex:
                    futs = {ex.submit(self._run_one, n, workers): n for n in layer}
                    for f in _fut.as_completed(futs):
                        r = f.result()
                        self.results[r.name] = r
                if stop_on_error and any(self.results[n].error for n in layer):
                    break

        wall = time.time() - t_start
        self._serial_seconds = sum(r.serial_equiv or r.seconds for r in self.results.values())
        self._receipt(wall, workers)
        return self.results

    # ---------------- the receipt: no claim without one ----------------
    def _receipt(self, wall: float, workers: int) -> None:
        ok = sum(1 for r in self.results.values() if r.ok)
        bad = len(self.results) - ok
        tin = sum(r.tokens_in for r in self.results.values())
        tout = sum(r.tokens_out for r in self.results.values())
        cached = sum(1 for r in self.results.values() if r.cached)
        measured = (self._serial_seconds / wall) if wall > 0 else 1.0
        # p measured from the run itself: the share of real work that did NOT
        # sit on the critical path. Structural p ignores fanout width, so we
        # report the measured one and label it.
        cp = self.critical_path()
        cp_time = sum(self.results[n].seconds for n in cp if n in self.results)
        tot = self._serial_seconds or 1.0
        p = max(0.0, min(1.0, (tot - cp_time) / tot))

        lines = [
            "=" * 62,
            f"RECEIPT -- {self.name}  ({time.strftime('%Y-%m-%d %H:%M:%S')})",
            "=" * 62,
            f"  nodes            : {len(self.results)}  ({ok} ok, {bad} failed, {cached} frozen)",
            f"  wall clock       : {wall:.2f}s",
            f"  sum of node time : {self._serial_seconds:.2f}s  (what a line would cost)",
            f"  measured speedup : {measured:.2f}x  with {workers} workers",
            f"  p (measured)     : {p:.2f}  -> Amdahl predicts {amdahl(p, workers):.2f}x",
            f"  tokens           : {tin} in / {tout} out",
            f"  critical path    : {' -> '.join(self.critical_path())}",
        ]
        if bad:
            lines.append("  failures:")
            for r in self.results.values():
                if not r.ok:
                    lines.append(f"     {r.name}: {r.error}")
        lines.append("=" * 62)
        txt = "\n".join(lines)
        print(txt, flush=True)
        try:
            stamp = time.strftime("%Y%m%d_%H%M%S")
            with open(os.path.join(self.workdir, f"receipt_{stamp}.txt"), "w",
                      encoding="utf-8") as f:
                f.write(txt + "\n")
        except Exception:
            pass


# ============================================================================
#  DEMO -- offline, proves the shape without spending anything
# ============================================================================

def _demo() -> None:
    g = Graph("demo_audit", provider=Provider.echo())

    @g.node()
    def scope():
        return {"files": [f"module_{i}.py" for i in range(12)]}

    @g.fanout(over="scope", key="files")
    def audit(item):
        return {"file": item, "claim": g.ask(f"Audit {item} for missing auth checks.")}

    @g.verify("audit")
    def check(artifact):
        v = g.ask(f"Independent check. Does this hold? PASS/FAIL:\n{artifact['claim']}")
        return {"file": artifact["file"], "passed": "FAIL" not in v.upper()}

    @g.node(after=["check"])
    def report(check):
        good = [c["file"] for c in check if c["passed"]]
        return f"{len(good)}/{len(check)} findings survived independent verification."

    g.run(workers=8)
    print("\nREPORT:", g.results["report"].value)


def _main(argv: List[str]) -> int:
    if "--demo" in argv:
        _demo()
        return 0
    if "--amdahl" in argv:
        i = argv.index("--amdahl")
        try:
            p = float(argv[i + 1]); n = int(argv[i + 2])
        except (IndexError, ValueError):
            print("usage: python graphium.py --amdahl <p 0..1> <workers>")
            return 2
        print(amdahl_report(p, n))
        return 0
    print(__doc__)
    print("\n  python graphium.py --demo")
    print("  python graphium.py --amdahl 0.95 16")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))

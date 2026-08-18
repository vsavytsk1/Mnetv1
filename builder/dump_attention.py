#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dump_attention.py -- one forward pass, and the only thing worth keeping.

WHY THIS IS SMALL. A transformer's attention matrix IS an adjacency matrix
(K1: "a transformer is already a graph, attention = weighted edge"). So there
is nothing to invent -- you run the model once, take attn[L][H][i][j], and
that is the graph. Everything else in the checkpoint is wiring; this is the
current.

WHAT IT WRITES  ->  shell/attentium_v0_1.html eats this directly

    { "model":     "the checkpoint name",
      "prompt":    "the text you ran",
      "tokens":    ["A", " fluffy", ...],
      "n_layers":  16,
      "n_heads":   32,
      "attn":      [L][H][i][j]        weight token i puts on token j
      "threshold": 0.01,               values below this were zeroed
      "synthetic": false }             <- the viewer trusts this field

CAUSALITY. attn[L][H][i][j] must be 0 for j > i. The viewer CHECKS this rather
than trusting it, and says so loudly if a dump fails. So can you:

    python dump_attention.py --check out.json

SIZE. Dense f32 at 16L x 32H x 64tok is 8.4 MB as JSON, which is silly. The
default threshold zeroes anything under 0.01 and the writer rounds to 4
decimals; that typically cuts it by 20x with no visible change. Raise
--threshold if the file is still fat. The viewer reports how many edges it
drew versus how many exist, so nothing is hidden by the pruning.

OLLAMA. Ollama does not expose attention weights -- it is a serving runtime,
not an interpretability tool. Use transformers with the same open checkpoint:

    pip install torch transformers
    python dump_attention.py --model meta-llama/Llama-3.2-1B \
        --prompt "A fluffy blue creature roamed the verdant forest" \
        --out attn.json

Then drag attn.json onto the viewer. Start SMALL -- 8 layers and 32 tokens is
already a million edges and renders instantly. See the arithmetic in the
session log before you reach for a bigger checkpoint.
"""

import argparse
import os
import json
import sys


def build(model_name, prompt, threshold, max_tokens, layers, heads):
    """Run one forward pass with attentions on, return the viewer's dict."""
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        sys.exit("  need torch + transformers:  pip install torch transformers")

    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, attn_implementation="eager"   # sdpa/flash do NOT return weights
    )
    model.eval()

    enc = tok(prompt, return_tensors="pt")
    ids = enc["input_ids"][0][:max_tokens]
    enc = {"input_ids": ids.unsqueeze(0)}

    with torch.no_grad():
        out = model(**enc, output_attentions=True)

    # out.attentions is a tuple of length n_layers, each [batch, heads, i, j]
    A = out.attentions
    n_lay_all, n_head_all = len(A), A[0].shape[1]
    n_lay = n_lay_all if layers <= 0 else min(layers, n_lay_all)
    n_head = n_head_all if heads <= 0 else min(heads, n_head_all)

    tokens = [tok.decode([int(t)]) for t in ids]
    n = len(tokens)

    attn, kept, total = [], 0, 0
    for L in range(n_lay):
        per_head = []
        for Hh in range(n_head):
            m = A[L][0, Hh].tolist()
            rows = []
            for i in range(n):
                row = [0.0] * n
                for j in range(i + 1):          # causal: never write j > i
                    v = m[i][j]
                    total += 1
                    if v >= threshold:
                        row[j] = round(float(v), 4)
                        kept += 1
                rows.append(row)
            per_head.append(rows)
        attn.append(per_head)

    print("  model      : %s" % model_name)
    print("  tokens     : %d   layers %d/%d   heads %d/%d"
          % (n, n_lay, n_lay_all, n_head, n_head_all))
    print("  causal edges: %s   kept %s (%.1f%%) at threshold %.3f"
          % ("{:,}".format(total), "{:,}".format(kept),
             100.0 * kept / max(1, total), threshold))

    return {"model": model_name, "prompt": prompt, "tokens": tokens,
            "n_layers": n_lay, "n_heads": n_head, "attn": attn,
            "threshold": threshold, "synthetic": False}


def check(path):
    """Verify a dump the way the viewer does -- claims are not evidence."""
    d = json.load(open(path, encoding="utf-8"))
    n = len(d["tokens"])
    bad = rows_bad = 0
    for L in range(d["n_layers"]):
        for Hh in range(d["n_heads"]):
            for i, row in enumerate(d["attn"][L][Hh]):
                if len(row) != n:
                    rows_bad += 1
                for j in range(i + 1, n):
                    if row[j] > 1e-6:
                        bad += 1
    print("  tokens %d, layers %d, heads %d" % (n, d["n_layers"], d["n_heads"]))
    print("  malformed rows          : %d" % rows_bad)
    print("  upper-triangle leaks    : %d %s"
          % (bad, "-- NOT CAUSALLY MASKED" if bad else "-- causal, OK"))
    print("  synthetic flag          : %r" % d.get("synthetic"))
    return 1 if (bad or rows_bad) else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="dump attention for attentium_v0_1.html")
    ap.add_argument("--model", default="meta-llama/Llama-3.2-1B")
    ap.add_argument("--prompt", default="A fluffy blue creature roamed the verdant forest")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "Gos", "runs", "attn.json"),
                    help="default lands in Gos/runs/ -- the gitignored payload lane")
    ap.add_argument("--threshold", type=float, default=0.01,
                    help="zero weights below this (default 0.01)")
    ap.add_argument("--max-tokens", type=int, default=48)
    ap.add_argument("--layers", type=int, default=0, help="0 = all")
    ap.add_argument("--heads", type=int, default=0, help="0 = all")
    ap.add_argument("--check", metavar="PATH", help="verify an existing dump, write nothing")
    a = ap.parse_args()

    if a.check:
        sys.exit(check(a.check))

    d = build(a.model, a.prompt, a.threshold, a.max_tokens, a.layers, a.heads)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, separators=(",", ":"))
    import os
    print("  wrote      : %s  (%.2f MB)" % (a.out, os.path.getsize(a.out) / 2**20))
    print("  now drag it onto shell/attentium_v0_1.html")
    # THE MAINFRAME RULE: no matter how small or big, we triplicate.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import vault
    vault.save(a.out)


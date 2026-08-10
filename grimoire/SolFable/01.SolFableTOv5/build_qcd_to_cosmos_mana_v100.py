#!/usr/bin/env python3
"""Portable deterministic builder for the QCD-to-Cosmos Mana Codex."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

TEX = "THEA_LIGHT_MATRIX_v1.3.4_QCD_TO_COSMOS_MANA_CODEX.tex"
PDF = "THEA_LIGHT_MATRIX_v1.3.4_QCD_TO_COSMOS_MANA_CODEX.pdf"
RECEIPT = "qcd_to_cosmos_mana_v1.0.0_receipt.json"
REPORT = "qcd_to_cosmos_mana_v1.0.0_report.md"
TABLE = "qcd_to_cosmos_check_table.tex"


def run(cmd: list[str], cwd: Path, env: dict[str, str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def tex_escape(value: Any) -> str:
    text = str(value)
    for old, new in [
        ("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
        ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
        ("{", r"\{"), ("}", r"\}"), ("^", r"\^{}"), ("~", r"\~{}"),
    ]:
        text = text.replace(old, new)
    return text


def summarize(result: Any) -> str:
    if isinstance(result, dict):
        items = []
        for key in sorted(result):
            value = result[key]
            if isinstance(value, (dict, list)):
                value_text = json.dumps(value, sort_keys=True, separators=(",", ":"))
            else:
                value_text = str(value)
            items.append(f"{key}={value_text}")
        return "; ".join(items)
    return str(result)


def write_table(root: Path) -> None:
    receipt = json.loads((root / RECEIPT).read_text(encoding="utf-8"))
    lines = [
        r"\begin{longtable}{p{8mm}p{42mm}p{32mm}p{78mm}}",
        r"\caption{Machine-verification ledger. PASS means the stated check reproduced; it does not promote a physical bridge.}\\",
        r"\toprule", r"\# & Check & Status & Receipt summary\\", r"\midrule",
        r"\endfirsthead", r"\toprule", r"\# & Check & Status & Receipt summary\\",
        r"\midrule", r"\endhead",
    ]
    for index, check in enumerate(receipt["checks"], 1):
        lines.append(
            f"{index} & {tex_escape(check['name'])} & {tex_escape(check['status'])} & "
            f"{tex_escape(summarize(check['result']))}\\\\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}"])
    (root / TABLE).write_text("\n".join(lines), encoding="utf-8", newline="\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent))
    parser.add_argument("--skip-figures", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    env = os.environ.copy()
    env.setdefault("SOURCE_DATE_EPOCH", "1786320000")
    env["TZ"] = "UTC"

    run(["python", "verify_qcd_to_cosmos_mana_v100.py", "--out", RECEIPT, "--report", REPORT], root, env)
    if not args.skip_figures:
        run(["python", "generate_qcd_to_cosmos_mana_figures.py", "--out-dir", "qcd_to_cosmos_mana_figures"], root, env)
    write_table(root)
    run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", TEX], root, env)

    result = {
        "tex_sha256": sha256(root / TEX),
        "pdf_sha256": sha256(root / PDF),
        "receipt_sha256": sha256(root / RECEIPT),
        "pages": int(subprocess.check_output(["pdfinfo", str(root / PDF)], text=True).split("Pages:", 1)[1].splitlines()[0].strip()),
    }
    (root / "qcd_to_cosmos_mana_build.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

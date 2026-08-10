#!/usr/bin/env python3
"""Regression tests for the v2.1 bit oracle and sealed artifact."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import math
from pathlib import Path
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "code"
MAGIC_PATH = CODE / "magic_constant_v2.py"
SEALED_PATH = CODE / "sol_tower_sealed_v2.py"
C_PATH = CODE / "rung_v2.c"


def load_magic():
    spec = importlib.util.spec_from_file_location("magic_constant_v2", MAGIC_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = load_magic()


def run(command: list[str], *, cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def assert_ok(proc: subprocess.CompletedProcess[str]) -> str:
    if proc.returncode != 0:
        raise AssertionError(
            f"command failed ({proc.returncode})\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc.stdout


def test_high_precision_constants() -> None:
    assert M.D_CANONICAL == 0x0016373AD151CA68
    assert M.C_ASYMPTOTIC == 0x3FF1109CBE5E8386
    # The v1 binary64 derivation rounded D one raw-bit unit too high.
    assert M.D_LEGACY == M.D_CANONICAL + 1


def test_full_binary64_ladder() -> None:
    assert M.MAX_BINARY64_RUNG == 737
    assert len(M.BINARY64_LADDER) == 738
    assert len(str(M.exact_T(737))) == 309
    assert M.classification_failures(M.C_ASYMPTOTIC, M.D_CANONICAL) == []
    assert M.classification_failures(M.C_ROBUST, M.D_CANONICAL) == []
    assert M.classification_failures(M.C_LEGACY, M.D_LEGACY) == []


def test_exact_magic_plateau() -> None:
    assert M.C_MIN == 0x3FE6AD27C6055065
    assert M.C_MAX == 0x3FFAAD27C6055064
    assert M.C_ROBUST == 0x3FF0AD27C6055064
    assert M.C_MAX - M.C_MIN + 1 == 5 * 2**50
    for value in (M.C_ASYMPTOTIC, M.C_ROBUST, M.C_LEGACY):
        assert M.C_MIN <= value <= M.C_MAX


def test_oracle_membership_and_domain() -> None:
    for n, exact, rounded, _bits in M.BINARY64_LADDER:
        assert M.rung_from_bits(rounded) == n
        assert M.is_rounded_ladder_value(rounded)
        assert M.exact_shell(n) == exact
        assert M.rung_from_bits(M.shell_guess(n)) == n
    for bad in (0.0, -1.0, math.inf, -math.inf, math.nan):
        try:
            M.rung_from_bits(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"bad domain value accepted: {bad!r}")


def test_inverse_guess_bound() -> None:
    worst, rung, mean = M.inverse_error(M.C_ROBUST, M.D_CANONICAL)
    assert worst < 0.047
    assert rung == 1
    assert mean < 0.027


def test_old_generated_c_block_was_not_certified() -> None:
    """v1's printed C snippet omitted +D/2 although its test used rounding."""
    misses = 0
    for n, _exact, rounded, _bits in M.BINARY64_LADDER:
        got = (M.bits_of(rounded) - M.C_LEGACY) // M.D_LEGACY
        misses += got != n
    assert misses == 718  # 738-domain audit; the displayed code was not 738/738.


def extract_field(text: str, label: str) -> str:
    match = re.search(rf"^\s*{re.escape(label)}\s*:\s*(\S+)", text, re.MULTILINE)
    if not match:
        raise AssertionError(f"missing field {label!r}\n{text[:1000]}")
    return match.group(1)


def test_seal_entry_paths() -> None:
    source_sha = hashlib.sha256(SEALED_PATH.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory() as td_raw:
        td = Path(td_raw)
        script = td / "sol_tower_sealed_v2.py"
        shutil.copy2(SEALED_PATH, script)

        commands = {
            "direct": [sys.executable, str(script)],
            "module": [sys.executable, "-m", "sol_tower_sealed_v2"],
            "import": [sys.executable, "-c", "import sol_tower_sealed_v2"],
            "runpy": [sys.executable, "-c", "import runpy;runpy.run_path('sol_tower_sealed_v2.py')"],
        }
        outputs: dict[str, str] = {}
        for name, command in commands.items():
            env_cwd = td
            proc = run(command, cwd=env_cwd)
            outputs[name] = assert_ok(proc)
            assert "SEALED: mathematics closed" in outputs[name]
            assert source_sha in outputs[name]

        bytecode = {
            extract_field(text, "normalized bytecode")
            for text in outputs.values()
        }
        assert len(bytecode) == 1

        clean_exec = run(
            [
                sys.executable,
                "-c",
                "src=open('sol_tower_sealed_v2.py').read();"
                "exec(compile(src,'<exec>','exec'),{})",
            ],
            cwd=td,
        )
        clean_text = assert_ok(clean_exec)
        assert "source fingerprint     : UNREACHABLE" in clean_text
        assert "OPEN: mathematics closed" in clean_text
        assert source_sha not in clean_text

        wrapper = td / "wrapper.py"
        wrapper.write_text(
            "src=open('sol_tower_sealed_v2.py').read()\n"
            "exec(compile(src,'<string>','exec'))\n",
            encoding="utf-8",
        )
        wrapper_sha = hashlib.sha256(wrapper.read_bytes()).hexdigest()
        inherited = assert_ok(run([sys.executable, str(wrapper)], cwd=td))
        assert "source fingerprint     : UNREACHABLE" in inherited
        assert wrapper_sha not in inherited

        reload_text = assert_ok(
            run(
                [
                    sys.executable,
                    "-c",
                    "import importlib,sol_tower_sealed_v2;"
                    "importlib.reload(sol_tower_sealed_v2)",
                ],
                cwd=td,
            )
        )
        assert reload_text.count("SOL TOWER, SEALED v2.1") == 1


def test_pyc_refuses_source_seal() -> None:
    with tempfile.TemporaryDirectory() as td_raw:
        td = Path(td_raw)
        source = td / "sol_tower_sealed_v2.py"
        shutil.copy2(SEALED_PATH, source)
        pyc = td / "sol_tower_sealed_v2.pyc"
        py_compile.compile(str(source), cfile=str(pyc), doraise=True)
        source.unlink()
        text = assert_ok(run([sys.executable, str(pyc)], cwd=td))
        assert "compiled-image hash" in text
        assert "source status          : UNREACHABLE" in text
        assert "OPEN: mathematics closed" in text


def test_c_kernel_strict_and_sanitized() -> None:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        raise AssertionError("no C compiler")
    with tempfile.TemporaryDirectory() as td_raw:
        td = Path(td_raw)
        binary = td / "rung"
        compile_cmd = [
            cc,
            "-O2",
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-DORACLE_BENCH_REPS=10000",
            "-DORACLE_BENCH_ROUNDS=3",
            str(C_PATH),
            "-lm",
            "-o",
            str(binary),
        ]
        assert_ok(run(compile_cmd, cwd=td))
        output = assert_ok(run([str(binary)], cwd=td))
        assert "bit-oracle hits      : 46/46" in output
        assert "log2-route hits      : 46/46" in output

        sanitized = td / "rung_san"
        san_cmd = [
            cc,
            "-O1",
            "-g",
            "-std=c11",
            "-fsanitize=undefined,address",
            "-fno-omit-frame-pointer",
            "-DORACLE_BENCH_REPS=1000",
            "-DORACLE_BENCH_ROUNDS=3",
            str(C_PATH),
            "-lm",
            "-o",
            str(sanitized),
        ]
        assert_ok(run(san_cmd, cwd=td))
        san = run([str(sanitized)], cwd=td)
        assert_ok(san)
        assert "runtime error" not in san.stderr.lower()


def test_existing_tower_regressions() -> None:
    output = assert_ok(run([sys.executable, str(CODE / "test_sol_tower_v2.py")], cwd=ROOT, timeout=240))
    assert "ALL 8/8 PASS" in output


TESTS = [
    test_high_precision_constants,
    test_full_binary64_ladder,
    test_exact_magic_plateau,
    test_oracle_membership_and_domain,
    test_inverse_guess_bound,
    test_old_generated_c_block_was_not_certified,
    test_seal_entry_paths,
    test_pyc_refuses_source_seal,
    test_c_kernel_strict_and_sanitized,
    test_existing_tower_regressions,
]


def main() -> None:
    for test in TESTS:
        test()
        print(f"PASS {test.__name__}")
    print(f"ALL {len(TESTS)}/{len(TESTS)} PASS")


if __name__ == "__main__":
    main()

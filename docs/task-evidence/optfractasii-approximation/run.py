#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Regenerate OptFractASII approximation blocker evidence deterministically."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reference as ref  # noqa: E402


def write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == payload:
        return
    path.write_bytes(payload)


def render_contract() -> bytes:
    return ref.canonical_bytes(ref.build_contract())


def render_report() -> tuple[bytes, bytes]:
    text, digest = ref.canonical_report()
    return text.encode("ascii"), (digest + "  report.json\n").encode("ascii")


def render_sources() -> bytes:
    return ref.sources_bytes()


def render_readme() -> bytes:
    readme = HERE / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    if not text:
        raise FileNotFoundError("README.md must exist before regeneration")
    return ref.update_readme_tables(text).encode("utf-8")


def generate_once() -> dict[str, bytes]:
    # Fixed-point regeneration: contract/report/sidecar, then README/SOURCES until stable.
    for _ in range(8):
        contract = render_contract()
        report, report_sha = render_report()
        write_bytes(HERE / "contract.json", contract)
        write_bytes(HERE / "report.json", report)
        write_bytes(HERE / "report.json.sha256", report_sha)
        readme = render_readme()
        write_bytes(HERE / "README.md", readme)
        sources = render_sources()
        write_bytes(HERE / "SOURCES.sha256", sources)
        readme2 = render_readme()
        sources2 = render_sources()
        if readme2 == readme and sources2 == sources:
            return {
                "contract.json": contract,
                "report.json": report,
                "report.json.sha256": report_sha,
                "README.md": readme2,
                "SOURCES.sha256": sources2,
            }
        write_bytes(HERE / "README.md", readme2)
        write_bytes(HERE / "SOURCES.sha256", sources2)
    raise RuntimeError("regeneration_did_not_converge")


def write_outputs(outputs: dict[str, bytes]) -> None:
    for name in ["contract.json", "report.json", "report.json.sha256", "SOURCES.sha256", "README.md"]:
        write_bytes(HERE / name, outputs[name])


def run_repeatability(repeats: int) -> dict[str, bytes]:
    reference: dict[str, bytes] | None = None
    for index in range(repeats):
        outputs = generate_once()
        if reference is None:
            reference = outputs
            continue
        for name, payload in outputs.items():
            if payload != reference[name]:
                raise RuntimeError(f"nondeterministic_output:{name}:run{index + 1}")
    assert reference is not None
    return reference


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["contract", "report", "sources", "readme", "all"])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    out = args.output_dir.resolve() if args.output_dir else HERE
    if out != HERE:
        out.mkdir(parents=True, exist_ok=True)
        src_root = Path(__file__).resolve().parent
        for name in ["LICENSES.md", "reference.py", "run.py", "test_reference.py", "verify.py", "README.md"]:
            (out / name).write_bytes((src_root / name).read_bytes())
        for src in src_root.glob("*.license"):
            (out / src.name).write_bytes(src.read_bytes())
        env = os.environ.copy()
        env["AUDIOML_ROOT"] = os.environ.get("AUDIOML_ROOT") or str(ref.AUDIO_ROOT)
        env["SDK_WORKTREE"] = os.environ.get("SDK_WORKTREE") or str(ref.SDK_ROOT)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        cmd = [sys.executable, str(out / "run.py"), args.command, "--repeats", str(args.repeats)]
        proc = subprocess.run(cmd, cwd=str(out), capture_output=True, text=True, encoding="utf-8", env=env)
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return proc.returncode
    if args.command == "contract":
        write_bytes(HERE / "contract.json", render_contract())
    elif args.command == "report":
        report, sha = render_report()
        write_bytes(HERE / "report.json", report)
        write_bytes(HERE / "report.json.sha256", sha)
    elif args.command == "sources":
        write_bytes(HERE / "SOURCES.sha256", render_sources())
    elif args.command == "readme":
        write_bytes(HERE / "README.md", render_readme())
    elif args.command == "all":
        outputs = run_repeatability(args.repeats)
        write_outputs(outputs)
        print(f"PASS run.py repeats={args.repeats} output={HERE}")
        return 0
    print(f"PASS run.py {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

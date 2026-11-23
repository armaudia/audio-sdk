#!/usr/bin/env python3
"""Run the paired MDF reference, repeat it exactly and verify the frozen oracle.

Every fixture is generated in memory by fixture.py and written only to a caller
scratch directory (outside the worktree). No asset, audio or build byte is read
from the repository and none is committed.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import pathlib
import shutil
import struct
import subprocess
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import fixture  # noqa: E402

TASK_DIR = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_ORACLE = TASK_DIR / "evidence" / "oracle.json"
DEFAULT_SOURCES = TASK_DIR / "SOURCES.sha256"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_f32(path: pathlib.Path) -> list[float]:
    raw = path.read_bytes()
    if len(raw) % 4 != 0:
        raise ValueError("f32 length is not a multiple of 4")
    return list(struct.unpack("<%df" % (len(raw) // 4), raw))


def load_sources(path: pathlib.Path, sdk_root: pathlib.Path,
                 ws_root: pathlib.Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        name = name.strip()
        if name.startswith("sdk:"):
            target = sdk_root / name[4:]
        elif name.startswith("ws:"):
            target = ws_root / name[3:]
        else:
            raise ValueError("source name must use sdk: or ws: prefix")
        actual = sha256_bytes(target.read_bytes())
        if actual != digest:
            raise ValueError("pin mismatch for %s: %s != %s" % (name, actual, digest))
        digests[name] = digest
    return digests


def run_cli(cli: pathlib.Path, work: pathlib.Path, label: str,
            render: list[float], capture: list[float],
            extra: list[str] | None = None) -> tuple[int, pathlib.Path, bytes | None]:
    case_dir = work / label
    case_dir.mkdir(parents=True, exist_ok=True)
    render_path = case_dir / "render.f32"
    capture_path = case_dir / "capture.f32"
    output_path = case_dir / "output.f32"
    render_path.write_bytes(fixture.pack_f32(render))
    capture_path.write_bytes(fixture.pack_f32(capture))
    if output_path.exists():
        output_path.unlink()
    command = [str(cli), "--render", str(render_path), "--capture",
               str(capture_path), "--output", str(output_path)]
    command.extend(extra or [])
    completed = subprocess.run(command, capture_output=True, text=True)
    payload = output_path.read_bytes() if output_path.exists() else None
    return completed.returncode, output_path, payload


def case_metrics(capture: list[float], output: list[float],
                 near: list[float]) -> dict[str, Any]:
    # The same fixed 20 ms window is used for every case. In overlap_small it
    # contains both near-end and residual echo, so the ratio is an upper bound
    # on near-end preservation and is disclosed as such.
    start = fixture.NEAR_BURST_FRAMES[0] * fixture.FRAME_SAMPLES
    end = fixture.NEAR_BURST_FRAMES[1] * fixture.FRAME_SAMPLES
    converged_start = fixture.CONVERGED_FRAMES[0] * fixture.FRAME_SAMPLES
    converged_end = fixture.CONVERGED_FRAMES[1] * fixture.FRAME_SAMPLES
    return {
        "erle_db_converged": fixture.round6(
            fixture.erle_db(capture, output, converged_start, converged_end)),
        "output_over_near_rms_overlap": fixture.round6(
            fixture.amplitude_ratio(output, near, start, end)),
        "peak": fixture.round6(max(abs(value) for value in output)),
        "nonfinite_count": sum(1 for value in output if not math.isfinite(value)),
        "duration_samples": len(output),
    }


def build_report(cli: pathlib.Path, work: pathlib.Path, repeat: int,
                 sources: dict[str, str], sources_path: pathlib.Path) -> dict[str, Any]:
    streams = fixture.generate()
    fixture_digests = {
        case: {
            "render": fixture.digest_f32(values["render"]),
            "capture": fixture.digest_f32(values["capture"]),
        }
        for case, values in streams.items()
    }
    fixture_payload = {
        "spec": fixture.spec(),
        "digests": fixture_digests,
    }
    fixture_digest = fixture.digest_text(fixture.canonical(fixture_payload))

    cases: dict[str, Any] = {}
    for index, case_name in enumerate(fixture.CASES):
        values = streams[case_name]
        digests: list[str] = []
        byte_equal = True
        outputs: list[list[float]] = []
        for pass_index in range(repeat):
            label = "case-%02d-repeat-%02d" % (index, pass_index)
            status, _, payload = run_cli(cli, work, label, values["render"],
                                         values["capture"])
            if status != 0 or payload is None:
                raise RuntimeError("%s repeat %d failed: status %d" %
                                   (case_name, pass_index, status))
            outputs.append(read_f32(work / label / "output.f32"))
            digests.append(sha256_bytes(payload))
            if payload != fixture.pack_f32(outputs[-1]):
                raise RuntimeError("unexpected f32 encoding")
        byte_equal = all(digest == digests[0] for digest in digests)
        near = streams["near_end_only"]["capture"]
        if case_name in ("near_end_only", "no_reference_passthrough"):
            near = values["capture"]
        cases[case_name] = {
            "render_digest": fixture_digests[case_name]["render"],
            "capture_digest": fixture_digests[case_name]["capture"],
            "output_digests": digests,
            "repeat_bytes_identical": byte_equal,
            "passthrough_bit_exact": (
                sha256_bytes(fixture.pack_f32(outputs[0])) ==
                sha256_bytes(fixture.pack_f32(values["capture"]))
                if values["render"] == [0.0] * fixture.SAMPLE_COUNT else False),
            **case_metrics(values["capture"], outputs[0], near),
        }

    controls: dict[str, Any] = {}
    echo = streams["echo_only"]
    bad_capture = list(echo["capture"])
    bad_capture[0] = float("nan")
    status, _, payload = run_cli(cli, work, "control-nonfinite", echo["render"],
                                 bad_capture)
    controls["reject_nonfinite_capture"] = {
        "exit_code": status, "output_written": payload is not None,
        "passed": status != 0 and payload is None}

    status, _, payload = run_cli(cli, work, "control-short", echo["render"],
                                 echo["capture"][:-1])
    controls["reject_wrong_length"] = {
        "exit_code": status, "output_written": payload is not None,
        "passed": status != 0 and payload is None}

    status, _, payload = run_cli(cli, work, "control-bad-rate", echo["render"],
                                 echo["capture"], ["--rate", "48000"])
    controls["reject_wrong_rate"] = {
        "exit_code": status, "output_written": payload is not None,
        "passed": status != 0 and payload is None}

    missing_render = work / "control-missing-render" / "absent.f32"
    missing_render.parent.mkdir(parents=True, exist_ok=True)
    capture_path = work / "control-missing-render" / "capture.f32"
    capture_path.write_bytes(fixture.pack_f32(echo["capture"]))
    output_path = work / "control-missing-render" / "output.f32"
    if output_path.exists():
        output_path.unlink()
    missing = subprocess.run(
        [str(cli), "--render", str(missing_render), "--capture", str(capture_path),
         "--output", str(output_path)], capture_output=True, text=True)
    controls["reject_missing_render"] = {
        "exit_code": missing.returncode,
        "output_written": output_path.exists(),
        "passed": missing.returncode != 0 and not output_path.exists()}

    controls["pinned_sources_verified"] = {
        "passed": True,
        "manifest_digest": sha256_bytes(sources_path.read_bytes())}

    for name, result in controls.items():
        if not result["passed"]:
            raise RuntimeError("negative control failed: " + name)
    for name, result in cases.items():
        if not result["repeat_bytes_identical"]:
            raise RuntimeError("repeat mismatch: " + name)
        if result["nonfinite_count"] != 0:
            raise RuntimeError("nonfinite output: " + name)

    return {
        "schema": fixture.SCHEMA,
        "repeat_count": repeat,
        "fixture": fixture.spec(),
        "fixture_digest": fixture_digest,
        "fixture_digests": fixture_digests,
        "source_digests": dict(sorted(sources.items())),
        "source_manifest_digest": sha256_bytes(sources_path.read_bytes()),
        "source_root_note": "sdk: task SDK worktree; ws: /Users/htsakanyan/workspace/audio/audioml",
        "cases": dict(sorted(cases.items())),
        "controls": dict(sorted(controls.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True, type=pathlib.Path)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--work", required=True, type=pathlib.Path)
    parser.add_argument("--oracle", type=pathlib.Path, default=DEFAULT_ORACLE)
    parser.add_argument("--sources-sha", type=pathlib.Path, default=DEFAULT_SOURCES)
    parser.add_argument("--sdk-root", type=pathlib.Path,
                        default=TASK_DIR.parents[2])
    parser.add_argument("--source-root", type=pathlib.Path,
                        default=pathlib.Path("/Users/htsakanyan/workspace/audio/audioml"))
    parser.add_argument("--write-oracle", action="store_true",
                        help="bootstrap the frozen oracle; use only once")
    args = parser.parse_args()
    if args.repeat != 3:
        raise SystemExit("the frozen protocol requires --repeat 3")
    if not args.cli.is_file():
        raise SystemExit("CLI not found: %s" % args.cli)
    sources = load_sources(args.sources_sha, args.sdk_root, args.source_root)
    if args.work.exists():
        shutil.rmtree(args.work)
    args.work.mkdir(parents=True)
    report = build_report(args.cli, args.work, args.repeat, sources,
                          args.sources_sha)
    text = fixture.canonical(report)
    if args.write_oracle:
        args.oracle.parent.mkdir(parents=True, exist_ok=True)
        if args.oracle.exists():
            raise SystemExit("refusing to overwrite an existing oracle")
        args.oracle.write_text(text, encoding="utf-8")
        args.oracle.with_suffix(".json.sha256").write_text(
            fixture.digest_text(text) + "  oracle.json\n", encoding="utf-8")
    else:
        expected = args.oracle.read_text(encoding="utf-8")
        if text != expected:
            raise SystemExit("oracle mismatch: generated %s, frozen %s" %
                             (fixture.digest_text(text), fixture.digest_text(expected)))
    print("report_digest=%s" % fixture.digest_text(text))
    print("cases=%d repeats=%d controls=%d" %
          (len(report["cases"]), args.repeat, len(report["controls"])))
    for name, case in sorted(report["cases"].items()):
        print("%s: erle_db=%s near_ratio=%s repeats_identical=%s" %
              (name, case["erle_db_converged"],
               case["output_over_near_rms_overlap"],
               case["repeat_bytes_identical"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

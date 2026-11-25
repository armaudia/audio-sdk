# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Build and run the pinned, separately staged Bungee Basic reference.

Opt-in developer evidence only. This runner never changes the SDK build, ABI,
registry or defaults. It copies no Bungee file into the SDK: the source stays in
its existing checkout and every build artifact stays in a fresh private scratch
directory. A missing or changed pin is a hard failure, never a skip.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

import synthetic

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
DEFAULT_BUNGEE_ROOT = Path(
    "/Users/htsakanyan/workspace/audio/audioml/data/checkouts/tsm-engines-20261101/bungee")
TASK_BASE = "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d"
EXPECTED_HEAD = "61f52bf34be577d189d388772ddfa3696dee77d8"
EXPECTED_TREE = "c8edb5f21ad58472d8ce6f635fa3e6c707474ca6"
EXPECTED_SUBMODULES = (
    " 4bf61f08697b110d9e3991864650a405b3dd515d submodules/cxxopts (4bf61f0)",
    " c29c800126982c561e8d0b9255dc65474cd98de3 submodules/eigen (c29c800)",
    " 02fe7715a5bf8bfd914681c53429600f94e0f536 submodules/pffft (02fe771)",
)
EXPECTED_FILES = {
    "LICENSE": "86cf9656479f1edb82245b985f4a2cc0d503b945766ebeda4269c60b307699ae",
    "CMakeLists.txt": "72e48f2f6e6d90430a10710d03d0baf24c2d719e24c936aec0c802e0280ae268",
    ".gitmodules": "65c8a5ee9a24ab50ca67a0811bf697a63ad8d171f89af26fe917713a2627eed3",
    "bungee/Bungee.h": "91ac529c35f527401add72030290ab65639d28f3a0cedd3c85ca361692b3d514",
    "bungee/Stream.h": "88e68f39fca48671fbccf6f376b8527215608cbc3ac5de117361d4c014c257d9",
    "submodules/cxxopts/LICENSE": None,
    "submodules/eigen/COPYING.MPL2": None,
    "submodules/pffft/README.md": None,
}
ALLOWED_STATUS = "?? build-rel/"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.rstrip("\n")


def check_source(root: Path) -> dict[str, object]:
    if not (root / ".git").exists() or not (root / "CMakeLists.txt").is_file():
        raise RuntimeError(f"not a staged Bungee checkout: {root}")
    head = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    submodules = tuple(git(root, "submodule", "status").splitlines())
    status = tuple(git(root, "status", "--porcelain=v1", "--untracked-files=normal").splitlines())
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"unexpected Bungee HEAD: {head}")
    if tree != EXPECTED_TREE:
        raise RuntimeError(f"unexpected Bungee tree: {tree}")
    if submodules != EXPECTED_SUBMODULES:
        raise RuntimeError(f"unexpected submodule revisions: {submodules}")
    unexpected = [line for line in status if line != ALLOWED_STATUS]
    if unexpected:
        raise RuntimeError(f"staged checkout has extra changes: {unexpected}")

    license_text = (root / "LICENSE").read_text(encoding="utf-8")
    if "Mozilla Public License Version 2.0" not in license_text[:200]:
        raise RuntimeError("Bungee LICENSE is not MPL-2.0")
    for header in ("bungee/Bungee.h", "bungee/Stream.h", "cmd/main.cpp"):
        if "MPL-2.0" not in (root / header).read_text(encoding="utf-8")[:200]:
            raise RuntimeError(f"missing MPL-2.0 SPDX header: {header}")
    cxxopts = (root / "submodules/cxxopts/LICENSE").read_text(encoding="utf-8")
    if "Permission is hereby granted" not in cxxopts:
        raise RuntimeError("cxxopts license marker missing")
    eigen = (root / "submodules/eigen/COPYING.MPL2").read_text(encoding="utf-8")
    if "Mozilla Public License Version 2.0" not in eigen[:200]:
        raise RuntimeError("Eigen MPL-2.0 marker missing")
    pffft = (root / "submodules/pffft/README.md").read_text(encoding="utf-8")
    if "license is BSD-like" not in pffft:
        raise RuntimeError("pffft BSD-like license marker missing")

    files = {}
    for name, expected in EXPECTED_FILES.items():
        digest = sha256(root / name)
        if expected is not None and digest != expected:
            raise RuntimeError(f"pin mismatch: {name}")
        files[name] = digest
    return {"head": head, "tree": tree, "submodules": list(submodules),
            "status": list(status), "file_sha256": files,
            "license": {"bungee": "MPL-2.0", "cxxopts": "MIT",
                        "eigen": "MPL-2.0 (COPYING.MPL2)", "pffft": "BSD-like"},
            "vendor_files_modified": False, "vendor_files_vendored_into_sdk": False}


def tokenize(command: list[str], root: Path, scratch: Path, cxx: str, cmake: str,
             python: str) -> str:
    replacements = [(str(root), "$BUNGEE_ROOT"), (str(scratch), "$SCRATCH"),
                    (str(HERE), "$TASK"), (cmake, "$CMAKE"), (cxx, "$CXX"),
                    (python, "$PYTHON"), (str(SDK_ROOT), "$SDK_ROOT")]
    parts = []
    for item in command:
        escaped = item
        for source, token in replacements:
            escaped = escaped.replace(source, token)
        parts.append(escaped if re.fullmatch(r"[\w./$+-]+", escaped) else
                     "'" + escaped.replace("'", "'\\''") + "'")
    return " ".join(parts)


def run(command: list[str], cwd: Path, label: str, commands: list[str],
        root: Path, scratch: Path, cxx: str, cmake: str, python: str) -> str:
    commands.append(tokenize(command, root, scratch, cxx, cmake, python))
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{label} failed ({result.returncode}):\n"
                           f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    return result.stdout


def first_line(command: list[str]) -> str:
    return subprocess.run(command, check=True, capture_output=True,
                          text=True).stdout.splitlines()[0]


def canonical_bytes(report: dict) -> bytes:
    return (json.dumps(report, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bungee-root", type=Path, default=DEFAULT_BUNGEE_ROOT)
    parser.add_argument("--cmake", required=True)
    parser.add_argument("--cxx", default="/usr/bin/clang++")
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--report", type=Path,
                        default=HERE / "native_report.json")
    args = parser.parse_args(argv)

    root = args.bungee_root.resolve()
    scratch = args.scratch.resolve()
    if scratch.exists() and any(scratch.iterdir()):
        raise RuntimeError(f"scratch is not empty: {scratch}")
    scratch.mkdir(parents=True, exist_ok=True)
    source = check_source(root)
    commands: list[str] = []
    cmake = str(Path(args.cmake).resolve())
    cxx = str(Path(args.cxx).resolve())
    python = str(Path(sys.executable).resolve())

    configure = [cmake, "-S", str(root), "-B", str(scratch / "build"),
                 "-DCMAKE_BUILD_TYPE=Release", "-DBUNGEE_BUILD_SHARED_LIBRARY=OFF",
                 "-DBUNGEE_SELF_TEST=0"]
    build = [cmake, "--build", str(scratch / "build"), "--parallel", "4"]
    run(configure, HERE, "cmake configure", commands, root, scratch,
        cxx, cmake, python)
    run(build, HERE, "cmake build", commands, root, scratch,
        cxx, cmake, python)
    build_dir = scratch / "build"
    objects = sorted(build_dir.rglob("*.o"))
    object_manifest = b"".join(
        f"{obj.relative_to(build_dir)} {sha256(obj)}\n".encode("utf-8")
        for obj in objects)
    artifacts = {
        "bungee_cli": sha256(build_dir / "bungee"),
        "object_files": len(objects),
        "object_manifest_sha256": hashlib.sha256(object_manifest).hexdigest(),
        "archive_note": "ar timestamps make static-archive bytes build-specific; "
                        "object manifest is the canonical build digest",
    }

    compile_command = [cxx, "-std=c++20", "-O2", "-I" + str(root),
                       str(HERE / "bungee_native.cpp"),
                       str(scratch / "build/libbungee.a"),
                       str(scratch / "build/libpffft.a"),
                       "-o", str(scratch / "bungee_native")]
    run(compile_command, HERE, "harness compile", commands, root, scratch,
        cxx, cmake, python)
    generator = [python, "-c",
                 f"import sys; sys.path.insert(0, {str(HERE)!r}); import synthetic; "
                 f"from pathlib import Path; "
                 f"synthetic.write_wav(Path({str(scratch)!r})/'input.wav', "
                 "synthetic.stimulus())"]
    run(generator, HERE, "generate stimulus", commands, root, scratch,
        cxx, cmake, python)
    stimulus_path = scratch / "input.wav"
    stimulus_digest = sha256(stimulus_path)

    cases: dict[str, object] = {}
    stream_cases = (
        ("identity_1x", "0:1", 0, ((0, "1"),)),
        ("slower_0p8", "0:0.8", 0, ((0, "0.8"),)),
        ("faster_1p25", "0:1.25", 0, ((0, "1.25"),)),
        ("faster_1p5", "0:1.5", 0, ((0, "1.5"),)),
        ("rate_changes", "0:1,4800:0.8,9600:1.25,12960:1", 0,
         synthetic.RATE_CHANGES),
        ("bounded_zero_tail", "0:1", 64, ((0, "1"),)),
    )
    source_samples = synthetic.read_wav(stimulus_path)
    for name, schedule_text, tail, schedule in stream_cases:
        output_path = scratch / f"{name}.wav"
        meta_path = scratch / f"{name}.json"
        command = [str(scratch / "bungee_native"), "--mode", "stream",
                   "--input", str(stimulus_path), "--output", str(output_path),
                   "--json", str(meta_path), "--schedule", schedule_text,
                   "--chunks", ",".join(map(str, synthetic.CHUNK_CYCLE)),
                   "--tail-samples", str(tail)]
        run(command, HERE, name, commands, root, scratch, cxx, cmake, python)
        meta = json.loads(meta_path.read_text(encoding="utf-8"),
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              ValueError(f"nonfinite {value}")))
        native = synthetic.analyze_stream(stimulus_path, output_path, meta, schedule)
        control_output = synthetic.matched_linear_control(source_samples, schedule)
        cases[name] = {"schedule": schedule_text, "chunks": synthetic.CHUNK_CYCLE,
                       "caller_zero_tail_samples": tail,
                       "native_bungee": native,
                       "matched_synthetic_control": synthetic.analyze_control(
                           source_samples, control_output),
                       "input_sha256": stimulus_digest,
                       "output_sha256": native["output_sha256"]}

    granular_output = scratch / "granular_flush.wav"
    granular_meta = scratch / "granular_flush.json"
    granular_command = [str(scratch / "bungee_native"), "--mode", "granular",
                        "--input", str(stimulus_path), "--output", str(granular_output),
                        "--json", str(granular_meta), "--speed", "1.25",
                        "--max-grains", "512"]
    run(granular_command, HERE, "granular flush", commands, root, scratch,
        cxx, cmake, python)
    granular_meta_data = json.loads(granular_meta.read_text(encoding="utf-8"))
    granular_analysis = synthetic.analyze_granular(granular_meta_data)
    granular_analysis["output_wav_sha256"] = sha256(granular_output)

    report = {
        "task_id": "SDK-BUNGEE-BASIC",
        "component": "bungee-basic",
        "kind": "opt_in_native_developer_reference",
        "status": "native_reference_proven_not_qualified",
        "qualification_status": "not_qualified",
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
        "base_commit": TASK_BASE,
        "boundary": {
            "sdk_abi_changed": False, "provider_registered": False,
            "enabled_by_default": False, "sdk_build_changed": False,
            "registry_changed": False, "ci_changed": False,
            "installed_v0_geometry": [16000, 1, "f32", 160],
            "elastic_contract": "audio-sdk/elastic-pcm-packets/0.1",
            "elastic_use": "variable-count contiguous chunks, caller-owned target clock, "
                           "piecewise ratio, bounded drain; task-local C++ only",
            "sdk_callback_invoked": False,
        },
        "rights": {
            "vendor": "Parabola Research Limited", "license": "MPL-2.0",
            "source_staged_separately": True, "build_staged_separately": True,
            "vendor_source_or_binary_in_sdk_git": False,
            "vendor_files_modified": False,
            "license_review": "local provenance and MPL file-level copyleft checked; "
                              "distribution and legal approval not claimed",
            "submodule_licenses": source["license"],
        },
        "source": source,
        "environment": {
            "python": first_line([python, "--version"]),
            "python_executable_token": "$PYTHON",
            "cmake": first_line([cmake, "--version"]),
            "cxx": first_line([cxx, "--version"]),
            "architecture": platform.machine(),
            "system": platform.system(),
            "release": platform.release(),
            "sdk_base_commit": TASK_BASE,
        },
        "build": {
            "configure_and_build_commands": commands[:2],
            "artifact_sha256": artifacts,
            "release_static": True,
        },
        "stimulus": {
            "kind": "synthetic analytic tone plus transient notches",
            "sample_rate_hz": synthetic.RATE, "frames": len(source_samples),
            "sha256": stimulus_digest, "markers": list(synthetic.MARKERS),
            "chunk_cycle": list(synthetic.CHUNK_CYCLE),
            "no_real_audio": True,
        },
        "cases": cases,
        "granular_flush": granular_analysis,
        "commands": commands,
        "skips": {
            "real_speech_and_music": "blocked: no rights-cleared unfamiliar cohort in this task",
            "listening_and_audibility": "blocked: no authorized listening panel; transient position proxy only",
            "device_timing": "blocked: no callback, DAC, paced playback or device clock",
            "provider_intake": "blocked: no vendor asset admitted, registered or packaged",
            "release_qualification": "blocked: rate acceptance profile is only partially applied",
            "rate_profile_items": "silence, rebuffer, drift and source-timestamp pause policy "
                                  "remain unmeasured; no missing result promoted",
        },
        "residual_gates": [
            "Native parity on a rights-cleared speech and music cohort at the final rate profile.",
            "Blinded listening for transients, naturalness and intelligibility.",
            "Target-runtime buffering, rebuffer, drift, callback deadline and output delay.",
            "MPL distribution review and a separate opt-in provider intake before any registration.",
            "Silence, rebuffer, drift and final-partial-window qualification under the rate profile.",
        ],
        "reproduction": "Use a fresh private scratch and the exact commands above with the "
                        "pinned checkout and toolchain. Byte-identical artifacts are expected "
                        "only on the recorded host/toolchain.",
    }

    payload = canonical_bytes(report)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_bytes(payload)
    sidecar = args.report.with_name(args.report.name + ".sha256")
    sidecar.write_text(f"{hashlib.sha256(payload).hexdigest()}  {args.report.name}\n",
                       encoding="utf-8")
    print(f"native_report_sha256={hashlib.sha256(payload).hexdigest()} "
          f"bytes={len(payload)} scratch={scratch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

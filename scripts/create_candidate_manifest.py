#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Write an external, byte-derived manifest for one immutable candidate."""
from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_files() -> list[Path]:
    excluded = {".git", "build", ".venv", "__pycache__", "target"}
    return sorted(
        (
            path
            for path in ROOT.rglob("*")
            if path.is_file()
            and not excluded.intersection(path.relative_to(ROOT).parts)
            and path.suffix != ".pyc"
        ),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def command_version(command: list[str]) -> str:
    try:
        return subprocess.check_output(
            command, text=True, stderr=subprocess.STDOUT
        ).splitlines()[0]
    except (OSError, subprocess.CalledProcessError, IndexError):
        return "unavailable"


def ctest_evidence(build_dir: Path, verify_inputs: bool = False,
                   junit_path: Path | None = None) -> dict[str, object]:
    if verify_inputs:
        checked = subprocess.run(
            [sys.executable, str(ROOT / "scripts/verify_build_inputs.py"),
             str(ROOT), str(build_dir)], text=True, capture_output=True, check=False
        )
        if checked.returncode != 0:
            return {"build_dir": str(build_dir), "status": "stale_or_unverified_build_inputs",
                    "verification_output": (checked.stdout + checked.stderr).strip()}
    junit = junit_path if junit_path is not None else build_dir / "candidate-qualification.xml"
    if junit.is_file():
        root = ET.parse(junit).getroot()
        cases = root.findall(".//testcase")
        failures = sum(len(case.findall("failure")) + len(case.findall("error"))
                       for case in cases)
        skipped = sum(bool(case.findall("skipped")) for case in cases)
        passed = len(cases) - failures - skipped
        return {"build_dir": str(build_dir),
                "status": "passed" if cases and failures == 0 and skipped == 0 else "failed",
                "passed": passed, "failed": failures, "skipped": skipped,
                "total": len(cases), "junit_sha256": sha256(junit)}
    log = build_dir / "Testing/Temporary/LastTest.log"
    if not log.is_file():
        return {"build_dir": str(build_dir), "status": "not_run"}
    text = log.read_text(errors="replace")
    match = re.search(r"(\d+)% tests passed, (\d+) tests failed out of (\d+)", text)
    if not match:
        return {"build_dir": str(build_dir), "status": "log_only_no_machine_summary",
                "log_sha256": sha256(log)}
    passed = int(match.group(3)) - int(match.group(2))
    failed = int(match.group(2))
    return {"build_dir": str(build_dir), "status": "passed" if failed == 0 else "failed",
            "passed": passed, "failed": failed, "total": int(match.group(3)),
            "log_sha256": sha256(log)}


def conformance_evidence(report_dir: Path) -> dict[str, object]:
    reports = sorted(report_dir.glob("*-report.json"))
    if not reports:
        return {"status": "not_run"}
    results = []
    for path in reports:
        report = json.loads(path.read_text())
        results.append({"report": path.name, "sha256": sha256(path),
                        "result": report.get("result"),
                        "summary": report.get("summary")})
    passed = all(item["result"] == "pass" and item["summary"] is not None
                 and item["summary"].get("fail") == 0 for item in results)
    return {"status": "passed" if passed else "failed", "reports": results}


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "usage: create_candidate_manifest.py <candidate-dir> <build-dir> <wheel>",
            file=sys.stderr,
        )
        return 2
    candidate_dir = Path(sys.argv[1]).resolve()
    build_dir = Path(sys.argv[2]).resolve()
    wheel = Path(sys.argv[3]).resolve()
    prefix = candidate_dir / "audio-sdk-0.1.0"
    archive = candidate_dir / "audio-sdk-0.1.0.tar.gz"
    files = source_files()
    source_digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(ROOT).as_posix().encode()
        source_digest.update(len(relative).to_bytes(8, "big"))
        source_digest.update(relative)
        source_digest.update(bytes.fromhex(sha256(path)))
    report_dir = candidate_dir / "verification"
    suffix = candidate_dir.name.rsplit("-", 1)[-1]
    external_dir = ROOT / f"build/onboarding-consumer-{suffix}"
    artifacts: dict[str, str] = {}
    for relative in (
        "audio-sdk-0.1.0.tar.gz",
        "audio-sdk-0.1.0/include/audio_sdk/provider_v0.h",
        "audio-sdk-0.1.0/include/audio_sdk/session_v0.h",
        "audio-sdk-0.1.0/lib/libaudio_sdk.a",
        "audio-sdk-0.1.0/lib/libaudio_sdk.dylib",
        "audio-sdk-0.1.0/bin/audio_sdk_conformance",
        "audio-sdk-0.1.0/share/audio-sdk/schemas/descriptor.schema.json",
        "audio-sdk-0.1.0/share/audio-sdk/schemas/effective-config.schema.json",
    ):
        path = candidate_dir / relative
        artifacts[relative] = sha256(path)
    for path in sorted(report_dir.glob("*-report.json")):
        artifacts[f"verification/{path.name}"] = sha256(path)
    for path in sorted(report_dir.glob("*-ctest.xml")):
        artifacts[f"verification/{path.name}"] = sha256(path)
    if (report_dir / "python-wheel-tests.json").is_file():
        artifacts["verification/python-wheel-tests.json"] = sha256(
            report_dir / "python-wheel-tests.json")
    for path in sorted(external_dir.glob("*-report.json")):
        artifacts[f"external-conformance/{path.name}"] = sha256(path)
    sanitizer_roots = [ROOT / "build/asan-ubsan", ROOT / "build/tsan"]
    python_report = report_dir / "python-wheel-tests.json"
    manifest = {
        "schema_id": "audio-sdk/candidate-manifest/0.1",
        "candidate_id": candidate_dir.name,
        "contract_version": "0.1",
        "source": {
            "identity_algorithm": "sha256(path-length||path||sha256(file-bytes), sorted all non-build/non-git files)",
            "identity_sha256": source_digest.hexdigest(),
            "file_count": len(files),
        },
        "package": {
            "archive": archive.name,
            "archive_sha256": sha256(archive),
            "install_prefix": str(prefix),
            "artifacts_sha256": artifacts,
        },
        "target": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "compiler": command_version(["clang", "--version"]),
            "cmake": command_version(["cmake", "--version"]),
            "build_type": next((line.split("=", 1)[1] for line in
                ((build_dir / "CMakeCache.txt").read_text(errors="replace").splitlines()
                 if (build_dir / "CMakeCache.txt").is_file() else [])
                if line.startswith("CMAKE_BUILD_TYPE:STRING=")), "unknown"),
        },
        "evidence": {
            "release_ctest": ctest_evidence(
                build_dir, verify_inputs=True,
                junit_path=report_dir / "release-ctest.xml"),
            "asan_ubsan_ctest": ctest_evidence(
                sanitizer_roots[0], verify_inputs=True,
                junit_path=report_dir / "asan-ubsan-ctest.xml"),
            "tsan_ctest": ctest_evidence(
                sanitizer_roots[1], verify_inputs=True,
                junit_path=report_dir / "tsan-ctest.xml"),
            "installed_external_provider": ctest_evidence(
                external_dir, junit_path=report_dir / "external-ctest.xml"),
            "provider_conformance": conformance_evidence(report_dir),
            "python_wheel": ({"path": str(wheel), "sha256": sha256(wheel),
                              "report_sha256": sha256(python_report),
                              "results": json.loads(python_report.read_text())}
                             if python_report.is_file() else
                             {"path": str(wheel), "sha256": sha256(wheel),
                              "status": "not_run_or_no_machine_report"}),
            "limits": ["Linux x86-64 requires a Linux runner",
                       "hosted CI must be run by the hosting service",
                       "callback-safe mode 1 is not advertised"],
        },
    }
    out = candidate_dir / "candidate-manifest.json"
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(out)
    print(source_digest.hexdigest())
    print(sha256(archive))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

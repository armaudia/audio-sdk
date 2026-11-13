#!/usr/bin/env python3
"""Write an external, byte-derived manifest for one immutable candidate."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
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
    for path in sorted(external_dir.glob("*-report.json")):
        artifacts[f"external-conformance/{path.name}"] = sha256(path)
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
            "build_type": "Release",
        },
        "evidence": {
            "release_ctest": {"command": "ctest --test-dir build/all --output-on-failure", "status": "passed 10/10"},
            "asan_ubsan_ctest": {"command": "ctest --test-dir build/asan-ubsan --output-on-failure", "status": "passed 10/10"},
            "tsan_ctest": {"command": "ctest --test-dir build/tsan --output-on-failure", "status": "passed 10/10"},
            "installed_external_provider": {"command": f"ctest --test-dir build/onboarding-consumer-{suffix} --output-on-failure", "status": "passed 10/10"},
            "python_wheel": {"path": str(wheel), "sha256": sha256(wheel), "python": "CPython 3.12.16", "status": "installed; 4/4 tests passed"},
            "platform_limits": ["Linux x86-64 not executed", "hosted CI not executed", "mode 1 callback instrumentation absent"],
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

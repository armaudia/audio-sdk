#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Stage committed source and enforce provider admission for every release archive."""
from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tarfile
from pathlib import Path

from check_provider_intake import check_public_catalog

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = (
    "api", "core", "bindings", "cmake", "conformance", "examples", "scripts",
    "schemas", "docs", "deps", "notices", "LICENSES", "CLA", "licensing", ".github",
    "tests", "third_party", "CMakeLists.txt", "LICENSE", "LICENSE.md", "SOURCE_LOCATION.md",
    "REUSE.toml", "README.md", "CONTRACTS.md", "TEST_PLAN.md", "CONTRIBUTING.md",
    "SECURITY.md", "RELEASING.md", "requirements-build.txt", ".gitignore", ".gitattributes",
)
# Recursive CMake install(DIRECTORY ...) inputs outside the committed source export.
DIRECT_INSTALL_DIRS = ("api/include/audio_sdk", "conformance", "schemas", "notices", "LICENSES")


def stage(root: Path, build: Path, prefix: Path) -> None:
    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", "--no-replace-objects", "-C", str(root), *args])

    if git("rev-parse", "--show-prefix").strip():
        raise ValueError("release packaging requires the SDK Git checkout root")
    head = git("rev-parse", "HEAD").decode("ascii").strip()
    if git("status", "--porcelain", "--untracked-files=no"):
        raise ValueError("release packaging requires clean tracked files; commit changes or use cmake --install for local builds")
    untracked = git("ls-files", "--others", "-z", "--", *DIRECT_INSTALL_DIRS)
    if untracked:
        first = untracked.split(b"\0", 1)[0].decode("utf-8", errors="replace")
        raise ValueError(f"untracked file in CMake release install inputs: {first}")
    cache = (build / "CMakeCache.txt").read_text(encoding="utf-8").splitlines()
    key = "CMAKE_HOME_DIRECTORY:INTERNAL="
    home = next((line.removeprefix(key) for line in cache if line.startswith(key)), "")
    if not home or Path(home).resolve() != root:
        raise ValueError("release build must be configured from this SDK checkout")

    share = prefix / "share/audio-sdk"
    source = share / "source"
    prefix.mkdir()
    source.mkdir(parents=True)
    snapshot = git("archive", "--format=tar", head, "--", *SOURCE_PATHS)
    with tarfile.open(fileobj=io.BytesIO(snapshot)) as archive:
        if any(not (entry.isfile() or entry.isdir()) for entry in archive.getmembers()):
            raise ValueError("release source inventory contains a link or special file")
        archive.extractall(source, filter="data")
    subprocess.run([sys.executable, str(source / "scripts/verify_build_inputs.py"), str(source), str(build)],
                   check=True)
    subprocess.run(["cmake", "--install", str(build), "--prefix", str(prefix)], check=True)
    errors = check_public_catalog(share / "schemas/providers", source, root)
    if errors:
        raise ValueError("\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("prefix", type=Path)
    args = parser.parse_args()
    try:
        stage(ROOT, args.build.resolve(), args.prefix.resolve())
    except (OSError, ValueError, subprocess.CalledProcessError, tarfile.TarError) as error:
        print(f"release staging refused: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

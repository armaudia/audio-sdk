#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Stage a release archive scoped to this task's evidence subtree.

This is a task-local wrapper around the installed SDK release checks. It keeps
the shared `SOURCE_PATHS` admission rules, build-input verification, CMake
install and public-catalog check, but replaces the broad `docs` export with an
explicit file list: the required migration CSV plus this task's evidence tree.
Unrelated merged docs therefore cannot change the archive bytes.
"""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tarfile
from pathlib import Path

TASK_DIR = Path("docs/task-evidence/identity-pcm-and-noop-fixtures")
SCOPED_DOCS = (
    "docs/migration/source-allocation.csv",
    TASK_DIR.as_posix(),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("build", type=Path)
    parser.add_argument("prefix", type=Path)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[3]
    scripts = root / "scripts"
    sys.path.insert(0, str(scripts))
    import stage_release as base  # noqa: PLC0415

    def git(*arguments: str) -> bytes:
        return subprocess.check_output(
            ["git", "--no-replace-objects", "-C", str(root), *arguments])

    if git("rev-parse", "--show-prefix").strip():
        raise ValueError("scoped packaging requires the SDK Git checkout root")
    head = git("rev-parse", "HEAD").decode("ascii").strip()
    if git("status", "--porcelain", "--untracked-files=no"):
        raise ValueError("scoped packaging requires clean tracked files")
    untracked = git("ls-files", "--others", "-z", "--", *base.DIRECT_INSTALL_DIRS)
    if untracked:
        first = untracked.split(b"\0", 1)[0].decode("utf-8", errors="replace")
        raise ValueError(f"untracked file in CMake release install inputs: {first}")
    cache = (args.build / "CMakeCache.txt").read_text(encoding="utf-8").splitlines()
    key = "CMAKE_HOME_DIRECTORY:INTERNAL="
    home = next((line.removeprefix(key) for line in cache if line.startswith(key)), "")
    if not home or Path(home).resolve() != root:
        raise ValueError("release build must be configured from this SDK checkout")

    source_paths = tuple(path for path in base.SOURCE_PATHS if path != "docs") + SCOPED_DOCS
    for path in source_paths:
        if subprocess.run(["git", "--no-replace-objects", "-C", str(root),
                           "cat-file", "-e", f"{head}:{path}"],
                          check=False, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode != 0:
            raise ValueError(f"scoped source path absent at HEAD: {path}")

    prefix = args.prefix.resolve()
    share = prefix / "share/audio-sdk"
    source = share / "source"
    prefix.mkdir()
    source.mkdir(parents=True)
    snapshot = git("archive", "--format=tar", head, "--", *source_paths)
    with tarfile.open(fileobj=io.BytesIO(snapshot)) as archive:
        if any(not (entry.isfile() or entry.isdir()) for entry in archive.getmembers()):
            raise ValueError("release source inventory contains a link or special file")
        archive.extractall(source, filter="data")
    subprocess.run([sys.executable, str(source / "scripts/verify_build_inputs.py"),
                    str(source), str(args.build.resolve())], check=True)
    subprocess.run(["cmake", "--install", str(args.build.resolve()),
                    "--prefix", str(prefix)], check=True)
    errors = base.check_public_catalog(share / "schemas/providers", source, root)
    if errors:
        raise ValueError("\n".join(errors))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.CalledProcessError, tarfile.TarError) as error:
        print(f"scoped release staging refused: {error}", file=sys.stderr)
        sys.exit(1)

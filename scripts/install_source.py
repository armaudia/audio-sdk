#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Include corresponding source and license notices with the native package."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = args.destination
    destination.mkdir(parents=True)
    for name in ("api", "core", "bindings", "cmake", "conformance", "examples", "scripts",
                 "schemas", "docs", "deps", "notices", "LICENSES", "CLA", "licensing", ".github", "tests",
                 "third_party"):
        shutil.copytree(root / name, destination / name,
                        ignore=shutil.ignore_patterns("build", "dist", "__pycache__", "*.pyc", "*.egg-info"))
    for name in ("CMakeLists.txt", "LICENSE", "LICENSE.md", "SOURCE_LOCATION.md", "REUSE.toml",
                 "README.md", "CONTRACTS.md", "TEST_PLAN.md",
                 "CONTRIBUTING.md", "SECURITY.md", "RELEASING.md", "requirements-build.txt", ".gitignore"):
        shutil.copy2(root / name, destination / name)


if __name__ == "__main__":
    main()

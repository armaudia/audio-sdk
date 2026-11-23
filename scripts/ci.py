#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Build and test an installed SDK and Python wheel on a clean runner."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def run(*command: str, cwd: Path | None = None, env: dict | None = None) -> None:
    subprocess.run(command, cwd=cwd, env=env, check=True)


def check_release_gates(root: Path, build: Path, output: Path) -> None:
    # Isolate the missing installed file from the source tree and the real candidate.
    probe = output / "missing-descriptor-install"
    probe.mkdir()
    for name in ("CMakeCache.txt", "runtime-inputs.sha256"):
        shutil.copyfile(build / name, probe / name)
    descriptor = root / "schemas/providers/dsp.highpass80.v0.descriptor.json"
    (probe / "cmake_install.cmake").write_text(
        'file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/audio-sdk/schemas/providers" '
        f'TYPE FILE FILES "{descriptor.as_posix()}")\n', encoding="utf-8")
    for target, args in (("native", ()), ("wasm", ("--wasm",))):
        rejected = output / f"rejected-{target}"
        result = subprocess.run(
            ["sh", str(root / "scripts/package.sh"), str(probe), str(rejected), *args],
            capture_output=True, text=True, check=False)
        if (result.returncode != 1 or rejected.exists()
                or "missing=['speex.ns.v0.descriptor.json']" not in result.stderr):
            raise RuntimeError(f"{target} packaging did not reject the missing descriptor:\n"
                               f"{result.stdout}\n{result.stderr}")
    print("native and Wasm archive gates refused a catalog missing Speex")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("build/ci"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    run(sys.executable, str(root / "scripts/generate_descriptors.py"), "--check")
    run(sys.executable, "-m", "unittest", "discover", "-s", str(root / "tests"), "-p", "test_*.py", "-v", cwd=root)
    api_build = output / "api"
    run("cmake", "-S", str(root / "api"), "-B", str(api_build), "-DCMAKE_INSTALL_LIBDIR=lib")
    run("cmake", "--build", str(api_build), "--parallel", "2")
    run("ctest", "--test-dir", str(api_build), "--output-on-failure", "--timeout", "60",
        "--output-junit", str(output / "api-tests.xml"))
    build = output / "native"
    candidate = output / "candidate"
    run("cmake", "-S", str(root), "-B", str(build),
        "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_INSTALL_LIBDIR=lib")
    run("cmake", "--build", str(build), "--parallel", "2")
    run("ctest", "--test-dir", str(build), "--output-on-failure", "--timeout", "60",
        "--output-junit", str(output / "native-tests.xml"))
    prefix = candidate / "audio-sdk-0.1.0"
    with tempfile.NamedTemporaryFile(dir=root / "docs", prefix="unlisted-audit-", suffix=".f32") as unlisted:
        unlisted.write(b"synthetic packaging probe; not model data\n")
        unlisted.flush()
        run("sh", str(root / "scripts/package.sh"), str(build), str(candidate))
        if (prefix / "share/audio-sdk/source/docs" / Path(unlisted.name).name).exists():
            raise RuntimeError("an untracked docs file leaked into the sealed release")
    print("release source excluded the untracked docs probe")
    check_release_gates(root, build, output)
    external = output / "external"
    conformance = prefix / "share/audio-sdk/conformance"
    run("cmake", "-S", str(conformance / "external_provider"), "-B", str(external),
        f"-DCMAKE_PREFIX_PATH={prefix}", f"-DAUDIO_SDK_CONFORMANCE_DIR={conformance}",
        "-DCMAKE_BUILD_TYPE=Release")
    run("cmake", "--build", str(external), "--parallel", "2")
    run("ctest", "--test-dir", str(external), "--output-on-failure", "--timeout", "60",
        "--output-junit", str(output / "external-tests.xml"))
    wheels = output / "wheels"
    python_source = output / "python-source"
    shutil.copytree(root / "bindings/python", python_source,
                    ignore=shutil.ignore_patterns("build", "dist", "*.egg-info", "__pycache__"))
    run(sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation",
        "--wheel-dir", str(wheels), str(python_source))
    environment = output / "python"
    venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    wheel = next(wheels.glob("audio_sdk-*.whl"))
    run(str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel))
    tests = output / "python-tests"
    shutil.copytree(root / "bindings/python/tests", tests)
    if sys.platform == "win32":
        library = prefix / "bin/libaudio_sdk.dll"
    else:
        library = prefix / "lib" / ("libaudio_sdk.dylib" if sys.platform == "darwin" else "libaudio_sdk.so")
    env = dict(os.environ, AUDIO_SDK_LIBRARY=str(library))
    env.pop("PYTHONPATH", None)
    if os.name == "nt":
        env["PATH"] = str(library.parent) + os.pathsep + env.get("PATH", "")
    run(str(python), "-m", "unittest", "discover", "-s", str(tests), "-v", cwd=output, env=env)
    # Verify normalization independently of the first archive invocation.
    original = candidate / "audio-sdk-0.1.0.tar.gz"
    repeated = candidate / "repeated.tar.gz"
    run(sys.executable, str(root / "scripts/create_archive.py"),
        "audio-sdk-0.1.0", repeated.name, cwd=candidate)
    if original.read_bytes() != repeated.read_bytes():
        raise RuntimeError("normalized archive is not repeatable for identical installed bytes")
    repeated.unlink()
    (candidate / "repeated.tar.gz.sha256").unlink()
    dist = output / "dist"
    dist.mkdir()
    target = f"{platform.system().lower()}-{platform.machine().lower()}"
    archive = dist / f"audio-sdk-0.1.0-{target}.tar.gz"
    shutil.copyfile(original, archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (dist / (archive.name + ".sha256")).write_text(f"{digest}  {archive.name}\n")
    info = json.loads((prefix / "share/audio-sdk/build-info.json").read_text())
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    source_dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=root, text=True).strip())
    artifacts = {line.split("  ", 1)[1]: line.split("  ", 1)[0]
                 for line in (candidate / "audio-sdk-0.1.0.files.sha256").read_text().splitlines()}
    artifacts[original.name] = digest
    (candidate / "candidate-manifest.json").write_text(json.dumps({
        "candidate_id": candidate.name, "source_revision": revision, "source_dirty": source_dirty,
        "package": {"artifacts_sha256": artifacts}, "build": info,
        "qualification": "not_assessed",
    }, indent=2) + "\n")
    (dist / f"audio-sdk-0.1.0-{target}.json").write_text(json.dumps({
        "schema_id": "audio-sdk/ci-package/0.1", "source_revision": revision, "source_dirty": source_dirty,
        "build": info, "archive_sha256": digest,
        "checks": ["native", "installed-c-cxx", "provider-conformance", "external-provider",
                    "installed-python-wheel", "archive-repeatability", "release-provider-catalog",
                    "committed-release-source"],
        "limits": ["No callback-safe guarantee", "No real-model or workload qualification"],
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()

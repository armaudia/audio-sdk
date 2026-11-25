# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Collect separate installed runtime smoke records; never qualify a workload."""

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).with_name("smoke.c").resolve()


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(record, phase, command, cwd):
    args = [str(arg) for arg in command]
    step = {"phase": phase, "argv": args}
    record["steps"].append(step)
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                            errors="replace", timeout=120, check=False)
    step.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    if result.returncode:
        raise ValueError(f"{phase} exited {result.returncode}; see steps")


def probe(prefix, out, native):
    if prefix is None:
        return {"status": "unavailable", "reason": "no extracted package prefix selected"}
    prefix = prefix.resolve()
    record = {"prefix": str(prefix), "steps": [], "inputs_sha256": {}}
    if native and sys.platform != "darwin":
        return dict(record, status="unavailable", reason="macOS host required")
    tools = ("xcrun",) if native else ("emcc", "node")
    commands = {tool: shutil.which(tool) for tool in tools}
    missing = [tool for tool in tools if commands[tool] is None]
    if missing:
        return dict(record, status="unavailable", reason=f"missing tools: {', '.join(missing)}")
    out.mkdir()
    record["cwd"] = str(out)
    try:
        metadata = prefix / "share/audio-sdk/build-info.json"
        library = prefix / "lib/libaudio_sdk.a"
        headers = prefix / "include/audio_sdk"
        inputs = [library, metadata, *sorted(headers.glob("*.h"))]
        if not (headers / "session_v0.h").is_file():
            raise ValueError("missing installed include/audio_sdk/session_v0.h")
        for path in inputs:
            record["inputs_sha256"][path.relative_to(prefix).as_posix()] = sha256(path)
        build = json.loads(metadata.read_text(encoding="utf-8"))
        if not isinstance(build, dict) or build.get("schema_id") != "audio-sdk/build-info/0.1":
            raise ValueError("expected audio-sdk/build-info/0.1")
        record["build_info"] = build
        target = build.get("target")
        if native and target != f"Darwin-{platform.machine()}":
            raise ValueError("expected installed build-info for this Darwin host architecture")
        # Emscripten CMake can report "x86"; the C compile guard checks actual wasm32.
        if not native and not (isinstance(target, str) and target.startswith("Emscripten-")):
            raise ValueError("expected installed Emscripten build-info")

        if native:
            compiler = [commands["xcrun"], "--sdk", "macosx", "clang"]
            flags = ["-DPROBE_APPLE"]
            binary = out / "smoke"
            execute = [binary]
        else:
            compiler = [commands["emcc"]]
            flags = ["-DPROBE_NODE", "-pthread", "-sENVIRONMENT=node", "-sEXIT_RUNTIME=1"]
            binary = out / "smoke.js"
            execute = [commands["node"], binary]
            run(record, "node-version", [commands["node"], "--version"], out)
        run(record, "compiler-version", [*compiler, "--version"], out)
        run(record, "compile-link", [*compiler, *flags, "-std=c11", "-Wall", "-Wextra",
                                     "-Werror", "-I", prefix / "include", SOURCE, library,
                                     "-o", binary], out)
        outputs = [binary] if native else [binary, binary.with_suffix(".wasm")]
        record["outputs_sha256"] = {path.name: sha256(path) for path in outputs}
        run(record, "synthetic-runtime", execute, out)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return dict(record, status="failed", reason=str(exc))
    return dict(record, status="passed", scope="installed static C11 consumer; unpaced mode 2")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-prefix", type=Path)
    parser.add_argument("--wasm-prefix", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="new private directory")
    args = parser.parse_args(argv)
    out = args.output.resolve()
    try:
        out.mkdir(mode=0o700)
    except OSError as exc:
        parser.error(str(exc))

    native = probe(args.native_prefix, out / "native", native=True)
    wasm = probe(args.wasm_prefix, out / "node", native=False)
    report = {
        "tool": "audio-sdk/apple-and-browser-runtime-probe/0.1",
        "probe_sha256": {p.name: sha256(p) for p in (Path(__file__), SOURCE)},
        "host": {"system": platform.system(), "release": platform.release(),
                 "macos_version": platform.mac_ver()[0], "arch": platform.machine(),
                 "python": platform.python_version()},
        "apple_native": native,
        "emscripten_node": wasm,
        "other_apple_targets": {"status": "not_measured", "reason": "macOS host smoke only"},
        "browser_audio_worklet": {"status": "blocked", "reason": "needs a browser-targeted "
                                  "SDK host with AudioWorklet and render/deadline instrumentation"},
        "device_scheduling": {"status": "blocked", "reason": "needs an approved physical-device "
                              "I/O host, calibrated clocks and a paced workload"},
        "workload_support": "not_assessed",
    }
    path = out / "report.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(path)
    return int(any(prefix is not None and result["status"] != "passed" for prefix, result
                   in ((args.native_prefix, native), (args.wasm_prefix, wasm))))


if __name__ == "__main__":
    sys.exit(main())

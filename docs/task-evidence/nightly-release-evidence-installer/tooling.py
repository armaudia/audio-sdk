# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Developer-facing, reproducible installer/probe entry point (task-local).

This is the tooling entry point referenced by this evidence package. It uses
**only already-installed local tools** and the pinned CPython 3.12.16. It never
uses the network, never writes into the SDK worktree, never creates a sealed
release candidate and never registers or enables a provider.

    PYTHONDONTWRITEBYTECODE=1 <PY312> tooling.py --print
        print the exact ordered commands and tool pins (read-only).

    PYTHONDONTWRITEBYTECODE=1 <PY312> tooling.py --run <fresh-dir-outside-worktree>
        execute the same commands in a caller-owned scratch directory, then
        compare deterministic observations with the frozen report constants.

The wheel archive is intentionally *not* asserted byte-for-byte: two builds of
the same checkout produced different digests (recorded in ``report.json``).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from typing import Any

import fixture as fx

HERE = pathlib.Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
PY = fx.PINNED_PYTHON

# Exact commands observed locally. <WT> is the pinned SDK checkout; <WORK> is a
# fresh caller-owned scratch directory outside the worktree; <PREFIX> is the
# scoped install prefix; <DYLIB> is the installed shared library.
COMMANDS: tuple[tuple[str, str], ...] = (
    ("clean-checkout", "git -C <WT> rev-parse HEAD && git -C <WT> status --porcelain"),
    ("configure", "cmake -S <WT> -B <WORK>/build -DCMAKE_BUILD_TYPE=Release"),
    ("build", "cmake --build <WORK>/build --parallel 2"),
    ("ctest", "ctest --test-dir <WORK>/build --output-on-failure"),
    ("install", "cmake --install <WORK>/build --prefix <PREFIX>"),
    ("c-consumer", "cc -std=c11 -Wall -Wextra -Werror -I<PREFIX>/include "
                   "<WORK>/consumer/consumer.c -L<PREFIX>/lib -laudio_sdk "
                   "-Wl,-rpath,<PREFIX>/lib -o <WORK>/consumer/consumer-c && "
                   "<WORK>/consumer/consumer-c"),
    ("cpp-consumer", "c++ -std=c++20 -Wall -Wextra -Werror -I<PREFIX>/include "
                     "<WORK>/consumer/consumer.cpp -L<PREFIX>/lib -laudio_sdk "
                     "-Wl,-rpath,<PREFIX>/lib -o <WORK>/consumer/consumer-cpp && "
                     "<WORK>/consumer/consumer-cpp"),
    ("conformance-speex", "<PREFIX>/bin/audio_sdk_conformance --provider speex.ns.v0 "
                          "--report <WORK>/reports/speex-report.json"),
    ("conformance-highpass", "<PREFIX>/bin/audio_sdk_conformance --provider dsp.highpass80.v0 "
                             "--report <WORK>/reports/highpass-report.json"),
    ("wheel", "PYTHONDONTWRITEBYTECODE=1 <PY> -m pip wheel --no-deps --no-build-isolation "
              "--wheel-dir <WORK>/wheels <WT>/bindings/python"),
    ("venv", "<PY> -m venv <WORK>/venv312"),
    ("wheel-install", "<WORK>/venv312/bin/python -m pip install --no-index --no-deps <WHEEL>"),
    ("installed-tests", "AUDIO_SDK_LIBRARY=<DYLIB> PYTHONDONTWRITEBYTECODE=1 "
                        "<WORK>/venv312/bin/python -m unittest discover "
                        "-s <WORK>/acceptance/tests -v"),
    ("synthetic-probe", "AUDIO_SDK_LIBRARY=<DYLIB> PYTHONDONTWRITEBYTECODE=1 "
                        "<WORK>/venv312/bin/python <WORK>/probe.py"),
)

C_CONSUMER = """#include <audio_sdk/session_v0.h>
int main(void) {
    as_registry_v0 *registry = 0;
    as_error_v0 error;
    as_error_v0_init(&error);
    if (as_registry_create_v0(&registry, &error) != AS_OK) return 1;
    return as_registry_close_v0(&registry) == AS_OK ? 0 : 2;
}
"""

CPP_CONSUMER = """#include <audio_sdk/session_v0.h>
int main() {
    as_result_v0 result{};
    as_result_v0_init(&result);
    return result.abi_major == AS_ABI_MAJOR ? 0 : 1;
}
"""

# Byte-for-byte the probe used for the frozen observation (caller-owned frames,
# two providers, malformed calls, missing optional selections).
PROBE_SOURCE = """import hashlib, json, math, os, struct, sys

def dig(vals):
    return hashlib.sha256(b"".join(struct.pack("<f", float(v)) for v in vals)).hexdigest()

def lcg(seed):
    s = seed & 0xffffffff
    while True:
        s = (1664525 * s + 1013904223) & 0xffffffff
        yield 2.0 * (s / 4294967296.0) - 1.0

FRAMES_N = 8
rng = lcg(31337)
frames = []
for i in range(FRAMES_N):
    if i == 0:
        f = [0.0] * 160
    elif i == 1:
        f = [0.0] * 160; f[0] = 0.5
    elif i == 2:
        f = [0.25] * 160
    elif i == 3:
        f = [0.0] * 160
    else:
        f = [0.05 * next(rng) for _ in range(160)]
    frames.append(f)
inputs_digest = dig([v for f in frames for v in f])

out = {"input": {"frames": FRAMES_N, "samples": FRAMES_N * 160,
                 "digest_f32": inputs_digest}, "providers": {}, "malformed": {},
       "missing_optional": {}}

from audio_sdk import Registry, FRAME_SAMPLES

for provider, delay in (("speex.ns.v0", 160), ("dsp.highpass80.v0", 0)):
    reg = Registry()
    produced, valid_total, flags, src_first, epochs = [], 0, [], [], []
    try:
        with reg.session(provider) as sess:
            for f in frames:
                before = list(f)
                o, r = sess.process(f)
                assert f == before, "caller input mutated"
                produced.extend(o)
                valid_total += r.valid_count
                flags.append(r.flags)
                src_first.append(r.source_first_sample)
                epochs.append(r.epoch)
                assert len(o) == FRAME_SAMPLES
                assert all(math.isfinite(v) for v in o)
            drain = sess.drain()
    finally:
        reg.close()
    out["providers"][provider] = {
        "declared_delay_samples": delay,
        "produced_samples": len(produced),
        "valid_samples": valid_total,
        "drain_frames": len(drain),
        "output_digest_f32": dig(produced),
        "flags": flags,
        "source_first_samples": src_first,
        "epochs": epochs,
        "all_finite": True,
        "caller_inputs_unchanged": True,
    }

reg = Registry()
try:
    with reg.session("dsp.highpass80.v0") as sess:
        ok_o, ok_r = sess.process([0.1] * FRAME_SAMPLES)
        expected_next = ok_r.source_first_sample + FRAME_SAMPLES
        cases = {
            "short_frame": lambda: sess.process([0.0] * (FRAME_SAMPLES - 1)),
            "nonnumeric_valid_count": lambda: sess.process([0.0] * FRAME_SAMPLES, valid_count=1.5),
            "negative_epoch": lambda: sess.reset(-1),
        }
        for name, fn in cases.items():
            try:
                fn()
                status = "no_error"
            except ValueError:
                status = "ValueError"
            except Exception as e:
                status = type(e).__name__
            o, r = sess.process([0.1] * FRAME_SAMPLES)
            out["malformed"][name] = {"status": status, "state_intact":
                r.source_first_sample == expected_next}
            expected_next = r.source_first_sample + FRAME_SAMPLES
finally:
    reg.close()

reg = Registry()
try:
    try:
        reg.session("dsp.nonexistent-optional.v0")
        status = "no_error"
    except Exception as e:
        status = type(e).__name__
    out["missing_optional"]["unknown_provider_id"] = {"status": status}
finally:
    reg.close()

out["runtime"] = {"python": sys.version.split()[0],
                  "library_env": os.environ.get("AUDIO_SDK_LIBRARY", "").split("/")[-1]}
print(json.dumps(out, sort_keys=True, indent=2))
"""


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(work: pathlib.Path, wheel: pathlib.Path | None = None,
           dylib: pathlib.Path | None = None) -> list[str]:
    prefix = work / "install" / "audio-sdk-0.1.0"
    values = {
        "<WT>": str(SDK_ROOT),
        "<WORK>": str(work),
        "<PREFIX>": str(prefix),
        "<PY>": PY,
        "<WHEEL>": str(wheel or (work / "wheels" / "audio_sdk-0.1.0-py3-none-any.whl")),
        "<DYLIB>": str(dylib or (prefix / "lib" / "libaudio_sdk.0.1.0.dylib")),
    }
    result = []
    for _name, command in COMMANDS:
        for key, value in values.items():
            command = command.replace(key, value)
        result.append(command)
    return result


def print_plan() -> None:
    # Print a template: <WORK> stays a placeholder so the plan never implies a
    # build directory inside the evidence/worktree path.
    template = render(pathlib.Path("<WORK>"))
    print(json.dumps({
        "entry_point": str(HERE / "tooling.py"),
        "sdk_root": str(SDK_ROOT),
        "pinned_python": PY,
        "tool_pins": fx.TOOL_PINS,
        "network": False,
        "writes_into_worktree": False,
        "sealed_candidate": False,
        "commands": [{"id": name, "command": command}
                     for (name, _), command in zip(COMMANDS, template)],
    }, indent=2, sort_keys=True))


def _run(command: str, env: dict[str, str]) -> None:
    # Commands are assembled from the pinned COMMANDS constants above; the
    # shell is required because several records use '&&' to chain steps.
    subprocess.run(command, shell=True, executable="/bin/sh", check=True,
                   env=env, stdout=subprocess.DEVNULL,
                   stderr=subprocess.PIPE)


def run(work: pathlib.Path) -> dict[str, Any]:
    resolved = work.resolve()
    if resolved == SDK_ROOT or SDK_ROOT in resolved.parents:
        raise SystemExit("refusing to build inside the SDK worktree")
    if resolved.exists() and any(resolved.iterdir()):
        raise SystemExit("refusing to use a non-empty scratch directory")
    resolved.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    prefix = resolved / "install" / "audio-sdk-0.1.0"
    dylib = prefix / "lib" / "libaudio_sdk.0.1.0.dylib"
    # Source-only writes happen in the caller-owned scratch dir.
    (resolved / "consumer").mkdir(exist_ok=True)
    (resolved / "consumer" / "consumer.c").write_text(C_CONSUMER)
    (resolved / "consumer" / "consumer.cpp").write_text(CPP_CONSUMER)
    (resolved / "reports").mkdir(exist_ok=True)
    (resolved / "acceptance" / "tests").mkdir(parents=True, exist_ok=True)
    (resolved / "acceptance" / "tests" / "test_sdk.py").write_bytes(
        (SDK_ROOT / "bindings" / "python" / "tests" / "test_sdk.py").read_bytes())
    (resolved / "probe.py").write_text(PROBE_SOURCE)

    by_id = dict(zip((name for name, _ in COMMANDS), render(resolved)))
    for name in ("configure", "build", "ctest", "install", "c-consumer",
                 "cpp-consumer", "conformance-speex", "conformance-highpass",
                 "wheel", "venv"):
        _run(by_id[name], env)
    wheels = sorted((resolved / "wheels").glob("audio_sdk-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("expected exactly one built wheel")
    wheel = wheels[0]
    _run(render(resolved, wheel=wheel, dylib=dylib)[11], env)  # wheel-install
    _run(render(resolved, wheel=wheel, dylib=dylib)[12], env)  # installed-tests

    probe_env = dict(env)
    probe_env["AUDIO_SDK_LIBRARY"] = str(dylib)
    outputs = []
    for index in range(2):
        result = subprocess.run(
            [str(resolved / "venv312" / "bin" / "python"),
             str(resolved / "probe.py")], check=True, env=probe_env,
            capture_output=True, text=True)
        outputs.append(result.stdout.encode("utf-8"))
    observed = json.loads(outputs[0])

    build_info = json.loads((prefix / "share" / "audio-sdk" / "build-info.json"
                             ).read_text())
    summary = {
        "head": subprocess.run(["git", "-C", str(SDK_ROOT), "rev-parse", "HEAD"],
                               check=True, capture_output=True, text=True
                               ).stdout.strip(),
        "build_id": build_info["build_id"],
        "wheel_name": wheel.name,
        "wheel_sha256": sha256(wheel),
        "dylib_sha256": sha256(dylib),
        "speex_report_sha256": sha256(resolved / "reports" / "speex-report.json"),
        "highpass_report_sha256": sha256(
            resolved / "reports" / "highpass-report.json"),
        "probe_output_sha256": hashlib.sha256(outputs[0]).hexdigest(),
        "probe_byte_identical": outputs[0] == outputs[1],
        "probe": observed,
        "wheel_byte_reproducible": False,
        "note": "Wheel bytes embed build-time metadata; no byte-reproducible package claim. No nightly publish, signing, target breadth or release claim.",
    }
    frozen = fx.OBSERVED
    summary["deterministic_matches"] = {
        "head": summary["head"] == frozen["clean_checkout"]["head"],
        "build_id": summary["build_id"] == frozen["compile_build"]["build_id"],
        "dylib_sha256": summary["dylib_sha256"]
        == frozen["native_install"]["dylib_sha256"],
        "speex_report_sha256": summary["speex_report_sha256"]
        == frozen["installed_conformance"]["speex.ns.v0"]["report_sha256"],
        "highpass_report_sha256": summary["highpass_report_sha256"]
        == frozen["installed_conformance"]["dsp.highpass80.v0"]["report_sha256"],
        "probe_output_sha256": summary["probe_output_sha256"]
        == frozen["synthetic_runtime_probe"]["probe_output_sha256"],
        "probe_byte_identical": summary["probe_byte_identical"]
        == frozen["synthetic_runtime_probe"]["byte_identical_across_runs"],
        "wheel_name": summary["wheel_name"]
        == frozen["python_wheel"]["wheel_name"],
    }
    summary["deterministic_all_match"] = all(
        summary["deterministic_matches"].values())
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--print", action="store_true",
                       help="print exact commands and tool pins; write nothing")
    group.add_argument("--run", metavar="FRESH_DIR",
                       help="execute the plan in a fresh dir outside the worktree")
    args = parser.parse_args()
    if args.print:
        print_plan()
        return
    print(json.dumps(run(pathlib.Path(args.run)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

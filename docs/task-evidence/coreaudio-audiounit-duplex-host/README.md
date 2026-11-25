# SDK-COREAUDIO-AUDIOUNIT-DUPLEX-HOST · offline callback replay

`audio-sdk/coreaudio-audiounit-duplex-replay/0.1` is a developer fixture,
not a native AudioUnit adapter. Run `replay.py` from this directory in an SDK
checkout or under `share/audio-sdk/source/docs/task-evidence/` in the
extracted native package. It is not installed as a command, linked against
the SDK, or enabled by a provider setting. It uses only the Python standard
library, includes no imported implementation or audio, and cannot open a
microphone or an output device. Installed v0 remains 16 kHz mono with
160-sample frames; there are no API, registry, build or CI changes.

## Provenance and inputs

- SDK base: `cafa74a1c10fc9d5e927e76183e850277288aade`. Required board
  dependencies: `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`, `SDK-FND-PROVIDER`.
- [Duplex clocks proposal](../duplex-clocks/README.md) (`SDK-FND-DUPLEX`,
  integration `3e2192f5676ffe9d54fd5fc5b7c3710b4bb87f41`) informs the
  independent source coordinates, rational mapping and explicit rejection
  of discontinuities. This fixture is not an implementation of that
  proposal: its output stays on the capture clock's nominal 48 kHz grid.
- Historical source: workspace `realtime-audio-library/implementation_record.md`
  (SHA-256 `12b7c17d6ae969cb3e9697f3309667518048f27792b283178d326746e1bbfb81`).
  See the 2026-10-29 variable-slice/device-clock sections and 2026-10-31
  mic-only diagnostic. The historical IOProc used timestamped render
  interpolation and a provisional 20 ms delay; neither hardware behavior
  nor historical timing results transfer to this fixture.

Caller-owned UTF-8 JSON files declare a fixed-rate mono trace per direction:
`origin_ns` (position of source sample zero), `rate_ppm` (within ±1000), and
`slices`. A row is `[first_sample, sample_count, arrival_ns, timestamp_offset_ns]`
with an inclusive **1–4096** sample count. There are at most 64 rows per file.
The clock ID is implicit and fixed: both affine maps target the same
**synthetic monotonic nanosecond domain**, while origins, sample indices,
rates and callback arrivals remain independent. Callback arrival is the
declared time its slice becomes available, not the slice's sample timestamp.
A nonzero timestamp offset injects a deviation from the declared slice
anchor; it does not change rate or silently recalibrate the clock. No
wall-clock time, drift estimator or Mach clock conversion is used.

The host forms full 480-sample capture intervals across slices, reports the
discarded partial tail and makes one immutable decision per complete frame,
at the arrival of its last capture sample's slice. At each capture sample
time `t`, it maps `t − 20 ms` onto the render grid and linearly interpolates
the deterministic render signal `((index mod 2048) − 1024) / 1024`. Capture
provides geometry only; no capture PCM is reconstructed or processed.
`reference_sha256` hashes the exact rational reference samples joined by
newlines, with no trailing newline. Integer render positions require one
sample; fractional positions require both neighbors.

## Reproduce and read the results

From a clean checkout root on a host with Python **3.12.16**, use a fresh,
private directory outside the checkout. `python3.12` below must resolve to
that version. Package verification requires a clean tracked tree.

```sh
umask 077
scratch=$(mktemp -d "${TMPDIR:-/tmp}/sdk-coreaudio-duplex.XXXXXXXX")
mkdir "$scratch/tmp"
export TMPDIR="$scratch/tmp" PYTHONDONTWRITEBYTECODE=1
python3.12 -m venv "$scratch/venv"
export PATH="$scratch/venv/bin:$PATH"
python --version
python -m pip install --require-hashes -r requirements-build.txt
task=docs/task-evidence/coreaudio-audiounit-duplex-host
python -m unittest discover -s "$task" -v
python -m unittest discover -s docs/task-evidence/duplex-clocks -v
python "$task/replay.py" --version
python "$task/replay.py" --capture "$task/capture.json" --render "$task/render.json" > "$scratch/matched.json"
python "$task/replay.py" --capture "$task/capture.json" > "$scratch/missing.json"
shasum -a 256 "$scratch/matched.json"
python scripts/ci.py --output "$scratch/ci"
prefix="$scratch/ci/extracted/audio-sdk-0.1.0"
python -m unittest discover -s "$prefix/share/audio-sdk/source/$task" -v
```

| Control | Expected result |
| --- | --- |
| `capture.json` (`−50 ppm`) and `render.json` (`+50 ppm`), with a 5 μs phase after the model delay | Variable slices produce `[0,480)`, `[480,960)`, `[960,1440)` and discard 73 tail samples. All three pair; clock slope is `20001/19999` render positions per capture sample. Collapsing the rates changes the reference digest. |
| Omitted `--render`, empty trace or reference outside the supplied span | `missing_reference` on affected frames; no padding, extrapolation, hash or substitution. |
| Change the second render slice arrival to `31000001` ns | `late_reference` on frame 0, then two `paired` frames. The missed frame is not revised. Arrival at `31000000` ns is admitted. The offline label uses the trace to distinguish late from absent; only arrived coverage can pair. |
| Render sample gap/overlap, signed timestamp jump or arrival regression | The **entire** render trace is rejected during offline preflight, even if the error is after a usable prefix. Frames report `discontinuous_reference`; no interpolation across a fault, no in-trace recovery. Invalid capture continuity yields no frames and a `capture_fault`. |
| Malformed JSON, duplicate keys, oversized slice or explicit nonexistent file | Input error; CLI exits 2 without a result. Validly encoded adverse traces exit 0 with the recorded failure status, not an assertion that pairing succeeded. |

The matched CLI report (including its trailing newline) has SHA-256
`fea1bf7ed00768c515b2dd5bbc77dd6a640893148dbc3611e4609e3e6be473b2`.
It includes the exact input file digests. The targeted suite also repeats the
command on caller-owned copies outside the checkout. The package build and
installed consumer checks test v0 separately, not native callback execution.

## Device gate — blocked, not tested

Device/microphone/playback access was not authorized for this task and no
physical route was opened or probed. Reopen with explicit clearance for the
exact capture and playback route, runtime and permitted data use, plus a
working native duplex harness on the target device/profile. The historical
one-IOProc harness required the same device ID for capture and render; its
separate built-in microphone and speakers were not a working duplex route
and the later authorized mic-only run does not satisfy this gate.

Before making any device claim, pin the hardware/OS, route, layout, formats,
host-time calibration and implementation, then measure real callback slices
and clock drift, render-mix coverage and physical render-to-capture delay,
callback/complete-frame service and correlated capture-to-output availability.
The historical reliability gate (`acceptance_targets_v3_20261030.md`)
calls for at least **30 minutes per device/profile** with independent paced
producers, route changes, overload, reset and recovery, zero lost or duplicate
accepted frames and ≤0.1% deadline misses. Record p50/p95/p99/max and every
miss; evaluate CPU, peak memory and energy against approved device caps. AEC
or acoustic quality additionally needs a separate rights-cleared cohort,
matched controls and listening clearance if applicable. No device timing,
quality, pacing, realtime-safety, native compile, public benchmark or release
claim follows from this fixture. Exact-head review and hosted quality checks
remain separate from local verification.

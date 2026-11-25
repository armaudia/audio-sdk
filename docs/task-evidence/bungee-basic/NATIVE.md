<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Native Bungee Basic developer reference

Opt-in, task-local continuation of PR #92. This package actually builds and runs
the pinned native Bungee Basic `Stream` and granular APIs on deterministic
synthetic PCM. It is a developer reference over a separately staged source
checkout, **not** an SDK provider, ABI, default, registry or CI change. Nothing
is registered, enabled, shipped as a binary, or called through an SDK callback.

## Provenance and rights

- Source: `data/checkouts/tsm-engines-20261101/bungee`, HEAD
  `61f52bf34be577d189d388772ddfa3696dee77d8`, tree
  `c8edb5f21ad58472d8ce6f635fa3e6c707474ca6`.
- Submodules: `cxxopts 4bf61f0`, `eigen c29c800`, `pffft 02fe771`.
- Bungee `LICENSE` and source headers are MPL-2.0; `cxxopts` is MIT, Eigen uses
  MPL-2.0 for its copied license file, and PFFFT is BSD-like. The staged checkout
  has only the pre-existing untracked `build-rel/`; no tracked vendor file was
  modified. No Bungee file is vendored into this SDK worktree.
- `native_report.json` records file digests, license markers, exact commands and
  host/toolchain. Distribution review and legal approval are **not** claimed.

## Boundary

`bungee_native.cpp` uses variable contiguous input counts `(160, 240, 80, ...)`,
a caller-owned cumulative output clock, a piecewise rate schedule, and a bounded
caller-owned zero tail. This is the proposed elastic PCM boundary used as a
task-local C++ reference only. The installed v0 geometry remains 16 kHz mono
float32 with a 160-sample call; no installed callback or provider is invoked.

The input is a binary-exact 400 Hz triangle with five transient notches. Pitch
and duration are numeric autocorrelation/lag and frame-count proxies, not
listening, speech-preservation or release results.

## Environment

- Host: macOS 27.2, arm64, Apple clang 21.0.0 (`clang-2100.4.1.1`).
- Python: 3.12.16 at `/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3`.
- CMake: 4.4.4 at
  `/Users/htsakanyan/workspace/audio/audioml/cpp-library/pipeline-validation/playback-speed/.venv/bin/cmake`.
  System CMake 3.27.4 is too old for this source.
- Fresh private scratch required; no build artifact is written into the SDK.

## Reproduce

From this directory, with the exact pinned checkout and toolchain above:

```sh
TASK=$PWD
SCRATCH=$(mktemp -d "${TMPDIR}opencode/bungee-native.XXXXXX")
PYTHON=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3
CMAKE=/Users/htsakanyan/workspace/audio/audioml/cpp-library/pipeline-validation/playback-speed/.venv/bin/cmake
CXX=/usr/bin/clang++
BUNGEE_ROOT=/Users/htsakanyan/workspace/audio/audioml/data/checkouts/tsm-engines-20261101/bungee

"$PYTHON" -B "$TASK/run_native.py" \
  --bungee-root "$BUNGEE_ROOT" --cmake "$CMAKE" --cxx "$CXX" \
  --scratch "$SCRATCH/scratch" --report "$SCRATCH/native_report.json"
cmp "$SCRATCH/native_report.json" "$TASK/native_report.json"
cmp "$SCRATCH/native_report.json.sha256" "$TASK/native_report.json.sha256"
```

`run_native.py` fails closed on any source, revision, submodule, status or
license-pin mismatch. It records the full tokenized command list in the report.
Two independent fresh-scratch runs produced byte-identical reports with SHA-256
`f3293f15aa12a56e1c377f56ca93f0284221e1c5dde825ba893de4bfe37a3a42`.

Targeted checks:

```sh
"$PYTHON" -B -m unittest -v test_reference.py test_native.py
"$PYTHON" -B verify.py
```

## Results

Every stream case below used the same 16,003-frame synthetic input and the
`(160, 240, 80)` chunk cycle. Native Bungee output duration matched the
caller-owned target exactly; the five native-mapped transient notches were
located in every case; all output samples were finite. The matched control uses
pitch-changing linear interpolation on the identical source and rate schedule.

| Case | Schedule | Output frames | Native pitch ratio | Control pitch ratio | Drain |
| --- | --- | ---: | ---: | ---: | ---: |
| Identity | `0:1` | 16,003 | 1.000 | 1.000 | 0 |
| Slower | `0:0.8` | 20,004 | 1.000 | 0.800 | 0 |
| Faster | `0:1.25` | 12,802 | 1.000 | 1.250 | 0 |
| Faster | `0:1.5` | 10,669 | 1.000 | 1.481 | 0 |
| Rate changes | `0:1,4800:0.8,9600:1.25,12960:1` | 16,531 | 1.000 | 1.000 | 0 |
| Bounded zero tail | `0:1`, +64 | 16,067 | 1.000 | 1.000 | 64 |

A separate low-level `Stretcher` probe reached `isFlushed()` in 106 grains at
1.25× with finite output. This is a native flush-state check, **not** a `Stream`
end-of-stream claim or a device fill/flush measurement.

## Skips and remaining gates

No rights-cleared unfamiliar speech/music cohort, listening panel, target
runtime callback, DAC or paced playback was used. Silence, rebuffer, drift,
source-timestamp pause/filler policy, deadline budget and final-partial-window
qualification remain unmeasured; no missing result was promoted. Provider intake
and MPL distribution review require a separate opt-in change. This reference
does **not** qualify Bungee Basic for release.

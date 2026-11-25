# SDK-RUBBER-BAND-R3-STREAMING evidence

## Status

**Proposal only, not qualified (`incomplete`, `DEFER`).** No processor is
exposed, no installed v0 behavior changes, and no candidate is promoted by this
evidence. The fixed installed boundary remains 16 kHz, mono, float32, 160
samples per frame. The optional C provider is task-local, default-OFF, unlinked
from all shared SDK targets and unregistered by default.

This bundle is a first-party, fully synthetic, deterministic, frame-causal
streaming time-stretch study. It is an overlap-add (OLA) engine with a bounded
backward alignment search in the style of WSOLA. It is **not** Rubber Band
source, a Rubber Band binary, a model, weights, a licensed runtime, a real
corpus, a listening test, a playback actuator or a release qualification.

- Claimed base: `add40f5cab979995b6114deb2a05302e547c148c`
- Rebased base: `ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d`
- Branch: `swarm/SDK-RUBBER-BAND-R3-STREAMING`
- Scope: `docs/task-evidence/rubber-band-r3-streaming/` only

## What is here

- `reference.py`: stdlib-only deterministic engine, frozen analytic stimuli,
  schedules, rejection codes, source-timestamp policy and C-boundary emitter.
- `fixture.py`: frozen fixture digests and source/boundary pin verification.
- `scorer.py`: report builder and rate-profile scoring. Missing, rejected,
  nonfinite and adverse results are recorded explicitly with `qualifies=false`.
- `contract.json`, `adapter.json`, `provider.json`: strict canonical machine
  declarations for the fixture, adapter and opt-in provider.
- `run.py`: regenerates `report.json`, `report.json.sha256`,
  `provider/expected_vectors.h` and `SOURCES.sha256`.
- `verify.py`: recomputes every source/boundary/fixture pin from the task-local
  inputs, then validates strict canonical JSON, sidecar, manifest, header,
  proposal status, executed invalids, rebuffer interruption/refill and
  identity/reset invariants.
- `test_reference.py`: 32 deterministic unittest cases.
- `provider/`: opt-in consumer, descriptor template and byte-level parity test.

## Model and boundary

The engine uses a 512-sample grain, exact rational Bartlett window, 384-sample
overlap, density-2 synthesis hop of 64 samples, and a strictly causal
32-sample backward search over the current complete grain. The phase is a
1,000,000-denominator accumulator and rate changes are slewed by at most 0.02
per grain. No future sample is read.

The adapter emulates the frozen v0 shape: one 160-sample output frame for every
160-sample input call, with `valid_count` as the only content-length signal.
There is exactly zero alignment lookahead. With this boundary, startup content
appears at output frame 3 (`30 ms` of input frame time), and expansion (`r<1`)
can only be represented as task-local FIFO depth rather than delivered
variable-length audio. The optional C provider completes a task-local protocol
call without inventing a playback actuator. The C cross-check covers process
bytes and frame shape only: it does **not** claim v0 source mapping or
tail/drain conformance. These limits are blockers, not waivers.

## Reproduction

Regeneration was performed with Python 3.12.16 (stdlib only) in a fresh private
scratch copy. The canonical report contains no absolute checkout path, Python
version string, platform string or other environment-dependent field, so a
detached checkout regenerates identical bytes.

Run from this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py
```

`run.py --report` and `run.py --sources` are idempotent and byte-identical on
repeated cold-start runs. The report sidecar is the SHA-256 of the canonical
report text without the trailing newline.

Optional C boundary build, with all SDK build/install output outside the
worktree:

```sh
SDK=<worktree root>
TMP=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/rb3-sdk
cmake -S "$SDK" -B "$TMP/build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMP/build" --parallel 4
ctest --test-dir "$TMP/build" --output-on-failure
cmake --install "$TMP/build" --prefix "$TMP/prefix"

cmake -S provider -B "$TMP/off" -DCMAKE_PREFIX_PATH="$TMP/prefix" \
  -DAS_ENABLE_RUBBER_BAND_R3_STREAMING=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/off" --parallel 2
ctest --test-dir "$TMP/off" --output-on-failure

cmake -S provider -B "$TMP/on" -DCMAKE_PREFIX_PATH="$TMP/prefix" \
  -DAS_ENABLE_RUBBER_BAND_R3_STREAMING=ON -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/on" --parallel 2
ctest --test-dir "$TMP/on" --output-on-failure
```

Board and whitespace checks from the worktree root:

```sh
python3 <workspace>/audio-benchmark-platform/plan/swarm/check.py --task SDK-RUBBER-BAND-R3-STREAMING
git diff --check
git diff --cached --check
```

Task-local REUSE 6.3.0 check:

```sh
uvx --from 'reuse[charset-normalizer]==6.3.0' \
  reuse lint-file $(find docs/task-evidence/rubber-band-r3-streaming -type f)
```

## Results summary

- Python acceptance suite: **32/32** passed on Python 3.12.16 from a fresh
  scratch regeneration and in the worktree.
- SDK baseline CTest: **11/11** passed.
- Consumer with `AS_ENABLE_RUBBER_BAND_R3_STREAMING=OFF`: **1/1** passed; the
  provider is unlinked and unregistered and built-ins are unchanged.
- Consumer with the option `ON`: **1/1** passed; explicit registration,
  duplicate rejection, descriptor/config gating, executed frame rejections,
  78-frame task-local Python/C byte-and-shape parity, final partial window,
  task-local drain completion and reset replay all passed. No v0 source
  mapping or tail/drain conformance is claimed.
- Report SHA-256:
  `7c32b3f127ebe907e786246b0c07aa1cbe3a2d1c06544c6076ae6f4a1556d609`.
- Synthetic C-vector content SHA-256:
  `5717e525060b71b3c72360f2d53111fc1a9a2f6d833a3f005fbcdc0df20fd569`.
- Parity stream: `78` frames, `10,294` delivered content samples, first output
  at input frame `3` (`30 ms`), and `970` undelivered samples in the Python
  model FIFO. The header carries no drain/source-sample conformance macro.
- All four scored stimuli have `12,416` identity samples and `11,264`
  candidate samples versus an expected dynamic-schedule duration of
  `10,864.67` samples. The relative duration error is `+0.0367552310`, which
  fails the proposed 1 ms/s gate; it is recorded, not waived.
- Drift uses the `drift_control` row (`12,416` observed versus `12,473.04`
  expected, `-0.0045730712`), not the scored candidate row.
- Pitch is sampled after mapping the output analysis window back through each
  stretch. Candidate and identity remain `220 → 220 Hz`; the varispeed adverse
  control shifts to `276 Hz` (`+25.45%`).
- Rebuffer control actually interrupts input for `800` samples (`5` frames at
  source `6400`), drains `32` buffered samples during the gap, then resumes at
  source `7200` and refills with `128` delivered samples. No device pacing or
  recovery is measured.
- Final partial frame starts at source `12320` with `137` valid samples; its
  input digest is verified against the analytic stimulus tail. All `18`
  invalid/adverse outcomes are produced by executed rejection paths.
- Whole-clip and 160-frame chunked feeds are byte-identical. Reset replay and
  input-offset behavior are deterministic.
- Source timestamp policy: protected source coverage minimum `0.91375`; no
  listening, intelligibility or audibility measurement is claimed.

## Source pins

`report.json` pins only task-local inputs: `contract.json`, `adapter.json`,
`provider.json`, the opt-in provider CMake/config/descriptor/source/test files.
`verify.py` recomputes every digest from those files and from the frozen
fixtures; a stale pin fails verification instead of being trusted. No mutable
sibling checkout document is hashed, and no absolute path, Python version or
platform string enters the canonical report. The board path/digest is
read-time provenance only and is validated separately with the swarm tool.

## Remaining release gates

1. Versioned variable-frame playback actuator or caller-owned timestamped FIFO
   so sub-unity expansion is outside the frozen fixed-160 boundary.
2. Paced target-device buffer occupancy, fill/flush, deadline, CPU and
   availability telemetry.
3. Rights-qualified unfamiliar speech and music cohorts with matched controls
   and authorized listening/intelligibility scoring.
4. Pinned, rights-cleared exact Rubber Band source or caller-supplied licensed
   runtime with matched parity evidence.
5. Explicit provider intake, license review, versioned public-surface decision
   and independent review before any processor exposure.

No external source, weights, licensed runtime, real corpus or audio device was
used. No shared CMake, CI, contract, public header, descriptor default,
installed provider registration, board, handoff or ruleset file was changed.

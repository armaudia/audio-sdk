<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SONIC — task-local synthetic time-stretch evidence

This directory contains **proposal-only, incomplete, not-qualified** evidence
for a deterministic, fully synthetic pitch-synchronous OLA time-stretch
reference at a protocol-shaped waveform adapter boundary. It is **not** Sonic:
no upstream source, binary, weights, licensed runtime, real corpus, device
measurement, listening result or release claim is present. Decision: **DEFER**;
status `proposal_only_not_qualified`; readiness `incomplete`; qualification
`not_qualified`.

## Exact scope

- Work is confined to `docs/task-evidence/sonic/`. Shared CMake, `CONTRACTS.md`,
  public headers, descriptor registry/defaults, installed v0 behavior,
  board/handoff files, rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  variable-frame playback actuator is installed. The whole-clip and 160-sample
  block profiles are task-local fixtures only.
- `adapter.json` and `provider.json` describe an **unregistered, default-OFF,
  opt-in** developer boundary. There is no C provider, no installed target, no
  descriptor registration and no public API/ABI change. With the provider
  switch OFF the adapter is bit-exact identity.
- No missing result qualifies a candidate. Invalid, nonfinite, out-of-range
  and missing-stimulus cases fail closed with no metrics and are recorded in
  `report.json`.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This disclosure and reproduction guide. |
| `SOURCES.sha256` | Curated SHA-256 pins for external sources, public headers, implementation, manifests and report. |
| `contract.json` | Task contract, rate profile, pins and excluded claims. |
| `adapter.json` | Unregistered, default-OFF protocol-v1 waveform adapter manifest. |
| `provider.json` | Conceptual opt-in provider manifest; no C provider is built or registered. |
| `reference.py` | Deterministic pitch-synchronous Hann OLA engine, source anchoring, fixture generators and report model. |
| `scorer.py` | Dependency-free duration, pitch, transient, envelope, map and playback-buffer metrics. |
| `fixture.py` | Read-only canonical report, frozen fixture digests and cold-start probe. |
| `run.py` | Adapter prototype, report/sidecar generator, source-pin generator and renderer crosscheck. |
| `verify.py` | Strict read-only verifier for pins, JSON, semantics, byte reproduction, licensing and git scope. |
| `check_licensing.py` | Local SPDX/REUSE checks with split identifier literals. |
| `test_reference.py` | 47 deterministic standard-library unit tests. |
| `report.json` | Canonical synthetic evidence report. |
| `report.json.sha256` | SHA-256 of the canonical report bytes. |

## Source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` for
`source:` rows and to the SDK worktree for header rows. Exact digests are in
`SOURCES.sha256`; they are reproduced in `contract.json`.

| Source | Use |
| --- | --- |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | Sonic candidate context and rate-policy background only. |
| `cpp-library/pipeline-validation/playback-speed/README.md` | Prior paced-playback pre-screen context only; none of its timing or WER numbers are imported. |
| `REALTIME_COMPONENT_CANDIDATES.md` | Component-candidate provenance only. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `rate` acceptance profile. |
| `api/include/audio_sdk/provider_v0.h`, `api/include/audio_sdk/session_v0.h` | Public boundary pins, read-only. |
| `audio-benchmark-platform/plan/swarm/TASKS.json` | Mutable board snapshot at read time; provenance only, never a gate or a result. |

Claim base: `add40f5cab979995b6114deb2a05302e547c148c`. The branch was rebased
onto `2bc2a13aa4c5b398933fd9097d09746ce151216e` and all verification was
repeated after the rebase.

## Rate profile application

`VERIFICATION.md` requires source/output mapping, duration, pitch, transient
audibility and playback buffering with 1×, rate changes, unfamiliar speech,
music, silence, rebuffer, drift and the final partial window. This package maps
each item to a **synthetic proxy**:

- **Source/output mapping** — every output sample carries a source sample
  index; five sampled anchors and a monotonicity check are reported.
- **Duration** — a fractional caller clock rounds cumulative
  `source samples / rate`; every 1×, 0.75×, 1.25×, 1.5×, policy, drift,
  rebuffer and final-window case records exact expected and observed lengths.
- **Pitch preservation** — pitch-synchronous grains are repeated or dropped;
  no grain is resampled. A 220 Hz analytic tone is scored with a grid Goertzel
  proxy. A varispeed adverse control intentionally shifts pitch and is
  excluded. These are frequency proxies, not perceived pitch.
- **Transient audibility** — adjacent-delta peak retention and timing error on
  a synthetic impulse train. This is a waveform proxy, not a listening score.
- **Playback buffering** — a caller-owned FIFO model with a 320-sample prefill
  records 160-sample-block occupancy for dynamic, drift and rebuffer profiles.
  No device fill/flush, deadline or availability claim is made.
- **Unfamiliar speech / speech preservation** — speech-like means seeded-noise
  plus analytic harmonics with explicit voiced/pause/filler spans, not real
  speech. Source-anchored RMS ratios are preservation proxies, not WER, MOS
  or comprehension.
- **Music** — a synthetic tone/click surrogate is a **negative control** for
  a speech-oriented reference and never qualifies the candidate.
- **Pause/filler decisions** — every rate anchor is a **source sample
  timestamp**. Voiced spans are never faster than 1.0× (0.9× here); pause and
  filler spans use 1.5×. No pause or filler is inferred from output time.
- **Final partial window** — a 12,737-sample stimulus at 1.25× yields 10,190
  output samples and a final 90-sample valid frame; zero-padded grain tail and
  output digest are explicit.

## Results summary

- Python acceptance suite: **47/47** passed.
- SDK baseline CTest: **11/11** passed after build and install.
- No opt-in consumer CTest applies: no C boundary is included in this package.
- `run.py --report`, `run.py --sources` and `run.py --crosscheck` are
  byte-identical on repeated runs; three cold-start interpreter probes match.
- All 16 synthetic rate cases have exact duration, zero nonfinite samples and
  bounded peaks. Silence stays exactly zero.
- 220 Hz identity ratio is `1.0`; fixed-rate OLA proxies stay within 5% of
  source frequency; the varispeed adverse control shifts to roughly `1.25×`
  and is excluded.
- Source-anchored pause policy maps 12,800 input samples to 12,800 output
  samples with seven observed source boundaries and no underrun in the caller
  FIFO model.
- Drift and rebuffer profiles each map 9,600 input samples to 9,600 output
  samples with exact target lengths.
- Independent OLA renderer crosscheck is byte-identical at all four rates.

Full values, digests, adverse observations and gate reasons are in
`report.json`. Source-reported numbers from the pinned notes are **not**
imported as results.

## Failure controls and adverse cases

- Invalid configuration (zero rate, nonfinite rate, out-of-range rate,
  wrong sample rate/frame size, unknown keys) is rejected before any engine is
  created.
- Nonfinite and out-of-range input samples are rejected with no output metrics.
- Missing or unknown stimulus is blocked with `metrics: null`; no default
  success is synthesized.
- Varispeed is an adverse control because it changes pitch by design.
- Unsmoothed rate steps have a larger waveform boundary proxy than the
  smoothed control; this is recorded as an adverse observation, not a pass.
- Music-like transient retention and every adverse case are marked
  `excluded_from_qualification`.

No gate was weakened to obtain a pass. No listening, WER, device-timing,
resource or release result is hidden in the report.

## Reproduction

From this directory, with Python 3.11.5 and the standard library only:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --crosscheck
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 check_licensing.py
```

The adapter can also be exercised without writing evidence:

```sh
python3 run.py --request request.json --result result.json
```

A request carries `protocol_version`, `operation` (`inspect` or `run`),
`candidate_ref`, `adapter_ref`, `configuration`, and for `run` also
`attempt_id`, `rate` and `samples`. Results are canonical JSON with a trailing
newline and a synthetic-only disclosure.

SDK build/install and baseline test, from the worktree root with build output
outside the task directory:

```sh
SDK=$PWD
TMP=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/sonic-check
cmake -S "$SDK" -B "$TMP/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMP/sdk-build" --parallel 4
ctest --test-dir "$TMP/sdk-build" --output-on-failure
cmake --install "$TMP/sdk-build" --prefix "$TMP/sdk-prefix"
```

Read-only checks from the worktree root:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-SONIC
git diff --check
git diff --cached --check
python3 -m reuse lint
```

## Licensing

Every new Python and Markdown file carries an explicit SPDX header. No Python
body embeds a full identifier token as a string; generators use split string
literals. The repository's `REUSE.toml` already annotates `docs/**` as
aggregate Apache-2.0, and `LICENSES/Apache-2.0.txt` is present. REUSE 6.3.0
lint is part of the verification sequence above.

## Remaining gates

All remain **blocked**; none is satisfied by this package:

1. `authorized_real_listening` — blind listening with a frozen cohort, score
   sheet, consent and independent review.
2. `real_speech_paired_cohort` — permitted paired real speech, transcripts,
   speaker/language stratification and an independent scorer.
3. `target_runtime_pacing_and_buffering` — target-device fill/flush, deadline,
   CPU, memory and separate algorithmic/FIFO/device delay measurement.
4. `provider_intake_and_public_surface` — provider intake, license/rights
   review, versioned public-surface decision and independent review.
5. `upstream_sonic_source_and_rights_review` — pinned upstream source/version,
   notice and patent/license review, local build and independent comparison.

## Final digests

- `report.json` SHA-256: `b4fea82b9bf596075e7a8ea3844651d6f982ea217f8c40498f16918a1d4ac1ec`
- `report.json.sha256` content: `b4fea82b9bf596075e7a8ea3844651d6f982ea217f8c40498f16918a1d4ac1ec`
- Frozen synthetic fixture digest: `258a0d78c59c17d6f1ae786339890a17d281dbfb21d541cc94120c6f75b702c1`
- Canonical report digest: `88cc4fd795983a5b342eb6f6597d460d1e1b53daa0b0f466a54199984c86b780`
- Base commit: `add40f5cab979995b6114deb2a05302e547c148c`
- Rebase base commit: `2bc2a13aa4c5b398933fd9097d09746ce151216e`

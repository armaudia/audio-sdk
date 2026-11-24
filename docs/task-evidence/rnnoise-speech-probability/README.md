# SDK-RNNOISE-SPEECH-PROBABILITY — deterministic synthetic speech-probability evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
an Analysis-profile speech-probability/VAD reference at a v0-shaped analysis
boundary. It is **synthetic, optional, unregistered and OFF by default**. It
changes no installed SDK behavior, public API/ABI, descriptor registry,
registry default, `CONTRACTS.md`, build text, board, handoff, other worktree or
branch. The installed v0 geometry is untouched: **16 kHz, mono, float32, 160
samples per call**.

The reference is **model-free**: a deterministic logistic transform of RMS over
a modeled evidence window. It is **not** RNNoise's neural-network posterior.
No native library, model archive, corpus, licensed runtime, device, download,
listening test or network benchmark is used. The pinned source report is
**context only**; none of its numbers are reused as results here.

## Boundary model

The shipped public `adapters/rnnoise/adapter.json`
declares `output_kinds: ["waveform"]`, `tasks: ["CLN-01"]`, offline mode and a
locally built native library/model archive with verified hashes. It does **not**
expose `speech_probability`. The separate
`cpp-library/pipeline-validation/rnnoise-side-vad/report.md` diagnostic reads
RNNoise's probability through a different native path and reports it at a
single threshold; that path and its assets are not in this task scope.

This fixture therefore models the missing analysis boundary at the public
v0-shaped tap:

- One `speech_probability` event per 160-sample source frame, with exact
  half-open interval `[k*160, (k+1)*160)`, decimal-string sample/epoch/ns fields
  and key `(producer_id, tap_id, epoch, event_id)`. There is no process-global
  latest-event slot.
- The modeled evidence window is 480 samples (one frame of past context, one
  frame of lookahead), so windows overlap three consecutive SDK frames. Events
  are placed by **exact source interval**, never rounded to a hop.
- `available_ns = origin_ns + window_end * 62500` on clock
  `fixture-monotonic-v0`, with `origin_ns = 1767225600000000000` (above 2^53).
  Availability is source-derived, not a wall-clock measurement and not the
  signal timestamp.
- Validity is explicit: `known` events are scored, `unknown` events are retained
  but excluded, `invalid` events are rejected. Invalid analysis is **never**
  relabeled as nonspeech.
- A `speech_event` detection is the union of contiguous frames whose
  probability is `>= 0.5`, with exact source boundaries.
- The task-local `adapter.json` records `registered=false`,
  `enabled_by_default=false`, `descriptor_settings={}` and
  `public_api_abi_change=false`. No provider is compiled, linked or installed.

A standalone energy-VAD control has its own 240-sample window, seed, threshold
calibration and decision pass. Two degenerate controls (always silent, always
speech) bound the confusion matrix. Timing and quality are deliberately kept
apart: the wall-clock pointer is a separate, unpaced, non-qualifying artifact,
and the source-reported observation that RNNoise returns probability from the
same native call means no separate VAD inference cost is added or pooled here.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, expected counts, results, gates. |
| `reference.py` | Deterministic synthetic signal, probability/VAD references, event adapter, metrics, report builder. |
| `run.py` | Regenerates `report.json` (byte-identical) + `report.json.sha256`, or the non-qualifying `runtime-measurements.json`. |
| `report.json` | Canonical machine-readable Analysis report; strict JSON, sorted keys, compact indent, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `adapter.json` | Task-local proposal-only analysis adapter descriptor; unregistered, OFF by default. |
| `runtime-measurements.json` | Unpaced wall-clock pointer; **not** qualifying timing, **not** quality evidence. |
| `test_reference.py` | 25 deterministic unittest checks (no skips, no network). |
| `verify.py` | Read-only pin, strict-JSON, digest, reproduction, licensing and write-scope verification. |
| `SOURCES.sha256` | SHA-256 manifest for all pinned external/boundary files and task-local artifacts. |

## Pinned source and boundary digests (SHA-256)

External `source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
SDK paths are relative to this worktree. All are machine-checked in
`SOURCES.sha256`.

| Path | SHA-256 |
| --- | --- |
| `cpp-library/pipeline-validation/rnnoise-side-vad/report.md` | `bbda960bd85e62ea096cc77e1305506ba9fc4757994a3ae8e64bfb657f3abe40` |
| `adapters/rnnoise/adapter.json` | `6c7ca68df9fe24bf67f249197777674e4bc8f6527bccbb2fcced4637e00abb44` |
| `adapters/rnnoise/run.py` | `4be2dc2f1c76e46b187a9e52c9faab7ff32e805461cf554a3b97fa3410d2993b` |
| `adapters/rnnoise/README.md` | `6c5cfb5c3493f40c1fd43a0fc54b87f590abf3712d3d3cef7c2f7bc16de15b85` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `api/include/audio_sdk/provider_v0.h` (worktree) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` (worktree) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

Source-reported context (pinned, **not** reproduced): three label-balanced
180-second windows; RNNoise probability FN 25.64% / FP 5.44%, Silero VAD FN
22.91% / FP 7.64%; per-meeting values in the pinned report. These are a
threshold/window diagnostic, not endpointing validation or a corpus accuracy
estimate, and are never pooled with the synthetic numbers below.

Pinned base commit `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`.

## Reproduction

From this directory with the pinned interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-RNNOISE-SPEECH-PROBABILITY
```

`run.py report.json` reproduces the committed bytes exactly; `verify.py`
regenerates into memory and compares byte-for-byte. Regenerating
`runtime-measurements.json` intentionally changes its digest because it records
unpaced wall-clock time; the committed bytes are pinned as delivered.

## Expected counts and digests

- Cohort: 200 frames = 32,000 samples = 2.0 s; seeds `20261124` (signal),
  `20261125` (probability), `20261126` (standalone VAD). Fully labeled:
  14,400 speech samples (quiet 6,400, active 8,000) and 17,600 nonspeech
  samples (idle quiet 11,200, idle loud 6,400); 0 unknown.
- Onset frames `[10, 40, 100, 150]`; offset frames `[30, 70, 120, 170]`.
- 200 timestamped probability events, 7 primary detections, 19,520 detected
  samples; exact event coverage of `[0, 32000)`, 0 gaps, 0 overlaps.
- Cross-hop window overlap counts: `[2, 3×198, 2]`; all 200 windows cross an
  SDK frame boundary.
- `report.json` SHA-256: `988e0686c884246aa1c5943588db3125b8dfdc45f766f6b80bbbcd9e6e7e66c1`
  (151,186 bytes).
- `reference.py` SHA-256: `174014cb19b6fff9cf7143dd093ef06ba2a56ebe8751ebc26647ee3cb18079ea`
- `run.py` SHA-256: `5d9cac9442cf97292f47e871ec7b720b50c7ebec9648d59da7fb8b61b2d3056a`
- `test_reference.py` SHA-256: `822450193eaaf3b10684e0b977ee12873c53515dfef049b6cc77340433845bba`
- `verify.py` SHA-256: `bd6920f9d52cd416980caba85d9bd8ad149d04f547ab6b21eeebf95c6b5dad66`
- `adapter.json` SHA-256: `d62b33eb9d86df586c08080bf57f109361c5a63fabdc9127676f9bfc80c8c70a`
- `runtime-measurements.json` SHA-256 (as committed): `a2dcc3c36bf25d7566c3ebb4f49538f5fec50b636c0473c306090ee9754faee9`
- Tests: **25 passed, 0 failed, 0 skipped** (Python 3.12.16).

## Synthetic Analysis results (not a quality claim)

| Condition | TP | FN | FP | TN | FN rate | FP rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RNNoise-style probability @0.50 | 12,960 | 1,440 | 6,560 | 11,040 | 0.100000000 | 0.372727273 |
| Standalone VAD control @0.50 | 8,800 | 5,600 | 6,560 | 11,040 | 0.388888889 | 0.372727273 |
| Always silent control | 0 | 14,400 | 0 | 17,600 | 1.000000000 | 0.000000000 |
| Always speech control | 14,400 | 0 | 17,600 | 0 | 0.000000000 | 1.000000000 |

Stratified FN/FP for the primary condition:

| Stratum | Errors / denominator | Rate |
| --- | ---: | ---: |
| Quiet speech FN | 1,440 / 6,400 | 0.225000000 |
| Active speech FN | 0 / 8,000 | 0.000000000 |
| Onset speech FN | 160 / 640 | 0.250000000 |
| Offset speech FN | 0 / 640 | 0.000000000 |
| Interior speech FN | 1,280 / 13,120 | 0.097560976 |
| Idle-loud noise FP | 6,400 / 6,400 | 1.000000000 |
| Idle-quiet noise FP | 160 / 11,200 | 0.014285714 |
| Near-speech noise FP | 1,120 / 1,920 | 0.583333333 |
| Far-from-speech noise FP | 5,440 / 15,680 | 0.346938776 |

The primary wins on FN rate versus the standalone VAD control
(−0.288888889) and **ties on FP rate (0.0)**; it does not beat that control on
every stratum in an absolute sense: both false-alarm on all 6,400 idle-loud
samples. Seven detection intervals bridge adjacent labeled speech regions, so
matched-detection offset delays can be large (for example `[1600,3200)` has
onset delay +160 and matched offset delay +6,560 samples) because a
false-alarmed noise region merges the runs. Local per-segment onset/offset
delays are reported separately; example `[1600,3200)` local onset +160,
local offset 0. Every delay is in source samples, not physical or availability
latency.

### Honest regressions

Three regressions are recorded verbatim in `report.json["regressions"]` against
the frozen 0.50 threshold on the *same* probabilities:

| Sweep threshold | Metric | 0.50 worse by |
| --- | --- | ---: |
| 0.40 | FN rate | +0.100000000 |
| 0.40 | Balanced error rate | +0.050000000 |
| 0.90 | FP rate | +0.045454546 |

At 0.40 FN falls from 1,440 to 0 with FP unchanged; at 0.90 FP falls from 6,560
to 5,760 with FN rising to 6,560. The frozen threshold is therefore not optimal
on this synthetic cohort. No regression is hidden, and no threshold was tuned
against a real cohort.

## Validity, state, availability and cross-hop

- 7 invalid probes (nonfinite probability, out-of-range value, wrong config
  digest, stale epoch, invalid validity tag, invalid source interval, invalid
  event validity) are each rejected with unchanged stream state. One `unknown`
  event at a known speech frame is retained but contributes **0** additional FN;
  if it had been mislabeled as nonspeech it would have added 160 FN.
- Two sessions with different producer IDs, taps and epochs have disjoint event
  keys and different event digests. A foreign-epoch event is rejected; reset to
  a higher epoch clears events, leaves the other session unchanged and replays
  bit-identically to a fresh epoch-3 session; an old event cannot revive after
  reset; a closed session rejects process.
- Dropping events `p-4-0003` and `p-4-0007` leaves explicit gaps `[3, 7]` with
  18 remaining events; no fill event is fabricated. A foreign epoch-9 event is
  rejected without changing the count.
- 200 events cover `[0, 32000)` exactly once; `available_ns` is monotonic
  non-decreasing, serialized as decimal strings and derived from the window
  end, not the signal timestamp. All 200 evidence windows cross an SDK frame
  boundary; overlap counts are exact (`[2, 3×198, 2]`).

## Runtime envelope (non-qualifying, separated)

`runtime-measurements.json` records unpaced `time.perf_counter` observations for
this Python reference on this host: stream wall about 0.007 s for 200 frames;
median per-call about 0.021 ms (primary) and 0.012 ms (standalone VAD);
`deadline_ns = null`, `paced = false`, `qualification_status = blocked`.
No native probability inference is measured, no standalone-VAD cost is pooled
with it, no quality metric appears in that file, and no timing value enters any
quality metric. These are neither target-device, paced, deadline, CPU, memory
nor release evidence.

## Gates and reopening conditions

`no_missing_result_qualifies_candidate = true`: any blocked gate, failed
control or missing metric keeps the candidate `not_qualified`. Status is
`proposal_only_synthetic_incomplete`.

| Gate | Status | Exact reopening condition |
| --- | --- | --- |
| `native_probability_boundary` | blocked | Pin native library/model hashes, expose `speech_probability` at a reviewed adapter boundary, and rerun the frozen cohort with independent scoring. |
| `matched_labeled_cohort` | blocked | Freeze a rights-qualified labeled cohort, candidate outputs and an independent scorer before any accuracy claim. |
| `endpointing_validation` | blocked | Run independently reviewed endpointing validation on permitted speech with an agreed delay budget. |
| `target_runtime_timing` | blocked | Measure the exact installed build on the target under pacing, load and deadline budgets with independent timing. |
| `provider_intake` | blocked | Complete opt-in provider intake with OFF default, empty descriptor settings, SPDX headers and independent review. |

No real weights, downloads, licensed runtime, corpus, listening result,
installed-provider change, public-surface change or shared-source change is
used. All files are confined to this task-local evidence directory.

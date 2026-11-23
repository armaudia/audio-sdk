# SDK-PIPE-CONTROL · identity loopback, explicit drain and session switch

**Status: proposal-only, model-free, synthetic and `incomplete`.** This is one
task-local recipe/host example and its evidence. It is not an SDK provider,
engine plugin, public API/ABI change, installed native behavior, release
candidate, target-device result, paced-workload result, corpus/weight evaluation
or audio-quality claim. The SDK v0 boundary is fixed at **16 kHz mono float32,
160-sample frames**. No public header, `CONTRACTS.md`, `CMakeLists.txt`,
descriptor, registry default, installed behavior or file outside
`docs/task-evidence/pipe-control/` was changed.

The Python executor is a deterministic reference model; an offline, stdlib-built
wheel is installed with `pip --no-index` and consumed by an external probe to
show that a third-party package can supply the identity providers and recipe
bytes without any in-tree import.

Pinned base: `0673cb354cceb66f2f71faf9af7703b5a5d2fcfa`. Branch:
`swarm/SDK-PIPE-CONTROL`. Reviewer: `reviewer-pipe-control`.

## Scope and source pins

| Source (relative to `/Users/htsakanyan/workspace/audio/audioml/`) | SHA-256 | Use in this fixture |
| --- | --- | --- |
| `cpp-library/src/core/recipe.cpp` | `3edea6d4fdfe11a244fab94c3fdde8d33f4435c8001559a808e761dbb41015d9` | Frozen preset stage shape: identity preset has exactly one `identity` capture stage; empty recipes, unknown stages, analysis-in-capture, duplicate instances and bad render targets fail validation. The model mirrors the admission ordering and fail-before-session policy without changing C++ sources. |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Buffered submit/pull, exact `consumed_count`/`produced_count`/`valid_offset`/`valid_count`, `source_first_sample`, half-open source intervals, epochs, drain/EOS, close, cancellation, reset, clocks, queue capacity and no automatic fallback. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Pipeline profile: control plus stage-removed ablation, failure policy, lifetime, end-to-end clock/buffer behavior, asset scope and paced-workload limits; stage timing separated from end-to-end availability. |

The pin digests are asserted by `test_pins_recipe_files_and_report_identity`
against the read-only workspace files when present, and are embedded in
`report.json` as `source_pins`.

## Task-local files

| Path | Role |
| --- | --- |
| `fixture.py` | Deterministic generator, recipe validation/admission, buffered reference session, canonical report builder and source pins. |
| `recipe.json` | Frozen primary recipe: `input → identity → output`, one registered identity stage, zero external assets. |
| `fallback_recipe.json` | Frozen second-provider recipe used for the planned switch and host fallback. |
| `generate_report.py` | Regenerates `report.json` and `report.json.sha256` from deterministic scenarios. |
| `report.json` | Machine-readable canonical result with counts, intervals, digests, ablations, adverse controls, clock/buffer data and explicit `incomplete` qualification. |
| `report.json.sha256` | SHA-256 sidecar for `report.json`. |
| `build_wheel.py` | Byte-reproducible stdlib-only wheel builder for the third-party fixture. |
| `third_party/src/pipe_control_fixture/` | Installed third-party identity provider objects and their own recipe copies. |
| `third_party/consumer_probe.py` | External consumer run from a temporary directory outside the source tree. |
| `test_fixture.py` | 15 offline unit/acceptance tests, including the installed-consumer probe. |
| `README.md` | This scope, pin, reproduction, digest, blocker and non-claim record. |

## Proposed control

* **Admission**: a recipe must name at least one capture stage with a unique
  instance, a registered provider, matching stage ID/delay/cost, fixed v0
  format, ordered ports and no assets. A missing identity stage fails with
  `rejected_missing_stage` before a session exists. An unregistered provider
  fails with `rejected_unavailable_stage`.
* **Input → identity → output**: `submit` accepts a 160-sample padded frame and
  returns `consumed_count=160`, `produced_count=0`. Identity transform is a
  float32 round-trip; `pull`/`drain_next` return one 160-sample output frame
  with `source_first_sample = first_input_sample - 0`, `valid_offset=0` and
  `valid_count` equal to the accepted source count. A final partial frame is
  zero-padded by the caller and flagged `FINAL_INPUT`/`FINAL_PADDING`; only the
  valid prefix is delivered.
* **Epochs and sessions**: session A uses provider
  `third_party.identity.v0` at epoch `11`; session B is a fresh session for
  `third_party.fallback_identity.v0` at epoch `12`, with independent queues,
  counters, state and digest. Switching is drain → EOS → close A → create B;
  there is no hot swap. Stale-epoch and duplicate-first-sample submissions are
  explicitly rejected with zero acceptance.
* **Host fallback**: after an explicit cancellation, the host discards the old
  session and opens a fresh fallback identity session with a strictly greater
  epoch. No automatic provider substitution exists.
* **Lifetime/failure policy**: `prepared → processing → draining → drained →
  closed`; cancellation moves to `cancelled → closed`; a backend port failure
  moves to `needs_reset` and requires a higher-epoch reset or a fresh session.
  Close before drain/cancel is rejected; a forced close records abandoned
  intervals. Repeated close is harmless; a stale handle is not simulated.
* **Clock and buffers**: one synthetic monotonic stream origin `1_000_000_000
  ns`, 62,500 ns/sample and 10,000,000 ns/frame. Declared availability is
  source-complete time plus a **declared** 25,000 ns stage cost. The three-frame
  output queue has capacity 3; a fourth submit is rejected with
  `rejected_queue_full`, `consumed_count=0`, high-water 3 and no drops.
  Stage cost is assessed as an independent declared attribute and is never used
  as, or inferred from, measured end-to-end availability.
* **Assets**: zero external assets, no weights, downloads, licensed runtimes,
  corpora, microphones or target-device access.

## Reproduction

From the worktree root:

```sh
task=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PIPE-CONTROL/docs/task-evidence/pipe-control
cd "$task"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
PYTHONDONTWRITEBYTECODE=1 python3 generate_report.py
python3 -m json.tool report.json >/dev/null
python3 -m json.tool recipe.json >/dev/null
python3 -m json.tool fallback_recipe.json >/dev/null
shasum -a 256 \
  /Users/htsakanyan/workspace/audio/audioml/cpp-library/src/core/recipe.cpp \
  /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/audio-sdk/CONTRACTS.md \
  /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/VERIFICATION.md
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-PIPE-CONTROL
```

`generate_report.py` rewrites the same bytes when inputs are unchanged; verify
with `git diff --exit-code -- docs/task-evidence/pipe-control`. The installed
probe uses only a temporary pip target and writes nothing into the worktree.

Observed result (macOS arm64, Python 3.11.5, pip 25.3): **15 tests passed, 0
failed, 0 skipped** in about `0.5 s`; all JSON files parse; the board checker exits
0 and returns `SDK-PIPE-CONTROL` as `in_progress` for `agent-pipe-control`.

## Expected counts and digests

| Artifact / property | Expected value |
| --- | --- |
| `recipe.json` file / canonical recipe digest | `d9581a6ee806ec5afcae8bad1c99761ca604fcfb2770ab7b0eb9ded03dbed7c3` |
| `fallback_recipe.json` file / canonical recipe digest | `b7bbfb8d798e0f376b1d05cd0013b6e65ab5e7db89130e2e422d36b185649192` |
| `report.json` file / canonical report digest | `64428914ee08309ab0bb3e18eec739d59f543711f342e488673ddd6246fe21ec` |
| Installed third-party source digest | `53397ac16064e748a24526bc80fcbacd5d4a5fb30484ee17bb04ed30dbf4f7ee` |
| Installed fixture wheel | `ba7c3a97346fd888628d05c6d862b281573b0f62c8d52312ca44f9bf0a6d91ae` |
| Baseline input / delivered-valid f32 bytes | `9c6165076289d999de0a523ecacc83a840f74edf1dcb9c2a59f1c34756355ff2` |
| Produced padded f32 bytes (480 samples) | `5778e7cafee61690e49a898ad8f2f0174b5ddef19f6ab23fca642c4411451ebc` |
| Switch session A / B delivered f32 bytes | `57fbfb33843af2296884066badc29d08e672a41101b527b0c0c3b4b574d535e3` / `40ae88f38d85bbb629a3b14d944f12ab345e16012cf07219cd07cfd8655be4a7` |
| Switch combined 714 delivered samples | `f815d34666505ecc0d85796145df3dad57a9bcef23b4a813fa0f02537bf39167` |
| Baseline accepted = delivered valid samples | `357` (frames `160/160/37`, produced padded samples `480`) |
| Switch accepted = delivered valid samples | `714` across 2 sessions/2 providers |
| Cancellation abandoned / fallback delivered | `320` / `160` |
| Adverse controls / installed probe runs | `10` / `2` identical outputs |

Baseline accepted and delivered intervals are exactly
`[9007199254740993,9007199254741153)`,
`[9007199254741153,9007199254741313)` and
`[9007199254741313,9007199254741350)`. Session B continues at
`9007199254741350`; the interval union is disjoint, with no overlap, duplicate
or old-epoch sample accepted. Cancellation abandons `[0,160)` and `[160,320)`;
fallback epoch `32` delivers only `[1000,1160)`.

Installed external probe output (twice, byte-identical):

```json
{"accepted_samples":"357","combined_delivered_f32_digest":"f815d34666505ecc0d85796145df3dad57a9bcef23b4a813fa0f02537bf39167","contract":"audio-sdk/session-loopback-control/0.1","delivered_valid_f32_digest":"9c6165076289d999de0a523ecacc83a840f74edf1dcb9c2a59f1c34756355ff2","delivered_valid_samples":"357","fallback_recipe_digest":"b7bbfb8d798e0f376b1d05cd0013b6e65ab5e7db89130e2e422d36b185649192","fixture_id":"third-party/pipe-control-fixture/0.1","fixture_source_digest":"53397ac16064e748a24526bc80fcbacd5d4a5fb30484ee17bb04ed30dbf4f7ee","input_f32_digest":"9c6165076289d999de0a523ecacc83a840f74edf1dcb9c2a59f1c34756355ff2","installed":true,"recipe_digest":"d9581a6ee806ec5afcae8bad1c99761ca604fcfb2770ab7b0eb9ded03dbed7c3","report_digest":"64428914ee08309ab0bb3e18eec739d59f543711f342e488673ddd6246fe21ec","status":"proposal_only_synthetic_incomplete"}
```

## Pipeline profile coverage and controls

| Profile requirement | Task-local evidence |
| --- | --- |
| Apply recipe stage ordering and acceptance | `recipe.json` and `fallback_recipe.json` declare one ordered audio path; `validate_recipe` enforces the pinned v0 format, unique instances, registered stage ID/delay/cost, port order and empty assets before session creation. |
| Control and stage-removed ablations | Control admits the full identity recipe (`ok`); `identity_stage_removed` returns `rejected_missing_stage` with 0 sessions; `provider_unavailable` returns `rejected_unavailable_stage` with 0 sessions. |
| Failure policy | Unknown/missing stages fail admission; port failure at source interval `[160,320)` returns `rejected_failing_port`, blocks process/drain with `rejected_needs_reset`, then a higher-epoch reset succeeds. No automatic fallback. |
| Lifetime | Prepared/processing/draining/drained/closed, cancellation and forced-close abandonment, lease outstanding checks, EOS repetition, idempotent close and fresh-session switch are tested. |
| End-to-end clock and buffer behavior | Synthetic origin/period/availability values are recorded per frame; declared stage cost is separate. Queue capacity 3, high-water 3, zero-consumption full rejection and no drops are recorded. |
| Asset scope and paced workload | Zero assets and no model/download/runtime. Paced workload, target device, physical availability and listening/quality are explicitly `blocked_not_measured`, not passes. |
| Stage timing independent of availability | `clock_and_timing.measured_stage_time_ns` and `measured_end_to_end_availability_ns` are `null`; the declared 25,000 ns stage cost is not derived from source timestamps or reported as measured availability. |

Adverse results (all non-empty; a missing result never qualifies a candidate):
`nonfinite_input → rejected_nonfinite_input`,
`nonzero_final_padding → rejected_bad_padding`,
`partial_without_final_input → rejected_bad_frame`,
`short_frame → rejected_bad_frame`,
`unknown_flags → rejected_bad_frame`,
`wrong_first_sample → rejected_bad_frame`,
`wrong_epoch → rejected_stale_epoch`,
`process_after_final → rejected_bad_frame`,
`invalid_metadata_rate → rejected_bad_format`,
`invalid_metadata_queue → rejected_bad_format`. Duplicate and stale switch
attempts are `rejected_bad_frame` and `rejected_stale_epoch`; post-close
submit/pull are `rejected_closed`.

## Blockers, deferrals and explicit non-claims

* **Blocked — paced/real-device support**: no paced workload, deadline, CPU
  load, backpressure-under-load, queue-timing, microphone, acoustic or target
  device measurement was performed. The declared clock is synthetic; source
  timestamp subtraction does not prove physical availability. Status remains
  `blocked_not_measured`.
* **Blocked — native/API qualification**: no C build/CTest, header, ABI,
  descriptor, registry, installed native consumer or public v0 behavior was
  changed or tested. The installed consumer here is a third-party Python wheel
  fixture, not an SDK plugin.
* **Deferred — real audio/assets**: no corpus, real weights, downloads,
  licensed runtimes, model inference, listening test or quality score exists.
  Asset scope is deliberately empty.
* **Not claimed — stage timing or end-to-end availability**: the 25,000 ns is
  a declared model attribute; it is neither measured stage execution time nor
  measured end-to-end availability. Pacing/backpressure under load is not
  inferred from the capacity-3 synthetic control.
* **Not claimed — release**: no built-in identity provider, graph/engine API,
  hot swap, automatic fallback, default change, board/handoff edit, PR merge or
  public release qualification is implied by this fixture.

Reopen only with an exact scoped decision and digests for a native
implementation, a measured paced/target-device workload with explicit clocks
and buffer accounting, or a real asset/corpus qualification that preserves the
fixed v0 boundary.

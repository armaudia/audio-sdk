# SDK-SILERO-VAD-PAUSE-DURATION-RULES — task-local synthetic Rate-profile evidence

Proposal-only, incomplete and **not qualified** evidence for
`Silero VAD + pause-duration rules`. The acceptance profile is **Rate** as
assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`.

This package applies the Rate profile to a frozen synthetic probability trace
and a deterministic pause-duration controller. It does **not** load a Silero
model, use a vendor wheel or runtime, read or write audio, render playback,
measure a device clock or callback deadline, conduct listening, benchmark the
SDK, or make a release claim. Every interval below is a half-open coordinate in
a synthetic fixture; every timestamp uses `fixture-monotonic-not-device`.

## Boundary

- Documented public v0 geometry only: 16 kHz, mono, float32, 160 samples/call;
  the final synthetic window is a 37-sample partial frame. No SDK callback is
  invoked and installed v0 behavior is unchanged.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `processor_exposure=false`.
- No C provider, descriptor, registry entry, shared CMake change, default
  change, board or handoff write. Only this task-local evidence directory is
  added.
- Evaluation fixture and any future production callback path are distinct; no
  production callback is implemented.

## Rate acceptance profile application

`report.json.rate_profile` records the pinned profile source, the exact rate
cases (`1`, `4/5`, `1.25`), the policy that active speech stays at factor 1 and
pause intervals are scheduled at `1/rate`, and the two measurements that remain
unmeasured without rendered audio: pitch and transient audibility. Those are
written as `null`/`not_measured_*`, never as passing proxies.

For every one of the nine synthetic conditions and all three rate cases,
`conditions.<condition>.<case>` records:

- `source_interval` and `output_interval` as exact half-open sample pairs;
- `event_intervals`: all accepted 160-sample frames plus the final partial;
- `pause_decisions`: every speech, pause and unknown run with its source start,
  source end, duration, decision, trim interval and retained samples; unknown
  validity is never treated as nonspeech and is always retained;
- `mapping`: source → output intervals per kept segment with exact rational
  ideal length and error (`error_samples` is a fraction string, not a rounded
  float);
- `word_spans` and `word_span_overlap_samples`: the synthetic word-span proxy
  used to expose pause-trim damage; it includes an 80 ms trailing tail after
  each speech segment and is not a transcript or human label;
- `speech_preservation_fraction`, `final_partial` with its exact source
  coordinates and fixture `available_ns`, and explicit `pitch_status` and
  `transient_audibility` fields.

The Rate-profile cases covered by the fixture are 1×, rate changes (0.8× and
1.25×), unfamiliar speech, music, silence, rebuffer, drift and the final
partial window. `playback_buffering` records only deterministic queue
accounting (initial fill of 3 frames, one-frame consume tick, injected rebuffer
event, tail drain and rejected stale positions). No target device, deadline or
renderer result is claimed.

## Controls and adverse cases

- `controls.identity`: no pause action; source interval maps exactly to the
  output interval and word-span overlap is zero.
- `controls.named_baseline`: `unguarded_500ms_pause_trim`, the risk flagged in
  the source research. Its synthetic overlap and speech-preservation loss are
  reported. The published 1172 s / 282 s finding is included only as
  `source_reported_not_reproduced`, never reproduced or promoted to a candidate
  result.
- `controls.candidate`: guarded 120/360 ms thresholds with 200 ms retention.
  `regressions` records the candidate's compression tradeoff and the baseline's
  overlap verbatim; no losing condition is hidden.
- `adverse` is produced by actually calling the validators: malformed configs
  fail before controller creation; malformed frames, stale epoch/position,
  invalid validity and lifecycle misuse fail with `state_unchanged=true`.
- Three fresh interpreter processes hash identical canonical core bytes; the
  report and its SHA-256 sidecar regenerate byte-for-byte with the pinned
  Python 3.12.16.

## Pinned sources and boundary

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless noted.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile. |
| `research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Task evidence row 23: pause-trim overlap risk. |
| `research/tsm-followup-20261101/root-baselines/REPORT.md` | `63ea22bd4d027467a1abe97639f7c9ff6e00cdc2c6c753a52c2bd5e4028bab85` | Pause-trim sweep details; provenance only. |
| `adapters/silero-vad/adapter.json` | `45222fd98fe1bd76550d0529cdaa442783807a727880b168d7879eca4f54a60a` | Upstream adapter identity; no runtime or weights used here. |
| `CONTRACTS.md` (SDK boundary) | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract. |
| `api/include/audio_sdk/provider_v0.h` (SDK boundary) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table. |
| `api/include/audio_sdk/session_v0.h` (SDK boundary) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade. |

`SOURCES.sha256` enumerates every source, boundary and task-local artifact pin.
`verify.py` fails closed on a missing, stale, malformed or duplicated pin, on a
non-canonical report, on a stale digest sidecar, on non-finite/duplicate JSON
keys and on any worktree change outside this directory.

## Files

- `contract.json` — task-local proposal manifest; scope, boundary and gates.
- `reference.py` — synthetic probability fixture, interval controller and report model.
- `run.py` — regenerates `report.json`, `report.json.sha256` and `SOURCES.sha256`.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — SHA-256 manifest for pinned boundaries and task files.
- `test_reference.py` — Python unittest acceptance suite.
- `verify.py` — read-only pins/JSON/reproduction/licensing/scope verifier.
- `*.json.license` / `SOURCES.sha256.license` — REUSE sidecars for generated JSON artifacts.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-SILERO-VAD-PAUSE-DURATION-RULES
```

`run.py report.json`, `run.py sources` and `run.py all` are idempotent. The
canonical report digest is the content of `report.json.sha256`; the manifest
digest is the SHA-256 of `SOURCES.sha256` itself.

## Gates

All six gates remain blocked: rights-cleared real cohorts, independent listening,
target playback pacing/deadline, opt-in provider intake, explicit public default
selection and exact approved external reference parity. Missing evidence never
qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.

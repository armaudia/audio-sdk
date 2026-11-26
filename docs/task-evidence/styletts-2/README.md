<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-STYLETTS-2 — task-local feasibility evidence

Task-local, proposal-only, **incomplete** and **not_qualified** feasibility
evidence for `StyleTTS 2` (`component_id=styletts-2`). The assigned acceptance
profile is **Voice**. Machine-readable decision: **DEFER**;
`status=proposal_only_asset_intake_incomplete_not_qualified`;
`evidence_status=incomplete`; `qualification_status=not_qualified`. No result
in this package qualifies the candidate.

This package does **not** import, load, link, execute, copy, vendor or download
a StyleTTS 2 implementation, checkpoint, vocoder, text frontend, aligner,
dataset or listening panel. It does not read, write, render or play real audio;
does not measure a device clock, callback deadline, first-output/tail latency or
buffer occupancy; does not benchmark the SDK; and makes no release claim. The
synthetic identity control is at the installed v0 geometry: 16 kHz, 1 channel,
float32, 160 samples per frame. It is **not StyleTTS 2 output**.

## Boundary

Installed v0 geometry is unchanged and documented only:
`16000 Hz`, 1 channel, `float32`, 160 samples per call. No provider, default,
descriptor, registry entry, ABI, CONTRACTS, shared-build or CI file is changed.
The adapter/provider remains OFF, unregistered and not exposed. No
caller-supplied asset is embedded, downloaded, parsed as source or executed;
the package only models a strict metadata/byte-hash intake shape. Board,
handoff, reviewer dispatch and release state are untouched.

## Decision, gates and blockers

All gates RG-01 through RG-08 are **blocked** and `qualifies=false`: exact
runnable source; exact assets and rights; installed-v0 boundary intake;
permitted voice cohort; separate text/semantic, identity/similarity and
naturalness results; alignment and timing; streaming/source-speech claim gate;
and public admission review. `DEFER` is before `opt_in_adapter_exposure`.
Exact blockers B-01 through B-04 and their reopening conditions are in
`report.json` and `contract.json`.

Source-reported claims are kept as provenance only. The pinned matrix marks
StyleTTS 2 unavailable/blocked with no local model/checkpoint adapter and notes
the available task is expressive TTS rather than streaming source-speech
enhancement. The transform-space audit marks it researched but not run. The
transform-spatial trials mark it not run and require a separate task-matched
TTS/VC benchmark. None of those records is promoted to a candidate result.

## Synthetic identity control

The synthetic control is a deterministic fixed integer-micro PCM sequence over
16000 samples at 16 kHz mono float32 geometry, split into typed
silence/voiced_synthetic intervals for structural accounting only. The identity
control is byte-identical by digest and has duration ratio 1. It is not speech,
not real audio, not TTS, not voice conversion, and not a StyleTTS 2 result.

## Caller-supplied asset contract (not satisfied)

Seven external assets are required for reopening: source revision, model
checkpoint, vocoder/decoder, runtime lock, rights/consent record, rights-cleared
voice cohort manifest and matched reference output. Each must be caller-owned,
referenced by exact id, byte count and lowercase SHA-256, with licence,
consent and output-use review sidecars. The shape-only verifier rejects
duplicate keys, field-set drift, missing/empty identifiers, bad digests,
relative or traversal paths, duplicate paths, embedded storage, absent bytes,
byte-count mismatch and hash mismatch. A hash-matched placeholder is still
shape-only and never qualifies. No such assets are present in the workspace or
SDK worktree; absence is not a runtime, rights or quality result.

## Reproduction

```text
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 -m reuse lint
git diff --check
```

`verify.py` is read-only and fails closed on duplicate-key/nonfinite JSON,
stale pins, stale canonical artifacts, stale README digest tables, unexpected
files, license gaps, whitespace damage, unavailable scope base, branch-diff
changes outside this task prefix (`base_out_of_scope_change:<path>`) and a dirty
diff check. The strict scope gate resolves the newest merge-base of HEAD with
`origin/main` or `main`; if neither ref exists it emits `scope_base_unavailable`.

Canonical artifacts are `report.json`, `report.json.sha256`, `contract.json`
and `SOURCES.sha256`. The board link pins only stable row identity, never the
mutable full `plan/swarm/TASKS.json`.

Base commit: `26bc48c58f9d69571571fa651862dcbe0fe1172d`.
Task ID: `SDK-STYLETTS-2`.

<!-- digest-table: source -->
| Pin key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/voice-enhancement-20261101/agent-transform-space/REPORT.md` | `479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4` |
| `source:research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md` | `fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- digest-table: end -->

<!-- digest-table: boundary -->
| Pin key | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `schemas/descriptor.schema.json` | `9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba` |
| `schemas/effective-config.schema.json` | `55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

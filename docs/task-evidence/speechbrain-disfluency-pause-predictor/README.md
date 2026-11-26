<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR — task-local feasibility evidence

Task-local, proposal-only, **incomplete** and **not_qualified** feasibility
evidence for `SpeechBrain disfluency/pause predictor`
(`component_id=speechbrain-disfluency-pause-predictor`). The assigned acceptance
profile is **Rate**. Machine-readable decision: **DEFER**;
`status=proposal_only_missing_exact_artifacts_not_qualified`;
`evidence_status=incomplete`; `qualification_status=not_qualified`. No result
in this package qualifies the candidate.

This package does **not** download, install, import, load, execute, copy, vendor
or fabricate any SpeechBrain model, checkpoint, recipe, runtime, corpus, label
set or audio artifact. It does not read, write, render or play real audio; does
not measure device clocks, callback deadlines, FIFO occupancy, pitch/transient
audibility or listening; does not benchmark the SDK; and makes no release claim.
Every envelope interval is a synthetic 16000-sample fixture at 16 kHz, mono,
float32, with 160-sample source frames.

## Boundary

Installed v0 geometry is unchanged and documented only:
`16000 Hz`, 1 channel, `float32`, 160 samples per call. No provider, default,
descriptor, registry entry, ABI, CONTRACTS, shared build or CI file is changed.
The adapter/provider remains OFF, unregistered and not exposed. No
caller-supplied asset is embedded, downloaded, parsed or executed; the package
models only a strict metadata/byte-hash intake shape. Board, handoff, reviewer
dispatch and release state are untouched. The mutable full `plan/swarm/TASKS.json`
is never hashed; only stable linked-row identity is gated.

## Exact blocker

The pinned TSM scorecard records: official SpeechBrain model inventory checked;
**no matching pretrained rate/disfluency head found**. SpeechBrain is a toolkit
with ASR/VAD recipes, not an off-the-shelf preferred-speed predictor for this
task. No exact SpeechBrain disfluency/pause checkpoint could be acquired or
tested. Existing Silero pause/VAD baselines are evaluated separately and are not
promoted here.

All gates RG-01 through RG-08 are **blocked** and `qualifies=false`: exact
runnable source; exact assets and rights; installed-v0 boundary intake; typed
disfluency/pause labels; measured unknown/deletion behavior; Rate-profile
evidence; playback pacing and listening; and public admission review. `DEFER` is
before `opt_in_adapter_exposure`.

## Blockers and reopening conditions

- **B-01 Exact runnable source.** Missing exact 40-hex source revision, reviewed
  license/terms, exact pretrained checkpoint/weights and locked runtime manifest.
  Reopen by supplying caller-owned SHA-256/byte-count verified artifacts; do not
  download or execute in this task.
- **B-02 Exact assets and rights.** Missing rights-cleared cohort manifest, typed
  label schema, matched reference outputs and evaluation terms. Reopen with
  reviewed digests/byte counts; absence remains non-qualifying.
- **B-03 Rate-profile evidence.** Missing source/output mapping, duration, pitch,
  transients, buffering, unfamiliar speech/music/silence, rebuffer/drift/final
  partial, and timestamp-tied pause/filler preservation. Reopen with a matched
  rights-cleared cohort at installed geometry.
- **B-04 Admission/release boundary.** Missing opt-in credential/counsel review
  and application-local intake decision. Reopen only after B-01..B-03 clear; keep
  default/registry/ABI/shared-build/CI unchanged.

## Synthetic controls (not qualifying)

The synthetic envelope uses typed `speech`, `silence` and `unknown` classes in
source-sample coordinates. Speech is never sped above 1x; silence is never slowed
below 1x; unknown spans are retained at rate 1 and are not deletion. Rates are
bounded to 3/4–3/2, dwell is >= 200 ms, output boundaries are integer samples,
and duration closes at 16000 source samples to 16000 output samples. This is
model-free protocol plumbing only and cannot qualify the candidate.

## Caller-supplied asset contract (not satisfied)

Six external assets are required for reopening: source revision, model
checkpoint/weights, runtime lock, typed disfluency/pause label schema,
rights-cleared cohort manifest and matched reference output/score bundle. Each
must be caller-owned, referenced by exact id, byte count and lowercase SHA-256,
with licence/consent review sidecars. The shape-only verifier rejects
duplicate keys, field-set drift, missing/empty identifiers, bad digests,
relative or traversal paths, duplicate paths, embedded storage, absent bytes,
byte-count mismatch and hash mismatch. A hash-matched placeholder is still
shape-only and never qualifies.

## Reproduction

```text
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m reuse lint
git -C ../../../ diff --check
```

Base commit: `4c0f5464eeddff2204b527e8bc4ad09c41b2a657`.
Task ID: `SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR`.

<!-- digest-table: source -->
| Pin key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
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
| `docs/task-evidence/silero-vad-pause-duration-rules/README.md` | `b6e422c591364dffa8b6ab0d3c9c78a579a6c85c88f831d86ee8c9d27593ab1f` |
| `docs/task-evidence/silero-vad-pause-duration-rules/report.json` | `9aebd32c6dc61cf4c5d3d5e0b38fd82a2f083792a453bf9db9548e52cfa5b22d` |
| `docs/task-evidence/source-vad-conditioning-for-playback/README.md` | `26d98518eda620228808587d5a396f9111794e80c333cbf594c8365b9a21f135` |
| `docs/task-evidence/source-vad-conditioning-for-playback/report.json` | `1f180b14ef33466f0950fe9128aa88be1004aca141d762bffff96822e7ec007a` |
| `docs/task-evidence/wavlm-acoustic-disfluency-model/README.md` | `b49b861a20bfa4e37b8a4f4b4aa231d8e4542ebf6305c08d568268653021b447` |
| `schemas/descriptor.schema.json` | `9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba` |
| `schemas/effective-config.schema.json` | `55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

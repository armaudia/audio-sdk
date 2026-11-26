<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SPEECHBRAIN-SGMSE-VOICEBANK — SpeechBrain SGMSE-VoiceBank caller-supplied-asset feasibility boundary

Task-local, proposal-only, `incomplete`, `not_qualified` feasibility and evidence
package for `SpeechBrain SGMSE-VoiceBank` (`component_id=speechbrain-sgmse-voicebank`).
Enhancement profile per `plan/swarm/VERIFICATION.md` and `plan/INVENTORY.json`.
Base commit: `4c0f5464eeddff2204b527e8bc4ad09c41b2a657`; branch:
`swarm/SDK-SPEECHBRAIN-SGMSE-VOICEBANK`. Decision: **DEFER** before
`opt_in_adapter_exposure`; no missing, blocked or synthetic result qualifies the
candidate.

## What this package does and does not do

This package models only a metadata **caller-supplied-asset boundary** at
16 kHz, mono, `float32`, 160-sample frames. It validates caller manifest fields,
absolute paths, SHA-256 values, byte counts and format before failing closed
with `SGMSE_VOICEBANK_ASSET_IDENTITY_UNPINNED`. It never imports, builds,
downloads, loads or executes SpeechBrain, SGMSE, sgmse, PyTorch, lightning,
torchaudio, Hugging Face Hub or any enhancement runtime. No source checkout,
checkpoint/config, weights, audio, cohort or runtime bytes are vendored. No
adapter or provider is registered, no default is selected, and no public API,
ABI, registry, build or CI file is changed.

All enhancement controls here are **synthetic, deterministic, integer-only
sample and frame geometry**: 165 source samples mapped to one full 160-sample
frame plus a 5-sample final partial window with 155 zero-padding samples,
half-open source intervals, and swap/insert/truncate controls. These controls
are explicitly **not audio, not enhancement output, and not SI-SDR/STOI/PESQ
evidence**. There is no listening result, device timing, benchmark or release
claim. Upstream reported PESQ/SI-SDR/STOI figures are source-reported
provenance only and are **no substitution** for local evidence.

## Exact readiness conclusion

`DEFER` / `incomplete` / `not_qualified`. Gates `RG-01` through `RG-08` are all
blocked and non-qualifying. The exact external blockers are:

- **XB-01** — no exact SpeechBrain SGMSE-VoiceBank source revision, checkpoint/
  config artifact, byte count, SHA-256, or locked runtime is staged. Census
  metrics are source-reported upstream only.
- **XB-02** — no rights-qualified paired noisy/clean cohort, pinned scorers,
  identity/noisy control run, or task-matched baseline is staged; rights are
  unreviewed.
- **XB-03** — enhancement profile unmet: no paired SI-SDR/STOI, clean-speech
  preservation, peak/invalid-output audit, alignment, state/memory/timing,
  unpaired screen, or listening evidence exists.
- **XB-04** — no opt-in provider intake, independent exact-head review, device
  timing, benchmark, or release approval exists. Default remains OFF.

Reopening requires exact licensed source/checkpoint/config identity and locked
runtime, reviewed rights, a rights-cleared paired cohort with pinned scorers
and controls, matched enhancement-profile outcomes on that exact runtime, and a
separate opt-in intake reviewed at an exact head with the default OFF.

## Matched source evidence

One pinned line is checked byte-for-byte: noise suppression candidate census row
for SpeechBrain SGMSE-VoiceBank (`research/noise_suppression_candidate_census.md`,
line 41). It is matched to component `speechbrain-sgmse-voicebank`, task
`SDK-SPEECHBRAIN-SGMSE-VOICEBANK` and the `enhancement` profile. It is
**provenance only**, never a local result.

## Stable board identity

Only stable row fields (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`) enter canonical bytes and gates. The full mutable
`plan/swarm/TASKS.json` is never hashed. Stable-row SHA-256:
`ed45cc640abbac44cea9af737a8bd890b199d55eca0053968e6629f1edf352ff`.

## Source pins (SHA-256)

`source:` paths are workspace-relative. Every row is checked by `verify.py`.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `source:research/voice-enhancement-20261101/findings.md` | `78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

Paths are SDK-worktree-relative. All are unchanged and machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/speechbrain-sgmse-voicebank/caller-supplied/0.1` is metadata-only.
Required fields are `adapter`, `configuration_id`, `checkpoint_path`,
`checkpoint_sha256`, `checkpoint_byte_count`, `checkpoint_revision`,
`source_revision`, `runtime_lock_digest`, `rights_digest`, `sample_rate_hz`,
`channels`, `frame_samples`, `sample_format`, `paired_cohort_digest` and
`scorer_digest`. The validator permits only the declared task-local metadata
configuration label, requires a 40-hex source revision, the pinned format,
absolute checkpoint paths and hash/size-matched checkpoint bytes. Even a
hash-matched caller file still fails as
`SGMSE_VOICEBANK_ASSET_IDENTITY_UNPINNED`; no asset is loaded or run.

## Scope gate

`verify.py` resolves the newest merge-base of `HEAD` with `origin/main`, falling
back to `main` only when `origin/main` is unavailable. If no base exists it
emits `scope_base_unavailable`. Any tracked branch difference outside
`docs/task-evidence/speechbrain-sgmse-voicebank/` emits
`base_out_of_scope_change` and fails closed. Three regression tests cover
newest-base selection, `main` fallback and out-of-scope/missing-base rejection.

## Reproduce

All commands are read-only except for canonical artifacts in this directory.

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SPEECHBRAIN-SGMSE-VOICEBANK/docs/task-evidence/speechbrain-sgmse-voicebank
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git diff --check
```

Canonical JSON uses sorted keys, compact separators, `allow_nan=False` and one
trailing LF. Three fresh builds are byte-identical; comparison is exact
SHA-256 with no tolerance. `report.json.sha256` is the canonical sidecar and
`SOURCES.sha256` pins source, boundary and local artifact bytes. `verify.py`
validates both README digest tables against the live pins.

## Licensing

No SpeechBrain/SGMSE source, weights, corpus or output bytes are redistributed
here. Code, weights, data, consent, reference availability and product-use terms
remain unreviewed and independent. All package files are Apache-2.0 via SPDX
headers and the repository `REUSE.toml` annotation for `docs/**`.

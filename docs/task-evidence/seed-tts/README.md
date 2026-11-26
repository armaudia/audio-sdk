<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SEED-TTS — Seed-TTS caller-supplied-asset feasibility boundary

Task-local, proposal-only, `incomplete`, `not_qualified` feasibility and evidence
package for `Seed-TTS` (`component_id=seed-ts`). The voice acceptance profile is
defined in `plan/swarm/VERIFICATION.md` and assigned by `plan/INVENTORY.json`.
Base commit: `a51e49f718500ec9e81242cf2816f0b576333d00`; branch:
`swarm/SDK-SEED-TTS`. Decision: **DEFER** before
`opt_in_adapter_exposure`; no missing, blocked or synthetic result qualifies the
candidate.

## What this package does and does not do

This package models only a metadata **caller-supplied-asset boundary** at
16 kHz, mono, `float32`, 160-sample frames. It validates caller manifest fields,
absolute paths, SHA-256 values, byte counts and format before failing closed
with `SEED_TTS_CHECKPOINT_IDENTITY_UNPINNED`. It never imports, builds,
downloads, loads or executes Seed-TTS, any tokenizer, any vocoder or any other
TTS/voice-conversion model. No source checkout, checkpoint, audio, cohort or
runtime bytes are vendored.

All voice content here is **synthetic, deterministic, integer-only token/text
framing**: a fixed 48-token sequence, one frame, token swap/insert/truncate
controls and a sample-interval mapping. These controls are explicitly **not
real text semantics, not audio, not Seed-TTS output and not listening
evidence**. There is no identity score, naturalness rating, ASR result, device
timing, first-output measurement, benchmark or release claim.

## Exact readiness conclusion

`DEFER` / `incomplete` / `not_qualified`. Gates `RG-01` through `RG-08` are all
blocked and non-qualifying. The exact external blockers are:

- **XB-01** — the census marks Seed-TTS `unavailable/blocked`; the voice audit
  finds no weights, adapter or evaluation and states that the public
  report/demo does not establish a locally downloadable, licensed streaming
  input-conversion model. No exact checkpoint path, revision, byte count or
  SHA-256 exists to pin.
- **XB-02** — no locked Python/PyTorch runtime, tokenizer/vocoder bundle,
  offline loader, autoregressive-versus-diffusion variant selection, chunking,
  alignment or finalization geometry is staged.
- **XB-03** — no consented reference voices, manual transcripts,
  speaker/language groups, held-out text split, target condition, output-use
  grant or pinned content/identity/naturalness scorer is staged.
- **XB-04** — no local Seed-TTS output, content-preservation result, identity
  or naturalness score, blinded listening, first-output/tail measurement,
  device timing, benchmark, opt-in intake or independent release review exists.

Reopening requires the exact licensed artifact identity and locked runtime,
reviewed rights, a rights-cleared frozen voice cohort with pinned scorers,
matched voice evidence on that exact runtime, and a separate opt-in intake
reviewed at an exact head with the default OFF.

## Matched source evidence

Three pinned lines are checked byte-for-byte: the structured census row
(`candidate_matrix.csv`, line 51), the voice-transformation audit row
(`agent-transform-space/REPORT.md`, line 19) and the blocked reaudit
(`agent-blocked-reaudit/REPORT.md`, line 36). They are matched to component
`seed-ts`, record 50, task `SDK-SEED-TTS` and the `voice` profile. They are
**provenance only**, never a local result. Technical-report and demo
descriptions are source-reported. Other TTS test-set uses belong to different
models and tasks; **no substitution** is made.

## Stable board identity

Only stable row fields (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`) enter canonical bytes and gates. The full mutable
`plan/swarm/TASKS.json` is never hashed. Stable-row SHA-256:
`b616ff242b23a1a1f1d9dc2c53da26cb002dac04a5ebd793c9a5cb4837a74181`.

## Source pins (SHA-256)

`source:` paths are workspace-relative. Every row is checked by `verify.py`.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/voice-conversion-eval-20261101/README.md` | `b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074` |
| `source:research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md` | `5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14` |
| `source:research/voice-enhancement-20261101/agent-matrix-audit/REPORT.md` | `865b0031d357b7009c2876f997ca188440451fb65d5cef3561e9848f34eaf1d0` |
| `source:research/voice-enhancement-20261101/agent-transform-space/REPORT.md` | `479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4` |
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
| `docs/task-evidence/cosyvoice-family/README.md` | `41ab92e27ed62d9379627be8714579ab168e16125c5496d99dc25b77fb20de67` |
| `docs/task-evidence/f5-tts/README.md` | `31ffbd70d9a6976509c492398bf17a0d43b0c4b2a5d98f0c4df320ac1489a0b8` |
| `docs/task-evidence/survey-trn-05/README.md` | `81b51f5696142a7fb77dd285e1db866f550de0faf5e5160ed66d15499b64c26b` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/seed-tts/caller-supplied/0.1` is metadata-only. Required fields are
`adapter`, `configuration_id`, `checkpoint_path`, `checkpoint_sha256`,
`checkpoint_byte_count`, `checkpoint_revision`, `source_revision`,
`runtime_lock_digest`, `rights_digest`, `sample_rate_hz`, `channels`,
`frame_samples`, `sample_format`, `text_cohort_digest` and
`reference_consent_digest`. The validator permits only the two declared family
configurations, requires a 40-hex source revision, the pinned format, absolute
checkpoint paths and hash/size-matched checkpoint bytes. Even a hash-matched
caller file still fails as `SEED_TTS_CHECKPOINT_IDENTITY_UNPINNED`; no asset is
loaded or run.

## Scope gate

`verify.py` resolves the newest merge-base of `HEAD` with `origin/main`, falling
back to `main` only when `origin/main` is unavailable. If no base exists it
emits `scope_base_unavailable`. Any tracked branch difference outside
`docs/task-evidence/seed-tts/` emits `base_out_of_scope_change` and fails
closed. Three regression tests cover newest-base selection, `main` fallback and
out-of-scope/missing-base rejection.

## Reproduce

All commands are read-only except for the canonical artifacts in this directory
and the temporary CI output under `build/ci`.

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SEED-TTS/docs/task-evidence/seed-tts
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
cd ../..
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output build/ci
```

Canonical JSON uses sorted keys, compact separators, `allow_nan=False` and one
trailing LF. Three fresh builds are byte-identical; comparison is exact
SHA-256 with no tolerance. `report.json.sha256` is the canonical sidecar and
`SOURCES.sha256` pins source, boundary and local artifact bytes. `verify.py`
validates both README digest tables against the live pins.

## Licensing

No Seed-TTS source, checkpoint, training data, reference voice or output bytes
are redistributed here. Code weights, data, consent, reference availability and
product-use terms remain unreviewed and independent. All package files are
Apache-2.0 via SPDX headers and the repository `REUSE.toml` annotation for
`docs/**`.

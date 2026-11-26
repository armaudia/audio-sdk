<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-CONVERT-AND-SPEAK - Convert and Speak source, weights, runtime and voice blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Convert and Speak` (`component_id=convert-and-speak`). The acceptance profile is
**Voice**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed Convert and Speak source, weights, runtime, adapter,
immutable revision, I/O geometry, alignment and numeric output are **absent**.
This package records that exact blocker, applies the Voice profile to a bounded
deterministic synthetic PCM accounting surrogate, and makes no accent,
conversion, quality, identity, naturalness, timing, listening, benchmark or
release claim. It is **not Convert and Speak**: no autoregressive model, content
encoder, speaker encoder, vocoder, weight file, native library, real audio,
corpus, device clock or upstream code is present, copied, downloaded, loaded,
imported or executed. Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=convert-and-speak`) is
`considered`, `disposition=sdk-model`, `verification_profile=voice`. Its only
evidence link is `research/accent-conversion-20261101/README.md`, line 172:

> **Convert and Speak** | Paper/demo inspected; no runnable local checkpoint
> found. | Strong accent-conversion research comparison with an autoregressive
> generation component; not a strict low-latency candidate.
> [Paper/demo](https://convert-and-speak.github.io/demo/)

Consequently:

- no Convert and Speak source tree, release archive, checkout, weight file,
  runtime environment or adapter is staged at
  `data/checkouts/convert-and-speak`, `data/models/convert-and-speak`,
  `data/envs/convert-and-speak` or `adapters/convert-and-speak`;
- no immutable source revision, weight SHA-256, byte count, model card,
  parameter layout, sample rate, hop, chunk scheme, lookahead, alignment or
  numeric output exists for the candidate;
- no upstream LICENSE, weight terms, training-data statement, attribution
  bundle, corpus rights or product-use review is staged;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream; no
  candidate input/output geometry, content delay or adapter is documented;
- no real source/target voice pair, consent record, held-out split,
  transcript truth, identity score, naturalness rating or listening result
  exists;
- no target-device timing, independent review, provider intake or release
  approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-CONVERT-AND-SPEAK`, `6967a728b5c4048fb01ed4522a76a6906fbcffe2` |
| Task mode | `feasibility` |
| Acceptance profile | `voice` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/mode/alignment asserted |
| Surrogate | synthetic 16 kHz mono offline whole-utterance accounting |
| Added content delay | 0 samples; no device timing or latency claim |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded integer Q15 one-pole transform with a declared
`3/4` coefficient and an exact source/output duration ratio of `1`. It is **not
Convert and Speak**, is not learned, uses no weights and cannot qualify the
candidate.

## Voice profile application

`plan/swarm/VERIFICATION.md` Voice row requires permitted input and target
references, frozen task/language/speaker groups, separate text/semantic,
identity/similarity and naturalness outcomes, alignment and first-output/tail
timing, and independent consent, reference-availability and output-use gates.
Every item is applied in `report.json` -> `acceptance_profile` and checked by
`verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Permitted source/target references | `absent` | No rights or consent record; no source/target pair |
| Task, language and speaker groups | `absent` | No frozen cohort or grouping |
| Text and semantic preservation | `not_measured` | No model, transcript truth or cohort |
| Identity/similarity | `not_measured` | No speaker reference or embedder runtime |
| Naturalness | `not_measured` | No authorized listening panel |
| Alignment and output timing | `structural_only` | Synthetic offline accounting only; no device clock |
| Consent, reference and output use | `absent` | No independent gate is cleared |

`satisfied_for_qualification=[]`, `real_model_metrics=null`, and every item has
`qualification_effect=none`.

## Synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`; surrogate input and output share this rate.
- Source PCM: 48,000 samples (3 s), deterministic integer-ratio triangles plus
  a fixed LCG perturbation; peak below 0.32.
- Target reference PCM: 32,000 samples (2 s), deterministic and separate from
  the output; it is **not** used for scoring and no similarity is computed.
- Output PCM: 48,000 samples (3 s), produced by the Q15 one-pole surrogate;
  finite, peak below 0.30.
- Duration accounting: exact `3`, `3`, ratio `1` as reduced fractions.
- Alignment: declared offline whole-utterance, first output sample 0,
  content delay 0, tail at 48,000; **not** a candidate claim.
- Reset: surrogate epoch 2 matches a fresh epoch-2 instance; zero, negative and
  non-increasing epochs are rejected with the state digest unchanged.

Measured synthetic observations are structural only and appear in
`report.json` -> `reference_protocol`. They are unqualified task-local
observations, not model output.

## Adverse, missing and invalid handling

`report.json` records 39 rejected inputs, each fail-closed. Rejections include
duplicate JSON key, `NaN`/`Infinity` constants, malformed JSON, missing/extra
manifest fields, relative paths, bad hashes, short/non-hex revisions, wrong
input/output rate, stereo, booleans and strings as samples, out-of-range and
nonfinite samples, an over-cap signal, epoch 0/-1//non-increasing, a negative
reset position, stale epoch, nonfinite input and output, a missing asset,
an unapproved revision, and malformed fixture length/rate/Q15 specifications.
For surrogate state changes, the state digest is compared before and after and
must be unchanged on rejection. Missing real source, weights, runtime outputs,
rights and labels are `blocked`, never passes.

The caller asset contract validates shape, identity, absolute paths and hashes
only. It never reads, imports, loads or executes a source tree, weight file or
runtime. Because no immutable source revision, weight digest, runtime lock or
rights record is approved, **every** manifest is rejected before processing.
A hash-matched placeholder is never accepted as a pinned Convert and Speak
artifact.

## Streaming, reset and determinism

The surrogate is offline whole-utterance: `streaming_supported=false`,
`incremental_streaming=false`, and no chunked replay is claimed. Reset semantics
are structural and surrogate-only. `run.py` builds the report, contract and
manifest three times and refuses to write unless every payload is byte-identical.
`run.py --check` is read-only, and `run.py --out DIR` supports external
cold-start regeneration.

## Separation from sibling evidence

The merged `tokan`, `chatterbox-vc` and `cosyvoice-2-0-5b` packages are separate
Voice-profile proposals with their own assets, fixtures, metrics and
dispositions. This package does not import, pool, score or reuse their source,
fixtures, metrics or results. Their README, report and contract files are
pinned only as read-only boundary references. The shared
`research/accent-conversion-20261101` note is pinned as the exact evidence
source; its three L2-ARCTIC clips are not Convert and Speak input/target pairs.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, fixed-path audit, synthetic surrogate, metrics, report and contract builders. |
| `run.py` | Builds all artifacts three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Voice report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | `sha256sum`-style digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only strict-JSON, pin, digest, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
| `source:research/accent-conversion-20261101/README.md` | `c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`worktree:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `worktree:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `worktree:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `worktree:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
| `worktree:docs/task-evidence/tokan/README.md` | `425008e6836ea01e797c1bb86708532962d6e75ea0a8d332552b90ce0b2977df` |
| `worktree:docs/task-evidence/tokan/report.json` | `6cd151f2178d95d6e5c98b389a9b71f80097a01efaaa92a4450a7c26db1bcd13` |
| `worktree:docs/task-evidence/chatterbox-vc/README.md` | `7a624864df916ef87b32655e6e0894bfe00c3da94ca6969352be68654ee1443c` |
| `worktree:docs/task-evidence/chatterbox-vc/report.json` | `321fe22b052823b43d772871b5b694df03c0586c6754c04491d40406055b3dee` |
| `worktree:docs/task-evidence/cosyvoice-2-0-5b/contract.json` | `b7e38b9569a6d240bd551e54ecf0f42ca9e6b28b1702f88fb74a0497c3365dc3` |
<!-- digest-table: end -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CONVERT-AND-SPEAK/docs/task-evidence/convert-and-speak
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CONVERT-AND-SPEAK diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `run.py` three times and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned Convert and Speak source, weights and immutable revision
   with license identity, byte counts and SHA-256 values.
2. `RG-02` isolated hash-pinned runtime admission, reproducible build and
   fail-closed absent behavior.
3. `RG-03` code, weight, training-data, corpus, voice-reference, consent and
   output-use rights with attribution and notices.
4. `RG-04` caller-supplied asset identity plus documented candidate geometry
   and content-delay mapping into the installed SDK v0 path.
5. `RG-05` rights-cleared held-out voice cohort scoring text/semantic
   preservation, identity/similarity and naturalness separately.
6. `RG-06` exact-runtime offline alignment, first-output and tail behavior,
   nonfinite handling, reset and state reproduction.
7. `RG-07` target-device pacing, timing and memory with independent listening
   and/or ASR controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`. Until every gate is cleared and independently
reviewed, no result may qualify the candidate and the candidate remains
**DEFER**, **incomplete** and **not qualified**.

**Reopen condition.** Pin the exact licensed source, weights and runtime with an
immutable revision, admit an isolated hash-pinned runtime, clear code, weight,
training-data, corpus, voice-reference, consent and output-use rights, freeze a
rights-cleared held-out voice cohort, document candidate geometry and alignment,
reproduce an approved parity vector, measure target timing and complete opt-in
provider intake. Until then the candidate stays **DEFER**, **incomplete** and
**not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only
(`tasks[id=SDK-CONVERT-AND-SPEAK]`, stable-field digest); the mutable full
`plan/swarm/TASKS.json` is never hashed, pinned or used as a digest source. No
provider, descriptor, registry, installed default, shared build or CI is
changed.

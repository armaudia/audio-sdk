<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WHISPER-TINY-EN-MFA — Whisper tiny.en + MFA readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`whisper-tiny-en-mfa` (title "Whisper tiny.en + MFA"). Decision: **DEFER**
before any implementation or intake step; `status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. Missing evidence
never qualifies a candidate.

This package does **not** contain, import, build, link, download, load or
execute OpenAI Whisper, `tiny.en.pt`, PyTorch, `openai-whisper`, Montreal
Forced Aligner (MFA 3.4.3), the `english_us_arpa` acoustic archive or
dictionary, AMI audio/annotations, a transcript, a word span, a TextGrid, an
audio signal or any inference path. It records the exact historical artifacts
and procedures, pins the research report and scripts by whole-file SHA-256,
probes fixed recorded workspace/temporary paths to evidence absence, defines a
fail-closed admission boundary for a future single-crop reproduction, and
records a synthetic boundary-score arithmetic control that is explicitly
labelled `synthetic_scorer_control_not_evidence` and can never qualify. Only
`docs/task-evidence/whisper-tiny-en-mfa/` is written; no provider, registry,
descriptor, public header/ABI, shared CMake, CI workflow, board or handoff file
changes.

## Profile mismatch and exact acceptance scope

The task row says "Apply the rate acceptance profile"; `plan/INVENTORY.json`
sets `verification_profile: rate`, and `plan/swarm/VERIFICATION.md` defines that
profile. Whisper + MFA is a **text-aware transcription and forced-alignment
tool**, not a time-stretch renderer. It can produce transcript/word boundaries
that a separate pause controller might use, but it does not map output duration,
change rate, buffer playback or preserve transients. Every Rate requirement is
therefore recorded as **blocked** rather than reinterpreted. A future review
must either supply Rate evidence for a composite path that contains a separate
renderer or record an explicit, reviewed waiver.

## Exact external blocker

The exact licensed source, weights, runtime and run artifacts are **absent or
unverified**:

- **Whisper weight.** The research report pins `openai-whisper==20250625`,
  `tiny.en.pt` and SHA-256
  `d3dd57d32accea0b295c96e26691aa14d8822fac7d9d27d5dc00b4ca2826dd03`
  under the MIT license. `/private/tmp/whisper-model/tiny.en.pt` is absent; no
  reviewed workspace/cache copy exists. The package archive digest, exact
  source revision and complete MIT notice bundle are not staged.
- **MFA assets.** The report records MFA 3.4.3 (Conda Forge) with
  `english_us_arpa` acoustic archive SHA-256
  `d35ce271ded357d833d2f4b8d1041dc3748b9538567ba13f2c697f4e4126711b`,
  dictionary SHA-256
  `e8c6c7b036ae2b7c78d2768b8dc6b1f9359175b842956d00b48c53c9c332e6b0`,
  266,823 dictionary entries and a CC-BY-4.0 model card. Those installed paths
  are outside this worktree and are not readable by this session; no digest was
  verified here, no MFA source revision or notice/attribution bundle is staged,
  and `/private/tmp/mfa-env` is absent.
- **Runtime.** The historical ASR environment `/private/tmp/asr-mfa-env`, MFA
  environment `/private/tmp/mfa-env` and `/private/tmp/mfa-root` are absent.
  The available Python 3.11.5 interpreter exposes no `whisper`, `torch`,
  `transformers` or `soundfile` module. No lockfile, wheel/conda digest,
  install/import digest, thread policy or offline-load trace exists.
- **Audio and annotations.** `/private/tmp/EN2003a.Headset-0.wav`,
  `data/tmp/ami/vad-verified-ami-archive/words/EN2003a.A.words.xml` and the
  whole `data/runs/tsm-followup-20261101-mfa/` tree are absent. The recorded
  crop SHA-256
  `a8fcab8547e24376367f97ce5967318e18cc6e052fe3f89934ff037dc90bd9ca`
  and the reference word spans cannot be verified. AMI CC BY 4.0 terms are not
  reviewed, and AMI word times are themselves forced alignment, not independent
  timing gold.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | `tiny.en.pt` with byte count and SHA-256 `d3dd57d3…`, the exact `openai-whisper` 20250625 source revision/package archive, and the complete MIT license/notice bundle with reviewed terms. |
| `BLK-02` | The exact MFA 3.4.3 acoustic archive and dictionary with byte counts and verified SHA-256, MFA source revision, license/notice/attribution text, a written CC-BY-4.0 output-use decision, and a pinned offline Conda environment. |
| `BLK-03` | Locked offline Whisper and MFA environments with exact package/wheel/conda hashes, install/import digests, deterministic thread settings and a clean-room offline load. |
| `BLK-04` | The exact AMI 15 s crop, `A.words` annotation, meeting/channel mapping and reviewable CC BY 4.0 terms, plus an independent human-checked timing reference instead of AMI forced alignment as gold. |
| `BLK-05` | A fresh offline Whisper ASR and MFA oracle/ASR alignment with frozen scorers, explicit substitution/deletion/insertion accounting, finite-boundary checks, a uniform-timing baseline and adverse/missing controls. |
| `BLK-06` | Rate-profile evidence or a reviewed waiver, target-device p50/p95/p99 timing/resources, and a separate OFF-by-default versioned provider/tool intake with independent exact-head review. |

**Reopen condition.** A caller supplies the exact Whisper weight/package/
license, exact MFA assets/source/license/runtime, a locked offline environment,
the exact AMI crop/annotation with reviewed terms and an independent timing
reference, a reproduced ASR+alignment result with controls, the exact Rate
protocol (or a reviewed waiver), target-device measurements, and a separate
opt-in intake with an OFF default and independent exact-head review. Until then
this task stays `DEFER` and all eight release gates stay `blocked`.

## Historical execution: provenance only

The research record contains one successful 15 s AMI crop evaluation. It is
transcribed with its original scope and is **not rerun, not merged task
evidence, not used for evidence and not a qualification**.

| Field | Recorded value |
| --- | --- |
| Whisper | `openai-whisper==20250625`, `tiny.en`, CPU, `fp16=False`, 4 Torch threads |
| Whisper weight / license | SHA-256 `d3dd57d3…` / MIT per report |
| Whisper load / inference | `0.839 s` load, `1.445 s` inference, RTF `0.096` excluding load |
| WER | `11.76%` (4 errors / 34 reference words) |
| MFA | 3.4.3, Conda Forge, `english_us_arpa` acoustic + dictionary, one job |
| Oracle alignment | 33/34 words matched (one `Mm` OOV); boundary MAE `23.79 ms`, median `10 ms`, `89.4%` within 50 ms |
| ASR alignment | 30 words matched; boundary MAE `23.17 ms`, median `10 ms`, `91.7%` within 50 ms |
| Crop | AMI `EN2003a.Headset-0`, 16–31 s, 16 kHz mono, CC BY 4.0 |
| Timing reference | AMI supplied word timestamps, already forced aligned, not manually corrected |
| Listening / device / release | absent |

The finding is that Whisper tiny.en plus MFA can produce usable transcript-
conditioned word timings on one crop relative to AMI timings. It is not general
ASR accuracy, independent timing gold, a preferred speed factor, a device
latency or a product claim.

## What this package actually verifies

1. **Source/recipe presence and exact pins.** The research README, detailed
   report, crop/ASR/alignment/scoring scripts, inventory, verification profile
   and SDK plan are pinned by SHA-256. The scripts contain the recorded
   `tiny.en` CPU call, English/fp16 settings, 16–31 s crop recipe,
   boundary-scoring and WER snippets. This is provenance, not a model, asset or
   runtime qualification.
2. **Absence evidence.** Thirteen fixed workspace probes and six fixed
   temporary-path probes are checked (no recursive workspace walk). All are
   absent. `reference.build_report()` and `verify.py` fail if any probe later
   appears, so a stale "absent" claim cannot ship.
3. **Admission boundary.** A caller-supplied single-crop Whisper+MFA manifest
   has a strict, task-local schema. Every malformed, missing, invalid,
   nonfinite, aliased, duplicated, out-of-range or non-integral control is
   rejected before any state change. One structural control is admitted to
   prove the validator is not blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights or invokes a model.
4. **Deterministic score arithmetic.** A stdlib-only integer-millisecond
   Levenshtein word aligner and boundary scorer is exercised on a synthetic
   four-reference/five-hypothesis fixture. It produces three matched words, six
   boundary errors, MAE `12.5 ms`, median `10 ms` and `100%` within 50 ms. It
   emits no audio and has no model input; it is arithmetic, not an ASR result.
5. **Rate-profile accounting.** Source/output mapping, duration,
   pitch/transient audibility, playback buffering, 1×/rate changes, unfamiliar
   speech/music/silence, rebuffer/drift/final partial window, timestamp-tied
   pause/filler decisions and the preferred-speed policy are each recorded as
   **blocked**.
6. **Quality and timing accounting.** WER, oracle/ASR boundary error,
   matched-word accounting and control baselines are separate blocked outcomes;
   Whisper latency, MFA wall time, device deadlines and resources are separate
   blocked timing rows. No value is inferred from the historical run.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, CI, the SDK README and the merged Vosk ASR and
   wav2vec2 sibling packages are pinned by SHA-256 and verified unchanged.

## Admission contract (task-local; not an SDK, Whisper or MFA contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `whisper`, `mfa`, `runtime`,
  `audio`, `transcripts`, `controls`, `outcomes`, `rights`. Unknown and missing
  fields are rejected.
- **Whisper**: exactly `openai/whisper tiny.en`, `openai-whisper` version
  `20250625`, `tiny.en.pt`, SHA-256 `d3dd57d3…`, a positive byte count and
  `license_id="mit"`.
- **MFA**: exactly 3.4.3 from `conda-forge`, `english_us_arpa` acoustic and
  dictionary, the recorded acoustic/dictionary SHA-256 values, positive byte
  counts and `license_id="cc-by-4.0"`.
- **Runtime**: non-empty Python/torch/whisper/MFA versions, CPU, one intra-op
  and one inter-op thread, deterministic algorithms on and offline on.
- **Audio**: exactly one canonical absolute path, 64-hex digest, `en`,
  speaker/meeting slug, `EN2003a`, `Headset-0`, 16 kHz, mono, exactly 240,000
  samples and a 15 s span starting at any nonnegative source time.
- **Transcripts**: oracle source `ami-orthographic` and ASR source
  `openai-whisper-tiny.en`, each with a 64-hex digest and positive word count.
- **Controls**: exactly one each of `oracle_transcript_mfa_alignment`,
  `asr_transcript_mfa_alignment` and `uniform_word_timing_baseline`.
- **Outcomes**: WER and within-50 ms fraction in 0–1, boundary MAE/median
  0–60,000 ms, nonnegative matched words, positive reference words,
  `nonfinite_count=0` and `sample_count=1`. These are admission bounds, not
  measured results.
- **Rights**: non-empty dataset/Whisper/MFA/output-use/review references and
  `claims_qualified=false`. The schema does not assert that any real right has
  been granted.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable projection `{id, title, component, mode, repository, depends_on}`
gates anything. `plan/swarm/TASKS.json` bytes are never hashed.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Candidate scorecard |
| `source:…/agent-text/REPORT.md` | `86657ba0d2c82d64110dc058f40082e2d701ce0ff2427fe2e0d3a3f1719bfd93` | Exact WER/alignment records and runtime |
| `source:…/agent-text/run_whisper_asr.py` | `7fb7a94b6117b7694ec04d3bb1f6491527c802651135fcf5f05eae8b0782bbd4` | Exact Whisper CPU recipe |
| `source:…/agent-text/run_mfa_alignment_smoke.py` | `245f05c557cb7b93ba14887b71fa93ef8098d94478fee4cd9baa1910dac7fa66` | Crop/annotation/manifest recipe |
| `source:…/agent-text/score_asr_alignment.py` | `0294e7681af9b6491bed6501bd1d7154b6809a9231101209187412c6f5b9c6bf` | ASR boundary scoring recipe |
| `source:…/agent-text/score_mfa_alignment_smoke.py` | `f6b99e3fb0864eea4dab999b875e88a7214fda1142f40e7cc8118c303225bd0a` | Oracle boundary scoring recipe |
| `source:…/agent-text/score_whisper_asr.py` | `624558e2835dfb25f2321c6ba3b505107536539164159e461a7c250bee6a27a8` | WER scoring recipe |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `whisper-tiny-en-mfa` row, Rate profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json` | `57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2` | Merged ASR sibling boundary |
| `docs/task-evidence/wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge/report.json` | `1ce7faa0b87faa8a8782083bd23ba6dd5803f9bd45ae5ef2db9a8692b0858f48` | Merged ASR-feature sibling boundary |

The Vosk and wav2vec2 numbers, manifests, admission rules and gates are never
reused here. This package's links to them are whole-file boundary pins only.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, profile mismatch, blocker, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Whisper/MFA/AMI license boundary; no vendored license or asset text. |
| `contract.json` | Machine-readable contract: exact models, pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, absence/projection checks, admission validator, synthetic scorer, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime, no audio). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/whisper-tiny-en-mfa` with Python 3.12 (3.11 also works)
and stdlib only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` reports `repeat=3 byte_identical=true`; all unittest checks
pass with 0 failed and 0 skipped; `verify.py` prints `PASS ... cold_starts=3/3
byte_identical=true profile=Rate status=incomplete decision=DEFER`; REUSE
reports no missing or bad license; `git diff --check` is clean. `verify.py`
itself writes only to a temporary directory and never to this package.

Current counts: 19 absence probes (13 workspace + 6 external, 0 present), 7
required artifacts (1 provenance artifact present, 6 blocked), 6 open
blockers, 71 rejected admission controls, 1 schema-only control, 8 blocked Rate
rows, 5 blocked quality outcomes, 4 blocked timing rows, 1 synthetic score
control, 8 blocked gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision and license provenance | blocked | Pin exact Whisper and MFA source/package revisions and stage complete MIT/CC-BY-4.0 license/notice/model-card sets with independent review. |
| `RG-02` weights, assets and digests | blocked | Supply `tiny.en.pt`, the MFA acoustic archive and dictionary with byte counts and verified SHA-256. |
| `RG-03` pinned runtime and offline load | blocked | A locked offline Whisper/MFA runtime loads the assets and records deterministic imports, loads and repeats. |
| `RG-04` rights-cleared audio, annotations and terms | blocked | Stage the exact AMI crop/annotation, review AMI and MFA terms, and provide independent timing gold. |
| `RG-05` ASR and alignment accuracy with controls | blocked | Reproduce WER and boundary errors with token accounting, finite checks and matched baselines. |
| `RG-06` Rate-profile condition coverage | blocked | Score the exact Rate cases for a composite renderer or record a reviewed waiver. |
| `RG-07` target timing, resources and deadlines | blocked | Measure paced p50/p95/p99 latency, CPU/memory/energy and fill/flush on the intended device. |
| `RG-08` provider intake, public surface and release | blocked | A separate versioned OFF-by-default intake with clean-install proof and independent exact-head review. |

No synthetic admission or score control opens a gate. No missing result is
promoted.

## Separation from other evidence

The merged Vosk small-en-us-0.15 package is a different ASR engine and gate; its
model/runtime bytes, batch recognizer trace, rate arithmetic and gates are never
substituted here. The merged wav2vec2-base-960h + ridge package is a rate
estimator; its feature/head artifacts and FP32 metrics are a different task and
are not reused. Silero, wav2vec2, WavLM, Vosk and Whisper int8 via sherpa-onnx
are boundaries only; none is pooled or reinterpreted as Whisper tiny.en + MFA
evidence.

## Expected digest

`report.json` SHA-256:
`6b9cc69ea2be5cd5cad9509021b7b5e7fb972a4c32c62721f07be995b582710c`.

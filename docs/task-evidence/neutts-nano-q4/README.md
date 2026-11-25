<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NEUTTS-NANO-Q4 — NeuTTS Nano Q4 readiness blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`NeuTTS Nano Q4` (`component_id=neutts-nano-q4`). The structured inventory
assigns the **Voice** acceptance profile (`verification_profile: voice`,
`plan/INVENTORY.json`), defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER** before any implementation or intake step; `status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. Missing evidence
never qualifies a candidate.

This package does **not** contain, import, build, link, download, load or
execute NeuTTS, a Q4 GGUF weight, a NeuCodec asset, `llama-cpp-python`, a
PyTorch runtime, a reference voice or an inference path. It decodes, plays and
analyzes no audio, generates no speech, clones no voice and measures no content,
identity, similarity, naturalness, alignment, first-output/tail, peak, device
timing, resource, benchmark or release result. Only a whole-file SHA-256
provenance check is performed on the upstream demo `output.wav`, and it is not
loaded as a signal. It records the exact missing artifacts and rights, probes a
fixed list of workspace and home-cache paths to evidence their absence, records
the one historical acquisition failure as provenance only, and defines a
fail-closed admission boundary for the Voice cohort a future qualified run would
need. Only `docs/task-evidence/neutts-nano-q4/` is written; no provider,
registry, descriptor, public header/ABI, shared CMake, CI workflow or
installed-v0 behavior changes.

## Exact external blocker

The official `neuphonic/neutts` code checkout is present at the pinned revision
`ac69851f28fc63a487917e7c2e27f0d75c759cba` with the **NeuTTS Open License 1.0**
(`LICENSE`). That is a source-and-model license, not an OSI license: it limits
commercial use above a revenue threshold and conditions Output use. The Q4 GGUF
backbone, NeuCodec codec assets and exact runtime are **absent**. The research
record states that the model download from `neuphonic/neutts-nano-q4-gguf`
returned HTTP 401 because the Hugging Face repository is gated and the
evaluation had no authenticated access; no alternate route was attempted. No
download, reconstruction or substitute was attempted by this package. Because
the weights, codec and runtime are absent, this package implements no
source-derived model surrogate or partial inference path; the smallest
verifiable reference is the exact source provenance plus the fail-closed
admission schema below.

Five exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The immutable `neuphonic/neutts-nano-q4-gguf` snapshot: exact GGUF filename(s), 40-hex snapshot revision, per-file byte counts and SHA-256, and the GGUF tokenizer/chat-template metadata. |
| `BLK-02` | The immutable `neuphonic/neucodec` (or `distill-neucodec`) asset set with exact revision, per-file byte counts and SHA-256, plus the selected ONNX decoder variant and an offline load path. |
| `BLK-03` | A reproducible isolated runtime with lock/install digest: `llama-cpp-python` 0.3.36 (Accelerate build), `transformers` 5.1.0, `torch` ≥ 2.8.0, `neucodec` ≥ 0.0.4, offline load, deterministic settings, a fixed seed and a recorded host profile. |
| `BLK-04` | Reviewed NeuTTS Open License 1.0 weight/model-card terms for weights and Outputs: commercial-revenue threshold, attribution/notice, watermark and redistribution conditions, plus the complete notice bundle. |
| `BLK-05` | A rights-cleared, consented frozen text/reference-voice cohort with manual transcripts, language/speaker groups, exact target conditions, output-use terms and fixed-voice, mismatched-reference and ignore-reference controls. |

**Reopen condition.** A caller supplies the immutable Q4 GGUF snapshot and
NeuCodec asset set with every digest, the reviewed weight/model-card and notice
bundle, a locked runtime that loads the snapshot offline, explicit consent,
reference-availability, output-use and commercial-threshold records for every
prompt voice, a frozen rights-cleared cohort with manual transcripts and matched
controls, and the independent quality/listening/timing protocol with agreed
margins. The pinned runtime reproduces approved reference outputs, and a
separate versioned intake records opt-in registration with an OFF default and
independent exact-head review. Until then this task stays `DEFER`.

## Historical execution: provenance only

The research record contains the gated acquisition failure and a successful
`llama-cpp-python` 0.3.36 source build. It contains **no inference result**. It
is transcribed here with its original scope and is **not rerun, not merged task
evidence, not used for evidence and not a qualification**.

| Field | Recorded value |
| --- | --- |
| Candidate | Neuphonic NeuTTS Nano Q4 (GGUF) |
| Mode | Streaming cloned-voice TTS; GGUF; CPU |
| Acquisition | `neuphonic/neutts-nano-q4-gguf` returned HTTP **401** (gated, no authenticated access) |
| Weights acquired | No |
| Historical runtime build | `llama-cpp-python` 0.3.36 built from source with Apple Accelerate (historical) |
| Runtime present now | No; `llama_cpp`, `neucodec`, `torch`, `transformers` and `gguf` are absent from the current interpreter |
| Inference attempted | No |
| Output / waveform | None |
| Seed / streaming chunks | None |
| Content / identity / naturalness | Not measured |
| Alignment / first-output / tail | Not measured |
| Manual transcript | None |
| Device timing / resources | None |

The HTTP 401 and the historical build are listed only to preserve provenance.
They are not decoded, played, scored, pooled or promoted. A source build is not
a weight, a runtime qualification or a call-device latency.

## What this package actually verifies

1. **Source presence and exact pins.** The official source checkout revision,
   the NeuTTS Open License 1.0, project metadata, the model-loading path, the
   streaming example and the streaming test are pinned by SHA-256. This is a
   source-code provenance fact, not a weight, codec or runtime qualification.
2. **Absence evidence.** Twenty-eight fixed workspace/worktree probes and three
   fixed home-cache probes are checked (no recursive workspace walk). All are
   absent. `reference.build_report()` and `verify.py` raise or fail if any probe
   later appears, so a stale “absent” claim cannot be shipped. No neuphonic
   Hugging Face cache entry exists; the unresolved revision is recorded as
   `null`, never invented.
3. **Admission boundary.** A caller Voice cohort manifest has a strict,
   task-local schema. Every malformed, missing, invalid, nonfinite, aliased,
   duplicated, out-of-range or non-integral control is rejected before any state
   change. One structural control is admitted to prove the validator is not
   blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights or invokes a model.
4. **Voice profile accounting.** Permitted inputs/targets, language/speaker
   groups, text/semantic preservation, identity/similarity, naturalness,
   alignment, first-output/tail, exact target condition and independent
   consent/reference/output-use gates are each recorded as **blocked**.
5. **Quality and timing accounting.** Content, identity and naturalness are
   separate blocked outcomes; alignment, first-output/tail, device timing,
   peaks and resources are separate blocked timing rows. No value is inferred
   from the HTTP 401 record, the historical build or a sibling TTS/voice task.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README and merged
   sibling evidence reports are pinned by SHA-256 and verified unchanged.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Freeze permitted input and target references, task and language/speaker groups | blocked | No rights-cleared reference voice, consent record, language/speaker group or frozen target condition. |
| Preserve text and semantic content | blocked | No manual transcript, semantic-content adjudication or reproduced content metric. |
| Identity/similarity as a separate outcome | blocked | No reference-voice similarity score, independent encoder or human identity rating. |
| Naturalness as a separate outcome | blocked | No naturalness rating, blinded listening or preference panel. |
| Record alignment | blocked | No word/phoneme, onset or reference-content alignment. |
| Record first-output/tail timing | blocked | No streaming run, chunk boundary, first-output or tail measurement. |
| Record the exact target condition | blocked | No consent, target-voice specification, language or reference-text policy. |
| Consent, reference availability and output use as independent gates | blocked | No consent, availability or output-use record; the NeuTTS Open License 1.0 clears none of them. |

## Admission contract (task-local; not an SDK, NeuTTS or Voice contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `source`, `weights`, `runtime`,
  `references`, `texts`, `controls`, `outcomes`, `rights`. Unknown and missing
  fields are rejected.
- **Source**: exact 40-hex revision `ac69851…`, canonical absolute source and
  license paths, `license_id="NeuTTS-Open-License-1.0"` and a 64-hex license
  digest. The manifest records provenance; it does not grant weight rights.
- **Weights**: non-empty unique names matching `[a-z0-9][a-z0-9._-]{0,127}`,
  each with a 64-hex SHA-256, byte count 1–4 GiB and 64-hex terms digest. At
  least one name must end in `.gguf` and at least one must contain `neucodec`.
  Exact filenames are intentionally not fabricated; `BLK-01`/`BLK-02` require
  the caller to supply them.
- **Runtime**: Python 3.10–3.13, `llama_cpp_version="0.3.36"`,
  `transformers_version="5.1.0"`, `torch_version ≥ 2.8.0`,
  `neucodec_version ≥ 0.0.4`, CPU, 1–64 threads, a fixed seed 0–2³¹−1 and
  `deterministic_algorithms=true`; any other value is rejected.
- **References**: unique slug IDs, canonical absolute paths, 64-hex digests,
  consent/rights/speaker slugs and a language tag.
- **Texts**: unique IDs, non-empty text ≤4,096 characters, language tag,
  speaker/consent/output-use slugs, and a reference ID whose digest must match
  the declared reference.
- **Controls**: exactly one each of `fixed_voice`, `mismatched_reference` and
  `ignore_reference`; mismatched reference must name a declared reference, the
  others must not.
- **Outcomes**: WER 0–1, cosine −1–1, MOS 1–5, alignment 0–96,000 samples,
  nonnegative first-output/tail, peak 0–4, clipped fraction 0–1,
  `nonfinite_count=0` and a positive sample count. These are admission bounds,
  not measured results.
- **Rights**: non-empty consent reference, reference availability, output use,
  commercial-terms review, terms review and listening protocol; a 1–1,000
  person panel. The schema does not assert that any real right has been granted.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-conversion-eval-20261101/README.md` | `b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074` | Historical HTTP 401 record |
| `source:…/repos/neutts/LICENSE` | `c3308963748766e2617138a754a0f6915564aae7a4cc31c7d60dc30abf326224` | NeuTTS Open License 1.0 |
| `source:…/repos/neutts/README.md` | `df870ea2ac040be5fdf25555d8c6b804d6119991653ee1530853186d0b26d68b` | Model/GGUF/license/watermark statements |
| `source:…/repos/neutts/pyproject.toml` | `3d74df60f0db27733b308c93b88ae95f9deaa8f396f48183b0cf4f14eb3deb94` | Declared runtime and version |
| `source:…/repos/neutts/neutts/neutts.py` | `88295403fdf5bb14dfc0df712231c57f5000afc470c9f197c590cf082f8bd7ed` | Exact GGUF/codec load path |
| `source:…/repos/neutts/examples/basic_streaming_example.py` | `dde68cb743b62db45b656d77444eb3a558b91fd04fe56d33ae676d9db771e2db` | Exact streaming invocation |
| `source:…/repos/neutts/tests/test_neutts.py` | `8aff58d09fb04ad0cd2941b0f5d1a10fa63447ac2628be2e9eb0764429c868c7` | GGUF/codec combinations |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `neutts-nano-q4` row, Voice profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Voice profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/survey-trn-05/README.md` | `81b51f5696142a7fb77dd285e1db866f550de0faf5e5160ed66d15499b64c26b` | Merged TTS/cloning survey, boundary only |
| `docs/task-evidence/chatterbox-nano/report.json` | `153a48e767fe368ed063ac7ba8543b243f62071a21513d985a2f5dd74de0cf95` | Merged sibling, not reused |
| `docs/task-evidence/cosyvoice-2-0-5b/report.json` | `aee352f4b45d3ad11af6372886a5f2a1e6458ef8d0d89d597f4c8379787b75f2` | Merged sibling, not reused |
| `docs/task-evidence/kokoro-82m/report.json` | `ee057a4ac944dd6af9f1c8845abbcc056fb9c81076ae17bfa78ab3092c6bd06c` | Merged sibling, not reused |

The shared board row is read only by `verify.py`, and only through the stable
projection `{id, title, component, mode, repository, depends_on}`. `status`,
`owner`, `claim`, `review`, `handoff`, `blocked_reason` and
`dispatch_priority` are excluded from gating, so a board state transition
cannot promote or block this package's claims. The full mutable `TASKS.json`
bytes are never hashed.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Upstream/license/weight/reference-voice boundary; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, absence/projection checks, manifest admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/neutts-nano-q4` with Python 3.12 and stdlib only:

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
byte_identical=true profile=Voice status=incomplete decision=DEFER`; REUSE
reports no missing or bad license; `git diff --check` is clean. `verify.py`
itself writes only to a temporary directory and never to this package.

Current counts: 28 workspace/worktree absence probes plus 3 home-cache probes
(0 present), 6 required artifacts (1 source present, 5 blocked), 5 open
blockers, 161 rejected admission controls, 1 schema-only control, 8 blocked
Voice rows, 3 blocked quality outcomes, 3 blocked timing rows, 8 blocked gates,
0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision, archive and license provenance | blocked | Exact archive or checkout, 40-hex revision, tree digest and complete license/notice set supplied and reviewed. |
| `RG-02` Q4 GGUF weights assets and terms | blocked | Immutable Q4 GGUF snapshot with per-file digests, tokenizer metadata and reviewed weight/model-card terms. |
| `RG-03` NeuCodec codec assets and terms | blocked | Immutable NeuCodec snapshot with per-file digests and reviewed codec/model-card terms. |
| `RG-04` pinned runtime and offline load | blocked | Locked runtime with install digest loads the pinned snapshot offline with deterministic settings and a fixed seed. |
| `RG-05` consent, reference availability, output use and commercial terms | blocked | Signed consent, availability, output-use and commercial-threshold review for every prompt voice and output. |
| `RG-06` rights-cleared text and voice cohort | blocked | Immutable cohort, manual transcripts, language/speaker groups, target conditions and matched controls. |
| `RG-07` separate content, identity, naturalness and listening | blocked | Pinned scorers and an approved blinded listening protocol produce reviewed results. |
| `RG-08` alignment, timing, resources, provider intake and release | blocked | Target-device paced runs record alignment, first-output/tail, peaks, nonfinite behavior, CPU, memory and deadlines; a separate versioned intake with OFF default and exact-head review passes. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

`survey-trn-05` is a merged taxonomy map for reference-conditioned voice
cloning/TTS. This package does not reuse its numbers, status or conclusions.
Chatterbox Nano, CosyVoice 2, Kokoro and the NeuTTS-Air gated-checkpoint lead are
different tasks or bounds only; none is pooled or reinterpreted as NeuTTS Nano
Q4 evidence. In particular, NeuTTS-Air uses Apache-2.0 while NeuTTS-Nano uses the
NeuTTS Open License 1.0, and Air weights are **not** Nano weights; this package
does not substitute one for the other. The upstream bundled `samples/*` and
`output.wav` are repository content, not consented references or run results.

## Expected digest

`report.json` SHA-256:
`9593511d7510b2ff40b99210547c0d992c3f5e1419ac104976ed3766432ac740`.

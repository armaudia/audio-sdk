<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NEUTTS-AIR-GATED-CHECKPOINT-LEAD — NeuTTS Air gated-checkpoint blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`NeuTTS Air / gated checkpoint lead`
(`component_id=neutts-air-gated-checkpoint-lead`, task mode `feasibility`). The
structured inventory assigns the **Voice** acceptance profile
(`verification_profile: voice`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER** before any implementation or
intake step; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does **not** contain, import, build, link, download, load or
execute NeuTTS, an Air weight, an Air Q4/Q8 GGUF snapshot, a NeuCodec asset, a
PyTorch or `llama-cpp-python` runtime, a reference voice or an inference path.
It decodes, plays and analyzes no audio, generates no speech, clones no voice
and measures no content, identity, similarity, naturalness, alignment,
first-output/tail, peak, device timing, resource, benchmark or release result.
Only a whole-file SHA-256 provenance check is performed on the upstream demo
`output.wav`, and it is not loaded as a signal. It records the exact missing
artifacts, the gated-access requirement and the unresolved license conflict,
probes a fixed list of workspace and home-cache paths to evidence their
absence, records the one historical acquisition failure as provenance only, and
defines a fail-closed admission boundary for the Voice cohort a future qualified
run would need. Only `docs/task-evidence/neutts-air-gated-checkpoint-lead/` is
written; no provider, registry, descriptor, public header/ABI, shared CMake, CI
workflow or installed-v0 behavior changes.

## Exact external blocker

The official `neuphonic/neutts` code checkout is present at the pinned revision
`ac69851f28fc63a487917e7c2e27f0d75c759cba` and includes the `neuttsair`
subclass. Two independent blockers prevent admission:

1. **Gated checkpoints.** The research record states that the available
   NeuTTS Nano/Air GGUF repositories require accepting gated Hugging Face
   conditions and returned **HTTP 401** with no authenticated access; only
   public models were used and no alternate route was attempted. No Air
   PyTorch or Q4/Q8 GGUF snapshot, revision or per-file digest exists in this
   workspace or in the Hugging Face cache.
2. **Unresolved license conflict.** The repository `LICENSE` text is the
   **NeuTTS Open License v1.0** (revenue threshold, Output conditions), while
   the upstream `README.md` states that **NeuTTS-Air weights are Apache-2.0**.
   The gated Air model card that would resolve which terms govern the weights
   and Outputs is absent. This package asserts neither reading.

The Q4/Q8 GGUF, PyTorch weights, NeuCodec codec assets, exact runtime, gated
access grant, model-card terms and any consented reference voice are absent. No
download, reconstruction, proxy or substitute was attempted. Because the
weights, codec and runtime are absent, this package implements no
source-derived model surrogate or partial inference path; the smallest
verifiable reference is the exact source provenance, the closed checkpoint gate,
the open license-conflict record and the fail-closed admission schema below.

Five exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | A recorded gated-access grant plus the immutable `neuphonic/neutts-air` PyTorch snapshot or `neutts-air-q4-gguf` / `-q8-gguf` snapshot: exact filenames, 40-hex revision, per-file byte counts, SHA-256 and tokenizer/chat-template metadata. |
| `BLK-02` | The immutable `neuphonic/neucodec` (or `distill-neucodec`) asset set with exact revision, per-file byte counts and SHA-256, plus the selected ONNX decoder variant and an offline load path. |
| `BLK-03` | A reproducible isolated runtime with lock/install digest: `torch` ≥ 2.8.0, `transformers` 5.1.0, `neucodec` ≥ 0.0.4 and, for GGUF, `llama-cpp-python` 0.3.36; offline load, deterministic settings, a fixed seed and a recorded host profile. |
| `BLK-04` | A reviewed Air model card, weight and Output terms that reconcile the README Apache-2.0 claim with the repository NeuTTS Open License v1.0, including commercial, attribution, watermark, redistribution and notice obligations, plus the access grant. |
| `BLK-05` | A rights-cleared, consented frozen text/reference-voice cohort with manual transcripts, language/speaker groups, exact target conditions, output-use terms and fixed-voice, mismatched-reference and ignore-reference controls. |

**Reopen condition.** A caller supplies the recorded gated-access grant, the
immutable Air weight snapshot and NeuCodec asset set with every digest, the
reviewed model-card/weight/Output terms and notice bundle, a locked runtime that
loads the snapshot offline, explicit consent, reference-availability and
output-use records for every prompt voice, a frozen rights-cleared cohort with
manual transcripts and matched controls, and the independent
quality/listening/timing protocol with agreed margins. The pinned runtime
reproduces approved reference outputs, and a separate versioned intake records
opt-in registration with an OFF default and independent exact-head review.
Until then this task stays `DEFER`.

## Closed checkpoint gate

| Field | Recorded value |
| --- | --- |
| Candidate | Neuphonic NeuTTS Air (~360M active parameters, phoneme input) |
| Repositories | `neuphonic/neutts-air`, `neuphonic/neutts-air-q4-gguf`, `neuphonic/neutts-air-q8-gguf` |
| Gating condition | Accepting gated Hugging Face conditions is required before any weight file can be fetched |
| Recorded acquisition | HTTP **401**, no authenticated access (research record) |
| Access grant present | No |
| Authenticated attempt | No |
| Anonymous download attempt | No |
| Weights present | No |
| Revision / per-file digests | `null` / none — intentionally not invented |
| Admitted | No |

## License conflict (open)

| Field | Value |
| --- | --- |
| Upstream README Air claim | `Apache-2.0` |
| Upstream README row | `| **License** | Apache 2.0 | NeuTTS Open License 1.0 |` |
| Repository `LICENSE` | `NeuTTS-Open-License-1.0`, SHA-256 `c3308963…6aef0f326224` |
| Air model card present | No (gated) |
| Air weight/Output terms present | No |
| Conflict | Yes |
| Resolved | **No**; `resolved_license_id=null` |
| Resolution requires | The exact gated Air model card and weight terms at a pinned revision, reviewed against the repository license and the Apache-2.0 README claim |

Neither `Apache-2.0` nor the NeuTTS Open License v1.0 is asserted as the Air
weight or Output license here. The Apache-2.0 claim may not be assumed.

## Historical execution: provenance only

The research record contains the gated acquisition failure. It contains **no
Air inference result** and **no Air runtime build**. The `llama-cpp-python`
0.3.36 source build in that record belongs to the separate NeuTTS Nano Q4
attempt. It is transcribed here with its original scope and is **not rerun, not
merged Air evidence, not used for evidence and not a qualification**.

| Field | Recorded value |
| --- | --- |
| Candidate | Neuphonic NeuTTS Air (gated PyTorch/Q4/Q8) |
| Mode | Streaming cloned-voice TTS; PyTorch or GGUF; CPU |
| Acquisition | Gated repositories returned HTTP **401** (no authenticated access) |
| Weights acquired | No |
| Air runtime build | None |
| Runtime present now | No qualified locked runtime supplied |
| Inference attempted | No |
| Output / waveform | None |
| Seed / streaming chunks | None |
| Content / identity / naturalness | Not measured |
| Alignment / first-output / tail | Not measured |
| Manual transcript | None |
| Device timing / resources | None |

The HTTP 401 is listed only to preserve provenance. It is not decoded, played,
scored, pooled or promoted. A source build recorded for another task is not an
Air weight, an Air runtime qualification or a call-device latency.

## What this package actually verifies

1. **Source presence and exact pins.** The official source checkout revision,
   its repository license, project metadata, the shared loader
   (`neutts/neutts.py`), the `neuttsair` subclass module, the phonemizer, the
   streaming example and the streaming test are pinned by SHA-256. This is a
   source-code provenance fact, not a weight, codec or runtime qualification.
2. **Closed checkpoint gate.** Three Air repositories are enumerated with the
   gated condition and HTTP 401 provenance; access grant, weights, revision,
   per-file digests and admission are all recorded `false`/`null`. No value is
   invented.
3. **License conflict record.** The README Apache-2.0 claim and the repository
   NeuTTS Open License v1.0 are both pinned and recorded as an unresolved
   conflict. The package does not choose a license.
4. **Absence evidence.** Thirty-two fixed workspace/worktree probes and five
   fixed home-cache probes are checked (no recursive workspace walk). All are
   absent. `reference.build_report()` and `verify.py` raise or fail if any probe
   later appears, so a stale “absent” claim cannot be shipped. No neuphonic
   Hugging Face cache entry exists; the unresolved revision is recorded as
   `null`, never invented.
5. **Admission boundary.** A caller Voice cohort manifest has a strict,
   task-local schema. Every malformed, missing, invalid, nonfinite, aliased,
   duplicated, out-of-range or non-integral control is rejected before any
   state change. One structural control is admitted to prove the validator is
   not blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights or invokes a model.
6. **Voice profile accounting.** Permitted inputs/targets, language/speaker
   groups, text/semantic preservation, identity/similarity, naturalness,
   alignment, first-output/tail, exact target condition and independent
   consent/reference/output-use gates are each recorded as **blocked**.
7. **Quality and timing accounting.** Content, identity and naturalness are
   separate blocked outcomes; alignment, first-output/tail, device timing,
   peaks and resources are separate blocked timing rows. No value is inferred
   from the HTTP 401 record, the Nano build or a sibling TTS/voice task.
8. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
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
| Consent, reference availability and output use as independent gates | blocked | No consent, availability or output-use record; neither the repository license nor the unverified Apache-2.0 claim clears them. |

## Admission contract (task-local; not an SDK, NeuTTS or Voice contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `source`, `weights`, `runtime`,
  `references`, `texts`, `controls`, `outcomes`, `rights`. Unknown and missing
  fields are rejected.
- **Source**: exact 40-hex revision `ac69851…`, canonical absolute source,
  license and model-card paths, `license_id="Apache-2.0"` as a **caller
  declaration only**, 64-hex license digest and a 64-hex model-card digest.
  The schema records provenance; the contract does not grant weight rights.
- **Weights**: non-empty unique names matching `[a-z0-9][a-z0-9._-]{0,127}`,
  each with a 64-hex SHA-256, byte count 1–4 GiB and 64-hex terms digest. At
  least one non-codec name must end in `.gguf` or `.safetensors` and at least
  one name must contain `neucodec`. Exact filenames are intentionally not
  fabricated; `BLK-01`/`BLK-02` require the caller to supply them.
- **Runtime**: Python 3.10–3.13; `backend` exactly `torch` or `gguf`;
  `llama_cpp_version="0.3.36"` for `gguf` and `null` for `torch`;
  `transformers_version="5.1.0"`; `torch_version` ≥ 2.8.0;
  `neucodec_version` ≥ 0.0.4; CPU; 1–64 threads; a fixed seed 0–2³¹−1 and
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
  gated access grant, weight-terms review, terms review and listening protocol;
  a 1–1,000 person panel. The schema does not assert that any real right has
  been granted.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-conversion-eval-20261101/README.md` | `b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074` | Historical HTTP 401 and public-only policy |
| `source:…/repos/neutts/LICENSE` | `c3308963748766e2617138a754a0f6915564aae7a4cc31c7d60dc30abf326224` | Repository NeuTTS Open License v1.0 |
| `source:…/repos/neutts/README.md` | `df870ea2ac040be5fdf25555d8c6b804d6119991653ee1530853186d0b26d68b` | Air Apache-2.0 claim, model list, watermark |
| `source:…/repos/neutts/pyproject.toml` | `3d74df60f0db27733b308c93b88ae95f9deaa8f396f48183b0cf4f14eb3deb94` | Declared runtime and version |
| `source:…/repos/neutts/CMakeLists.txt` | `bafe8e5131ebcf804a27679b2de91ad7d8a901e70c9d22c4688d5d49a2f5e267` | Espeak data build for phonemes |
| `source:…/repos/neutts/neutts/neutts.py` | `88295403fdf5bb14dfc0df712231c57f5000afc470c9f197c590cf082f8bd7ed` | Shared backbone/codec load path |
| `source:…/repos/neutts/neutts/phonemizers.py` | `737d1138839271f06bf762552de376f1c6816460bbf5855b51192b717d67d9cb` | Phoneme input path |
| `source:…/repos/neutts/neuttsair/__init__.py` | `6757ea82810bf5b91c52dc0770eeb2e25cb4bc835af7da484951592853bdfd44` | Air subclass export |
| `source:…/repos/neutts/neuttsair/neutts.py` | `d466a4558459667953b65b191af4710d1639efaf2ccb0511a272c72c14a37a25` | Air subclass definition |
| `source:…/repos/neutts/examples/basic_streaming_example.py` | `dde68cb743b62db45b656d77444eb3a558b91fd04fe56d33ae676d9db771e2db` | Exact streaming invocation |
| `source:…/repos/neutts/tests/test_neutts.py` | `8aff58d09fb04ad0cd2941b0f5d1a10fa63447ac2628be2e9eb0764429c868c7` | Backbone/codec combinations |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `neutts-air-gated-checkpoint-lead` row, Voice profile |
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
| `docs/task-evidence/survey-trn-05/report.json` | `fd281bbacb62298102af00da3f304bd564a1f7f25b7be050e5c95ad4e4fc0773` | Merged survey, boundary only |
| `docs/task-evidence/chatterbox-nano/report.json` | `153a48e767fe368ed063ac7ba8543b243f62071a21513d985a2f5dd74de0cf95` | Merged sibling, not reused |
| `docs/task-evidence/cosyvoice-2-0-5b/report.json` | `aee352f4b45d3ad11af6372886a5f2a1e6458ef8d0d89d597f4c8379787b75f2` | Merged sibling, not reused |
| `docs/task-evidence/kokoro-82m/report.json` | `ee057a4ac944dd6af9f1c8845abbcc056fb9c81076ae17bfa78ab3092c6bd06c` | Merged sibling, not reused |
| `docs/task-evidence/neutts-nano-q4/report.json` | `9593511d7510b2ff40b99210547c0d992c3f5e1419ac104976ed3766432ac740` | Merged NeuTTS sibling, not reused |

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
| `contract.json` | Machine-readable contract: pins, artifacts, checkpoint gate, license conflict, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, absence/projection checks, manifest admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, checkpoint gate, license conflict, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/neutts-air-gated-checkpoint-lead` with Python 3.12 and
stdlib only:

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
byte_identical=true profile=Voice mode=feasibility status=incomplete
decision=DEFER`; REUSE reports no missing or bad license; `git diff --check` is
clean. `verify.py` itself writes only to a temporary directory and never to
this package.

Current counts: 32 workspace/worktree absence probes plus 5 home-cache probes
(0 present), 6 required artifacts (1 source present, 5 blocked), 5 open
blockers, 3 gated Air repositories (0 granted, 0 weights), 1 open license
conflict, 179 rejected admission controls, 1 schema-only control,
8 blocked Voice rows, 3 blocked quality outcomes, 3 blocked timing rows, 8
blocked gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision, license conflict and notice provenance | blocked | Exact checkout revision, tree digest and complete license/notice set supplied, and the Air Apache-2.0 README claim reconciled with the repository NeuTTS Open License v1.0 by the pinned Air model card. |
| `RG-02` gated Air checkpoint access and weight assets | blocked | Recorded gated-access grant and an immutable Air PyTorch or Q4/Q8 GGUF snapshot with per-file digests and tokenizer metadata. |
| `RG-03` NeuCodec codec assets and terms | blocked | Immutable NeuCodec snapshot with per-file digests and reviewed codec/model-card terms. |
| `RG-04` pinned runtime and offline load | blocked | Locked runtime with install digest loads the pinned Air snapshot and codec offline with deterministic settings and a fixed seed. |
| `RG-05` weight terms, Output use, watermark and commercial review | blocked | Reviewed Air model-card, weight and Output terms resolve commercial, attribution, watermark, redistribution and notice obligations. |
| `RG-06` rights-cleared text and voice cohort | blocked | Immutable cohort, manual transcripts, language/speaker groups, target conditions and matched controls. |
| `RG-07` separate content, identity, naturalness and listening | blocked | Pinned scorers and an approved blinded listening protocol produce reviewed results. |
| `RG-08` alignment, timing, resources, provider intake and release | blocked | Target-device paced runs record alignment, first-output/tail, peaks, nonfinite behavior, CPU, memory and deadlines; a separate versioned intake with OFF default and exact-head review passes. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

`survey-trn-05` is a merged taxonomy map for reference-conditioned voice
cloning/TTS. This package does not reuse its numbers, status or conclusions.
The merged `neutts-nano-q4` package is a **different task**: its Q4 weights,
NeuCodec files, historical `llama-cpp-python` build and license review are not
Air weights, an Air runtime or Air terms, and are not pooled here. NeuTTS-Air
weights are not NeuTTS-Nano weights even though both share the same upstream
code checkout, and the README Apache-2.0 claim applies only to the Air row while
the repository LICENSE text is the NeuTTS Open License v1.0. The upstream
bundled `samples/*` and `output.wav` are repository content, not consented
references or run results. Chatterbox Nano, CosyVoice 2 and Kokoro are separate
bounds only; none is pooled or reinterpreted as NeuTTS Air evidence.

## Expected digest

`report.json` SHA-256:
`f56c65c237c136ba8c4a8942c6b404a8370f8f31b29a4c7169c4d9b432ba1846`.

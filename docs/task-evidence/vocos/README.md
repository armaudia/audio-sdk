<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-VOCOS — Vocos readiness blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Vocos` (`component_id=vocos`). The structured inventory assigns the **Voice**
acceptance profile (`verification_profile: voice`, `plan/INVENTORY.json`),
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER** before any
implementation or intake step; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does **not** contain, import, build, link, download, load or
execute Vocos, a JIT weight, a PyTorch runtime, a feature tensor, a reference
voice or an inference path. It decodes, plays and analyzes no audio, reads no
mel/feature input, generates no waveform and measures no content,
conditioning, identity, similarity, naturalness, alignment, first-output/tail,
peak, device timing, resource, benchmark or release result. It records the exact
missing artifacts and rights, probes a fixed list of workspace and home-cache
paths to evidence their absence, records the one historical decoder-only run as
provenance only, and defines a fail-closed admission boundary for the Voice
qualification a future run would need. Only `docs/task-evidence/vocos/` is
written; no provider, registry, descriptor, public header/ABI, shared CMake, CI
workflow or installed-v0 behavior changes.

## Exact external blocker

A **modified Vocos-derived source copy** is present at
`research/voice-conversion-eval-20261101/repos/meanvc/vocos`, vendored inside a
MeanVC2 checkout. The containing checkout is at 40-hex revision
`fe5286ae205a26ad4eba64395513130bd5974b46` and its root is Apache-2.0. The
vendored directory carries no separate Vocos `LICENSE`, `NOTICE` or package
metadata. The exact upstream `gemelo-ai/vocos` source revision, its MIT license
and notice set are **absent**, and the local copy is modified (for example it
adds export/conditioning code and prints). Source presence is therefore
recorded but **not admitted**.

The MeanVC2-bundled JIT `vocos.pt` decoder (32 MB) was downloaded for a
historical synthetic benchmark and later removed with the rest of the MeanVC2
weights. No weight file, byte count or SHA-256 is retained. A pinned Torch/JIT
runtime is also absent: `torch` is not installed in the current interpreter and
no lock or install digest exists. No download, reconstruction or substitute was
attempted by this package. Because the exact source, weights and runtime are
absent as a set, this package implements no source-derived model surrogate or
partial inference path; the smallest verifiable reference is the exact source
provenance plus the fail-closed admission schema below.

Five exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The exact upstream `gemelo-ai/vocos` checkout/archive at a 40-hex revision, its MIT license, copyright notice and complete notice bundle, reviewed against the modified vendored copy. |
| `BLK-02` | The immutable `vocos.pt` or exact upstream weight snapshot with repository, 40-hex revision, byte count, SHA-256, selected format and expected mel geometry. |
| `BLK-03` | A locked isolated Torch/JIT runtime with install digest that loads the pinned weights offline with deterministic settings, a fixed seed and a recorded host profile. |
| `BLK-04` | Reviewed weight/model-card/license/notice terms that settle attribution, redistribution, commercial use and generated-output use. |
| `BLK-05` | A rights-cleared frozen mel/feature cohort with consent, exact geometry and hashes, language/speaker groups, output-use terms and matched-feature, mismatched-feature and zero-feature controls. |

**Reopen condition.** A caller supplies the exact upstream source and notices,
the immutable weight snapshot with every digest and mel geometry, the reviewed
weight/model-card/output terms, a locked runtime that loads the snapshot
offline, explicit consent/feature-availability/output-use/commercial-terms
records, a frozen rights-cleared feature cohort with matched controls, and the
independent quality/listening/timing protocol with agreed margins. The pinned
runtime reproduces approved reference outputs, and a separate versioned intake
records opt-in registration with an OFF default and independent exact-head
review. Until then this task stays `DEFER`.

## Historical execution: provenance only

The research record contains one decoder-only run of the MeanVC2-bundled Vocos
JIT decoder on a synthetic 1 s mel. It is transcribed with its original scope
and is **not rerun, not merged task evidence, not used for evidence and not a
qualification**.

| Field | Recorded value |
| --- | --- |
| Candidate | MeanVC2-bundled Vocos JIT decoder |
| Mode | decoder-only synthetic mel; CPU; Torch JIT |
| Input mel shape | `[1, 80, 100]` (model-space, synthetic) |
| Output shape | `[1, 15840]` (16 kHz, 0.99 s) |
| Historical mean decode | `0.17284687500214205` s over 5 post-warm-up calls |
| Historical RTF | `0.17459280303246671` (decoder-only) |
| Output finite | Yes (historical) |
| Historical bundle | 32 MB; removed after the run |
| Weight file / digest retained | None |
| Runtime present now | No; `torch` is absent |
| Output / waveform retained | None |
| Content / conditioning / naturalness | Not measured |
| Alignment / first-output / tail | Not measured |
| Device timing / resources | Not measured |

The historical 173 ms and RTF 0.175 are decoder-only provenance. They are not a
current runtime, quality, device-timing, benchmark or release result and open no
gate.

## What this package actually verifies

1. **Source presence and exact pins.** The modified vendored Vocos copy, the
   MeanVC2 root license/README, the historical benchmark script/result and the
   inventory/verification inputs are pinned by SHA-256. This is provenance, not
   a weight, runtime or quality qualification.
2. **Absence evidence.** Thirty fixed workspace/worktree probes and five fixed
   home-cache probes are checked (no recursive workspace walk). All are absent.
   `reference.build_report()` and `verify.py` raise or fail if any probe later
   appears, so a stale “absent” claim cannot be shipped. No ASLP-lab/MeanVC
   Hugging Face cache entry exists; the unresolved revision is recorded as
   `null`, never invented.
3. **Admission boundary.** A caller qualification manifest has a strict,
   task-local schema. Every malformed, missing, invalid, nonfinite, aliased,
   duplicated, out-of-range or non-integral control is rejected before any
   state change. One structural control is admitted to prove the validator is
   not blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads a feature tensor, loads weights or invokes a model.
4. **Voice profile accounting.** Permitted inputs/targets, language/speaker
   groups, content/intelligibility, conditional identity, naturalness,
   alignment, first-output/tail, exact target condition and independent
   consent/input/output-use gates are each recorded as **blocked**.
5. **Quality and timing accounting.** Content/intelligibility, mel conditioning
   fidelity, naturalness and conditional identity are separate blocked
   outcomes; alignment, first-output/tail, device timing/resources and
   benchmark/RTF are separate blocked timing rows. No value is inferred from
   the historical run or a sibling vocoder/TTS task.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README and merged
   sibling evidence reports are pinned by SHA-256 and verified unchanged.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Freeze permitted input and target references, task and language/speaker groups | blocked | No rights-cleared feature cohort, consent record, language/speaker group or exact target condition. |
| Preserve content: intelligibility, semantic content and feature conditioning | blocked | No generated waveform, manual transcript, intelligibility score or feature-conditioning result. |
| Identity/similarity as a separate outcome, only when the decoder is explicitly speaker-conditioned | blocked | No selected speaker-conditioned model, encoder, reference target or human identity rating. |
| Naturalness as a separate outcome | blocked | No naturalness rating, blinded listening or preference panel. |
| Record alignment | blocked | No frame/sample alignment, onset mapping or feature-output content mapping. |
| Record first-output/tail timing | blocked | No streaming run, chunk boundary, first-output or tail measurement. |
| Record the exact target condition | blocked | No model/weight identity, mel geometry, sample rate, hop, precision, runtime or device target. |
| Consent, reference availability and output use as independent gates | blocked | No consent, feature-availability or output-use record; the repository and model terms clear none of them. |

## Admission contract (task-local; not an SDK or Vocos contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `source`, `weights`, `runtime`,
  `features`, `controls`, `outcomes`, `rights`. Unknown and missing fields are
  rejected.
- **Source**: exact vendored 40-hex revision `fe5286ae…`, canonical absolute
  source and license paths, `license_id="Apache-2.0"`, a 64-hex license digest,
  a 40-hex upstream revision and a 64-hex upstream-license digest. The manifest
  records provenance; it does not grant weight rights.
- **Weights**: non-empty unique names matching `[a-z0-9][a-z0-9._-]{0,127}`,
  canonical absolute paths, 64-hex SHA-256, byte count 1–8 GiB, a declared
  format (`jit_torchscript`, `pytorch_state_dict`, `safetensors`, `onnx`), a
  64-hex terms digest, at least one name containing `vocos`, and an allowed
  suffix (`.pt`, `.pth`, `.safetensors`, `.onnx`). Exact filenames are
  intentionally not fabricated; `BLK-02` requires the caller to supply them.
- **Runtime**: Python 3.10–3.13, a semver Torch version, CPU, 1–64 threads, a
  fixed seed 0–2³¹−1, `deterministic_algorithms=true` and a 64-hex install
  digest. Any other value is rejected.
- **Features**: unique slug IDs, canonical absolute paths, 64-hex digests, a
  declared input sample rate, 1–256 mels, 1–2,048 hop samples, 1–1,000,000
  frames, a declared feature kind, consent/rights/speaker slugs and a language
  tag.
- **Controls**: exactly one each of `matched_features`, `mismatched_features`
  and `zero_features`; matched/mismatched must name a declared feature and
  match its digest; zero features must name neither.
- **Outcomes**: mel spectral convergence 0–100, WER 0–1, STOI 0–1, MOS 1–5,
  cosine −1–1, alignment 0–96,000 samples, nonnegative first-output/tail, peak
  0–4, clipped fraction 0–1, `nonfinite_count=0`, a positive sample count and a
  declared output sample rate. These are admission bounds, not measured
  results.
- **Rights**: non-empty consent reference, input availability, output use,
  commercial-terms review, terms review and listening protocol; a 1–1,000
  person panel. The schema does not assert that any real right has been
  granted.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/accent-conversion-20261101/README.md` | `c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c` | Historical decoder-only record |
| `source:research/accent-conversion-20261101/benchmark_vocos_cpu.py` | `6daf428ff4862d74b77fb7eaee4ea513c1078796eb88ead28d6d6c49ac3117c1` | Historical synthetic benchmark |
| `source:research/accent-conversion-20261101/results/vocos-cpu-benchmark.json` | `1948ef27a8ff6f1ddeb24312b0a75ff0303dc6ef05bb2c659c014651cb480741` | Historical result, provenance only |
| `source:…/repos/meanvc/LICENSE` | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` | MeanVC2 Apache-2.0 root |
| `source:…/repos/meanvc/README.md` | `5421a6346a5b1fdb93722307898d5019a3c22756b90333139cd0ac30a94b0f8d` | Upstream credit and model statement |
| `source:…/repos/meanvc/download_ckpt.py` | `f08930c9af4afbe6992809dd27a2d0259f8fe2565d98c207b191f8d064d0f83d` | Historical `vocos.pt` source |
| `source:…/repos/meanvc/vocos/__init__.py` | `89adaa6f53c75f96f53ee8fc79720e701f109b242d6f7a78fa51fa9a35e07ec6` | Vendored copy |
| `source:…/repos/meanvc/vocos/models.py` | `47065294c38d042f01262e39dd50b437231506facdb13f3aaa960db9cc31b5e8` | Vendored copy |
| `source:…/repos/meanvc/vocos/modules.py` | `f60b36d6af92cef1baa8e22f8cc6a75a18467ffbe0543e8c232992dbccecfe59` | Vendored copy |
| `source:…/repos/meanvc/vocos/pretrained.py` | `07773c3146e072fb609dd99468ce9667e6dfbb73c869dd7472b8b142890c002d` | Vendored copy |
| `source:…/repos/meanvc/vocos/heads.py` | `1ae5389805e63a77eaaf36502396591e34e0d92ccc4ae94e69e3f495f551a38d` | Vendored copy |
| `source:…/repos/meanvc/vocos/spectral_ops.py` | `5577771daae83a9ffc6df3f1a3ce7f3f9c2543562c8ca3f5aff740ee2b515682` | Vendored copy |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `vocos` row, Voice profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Voice profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/phase-vocoder-baseline/report.json` | `555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7` | Merged vocoder baseline, not reused |
| `docs/task-evidence/chatterbox-nano/report.json` | `153a48e767fe368ed063ac7ba8543b243f62071a21513d985a2f5dd74de0cf95` | Merged sibling, not reused |
| `docs/task-evidence/neutts-nano-q4/report.json` | `9593511d7510b2ff40b99210547c0d992c3f5e1419ac104976ed3766432ac740` | Merged sibling, not reused |
| `docs/task-evidence/survey-trn-05/README.md` | `81b51f5696142a7fb77dd285e1db866f550de0faf5e5160ed66d15499b64c26b` | Merged TTS survey, boundary only |

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
| `LICENSES.md` | Upstream/license/weight/feature boundary; no vendored license text. |
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

From `docs/task-evidence/vocos` with Python 3.12 and stdlib only:

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

Current counts: 30 workspace/worktree absence probes plus 5 home-cache probes
(0 present), 6 required artifacts (1 source present, 5 blocked), 5 open
blockers, 209 rejected admission controls, 1 schema-only control, 8 blocked
Voice rows, 4 blocked quality outcomes, 4 blocked timing rows, 8 blocked gates,
0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision, archive and license provenance | blocked | Exact upstream Vocos archive/checkout, 40-hex revision, tree digest, MIT license/notice set and a reviewed comparison with the vendored copy. |
| `RG-02` Vocos weights identity and mel geometry | blocked | Immutable weight snapshot with per-file byte counts, SHA-256, format and exact mel geometry, verified offline. |
| `RG-03` weight, model-card and output terms | blocked | Reviewed terms settle attribution, redistribution, commercial use and output use. |
| `RG-04` pinned runtime and offline load | blocked | Locked runtime with install digest loads the pinned weights offline deterministically with a fixed seed and host profile. |
| `RG-05` consent, feature availability and output use | blocked | Signed consent, feature-availability, output-use and commercial-terms review for every input and output. |
| `RG-06` rights-cleared feature cohort and conditioning controls | blocked | Immutable cohort, exact geometry, language/speaker groups and matched/mismatched/zero controls. |
| `RG-07` separate content, conditioning, naturalness and listening | blocked | Pinned scorers and an approved blinded listening protocol produce reviewed intelligibility, conditioning, naturalness and conditional identity results. |
| `RG-08` alignment, timing, resources, provider intake and release | blocked | Target-device paced runs record alignment, first-output/tail, peaks, nonfinite behavior, CPU, memory and deadlines; a separate versioned intake with OFF default and exact-head review passes. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

`phase-vocoder-baseline` is a model-free playback/rate comparison, not Vocos.
`vocos-vocoder` is a research-control row for generic vocoder components and
does not establish accent transformation. `vocos-bwe` is bandwidth extension
and has no exact model/checkpoint; it is not this decoder. HiFi-GAN and the
other phase-vocoder rows are different tasks or bounds only. Chatterbox Nano,
NeuTTS Nano Q4 and the TTS/voice-cloning survey are merged siblings used only as
boundary pins; none is pooled, reinterpreted or substituted as Vocos evidence.
The historical MeanVC2-bundled decoder is not an upstream release and its
numbers are provenance only.

## Expected digest

`report.json` SHA-256:
`3f961e3fbffb63af701e38dd16914711288facb7f1285b054a2ffc1a5ad3b059`.

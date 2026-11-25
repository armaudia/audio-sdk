<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-OPENVOICE-V2 — OpenVoice V2 readiness blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`OpenVoice V2` (`component_id=openvoice-v2`). The structured inventory assigns
the **Voice** acceptance profile (`verification_profile: voice`,
`plan/INVENTORY.json`), defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER** before any implementation or intake step; `status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. Missing evidence
never qualifies a candidate.

This package does **not** contain, import, build, link, download, load or
execute OpenVoice, a V2 converter checkpoint, a speaker-embedding tensor, the
`checkpoints_v2_0417.zip` release archive, PyTorch, MeloTTS or a pinned runtime.
It decodes, plays and analyzes no audio, converts no voice, and measures no
content, identity, similarity, naturalness, alignment, first-output/tail, peak,
device-timing, resource, benchmark or release result. Only a whole-file SHA-256
provenance check is performed on the retained historical inputs and output, and
they are not loaded as signals. It records the exact missing artifacts and
rights, probes a fixed list of workspace and home-cache paths to evidence their
absence, records the one historical run as provenance only, and defines a
fail-closed admission boundary for the Voice cohort a future qualified run
would need. Only `docs/task-evidence/openvoice-v2/` is written; no provider,
registry, descriptor, public header/ABI, shared CMake, CI workflow or
installed-v0 behavior changes.

## Exact external blocker

The official code checkout is present at the pinned revision
`74a1d147b17a8c3092dd5430504bd83ef6c7eb23` with an MIT `LICENSE`, a verified
37-file tree digest (3,463,846 bytes) and project version `0.0.0`. The V2
converter checkpoint, the official release archive, the speaker-embedding
assets and the exact runtime are **absent**. A V2 converter config-shaped file
is present only inside the Seed-VC vendored OpenVoice module; it is hashed and
disclosed but **not admitted** as the exact release-archive member, and its
companion `checkpoint.pth` does not exist.

The research record states the 125 MiB converter checkpoint was removed after
the historical run; `research/voice-conversion-eval-20261101/checkpoints/` is
empty and no `checkpoints_v2` directory exists in the OpenVoice checkout. No
download, reconstruction or substitute was attempted. Because the archive,
checkpoint and runtime are absent, this package implements no source-derived
model surrogate or partial inference path; the smallest verifiable reference is
the exact source provenance, the observed non-admitted config copy and the
fail-closed admission schema below.

Five exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The immutable official `checkpoints_v2_0417.zip` archive or an equivalent reviewed snapshot at a recorded revision: `checkpoints_v2/converter/config.json`, `checkpoints_v2/converter/checkpoint.pth` and every speaker-embedding asset used, with per-file byte counts and SHA-256. |
| `BLK-02` | A reproducible isolated runtime matching the historical run: CPython 3.11.x, PyTorch 2.15.0, TorchAudio 2.11.1, the pinned OpenVoice source, librosa 0.9.1 and the required audio-I/O compatibility layer, CPU, with a lock/install digest, offline load path, deterministic settings and recorded host profile. |
| `BLK-03` | Reviewed release-archive terms and notice bundle, explicit speaker-reference availability for every source and target used, and generated-output use terms. The upstream README assertion that V1/V2 are MIT is not a staged archive license, consent record or product-use decision. |
| `BLK-04` | A rights-cleared, frozen speech-to-speech cohort with permitted source utterances, target reference speakers, manual transcripts, language/speaker groups, exact target conditions and identity, target and alternate-target controls. |
| `BLK-05` | An agreed Voice protocol that separately measures content preservation, target identity/similarity, naturalness, alignment, first-output/tail, nonfinite/peak behavior, independent listening, device timing, resources and uncertainty. |

**Reopen condition.** A caller supplies the immutable release archive with every
digest, the reviewed archive/notice and speaker-asset terms, a locked runtime
that loads the snapshot offline, explicit speaker-reference availability and
output-use records, a frozen rights-cleared cohort with manual transcripts and
matched controls, and the independent quality/listening/timing protocol with
agreed margins. The pinned runtime reproduces approved reference outputs, and a
separate versioned intake records opt-in registration with an OFF default and
independent exact-head review. Until then this task stays `DEFER`.

## Historical execution: provenance only

The research record contains one successful offline CPU conversion. It is
transcribed here with its original scope and is **not rerun, not merged task
evidence, not used for evidence and not a qualification**.

| Field | Recorded value |
| --- | --- |
| Candidate | MyShell OpenVoice V2 (official repository, `ToneColorConverter`) |
| Mode | Offline whole-utterance tone-color conversion; CPU |
| Runtime recorded | Python 3.11.5 evaluation stack, PyTorch 2.15.0, TorchAudio 2.11.1 |
| Source | LJ Speech `lj001-0001`, 9.648 s, 22.05 kHz processing |
| Target | p360 reference (revised VCTK-style reference), same fixed pair as siblings |
| Converter checkpoint | 125 MiB; **removed after the run** |
| Output | `source_to_p360.wav`, 22.05 kHz, 9.648 s, 425,516 bytes, SHA-256 `1e1fac98e38da71999f6bfe0ca65879c82f7be104dd958f27eb5a0d2bb2709f7` |
| Model init | `0.38248795800609514` s |
| Two speaker embeddings | `0.9023486669757403` s |
| Conversion | `3.292042249988299` s for 9.648 s input; file RTF `0.3412188421905178` |
| Peak / clipping | `0.847869873046875` / `0.0` |
| ASR proxy | Whisper Tiny English WER `0.0` on the source transcript |
| In-model speaker cosine | `0.8901664018630981` to p360 |
| First-audio latency | absent; whole-file offline path, no causal streaming |
| Independent identity / naturalness / listening | not measured |
| Manual transcript adjudication | absent |
| Device timing | absent |
| Multi-speaker / language coverage | absent |

The historical output and the source/target audio are listed only to preserve
provenance. They are not decoded, played, scored, pooled or promoted; only
whole-file SHA-256 provenance checks are recorded. The 0.00 WER proxy is not a
content or semantic certificate, the 0.890 cosine is OpenVoice's own
reference-encoder diagnostic and not an independent or perceptual identity
score, and 0.341× file RTF is not a call-device latency.

## What this package actually verifies

1. **Source presence and exact pins.** The official source checkout revision,
   MIT `LICENSE`, `README.md`, `docs/USAGE.md`, `requirements.txt`, `setup.py`,
   `openvoice/api.py`, `openvoice/models.py`, `openvoice/se_extractor.py` and
   `demo_part3.ipynb` are pinned by SHA-256. The non-`.git` tree is hashed with
   a fixed recipe (37 files, 3,463,846 bytes, SHA-256 `477585d1…`). This is
   source-code provenance, not a weight or runtime qualification.
2. **Observed config copy, not admitted.** The Seed-VC vendored V2 converter
   config (`838` bytes, SHA-256 `9dfff603…`, `_version_="v2"`, 22,050 Hz) is
   hashed and disclosed. It is not treated as the official archive member, its
   companion checkpoint is absent, and it is not used for evidence.
3. **Absence evidence.** Thirty fixed workspace/worktree probes and three fixed
   home-cache probes are checked (no recursive workspace walk). All are absent.
   `reference.build_report()` and `verify.py` raise or fail if any probe later
   appears, so a stale “absent” claim cannot be shipped.
4. **Admission boundary.** A caller Voice cohort manifest has a strict,
   task-local schema. Every malformed, missing, invalid, nonfinite, aliased,
   duplicated, out-of-range or non-integral control is rejected before any
   state change. One structural control is admitted to prove the validator is
   not blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights or invokes a model.
5. **Voice profile accounting.** Permitted input/target references, task and
   language/speaker groups, content preservation, identity/similarity,
   naturalness, alignment, first-output/tail, exact target condition, consent,
   reference availability and output use are each recorded as **blocked**.
6. **Quality and timing accounting.** Content, identity and naturalness are
   separate blocked outcomes; alignment, first-output/tail, device timing,
   peaks and resources are separate blocked timing rows. No value is inferred
   from the historical run or from a sibling voice task.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README and the
   merged survey maps are pinned by SHA-256 and verified unchanged.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Freeze permitted input and target references, task and language/speaker groups | blocked | No rights-cleared source utterance, target reference, consent record, language/speaker group or frozen target condition. |
| Preserve text and semantic content | blocked | No manual transcript, semantic-content adjudication or reproduced content metric; the historical WER proxy is not a certificate. |
| Identity/similarity as a separate outcome | blocked | The historical 0.890 cosine is OpenVoice's own reference-encoder diagnostic on one pair; no independent encoder or perceptual identity rating. |
| Naturalness as a separate outcome | blocked | No naturalness rating, blinded listening or preference panel. |
| Record alignment | blocked | No phoneme, token, word or frame alignment. |
| Record first-output/tail timing | blocked | The published converter is whole-file; only model-init, embedding and conversion wall times exist. |
| Record the exact target condition | blocked | One LJ Speech utterance to a p360 reference on CPU with no reference-availability, target-specification or output-use policy; provenance only. |
| Consent, reference availability and output use as independent gates | blocked | No consent, availability or output-use record; the upstream MIT assertion clears none of them in this package. |

## Admission contract (task-local; not an SDK, OpenVoice or Voice contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `source`, `weights`, `runtime`,
  `references`, `pairs`, `controls`, `outcomes`, `rights`. Unknown and missing
  fields are rejected.
- **Source**: exact 40-hex revision `74a1d147…`, canonical absolute source and
  license paths, `license_id="MIT"` and a 64-hex license digest. The manifest
  records provenance; it does not grant archive or speaker-asset rights.
- **Weights**: non-empty unique names matching the bounded slash-safe pattern,
  each with a 64-hex SHA-256, byte count 1–4 GiB and 64-hex terms digest.
  `checkpoints_v2/converter/config.json` and
  `checkpoints_v2/converter/checkpoint.pth` are mandatory; path traversal,
  absolute and doubled-slash names are rejected.
- **Runtime**: Python 3.11.x, torch `2.15.0`, torchaudio `2.11.1`, openvoice
  `0.0.0`, CPU, 1–64 threads and `deterministic_algorithms=true`; any other
  value is rejected.
- **References**: unique speaker slug IDs, canonical absolute paths, 64-hex
  digests, consent/rights/speaker slugs and a language tag.
- **Pairs**: unique IDs, declared source and target references that must differ,
  a target digest matching the declared reference, a canonical source path and
  digest, non-empty source text ≤4,096 characters, a language tag and
  consent/output-use slugs.
- **Controls**: exactly one each of `source_identity`, `target_reference` and
  `alternate_target`; the identity control must name a declared source speaker,
  the target control must name a target used by a pair, and the alternate
  target must not be a pair target.
- **Outcomes**: WER 0–1, cosine −1–1, MOS 1–5, alignment 0–96,000 samples,
  nonnegative first-output/tail, peak 0–4, clipped fraction 0–1,
  `nonfinite_count=0` and a positive sample count. These are admission bounds,
  not measured results.
- **Rights**: non-empty consent reference, reference availability, output use,
  terms review and listening protocol; a 1–1,000 person panel. The schema does
  not assert that any real right has been granted.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-conversion-eval-20261101/README.md` | `b2c5e168…` | Historical run and provenance |
| `source:…/results/openvoice/metrics.json` | `322d4998…` | Historical timing/RTF/cosine |
| `source:…/results/openvoice/asr.json` | `30a851e4…` | Historical ASR proxy and peaks |
| `source:…/scripts/run_openvoice_eval.py` | `2060622f…` | Exact historical invocation |
| `source:…/agent-matrix-crosswalk/REPORT.md` | `b7db9a73…` | Crosswalk provenance and scope |
| `source:…/repos/openvoice/LICENSE` | `bb3541f4…` | MIT code license, not archive terms |
| `source:…/repos/openvoice/README.md` | `3c6f5d24…` | Declared V2 model and MIT assertion |
| `source:…/repos/openvoice/docs/USAGE.md` | `8dc88ad1…` | Declared release archive and extraction |
| `source:…/repos/openvoice/requirements.txt` | `ff3a30cd…` | Declared dependency set |
| `source:…/repos/openvoice/setup.py` | `bdc21e07…` | Declared project version |
| `source:…/repos/openvoice/openvoice/api.py` | `6830abaf…` | Exact config/checkpoint/SE load path |
| `source:…/repos/openvoice/openvoice/models.py` | `54f9e828…` | Converter model geometry |
| `source:…/repos/openvoice/openvoice/se_extractor.py` | `deb53f75…` | Tone-color embedding extraction |
| `source:…/repos/openvoice/demo_part3.ipynb` | `b60a930f…` | Exact V2 archive member names |
| `source:…/repos/seed-vc/modules/openvoice/checkpoints_v2/converter/config.json` | `9dfff603…` | Observed config copy, not admitted |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945…` | `openvoice-v2` row, Voice profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f263133…` | Voice profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50…` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f…` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965a…` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74…` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba5…` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc9…` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cd…` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb…` | Unchanged build surface |
| `docs/task-evidence/survey-trn-04/README.md` | `e0b4ea4d…` | Merged VC survey, boundary only |
| `docs/task-evidence/survey-trn-04/report.json` | `fb34a112…` | Merged VC survey, not reused |
| `docs/task-evidence/survey-trn-05/README.md` | `81b51f56…` | Merged TTS/cloning survey, boundary only |
| `docs/task-evidence/survey-trn-05/report.json` | `fd281bba…` | Merged TTS/cloning survey, not reused |

The shared board row is read only by `verify.py` and one test, and only through
the stable projection `{id, title, component, mode, repository, depends_on}`.
`status`, `owner`, `claim`, `review`, `handoff`, `blocked_reason` and
`dispatch_priority` are excluded from gating, so a board state transition
cannot promote or block this package's claims. The full mutable `TASKS.json`
bytes are never hashed.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Upstream/license/archive/speaker-asset boundary; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, source tree, absence/projection checks, manifest admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, board identity, pins, source tree, config copy, report bytes/digest, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/openvoice-v2` with Python 3.12 and stdlib only:

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

Current counts: 30 workspace/worktree absence probes plus 3 home-cache probes
(0 present), 6 required artifacts (1 source present, 5 blocked), 5 open
blockers, 161 rejected admission controls, 1 schema-only control, 8 blocked
Voice rows, 3 blocked quality outcomes, 3 blocked timing rows, 8 blocked gates,
0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision, archive and license provenance | blocked | Immutable source archive matching the pinned revision, tree digest and file count, with the complete MIT license/notice set, supplied and reviewed. |
| `RG-02` weights, speaker assets and terms | blocked | Immutable release archive and all per-file digests supplied, and weight/archive and speaker-asset terms reviewed. |
| `RG-03` pinned runtime and offline load | blocked | Locked CPython 3.11.x runtime loads the pinned snapshot offline with deterministic settings. |
| `RG-04` speaker-reference availability and output use | blocked | Speaker-reference availability and output-use terms staged and reviewed for every source and target reference used. |
| `RG-05` rights-cleared source and target cohort | blocked | Immutable cohort, manual transcripts, groups, target conditions and identity/target/alternate-target controls. |
| `RG-06` separate content, identity, naturalness and listening | blocked | Pinned scorers and an approved blinded listening protocol produce reviewed results. |
| `RG-07` alignment, first-output/tail, peaks and resources | blocked | Target-device paced runs record alignment, timing, peaks, nonfinite behavior, CPU, memory and deadlines. |
| `RG-08` provider intake, public surface and release | blocked | Separate versioned intake with OFF default, public-surface decision and independent exact-head review. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

`survey-trn-04` is a merged taxonomy map for speech-to-speech voice conversion;
this package does not reuse its numbers, status or conclusions. `survey-trn-05`
covers reference-conditioned voice cloning/TTS, a different task. LLVC,
MeanVC2, Chatterbox VC, Seed-VC, RVC, CosyVoice 2, Kokoro 82M and the
Chatterbox Nano TTS control are boundaries only; none is pooled or
reinterpreted as OpenVoice V2 evidence. OpenVoice V2 is an offline tone-color
converter, not a streaming real-time call path, and this package does not
substitute one role for the other.

## Expected digest

`report.json` SHA-256:
`27986b993beca10ae2d9e354fca4102db8795e10d845f3b89d8273fa9531b9c8`.

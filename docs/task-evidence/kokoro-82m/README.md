<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-KOKORO-82M — Kokoro 82M readiness blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Kokoro 82M` (`component_id=kokoro-82m`). The structured inventory assigns the
**Voice** acceptance profile (`verification_profile: voice`,
`plan/INVENTORY.json`), defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER** before any implementation or intake step; `status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. Missing evidence
never qualifies a candidate.

This package does **not** contain, import, build, link, download, load or
execute Kokoro, a Kokoro-82M weight, `config.json`, an `af_heart` voice-style
asset, PyTorch or a pinned runtime. It decodes, plays and analyzes no audio,
generates no speech, clones no voice and measures no content, identity,
similarity, naturalness, alignment, first-output/tail, peak, device timing,
resource, benchmark or release result. Only a whole-file SHA-256 provenance
check is performed on the one historical output, and it is not loaded as a
signal. It records the exact missing artifacts and rights, probes a fixed list
of workspace and home-cache paths to evidence their absence, records the one
historical run as provenance only, and defines a fail-closed admission boundary
for the Voice cohort a future qualified run would need. Only
`docs/task-evidence/kokoro-82m/` is written; no provider, registry, descriptor,
public header/ABI, shared CMake, CI workflow or installed-v0 behavior changes.

## Exact external blocker

The official code checkout is present at the pinned revision
`dfb907a02bba8152ca444717ca5d78747ccb4bec` with an Apache-2.0 `LICENSE`, a
verified 108-file tree digest and project version `0.9.4`. The model weights,
the preset voice-style asset and the exact runtime are **absent**. A code
license is not a weight, voice-asset, model-card or output-use grant. The
research record states that the weights were removed after the historical run;
`research/voice-conversion-eval-20261101/checkpoints/` is empty and
`~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M` does not exist. No
download, reconstruction or substitute was attempted. Because the weights and
runtime are absent, this package implements no source-derived model surrogate
or partial inference path; the smallest verifiable reference is the exact
source provenance plus the fail-closed admission schema below.

Five exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The immutable `hexgrad/Kokoro-82M` snapshot: `config.json`, `kokoro-v1_0.pth`, `voices/af_heart.pt`, a 40-hex snapshot revision, per-file byte counts and SHA-256. |
| `BLK-02` | A reproducible isolated runtime matching the historical run: CPython 3.11.x, `kokoro 0.9.4`, `misaki 0.9.4`, `torch 2.15.0`, `torchaudio 2.11.1`, CPU, with a lock/install digest, offline load path, deterministic settings and recorded host profile. |
| `BLK-03` | Reviewed weight/model-card terms plus explicit preset-voice asset terms, availability and generated-output use terms. The code Apache-2.0 license covers none of these. |
| `BLK-04` | A rights-cleared, frozen text/preset-voice cohort with manual transcripts, language/speaker groups, exact target conditions and fixed-voice, alternate-voice and text-control controls. |
| `BLK-05` | An agreed Voice protocol that separately measures text/semantic preservation, preset-identity/similarity, naturalness, alignment, first-output/tail, nonfinite/peak behavior, independent listening, device timing, resources and uncertainty. |

**Reopen condition.** A caller supplies the immutable weight/config/voice
snapshot with every digest, the reviewed weight/model-card and notice bundle, a
locked runtime that loads the snapshot offline, explicit voice-asset
availability and output-use records, a frozen rights-cleared cohort with manual
transcripts and matched controls, and the independent quality/listening/timing
protocol with agreed margins. The pinned runtime reproduces approved reference
outputs, and a separate versioned intake records opt-in registration with an
OFF default and independent exact-head review. Until then this task stays
`DEFER`.

## Historical execution: provenance only

The research record contains one successful whole-utterance CPU run. It is
transcribed here with its original scope and is **not rerun, not merged task
evidence, not used for evidence and not a qualification**.

| Field | Recorded value |
| --- | --- |
| Candidate | hexgrad/Kokoro-82M (official repository) |
| Mode | Fixed-voice whole-utterance TTS; CPU; 4 Torch threads; speed 1 |
| Runtime recorded | Python 3.11.5 evaluation stack, `kokoro 0.9.4` |
| Preset voice | `af_heart` (fixed preset; no reference-voice cloning) |
| Text | One 27-word English sentence (the fixed evaluation text) |
| Output | `af_heart.wav`, 24 kHz, 9.025 s, 433,244 bytes, SHA-256 `85de4ae78e14aa7826f7f3bf6572adc2366a0338c33aac914f65957bbea233fa` |
| Segments | 1 (whole utterance); no incremental streaming chunks |
| First segment | `57.297223249974195` s after start; `3.841400207951665` s after pipeline init |
| Total wall | `57.29795258399099` s; audio-per-wall RTF `0.1575099910729023` |
| Peak / clipping | `0.37054443359375` / `0.0` |
| ASR proxy | Whisper Tiny English WER `0.0` on the same one text |
| First-audio latency | absent; one whole segment, not a streaming first output |
| Identity/similarity | not measured |
| Naturalness / listening | not measured |
| Manual transcript | absent |
| Device timing | absent |
| Multi-speaker / language coverage | absent |

The historical output is listed only to preserve provenance. It is not
decoded, played, scored, pooled or promoted; only a whole-file SHA-256
provenance check is recorded. A 0.00 WER proxy is not a content, semantic,
preset-identity or naturalness certificate, and 0.158× audio-per-wall RTF is
not a call-device latency.

## What this package actually verifies

1. **Source presence and exact pins.** The official source checkout revision,
   Apache-2.0 `LICENSE`, project metadata, model loader, pipeline loader and
   README are pinned by SHA-256. The non-`.git` tree is hashed with a fixed
   recipe (108 files, 29,147,679 bytes, SHA-256 `2530843b…`). This is
   source-code provenance, not a weight or runtime qualification.
2. **Absence evidence.** Twenty-seven fixed workspace/worktree probes and two
   fixed home-cache probes are checked (no recursive workspace walk). All are
   absent. `reference.build_report()` and `verify.py` raise or fail if any probe
   later appears, so a stale “absent” claim cannot be shipped.
3. **Admission boundary.** A caller Voice cohort manifest has a strict,
   task-local schema. Every malformed, missing, invalid, nonfinite, aliased,
   duplicated, out-of-range or non-integral control is rejected before any
   state change. One structural control is admitted to prove the validator is
   not blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights or invokes a model.
4. **Voice profile accounting.** Permitted input/target conditions, language
   and speaker groups, text/semantic preservation, preset-identity/similarity,
   naturalness, alignment, first-output/tail, exact target condition and
   independent voice-availability/output-use gates are each recorded as
   **blocked**.
5. **Quality and timing accounting.** Content, identity and naturalness are
   separate blocked outcomes; alignment, first-output/tail, device timing,
   peaks and resources are separate blocked timing rows. No value is inferred
   from the historical run or from a sibling TTS/voice task.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README and the
   merged survey maps are pinned by SHA-256 and verified unchanged.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Freeze permitted input text and target preset voice, task and language/speaker groups | blocked | No rights-cleared text set, preset-voice terms, or frozen target condition. |
| Preserve text and semantic content | blocked | No manual transcript, semantic-content adjudication or reproduced content metric; the historical WER proxy is not a certificate. |
| Identity/similarity as a separate outcome | blocked | No preset-voice consistency score or human identity rating; Kokoro is a fixed-voice TTS control, not a cloning model. |
| Naturalness as a separate outcome | blocked | No naturalness rating, blinded listening or preference panel. |
| Record alignment | blocked | No phoneme, token or word alignment. |
| Record first-output/tail timing | blocked | The historical generator returned one whole segment; no streaming first output or tail. |
| Record the exact target condition | blocked | One 27-word English sentence with `af_heart` at speed 1 and no voice-asset terms or target specification; provenance only. |
| Voice availability and output use as independent gates | blocked | No voice-availability or output-use record; the code Apache-2.0 license clears neither. |

## Admission contract (task-local; not an SDK, Kokoro or Voice contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `source`, `weights`, `runtime`,
  `references`, `texts`, `controls`, `outcomes`, `rights`. Unknown and missing
  fields are rejected.
- **Source**: exact 40-hex revision `dfb907a…`, canonical absolute source and
  license paths, `license_id="Apache-2.0"` and a 64-hex license digest. The
  manifest records provenance; it does not grant weight rights.
- **Weights**: non-empty unique names matching the bounded slash-safe pattern,
  each with a 64-hex SHA-256, byte count 1–4 GiB and 64-hex terms digest.
  `config.json`, `kokoro-v1_0.pth` and `voices/af_heart.pt` are mandatory; path
  traversal, absolute and doubled-slash names are rejected.
- **Runtime**: Python 3.11.x, kokoro/misaki `0.9.4`, torch `2.15.0`,
  torchaudio `2.11.1`, CPU, 1–64 threads and
  `deterministic_algorithms=true`; any other value is rejected.
- **References**: unique preset-voice slug IDs, canonical absolute paths,
  64-hex digests, consent/rights/speaker slugs and a language tag.
- **Texts**: unique IDs, non-empty text ≤4,096 characters, language tag,
  speaker/consent/output-use slugs, and a reference ID whose digest must match
  the declared preset voice.
- **Controls**: exactly one each of `fixed_voice`, `alternate_voice` and
  `text_control`; the fixed and alternate voices must be declared and
  different, while the text control must not name a voice.
- **Outcomes**: WER 0–1, cosine −1–1, MOS 1–5, alignment 0–96,000 samples,
  nonnegative first-output/tail, peak 0–4, clipped fraction 0–1,
  `nonfinite_count=0` and a positive sample count. These are admission bounds,
  not measured results.
- **Rights**: non-empty consent reference, voice availability, output use,
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
| `source:…/results/kokoro/metrics.json` | `e96da8bd…` | Historical timing/RTF |
| `source:…/results/kokoro/asr.json` | `8be4df45…` | Historical one-text ASR proxy |
| `source:…/scripts/run_kokoro_tts.py` | `c4b6ba54…` | Exact historical invocation |
| `source:…/repos/kokoro/LICENSE` | `c71d239d…` | Apache-2.0 code license, not weight terms |
| `source:…/repos/kokoro/pyproject.toml` | `f8c3ae1c…` | Declared version and dependencies |
| `source:…/repos/kokoro/README.md` | `b50b8422…` | Declared model and voice usage |
| `source:…/repos/kokoro/kokoro/model.py` | `301c5535…` | Exact weight/config load path |
| `source:…/repos/kokoro/kokoro/pipeline.py` | `499982bb…` | Exact preset voice load path |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945…` | `kokoro-82m` row, Voice profile |
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
| `LICENSES.md` | Upstream/license/weight/voice-asset boundary; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, source tree, absence/projection checks, manifest admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, source tree, report bytes/digest, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/kokoro-82m` with Python 3.12 and stdlib only:

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

Current counts: 27 workspace/worktree absence probes plus 2 home-cache probes
(0 present), 6 required artifacts (1 source present, 5 blocked), 5 open
blockers, 158 rejected admission controls, 1 schema-only control, 8 blocked
Voice rows, 3 blocked quality outcomes, 3 blocked timing rows, 8 blocked gates,
0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision, archive and license provenance | blocked | Immutable source archive matching the pinned revision, tree digest and file count, with the complete license/notice set, supplied and reviewed. |
| `RG-02` weights, voice assets and terms | blocked | Immutable weight/config/voice snapshot with per-file digests and reviewed weight/model-card and voice-style terms. |
| `RG-03` pinned runtime and offline load | blocked | Locked CPython 3.11.x runtime loads the pinned snapshot offline with deterministic settings. |
| `RG-04` voice availability and output use | blocked | Preset-voice asset availability and output-use terms staged for every voice, including `af_heart`. |
| `RG-05` rights-cleared text and voice cohort | blocked | Immutable cohort, manual transcripts, groups, target conditions and matched controls. |
| `RG-06` separate content, identity, naturalness and listening | blocked | Pinned scorers and an approved blinded listening protocol produce reviewed results. |
| `RG-07` alignment, first-output/tail, peaks and resources | blocked | Target-device paced runs record alignment, timing, peaks, nonfinite behavior, CPU, memory and deadlines. |
| `RG-08` provider intake, public surface and release | blocked | Separate versioned intake with OFF default, public-surface decision and independent exact-head review. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

`survey-trn-05` is a merged taxonomy map for reference-conditioned voice
cloning/TTS; it records the same historical Kokoro row as adjacent research
context, but this package does not reuse its numbers, status or conclusions.
`survey-trn-04` covers speech-to-speech voice conversion, a different task.
Chatterbox Nano, Chatterbox VC, CosyVoice 2, F5-TTS, NeuTTS, StyleTTS 2 and
YourTTS results are boundaries only; none is pooled or reinterpreted as Kokoro
82M evidence. Kokoro is a fixed-voice TTS model, not a zero-shot voice-cloning
model, and this package does not substitute one role for the other.

## Expected digest

`report.json` SHA-256:
`ee057a4ac944dd6af9f1c8845abbcc056fb9c81076ae17bfa78ab3092c6bd06c`.

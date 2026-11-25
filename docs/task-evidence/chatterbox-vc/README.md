<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-CHATTERBOX-VC — Chatterbox VC readiness blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Chatterbox VC` (`component_id=chatterbox-vc`). The structured inventory assigns
the **Voice** acceptance profile (`verification_profile: voice`,
`plan/INVENTORY.json`), defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER** before any implementation or intake step; `status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. Missing evidence
never qualifies a candidate.

This package does **not** contain, import, build, link, download, load or
execute Chatterbox, an S3Gen weight, `conds.pt`, `chatterbox-tts`, PyTorch, a
reference voice or an inference path. It decodes, plays and analyzes no audio,
converts no voice and measures no content, identity, similarity, naturalness,
alignment, first-output/tail, peak, device timing, resource, benchmark or
release result. Only whole-file SHA-256 and byte-count provenance checks are
performed on the three historical media paths, and none is loaded as a signal.
It records the exact missing artifacts and rights, probes a fixed list of
workspace and home-cache paths to evidence their absence, records the one
historical run as provenance only, and defines a fail-closed admission boundary
for the Voice conversion cohort a future qualified run would need. Only
`docs/task-evidence/chatterbox-vc/` is written; no provider, registry,
descriptor, public header/ABI, shared CMake, CI workflow or installed-v0
behavior changes.

## Exact external blocker

The LAION `chatterbox-voice-conversion` wrapper checkout is present at the
pinned revision `9043873c7501033991e9907af7ddf8c394d74522` with an Apache-2.0
`LICENSE`. The wrapper is a thin interface over the separately distributed
ResembleAI Chatterbox S3Gen model. The S3Gen weights and the exact runtime are
**absent**. A wrapper code license is not a weight, model-card, source-speaker,
target-voice, consent or output-use grant. The local Hugging Face cache has
directories only for `FunAudioLLM/CosyVoice2-0.5B` and
`ResembleAI/chatterbox-nano`; it has no `ResembleAI/chatterbox` directory, no
`s3gen.safetensors` and no VC `conds.pt`. No download, reconstruction or
substitute was attempted. Because the weights and runtime are absent, this
package implements no model surrogate or partial inference path; the smallest
verifiable reference is the exact source provenance plus the fail-closed
admission schema below.

Five exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The immutable `ResembleAI/chatterbox` S3Gen snapshot: `s3gen.safetensors`, `conds.pt`, any snapshot-declared tokenizer/config asset, a 40-hex snapshot revision, per-file byte counts and SHA-256. |
| `BLK-02` | A reproducible isolated runtime matching the historical environment (Python 3.11, torch 2.6.0, torchaudio 2.6.0, `chatterbox-tts` 0.1.3, transformers 4.51.3, librosa 0.11.0, soundfile 0.14.0, numpy 1.26.4, safetensors 0.5.3), with a lock/install digest and a fail-closed offline load path; the historical `.venv-chatterbox` is absent. |
| `BLK-03` | Reviewed weight/model-card terms plus explicit source-speaker consent, target-voice consent, reference-availability and output-use terms. The wrapper Apache-2.0 license covers none of these, and the historical p360 target provenance is explicitly unconfirmed. |
| `BLK-04` | A rights-cleared, consented frozen speech-to-speech cohort with manual transcripts, language/speaker groups, exact target conditions and matched-target, mismatched-target and identity-passthrough controls. |
| `BLK-05` | An agreed Voice protocol that separately measures content preservation, identity/similarity, naturalness, alignment, first-output/tail, nonfinite/peak behavior, independent listening, device timing, resources and uncertainty. |

**Reopen condition.** A caller supplies the immutable S3Gen weight snapshot with
every digest, the reviewed weight/model-card and notice bundle, a locked runtime
that loads the snapshot offline, explicit source-speaker consent, target-voice
consent, reference-availability and output-use records for every voice, a frozen
rights-cleared cohort with manual transcripts and matched controls, and the
independent quality/listening/timing protocol with agreed margins. The pinned
runtime reproduces approved reference outputs, and a separate versioned intake
records opt-in registration with an OFF default and independent exact-head
review. Until then this task stays `DEFER`.

## Historical execution: provenance only

The research record contains one successful offline whole-file conversion on a
single source/target pair. It is transcribed here with its original scope and is
**not rerun, not merged task evidence, not used for evidence and not a
qualification**.

| Field | Recorded value |
| --- | --- |
| Candidate | LAION `chatterbox-voice-conversion` 0.1.0 over ResembleAI Chatterbox S3Gen |
| Mode | Whole-file speech-to-speech voice conversion; CPU; 4 Torch threads |
| Output | `source_to_p360.wav`, 24 kHz, 9.68 s, 464,684 bytes, SHA-256 `946f3e02ba25df3511f6ca548121b9304196dcffd39a63b52dd7a1c6e7aa262c` |
| Source | `source_ljspeech_lj001-0001.wav`, 16 kHz, 9.655 s, SHA-256 `adc9736d0a02b8efe57128b2c6843605e81ab24027f23f6fc7d05bcd6107753b` |
| Target | `target_rtvc_p360.flac`, 16 kHz, 3.562 s, SHA-256 `fcfffdbf9b96bdc720f924de1877f515766e438242afe2306f4a919ba6809b44`; provenance unconfirmed |
| Initialization | `129.61915799998678` s |
| Conversion | `25.46761295798933` s; file RTF `2.6309517518584022` |
| Peak / clipping | `0.735504150390625` / `0.0` |
| ASR proxy | Whisper Tiny English WER `0.0` on the one source utterance |
| First-audio latency | absent; the API returns one whole file |
| Identity/similarity | not measured |
| Naturalness / listening | not measured |
| Manual transcript | absent |
| Device timing | absent |
| Multi-utterance / speaker breadth | absent |

The historical output is listed only to preserve provenance. It is not decoded,
played, scored, pooled or promoted; only a whole-file SHA-256 and byte-count
provenance check is recorded. A 0.00 WER proxy is not a content, semantic,
identity or naturalness certificate, and 2.63× file RTF is not a call-device
latency.

## What this package actually verifies

1. **Source presence and exact pins.** The LAION wrapper revision, Apache-2.0
   `LICENSE`, project metadata, README, `convert.py` and `__init__.py` are
   pinned by SHA-256. This is a source-code provenance fact, not a weight or
   runtime qualification.
2. **Absence evidence.** Twenty-two fixed workspace/worktree probes and four
   fixed home-cache probes are checked (no recursive workspace walk). All are
   absent. `reference.build_report()` and `verify.py` raise or fail if any
   probe later appears, so a stale “absent” claim cannot be shipped. The
   remaining cache entries are recorded separately as provenance only
   (`admitted=false`, `used_for_evidence=false`).
3. **Admission boundary.** A caller Voice conversion cohort manifest has a
   strict, task-local schema. Every malformed, missing, invalid, nonfinite,
   aliased, duplicated, out-of-range or non-integral control is rejected before
   any state change. One structural control is admitted to prove the validator
   is not blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights or invokes a model.
4. **Voice profile accounting.** Permitted inputs/targets, language/speaker
   groups, content preservation, identity/similarity, naturalness, alignment,
   first-output/tail, exact target condition and independent consent/reference/
   output-use gates are each recorded as **blocked**.
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
| Freeze permitted input and target references, task and language/speaker groups | blocked | No rights-cleared source utterance, target voice, consent record, language/speaker group or frozen target condition. |
| Preserve text and semantic content | blocked | No manual transcript, semantic-content adjudication or reproduced content metric; the historical WER proxy is not a certificate. |
| Identity/similarity as a separate outcome | blocked | No target-voice similarity score, independent encoder or human identity rating. |
| Naturalness as a separate outcome | blocked | No naturalness rating, blinded listening or preference panel. |
| Record alignment | blocked | No word/phoneme, onset or source-content alignment. |
| Record first-output/tail timing | blocked | The historical API returns one whole file; no chunks, first-output or tail. |
| Record the exact target condition | blocked | One RT-VC demo p360 target with unconfirmed provenance and no consent, target-voice specification or reference policy. |
| Consent, reference availability and output use as independent gates | blocked | No source-speaker consent, target-voice consent, availability or output-use record; the wrapper Apache-2.0 license clears none. |

## Admission contract (task-local; not an SDK, Chatterbox or Voice contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `converter`, `weights`,
  `runtime`, `source_audio`, `targets`, `controls`, `outcomes`, `rights`.
  Unknown and missing fields are rejected.
- **Converter**: exact 40-hex revision `9043873c…`, canonical absolute source
  and license paths, `license_id="Apache-2.0"` and a 64-hex license digest. The
  manifest records provenance; it does not grant weight rights.
- **Weights**: non-empty unique names matching `[a-z0-9][a-z0-9._-]{0,127}`,
  each with a 64-hex SHA-256, byte count 1–4 GiB and 64-hex terms digest.
  `s3gen.safetensors` and `conds.pt` are mandatory.
- **Runtime**: Python 3.10–3.13, torch/torchaudio `2.6.0`, `chatterbox-tts`
  `0.1.3`, transformers `4.51.3`, librosa `0.11.0`, soundfile `0.14.0`,
  numpy `1.26.4`, safetensors `0.5.3`, CPU, 1–64 threads and
  `deterministic_algorithms=true`; any other value is rejected.
- **Source audio**: unique slug IDs, canonical absolute paths, 64-hex digests,
  language tags, speaker slugs, a non-empty transcript and
  `transcript_source="manual"`.
- **Targets**: unique slug IDs, canonical absolute paths, 64-hex digests,
  consent/rights/speaker slugs and a language tag.
- **Controls**: exactly one each of `matched_target`, `mismatched_target` and
  `identity_passthrough`; the matched and mismatched targets must both name a
  declared target and must differ, while identity passthrough names none.
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
| `source:research/voice-conversion-eval-20261101/README.md` | `b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074` | Historical VC run and candidate ledger |
| `source:…/agent-chatterbox-breadth/REPORT.md` | `0ff66ba53399c495106c21c43072ff17292c9ac0be00a04fde06c312bcd73ce8` | Exact weights/runtime absence and p360 gap |
| `source:…/agent-matrix-crosswalk/REPORT.md` | `b7db9a73b45b3a8918e99453e0de00c9f8f2f64604acee56c3838d3a10e2f9b6` | Crosswalk disposition context |
| `source:…/scripts/run_chatterbox_eval.py` | `ddfd9e11ff2b300c20359d7ee946465d786e8277cd915866ea60874e821e4b67` | Exact historical invocation |
| `source:…/results/chatterbox/metrics.json` | `8c1ffe0fafc395d79d2f48c6e860c8bd4d30a385c2d2a49901c43da05ecf5627` | Historical timing/RTF |
| `source:…/results/chatterbox/asr.json` | `38981c46e7f15f4da144595979ee5e7c9451a3c5a8b4264a31c0114da9d17872` | Historical one-utterance ASR proxy |
| `source:…/repos/chatterbox-vc/LICENSE` | `1fa474d00e581cc0b506c9d87f4e7d480a5d7944df584e654661ad84e8d4b88a` | Apache-2.0 wrapper license, not weight terms |
| `source:…/repos/chatterbox-vc/pyproject.toml` | `424040c5c2fe435190b803df44899476ed1b191b30e2fa870734155d3e984288` | Declared runtime and version |
| `source:…/repos/chatterbox-vc/README.md` | `96b789a0e7647e1b38db97d7dfa018d6cb71e81c266d73fd34bbb238671e4219` | Wrapper scope (offline whole-file) |
| `source:…/chatterbox_vc/convert.py` | `9c1f6f60cef1b3aea0161907b061cdb6a8f3bbde8c7ce9cb171d6fdd51e5c99f` | Exact weight names and load path |
| `source:…/chatterbox_vc/__init__.py` | `b5e33a9801074d048641f42e8b3b5a267e48f9e6afc606d5187e16cd492697aa` | Public converter entry |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `chatterbox-vc` row, Voice profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Voice profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/survey-trn-04/README.md` | `e0b4ea4d92b122e9820b9857da5e4813db29b048468f2b0383e67ef4264eccae` | Merged VC survey, boundary only |
| `docs/task-evidence/survey-trn-04/report.json` | `fb34a1129db91808c450cf9ce90d68a2f2ff34734b26891763ede6b0915f0446` | Merged VC survey, not reused |
| `docs/task-evidence/survey-trn-05/README.md` | `81b51f5696142a7fb77dd285e1db866f550de0faf5e5160ed66d15499b64c26b` | Merged TTS/cloning survey, not reused |
| `docs/task-evidence/survey-trn-05/report.json` | `fd281bbacb62298102af00da3f304bd564a1f7f25b7be050e5c95ad4e4fc0773` | Merged TTS/cloning survey, not reused |

The shared board row is read only by `verify.py` and the unit tests, and only
through the stable projection `{id, title, component, mode, repository,
depends_on}`. `status`, `owner`, `claim`, `review`, `handoff`,
`blocked_reason` and `dispatch_priority` are excluded from gating, so a board
state transition cannot promote or block this package's claims. The full
mutable `TASKS.json` bytes are never hashed.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Wrapper/weight/reference-voice boundary; no vendored license text. |
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

From `docs/task-evidence/chatterbox-vc` with Python 3.12 and stdlib only:

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

Current counts: 22 workspace/worktree absence probes plus 4 home-cache probes
(0 present), 6 required artifacts (1 source present, 5 blocked), 5 open
blockers, 158 rejected admission controls, 1 schema-only control, 8 blocked
Voice rows, 3 blocked quality outcomes, 3 blocked timing rows, 8 blocked gates,
0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source, model revision, archive and license provenance | blocked | Both source archives, 40-hex revisions, tree digests and complete license/notice sets supplied and reviewed. |
| `RG-02` weights assets and terms | blocked | Immutable S3Gen/conds snapshot with per-file digests and reviewed weight/model-card terms. |
| `RG-03` pinned runtime and offline load | blocked | Locked runtime with install digest loads the pinned snapshot offline with deterministic settings. |
| `RG-04` consent, reference availability and output use | blocked | Signed source-speaker consent, target-voice consent, availability and output-use terms for every voice. |
| `RG-05` rights-cleared voice cohort | blocked | Immutable cohort, manual transcripts, groups, target conditions and matched controls. |
| `RG-06` separate content, identity, naturalness and listening | blocked | Pinned scorers and an approved blinded listening protocol produce reviewed results. |
| `RG-07` alignment, first-output/tail, peaks and resources | blocked | Target-device paced runs record alignment, timing, peaks, nonfinite behavior, CPU, memory and deadlines. |
| `RG-08` provider intake, public surface and release | blocked | Separate versioned intake with OFF default, public-surface decision and independent exact-head review. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

`survey-trn-04` is a merged taxonomy map for speech-to-speech voice conversion;
`survey-trn-05` covers reference-conditioned voice cloning/TTS. This package
does not reuse either package's numbers, status or conclusions. The merged
Chatterbox Nano package (`docs/task-evidence/chatterbox-nano/`) is a different
model: its TTS weights, tokenizer assets and `conds.pt` are not Chatterbox VC
weights and are never substituted here. MeanVC2, Seed-VC, LLVC, RVC, OpenVoice,
CosyVoice 2, Kokoro and other voice results are boundaries only; none is pooled
or reinterpreted as Chatterbox VC evidence.

## Expected digest

`report.json` SHA-256:
`321fe22b052823b43d772871b5b694df03c0586c6754c04491d40406055b3dee`.

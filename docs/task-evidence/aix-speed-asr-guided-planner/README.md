<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-AIX-SPEED-ASR-GUIDED-PLANNER — AIx Speed rate-planner blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
the **AIx Speed ASR-guided planner** (`component_id=aix-speed-asr-guided-planner`).
The structured inventory assigns the **Rate** acceptance profile
(`verification_profile: rate`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Machine-readable decision: **`DEFER`**;
`status=proposal_only_incomplete_not_qualified`; `completeness=incomplete`;
`qualification.status=not_qualified`; `qualifies=false`. No result qualifies.

This package does **not** import, load, link, execute, copy, vendor or download
the AIx Speed research method, a jointly trained speed/ASR model, Wav2Vec2
weights, an ASR runtime, a held-out transcript cohort, a listening panel or a
corpus. It does not process or play audio, run an ASR proxy, listen, measure a
device, time a callback, run a benchmark or make a release claim. It pins the
research and pre-screen provenance that is present, proves that the exact
source, weights, runtime, rights, held-out transcripts, ASR proxy and listening
evidence are absent, reproduces only a deterministic rate-envelope arithmetic
control, and records the exact deferral condition. Only
`docs/task-evidence/aix-speed-asr-guided-planner/` is written; no provider,
descriptor, registry, default, installed-v0, ABI, shared-build, CI, board or
handoff file changes.

## Exact blocker

The pinned note records AIx Speed only as a paper-level candidate:

> **AIx Speed (AHs '23 / arXiv 2403.02938)** chooses playback speed per
> phoneme, using an ASR model's recognition score as a proxy for human
> intelligibility, and reports ~1.3× average with lower CER/WER than
> constant-speed playback. It is a stronger but heavier design (Wav2Vec2-based,
> joint speed/ASR training); **no public implementation was found**.

The note also says: "Do **not** start with … AIx Speed (no code, heavy)." The
paper is provenance, not source code, weights or a runtime. No author
implementation, revision, checkpoint, model card, licence, dependency lock,
held-out transcript cohort, ASR-proxy scorer, listening protocol or reference
output is present. None is fabricated here.

| Required artifact | Recorded local state |
| --- | --- |
| Exact AIx Speed source or authorized implementation | No `data/checkouts/aix-speed*` or `data/sources/aix-speed*`; no 40-hex revision or full SHA-256 |
| Jointly trained speed/ASR weights | No `data/models/aix-speed*`; no checkpoint, Wav2Vec2 derivative or model card |
| Pinned ASR runtime environment | No `data/envs/aix-speed*`; no framework, tokenizer, frontend or accelerator lock |
| Licence and output rights | No `data/licenses/aix-speed*`; no code/weight terms or signed output-use decision |
| Rights-cleared held-out transcript cohort | No `data/reference/aix-speed*`; no consent, human-verified phoneme timestamps or manifest |
| Independent ASR proxy scorer | No pinned scorer, reference transcript, aggregation or calibration |
| Listening protocol and panel | No protocol, anchors, authorization or result |
| Adapter intake and release review | No adapter, registration, default, measured rate evidence or release decision |

A model load, ASR decode, planner run, listening session and timing run were
**not** attempted. Path absence is not a runtime, reproducibility or ABI
result. Every release gate remains `blocked`.

## Scope and invariants

- Work is confined to `docs/task-evidence/aix-speed-asr-guided-planner/`.
  Shared CMake, contracts, public headers, descriptor registry, defaults,
  installed v0 behavior and other tasks are untouched.
- Installed v0 stays 16 kHz / mono / float32 / 160-sample frames. No provider is
  registered, exposed or default-enabled. No adapter code, readiness file or
  registry entry is added.
- The reference is deterministic, model-free and standard-library only. It is
  default OFF, unregistered and not a provider.
- No real speech corpus, held-out transcript, listening panel, model weights,
  ASR runtime, network download, target-device timing, WER/CER on candidate
  output or release qualification is used. Every control is integer or exact
  rational arithmetic.
- Missing, invalid, nonfinite, out-of-range, guarded, gap, overlap,
  candidate-claim and missing-artifact cases fail closed. No missing result may
  qualify the candidate.
- The `ASR proxy` result and the `listening` result are separate evidence
  classes. Both are `blocked`; neither is relabelled, pooled or promoted.
- Source-reported claims, the declared boundary and local synthetic controls
  are reported separately and are never pooled.

## Candidate and declared boundary (proposal only)

`report.json` → `candidate_record` and `declared_contract` record only what the
pinned note states or what the local control declares.

| Field | Declared value | Status |
| --- | --- | --- |
| Candidate | AIx Speed (AHs '23 / arXiv 2403.02938) | Source-reported |
| Method | Per-phoneme speed from an ASR recognition score as an intelligibility proxy | Source-reported |
| Backbone | Wav2Vec2-based joint speed/ASR training | Source-reported |
| Claimed outcome | ~1.3× average, lower CER/WER than constant speed | Source-reported, **not reproduced** |
| Public implementation | Not found | Blocked |
| Host grid | 16 kHz, mono, float32, 160 samples | Installed v0, unchanged |
| Declared first-product rate range | `3/4` to `3/2` | Declared policy, not measured |
| Protected speech ceiling | `1` | Declared policy, not measured |
| Design lookahead | 200–1000 ms | Design guidance, not measured |
| Duration target | `sum(d_i / r_i) == sum(d_i)` | Declared identity |
| Per-phoneme alignment, rate application, lookahead, buffering, reset, drain, content delay, final window | Not established | Blocked |

The rate range, speech ceiling and lookahead are design values from the pinned
note. They are **not** AIx Speed behaviour, runtime geometry or measurements.

## Synthetic rate-envelope arithmetic control

`reference.py` validates a strict content-aware envelope: exact rational rates,
contiguous source coverage, exact 1 ms-free sample mapping, the declared
`3/4..3/2` clamp, `speech <= 1`, `silence/filler >= 1`, and an explicit
non-candidate flag. The fixture is 16,000 samples (1 s at 16 kHz), not speech,
not a corpus and not audio.

| Segment | Source samples | Class | Rate | Output samples |
| --- | ---: | --- | ---: | ---: |
| `seg-00-silence` | 0–2400 | silence | `3/2` | 0–1600 |
| `seg-01-filler` | 2400–3600 | filler | `6/5` | 1600–2600 |
| `seg-02-speech` | 3600–7600 | speech | `4/5` | 2600–7600 |
| `seg-03-speech` | 7600–16000 | speech | `1/1` | 7600–16000 |

Exact invariants: total input = total output = 16,000 samples; average rate
`1`; duration delta `0` samples / `0.0` ms; minimum rate `4/5`; maximum rate
`3/2`; every output boundary is an integer; source coverage is contiguous and
ends exactly at the fixture boundary; the identity control is an exact `1×`
passthrough. The control is labelled `is_synthetic_control=true`,
`is_aix_speed=false` and `is_candidate_result=false`.

This is **not** an AIx Speed output, an ASR decode, a rate-envelope result on
held-out speech or a listening result. It only exercises the arithmetic that a
future qualified planner must satisfy.

## ASR proxy and listening are separate

| Evidence class | Status | Value |
| --- | --- | --- |
| ASR proxy (WER/CER delta) | `blocked` | `scorer_id=null`, `wer_delta_pp=null`, `cer_delta_pp=null` |
| Listening / comprehension | `blocked` | `protocol_id=null`, `comprehension=null`, `preference=null`, `mos=null` |
| Separation | Enforced | `asr_proxy_is_listening=false`, `pooled_metric=null` |

The qualification manifest rejects a document whose `listening_protocol_id`
equals its `asr_proxy_scorer_id`, and rejects `not_established` as a listening
protocol. An ASR proxy is never counted as comprehension or preference.

## Caller-supplied qualification manifest (shape and hash only)

`reference.parse_manifest()` validates a strict 21-field bundle for a
caller-owned qualified artifact: exact key set, candidate and family IDs,
identifier grammar, 40-hex source revision, full SHA-256 for source, weights,
runtime, licence, approval and transcript manifest, absolute POSIX paths without
traversal or duplication, accepted terms, a fixed caller attestation, and an
explicit ASR-proxy/listening separation. `reference.verify_manifest_files()`
hashes the caller-owned bytes only. It **never parses, imports, links or
executes** the source, weights, runtime or transcript. Even a fully
hash-matched caller bundle reports `official_identity=false` until author and
rightsholder review exists.

`report.json` → `manifest_controls` records one accepted shape-only control and
seventeen explicit rejections. All controls have `qualifies=false`.

## Failure controls (exact failures recorded as failures)

- **Envelope:** 24 adverse vectors are rejected: NaN/infinity/boolean/string
  rates, zero denominator, negative numerator, rate below floor and above
  ceiling, speech speed-up, silence slow-down, interval gap, overlap, empty
  interval, uncovered tail, duplicate ID, nonfinite/boolean/out-of-range ASR
  score, candidate claim, non-object segment, empty envelope, mapping container,
  extra field and unsupported content class. Every rejection records the
  expected error and `qualifies=false`.
- **Manifest:** 17 adverse documents are rejected: missing and extra fields,
  wrong candidate and family, relative path, parent traversal, 39-hex revision,
  uppercase hash, 63-character hash, duplicate paths, rejected terms, wrong
  attestation, empty cohort ID, missing ASR scorer, ASR/listening identity,
  `not_established` listening protocol and empty artifact ID. Missing files and
  mismatched bytes are rejected by the file checker.
- **Qualification:** all 13 missing-result rows are `blocked` with
  `value=null`; all 9 qualification slots are null; all eight gates are
  `blocked`.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json` → `acceptance_profile`; every item is `qualifies=false`.

| Required item | Status here | Evidence |
| --- | --- | --- |
| Source/output mapping | synthetic_control_only | Exact rational sample mapping on the fixture |
| Duration | synthetic_control_only | Exact `sum(d/r) == sum(d)`, delta `0` |
| Unity 1× | synthetic_control_only | Exact identity envelope |
| Silence / filler policy | synthetic_control_only | Declared-only 3/2 and 6/5 on the fixture |
| Source-timestamp-tied decisions | synthetic_control_only | Every control segment is a source interval |
| Final partial window | synthetic_control_only | Coverage ends exactly at the fixture boundary |
| Pitch | blocked | No actuator, audio path or pitch measurement |
| Transient audibility | blocked | No actuator or listening asset |
| Playback buffering / rebuffer | blocked | No playout FIFO, lookahead run or injection |
| Rate changes (step/ramp) | blocked | No runtime or rate-change trace |
| Unfamiliar speech / music | blocked | No real speech, music or held-out corpus |
| Drift over a long run | blocked | No actuator or long-run measurement |
| Speech preservation | blocked | No candidate output or preservation metric |
| ASR proxy separate from listening | blocked | Both classes blocked and separately reported |
| Listening / comprehension | blocked | No protocol, panel or authorization |
| Adverse / missing / nonfinite | synthetic_control_only | 24 envelope and 17 manifest rejections |
| Release and distribution terms | blocked | No code, weight or output-use approval |

## Eight blocked release gates

1. `exact_aix_speed_source_and_weights_identity`
2. `license_and_output_rights`
3. `pinned_asr_runtime_and_environment`
4. `declared_planner_geometry_lookahead_and_content_delay`
5. `rights_cleared_heldout_transcript_cohort`
6. `separate_asr_proxy_and_listening_quality`
7. `measured_rate_duration_pitch_transient_and_device_timing`
8. `opt_in_adapter_intake_and_release_review`

Each gate is `blocked` with `evidence=null` and `qualifies=false` in
`contract.json` and `report.json`.

## Exact missing artifacts and rights

| Missing artifact | Rights requirement |
| --- | --- |
| Exact AIx Speed source or authorized implementation | Repository/paper code licence, reproduction grant and output-use decision |
| Jointly trained speed/ASR weights (Wav2Vec2 derivative) | Weight-specific execution, commercial-use, redistribution and output-use terms |
| Pinned ASR runtime and dependency lock | Runtime/dependency licences and exact-version approval |
| Reviewed licence text and rights decision | Author and rightsholder terms for code, weights and outputs |
| Rights-cleared held-out transcript cohort | Corpus, participant, annotation, redistribution and evaluation rights |
| Independent ASR proxy scorer | Scorer, model and reference-transcript terms at exact revisions |
| Blind listening protocol and panel | Panel consent, participant-data terms and publication approval |
| OFF-by-default adapter intake and release review | Reviewer, timing-harness and release-authority approval |

No download, fabrication or substitution was attempted. A paper DOI/arXiv
locator is not source code, a weight identity or a runtime.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, controls, gates. |
| `reference.py` | Deterministic rational envelope control, strict manifest parser, adverse controls, declared boundary and report/contract builders. |
| `run.py` | Regenerates the report three times, the contract and the manifest. |
| `report.json` | Canonical machine-readable rate report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, qualification. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only pin, strict-JSON, digest, README-table, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for every local artifact and this README. |
| `*.license` | REUSE sidecars for JSON and digest artifacts. |

## Source pins (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.
Every row is machine-checked by `verify.py` and the test suite. Only provenance
files that exist are pinned; no absent candidate artifact is given a fabricated
hash. The mutable full `plan/swarm/TASKS.json` is not pinned or hashed.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:cpp-library/pipeline-validation/playback-speed/README.md` | `a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f` |
| `source:cpp-library/pipeline-validation/playback-speed/results/report.md` | `9c9383297b1160dbe4f7261f789b493d70354b11930f4d8527b20b0ca8c87c34` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`boundary:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `boundary:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `boundary:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `boundary:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `boundary:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `boundary:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `boundary:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Merged sibling evidence pins (SHA-256)

The sibling packages are separate evidence. They are pinned as prior local
artifacts, not imported, pooled or reinterpreted. The Vosk and VM-ASR packages
are ASR-adjacent blockers; D1, FFmpeg `atempo` and Signalsmith Stretch are
rate/actuator evidence. None is AIx Speed.

<!-- digest-table: sibling -->
| Key | SHA-256 |
| --- | --- |
| `sibling:docs/task-evidence/vosk-small-en-us-0-15-playback-gate/contract.json` | `ee23e6cc21f9f3293a48dab7008a4c41f129074cafa3eb6b273f2f3ef413d694` |
| `sibling:docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json` | `57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2` |
| `sibling:docs/task-evidence/d1-whole-clip-duration-planner/reference.py` | `ffb59e3d09d7cef0580d73cf9772d6e69d0ddfb991457e7878ac4bf86cf7c253` |
| `sibling:docs/task-evidence/d1-whole-clip-duration-planner/fixtures/report.json` | `522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98` |
| `sibling:docs/task-evidence/additional-vm-asr-audio-super-resolution/contract.json` | `c59d99d0bb9280bb73bdf8608d8021cc338556609748db597b385c5d12d91301` |
| `sibling:docs/task-evidence/additional-vm-asr-audio-super-resolution/report.json` | `3fa34b0e49d992f7e6261970b648aaa095a88bc07877372ba4df4422c5023b12` |
| `sibling:docs/task-evidence/ffmpeg-atempo/contract.json` | `0f3ca86b4658d6656b0528bbcc1e1aa822928dbd72a48a66f16ad4f981b10fac` |
| `sibling:docs/task-evidence/ffmpeg-atempo/report.json` | `a3986e6cb9d7315995aa13c74806c260c620d01b6f545e0837b127565c2ba249` |
| `sibling:docs/task-evidence/signalsmith-stretch/contract.json` | `cec65c71a339e76bb668cb9d895285b7b152229d6a9af20c2401b69c7785ff9e` |
| `sibling:docs/task-evidence/signalsmith-stretch/report.json` | `e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231` |
<!-- digest-table: end -->

## Artifact digests (SHA-256)

`report.json` is canonical JSON (sorted keys, indent 2, `allow_nan=False`, LF,
one trailing newline). The canonical digest of the committed bytes is stored in
[`report.json.sha256`](report.json.sha256). `SOURCES.sha256` pins every artifact
and this README; it does not pin itself. No external artifact is pinned: the
source, weights, runtime, licence, held-out cohort and reference output are not
established, and every required-artifact row records `present=false`.

## Reproduce

Run from this directory with a pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-AIX-SPEED-ASR-GUIDED-PLANNER
TASK=$WT/docs/task-evidence/aix-speed-asr-guided-planner
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py --report
PYTHONDONTWRITEBYTECODE=1 $PY run.py --contract
PYTHONDONTWRITEBYTECODE=1 $PY run.py --sources
PYTHONDONTWRITEBYTECODE=1 $PY run.py --inspect
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
git -C "$WT" diff --check
```

`run.py --report` builds the report three times in one process and refuses to
write unless all payloads are byte-identical. `verify.py` separately launches
three cold starts for each command and compares the exact bytes, and checks the
declared boundary, null candidate slots, ASR/listening separation, controls,
eight blocked gates, SPDX annotations, dependency hygiene and task-local scope
containment.

## Non-claims and boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`asset_bundled=false`, `weights_vendored=false`,
`model_runtime_invoked=false`, `asr_runtime_invoked=false`,
`native_engine_built=false`, `sdk_data_dir_added=false`.

Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row identity only (`tasks[id=SDK-AIX-SPEED-ASR-GUIDED-PLANNER]`,
stable-field projection); the mutable full `plan/swarm/TASKS.json` is never
hashed by or pinned to this package. No provider, descriptor, registry,
installed default, public ABI, shared build or CI is changed.

## Separation from sibling evidence

Vosk, VM-ASR, D1, FFmpeg `atempo` and Signalsmith Stretch packages are
**separate evidence**. They use different candidates, fixtures and
dispositions. This package does not pool, import, reuse or reinterpret their
outputs, metrics or adapters. The pinned playback-speed README is a local
pre-screen of D1/D2 with a Vosk gate, Whisper tiny.en proxy and
Bungee/Signalsmith/Sonic actuators; it is **not** AIx Speed and it has no
listening result. Its numbers are provenance only and are not remeasured here.

## Reopen condition

Supply (a) the exact AIx Speed source revision or an authorized implementation
with a 40-hex revision and full SHA-256; (b) the exact jointly trained
speed/ASR weights and backbone with full SHA-256; (c) a locked ASR runtime with
exact framework, tokenizer, frontend and accelerator versions; (d) reviewed
paper/code/weight terms and a signed output-use decision; (e) a rights-cleared
held-out transcript cohort with consent and human-verified word/phoneme
timestamps; (f) a pinned independent ASR proxy scorer and a separate authorized
blind listening/comprehension protocol; (g) measured duration, drift, pitch,
transient, buffering, final-window and target-device timing; and (h) independent
exact-head review and an OFF-by-default opt-in adapter intake. Until then the
candidate stays **DEFER**, **incomplete** and **not qualified**.

## License

All files here are first-party `Apache-2.0`, copyright 2026 Tsakanyan Hovhannes.
Python and Markdown files carry file-level SPDX tags; JSON and digest files are
covered by adjacent `.license` sidecars and the repository `REUSE.toml`
annotation for `docs/**`.

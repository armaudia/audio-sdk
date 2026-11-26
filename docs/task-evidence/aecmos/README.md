<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-AECMOS — DEFER blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`SDK-AECMOS` (`component_id=aecmos`). The structured inventory assigns the
**Evidence** acceptance profile (`verification_profile: evidence`,
`plan/INVENTORY.json`), defined in `plan/swarm/VERIFICATION.md`.
Machine-readable decision: **`DEFER`**; `status=proposal_only_not_qualified`;
`completeness=incomplete`; `qualification.status=not_qualified`;
`qualifies=false`. No result qualifies.

This package does **not** import, load, link, execute, copy or download
Microsoft AECMOS, its ONNX weights, the official AEC-Challenge inference source,
ONNX Runtime, librosa or numpy. It does not listen, measure a device, time a
callback, run a benchmark or make a release claim. It pins the research, adapter
and pilot provenance that is present, proves that the licensed weights, official
source, qualified runtime and rights-cleared cohort are absent, reproduces only
the documented **three-stream input/feature geometry**, and records the exact
deferral condition. Only `docs/task-evidence/aecmos/` is written; no provider,
descriptor, registry, default, installed-v0, ABI, shared-build, CI, board or
handoff file changes.

## Exact scope and boundary

- Installed v0 stays 16 kHz mono `float32`, 160 samples per frame. There is no C
  boundary, public header, provider registration, descriptor, default,
  `CMakeLists.txt`, CI or installed-behavior change.
- `reference.py` is a stdlib-only deterministic **input-contract** reference,
  not AECMOS. It validates the three streams and records the declared geometry
  requested by the pinned adapter: 513-point STFT, 256-sample hop, 160 mel
  bands, first 320,000 samples, 20-frame `st`/`nst`/`dt` marker, 20-frame zero
  terminator, zero `(4,1,64)` `h0` state and the `aecmos_echo` /
  `aecmos_degradation` output names.
- **No mel value, feature tensor, GRU state or model output is computed.** The
  report records `mel_implementation_reproduced=false`,
  `feature_values_reproduced=false` and `scores_reproduced=false`. Every score
  slot is `null` with `score_status=unavailable_weights_and_official_source_absent`.
- The fixture is synthetic: deterministic sines plus seeded integer noise. It is
  not speech, a room, a device or a corpus.
- Stream RMS/peak values are **geometry diagnostics only**. They are not
  AECMOS predictions, a MOS, a human rating, a quality score or a threshold.
- The mutable full `plan/swarm/TASKS.json` is never hashed. Only the stable
  linked-row projection (`id`, title, repository, mode, component, dependencies,
  evidence, base commit, branch) is compared.

## Exact external blocker: absent licensed weights, source and cohort

The research, wrapper and pilot reports are present and pinned, but none of the
artifacts needed to reproduce AECMOS are:

1. **No model weights.** The expected file
   `data/models/aecmos/Run_1663915512_Stage_0.onnx`
   (SHA-256 `f53122f43cb7e5b77ec797e85c8b997cfc2aac8220857c709226d876de8c0a99`)
   is absent. A filename scan finds no `Run_1663915512*` file and an ONNX hash
   scan finds no matching file; the digest appears only in text provenance.
   Nothing was downloaded, copied or substituted.
2. **No official AECMOS inference source.** No AEC-Challenge or AECMOS checkout
   is present. `adapters/aecmos/run.py` is a local wrapper, not the official
   implementation, and its feature values are not reproduced here.
3. **No qualified runtime.** The default interpreter cannot import
   `onnxruntime`, `librosa` or `numpy`. An incidental pipeline-validation
   virtualenv contains onnxruntime 1.31.1 / librosa 0.11.0 / numpy 2.4.6, but it
   is unpinned and not approved for this task. That environment was used only
   for a recorded frame-count crosscheck and is explicitly not qualification
   evidence.
4. **No rights-cleared cohort.** No paired lpb/microphone/enhanced audio with
   talk-type labels is present. The historical AEC-Challenge pilots are
   training-split subsets with unresolved source-component, participant and
   redistribution terms; they are not bundled, remapped or used as an oracle.
5. **No scores.** The repository MIT license is a **code** license; the AECMOS
   weight terms are not established here. No echo/degradation prediction,
   ranking, listening result or release claim exists.

**Reopen condition.** A caller supplies (a) the exact AECMOS v4 16 kHz ONNX
weights with SHA-256 `f53122f4…0a99` and their own license/redistribution terms
plus approval to execute; (b) the official AEC-Challenge AECMOS inference source
pinned to one revision and a pinned approved onnxruntime/librosa/numpy
environment; (c) a rights-cleared paired lpb/microphone/enhanced cohort with
talk-type labels, alignment and device metadata; (d) verified numerical parity
for the log-mel features, markers, `h0` state and both outputs; and (e) a frozen
paired aggregation with uncertainty, retained failed items, an
authorized listening/quality assessment where a rating is claimed, and
independent exact-head review through a separate OFF-by-default evidence-adapter
intake. Until then every release gate stays `blocked`.

## Reproduced input geometry (declared, not runtime-verified)

`report.json` → `input_contract` pins the contract; `adapter_contract_audit`
re-reads the pinned wrapper and confirms every token below is present.

| Field | Value |
| --- | --- |
| Sample rate / channels | 16,000 Hz / mono |
| Max input | 20 s = 320,000 samples (first samples kept) |
| STFT | `n_fft=513`, `hop_length=256`, center padding (default) |
| Real rFFT bins | 257 |
| Mel bands | 160, `power_to_db(..., ref=max)` then `(+40)/40` |
| Frame rule | `1 + (n - 1) // hop_length` |
| Stream order | `lpb`, `microphone`, `enhanced` |
| Marker / terminator | 20 frames / 20 zero frames, appended after normalization |
| State input | `h0`, shape `(4, 1, 64)`, zeros |
| Outputs | `aecmos_echo`, `aecmos_degradation` |

Marker values are the adapter's post-normalization constants:

| Talk type | `lpb` | `microphone` | `enhanced` |
| --- | ---: | ---: | ---: |
| `st` | 1.0 | 0.0 | 1.0 |
| `nst` | 0.0 | 1.0 | 1.0 |
| `dt` | 1.0 | 1.0 | 1.0 |

## Synthetic geometry runs (not scores, not evidence)

Frozen fixture: 19,200 samples / 1.2 s, 16 kHz mono. Frame geometry is identical
for all three talk types because only the marker values change:

| Field | Value |
| --- | ---: |
| Samples before marker | 75 frames |
| Marker frames | 75–94 (20) |
| Terminator frames | 95–114 (20) |
| Total feature frames | 115 |
| Feature shape | `[3, 115, 160]` |
| Echo/degradation scores | `null` / `null` |

The three valid runs (`st`, `nst`, `dt`) share one triplet digest and differ only
in their scenario marker. All controls are non-qualifying:

| Control | Status | Scores |
| --- | --- | --- |
| paired reference | `geometry_only_not_scored` | null |
| swapped streams | `stream_order_control_not_scored` | null |
| no reference | `no_reference_input_not_scored` | null |
| reference dropout | `partial_reference_not_scored` | null |
| delayed enhanced (128 samples) | `misaligned_enhanced_not_scored` | null |
| silence | `degenerate_silence_not_scored` | null |
| over 20 s | `truncation_policy_only` | null |

`ranking.order` is `not_ranked` and `recommendation` is `null`. Every adverse
and missing result is retained with `qualifies: false`; none is promoted.

## Evidence profile application

| Evidence requirement | Status here | Evidence |
| --- | --- | --- |
| Scorer pinned | blocked | No weights, revision or approved runtime. |
| Corpus pinned | blocked | No rights-cleared paired corpus. |
| Cohort pinned | blocked | No frozen triplet cohort with talk-type labels. |
| Aggregation pinned | proposal_only | Policy stated, not applied. |
| Failed items retained | synthetic_control_only | Adverse, rejected and missing rows kept. |
| Controls present | synthetic_control_only | Identity, swapped, no-reference, dropout, delayed, silence, truncation. |
| Paired vs unpaired separation | proposal_only | Only synthetic triplet geometry. |
| Synthetic vs human separation | proposal_only | Diagnostics never called ratings. |
| Invalid case validated | synthetic_control_only | Ten explicit rejections. |
| Valid case validated | synthetic_geometry_only | Declared geometry only. |
| Source-reported separation | proposal_only | Historical values quoted as statements. |

## Eight blocked release gates

1. Exact AECMOS v4 ONNX weights, their own license terms and approval to execute.
2. Official AEC-Challenge AECMOS source revision plus a pinned approved runtime.
3. Rights-cleared paired lpb/microphone/enhanced cohort with labels and metadata.
4. Numerical parity for log-mel features, markers, `h0` state and both outputs.
5. Reproduced paired echo and degradation scores on the exact runtime.
6. Frozen aggregation, uncertainty and retained failed items.
7. Human-versus-predicted labelling separation plus authorized listening.
8. Evidence-adapter intake, public-surface review and explicit release approval.

All eight are `blocked` with `evidence: null` and `qualifies: false`.

## Exact missing artifacts and rights

| Missing artifact | Rights requirement |
| --- | --- |
| AECMOS v4 16 kHz ONNX weights (`Run_1663915512_Stage_0.onnx`, SHA-256 `f53122f4…0a99`) | Model weight license, redistribution terms and written approval to execute; the repository MIT license is code-only. |
| Official AECMOS inference source at one revision | Upstream code license and redistribution terms for that revision. |
| Pinned approved onnxruntime/librosa/numpy environment | Runtime licenses and execution approval for the exact versions. |
| Rights-cleared paired lpb/microphone/enhanced cohort | Corpus, participant, device and redistribution rights. |
| Aggregation, listening and release review | Reviewer, panel (where applicable) and release approval. |

No download, fabrication or substitution was attempted.

## Source pins (SHA-256)

Paths are relative to the `audioml` workspace; boundary and sibling paths are
relative to this SDK worktree. `SOURCES.sha256` pins all 12 local artifacts and
excludes itself. The mutable board is **not** pinned; only the stable linked row
gates verification.

| Input group | Count | Use |
| --- | ---: | --- |
| Research, adapter, pilot script and summary provenance | 6 | Documented context and declared geometry |
| Plan profile documents | 2 | Task scope and acceptance profile |
| Public boundary (`CONTRACTS.md`, both v0 headers) | 3 | Unchanged public surface |
| Merged sibling AEC/quality evidence (`erle-and-double-talk-preservation`, `stoi-estoi`, `srmr-and-reverb-metrics`, `localvqe-compact-echo-only`, `webrtc-aec3`) | 10 | Prior task-local evidence, unchanged |

Key digests:

| Input | SHA-256 |
| --- | --- |
| `research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` |
| `adapters/aecmos/run.py` | `5add699066f267a68bc44bfb114d0e1f36cd22561a523cf5c87d73cec45e9e59` |
| `scripts/evaluate_aec_challenge_real_pilot.py` | `922cd0e155efc48d9042b23a863d59f0aba07fda825741567cbdd9b04c089a88` |
| `reports/aec_challenge_real_pilot_20261028.csv` | `32b41d1cab6b6b28a03cb6db164debfb408441822642c2a0c1a9b42b5889aba3` |
| `reports/aec_challenge_real_pilot_summary_20261028.csv` | `4784755161aa0fa4027b2b6524f8dd34b7ccc9390ecd785103dda95b65bb27e7` |

## Reproduction

Run from this directory on the pinned worktree:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 run.py --sources
python3 run.py --inspect
python3 verify.py
```

`run.py --report` builds the report three times and writes only byte-identical
output; `--sources` prints the exact local manifest; `--inspect` prints a
canonical input-contract summary. `verify.py` separately launches three cold
starts for each command and checks the exact external/boundary/sibling/local
pins, the stable linked row, canonical bytes, the input geometry and marker
contract, null score slots, eight blocked gates, adverse/missing/invalid/
nonfinite controls, SPDX annotations, dependency hygiene and task-local scope
containment. JSON is canonical (`sort_keys=True`, compact separators,
`allow_nan=False`) with one trailing newline.

Report digest: see [`report.json.sha256`](report.json.sha256), the canonical
SHA-256 of the byte-identical [`report.json`](report.json). No self-referential
digest is repeated in this README.

## Failure controls and non-claims

- No AECMOS algorithm, model, weight, official source, runtime or emulator is
  implemented, linked or executed.
- No real speech, corpus, weight, device timing, listening panel or release
  evidence is present.
- Rejections are explicit: invalid talk type, missing/empty/string stream,
  unequal lengths, bool sample, nonfinite sample, out-of-bounds sample, zero or
  bool sample count. No rejected value is repaired, scored or promoted.
- Missing, delayed, dropout, swapped, no-reference, silence and truncation
  results are retained with `qualifies: false`; none is promoted.
- Historical AECMOS and pilot values are source statements only, marked
  `reproduced_here: false` and `is_human_rating: false`; none is used as a
  threshold.

## License

All files here are first-party `Apache-2.0`, copyright 2026 Tsakanyan Hovhannes.
Python and Markdown files carry file-level SPDX tags; JSON and digest files are
covered by adjacent `.license` sidecars and the repository `REUSE.toml`
annotation for `docs/**`.

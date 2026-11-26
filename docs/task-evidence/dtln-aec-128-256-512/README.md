<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DTLN-AEC-128-256-512 — DTLN-AEC source, checkpoint and runtime blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DTLN-AEC 128/256/512` (`component_id=dtln-aec-128-256-512`). The acceptance
profile is **Room**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed DTLN-AEC source, the 128/256/512 two-stage TFLite
checkpoints, the TFLite runtime, the model content delay, the recurrent-state
shapes and an exact numeric output are **absent**. This package records that
blocker, applies the Room profile to a bounded deterministic synthetic paired
render/capture surrogate at the documented 512/128 geometry, and makes no echo,
quality, timing, listening, benchmark or release claim. It is **not DTLN-AEC**:
no recurrent state, mask network, TFLite graph, weight file, native library,
real audio, corpus, model, device clock or upstream DTLN-AEC code is present,
copied, downloaded, loaded, imported or executed. Only this task-local
directory is added.

## Exact blocker

The task row `plan/swarm/TASKS.json[id=SDK-DTLN-AEC-128-256-512]` is
`mode=feasibility`, `component=dtln-aec-128-256-512`, and the linked catalogued
record is `evidence_status=blocked`, `disposition=sdk-model`,
`verification_profile=room`, with the plan note "Obtain and pin the real
paired-reference checkpoints; mock coverage does not qualify it." Its only
evidence link is `adapters/dtln-aec/README.md`.

The pinned local adapter documents 16 kHz mono, a 512-sample analysis block with
128-sample hops, two `.tflite` stages per variant and upstream 128-, 256- and
512-unit models. It states explicitly that the model files are external assets
and are not included. The pinned research note adds: "The actual AEC checkpoint
and TFLite runtime remain unavailable locally" and "`data/checkouts/DTLN`
contains generic DTLN speech-enhancement weights, not the distinct
paired-reference DTLN-AEC weights." The pinned evaluation records add:
"DTLN-AEC does not have its proper checkpoint evaluated; generic DTLN
enhancement weights are not a valid substitute."

Consequently:

- no DTLN-AEC checkout, weight set, runtime environment or caller manifest is
  staged at `data/checkouts/DTLN-aec`, `data/models/dtln-aec`,
  `data/envs/dtln-aec` or `data/manifests/dtln-aec.json`;
- the present `data/checkouts/DTLN` TFLite files are generic DTLN enhancement
  weights, not DTLN-AEC, and are **not accepted** as a substitute;
- `tflite_runtime` and `tensorflow` are not importable in the pinned CPython
  3.12.16 evidence interpreter;
- no DTLN-AEC immutable revision, stage-1/stage-2 SHA-256, byte size, state
  shape, tensor order, model content delay or numeric output exists;
- no DTLN-AEC LICENSE, model card, weight terms, training-data statement,
  attribution bundle, corpus rights or product-use review is staged. The
  generic DTLN MIT license is not accepted as DTLN-AEC permission;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream; there is no
  accepted paired render/capture AEC provider geometry. The merged duplex
  evidence is a model-free proposal only;
- no real room, paired recording, consent, held-out split, AECMOS/STOI/ASR
  score or listening result exists;
- no target-device timing, independent review, provider intake or release
  approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-DTLN-AEC-128-256-512`, `7c6653f5a7db7f6de34ad709a96a455a9ad3263a` |
| Task mode | `feasibility` |
| Acceptance profile | `room` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate I/O geometry | documented 16 kHz mono, 512-sample block, 128-sample hop |
| Candidate model delay / state shapes | not documented, not measured |
| Surrogate | synthetic paired 16 kHz mono render/capture at 512/128, integer taps |
| Surrogate framing delay | 384 samples (block minus hop), compensated for scoring |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded 64-tap integer-fed NLMS echo canceller plus a
deterministic residual-energy gate run through a 512/128 overlap-add frame
clock. It is **not DTLN-AEC**, is not learned, uses no weights, TFLite graph or
recurrent state and cannot qualify the candidate.

## Room profile application

`plan/swarm/VERIFICATION.md` Room row is applied item by item in
`report.json` -> `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Render/reference freeze | synthetic only | Frozen 16 kHz mono 512/128 synthetic render and capture, fixed taps, declared 16-sample render delay, noise levels, one path switch and reset |
| Echo-only | synthetic only | Two far-end-only regions before and after one coefficient switch |
| Near-end-only | synthetic only | Two near-end regions with known clean near component and injected noise |
| Overlap | synthetic only | One synthetic render plus near-end region; one fixed SER, no device or listener |
| No-reference comparison | synthetic only | Independent gate-only control without AEC on the same synthetic mic |
| Echo attenuation | synthetic only | ERLE in integer millidB on echo-only regions |
| Near-end damage | synthetic only | Near-reference SNR, level change and peak on near-only regions |
| Nonfinite failures | synthetic only | Nonfinite input/output checks and peak bound; no runtime failure |
| Alignment, delayed/missing render | synthetic only | Declared 16-sample render delay; 256-sample shifted render and all-zero render probes; missing render hop rejected before processing |
| Movement/path change | synthetic only | One fixed synthetic coefficient switch at sample 6144 |
| Task-matched held-out qualification | blocked | No rights-cleared paired AEC cohort, held-out split, AECMOS/STOI/ASR or listening result |

Every echo, near-end, overlap and alignment row is `qualifies=false`. Synthetic
exactness means only that the fixture is self-consistent.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 512-sample block, 128-sample hop, 257
  magnitude bins, 62,500 ns per sample.
- Fixture length: 8,192 samples (0.512 s), five contiguous segments:
  `echo_only_initial` 0-2048, `near_only_clean` 2048-4096,
  `overlap_double_talk` 4096-6144, `echo_only_after_path_change` 6144-7168,
  `near_only_noisy` 7168-8192.
- Render: deterministic integer LCG excitation at amplitude 8000 in active
  segments; near-end: deterministic three-tone speech-like source with a fixed
  16-step syllable envelope; noise: deterministic LCG at amplitude 20, 80 or
  120 depending on the segment.
- Echo paths: seven fixed integer taps at offsets 0, 4, 8, 12, 16, 20 and 24
  from a declared 16-sample render delay. Coefficients switch exactly once at
  sample 6144. Convolution is exact integer arithmetic with a Q10 divisor.
- Surrogate: 64-tap NLMS, step `35/100`, per-sample update; residual energy gate
  with a 0.25 gain floor and deterministic noise-floor tracking; 512/128
  overlap-add emits the oldest hop, a 384-sample framing delay that is removed
  before scoring.
- Echo-only ERLE regions: `[1024,2048)` and `[6656,7168)` (convergence skipped).
- Near-end regions: `[2048,4096)` and `[7168,8192)`; overlap `[4096,6144)`.

Measured synthetic observations (integer millidB, unqualified):

| Item | Value |
| --- | --- |
| Echo-only ERLE, initial / after path change | 58891 / 26285 |
| Min / max echo-only ERLE | 26285 / 58891 |
| Near-reference SNR, clean / noisy | 27704 / 14649 |
| Near level change, clean / noisy | -53 / +185 |
| Near peak, clean / noisy | 99 / 48 |
| Overlap near-reference SNR / level change | 5351 / 1574 |
| No-reference control ERLE | 11111 |
| AEC echo gain over control | 47780 |
| Control / AEC near-reference SNR | 5717 / 27704 |
| Aligned / delayed / missing-render ERLE | 58891 / 9361 / 11111 |

The high echo-only ERLE is an artifact of an exact linear synthetic path, not
evidence of real-room performance; the research note makes the same caution for
its own linear simulation. Delayed and missing render are detected by the ERLE
collapse, and a missing render *hop* is rejected before processing.

## Adverse, missing and invalid handling

`report.json` records 57 rejected inputs, each with unchanged processing state.
Rejections include duplicate JSON key, `NaN`/`Infinity` constants, malformed
JSON, missing/extra config fields, 8 kHz, 44.1 kHz, stereo, 256-sample block,
64-sample hop, `int16`, clock drift, linear resampling, wrong render delay,
nonzero algorithmic latency, boolean rate, missing mic, missing render, epoch
mismatch, wrong mic/render count, invalid valid-count, nonfinite mic, nonfinite
render, nonzero mic/render padding, string and boolean samples, wrong input
position, reset epoch 0/-1/non-increasing, negative reset position,
missing/unsupported/relative/duplicate/wrong-name/bad-hash/zero-byte/wrong-rate/
wrong-channel/wrong-block/wrong-hop/negative-delay/unknown-runtime/empty-version/
extra-field caller manifests, and malformed fixture length/switch/segment/tap/
delay specifications. Missing real recordings, weights, runtime outputs and
labels are `blocked`, never passes.

The caller asset contract validates identity only. It never reads, loads,
imports or executes a source tree, TFLite graph, weight file or runtime. A
hash-matched placeholder is never accepted as a pinned DTLN-AEC artifact.

## Streaming, reset and determinism

The probe is frame-clocked: arbitrary caller chunks
`128/256/384/640/512/128` reproduce the full-block output exactly
(`all_match=true`, `accepted_samples=8192`, `output_samples=8576`). Reset to
epoch 2 matches a fresh epoch-2 session; epoch 0, negative and non-increasing
epochs are rejected with the state digest unchanged. A 100-sample final partial
hop advances state by exactly 100 samples, emits 128 outputs and leaves the
tail invalid samples zero. `run.py` builds the report three times and refuses to
write unless every payload is byte-identical.

## Separation from sibling evidence

The merged `dtln-onnx` package is the separate two-graph ONNX **speech
enhancement** probe; it is not DTLN-AEC and neither imports nor supplies the
paired-reference checkpoints. The merged `cagcrn-joint-aec-and-ns`,
`localvqe-compact-full`, `erle-and-double-talk-preservation`, `nlms-aec`,
`webrtc-aec3` and `aec-challenge-paired-render-capture-fixtures` packages are
separate AEC proposals or references with their own fixtures, assets, metrics
and dispositions. This package does not import, pool, score or reuse their
source, fixtures, metrics or results. Their README/contract/report files are
pinned only as read-only boundary references.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, frozen paired fixture, 512/128 two-stage surrogate, metrics, report and contract builders. |
| `run.py` | Builds all artifacts three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Room report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only strict-JSON, pin, digest, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root
`/Users/htsakanyan/workspace/audio/audioml`. Every row is machine-checked by
`verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` |
| `source:research/voice-enhancement-20261101/evaluation_records.md` | `962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
| `source:adapters/dtln-aec/README.md` | `d19deb34e849fdb19fa3bf942ccb285397252fb233e67ce23a41bc1eda0524c5` |
| `source:adapters/dtln-aec/run.py` | `526a293faa68241f513c7fba5633f33a2429d65fee25a100c0fe4409baa53e98` |
| `source:tests/test_dtln_aec_adapter.py` | `bcc1405d17a50bb426fc047e1658c60b38338d2022d758053ee1fbba65d5699e` |
| `source:data/checkouts/DTLN/pretrained_model/model_1.tflite` | `91281a38e80fe9fd330e28eda7e16fe4e483ee5199a3e687a099939013c25de0` |
| `source:data/checkouts/DTLN/pretrained_model/model_2.tflite` | `7ae37ec802862d8a65b5cdabfbcbbe22caaf7cd39e79adf574d15837d1520830` |

The final two rows are the **present but non-candidate** generic DTLN
speech-enhancement TFLite weights. They are pinned only to prove that the local
generic model is not DTLN-AEC; they are never loaded, scored or substituted.

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
| `sdk:docs/task-evidence/dtln-onnx/README.md` | `aa4d3f0e1f75730c7e1e13f8ed1e75291eeb863d0f64284459b97d0b669d5abe` |
| `sdk:docs/task-evidence/dtln-onnx/contract.json` | `a498c80cdf8f764af8e102f986e6c39a3e4fa8757cdb2e95495a73214324947b` |
| `sdk:docs/task-evidence/dtln-onnx/report.json` | `db37b4c88bf81bca5e0397dd3fcb5d45ffccf95a217cd1f59e198f2fae562bdf` |
| `sdk:docs/task-evidence/cagcrn-joint-aec-and-ns/README.md` | `aeae96f49acad572294b69cafb1b581392c3c3c11171d60545eadd6ede3187c7` |
| `sdk:docs/task-evidence/cagcrn-joint-aec-and-ns/contract.json` | `28870f4d014b198b05bde47c299250ae280442353696bf228f70caf146070668` |
| `sdk:docs/task-evidence/cagcrn-joint-aec-and-ns/report.json` | `697eb9feb470d529ba8132a8d597cb52308f46f5d2c6afd36803de268f9d7828` |
| `sdk:docs/task-evidence/erle-and-double-talk-preservation/README.md` | `0f8ddc78f41459734f4ed096eb71789ecf5bcc809d833c5b65f63319ef11db2e` |
| `sdk:docs/task-evidence/nlms-aec/report.json` | `2910e9e986259a9de738822c35a2908e47a836a9daabc292118f6c7389988f6a` |
| `sdk:docs/task-evidence/webrtc-aec3/report.json` | `da1c2d7bc30fd8e2ae533110cd4130b623859a1747415312386044f41c8c2283` |
| `sdk:docs/task-evidence/aec-challenge-paired-render-capture-fixtures/README.md` | `de5b37cb55275da0f130c2eb524c15f4f12fed18171725596156789ef8b41ccf` |
<!-- digest-table: end -->

## Canonical artifacts and local digests

| File | SHA-256 |
| --- | --- |
| `report.json` | `61d5e6f814e09ea72a622c3f82b566a6930469d1d2c487727ce4177ea86a6a4f` |
| `report.json.sha256` | `fb915156df588b5ae1f5e51fa5fd6ad1975807ec687a9bfe979f561a7d9edec0` |
| `reference.py` | `e6eac30ed7011450a810fd67126e17b1d4f7e1abc3f09c8218aae7953eb55a80` |
| `run.py` | `6687cf29f17abd14e857a51e6c35e36f1509d906d7d72345c55b247eb2ade0df` |
| `test_reference.py` | `2005b6eee9f9000c45f1b77ec9fdf5cb99eba3ccb13a7df491dce3f32a4dd6bc` |
| `verify.py` | `91cfe088414dbde4ed1b8bb2cdec78dc924f1463f805c587660df03ab6509ed7` |

`report.json` is canonical JSON (`sort_keys`, minimal separators, no
`-0.0`/NaN/Infinity, trailing newline). `report.json.sha256` is regenerated
from those exact bytes. `SOURCES.sha256` is a generated manifest of every
pinned boundary, provenance input and file in this directory except itself;
the README is pinned there and is therefore not listed above. `verify.py`
recomputes every digest in this table from the committed bytes and requires the
numbered remaining-gate list below to match the eight contract/report gate
objects.

## Licensing analysis

- Task files are `Apache-2.0` with REUSE SPDX headers/sidecars.
- **No DTLN-AEC license identity or license text is staged.** The generic DTLN
  repository is MIT-licensed, but it is a different model; that MIT text is
  **not accepted** as DTLN-AEC permission.
- No DTLN-AEC model-card, weights, training-data or TFLite-runtime terms were
  found or staged. That absence is recorded, not treated as permission.
- Training-data provenance, product use, redistribution and legal review are
  **not established**. The rights gate stays `blocked`; no upstream asset is
  copied, vendored, built, packaged, downloaded or redistributed.

## Source-reported pilot values (provenance only)

The pinned research note records that a causal TFLite streaming adapter exists
but has only mock-interpreter coverage, that upstream publishes 128/256/512-unit
checkpoints and reports third place in the 2021 challenge, and that the actual
AEC checkpoint and TFLite runtime remain unavailable locally. The pinned
evaluation record states that DTLN-AEC does not have its proper checkpoint
evaluated. These are source-reported conditions; they are not reproduced,
pooled, assigned to the synthetic surrogate or used as thresholds here.

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DTLN-AEC-128-256-512/docs/task-evidence/dtln-aec-128-256-512
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py --check
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DTLN-AEC-128-256-512 diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `run.py` three times and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned DTLN-AEC source, the 128/256/512 two-stage checkpoints
   and a TFLite runtime with an immutable revision, license identity,
   parameter/geometry record and adapter settings.
2. `RG-02` isolated hash-pinned TFLite runtime admission, reproducible build,
   verified stage-1/stage-2 weight identity and recurrent-state shapes, and
   fail-closed absent behavior.
3. `RG-03` code, weight, training-data and corpus rights plus attribution,
   notices, redistribution, product-use and derivative-output review.
4. `RG-04` paired render/capture 512/128 geometry, declared content delay and
   clock mapping into the SDK duplex contract with byte-level output parity.
5. `RG-05` echo-only, near-end-only, overlap and no-reference qualification on a
   rights-cleared task-matched held-out paired cohort including ERLE,
   preservation and alignment.
6. `RG-06` streaming recurrent state, reset, latency, availability, path change,
   delayed/missing render and nonfinite behavior at the exact runtime.
7. `RG-07` target-device pacing, timing and memory with independent listening
   and/or ASR controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed DTLN-AEC source and the selected
128/256/512 two-stage TFLite checkpoints with immutable revision, file hashes,
byte sizes and state shapes; admit an isolated hash-pinned `tflite_runtime` or
TensorFlow environment; clear code/weight/training-data/corpus rights; map
paired render/capture delay and clocks into the accepted duplex contract;
reproduce exact output; qualify echo-only, near-end-only, overlap and
no-reference behavior on a rights-cleared task-matched held-out cohort;
measure target timing and complete opt-in provider intake. Until then the
candidate stays **DEFER**, **incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only
(`tasks[id=SDK-DTLN-AEC-128-256-512]`, stable-field digest); the mutable full
`plan/swarm/TASKS.json` is never hashed, pinned or used as a digest source. No
provider, descriptor, registry, installed default, shared build or CI is
changed.

<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-ESPNET-USES-UNIVERSAL-ENHANCEMENT — source/weights/runtime blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`ESPnet USES universal enhancement`
(`component_id=espnet-uses-universal-enhancement`). The structured inventory
assigns the **Enhancement** acceptance profile
(`verification_profile: enhancement`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Machine-readable decision: **`DEFER`**;
`status=proposal_only_incomplete_not_qualified`; `completeness=incomplete`;
`qualification.status=not_qualified`; `qualifies=false`. No result qualifies.

This package does **not** import, load, link, execute, copy, vendor or download
the ESPnet toolkit, the USES model, the
`espnet/Wangyou_Zhang_universal_train_enh_uses_ref_ch0_2mem_raw` checkpoint,
any PyTorch runtime, any corpus or any vendor artifact. It does not listen,
measure a device, time a callback, run a benchmark or make a release claim. It
pins the research and discovery provenance that is present, proves that the
licensed source, checkpoint, terms, runtime, isolated single-channel mode and
rights-cleared cohort are absent, reproduces only the declared external
boundary and deterministic synthetic controls, and records the exact deferral
condition. Only `docs/task-evidence/espnet-uses-universal-enhancement/` is
written; no provider, descriptor, registry, default, installed-v0, ABI,
shared-build, CI, board or handoff file changes.

## Exact blocker

The pinned census records a **unified single/multi-microphone
enhancement/separation model with variable sample rate**, an official ESPnet
pretrained model-zoo checkpoint, a published demo with a 13 MB model and a
reported CPU speed of a few times real time. It requires freezing the exact
model revision, checking model/data terms, and testing single-channel noise
suppression **separately** from multi-speaker separation. The discovery record
identifies the checkpoint and marks eligibility `blocked`, weights
`located_unverified`, code `available` and `benchmark_state=not_run`, with the
locators:

`https://github.com/espnet/espnet` ·
`https://github.com/espnet/espnet_model_zoo` ·
`https://colab.research.google.com/github/espnet/notebook/blob/master/Demos/enh_demo.ipynb`

It records no immutable source revision, no checkpoint SHA-256, no
toolkit/model/data licence decision, no Python/PyTorch/ESPnet environment, no
rate/frame/utterance/reset/drain contract, no isolated single-channel mode, no
multi-channel layout, no measured latency, no reference output and no
rights-cleared cohort. None is fabricated here.

| Required artifact | Recorded local state |
| --- | --- |
| ESPnet source revision and USES checkpoint | No `data/checkouts/espnet`, `data/models/espnet-uses` or `data/sources/espnet-uses-universal-enhancement`; no immutable revision or full SHA-256 |
| Toolkit/model/data licence and rights approval | No `data/licenses/espnet-uses-universal-enhancement`; no terms text, training-data provenance or signed approval |
| Pinned Python/PyTorch/ESPnet runtime | No `data/envs/espnet-uses-universal-enhancement`; no package lock, installation digest or import route |
| Official geometry and single-channel contract | Only a unified single/multi-microphone model with variable rates and a 16 kHz demo; frame, hop, utterance window, reset, drain, state, delay, multichannel layout and isolated single-channel mode unspecified |
| Rights-cleared cohort | No `data/reference/espnet-uses-universal-enhancement`; no paired noisy/clean speech, consent or metadata |
| Calibrated outputs and scorer | No reference output and no approved SI-SDR/STOI implementation |
| Device timing, memory and state | No timing harness, target device or runtime measurement |
| Adapter intake and release review | No adapter, registration, default, review or release decision |

A PyTorch install, a checkpoint load and an inference call were **not**
attempted. Observed path presence is not runtime admission, reproducibility or
ABI evidence. Every release gate remains `blocked`.

## Scope and invariants

- Work is confined to `docs/task-evidence/espnet-uses-universal-enhancement/`.
  Shared CMake, contracts, public headers, descriptor registry, defaults,
  installed v0 behavior and other tasks are untouched.
- Installed v0 stays 16 kHz / mono / float32 / 160-sample frames. No provider is
  registered, exposed or default-enabled. No adapter code, readiness file or
  registry entry is added.
- The reference is deterministic, model-free and standard-library only. It is
  default OFF, unregistered and not a provider.
- No real speech corpus, listening panel, ESPnet/PyTorch runtime, model weights,
  network download, multichannel input, target-device timing, SI-SDR on
  candidate output, STOI, quality score or release qualification is used. Every
  signal is analytic or seeded-noise.
- Missing, invalid, nonfinite, out-of-range, stale, unapproved and
  missing-artifact cases fail closed. No missing result may qualify the
  candidate.
- Source-reported values (13 MB, CPU a few times real time, variable rates) and
  fixed local controls are reported separately and are never pooled.

## Declared external boundary (proposal only)

`report.json` -> `declared_contract` records only what the pinned sources state.
Nothing is reproduced from an ESPnet/PyTorch runtime.

| Field | Declared value | Status |
| --- | --- | --- |
| Host grid | 16 kHz, mono, float32, 160 samples | Installed v0, unchanged |
| Model family | USES | Source-reported |
| Model-zoo checkpoint | `espnet/Wangyou_Zhang_universal_train_enh_uses_ref_ch0_2mem_raw` | Located, unverified |
| Inference surface | Python/PyTorch model-zoo checkpoint | Source-reported |
| Reported size | 13 MB | Source-reported, not measured |
| Reported CPU speed | A few times real time | Source-reported, not reproduced |
| Sample rates | Variable declared; demo uses 16 kHz | Not established |
| Tasks | Single/multi-microphone enhancement, separation | Source-reported |
| Isolated single-channel mode | Not established | Blocked |
| Multi-speaker separation contract | Not established | Blocked |
| Frame / hop / utterance window | Not established | Blocked |
| Resampling | Not established; host route is 16 kHz only | Blocked |
| Reset / drain / state isolation | Not established | Blocked |
| Content / availability delay | No value declared | Blocked |
| Channel layout | Mono only on the host grid | Not verified against ESPnet |

The Python/PyTorch surface is a deployment description, not an executed
backend. Unified single-channel enhancement, multi-microphone enhancement and
multi-speaker separation are not separated, so they must not be ranked
interchangeably as pure noise suppression.

## Caller-supplied artifact manifest (shape and hash only)

`reference.parse_manifest()` validates a strict 18-field manifest for a
caller-owned artifact. It checks the exact key set, candidate and family IDs,
identifier grammar, full SHA-256 for checkpoint/licence/approval/runtime, a
PyTorch-only backend, a hexadecimal source revision, absolute POSIX paths
without traversal or duplication, the 16 kHz mono host rate, accepted terms and
a fixed caller attestation. `reference.verify_manifest_files()` hashes the
caller-owned bytes and never parses, imports, links or executes them. It records
`official_identity=false`, `vendor_rate_verified=false`,
`single_channel_mode_verified=false` and `separation_mode_verified=false` even
when the bytes match.

The manifest is a shape contract, not admission. An ESPnet review is still
required for the official identity, the supported rates, the isolated
single-channel mode and the multi-speaker separation scope.

## Deterministic synthetic fixture and local controls

The fixture is task-local: 32,000 samples at 16 kHz, mono, seeded harmonic
segments, fixed clicks and seeded noise. It is not speech, not a corpus and not
a candidate output.

| Control | Purpose | Candidate result |
| --- | --- | --- |
| `identity_noisy` | Exact passthrough of the synthetic mixture | No |
| `fixed_highpass_noisy` | Established 80 Hz high-pass control on the mixture | No |
| `identity_clean` | Exact passthrough of the synthetic clean signal | No |
| `fixed_highpass_clean` | High-pass preservation control on clean | No |
| `identity_silence` | Degenerate exact-zero control | No |
| `fixed_highpass_silence` | Degenerate exact-zero control | No |

SI-SDR/SNR in these rows are measured only against the synthetic clean signal.
They are local control diagnostics, not ESPnet USES scores. No row qualifies.

## Adverse, missing and invalid controls

- Ten audio vectors (NaN, infinity, boolean, string, nested, short, long, empty,
  out-of-range, mapping) are rejected with an exact reason.
- Seventeen manifest documents exercise valid shape plus sixteen adverse
  mutations (missing/extra field, wrong candidate/family, relative path,
  traversal, bad/uppercase hash, non-PyTorch backend, unsupported rate, boolean
  rate, stereo, rejected terms, wrong attestation, duplicate paths, empty
  revision). Only `valid_shape` is accepted; it still records
  `files_verified=false` and `official_identity=false`.
- Fifteen required results and ten qualification slots stay `null`/`blocked`.
- Non-host rates, frames and channel counts are rejected by
  `reference.validate_geometry`.
- All eight release gates stay `blocked` with `evidence=null`.

## Enhancement acceptance profile

The profile items record identity/noisy controls and synthetic SI-SDR as
`synthetic_control_only`; the task-matched baseline, isolated single-channel
mode, multichannel/separation scope, variable-rate geometry, paired STOI,
timing, state, rights-cleared cohort, listening, and release terms are
`blocked`. `all_qualify=false`; nothing is promoted.

## Eight blocked release gates

1. Exact ESPnet source revision and USES checkpoint with immutable version and
   full SHA-256.
2. Toolkit/model/data licence, training provenance and written rights approval.
3. Locked Python/PyTorch/ESPnet runtime with exact versions and import digest.
4. Official rate/frame/utterance/reset/drain/delay geometry and an isolated
   single-channel noise-suppression mode.
5. Rights-cleared paired noisy/clean cohort.
6. Independent paired SI-SDR/STOI, preservation, peak and invalid-output
   scoring.
7. Measured state, memory, content/availability timing and callback suitability.
8. OFF-by-default opt-in adapter intake, independent exact-head review,
   listening/quality authorization and release approval.

## Reproduction

```sh
cd docs/task-evidence/espnet-uses-universal-enhancement
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 run.py --contract
python3 run.py --sources
python3 run.py --inspect
python3 verify.py
```

`run.py --report` builds the report three times in process and writes only on
byte-identical canonical output; `verify.py` repeats `--report`, `--contract`,
`--sources` and `--inspect` three times each from cold starts. `SOURCES.sha256`
pins every local artifact except itself. The mutable full
`plan/swarm/TASKS.json` is never read into, hashed by or pinned to this package;
only the stable linked-row identity is compared.

## Exact pins

| Pin | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/evidence/pilot-discovery-20261027/source.txt` | `3591d17581fb9c9168f10d3816f42a9c6178d6168ea386de6eafc6280c18c590` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/store/HEAD.json` | `0f94611fa99911ac1624a3b1eedb576a671fb63a6d8797167e40bfeb7b36fe02` |
| `source:research/store/snapshots/90d8ef52996098cb779a7acfef2e07a3337f6627da94ef7beab9315f6669b2c8.jsonl` | `90d8ef52996098cb779a7acfef2e07a3337f6627da94ef7beab9315f6669b2c8` |
| `boundary:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `boundary:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `boundary:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `boundary:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `boundary:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `boundary:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
| `sibling:docs/task-evidence/ai-coustics-quail/contract.json` | `39c0b277fdff552bacb53dfee86614cfc5273b747800cfacbbbce6330fd95d23` |
| `sibling:docs/task-evidence/ai-coustics-quail/report.json` | `77ac817a110bd243849c6e117e9b805f6a5aad082b5dd3befc6b20ff2dc218a0` |
| `sibling:docs/task-evidence/clearvoice-frcrn-16khz/contract.json` | `d3280353a0360be5b4e56203cad7fc93c6e76b68b20ea65ef667f35456744799` |
| `sibling:docs/task-evidence/clearvoice-frcrn-16khz/report.json` | `a1c41721ba3866ae4bec22d71494ff235699c2887f10d813cdd834e0a97f8aba` |
| `sibling:docs/task-evidence/deepfilternet3-local-listening-preset/contract.json` | `71dce6d33ba03312245abce828a5aa864461ef4376d15a0846eb95decd928a18` |
| `sibling:docs/task-evidence/deepfilternet3-local-listening-preset/report.json` | `66398406770227f04c6d6ab6780bd5f479a3790f5be973a3023e3d9b42e1b95a` |
| `sibling:docs/task-evidence/dpdfnet-2-streaming/contract.json` | `225e0072f021bd592cd5a4685ded735063423c1dda730f065b56652457360ad5` |
| `sibling:docs/task-evidence/dpdfnet-2-streaming/report.json` | `8c9f651f00e26b4be550fd53585cda94d68a4f2903ccfdff94440891ae9a8101` |
| `sibling:docs/task-evidence/fastenhancer-small-reference/contract.json` | `b14d6c657c0ba74b120dc9b8e84c34f381ccef41d52a59e6a7f2434d542e7ce0` |
| `sibling:docs/task-evidence/fastenhancer-small-reference/report.json` | `ecb188b4a1f0d929bd8ddcc19aa1fdb81a7d42892e6dc7aef3ed81aa37bc456e` |
| `sibling:docs/task-evidence/hush/contract.json` | `dff969f74ebb1e7627bebe90aa73e8e40eb18efca99b44d5a956be4208a04d03` |
| `sibling:docs/task-evidence/hush/report.json` | `deaa6ff7bf89bb2727619e69cd41ce40b481ae7db93d25a007cb04b3a218cac4` |

## Non-claims

No ESPnet USES prediction, score, ranking, size measurement, speed measurement,
latency, rate, channel, state, separation, listening, benchmark or release
claim is made. No source, checkpoint, runtime or corpus is present or
reproduced. No result qualifies.

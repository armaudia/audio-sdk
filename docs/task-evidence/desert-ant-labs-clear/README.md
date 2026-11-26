<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DESERT-ANT-LABS-CLEAR — source-available vendor-boundary blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Desert Ant Labs Clear` (`component_id=desert-ant-labs-clear`). The structured
inventory assigns the **Enhancement** acceptance profile
(`verification_profile: enhancement`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Machine-readable decision: **`DEFER`**;
`status=proposal_only_incomplete_not_qualified`; `completeness=incomplete`;
`qualification.status=not_qualified`; `qualifies=false`. No result qualifies.

This package does **not** import, load, link, execute, copy, vendor or download
the Desert Ant Labs Clear model, its source, its ONNX/LiteRT/Apple artifacts,
any vendor runtime or a corpus. It does not listen, measure a device, time a
callback, run a benchmark or make a release claim. It pins the research and
discovery provenance that is present, proves that the licensed artifact, its
own terms, a pinned runtime, a separable denoise-only mode and a rights-cleared
cohort are absent, reproduces only the declared external boundary and
deterministic synthetic controls, and records the exact deferral condition.
Only `docs/task-evidence/desert-ant-labs-clear/` is written; no provider,
descriptor, registry, default, installed-v0, ABI, shared-build, CI, board or
handoff file changes.

## Exact blocker

The pinned census records the candidate as an on-device speech denoise,
dereverb and loudness-normalization product whose model card offers
ONNX/LiteRT/Apple-oriented inference and a source-available license, and warns
that the stages are bundled and are not a pure suppression baseline. The pinned
discovery record marks eligibility `blocked`, weights `located_unverified`,
code `available` and `benchmark_state=not_run`, with the public locators:

`https://huggingface.co/desert-ant-labs/clear` ·
`https://github.com/Desert-Ant-Labs/desert-ant-core`

It records no immutable source revision, no full weight checksum, no licence
text, no SDK version, no rate/frame/hop/reset/drain contract, no separable
denoise-only mode, no declared latency, no reference output and no
rights-cleared cohort. None is fabricated here.

| Required artifact | Recorded local state |
| --- | --- |
| Desert Ant Labs source revision and model/weight artifact | No `data/checkouts/desert-ant-labs`, `data/models/clear` or `data/sources/desert-ant-labs-clear`; no immutable revision or full SHA-256 |
| Source-available licence and rights approval | No `data/licenses/desert-ant-labs-clear`; no terms text, commercial-scale threshold or signed approval |
| Pinned ONNX/LiteRT/Apple runtime | No `data/envs/desert-ant-labs-clear`; no package lock, backend runtime or install digest |
| Official geometry and denoise-only contract | Only ONNX/LiteRT/Apple deployment and bundled denoise/dereverb/loudness stages; frame, hop, reset, drain, state, delay and denoise-only mode unspecified |
| Rights-cleared cohort | No `data/reference/desert-ant-labs-clear`; no paired noisy/clean speech, consent or metadata |
| Calibrated outputs and scorer | No reference output and no approved SI-SDR/STOI implementation |
| Device timing, memory and state | No timing harness, target device or runtime measurement |
| Adapter intake and release review | No adapter, registration, default, review or release decision |

A vendor runtime, a build, an import and an inference call were **not**
attempted. Observed path presence is not runtime admission, reproducibility or
ABI evidence. Every release gate remains `blocked`.

## Scope and invariants

- Work is confined to `docs/task-evidence/desert-ant-labs-clear/`. Shared CMake,
  contracts, public headers, descriptor registry, defaults, installed v0
  behavior and other tasks are untouched.
- Installed v0 stays 16 kHz / mono / float32 / 160-sample frames. No provider is
  registered, exposed or default-enabled. No adapter code, readiness file or
  registry entry is added.
- The reference is deterministic, model-free and standard-library only. It is
  default OFF, unregistered and not a provider.
- No real speech corpus, listening panel, licensed runtime, model weights,
  network download, target-device timing, SI-SDR on candidate output, STOI,
  quality score or release qualification is used. Every signal is analytic or
  seeded-noise.
- Missing, invalid, nonfinite, out-of-range, stale, unapproved and
  missing-artifact cases fail closed. No missing result may qualify the
  candidate.
- Vendor claims, fixed local controls and the declared boundary are reported
  separately and are never pooled.

## Declared external boundary (proposal only)

`report.json` -> `declared_contract` records only what the pinned sources state.
Nothing is reproduced from a vendor runtime.

| Field | Declared value | Status |
| --- | --- | --- |
| Host grid | 16 kHz, mono, float32, 160 samples | Installed v0, unchanged |
| Inference paths | ONNX, LiteRT, Apple-oriented | Source-reported |
| Bundled tasks | Denoise, dereverb, loudness normalization | Source-reported |
| Denoise-only mode | Not established | Blocked |
| Sample-rate variants | Not established | Blocked |
| Frame / hop | Not established | Blocked |
| Resampling | Not established; host route is 16 kHz only | Blocked |
| Reset / drain / state isolation | Not established | Blocked |
| Content / availability delay | No value declared | Blocked |
| Channel layout | Mono only on the host grid | Not verified against vendor |

The ONNX/LiteRT/Apple list is a deployment description, not an executed backend.
The bundled tasks are not separated, so combined denoise/dereverb/normalization
must not be ranked as pure suppression.

## Caller-supplied artifact manifest (shape and hash only)

`reference.parse_manifest()` validates a strict 18-field manifest for a
caller-owned artifact. It checks the exact key set, candidate and family IDs,
identifier grammar, full SHA-256 for artifact/licence/approval/runtime, an
ONNX/LiteRT/Apple backend, a hexadecimal source revision, absolute POSIX paths
without traversal or duplication, the 16 kHz host rate, mono, accepted terms and
a fixed caller attestation. `reference.verify_manifest_files()` hashes the
caller-owned bytes and never parses, imports, links or executes them. It records
`official_identity=false`, `vendor_rate_verified=false` and
`denoise_only_mode_verified=false` even when the bytes match.

The manifest is a shape contract, not admission. A vendor review is still
required for the official identity, the vendor's supported rates and a
denoise-only mode.

## Deterministic synthetic fixture and local controls

The fixture is task-local: 32,000 samples at 16 kHz, mono, seeded harmonic
segments, fixed clicks and seeded noise. It is not speech, not a corpus and not
a candidate output.

| Segment | Samples | Frames | Description |
| --- | --- | --- | --- |
| `silence-head` | 0–3200 | 0–19 | Exact digital silence |
| `quiet-speech` | 3200–11200 | 20–69 | Low-level harmonic segment |
| `speech` | 11200–19200 | 70–119 | Mid-level harmonic segment |
| `loud-transient` | 19200–27200 | 120–169 | Loud harmonic segment plus fixed clicks |
| `silence-tail` | 27200–32000 | 170–199 | Exact digital silence |

Two local controls are measured: exact identity passthrough and a fixed causal
80 Hz second-order high-pass (`Q=0.7071067811865476`). Neither is Clear, neither
is a candidate result, and neither can rank the candidate.

## Results (local control invariants only, not Clear results)

All values are exact `report.json` values. They are local control observations,
**not Desert Ant Labs Clear results**, not device timing and not a release claim.
No intelligibility, quality, listening, SI-SDR-on-candidate, STOI/MOS or
perceptual score is claimed.

| Control | RMS | Peak abs | Clipped | SI-SDR dB* | SNR dB* |
| --- | ---: | ---: | ---: | ---: | ---: |
| Identity, noisy | 0.085905554 | 0.454498291 | 0 | 6.572541626 | 6.585453593 |
| Fixed high-pass, noisy | 0.079521652 | 0.607267979 | 0 | 5.251859246 | 6.013788694 |
| Identity, clean | 0.077886104 | 0.459869385 | 0 | null | null |
| Fixed high-pass, clean | 0.077454567 | 0.556248154 | 0 | 6.369972982 | 7.075345355 |
| Identity, silence | 0.0 | 0.0 | 0 | null | null |
| Fixed high-pass, silence | 0.0 | 0.0 | 0 | null | null |

\* Against the synthetic clean signal only. `null` means the metric is
undefined for an exact or degenerate control, not a perfect score.

Additional exact invariants: the identity noisy output is byte-identical to the
synthetic mixture; both silence controls return exact zero; no control produces
a nonfinite sample or a clipped sample; the fixture, control rows and their
digests are identical across regeneration; invalid, nonfinite, out-of-range,
short, long, empty and nonnumeric frames are rejected before any state change.

## Failure controls (exact failures recorded as failures)

- **Audio:** 10 adverse vectors are rejected: NaN, positive infinity, boolean,
  string, nested, 159-sample short, 161-sample long, empty, out-of-range 8.5 and
  a mapping container. Every rejection records the expected error and
  `qualifies=false`. Nonfinite input is never counted as silence.
- **Geometry:** 44.1 kHz, stereo, 320-sample frames, `int16` and boolean rate are
  rejected.
- **Manifest:** 16 adverse documents are rejected: missing and extra fields,
  wrong candidate and family, relative path, parent traversal, 63-character and
  uppercase hashes, an unsupported backend, unsupported host rate, boolean rate,
  stereo, rejected terms, wrong attestation, duplicate paths and empty source
  revision. Missing files and mismatched bytes are rejected by the file checker.
- **Qualification:** all 13 missing-result rows are `blocked` with `value=null`;
  all 10 qualification slots are null; all eight gates are `blocked`.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied item by item in
`report.json` -> `acceptance_profile`; every item is `qualifies=false`. The
combined-stage warning is a separate blocked item because the candidate bundles
denoise, dereverb and loudness normalization.

| Required item | Status here | Evidence |
| --- | --- | --- |
| Identity / noisy control | synthetic_control_only | Exact passthrough on the synthetic mixture |
| Established task-matched baseline | blocked | No approved baseline or vendor reference |
| Combined-stage separation | blocked | Denoise-only mode not established |
| Paired SI-SDR | synthetic_control_only | Control-only values against synthetic clean |
| Paired STOI | blocked | No approved scorer or rights-cleared cohort |
| Clean-speech preservation | synthetic_control_only | Fixed high-pass on synthetic clean only |
| Peaks and invalid outputs | synthetic_control_only | Control peaks, zero clipping, explicit rejections |
| Alignment and content delay | blocked | No rate, frame or latency contract established |
| State, memory and independent instances | blocked | No vendor runtime or stateful test |
| Rights-cleared cohort | blocked | No cohort, consent or metadata |
| Listening or authorized quality | blocked | No panel, authorization or result |
| Adverse / missing / nonfinite | synthetic_control_only | 10 audio and 16 manifest rejections |
| Release and distribution terms | blocked | Source-available terms and combined output use unapproved |

## Eight blocked release gates

1. `exact_source_revision_and_weight_artifact`
2. `source_available_license_and_distribution_terms`
3. `pinned_runtime_and_backend_environment`
4. `official_geometry_denoise_only_mode_and_delay`
5. `rights_cleared_paired_cohort`
6. `independent_paired_quality_and_preservation`
7. `measured_state_memory_and_target_timing`
8. `opt_in_adapter_intake_listening_and_release_review`

Each gate is `blocked` with `evidence=null` and `qualifies=false` in
`contract.json` and `report.json`.

## Exact missing artifacts and rights

| Missing artifact | Rights requirement |
| --- | --- |
| Desert Ant Labs Clear source revision and model/weight artifact for a recorded backend | Artifact-specific source-available terms, redistribution and derivative-output permissions, and written approval to execute |
| Reviewed licence text and rights decision | Licence text, commercial-scale threshold, output-use and redistribution terms |
| Pinned ONNX/LiteRT/Apple runtime and dependency lock | Runtime/dependency licences and exact-version approval |
| Official geometry and denoise-only contract | Vendor documentation admitted under the reviewed terms |
| Rights-cleared paired noisy/clean speech cohort | Corpus, participant, device and redistribution rights |
| Reference outputs and approved scorer | Scorer/reference terms and exact-revision approval |
| Target-device timing, memory and state evidence | Device and timing-harness approval |
| OFF-by-default adapter intake and review | Reviewer, panel and release-authority approval |

No download, fabrication or substitution was attempted. A located-but-unverified
weight is not an artifact identity.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, results, gates. |
| `reference.py` | Deterministic fixture, local controls, strict manifest parser, declared boundary and report/contract builders. |
| `run.py` | Regenerates the report three times, the contract and the manifest. |
| `report.json` | Canonical machine-readable enhancement report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, qualification. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only pin, strict-JSON, digest, README-table, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for every local artifact and this README. |
| `*.license` | REUSE sidecars for JSON and digest artifacts. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py` and the test suite. Only provenance files that
exist are pinned; no absent candidate artifact is given a fabricated hash.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/evidence/pilot-discovery-20261027/source.txt` | `3591d17581fb9c9168f10d3816f42a9c6178d6168ea386de6eafc6280c18c590` |
| `source:research/store/HEAD.json` | `0f94611fa99911ac1624a3b1eedb576a671fb63a6d8797167e40bfeb7b36fe02` |
| `source:research/store/snapshots/90d8ef52996098cb779a7acfef2e07a3337f6627da94ef7beab9315f6669b2c8.jsonl` | `90d8ef52996098cb779a7acfef2e07a3337f6627da94ef7beab9315f6669b2c8` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
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

The sibling packages are separate evidence. They are pinned here as prior local
artifacts, not imported, pooled or reinterpreted. They cover enhancement and
denoiser boundaries only; none is the Desert Ant Labs Clear candidate, and none
of their metrics, fixtures or adapters enter this package.

<!-- digest-table: sibling -->
| Key | SHA-256 |
| --- | --- |
| `sibling:docs/task-evidence/ai-coustics-quail/contract.json` | `39c0b277fdff552bacb53dfee86614cfc5273b747800cfacbbbce6330fd95d23` |
| `sibling:docs/task-evidence/ai-coustics-quail/report.json` | `77ac817a110bd243849c6e117e9b805f6a5aad082b5dd3befc6b20ff2dc218a0` |
| `sibling:docs/task-evidence/clearvoice-frcrn-16khz/contract.json` | `d3280353a0360be5b4e56203cad7fc93c6e76b68b20ea65ef667f35456744799` |
| `sibling:docs/task-evidence/clearvoice-frcrn-16khz/report.json` | `a1c41721ba3866ae4bec22d71494ff235699c2887f10d813cdd834e0a97f8aba` |
| `sibling:docs/task-evidence/clearvoice-mossformergan/contract.json` | `cd98bc7b615b0861923d2a53a24ec91fd939c6dcade0818022912a5a5e34869c` |
| `sibling:docs/task-evidence/clearvoice-mossformergan/report.json` | `5c806186d35c1f39021617dc5649bf32d87030a1a059d26e35492a69ee1a7afc` |
| `sibling:docs/task-evidence/deepfilternet3-local-listening-preset/contract.json` | `71dce6d33ba03312245abce828a5aa864461ef4376d15a0846eb95decd928a18` |
| `sibling:docs/task-evidence/deepfilternet3-local-listening-preset/report.json` | `66398406770227f04c6d6ab6780bd5f479a3790f5be973a3023e3d9b42e1b95a` |
| `sibling:docs/task-evidence/fastenhancer-small-reference/contract.json` | `b14d6c657c0ba74b120dc9b8e84c34f381ccef41d52a59e6a7f2434d542e7ce0` |
| `sibling:docs/task-evidence/fastenhancer-small-reference/report.json` | `ecb188b4a1f0d929bd8ddcc19aa1fdb81a7d42892e6dc7aef3ed81aa37bc456e` |
| `sibling:docs/task-evidence/hush/contract.json` | `dff969f74ebb1e7627bebe90aa73e8e40eb18efca99b44d5a956be4208a04d03` |
| `sibling:docs/task-evidence/hush/report.json` | `deaa6ff7bf89bb2727619e69cd41ce40b481ae7db93d25a007cb04b3a218cac4` |
<!-- digest-table: end -->

## External artifact identity

No external artifact is pinned: the source revision, model/weight artifact, full
checksum, licence, runtime, geometry, denoise-only mode and reference output are
not established. Every required-artifact row records `present=false`. If any of
those artifacts appears, this package is stale and must reopen.

## Artifact digests (SHA-256)

`report.json` is canonical JSON (sorted keys, indent 2, `allow_nan=False`, LF,
one trailing newline). The canonical digest of the committed bytes is stored in
[`report.json.sha256`](report.json.sha256). `SOURCES.sha256` pins every artifact
and this README; it does not pin itself.

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `09d3b295bec7640f5259776a2713771c632bcf0356f639c9c4b2a11a727257a9` | 69744 |
| `report.json` | `d25b33e6ca4febbd6ea8af385c3736e96ce45ed31ccb46ad16740a4f81be52ac` | 41435 |
| `report.json.sha256` | `19c70a344756adbfe4c08970271897f65cd28a7300330506e713305ceb2e4530` | 65 |
| `run.py` | `5c22f847a84feb2a92910e37c72036c8cfd1a8add600ddcdf6b510e137b8f80c` | 2979 |
| `test_reference.py` | `c04625904bf9da8de215aa370f2c7f0b3bfd3d3f73940f4419b47182907d5f09` | 25093 |
| `verify.py` | `ccfc97e05460ddab9aa6607e153071ded82494240c60f9535759ffca49e1753b` | 26635 |

The `report.json` SHA-256 is
`d25b33e6ca4febbd6ea8af385c3736e96ce45ed31ccb46ad16740a4f81be52ac`
(41,435 bytes). Tests: **54 passed, 0 failed, 0 skipped**.

## Reproduce

Run from this directory with the pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DESERT-ANT-LABS-CLEAR
TASK=$WT/docs/task-evidence/desert-ant-labs-clear
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
declared boundary, null candidate slots, controls, eight blocked gates, SPDX
annotations, dependency hygiene and task-local scope containment. JSON is
canonical (`sort_keys=True`, `allow_nan=False`) with one trailing newline.

## Non-claims and boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`asset_bundled=false`, `weights_vendored=false`,
`vendor_runtime_invoked=false`, `native_engine_built=false`,
`sdk_data_dir_added=false`.

Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row identity only (`tasks[id=SDK-DESERT-ANT-LABS-CLEAR]`,
stable-field projection); the mutable full `plan/swarm/TASKS.json` is never read
into, hashed by or pinned to this package. No provider, descriptor, registry,
installed default, public ABI, shared build or CI is changed.

## Separation from sibling evidence

AI-coustics Quail, ClearerVoice FRCRN, ClearerVoice MossFormerGAN, HUSH,
DeepFilterNet3 and FastEnhancer packages are **separate evidence**. They use
different candidates, fixtures, cadences and dispositions. This package does not
pool, import, reuse or reinterpret their outputs, metrics or adapters. The
research notes, inventory and discovery snapshot are pinned provenance only;
they are not source archives, runnable candidates or reference outputs, and they
are not changed.

## Reopen condition

Supply (a) the exact Desert Ant Labs Clear source revision and model/weight
artifact for a recorded ONNX/LiteRT/Apple backend, with an immutable version and
full SHA-256; (b) the artifact's own source-available terms, any commercial
scale threshold, redistribution and output-use permissions, plus written
approval to execute; (c) a locked runtime with exact dependency versions; (d)
the official rate/frame/hop/reset/drain/state geometry, channel layout,
resampling and measured content/availability delay on the target device, plus a
separable denoise-only mode; (e) a rights-cleared paired noisy/clean cohort with
consent and metadata; (f) approved reference outputs and a pinned SI-SDR/STOI
implementation; and (g) independent exact-head review, authorized
listening/quality assessment and an OFF-by-default opt-in adapter intake. Until
then the candidate stays **DEFER**, **incomplete** and **not qualified**.

## License

All files here are first-party `Apache-2.0`, copyright 2026 Tsakanyan Hovhannes.
Python and Markdown files carry file-level SPDX tags; JSON and digest files are
covered by adjacent `.license` sidecars and the repository `REUSE.toml`
annotation for `docs/**`.

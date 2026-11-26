<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-HECTTOR-HERMES-NOISE-CANCELLATION — Hecttor Hermes vendor-boundary blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Hecttor Hermes noise cancellation`
(`component_id=hecttor-hermes-noise-cancellation`). The structured inventory
assigns the **Enhancement** acceptance profile (`verification_profile:
enhancement`, `plan/INVENTORY.json`), defined in `plan/swarm/VERIFICATION.md`.
Machine-readable decision: **`DEFER`**;
`status=proposal_only_incomplete_not_qualified`; `completeness=incomplete`;
`qualification.status=not_qualified`; `qualifies=false`. No result qualifies.

This package does **not** import, load, link, execute, copy, vendor or download
the commercial Hecttor Hermes SDK, either optional denoising model family, the
blend control, a platform build, an evaluation key or a corpus. It does not
listen, measure a device, time a callback, run a benchmark or make a release
claim. It pins the research and discovery provenance that is present, proves
that the licensed artifact, its own terms, a commercial evaluation key, a
pinned runtime and a rights-cleared cohort are absent, reproduces only the
declared external boundary and deterministic synthetic controls, and records
the exact deferral condition. Only
`docs/task-evidence/hecttor-hermes-noise-cancellation/` is written; no provider,
descriptor, registry, default, installed-v0, ABI, shared-build, CI, board or
handoff file changes.

## Exact blocker

The pinned census and discovery record state the candidate as a commercial
native SDK with **two optional denoising model families** and a **blend
control**. Official docs are said to support **six SDK languages/platforms**,
**multiple sample rates** and a **denoise-only module configuration**; an
**evaluation license/key and platform build are supplied through onboarding**.
The discovery record marks eligibility `blocked`, weights `bundled_or_gated`
and `benchmark_state=not_run`, with access condition
`commercial_evaluation_key_required`. It records no immutable artifact
revision, no full checksum, no licence text, no SDK version, no rate list, no
frame/hop/reset/drain contract, no latency value, no reference output and no
rights-cleared cohort. None is fabricated here.

| Required artifact | Recorded local state |
| --- | --- |
| Vendor SDK, platform build and model artifact | No `data/checkouts/hecttor`, `data/models/hecttor` or `data/sources/hecttor-hermes-noise-cancellation`; no immutable version or full SHA-256 |
| Commercial evaluation key and rights approval | No `data/licenses/hecttor-hermes-noise-cancellation`; no key, terms text, telemetry review or signed approval |
| Pinned runtime environment | No `data/envs/hecttor-hermes-noise-cancellation`; no package lock or install digest |
| Official geometry and process contract | Only "multiple sample rates" with no list; frame/hop/reset/drain/state/blend/delay unspecified |
| Rights-cleared cohort | No `data/reference/hecttor-hermes-noise-cancellation`; no paired noisy/clean speech, consent or metadata |
| Calibrated outputs and scorer | No reference output and no approved SI-SDR/STOI implementation |
| Device timing and memory | No timing harness, target device or runtime measurement |
| Adapter intake and release review | No adapter, registration, default, review or release decision |

A vendor runtime, a platform build, an import and an inference call were **not**
attempted. Observed path presence is not runtime admission, reproducibility or
ABI evidence. Every release gate remains `blocked`. No latency value is stated
in the pinned record and **none is assumed, converted or measured**.

## Scope and invariants

- Work is confined to `docs/task-evidence/hecttor-hermes-noise-cancellation/`.
  Shared CMake, contracts, public headers, descriptor registry, defaults,
  installed v0 behavior and other tasks are untouched.
- Installed v0 stays 16 kHz / mono / float32 / 160-sample frames. No provider is
  registered, exposed or default-enabled. No adapter code, readiness file or
  registry entry is added.
- The reference is deterministic, model-free and standard-library only. It is
  default OFF, unregistered and not a provider.
- No real speech corpus, listening panel, licensed runtime, model weights,
  network download, target-device timing, SI-SDR on candidate output, STOI,
  quality score or release qualification is used. Every signal is analytic or
  seeded-noise.
- Missing, invalid, nonfinite, out-of-range, out-of-bound, stale, unapproved,
  non-isolated and missing-artifact cases fail closed. No missing result may
  qualify the candidate.
- Vendor claims, fixed local controls and the declared boundary are reported
  separately and are never pooled.

## Declared external boundary (proposal only)

`report.json` -> `declared_contract` records only what the pinned record states.
Nothing is reproduced from the vendor runtime.

| Field | Declared value | Status |
| --- | --- | --- |
| Host grid | 16 kHz, mono, float32, 160 samples | Installed v0, unchanged |
| Vendor model families | Two optional denoising families, **unnamed** in the record | Source-reported |
| Blend control | Present, range and law unspecified | Source-reported |
| SDK languages/platforms | 6 | Source-reported |
| Vendor sample rates | "Multiple", **no list** | Blocked |
| Vendor rate verification | Not established | Blocked |
| Declared latency | **No value stated** | Blocked |
| Frame / hop | Not established | Blocked |
| Resampling | Policy not established | Blocked |
| Reset / drain / state isolation | Not established | Blocked |
| Blend-control contract | Not established | Blocked |
| Channel layout | Mono on the host grid | Not verified against vendor |
| Telemetry / deployment terms | Not reviewed | Blocked |
| Isolation requirement | Denoise-only; Voice Boost and speed control disabled | Source-reported requirement |

`declared_latency_ms` is `null` in `contract.json` and `report.json`. The
reference rejects attempts to assert a vendor rate or latency instead of
converting a claim that the record does not contain.

## Caller-supplied artifact manifest (shape and hash only)

`reference.parse_manifest()` validates a strict **22-field** manifest for a
caller-owned artifact. It checks the exact key set, candidate and family IDs,
identifier grammar, full SHA-256 for artifact/licence/approval/runtime,
provider checksum prefix agreement, absolute POSIX paths without traversal or
duplication, a positive integer rate within the generic structural bound
8,000–192,000 Hz (explicitly **not** a vendor rate claim), mono, and a fixed
caller attestation. It additionally enforces the task isolation requirement:
`denoise_only`, `voice_boost_disabled`, `speed_control_disabled`,
`telemetry_terms_reviewed` and `terms_accepted` must all be `true`.

`reference.verify_manifest_files()` hashes the caller-owned bytes only. It
**never parses, imports, links or executes** the artifact, and even a fully
hash-matched caller placeholder reports `official_identity=false` because
vendor rights review is still required.

`report.json` -> `manifest_controls` records one accepted shape-only control and
**21** explicit rejections. All controls have `qualifies=false`.

## Synthetic fixture and local controls

`reference.build_clean()` and `reference.build_noise()` synthesise 32,000
samples (2 s, 200 frames) from a fixed 256-entry sine table, integer phase
increments, a 31-bit LCG, integer-quantised amplitudes and exact segment
boundaries. The mixture is quantised int16 and exposed as
`float32 / 32768`. The fixture is not speech and not a corpus.

| Stratum | Samples | Frames | Condition |
| --- | --- | ---: | --- |
| `silence-a` | 0–3200 | 0–19 | Exact digital silence |
| `quiet-speech` | 3200–11200 | 20–69 | Quiet harmonic segment |
| `speech` | 11200–19200 | 70–119 | Mid-level harmonic segment |
| `loud-transient` | 19200–27200 | 120–169 | Loud harmonic segment plus fixed clicks |
| `silence-tail` | 27200–32000 | 170–199 | Exact digital silence |

Two local controls are measured: exact identity passthrough and a fixed causal
80 Hz second-order high-pass (`Q=0.7071067811865476`). Neither is Hecttor
Hermes, neither is a candidate result, and neither can rank the candidate.

## Results (local control invariants only, not Hermes results)

All values are exact `report.json` values. They are local control observations,
**not Hecttor Hermes results**, not device timing and not a release claim. No
intelligibility, quality, listening, SI-SDR-on-candidate, STOI/MOS or perceptual
score is claimed.

| Control | RMS | Peak abs | Clipped | SI-SDR dB* | SNR dB* |
| --- | ---: | ---: | ---: | ---: | ---: |
| Identity, noisy | 0.089891823 | 0.414337158 | 0 | 8.157794455 | 8.140330486 |
| Fixed high-pass, noisy | 0.084449609 | 0.583052822 | 0 | 3.945514637 | 5.016440565 |
| Identity, clean | 0.08355438 | 0.449981689 | 0 | null | null |
| Fixed high-pass, clean | 0.082655339 | 0.571803127 | 0 | 4.508223459 | 5.553344065 |
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
- **Geometry:** 44.1 kHz, 8 kHz, stereo, 320-sample frames, `int16` and boolean
  rate are rejected; vendor rates are not asserted because the record lists
  none.
- **Manifest:** 21 adverse documents are rejected: missing and extra fields,
  wrong candidate, empty family ID, relative path, parent traversal,
  non-POSIX path, 63-character and uppercase hashes, checksum-prefix mismatch,
  boolean rate, out-of-structural-bound rate, stereo, `denoise_only=false`,
  Voice Boost enabled, speed control enabled, unreviewed telemetry terms,
  rejected terms, wrong attestation, duplicate paths and empty SDK version.
  Missing files and mismatched bytes are rejected by the file checker.
- **Qualification:** all 12 missing-result rows are `blocked` with `value=null`;
  all 10 qualification slots are null; all eight gates are `blocked`.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied item by item in
`report.json` -> `acceptance_profile`; every item is `qualifies=false`.

| Required item | Status here | Evidence |
| --- | --- | --- |
| Identity / noisy control | synthetic_control_only | Exact passthrough on the synthetic mixture |
| Established task-matched baseline | blocked | No approved baseline or vendor reference |
| Paired SI-SDR | synthetic_control_only | Control-only values against synthetic clean |
| Paired STOI | blocked | No approved scorer or rights-cleared cohort |
| Clean-speech preservation | synthetic_control_only | Fixed high-pass on synthetic clean only |
| Peaks and invalid outputs | synthetic_control_only | Control peaks, zero clipping, explicit rejections |
| Alignment and content delay | blocked | No latency value is stated and none is measured |
| State, memory and independent instances | blocked | No vendor runtime or stateful test |
| Rights-cleared cohort | blocked | No cohort, consent or metadata |
| Listening or authorized quality | blocked | No panel, authorization or result |
| Adverse / missing / nonfinite | synthetic_control_only | 10 audio and 21 manifest rejections |
| Release and distribution terms | blocked | Commercial terms, telemetry and output use unapproved |

## Eight blocked release gates

1. `exact_vendor_artifact_and_full_checksum`
2. `commercial_license_key_and_distribution_terms`
3. `pinned_sdk_runtime_and_environment`
4. `official_geometry_content_and_availability_delay`
5. `rights_cleared_paired_cohort`
6. `independent_paired_quality_and_preservation`
7. `measured_state_memory_and_target_timing`
8. `opt_in_adapter_intake_listening_and_release_review`

Each gate is `blocked` with `evidence=null` and `qualifies=false` in
`contract.json` and `report.json`.

## Exact missing artifacts and rights

| Missing artifact | Rights requirement |
| --- | --- |
| Hecttor Hermes commercial SDK, platform build and one denoising model artifact for a declared rate | Artifact-specific commercial terms, redistribution and derivative-output permissions, and written approval to execute |
| Reviewed licence text, commercial evaluation key and rights decision | Vendor account, model-use, telemetry, deployment, output-use and redistribution terms |
| Pinned SDK runtime and dependency lock | Runtime/dependency licences and exact-version approval |
| Official geometry and process contract | Vendor documentation admitted under the reviewed terms |
| Rights-cleared paired noisy/clean speech cohort | Corpus, participant, device and redistribution rights |
| Reference outputs and approved scorer | Scorer/reference terms and exact-revision approval |
| Target-device timing and memory evidence | Device and timing-harness approval |
| OFF-by-default denoise-only adapter intake and review | Reviewer, panel and release-authority approval |

No download, fabrication or substitution was attempted. No checksum prefix,
rate list or latency value is invented to fill a gap.

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
artifacts, not imported, pooled or reinterpreted. The two commercial
ai-coustics comparators (Quail, Rook) and the research denoisers follow the same
enhancement-profile DEFER pattern but address different candidates, fixtures and
dispositions.

<!-- digest-table: sibling -->
| Key | SHA-256 |
| --- | --- |
| `sibling:docs/task-evidence/ai-coustics-quail/contract.json` | `39c0b277fdff552bacb53dfee86614cfc5273b747800cfacbbbce6330fd95d23` |
| `sibling:docs/task-evidence/ai-coustics-quail/report.json` | `77ac817a110bd243849c6e117e9b805f6a5aad082b5dd3befc6b20ff2dc218a0` |
| `sibling:docs/task-evidence/ai-coustics-rook/contract.json` | `19080a3e2068c0042352fdf5476b056cc4ca5ecf813d938d618715b8dcc45966` |
| `sibling:docs/task-evidence/ai-coustics-rook/report.json` | `e69a2bf3dd3e7fd496176c77c04285d9bd5d37f09fd4f76a51be394239832f20` |
| `sibling:docs/task-evidence/dasheng-denoiser/contract.json` | `9b2c86f9056b102f0c58cbfe4cc46b0d8f72bc9ccfc0f7f2baf637df337a45cd` |
| `sibling:docs/task-evidence/dasheng-denoiser/report.json` | `cdb85350b4f5d6ccc771813f72be1291049397678151f572127e768297045984` |
| `sibling:docs/task-evidence/facebook-denoiser-dns48/contract.json` | `525d969d8505d2d5ed91f9a06c078800231e90e5dca0cba7e335e0596d89d61b` |
| `sibling:docs/task-evidence/facebook-denoiser-dns48/report.json` | `9e1caa72da181e41fb9d95f1e1c2c4aacfe4d246000a8f977211edd970e2c8c5` |
| `sibling:docs/task-evidence/deepvqe-dns3-noise-suppression-configuration/contract.json` | `1fbbc4e365c4b359898354622ec522ca0f9949c85a2fc1f8818b6dae8dd519c9` |
| `sibling:docs/task-evidence/deepvqe-dns3-noise-suppression-configuration/report.json` | `b5c5eef3f22d39bf8ceea9a177b7d5d6b194ef21326a56742fe69c489e5b3455` |
| `sibling:docs/task-evidence/hush/contract.json` | `dff969f74ebb1e7627bebe90aa73e8e40eb18efca99b44d5a956be4208a04d03` |
| `sibling:docs/task-evidence/hush/report.json` | `deaa6ff7bf89bb2727619e69cd41ce40b481ae7db93d25a007cb04b3a218cac4` |
<!-- digest-table: end -->

## External artifact identity

No external artifact is pinned: the vendor SDK, platform build, model artifact,
full checksum, commercial key, licence, version, runtime geometry and reference
output are not established. Every required-artifact row records `present=false`.
If any of those artifacts appears, this package is stale and must reopen.

## Artifact digests (SHA-256)

`report.json` is canonical JSON (sorted keys, indent 2, `allow_nan=False`, LF,
one trailing newline). The canonical digest of the committed bytes is stored in
[`report.json.sha256`](report.json.sha256). `SOURCES.sha256` pins every artifact
and this README; it does not pin itself.

## Reproduce

Run from this directory with the pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-HECTTOR-HERMES-NOISE-CANCELLATION
TASK=$WT/docs/task-evidence/hecttor-hermes-noise-cancellation
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
referenced by stable linked-row identity only
(`tasks[id=SDK-HECTTOR-HERMES-NOISE-CANCELLATION]`, stable-field projection); the
mutable full `plan/swarm/TASKS.json` is never read into, hashed by or pinned to
this package. No provider, descriptor, registry, installed default, public ABI,
shared build or CI is changed.

## Separation from sibling evidence

The ai-coustics Quail and Rook packages, Dasheng, Facebook Denoiser DNS48,
DeepVQE DNS3 and HUSH packages are **separate evidence**. They use different
candidates, fixtures, cadences and dispositions. This package does not pool,
import, reuse or reinterpret their outputs, metrics or adapters. The research
notes, inventory and discovery snapshot are pinned provenance only; they are not
source archives, runnable candidates or reference outputs, and they are not
changed.

## Reopen condition

Supply (a) the exact Hecttor Hermes commercial SDK, platform build and one
denoising model artifact for a declared rate, with an immutable version and full
SHA-256; (b) the artifact's own commercial terms, evaluation key, telemetry and
deployment terms, redistribution and output-use permissions, plus written
approval to execute; (c) a locked runtime with exact dependency versions; (d)
the official rate list, frame/hop/reset/drain/state/blend geometry, channel
layout, resampling and **measured** content/availability delay on the target
device; (e) a rights-cleared paired noisy/clean cohort with consent and
metadata; (f) approved reference outputs and a pinned SI-SDR/STOI
implementation; and (g) independent exact-head review, authorized
listening/quality assessment and an OFF-by-default denoise-only opt-in adapter
intake. Until then the candidate stays **DEFER**, **incomplete** and **not
qualified**; all eight release gates remain blocked.

## License

All files here are first-party `Apache-2.0`, copyright 2026 Tsakanyan Hovhannes.
Python and Markdown files carry file-level SPDX tags; JSON and digest files are
covered by adjacent `.license` sidecars and the repository `REUSE.toml`
annotation for `docs/**`.

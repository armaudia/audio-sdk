<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PCEN-FEATURE-FRONTEND — PCEN feature frontend blocker

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **feasibility and blocker package** for inventory
component `pcen-feature-frontend` (Detection, verification profile `analysis`).
PCEN (Per-Channel Energy Normalization) is a feature frontend; the merged
inventory and research boundary keep it separate from waveform loudness
control. No exact licensed PCEN reference implementation, pinned revision,
reference parameters/assets, runtime, rights record, detection/keyword cohort,
or parity vector is present in this workspace. It creates **no new execution,
model, corpus, real audio, provider, processor, ABI, default, build, CI,
board, handoff or release change**.

Task owner: `agent-PCEN-FEATURE-FRONTEND`; reviewer:
`reviewer-PCEN-FEATURE-FRONTEND`. Claim base: audio-sdk
`180e2bcd29430280f939f229ab0af2171a57e69f`; branch
`swarm/SDK-PCEN-FEATURE-FRONTEND`. The task depends on `SDK-FND-AUDIT`,
`SDK-FND-EVIDENCE` and `SDK-FND-PROVIDER`; write scope is the task-local
evidence directory only (`docs/task-evidence/pcen-feature-frontend/`).

## What is missing and why no result can qualify

Merged inventory records `pcen-feature-frontend` as `considered`, repository
`audio-sdk`, verification profile `analysis`, with evidence
`research/level_tone_control_20261028.md` and plan note: test as a feature
stage for detection and keyword spotting; keep waveform loudness under its own
task. `docs/task-evidence/survey-cln-09/` records PCEN as an adjacent feature
frontend, not a waveform loudness controller. The research note cites Wang et
al., “Trainable Frontend For Robust and Far-Field Keyword Spotting” (ICASSP
2017), but this workspace contains no exact licensed checkout, pinned
revision, reference params/weights, runtime lock, rights record, detection or
keyword cohort, degradation/parity manifest, or measured PCEN output.

No missing result can qualify the candidate. The package decision is
`DEFER` and qualification is `not_qualified`. Any future work must first
supply the missing artifacts, clear rights, establish exact geometry/scope,
produce exact-reference parity on a frozen caller-supplied input, and pass
analysis-profile quality/timing evidence before opt-in provider intake.

## Boundary

- **No registration/default.** No provider, descriptor, registry entry,
  installed v0 path, shared build or CI file changes.
- **No model/runtime execution.** Python stdlib only. No TensorFlow, PyTorch,
  LEAF, KWS runtime, NumPy, audio runtime, download, or device timing.
- **No real data.** No real audio, detection corpus, keyword corpus, labels,
  listening, or public benchmark.
- **PCEN is not performed.** The synthetic control is shape/accounting only;
  it validates finite input handling, frame accounting, and declared parameter
  bounds. It is not PCEN output, not model output, and cannot qualify.
- **Stable TASKS identity only.** The mutable full `plan/swarm/TASKS.json` is
  never hashed. Only the linked stable row identity is pinned/gated.

## Exact blockers and 8 blocked release gates

| Blocker | State | Requirement |
| --- | --- | --- |
| `source_checkout_absent` | absent | Supply exact licensed PCEN reference implementation at immutable 40-hex revision. |
| `reference_assets_absent` | absent | Supply exact reference params/config/assets with SHA-256 and byte counts. |
| `task_geometry_unestablished` | absent | Record exact sample rate, frame/hop, FFT/mel geometry, PCEN params, channels, streaming/windowing contract. |
| `runtime_absent` | absent | Provide isolated hash-pinned runtime with complete lock and recorded platform. |
| `source_license_unverified` | absent | Add upstream code/asset licence and terms at resolved revision. |
| `rights_and_cohort_uncleared` | absent | Clear code/asset/data/label/output rights and freeze rights-cleared detection/keyword cohort. |
| `parity_and_quality_absent` | absent | Produce approved exact-reference output on frozen caller input plus analysis quality and independent timing evidence. |
| `provider_intake_not_started` | absent | Complete opt-in provider intake, descriptor/registry review, independent public-surface/release decision. |

Blocked gates (all `blocked`): `exact_source_and_asset_identity`,
`runtime_admission`, `artifact_rights_and_licence`, `exact_reference_parity`,
`analysis_cohort_and_scoring`, `task_scope_and_geometry`,
`opt_in_provider_intake`, `public_default_and_release`.

## Reproduction

```sh
cd docs/task-evidence/pcen-feature-frontend
python3 -m unittest -v test_reference.py
python3 run.py all
python3 run.py all --check
python3 verify.py
```

`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json`, and
`SOURCES.sha256`. `verify.py` is read-only/fail-closed, checks strict JSON,
pins, blockers/gates, boundary/scope, adverse controls, and requires 3
byte-identical cold-start regenerations.

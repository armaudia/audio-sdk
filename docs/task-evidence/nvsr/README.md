<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NVSR — NVSR blocker

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **feasibility and blocker package** for inventory
component `nvsr` (Restoration, verification profile `restoration`). The exact
licensed NVSR source, revision, inference weights, runtime, rights record,
paired band-limited/full-band cohort and parity vector are absent. It creates
**no new execution, model, corpus, real audio, provider, processor, ABI,
default, build, CI, board, handoff or release change**.

Task owner: `agent-NVSR`; reviewer: `reviewer-NVSR`. Claim base: audio-sdk
`0b0f2dee5902278fcea1a47f576b4df70e99ab3a`; branch `swarm/SDK-NVSR`. The task
depends on `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE` and `SDK-FND-PROVIDER`; write
scope is the task-local evidence directory only (`docs/task-evidence/nvsr/`).

## What is missing and why no result can qualify

Merged research evidence records candidate matrix row 32 (NVSR) as
`unavailable/blocked`: *"No local source checkout, checkpoint or adapter; no
local candidate accuracy/performance result."* The agent-denoise report cites
the Interspeech 2022 NVSR paper (Liu et al., "Neural Vocoder is All You Need
for Speech Super-resolution") and records an author project page and `ssr_eval`
code lead. The blocked re-audit and transform-spatial reports confirm no local
NVSR source, checkpoint, adapter, asset hash or BWE benchmark exists.

No fixed path in this workspace contains an NVSR checkout, resolved 40-hex
revision, checkpoint digest, model config, runtime environment, runtime lock,
licence grant, rights record, degradation manifest, paired cohort, clean
full-band reference or parity vector. Nothing is downloaded, vendored or
inferred from recorded URLs. Consequently:

- source identity, artifact hashes and licence terms cannot be pinned;
- NVSR task geometry (input/output rates, bandwidth, channels, duration,
  padding/crop, resampling) is **not established** by merged evidence;
- no NVSR output exists, so no high-band fidelity, content preservation,
  SI-SDR, STOI, WER, MOS, latency or RTF value is reported;
- missing evidence is never promoted to a pass, partial qualification or
  capability claim.

NVSR is a speech bandwidth-extension/super-resolution candidate in the
restoration family. Sibling ASR/transcription, classical low-pass/interpolation,
spectrum-copy, and other BWE model rows are not NVSR evidence.

## Evidence classes and boundaries

- **Merged research metadata:** candidate matrix row 32, agent-denoise report,
  transform-spatial report, matrix audit and blocked re-audit. Provenance only,
  not local execution.
- **Sibling maps/controls:** survey-rst-02/blocked-reaudit list NVSR as
  blocked; survey-rec-01 is recognition-only. Classical low-pass
  identity/interpolation and spectrum-copy controls are proxies, not NVSR.
- **Synthetic accounting:** deterministic synthetic PCM at 16 kHz input and a
  declared 48 kHz output surrogate with a declared 4 kHz cutoff. It checks
  nonfinite/invalid rejection, exact duration conservation, declared
  cutoff/bandwidth arithmetic and peak bounds. It performs **no interpolation,
  envelope extension, neural vocoding, generative reconstruction or model
  inference** and is never model output.
- **Not present:** real paired speech, frozen degradation trace, clean
  full-band reference, model checkpoint, runtime invocation, generated output,
  human listening, device timing, public benchmark or release approval.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `exact_source_and_asset_identity` | Full 40-hex revision, checkpoint/config/metadata hashes and source licence match exact pins | blocked |
| `runtime_admission` | Isolated hash-pinned runtime with a complete lock on a recorded platform | blocked |
| `artifact_rights_and_licence` | Weight, training-data, source-audio, clean-reference, output-use and redistribution rights cleared | blocked |
| `exact_reference_parity` | Approved exact-runtime output matches a frozen caller input and configuration | blocked |
| `restoration_cohort_and_scoring` | Rights-cleared held-out cohort scoring high-band fidelity, content preservation and listening separately | blocked |
| `task_scope_and_geometry` | Input/output rates, bandwidth, channels, duration and padding established without overclaiming | blocked |
| `opt_in_provider_intake` | Explicit opt-in intake, licence review, descriptor review and independent public-surface decision | blocked |
| `public_default_and_release` | Explicit default selection, resource/deadline evidence and release or benchmark approval | blocked |

The eight exact blockers in `report.json` name concrete absent artifacts/rights:
source checkout, upstream revision pin, inference weights/config, task geometry,
hash-pinned runtime, source licence, rights/cohort, and parity/benchmark
evidence. Restoration profile requirements are unsatisfied for qualification;
structural/synthetic controls have no qualification effect.

## Caller-supplied asset contract

`reference.py` validates a future caller-owned asset manifest without importing
or executing anything. It requires absolute paths and lowercase SHA-256 values
for checkpoint/config/licence/rights/runtime lock/cohort/degradation/parity; a
full 40-hex source revision; mono geometry; an admitted input/output rate pair;
and a positive cutoff leaving a missing input band below output Nyquist. Any
missing, malformed, nonfinite, out-of-range, mismatched or non-offline variant
is rejected before processing. No upstream revision is pinned by merged
evidence; a shape-valid manifest cannot manufacture qualification.

## Files and reproduction

- `reference.py` — strict JSON, stable linked-row identity, fixed-path asset
  audit, caller manifest validation, synthetic duration/bandwidth accounting
  and 27 adverse controls.
- `contract.json` — machine-readable `decision="DEFER"`, `incomplete`,
  proposal-only status, `qualification.status="not_qualified"`, eight blocked
  gates, eight exact blockers and caller asset contract.
- `report.json` + `report.json.sha256` — canonical report and digest.
- `SOURCES.sha256` — pins for read-only source documents, SDK contract files
  and package files. The mutable full `plan/swarm/TASKS.json` is **never
  hashed**; only stable linked-row fields are projected to a digest.
- `run.py` — byte-identical regeneration of report, contract and sources.
- `test_reference.py` — canonical output, identity, audit, manifest, PCM,
  bandwidth, duration and adverse-rejection tests.
- `verify.py` — strict JSON, exact pins, licensing, task-local git scope and
  three cold-start regeneration checks.

```sh
cd docs/task-evidence/nvsr
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
git diff --check
```

JSON, digest, manifest and contract files have SPDX `Apache-2.0` sidecars. All
files are inside this task directory; board, handoff and reviewers were not
changed or dispatched. No merge, formal approval or release action is taken.
Workspace pins are SHA-256 values of read-only documents; a pin grants no
rights and verifies no media. `SOURCE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.

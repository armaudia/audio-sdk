<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-ADDITIONAL-VM-ASR-AUDIO-SUPER-RESOLUTION — VM-ASR audio super-resolution blocker

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **feasibility and blocker package** for inventory
component `additional-vm-asr-audio-super-resolution` (Restoration, verification
profile `restoration`). The exact licensed VM-ASR source, revision, inference
weights, runtime, rights record, paired band-limited/full-band cohort and
parity vector are absent. It creates **no new execution, model, corpus, real
audio, provider, processor, ABI, default, build, CI, board, handoff or release
change**.

Task owner: `agent-ADDITIONAL-VM-ASR-AUDIO-SUPER-RESOLUTION`; reviewer:
`reviewer-ADDITIONAL-VM-ASR-AUDIO-SUPER-RESOLUTION`. Claim base: audio-sdk
`7dae8a27c07f9360e6243d226d44e3597ad8560f`; branch
`swarm/SDK-ADDITIONAL-VM-ASR-AUDIO-SUPER-RESOLUTION`. The task depends on
`SDK-FND-AUDIT`, `SDK-FND-EVIDENCE` and `SDK-FND-PROVIDER`; write scope is the
task-local evidence directory only.

## What is missing and why no result can qualify

The merged research evidence records only the author repository URL
`https://github.com/ghnmqdtg/vm-asr` and a source-reported lightweight
state-space audio-SR method measured by the authors on a single V100 research
setup. `research/voice-enhancement-20261101/candidate_matrix.csv` record 33
labels the candidate `unavailable/blocked` with the finding: *"No pinned
code/checkpoint/adapter for the author-reported model; no local output or
timing."* The blocked re-audit confirms that VM-ASR still lacks a
candidate-specific local model, code and decoder path.

No fixed path in this workspace contains a VM-ASR checkout, resolved 40-hex
revision, checkpoint, config, runtime environment, runtime lock, licence
grant, rights record, degradation manifest, paired cohort, clean high-band
reference or parity vector. Nothing is downloaded, vendored or inferred from
the repository URL. Consequently:

- source identity, artifact hashes and licence terms cannot be pinned;
- input/output sample rates, cutoff, channels, duration and padding geometry
  are `unestablished` and are **not** invented;
- no VM-ASR output exists, so no high-band fidelity, content preservation,
  SI-SDR, STOI, WER, MOS, latency or RTF value is reported;
- missing evidence is never promoted to a pass, partial qualification or
  capability claim.

The candidate name contains "VM-ASR", but the merged evidence classifies it as
bandwidth extension / audio super-resolution in the `RST-02` family. It is not
treated here as an ASR or transcription system; ASR results from the sibling
`survey-rec-01` map are not attributed to it.

## Evidence classes and boundaries

- **Merged research metadata:** candidate row 33, the two cited report paths,
  the blocked re-audit and the category source map. These are provenance, not
  local execution.
- **Sibling maps:** `survey-rst-02` records VM-ASR as blocked and supplies no
  VM-ASR output; `survey-rec-01` describes recognition only. Neither is used
  as a VM-ASR measurement.
- **Adjacent controls only:** the 12-clip spectrum-copy pilot is a classical
  BWE proxy and is not VM-ASR evidence. Vocos-BWE, NVSR, AudioSR and vocoder
  rows are separate candidates or baselines.
- **Synthetic accounting:** the task-local control generates deterministic
  synthetic PCM at 16 kHz input and a declared 32 kHz output surrogate with a
  declared 3.5 kHz cutoff. It checks nonfinite/invalid rejection, exact
  duration conservation, declared cutoff/bandwidth arithmetic and peak
  bounds. It performs **no** interpolation, envelope extension, generative
  reconstruction or model inference and is never model output.
- **Not present:** real paired speech, a frozen degradation trace, clean
  high-band reference, model checkpoint, runtime invocation, generated output,
  human listening, device timing, public benchmark or release approval.

The failure envelope is explicit: a declared missing band does not prove it
was restored; a synthetic duration ratio does not prove alignment or quality;
and the absent source/weights/runtime means neither parity nor product
suitability can be evaluated.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `exact_source_and_asset_identity` | Full 40-hex revision, checkpoint/config/metadata hashes and source licence match exact pins | blocked |
| `runtime_admission` | Isolated hash-pinned runtime with a complete lock on a recorded platform | blocked |
| `artifact_rights_and_licence` | Weight, training-data, source-audio, clean-reference, output-use and redistribution rights cleared | blocked |
| `exact_reference_parity` | Approved exact-runtime output matches a frozen caller input and configuration | blocked |
| `restoration_cohort_and_scoring` | Rights-cleared held-out cohort scoring high-band fidelity, content preservation and listening separately | blocked |
| `task_scope_and_geometry` | Input/output rates, cutoff, channels, duration and padding established without ASR misrepresentation | blocked |
| `opt_in_provider_intake` | Explicit opt-in intake, licence review, descriptor review and independent public-surface decision | blocked |
| `public_default_and_release` | Explicit default selection, resource/deadline evidence and release or benchmark approval | blocked |

The eight exact blockers in `report.json` name the concrete artifact or rights
requirement: absent source checkout, unpinned upstream revision, absent
weights/config, unestablished geometry, absent hash-pinned runtime, unverified
licence, uncleared rights/cohort, and absent parity/benchmark evidence. The
seven `restoration` profile requirements are all unsatisfied for qualification;
three are explicitly structural-only or synthetic-only, and none has a
qualification effect.

## Caller-supplied asset contract

`reference.py` validates a future caller-owned asset manifest without importing
or executing anything. It requires absolute paths and lowercase SHA-256 values
for the checkpoint, config, licence, rights record, runtime lock, cohort
manifest, degradation manifest and parity vector; a full 40-hex source
revision; mono geometry; an admitted input/output rate pair; and a positive
cutoff that leaves a missing input band below the output Nyquist. Any missing,
malformed, nonfinite, out-of-range, mismatched or non-offline variant is
rejected before processing. No upstream revision is pinned because the merged
evidence records only the repository URL; a shape-valid manifest cannot
manufacture qualification.

## Files and reproduction

- `reference.py` — strict JSON, stable linked-row identity, fixed-path asset
  audit, caller manifest validation, synthetic duration/bandwidth accounting
  and 27 adverse controls.
- `contract.json` — machine-readable `decision="DEFER"`, `incomplete`,
  proposal-only status, `qualification.status="not_qualified"`, eight blocked
  gates, eight exact blockers and the caller asset contract.
- `report.json` + `report.json.sha256` — canonical report and digest.
- `SOURCES.sha256` — pins for read-only source documents, SDK contract files
  and package files. The mutable full `plan/swarm/TASKS.json` is **never
  hashed**; only the stable linked-row fields are projected to a digest.
- `run.py` — byte-identical regeneration of report, contract and sources.
- `test_reference.py` — canonical output, identity, audit, manifest, PCM,
  bandwidth, duration and adverse-rejection tests.
- `verify.py` — strict JSON, exact pins, licensing, task-local git scope and
  three cold-start regeneration checks.

```sh
cd docs/task-evidence/additional-vm-asr-audio-super-resolution
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

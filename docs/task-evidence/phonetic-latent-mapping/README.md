<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-PHONETIC-LATENT-MAPPING — phonetic/latent mapping DEFER blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`phonetic-latent-mapping` (`SDK-PHONETIC-LATENT-MAPPING`). Structured inventory
assigns the **Voice** acceptance profile (`verification_profile: voice`).
Machine-readable decision: **`DEFER`**; `status=incomplete`; `proposal_only=true`;
`qualification.status=not_qualified`; `qualifies=false`. No result qualifies.

This package does **not** import, build, execute, download, benchmark, or
qualify any encoder, mapper, decoder, vocoder, checkpoint, or runtime. It pins
source-reported provenance, proves exact licensed source/weights/runtime are
absent, reproduces only declared synthetic frame/admission controls, and records
exact blockers. Only `docs/task-evidence/phonetic-latent-mapping/` is written;
no provider, descriptor, registry, default, installed-v0, ABI, shared-build, CI,
board, or handoff file changes.

## Exact blocker

Pinned research records describe phonetic/latent mapping as an underspecified
method family: `candidate_matrix.csv` record 49 marks it
`unavailable/blocked` with no frozen encoder-mapper-decoder, checkpoint, or
target identity; transform-space reports mark it researched/not run and state a
fair candidate must freeze content encoder, speaker/style mapper, decoder/vocoder,
target voice/accent, data, and training recipe. This is source-reported
provenance, not an admitted implementation, license review, measurement, or
qualification.

| Required artifact | Recorded local state |
| --- | --- |
| Frozen encoder-mapper-decoder/vocoder identity | No frozen system, target identity, or exact revision |
| Pinned checkpoints/configs/assets | No checkpoint, config, weight file, byte count, or SHA-256 |
| Pinned offline runtime/recipe | No runtime, lockfile, install proof, or deterministic recipe |
| Rights-cleared input/target/cohort | No consented input, target reference, cohort, or output-use decision |
| Deterministic converted outputs | No converted audio, semantic/identity/naturalness/timing measurement |
| Device timing/listening evidence | No target-device timing, memory, callback, listening, or labeled screen |
| Opt-in provider intake/release | No provider registration, default, intake, or release review |

## Scope and invariants

- Work confined to `docs/task-evidence/phonetic-latent-mapping/`.
- Installed v0 stays 16 kHz / mono / float32 / 160 samples. No provider is
  registered, exposed, or default-enabled.
- Deterministic, stdlib-only, default OFF, unregistered, not a provider.
- No real audio, listening, network download, target-device timing, benchmark,
  or release qualification. Every signal is synthetic.
- Missing, invalid, nonfinite, out-of-range, stale, unapproved, and
  missing-artifact cases fail closed. No missing result may qualify anything.
- Source-reported provenance, synthetic controls, and declared boundary are
  never pooled.

## Declared synthetic controls (not evidence)

`reference.py` provides deterministic synthetic frame validation/identity and
admission-manifest validation only. It is
`synthetic_contract_control_not_evidence` and does not run any mapping model.

Frame controls reject NaN/Inf/bool/string/None/short/long/empty/out-of-range/
nested/non-list with exact codes and `state_unchanged=true`.

## Voice profile outcomes (all blocked)

All Voice requirements are blocked: permitted input/target references;
task/language/speaker groups; text and semantic content; identity/similarity;
naturalness; alignment/first-output/tail timing; exact target condition; consent,
reference availability and output use.

## Release gates (all blocked)

RG-01 frozen method identity/source pin; RG-02 pinned checkpoints and offline
runtime; RG-03 rights/consent/cohort; RG-04 deterministic reference execution;
RG-05 voice semantic and identity quality; RG-06 alignment and timing; RG-07
target-device and listening evidence; RG-08 opt-in intake and release review.

## Reproduction

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

`run.py` regenerates `contract.json`, `report.json`, `report.json.sha256`, and
`SOURCES.sha256` three times and requires byte-identical output. The mutable
full `plan/swarm/TASKS.json` is never hashed; only the stable linked-row
projection is read and gated.

<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX License Identifier: Apache-2.0 -->

# SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING — task-local Evidence-profile blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`VADToolkit and AMI scoring tooling` (`component=vadtoolkit-and-ami-scoring-tooling`).
Acceptance profile: **Evidence** (`plan/swarm/VERIFICATION.md`). Decision:
**DEFER**, before `opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. No missing result qualifies the candidate.

Pinned base: `26bc48c58f9d69571571fa651862dcbe0fe1172d`.
Branch: `swarm/SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING`.
Linked-row stable SHA-256: `2b18653e9410c4422f5e477e5fe74c54c9d88a94452927da5edac192e35b152f`.

## Exact blockers

1. **Exact source/revision absent.** No exact VADToolkit/AMI scoring source checkout, immutable revision, command recipe, or artifact manifest is staged.
2. **Exact assets/labels absent.** No exact licensed audEERING VADToolkit audio/annotation package, AMI meeting audio/labels, scored-region manifest, or hashed reference artifact is present.
3. **Rights/publication uncleared.** No acquisition, local-evaluation, publication, redistribution, or derivative-output rights record is present.
4. **Reference parity absent.** No pinned reference scoring run, hashed outputs, or verified parity/tolerance record exists.
5. **Held-out scored cohort absent.** No rights-cleared held-out cohort with explicit scored regions and unknown-gap handling exists.
6. **Runtime execution absent.** No isolated pinned runtime/lockfile/deterministic execution trace exists.
7. **Adapter boundary incomplete.** No optional dev-evidence adapter is added; tooling is not exposed as a processor.
8. **Public default/release blocked.** No default, release, public benchmark, device timing, or listening approval exists.

## Asset audit

Fixed local path probes only; no network/download. The audit reports `absent` for
VADToolkit/AMI datasets/checkouts/runtime artifacts in expected workspace/worktree
locations. Any appearance must fail closed and trigger re-evaluation.

## Reference protocol

`reference.py` is stdlib-only and deterministic. It validates interval scoring
semantics on a **synthetic control case** only: scored regions, unknown gaps,
speech/hypothesis intervals, weak/advisory labels, and miss/FAR arithmetic.
Unknown samples outside scored regions are never counted as nonspeech. Weak labels
are reported separately and never qualify accuracy. 14 adverse controls are
actually invoked and all fail closed. No real audio, corpus, runtime, device,
or model is used.

## Eight blocked release gates

All gates are `blocked`: `exact_source_and_asset_identity`,
`rights_and_publication`, `matched_reference_parity`,
`analysis_cohort_and_scoring`, `weak_label_separation`,
`runtime_and_reproducibility`, `adapter_boundary_and_isolation`,
`public_default_and_release`.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`descriptor_settings={}`, `public_api_abi_change=false`,
`provider_registration=false`, `production_callback_registered=false`,
`processor_exposure=false`. No installed-v0/shared-build/CI/board/handoff change.
No adapter JSON is added; no tooling is exposed as a processor.

## Source-reported context

`research/plans/F02/vad_accuracy_contract.md` is pinned as context only. It
documents audEERING VADToolkit staging/coverage limits and AMI-related contract
constraints, but it is **source_reported_not_measured_here** and cannot qualify
this task. No local dataset/runtime/parity evidence is promoted.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py report.json
PYTHONDONTWRITEBYTECODE=1 python3 run.py sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git diff --check
```

`verify.py` runs three cold-start regenerations in a private temp directory and
requires byte-identical `report.json` and sidecar output.

## Non-claims

No VADToolkit/AMI source/runtime execution, no real audio/corpus, no download,
no accuracy/FAR/miss/onset/offset/latency/memory/RTF result, no device timing,
no listening, no public benchmark, no release claim, and no processor exposure.
Missing evidence never qualifies this candidate.

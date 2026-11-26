<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX License Identifier: Apache-2.0 -->

# SDK-VOICEBANK-DEMAND-VOICES-AND-DNS5-EVIDENCE — task-local Evidence-profile blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`VoiceBank+DEMAND, VOiCES and DNS5 evidence`
(`component=voicebank-demand-voices-and-dns5-evidence`). Acceptance profile:
**Evidence** (`plan/swarm/VERIFICATION.md`). Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. No missing result qualifies the candidate.

Pinned base: `26bc48c58f9d69571571fa651862dcbe0fe1172d`.
Branch: `swarm/SDK-VOICEBANK-DEMAND-VOICES-AND-DNS5-EVIDENCE`.
Linked-row stable SHA-256: `62d77ca56879fbdffc9ef10f459828771d9bd6843a9bf6cdd357f03683bd5271`.

## Exact blockers

1. **Exact assets/manifests absent.** No exact VoiceBank+DEMAND, VOiCES, or DNS5 archives, selected files, hashes, byte counts, or frozen cohort definitions are staged in this task worktree.
2. **Rights/publication scope unresolved.** No task-local per-track approval record covers SDK evidence reuse for all three tracks; DNS5/VOiCES/VoiceBank scope cannot be broadened silently.
3. **Track protocol unfrozen for SDK evidence.** Paired, real-room, and acquisition-only protocols, scorer identities, alignment/resampling rules, and non-pooling boundaries are not frozen as verified SDK-local artifacts.
4. **Pinned scorer/runtime absent.** No STOI/SI-SDR/DNSMOS/P.835/listening scorer implementation, lockfile, deterministic command, or verified output is staged.
5. **Held-out control execution absent.** No frozen cohort execution, control run, invalid/missing/nonfinite accounting, or independent verification exists.
6. **SDK adapter boundary not defined.** No optional dev-evidence adapter is added; no provider registration, descriptor, registry, processor exposure, or installed-v0 change.
7. **Target runtime/timing absent.** No paced target runtime/resource/deadline/availability evidence exists.
8. **Public default/release blocked.** No default-selection, release, public benchmark, listening, or qualification approval exists.

## Track separation

| Track | Role | Status | Boundary |
| --- | --- | --- | --- |
| VoiceBank+DEMAND | paired enhancement | blocked | Separate paired track only; no local audio/scores. |
| VOiCES | real-room robustness | blocked | Separate real-room track only; never pooled with paired-mixture scores. |
| DNS5 Track 2 dev | acquisition-only/non-intrusive | blocked | No clean paired references; non-intrusive/listening protocol must be pinned separately; never scored as paired evidence. |

## Asset audit

Fixed local path probes only; no network/download. Audit reports `absent` for
VoiceBank+DEMAND/VOiCES/DNS5 dataset/cache locations in expected
workspace/worktree paths. Any appearance must fail closed and trigger re-evaluation.

## Reference protocol

`reference.py` is stdlib-only and deterministic. It validates **synthetic
track-separation control only**: paired, real-room, and acquisition-only records
must remain separate, acquisition-only tracks cannot be scorable, and 14 adverse
controls are actually invoked and all fail closed. No real audio, corpus,
runtime, scorer, device, or model is used.

## Eight blocked release gates

All gates are `blocked`: `exact_source_and_asset_identity`,
`rights_and_publication_scope`, `track_separation_and_protocol`,
`scorer_runtime_and_reproducibility`, `cohort_controls_and_failure_accounting`,
`sdk_adapter_boundary_isolation`, `target_runtime_and_resource_timing`,
`public_default_and_release`.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`descriptor_settings={}`, `public_api_abi_change=false`,
`provider_registration=false`, `production_callback_registered=false`,
`processor_exposure=false`. No installed-v0/shared-build/CI/board/handoff change.
No adapter JSON added; no processor exposure.

## Source-reported context

`audio-benchmark-platform/audio-bench/docs/CORPUS.md` is pinned as context only.
It documents corpus policy/boundaries, but it is
**source_reported_not_measured_here** and cannot qualify this task. No local
dataset/runtime/scorer/parity evidence is promoted.

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

No VoiceBank+DEMAND/VOiCES/DNS5 audio/runtime/scorer execution, no real corpus,
no download, no quality/intelligibility/DNSMOS/MOS/WER/SI-SDR/STOI/PESQ/POLQA
result, no device timing, no listening, no public benchmark, no release claim,
no pooled ranking, and no processor exposure. Missing evidence never qualifies
this candidate.

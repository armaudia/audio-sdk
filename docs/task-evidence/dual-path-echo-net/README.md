<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-DUAL-PATH-ECHO-NET — unresolved dual-path family blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`dual-path-echo-net` (title "Dual-Path Echo Net"). Decision: **DEFER** before
any implementation or intake step; `status=proposal_only_incomplete`,
`qualification.status=not_qualified`. No result qualifies.

Task `SDK-DUAL-PATH-ECHO-NET`, component `dual-path-echo-net`, base commit
`42453ca5fbedc550a42276bbc94e76985b846544`, branch
`swarm/SDK-DUAL-PATH-ECHO-NET`.

The recorded label is an **unresolved family**, not one exact candidate. The
pinned matrix row 67 states: *"Name maps to distinct architectures; no exact
repository/checkpoint is selected, so no candidate-specific AEC evaluation is
possible."* The transform-space audit adds: *"No exact model by this name in
repo; no distinct checkpoint/adapter"* and *"Treat as unresolved name/family;
select one exact paper, source, checkpoint and input contract before claiming a
candidate."* The spatial-trials audit repeats that the label *"still maps to
multiple distinct architectures."*

This package does **not** contain, import, clone, build, link, download, load or
execute any dual-path model, paper implementation, checkpoint, runtime, audio
file or room impulse response. It records the exact pinned claims, proves the
fixed candidate paths are absent, implements the exact fail-closed family
resolver and Room-profile arithmetic that a future run would use, and records
one explicitly synthetic schema control that can never qualify. Only
`docs/task-evidence/dual-path-echo-net/` is written; no provider, registry,
descriptor, default, installed-v0, ABI, shared build, CI, board or handoff file
changes.

## Room profile scope

The inventory row and `plan/swarm/VERIFICATION.md` assign the **Room**
acceptance profile: freeze render/reference or measured RIRs,
channel/rate/hop, excitation, delay, movement, noise and reset schedule; include
echo-only, near-end-only, overlap and no-reference cases; report echo
attenuation, near-end damage, nonfinite failures and alignments including
delayed/missing render; and give a no-reference suppressor its own independent
comparison.

Only the synthetic half of that arithmetic exists here. Every candidate outcome
is **blocked**, because no exact model can be selected from the family, let
alone run.

## Exact external blocker: identity, source, weights, runtime, rights

1. **Family identity unresolved.** The label maps to distinct architectures;
   there is no canonical paper title, DOI, arXiv identifier, author list,
   repository or checkpoint ID for it. 0 exact-model matches.
2. **No selected source.** No source checkout, archive, 40-hex revision,
   LICENSE or NOTICE bundle. Because the family is unresolved, no source can be
   attributed.
3. **No selected weights.** No model ID, revision, byte count, SHA-256, model
   card or training-data statement. The pinned records say no distinct
   checkpoint or adapter exists locally.
4. **No runtime.** The fixed checkout/model/env/adapter/HF-cache probes are
   absent; there is no lockfile, wheel digest, import digest or deterministic
   thread trace.
5. **No rights-cleared room data.** No paired render/capture recording,
   measured RIR, consent, dataset terms, independent scorer, baseline or
   listening result. Existing AEC pilots belong to other candidates and are not
   reused.
6. **No qualification or intake.** No echo/near-end/double-talk/alignment
   result, no target timing, no no-reference comparison, no provider intake.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | One exact model selected from the dual-path family with paper title, DOI/arXiv citation, authors, official repository and checkpoint identity under independent provenance review. |
| `BLK-02` | Exact source revision and package/archive digest plus the complete code license and notice bundle with independent terms review. |
| `BLK-03` | Exact weight identity, revision, byte count and SHA-256, model card, training-data statement and reviewed weight terms. |
| `BLK-04` | A locked offline runtime with exact package hashes, install/import digests, one thread per pool, deterministic settings and clean-room offline load. |
| `BLK-05` | Rights-cleared paired render/capture audio or measured RIRs with geometry/delay/movement/noise/reset schedule, plus an independent pinned scorer and baseline. |
| `BLK-06` | Reproduced Room outcomes with controls, target-device timing/resources, a no-reference suppressor comparison and a separate OFF-by-default intake with independent exact-head review. |

**Reopen condition.** A caller selects one exact model from the family, supplies
the exact source/weights/runtime with complete terms, freezes a rights-cleared
paired-render/capture or measured-RIR cohort with an independent scorer, and
reproduces every Room case with controls and target timing. Until then this task
stays `DEFER` and all eight release gates stay `blocked`.

## Recorded claims: provenance only

| Field | Recorded value |
| --- | --- |
| Candidate label | Dual-Path Echo Net (only recorded string) |
| Recorded status | `unavailable/blocked` |
| Recorded finding | Name maps to distinct architectures; no exact repository/checkpoint is selected, so no candidate-specific AEC evaluation is possible |
| Baselines named | WebRTC AEC3; LocalVQE; SpeexDSP MDF |
| Related but distinct | DPCTNet; MSA-DPCRN; DeepAEC; Deep Echo Path Modeling |
| Cited source/revision | Not recorded |
| Weight identity/digest | Not recorded |
| Measured ERLE/near-end/alignment | Not recorded |
| Local runnable artifact | None |

The finding is only that the pinned records cannot identify one exact candidate
under this label. It is not an accuracy result, a timing result, a rights basis
or a product claim.

## What this package actually verifies

1. **Source/record presence and exact pins.** The candidate matrix, three
   research notes, the AEC note, inventory row/list, Room profile, SDK plan and
   merged AEC sibling reports are pinned by SHA-256. `recipe_provenance()`
   quote-checks the exact recorded sentences. This is provenance, not
   qualification.
2. **Absence evidence.** Fifteen fixed probes (eleven workspace, four external;
   no recursive walk) are checked. All are absent. `build_report()` and
   `verify.py` fail if any probe later appears, so a stale "absent" claim
   cannot ship.
3. **Family resolver.** Exact, case-sensitive match only: no fuzzy matching, no
   case folding and no alias merging. Fourteen probes (the exact label, eight
   near-name forms, four related names and the empty string) are all rejected.
   Even the exact recorded label returns
   `identity_family_unresolved_no_exact_model`, so a bare family name can never
   be promoted. Four related papers are recorded as distinct and
   `substitutable=false`.
4. **Exact integer Room arithmetic.** A frozen synthetic 16 kHz mono
   render/capture fixture with an authored **two-cluster** path (240-sample
   primary cluster of three taps, 560-sample secondary cluster of two taps) is
   scored with exact integer arithmetic: echo-only oracle ERLE `20709`
   millidB, near-end-only oracle SNR `23687` millidB, double-talk near-end SNR
   `23868` millidB with separate residual accounting, delay estimate `240`
   (correlation `932` millide) and delayed-render estimate `720` with 0 error.
   The all-zero render case is rejected with `no_render_reference`; no lag is
   guessed. These are oracle bounds on an authored fixture, not a candidate
   result. The synthetic oracle is **not Dual-Path Echo Net** output.
5. **Fail-closed admission.** A future caller-supplied room cohort manifest has
   a strict task-local schema. Sixty-four malformed, missing, invalid,
   nonfinite, out-of-range, duplicate, near-name, related-name, substitution,
   non-deterministic, online and qualification-claiming controls are rejected
   exactly. One placeholder-only structural control is admitted with
   `qualifies=false` to prove the validator is not blanket-rejecting.
   Admission never reads audio or weights.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, CI, the SDK README and eight merged AEC
   sibling reports are pinned by SHA-256 and verified unchanged.
7. **Stable board identity.** Only the projected
   `{id,title,component,mode,repository,depends_on}` row set is gated. The
   mutable full `plan/swarm/TASKS.json` is **never hashed**.

## Admission contract (task-local; not an SDK or candidate contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `identity`, `source`,
  `weights`, `runtime`, `render`, `capture`, `controls`, `outcomes`, `rights`.
  Unknown and missing fields are rejected.
- **Identity**: canonical name exactly `Dual-Path Echo Net`; a citation
  containing a DOI or arXiv identifier; paper title, HTTPS repository,
  checkpoint ID, review reference; `substitute_of` must be null. Any related
  paper name is rejected as `identity_substitution_attempt`.
- **Source**: 40-hex revision, 64-hex archive digest, license ID and review
  reference.
- **Weights**: model ID, 40-hex revision, 64-hex SHA-256, positive byte count,
  model card present, training-data statement present, license ID.
- **Runtime**: non-empty Python/framework/device fields, exactly one intra-op
  and one inter-op thread, deterministic algorithms on, offline on, lockfile
  digest.
- **Render/capture**: exactly one canonical absolute path each, 64-hex digest,
  16 kHz, mono, 1–960,000 samples, source and rights references, equal lengths.
- **Controls**: exactly one each of `echo_only_case`, `near_end_only_case`,
  `double_talk_case`, `no_render_reference_case`, `delayed_render_case`,
  `path_change_case`, `nonfinite_rejection_case`.
- **Outcomes**: bounded ERLE, near-end and double-talk preservation, primary and
  secondary path alignment errors, `nonfinite_output_count=0` and a positive
  sample count. These are admission bounds, not measured results.
- **Rights**: dataset/weights/output-use/review references and
  `claims_qualified=false`.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Recorded `unavailable/blocked` row 67 |
| `source:research/voice-enhancement-20261101/agent-transform-space/REPORT.md` | `479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4` | Family finding and DPCTNet/MSA-DPCRN distinction |
| `source:research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md` | `fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b` | Multiple-architecture recheck |
| `source:research/voice-enhancement-20261101/findings.md` | `78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c` | No-substitution finding |
| `source:research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` | AEC context and ERLE/preservation protocol |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `dual-path-echo-net` row, Room profile |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` | Blocked inventory listing |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Room profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | v0 contract |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` | Unchanged CI driver |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/aecmos/report.json` | `8055f6627d462c124182743469109a850087c11773899a6f64b02309be16c320` | Merged AEC-quality sibling boundary |
| `docs/task-evidence/webrtc-aec3/report.json` | `da1c2d7bc30fd8e2ae533110cd4130b623859a1747415312386044f41c8c2283` | Merged AEC3 sibling boundary |
| `docs/task-evidence/nlms-aec/report.json` | `2910e9e986259a9de738822c35a2908e47a836a9daabc292118f6c7389988f6a` | Merged NLMS sibling boundary |
| `docs/task-evidence/rls-aec/report.json` | `3fd2611c1b4619fab5858a78ee62920b66fd7acfb6aaac79b613dffd169e3b25` | Merged RLS sibling boundary |
| `docs/task-evidence/cagcrn-joint-aec-and-ns/report.json` | `697eb9feb470d529ba8132a8d597cb52308f46f5d2c6afd36803de268f9d7828` | Merged joint AEC/NS sibling boundary |
| `docs/task-evidence/localvqe-compact-echo-only/report.json` | `28b17d5ee0afa2f017009456ef58d0fbac6383bf64744682e7400079df862369` | Merged neural AEC sibling boundary |
| `docs/task-evidence/deepaec/report.json` | `4ebd1d208857aca5f042a68501f4938099afba637f5d2eb2b21e203149192661` | Merged DeepAEC sibling boundary (distinct candidate) |
| `docs/task-evidence/fixed-rls-to-nlms-aec/report.json` | `94cc863242f8b7b0320ae670cd24722ce197e6c588bfe8bb498bfa8ae0684fce` | Merged hybrid AEC sibling boundary |

Sibling numbers, manifests and conclusions are **never reused**. Those links
are whole-file boundary pins only.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Unresolved-family licensing boundary; no vendored terms or assets. |
| `contract.json` | Machine-readable contract: family identity, pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, family resolver, absence/pin/board checks, synthetic Room arithmetic, admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of report/contract/digest/SOURCES, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime, no audio). |
| `verify.py` | Read-only verifier: pins, canonical bytes, family identity, arithmetic, gates, licensing, scope, cold-start regeneration. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/dual-path-echo-net` with Python 3.12 (3.11 also
works) and stdlib only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` reports `rounds=3` with byte-identical output; all unittest
checks pass with 0 failed and 0 skipped; `verify.py` prints
`PASS ... cold_starts=3/3 byte_identical=true profile=room status=incomplete
decision=DEFER qualification=not_qualified`; `git diff --check` is clean.
`verify.py` writes only a temporary subprocess check and never this package.

Current counts: 15 absence probes (11 workspace + 4 external, 0 present),
7 required artifacts (1 provenance artifact present, 6 blocked), 6 open
blockers, 14 identity probes (14 rejected, 0 accepted), 64 rejected admission
controls, 1 placeholder-only admission control, 14 Room-profile rows (8
synthetic-only, 6 blocked), 3 synthetic Room cases, 2 synthetic path clusters,
3 delay scenarios, 8 blocked gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` exact model identity and citation | blocked | Select one exact dual-path model and resolve its paper, DOI/arXiv citation, repository and checkpoint identity with independent provenance review. |
| `RG-02` source revision and code license | blocked | Pin the exact source revision and package digest, stage the complete license/notice set and record independent review. |
| `RG-03` weights, model card and training terms | blocked | Supply the exact weight identity/revision/byte count/SHA-256, model card, training-data statement and reviewed weight terms. |
| `RG-04` pinned runtime and offline load | blocked | A locked offline runtime loads the exact packages and records deterministic imports, loads and repeats. |
| `RG-05` rights-cleared room corpus and scorer | blocked | Freeze rights-cleared paired render/capture or measured RIRs with geometry/delay/movement/noise/reset schedule plus an independent pinned scorer. |
| `RG-06` Room qualification with controls | blocked | Reproduce echo attenuation, near-end damage, double-talk, delayed/path-change/missing render, alignment and nonfinite behavior against a matched baseline. |
| `RG-07` target timing, resources and deadlines | blocked | Measure paced p50/p95/p99 latency, CPU/memory/energy, fill/flush and deadline behavior on the intended device. |
| `RG-08` provider intake and release | blocked | Open a separate versioned OFF-by-default intake with a clean install and independent exact-head review. |

No synthetic admission or arithmetic control opens a gate. No missing result is
promoted.

## Separation from other evidence

WebRTC AEC3, NLMS, RLS, LocalVQE, AECMOS, CAGCRN joint AEC/NS, DeepAEC and the
fixed RLS→NLMS hybrid are different candidates and tasks. Their reports are
pinned as boundaries only; no metric, checkpoint, manifest or conclusion is
pooled or reinterpreted as evidence for this label. DPCTNet, MSA-DPCRN, DeepAEC
and Deep Echo Path Modeling are recorded as distinct candidates that must not be
substituted.

## Non-claims

- No exact dual-path model source, weight, checkpoint, model card, runtime or
  numeric output is present, downloaded, loaded or executed.
- No candidate, PyTorch, ONNX, TensorFlow or other framework is imported.
- No render/capture audio, RIR, corpus, transcript or annotation is read.
- No ERLE, near-end, double-talk, alignment, finite-output or timing result
  exists; the synthetic arithmetic is an oracle bound on an authored fixture,
  **not** candidate output.
- No listening, device timing, benchmark, pipeline or release claim is made.
- No provider registration, public ABI, registry/default, shared build or CI
  change exists.
- The recorded label is an unresolved family; no nearby paper is treated as
  the same candidate.

## Expected digest

`report.json` SHA-256:
`2045e3d665928847392486a3893568d38390c133cbeba8e4332d350ed695cd8d`.

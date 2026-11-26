<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SOX-TEMPO — SoX tempo feasibility/readiness evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for `SoX tempo` (`component_id=sox-tempo`, `task=SDK-SOX-TEMPO`). The inventory assigns the **Rate** acceptance profile. Decision: **DEFER**; `qualification.status=not_qualified`; `readiness=incomplete`.

No exact SoX source revision/archive, runnable pinned runtime/binary, reviewed LGPL-2.1/GPL-2.0 license/notice bundle, or rights/distribution decision is staged in this worktree. No SoX/libsox code, binary, model, weight, or real audio was downloaded, built, copied, imported, linked, or executed. This package does **not** provide SoX tempo, does **not** register or expose a provider/processor, and does **not** change installed v0/public API/ABI/registry/defaults/shared build/CI.

## Catalogued evidence

- `cpp-library/pipeline-validation/playback-speed-candidates.md:250` — "### 3.11 SoX `tempo` (WSOLA reference)"
- `:252` source link `https://github.com/chirlu/sox/blob/master/src/tempo.c`
- `:253` WSOLA/quick-hierarchical-search/linear-search description
- `:254` **Licence:** effect file LGPL-2.1; `sox` binary GPL-2.0; use libsox under LGPL or reimplement
- `:255` parameters/profile table including speech 35ms segment scaling
- `:257` verdict: good reference; avoid linking `libsox` into a real-time callback

## Exact blocker

- Missing exact immutable SoX source revision/archive and complete reviewed license/copyright/notice bundle.
- Missing pinned offline deterministic runtime/binary/build recipe and rights/distribution decision for the selected LGPL/GPL path.
- Missing installed-geometry mapping proof for 16 kHz mono float32 160-sample frames (buffering/delay/flush/drain/source mapping).
- Missing Rate-profile matched evidence, real-corpus/listening, target-runtime timing/resources, and opt-in provider intake/public-surface decision.

Reopen only after exact artifacts/rights/runtime are staged and reviewed; then run deterministic offline reference checks, Rate-profile evidence with matched controls, and independent review before any opt-in unregistered adapter/provider exposure.

## What was checked

- Stable inventory/TASKS identity projection (no mutable full TASKS.json hash/gate).
- Bounded read-only source/runtime/artifact absence probes (no download/fabrication).
- Strict fail-closed request/JSON/reset validation.
- Synthetic harness controls only (silence/impulse/sine/DC); no candidate output, no real corpus, no timing/listening/release claim.

## Release gates

| Gate | Status | Reason | Reopen condition |
| --- | --- | --- | --- |
| RG-01 exact_source_revision_archive_and_license | blocked | No exact SoX source revision/archive is staged. The catalogued note identifies the tempo effect as LGPL-2.1 and the sox binary as GPL-2.0, but no reviewed immutable source bundle, complete license/copyright/notice set, or redistribution decision is present in this worktree. | Provide an exact immutable SoX source revision/archive with SHA-256, complete applicable license/copyright/notice files, and a reviewed build/distribution decision before any reproduction claim. |
| RG-02 pinned_runtime_offline_execution | blocked | No pinned runnable SoX tempo runtime/binary or deterministic offline execution recipe is present. No execution was attempted. | Provide a hash-pinned offline runtime or reviewed binary/build with exact command line, environment lock, and deterministic outputs; keep execution out of the realtime callback path. |
| RG-03 rights_and_redistribution_review | blocked | LGPL/GPL scope is identified but not reviewed for this task. No rights decision covers source, binaries, dependencies, outputs, or any future SDK integration/distribution path. | Complete rights review for selected source/runtime path, including LGPL-2.1/GPL-2.0 obligations, source-offer/relink requirements where applicable, and output/corpus rights. |
| RG-04 installed_geometry_and_adapter_mapping | blocked | Installed v0 requires 16 kHz mono float32 160-sample frames. No SoX tempo caller-supplied-asset/reference adapter mapping has been proven for this geometry, including buffering, delay, flush/drain, and source/output timestamp mapping. | Demonstrate a deterministic adapter mapping on the installed geometry with exact buffering/delay/drain semantics and fail-closed invalid-input behavior; keep it opt-in and unregistered. |
| RG-05 rate_profile_qualification | blocked | No SoX tempo output exists. Rate profile mapping, duration, pitch preservation, transient audibility, playback buffering, 1x/rate changes, unfamiliar speech/music, silence, rebuffer, drift, and final partial window are unmeasured. | Run the exact pinned reference on a frozen synthetic and rights-cleared cohort with the Rate acceptance profile and matched controls. |
| RG-06 real_corpus_and_listening | blocked | No real speech/music corpus, consent, or listening judgment exists. Synthetic controls are non-qualifying. | Provide rights-cleared real-corpus/listening evidence under an independent protocol; keep synthetic probes non-qualifying. |
| RG-07 target_runtime_timing_and_resources | blocked | No target-device pacing, callback suitability, CPU, memory, buffering, fill/flush, or end-to-end timing was measured. The catalogued note warns against linking libsox into a real-time callback. | Measure paced target runtime behavior separately if real-time exposure is ever proposed; offline evidence cannot close this gate. |
| RG-08 provider_intake_and_public_surface | blocked | No provider intake, descriptor registration, public surface, registry/default, or installed-v0 behavior decision exists. This package is task-local evidence only. | After prior gates clear, complete opt-in provider intake with OFF default, no ABI/registry/default/shared-build change without separate approval, and independent review. |

## Reproduction

From `docs/task-evidence/sox-tempo/`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse --root ../.. lint
git diff --check
```

Installed-package checks (from SDK root, after install/build as needed):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/ci.py
```

No missing result qualifies a candidate. Decision remains **DEFER**.

<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PAULSTRETCH — PaulStretch blocker evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for `PaulStretch` (`component_id=paulstretch`, `task=SDK-PAULSTRETCH`). The inventory assigns the **Rate** acceptance profile. Decision: **DEFER**; `qualification.status=not_qualified`; `readiness=incomplete`.

No exact licensed PaulStretch source revision, runtime/binary, reviewed GPL notice bundle, or rights decision is staged in this worktree. No PaulStretch code/binary was downloaded, built, copied, imported or executed. This package does **not** provide PaulStretch, does **not** register or expose a processor/provider, and does **not** change installed v0/public API/ABI/registry/defaults/shared build/CI.

## Exact blocker

- Catalogued evidence: `cpp-library/pipeline-validation/playback-speed-candidates.md` line 281 states PaulStretch is GPL, extreme offline stretching, not a real-time candidate.
- Missing artifact/rights requirement: exact source revision/archive with complete GPL-2.0-only/license/copyright/notice bundle and redistribution decision; pinned offline deterministic runtime/binary; rights-cleared frozen Rate-profile cohort and protocol; independent review before any exposure.
- Reopen: stage exact licensed artifacts/rights/runtime, reproduce approved outputs deterministically, then complete opt-in intake with OFF default and independent review.

## What was checked

- Stable inventory/TASKS identity projection (no mutable full TASKS.json hash/gate).
- Bounded read-only source/runtime absence probes (no download/fabrication).
- Strict fail-closed request/JSON/reset validation.
- Synthetic harness controls only; no candidate output, no real corpus, no timing/listening/release claim.

## Release gates

- `RG-01` `blocked` **exact_source_revision_archive_and_license**: No exact PaulStretch source revision/archive is staged. The catalogued note identifies PaulStretch as GPL/extreme offline, but no reviewed GPL-2.0-only source bundle, archive digest, complete notices or redistribution decision is present. Reopen: Provide an exact source revision/archive with SHA-256, complete license/copyright/notice bundle, and a reviewed redistribution/build decision before any reproduction claim.
- `RG-02` `blocked` **pinned_runtime_offline_execution**: No pinned PaulStretch runtime/binary or offline deterministic execution recipe is present. No execution was attempted. Reopen: Provide a hash-pinned offline runtime or reviewed binary with an exact command line, environment lock and deterministic outputs.
- `RG-03` `blocked` **rights_and_redistribution_review**: GPL/extreme-offline status is a blocker, not a release grant. No reviewed rights decision covers code, assets, outputs, or any SDK integration/distribution path. Reopen: Complete rights review for source, binaries, assets and outputs, including GPL-2.0-only obligations and any downstream use terms.
- `RG-04` `blocked` **rate_profile_qualification**: No PaulStretch output exists. Rate profile mapping, duration, pitch, transient, playback buffering, drift/rebuffer/final-window and pause/filler controls are unmeasured. Reopen: Run the exact pinned reference on a frozen synthetic and rights-cleared cohort with the Rate acceptance profile and matched controls.
- `RG-05` `blocked` **real_corpus_and_listening**: No real speech/music corpus, consent, or listening judgment exists. Extreme-stretch quality cannot be qualified by synthetic proxies. Reopen: Provide rights-cleared real-corpus/listening evidence under an independent protocol; keep synthetic probes non-qualifying.
- `RG-06` `blocked` **target_runtime_timing_and_resources**: No target-device pacing, callback suitability, CPU, memory, fill/flush or end-to-end timing was measured. PaulStretch is catalogued as extreme offline, not a real-time candidate. Reopen: If real-time exposure is ever proposed, measure paced target runtime behavior separately; offline extreme stretch remains non-real-time evidence only.
- `RG-07` `blocked` **provider_intake_and_public_surface**: No provider intake, descriptor registration, public surface, registry/default, or installed-v0 behavior decision exists. This package is task-local evidence only. Reopen: After prior gates clear, complete opt-in provider intake with an OFF default, versioned public surface decision and independent review.
- `RG-08` `blocked` **independent_review_and_release**: No independent exact-head review, benchmark/release approval, or qualified result exists. DEFER/incomplete/not_qualified is the only allowed decision. Reopen: Obtain independent exact-head review and release approval only after all required evidence, rights and runtime gates clear.

## Reproduction

From `docs/task-evidence/paulstretch/`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse --root ../.. lint
git diff --check
```

No missing result qualifies a candidate. Decision remains **DEFER**.

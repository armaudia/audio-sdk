<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SINUSOIDAL-SMS-TSM — Sinusoidal SMS TSM strict readiness evidence

**Status: `proposal_only_synthetic_incomplete`; qualification `incomplete`;
qualification status `not_qualified`; decision `DEFER` before any processor
exposure, default, registration or release claim.**

This package is a deterministic, task-local investigation handoff for the
`SDK-SINUSOIDAL-SMS-TSM` feasibility row. It is **not** an SMS or SBSMS
implementation, not a wrapped binary, not a vendored source, not an FFmpeg or
Rubber Band substitute, not a licensed runtime, not an installed SDK provider,
and not a listening, device-timing, benchmark or production qualification. No
public API/ABI, `CONTRACTS.md`, shared `CMakeLists.txt`, descriptor default or
registry, installed v0 behavior, board, handoff, ruleset, main branch or other
worktree was changed.

Pinned base: `f93d25f3d455a4278030d1bf0a3338dc6f8b95fe`. Branch:
`swarm/SDK-SINUSOIDAL-SMS-TSM`. All files live only under
`docs/task-evidence/sinusoidal-sms-tsm/`.

## What was checked

1. **Exact scope.** The branch diff against the newest available merge-base of
   `HEAD` with `origin/main` (falling back to `main`) is enumerated. Any tracked
   change outside this task directory fails closed as
   `base_out_of_scope_change`; if no base ref resolves, verification fails with
   `scope_base_unavailable`.
2. **Task-board and inventory identity.** Only stable identity fields of the
   `SDK-SINUSOIDAL-SMS-TSM` row and the `sinusoidal-sms-tsm` inventory record
   enter canonical bytes. Mutable status, owner, claim, review, handoff and
   history fields are excluded and never treated as evidence.
3. **Source and asset identity.** The pinned census at
   `cpp-library/pipeline-validation/playback-speed-candidates.md` records
   SBSMS/libsbsms as GPL-2.0, excluded, with **no local run**. The Serra/Smith
   SMS paper is a public method reference, not a staged runnable asset. No
   exact source revision, immutable byte count, SHA-256, locked runtime, rights
   grant or matched cohort is present. Bounded read-only probes confirm absence
   at declared workspace, SDK and home-cache paths; no download, import, load
   or audio read occurs.
4. **Installed geometry.** The contract accepts only 16 kHz, mono, float32 and
   160-sample frames. Integer-only mapping probes cover `1/1`, `5/4`, `4/5`,
   `3/2`, `3/4`, a final partial window and exact `1x` identity. These are
   labelled synthetic structural fixtures; they are not SMS parameters, not
   measured renderer output and cannot qualify the candidate.
5. **Caller-supplied boundary.** A metadata-only manifest is validated for
   adapter, configuration, source revision, digests, rights and format. Even a
   hash-matched local file fails closed as
   `SINUSOIDAL_SMS_SOURCE_IDENTITY_UNPINNED`: no source is read as code, loaded
   or executed, and no renderer is promoted.
6. **Rate profile.** Source/output mapping and duration are synthetic only.
   Pitch, transient audibility, playback buffering, unfamiliar speech, music,
   silence, rebuffer, pause/filler timestamp decisions and speech preservation
   are explicitly `blocked` because no exact source, runtime or cohort exists.
   There is no substitution from a source-reported description or an adjacent
   study.
7. **Adversarial controls.** All caller-manifest mutations, invalid JSON forms
   and invalid pin lines are rejected. Three cold-start SHA-256 builds of the
   canonical report are byte-identical.

## Decision and reopening

`DEFER` at `opt_in_adapter_exposure`: all eight gates `RG-01`…`RG-08` remain
`blocked` and `qualifies: false`. Exact external blockers:

- `XB-01` — exact runnable SMS/SBSMS source absent. Reopen with an exactly
  pinned runnable source or separately licensed artifact (revision, bytes,
  SHA-256 and reviewed rights record).
- `XB-02` — offline-first geometry and runtime unpinned. Reopen with the exact
  offline-first renderer and runtime, deterministic source/output and
  finalization on the installed grid, then a hash-matched caller asset.
- `XB-03` — matched rate cohort and scorers absent. Reopen with a frozen,
  rights-cleared cohort and pinned pitch, transient and speech-preservation
  scorers on the exact renderer.
- `XB-04` — release and timing gates unmet. Reopen with target-runtime paced
  availability, first-output/tail measurement, licence clearance and
  independent opt-in review with the default OFF.

This is an accepted investigation handoff. It does **not** close the conditional
implementation row. Missing, blocked, source-reported or synthetic results do
not qualify the candidate.

## Reproduce

From this directory, with pinned Python 3.12.16:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output build/ci
```

## Source pins (workspace-relative, `source:` prefix)

<!-- digest-table: source -->
| Path | SHA-256 |
| --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
<!-- digest-table: end -->

## SDK-worktree boundary pins

<!-- digest-table: boundary -->
| Path | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
| `docs/task-evidence/granular-tsm/README.md` | `d97f06911fd90667288fe571c7a3f4210ece629f7e839c1d41200ceec48ec0a0` |
| `docs/task-evidence/ffmpeg-atempo/README.md` | `11773a543c6dab54ff4754989501a0a70a29b247612e51aee5fb54c0050457b8` |
| `docs/task-evidence/soundtouch/README.md` | `951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550` |
<!-- digest-table: end -->

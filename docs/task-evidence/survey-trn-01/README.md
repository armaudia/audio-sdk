# SDK-SURVEY-TRN-01 — TRN-01 category evidence map

**Status `incomplete` · qualification `not_qualified` · decision `DEFER`.**
This package maps the original TRN-01 category — *Pitch-preserving speed /
time-scale modification* — to pinned inventory records, named source leads,
historical source reports and existing task-local synthetic evidence. It is a
read-only survey map. It is not a component, provider, harness, benchmark or
release result.

The task is `SDK-SURVEY-TRN-01` on the pinned board. Its acceptance asks for
matching of the original classic/ML method families, source leads and historical
executions to existing components, with a linked feasibility follow-up for each
actionable gap. Every gap in `report.json.gaps` points to an already-present
feasibility task on the board; no board, handoff or new task is written.

## Boundary

- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `descriptor_registry_change=false`,
  `shared_cmakelists_change=false`, `installed_v0_behavior_change=false`,
  `processor_exposure=false`, `ci_change=false`, `board_write=false`,
  `shared_repo_write=false`.
- Fixed installed v0 geometry is unchanged: 16 kHz, mono, float32, 160 samples
  per frame. No SDK callback is invoked. No source, build file, registry,
  default, CI file, board record or handoff outside this directory is changed.
- No real corpus, weights, runtime, audio, device timing, listening test,
  public benchmark or release claim is present. Source URLs are pinned text
  only and are never fetched. Historical numbers are labelled
  `source_reported_not_reproduced`; task-local numbers are labelled
  `task_local_synthetic_reference_only`.

## What is mapped

- **Category cross-check:** the TRN-01 fields in `plan/INVENTORY.json` and
  `research/category_registry.json` are compared field-by-field and must be
  identical before a report is built.
- **Classic families:** SOLA/WSOLA, overlap-add and phase vocoder. Named leads
  S32 (SoundTouch) and S33 (Rubber Band technical description) map to existing
  evaluated components with pinned source reports and pinned task-local
  synthetic evidence.
- **ML family:** disentangled analysis/resynthesis maps to the blocked or
  considered neural TSM components. No model, weight or runtime is loaded.
- **Integration lead S51:** variable sample-count integration maps to the
  Rubber Band streaming record, the whole-clip planner and the linked
  buffer-occupancy pacing follow-up.
- **Gaps:** WSOLA reference, phase-locking and transient-aware phase vocoder,
  six neural family records and continuous-stream pacing each link to an
  existing board task of `mode=feasibility`. The verifier rejects any gap whose
  link is missing, unknown or not a feasibility task.

All six release gates stay blocked: rights-cleared cohort, independent
listening, target pacing/variable-sample-count evidence, opt-in provider
intake, explicit public default selection and exact external reference parity.

## Pinned inputs and evidence

Paths beginning `source:` are relative to `SOURCE_ROOT`
(`/Users/htsakanyan/workspace/audio/audioml`, overridable by environment).
Other paths are relative to the SDK worktree root.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Category and component records. |
| `docs/task-evidence/survey-trn-01/board-snapshot.json` | `dcd077b07cf38071a0696eaf8d5312d8ea422aca4b9cbd67f0268fdf0baf3967` | Read-only extraction of 21 board records (survey task, mapped component tasks and feasibility links). Its source `audio-benchmark-platform/plan/swarm/TASKS.json` was `a48298d0e43690ae2de563e9d73c9122266056fe2f5d1f4b2f6c64f2a5f3a351` at extraction; the live board is intentionally never read during generation or verification because other agents write it concurrently. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile. |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` | Original families and S32/S33/S51 leads. |
| `source:audio_categories.md` | `97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905` | Published category row and distinctions. |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Historical stretch screen. |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Historical candidate roles. |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Reported streaming latency and integration caveats. |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Pinned offline comparator rows. |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Component-track and delivery boundary. |
| `CONTRACTS.md`, `REUSE.toml`, `api/include/audio_sdk/provider_v0.h`, `api/include/audio_sdk/session_v0.h` | see `SOURCES.sha256` | Unchanged SDK boundary and licensing coverage. |
| `docs/task-evidence/{soundtouch,rubber-band-r3-offline,rubber-band-r3-streaming,bungee-basic,psola-praat,sonic,phase-vocoder-baseline,ola-sola,granular-tsm,signalsmith-stretch}/README.md` | see `SOURCES.sha256` | Existing task-local synthetic evidence, never promoted to qualification. |

`SOURCES.sha256` enumerates every source, evidence, boundary and task-local
artifact pin. `verify.py` fails closed on a missing, stale, duplicated or
malformed pin, non-canonical JSON, duplicate/nonfinite JSON keys, stale digest
sidecar, an unlinked gap, an out-of-scope worktree change or a licensing gap.

## Files

- `board-snapshot.json` — pinned read-only extraction of the exact board records used for status and feasibility links.
- `contract.json` — task-local map manifest, scope, boundary and gates.
- `reference.py` — stdlib-only deterministic map builder and read-only validators.
- `run.py` — byte-identical regeneration of report, digest and source manifest.
- `report.json` / `report.json.sha256` — canonical map and its SHA-256.
- `SOURCES.sha256` — SHA-256 manifest for all pinned inputs and task files.
- `verify.py` — read-only strict verifier.
- `test_reference.py` — Python unittest acceptance suite.
- `*.json.license`, `SOURCES.sha256.license` — REUSE sidecars for generated artifacts.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
```

`run.py report.json`, `run.py sources` and `run.py all` are idempotent. The
canonical report digest is the content of `report.json.sha256`; the manifest
digest is the SHA-256 of `SOURCES.sha256` itself. Three fresh interpreter
processes producing the same canonical core hash are recorded in
`report.json.repeatability`.

## Disposition

The map is complete only as a survey of text evidence. It does not close any
component task, qualify a candidate, register a provider, change a default or
support a release. Missing evidence never qualifies a candidate: the outcome is
`incomplete` / `not_qualified` / `DEFER`.

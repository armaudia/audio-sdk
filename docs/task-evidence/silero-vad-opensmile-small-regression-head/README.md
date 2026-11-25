<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SILERO-VAD-OPENSMILE-SMALL-REGRESSION-HEAD — task-local Rate-profile evidence

Proposal-only, incomplete and **not qualified**. This is a deterministic
Python reference over synthetic signals and frozen caller-supplied surrogate
feature vectors. It is optional, unregistered and OFF by default. It does not
change the public API/ABI, installed v0 behavior, descriptor settings, provider
registry, defaults, shared build, CI, board or handoffs. No real Silero model,
openSMILE engine, media, device timing, listening result or release claim is
made.

Pinned base: `ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d`.
Branch: `swarm/SDK-SILERO-VAD-OPENSMILE-SMALL-REGRESSION-HEAD`.

## Boundary

- Documented v0 geometry only: 16 kHz, mono, float32, 160 samples/call.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `production_callback_registered=false`.
- No public variable-frame playback actuator is installed; evaluation fixtures
  and any future production callback path are distinct. No production callback
  is implemented or invoked.

## Rate-profile evidence

- **Exact source/output intervals**: half-open source ranges map through a
  single rational clock to integer output ranges. Constant rates `0.75×`, `1×`,
  `1.25×`, `1.5×`, a `1→1.25→0.75→1.5×` step schedule and a drift schedule are
  reported with exact fractional ends and duration errors. The final partial
  window is 3 samples of a 16,003-sample synthetic clip.
- **Pitch and transient proxies**: the pitch-changing linear control shifts the
  synthetic tone's crossing proxy away from 400 Hz at rates other than `1×`.
  An isolated impulse records an output peak-index proxy but `audibility =
  not_measured`. These are not intelligibility or naturalness results.
- **Coverage**: `1×`, rate changes, unfamiliar-speech surrogate, music surrogate,
  silence, rebuffer/drift schedules and the final partial window are recorded.
  Pause/filler decisions are anchored to source intervals; active speech stays
  at `1×` and is bit-exact in the synthetic fixture, with no pause deletion or
  invented filler. Playback buffering is a sample-queue simulation, not device
  timing.
- **Frozen caller-supplied features**: 95 synthetic surrogate vectors
  (88 eGeMAPS-like plus 7 VAD-summary-like) are pinned by SHA-256. No extractor,
  model, checkpoint, audio file or download is used. The head consumes only the
  frozen records and rejects missing, wrong-dimension, nonfinite, malformed and
  out-of-range inputs.
- **Standardized regression head controls**: training-dev-only feature
  standardization, an unpenalized intercept, an alpha grid with grouped
  development CV, an eGeMAPS-only ablation, a constant fold-mean baseline,
  a constant dev-mean held-out baseline and a permuted-target adverse control.
  The surrogate head loses to the constant dev-mean baseline on the held-out
  group; that regression is reported verbatim.
- **Adverse cases**: malformed config, frames, rates and feature records, stale
  clock values and closed/finished lifecycle states fail closed; unknown
  validity is never counted as nonspeech.
- **Repeatability**: three cold regenerations are byte-identical. Regressions
  are recorded verbatim; losing conditions are not hidden.

Historical `Silero + openSMILE eGeMAPS + ridge` values are included only as
source-reported provenance and are explicitly labeled
`source_reported_not_measured_here`. They never promote this candidate.

## Exact source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`; SDK-boundary
paths are pinned relative to this worktree. The full machine-readable set is
[`SOURCES.sha256`](SOURCES.sha256) and `contract.json`.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile. |
| `research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Task evidence and candidate scope. |
| `research/tsm-followup-20261101/root-baselines/REPORT.md` | `63ea22bd4d027467a1abe97639f7c9ff6e00cdc2c6c753a52c2bd5e4028bab85` | Source-reported head values, not measured here. |
| `CONTRACTS.md` (worktree) | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | v0 provider/session provenance. |
| `api/include/audio_sdk/provider_v0.h` (worktree) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged public boundary. |
| `api/include/audio_sdk/session_v0.h` (worktree) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged public boundary. |

## Files

- `reference.py` — synthetic signals, exact interval maps, frozen feature
  surrogate, standardized head, adverse cases and canonical report model.
- `run.py` — regenerates or checks `report.json` and its digest sidecar.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — fail-closed SHA-256 manifest for every package file and
  every pinned boundary/source file.
- `contract.json` — task contract, profile interpretation and pinned digests.
- `test_reference.py` — Python unittest acceptance suite.
- `verify.py` — read-only pins/JSON/reproduction/licensing/scope verifier.
- `check_licensing.py` — explicit SPDX tags plus repository REUSE coverage.

Canonical report SHA-256:
`208d81e915839a40a96033d657443691f62e4973930ef1543bea40f8793f946d`.
Sidecar SHA-256:
`e5c980ecf3912e62839f35f231f3acad612dfaebfa4d6076c8b202e5e6ebfb66`.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 check_licensing.py
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-SILERO-VAD-OPENSMILE-SMALL-REGRESSION-HEAD
```

`verify.py` runs three cold regenerations in a private scratch directory and
checks every report and source pin. When the package is copied out of the
worktree, set `SDK_ROOT` to the SDK checkout and `SOURCE_ROOT` to the common
workspace root so the fail-closed pins remain verifiable.

Repository-level checks from the SDK root:

```sh
reuse lint
python3.12 scripts/ci.py --output <private-scratch>/ci
git diff --check
```

## Remaining gates

All gates remain blocked pending caller-asset licensing, exact approved
reference parity, a rights-qualified unfamiliar speech/music cohort,
independent listening, target playback pacing, opt-in provider intake and
explicit default selection. Missing evidence never qualifies the candidate.
This task remains `proposal_only_synthetic_incomplete` / `not_qualified`.

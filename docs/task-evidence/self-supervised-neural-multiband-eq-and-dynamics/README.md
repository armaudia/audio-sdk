<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS — NDMP caller-supplied-asset boundary

Task-local, proposal-only, `incomplete`, `not_qualified` feasibility and evidence
package for `Self-supervised neural multiband EQ and dynamics`
(`component_id=self-supervised-neural-multiband-eq-and-dynamics`). The DSP
acceptance profile is defined in `plan/swarm/VERIFICATION.md` and assigned by
`plan/INVENTORY.json`. Base commit:
`a51e49f718500ec9e81242cf2816f0b576333d00`; branch:
`swarm/SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS`. Decision:
**DEFER** before `opt_in_adapter_exposure`; no missing, blocked or synthetic
result qualifies the candidate.

## What this package does and does not do

This package models a caller-supplied-asset reference for the DAFx-2025
Neural-Driven Multi-Band Processor (NDMP) at the installed **16 kHz**, mono,
`float32`, **160-sample** frame geometry. It validates caller metadata, byte
counts and SHA-256 values and then fails closed with
`NDMP_ASSET_IDENTITY_UNPINNED`. It never imports, builds, loads, executes or
downloads NDMP source, checkpoints or weights. No paper PDF, source tree,
checkpoint or audio bytes are vendored here.

All DSP content is **synthetic, deterministic and in-memory**: integer tone
sweeps, impulse, step, silence, a seeded harmonic/formant-like proxy and a
saturating cascade. These are **not real audio, not clean speech, not MUSDB18
and not NDMP output**. The identity control is bit-exact only for the synthetic
fixture; it is not a task-matched baseline or a listening result. There is no
six-band EQ/dynamics output attribution, no device timing, no benchmark and no
release claim.

The linked research (`research/level_tone_control_20261028.md`, line 24) names
the DAFx 2025 paper *Neural-Driven Multi-Band Processing for Automatic
Equalization and Style Transfer* by Parakrant Sarkar and Permagnus Lindborg.
The paper/archive report a six-band parametric EQ with per-band compression,
self-supervised training, MUSDB18 objective scores and a listening test. Those
are **source-reported** claims, not local outputs. The paper record and PDF link
were read for provenance only; no PDF, code or checkpoint bytes were
downloaded. MUSDB18 is a music-production corpus and is not a rights-cleared
task-matched speech cohort at the installed v0 geometry. The dynamics half is a
`CLN-09` boundary and is never pooled into a `CLN-10` tonal-correction claim.

## Exact readiness conclusion

`DEFER` / `incomplete` / `not_qualified`. Gates `RG-01` through `RG-08` are all
blocked and non-qualifying. The exact external blockers are:

- **XB-01** — no runnable NDMP source revision, immutable checkout, licence or
  deterministic offline build recipe is pinned or staged; the archive supplies
  only a paper record and PDF link.
- **XB-02** — no AutoEQ checkpoint path, revision, byte count or SHA-256, and no
  locked runtime or exact six-band analysis/hop/delay/finalization geometry is
  staged. Installed 16 kHz/1/160/float32 geometry does not establish NDMP's
  native geometry.
- **XB-03** — no rights-cleared task-matched clean/perturbed cohort, calibrated
  desired-response definition, held-out split, pinned scorer or listening
  protocol is staged; source-reported MUSDB18 results are out of scope.
- **XB-04** — no real DSP outcome, device timing, availability, listening,
  benchmark, opt-in intake or independent release review exists.

Reopening requires the exact licensed source/weights/runtime and geometry, a
rights-cleared matched cohort with pinned DSP controls and scorers, matched
outcomes on the exact runtime, and a separate opt-in intake reviewed at an
exact head with the default OFF.

## Stable board identity

Only stable row fields (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`) enter canonical bytes and gates. The full mutable
`plan/swarm/TASKS.json` is never hashed. Stable-row SHA-256:
`5a2ce264fd3ab23c408b111a2d58ceb1f45449bede0b9e5af01a4599764352a3`.

## Source pins (SHA-256)

`source:` paths are workspace-relative. Every row is checked by `verify.py`.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio_categories.md` | `97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905` |
| `source:reports/level-tone/20261028-synthetic-evaluation.json` | `1054a0b6d22dac695e17dfa84ab21f9f2a1677838285fb746834010424b91c34` |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` |
| `source:research/category_survey/sources.md` | `9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d` |
| `source:research/level_tone_control_20261028.md` | `b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

Paths are SDK-worktree-relative. All are unchanged and machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `docs/task-evidence/differentiable-biquad-neural-parametric-eq/README.md` | `3d1959a7a925b6c432460068b3e28af2ff5b91ce6e4b08ea488f488d0e5ae470` |
| `docs/task-evidence/differentiable-biquad-neural-parametric-eq/report.json` | `fd02a76b9a5d2fdef3df69c4603f8dfe96dcde800a20f163abc18d10bce6557b` |
| `docs/task-evidence/fixed-six-band-spectral-tilt/README.md` | `70b2edcd154821445a5ff24f430b19fc42dac3cec8273a9baae896e3245f56de` |
| `docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json` | `2673433a9db9ac348d3624b73a739196815374ccb68aa4427aee53b94702826c` |
| `docs/task-evidence/learned-inverse-eq/README.md` | `719910254b5399b79e20208cff40ff6920fe12b77813731b70c0c6abd833b20e` |
| `docs/task-evidence/learned-inverse-eq/report.json` | `2ee8271a3b08c989fe037f2753d013b8e6dcafb6881e5b0e59bb6724eff9e0dc` |
| `docs/task-evidence/survey-cln-10/README.md` | `f63847915ab78d50bccd73bdcffdcbf625faef2b6312024e8ede21bb2635a787` |
| `docs/task-evidence/survey-cln-10/report.json` | `90c1b2472e8547d3ff78d67d6d0db60b912be5befd6ef4fa4e289cf406642bd5` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/ndmp-autoeq/caller-supplied/0.1` is metadata-only. Required fields
are `adapter`, `configuration_id`, `paper_record_id`, `source_revision`,
`checkpoint_path`, `checkpoint_sha256`, `checkpoint_byte_count`,
`checkpoint_revision`, `runtime_lock_digest`, `sample_rate_hz`, `channels`,
`frame_samples`, `sample_format`, `band_count`, `eq_stage`, `dynamics_stage`,
`control_scope`, `native_delay_samples` and `max_drain_calls`. The validator
requires the pinned paper record, installed 16 kHz mono float32 160-sample
format, six-band static PEQ/per-band-compressor structure, absolute paths and
hash-matched checkpoint bytes. Even a hash-matched caller asset still ends in
`NDMP_ASSET_IDENTITY_UNPINNED`; no asset is loaded or run.

## Scope gate

`verify.py` resolves the newest merge-base of `HEAD` with `origin/main`, falling
back to `main` only when `origin/main` is unavailable. If no base exists it
emits `scope_base_unavailable`. Any tracked branch difference outside
`docs/task-evidence/self-supervised-neural-multiband-eq-and-dynamics/` emits
`base_out_of_scope_change` and fails closed. Three regression tests cover
newest-base selection, `main` fallback and out-of-scope/missing-base rejection.

## Reproduce

All commands are read-only except for the canonical artifacts in this directory
and the temporary CI output under `build/ci`.

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS/docs/task-evidence/self-supervised-neural-multiband-eq-and-dynamics
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
cd ../..
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output build/ci
```

Canonical JSON uses sorted keys, compact separators, `allow_nan=False` and one
trailing LF. Three fresh builds are byte-identical; comparison is exact
SHA-256 with no tolerance. `report.json.sha256` is the canonical sidecar and
`SOURCES.sha256` pins source, boundary and local artifact bytes.

## Licensing

The DAFx paper is a source-reported publication; its copyright statement does
not clear source code, checkpoints, MUSDB18 audio, listening outputs or product
use. No source, weights, audio or PDF bytes are redistributed here. All package
files are Apache-2.0 via SPDX headers and the repository `REUSE.toml`
annotation for `docs/**`.

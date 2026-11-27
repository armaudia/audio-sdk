<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WAVLM-LARGE-IN-TOKAN — WavLM-Large in TokAN (research-control, DEFER)

Task-local, proposal-only, `incomplete`, `not_qualified` evidence for
**WavLM-Large in TokAN** (`component_id=wavlm-large-in-tokan`, Voice profile,
`research-control`). Base commit: `b50134a300d1daf9cafdded23aa2e511d1cefda9`;
branch: `swarm/SDK-WAVLM-LARGE-IN-TOKAN`. Decision: **DEFER**. No missing,
blocked, invalid, or synthetic result qualifies.

## Exact scope

This package records the research-control comparison boundary: WavLM-Large as
used inside TokAN may be retained/reproduced only as an optional SDK
developer/evidence adapter after all gates clear. It does **not** expose a
processor, register a provider, change defaults, public API/ABI, CONTRACTS,
registry, shared build, or CI. No model/source/checkpoint/runtime/audio is
downloaded, vendored, loaded, imported, or executed. No listening, device
timing, benchmark, or release claim is made.

## Pinned source context (context only; not qualifying)

TokAN source is pinned at `cbfc09a2716003463a0501ceae04ee62809c3822`
(`https://github.com/P1ping/TokAN.git`). The pinned extractor uses
`microsoft/wavlm-large`, layer 22, 16 kHz. The historical accent-conversion
README reports CPU full-pipeline smoke runs (RTF 17.38–20.56, no MPS) with
compatibility pins; these are source-reported context only and are **not**
WavLM-Large encoder isolation, Voice-profile quality, device timing, or SDK
qualification evidence.

## Exact blockers / release gates

| Gate | Status | Qualifies | Reopen condition |
|---|---:|:---:|---|
| RG-01 Exact source/license provenance | blocked | no | Pin immutable TokAN source/license artifacts and reviewed redistribution/product-use clearance. |
| RG-02 Exact WavLM-Large checkpoint identity | blocked | no | Stage exact WavLM-Large assets with byte counts, SHA-256, revision, reviewed terms. |
| RG-03 Pinned runtime and offline reproduction | blocked | no | Provide locked offline deterministic runtime/reproduction logs for the exact encoder path. |
| RG-04 Rights-cleared Voice cohort and labels | blocked | no | Stage reviewed cohort manifest with consent, reference availability, output use, task labels. |
| RG-05 Isolated encoder latency and feature parity | blocked | no | Measure encoder-only latency/memory and parity against pinned TokAN feature contract. |
| RG-06 Voice profile controls and preservation | blocked | no | Run frozen Voice-profile evaluation with controls and separate outcome reporting. |
| RG-07 Target-device timing and availability | blocked | no | Collect paced on-target timing/resources with explicit clock domain and deadline budget. |
| RG-08 Opt-in SDK intake and release | blocked | no | Pass separate opt-in intake with exact-head independent review; keep default OFF. |

## Voice profile (blocked)

Required items are frozen input/reference cohort; content/semantic preservation;
identity/similarity/naturalness as separate outcomes; alignment/first-output/tail
timing; consent/reference availability/output use; and isolated WavLM-Large
encoder latency/feature parity. All are blocked/not satisfied.

## Stable board identity

Only stable row fields (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`) are hashed/gated. Mutable TASKS.json fields are excluded and the
full mutable board file is never pinned.

## Source pins (SHA-256)

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/accent-conversion-20261101/README.md` | `c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c` |
| `source:research/accent-conversion-20261101/repos/TokAN/README.md` | `e1686415f5cb77ed570f0284322fa67883663d52bed081c0f1287fff42fb2700` |
| `source:research/accent-conversion-20261101/repos/TokAN/configs/tokan.model-only.yaml` | `63280ebc0d0ad68730e780a11cca927e0890e2164ba966424caf9a4580fc8f45` |
| `source:research/accent-conversion-20261101/repos/TokAN/infer_wav.py` | `85ccde2fca4e2d8dc34c686c5a9c4ee2a80fa666e1e8d5c7a9b50c6b4fd82bd5` |
| `source:research/accent-conversion-20261101/repos/TokAN/requirements.txt` | `31baee3dc62a6a5b68130b158a9ff3ec0702203cce9f753dc3febd822cf95c7f` |
| `source:research/accent-conversion-20261101/repos/TokAN/tokan/model/ssl_quant/vq_joint.py` | `504097caf3fdad4911fa5e6643af853072959935bd3430335d21becc789d6a13` |
| `source:research/accent-conversion-20261101/repos/TokAN/tokan/model/ssl_wrapper/wavlm_extractor.py` | `e11d07fb6269834443ee33ecdc21dba0357d1e748ffe99f2a6f7033027cb34e4` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

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
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Scope gate

`verify.py` resolves the newest merge-base of `HEAD` with `origin/main`, falling
back to `main` only when `origin/main` is unavailable. If no base exists it
emits `scope_base_unavailable`. Any tracked branch difference outside
`docs/task-evidence/wavlm-large-in-tokan/` emits `base_out_of_scope_change` and
fails closed. Three regression tests cover newest-base selection, `main`
fallback, and out-of-scope/missing-base rejection.

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v docs/task-evidence/wavlm-large-in-tokan/test_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 docs/task-evidence/wavlm-large-in-tokan/run.py --all
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 docs/task-evidence/wavlm-large-in-tokan/run.py --check
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 docs/task-evidence/wavlm-large-in-tokan/verify.py
python3 -m reuse lint
git diff --check
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py
```

Canonical JSON: sorted keys, compact separators, `allow_nan=False`, one trailing
LF. `report.json.sha256` is `sha256  report.json`. `SOURCES.sha256` pins source,
boundary, and local artifact bytes.

## Licensing / non-claims

No upstream TokAN/WavLM weights, audio, or runtime bytes are redistributed.
TokAN upstream has no visible license file in the pinned checkout; rights remain
unreviewed and blocked. This package is Apache-2.0 via SPDX headers/sidecars.

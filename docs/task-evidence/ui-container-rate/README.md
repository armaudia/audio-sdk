<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-UI-CONTAINER-RATE — task-local feasibility evidence

Task-local, proposal-only, **incomplete** and **not_qualified** feasibility
evidence for `UI / container rate` (`component_id=ui-container-rate`). The
assigned acceptance profile is **Rate**. Machine-readable decision: **DEFER**;
`status=proposal_only_blocked_incomplete_not_qualified`;
`evidence_status=incomplete`; `qualification.status=not_qualified`. No result
in this package qualifies the candidate.

This package does **not** download, copy, import, load, execute, or vendor any
UI, container, browser, player, host runtime, corpus, or audio asset. It does
not read, write, render, or play real audio; does not measure a device clock,
callback deadline, FIFO occupancy, pitch, transient audibility, or listener
preference; does not benchmark the SDK; and makes no release claim.

## Candidate boundary

The pinned playback-speed candidate note records "UI / container rate" as a
factor provider: factor directly, n/a license, always available, no estimation
error (`cpp-library/pipeline-validation/playback-speed-candidates.md:87`). That
row is source-reported provenance only. It is not an implementation, not a host
contract, not a timing result, and not qualification evidence.

Installed v0 geometry remains documented only: `16000 Hz`, 1 channel, `float32`,
160 samples per call. No provider, descriptor, registry entry, default, ABI,
CONTRACTS, shared-build, or CI file is changed.

## Decision, gates, blockers

All gates RG-01 through RG-08 are **blocked** and `qualifies=false`: exact
host/API contract, rights/license review, typed source-timestamped rate-control
contract, exact source-timestamp mapping, matched rate evidence, failure/control
evidence, target-runtime timing, and OFF-by-default opt-in intake. `DEFER` is
before `opt_in_adapter_exposure`.

Exact blockers B-01..B-04 and reopening conditions are in `report.json` and
`contract.json`. Missing evidence never qualifies the candidate.

## Synthetic boundary surrogate

The deterministic stdlib-only surrogate exercises rate-factor and
source-timestamp arithmetic on typed speech/music/silence segments. It is
explicitly `surrogate=true`, `candidate_is_ui_container_rate=false`,
`qualified=false`. It is not a UI, not a container, not a player, not a
browser, not a device clock, and not a rate claim.

## Caller-supplied asset contract (not satisfied)

Any future candidate artifact must be caller-owned and validated by exact id,
absolute path, byte count, SHA-256, reviewed license/notice, and geometry.
The shape-only verifier rejects duplicate keys, field-set drift, missing/empty
identifiers, bad digests, relative/traversal paths, duplicate paths, missing
bytes, byte-count mismatch, hash mismatch, and non-permissive/GPL license ids.
A hash-matched placeholder is still shape-only and never qualifies. No such
assets are present.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-UI-CONTAINER-RATE diff --check
```

`verify.py` is read-only and fail-closed on duplicate-key/nonfinite JSON, stale
pins, stale canonical artifacts, stale README digest tables, unexpected files,
license gaps, SPDX-token violations, scope changes outside this task prefix, and
whitespace damage.

Board link pins only stable row identity (`component`, `depends_on`, `id`,
`mode`, `repository`, `title`), never the mutable full `plan/swarm/TASKS.json`.

Base commit: `70695fd3abc5b60c88ba8bdd86e970f4760c4dae`.
Task ID: `SDK-UI-CONTAINER-RATE`.

<!-- digest-table: source -->
| Pin key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
<!-- digest-table: end -->

<!-- digest-table: boundary -->
| Pin key | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `schemas/descriptor.schema.json` | `9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba` |
| `schemas/effective-config.schema.json` | `55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

<!-- digest-table: artifacts -->
| Pin key | SHA-256 |
| --- | --- |
| `docs/task-evidence/ui-container-rate/README.md` | `20faf5740774b73c85b0a9646559e5acf019fc233037d6e7698b0e7e1dd34d10` |
| `docs/task-evidence/ui-container-rate/SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/ui-container-rate/contract.json` | `920bd6951b2434765824219009e329df5bc57557a619110424030e996b18f8ee` |
| `docs/task-evidence/ui-container-rate/contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/ui-container-rate/reference.py` | `e01f78d5b29742a8e2afd23fe74302bbe9afa1060a399ace7f66f3144015c0fd` |
| `docs/task-evidence/ui-container-rate/report.json` | `6bb15496a15c733e195f01ffd3b9a63e8536a6c7b690b3aba89a918d676d07de` |
| `docs/task-evidence/ui-container-rate/report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/ui-container-rate/report.json.sha256` | `5d9658e1b9a30c6ffa57d3af41d33a0fe004042d1f5d5bb12c4ee2a1330260ef` |
| `docs/task-evidence/ui-container-rate/report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/ui-container-rate/run.py` | `80a0574d5c164f15b782e4f38d9dd1743cdee76b1277c0e46cce0cd4d7007923` |
| `docs/task-evidence/ui-container-rate/test_reference.py` | `1bbacc217878f042ca2717e2af7c3c0eda452751bbb64fdbfb7eac89f4211e95` |
| `docs/task-evidence/ui-container-rate/verify.py` | `6e7e36a89ad70cb25c34b858376658d1dd05b99bcfd95b544369cd2c897c67aa` |
<!-- digest-table: end -->

<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WHISPER-TINY-EN-INT8-VIA-SHERPA-ONNX — research-control evidence (DEFER)

Task: `SDK-WHISPER-TINY-EN-INT8-VIA-SHERPA-ONNX`
Component: `whisper-tiny-en-int8-via-sherpa-onnx`
Profile: `Evidence` (`verification_profile=evidence`)
Decision: **DEFER**
Status: **incomplete**
Qualification: **not_qualified**
Proposal only: **true**

## Scope

This package is a deterministic, task-local research-control evidence bundle.
It records a conservative blocker outcome for using Whisper tiny.en int8 via
sherpa-onnx as an offline transcript-drift scorer scoped to prototype clips. It
does **not** implement, register, enable, download, load, or run any model,
runtime, adapter, provider, benchmark, listening test, or device-timing claim.

Write scope: `docs/task-evidence/whisper-tiny-en-int8-via-sherpa-onnx/` only.

## Evidence profile application

Per `plan/swarm/VERIFICATION.md` Evidence profile, this package pins scorer/corpus/cohort
identity as absent/unreviewed, preserves separation between paired/unpaired/synthetic/human/source-reported
evidence, and includes deterministic invalid/missing schema controls through the
reported bundle. No qualifying result is produced.

## Source/provenance pins

- `cpp-library/pipeline-validation/playback-speed/README.md` (source-reported
  prototype context only; no rerun, no qualification).
- Local scratch model files under
  `cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/`
  are probed by hash/size for provenance only. They are **not vendored**, **not
  admitted**, and **not** evidence of rights/runtime qualification.

## Exact blockers (all open)

| ID | Blocker | Status |
|---|---|---|
| B1 | Exact sherpa-onnx source revision/archive digest/complete Apache-2.0 license+NOTICE+third-party review unpinned | open |
| B2 | Model/tokenizer identity, conversion provenance, model/output-use/distribution terms unreviewed | open |
| B3 | Pinned offline runtime/package lock and deterministic clean-room load/import proof absent | open |
| B4 | Rights-cleared task-matched audio/transcript cohort, frozen normalization/scorer, invalid/missing controls absent | open |
| B5 | No reproduced transcript-drift run, target-device timing/resources, listening, or benchmark/release evidence | open |
| B6 | No separate opt-in OFF-by-default adapter/provider intake or independent exact-head review | open |

## Release gates (all blocked)

| Gate | Status |
|---|---|
| RG-01 source revision and license | blocked |
| RG-02 model asset identity and terms | blocked |
| RG-03 pinned offline runtime | blocked |
| RG-04 rights-cleared eval cohort | blocked |
| RG-05 reproduced scoring with controls | blocked |
| RG-06 target timing and resources | blocked |
| RG-07 listening/human review if claimed | blocked |
| RG-08 opt-in intake and exact-head review | blocked |

## Admission/control policy

`reference.py` defines deterministic synthetic admission cases. Valid-shaped
manifests are accepted for schema/control only and never qualify. Missing model
digest, unreviewed license, unreviewed rights, missing invalid control, and bad
digest shape are rejected fail-closed. A synthetic WER arithmetic control is
included and explicitly `qualifies=false`.

## Scope enforcement

The strict verifier enforces newest-merge-base branch-diff scope against
`origin/main`, falling back to `main`. If no base is available it fails closed
with `scope_base_unavailable`. Any out-of-scope branch diff path fails with
`base_out_of_scope_change`. Working-tree out-of-scope paths also fail.

## Reproduce

From this package directory:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 run.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 test_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 verify.py
```

From SDK worktree root (after installing required tools as project expects):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -m scripts.ci --skip-build --skip-test
python3 -m reuse lint
git diff --check
```

## Non-claims

- No ASR/model/runtime executed.
- No model weights/runtime vendored or downloaded.
- No real audio, listening, device timing, benchmark, or release claim.
- No provider/adapter registered or enabled by default.
- No ABI/CONTRACTS/registry/shared build/CI/default change.

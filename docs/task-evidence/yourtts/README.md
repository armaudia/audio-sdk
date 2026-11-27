<!--
SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0
-->

# SDK-YOURTTS — YourTTS blocker evidence

> Decision: **DEFER**. Status: **incomplete**. Qualification: **not_qualified**.  
> Profile: **Voice**. Proposal-only, task-local, deterministic, fail-closed.

## Why DEFER

YourTTS is a voice/speech-to-speech conversion feasibility row. This package
records blocker evidence only: no exact reviewed YourTTS source revision,
checkpoint/weights, pinned offline runtime, rights/terms review, rights-cleared
voice cohort with consent/reference/output-use records, or approved matched
reference/protocol is present in this workspace. Missing evidence never
qualifies.

Pinned context (not matched evidence): inventory marks YourTTS as
`unavailable/blocked`; candidate matrix row 46 reports no local checkpoint,
source checkout, or speech-conversion adapter; accent-conversion research marks
YourTTS/VITS streaming adaptations as not run and generic speech synthesis/voice
cloning rather than an official sub-100 ms streaming audio-to-audio accent
conversion checkpoint.

## Scope / non-claims

- No model/source/weights/runtime/audio/corpus downloaded, loaded, executed,
  vendored, or redistributed.
- No listening, device timing, benchmark, quality, identity, naturalness,
  latency, or release claim.
- No provider registration, descriptor/registry/default, installed v0/ABI,
  shared build, CI, board, or handoff change.
- Task-local only: `docs/task-evidence/yourtts/`.

## Voice profile (all blocked)

| ID | Requirement | Status |
| --- | --- | --- |
| VP-01 | Freeze permitted input and target references, task and language/speaker groups. | blocked |
| VP-02 | Preserve text and semantic content, identity/similarity and naturalness as separate outcomes. | blocked |
| VP-03 | Record alignment, first-output/tail timing and the exact target condition. | blocked |
| VP-04 | Consent, reference availability and output use are independent gates. | blocked |

## Release gates (8 blocked)

| Gate | Title | Status |
| --- | --- | --- |
| RG-01 | Source revision and license provenance | blocked |
| RG-02 | Checkpoint identity and geometry | blocked |
| RG-03 | Rights and output terms | blocked |
| RG-04 | Pinned runtime and deterministic load | blocked |
| RG-05 | Consent, reference availability and output use | blocked |
| RG-06 | Frozen voice cohort and separated outcomes | blocked |
| RG-07 | Alignment and timing evidence | blocked |
| RG-08 | Independent review and release boundary | blocked |

## Exact blockers (6 open)

| Blocker | Status | Summary |
| --- | --- | --- |
| BLK-01 | open | No exact reviewed YourTTS source/revision/LICENSE/NOTICE/archive digest. |
| BLK-02 | open | No exact checkpoint/weights with filename, byte count, SHA-256, format, geometry. |
| BLK-03 | open | No pinned offline deterministic runtime/install digest/host profile. |
| BLK-04 | open | No reviewed source/weight/model-card/output/voice-use terms. |
| BLK-05 | open | No rights-cleared frozen voice cohort, target refs, consent, or groups. |
| BLK-06 | open | No approved reference/protocol or separated content/identity/naturalness/timing evidence. |

## Reproduce

Pinned Python: **3.12.16**. Environment: `PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0`.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 -m unittest -q docs.task-evidence.yourtts.test_reference
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 docs/task-evidence/yourtts/run.py all
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 docs/task-evidence/yourtts/verify.py
```

`run.py all` performs 3 cold-start byte-identical regenerations and writes only
task-local files. `verify.py` is read-only (temp dir for cold-start checks) and
enforces newest-merge-base branch-diff scope (`origin/main`→`main`, fail closed
`scope_base_unavailable`) and `base_out_of_scope_change`.

## Pinned digests

<!-- DIGEST_TABLE:START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `039aaad7b4a9ef4097256440b178aa104abf72d40399b5455b2185e1c919e45e` | 501 |
| `README.md` | `2b3f7fc69d3ac0d5ec34eb2817d38c1b6390697b28515b7ae9d0c8e5a4200161` | 4879 |
| `contract.json` | `869267f8eca55048464e0fab271b3f1ffa598696cfd6f3953366892ef605ea32` | 24830 |
| `reference.py` | `8a7c7180bd17ab0d08f2ef9d02fe08941b20eba9c145fe81ca0cc98b11da95d0` | 44925 |
| `report.json` | `fddc7dd7a104a740c72762be560f9ae60ade4f07204a604f8815569d8c054149` | 25219 |
| `report.json.sha256` | `6a0aace81094f2602e5c7654a6dfa1cc245bcd2f49c793447a80f18e5c22052a` | 78 |
| `run.py` | `1218a432b301423011ddf5dbcd47dcf49d28f45748e3f9869eace7f5fa7d5afb` | 4346 |
| `test_reference.py` | `dfba010a0f4e19114bae55b8a6ebe6d8c8ca9da3612323d9d7fc3dc3847d8c86` | 5812 |
| `verify.py` | `5e9f1d868eaec611ca6a36e9b41270c73035ad0f27146c5b70df96be541859a1` | 13524 |
<!-- DIGEST_TABLE:END -->

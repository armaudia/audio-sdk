<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PPG-FOREIGN-ACCENT-CONVERSION — PPG foreign-accent conversion blocker evidence

**Disposition: `DEFER` / `proposal_only_incomplete` / `not_qualified`.**
This package is a bounded, deterministic, task-local evidence and blocker record
for `SDK-PPG-FOREIGN-ACCENT-CONVERSION` (`component_id=ppg-foreign-accent-conversion`).
It applies the **Voice** acceptance profile as a feasibility blocker package.
It does **not** implement, download, load, execute, benchmark, or qualify PPG
foreign-accent conversion.

**Task identity:** `SDK-PPG-FOREIGN-ACCENT-CONVERSION`, base commit `d2e83803b2d00d2588d0735d5f35c7ef0c089cc7`, branch `swarm/SDK-PPG-FOREIGN-ACCENT-CONVERSION`.

## Exact blocker

The merged research note
`research/accent-conversion-20261101/README.md` (pinned in `SOURCES.sha256`)
records:

> **PPG foreign-accent conversion** | Official code found, but no pretrained
> system suitable for an out-of-box test. | Older trainable baseline; code is
> available at [fac-via-ppg](https://github.com/guanlongzhao/fac-via-ppg).

The exact licensed source checkout, pretrained weights/checkpoints, runtime,
rights/consent records, approved reference parity vector, and device/listening
qualification evidence required by the task are **absent** from this workspace.
No artifact was downloaded, copied, vendored, imported, or executed. The
candidate remains `DEFER`, `incomplete`, and `not_qualified`.

## Scope and boundary

- Task-local documentation and stdlib-only tooling only under
  `docs/task-evidence/ppg-foreign-accent-conversion/`.
- No provider registration, descriptor/catalog/default change, installed-v0/ABI
  change, shared build/CI change, board/handoff change, or public claim.
- No real corpus, weights, runtime, audio, listening, device timing, benchmark,
  or release claim.
- The deterministic surrogate in `reference.py` is a synthetic Q15 accounting
  control only; it is **not** PPG foreign-accent conversion and cannot qualify
  the candidate.

## Voice acceptance profile

Voice requires permitted input/target references, frozen task/language/speaker
groups, separate text/semantic preservation, identity/similarity, and
naturalness outcomes, alignment and first-output/tail timing, and independent
consent/reference/output-use gates. All qualification-bearing items are absent,
unmeasured, or structural-only. `qualification.status=not_qualified`.

## Release gates (all blocked)

| Gate | Status | Requirement |
| --- | --- | --- |
| RG-01 | blocked | Exact pinned licensed source and immutable revision. |
| RG-02 | blocked | Exact pretrained weights/checkpoints with hashes and rights. |
| RG-03 | blocked | Reproducible isolated runtime/environment lock and hardware record. |
| RG-04 | blocked | Rights-cleared input/target/reference corpora with consent and use terms. |
| RG-05 | blocked | Approved reference parity vectors and deterministic rerun evidence. |
| RG-06 | blocked | Voice-profile quality/listening/identity/naturalness evidence. |
| RG-07 | blocked | Device timing, streaming/tail latency, and resource evidence on approved targets. |
| RG-08 | blocked | Independent review, release approval, and explicit opt-in intake decision. |

## Pinned evidence and boundary digests

The following digests are pinned and checked by `verify.py` and `SOURCES.sha256`.
This package never hashes the mutable full `plan/swarm/TASKS.json` as canonical
artifact bytes; only stable linked-row identity is gated.

| Kind | Path | SHA-256 |
| --- | --- | --- |
| source | `audio-benchmark-platform/plan/swarm/TASKS.json` (linked-row identity only) | `94c6baca69caecb5c6015268715b70a1f43e9ce6fbc6ccbf2b7cd58fc630dd12` |
| source | `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| source | `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| source | `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| source | `research/accent-conversion-20261101/README.md` | `c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c` |
| boundary | `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| boundary | `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| boundary | `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| boundary | `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| boundary | `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| boundary | `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
| boundary | `docs/task-evidence/convert-and-speak/README.md` | `a89653d3b127f7d2b6cc7f5abc767fb24259b580b4dec2e29ddaed10c74630be` |
| boundary | `docs/task-evidence/convert-and-speak/report.json` | `2423c9cff507fd2c88045ca279367da76a2355168af3d62f29aea425630fcce1` |
| boundary | `docs/task-evidence/survey-trn-04/README.md` | `e0b4ea4d92b122e9820b9857da5e4813db29b048468f2b0383e67ef4264eccae` |

## Reproduction

```sh
cd docs/task-evidence/ppg-foreign-accent-conversion
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git diff --check
```

`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json`, and
`SOURCES.sha256` only after three byte-identical cold-start builds. This
package is not PPG foreign-accent conversion; it records the blocker as
**voice** evidence with `DEFER` / `incomplete` / `not_qualified`, and the exact
finding remains: no pretrained system suitable for an out-of-box test.

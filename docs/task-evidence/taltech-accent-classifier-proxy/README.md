<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-TALTECH-ACCENT-CLASSIFIER-PROXY — TalTech accent classifier proxy blocker evidence

**Disposition: `DEFER` / `proposal_only_incomplete` / `not_qualified`.**
This package is a bounded, deterministic, task-local evidence and blocker record
for `SDK-TALTECH-ACCENT-CLASSIFIER-PROXY`
(`component_id=taltech-accent-classifier-proxy`). It applies the **Evidence**
acceptance profile as a research-control blocker package. It does **not**
implement, download, load, execute, benchmark, or qualify TalTech accent
classifier proxy.

**Task identity:** `SDK-TALTECH-ACCENT-CLASSIFIER-PROXY`, base commit
`26bc48c58f9d69571571fa651862dcbe0fe1172d`, branch
`swarm/SDK-TALTECH-ACCENT-CLASSIFIER-PROXY`.

## Exact blocker

The linked research note `research/accent-conversion-20261101/README.md` records
an accent-classifier **proxy** comparison using
`MilesPurvis/english-accent-classifier` on three TokAN sample pairs. It labels
those predictions as directional only and states no blinded listening panel was
run. This package does **not** treat that proxy as TalTech source, weights,
runtime, reference parity, or listener-confirmed accent evidence.

No exact TalTech accent classifier source checkout, immutable revision, license
record, weights/checkpoint identity, pinned runtime, rights/consent record,
approved reference vector, matched rights-cleared cohort, device timing, or
independent release review is present in audited workspace paths. No artifact
was downloaded, copied, vendored, imported, or executed. The candidate remains
`DEFER`, `incomplete`, and `not_qualified`.

## Scope and boundary

- Task-local documentation and stdlib-only tooling only under
  `docs/task-evidence/taltech-accent-classifier-proxy/`.
- No provider registration, descriptor/catalog/default change, installed-v0/ABI
  change, shared build/CI change, board/handoff change, or public claim.
- No real corpus, weights, runtime, audio, listening, device timing, benchmark,
  or release claim.
- The deterministic synthetic label-accounting control in `reference.py` is a
  synthetic contract control only; it is **not model output** and cannot qualify
  the candidate. Classifier direction is not listener-confirmed accent.

## Evidence acceptance profile

Evidence profile requires pinned scorer/corpus/cohort/aggregation, failed-item
and control preservation, separation between paired/unpaired/synthetic/human and
source-reported evidence, and validation of one invalid/missing case and one
representative valid control through the reported bundle. All qualification-
bearing TalTech classifier items are absent or structural-only.
`qualification.status=not_qualified`.

## Release gates (all blocked)

| Gate | Status | Requirement |
| --- | --- | --- |
| RG-01 | blocked | Pin exact TalTech classifier source, revision, license and attribution. |
| RG-02 | blocked | Pin exact weights/checkpoints, hashes, runtime lock and execution contract. |
| RG-03 | blocked | Clear code/weight/corpus/reference/consent/output-use/redistribution rights. |
| RG-04 | blocked | Reproduce approved reference parity vector on frozen input with deterministic reruns. |
| RG-05 | blocked | Freeze matched rights-cleared cohort/scope; separate proxy from listener-confirmed accent. |
| RG-06 | blocked | Measure device timing, memory, CPU and deadline behavior on approved targets. |
| RG-07 | blocked | Complete independent evidence/rights/scope/release review. |
| RG-08 | blocked | Record explicit opt-in intake; no default/processor exposure/public claim before gates clear. |

## Pinned evidence and boundary digests

This package never hashes the mutable full `plan/swarm/TASKS.json` as canonical
artifact bytes; only stable linked-row identity is gated.

| Kind | Path | SHA-256 |
| --- | --- | --- |
| source | `audio-benchmark-platform/plan/swarm/TASKS.json` (linked-row identity only) | `4a36d634b004dd4bb7aa2096b087909773f67bb9056c30ffae894664a3262957` |
| source | `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| source | `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| source | `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| source | `research/accent-conversion-20261101/README.md` | `c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c` |
| boundary | `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| boundary | `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| boundary | `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| boundary | `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| boundary | `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| boundary | `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |

## Reproduction

```sh
cd docs/task-evidence/taltech-accent-classifier-proxy
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py report.json
PYTHONDONTWRITEBYTECODE=1 python3 run.py sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git diff --check
```

`run.py` regenerates `report.json`, `report.json.sha256`, and `SOURCES.sha256`.
`verify.py` performs strict read-only checks and three cold-start byte-identical
regenerations. This package is not TalTech accent classifier output; it records
the blocker as **evidence** with `DEFER` / `incomplete` / `not_qualified`.

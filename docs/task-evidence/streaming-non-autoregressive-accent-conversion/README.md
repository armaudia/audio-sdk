<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION — Streaming non-autoregressive Accent Conversion blocker evidence

**Disposition: `DEFER` / `proposal_only_incomplete` / `not_qualified`.**
This package is a bounded, deterministic, task-local evidence and blocker record
for `SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION`
(`component_id=streaming-non-autoregressive-accent-conversion`). It applies the
**Voice** acceptance profile as a feasibility blocker package. It does **not**
implement, download, load, execute, benchmark, or qualify Streaming
non-autoregressive Accent Conversion.

**Task identity:** `SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION`, base
commit `14af17740bf8c571f9a985c88fd56f5b5b8e8ae8`, branch
`swarm/SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION`.

## Exact blocker

The merged research note
`research/accent-conversion-20261101/README.md` (pinned in `SOURCES.sha256`)
records:

> **Streaming non-autoregressive Accent Conversion** | Paper/demo inspected; no
> public runnable checkpoint or implementation located. | The paper reports
> about 0.8 s latency and says it remains to be reduced. Use as a
> research-quality comparison, not a sub-100 ms deployment candidate.
> [Paper](https://arxiv.org/abs/2506.16580)

The exact licensed source checkout, pretrained weights/checkpoints, runtime,
rights/consent records, approved reference parity vector, and
device/listening/voice qualification evidence required by the task are
**absent** from this workspace. No artifact was downloaded, copied, vendored,
imported, or executed. The candidate remains `DEFER`, `incomplete`, and
`not_qualified`.

## Scope and boundary

- Task-local documentation and stdlib-only tooling only under
  `docs/task-evidence/streaming-non-autoregressive-accent-conversion/`.
- No provider registration, descriptor/catalog/default change, installed-v0/ABI
  change, shared build/CI change, board/handoff change, or public claim.
- No real corpus, weights, runtime, audio, listening, device timing, benchmark,
  or release claim.
- The deterministic synthetic Q15 accounting control in `reference.py` is a
  synthetic contract control only; it is **not model output** and cannot qualify
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

This package never hashes the mutable full `plan/swarm/TASKS.json` as canonical
artifact bytes; only stable linked-row identity is gated.

| Kind | Path | SHA-256 |
| --- | --- | --- |
| source | `audio-benchmark-platform/plan/swarm/TASKS.json` (linked-row identity only) | `6cfcd19ec6a8f32c306062da9ff9b59e48187eb0e24436417c347ca34d0cb42e` |
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
cd docs/task-evidence/streaming-non-autoregressive-accent-conversion
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
regenerations. This package is not Streaming non-autoregressive Accent
Conversion output; it records the blocker as **voice** evidence with
`DEFER` / `incomplete` / `not_qualified`, and the exact finding remains: no public runnable checkpoint or implementation located.

# Voice-Preserving Zero-Shot Multiple Accent Conversion - task-local evidence

> Decision: **DEFER**. Evidence status: **incomplete**. Qualification: **not_qualified**. No release gate is qualified.

## Source

- Task: `SDK-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION` (audio-sdk, feasibility, voice-preserving-zero-shot-multiple-accent-conversion)
- Base commit: `d66fc99e20f21f8458cd0e846567500c1ed90623`
- Branch: `swarm/SDK-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION`
- Merged evidence: `research/accent-conversion-20261101/README.md` line 174
  - `| **Voice-Preserving Zero-Shot Multiple Accent Conversion** | Paper inspected; no official weights/repo located. | Research comparison only. [Paper](https://arxiv.org/abs/2211.13282) |`
- Inventory: `audio-benchmark-platform/plan/INVENTORY.json` component `voice-preserving-zero-shot-multiple-accent-conversion` (`sdk-model`, `considered`, voice profile).

This package is task-local blocker evidence only. It records absence of official implementation/weights/runtime/rights/matched evidence. It does **not** contain paper code, weights, runtime, audio, converted speech, or benchmark output.

## Boundary

Non-claims (all enforced by contract/report/verify):

- No provider, adapter, descriptor, registry entry, default, or installed-v0/ABI/shared-build/CI change.
- No download, vendoring, in-process file access, network call, or runtime execution.
- No real corpus audio, consented reference, listening test, device timing, or benchmark claim.
- No source-reported paper score treated as matched/comparable evidence.
- No missing/blocked/rejected result qualifies candidate.

Installed v0 geometry remains unchanged: `16000 Hz`, `1` channel, `float32`, `160` samples/frame.

## Voice profile gates (blocked)

Voice profile (`plan/swarm/VERIFICATION.md:22`): freeze permitted input/target references and task/language/speaker groups; separate text/semantic, identity/similarity, naturalness outcomes; record alignment, first-output/tail timing and exact target condition; consent/reference availability/output use are independent gates.

| ID | Requirement | Status |
| --- | --- | --- |
| VR-01 | Freeze input, target references, task and language/speaker groups | blocked |
| VR-02 | Separate content, identity/similarity and naturalness outcomes | blocked |
| VR-03 | Record alignment, first-output/tail timing and exact target condition | blocked |
| VR-04 | Keep consent, reference availability and output use independent | blocked |

## Exact blockers / release gates

All 6 blockers open; all 8 release gates blocked; `decision=DEFER`, `evidence_status=incomplete`, `qualification.status=not_qualified`.

| Gate | Status | Qualifies |
| --- | --- | --- |
| RG-01 source_runtime_identity_and_license | blocked | false |
| RG-02 external_asset_manifest | blocked | false |
| RG-03 pinned_offline_load | blocked | false |
| RG-04 voice_geometry_and_rights | blocked | false |
| RG-05 matched_outcomes | blocked | false |
| RG-06 timing_and_resource_controls | blocked | false |
| RG-07 off_by_default_integration_review | blocked | false |
| RG-08 release_approval | blocked | false |

## Regeneration

```sh
PYTHONHASHSEED=0 pyenv exec python3.12 docs/task-evidence/voice-preserving-zero-shot-multiple-accent-conversion/run.py --all
PYTHONHASHSEED=0 pyenv exec python3.12 docs/task-evidence/voice-preserving-zero-shot-multiple-accent-conversion/verify.py
PYTHONHASHSEED=0 pyenv exec python3.12 -m unittest -q docs.task-evidence.voice-preserving-zero-shot-multiple-accent-conversion.test_reference
```

`run.py` performs 3 cold-start byte-identical regenerations. `verify.py` is read-only over package evidence and checks pins, digests, README tables, scope, and regen stability.

## Pinned source digests

<!-- digest-table: source -->
| Pin | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/accent-conversion-20261101/README.md` | `c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c` |
<!-- digest-table: end -->

## Pinned boundary digests

<!-- digest-table: boundary -->
| Pin | SHA-256 |
| --- | --- |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `840c7accc48426fb34fa36782aa32b8cd9059567723a2cde786e4151916fa3b7` | 262 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `1fdf4012f6579739e0612ca485c94a75371983063b8915f6401f571e87acfa22` | 14266 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `3e7b982e0fa817ec9d01d644f924c2c238e205960e03e92c793f3a185abad0f0` | 34667 |
| `report.json` | `c890a1903969c336658212bd815284747025f9673dd1662ae6347ff251f06e08` | 15222 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `1a1317712e87440df828dbbfc91906f39c0fe0806f0a743263df050011ab10dd` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `66c0805d5fcd793dd9f1f00a3793a119cb019f947f3f17f8e4166a9c19f5674b` | 4659 |
| `test_reference.py` | `b72e359ac97223d4e873c31bf159d4386cf3331b88ff29a271910365cc640e56` | 9340 |
| `verify.py` | `afa8325f1ed4f87eecea8eef21ffd661da72b70a34f63c9906affd03bec4ee09` | 14834 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

<!-- SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION — spectrum-copy bandwidth extension

> **DEFER / incomplete / not_qualified** — task-local synthetic evidence only.
> No exact runnable source/artifact, weights, runtime, rights-cleared cohort,
> real audio, listening, device timing, benchmark, or release claim is made.

## Status

| Field | Value |
|---|---|
| Task | `SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION` |
| Component | `spectrum-copy-bandwidth-extension` |
| Repository | `audio-sdk` |
| Base commit | `4c0f5464eeddff2204b527e8bc4ad09c41b2a657` |
| Branch | `swarm/SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION` |
| Profile | Restoration |
| Decision | **DEFER** |
| Evidence status | **incomplete** |
| Qualification | **not_qualified** |
| Defer before | `opt_in_adapter_exposure` |

## Scope and boundary

This package is **task-local only** under
`docs/task-evidence/spectrum-copy-bandwidth-extension/`. It does not register a
provider, change descriptors/defaults/ABI/registry/shared build/CI, load or
download assets, run real audio, perform listening, measure device timing, or
make benchmark/release claims.

Installed v0 boundary remains unchanged: 16 kHz, mono, float32, 160-sample
frames.

## Negative comparison retained

The pinned research reports spectrum-copy BWE at 3.5 kHz cutoff falling to
14.39 dB SI-SDR versus 17.40 dB band-limited input on the 12-clip synthetic
pilot, and states the local copy-spectrum baseline should be rejected because it
harms fidelity. This package retains that negative comparison and requires
content preservation before inclusion. No result here overturns that finding.

## Exact blockers

| ID | Blocker | Reopen condition |
|---|---|---|
| B-01 | No exact runnable source/artifact revision, immutable bytes, SHA-256 or reviewed licence/rights. | Pin exact source/artifact with bytes, SHA-256 and reviewed rights; do not download/execute here. |
| B-02 | No exact weights/runtime/cohort/reference/attestation assets; caller manifest is shape-only. | Supply six required external assets by id, byte count and SHA-256 with reviewed rights sidecars. |
| B-03 | No Restoration-profile matched evidence: no paired cohort, perceptual/listening/content-preservation or device timing. | Run rights-cleared matched Restoration cohort with negative controls, perceptual/listening, and target-device timing. |
| B-04 | No opt-in intake/release decision; negative spectrum-copy control must remain retained. | Obtain independent opt-in review, rights/counsel clearance, explicit release decision; no default/ABI/shared-build/CI change. |

## Release gates (all blocked)

| Gate | Status | Missing |
|---|---|---|
| RG-01 exact runnable source/artifact | blocked | exact source revision, bytes, SHA-256, reviewed licence/rights |
| RG-02 exact assets and runtime lock | blocked | pinned weights/runtime/cohort/reference assets |
| RG-03 installed v0 boundary | blocked | opt-in adapter intake without ABI/registry/default/shared-build change |
| RG-04 Restoration paired cohort | blocked | rights-cleared paired low/high-band cohort with frozen corruption metadata |
| RG-05 content preservation and negative control | blocked | matched preservation evidence retaining negative spectrum-copy control |
| RG-06 perceptual/listening evidence | blocked | task-appropriate perceptual scoring and authorized listening |
| RG-07 device timing/availability | blocked | target-device timing, availability, paced workload evidence |
| RG-08 public admission review | blocked | independent review, rights/counsel clearance, release decision |

## Regeneration

```sh
python3 docs/task-evidence/spectrum-copy-bandwidth-extension/run.py --all
python3 docs/task-evidence/spectrum-copy-bandwidth-extension/run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest docs/task-evidence/spectrum-copy-bandwidth-extension/test_reference.py -v
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/spectrum-copy-bandwidth-extension/verify.py
```

## Pinned digests

<!-- digest-table: source -->
| Path | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/distortion_restoration_20261028.md` | `8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71` |
<!-- digest-table: end -->

<!-- digest-table: boundary -->
| Path | SHA-256 |
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

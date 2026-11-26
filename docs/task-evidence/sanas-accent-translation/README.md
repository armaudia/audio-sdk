<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SANAS-ACCENT-TRANSLATION — Sanas Accent Translation blocker evidence

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for
`sanas-accent-translation` (title "Sanas Accent Translation", mode
`external-adapter`). It is **not** a Sanas adapter, provider, vendor wrapper,
benchmark or registration. No vendor source, weight, model card, runtime,
caller manifest, audio, converted output, listening result, device timing or
release claim is present. **No result here qualifies the candidate.**

Pinned base: `56eeb134b740d41d770940bf47bd0f035d73f097`.
Branch: `swarm/SDK-SANAS-ACCENT-TRANSLATION`.
Owner: `agent-SANAS-ACCENT-TRANSLATION`.
Reviewer: `reviewer-SANAS-ACCENT-TRANSLATION`.
Interpreter for byte-identical regeneration: CPython `3.12.16`.

## Exact linked evidence

The mutable board file is never hashed as a whole. Only stable identity fields
(`id`, `title`, `mode`, `repository`, `component`, `depends_on`) of this task and
its two foundation dependencies are projected and gated; status, owner, claim,
review, handoff and other mutable fields are excluded.

- Task row: `SDK-SANAS-ACCENT-TRANSLATION` in
  `audio-benchmark-platform/plan/swarm/TASKS.json`; dependencies `SDK-FND-AUDIT`
  and `SDK-FND-EVIDENCE`.
- Accent census: `research/accent-conversion-20261101/README.md:180` —
  "Product docs inspected; closed/proprietary model, not locally downloadable.
  Product benchmark only; comparable latency and weights are not public.
  [Model docs](https://help.sanas.ai/portalv3/docs/ai-models-accent-translation)"
- Inventory row: `sanas-accent-translation` in
  `audio-benchmark-platform/plan/INVENTORY.json`, `evidence_status:
  considered`, `disposition: external-adapter`, pointing to the same census
  line 180.
- Acceptance profile: Voice, `audio-benchmark-platform/plan/swarm/VERIFICATION.md:22`.
- Vendor boundary: `CONTRACTS.md` — linking an external provider does not
  register it; application-local registration and exact advertised modes are
  required, and external assets are declared by ID/hash/byte count and supplied
  exactly by the caller with no provider file access or download in
  process/drain.

## Exact external blocker

The deliverable permits an isolated adapter only if an approved public or
user-supplied runtime is available. No such runtime is staged. The census row
and inventory row record a closed/proprietary product with no local download,
no public comparable latency and no public weights. No immutable source or
runtime digest, reviewed vendor licence/notice/terms, caller-supplied
tool-manifest reference, external asset manifest, voice cohort, rights record
or matched result exists. Vendor product benchmarks are source-reported only
and are not treated as matched, comparable or qualifying evidence.

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Immutable vendor source/runtime identity with reviewed licence, notice and permitted-use terms. |
| `BLK-02` | Per-asset ID, byte count, SHA-256 and `storage:"external"` declaration for every required asset. |
| `BLK-03` | Caller-supplied tool manifest with pinned runtime digest, offline load path and installation location. |
| `BLK-04` | Frozen input, target reference, task and language/speaker groups plus consent and output-use permission. |
| `BLK-05` | Matched runs with alignment and separated content, identity/similarity, naturalness and accent outcomes. |
| `BLK-06` | OFF-by-default opt-in descriptor/provider entry, exact-head review and explicit release approval. |

**Reopen condition.** A caller supplies an exact reviewed vendor or
user-supplied runtime and terms, a complete external asset manifest with exact
bytes and digests, frozen Voice-profile geometry and independent rights,
matched separated outcomes with source-reported scores labelled separately,
device-domain timing controls, and an OFF-by-default opt-in integration with
independent exact-head review and explicit release approval. Until then this
task stays `DEFER`. No vendor download or reconstructed substitute is attempted
to force a reopen.

## Voice acceptance profile

| ID | Requirement from the pinned row | Status |
| --- | --- | --- |
| `VR-01` | Freeze permitted input, target references, task and language/speaker groups | `blocked` |
| `VR-02` | Preserve text/semantic content, identity/similarity and naturalness as separate outcomes | `blocked` |
| `VR-03` | Record alignment, first-output/tail timing and exact target condition | `blocked` |
| `VR-04` | Keep consent, reference availability and output use as independent gates | `blocked` |

Every gate is `blocked` with `qualifies=false`; no missing, synthetic or
source-reported result qualifies. The installed v0 geometry remains 16 kHz,
mono, float32, 160 samples/frame; no Sanas mapping is claimed.

## Release gates

`RG-01` through `RG-08` are all `blocked`/`qualifies=false` in
`contract.json` and `report.json`: source/runtime identity and licence,
external asset manifest, pinned offline load, voice geometry and rights,
matched outcomes, timing and resource controls, OFF-by-default integration
review, and release approval.

## Boundary

No provider registration, descriptor, registry entry or default change; no
public API/ABI change; no shared CMake or CI change; no board or handoff edit;
no vendor download or in-process file access; no real corpus audio, listening,
device timing, benchmark or release claim. Only files under
`docs/task-evidence/sanas-accent-translation/` are written. The strict verifier
compares branch changes against the newest merge-base with `origin/main` then
`main` and fails closed with `base_out_of_scope_change` for any outside path
and `scope_base_unavailable` when no base ref resolves.

## Pinned inputs

<!-- digest-table: source -->
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/accent-conversion-20261101/README.md` | `c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c` |
<!-- digest-table: end -->

<!-- digest-table: boundary -->
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifacts

README.md and SOURCES.sha256 are excluded from this self-referential table;
SOURCES.sha256 pins every task-local file except itself.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `69f9a44e7032d1d2ab1b48796351453f9607d28615067a0345feef531e8f9602` | 546 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `3f8500908f497321c1b33fe5bd60e0259e03974cec773f19fc2be005a7cb5c41` | 13827 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `2eef1445923310ca64306ea91ee5fa2fc9194d4bbdbbe01f9674b16a3a7cdea8` | 36460 |
| `report.json` | `b7c7ccc2d0c5aa23098b79ea169affb0476c54c5bda664819437d8034f6880cf` | 14621 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `5d346897227f4bd218466ceb8bff267188bc7ff791385bd4a9c23dfca90d02d2` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `8e6257555ba725d98a0f1d7c84396cdfd3c34fe717926dd1b12b184e55cdd397` | 4644 |
| `test_reference.py` | `5c0e03c2c7c321e7786a8f0cac4e140d87605a65b5ba134fe299091d22bd0103` | 10022 |
| `verify.py` | `2c9d598d825022768ff1c333f14d119a6864c8d8c9cef63aae944f3a2db3a646` | 18050 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Regenerate and verify

```sh
export PYTHONDONTWRITEBYTECODE=1
python3.12 run.py all
python3.12 -m unittest -v test_reference.py
python3.12 verify.py
```

`verify.py` is read-only for package evidence: it checks strict JSON, canonical
report bytes and SHA-256 sidecar, all source/boundary/artifact pins, the three
README digest tables, blocker and Voice-profile semantics, licensing and
license sidecars, absence probes, newest-merge-base task-local scope, and three
byte-identical cold-start regenerations. It writes only to a temporary
directory used by the scope regression tests.

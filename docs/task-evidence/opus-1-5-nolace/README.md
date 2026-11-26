<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-OPUS-1-5-NOLACE — restoration-category feasibility blocker

**Decision: `DEFER` · status `proposal_only_not_qualified` · completeness
`incomplete` · qualification `not_qualified`.** This is a self-contained,
deterministic, task-local evidence package. It does **not** contain, download,
link, install, execute or wrap Opus 1.5, LACE or NoLACE. It makes no
audio-quality, low-bitrate, benchmark, device-timing, listening or release
claim.

## Exact scope and boundary

- Installed v0 stays 16 kHz mono `float32`, 160 samples per frame. No C ABI,
  header, registry, descriptor, default, shared CMake, CI or installed behavior
  is changed.
- `reference.py` is the smallest verifiable **feasibility probe**, not a codec
  or postfilter implementation. It performs strict 160-sample PCM accounting,
  synthetic Opus-like packet geometry accounting at 160/320/480 samples and a
  1275-byte payload bound, rejects invalid/missing/nonfinite unsupported
  requests, and records that NoLACE has no available decoder surface. It
  produces no decoded audio and never fabricates a postfilter output.
- The probe is stdlib-only, deterministic and independent of the mutable board
  file. It never hashes `plan/swarm/TASKS.json`; only the stable linked-row
  identity is gated.
- No real speech, low-bitrate Opus packet stream, corpus, weights, model,
  wheel, binary, runtime, device timing or listening panel is present.

## Why the task is blocked

The exact task evidence, `research/distortion_restoration_20261028.md`, records:

> **RST-03:** avoid generic postfiltering when the codec is unknown. For Opus,
> evaluate the codec-integrated LACE/NoLACE neural postfilters; their decoder
> has access to codec-specific information. They are part of Opus 1.5 and are
> not enabled by default.

The task asks for the **restoration** acceptance profile at the Opus 1.5
decoder boundary and specifically to *isolate decoder-specific postfilter
behavior and compatibility with intended packets*. That object is a licensed
Opus 1.5 decoder whose NoLACE configuration can be toggled against LACE on the
same packets. The workspace contains no licensed Opus 1.5 source, build,
decoder configuration or packet corpus:

- the bounded candidate workspace/worktree paths were probed and are absent;
- `opuslib`, `opus` and `pyopus` are not importable;
- no `.opus`, `.wav`, model, wheel or native Opus artifact is bundled here;
- no low-bitrate Opus packet trace or rights manifest is supplied.

Because the exact licensed source/runtime/asset is absent, the package does not
invent a substitute. It records the exact missing artifact and rights
requirements and remains `DEFER`. A generic postfilter, an Opus 1.4 PLC
surrogate or a synthetic neural postfilter would answer a different question.

## Source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. SHA-256 is
exact; a changed pin is a hard verification failure. The mutable full board is
**not** pinned or hashed.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/distortion_restoration_20261028.md` | `8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71` | Records LACE/NoLACE as Opus 1.5 codec-integrated postfilters, default off, and defines the restoration blocker. |
| `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Delivery sequence and task-local optional-reference policy. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Restoration acceptance profile applied below. |
| `adapters/opus-plc/adapter.json` | `a36dd6798d3e9f273c7705fea6d11d888680e633a4b4c41c00e20242f45765ae` | Opus 1.4 adapter boundary; integration-scope context only, not NoLACE. |
| `adapters/opus-plc/run.py` | `3f1dcce3102815bf1207a438f3946354f87ebbae5d320cfcf9a6a132b7c3adf8` | Shows the existing 1.4 packet/PLC boundary; no 1.5 NoLACE surface. |
| `research/voice-enhancement-20261101/agent-opus-plc/REPORT.md` | `79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b` | Opus 1.4 PLC provenance. Not reused as Opus 1.5 evidence. |

Boundary pins (worktree-relative): `CONTRACTS.md`
`f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69`,
`api/include/audio_sdk/provider_v0.h`
`f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766`, and
`api/include/audio_sdk/session_v0.h`
`a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1`.

Merged sibling evidence is pinned by `report.json` digests for
`opus-1-4-standard-decoder-plc`, `autoregressive-plc`,
`pitch-period-repeat-plc`, `zero-fill-plc` and `linear-interpolation-plc` in
`contract.json` and `report.json`. No Opus 1.5 LACE evidence package is merged
at this base commit, so none is pinned or implied. The linked task row is gated
only by stable identity fields (`id`, title, repository, mode, component,
dependencies, evidence, base commit, branch). The full mutable `TASKS.json` is
never hashed into canonical bytes.

## Restoration profile application

The restoration profile is applied as a completeness/blocker checklist, not as
a quality claim. Every element is `blocked`, `analytic_only` or
`not_applicable`; none qualifies.

| Required element | Result |
| --- | --- |
| Frozen corruption, codec and metadata | Blocked: no rights-cleared low-bitrate Opus packets or trace. |
| Clean/audio packet baseline | Blocked: no matched clean or decoded no-loss baseline. |
| Degradation stratification | Blocked: no stratified low-bitrate/degradation cohort. |
| Erasure burst stratification | Blocked: no erasure or burst-loss trace. |
| Bandwidth stratification | Blocked: no bandwidth-conditioned packet cohort. |
| Packet geometry accounting | Analytic only: synthetic 160/320/480-sample schedule; no codec. |
| Decoder/packet compatibility | Blocked: no decoder to verify intended packets. |
| LACE versus NoLACE isolation | Blocked: no licensed decoder postfilter surface. |
| Discrete concealment and validity | Blocked: no decode output or concealment events. |
| Decoded intervals | Blocked: no decode output intervals. |
| Task-specific quality | Blocked: no genuine low-bitrate quality measurement. |
| Output peak bounds | Blocked: no decode output to bound. |
| Content/availability timing | Blocked: no runtime or device timing. |
| Authorized listening | Blocked: no listening panel or authorization. |

## Probe and failure controls

`run.py --request` implements a strict protocol-v1 request with exact candidate
and adapter references. Representative results:

- `pcm_boundary_accounting`: `analytic_identity_only`; in/out sample counts
  equal; `qualifies=false`.
- `packet_geometry_accounting`: `analytic_packet_geometry_only`; six synthetic
  packets, one missing, frame-aligned; `codec_decode=false`.
- `postfilter_nolace`, `postfilter_lace_contrast`: `blocked_missing_licensed_runtime`;
  no decoded intervals, output or peak is produced.
- `compatibility_opus_1_5`: `blocked_missing_licensed_runtime`; intended
  packets cannot be verified without the decoder.
- `compatibility_opus_1_4_adverse`: `blocked_decoder_revision_mismatch`;
  retained as adverse cross-version evidence, never validated.
- `runtime_claim`, `cohort_claim`: explicit missing-runtime / missing-corpus
  blockers.
- partial frame, missing/empty packets, partial/unsupported packet duration,
  packet order, invalid fields, fractional/negative/oversized payload bytes,
  nonfinite/wrong-type samples and payloads, bad postfilter mode, bad decoder
  revision, unknown runtime/cohort and missing inputs: explicit `rejected_*`
  results, never scored or dropped.
- Strict JSON rejects duplicate keys, NaN/Infinity and non-object roots.

No missing or adverse result is promoted. All results carry `qualifies=false`.

## Eight blocked release gates

1. Pinned, hash-verified licensed Opus 1.5 source/runtime with LICENSE/NOTICE
   and execution approval.
2. A documented NoLACE decoder configuration surface plus the LACE contrast.
3. Rights-cleared low-bitrate Opus packet corpus with exact encoder revision,
   bitrate, frame duration, bandwidth and loss trace.
4. Paired LACE-versus-NoLACE isolation on the same packets and revision.
5. Decoded intervals, discrete concealment/validity and rejected-packet
   accounting.
6. Task-specific quality, clean-reference comparison and output peak bounds on
   genuine low-bitrate traffic.
7. Target-device content/availability timing, memory and deadline budget.
8. Provider/catalog/license intake, descriptor/public-surface review and release
   approval.

All eight are `blocked`; none has evidence.

## Exact missing artifacts and rights

| Missing artifact | Rights requirement |
| --- | --- |
| Pinned Opus 1.5 source revision or official build with exact SHA-256 | Opus/upstream LICENSE and NOTICE for the exact revision, redistribution terms, and approval to execute the native decoder. |
| Documented Opus 1.5 NoLACE decoder configuration/API | Public API documentation for the exact upstream revision. |
| Rights-cleared low-bitrate Opus packets and loss trace | Written corpus rights for evaluation and derived outputs. |
| Decode/restoration harness and listening authorization | Harness license, device access approval and listening-panel permission. |

No download, fabrication or substitution was attempted.

## Reproduction

Run from this directory on the pinned worktree:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 run.py --sources
python3 run.py --inspect
python3 verify.py
```

`run.py --report` builds the report three times and writes only byte-identical
output; `verify.py` separately launches three cold starts for `--report`,
`--sources` and `--inspect`, checks exact external/boundary/sibling/local pins,
the stable linked row, canonical bytes, eight blocked gates, all adverse/
missing/invalid/nonfinite controls, SPDX annotations, dependency hygiene and
task-local scope containment. JSON is canonical (`sort_keys=True`, compact
separators, `allow_nan=False`) with one trailing newline.

Report digest: see [`report.json.sha256`](report.json.sha256), the canonical
SHA-256 of the byte-identical [`report.json`](report.json). No self-referential
digest is repeated in this README.

## Failure controls and non-claims

- No Opus 1.5 decoder, LACE/NoLACE postfilter, codec or audio output is
  implemented.
- No Opus 1.5 source, build, model, weight, packet corpus or licensed asset is
  present.
- No genuine low-bitrate decode, listening, benchmark, device-timing or release
  claim is made.
- Opus 1.4 PLC evidence is provenance only and is not reused for Opus 1.5
  NoLACE.
- No installed v0, ABI, registry, descriptor, default, shared build or CI change
  is included.
- No provider is registered, exposed or default-enabled.
- Historical source statements are provenance only; none is reproduced or used
  as a threshold here.

## Remaining gates / reopen

`DEFER` until all eight gates pass for the exact runtime and workload. Reopen
only with an exact licensed Opus 1.5 decoder plus the NoLACE configuration
surface, a rights-cleared low-bitrate packet trace and the restoration harness
above.

## License

All files here are first-party `Apache-2.0`, copyright 2026 Tsakanyan Hovhannes.
Python and Markdown files carry file-level SPDX tags; JSON and digest files are
covered by adjacent `.license` sidecars and the repository `REUSE.toml`
annotation for `docs/**`.

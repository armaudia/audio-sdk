<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-COSYVOICE-FAMILY — CosyVoice family routing/blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`.** This directory is bounded, deterministic,
task-local evidence for the legacy umbrella Voice row `CosyVoice family`
(`component_id=cosyvoice-family`, mode `research-control`). It is **not** a
CosyVoice implementation, conversion adapter, provider or result. No
source-speech conversion checkpoint, adapter, weight bundle, runtime,
rights-cleared pair, converted output, listening result, device measurement,
benchmark or release claim is included. **No result here qualifies the
CosyVoice family.**

The acceptance profile is **Voice**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. The decision is **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`.

## Exact blocker: no source-speech conversion artifact exists

The family row asks for a **source-speech voice-conversion** comparison. The
catalogue record is `unavailable/blocked`: *"No local source-speech conversion
checkpoint/adapter. The distinct official CosyVoice 2 streaming TTS path did run
locally (23.81s first chunk; 8.07x file RTF) but does not convert input speech;
see separate TTS row."*

| Item | Status |
| --- | --- |
| Official source checkout | **Present and pinned**: `research/voice-conversion-eval-20261101/repos/cosyvoice`, `FunAudioLLM/CosyVoice` commit `074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc`, Apache-2.0 `LICENSE` SHA-256 `c71d239d…`, 156 tracked files + 8 symlinks (3,073,286 bytes), tree digest `9b0d2b60…` |
| Source submodule | **Present and pinned**: `third_party/Matcha-TTS`, `shivammehta25/Matcha-TTS` commit `dd9105b34bf2be2230f4aa1e4769fb586a3c824e`, 107 files + 1 symlink (826,391 bytes), tree digest `de380235…` |
| Task kind of that source | **TTS/voice-cloning code**, not a source-speech converter. The pinned checkout includes no conversion checkpoint. |
| Source-speech conversion checkpoint/adapter | **Absent**: no filename, byte count, immutable revision or SHA-256 is known; no candidate artifact can be pinned |
| Pinned conversion runtime | **Absent**: no isolated environment, package lock or environment digest exists at any fixed probe path |
| Rights, consent and output use | **Unresolved**: conversion-weight terms, training-data provenance, target-speaker consent, reference availability and output-use/redistribution clearance |
| Frozen conversion cohort | **Absent**: only one research LJ Speech source and one upstream RT-VC demo target exist; target provenance is unconfirmed |
| Converted output / scores / timing | **Absent**: no converted audio, content/identity/naturalness result, authorized listening, alignment, first-output/tail, memory or streaming measurement |
| CosyVoice 2 0.5B TTS result | **Routed, not reproduced here**: historical TTS only, merged under `SDK-COSYVOICE-2-0-5B`; it does not convert input speech |

The machine-readable record is `report.json` → `source_probe`,
`conversion_artifact_probe`, `runtime_probe`, `absence_evidence`,
`family_routing`, `family_scope_decision`, `exact_blockers`, `voice_profile`,
`routed_tts_evidence`, `admission` and `gates`. `contract.json` carries the same
disposition, pins, geometry, routing ledger and all eight blocked release gates.

Because the conversion artifact and runtime are absent, **no result qualifies
the family row**, no provider or developer/evidence adapter is registered, and
release gate `RG-01` stays blocked. Nothing was fabricated, reconstructed or
downloaded.

## Family routing ledger

The package distinguishes what is present from what the family row needs:

| Member | Kind | Status | Task route |
| --- | --- | --- | --- |
| `FAM-01` official source | source checkout | `present_pinned_code_only` | none; TTS/voice-cloning code, not a converter |
| `FAM-02` CosyVoice 2 0.5B streaming TTS | TTS provenance | `routed_not_reproduced_here_not_conversion` | **`SDK-COSYVOICE-2-0-5B`** |
| `FAM-03` conversion checkpoint/adapter | required artifact | `absent_blocked` | none |
| `FAM-04` conversion runtime | runtime | `absent_blocked` | none |
| `FAM-05` conversion cohort and rights | corpus/rights | `absent_blocked` | none |
| `FAM-06` conversion result | result | `absent_blocked` | none |

The TTS route is pinned to the merged sibling evidence: PR **#188**, reviewed
head `87bb50d1c547816b1e7c9edfdbf561fac3691921`, live head
`2995fb6895a24dbd56f87d596ed7c711a9874883`, squash merge
`4a06f9af3fe86d73847b1dbddc214bfa555c9c19`, sibling `report.json` SHA-256
`aee352f4…`. The sibling package is pinned read-only in `SOURCES.sha256` and is
never copied, reproduced or promoted. **TTS is not source-speech conversion.**

The routing ledger is a deterministic object; its digest is recorded as
`family_routing.ledger_sha256`. `tts_promoted_to_conversion` is `false` and
`conversion_result_present` is `false`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-COSYVOICE-FAMILY`, `c07f8540b4c32d2add5c6e0c1baddf625d9d9312` |
| Task mode | `research-control` |
| Acceptance profile | `voice` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `f32`, 160 samples/frame |
| Declared adapter intake | 16 kHz mono `f32`, 160-sample frame — **proposal only, not verified** |
| Asset boundary | caller-supplied `external` only; no bytes read, no download |
| Provider registration, default, ABI, CI | none |

- Work is confined to `docs/task-evidence/cosyvoice-family/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, board/handoff files, CI, rulesets and `main` are untouched.
- The declared 16 kHz/f32/160-sample adapter format is a proposal used to
  exercise admission checks. It is not read from, and must not be cited as, any
  CosyVoice conversion configuration.
- No request is ever processed as CosyVoice family conversion. Valid requests
  fail closed because the conversion bundle and runtime are absent.
- Board linkage is projected from **stable row identity only** (`id`, `title`,
  `component`, `mode`, `repository`, `depends_on`). Mutable status, owner,
  review, handoff, priority, claim and history never enter canonical bytes and
  are never a gate. The mutable full `plan/swarm/TASKS.json` is **not hashed**
  into any canonical artifact.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not a conversion
engine:

1. **Strict JSON** with duplicate-key, NaN, Infinity, BOM and root-type
   rejection; canonical compact sorted-key bytes with one trailing LF and no
   floats.
2. **Source verification.** It recomputes a digest over the tracked non-`.git`
   files and symlinks in the pinned checkout and its submodule, checks the
   commit, counts, byte totals and Apache-2.0 licence pin. It never imports or
   executes upstream code and records that the checkout contains no
   source-speech conversion checkpoint.
3. **Fixed-path absence probes.** It checks a bounded list of conversion
   weight, runtime and cohort locations without a recursive workspace walk.
4. **Conversion artifact probe.** It records that the family record names no
   artifact filename, byte count, revision or digest, so no candidate pin can
   exist. It never opens, hashes, loads or downloads a weight.
5. **Runtime probe.** Fixed-path checks only; no package is imported, installed
   or opened and no network is used.
6. **Family routing ledger.** It records the one pinned code checkout, the one
   routed TTS row, and the four absent conversion members, with a stable digest.
7. **Fail-closed conversion-adapter admission.** It validates a proposed
   manifest with exact revisions, digests, runtime, format, rights, consent,
   reference pair, cohort and finiteness checks. It rejects a manifest whose
   adapter says it does not convert input speech, and one that declares
   text-only output — so the routed TTS row cannot be promoted into a conversion
   row. A structural schema control is labelled non-evidence and never
   qualifies.
8. **Stable board identity** from the linked row and its two dependencies.
9. **Canonical report, contract and source-manifest bytes.**

It does **not** load a conversion bundle, create a model or runtime session,
convert speech, synthesize audio, score quality, run listening or produce any
audio.

## Voice acceptance profile application

`plan/swarm/VERIFICATION.md` assigns the Voice profile. With the conversion
artifact, runtime, rights and cohort absent, the profile maps as follows
(`report.json` → `voice_profile`; each row is also verified):

| Required element | Local status |
| --- | --- |
| Permitted input and target references | `blocked` — no permitted conversion pair; research single pair only |
| Task, language and speaker groups | `blocked` — no family cohort |
| Text and semantic content preserved | `blocked` — no converted output |
| Identity/similarity separate | `blocked` — no similarity result |
| Naturalness separate | `blocked` — no listening or MOS |
| Alignment, first-output/tail timing, exact target condition | `blocked` — not measured |
| Consent, reference availability, output use | `blocked` — rights unresolved |

The routed TTS historical values never enter `report.json` as floats or as
candidate results. They are labelled
`historical_research_routed_not_reproduced_not_qualified`, are not promoted and
do not establish conversion content preservation, identity, naturalness,
consent, output use, latency or device timing.

## Admission controls

`report.json` → `admission.cases` contains **68 synthetic adverse cases**, all
rejected with an unchanged frozen evaluation state, plus one structurally valid
schema control that is explicitly **not evidence**. Cases cover missing objects
and fields, malformed adapter revisions and digests, model-file path traversal,
oversize counts, unresolved weight terms, non-converter and text-only adapters,
wrong runtime and format, missing consent, redistribution and output-use rights,
missing reference-pair consent, missing cohort source/target pairs, duplicate
JSON keys, NaN/Infinity and BOM input. The summary records
`qualifying_results=0`, `weights_loaded=false`, `runtime_invoked=false`,
`audio_read=false`, `inference_performed=false` and `conversion_performed=false`.

## Eight blocked release gates

| Gate | Blocked reason |
| --- | --- |
| `RG-01` exact licensed source and conversion artifact identity | The source is pinned, but no conversion checkpoint, adapter, filename or digest exists. |
| `RG-02` exact pinned conversion runtime and package lock | No isolated environment, lock or environment digest exists. |
| `RG-03` conversion-weight terms, training data, consent and output use | Model/training terms, target-speaker consent and output-use rights are unresolved. |
| `RG-04` exact reference-pair parity | No approved conversion pair or regenerable output exists. |
| `RG-05` frozen rights-cleared conversion cohort | No multi-item permitted source/target cohort exists. |
| `RG-06` independent content, identity and naturalness results | No independent content, similarity, naturalness or listening result exists. |
| `RG-07` alignment, first-output/tail, memory and streaming | No exact-runtime conversion timing, memory or streaming measurement exists. |
| `RG-08` opt-in developer/evidence adapter intake and release decision | No adapter, descriptor, public-surface decision or independent review exists. |

## Reproduction and verification

From this directory, with the pinned interpreter and no bytecode:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py all` regenerates the canonical report, sidecar, contract and source
manifest three times in one process and requires byte-identical output.
`verify.py` additionally runs three cold-start regenerations in fresh scratch
trees, checks strict JSON, exact pins, stable board identity, licensing,
task-local git scope and blocker semantics. Expected: all tests pass and
`verify.py` prints
`PASS pins=… gates=8 blockers=6 routing_members=6 admission_cases=68 cold_starts=3/3 … decision=DEFER`.

## Non-claims

No source-speech conversion checkpoint, adapter, model output, runtime, corpus,
cohort, consent, reference pair, listening panel, speaker similarity,
naturalness, latency, device, callback, benchmark or release claim is made. The
pinned CosyVoice checkout is TTS/voice-cloning code and is not executed. The
CosyVoice 2 0.5B TTS result is a different task and belongs to
`SDK-COSYVOICE-2-0-5B`. No installed v0, public API, C ABI, descriptor, registry,
default, shared build, CI, board or handoff change is made.

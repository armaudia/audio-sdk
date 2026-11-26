<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-HUME-OCTAVE — task-local Voice-profile blocker

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`.** This directory is bounded, deterministic,
task-local evidence for the board row `Hume Octave`
(`component_id=hume-octave`, mode `external-adapter`). It is **not** a vendor
integration, TTS adapter, provider or result. No vendor entitlement, credential,
API contract, terms or data-processing record, consent-cleared voice, client
runtime, generated output, listening result, device measurement, benchmark or
release claim is included. **No result here qualifies the candidate.**

The acceptance profile is **Voice**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. The decision is **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`.

Pinned base: `59971563b2c9cdf7b845e8210dd2697d55b8bc08`.
Branch: `swarm/SDK-HUME-OCTAVE`.

## Exact blocker: a cloud service with no admitted access

Candidate matrix record 55 is `out of scope`: *"Cloud text-to-speech, not input
microphone enhancement; vendor TTFB is not local."* The record names the product
page only, so no contract revision, endpoint, model/voice version, credential,
entitlement or asset can be pinned. Nothing was fabricated, reconstructed,
mirrored, downloaded or substituted. The task deliverable explicitly permits a
prototype adapter *only if an approved public or user-supplied runtime is
available*; none is.

| Item | Status |
| --- | --- |
| Vendor entitlement, account/project or credential | **Absent**; no credential or entitlement record exists |
| Pinned API contract, endpoint, model/voice version, schema | **Absent**; the record names no revision or endpoint identity |
| Vendor terms, data-processing/retention and training use | **Absent** |
| Generated-output ownership, redistribution and product use | **Absent** |
| Consent-cleared target/reference voice | **Absent** |
| Local source checkout or weights | **Absent and not applicable** to a hosted service |
| Isolated client runtime and package lock | **Absent**; no environment exists at `data/envs/hume-octave` |
| Network/egress boundary and recorded platform | **Absent**; vendor TTFB is source-reported, not measured here |
| Frozen voice cohort | **Absent** |
| Approved parity vector | **Absent** |
| Generated output, scores, timing | **Absent**; no audio, content/identity/expressiveness result, listening, alignment, first-output/tail, memory or network measurement |

The machine-readable record is `report.json` → `candidate`, `asset_audit`,
`absence_probes`, `asset_requirements`, `caller_asset_contract`,
`voice_profile`, `reference_protocol`, `controls`, `gates`, `exact_blockers`,
`source_reported_context` and `missing_historical_artifacts`. `contract.json`
carries the same disposition, pins, geometry, invariants, blockers and all eight
blocked release gates.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-HUME-OCTAVE`, `59971563b2c9cdf7b845e8210dd2697d55b8bc08` |
| Task mode | `external-adapter` |
| Acceptance profile | `voice` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Declared control geometry | 16 kHz mono `float32`, 160-sample frame — **control only, not candidate geometry** |
| Candidate geometry | `unestablished`; no rate, chunking, voice taxonomy, expressiveness scale or output geometry is asserted |
| Asset boundary | caller-supplied `external` only; no bytes read, no download, no request |
| Provider registration, default, ABI, CI | none |

- Work is confined to `docs/task-evidence/hume-octave/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, board/handoff files, CI and other worktrees are untouched.
- Board linkage is projected from **stable row identity only** (`id`, `title`,
  `component`, `mode`, `repository`, `depends_on`, `deliverable`, `acceptance`,
  `evidence`, `write_scope`). Mutable status, owner, review, handoff, priority,
  claim and history never enter canonical bytes and are never a gate. The
  mutable full `plan/swarm/TASKS.json` is **not hashed** into any canonical
  artifact.
- No request is ever sent as a TTS generation. Any synthesized voice or
  expressiveness target fails closed because the vendor runtime and entitlement
  are absent.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not a TTS client:

1. **Strict JSON** with duplicate-key, NaN, Infinity, BOM and root-type
   rejection; canonical compact sorted-key bytes with one trailing LF and no
   floats.
2. **Fixed-path vendor/source audit.** It checks a bounded list of candidate
   source, weight, vendor-contract, entitlement, terms, data-processing,
   consent, runtime, rights, cohort and parity paths without a recursive
   workspace walk. Every probe is currently absent; any later presence makes
   `reference.build_report()` and `verify.py` fail closed.
3. **Caller-supplied-asset manifest contract.** It validates exact fields,
   absolute paths, file/directory existence, SHA-256 values, a bounded vendor
   contract revision string, mono geometry, admitted rates, task kind, baseline,
   offline variant, voice label and a bounded integer expressiveness. It hashes
   the caller's files but never imports, executes or calls the caller's client
   and never loads an asset.
4. **Target-condition admission.** It accepts only the declared `local_identity`
   comparison baseline at the full control expressiveness. Any other voice
   label, reduced expressiveness, plain TTS task kind, microphone-enhancement
   task kind, streaming variant or wrong baseline is rejected with
   `absent_cloud_runtime_and_entitlement` because the vendor runtime and
   entitlement are absent.
5. **Synthetic identity control.** It generates 2.0 s of deterministic
   integer-derived 16 kHz mono PCM, applies only the identity baseline, and
   checks exact sample count, exact duration, digest equality, peak bound and
   offline-only alignment. It is labelled
   `caller_supplied_synthetic_identity_acceptance_plan_not_vendor_output` and
   has `qualification_effect=none`.
6. **Adverse rejection.** 45 malformed, missing, invalid, nonfinite,
   wrong-domain and non-identity controls are actually invoked; all fail closed.
7. **Stable board identity** from the linked row and its three dependencies.
8. **Canonical report, contract and source-manifest bytes.**

It does **not** install a client, create a session, send a network request,
synthesize speech, score content, identity, expressiveness or naturalness, run
listening or produce any audio.

## Voice acceptance profile application

`plan/swarm/VERIFICATION.md` assigns the Voice profile. With the vendor runtime,
contract, terms, consent, cohort and parity absent, the profile maps as follows
(`report.json` → `voice_profile`; each row is also verified):

| Required element | Local status |
| --- | --- |
| Permitted input and target references | `absent` — no permitted text/target pair |
| Task, language, speaker and expressiveness groups | `absent` — no cohort |
| Text and semantic content preserved | `not_measured` — no vendor output |
| Identity/similarity separate | `not_measured` — no similarity result |
| Target voice and expressiveness separate | `not_measured` — no taxonomy, scale or scorer |
| Naturalness separate | `not_measured` — no listening or MOS |
| Alignment, first-output/tail timing, exact target condition | `structural_only` — offline accounting only |
| Consent, reference availability, output use | `absent` — rights unresolved |

`satisfied_for_qualification=[]` and `real_model_metrics=null`. No sibling
accent, voice-conversion, prosody, emotion or TTS value is copied into this
report as a candidate metric, and the vendor-reported ~300 ms time-to-first-byte
is labelled `vendor_reported_not_measured_here`.

## Eight blocked release gates

| Gate | Blocked reason |
| --- | --- |
| `exact_source_and_artifact_identity` | No vendor contract, endpoint, API/model/voice version or entitlement identity exists. |
| `runtime_admission` | No isolated client environment, lock, egress boundary or recorded platform exists. |
| `artifact_rights_consent_and_output_use` | Vendor terms, data processing, training use, output ownership, voice consent and redistribution are unresolved. |
| `exact_reference_parity` | No approved vendor output or local identity parity vector exists. |
| `frozen_voice_cohort` | No rights-cleared, task-matched cohort exists. |
| `content_identity_expressiveness_naturalness_results` | No independent content, identity, expressiveness or naturalness result exists. |
| `alignment_timing_and_streaming` | No exact-runtime alignment, first-output/tail, chunking, network latency, memory or device measurement exists. |
| `opt_in_adapter_intake_and_release` | No adapter, descriptor, public-surface decision or independent review exists. |

## Reproduction and verification

From this directory, with no bytecode:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` regenerates the canonical report, sidecar, contract and source
manifest three times in one process and refuses to write unless all rounds are
byte-identical. `verify.py` additionally runs three cold-start regenerations in
fresh scratch copies, checks strict JSON, exact pins, stable board identity,
licensing, task-local git scope and blocker semantics. Expected: all tests pass
and `verify.py` prints
`PASS pins=… gates=8 blockers=8 cold_starts=3/3 … decision=DEFER`.

When the package is copied out of the worktree, set `SDK_ROOT` to the SDK
checkout and `SOURCE_ROOT` to the common workspace root. Any appearance of a
required contract, entitlement, consent or licence makes `verify.py` fail closed
so the blocker must be re-evaluated rather than silently promoted.

## Files

- `reference.py` — stdlib-only absence/vendor audit, caller manifest contract,
  fail-closed target admission, synthetic identity control and report model.
- `run.py` — 3× byte-identical regeneration of `report.json`, its SHA-256
  sidecar, `contract.json` and `SOURCES.sha256`; `--check` is read-only.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — fail-closed SHA-256 manifest for sources, boundaries and
  package files. It never pins the mutable full `plan/swarm/TASKS.json`; only
  the linked-row stable identity is gated.
- `contract.json` — task contract, scope, boundary, pins, invariants, blockers
  and eight gates.
- `test_reference.py` — deterministic Python `unittest` acceptance checks.
- `verify.py` — read-only pins/JSON/identity/assets/control/licensing/
  reproduction/scope verifier, including three cold regenerations.
- `LICENSES.md` — licensing and provenance statement.
- `*.json.license`, `*.sha256.license` — SPDX sidecars for generated artifacts.

## Non-claims

No vendor credential, entitlement, API client, model, checkpoint, config, voice
reference, contract, consent record or runtime is claimed. No generated response
voice, text/semantic preservation, speaker similarity, expressiveness
realization, naturalness, latency, memory, RTF, network timing, device timing
or release result is claimed. The vendor's source-reported time-to-first-byte is
not reproduced or presented as a local measurement. The synthetic identity
control is not vendor output and cannot qualify the candidate. No installed v0,
public API, C ABI, descriptor, registry, default, shared build, CI, board or
handoff change is made. Missing evidence never qualifies this row; the decision
remains **DEFER**.

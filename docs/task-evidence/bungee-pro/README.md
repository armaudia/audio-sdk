<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-BUNGEE-PRO — commercial Bungee Pro blocker

`audio-sdk/bungee-pro/0.1`

| Field | Value |
| --- | --- |
| Decision | **DEFER** |
| Status | **incomplete** |
| Disposition | **proposal only** |
| Qualification | **not_qualified** |
| Qualifying results | **0** |
| Blocked release gates | **8** |
| Open exact blockers | **6** |
| Profile | Rate (`plan/swarm/VERIFICATION.md`) |
| Mode | external-adapter |
| Pinned base | `4d9a7568583fd1764d2ca9006e8e660e8662aaf9` |

This directory is a bounded, task-local blocker package for **Bungee Pro**, the
commercial upgrade to the open-source Bungee Basic time stretcher. It is **not**
an implementation, adapter, provider, benchmark or release. It records why the
candidate cannot be qualified from the artifacts that are actually present, and
it reproduces only declared arithmetic and deterministic synthetic controls.
Nothing here may be promoted to a runtime or quality claim.

## Why DEFER

The pinned candidate note describes Bungee Pro only as a **commercial upgrade**
to Bungee Basic: proprietary algorithms, claimed sharper transients and timbre,
SIMD builds (WebAudioWorklet SIMD128 WebAssembly, Arm NEON, x86-64 SIMD) and
professional support. It records:

- licence: **Commercial**, paid;
- evidence status: **vendor claims only; no local evaluation**;
- no local build or benchmark of Bungee Pro;
- no pricing, contract terms or patent indemnity for Bungee Pro.

No Bungee Pro SDK package, binary, source snapshot, licence key, executed
agreement, terms text, integration host or measured render trace exists in the
project workspace. The open-source Bungee Basic checkout that is used by the
sibling `SDK-BUNGEE-BASIC` evidence is a **different MPL-2.0 implementation**
and cannot be substituted for the proprietary Pro artifact or its rights.
Nothing was downloaded, copied, reconstructed or fabricated. Supplying the
missing artifacts reopens the task; absence of a result is the correct outcome.

## Exact blockers

| ID | Missing artifact | Minimum reopening condition |
| --- | --- | --- |
| `BLK-01` | Licensed Bungee Pro distribution artifact | Exact Pro version/build, immutable acquisition record, full SHA-256 of every supplied library/binary/source file and the exact Pro API identity. No Pro artifact is present in the workspace. |
| `BLK-02` | Executed commercial licence and rights decision | Signed entitlement for the exact Pro build; reviewed terms for local execution, benchmarking, redistribution, derivative output use, commercial use and patent indemnity. The candidate note verifies none of these. |
| `BLK-03` | Pinned host, toolchain and key handling | Exact OS/architecture/compiler/link mode, license-key handling, install location, ABI/API compatibility record and a reproducible build or package install record. |
| `BLK-04` | Official Pro geometry and measured trace | Vendor-pinned rate/pitch/latency/rate-change/final-partial semantics and an exact offline render trace with source/output mapping, duration, pitch, transient behaviour, buffering, rebuffer and drift. "Similar to Basic" is not a specification. |
| `BLK-05` | Rights-cleared cohort and approved scoring | Immutable consented unfamiliar-speech, music and silence cohort with output-use terms, matched controls, approved preservation scorer and blind listening protocol. |
| `BLK-06` | Rate acceptance, device timing and release review | Measured Rate-profile results, target-device timing/resources, separate opt-in adapter intake with an OFF default, independent exact-head review and release approval. |

The eight blocked release gates are enumerated in `report.json` under `gates`.
Every gate is `blocked` and `qualifies=false`.

## What is pinned

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless marked
as SDK-worktree relative.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Bungee Pro matrix row and §3.8: commercial/proprietary status, vendor claims only, no local evaluation, no pricing or terms. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component row `bungee-pro`; Rate profile; external-adapter disposition. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile. |
| `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK implementation plan and external-adapter boundary. |

The unchanged public boundary is pinned separately: `CONTRACTS.md`,
`api/include/audio_sdk/provider_v0.h`, `api/include/audio_sdk/session_v0.h`,
`CMakeLists.txt`, `REUSE.toml`, `.github/workflows/ci.yml` and `README.md`.

Merged sibling time-stretch and pitch evidence is pinned under
`docs/task-evidence/`: Bungee Basic, Signalsmith Stretch, SoundTouch, Rubber
Band R3, Sonic, libsamplerate, granular TSM, OLA/SOLA, the phase-vocoder
baseline, the duration planner, browser `playbackRate`, the AVAudioUnit
blocker and the Speex resampler. Exact values are in `SOURCES.sha256` and
`report.json`.

The mutable full `plan/swarm/TASKS.json` is **never hashed**. Only the stable
linked-row projection (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`, `evidence`) is read; board status, claim and review fields gate
nothing.

## Parameter provenance

The candidate note does **not** record a numeric rate or pitch range for
Bungee Pro, its defaults, its API identity or its latency. It records only
"Similar to Basic" for latency and "Yes, per grain" for rate control in the
matrix row. Therefore:

- `documented_parameter_envelope` leaves every numeric bound and default
  `null`, sets `api_identity_recorded=false`, and marks
  `semantics_verified_here=false`.
- `synthetic_control_envelope` is a **synthetic validation envelope**
  (rate `1/4–4`, pitch `-1200..1200` cents, 1600-sample partial-window block)
  used only to exercise the fail-closed manifest. It is not vendor evidence
  and it cannot qualify a result.

## Synthetic arithmetic controls

`gate_control` evaluates a declared recipe:

- output duration = source samples / rate for each contiguous rate segment
  (Bungee `speed` semantics: `0.75` is slower and yields a longer output);
- pitch ratio = `2^(cents/1200)` rounded to twelve decimal places;
- a final partial window is computed with the declared 1600-sample block;
- every case is labelled `synthetic_contract_control_not_evidence` and has
  `qualifies=false`.

Cases cover 1×, 2×, 1/2×, 3/4×, 3/2×, the synthetic envelope bounds 1/4× and
4×, a contiguous three-segment rate change, a final partial window and a
combined rate/pitch case. No audio is synthesized, read or rendered.

`frame_control` reproduces the installed v0 16 kHz mono 160-sample frame shape
and rejects non-finite, non-numeric, boolean, wrong-length and out-of-range
inputs with exact codes. Bungee documents float input in `[-1, 1]` with no
internal clipping; that caller contract is enforced here. No sample is
processed by any Bungee Pro runtime.

## Admission and fail-closed behaviour

`admission` validates a caller-authored qualification manifest that requires an
exact Pro version and artifact digest, a commercial licence and terms digest,
a pinned host/toolchain and license key, an audio fixture digest, a mapping
block and complete rights. Every mutation (missing/unknown field, wrong schema,
malformed digest, out-of-range or malformed rate, non-integer or mismatched
duration, duplicate control, false rights, non-finite numeric value) is
rejected with its expected code and no state advance. A synthetic manifest can
be admitted as a **schema control** only; it is never `admitted` and always
`qualifies=false` because no vendor artifact exists.

## Reproduce

From this directory, with Python 3.11+ and the standard library only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

`run.py all` regenerates `contract.json`, `report.json`,
`report.json.sha256` and `SOURCES.sha256` three times and requires
byte-identical results. `verify.py` re-checks the Rate profile, exact pins,
strict JSON, canonical bytes, all controls, eight blocked gates, six open
blockers, licensing, task-local git scope and three cold-start
regenerations. No network, vendor SDK, runtime, audio file or device is used.

## Files

| File | Role |
| --- | --- |
| `reference.py` | Deterministic model, strict JSON, pins, presence probes, controls, contract/report builders. |
| `run.py` | Three-repeat canonical regeneration. |
| `contract.json` | Canonical task contract and pins. |
| `report.json` | Canonical machine-readable DEFER report. |
| `report.json.sha256` | SHA-256 sidecar for `report.json`. |
| `SOURCES.sha256` | SHA-256 pins for all source, boundary, sibling and local files. |
| `test_reference.py` | Standard-library test suite. |
| `verify.py` | Read-only package verifier. |
| `*.license` | REUSE/SPDX sidecars for JSON artifacts. |

## Non-claims

- No result in this package is a qualification, benchmark or release.
- Bungee Pro is a proprietary commercial product; no vendor source, binary,
  SDK package, model, licence key or licence text was copied, imported, loaded
  or reconstructed.
- The open-source Bungee Basic checkout/evidence is not Bungee Pro and was not
  used as a substitute, parity oracle or measured baseline.
- No numeric Pro rate, pitch, latency, API or defaults were verified; the
  candidate note records vendor claims only.
- No audio was read or played; no cohort, consent or output-use grant exists.
- No rate, duration, pitch, transient, buffering, rebuffer, drift or
  final-partial result was rendered or measured.
- No listening, target-device timing, resource, benchmark or release review was
  performed.
- No provider, descriptor, registry, default, installed-v0 behavior, ABI,
  shared build, CI, board or handoff file is changed.

SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0

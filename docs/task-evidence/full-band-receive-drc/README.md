<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FULL-BAND-RECEIVE-DRC-CONTROL — task-local synthetic receive DRC evidence

This directory contains **proposal-only, incomplete, not-qualified** evidence for
full-band receive dynamic-range control. It is a self-contained Python reference
at a **protocol-shaped waveform adapter boundary**. It is not an installed SDK
provider, not a public API/ABI change, not a listening result and not a release
claim. No processor exposure is authorized: the decision is **DEFER** until
independent review.

## Scope and invariants

- Work is confined to `docs/task-evidence/full-band-receive-drc/`. Shared CMake,
  contracts, public headers, descriptor registry, defaults, installed v0
  behavior and other tasks are untouched.
- Installed v0 stays 16 kHz / mono / float32 / 160-sample frames. The reference
  is causal and has 0 samples of content delay; it processes on that exact grid.
- The adapter/provider manifests (`adapter.json`, `provider.json`) are opt-in,
  default-OFF, unregistered and have empty descriptor settings. OFF is bit-exact
  identity below the shared safety ceiling; ON selects the deterministic DRC
  reference. Above the 0.95 ceiling the shared clamp applies in every mode and
  is reported honestly in `ceiling_clamp_probe`.
- No real speech corpus, listening panel, licensed runtime, model weights,
  network download, target-device timing, STOI/ESTOI computation, quality score
  or release qualification is used. Every signal is analytic or seeded-noise.
- The near-end listening baseline is reproduced **only** as a SYNTHETIC,
  non-human, non-predictive level/masker control. It is excluded from
  qualification. Authorized listening remains a separate blocked gate.
- Missing, invalid, nonfinite, out-of-range, stale-session and missing-reference
  cases fail closed. No missing result may qualify the candidate.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This disclosure and reproduction guide. |
| `SOURCES.sha256` | Curated SHA-256 pins for external sources, boundary headers, implementation, manifests, README and report. |
| `contract.json` | Task contract, verification profile, pins and excluded claims. |
| `adapter.json` | Unregistered, default-OFF protocol-v1 waveform adapter manifest. |
| `provider.json` | Conceptual opt-in provider manifest; no C provider is built or registered. |
| `reference.py` | Deterministic causal compressor/limiter engine and frozen synthetic fixtures. |
| `scorer.py` | Dependency-free gain, response, attack/release, headroom, delay, numerical and level/masker metrics. |
| `fixture.py` | Read-only digest/canonical-report surface; no writes. |
| `run.py` | Protocol adapter, report/sidecar generator and source-pin generator. |
| `verify.py` | Strict read-only verifier for pins, JSON, semantics, reproducibility, licensing and git scope. |
| `check_licensing.py` | Local SPDX/REUSE checks with split identifier literals. |
| `test_reference.py` | 34 deterministic standard-library unit tests. |
| `report.json` | Canonical synthetic evidence report. |
| `report.json.sha256` | SHA-256 of the canonical report bytes. |

## Source provenance

Pinned context (never reproduced or claimed as a local result):

- `research/listening_intelligibility_20261028.md` — near-end listening source;
  used only to pin provenance and protocol shape. Its source-reported objective
  predictors are not imported, pooled or reused here.
- `audio-benchmark-platform/plan/swarm/VERIFICATION.md` — DSP acceptance profile.
- `audio-benchmark-platform/plan/swarm/TASKS.json` — mutable board snapshot,
  recorded at read time as provenance only, never as a gate or result.
- `api/include/audio_sdk/provider_v0.h`, `api/include/audio_sdk/session_v0.h` —
  public boundary headers, pinned read-only.

Exact digests are in `SOURCES.sha256`.

## DSP profile coverage

`report.json` records sweeps, steps, impulses, silence and synthetic clean
speech; level and masker controls (-30/-18/-12/-6/0 dBFS RMS × -5/0/+5 dB TMR);
gain, steady-state frequency response, step attack/release, peaks/headroom, 0
sample delay, finite/nonfinite behavior, state transitions, causality,
chunk-boundary equivalence, reset/replay, session rejection and interacting
compressor + limiter + masker-control configurations. Adverse and losing
observations are recorded verbatim in `regressions`, not filtered.

The report explicitly excludes human intelligibility, real-speech STOI/ESTOI,
MOS, listening effort, target-device timing, release qualification and installed
provider availability. All five qualification gates remain blocked with stated
reopening conditions.

## Reproduction

From this directory, with Python 3.11.5 and the standard library only:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 check_licensing.py
```

`run.py --report` and `run.py --sources` must be byte-identical on repeated
runs; `verify.py` re-checks all pins, strict JSON, report semantics, exact report
bytes, three cold-start interpreter probes, SPDX headers and git write scope.
The adapter can also be exercised without writing evidence:

```sh
python3 run.py --request request.json --result result.json
```

A request carries `protocol_version`, `operation` (`inspect` or `run`),
`candidate_ref`, `adapter_ref`, `configuration`, and for `run` also
`attempt_id`, `stimulus_id` and `samples`. Results are canonical JSON with a
trailing newline and synthetic-only disclosure.

## Verification status

- Tests: 34 unit tests covering pins, manifests, boundary, determinism, DSP
  controls, state/validity and evidence shape.
- Report regeneration and all pins: byte-identical; three cold-start repeats.
- Licensing: explicit SPDX headers plus the repository `docs/**` REUSE 6.3.0
  annotation; no literal full identifier token is embedded in Python strings.
- Decision: **DEFER**, readiness `incomplete`, qualification `not_qualified`,
  status `proposal_only_not_qualified`. No gate was weakened to obtain a pass.

## Final digests

- `report.json` SHA-256: `9a685e1868e8290aa99131d810aa919df5c64712f3eebba40ab754788624d3f9`
- `report.json.sha256` content: `9a685e1868e8290aa99131d810aa919df5c64712f3eebba40ab754788624d3f9`
- Frozen synthetic fixture digest: `41c4bfc6cbcaf4f705a751efef5bd2cb9d8655725b7add5a522d08593415466f`
- Base commit: `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`

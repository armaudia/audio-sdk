<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-TD-PSOLA - TD-PSOLA readiness blocker package

**Status: `incomplete`; decision `DEFER`; qualification `not_qualified`.**
This directory is bounded, deterministic, task-local feasibility evidence for
`SDK-TD-PSOLA` (component `td-psola`, Rate profile). It is **not** a TD-PSOLA
implementation, provider, runtime, benchmark, or release claim.

`plan/INVENTORY.json` records `td-psola` as `evidence_status=considered`,
`disposition=sdk-reference`, area `Rate and content`, with the Rate
acceptance profile and task `SDK-TD-PSOLA`. Its evidence link is
`cpp-library/pipeline-validation/playback-speed-candidates.md`. The inventory
note requires causal streaming design work to remain separate from offline
Praat reference runs.

## Exact external blocker

No exact licensed TD-PSOLA/Praat/Parselmouth source snapshot, immutable
revision, reviewed license text, pinned offline runtime, exact audio
geometry/casual contract, rights-cleared inputs, deterministic outputs, matched
Rate-profile evidence, device timing, listening/screen, or independent review
is present. Nothing was fabricated, reconstructed, downloaded, mirrored, or
substituted. No revision, file name, byte count, or SHA-256 is asserted as
verified for missing upstream artifacts.

| Missing artifact | Exact requirement |
| --- | --- |
| Source/runtime snapshot | Exact licensed implementation or reference runtime at immutable revision/tag with reviewed license, notice, README, and per-file SHA-256 manifest. |
| Pinned runtime | Locked offline runtime: interpreter, packages, wheel hashes, platform, device, dtype, determinism settings, install location, clean-room import digest. |
| Task geometry | Exact audio-in/audio-out contract: sample rate, channels, frame/hop, lookahead, latency, reset/drain, epoch/pitch-mark policy; causal streaming kept separate from offline reference runs. |
| Rights-cleared inputs | Reviewed code/data/output terms and digest-pinned speech/music/silence inputs with consent, evaluation, and redistribution decisions. |
| Matched evidence | Deterministic outputs and Rate-profile measurements on a rights-cleared cohort with 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final partial, and speech preservation. |
| Release evidence | Separate mode/platform timing/resources/pacing, authorized listening/labeled screen, OFF-by-default intake, clean-install proof, and independent exact-head review. |

## Rate profile application

All Rate rows are blocked or documented-only; every row is `qualifies=false`.
There are zero real results and zero synthetic result promotions. No candidate
output, audio, timing, or listening claim is made.

| Requirement | State |
| --- | --- |
| Source/output mapping | blocked |
| Duration target/actual | blocked |
| Pitch preservation/shift | blocked |
| Transient audibility | blocked |
| Playback buffering/fill/flush/deadline | blocked |
| 1x identity control | blocked |
| Rate changes (step/ramp) | blocked |
| Unfamiliar speech | blocked |
| Music and synthetic music negative control | blocked |
| Silence/empty input | blocked |
| Rebuffer, drift, final partial window | blocked |
| Pause/filler tied to source timestamps and speech preservation | blocked |
| Separate evidence categories | documented, no pooling |

## Fail-closed asset declaration

`reference.py` accepts only the unpopulated declaration
`audio-sdk/td-psola-asset-declaration/0.1` with `decision="DEFER"` and
`qualifies=false`. Presence claims, set digests, invented geometry, rights
claims, or qualification claims are rejected. The validator never resolves
paths, imports modules, reads audio/weights, or runs inference.

## Absence evidence

Fixed probes only (no recursive walk): 9 workspace paths, 5 SDK-worktree paths,
3 home-cache paths. All 17 must be absent. `verify.py` fails if any probe later
appears. No asset/source bytes are asserted for missing artifacts.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| RG-01 source revision and license provenance | blocked | Stage immutable source/runtime revisions with complete license, notice, README records and independent review. |
| RG-02 pinned runtime and task geometry | blocked | Provide locked offline runtime and exact geometry/casual contract with deterministic settings and clean-room import digest. |
| RG-03 assets and dependency manifest | blocked | Stage every required file with immutable revision, byte counts and SHA-256 values. |
| RG-04 rights-cleared inputs and terms | blocked | Freeze permitted digest-pinned inputs with consent, evaluation, derived-output and redistribution decisions plus code/data terms. |
| RG-05 reference execution and output validity | blocked | Execute pinned runtime offline and record output hashes, finite/length behavior, exact repeats and peak/RSS. |
| RG-06 Rate profile against real runtime | blocked | Run every Rate-profile case on a rights-cleared cohort with required controls and conditions. |
| RG-07 mode/platform timing/resources/listening | blocked | Measure each mode/platform separately with timing/resources/pacing and complete authorized listening or labeled screen. |
| RG-08 provider intake/public surface/release | blocked | Open separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after prior gates clear. |

## Boundary

Only `docs/task-evidence/td-psola/` is written. No provider registration,
descriptor, registry, default, public header, ABI, shared CMake, CI workflow,
installed-v0 behavior, board or handoff is changed. No network access or
download is attempted.

## Reproduction

Requires CPython 3.11.5. Commands from this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint  # from SDK root
```

`run.py` regenerates `contract.json`, `report.json`, `report.json.sha256`, and
`SOURCES.sha256` three times and requires byte-identical output. `verify.py`
performs a fresh three-run cold-start regeneration in a temporary directory and
compares committed bytes.

## Source pins (SHA-256)

`source:` paths are relative to `AUDIO_ROOT`; boundary paths are relative to the
SDK worktree. The mutable shared board is not pinned; only stable linked-row
identity is gated.

| Kind | Path | SHA-256 |
| --- | --- | --- |
| source | `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| source | `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| source | `research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
| source | `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| source | `audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| source | `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| source | `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |

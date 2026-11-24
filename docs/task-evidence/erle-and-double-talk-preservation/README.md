# SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION — research-control evidence adapter

Task-local, deterministic, synthetic paired-signal comparison of far-end-only
ERLE and near-end preservation under double talk. The outcome is **DEFER**:
proposal-only, incomplete, `not_qualified`, with **no processor exposure** and
no SDK provider, descriptor, registry, catalog, default, API/ABI or installed
v0 change. Installed v0 remains 16 kHz mono float32, 160 samples per frame.

The adapter reproduces the *shape* of the research comparison on frozen seeded
signals; it does not reproduce any historical real-recording score. A paired
adaptive-reference candidate is compared against identity, fixed attenuation and
a synthetic replay of fixed-hybrid near-end damage. Historical fixed-hybrid
damage is kept as a separately pinned, source-reported control.

## Scope and boundary

- All new files are under this directory. No shared `CMakeLists.txt`,
  `CONTRACTS.md`, public header, descriptor registry, registry default,
  installed-v0 behavior, board, handoff, ruleset, other worktree/branch or PR
  is changed.
- No provider is included. The `provider OFF/ON` check is therefore not
  applicable; no opt-in build target exists to enable. The adapter is
  unregistered and developer-only.
- `run.py` is a task-local protocol-v1-shaped JSON adapter (`inspect` / `run`)
  and a byte-identical report generator. It produces no Bench bundle.
- Synthetic signals are generated in Python from the pinned scalars in
  `fixture_spec`; no corpus, WAV, model, download or licensed runtime is read.
- Evidence profile: `evidence` with the frozen `room` controls from the plan.

## Source and boundary pins (SHA-256)

Workspace paths are relative to the directory containing `research/` and
`audio-benchmark-platform/`; SDK paths are relative to the worktree root.
`SOURCES.sha256` pins every local artifact except itself.

| Pinned bytes | SHA-256 | Purpose |
| --- | --- | --- |
| `research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` | ERLE only on far-end-only regions; separate double-talk preservation; historical fixed-hybrid damage and suppressor caveats. |
| `research/voice-enhancement-20261101/agent-hybrid-aec-real/REPORT.md` | `4577d59347d9f48a693228ccbf40a9de77494294e7d0df111c98e8591c3e438e` | Source-reported fixed RLS→NLMS hybrid double-talk damage, peaks and RLS near-only failure. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Evidence and room acceptance profiles: freeze render/reference, excitation, delay, movement, noise and reset; include echo-only, near-only, overlap and no-reference. |
| `audio-benchmark-platform/plan/swarm/check.py` | `5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539` | Read-only board validator used for the task check. |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public v0 provider boundary, unchanged; confirms 16 kHz / mono / 160-sample grid. |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public session boundary, unchanged. |
| `docs/task-evidence/SDK-PIPE-DUPLEX.md` | `c0a550ffafe3de25f7d37ba5eadc23ae94df347666e8212094664d1fffe20871` | Merged Speex MDF limitation disclosure: higher ERLE on misaligned render and residual echo in a small-overlap near-ratio window. |
| `docs/task-evidence/offline-mono-wpe/scorer.py` | `22c2ba7e60dc4f6e0a58b5ad5a5b89bf643e620ec37736082e3a64bffd034d96` | Local SI-SDR / synthetic-scoped STOI scorer inherited with only `SCORER_ID` changed. |
| `docs/task-evidence/nlms-aec/reference.py` | `12efcf612cb15404bd3cb32c2d215d0424bcfce76cee73078ca5d26c9760b492` | Prior paired-reference NLMS evidence, pinning provenance only; this implementation is independent. |

The mutable board snapshot `audio-benchmark-platform/plan/swarm/TASKS.json`
had SHA-256 `7c1e90c1a2c87906533b56429127b4527c09e7550bb9ec8e286ae92f24ed1128`
when read. It is provenance only and never qualifies this evidence.

## Local artifact digests

| Path | SHA-256 |
| --- | --- |
| `adapter.json` | `31b7a8f307eee8fcb99fc80a436ada4383a387e8d0aea4f211b47f3c153935a9` |
| `contract.json` | `d95d812edd6986929e3e67dd791f1f1d62417a6724a8464bb1eb48672a6f1c29` |
| `fixture.py` | `df6adefccac0c174e413521106704dbd98eed19f4649ed787805909d02b9bebc` |
| `reference.py` | `1994d59541a6dd343ce373348e4bf71275323a98adfaac1bd2f353dd8f6e9c7b` |
| `run.py` | `2ada95b938fe1bca8c3a3e16b1688733f191779ccc4906285fd838e2de88bd8d` |
| `scorer.py` | `d00b18f3e4be6e72f716b3279b741a9c6daabdff8ec929954e71102f67b66bdb` |
| `test_reference.py` | `b73191e091fce84c40b01d2ff2b6e13a174a853363225785b423f14330721ea7` |
| `verify.py` | `7aa53192329d1ff3b77e939603c59b37fa7bcceb9216183c02fa756de7de1786` |
| `report.json` (file bytes = canonical bytes) | `6860139e8c1a9f5c01fa219f81b6b8f5ee3f43160dd139d00e45cfb853d63b50` |
| `report.json.sha256` (file bytes) | `99ab61451f1164a2eb362e9c8177224ab54b0da0262e8d8db2a5f888e30ebb20` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`) plus one trailing newline; both its canonical digest and file
digest are `6860139e8c1a9f5c01fa219f81b6b8f5ee3f43160dd139d00e45cfb853d63b50`.
The frozen fixture digest is
`fe7ea930e2f753996c9709a7ca05d744852aa99ba951a6bba5ab21a955838bd4`.
Regeneration is byte-identical and checked with `cmp`, SHA-256 and `verify.py`.

Three internal canonical repeats of the report core (all fields except
`repeat_runs`) share the digest
`b37a8aeb9c3c5ea1f6a06dd9e02a25a9c8afe5cda78b202e344104dc7a717e9b`.
`verify.py` additionally performs three independent `run.py --report`
regenerations and requires all three stdout byte streams to equal the checked-in
`report.json` bytes. No tolerance is widened and no provider is substituted.

## Frozen room profile

- 112,000 samples (7 s), 16 kHz mono f32, 160-sample frames, seed `20261124`.
- Two sparse linear paths: `PATH_A` primary delay 32 samples; `PATH_B` after the
  switch at sample 76,800, primary delay 48 samples (+16 samples delay change).
  The 6,400-sample transition window is excluded from scoring.
- Analytic harmonic/syllable far-end and independent near-end sources; seeded
  LCG capture noise at 0.0015 full scale; near gain 0.55; no corpus or RIR.
- Overlap ratios are frozen at 0, 0.25, 0.5 and 1.0 of far-end-active frames in
  the double-talk segment. Render latency is the 32-sample primary path delay;
  an explicit `delayed_render` condition shifts the reference by 32 samples.
- ERLE windows: early `[9600,18400)`, pre-switch `[71200,76000)`, post-change
  `[84800,95200)`. Each requires near silence, render energy, no gap and no
  transition; otherwise the value is withheld with reasons.
- Near-end preservation window: `[22400,68800)`; near-only tail
  `[97600,108800)` for the near-only case.
- Reset schedule: epoch 1 from sample 0, explicit reset to epoch 2 at sample
  76,800; stale epoch, stale position and invalid frames are rejected with
  unchanged state. A withheld reference preserves state and passes through.
- Candidate: causal samplewise NLMS, 96 taps, step 0.22, leak 0.9999. The
  instantaneous double-talk hold is deliberately OFF because the pinned
  research measured sharp ERLE loss from such a rule. No detector is proposed.

## Evidence summary (all synthetic)

ERLE is reported only on valid far-end-only windows; near preservation is a
separate field. Candidate values are from `report.json:results`.

| Condition | Status | Qualifies | Early ERLE (dB) | Pre-switch ERLE (dB) | Post-change ERLE (dB) | Near SI-SDR / STOI (dB / index) | Near attenuation (dB) | Residual echo re echo (dB) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| echo_only | ok | yes | 17.65 | 17.78 | 11.34 | withheld (no near speech) | — | — |
| overlap_25 | ok | yes | 17.65 | 17.88 | 11.34 | -7.80 / 0.868 | -13.78 | -10.49 |
| overlap_50 | ok | yes | 17.65 | 17.92 | 11.34 | -8.01 / 0.877 | -14.57 | -10.15 |
| overlap_100 | ok | yes | 17.65 | 17.90 | 11.34 | -8.29 / 0.881 | -15.30 | -9.77 |
| delay_change | ok | yes | 17.65 | 17.92 | 11.34 | -8.01 / 0.877 | -14.57 | -10.15 |
| near_only | ok | no | withheld | withheld | withheld | 35.40 / 1.000 | -0.00 | withheld (no echo component) |
| delayed_render | misaligned_reference | no | 19.64 | 19.86 | 18.40 | -7.77 / 0.899 | -14.59 | -10.40 |
| reference_dropout | partial_reference | no | 17.65 | 17.92 | withheld (render gap) | -8.01 / 0.877 | -14.57 | -10.15 |
| no_reference | blocked_no_reference | no | withheld | withheld | withheld | withheld | withheld | withheld |

Controls are never allowed to qualify. On `overlap_50`: identity near SI-SDR /
STOI is `-3.54 dB / 0.744`; fixed −6.02 dB attenuation is `-3.54 dB / 0.744`
with −5.96 dB near attenuation; the synthetic oracle-gated fixed-hybrid replay
is `-7.02 dB / 0.609` with −13.10 dB near attenuation. The candidate's near
SI-SDR damage versus identity is about −4.5 dB even though its far-end ERLE is
much higher: this is the central tradeoff, not a preservation win. The
`near_only` residual-echo metric is legitimately undefined because there is no
echo component, so that row is not qualified.

Historical fixed hybrid (source-reported, **not** reproduced here): double-talk
echo MOS-like `2.610 → 3.373`, degradation `4.012 → 2.219`
(`Δ -1.793`, 95% CI `[-2.181,-1.374]`); movement double-talk degradation
`Δ -2.152` (`[-2.511,-1.797]`); peaks 14.72 and 48.12; full RLS nonfinite on
12/12 near-end-only clips. These values are kept only as a damage-control
warning.

A separate pinned MDF limitation disclosure is recorded from
`docs/task-evidence/SDK-PIPE-DUPLEX.md`: aligned ERLE 16.453939 dB,
misaligned ERLE 16.888932 dB and overlap near-ratio 0.985161. ERLE is therefore
not an alignment detector, and overlap near-ratio is not a double-talk quality
result. No Tiny16 comparison, approved independent reference adapter or
permitted-case manifest exists here.

`qualification.no_missing_result_may_qualify` is true. Five candidate rows have
all required metrics; every row with a blocked/misaligned/partial status or an
undefined metric has `qualifies: false`. `qualification.missing_result_count`
is 18. The overall decision remains DEFER regardless of synthetic completeness.

## Evidence acceptance profile

The `evidence` profile is applied with frozen `room` controls: `report.json`
pins the scorer bytes, the synthetic corpus/fixture digest, the nine-condition
cohort, the exact per-window aggregation rule, all eight failed items and the
three non-qualifying control variants. The adapter is exercised through
`run.py --request` for one representative valid result (`overlap_50` candidate)
and one invalid/missing case (`no_reference` candidate); `verify.py` requires the
adapter responses to match the checked-in report rows on status, metrics,
missing results and qualification. No Bench bundle, hosted submission or public
corpus claim follows from this local validation.

## Explicit invalid and missing cases

`invalid_and_missing_cases` records eight cases: nonfinite microphone,
out-of-range microphone, short microphone, reference length mismatch, stale
epoch, stale position, missing near reference and missing far-end-only window.
Each has `metrics: null` and `qualifies: false`; rejected frames leave DSP state
unchanged. Delayed, partial and withheld reference rows are scored only where
meaningful and never qualify.

## Commands and verification

Run from this directory unless noted:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report > report.regen && cmp report.json report.regen
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m json.tool adapter.json >/dev/null
python3 -m json.tool contract.json >/dev/null
python3 -m json.tool report.json >/dev/null
```

The local unittest suite is 28 tests and passes. JSON validation is applied to
`adapter.json`, `contract.json` and `report.json`; `verify.py` additionally
rejects duplicate keys and nonfinite constants. It re-checks all pinned source
and boundary bytes (including the MDF disclosure), every local artifact in
`SOURCES.sha256`, the canonical/file digests, report completeness, the
qualification rule, the DEFER decision, the absence of provider/CMake scope,
three exact internal canonical repeats and three byte-identical CLI report
regenerations.

SDK CTest uses a build outside the worktree:

```sh
cmake -S <worktree> -B <tmp>/sdk-build -DCMAKE_BUILD_TYPE=Release
cmake --build <tmp>/sdk-build --parallel 4
ctest --test-dir <tmp>/sdk-build --output-on-failure
```

Board and whitespace checks are read-only:

```sh
python3 <audio-benchmark-platform>/plan/swarm/check.py --task SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION
git -C <worktree> diff --check
```

Licensing: `reuse lint` and `reuse spdx` with CI-pinned `reuse[charset-normalizer]==6.3.0`.
All new Python files carry SPDX headers; no C header is generated, and no
generated-header string contains a split SPDX token.

## Exact release gates / reopening conditions

No default, production, processor or provider exposure until all of these pass:

1. Paired licensed render/capture recordings with pinned provenance, hashes,
   sample alignment and measured render latency; source-component and
   participant-use rights resolved.
2. AECMOS echo/degradation, ASR word accuracy and authorized listening on real
   speech, with double-talk, near-only, path-change, nonlinear-loudspeaker and
   noise strata; clean near references where permitted. Keep synthetic and
   source-reported evidence separate.
3. Measured loudspeaker/microphone loop gain and gain-before-feedback, plus
   target-device content delay, buffer/clock drift, p50/p95 compute, memory,
   pacing and deadline measurements.
4. Provider/license/catalog intake: SPDX/REUSE review, opt-in provider OFF by
   default and unregistered until approved, descriptor and public-catalog
   review, and no installed-v0 behavior change.

Until then this directory is proposal-only research-control evidence and the
installed SDK behavior stays frozen.

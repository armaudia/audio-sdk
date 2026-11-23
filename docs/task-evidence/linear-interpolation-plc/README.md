# SDK-LINEAR-INTERPOLATION-PLC — deterministic synthetic evidence

Task-local, proposal-only fixture for a minimal linear-interpolation packet-loss
concealment (PLC) reference. It is **synthetic**, **optional**, **unregistered**,
and changes no installed SDK behavior, public API, ABI, descriptor, registry
default, `CONTRACTS.md`, `CMakeLists.txt`, board or handoff file.

## Scope and boundary model

The fixture implements a deterministic Python reference of a linear
interpolation PLC stage at the modeled public-adapter boundary. It models the
SDK v0 geometry exactly: 16 kHz, mono, float32, 160-sample frames. Results use
the public `as_result_v0` flag semantics: `AS_RESULT_CONCEALMENT = 4`, with
`valid_count = 0` for concealed frames.

Explicit boundary note: the shipped public v0 facade has **no frame-level
"packet lost" flag**; its frame flags only admit `AS_FRAME_FINAL_INPUT`, and
`AS_RESULT_CONCEALMENT` is a *result* flag. The fixture therefore models the
host delivery-adapter boundary: the adapter emits one call per source frame and
marks a missing packet with `present=False` and `valid_count=0`. The reference
uses a 5-frame (800-sample) lookahead buffer, bridges each erased interval with
a linear ramp from the last received good sample to the first sample of the next
good frame, and reports those intervals as concealment with zero valid samples.
No SDK source file is changed to enable this; no new public flag is implied.

Everything here is generated under fixed seeds. No corpus, weights, download,
codec runtime, licensed runtime, device, network trace, or listening panel is
used. The candidate status is `proposal_only_synthetic_incomplete`.

## Files

| Path | Purpose |
| --- | --- |
| `fixture.py` | Deterministic generator, reference session model, metrics and report writer. |
| `report.json` | Canonical machine-readable report (deterministic bytes). |
| `runtime-measurements.json` | Non-deterministic unpaced wall-clock/RSS envelope pointer; not qualifying timing evidence. |
| `test_fixture.py` | 16 Python unittest checks. |
| `README.md` | This file. |

## Source pins (SHA-256)

| Path (relative to `/Users/htsakanyan/workspace/audio/audioml` unless noted) | SHA-256 |
| --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `research/voice-enhancement-20261101/agent-opus-plc/REPORT.md` | `79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b` |
| `audio-benchmark-platform/audio-bench/src/audio_bench/metrics.py` (SI-SDR definition reference, not imported) | `5f4a16aab66bdef244e57d7b3c93237ebf0bf2bf9ef2d9ad0e0b4ff063107210` |
| `api/include/audio_sdk/provider_v0.h` (in this worktree) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` (in this worktree) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

Pinned scorer: Python 3.12.16, `numpy 2.5.4`, `pystoi 0.4.1`,
`pystoi/stoi.py` SHA-256
`482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658`,
non-extended STOI at 16 kHz. SI-SDR is the zero-mean v1 definition implemented
locally in `fixture.py`. A missing or unpinned scorer returns `None` with a
reason and never triggers a substitute metric.

## Reproduction

From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python fixture.py report.json runtime-measurements.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python -m unittest -v test_fixture.py
```

`report.json` regeneration is byte-for-byte deterministic. Regenerating
`runtime-measurements.json` changes its SHA-256 because it records unpaced
wall-clock time; its values are observations of this Python runtime only.

Board verification (run from `/Users/htsakanyan/workspace/audio/audioml`):

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-LINEAR-INTERPOLATION-PLC
```

Base commit: `0673cb354cceb66f2f71faf9af7703b5a5d2fcfa`.

## Expected counts and digests

- Cohort: 250 frames = 40,000 samples = 2.5 s; 9 erased frames = 1,440 samples.
  Erased frame indices: `20, 60, 61, 80, 140, 200, 201, 202, 203`
  (isolated, two-frame burst, four-frame maximum burst).
- Produced frames per condition: 255 (5 startup + 250 source frames); drain
  frames: 5. Valid content samples: 40,000 for identity, 38,560 for candidate
  and zero-fill; 9 concealed frames carry `valid_count = 0` each.
- Clean reference digest: `d7895f2c49486a9282384ee5dc780b9a41c60f3b2b95ee381bfb82fe145a54d6`.
- Fixture spec digest: `de2eda6935bb687fe684351cc9dd3bdc9f90aacbc39cd337543de630a53f2589`.
- Candidate output digest: `dbdc7a26f626734d9905e7e53d439c0009663934baa04d4460fd0e1e54ebdc06`.
- Zero-fill input/output digest: `f6601e2ab4799020461361d158b5ee33a3ad27f0b12f1736d3459cd4a5e1efd0`.
- `report.json` SHA-256: `0a711aa398be0f86559249781f429323cee2eaf31ced1585f5d8fc205248b323`.
- `fixture.py` SHA-256: `35054c6f79279d9ab64b301a2f2c24dbfdbf776c4e579fe4e9f5d3ede7129e61`.
- `test_fixture.py` SHA-256: `6b68ffef3f57b88ebd3c598368a77062e5936360098ff497f6c4ac8f5d7dc069`.
- Tests: 16 passed, 0 failed, 0 skipped.
- Flags: `controls_all_pass=true`, `alignment_pass=true`, `state_pass=true`,
  `all_outputs_finite=true`, `all_metrics_available=true`.

Pinned paired scores (synthetic clean reference):

| Condition | SI-SDR (dB) | STOI | SI-SDR Δ vs identity | STOI Δ vs identity | Concealed RMSE |
| --- | --- | --- | --- | --- | --- |
| Identity clean | undefined (exact reconstruction) | 1.000000 | — | — | — |
| Zero-fill baseline | 10.983909 | 0.951020 | 0.000000 | 0.000000 | 0.030219 |
| Linear interpolation | 11.820617 | 0.949594 | +0.836708 | -0.001426 | 0.027524 |

The identity clean SI-SDR is intentionally undefined because the estimate is
bit-identical to the reference; no substitute value is invented. STOI for the
candidate is slightly below the identity/noisy control while SI-SDR and
concealed-region RMSE improve. These are synthetic observations, not a claim of
general perceptual improvement.

## Adverse controls and alignment

Recorded in `report.json` under `adverse`, `alignment` and `state`:

- Missing frame, wrong frame shape, short frame, non-finite input, stale epoch,
  duplicate packet, out-of-order packet: each rejected without changing
  stream/valid-content state.
- Erase burst length: four-frame bursts are concealed; a fifth consecutive
  erased frame is rejected with no accepted content.
- Erase boundary: leading erasure produces zero-valid concealment output; two
  trailing erased frames are explicitly counted as unresolved; a boundary
  burst across frames 99–102 is fully concealed.
- Concealment output: flag 4 with `valid_count = 0`, excluded from the 38,560
  valid content samples.
- Final short frame: 37 valid samples accepted from an 8-frame-plus-37 stream.
- State leakage: isolated sessions are uncoupled; reset to a higher epoch is
  bit-identical to a fresh session, rejects stale frames and rejects process
  after close.
- Alignment: declared 800-sample buffering delay, raw source origin `-800`,
  measured impulse peak index `4800` (expected `4800`), measured content lag
  `0`, and all per-frame source mappings check out.

## Runtime envelope (non-qualifying)

`runtime-measurements.json` records unpaced wall-clock and process high-water
RSS for the exact Python reference runtime on Darwin arm64, Python 3.12.16:
per-condition stream time about 0.0086–0.0097 s, median process-call time about
0.035 ms, and first valid output after about 0.0002 s / 5 process calls.
`qualification_status` is `blocked`. These are not paced, deadline, target-device
or installed-provider timing claims.

## Explicit non-claims and blockers

- No real clean-reference cohort, rights-qualified speech, EARS/DNS rerun, or
  external corpus is used. The historical Opus PLC and candidate-matrix
  values are pinned context only; they are not rerun or pooled with local
  synthetic results.
- No authorized listening test, MUSHRA registration, unpaired predictive
  screen, or target-device/listening claim exists.
- No codec-native PLC, captured network trace, jitter buffer, FEC/DRED, stereo,
  mobile pipeline, real weights, downloads, licensed runtime, or installed SDK
  behavior is tested or changed.
- No target-device or exact-runtime deadline qualification is made. Source
  reported RTF values in `REALTIME_COMPONENT_CANDIDATES.md` are not verified
  here.
- `no_missing_result_qualifies_candidate = true`: real clean-reference,
  authorized-listening, target-runtime-timing and codec/network-pipeline
  qualification remain `blocked`, so the task remains `incomplete` for real
  quality/availability decisions.

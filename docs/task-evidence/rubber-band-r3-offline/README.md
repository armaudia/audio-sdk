# SDK-RUBBER-BAND-R3-OFFLINE — task-local synthetic offline time-stretch evidence

**Status: `proposal_only_not_qualified` / incomplete. Decision: `DEFER`.**
No processor exposure. This is a self-contained, deterministic, synthetic,
whole-clip offline time-scale-modification (TSM) reference at a
protocol-v1-shaped task-local adapter boundary. It is **not** a Rubber Band
integration, not an SDK provider, not a default, not a public API/ABI change,
not a benchmark result and not a release qualification.

Task-pinned base: `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`; rebased onto
`origin/main` `2bc2a13aa4c5b398933fd9097d09746ce151216e` before final push;
branch `swarm/SDK-RUBBER-BAND-R3-OFFLINE`. Only files under
`docs/task-evidence/rubber-band-r3-offline/` were added. No shared
`CMakeLists.txt`, `CONTRACTS.md`, header, descriptor registry, default,
installed v0 behavior, board file, handoff, ruleset, other task, branch or
`main` was changed.

## Exact scope and boundary

- Installed v0 stays **16 kHz, mono float32, 160 samples/frame**. No new frame
  size, format, resampler, playback device, callback or native symbol.
- The engine consumes whole synthetic clips offline. There is no streaming
  first-output claim, no device pacing and no fill/flush measurement.
- `adapter.json` and `provider.json` describe a **disabled-by-default,
  unregistered, developer-only** boundary. There is **no C provider, CMake
  subtree, generated header, public registration or descriptor setting**.
- All stimuli are generated from a fixed LCG seed and analytic formulas in
  `fixture.py`. No recording, corpus, model, weight, third-party binary,
  download, audio device or listening result is read or claimed.
- Synthetic pitch and transient fields are numeric proxies. Authorized
  listening, intelligibility and naturalness remain open gates.
- Absent, withheld, invalid and adverse results are recorded with
  `candidate_qualified=false`; no missing result is promoted.

## Exact source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`; override with
`AUDIOML_ROOT`. `fixture.verify_source_pins()` and `run.py --sources` recompute
every digest; a missing or changed pin is a failure, never a skip.

| Pinned source | SHA-256 | Use |
| --- | --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | TSM/rate candidate provenance. |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Rate semantics, OLA/WSOLA context, varispeed contrast, final-window and queue caveats. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Offline-versus-streaming distinction and licensing provenance only. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | `rate` acceptance profile. |
| `audio-benchmark-platform/plan/swarm/check.py` | `5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539` | Read-only board validator. |

Unchanged public boundary pins:

| Header | SHA-256 |
| --- | --- |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

The mutable board snapshot read at setup
(`audio-benchmark-platform/plan/swarm/TASKS.json`) had SHA-256
`721c972afbce171752475a1f082f822b29b59c31cd22b3534124d481530f724a`.
It is provenance only and never qualifies this evidence.
`SOURCES.sha256` pins every local artifact except itself.

## Method

- OLA/WSOLA-style reference: 1024-sample Hann windows, 512-sample analysis hop,
  128-sample waveform-similarity search over ±32 source samples, overlap-add
  denominator normalization and a cumulative source→output sample map.
- Constant and piecewise source-timestamped rates are supported in `[0.8, 1.5]`
  with an 800-sample ramp. The unsmoothed rate-step control uses zero ramp.
- The target output length is `round(prefix[source_length])`. Identity is
  bit-exact passthrough. A terminal overlap-add window covers the last partial
  output window where required and is excluded from nominal coverage checks.
- Varispeed linear resampling and unsmoothed rate steps are adverse controls,
  never substitutes for the OLA/WSOLA candidate.
- Autocorrelation pitch and synthetic click peak/width are proxies on generated
  signals. The pitch proxy is octave-equivariant because chord autocorrelation
  can choose a different octave; fractional varispeed ratios remain visible.

## Rate-profile application

| Required item | Where it is recorded |
| --- | --- |
| Source/output mapping | Per-window nominal source intervals, monotone output centers, coverage and shift fields in each `cases.*.mapping` / `mapping_records`. |
| Duration | `cases.*.duration`: input, target, actual, error samples and relative error; all 16 cases have exact target length. |
| Pitch | `cases.*.pitch_proxy`: source/output frequencies, raw and octave-normalized scale; explicitly not listening. |
| Transient audibility | `cases.*.transient_proxy_comparison`: synthetic click peak and threshold-crossing width against an identity control; not listening. |
| Playback buffering | `cases.*.playback_buffering`: caller-owned FIFO checkpoints in source samples/ns, full frames, final partial valid samples and source-timestamped rebuffer gap. |
| 1× / faster / slower | `identity_1x`, `speed_up_125`, `speed_up_150`, `speed_down_080`, `speed_down_090`. |
| Unfamiliar speech / music / silence | `unfamiliar_speech` (synthetic pitch 190 Hz / formant 1180 Hz), `music_material`, `silence_case`. |
| Rebuffer / drift / final partial | `rebuffer_case`, `drift_case`, `final_partial_window`. |
| Pause/filler and speech preservation | `source_timestamp_policy`: frozen labels at source samples 0/4800/6400/11200/12800 with protect/flex decisions and mapped RMS preservation per labelled interval. |

Pause/filler decisions are tied to frozen source timestamps, never wall time,
playback position or a device clock. The labels are synthetic metadata, not a
real VAD/ASR gate.

## Results (all synthetic; overall DEFER)

- 16 cases, 12 with all applicable proxy checks passing, 2 explicitly adverse
  controls, 4 non-qualifying cases total; 13 invalid/missing controls observed.
  No candidate is qualified or exposed: the report decision is `DEFER`.
- Identity `19200 → 19200`; `1.25×` `19200 → 15360`; `1.5×` `19200 → 12800`;
  `0.8×` `19200 → 24000`; `0.9×` `19200 → 21333`. Every duration error is
  `0` samples.
- Pitch proxy on the 220 Hz tone: `220 → 220` Hz (scale `1.0`); music's raw
  scale `2.018` is octave-equivalent (`1.009`) and therefore not a pitch shift.
  Varispeed adverse control shifts `219.2 → 275.9` Hz (scale `1.259`) and does
  not qualify.
- Source-timestamp policy preserves protected synthetic speech intervals at
  `-0.005`, `+0.018` and `-0.056` dB mapped RMS ratio; flex intervals are
  reported separately and never used as speech-preservation evidence.
- Final partial input window is `12485` samples (not frame aligned); the
  buffered final output window carries `68` valid samples. `source_timestamp_policy`
  ends with a 5-sample partial valid window.
- Rebuffer at source sample `6400` (`400000000` ns) records a `1600`-sample
  uncompensated playback deficit with no fabricated compensation. Drift changes
  at four source-timestamped rates and still ends at exact target length.
- All outputs are finite with `0` clipped samples and peak `<= 0.9584`.

## Failure controls and explicit non-claims

- **Silence:** pitch proxy is withheld, not imputed; the case does not qualify.
- **Transient proxy regression:** candidate click width `102` versus identity
  `40` samples. This is an adverse measurement of synthetic OLA smearing, not a
  listening result; it remains a gate and is not widened to pass.
- **Varispeed adverse:** pitch shifts by `1.259×`; recorded as a non-qualifying
  control, not a TSM substitute.
- **Unsmoothed rate-step adverse:** transient width `101` versus identity `40`,
  zero ramp; non-qualifying.
- Invalid/withheld controls include nonfinite, infinite, empty and out-of-range
  samples; empty/nonfinite/zero/oversized/nonmonotone schedules; schedule without
  origin; unknown case; silence pitch; and missing rebuffer event.
- No target-device timing, pacing, CPU/deadline, RSS, fill/flush, listening,
  real-speech or music corpus, model, third-party runtime, public surface,
  provider registration, Bench bundle or release claim is made.

## Local artifact digests (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `adapter.json` | `3ae25bb80236a69635a0d389a84cbfe668d9ed197d3aded6da0aea538c309079` |
| `check_licensing.py` | `542af0227a8e2b8c8f23d67b5eeeae72a1d328239aa0923ecdedae31736dfc3a` |
| `contract.json` | `8f8c36d06c81d392808a6669c6d77424a0b56e107285001bf1292f931d35c63f` |
| `fixture.py` | `dda8381c0f12236947b28655054bf0a8e6b49adfacddb544bb551f8ebc9fc25a` |
| `provider.json` | `c8e528364ca40a483cfbba5a71b473f5fa9efaa1a2a65722777ea6b99dee7f8c` |
| `reference.py` | `da8771f412a284bde1aa4d99f270f606afa02d43d4d1126c2a2359fcc92bc40c` |
| `report.json` (file bytes) | `b9dda54f2ae86a200b1cfd251f56abb4f9d741ee28778145544650ea38fb10db` |
| `report.json.sha256` (file bytes) | `33f89c3044ad1da43211f6b83ec305b7653ffdfd23b40efaf976dc8d4e3a95de` |
| `run.py` | `87063c13551891212ed04fdc4abbc7c71ead464f8761f80779a7cfbb6e266a2a` |
| `scorer.py` | `00ab202c0665e682633749e9599753c35c21ed703b9838e959de92355dc716ec` |
| `test_reference.py` | `d326a0f8d4056735c4acd18ab4e35197af674903914fd48e419b67ddef1ac726` |
| `verify.py` | `2927b2d716fb4fe15d8aa25aa3c38eb16a38dbdea655fa105071dc0555c88f92` |

`README.md` is included in `SOURCES.sha256`; `SOURCES.sha256` excludes itself by design.

Canonical report digest (sidecar):
`dd22481c6617ec5eeaa8dac9b29017e10bed579f025cd6fb0a4be5addad6d5b8`.
Canonical core digest from three cold-start repeats:
`2e01a5e54e21843faaf5060fa1e4f967af951874bbd15e51cd77f798c7ea81fb`.
Regeneration is byte-identical with no tolerance widening or substitution.

## Reproduction

From this task directory (Python 3.11.5, stdlib only):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --crosscheck
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 check_licensing.py
python3 -m json.tool contract.json >/dev/null
python3 -m json.tool adapter.json >/dev/null
python3 -m json.tool provider.json >/dev/null
python3 -m json.tool report.json >/dev/null
```

`run.py --report` rewrites `report.json` and the sidecar byte-identically.
`verify.py` checks strict JSON (duplicate keys and nonfinite constants), all
pins, `SOURCES.sha256`, canonical bytes, three cold-start digests, three CLI
regenerations, SPDX coverage, licensing, scope and qualification guards.

From the worktree root:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-RUBBER-BAND-R3-OFFLINE
git diff --check
git diff --cached --check
```

SDK baseline build/install and CTest run outside the worktree:

```sh
tmp=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/rubber-band-r3-offline-check
cmake -S <worktree-root> -B "$tmp/build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$tmp/build" --parallel 4
ctest --test-dir "$tmp/build" --output-on-failure --timeout 60
cmake --install "$tmp/build" --prefix "$tmp/prefix"
```

REUSE 6.3.0 lint was run with the pinned environment. This package's files are
REUSE-clean when linted in isolation; all Python files carry SPDX headers and
no generated C header exists. At the final rebase, a full-repository
`reuse lint` was blocked only by pre-existing invalid SPDX expressions in
unrelated task-local files already on `origin/main`; this package added none of
them and does not modify those tasks. No build bytes are written inside the
worktree.

## Remaining gates

1. Rights-qualified unfamiliar speech and music material with authorized
   listening, intelligibility and naturalness scoring; synthetic proxies never
   substitute.
2. Exact target-device playback path with paced fill/flush, rebuffer recovery,
   drift correction and final partial window under the intended load.
3. A versioned variable-frame actuator or caller-owned TSM FIFO with explicit
   source/output timestamps outside the frozen v0 boundary.
4. Native boundary intake, rights/license review, descriptor/registry decision
   and independent review before any processor or default exposure.

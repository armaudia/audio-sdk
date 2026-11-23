# SDK-MEDIAN-RESIDUAL-CLICK-GATE · opt-in synthetic click-gate reference

**Status: synthetic, deterministic, opt-in, developer-only; not qualified.**
This is a 7-sample median-residual click gate wrapped at a task-local,
protocol-v1-shaped adapter boundary. It is **not** an SDK provider, public API,
ABI, descriptor, registry entry, default provider, benchmark bundle or release
result. The installed v0 format stays 16 kHz mono float32, 160 samples. No
model, weights, download, corpus, licensed runtime, listening test or
target-device measurement is included. No missing or unrun control is promoted
to a pass.

Pinned SDK base: `9677040cba2929f9936eaa565f200f585d5270a8`; branch
`swarm/SDK-MEDIAN-RESIDUAL-CLICK-GATE`. All files are under this one task-local
directory; no shared `CMakeLists.txt`, `CONTRACTS.md`, header, registry,
default, board/handoff or installed behavior is changed.

## Files

| File | Role |
| --- | --- |
| `adapter.json` | Unregistered opt-in descriptor; SHA-256 `0b4f32bed804331ee740d91f076fd531e62293df52a9672ff48894f0cc533bb1`. |
| `reference.py` | stdlib f32 detector/repair, 160-sample frame state, source-coordinate decisions, fail-closed controls. |
| `fixtures.py` | Deterministic synthetic material, rate plans, source pins and case digests. |
| `run.py` | protocol-v1 `inspect`/`run` request boundary with strict JSON, caller-owned input and four scenarios (`case`, `manual`, `adverse`, `state`). |
| `report.py` | Builds the canonical report only by driving `run.dispatch()`. |
| `report.json` | Canonical one-line rate-profile evidence report (299,710 bytes, terminal LF). |
| `report.json.sha256` | SHA-256 sidecar for `report.json`. |
| `test_fixture.py` | 30 offline `unittest` acceptance tests. |

## Source pins and what they establish

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`; set
`AUDIOML_ROOT` to override. `fixtures.verify_source_pins()` recomputes every
digest; a missing or altered file is a failure, not a skip. The shared mutable
board is provenance only and is not a frozen pin.

| Pinned source | SHA-256 | Use |
| --- | --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Record 38: partly evaluated, 0 false positives, misses all 0.20 and all width-5 clicks. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Line 95: transform RTF `0.000290` is source-reported, not reproduced here. |
| `research/voice-enhancement-20261101/agent-click-gate-expanded/REPORT.md` | `b8a42f9b0b782ad3aaa0be64da0d23b37c3c54b65a31caf252a4cd2ace88841e` | Normative width-7 reflect-median detector, threshold `0.35` and pointwise repair. |
| `research/voice-enhancement-20261101/agent-click-gate-expanded/expand_click_gate.py` | `98a9b283029f049458c513b07762943447757c17986e47cc67c80ad974cf78b2` | Exact stress protocol (widths 1/2/3/5, amplitudes ±0.20/0.40/0.75). |
| `research/voice-enhancement-20261101/agent-click-gate-eval/REPORT.md` | `ae4b0065eabbb62fe8880c7a04dee146415d463c5ae6676db6329147a901e1cc` | Initial one-sample screen and natural-event limits. |
| `research/voice-enhancement-20261101/agent-click-gate-eval/evaluate_click_gate.py` | `9195ddbdf7ea20da36fcd69ff72608b0eacefcee17cad7144cafbf37e0ff82e1` | Exact threshold/repair source. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate profile: mapping, duration, pitch/transients, buffering, rate cases, partial window. |
| `adapters/controls/adapter.json` | `3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599` | Public protocol-v1 envelope shape reused by the task-local descriptor. |
| `adapters/controls/run.py` | `4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66` | Public strict JSON/request validation pattern. |

## Method and boundary

- Detector: `abs(x - median of 7 reflected taps) >= 0.35` in source samples.
- Repair: detected interior samples are replaced simultaneously by the midpoint
  of their immediate source neighbors. Endpoint detections are counted but not
  repaired. This deliberately preserves the source's known failure envelope.
- Fixed v0 format is unchanged at the boundary: 16 kHz, mono, f32, 160-sample
  input frames. The task-local adapter declares a 3-sample trailing-lookahead
  buffering delay (`source_first_sample = frame_start - 3`); startup and final
  padding are flagged and excluded from valid content.
- One source clock domain: source sample `i` maps to `i * 62500 ns`. Every
  detection carries its exact source interval. The gate adds no samples, drops
  no samples, pauses nothing and inserts no filler.
- Playback rate plans are **schedule controls only** (piecewise integer
  source-sample → playback-nanosecond maps). They are not resampling, time
  stretching or pitch modification of the source-domain output. Perceptual pitch
  under faster/slower playback is not measured or claimed.
- Request validation rejects duplicate JSON keys, nonfinite JSON constants,
  unknown fields, malformed refs/config, nonfinite or wrong-shape input, stale
  epoch/session/source position, invalid final padding and invalid rate plans.

## Rate-profile evidence

`report.json` contains 21 case results (12 click-grid, 9 rate/control cases),
all produced through the `run` boundary. Each case records source and output
digests, full frame map, playback map, detection runs, preservation proxies and
`candidate_qualified: false`.

### Source/output mapping and duration

| Case / group | Source samples | Playback duration | Mapping result |
| --- | ---: | ---: | --- |
| 12 click-grid cases | 6,400 each (0.4 s) | 0.4 s each | Valid intervals union to `[0,6400)`, 0 gaps, 0 overlaps. |
| `speech_1x` | 6,400 | 0.4 s | Output digest equals source digest; 0 detections. |
| `speech_rate_125_080` | 6,400 | 0.385 s | 1x → 5/4 → 4/5 at source samples 1,600 and 4,800 (`100 ms`, `300 ms`). |
| `music_1x` / `music_rate_08` | 6,400 | 0.4 s / 0.5 s | Same source digest; 0 detections; percussion transients preserved. |
| `silence_1x` / `silence_drift` | 6,400 | 0.4 s / 0.399900024 s | Identity; 0 detections; drift segment 1,000,250/1,000,000. |
| `rebuffer_speech` | 6,400 | 0.48 s | 80 ms gap inserted at source sample 3,200 (`200 ms`); no content change. |
| `final_partial_speech` | 165 | 0.0103125 s | Final frame `source_first_sample=157`, valid `[157,165)`, `valid_count=8`, flag 2, 152 zero-padding samples. |
| `rate_change_partial` | 325 | 0.01825 s | 1x → 5/4 at source sample 160 (`10 ms`), final partial window. |

All 21 maps report `union_equals_source=true`, zero gaps and zero overlaps;
produced samples = delivered valid + startup padding + final padding. The first
output frame has `source_first_sample=-3` and `valid_offset=3`.

### Pitch and transient audibility controls

- Autocorrelation pitch proxy is computed on a deterministic click-free window
  selected from source labels. Available cases show `pitch_delta_samples=0`:
  `speech_1x` 116 → 116, `speech_rate_125_080` 146 → 146,
  `rebuffer_speech` 146 → 146, `rate_change_partial` 63 → 63 samples. The two
  short partial cases with no usable window are explicitly `applicable=false`;
  no pitch result is fabricated.
- Music-like percussion transients: 100% preserved (0 changed samples).
  Speech-like consonant transients: all preserved in `speech_1x`.
- Detection timestamps: all decisions equal `source_index * 62500 ns`; no
  time-based pause or filler decision exists.

### Click / suppression counts

Across the 12 click-grid cases: 96 true-positive samples, 0 false positives,
168 false negatives out of 264 labeled samples. Per-condition counts:

| Width (samples) | ±0.20 | ±0.40 | ±0.75 |
| ---: | --- | --- | --- |
| 1 | TP 0 / FP 0 / FN 8 | TP 8 / FP 0 / FN 0 | TP 8 / FP 0 / FN 0 |
| 2 | TP 0 / FP 0 / FN 16 | TP 16 / FP 0 / FN 0 | TP 16 / FP 0 / FN 0 |
| 3 | TP 0 / FP 0 / FN 24 | TP 24 / FP 0 / FN 0 | TP 24 / FP 0 / FN 0 |
| 5 | TP 0 / FP 0 / FN 40 | TP 0 / FP 0 / FN 40 | TP 0 / FP 0 / FN 40 |

This reproduces the documented failure envelope: width-5 pulses and low-amplitude
clicks are missed. It is not evidence of natural click or breath removal.

### Speech preservation proxy

- Clean synthetic controls (`speech_1x`, `music_1x`, `silence_1x`,
  `silence_drift`): 0 non-click samples changed; envelope correlation 1.0 for
  the non-silent cases. Silence envelope correlation is reported as 0.0 because
  the signal has no energy; no preservation claim is made from it.
- Click-grid SI-SDR versus the clean synthetic source is a paired developer
  proxy only. No STOI, intelligibility, listener score or natural-speech
  quality result is claimed.
- Key digests: click-grid source `e7d568d7eeed78e75493a775482dd99f21f6106b62fcf78a21f282243a42910d`;
  `speech_1x` source/output `cb2d19f35380028adf9f518e890537dcf510f1100eb45ab6038ab01cf911a4bd`;
  final partial output `dafee6ee3179a150cf37ac76adc77664b57990e077370c77c154743746348d8b`.

## Adverse and state controls

25/25 adverse controls are observed and rejected with unchanged functional
state: nonfinite input; wrong frame length/count; nonzero final padding;
unknown flags; stale epoch/session/source position; drain before final input;
process after final input; missing/unknown/invalid config (width, threshold,
rate, channels, format); four invalid rate plans; and two malformed requests.
State controls verify distinct session digests, no cross-session mutation,
rejection of stale decisions/frames, and successful strictly-greater-epoch
reset. No result is missing; `missing_result_qualifies=false` everywhere.

## Digests and reproduction

| Artifact | SHA-256 |
| --- | --- |
| `reference.py` | `2a26d4fd471e8764fb378a5149fcca70a9d27bb28a4b87160bc5d2f885255998` |
| `fixtures.py` | `14c128e7e029eb8ce266e05139664bdab93e2c98dbe4fc8c66f63d3fe8a3a6c7` |
| `run.py` | `83ba704d5ccf00ef5dab9bbdd7c170a5178d221372537eb4718fe260c0ac1eef` |
| `report.py` | `64bba80cb1e44930d0c1a8535c4c8e55fb597a77f9dcf03bc125fb640c449b5b` |
| `test_fixture.py` | `7c43dfda14c9c3bc3b3a3af16aa5cdaad921985a3c4fd3628b080e0aaf5c3cef` |
| `report.json` | `d3a619a280bc9a538f6bd1bb643d0919fab53e138a47275710f58c59ac509139` |
| `report.json.sha256` | `724a1328368636be11600c2898e6d6c74c1c12c619fa4305fce12a53d42b2f91` |

Runner recorded in the report: Python 3.11.5 stdlib only,
macOS-27.2.1-arm64-arm-64bit. From the worktree root:

```sh
evidence=docs/task-evidence/median-residual-click-gate
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-MEDIAN-RESIDUAL-CLICK-GATE
git diff --check

cd "$evidence"
PYTHONDONTWRITEBYTECODE=1 python3 report.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
python3 -m json.tool report.json > /dev/null
shasum -a 256 adapter.json reference.py fixtures.py run.py report.py \
  report.json report.json.sha256 test_fixture.py
```

Expected: `report.py` prints the two report digests above; regeneration is
byte-identical; 30/30 tests pass; JSON parses; all source pins verify from
`AUDIOML_ROOT`; `git diff --check` is silent and the board check reports the
claimed base/branch/worktree. Manual adapter use: write an `inspect` or `run`
request matching `report.py:standard_request()` to a file and call
`python3 run.py --request request.json --result result.json`; results are
developer output and are **not** an `audio_bench` bundle.

## Exact blockers and reopening conditions

This closes only the opt-in synthetic reference question. It does **not**
qualify a candidate, promote a default or authorize a release.

1. Natural click, breath, consonant and disfluency labels are absent; synthetic
   square pulses do not establish natural-event behavior.
2. No listening test or authorized human preservation score; envelope/SI-SDR
   proxies are not STOI or intelligibility.
3. No real weights, downloads, licensed runtime or model asset.
4. No target-device pacing, fill/flush, CPU/deadline, memory or availability
   result. The source-reported RTF `0.000290` is not reproduced locally.
5. No native provider build, installed public-header consumer, descriptor or
   registration evidence; no public ABI/API change was attempted.
6. No Benchmark bundle, publication entry, independent reviewer approval or
   board transition.

Reopen before any promotion: agree click/breath target definitions, preservation
and pitch/transient margins, buffering/fill/flush policy and deadline budget;
collect rights-cleared labeled natural material with independent scoring; build
the exact native provider through public registration and verify an installed
consumer; run the paced target workload; and complete independent review plus
separate contract/release work.

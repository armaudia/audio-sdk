# SDK-FIXED-RMS-VAD — deterministic fixed-RMS analysis fixture

**Status: proposal-only, model-free, synthetic; qualification `incomplete`.**
This is an opt-in developer fixture at a task-local, protocol-v1-shaped adapter
boundary. It is **not** an SDK provider, ABI/descriptor change, registry entry,
default, installed behavior, bench bundle or accuracy/qualification result.
SDK v0 stays fixed at 16 kHz mono `float32`, 160-sample frames. No real weights,
downloads, corpora, licensed runtimes, target-device or listening claims exist.

## Scope and boundary

- Task-local adapter descriptor: `adapter.json` (unregistered). Its boundary
  source is the public `adapters/rms-energy-vad/adapter.json` /
  `adapters/rms-energy-vad/run.py` fixed-threshold RMS detector, identity
  `rms-energy-vad-1-threshold-minus-42dbfs`.
- Two 160-sample SDK frames form one 320-sample RMS analysis window: the public
  adapter's 20 ms window is preserved without changing SDK frame geometry.
- Each SDK frame keeps its own exact half-open source interval. `source_time_mapping`
  is `identity`; declared analysis content delay is 0 samples.
- The timestamped `probability` is an **uncalibrated deterministic logistic
  transform** of window RMS with threshold −42 dBFS and 2 dB softness. It is not
  a model posterior. Threshold decisions use `probability >= 0.5`.
- `speech_event` source intervals are the union of contiguous active SDK frames.
  Availability is at the end of the first inactive SDK frame that closes a run
  (or stream end), with `available_ns = origin + end_sample * 62500` on clock
  `fixture-monotonic-v0`. Invalid/nonfinite/out-of-range analysis is never
  relabeled as nonspeech.

## Source pins (SHA-256)

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. The tests
verify all five files; a missing file is a failure, never a skip.

| Source | SHA-256 |
| --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `adapters/rms-energy-vad/adapter.json` | `b4801bbce2a9278940d107e43d696c5e0b5c0ee23f84967a5479be3c5767fc9e` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |

Pinned SDK base: `0673cb354cceb66f2f71faf9af7703b5a5d2fcfa`; branch
`swarm/SDK-FIXED-RMS-VAD`. The board is mutable provenance, not a qualification
source. Historical AMI figures (RMS FN 62.95%, FP 25.35%) are source-reported
desktop-baseline values and are **not** reproduced or confirmed here.

## Local artifacts and digests

| File | SHA-256 |
| --- | --- |
| `adapter.json` | `859cfd46a72f853d9ed5c765cf166d2972ab5950ea0bcbf5d2df536a0781f9d0` |
| `fixtures.py` | `28ae1211ec767811c954cef35758e009d31ae944d5fcabfe0fec7dcaebaf6930` |
| `reference.py` | `f275ad6fbadadc6d6aa222644c066302c9584230695b0236fa1cdf8e2d0aec9c` |
| `run.py` | `21210b08752317c0c1b49172b8ac146c18236009416ae1b1e29c8ccbde2c5953` |
| `report.py` | `a71582b4fb2a16c7636ad73c71f9e2c8647ea1f29091992fbed1f7b05c4eaad4` |
| `test_fixture.py` | `597f3cac148ba1473e81d9d97f98fa74d65c33d8c02e409db841bcfdd7229f9b` |
| `report.json` | `8baba230223816fea7792c76b7f971f2d289a587b5a03289063de7bde87e31fc` |

`report.json` is canonical JSON (sorted keys, compact separators, LF, 10,499
bytes). Report-internal digests:

| Name | SHA-256 |
| --- | --- |
| `fixture_spec` | `0ca64140c1c6bffcbba0df4a9a548df4b507dd36df4875e7a0a3eff35aacf47f` |
| `stream_f32` | `8254657969b6e6ec29542bda333d2ea072864a5bccde0fa3a825fb438a881812` |
| `primary_events` | `fd47f25eec0eaef60b2a64fdc8e65dcc221510dbef2c4ead0859126d71c4df16` |
| `primary_windows` | `905431b5c70aa80f3053426e8d310c4b10db9b696a258796888a1ca73a50a515` |
| `independent_left_events` | `29923f38fb468c393773f3cfc37c1fdf718907091ae02f4698b66d034f5d4d49` |
| `independent_right_events` | `9dc3fbd9b240d8ce05babf64ea78ae74a33fa6f18f4c25c5d0671c15b8ae6772` |

## Reproduction (Python 3.11.5, stdlib only)

From the SDK worktree root:

```sh
evidence=docs/task-evidence/fixed-rms-vad
scratch="${TMPDIR:-/tmp}/fixed-rms-vad-$$"
mkdir -p "$scratch"

# Regenerate canonical report and compare byte-for-byte.
cp "$evidence/report.json" "$scratch/report.json"
PYTHONDONTWRITEBYTECODE=1 python3 "$evidence/report.py"
cmp "$scratch/report.json" "$evidence/report.json"
shasum -a 256 "$evidence/report.json"

# Analysis fixture tests.
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "$evidence" -p 'test_fixture.py' -v

# JSON validity and local digests.
python3 -m json.tool "$evidence/report.json" > /dev/null
shasum -a 256 "$evidence"/*.py "$evidence"/adapter.json "$evidence"/report.json

# Optional direct adapter call (inspect).
python3 - "$evidence" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
request = {
    "protocol_version": 1, "operation": "inspect",
    "candidate_ref": {"kind": "reference", "id": "fixed-rms-vad.synthetic.v1", "revision": 1},
    "adapter_ref": {"kind": "adapter", "id": "fixed-rms-vad-reference", "revision": 1},
    "configuration": json.loads((root / "adapter.json").read_text())["configuration"],
}
pathlib.Path("inspect-request.json").write_text(json.dumps(request) + "\n")
PY
python3 "$evidence/run.py" --request inspect-request.json --result "$scratch/inspect.json"

# Scope and board checks from the worktree root.
git diff --check
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-FIXED-RMS-VAD
```

Expected: 18 tests pass; report digest
`8baba230223816fea7792c76b7f971f2d289a587b5a03289063de7bde87e31fc`; JSON
parses; five source-pin digests match; `git diff --check` is silent; board check
exits 0. Delete the scratch request afterward if desired; it is outside the
fixture directory.

## Synthetic results (analysis profile)

Frozen 16,000-sample stream (1 s), 100 SDK frames, 50 analysis windows, 50
timestamped probabilities, 2 speech events, 52 total events. The stream has 3
known speech segments (2,720 samples) and 4 known nonspeech segments (13,280
samples); all 16,000 samples are scored, with 0 unknown and 0 invalid samples.

| Metric | Exact value |
| --- | ---: |
| TP / FN / FP / TN (samples) | 1440 / 1280 / 480 / 12800 |
| Speech miss rate (FN / speech) | 0.47058823529411764 |
| False-alarm rate (FP / nonspeech) | 0.03614457831325301 |
| Detected hypothesis intervals | `[640,960)`, `[1920,3520)` |
| Speech event intervals | `[640,960)`, `[1920,3520)` |

Stratified checks: quiet speech `[320,1120)` gets TP 320 / FN 480 with onset
delay 480 samples and offset delay −160 samples; active speech `[1920,3040)`
gets TP 1120 / FN 0 with onset 160 and offset 0; below-threshold speech
`[3520,4320)` is a complete known miss (FN 800); loud idle noise `[3040,3520)`
is a known false alarm (FP 480); quiet idle tail `[4320,16000)` contributes TN
11680. Delay signs follow source coordinates: a negative offset means the
detection ended before the reference segment end. These are window-grid effects
on synthetic data, not physical or availability latency.

Validity, state and events:

- Frame and probability intervals each cover `[0,16000)` exactly once, with no
  gaps or overlaps; availability follows the 62,500 ns/sample formula.
- Two overlapping sessions with distinct epochs and streams have different
  event digests; resetting one leaves the other's summary unchanged. Old-epoch
  events are rejected in both.
- Dropping sequences 1 and 3 records two explicit gaps (2 dropped events); no
  event is fabricated to fill them. After reset, an old event cannot revive
  analysis; an invalid event is rejected with `invalid_event_validity`.
- Eleven adverse controls reject with unchanged state: NaN/Inf windows, short
  frame, short valid count without final, 48 kHz, 2 channels, `s16` format,
  double-size frame, stale epoch, bad source interval and nonzero final
  padding. A valid low-level frame is accepted and labeled nonspeech.
- `report.json` marks invalid controls separately from the primary scoring
  denominator; invalid never becomes a nonspeech label.

## Blocked work and non-claims

- **Matched cohort: blocked.** No rights-cleared held-out AMI cohort, label
  partition, frozen candidate outputs or the historical
  `data/runs/vad-chaining-ami-20261031-01/heldout-results.json` asset is
  available in this task scope. Source-reported FN/FP values are not reused as
  results. Reopen with a pinned cohort, exact candidate outputs and an
  independent scorer.
- **Intended execution profile: blocked.** No installed native SDK provider,
  pinned runtime, target device, deadline budget or matched workload is
  available. This fixture runs only a stdlib Python reference. Reopen with an
  installed provider and agreed availability/deadline budget with independent
  timing and state evidence.
- **No missing result qualifies a candidate.** Missing, rejected, unrun or
  blocked results are recorded as failures/incomplete, never counted as passes.
- No public API, ABI, `CONTRACTS.md`, `CMakeLists.txt`, descriptor, registry
  default, installed behavior, board/handoff or other worktree is modified.
  All files are confined to this task-local directory.

# SDK-D1-WHOLE-CLIP-DURATION-PLANNER · opt-in whole-clip duration planner reference

**Status: synthetic, deterministic, offline proposal-only, developer-only; not
qualified.** This is an exact-rational D1 rate planner wrapped at a task-local,
protocol-v1-shaped adapter boundary. It emits a source-to-playback schedule; it
does **not** resample, time-stretch, play, buffer or measure audio. It is **not**
an SDK provider, public API/ABI change, descriptor, registry entry, default,
bench metric, Bench bundle or release result. Installed v0 stays 16 kHz mono
float32, 160 samples. No model, real speech, licensed runtime, download, target
device, listening test or release claim is included. No missing or unrun control
is promoted to a pass.

Pinned base: `dc6b8ecb5c7fa0a6a00072ddf9c6a2e168b68acc`; branch
`swarm/SDK-D1-WHOLE-CLIP-DURATION-PLANNER`. Every file is under this one
task-local directory. No shared `CMakeLists.txt`, `CONTRACTS.md`, header,
descriptor registry, default, installed behavior, board file or handoff is
modified.

## Source pins and what they establish

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`; set
`AUDIOML_ROOT` to override. `fixtures.verify_source_pins()` recomputes every
digest. A missing or changed pinned file is a failure, not a skip. The shared
mutable board is provenance only and is not a frozen pin.

| Pinned source | SHA-256 | Use |
| --- | --- | --- |
| `cpp-library/pipeline-validation/playback-speed/README.md` | `a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f` | D1 rules: protected speech ≤1.0× with 0.8× floor, silence/filler ≤1.5×, duration identity, pause-budget fallback; recorded 0.95× fast and 0.86× filler floors and fixed_1.25/slow_only controls. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate profile: mapping, duration, pitch, transient audibility, 1×, rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial window. |
| `adapters/controls/adapter.json` | `3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599` | Public protocol-v1 envelope shape reused by the task-local descriptor. |
| `adapters/controls/run.py` | `4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66` | Public strict JSON / explicit-reference validation pattern. |

The recorded 0.95× and 0.86× numbers are source-reported prevalidation values.
The two `recorded_*` fixtures choose 95/15 and 43/21 protected/flex 100 ms block
counts so the exact D1 budget identity produces those rationals (19/20 and
43/50). This is a budget-arithmetic check, **not** a reconstruction of the
source corpus, gate, engines or listening results.

## Files

| File | Role | SHA-256 |
| --- | --- | --- |
| `adapter.json` | Unregistered opt-in descriptor; fixed v0 shape and offline-only buffering declaration. | `0c0cb57dbe63e2d24657ef88af41b4afa89a8e7bb0072635ea958b4e3284391b` |
| `reference.py` | Exact-rational D1 budget, source-timestamp rate blocks, drift/rebuffer maps, oracle variants and fail-closed controls. | `ffb59e3d09d7cef0580d73cf9772d6e69d0ddfb991457e7878ac4bf86cf7c253` |
| `fixtures.py` | Integer/rational fixture recipes, recorded values and source-pin verification. | `ccabb2de68e1cad016351d7d2a3931e3ef6d5202aede0b37a9585a50804bbf92` |
| `run.py` | protocol-v1 `inspect`/`run` boundary; `case`, `manual` and `adverse` scenarios with strict JSON. | `125cb998cdfa8a78593e56767b3b19e4d31fe9062812b01e495afe9f404c49b4` |
| `report.py` | Builds the canonical report only by driving `run.dispatch()`. | `8ca2debf1e4714d076d89d9ef02d15c7c6358770d128a83da67c4c9e3a5aa31e` |
| `test_fixture.py` | 33 deterministic offline `unittest` cases. | `c02b4f354d3b7906b59d1a4967a8a6a884353ca26a34bd8df3e6c297e962f00f` |
| `fixtures/stimuli.json` | Frozen cases, case digests, recorded reference and source pins. | `d817ab6729271d47ab200c9217729fcac36368da4abe26678827f26e275888c4` |
| `fixtures/report.json` | Canonical one-line rate-profile evidence report (624,741 bytes, terminal LF). | `522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98` |
| `fixtures/report.json.sha256` | SHA-256 sidecar for the report. | `0a58f693938dcbbb2dd0b1cc41e392379819b5d54a3ac618740d3fbaaf36a776` |

## Method and boundary

- One source clock: source sample `i` is at `i * 62500 ns`. Planning blocks are
  1600 source samples (100 ms); the final block may be shorter. The installed
  160-sample framing is represented in the final partial window, not changed.
- Protected labels are `speech`, `speech_like` and `music`; flex labels are
  `silence` and `filler`. Protected blocks get one uniform rate in `[4/5, 1]`;
  flex blocks get one uniform rate in `[1, 3/2]`.
- For protected duration `S` and flex duration `F`, full flex budget is
  `B = F - F/(3/2) = F/3`. The rate from full budget is `S/(S+B)`, clamped at
  the 0.8× floor. Required slowdown is `S(1/r_s − 1)`, and the balancing flex
  rate is `F/(F − required)`. Therefore planned playback is `S/r_s + F/r_f =
  S + F` exactly, in rational arithmetic. With no flex budget the planner
  falls back to 1× rather than extending the file.
- Every block record carries its source interval, source-ns interval, decision
  label, rate and cumulative playback interval. Rate changes are emitted only
  at block boundaries tied to source samples. No decision is made from wall
  time, device clock or playback position.
- Drift scales and rebuffer gaps are caller-supplied, source-timestamped
  schedule perturbations. They never change source samples. Uncompensated
  variants show the resulting duration error; `oracle_compensated` rebalances
  flex blocks within bounds when feasible and reports infeasibility otherwise.
- Buffering is declared as whole-clip: no plan exists until all source blocks
  and labels are available. This is a planning dependency, **not** a measured
  streaming latency, first-output time, fill/flush result or actuator behavior.
- Request validation rejects duplicate JSON keys, nonfinite JSON constants,
  unknown fields, malformed refs/config, nonfinite or wrong-shape case data,
  unaligned events, stale variant/case selection and malformed adverse IDs.

## Rate-profile evidence

All 23 case variants and 21 adverse controls were produced through the
boundary and are recorded in `fixtures/report.json`. Summary: 18 exact
duration-identity passes, 5 explicit nonidentity controls, 22 rate-bounds
passes (the sole bounds failure is `fixed_125`), 20 rejected adverse controls,
1 reported-infeasible oracle control, 0 missing results, 0 qualified candidates.

| Evidence item | Observed result |
| --- | --- |
| Source/output mapping | All 23 maps are contiguous in source block intervals, union to the source, with zero overlaps; playback intervals are exact rationals. |
| 1× control | `identity_all_speech/1x`: all rates 1/1, 0 rate changes, exact identity. `d1` on the same all-speech clip falls back to 1× with reason `insufficient_pause_budget`. |
| Recorded budget | `recorded_fast_budget/d1` plans speech 19/20 and flex 3/2; `recorded_filler_budget/d1` plans 43/50 and 3/2. Both match the recorded source floors and preserve duration exactly. |
| Floor clamp | `floor_limited_budget/d1` plans 4/5 speech and 28/19 flex; the pause budget is deliberately underspent rather than exceeding the flex ceiling. |
| Final partial window | `final_partial_window/d1`: source `[4800,4965)`, 165 valid samples = 1 full 160-sample SDK frame plus 5 valid tail samples; exact rational playback duration; identity holds. |
| Oracle labels | `gate_label_error` mislabels block 10 at source sample 16000 as speech; `oracle_labels` changes the rate decision at that timestamp and both plans keep exact identity and bounds. |
| Material changes | `material_transitions` uses speech, unfamiliar speech-like, music, silence and filler blocks; protected rates stay ≤1, flex rates ≤1.5. |
| Drift | `drift_interval/drift_uncompensated` misses identity by 93,750 ns; `oracle_compensated` restores identity by raising flex rate to 3200/2171, within bounds. |
| Rebuffer | `rebuffer_gap/rebuffer_uncompensated` adds 80,000,000 ns at source sample 6400; `oracle_compensated` restores identity with flex rate 100/73. |
| Infeasible oracle | `oracle_infeasible_gap/oracle_compensated` reports infeasible instead of fabricating a qualified result; the 2 s gap remains visible as duration error. |
| Explicit controls | `fixed_125` misses by −2.2 s and violates speech bounds; `slow_only` misses by +2.375 s. Neither qualifies. |
| Decisions/timestamps | Every rate change records `source_ns = source_sample * 62500`; drift and rebuffer events are pinned to block-boundary source samples. |

### Explicitly not measured

Pitch audibility and transient audibility are recorded as `not_measured with
qualifies=false`: this reference emits no stretched waveform. Realtime pacing,
fill/flush, CPU/deadline, RSS, target-device timing, listening, naturalness,
WER and release readiness are outside this evidence. The source README's RTF,
WER and listener statements are **not** reproduced here.

### Adverse controls

21/21 controls were observed: missing/unknown case, undeclared variant, wrong
control/sample rate/rate bounds, nonfinite and zero/oversized blocks,
noncontiguous blocks, unknown label, unaligned/overlapping events, invalid drift
scale and rebuffer gap, duplicate JSON keys, nonfinite JSON constant, missing
request field, invalid ref revision, and an infeasible oracle gap. Each result
includes `candidate_qualified=false` and `missing_result=false`; no absent
result is counted as a pass.

## Reproduction (from the SDK worktree root)

Use Python 3.11.5 stdlib only and `PYTHONDONTWRITEBYTECODE=1`.

```sh
evidence=docs/task-evidence/d1-whole-clip-duration-planner
board=/Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py

python3 "$board" --task SDK-D1-WHOLE-CLIP-DURATION-PLANNER
git diff --check

cd "$evidence"
PYTHONDONTWRITEBYTECODE=1 python3 fixtures.py --check
scratch="${TMPDIR:-/tmp}/d1-duration-planner-$$"
mkdir -p "$scratch"
PYTHONDONTWRITEBYTECODE=1 python3 report.py > "$scratch/report.json"
cmp "$scratch/report.json" fixtures/report.json
shasum -a 256 "$scratch/report.json" fixtures/report.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
python3 -m json.tool fixtures/report.json > /dev/null
```

Expected: four source pins verify; regeneration is byte-identical to
`522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98`;
33/33 tests pass; JSON parses; `git diff --check` is silent; board check reports
the claimed base, branch and worktree.

Manual adapter call (optional): write an `inspect` or `run` request matching
`report.py:standard_request()` to a file and call
`python3 run.py --request request.json --result result.json`. The result is
developer output and is not an `audio_bench` bundle.

## Exact blockers and reopening conditions

This closes only the opt-in synthetic D1 budget-identity question. It does not
qualify a candidate, promote a default or authorize a release.

1. Gate labels are synthetic. The source gate's IoU 0.94–0.95 and missed/false
   speech blocks are source-reported, not reproduced here; no Vosk or real word/
   filler/pause labels are present.
2. No actual rate/transient/pitch output exists; all playback intervals are a
   proposal. No listening, WER, STOI or naturalness result is claimed.
3. Drift and rebuffer are caller-supplied synthetic schedule events, not
   measured device clock or network behavior.
4. No target-device pacing, fill/flush, CPU/deadline, RSS or availability
   result; no native provider build, installed public-header consumer,
   descriptor registration or ABI/API change was attempted.
5. No Benchmark bundle, publication entry, independent reviewer approval or
   board transition.

Reopen before any promotion: agree coverage, metric margins, content delay,
availability, resource limits and deadline budget for the intended workload;
collect rights-cleared labeled real material with human-verified word/filler/
pause spans and independent scoring; implement and measure the exact actuator
and gate on the target device including fill/flush and final partial windows;
verify the native path through public registration and an installed consumer;
then complete independent review plus separate contract/release work.

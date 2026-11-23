# Peak limiter reference (opt-in developer fixture)

**SDK-PEAK-LIMITER-REFERENCE · DSP acceptance profile · status: opt-in,
synthetic, developer-only.** A deterministic Python reference of the documented
legacy stage is exposed through a protocol-v1-shaped, task-local adapter
boundary. It is **not** an SDK provider, ABI/descriptor change, registry entry,
default provider, bench metric, Bench bundle, or qualification result. Fixed v0
remains 16 kHz mono float32, 160 samples. No model, real speech, corpus, device,
host-timing or release claim is made.

## Source pins and what they establish

| Source (relative to `/Users/htsakanyan/workspace/audio/audioml`) | SHA-256 | Use |
| --- | --- | --- |
| `cpp-library/src/stages/limiter.cpp` | `fc4bb899f81e87466b3ad1aafea28ae392fed5ca10f4ea99bfde56f313079ac3` | Normative behavior: `ceiling` and `release_ms` settings, `(0,1]` / `(0,5000]` validation, copy fast path in the fully released sub-ceiling case, per-sample `ceiling/peak` target, one-pole release, double gain state, float32 clamp, `limiter_engaged` flag (`gain < 0.999999`), `reset()` to unity. |
| `cpp-library/src/stages/dsp_util.hpp` | `91efb8b16091c841da2e50225ae7b90b3ec7786aac1ef21e04bfe47672f882e9` | `smoothing_coefficient(t, sr) = 1 - exp(-1000/(t*sr))`; default 50 ms at 16 kHz gives `0.0012498964618064256`. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | DSP profile: sweeps, steps, impulses, silence, clean speech, load/intelligibility control, gain, response, attack/release, headroom, delay, numerical behavior, state transitions, nonlinear interactions. |
| `adapters/controls/adapter.json` | `3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599` | Public protocol-v1 envelope reused by the task-local descriptor (`inspect`/`run`, `candidate_ref`, `adapter_ref`, `configuration`). |
| `adapters/controls/run.py` | `4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66` | Public request validation pattern: strict JSON, no duplicate keys, no nonfinite JSON constants, explicit refs. |
| `audio-benchmark-platform/plan/swarm/TASKS.json` | `be5bf2f…` at initial read, `d336e52…` at report build | Shared mutable board; digest recorded as provenance in `fixtures/stimuli.json` (`task_board`), not treated as a frozen source pin. |

Pinned SDK base: `3e2192f5676ffe9d54fd5fc5b7c3710b4bb87f41`, branch
`swarm/SDK-PEAK-LIMITER-REFERENCE`. Source-pin verification is performed by
`tests/test_peak_limiter_reference.py` when the pinned paths exist; set
`AUDIOML_ROOT` if the checkout lives elsewhere. A missing pinned file is a
failure, not a skip.

## Boundary and files

- `adapter.json` — task-local, unregistered descriptor; SHA-256
  `97ca2c8e0b836d69bd5d467367e9b130207a2208b21d821d277b00f07de9d679`.
  Controls: `identity`, `peak_limiter_reference` with `ceiling` and
  `release_ms`.
- `reference.py` — stdlib float32 model with explicit config validation,
  `process()`, `reset()`, C++ `std::min`/`std::max` ordering for nonfinite
  values and bit-level float32 digests.
- `run.py` — `inspect`/`run` request/result boundary. `run` accepts a named
  fixture stimulus or a caller-owned `stimulus_samples` array with
  `reset_frames`; it writes canonical JSON to `--result`. Results are
  developer output, **not** an `audio_bench` bundle and not validatable by
  `python -m audio_bench validate`. No WAV, asset, model or download path exists.
- `fixtures/stimuli.json` — frozen geometry, source pins and eight synthetic
  stimuli (SHA-256
  `7a3073ba47586ff1db5764d6aa74f8ad35c2860ac333f8e5cb6ea49b985c7f55`).
- `report.py` → `fixtures/report.json` — canonical DSP report built solely by
  driving the adapter boundary. Report SHA-256
  `693890fed7e069fedfe240954c6b005251c60575462e44e9291afcdae4e7fad4`
  (one line, LF, 25,591 bytes; regenerate to confirm exact bytes).
- `tests/test_peak_limiter_reference.py` — 18 deterministic unittest cases.

Nothing outside this directory is modified. In particular no shared
`CMakeLists.txt`, `CONTRACTS.md`, public header, descriptor, registry, default
provider, installed v0 behavior, board file or handoff is touched.

## Reproduction (from the SDK worktree root)

Use Python 3.11.5 (stdlib only) and a fresh scratch directory:

```sh
evidence=docs/task-evidence/peak-limiter-reference
scratch="${TMPDIR:-/tmp}/peak-limiter-reference-$$"
mkdir -p "$scratch"

# Canonical report (stdout, no trailing spaces; one terminal LF).
PYTHONDONTWRITEBYTECODE=1 python3 "$evidence/report.py" > "$scratch/report.json"
cmp "$scratch/report.json" "$evidence/fixtures/report.json"
shasum -a 256 "$scratch/report.json" "$evidence/fixtures/report.json"

# Fixture/control tests, JSON validity and repository checks.
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "$evidence/tests" -p 'test_*.py' -v
python3 -m json.tool "$evidence/fixtures/report.json" > /dev/null
shasum -a 256 /Users/htsakanyan/workspace/audio/audioml/cpp-library/src/stages/limiter.cpp \
  /Users/htsakanyan/workspace/audio/audioml/cpp-library/src/stages/dsp_util.hpp \
  /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/VERIFICATION.md \
  /Users/htsakanyan/workspace/audio/audioml/adapters/controls/adapter.json \
  /Users/htsakanyan/workspace/audio/audioml/adapters/controls/run.py
git diff --check
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-PEAK-LIMITER-REFERENCE
```

Manual adapter call (optional):

```sh
python3 - "$evidence" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
request = {
  "protocol_version": 1, "operation": "inspect",
  "candidate_ref": {"kind": "reference", "id": "dsp.peak-limiter.ref", "revision": 1},
  "adapter_ref": {"kind": "adapter", "id": "peak-limiter-reference", "revision": 1},
  "configuration": {"control": "peak_limiter_reference", "ceiling": 0.98, "release_ms": 50.0},
}
pathlib.Path("inspect-request.json").write_text(json.dumps(request) + "\n")
PY
python3 "$evidence/run.py" --request inspect-request.json --result "$scratch/inspect-result.json"
```

Expected: report byte-identical (digest above), 18/18 tests pass, JSON parses,
five source-pin digests match, `git diff --check` silent, board check reports
`in_progress` with the claimed base/branch/worktree.

## Local results (synthetic only)

| Stimulus / control | Peak in | Peak out | Engaged frames | Fast-path frames | First modified sample |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sweep, ceiling 0.98 | 1.597809 | 0.980000 | 2 | 2 | 364 |
| Steps, ceiling 0.98 | 1.400000 | 0.980000 | 4 | 1 | 169 |
| Impulse, ceiling 0.98 | 2.099479 | 0.980000 | 66 | 0 | 17 |
| Silence | 0 | 0 | 0 | 2 | — |
| Clean-speech-like synthetic bursts | 1.107014 | 0.980000 | 4 | 6 | 1032 |
| LCG load control (0.9 amplitude) | 0.899825 | 0.899825 | 0 | 20 | — |
| Sub-ceiling tone (transparency) | 0.400000 | 0.400000 | 0 | 2 | — |
| Sweep, ceiling 0.5 | 1.597809 | 0.500000 | 4 | 0 | 145 |

- **Peak protection / headroom:** every finite over-ceiling stimulus is clamped
  to the configured ceiling. The double-precision clamp stored as float32 gives
  `f32(0.98) = 0.9800000190734863`, so reported headroom is `-1.9073486e-8`
  rather than exactly zero; tolerance and cause are recorded in the report.
- **Transparency:** the reference is bit-exact to identity on finite
  sub-ceiling frames while `gain_ == 1` (input, identity-output and
  reference-output digests all `9c1211e8…`). Once engaged, later sub-ceiling
  frames remain scaled until release; no unconditional transparency claim.
- **Attack / release:** first modified sample is the first over-ceiling sample
  (impulse 17). Recovery to the source's `0.999999` engaged threshold occurs at
  sample 10567 (≈0.66 s) for release 50 ms and at sample 228 (≈14 ms) for
  release 1 ms; release 5000 ms does not recover within the 1 s fixture. The
  source never restores `gain_` to exactly 1 without `reset()`.
- **Delay:** impulse peak sample 17 → output sample 17; content delay 0 and no
  lookahead. This is not an availability-latency measurement.
- **Intelligibility/load-specific control:** synthetic burst-envelope
  correlation is `0.99850` for the reference versus `0.84910` for a
  deliberately degraded hard-clip anchor; this is a developer proxy, not STOI
  or listening. The dense LCG load case stays below ceiling with 0 engaged
  frames; no host timing is measured or claimed.
- **State transitions:** with `reset` at frame 3, 4 fast-path frames and final
  gain 1.0; without reset, 2 fast-path frames and final gain 0.719756.
- **Interacting nonlinearities:** clip→limiter peaks at 0.5 with the limiter
  transparent; limiter→clip keeps 2 engaged frames upstream while the output is
  clipped to 0.5; cascaded ceilings 0.9→0.7 produce a finite `0.7`-bounded
  second stage. Exact output digests are in the report.

## Controls, adverse and skipped cases

- Rejected at the boundary: missing controls, unknown key, `ceiling = 0`,
  `ceiling = 1.5`, `release_ms = 0`, `release_ms = 5001`, string `"nan"`,
  float `Inf`, and a JSON `NaN` constant. All nine reasons are retained in
  `adverse_and_skipped.control_rejections`; none is silently defaulted.
  The pinned source itself defaults absent settings; this boundary deliberately
  fails closed instead.
- Nonfinite **input** (NaN at 5, +Inf at 165) is retained as
  `adverse_numerical_observed`: the pinned C++ `std::min`/`std::max` ordering
  yields finite clamp values (2 nonfinite inputs, 0 nonfinite outputs). This is
  an observation of the pinned code, not a robustness endorsement.
- Unreached recovery cases are recorded with `not_reached_within_fixture` and
  no fabricated recovery sample. No missing result qualifies a candidate.
- No established-baseline parity is claimed: `baseline_comparison.status` and
  `adverse_and_skipped.missing_baseline.status` are both `not_run`.

## Boundary and reopen conditions

This closes only the opt-in reference/descriptive DSP fixture question at the
pinned source. Reopen before any default promotion or claim of parity,
suitability or release:

1. Build and pin the matched native stage/SDK provider and an independent
   baseline from the exact source revision, with descriptor/config digests and
   an installed-archive check; compare frame-by-frame on a frozen cohort.
2. Agree on peak/headroom and preservation margins, recovery definition,
   content-delay and availability limits, workload/deadline budgets and failure
   budgets before qualification. Neither envelope correlation nor this LCG
   load case is an intelligibility, STOI or CPU-load result.
3. Use rights-cleared, matched real speech with independently scored quality;
   add device, rate, channel and interacting-chain coverage and independent
   review. No real-audio, model, device or release qualification is supplied here.
4. Any public registration, descriptor or default-provider change requires its
   own SDK contract, conformance and release-gate work outside this task scope.

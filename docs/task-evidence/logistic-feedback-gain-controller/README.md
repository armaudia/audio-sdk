# SDK-LOGISTIC-FEEDBACK-GAIN-CONTROLLER — optional logistic feedback gain reference

Task-local, deterministic DSP evidence for a logistic howl-risk detector and
feedback gain controller on the public v0 provider boundary. This is
**reference evidence only**: the installed SDK, its ABI, descriptors, registry,
defaults and frozen v0 behaviour are unchanged. No real speech/model weights,
downloads, licensed runtime, listening test, device timing or release
qualification is claimed.

## Scope and boundary

- Fixed v0 format only: 16 kHz, mono `f32`, 160 samples/frame. The pinned source
  screen uses 256-sample frames; this reference uses the same formulas at the
  public v0 frame size and records that deviation explicitly.
- Python reference: `reference.py` (dependency-free feature extraction,
  labelling, balanced logistic fit, threshold grid, closed-loop simulator and
  controller), `run.py` (deterministic report entrypoint) and
  `external_crosscheck.py` (external-only numpy/scipy formula cross-check).
- C reference: `provider/` (optional, unregistered provider source plus an
  opt-in CMake consumer test). It uses only `audio_sdk/provider_v0.h` and
  `audio_sdk/session_v0.h`; it is not built, registered or linked by default.
- Write scope is limited to this directory. No shared SDK file was modified.

## Source pins (SHA-256)

| Source | SHA-256 |
| --- | --- |
| `scripts/evaluate_feedback_control_ml.py` | `e6cd1903cce7724a15c6ef162b59b8fc27dbf1a80ba5e47ebaa66a3845276d04` |
| `scripts/evaluate_feedback_control.py` | `cde956dd584fc560063ac91e2725f36869cb3508c0a1e4fac00aa9fa3fd99e0c` |
| `scripts/evaluate_feedback_control_smard.py` | `c570ce9f33f0631864e10acc4d11ce02f1b4a7d6bc7c5fda167e3ae6fadcd28c` |
| `src/audioml_eval/feedback_control.py` | `a708b085320bc493fe975616bb2f9bb13d78745ec4df6c313c705f45f67e5cb3` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `api/include/audio_sdk/provider_v0.h` (boundary) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` (boundary) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

`audio-benchmark-platform/plan/swarm/TASKS.json` is mutable board state, not a
qualification source. Its read-time digest is recorded as a snapshot
(`571c352c0f5ecc09ed488f78a60b300ca28cecee83d14dedb1b3edae9bb4a005`) in
`contract.json` and must not gate results.

The pinned ML source trains a class-balanced logistic detector on AMI/SMARD
data with seven exact features, a 97-point threshold grid and a precision-first
selection rule; the source controller uses 2-frame persistence, −3 dB per event,
a −12 dB floor and slow +0.25 dB recovery. This evidence ports those exact
formulas to synthetic fixtures and 160-sample frames; it does not reproduce the
source report numbers.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `adapter.json` | `c82eb1c13c09be4c66f267a12c377f106458488bcb233666475a39147ca89882` |
| `contract.json` | `a89f72e9804741bff3734956d70dc4b21ef22ef33be055fb6b106e0c84a3c759` |
| `reference.py` | `b31229e58c3c7ed00fcc34d55cd4c9799465687eae59774f550bab6de0db98cd` |
| `run.py` | `b6f5c01afd52ef2361a38e75cdeaedcd4112f93a4d835bfd0570e046f3e1b6d2` |
| `test_reference.py` | `5323a582bf04aac8e16a3db471671c9d02b44acd8407726a7fa7a2de4808a8a3` |
| `external_crosscheck.py` | `f9f965b3077c057df98704bbd09317abeace2ba95a8bcb5170f3d507860c131e` |
| `crosscheck_vectors.json` | `2ab4de7d04732247b09dd5889d9398a00352e98631b488dc3b7ed47c2be630e3` |
| `report.json` | `73445d3ef8c79b9ec34f56d81797310d5a53366289a52824b325e726083ff23e` |
| `report.json.sha256` | `d2fd79029fe4221eb0e4976d8b46fb3fd39742afb85bacbf156b210ea4c1f308` |
| `model.json` | `060dc16dcbdc8a71506f1a4fc8c1ad33de9f6a4f31bd25d76eb6e70421dd99c9` |
| `provider/CMakeLists.txt` | `a4b645782c57e158bc5b4182be0f1887318e12a433c3221369a731adf0a93473` |
| `provider/logistic_feedback_provider.c` | `236193430b96a7ec7aca2b820599959f6a84a75ecaf65a3008706aeed44fe053` |
| `provider/config/config.json` | `ee4840a8f7e942ee977752fa8d4b5f52ec14547900a81b35cab1c4d5978b7c6f` |
| `provider/config/descriptor.h.in` | `0788422f075f0a3200c771f0aef626b10ea8ecf0946592df9307a2b88706a1b5` |
| `provider/tests/test_provider.c` | `95a312d3d41e63e53a61ece5ed36c96c0c713fcf52d606d0dbf9f42f1f257fc4` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`) and `report.json.sha256` is its canonical digest. The
`fixture_digest` inside the report
(`a9bac04e5968ffdcb9d6c532236bd731f28a94a303135006fe6402474d0d62cc`) pins the
fixture specification, and `model_digest`
(`060dc16dcbdc8a71506f1a4fc8c1ad33de9f6a4f31bd25d76eb6e70421dd99c9`) pins the
trained logistic model bytes. Regeneration is byte-identical and asserted by
`test_reference.py`.

## DSP evidence summary (synthetic)

All speech and feedback paths are seeded analytic resonators and synthetic
speech; no recordings are read. Values below are from `report.json`.

- Exact-feature cross-check: 7 features, 150 training frames and 150 held-out
  frames compared against the SHA-pinned numpy/scipy source implementation.
  Maximum absolute deltas: features `9.95e-14`, weights `6.66e-15`, intercept
  `1.33e-15`, mean `1.07e-14`, scale `8.88e-15`, selected threshold `0.0`,
  probabilities `4.66e-15`; detection counts equal. The report-generation path
  itself imports no numpy, scipy or soundfile.
- Training: 2700 frames (1893 positive) on two generated resonant paths;
  class-balanced L2 logistic regression, 600 gradient steps, 97-point threshold
  grid; selected threshold `0.04`; training precision `0.9406`, recall `0.9952`,
  F1 `0.9671`.
- Held-out detection: 4050 frames across three disjoint generated paths and
  loop gains 0.95/1.05/1.15; precision `0.9731`, recall `0.9968`,
  false-positive rate `0.0612` (2783 TP, 77 FP, 9 FN, 1181 TN).
- Closed-loop comparison (27 held-out runs each): identity median SDR
  `10.825 dB`, median tail output/speech `−16.619 dB`; fixed −5 dB median SDR
  `7.164 dB`, tail `−44.770 dB`; logistic gain median SDR `20.775 dB`, tail
  `−37.990 dB`, 52 median detection events; detection-only ablation matches
  identity audio with 52 events (ablation confirms the gain action, not just
  detection, drives the improvement). All runs: zero clipped, zero nonfinite,
  peak `< 1.0`, negative headroom, gain ≥ −12 dB.
- Stratified per-condition/gain tails are present for all nine cells; in the
  high-gain (1.15) low-resonance cell identity tail is `−1.131 dB` versus
  logistic `−35.693 dB`.
- Static fallback: missing, wrong-dimension, nonfinite, nonpositive-scale and
  bad-threshold models all fall back to fixed −5 dB gain (`0.562341`) without
  qualifying a result. Clean-speech detection events are zero for all profiles;
  identity/logistic clean-speech SDR is `null` (no attenuation) versus
  `7.177 dB` for fixed −5 dB.
- State/adverse controls: nonfinite frames rejected with state unchanged (2
  cases), reset replays exactly, sessions independent, partial frame length
  preserved, impulse added delay 0 samples, silence peak 0.0.

## Commands run (from the worktree root unless noted)

```sh
cd docs/task-evidence/logistic-feedback-gain-controller
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 /path/to/numpy-scipy-python external_crosscheck.py
```

Result: 19 Python tests passed; `--check` digest validation passed;
external cross-check passed with all deltas within tolerance.

Deterministic regeneration (`python3 run.py --report`) reproduces the committed
`report.json`, `model.json` and `report.json.sha256` byte-for-byte.

Optional C boundary check (SDK installed to a temporary prefix; both builds
outside the worktree):

```sh
cmake -S <worktree> -B <tmp>/sdk-build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build <tmp>/sdk-build --parallel 4
cmake --install <tmp>/sdk-build --prefix <tmp>/sdk-prefix
ctest --test-dir <tmp>/sdk-build --output-on-failure
cmake -S docs/task-evidence/logistic-feedback-gain-controller/provider -B <tmp>/provider-off \
  -DCMAKE_PREFIX_PATH=<tmp>/sdk-prefix -DAS_ENABLE_LOGISTIC_FEEDBACK=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build <tmp>/provider-off --parallel 2 && ctest --test-dir <tmp>/provider-off --output-on-failure
cmake -S docs/task-evidence/logistic-feedback-gain-controller/provider -B <tmp>/provider-on \
  -DCMAKE_PREFIX_PATH=<tmp>/sdk-prefix -DAS_ENABLE_LOGISTIC_FEEDBACK=ON -DCMAKE_BUILD_TYPE=Release
cmake --build <tmp>/provider-on --parallel 2 && ctest --test-dir <tmp>/provider-on --output-on-failure
```

Result: SDK 11/11 ctest passed; OFF build unlinked/unregistered 1/1 passed;
ON build registered two caller-local providers (logistic and static fallback),
applied gain action under a sustained tone, and passed fallback, reset/drain/
close, stale-position/epoch and nonfinite-frame checks, 1/1 passed. Built-in
provider queries were unchanged in both builds.

Read-only board check:

```sh
python3 <audio-benchmark-platform>/plan/swarm/check.py --task SDK-LOGISTIC-FEEDBACK-GAIN-CONTROLLER
```

Result: passed; component `logistic-feedback-gain-controller` is
`verification_profile: dsp`, `disposition: sdk-reference`,
`evidence_status: evaluated`.

`git diff --check` passed on the staged tree before commit.

## Adverse cases, skips and explicit non-claims

- Rejected controls: missing/invalid models (five cases) all fall back to fixed
  −5 dB; nonfinite frames rejected with state unchanged; wrong execution modes
  and stale epoch/position fail explicitly in the optional C check.
- No real recordings, measured loudspeaker/microphone path, real model assets,
  downloads, licensed runtime, listening test, target-device CPU/deadline
  measurement or release approval is included. The C provider is intentionally
  not installed, registered by default or added to any catalog.
- The mutable board digest is a snapshot only; board changes do not qualify or
  disqualify this evidence.

## Blockers

1. No real-speech or measured-path held-out cohort with pinned rights and
   labels.
2. No real model weights, licensed runtime or approved inference asset in this
   task-local scope.
3. No target-device CPU, memory, deadline, pacing or maximum-stable-gain
   measurement.
4. No provider intake, rights/license, descriptor catalog or public API review
   for a default or installed provider.

## Reopen / release gates

Reopen before any default or production claim:

1. Pinned real-speech and measured-path cohorts with disjoint train/held-out
   conditions, labels and rights review.
2. Held-out false-trigger and intelligibility/quality assessment, including
   double-talk and changing paths, with stated margins.
3. Target-device timing, CPU, memory, saturation, clipping and maximum-stable-
   gain evidence at the intended frame size.
4. Provider intake, license/notice, descriptor registry and public API/ABI
   review; only then consider a separate default-enablement change.

Until those gates pass, this directory remains optional task-local reference
evidence and the installed v0 behaviour stays frozen.

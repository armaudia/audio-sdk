# SDK-PHASE-VOCODER-BASELINE

**Decision: defer playback exposure.** This opt-in, model-free comparison
preserves the pitch of one synthetic tone but smears the transient and
displaces the tail. It runs only when called explicitly; there is no SDK
provider, default change, new ABI, asset, or licensed runtime.

## Scope and method

- Base: `cafa74a1c10fc9d5e927e76183e850277288aade`.
  Dependencies: `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`, `SDK-FND-PROVIDER`.
- [`adapter.json`](adapter.json) declares the task-local entry point.
  It uses the existing [`audio-sdk/elastic-pcm-packets/0.1`](../elastic-pcm-packets/README.md)
  **proposal fixture** for timestamped contiguous input, exact rational time
  maps, capacity, variable-count pulls and EOS. Map indices are nominal time
  coordinates, not attribution of individual spectral output samples.
  The installed v0 provider/session is intentionally not used for stretching:
  its fixed 160-sample process buffers cannot represent both shrink and
  expansion. No public variable-count playback actuator is installed.
- Original Python standard-library implementation of the baseline described in
  the candidate note §5.3 (Flanagan & Golden, 1966); no upstream code or test
  data copied. [`EVIDENCE.sha256`](EVIDENCE.sha256) pins that note and the rate
  acceptance profile; [`BOUNDARY.sha256`](BOUNDARY.sha256) pins the SDK
  fixture and installed-v0 header sources. Historical vendor and device
  figures are not used as measured results. The existing repository REUSE
  annotation covers this directory; no licensing exceptions are introduced.
- 16 kHz, mono normalized float32 PCM, at most 32,768 source samples per
  render. Centered and zero-extended 1024-sample periodic Hann windows with
  256-sample synthesis hops. At speed `r`, analysis centers are
  `round(output_center × r)`; per-bin unwrapped phase advance is converted
  from the actual analysis hop to the synthesis hop. Hann-squared overlap
  normalization, no phase locking, no transient reset. The last synthesis
  window covers the partial tail; padding is never returned as valid samples.
- Whole clip is held until flush. Each deliberate rate region resets phase,
  has `floor(input_count / r)` output samples and is trimmed independently.
  This preserves the proposal fixture's map but can accumulate a rounding
  deficit (`-9/5` samples for three 161-sample regions at 0.75/1.25/1.5×).
  It is not a clock-drift correction, continuous rate automation or streaming
  design.

## Results and failure controls

The frozen inputs are generated in `run.py`: 8,197 samples of a 437 Hz sine at
amplitude 0.2, an isolated 0.25 impulse at source index 4080 (and separately at
0 and 8196), and 161 zeros. No recordings or generated audio files are stored.
Comparison rates are 0.75×, 1×, 1.25× and 1.5×. Both methods receive the same
source samples, rates, duration rule and nominal map. The linear varispeed
control changes pitch; it is not an antialiased resampler. The unity identity
control is exact; the unity FFT render reconstructs within `1e-6` peak error.

| Rate | Output samples, both methods | Phase-vocoder tone (Hz) | Varispeed tone (Hz) | Impulse central 90% energy width, phase / varispeed (samples) |
| --- | ---: | ---: | ---: | ---: |
| 0.75× | 10,929 | 437.0003 | 327.7500 | 225 / 3 |
| 1× | 8,197 | 437.0000 | 437.0000 | 1 / 1 |
| 1.25× | 6,557 | 437.0005 | 546.2503 | 321 / 1 |
| 1.5× | 5,464 | 437.0009 | 655.5001 | 225 / 1 |

Pitch is measured by interpolated positive zero crossings after trimming 1024
samples at either end; the fixture check is ±1 Hz from the expected tone
frequency, **not** a release margin. The variance in impulse width and the
energy outside ±16 samples of the ideal position are proxies, not listening
results. At 1.25× the start impulse peaks at the expected sample; the tail
peaks 280 samples **early** relative to the trimmed nominal reference. These
are content offsets, not availability or device delays.

There is no output before flush. For the 1.25× clip, the first pull is only
possible after all 8,197 input samples have been admitted and flushed. The
6,557 pending output samples drain in 41 pulls capped at 160, ending with
157 samples and stable EOS; flush creates no extra admitted input. This
measures offline buffering in samples, not elapsed processing time. The
piecewise 1→1.25→0.75× step at source samples 3200 and 6400 emits 8,156
samples with exact regional counts and visible seams (adjacent-sample jumps
0.028953 and 0.331461); it is not a recommendation to switch abruptly.

Malformed rates/chunks, gaps, backpressure and nonfinite input are rejected
without consumption. Missing fixture inputs, source pins (when requested),
report drift and metric failures exit nonzero. A short, nonfinite or overrange
render fails before publication and the adapter exposes no partial PCM.
Expected adverse controls are recorded rather than discarded; neither those
controls nor the phase-vocoder result can report `candidate_qualified=true`.

## Reproduction

From the SDK root (`AUDIOML` is the common root containing `cpp-library/`
and `audio-benchmark-platform/plan/`):

```sh
export PYTHONDONTWRITEBYTECODE=1
D=docs/task-evidence/phase-vocoder-baseline
python3 -m unittest discover -s "$D" -p test_reference.py -v
python3 "$D/run.py" --check --source-root "$AUDIOML"
```

Expected: 5 tests; report SHA-256
`555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7`.
On a standalone SDK checkout omit `--source-root` to verify only the SDK pins
and synthetic results; this does not verify the external research provenance.
To regenerate the report, run without `--check` and redirect stdout to a
temporary file before comparing it with `report.json`.

Installed SDK regression is independent of the fixture. Follow
[the SDK build and test instructions](../../../README.md#build-and-test)
with a fresh output directory; this checks the unchanged package, not an
installed phase vocoder:

```sh
python3.12 -m venv "$TMP/env"
"$TMP/env/bin/python" -m pip install --require-hashes -r requirements-build.txt
"$TMP/env/bin/python" scripts/ci.py --output "$TMP/ci"
reuse lint
git diff --check
```

## Remaining rate-profile and release gates

No unfamiliar speech or real music, intelligibility/speech preservation,
pause/filler decisions, authorized listening, live rebuffer recovery,
device-clock drift, resource/deadline budget, or paced first-output and tail
delivery were tested. The offline `NOT_READY` state is not a rebuffer
simulation. Reopen for product use only with a versioned elastic playback
actuator, continuous rate changes, transient and pacing limits agreed in
advance, permitted matched speech and music with controls, and measurements
of clock/drain behavior, resources, availability and quality on the target.

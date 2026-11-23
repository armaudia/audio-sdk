# SI-SDR, SD-SDR and SNR developer evidence

**SDK-SI-SDR-SDR-AND-SNR · Evidence profile.** Proceed with the optional
[developer screen](compare.py); defer an SDK processor, API, runtime
dependency, or Bench metric registration. This is paired, analytic synthetic
evidence, not an enhancement result. The historical DNS pilot is retained
separately below.

## Scorers and controls

Use the [Bench scorer at `e623e14`](https://github.com/armaudia/audio-bench/blob/e623e14a4e85a6be7f6061aa50a30bb8824af132/src/audio_bench/metrics.py),
`zero-mean.v1` for `si_sdr_db` and `si_sdr_improvement_db`. The script checks
the scorer's SHA-256 and NumPy 2.5.4 from the Bench lock. Bench does not
register SDR or SNR at this pin. `local_sd_sdr_db` and `local_snr_db` are
diagnostics only and will not validate as Bench observations.

Let `s` be clean, `y` the estimate, and `x` the raw noisy input. All vectors are
mono float64 on the same fixed source interval. Let `s₀` and `y₀` be the
independently mean-subtracted vectors, `a = dot(y₀,s₀)/sum(s₀²)`, and
`p = a·s₀`. Scores are dB (higher is better):

| Score | Exact formula |
| --- | --- |
| SI-SDR | `10·log10(sum(p²)/sum((y₀−p)²))` |
| SI-SDR improvement | `SI-SDR(s,y) − SI-SDR(s,x)` |
| Local SD-SDR | `10·log10(sum(p²)/sum((y₀−s₀)²))`, the zero-mean variant of [scale-dependent SDR](https://arxiv.org/abs/1811.02508) |
| Local SNR | `10·log10(sum(s²)/sum((y−s)²))`, **no** centering, gain fit or RMS matching |

No filter-based BSS Eval SDR or generic `sdr_db` label. Fitting a filter would
answer a different question and is deferred. No resampling, normalization,
post-score lag search, epsilon, or ±300 dB score caps. Bench's null/reason
behavior is unchanged; the local metrics also use null/reason for zero
reference or exact reconstruction, and SD-SDR for zero projection. Local
SNR for a nonzero reference and a silenced estimate is a defined 0 dB. The
report includes `rms_gain_ratio` (estimate/noisy) to expose level changes
which SI-SDR ignores.

## Frozen validity, delay and aggregation

- Reuse the pinned SDK [positive handoff fixture](../../../conformance/evidence/positive/input.json)
  (340 valid / 500 produced samples, 16 kHz). Its source-valid union is
  `[0,340)` with a fully invalid startup block and a valid 20-sample drain.
  This is fixture metadata, not a processor output capture.
- A separate impulse at source sample 19 goes through the synthetic renderer
  before scoring. Its raw peak at sample 179 measures content delay of
  160 samples (10 ms), not availability latency. Check that raw valid offset
  minus source offset equals that measured delay; then use the source map
  **once**. Missing or inconsistent calibration and gaps fail closed.
  Neither clean scoring samples nor a candidate/reference similarity metric
  are used to find the delay.
- Freeze crops to `long=[0,340)` and `short=[1,161)`; the latter crosses a
  frame boundary. All scores and identity comparisons use those same
  half-open intervals (raw `[160,500)` and `[161,321)` respectively). NaNs in
  the deliberately poisoned, invalid startup do not enter the crop. A NaN
  **inside** the valid crop invalidates that observation.
- `compare.py` is the complete cohort definition: repeat orthogonal,
  zero-mean four-sample reference/noise patterns at amplitude 0.25; identity
  is the raw mixture with noise multiplier 0.5 or 0.25, not a clean-copy
  oracle. Reduce noise to 1/4 or 1/2 of the raw noise for the positive control;
  double it for the negative control. Half gain and DC offset independently
  change the noisy mixture. No third-party corpus, trained model or audio
  file is needed.
- One finite candidate-minus-identity dB delta per item and metric; arithmetic
  mean with equal item weight, no sample pooling, rounding before aggregation
  or bootstrap. Keep planned and paired counts, explicit included IDs and
  excluded IDs/reasons per metric. Missing output/reference is blocked;
  truncated output is failed; malformed geometry and nonfinite valid output
  are invalid. Partial means are diagnostics and cannot be ranked as a
  full-cohort result. No population inference from two synthetic items.

## Local results and reproduction

Mean paired deltas from identity, on macOS arm64, Python 3.12.16 and NumPy 2.5.4:

| Control | Paired / planned per metric | SI-SDR | Local SD-SDR | Local SNR |
| --- | ---: | ---: | ---: | ---: |
| Identity/noisy | 2/2 | 0.000 | 0.000 | 0.000 |
| Less noise | 2/2 | +9.031 | +9.031 | +9.031 |
| More noise | 2/2 | −6.021 | −6.021 | −6.021 |
| Half gain alone | 2/2 | 0.000 | −9.647 | −3.626 |
| DC offset alone | 2/2 | 0.000 | 0.000 | −5.000 |
| Missing `short` output (blocked) | 1/2 | +12.041 | +12.041 | +12.041 |
| Nonfinite `long` (invalid) | 1/2 | +6.021 | +6.021 | +6.021 |

The last two rows are partial diagnostics, not results better or worse than
the complete positive control. The metric disagreement under level change
is intentional; SI-SDR alone cannot validate gain preservation.

Use a Python 3.12 environment with the
[pinned Bench checkout and locked requirements](https://github.com/armaudia/audio-bench/tree/e623e14a4e85a6be7f6061aa50a30bb8824af132#development).
For the adapter use `PYTHONPATH="$BENCH/src"` (or an installation at that
pin) and run from the SDK checkout. Use a new scratch path for each output:

```sh
task=docs/task-evidence/si-sdr-sdr-and-snr
fixture=conformance/evidence/positive
python scripts/evidence_bundle.py create --input "$fixture/input.json" \
  --artifacts "$fixture/artifacts" --output "$SCRATCH/sdk-valid-region-handoff"
python scripts/evidence_bundle.py validate "$SCRATCH/sdk-valid-region-handoff"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$BENCH/src" \
  python "$task/compare.py" > "$SCRATCH/sdk-metrics-comparison.json"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$BENCH/src" \
  python -m unittest discover -s "$task" -p 'test_*.py' -v
```

The sealed input handoff validated `complete` (ID
`sha256:bbd3d6de15ca7f5e876d48397ec0257bf4adeb6b762ad2a5de9689bc985e5a18`).
The tests check the emitted report, including analytic values, negative and
excluded observations, invalid delay, full/partial bounds, perfect
reconstruction and silence. The JSON report itself is not an SDK handoff or a
Bench bundle. Two local generations were byte-identical (SHA-256
`78d86f3bf5d533aeab353cf3b97cb4a90d740bce9b8855687e3b87dc456ca1ac`).

### Independent Bench smoke (separate cohort)

In a scratch copy of Bench `e623e14`, `scripts/prepare_sdk.py` rebuilt Bench's
source-pinned SDK `84a102112ce83fb519303a832be15ad88e452d74` and refreshed
only the scratch package lock. The verified SDK archive SHA-256 was
`c983378d2636eb55995d5ef14c0cbafab96a34d26c8e4d649e0998a932e325ac`.
`scripts/ci.py` passed 146 Python and 2 native tests. Each smoke bundle
passed `python -m audio_bench validate`, with one sealed attempt, 24 cases,
168/168 observations, and 24/24 finite values for each registered SI-SDR
metric. Removing a required source map from a copy of the Speex bundle
failed validation (exit 1; inventory/payload mismatch).

| Run | Bench run ID | Descriptor check |
| --- | --- | --- |
| Source runner, high-pass | `cb0132a6-47d4-4354-935f-11e9052befac` | Sealed descriptor matched driver |
| Source runner, Speex NS | `db65313b-a66d-443c-b79c-f63ebfcc9748` | Sealed descriptor matched driver |
| Relocated wheel, high-pass | `8a141614-fc76-4ac0-8658-726ab3cc7028` | Stale sealed descriptor; functional smoke only |

The relocated bundle sealed `6fcf3621a8d31ba6fe1eaed191ca4dcf71987718dd135b773925092dbac1219f`
against actual driver descriptor `d664ddc7977b5ff193e184b12dca48f3923675e8a7f0d4feb79781b0ca7c77e3`
(SHA-256, excluding terminal LF). Validator success does not resolve this
provenance mismatch. Standalone SDK conformance on the rebuilt Bench package
independently measured high-pass delay 0 and Speex NS delay 160, with
0-sample residual in the mapped valid output for both. These are content
delays of that exact installed package, not availability. None of the
24-case Bench runs is matched to the two-case developer screen, to this
task's SDK base, or to the historical DNS cohort.

## Historical evidence (not rerun)

The source-reported `research/noise_suppression_pilot_20261027.md`
and `scripts/evaluate_noise_suppression.py` are pinned by SHA-256 in
[Bench's source inventory](https://github.com/armaudia/audio-bench/blob/e623e14a4e85a6be7f6061aa50a30bb8824af132/deps/source-inventory.json).
The pilot used 30 paired DNS2020 no-reverb synthetic mixtures, IDs
`0, 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 17, 19, 20, 21, 23, 26, 33, 34, 35, 37, 38, 42, 43, 44, 45, 47, 48, 49, 50`.
It is an exploratory subset, not a representative or independent holdout.
The historical scorer used raw waveform SNR, centered SI-SDR with
degenerate ±300 dB sentinels, and non-extended STOI (pystoi 0.4.1); it did not
report SD-SDR. The comparison used identity/noisy input and per-item
candidate-minus-identity deltas, mean/median, wins/ties/losses, and 10,000
independent item bootstrap replicates (NumPy PCG64, first four big-endian
bytes of SHA-256 of `CLN-01-exploratory:{candidate}:{metric}`, percentile
2.5/97.5). No independent-speaker inference. Wrapper alignment differs by
candidate (e.g. DTLN 384 and WebRTC 96 samples measured against noisy input);
those scores do not establish SDK valid-interval compliance or availability.

As reported, ROSE-CD's raw output improved mean SI-SDR by **5.9347 dB** but
reduced mean SNR by **12.0866 dB**. Its separately named offline input-RMS
match gave **+5.0862 dB** mean SNR with the same SI-SDR. Its batch timed out
after 29 outputs and the last clip was retried; comparable runtime metrics
were not available. FFmpeg `afftdn` was a configuration-specific negative
control (mean SI-SDR delta **−44.9806 dB**). None of these is a local SDK
score. The separate 743-recording EARS DNSMOS screen was no-reference
predicted evidence; neither it nor human listening was run here or combined
with the paired DNS results.

## Remaining gates

Before any workload or release claim: approve corpus/reference rights and a
frozen matched cohort, measure content mapping and availability independently
for the exact build and target config, pre-agree metric and preservation
margins, resource/deadline and failure budgets, and collect and independently
review sealed results. Decide whether a distinct SDR definition or metric
registration belongs in Bench before adding one. No runtime timing,
model/corpus reproduction, listening, or suitability claim follows from
this screen.

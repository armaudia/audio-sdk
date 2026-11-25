# SDK-SPEEX-ONE-PREPROCESSOR-OPTIMIZATION

**Recipe-owner result:** One pinned Speex preprocessor can run NS and optional
AGC and report advisory speech probability without a second analysis pass.
It is **not** a drop-in replacement for separate serial NS and AGC: the state
sees a different signal, the aligned waveform changes, and the content delay
changes. Keep AGC off and do not use Speex activity to gate, route, or skip work.
This is a task-local synthetic reconstruction; the installed SDK is unchanged.

## Source and rights

- SDK base `cafa74a1c10fc9d5e927e76183e850277288aade`; SpeexDSP 1.2.1
  (`7a158783df74efe7c2d1c6ee8363c1e695c71226` plus the SDK's documented
  hardening). `run.py` checks the committed `deps/speexdsp-files.sha256` pin
  and every listed file before building a private floating-point SmallFT
  library. It uses the vendored public preprocessor header and real native
  state, not a substitute algorithm or host-installed Speex. See the
  [source and notices](../../../third_party/speexdsp/UPSTREAM.md).
- Historical reading: C++ research tree `3e2446fc58886fc02b099b54651adc9a10a65454`,
  `pipeline-validation/README.md`, `run_basic_speex.py`, `speex-side-vad/report.md`,
  `speex-agc/report.md` and `PIPELINE_DESIGN_REPORT.md`. The former Basic recipe
  uses 320 samples at 16 kHz, NS −20 dB, activity 65/50, and a final 0.98
  sample-peak limiter; the AGC toggle uses target 8000. Those controls are
  retained. The earlier reused AMI diagnostic reported a 68.84% false-positive
  rate with or without NS; that figure is historical, not reproduced here.
- The Pipeline profile in `plan/swarm/VERIFICATION.md` and the Basic recipe
  in `plan/audio-sdk/PIPELINES.md` inform the controls. This isolates Speex
  and the final limiter; the recipe's optional high-pass and RMS tap, AEC,
  routing and graph integration are not part of the comparison. No third-party
  runtime, audio recordings, weights, corpus, download or private dataset is
  needed or reproduced. Generated inputs are PCM16 at the Speex boundary, not
  an alternate SDK format or an installed v0 ABI claim.

## Matched comparisons

| Variant | Audio path | Advisory |
| --- | --- | --- |
| `identity` | Exact PCM16 bypass | None |
| `separate` | NS → AGC → limiter | Independent Speex on a copy of the raw input; output PCM discarded |
| `common` | One NS + AGC state → limiter | `GET_PROB` and Boolean return from the same `speex_preprocess_run` hop |
| `no_ns`, `no_agc` | Disable only that feature in `common` | Same-state |
| `no_advisory` | Same as `common`, VAD flag off and no probability read | None |
| `no_limiter` | Same as `common`, no final limiter | Same-state |
| `fallback` | Continuous NS → limiter (no AGC) | None |

Each run gets fresh state; no state is carried between sessions or variants.
The raw tap runs inline before publishing output, but it is not on the audio
path and adds no content delay. AGC is computed after spectral suppression in
the common state; the separate AGC state instead receives already synthesized
NS PCM. Removing advisory export does not remove Speex's internal probability
calculation. A common hop makes one preprocess call instead of three in this
specific separate comparison; it does not establish the savings over modern
detectors or over an already-shared NS-only implementation.

The same 22,473 accepted samples are used in each ablation at 160 and 320
samples/hop (SDK geometry and historical geometry, respectively). The generated
reference varies silence, quiet/loud two-tone sections and level transitions.
The mixed version adds seeded broadband noise and 61 Hz hum, including
noise-only sections. This is a diagnostic with exact synthetic labels, not real
speech or detector calibration. A partial final input has 73 valid samples.
Audio alignment is fixed before scoring: separate buffers two hops; common
and fallback buffer one. A staged impulse test independently checks the
position and tail. The replay records startup as invalid, releases the remaining
source content with bounded zero flush, and checks the delivered interval union
against accepted content. The flush is a harness operation, not native SDK drain.

## What the synthetic control found

- Shared and independent advisory flags agreed on the scored mixed windows.
  That is not a useful gate: at 160 samples they marked **30/48** noise-only
  windows active and missed **19/38** quiet surrogate windows; at 320 samples
  they marked **23/23** noise-only windows active. Only windows fully contained
  in one known label count; startup, mixed boundary, pad/flush and invalid
  events do not become negatives. No calibrated probability or onset accuracy
  is inferred.
- Active AGC changed the waveform and performed worse than AGC-off in the
  source-aligned synthetic SI-SDR control at both hops, for both mixed and clean
  inputs. For example, the mixed 160-sample replay scored 10.56 dB bypass,
  5.98 dB separate, 5.84 dB common, and 13.12 dB common AGC-off. These numbers
  describe this generated stimulus only, not speech quality. Removing advisory
  export left audio byte-identical. The final limiter did not engage in this
  cohort; a separate forced-peak test exercised it.
- Private replay separates native per-stage **call wall time** (including
  the Python FFI call, not CPU) from inline service time (copy, calls, policy,
  limiter and slicing), and from paced release-to-ready and source-to-ready.
  The simulated complete-hop release is `(i+1) × hop` on one monotonic clock,
  including the zero-padded final hop and bounded paced flush, with a
  one-hop deadline after release. There are no queues, workers, or hardware
  buffers. Ready time means available inside this harness, not DAC output or
  callback latency. No timing, capacity or device claim is made.

## Failure and reopen policy

Treat failed or out-of-range `GET_PROB` as **unknown**, never as nonspeech;
continue the same audio path. An unexpected process return fails the replay,
discards that epoch and releases each state. Do not silently substitute a
backend, re-use failed state or switch the content offset midstream. The
recipe owner can explicitly choose the NS-only/limiter fallback in a fresh
epoch; if NS itself is unavailable or fails, close/report and only then use
an explicit identity route in a fresh epoch if the host policy permits it.
Missing, unbuildable or mismatched native source is a hard execution gate for
this fixture, not a reason to run a smoother in its place.

Reopen for promotion only with a frozen rights-approved matched speech/noise
cohort, pre-agreed preservation and level/headroom margins, validity-labeled
quiet onsets/noise and independent detector acceptance if the tap affects
policy, plus installed graph lifecycle and target-paced deadline/availability
evidence. This does not change any default, descriptor, ABI, registry or build
entry. No public benchmark entry, device result, or release qualification.

## Reproduce

From the SDK checkout with Python **3.12.16**, a macOS/Linux C compiler and a
fresh private `$SCRATCH` outside the checkout:

```sh
export PYTHONDONTWRITEBYTECODE=1
python -m unittest discover -s docs/task-evidence/speex-one-preprocessor-optimization -v
python docs/task-evidence/speex-one-preprocessor-optimization/run.py --paced --output "$SCRATCH/replay"
python scripts/ci.py --output "$SCRATCH/installed"
```

Use the SDK's hash-pinned `requirements-build.txt` for the installed checks.
The private replay writes 48 trace files and a report with input/reference/output
hashes and build provenance. On each paced replay it requires identical PCM
and advisory values to the matched unpaced replay; clock values are not
reproducible bytes. Reports, libraries and raw traces stay out of Git.

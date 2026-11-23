# Fixed six-band spectral tilt — synthetic DSP evidence

Candidate: `sixband.tilt.reference.v0` · profile: dsp · status: **evidence_complete_synthetic_only**.

Task-local optional reference behind the public provider_v0/session boundary. Not installed, not a default. The source study's whole-clip energy restoration is replaced by a smoothed causal power follower; the receiver-side comparison uses an explicit energy-matched control.

## Six-band sweep / stepped gains

Measured gain is the probe-to-anchor amplitude ratio after processing divided by the same ratio before processing. The anchor is a 750 Hz sine in the 0 dB band (500-1000 Hz); the global power follower cancels in this ratio.

| band | target dB | probes | mean measured | max abs error |
| --- | ---: | --- | ---: | ---: |
| 1 | -3.0 | 2 | 0.7225 | 0.0277 |
| 2 | -1.5 | 2 | 0.8575 | 0.0332 |
| 3 | 0.0 | 2 | 1.0190 | 0.0398 |
| 4 | 1.5 | 1 | 1.1885 | 0.0000 |
| 5 | 3.0 | 2 | 1.4125 | 0.0000 |
| 6 | 4.0 | 2 | 1.5848 | 0.0000 |

Across 11 probes the maximum absolute gain error is 0.0398 linear.

## Response, delay, headroom and numerical controls

- Impulse: peak at input sample 800 and output sample 800; measured content lag 0 samples; output peak 1.126789 (-1.04 dB); block-stamped buffering delay 160 samples with 160 startup-padding samples.
- Step: 50% crossing lag 0 samples; plateau level error -1.06 dB versus the input step level; pre-transition ringing peak 0.004119.
- Silence peak 0.000000; tiny-signal peak 0; nonfinite outputs 0.
- Level steps: per-segment RMS ratio 0.802–1.159; settled mean 1.006.

## Clean/masker-like preservation

| stimulus | input RMS | output RMS | RMS ratio | output peak | headroom dB |
| --- | ---: | ---: | ---: | ---: | ---: |
| clean_a | 0.105886 | 0.105992 | 1.0010 | 0.660086 | +3.61 |
| clean_b | 0.105918 | 0.105961 | 1.0004 | 0.670546 | +3.47 |
| clean_c | 0.105889 | 0.105962 | 1.0007 | 0.688757 | +3.24 |
| masker_receiver | 0.149959 | 0.148706 | 0.9916 | 0.643257 | +3.83 |
| near_clip | 0.196012 | 0.196209 | 1.0010 | 1.221927 | -1.74 |
| clipped | 0.098738 | 0.098393 | 0.9965 | 0.430917 | +7.31 |

Band-gain shape error on these broadband stimuli: max 0.0179 linear relative to the 500-1000 Hz band.

## Receiver-side masking fixture and energy-matched control

The masker is added **after** target processing at −5, 0 and +5 dB target-to-masker RMS ratio. Each condition mixes the same masker waveform with four target variants: unprocessed identity, tilt, a scalar-only control matched to the tilt RMS, and a deliberate +1 dB level-only control. Reported values are per-band target-plus-masker excess above masker-only energy in dB. They describe energy distribution only; they are not STOI/ESTOI, intelligibility or a listener-benefit result.

| method | RMS vs identity | mean Δ band 5 excess (dB) | mean Δ bands 1-2 (dB) |
| --- | ---: | ---: | ---: |
| identity | 1.000000 | +0.000 | +0.000 |
| tilt | 1.000697 | +0.123 | -0.289 |
| energy_matched_gain | 1.000697 | +0.000 | +0.003 |
| level_confound | 1.122018 | +0.013 | +0.563 |

Tilt output RMS / identity RMS averaged 1.000697; the scalar-only control is matched to that measured RMS by construction. The +1 dB control is an intentionally unmatched negative control: its near-uniform band excess shift shows why level matching is required before interpreting the tilt comparison.

## Controls, blockers and scope

- Provider registration/lifecycle/adverse CTest: True (OFF and ON builds).
- Coverage True; collisions 0; out-of-range samples 0; unity-peak exceedances 4.
- Missing clean-reference control: passed (a missing clean reference is not scored and cannot qualify the candidate).
- All required results present: True; all controls passed: True; no missing result qualifies the candidate.

- The source study's whole-clip FFT energy restoration is noncausal; this reference uses a causal 160 ms/80 ms smoothed power follower, and exact clip-level matching is applied only in the control.
- The source study reports STOI/ESTOI on EARS and VADToolkit speech; none of that data or scoring is reproduced here. These synthetic band-excess values are not intelligibility scores.
- No listening panel, listener profile, MOS, real-speech STOI/ESTOI or held-out benchmark is claimed.
- Unity-peak exceedances from energy restoration are recorded as a headroom risk; no limiter, DRC or release configuration is qualified by this evidence.
- No target-device timing, CPU/deadline, memory, licensed runtime, model weights, downloads or release qualification measured.
- No shared CMakeLists.txt, CONTRACTS.md, descriptor registry, default, public API/ABI, installed v0 behavior, board, handoff or main-branch change is included.

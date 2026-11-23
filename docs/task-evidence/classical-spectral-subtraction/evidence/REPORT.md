# Classical spectral subtraction — synthetic task evidence

Candidate: `css.reference.v0` · profile: enhancement · status: **evidence_complete_synthetic_only**.

Scope: task-local optional reference behind the public v0 provider registration boundary. Not installed, not a default, no real weights, no downloads, no licensed runtime, no listening and no release qualification.

## Paired synthetic cohort

| item | identity SI-SDR | CSS SI-SDR | Speex SI-SDR | identity STOI* | CSS STOI* | Speex STOI* |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| a | 5.015 | 6.074 | 7.174 | 0.838 | 0.788 | 0.770 |
| b | 5.010 | 6.181 | 6.788 | 0.840 | 0.789 | 0.777 |
| c | 2.922 | 4.749 | 5.531 | 0.814 | 0.765 | 0.720 |

Means: ΔSI-SDR CSS +1.352 dB, Speex +2.182 dB; ΔSTOI* CSS -0.050, Speex -0.075.

*STOI is the pinned synthetic `stoi_screen` envelope-correlation scorer, not standard STOI and not comparable with pilot values.

## Controls and integrity

- Registration/lifecycle/adverse CTest: true.
- Nonfinite outputs: 0; maximum absolute output peak: 0.667086.
- Coverage: True; delay 160 samples; startup padding 1120 samples; final padding counted 0 samples.
- Missing clean-reference control: passed (missing clean reference is not scored and cannot qualify the candidate).

## Clean-speech preservation

CSS on clean synthetic fixture a: ΔSI-SDR 16.922 dB, STOI* 0.911, RMS ratio 0.818.

## Scope and blockers

- No real weights, model downloads, licensed runtime or vendor claim; implementation is first-party C.
- No real speech, listening test, MOS or real-speech STOI; only deterministic synthetic pairs.
- STOI is a pinned synthetic envelope-correlation screen, not standard STOI or pilot-comparable; it may decrease even when SI-SDR improves and is reported without a pass/fail gate.
- Historical pilot values (mean ΔSI-SDR +1.31 dB, batch RTF 0.0505) were not reproduced here; the tested whole-clip noise estimate is noncausal and is not used in this causal reference.
- No target-device pacing, CPU/deadline, memory RSS or release qualification measured.
- Fixed state is a single calloc'd instance; no dynamic allocation after create; no numeric workload timing is claimed.

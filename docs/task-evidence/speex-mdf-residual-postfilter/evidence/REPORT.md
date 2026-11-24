# SDK-SPEEX-MDF-RESIDUAL-POSTFILTER — synthetic paired evidence report

Status: **optional, unregistered, default-OFF reference tooling only**. No AEC,
double-talk quality, listening, device, pacing or release claim. The frozen
canonical report is `report.json` (SHA-256
`ad15c446442058b82c003f15527637edae02a819a2033b0f289bc89042b170b6`, identical
as canonical bytes and file bytes).

## Frozen room profile

- 16 kHz mono f32, 160-sample frames, 300 frames (48,000 samples) per stream.
- 3,200-sample (200 ms) MDF filter; 512-sample fixed echo delay; frozen three-tap
  path `[0.30, 0.45, 0.25]` × `0.40`; no movement and no path switch.
- Seeded LCG render/noise and an analytic near-end tone surrogate; no corpus,
  WAV, model, RIR, download or licensed runtime is read.
- Echo-only, near-end-only, 20 ms overlap, withheld-reference and
  one-frame-misaligned-reference conditions are frozen in `fixture.py`.
- No reset within a case; fresh MDF and postfilter state per case and repeat.
- Denoise, AGC, VAD and dereverb are disabled; residual echo suppression is
  bound to the same MDF state with `ECHO_SUPPRESS=-40` and
  `ECHO_SUPPRESS_ACTIVE=-15`. The postfilter is created only under
  `--postfilter`; the flag is absent by default.
- Metrics are withheld where not meaningful (silent render or no near in the
  scoring window). Twenty withheld fields across the ten rows are recorded as
  missing results; none is imputed and no row qualifies.

## Paired comparison: MDF alone vs MDF + optional postfilter

`ERLE` is measured on frames 80–139 (converged, far-end only). `near ratio` is
`sqrt(sum(out²)/sum(near²))` on the fixed 20 ms window at frames 150–151; in
`overlap_20ms` it contains residual echo, so it is an upper bound on near-end
preservation, not a preservation pass.

| Condition | Variant | ERLE (dB) | Near ratio | Near attenuation (dB) | Peak | Nonfinite | Output SHA-256 (all 3 repeats) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `echo_only` | `mdf_only` | 15.675997 | withheld | withheld | 0.123718 | 0 | `3a3310f606710dea5ee82ca95566b8af4837401b4d46c38b89114a9333a4a30e` |
| `echo_only` | `mdf_postfilter` | 15.590018 | withheld | withheld | 0.123718 | 0 | `92d50a21dc7ceb854eec7c97a6d6efc1fb65d7a1b7c59f121c12ae496124e5ec` |
| `near_end_only` | `mdf_only` | withheld | withheld | -0.0 | 0.130571 | 0 | `943a0e882a93bc968805eae509035eba1b1806beb79318e95e16ea229ee4b897` |
| `near_end_only` | `mdf_postfilter` | withheld | withheld | -0.0 | 0.130571 | 0 | `943a0e882a93bc968805eae509035eba1b1806beb79318e95e16ea229ee4b897` |
| `overlap_20ms` | `mdf_only` | 15.675997 | 0.968517 | withheld | 0.123718 | 0 | `0c7ae1b579a9a5da19cbe63fd29fde24834869bace45c9aa5d3a44873feebb68` |
| `overlap_20ms` | `mdf_postfilter` | 15.590018 | 0.687357 | withheld | 0.123718 | 0 | `8a07f69b147caada149f9157ef6126ff3793b492deb0d191c6c8d530ef0e298f` |
| `no_reference` | `mdf_only` | withheld | withheld | withheld | 0.146505 | 0 | `052ab702d73e94e3fdd8910821908194a3d7c1fb0f50acc4271146e0469b79a6` |
| `no_reference` | `mdf_postfilter` | withheld | withheld | withheld | 0.146505 | 0 | `052ab702d73e94e3fdd8910821908194a3d7c1fb0f50acc4271146e0469b79a6` |
| `misaligned_render` | `mdf_only` | 16.884243 | withheld | withheld | 0.112885 | 0 | `5b3b81dbffe32a1b3beb006276601de6afc190fc806dff4d4dca93f753ef01e7` |
| `misaligned_render` | `mdf_postfilter` | 16.837898 | withheld | withheld | 0.112885 | 0 | `e47aa277ff8e5cf8f139abb24a5fef1529b9cf4c31a4a1611b6b55e17094103c` |

Every row was executed three times with byte-identical output digests. The
entire core was also rebuilt three times with identical canonical digest
`ce86680b8a683084850884ebb5fcb91b0b4d66503e80e30c4173458edc6c4cc5`, and three
independent `run.py --report` regenerations reproduced `report.json` byte for
byte.

## Decision: keep the postfilter OFF

- Overlap near ratio falls from `0.968517` (MDF alone) to `0.687357` (postfilter),
  delta `-0.281160`. Far-end ERLE changes only from `15.675997 dB` to
  `15.590018 dB`, delta `-0.085979 dB`.
- The near-only case is bit-exact passthrough under the zero-render policy, so
  its `-0.0 dB` attenuation is a control, not a preservation measurement.
- Near-end preservation against MDF alone is therefore **not recovered**. The
  postfilter remains optional, default OFF, unregistered and not recommended.
  Nothing here enables it in a provider, descriptor, catalog or installed SDK.

## Merged MDF caveats (disclosed, not reproduced as an oracle)

From `speexdsp-mdf-reference/evidence/REPORT.md`: aligned ERLE `16.453939 dB`,
one-frame-misaligned ERLE `16.888932 dB`, and 20 ms overlap near ratio
`0.985161`. ERLE is not an alignment detector. The local misaligned case also
measured *higher* ERLE (`16.884243 dB`) than the aligned case
(`15.675997 dB`), so alignment must be enforced by the caller. The overlap near
ratio includes residual echo and is not a double-talk quality result. These
merged numbers are provenance/disclosure only; this task's oracle is the frozen
report above.

## Negative and positive controls

| Control | Result | Passed |
| --- | --- | --- |
| Nonfinite capture sample | exit 3, no output file | yes |
| Capture one sample short | exit 3, no output file | yes |
| Unsupported rate (`48000`) | exit 2, no output file | yes |
| Missing render file | exit 4, no output file | yes |
| Positive echo-suppress level | exit 2, no output file | yes |
| Unknown CLI option | exit 2, no output file | yes |
| No `--postfilter` flag equals MDF-only digest | identical | yes |
| Withheld render passthrough | bit-exact in both variants | yes |
| 20 external source/boundary pins + 9 legacy blobs | exact match | yes |

No failure was treated as a score and no missing output was filled in.

## Remaining gates

1. Rights-qualified paired real-speech room cohort with frozen RIRs, delay,
   movement, noise and capture-clock drift.
2. Agreed preservation, ERLE, alignment, availability and nonfinite margins with
   an independent scorer and sealed review.
3. Paced target-device CPU, memory, deadline and buffer/backpressure evidence.
4. Provider, ABI, license and default-policy intake. Until all four pass, this
   directory stays task-local, default-off tooling evidence and no benchmark,
   product or release claim is made.

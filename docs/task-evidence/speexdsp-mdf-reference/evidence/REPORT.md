# SDK-SPEEXDSP-MDF-REFERENCE — synthetic paired evidence report

Status: paired synthetic reference tool only. No AEC, double-talk quality,
listening, device, real-audio, performance or release claim. The frozen oracle
is `oracle.json` (SHA-256 `c1e1c232cb80d344fe6a1131ebf80caf112cd68e2baad9a2543ee8ccc1e08411`).

## Frozen protocol

- 16 kHz, mono, 160-sample frames, 300 frames (48,000 samples) per stream.
- 3,200-sample (200 ms) MDF filter, 480-sample (30 ms) fixed echo delay,
  frozen three-tap path `[0.35, 0.50, 0.15]` × `0.45`, no movement.
- Seeded LCG render/noise plus analytic near-end tone surrogate; no file asset
  or recording is read.
- Full fixture generation, CLI execution, metric calculation and negative
  controls are repeated **three times**. Every repeat produced byte-identical
  output digests and the regenerated canonical report is byte-identical to the
  frozen `oracle.json`.
- Source pins are checked against `SOURCES.sha256` before any score is emitted;
  a mismatch aborts. Exact legacy Git blobs are checked against
  `LEGACY_BLOBS.sha1` and direct `git rev-parse` at
  `3e2446fc58886fc02b099b54651adc9a10a65454`.

## Paired render/capture cases

`ERLE` is measured on frames 80–139 (converged, far-end only). `near ratio` is
`sqrt(sum(out²)/sum(near²))` on the fixed 20 ms window at frames 150–151; in
`overlap_small` that window also contains residual echo, so it is an upper
bound on near-end preservation, not a preservation pass.

| Case | Render/Capture | ERLE (dB) | Near ratio | Peak | Nonfinite | Output SHA-256 (all 3 repeats) |
| --- | --- | --- | --- | --- | --- | --- |
| `echo_only` | active render / echo + noise | 16.453939 | 0.171306 (no near present) | 0.133636 | 0 | `4b6b1ba808f3f3919aa6f64dcec1661545208d0e382cb9199ff2a5a6d5ac63eb` |
| `near_end_only` | silent render / near-end only | 0.0 | 1.0 | 0.147248 | 0 | `0559befd3a5c3fe44d67f2c93a26e4df4b27ebba2c9a501dcd1a2551c491da05` |
| `overlap_small` | active render / echo + 20 ms near-end burst | 16.453939 | 0.985161 | 0.133636 | 0 | `abb6cdc25f2371ecbeac05ef6ba564d51adf0c66390da09091948f23d2ab9327` |
| `no_reference_passthrough` | withheld render / echo + noise | 0.0 | 1.0 | 0.149149 | 0 | `198eaadb2fb1eed9db1fab8f99e58608cd33c84f55c3ff3aea6d2c1d4fcb82d5` |
| `misaligned_reference` | render shifted one frame / echo + noise | 16.888932 | 0.159131 (no near present) | 0.133636 | 0 | `a1fa383eacc50cde77e8881a0369b67fe09f233b0f8a76769ad0734d2f1ab71b` |

Near-only and no-reference cases are bit-exact passthrough by the documented
zero-render policy; their `near ratio = 1.0` is a control result, not echo
cancellation. Peak values are below 1.0 and every valid output has exactly
48,000 samples with the expected content position (no added delay).

## Measured limitations (disclosed, not hidden)

- A one-frame reference shift did **not** reduce measured ERLE
  (`16.888932 dB` versus `16.453939 dB` aligned). This tool therefore does not
  validate render/capture alignment; alignment must be enforced by the caller.
- The 20 ms overlap case shows `near ratio = 0.985161` including residual echo.
  It does not reproduce the source-reported severe near-end damage from the
  optional residual echo suppressor, which this adapter does not enable. No
  double-talk, convergence-rate or suppression-quality conclusion follows.
- The fixture is a stationary three-tap echo path with tiny synthetic noise.
  It does not exercise room impulse responses, movement, capture-clock drift,
  nonstationary noise or long double-talk windows.
- The exact oracle is scoped to this pinned source set, Apple clang 21.0.0 and
  the observed host; it is not a cross-toolchain or cross-platform guarantee.

## Negative controls

| Control | Result | Passed |
| --- | --- | --- |
| Nonfinite capture sample | exit 3, no output file | yes |
| Capture one sample short | exit 3, no output file | yes |
| Unsupported rate (`48000`) | exit 2, no output file | yes |
| Missing render file | exit 4, no output file | yes |
| Tampered source digest manifest | `ValueError`, no report emitted | yes |
| Zero-render passthrough | output digest equals capture digest, bit-exact | yes |
| Pinned legacy blobs (`7`) | git blob IDs match exact files and legacy checkout | yes |

No failure was treated as a score and no missing output was filled in.

## Remaining gates

Default-off, task-local evidence only. Before any product, default, quality or
release claim: rights-qualified paired real-speech room cohort with frozen RIRs
and delay/movement/drift; agreed preservation, ERLE, alignment and availability
margins; paced target-device CPU/memory/deadline measurement; independent
review; provider/ABI/license intake. No public benchmark entry is implied.

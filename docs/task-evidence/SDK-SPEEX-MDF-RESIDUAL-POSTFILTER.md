# SDK-SPEEX-MDF-RESIDUAL-POSTFILTER — evidence summary

Task scope: optional, task-local Speex MDF residual postfilter reference for the
duplex pipeline workstream. **Paired synthetic tooling only** — not an AEC,
double-talk, quality, device, listening, pacing or release claim.

Full protocol, pins, digests, commands and disclosure:
[speex-mdf-residual-postfilter/README.md](speex-mdf-residual-postfilter/README.md)
and [evidence/REPORT.md](speex-mdf-residual-postfilter/evidence/REPORT.md).

## Exact scope

- Base `941cabfc39f7e33f01881b6e50e3a1e49e7eb9ce`; branch
  `swarm/SDK-SPEEX-MDF-RESIDUAL-POSTFILTER`.
- New files only under `docs/task-evidence/speex-mdf-residual-postfilter/` plus
  this summary. No shared CMake/CI/header/ABI/provider/default/board edit.
- Standalone adapter option `AS_ENABLE_SPEEX_MDF_RESIDUAL_POSTFILTER` defaults
  **OFF**; OFF and ON configurations were both verified. The CLI's
  `--postfilter` flag is also absent by default. No provider is registered.
- Nine exact legacy Git blobs at commit
  `3e2446fc58886fc02b099b54651adc9a10a65454`, including `mdf.c`,
  `preprocess.c` and both public headers, are compiled in place from the
  SDK-vendored tree pinned by `deps/lock.json`
  (`7a158783df74efe7c2d1c6ee8363c1e695c71226`); no substitution or tolerance
  change. Installed SDK build ID unchanged:
  `audio-sdk/0.1.0+sha256:0bc71dcab04880033a4ad4c1cfcebb8a05eccb11a20a786b9c844e394c035972`.

## Frozen evidence and decision

- Canonical oracle: `speex-mdf-residual-postfilter/report.json`, SHA-256
  `ad15c446442058b82c003f15527637edae02a819a2033b0f289bc89042b170b6`
  (canonical bytes equal file bytes).
- Five paired render/capture conditions × two variants (MDF alone, MDF plus
  optional postfilter), **three byte-identical repeats each**, nine controls,
  20 external pins and nine verified legacy blobs. No missing result was
  scored; 20 withheld metrics are recorded.
- Measured: converged echo-only ERLE `15.675997 dB` (MDF alone) versus
  `15.590018 dB` (postfilter); 20 ms overlap near ratio `0.968517` versus
  `0.687357`. Near preservation against MDF alone was **not recovered**.
- Decision: **DEFER**; postfilter remains optional, default OFF and
  unregistered. No enablement, no quality, double-talk or device claim.
- Disclosed merged MDF caveats: one-frame-misaligned ERLE `16.888932 dB` versus
  `16.453939 dB` aligned; 20 ms overlap near ratio `0.985161`. ERLE is not an
  alignment detector. No adverse Tiny16 comparison is made.

## Checks

Adapter OFF configure/build: passed (no target). Adapter ON build + CTest 2/2.
Python unit tests and strict JSON/schema checks passed. Full verify: exact
oracle regeneration, three report-core repeats and three byte-identical
`run.py --report` regenerations. Baseline SDK CTest 11/11 with unchanged build
ID. Board check exit 0; `git diff --check` clean. All fixture/build bytes stayed
in caller scratch outside the worktree.

## Remaining gates

Rights-qualified paired real-speech room cohort with frozen RIRs/delay/
movement/drift; agreed preservation/ERLE/alignment/availability margins and
independent sealed review; paced target-device resource evidence; provider,
ABI, license and default-policy intake. No default, production, benchmark or
release claim is made.

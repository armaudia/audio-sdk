# SDK-SPEEXDSP-MDF-REFERENCE — evidence summary

Task scope: optional, task-local SpeexDSP MDF reference adapter for the duplex
pipeline workstream. **Paired synthetic reference only** — not an AEC,
double-talk, quality, device, listening or release claim.

Full protocol, pins, digests, commands and disclosure:
[speexdsp-mdf-reference/README.md](speexdsp-mdf-reference/README.md) and
[evidence/REPORT.md](speexdsp-mdf-reference/evidence/REPORT.md).

## Exact scope

- Base `d665c298e8cce8b4d576dc45f3c7f7d3b3457425`; branch
  `swarm/SDK-SPEEXDSP-MDF-REFERENCE`.
- New files only under `docs/task-evidence/speexdsp-mdf-reference/` plus this
  summary. No shared CMake/CI/header/ABI/provider/default/board edit.
- Standalone adapter option `AS_ENABLE_SPEEXDSP_MDF_REFERENCE` defaults **OFF**;
  OFF and ON configurations were both verified.
- Seven exact legacy Git blobs at commit
  `3e2446fc58886fc02b099b54651adc9a10a65454` are compiled in place from the
  SDK-vendored tree pinned by `deps/lock.json`
  (`7a158783df74efe7c2d1c6ee8363c1e695c71226`); no substitution or tolerance
  change. Installed SDK build ID unchanged:
  `audio-sdk/0.1.0+sha256:0bc71dcab04880033a4ad4c1cfcebb8a05eccb11a20a786b9c844e394c035972`.

## Frozen evidence

- Canonical oracle: `speexdsp-mdf-reference/evidence/oracle.json`, SHA-256
  `c1e1c232cb80d344fe6a1131ebf80caf112cd68e2baad9a2543ee8ccc1e08411`.
- Five paired render/capture cases (echo-only, near-end-only, 20 ms overlap,
  no-reference passthrough, one-frame-misaligned reference), **three
  byte-identical repeats each**, zero nonfinite outputs, five negative controls
  and seven verified legacy blobs. No missing result was scored.
- Measured: converged echo-only ERLE `16.453939 dB`; 20 ms overlap
  output/near RMS `0.985161` (includes residual echo); misaligned reference
  still `16.888932 dB` ERLE. Near-only/no-reference are bit-exact passthrough
  controls. These are tool observations, not quality gates.
- Disclosed limitation: one-frame reference shift is **not** detected by ERLE;
  the small-overlap result does not reproduce source-reported residual
  suppressor near-end damage; static three-tap synthetic path only.

## Checks

Adapter OFF configure/build: passed (no target). Adapter ON build + CTest 1/1.
Python unit tests 16/16. Full verify: exact oracle regeneration, 5 cases × 3
repeats, 5 controls, 7 blobs. Baseline SDK CTest 11/11, unchanged build ID.
Board check exit 0; `git diff --check` clean. All fixture/build bytes stayed in
a scratch directory outside the worktree.

## Remaining gates

Rights-qualified paired real-speech room cohort with frozen RIRs/delay/
movement/drift; agreed preservation/ERLE/alignment/availability margins and
independent sealed review; paced target-device resource evidence; provider,
ABI, license and default-policy intake. No default, production, benchmark or
release claim is made.

# SDK-PIPE-DUPLEX · task-local synthetic duplex pipeline

**Status: proposal-only, synthetic, task-local and incomplete. No AEC,
double-talk, listening, quality, device, paced-workload, public benchmark or
release result is claimed.** This directory is one opt-in host/recipe example
under `docs/task-evidence/`. It composes the already-merged, unmodified SpeexDSP
MDF reference CLI with the already-merged capture arithmetic into:

```
capture + timestamped far-end render
  -> reference validation / integer-frame alignment
  -> pinned SpeexDSP MDF (merged CLI, default-OFF option)
  -> Speex NS policy surrogate -> sample-peak limiter
  -> optional task-local residual-suppressor policy surrogate
```

No shared source, ABI, public header, provider registry, SDK default, CMake or
CI file is changed. No audio, model, asset, corpus, build output or native byte
is committed. All fixture renders and CLI outputs live in a caller-supplied
scratch directory outside the worktree.

## Pinned inputs

| Pin | Value |
| --- | --- |
| SDK base / parent | `45b1b82a021ba350ee9e419013df146785b2f426` / `c41814bc0ea39151c29ca83fbde9267ccc063493` |
| Branch | `swarm/SDK-PIPE-DUPLEX` |
| SpeexDSP | `1.2.1`, revision `7a158783df74efe7c2d1c6ee8363c1e695c71226`, vendored, no network fetch |
| MDF CLI source | merged `docs/task-evidence/speexdsp-mdf-reference/adapter/src/mdf_reference_cli.c`, unchanged |
| MDF adapter CMake | merged `docs/task-evidence/speexdsp-mdf-reference/adapter/CMakeLists.txt`, unchanged, `AS_ENABLE_SPEEXDSP_MDF_REFERENCE=OFF` by default |
| MDF settings | 16 kHz mono f32, 160-sample frames, filter length `3200`, conversion `lrint(x*32767)->int16->x/32768` |
| Capture arithmetic | merged `docs/task-evidence/pipe-capture/host.py`, unchanged source of the copied policy arithmetic |
| Frozen comparison | merged `speexdsp-mdf-reference/evidence/oracle.json` and its sidecar, digests checked before use |

`fixtures.json` records `28` source/pin digests plus the dependency, native
manifest and merged-oracle pins. No tolerance is widened and no provider is
substituted.

## What is task-local

* `recipe.json` declares the stage policies, variants and 11-case matrix.
  Activation is `default_enabled=false`, `opt_in_only=true`, with zero build
  targets, shared changes, ABI changes or registry changes.
* `host.py` regenerates the deterministic streams, validates render timestamps
  before MDF, selects an explicit capture-only recipe when a reference is
  absent or invalid, invokes the unmodified merged CLI, then applies task-local
  capture stages and computes exact metrics.
* `fixture.residual_suppressor_surrogate.v0` is a **task-local energy gate**, not
  SpeexDSP's internal residual echo suppressor. The vendored public
  `speex/speex_echo.h` exposes no such control; no such capability is implied.
  It requires a valid far-end reference, is independently toggled, and is never
  on by default.
* `generate_report.py` bootstraps or byte-compares the frozen `report.json`.
* `test_host.py` contains `31` deterministic tests.

## Reference validation and fallback

The host validates render frame presence and monotonic, integer-frame
timestamps before any MDF call:

| Condition | Decision | Evidence |
| --- | --- | --- |
| Valid reference, including one-frame positive skew | `duplex`; skew repaired by frame-index alignment | `skew_timestamp_repair` repairs `200` frames and restores the aligned MDF output digest exactly |
| Zero render frames withheld | `duplex` with zero-render bit-exact MDF passthrough | `near_end_only` |
| Reference starvation (frames withheld) | `capture_only`, reason `reference_starvation` | `render_dropout`, `reference_absent` |
| Negative timestamp offset | `capture_only`, reason `stale_reference` | `reference_stale` |
| Non-monotonic or fractional/excessive skew | `capture_only` with the recorded reason | `reject_nonmonotonic_timestamps`, classifier controls |

No variant containing MDF or the residual surrogate is admitted on an
invalid-reference case. No ERLE value is used as an alignment detector.

## Frozen synthetic results

| Case / property | Frozen observation |
| --- | --- |
| Aligned echo-only MDF output digest | `4b6b1ba808f3f3919aa6f64dcec1661545208d0e382cb9199ff2a5a6d5ac63eb` (exact merged-oracle match) |
| Aligned echo-only ERLE | `16.453939 dB` |
| One-frame content-shifted ERLE | `16.888932 dB` (higher despite misalignment; ERLE is not an alignment detector) |
| Overlap near-ratio | `0.985161` (window contains residual echo; not a near-end preservation or double-talk conclusion) |
| Zero-render MDF | bit-exact passthrough, digest `0559befd3a5c3fe44d67f2c93a26e4df4b27ebba2c9a501dcd1a2551c491da05` |
| Timestamp-skew repair | `200` frames repaired; post-repair MDF digest equals aligned case |
| Changing delay, warm state | post-change ERLE `-0.103434 dB` |
| Changing delay, pinned reset at frame 150 | post-change ERLE `11.272770 dB`; output differs from warm case and is finite |
| Residual toggle | `duplex_residual` differs from `duplex_base` with `264` suppressed frames in `echo_only`; `duplex_base` suppresses `0` |
| Identity preservation | identity output digest equals capture digest in all `11` cases |
| Capture dropout | `11` zeroed frames recorded; valid reference still permits duplex processing |
| Finite full-length outputs | all variant outputs finite and `48000` samples |
| Three repeats | three canonical report digests all `5b34ce55aa4f7d906ae7b8f3702b989f17e11b3d5d6f6151095ef4e5345c29df` |

The changed-delay ERLE values are tool observations on one synthetic step, not
a convergence or tracking guarantee. The residual toggle changes bytes, not a
quality score. The limiter is inactive on the sub-ceiling synthetic levels, so
`duplex_no_limiter` is byte-identical to `duplex_base` in `echo_only`; this is
reported as an ablation observation, not as limiter validation.

## Reproduce without touching shared code

```sh
worktree=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PIPE-DUPLEX
task="$worktree/docs/task-evidence/pipe-duplex"
scratch=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/pipe-duplex
mkdir -p "$scratch"

# Confirm the merged adapter remains default-OFF, then build the opt-in CLI in scratch only.
cmake -S "$worktree/docs/task-evidence/speexdsp-mdf-reference/adapter" -B "$scratch/build-off" -DCMAKE_BUILD_TYPE=Release
cmake --build "$scratch/build-off" --parallel 4
test ! -e "$scratch/build-off/mdf_reference_cli"

cmake -S "$worktree/docs/task-evidence/speexdsp-mdf-reference/adapter" -B "$scratch/build-on" -DCMAKE_BUILD_TYPE=Release -DAS_ENABLE_SPEEXDSP_MDF_REFERENCE=ON
cmake --build "$scratch/build-on" --parallel 4
ctest --test-dir "$scratch/build-on" --output-on-failure

# Verify frozen report (no --write) and run tests.
cd "$task"
PYTHONDONTWRITEBYTECODE=1 python3 generate_report.py --cli "$scratch/build-on/mdf_reference_cli" --work "$scratch/frozen-check"
PIPE_DUPLEX_MDF_CLI="$scratch/build-on/mdf_reference_cli" PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p 'test_*.py' -v
python3 -m json.tool report.json >/dev/null
```

`generate_report.py --write` is bootstrap-only and refuses to replace an
existing frozen report unless `--force` is given. The CLI's
`AS_ENABLE_SPEEXDSP_MDF_REFERENCE=ON` option is the already-merged opt-in path;
this task neither adds nor changes it.

## Non-claims and remaining gates

* No real audio, corpus, device, acoustic room, listening panel or target
  runtime is present. No measured latency, deadline, paced-resource or
  availability claim is made.
* The Speex NS and residual stages are task-local policy surrogates, not vendor
  bit parity. No improvement in speech quality or echo return loss is claimed.
* No S10/protocol clearance, approved independent reference adapter or
  permitted case manifest exists for Tiny16 or adverse exploratory comparison.
* Independent review, hosted-CI/exact-head verification, target-runtime paced
  evidence, rights-cleared paired real-speech room qualification and release
  qualification remain open.
* No push, PR, merge, board edit, default promotion or public benchmark is
  implied.

See `docs/task-evidence/SDK-PIPE-DUPLEX.md` for the task-level acceptance
record and digests.

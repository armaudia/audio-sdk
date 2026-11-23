# SDK-PIPE-DUPLEX · task evidence

**Status: proposal-only, synthetic, task-local and incomplete.** One opt-in
host/recipe example is added under `docs/task-evidence/pipe-duplex/`. It joins
capture with timestamped far-end render, validates and aligns the reference,
runs the unchanged merged SpeexDSP MDF reference CLI, then applies a task-local
Speex NS policy stage, a sample-peak limiter and an independently toggled
task-local residual-suppressor policy surrogate. No AEC, double-talk, quality,
device, listening, public benchmark or release conclusion is made.

| Field | Record |
| --- | --- |
| Base / parent | `45b1b82a021ba350ee9e419013df146785b2f426` / `c41814bc0ea39151c29ca83fbde9267ccc063493` |
| Branch / worktree | `swarm/SDK-PIPE-DUPLEX` / `/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PIPE-DUPLEX` |
| Write scope | Task-local evidence only; no board, plan, CMake, CI, ABI, descriptor, registry, default or shared-source change |
| Evidence class | Deterministic frozen synthetic fixture with declared clocks; no real audio, assets, models or downloads |
| Reviewer | `reviewer-sdk-pipe-duplex` (dispatch after implementation, outside this commit) |

## Delivered fixture

`recipe.json` declares default-OFF, opt-in-only activation with zero build
targets, shared changes, ABI changes or provider registrations. It defines the
MDF stage pins, the capture stages, the residual surrogate, ablations and an
11-case matrix. `host.py` regenerates the frozen streams, classifies render
timestamps before MDF, repairs one-frame positive skew, forces explicit
capture-only on absent/invalid reference, invokes the merged CLI with pinned
settings, and emits exact f32 output digests plus finite, ceiling and energy
metrics. `fixtures.json` records `28` verified source/pin digests, the SpeexDSP
`1.2.1` revision `7a158783df74efe7c2d1c6ee8363c1e695c71226` dependency pin,
the native manifest pin and the merged-oracle pin with sidecar.

The Speex NS and residual stages are task-local deterministic policy surrogates,
not vendored vendor bit parity. The vendored public `speex/speex_echo.h` exposes
no residual-suppressor control, so the surrogate is disclosed as a task-local
energy gate that requires a valid far-end reference and is never on by default.

## Acceptance coverage

| Requirement | Evidence |
| --- | --- |
| Echo-only baseline | MDF output digest `4b6b1ba808f3f3919aa6f64dcec1661545208d0e382cb9199ff2a5a6d5ac63eb` and ERLE `16.453939 dB` exactly match the merged oracle; render/capture digests also exact |
| Double-talk overlap | Short synthetic near burst measured; MDF output `abb6cdc25f2371ecbeac05ef6ba564d51adf0c66390da09091948f23d2ab9327`, near-ratio `0.985161`; explicitly not a double-talk or quality conclusion |
| Near-end only | Zero-render MDF is bit-exact passthrough, digest `0559befd3a5c3fe44d67f2c93a26e4df4b27ebba2c9a501dcd1a2551c491da05`; residual toggle has no effect |
| Reference starvation / absence / staleness | `capture_only` decision with reasons `reference_starvation` or `stale_reference`; no MDF or residual variant admitted; forced residual attempt rejected in controls |
| Capture dropout | `11` zeroed frames recorded with valid reference retained; all outputs finite |
| Changing delay, warm vs reset | Warm post-change ERLE `-0.103434 dB`; pinned frame-150 reset post-change ERLE `11.272770 dB`; outputs differ and both are finite |
| Timestamp skew | One-frame positive skew on `200` frames detected and repaired; post-repair MDF digest equals aligned baseline |
| Residual suppressor toggled independently | `duplex_residual` differs from `duplex_base` with `264` suppressed frames; `duplex_base` suppresses `0`; NS and limiter ablations also recorded |
| Preservation against identity | Identity output digest equals capture digest in all `11` cases; identity RMS ratio recorded for every variant |
| Finite full-length signals | All variant outputs finite and `48000` samples; non-finite, wrong-length, wrong-rate and missing-render CLI controls rejected |
| Exact pins and repeats | `28/28` source pins, dependency/native/oracle pins and sidecar verified; three byte-identical internal repeats and three identical canonical report digests |
| Default-OFF additive scope | Adapter default confirmed `OFF` in scratch; opt-in `ON` CLI built in scratch only; no CMake/CI edits, ABI/default changes, provider substitution or tolerance widening |

## Key digests and counts

| Artifact / property | Value |
| --- | --- |
| `recipe.json` file / canonical | `4a017c925e33b6d888175b1a347a48c8ee0e68700b9a6a9cdca4425c441066a4` / `1a8e6bf9c02464a5af1b7d7e97c5d44715b4991b260c196f33b7b5d9adf73fe7` |
| `fixtures.json` file / canonical | `b38603d20cf3db8c88f42731d738f5f8ead3411867080f2a406ca40e34bdc9aa` / `d5649b4fbb40cc21dea04d8180c8850c62b41c27d1b43d3960eb8c1044b4eb97` |
| `report.json` file / canonical repeat | `ff69e229d35fa6cff3729f1ed66dfb277b9319e050adc7aa0e485337476986f4` / `5b34ce55aa4f7d906ae7b8f3702b989f17e11b3d5d6f6151095ef4e5345c29df` |
| `report.json.sha256` sidecar file | `38a3ac85f4d2823a3da22e98f0d9b11e2ccf0b4d05f7735c813271234b66d8c4` |
| `host.py` / `README.md` / `test_host.py` | `095d8214eae1bf57b20b90c1359eb2eb4890f52935d83c7802a9223059ef9753` / `014ef5c83584eec8728d13598217d9847ab5ac79485a9a8a54a546c1ce5c9431` / `5ecbe9753ca70c9e9e7e1cb57fe3f883cced8fe2b5f4460de28ad61116809dd0` |
| Source pins / dependency pin | `28/28` verified / SpeexDSP `1.2.1` revision `7a158783df74efe7c2d1c6ee8363c1e695c71226` |
| Tests | `31` passed, `0` failed, `0` skipped |
| Case count / comparisons / controls | `11` cases, all comparisons pass, all controls pass |
| Byte-identical repeats | `3` internal canonical repeats, one shared digest |
| Task-local files in commit | `9` |

Exact commit SHA, signature, parent and changed-file count are reported in the
local handoff response; evidence bytes do not depend on commit metadata.

## MDF limitation disclosure

The merged reference reported a *higher* ERLE for a one-frame misaligned render
(`16.888932 dB`) than for the aligned render (`16.453939 dB`), and the small
overlap near-ratio (`0.985161`) window contains residual echo. This task repeats
those exact values as tool observations and does **not** infer that ERLE detects
alignment, that the overlap is a double-talk test, or that any suppressor
preserves near-end speech. The changing-delay warm/reset values are single
synthetic step observations, not a tracking guarantee.

## Reproduction

```sh
worktree=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PIPE-DUPLEX
task="$worktree/docs/task-evidence/pipe-duplex"
scratch=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/pipe-duplex

cmake -S "$worktree/docs/task-evidence/speexdsp-mdf-reference/adapter" -B "$scratch/build-off" -DCMAKE_BUILD_TYPE=Release
cmake --build "$scratch/build-off" --parallel 4
test ! -e "$scratch/build-off/mdf_reference_cli"
cmake -S "$worktree/docs/task-evidence/speexdsp-mdf-reference/adapter" -B "$scratch/build-on" -DCMAKE_BUILD_TYPE=Release -DAS_ENABLE_SPEEXDSP_MDF_REFERENCE=ON
cmake --build "$scratch/build-on" --parallel 4
ctest --test-dir "$scratch/build-on" --output-on-failure

cd "$task"
PYTHONDONTWRITEBYTECODE=1 python3 generate_report.py --cli "$scratch/build-on/mdf_reference_cli" --work "$scratch/frozen-check"
PIPE_DUPLEX_MDF_CLI="$scratch/build-on/mdf_reference_cli" PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p 'test_*.py' -v
python3 -m json.tool report.json >/dev/null
```

All scratch paths are outside the worktree and are not part of the commit.

## Remaining gates and non-claims

* Independent reviewer dispatch/review is outside this commit.
* Hosted-CI and exact-head verification are not claimed.
* Target-runtime paced resource, deadline, availability and device evidence
  are `blocked_not_measured`.
* Rights-cleared paired real-speech room qualification and listening tests are
  not performed; no listening result is claimed.
* No S10/protocol clearance, approved independent reference adapter or
  permitted case manifest exists for Tiny16 or adverse exploratory comparison.
* No push, PR, merge, board edit, default promotion, public benchmark or
  release qualification is implied.

See `docs/task-evidence/pipe-duplex/README.md` for the full scope, controls,
pin table and explicit non-claims.

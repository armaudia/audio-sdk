# SDK-SPEEX-MDF-RESIDUAL-POSTFILTER — task-local optional reference

A **paired synthetic reference tool**, not an AEC, double-talk, quality, device,
listening, pacing or release claim. It wraps the exact pinned SpeexDSP MDF core
at the public `speex/speex_echo.h` boundary and, only when explicitly requested,
the residual echo suppressor at the public `speex/speex_preprocess.h` boundary.
It records a frozen oracle with three byte-identical repeats. No real audio,
model, corpus, download, licensed runtime or public benchmark claim is included.

**Outcome: the postfilter stays optional, default OFF and unregistered.**
Near-end preservation against MDF alone was **not recovered**: the 20 ms overlap
near ratio falls from `0.968517` to `0.687357` while far-end ERLE changes only
from `15.675997 dB` to `15.590018 dB`. No provider, descriptor, catalog,
installed-v0 behavior, public API/ABI or shared code was changed.

## Scope and isolation

- Write scope: this directory only (`docs/task-evidence/speex-mdf-residual-postfilter/`)
  and the summary `docs/task-evidence/SDK-SPEEX-MDF-RESIDUAL-POSTFILTER.md`.
- No shared CMake file, CI workflow, public header, ABI, descriptor, registry,
  SDK provider, default provider or board file changed.
- `adapter/CMakeLists.txt` is a standalone project with one new option,
  `AS_ENABLE_SPEEX_MDF_RESIDUAL_POSTFILTER`, default **OFF**. Nothing is built,
  installed or registered when the caller does not opt in. Both OFF and ON
  configurations were verified. The installed SDK build ID remains
  `audio-sdk/0.1.0+sha256:0bc71dcab04880033a4ad4c1cfcebb8a05eccb11a20a786b9c844e394c035972`.
- The adapter compiles the existing vendored sources in place; no source file
  is copied, edited, substituted or given a relaxed tolerance.
- All fixture, output and build bytes stay in a caller scratch directory outside
  the worktree; only canonical JSON evidence, digests and source text are
  committed here. No asset is published.

## Exact pins

Legacy checkout: `3e2446fc58886fc02b099b54651adc9a10a65454`
(`/Users/htsakanyan/workspace/audio/audioml/cpp-library`). SDK dependency lock:
`deps/lock.json` revision `7a158783df74efe7c2d1c6ee8363c1e695c71226`, vendored
SpeexDSP 1.2.1. The full 20-entry source/boundary pin set and the nine exact
legacy Git blobs are in `contract.json`; `verify.py` recomputes every SHA-256
and Git blob ID and, when `--legacy-repo` is supplied, checks direct
`git rev-parse` at the legacy commit.

| Key pin (relative to SDK worktree or workspace) | SHA-256 | Scope used |
| --- | --- | --- |
| `third_party/speexdsp/libspeexdsp/mdf.c` | `15e08b7fa89562d74aaa3e61911a07e56078ea00f8476daf28d9cf6d5d22c07f` | exact MDF core, compiled in place |
| `third_party/speexdsp/libspeexdsp/preprocess.c` | `76b78805acce558177a57029ce4da02554a49a465cdd8dd0651ea7807f4eba2d` | exact residual suppressor, compiled in place |
| `third_party/speexdsp/include/speex/speex_echo.h` | `19e722fdfe03864ae9dadc91637270e8c70191950c49892fa8a62478be79e71d` | public echo boundary, unchanged |
| `third_party/speexdsp/include/speex/speex_preprocess.h` | `7c12339881fce3250c69af7f36b8440a8d8012976b54331b3c980b8074393b25` | public residual-suppression boundary, unchanged |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | 16 kHz / mono / 160-sample v0 grid, unchanged |
| `research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` | source-reported suppressor near-end damage; provenance only |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | residual suppression should not be default |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | room acceptance profile |
| `speexdsp-mdf-reference/evidence/REPORT.md` | `a5b1a6e91203d18eac546e130bf02515eea22139b222e0b4c52dd4bab2dc0eb6` | merged MDF caveats; disclosure only, not this task's oracle |

The mutable board snapshot had SHA-256
`7cd94ec7a32f3ff8ff8df1c7a8e40db0f888c31634721ec2e58bd147d2605a53` at read
time. It is recorded as informational provenance and is never a gate.

## Local artifact digests (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `adapter/CMakeLists.txt` | `20e62d712e77f739e606dfa52165e97736ac4456ea74a279794005b8ba922321` |
| `adapter/src/mdf_postfilter_cli.c` | `3599fcae021460cab2294aa16d55502109a7165dabad58476d541b838ab2adb0` |
| `fixture.py` | `6d72c92a6f22d23348b290eaf0ccae153d87108bf243629283cb5ed2131af2db` |
| `scorer.py` | `179dc4a88a64e87841a550915ed6d9c347fe66957fa96a0263a4820151c91df6` |
| `reference.py` | `f445d5317cf4e8dc57aba89013655f4bcc04eb061cf99808ca759479555d1e74` |
| `run.py` | `44820f93fe2287a6a381fe1ab6d50dfd5aa63e5d184b3fe25024a2a0eb980b93` |
| `verify.py` | `2696b1be8f4a925a375036896b3dc9aa23c0d301105c0f7556830ade3ca0b24d` |
| `test_reference.py` | `417ae5f045dcd2d759b899474e07e158ee40feaf893815a207b4f06891f40d18` |
| `adapter.json` | `4bd1a2abd294d6f0da87164a60a120925b3b1e7af9d95ca9fd95290a509c44a7` |
| `contract.json` | `b5b4755634eebbd31f217a35742864fadf4b4c83eb269949329def4b0b52dd79` |
| `report.json` (canonical bytes = file bytes) | `ad15c446442058b82c003f15527637edae02a819a2033b0f289bc89042b170b6` |
| `report.json.sha256` (file bytes) | `8c5748affe9f9cf5b6d608f039b673814725b2fa769f896dda5b268e13917767` |
| `evidence/REPORT.md` | `9260b81948ac125027115023615e532c283b7c531d5cee52671e47acf6327622` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`) plus one trailing newline. Its internal fixture digest is
`c26dbcbbb5d39789dce05f1c0eb0b024031a87b808424ac6fb05c62583f3e537`, and the
three full report cores share canonical digest
`ce86680b8a683084850884ebb5fcb91b0b4d66503e80e30c4173458edc6c4cc5`. The
frozen report was bootstrapped once with a fresh output file; all later runs
only compare bytes and fail on any difference.

## Reproduction

All commands run from this worktree; scratch/build output is outside it.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SPEEX-MDF-RESIDUAL-POSTFILTER
ADAPTER=$WT/docs/task-evidence/speex-mdf-residual-postfilter/adapter
TASK=$WT/docs/task-evidence/speex-mdf-residual-postfilter
SCRATCH=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/mdf-postfilter

# Default-OFF isolation: configure/build with and without the opt-in target.
cmake -S "$ADAPTER" -B "$SCRATCH/build-off" -DAS_ENABLE_SPEEX_MDF_RESIDUAL_POSTFILTER=OFF
cmake --build "$SCRATCH/build-off"
cmake -S "$ADAPTER" -B "$SCRATCH/build-on" -DCMAKE_BUILD_TYPE=Release \
  -DAS_ENABLE_SPEEX_MDF_RESIDUAL_POSTFILTER=ON
cmake --build "$SCRATCH/build-on" --parallel 4
ctest --test-dir "$SCRATCH/build-on" --output-on-failure

# Frozen oracle, exact pins, controls and three byte-identical regenerations.
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 python3 verify.py \
  --cli "$SCRATCH/build-on/mdf_postfilter_cli" \
  --work "$SCRATCH/verify" \
  --legacy-repo /Users/htsakanyan/workspace/audio/audioml/cpp-library

# Unit checks (MDF_POSTFILTER_CLI includes the CLI-dependent cases).
PYTHONDONTWRITEBYTECODE=1 MDF_POSTFILTER_CLI="$SCRATCH/build-on/mdf_postfilter_cli" \
  python3 -m unittest -v test_reference.py

PYTHONDONTWRITEBYTECODE=1 python3 run.py --report \
  --cli "$SCRATCH/build-on/mdf_postfilter_cli" --work "$SCRATCH/regen" > "$SCRATCH/regen.json"
cmp report.json "$SCRATCH/regen.json"
```

Read-only board and whitespace checks from the worktree root:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-SPEEX-MDF-RESIDUAL-POSTFILTER
git diff --check
```

Observed locally: OFF configure/build succeeded with no target and no tests; ON
build plus CTest **2/2** passed; Python unit suite passed; `verify.py`
regenerated the frozen report exactly with **5 conditions × 2 variants × 3
repeats**, nine controls, 20 external pins and nine legacy blobs; three
independent `run.py --report` regenerations were byte-identical; baseline SDK
CTest **11/11** passed with unchanged build ID; board check exit 0;
`git diff --check` clean.

## Disclosures

- The merged SpeexDSP MDF evidence measured one-frame-misaligned ERLE
  `16.888932 dB` versus `16.453939 dB` aligned, and a 20 ms overlap near ratio
  of `0.985161`. ERLE is not an alignment detector. This task's misaligned case
  likewise measured higher ERLE (`16.884243 dB`) than the aligned case
  (`15.675997 dB`).
- The 20 ms overlap near ratio includes residual echo and is not double-talk
  quality. The near-only case is bit-exact passthrough under the zero-render
  policy, so its attenuation result is a control, not a preservation pass.
- The fixture is a stationary three-tap synthetic path with tiny seeded noise.
  It does not exercise real room responses, movement, clock drift, nonstationary
  noise, long double-talk, human listening or target-device pacing.
- No adverse Tiny16 comparison is made: there is no S10/protocol clearance,
  approved independent reference adapter or permitted case manifest here.
- Source-reported suppressor numbers from `research/aec_research_20261028.md`
  are provenance only and are never pooled with these local measurements.

## Remaining gates / reopening conditions

1. Rights-qualified paired real-speech room cohort with frozen RIRs, delay,
   movement, noise and capture-clock drift.
2. Agreed preservation, ERLE, alignment, availability and nonfinite margins with
   an independent scorer and sealed review.
3. Paced target-device CPU, memory, deadline and buffer/backpressure evidence.
4. Provider, ABI, license and default-policy intake. Until all four pass, the
   postfilter stays optional, unregistered and OFF; this directory remains
   task-local tooling evidence and nothing here qualifies a public benchmark or
   production AEC.

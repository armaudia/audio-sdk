# SDK-SPEEXDSP-MDF-REFERENCE — task-local SpeexDSP MDF reference

A **paired synthetic reference tool**, not an AEC, double-talk, quality, device,
listening or release claim. It wraps the exact pinned SpeexDSP MDF source at
the public `speex/speex_echo.h` boundary and records a frozen oracle with three
byte-identical repeats. No real audio, room recording, model, asset, download,
licensed runtime, listening result or public benchmark claim is included.

## Scope and isolation

- Write scope: this directory only (`docs/task-evidence/speexdsp-mdf-reference/`
  and the summary `docs/task-evidence/SDK-SPEEXDSP-MDF-REFERENCE.md`).
- No shared CMake file, CI workflow, public header, ABI, descriptor, registry,
  SDK provider, default provider, installed v0 behavior or board file changed.
- `adapter/CMakeLists.txt` is a standalone project with one new option,
  `AS_ENABLE_SPEEXDSP_MDF_REFERENCE`, default **OFF**. Nothing is built,
  installed or registered when the caller does not opt in. The installed SDK
  build ID remains `audio-sdk/0.1.0+sha256:0bc71dcab04880033a4ad4c1cfcebb8a05eccb11a20a786b9c844e394c035972`.
- The adapter compiles the existing vendored sources in place; no source file
  is copied, edited, substituted or given a relaxed tolerance.
- All fixture, output and build bytes stay in a caller scratch directory
  outside the worktree. Only canonical JSON evidence and source digests are
  committed.

## Exact pins

Legacy checkout: `3e2446fc58886fc02b099b54651adc9a10a65454`
(`/Users/htsakanyan/workspace/audio/audioml/cpp-library`).
SDK dependency lock: `deps/lock.json` revision
`7a158783df74efe7c2d1c6ee8363c1e695c71226`, vendored SpeexDSP 1.2.1.

| Vendored file (relative to SDK worktree) | Legacy Git blob | SDK file SHA-256 |
| --- | --- | --- |
| `third_party/speexdsp/libspeexdsp/mdf.c` | `ccbc95f2c256ec89ce2939ecb599e13f45321f0d` | `15e08b7fa89562d74aaa3e61911a07e56078ea00f8476daf28d9cf6d5d22c07f` |
| `third_party/speexdsp/include/speex/speex_echo.h` | `a5a633b914528779497a114c5b18b7449969b34c` | `19e722fdfe03864ae9dadc91637270e8c70191950c49892fa8a62478be79e71d` |
| `third_party/speexdsp/libspeexdsp/fftwrap.c` | `fa3b23fc7d920de8837348466871c3505b09e77d` | `fd96f1e44245a403bbba3d3328f4f60b763132f939c217c76409621c3f66b8f0` |
| `third_party/speexdsp/libspeexdsp/filterbank.c` | `670c523e2bad6641223d2dc9b52aa5a92f3b1ef8` | `0c925d5bd0be9668853e262f3474c3b8203c7cf31aecb63531257e126e87631d` |
| `third_party/speexdsp/libspeexdsp/smallft.c` | `fd53cdf90e0a5adf43e689c018b93ed5d5124bb9` | `d2baa3d5378ed9fd344d2ee61f92c30c8d930db4968b3a8a2cf0760ca0ef376d` |
| `third_party/speexdsp/libspeexdsp/kiss_fft.c` | `8dc9345428b13a3694c1d909574ae56596b1403d` | `cf0da304f5067c71cf85df711af74252802805714dfda736be93be391e7c4c1c` |
| `third_party/speexdsp/libspeexdsp/kiss_fftr.c` | `827e0b14df9675d61d0cd9618f1bd3603ad205be` | `13b7ec32c17b927e0978195ce9eeb09e9791b236fcee94b807fd0086d14cb25e` |

`LEGACY_BLOBS.sha1` records those seven blobs. `verify.py` recomputes each Git
blob ID from the SDK file and, when `--legacy-repo` is supplied, checks
`git rev-parse <commit>:<path>` against the same value. `SOURCES.sha256` pins
those seven files, `deps/lock.json`, `deps/speexdsp-files.sha256`, the two
unchanged public SDK headers and five research/profile documents.

| Research/profile pin (relative to `/Users/htsakanyan/workspace/audio/audioml`) | SHA-256 | Scope used |
| --- | --- | --- |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Line 55: synthetic/recorded training pilots, 20 ms frames; residual suppression damaged near-end and should not be default. |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | AEC row 69: SpeexDSP MDF control, AECMOS predicted quality, not human ratings. |
| `research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` | Source-reported pilots, 250 ms tail/320 hop and optional residual suppressor finding; provenance only. |
| `reports/aec_challenge_real_pilot_summary_20261028.csv` | `4784755161aa0fa4027b2b6524f8dd34b7ccc9390ecd785103dda95b65bb27e7` | Linked summary; not reproduced here. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Room acceptance profile. |

Mutable board snapshot digest at read time was informational only and is not
part of the frozen evidence. Source-reported pilot numbers are never pooled
with these local synthetic measurements.

## Local artifact digests (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `adapter/CMakeLists.txt` | `8932ce329820e02311962e9d5d009af23292dcc282fc6ae4bc490c28efb18887` |
| `adapter/src/mdf_reference_cli.c` | `e803ddeb779a7898d8e6fc75bf64fc17a1c3b7b65692e5f9c90f87af82e1f114` |
| `tools/fixture.py` | `314f36d865a6a7e1580205a2a82484cb9226479e4f6d6d677027c35bf6e627bd` |
| `tools/evaluate.py` | `af5998bce756482045b8aeac2ffee7a598ede9b3c3aecc838bd9a7f41aff1045` |
| `tools/verify.py` | `fd814b3ad85e5c8d2c8b3fb4ee1b95a49a86561c81bb7515c7dee9ec6369f19a` |
| `tools/test_reference.py` | `265811c9e6c539f55880e6acecec1780e21840394194a17ec3d4c2ddd5d19288` |
| `SOURCES.sha256` | `1df7645390c8b746f4db8be6a6cd938f1b08d99ec21be27d95c03065cf0b4509` |
| `LEGACY_BLOBS.sha1` | `70a644e8712ae47111fd077f68c2370ac2de0449eedf36cb19af6288396aa296` |
| `evidence/oracle.json` (file bytes) | `c1e1c232cb80d344fe6a1131ebf80caf112cd68e2baad9a2543ee8ccc1e08411` |
| `evidence/oracle.json.sha256` (file bytes) | `71660089b00de08da0973695a9f960fd0435a55644bf211d63118ccbd0580681` |

`oracle.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`) plus one trailing newline; its digest equals the value in
`oracle.json.sha256`. The internal `fixture_digest` is
`1ab4d6e0fbe723f88a2d765a01b02b9eb912aae7f18bea97039854f1ade2ca9b`. The
frozen report was bootstrapped once with `--write-oracle`; all later runs only
compare bytes and fail on any difference.

## Reproduction

All commands run from this worktree; scratch/build output is outside it.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SPEEXDSP-MDF-REFERENCE
ADAPTER=$WT/docs/task-evidence/speexdsp-mdf-reference/adapter
TASK=$WT/docs/task-evidence/speexdsp-mdf-reference
SCRATCH=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/mdf-reference

# Default-OFF isolation: configure/build with and without the opt-in target.
cmake -S "$ADAPTER" -B "$SCRATCH/build-off" -DAS_ENABLE_SPEEXDSP_MDF_REFERENCE=OFF
cmake --build "$SCRATCH/build-off"
cmake -S "$ADAPTER" -B "$SCRATCH/build-on" -DCMAKE_BUILD_TYPE=Release \
  -DAS_ENABLE_SPEEXDSP_MDF_REFERENCE=ON
cmake --build "$SCRATCH/build-on" --parallel 4
ctest --test-dir "$SCRATCH/build-on" --output-on-failure

# Frozen oracle: source pins, seven exact blobs and byte-identical repeats.
PYTHONDONTWRITEBYTECODE=1 python3 "$TASK/tools/verify.py" \
  --cli "$SCRATCH/build-on/mdf_reference_cli" --work "$SCRATCH/eval-verify" \
  --legacy-repo /Users/htsakanyan/workspace/audio/audioml/cpp-library

# Unit checks (set MDF_CLI to include the CLI nonfinite-input control).
cd "$TASK/tools"
PYTHONDONTWRITEBYTECODE=1 MDF_CLI="$SCRATCH/build-on/mdf_reference_cli" \
  python3 -m unittest -v test_reference.py

# Read-only board check and whitespace check (from the worktree root).
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-SPEEXDSP-MDF-REFERENCE
git diff --check
```

Observed locally: OFF configure/build succeeded with no target and no tests;
ON build plus CTest **1/1** passed; `verify.py` regenerated the report exactly
(`c1e1c232…`) with **5 cases × 3 repeats**, 5 negative controls and 7 verified
legacy blobs; Python **16/16** tests passed; baseline SDK CTest **11/11** passed
with unchanged build ID; board check exit 0; `git diff --check` clean.

## Results and disclosures

See `evidence/REPORT.md` for the full paired table. In short: far-end-only ERLE
`16.453939 dB` on the frozen three-tap path; 20 ms overlap output/near RMS
`0.985161` including residual echo; one-frame reference misalignment still
measured `16.888932 dB` ERLE, so ERLE alone does not validate alignment.
Near-only and withheld-reference cases are bit-exact passthrough controls, not
cancellation results. No output was nonfinite, clipped or missing. These are
observations of one synthetic, stationary fixture on one pinned toolchain.

The source-reported residual-suppressor near-end damage is **not reproduced**
because this adapter does not enable that suppression. The overlap result must
not be generalized to double-talk quality.

## Reopen / release gates

1. Rights-qualified paired real-speech room cohort with frozen RIRs, delay,
   movement, noise and capture-clock drift.
2. Agreed preservation, ERLE, alignment, content/availability and nonfinite
   margins with an independent scorer and sealed review.
3. Paced target-device CPU, memory, deadline and buffer/backpressure evidence.
4. Provider/ABI/license intake and explicit default-policy review; this
   reference stays optional until then.

Until all four are met, this directory remains task-local evidence for the
dependent duplex pipeline work and nothing here qualifies a public benchmark
or production AEC.

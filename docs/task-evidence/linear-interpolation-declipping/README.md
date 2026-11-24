# Linear-interpolation declipping (opt-in offline comparator)

**SDK-LINEAR-INTERPOLATION-DECLIPPING · Restoration acceptance profile · status:
proposal-only, synthetic, developer-only, offline.** A deterministic, stdlib-only
linear-interpolation declipper is implemented behind a protocol-v1-shaped,
task-local adapter boundary. It is **not** an SDK processor, provider, public
API/ABI or descriptor change, registry entry, default provider, Bench bundle,
benchmark ingestion, listening result or release qualification. Installed v0
remains 16 kHz mono float32, 160-sample frames; this comparator processes fixed
**2048-sample offline blocks** and makes **no realtime claim**.

**Proceed/defer decision: DEFER processor exposure.** The decision is recorded
before any processor exposure in [`adapter.json`](adapter.json)
(`processor_decision: "defer"`) and in `report.json`
(`processor_decision.decision: "defer"`). Keep this comparison only as an
offline comparator on the **exact known clipping mask**: the source RST-01
screen reports linear interpolation at 10.99 dB SI-SDR versus 15.05 dB for
band-limited POCS at clip threshold 0.35, and this synthetic cohort confirms a
loss against the clipped-input anchor at every occupancy stratum. No quality,
listening, native-provider or timing evidence supports a processor. Conditions
to reopen are listed below.

Pinned base: `68e3e292b0b2c4b0a96b5f3d3002bb9cb36282d4`, branch
`swarm/SDK-LINEAR-INTERPOLATION-DECLIPPING`. Nothing outside this evidence
directory is modified by the implementation.

## Source pins and what they establish

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`; set
`AUDIOML_ROOT` if the checkout lives elsewhere. Verification is by exact
SHA-256 and a missing pinned file is a **failure, not a skip**.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/distortion_restoration_20261028.md` | `8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71` | RST-01 task boundary; hard clipping at 0.35/0.55 of peak; 2.74%/0.55% pilot occupancy; linear interpolation drops to 10.99 dB at 0.35 while POCS reaches 15.05 dB; small pilot, no listening. |
| `src/audioml_eval/distortion_restoration.py` | `c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f` | Normative `declip_linear(x, mask)`: copy input, interpolate masked positions from unmasked anchors, leave input unchanged with fewer than two anchors; runner builds the clipping mask from `abs(clipped) >= threshold - 1e-10`. |
| `reports/distortion-restoration/20261028-synthetic-screen.json` | `87df91e30905ead24786146b8e82257b7132cd5cd51bcee46570955eff826ece` | Source-reported 12-clip screen; provenance only, **not** reproduced or pooled with local results. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Restoration profile: freeze corruption, metadata and clean baseline; stratify by degradation and bandwidth; report validity, task-specific quality, output peaks and missing results; validate one invalid and one valid case through the bundle. |
| `adapters/controls/adapter.json` | `3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599` | Public protocol-v1 envelope shape reused by the task-local descriptor (`inspect`/`run`, refs, configuration). |
| `adapters/controls/run.py` | `4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66` | Public request-validation pattern: strict JSON, duplicate-key and nonfinite-constant rejection, explicit refs. |

The pilot uses NumPy arbitrary-length arrays; this comparator uses portable
binary32 samples and closed-form anchor arithmetic on 2048-sample blocks.
Numbers here are descriptive for these frozen synthetic stimuli, not a
bit-exact replay of the pilot or a real-speech result.

## Boundary and files

| File | SHA-256 | Role |
| --- | --- | --- |
| `adapter.json` | `c62e53093fcc5a92cbff3fd7525c5af6a3d2fd160c9c6248cbfe44ba6dc5cadc` | Task-local, unregistered descriptor; `identity`, `clipped_input`, `linear_interp`; `modes: ["offline"]`; deferred processor decision. |
| `reference.py` | `322fc0af5721c76f9d61998f73f418f7424ad51d0177085f7c3cd9b1739e835c` | Exact clipping mask, hard clip, linear reconstruction with endpoint holds, SI-SDR/RMSE, fail-closed control validation. |
| `fixtures.py` | `0e4c5da663713246c9e3ddd692c95e146defa614236fa2c42e9f6076d027ee3d` | Six pinned source digests and 13 deterministic stimuli: tones, transients, speech-like bursts, leading/trailing runs, isolated peaks, two-anchor, nearly-all-clipped, all-clipped and nonfinite. |
| `run.py` | `991122266918b28fd88002fa691c52825da03e7881f2ec346e857ea883b4fc9a` | `inspect`/`run` boundary; derived **or** caller-owned exact mask; canonical JSON result with digests, mask metadata, reconstruction trace, peak/scoring and adverse status. |
| `report.py` | `ae6f5e8e2cc7e73991f31cd32d4aee26e27a2bc4485f0b7377dc25de77a96a3a` | Builds the canonical report solely by driving the adapter boundary. |
| `report.json` | `c3252fd080299e4b1804a9facf3fea02fe66f0df31728426476346f28d8dc310` | 98,943 bytes, one line, LF. Regeneration is byte-identical. |
| `report.json.sha256` | `90a280f2a092782779f905429937d45bd8fe2b545a5440cb13254731bd356b4f` | Digest sidecar. |
| `test_fixture.py` | `e8d7f1e27227708284eeb63fe2e16adb36b96fc1e0fe91852d4fea2c77eeb600` | 23 deterministic unittest cases. |

Local report digests: fixture spec
`63dd65d30443ef744b5471fb53bf9e2b779701a0ca71341c339696f1be652b0f`;
clean/identity/clipped-no-occupancy/linear-no-occupancy f32 output
`a7ce0b077a5af0269afb212eb21511e5ebf4862e4dbca0def7833892a936ffab`
(all four equal — measured transparency).

## Exact clipping mask and reconstruction contract

- The clean source is frozen separately from corruption. Hard clipping is
  symmetric at `f32(threshold)`. The pilot's float64 rule
  `abs(clipped) >= threshold - 1e-10` is represented with binary32 absolute
  tolerance `1e-7`; `assert_exact_mask` then requires exact equality
  `abs(clipped) == abs(f32(threshold))` for every masked sample and exact
  `clipped == clean` preservation for every unmasked sample. This is verified
  for all 19 finite-source cases.
- `mask_source: "derived"` derives the mask from the frozen clean source.
  `mask_source: "caller"` accepts a caller-owned boolean mask only if it
  matches that derived mask exactly; mismatch, wrong length, non-boolean
  entries, nonfinite entries and a missing mask are rejected. This comparator
  never detects clipping or estimates a threshold.
- Each masked run is reconstructed from reliable anchors: interior runs use a
  linear ramp between the nearest reliable samples; leading and trailing runs
  hold the nearest reliable anchor (NumPy `interp` endpoint behavior, **no
  extrapolation**); with fewer than two reliable samples the clipped input is
  returned unchanged. Unmasked samples are always preserved bit-for-bit.
- Boundary stimuli are explicit: `head_clip` (leading run), `tail_clip`
  (trailing run), `single_interior` (one isolated clipped sample between
  anchors 1023 and 1025), `two_anchors` (two interior runs),
  `minimal_anchors` (exactly two reliable anchors with leading and trailing
  holds plus an interior ramp) and `all_clipped` (no reliable anchor, input
  unchanged). Every run rule is recomputed from adapter output by
  `report._check_boundary_runs`.

## Reproduction (from the SDK worktree root)

Use Python 3.11.5 (stdlib only) and a scratch directory:

```sh
evidence=docs/task-evidence/linear-interpolation-declipping
scratch="${TMPDIR:-/tmp}/linear-declip-$$"
mkdir -p "$scratch"

cp "$evidence/report.json" "$scratch/report.committed.json"
PYTHONDONTWRITEBYTECODE=1 python3 "$evidence/report.py"
cmp "$scratch/report.committed.json" "$evidence/report.json"
shasum -a 256 "$evidence/report.json"
cat "$evidence/report.json.sha256"

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "$evidence" -p 'test_*.py' -v
python3 -m json.tool "$evidence/report.json" > /dev/null

cmake -S . -B build/baseline -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build build/baseline --parallel 2
ctest --test-dir build/baseline --output-on-failure --timeout 60

git diff --check
```

Expected: 23/23 fixture tests pass; baseline SDK ctest 11/11 pass; report digest
`c3252fd080299e4b1804a9facf3fea02fe66f0df31728426476346f28d8dc310`; six source
pins exact; `git diff --check` silent. There is **no consumer opt-in OFF/ON
matrix** because no opt-in provider, CMake option or consumer surface was
added; the unchanged baseline ctest suite is the relevant local check. `reuse`
is not installed locally here; `docs/**` is covered by the repository
`REUSE.toml` aggregate annotation and no C header is generated, so no SPDX
header text is embedded in Python strings.

## Frozen cohort and results (synthetic only)

21 cases: 20 complete, 1 adverse; 22 rejected invalid/missing controls; 8
explicitly unrun results. Clipping occupancy and per-case scores are in
`report.json`.

| Case | Stratum / stimulus / control | Occ. % | Peak in → out | SI-SDR (dB) |
| --- | --- | ---: | ---: | ---: |
| `clean_identity` | baseline · clean_bandlimited · identity | 0 | 0.900 → 0.900 | 120.0 |
| `clean_clip_no_occupancy` | baseline · clean_quiet · clipped input | 0 | 0.300 → 0.300 | 120.0 |
| `clean_linear_no_occupancy` | baseline · clean_bandlimited · linear | 0 | 0.900 → 0.900 | 120.0 |
| `occupancy_very_low` | 0.35 · very_sparse_transients · linear | 0.4883 | 1.000 → 0.324 | 3.860 |
| `occupancy_low` | 0.35 · sparse_transients · linear | 1.9531 | 1.000 → 0.325 | 3.771 |
| `occupancy_mid` | 0.55 · speech_like · linear | 9.5703 | 1.000 → 0.550 | 12.784 |
| `occupancy_high` | 0.35 · dense_tones · linear | 42.1875 | 1.000 → 0.350 | 4.925 |
| `occupancy_saturated` | 0.01 · clean_bandlimited · linear | 98.6816 | 0.900 → 0.009 | -34.510 |
| `clipped_very_low` | control · very_sparse_transients | 0.4883 | 1.000 → 0.350 | 7.818 |
| `clipped_low` | control · sparse_transients | 1.9531 | 1.000 → 0.350 | 8.101 |
| `clipped_mid` | control · speech_like (0.55) | 9.5703 | 1.000 → 0.550 | 13.769 |
| `clipped_high` | control · dense_tones | 42.1875 | 1.000 → 0.350 | 9.263 |
| `clipped_saturated` | control · clean_bandlimited (0.01) | 98.6816 | 0.900 → 0.010 | 5.198 |
| `boundary_leading` | boundary · head_clip · leading hold | 0.1953 | 1.000 → 0.280 | 16.427 |
| `boundary_trailing` | boundary · tail_clip · trailing hold | 0.1953 | 1.000 → 0.280 | 15.979 |
| `boundary_single_interior` | boundary · single_interior · ramp | 0.0488 | 1.000 → 0.050 | 4.361 |
| `boundary_two_anchors` | boundary · two_anchors · two ramps | 0.0977 | 1.000 → 0.040 | -0.391 |
| `boundary_minimal_anchors` | boundary · minimal_anchors · 2 anchors | 99.9023 | 1.000 → 0.100 | -63.516 |
| `boundary_all_clipped` | boundary · all_clipped · no anchor | 100 | 1.000 → 0.350 | 120.0 |
| `caller_mask_exact` | mask contract · speech_like (0.55) | 9.5703 | 1.000 → 0.550 | 12.784 |
| `nonfinite_input` | adverse · NaN at 17, Inf at 1025 | 51.5625 | 0.800 → none | n/a |

- **Occupancy comparison:** linear interpolation is below the clipped-input
  anchor in every stratum: very low -3.96 dB, low -4.33 dB, mid -0.99 dB, high
  -4.34 dB, saturated -39.71 dB. These are frozen synthetic observations, not
  real-speech or perceptual results.
- **Boundary behavior:** all six boundary cases match their documented rule;
  every complete case preserves unmasked samples bit-for-bit and reports finite
  output. The degenerate `minimal_anchors` and `single_interior` cases are
  controls showing the method's limits, not quality claims.
- **Output peaks:** all 20 complete cases are finite and stay within their
  input peak; maximum observed output peak is 0.900. This is a cohort-only
  bound, not a limiter guarantee.
- **Transparency:** identity, zero-occupancy clipped input and zero-occupancy
  linear interpolation are bit-identical to their clean sources (f32 digest
  above); no unconditional transparency is claimed for nonzero occupancy.

## Controls, adverse cases and skipped results

- 22 boundary rejections are retained with reasons: missing/invalid/nonnumeric/
  nonfinite threshold, threshold 0 or >1, unsupported `mask_source`, missing,
  wrong-length, non-boolean, nonfinite or mismatched caller mask, unexpected
  caller mask, unknown control key, invalid candidate ref, wrong protocol,
  wrong block length, missing attempt/configuration, unknown stimulus,
  duplicate JSON key and JSON `NaN`.
- Nonfinite input (NaN at 17, +Inf at 1025) is an explicit `adverse_numerical`
  result: no output samples are serialized, no SI-SDR is computed and it cannot
  count as a pass.
- Eight results are recorded `not_run`: paired real speech/EARS cohort,
  STOI/perceptual scoring and listening, installed native provider/conformance,
  target-device timing and realtime, release qualification and Bench ingestion,
  SPADE/social-sparsity/C-OMP parity, pilot 12-clip mean reproduction, and blind
  clipping detection/unknown-mask operation. **No missing result qualifies the
  candidate.**
- The consumer opt-in OFF/ON matrix and generated-header/SPDX checks are
  recorded `not_applicable`: no opt-in provider, CMake option, consumer surface
  or generated header was added.

## Exact blockers and reopening conditions

This closes only the opt-in, offline, synthetic comparator question, with a
**defer** decision on processor exposure. It is blocked from any release,
quality, parity or benchmark claim until:

1. A paired rights-cleared real-speech cohort is frozen with threshold, exact
   mask, clean reference, crop and alignment policy.
2. Independent perceptual scoring and blinded listening are run with held-out
   speakers and bandwidth strata.
3. A pinned native/SDK provider is compared frame-for-frame under an agreed
   quality margin, with descriptor and installed-archive digests.
4. Blind detection or threshold estimation is validated separately; this
   comparator assumes the exact known mask.
5. SPADE/social-sparsity/C-OMP and band-limited POCS parity plus target-device
   paced timing are measured under an explicit workload.
6. Any public registration, descriptor, default-provider or CMake change gets
   separate SDK contract, conformance and release-gate work outside this task.

Scope confirmation: no shared `CMakeLists.txt`, `CONTRACTS.md`, public header,
descriptor registry, default provider, installed v0 behavior, board file,
handoff or other worktree was touched. No real corpora, weights, downloads,
licensed runtime, device, listening, release or benchmark-ingestion claim is
made. This change has **no public surface and no installed behavior change**.

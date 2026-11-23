# Band-limited POCS declipping (opt-in offline reference)

**SDK-BAND-LIMITED-POCS-DECLIPPING · Restoration acceptance profile · status:
opt-in, synthetic, developer-only, offline.** A deterministic, stdlib-only
band-limited projection-onto-convex-sets (POCS) declipper is implemented behind
a protocol-v1-shaped, task-local adapter boundary. It is **not** an SDK
provider, public API/ABI or descriptor change, registry entry, default
provider, Bench bundle, benchmark ingestion, listening result or release
qualification. Installed v0 remains 16 kHz mono float32, 160-sample frames;
this reference processes fixed **2048-sample offline blocks** and makes **no
realtime claim**.

Pinned base: `9677040cba2929f9936eaa565f200f585d5270a8`, branch
`swarm/SDK-BAND-LIMITED-POCS-DECLIPPING`. Nothing outside this evidence
directory is modified by the implementation.

## Source pins and what they establish

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`; set
`AUDIOML_ROOT` if the checkout lives elsewhere. Verification is by exact
SHA-256 and a missing pinned file is a **failure, not a skip**.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/distortion_restoration_20261028.md` | `8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71` | RST-01 task boundary; hard clipping at 0.35/0.55 of peak; band-limited POCS best local baseline; 2.74%/0.55% occupancy pilot; sparse alternatives require MATLAB/LTFAT/CVX; result is a small pilot with no listening. |
| `src/audioml_eval/distortion_restoration.py` | `c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f` | Normative `declip_pocs`: zero clipped samples, alternate band-limit with reliable-sample and saturation-cone projections, final band-limit/constraint pass; `cutoff_hz=7600`, `iterations=60`; plus `declip_linear` control. |
| `reports/distortion-restoration/20261028-synthetic-screen.json` | `87df91e30905ead24786146b8e82257b7132cd5cd51bcee46570955eff826ece` | Source-reported 12-clip screen; retained as provenance only, **not** reproduced or reused as a local result. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Restoration profile: freeze corruption, metadata and clean baseline; stratify by degradation and bandwidth; report validity, task-specific quality, output peak bounds and missing results. |
| `adapters/controls/adapter.json` | `3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599` | Public protocol-v1 envelope shape reused by the task-local descriptor (`inspect`/`run`, refs, configuration). |
| `adapters/controls/run.py` | `4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66` | Public request-validation pattern: strict JSON, duplicate-key and nonfinite-constant rejection, explicit refs. |

The pilot uses NumPy arbitrary-length rFFT; this reference uses a portable
power-of-two radix-2 transform on 2048-sample blocks. Numbers here are
therefore descriptive for these frozen synthetic stimuli, not a bit-exact
replay of the pilot or a real-speech result.

## Boundary and files

| File | SHA-256 | Role |
| --- | --- | --- |
| `adapter.json` | `56ce18285496ea628759ee2cc370c910bcce138e709c9cd0d2cdb9fb395605e6` | Task-local, unregistered descriptor; controls `identity`, `clipped_input`, `linear_interp`, `pocs_declip`; `modes: ["offline"]`. |
| `reference.py` | `d55aa9dc52a1bdffb124ce0780878361bfa049f7ee14196003890ebc915fdb30` | stdlib f32/radix-2 FFT, hard-clip corruption and mask, POCS projection with per-projection trace, linear-interpolation baseline, SI-SDR/RMSE, strict control validation (cap 60 iterations). |
| `fixtures.py` | `4c6058e2e8a623e21b65b41e10a401f9eb5e27025cc4f93838dd1b1e5aa1e889` | Pinned source digests and seven deterministic stimuli: band-limited tones, quiet clean, sparse/very-sparse transients, speech-like harmonic bursts, dense tones, nonfinite. Clean source frozen separately from clipping. |
| `run.py` | `88d8b49e2c95289cf85874a56b5273e90248c41addda5c783ef688353666b855` | `inspect`/`run` boundary; accepts a named fixture or a caller-owned 2048-sample waveform; canonical JSON result with input/clean/output digests, occupancy, peaks, scoring, trace and adverse status. |
| `report.py` | `e8c4e6e1075c1afe3cd4b71518a7f0e2fc0f5bea874a9623e06b0af5d818f50a` | Builds the canonical report solely by driving the adapter boundary. |
| `report.json` | `8d893e8055cdc2e982a4e568e7996b45d1b6dd73841ac2b701a15ec5160dc65b` | 35,794 bytes, one line, LF. Regeneration is byte-identical. |
| `report.json.sha256` | `658355d1009bc69547b6d527e0ed5e1c6752846fc788497d29ba24b466e94cec` | Digest sidecar. |
| `test_fixture.py` | `01c98680c06247ab707a83ea86e9684dd43b207d4934ecf06a22476866f04868` | 22 deterministic unittest cases. |

Local report digests: fixture spec
`9d557be7978ef765d23d230d62a4ed8a749661f3f2a48514c5863e3dfea4e443`;
clean/identity/POCS-clean f32 output
`a7ce0b077a5af0269afb212eb21511e5ebf4862e4dbca0def7833892a936ffab`
(all three equal — measured transparency).

## Reproduction (from the SDK worktree root)

Use Python 3.11.5 (stdlib only) and a scratch directory:

```sh
evidence=docs/task-evidence/band-limited-pocs-declipping
scratch="${TMPDIR:-/tmp}/pocs-declipping-$$"
mkdir -p "$scratch"

cp "$evidence/report.json" "$scratch/report.committed.json"
PYTHONDONTWRITEBYTECODE=1 python3 "$evidence/report.py"
cmp "$scratch/report.committed.json" "$evidence/report.json"
shasum -a 256 "$evidence/report.json"
cat "$evidence/report.json.sha256"

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "$evidence" -p 'test_*.py' -v
python3 -m json.tool "$evidence/report.json" > /dev/null

git diff --check
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-BAND-LIMITED-POCS-DECLIPPING
```

The test suite includes a clean-copy subprocess regeneration check, so it
verifies byte identity without overwriting the committed report. Expected:
22/22 tests pass, report digest
`8d893e8055cdc2e982a4e568e7996b45d1b6dd73841ac2b701a15ec5160dc65b`,
six source pins exact, `git diff --check` silent, board check reports
`in_progress` with the claimed base/branch/worktree.

## Frozen cohort and results (synthetic only)

18 cases: 17 complete, 1 adverse, 9 successful POCS runs, 17 rejected control
checks, 7 explicitly unrun items. Clipping occupancy and bandwidth cutoffs are
reported per case in `report.json`.

| Case | Stratum / stimulus / control | Occ. % | Peak in → out | SI-SDR (dB) |
| --- | --- | ---: | ---: | ---: |
| `clean_identity` | baseline · clean_bandlimited · identity | 0 | 0.900 → 0.900 | 120.0 |
| `clean_clip_no_occupancy` | baseline · clean_quiet · clipped_input | 0 | 0.300 → 0.300 | 120.0 |
| `clean_pocs_transparency` | baseline · clean_bandlimited · pocs | 0 | 0.900 → 0.900 | 120.0 |
| `occupancy_very_low` | 0.35 · very_sparse_transients · pocs | 0.4883 | 1.000 → 0.444 | 8.832 |
| `occupancy_low` | 0.35 · sparse_transients · pocs | 1.9531 | 1.000 → 0.472 | 8.865 |
| `occupancy_mid` | 0.55 · speech_like · pocs | 9.5703 | 1.000 → 0.561 | 13.807 |
| `occupancy_high` | 0.35 · dense_tones · pocs | 42.1875 | 1.000 → 0.387 | 9.398 |
| `occupancy_saturated` | 0.01 · clean_bandlimited · pocs | 98.6816 | 0.900 → 0.013 | 4.932 |
| `clipped_very_low` | control · very_sparse_transients | 0.4883 | 1.000 → 0.350 | 7.818 |
| `clipped_low` | control · sparse_transients | 1.9531 | 1.000 → 0.350 | 8.101 |
| `clipped_high` | control · dense_tones | 42.1875 | 1.000 → 0.350 | 9.263 |
| `linear_high` | adverse control · dense_tones · linear interp | 42.1875 | 1.000 → 0.781 | 4.885 |
| `clipped_anchor` | control · speech_like (0.55) | 9.5703 | 1.000 → 0.550 | 13.769 |
| `linear_interp_anchor` | control · speech_like · linear interp | 9.5703 | 1.000 → 0.550 | 12.784 |
| `bandwidth_narrow` | 2 kHz cutoff · speech_like · pocs | 9.5703 | 1.000 → 0.676 | 14.671 |
| `bandwidth_mid` | 3.5 kHz cutoff · speech_like · pocs | 9.5703 | 1.000 → 0.612 | 13.975 |
| `iterations_min` | 1 iteration (2 projections) · speech_like | 9.5703 | 1.000 → 0.553 | 13.786 |
| `nonfinite_input` | adverse · NaN at 17, Inf at 1025 | 51.5625 | 0.800 → none | n/a |

- **Clipping occupancy:** POCS improves synthetic SI-SDR over the clipped input
  in all four main strata (very low +2.01 dB, low +0.76 dB, mid +0.04 dB,
  high +0.14 dB). The 98.68% saturation case is a control showing heavy
  information loss (4.93 dB), not a successful restoration. Effects are
  small; the source pilot itself calls them modest.
- **Clean transparency:** identity and zero-occupancy clipped-input controls
  are bit-identical to the clean source. POCS on a clean band-limited source
  with cutoff 3.5 kHz is also bit-identical (max abs diff 0.0, digest above).
  No unconditional transparency is claimed for broadband clean input: the
  band-limit is destructive by design.
- **Bounded iterations:** controls are capped at 60 (61 is rejected). Traces
  have `iterations + 1` projections (the pilot's final extra pass). Max delta
  is finite and non-increasing: 0.00175 → 7.13e-5 at 60 iterations, and
  0.00175 → 0.00127 at 1 iteration. No divergence or unbounded loop is
  observed; no early-stop or iteration-quality guarantee is claimed.
- **Output peaks:** all 17 complete cases are finite; maximum observed output
  peak is 0.900 and every case stays within its input peak. This is a
  cohort-only bound, not a limiter guarantee.
- **Bandwidth:** at fixed 9.57% occupancy, 2 kHz projection scores 14.67 dB
  vs 13.97 dB at 3.5 kHz and 13.81 dB at 7.6 kHz on this synthetic source;
  this is a stratum observation, not a bandwidth-selection rule.

## Controls, adverse cases and skipped results

- `clipped_input` and `linear_interp` anchors are run on the same frozen clean
  sources, thresholds and masks. Linear interpolation **harms** the high-
  occupancy case (4.89 dB vs 9.26 dB clipped), matching the qualitative source
  finding that it can degrade clipped speech.
- 17 boundary rejections are retained with reasons: missing/unknown controls,
  threshold 0 / >1, cutoff outside 100–7900 Hz, iterations 0 / 61 / non-integer,
  nonnumeric or nonfinite threshold, bad refs, wrong protocol, wrong block
  length, duplicate JSON key and JSON `NaN`.
- Nonfinite **input** (NaN at 17, +Inf at 1025) is an explicit
  `adverse_numerical` result: no output samples are serialized, no SI-SDR is
  computed, and it cannot count as a pass.
- Seven results are recorded `not_run`: paired real-speech/EARS cohort,
  STOI/perceptual scoring and listening, installed native provider and
  descriptor conformance, target-device timing/realtime availability, release
  qualification and Bench ingestion, SPADE/social-sparsity/C-OMP parity, and
  reproduction of the pilot's 12-clip means. **No missing result qualifies the
  candidate.**

## Exact blockers and reopening conditions

This closes only the opt-in, offline, synthetic reference-fixture question.
It is **blocked from any release, quality, parity or benchmark claim** until
all of the following are done:

1. Build and pin a native/SDK provider at a fixed revision with descriptor and
   installed-archive digests; compare frame-for-frame on a frozen paired cohort.
2. Agree clipping-occupancy, bandwidth, transparency, peak and iteration
   margins plus content-delay/availability budgets before qualification.
3. Score rights-cleared real speech with an independent perceptual metric and
   blinded listening, including held-out speaker and bandwidth strata.
4. Add SPADE/social-sparsity/C-OMP comparisons and target-device timing under
   an explicit workload before any best-baseline or realtime claim.
5. Any public registration, descriptor, default-provider or CMake change needs
   separate SDK contract, conformance and release-gate work outside this
   task's scope.

Scope confirmation: no shared `CMakeLists.txt`, `CONTRACTS.md`, public header,
descriptor registry, default provider, installed v0 behavior, board file,
handoff or other worktree was touched. No real corpora, listening, target-device
timing, release qualification or benchmark ingestion is claimed.

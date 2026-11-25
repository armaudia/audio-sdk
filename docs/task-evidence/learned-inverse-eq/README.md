<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-LEARNED-INVERSE-EQ — task-local synthetic inverse-EQ evidence

**Status: `proposal_only_not_qualified` / `incomplete`.** This is a self-contained,
synthetic-only evidence package for a frozen six-band inverse-EQ reference. It
is **not** a released processor, not a Bench bundle, not a quality claim and not
a release gate. No public surface, installed behavior, default, descriptor,
registry, board, handoff or other task was changed.

## Exact scope and boundary

- Worktree: `audio-sdk` task branch `swarm/SDK-LEARNED-INVERSE-EQ`, rebased onto
  `origin/main` `2bc2a13aa4c5b398933fd9097d09746ce151216e` (initial pin was
  `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`).
- Write scope: only `docs/task-evidence/learned-inverse-eq/`. No shared
  `CMakeLists.txt`, `CONTRACTS.md`, API/ABI header, descriptor registry,
  installed provider, catalog or build file was touched.
- Fixed v0 format only: 16 kHz, mono `f32`, 160 samples/frame. The installed v0
  behavior is unchanged.
- Processor exposure is **deferred**: `contract.json`, `adapter.json`,
  `provider.json` and `report.json` all record `registered: false`,
  `default_enabled: false`, `expose_as_processor: false` and no public API/ABI
  change. No C boundary, C header or opt-in consumer is included.
- The Python adapter in `run.py` is task-local and unregistered. It produces
  developer result JSON, not a Bench result.
- No external learned model, weights, checkpoint, download, licensed runtime,
  WAV, corpus, real speech, listening test, device timing or release approval.

## Source pins and provenance

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless noted.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/level_tone_control_20261028.md` | `b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44` | Source study: six-band inverse-EQ ridge baseline, synthetic-only results and explicit warning that natural spectral balance is not established. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | DSP profile: sweeps, steps, impulses, silence, clean speech and a control; report gain, response, attack/release, headroom, delay and numerical behavior. |
| `audio-benchmark-platform/plan/swarm/check.py` | `5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539` | Read-only board validator used for `SDK-LEARNED-INVERSE-EQ`. |
| `api/include/audio_sdk/provider_v0.h` (boundary only) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public provider contract, read and pinned; unchanged. |
| `api/include/audio_sdk/session_v0.h` (boundary only) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public session facade, read and pinned; unchanged. |

The mutable board snapshot
`audio-benchmark-platform/plan/swarm/TASKS.json` had SHA-256
`b3e8aa913076c0b0496756cdbd1b717cc9f7e65206824198b33278e70c935294` when read
during final verification. The board is mutable and never qualifies or
disqualifies this evidence.
It is provenance only and never qualifies or disqualifies this evidence.

The source study reports a held-out synthetic inverse-EQ RMSE of 2.577 dB
versus 4.414 dB for identity. That figure is **not reproduced** here: this
package uses its own frozen synthetic perturbation, response probes and
seed, and reports only the measured values below.

## DSP-profile application

The `dsp` profile is applied in `report.json:dsp_profile` as follows.

| Profile element | Fixture / measurement |
| --- | --- |
| Sweeps | 100 Hz–8 kHz logarithmic sweep, 2 comparison lengths, analytic probe response and filtered-tone check. |
| Steps | Level step at one quarter of each step signal; RMS/gain error and state tracked. |
| Impulses | Single impulse at sample 16; cross-correlation delay and zero added delay. |
| Silence | All-zero stimulus; silent output and finite values checked. |
| Synthetic clean speech | Formant/harmonic excitation with syllable envelope and fixed-seed noise; paired perturbed and clean references. |
| Level/tone control | Synthetic RMS target control with 1 kHz notch, attack/release coefficients, peak ceiling and measured gain slew. |
| Interacting nonlinearity | `perturbed → learned_inverse → tanh(3x) → level_tone_control`, with three stage-removed ablations. |
| Headroom / clipping | Peak and dB headroom on every run; near-clip and deliberately clipped inputs included. |
| Numerical behavior | Finite counts, nonfinite rejection, out-of-range rejection, non-monotonic reset, stale epoch/position and partial final frame. |
| State transitions | Framewise vs whole-call equality, replay after reset, invalid-count audit and independent cold starts. |
| Adverse inverse | Ill-conditioned clustered probes and out-of-band noise amplification, explicitly non-qualifying. |

## Method

1. A frozen six-band EQ perturbation with gains
   `[-6, +4, -3, +5, -4, +3] dB` at
   `[125, 250, 500, 1000, 2000, 4000] Hz`, Q = 1, is generated as RBJ peaking
   biquads. Coefficients are deterministic and pinned by digest.
2. Twelve synthetic coefficient/response pairs are generated from a fixed LCG
   seed. Responses are analytic biquad magnitudes at nine probe frequencies
   (62.5 Hz–12 kHz) with small seeded jitter. The fixture is pinned by
   SHA-256; no external weights are loaded.
3. A ridge fit maps response probes to six inverse band gains. The learned
   correction is applied as a causal, zero-added-delay peaking biquad cascade.
4. Identity and fixed EQ (the frozen forward EQ, i.e. a colouration-doubling
   control) are measured **before** the learned inverse. Every candidate result
   is marked `qualifies: false`.

The result is a controlled synthetic EQ-inversion experiment only. It does not
establish a desired-response definition for natural spectral balance, and does
not select a processor for real speech.

## Synthetic results

All scores are paired against generated clean references. Identity is
bit-exact to the perturbed input in every comparison; no clipped or nonfinite
sample appears in any comparison.

| Condition | Variant | RMS gain error (dB) | Paired SNR (dB) | Peak | Measured delay |
| --- | --- | ---: | ---: | ---: | ---: |
| sweep | identity | +0.436486 | 10.002952 | 0.290933 | 0 |
| sweep | fixed EQ | +1.543840 | 3.878077 | 0.423221 | 0 |
| sweep | learned inverse | −0.011465 | 55.366408 | 0.199999 | 0 |
| step | identity | −0.033739 | 22.219566 | 0.370490 | −7 |
| step | fixed EQ | −0.058359 | 17.110439 | 0.416887 | −13 |
| step | learned inverse | −0.000234 | 75.491967 | 0.361924 | 0 |
| clean speech | identity | −1.941000 | 7.843217 | 0.237578 | 0 |
| clean speech | fixed EQ | −2.291138 | 3.268946 | 0.247058 | −1 |
| clean speech | learned inverse | −0.012671 | 55.658313 | 0.211906 | 0 |

The nonzero offsets for some controls are cross-correlation maxima caused by
colouration, not added buffering; the learned inverse measures 0 samples on
all three conditions. Probe-response RMSE to flat is
identity `2.493142561 dB`, fixed EQ `4.986285122 dB`, learned inverse
`0.012285013 dB`. Frozen inverse gain error is at most `0.020509 dB` per band.

The nonlinear interaction chain is finite with output peak `1.0` (the
task-local level/tone limiter ceiling), gain trace peak `8.990165`,
gain trace minimum `1.743083`, configured attack/release `0.35 / 0.08` and
maximum per-frame gain slew `+1.922203 / −0.541407`. This is an adverse
saturation case, not an accepted operating point.

### Explicit adverse and failure controls

- Ill-conditioned inverse: clustered probes produce condition estimate
  `7.608175e17`, gain excursions up to `30.816 dB` and still-finite but
  unusable coefficients.
- Out-of-band noise: nominal correction changes 12–15 kHz RMS by
  `−0.237117 dB`; the ill-conditioned correction amplifies it by
  `+8.833983 dB`. Both are reported, and neither qualifies.
- Seven invalid/missing calls (missing frame, wrong type, partial frame,
  nonfinite, out-of-range, stale epoch, stale position) are rejected with DSP
  state unchanged and an incremented invalid-count audit.
- Clipped input (±1.4) and near-clip input are processed explicitly; no
  missing, skipped or nonfinite result is counted as a pass.
- Level/tone control, reset, epoch monotonicity, partial final frame and
  three cold-start rebuilds are checked.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `contract.json` | `3503504947a558257c82e1b181f21189d5534a05a1c65c92505e9ad2da0d71e8` |
| `adapter.json` | `50238d294c281d3d13fdc02bc940316f148d7382cc05f9da8c1dc16e1e65ce4d` |
| `provider.json` | `487bb9520a61ed5231b078b3b22da1bc8983f6ebf68e270899006b9b27aa8896` |
| `scorer.py` | `27e16af815ff41e851d3efb84f19fd5959d5ed3f1a4e5531d655d38c63bbe8ee` |
| `reference.py` | `a210ae577090b758b40ef138b17285d83a7e6751abcc4f63d19f0e56a5c530e2` |
| `fixture.py` | `1fdc77da6fbfe69d98416d917275885dfea6e3a0f9060232277e2ae283596fb2` |
| `run.py` | `d15dd44a405130c1b1b66db9b474d3c24e624b03880013ac5ccb819b376ea5ca` |
| `verify.py` | `7bb42a4681c80a1a87ddb461dcbd38f81d53dc2fad800d83ae3efd9ccedb1a36` |
| `check_licensing.py` | `4de19b994e04267996c18503ba49deeebb3f7d6847492d9c8dab3bb419f0587e` |
| `test_reference.py` | `a52b9e32031523d4d547c67b9399a2fb88fde7a032f61f0eb58db2be189ab739` |
| `report.json` (file bytes) | `2ee8271a3b08c989fe037f2753d013b8e6dcafb6881e5b0e59bb6724eff9e0dc` |
| `report.json.sha256` (file bytes) | `56b2ec8254045d1ffbf7478afc06af81b21dc97475270337c1ddd4b057a8e451` |
| `crosscheck_vectors.json` | `9521cce3a3843d8e1210b5f15ec472583e57719bc2f4de9a22b66ee7f075e096` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`) plus one trailing newline. Its canonical digest recorded in
`report.json.sha256` is
`474e579b3519f9be8bf659c7c371c63573d9fa67bb7dd65d4aed5f738b2978c2`.
The frozen response fixture digest is
`3226c4224ac33e0a88c0ab9db732d9e6c2c055fba1f95e20c75f2ba21a30389f`;
the frozen coefficient digest is
`aa9944f0cafc8a07ed1c65909050f1b9b47ad3f2cdde4f520ef4af93e05572a1`.
`SOURCES.sha256` pins every file in this directory except itself.

## Reproduction

Run from this directory unless otherwise noted. Generation order matters:
crosscheck, report, sources.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py --crosscheck
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 check_licensing.py
```

Regeneration of `crosscheck_vectors.json`, `report.json` and `SOURCES.sha256`
is byte-identical; `verify.py` additionally rebuilds the canonical report three
times in separate cold Python processes and compares the digests.

REUSE 6.3.0 lint was run both on this package in isolation (copy the package
with the repository `REUSE.toml` and `LICENSES/Apache-2.0.txt` into a temporary
project root) and on the full worktree. The scoped result is clean: 15/15 files
with copyright and license information, 0 invalid expressions, 0 problems. At
final verification the full-worktree lint reported six invalid SPDX expressions
in `docs/task-evidence/clang-sanitizers-qualification-matrix/` and
`docs/task-evidence/rnnoise-speech-probability/`; those files belong to other
tasks, are outside this task's write scope and were not modified here. Every
file in `docs/task-evidence/learned-inverse-eq/` passed both checks.

Optional task-local adapter request (example, writes a canonical result):

```sh
cat > /tmp/lieq-request.json <<'JSON'
{
  "protocol_version": 1,
  "operation": "run",
  "candidate_ref": {"kind": "task-local", "id": "learned-inverse-eq", "revision": 1},
  "adapter_ref": {"kind": "task-local", "id": "learned-inverse-eq", "revision": 1},
  "configuration": {"control": "learned_inverse"},
  "attempt_id": "example-1",
  "stimulus_id": "impulse",
  "samples": null
}
JSON
PYTHONDONTWRITEBYTECODE=1 python3 run.py --request /tmp/lieq-request.json --result /tmp/lieq-result.json
```

SDK baseline build/install check (outside the worktree):

```sh
TMP=$(mktemp -d "${TMPDIR:-/tmp}/lieq-sdk.XXXXXX")
cmake -S <worktree> -B "$TMP/build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMP/build" --parallel 4
ctest --test-dir "$TMP/build" --output-on-failure
cmake --install "$TMP/build" --prefix "$TMP/prefix"
```

Board and whitespace checks (from the worktree root):

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-LEARNED-INVERSE-EQ
git diff --check
git diff --cached --check
```

## Remaining gates

1. Held-out real-speech paired response and quality evidence with pinned rights
   and blinded listening.
2. Desired-response definition and calibration for natural spectral balance.
3. Ill-conditioning guard, band limits and out-of-band amplification limits.
4. Target-device CPU, memory, deadline and real-time pacing measurement.
5. Provider intake, license, descriptor and public catalog review before any
   processor exposure or default.

Until all gates pass, no default, production, quality or release claim exists;
the installed SDK v0 remains frozen and unchanged.

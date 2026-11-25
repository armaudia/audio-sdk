<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SPEEX-RESAMPLER — task-local varispeed resampler evidence

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This is a bounded, deterministic,
task-local reference that compiles the **exact vendored SpeexDSP resampler
source** and measures it on synthetic stimuli. It is **not** an installed
provider, descriptor, registry entry, default, public ABI change, benchmark,
listening result, device-timing measurement or release claim.

The component is a **varispeed / resampling** rate changer: it changes duration
**and pitch**. It is not a pitch-preserving time-scale modifier. That
limitation is characterised as an adverse control, not hidden.

## Exact scope

- Write scope: `docs/task-evidence/speex-resampler/` only. Shared CMake, CI,
  `CONTRACTS.md`, public headers, descriptors, registry/defaults, installed v0,
  board/handoff files, rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. This
  package does not install or register a provider; the adapter is an
  unregistered, default-OFF developer harness.
- The harness compiles `third_party/speexdsp/libspeexdsp/resample.c` **in
  place** through the public documented `speex/speex_resampler.h` boundary. No
  vendored file is copied, edited, patched or relicensed.
- All stimuli are analytic or seeded. No real speech, music, room recording,
  model weight, download, corpus, listening panel or device timing is present.
- Missing, invalid, nonfinite and out-of-range inputs fail closed with no
  metrics. No missing or rejected result qualifies a candidate.

## Geometry

For playback speed `r`, the source is relabelled from `16000 Hz` to
`16000*r Hz` and converted back to the installed `16000 Hz` playback clock.
This is the standard varispeed construction:

| Quantity | Exact task-local relation |
| --- | --- |
| Output samples | `ceil(N / r)` |
| Output duration | `N / (16000*r)` seconds |
| Pitch | `f * r` (adverse varispeed property) |
| Source anchor | `round_half_up(p / r) + output_latency` |
| Frame geometry | caller blocks of 160 samples; final partial block is passed as-is |
| Flush | bounded `NULL`-input flush until zero output |

All four declared speeds have exact integer `16000*r` input clocks, so duration
and anchor checks are exact integer arithmetic, not tolerance fits.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This disclosure, geometry and reproduction guide. |
| `harness.c` | C11 CLI wrapper over the vendored `speex/speex_resampler.h` boundary; raw float32 mono, deterministic summary line. |
| `reference.py` | Stdlib-only Python driver: fixtures, compile/run, exact rational model, metrics, canonical report. |
| `run.py` | `--report`, `--sources`, `--crosscheck` generator. |
| `verify.py` | Strict read-only verifier: pins, JSON, semantics, byte reproduction, three cold starts, licensing, git scope. |
| `check_licensing.py` | Local SPDX/REUSE and third-party-notice checks. |
| `test_reference.py` | Deterministic standard-library acceptance suite. |
| `contract.json` | Frozen task contract, pins, boundary, report identity and eight blocked gates. |
| `report.json` | Canonical machine-readable synthetic evidence. |
| `report.json.sha256` | SHA-256 of the canonical report bytes. |
| `SOURCES.sha256` | Curated pins for context sources, boundary headers, vendored files and task artifacts. |
| `LICENSE` | Apache-2.0 sidecar for this directory. |
| `THIRD_PARTY_NOTICES.md` | SpeexDSP BSD-3-Clause/KISS attribution pointer. |

## Pinned sources and boundary

Paths prefixed `source:` are relative to `/Users/htsakanyan/workspace/audio/audioml`;
all other paths are relative to this SDK worktree. Exact digests are in
`SOURCES.sha256` and `contract.json`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Candidate context: Speex resampler is a varispeed-only cheap fallback. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Component provenance only. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | `rate` acceptance profile. |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Fixed v0 format, mapping, drain and boundary semantics. |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public boundary pin, read-only. |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public boundary pin, read-only. |
| `third_party/speexdsp/libspeexdsp/resample.c` | `c4ec3bc71fc4414d7ebd62fc745290c7b5b06b149a05dd70cf72553bc57c8c76` | Compiled in place. |
| `third_party/speexdsp/include/speex/speex_resampler.h` | `7e439ec0dd30c32216b3ced17135f8992e5aaf53389d3f5996a7d900c453e65f` | Public adapter boundary. |
| `third_party/speexdsp/COPYING` | `2654a4264b2bfe298dedc508748d140111840c315cc8eb646a3a68c13fa75b01` | BSD-3-Clause-style terms. |
| `deps/lock.json` | `7e834253dad944604a2e2283f4d809ab1383c9db4f08b83482a8b41efc043e3a` | SpeexDSP revision `7a158783df74efe7c2d1c6ee8363c1e695c71226`, v1.2.1. |

The mutable board row is used **only** through a stable linked-row identity
(`component`, `task`, `evidence_path`, `record_name`), never through its line
number or a mutable snapshot digest. The snapshot digest is provenance only.

## Rate profile application

`VERIFICATION.md` requires source/output mapping, duration, pitch, transient
audibility and playback buffering with 1×, rate changes, unfamiliar speech,
music, silence, rebuffer, drift and the final partial window. Each item maps to
a synthetic proxy:

| Profile item | Local synthetic evidence |
| --- | --- |
| Source/output mapping | Impulse anchors on four declared speeds; exact residual 0. |
| Duration | Exact integer `ceil(N/r)` equality for 0.75×, 1×, 1.25×, 1.5×. |
| Pitch | Goertzel dominant-frequency ratio matches speed; 1× is 1.0; 1.25× shifts pitch ≥0.10 (adverse). |
| Transient audibility | Impulse peak position and amplitude within the declared window. |
| Playback buffering | Caller-clock 160-sample FIFO with a stall/refill/resume window and zero skipped audio. |
| 1× / rate changes | Four frozen speeds; no dynamic smoothing is claimed. |
| Unfamiliar speech | Deterministic speech-like harmonic spans with pauses and a filler; proxy only. |
| Music | Deterministic chord/percussion negative control; no music-quality claim. |
| Silence | Exact zero output on every speed. |
| Rebuffer | Playback pauses then resumes; played samples equal expected. |
| Drift | 48,000-sample synthetic input, exact length and anchors, no device clock. |
| Final partial window | 8,075 accepted samples at 1.25× → exactly 6,460 output samples. |
| Speech preservation | Voiced/pause RMS contrast > 10 dB on every speed; not intelligibility. |

## Exact recorded results

All values are regenerated by `run.py --report`; the canonical report is
byte-identical across three cold-start processes.

| Speed | Output samples (from 9,600) | Exact | Pitch ratio | Anchor residual | Pause contrast |
| --- | --- | --- | --- | --- | --- |
| 0.75× | 12,800 | yes | 0.75 | 0 samples | > 10 dB |
| 1.0× | 9,600 | yes | 1.0 | 0 samples | > 10 dB |
| 1.25× | 7,680 | yes | 1.25 | 0 samples | > 10 dB |
| 1.5× | 6,400 | yes | 1.5 | 0 samples | > 10 dB |

Adverse controls (all fail closed, no metrics): nonfinite input, 0.25× speed,
3.0× speed, quality 11, empty stimulus and a non-160 frame declaration. The
harness also scans output for nonfinite values.

## Exact digests

| Artifact | SHA-256 |
| --- | --- |
| `report.json` | `abc096dd8ca3153c9f8a70fb2bc04f87e170ae5f4479939bf782802780b519cd` |
| `report.json` canonical text | `119ae84bfa18f10341fbc7c434f6c5363b94a66bf7edaafc19290036d5b5369a` |
| `contract.json` | `3a28b41b97920ac0f4aaa69408b5ad850eeb3040375f13fbcd1ff7deb0553952` |
| `harness.c` | `6032be99aba28d706444fc7235f893dcf54e32b4f1a0da7656f9632353a6a447` |
| `reference.py` | `14ac812bee7e993056cfa638ec31a7def5f58addb528065a514e49317530f430` |
| `run.py` | `af7ee05687d8550359d359785423d6a83d48b6ce35b848f03cf53997b9115251` |
| `verify.py` | `5da473dbe9761448d93b883fd810bb45176cf9bb88691885fd99402ec6476cca` |
| `test_reference.py` | `b3e91126e245375a24c43695d48eb0be18ca0bae94b2b31d2b94e3aa3a9c01e5` |
| `check_licensing.py` | `92572bb4e16edc4d05c025a62dd65483d21ffa5dfd259f422ca5312cf1c86504` |
| `README.md` | `README_SHA256` |
| `LICENSE` | `806d46225a31c67e84db5ee50e5f09260e356fccb91c1e3d1e1b436cb0c74fdb` |
| `THIRD_PARTY_NOTICES.md` | `b00cca99ac97efd5d07fcb3c4d42d67807cab8caeabdbf229ce57e9aa7408555` |

## Reproduction

All build output stays outside the worktree. `SPEEX_RESAMPLER_SCRATCH` is
optional; without it a fresh system temporary directory is used.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SPEEX-RESAMPLER
TASK="$WT/docs/task-evidence/speex-resampler"
SCRATCH=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/speex-resampler
mkdir -p "$SCRATCH"

cd "$TASK"
SPEEX_RESAMPLER_SCRATCH="$SCRATCH" PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
SPEEX_RESAMPLER_SCRATCH="$SCRATCH" PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
SPEEX_RESAMPLER_SCRATCH="$SCRATCH" PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
SPEEX_RESAMPLER_SCRATCH="$SCRATCH" PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 check_licensing.py
python3 -m json.tool report.json >/dev/null
shasum -a 256 report.json
git -C "$WT" diff --check
```

Expected: the report digest above, all unit tests pass, `verify.py` prints
`pins_ok=... reproduction_ok=1 repeats_ok=3 ...`, licensing passes and the
diff check is clean. `cc` (or `$CC`) and `libm` are required; the compiler is
recorded only as `system CC`, never as a quality or support claim.

## Remaining release gates (all blocked)

1. `real_speech_paired_cohort` — no permitted paired speech holdout.
2. `real_music_and_silence_cohort` — no rights-qualified music/silence set.
3. `authorized_listening` — no blind listener panel or perceived pitch/quality.
4. `target_runtime_pacing_and_buffering` — no device fill/flush, deadline, CPU or memory.
5. `installed_provider_intake_and_public_surface` — no provider intake, descriptor or ABI decision.
6. `upstream_source_and_rights_review` — pins compiled, but no independent rights/version review.
7. `device_clock_and_drift_qualification` — no real capture/playback clock drift.
8. `release_manifest_and_bench_bundle` — no release manifest, Bench bundle or host matrix.

**Exact blocker for any rate qualification:** a rights-qualified, task-matched
real speech/music cohort on a locked host, with independent clock/drift
telemetry, authorized listening and provider-intake/rights review. None of
those artifacts is present in this workspace, so this package cannot qualify
the component. It deliberately records `DEFER`, `incomplete` and
`not_qualified` rather than inventing them.

## Non-claims

No public API/ABI, installed v0, descriptor, registry, default, shared build or
CI change. No provider registration. No real corpus, model, weight, download,
device timing, listening result, benchmark, publication or release
qualification. No pitch-preserving time-stretch claim. No missing result
qualifies a candidate.

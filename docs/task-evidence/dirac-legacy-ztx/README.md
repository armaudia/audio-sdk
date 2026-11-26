<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DIRAC-LEGACY-ZTX - DIRAC (legacy ZTX) vendor-artifact and rights blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DIRAC (legacy ZTX)` (`component_id=dirac-legacy-ztx`). The acceptance profile is
**Rate**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify either candidate, and no DIRAC or ZTX result exists here.

The exact licensed legacy DIRAC artifact and the contemporary Zynaptiq ZTX
comparator are **absent**. This package records the exact blocker, applies the
Rate profile to a bounded deterministic synthetic probe, and makes no candidate
duration, pitch, transient, buffering, listening, benchmark or release claim. It
is **not DIRAC** and **not ZTX**: no vendor binary, SDK, header, evaluation kit,
installer, SLA, license, source, recording, corpus, model, device clock or
listening result is present, copied, downloaded, loaded, imported or executed.
Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=dirac-legacy-ztx`) is
`external-adapter`, `verification_profile=rate`, area `Rate and content`. Its
only evidence link is
`cpp-library/pipeline-validation/playback-speed-candidates.md` sections
3.13-3.14, which records:

> Legacy DIRAC is the legacy name for the DSP Dimension technology; current
> licensing is through Zynaptiq. Old free binaries should not be adopted without
> checking their terms.

The contemporary ZTX tiers are source-reported as: **LE** free-to-use under a
signed per-product SLA, one channel at 44.1/48 kHz and no dynamic stretch/pitch
changes; **STUDIO** two channels, 8-96 kHz, no dynamic changes; **PRO** any rate,
unlimited channels and dynamic parameter changes. The same record states that
no evaluation kit, pricing or local run existed on 2026-11-04, and the vendor has
no public source.

Consequently:

- no licensed legacy DIRAC binary, installer, archive, platform identity or
  immutable SHA-256 is staged at any data, adapter or vendor directory;
- no ZTX STUDIO/PRO evaluation kit, quote, approval, archive hash, header,
  library or signed SLA is staged;
- no exact callable API, symbol list, block/seek geometry, channel/rate limit,
  dynamic-rate semantics, content delay or final-partial behavior is locally
  verified;
- no executed license, redistribution, product-use, derivative-output,
  attribution/notice or patent-indemnity review exists;
- no rights-cleared unfamiliar-speech or music cohort, authorized listening,
  intelligibility score or candidate render exists;
- no target-device pacing, fill/flush, CPU, memory, power or deadline
  measurement exists;
- no provider intake, descriptor/registry decision, independent review or
  default/release approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; machine-readable blocker records are in
`contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-DIRAC-LEGACY-ZTX`, `708b9a4197ed35fd2528fad425832c55ef393eb7` |
| Reviewer | `reviewer-DIRAC-LEGACY-ZTX` |
| Task mode | `external-adapter` |
| Acceptance profile | `rate` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate runtime | absent: legacy DIRAC and Zynaptiq ZTX both unavailable |
| Candidate geometry | not locally verified; no rate/channel/block value asserted |
| Local probe | deterministic native-grain Hann OLA, 1024/512, ramp 800 |
| Probe rate range | `[0.8, 1.5]`; whole synthetic clips only |
| Provider registration, default, ABI, CI | none |

The probe is an original stdlib-only reference over a frozen synthetic fixture.
It is not learned, uses no weights, and cannot qualify either candidate.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json` -> `acceptance_profile` and `rate_profile.coverage`; each item is
checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Source/output mapping | synthetic only | Monotone output centers, native source windows, mapping digest and terminal flags per case |
| Duration | synthetic only | Rounded cumulative source-to-output map; zero error in all 13 cases |
| Pitch | synthetic only | Autocorrelation proxy on synthetic stationary tones; listening deferred |
| Transient audibility | synthetic only | Synthetic click peak/width compared with identity; not listening |
| Playback buffering | synthetic only | Caller-owned FIFO checkpoints in source samples/ns; no device pacing |
| 1x | synthetic only | Byte-exact identity passthrough, 9600 -> 9600 |
| Rate changes | synthetic only | 1.25x, 1.5x, 0.8x and a four-segment drift schedule |
| Unfamiliar speech | synthetic only | Generated voiced/mixed surrogate, not a recording or speaker |
| Music | synthetic only | Generated three-tone surrogate, no music rights |
| Silence | synthetic only | All-zero clip; pitch withheld, never imputed |
| Rebuffer | synthetic only | Source-timestamped 1600-sample deficit, uncompensated |
| Drift | synthetic only | Four source-timestamped rates with an 800-sample ramp |
| Final partial window | synthetic only | 12485-sample non-frame-aligned clip; 5 input and 68 output partial samples |
| Pause/filler tied to source timestamps | synthetic only | Protect/flex labels frozen at source samples 0/4800/6400/11200/12800 |
| Speech preservation | synthetic only | Mapped RMS of protected synthetic intervals; intelligibility blocked |

Pause/filler decisions are tied to frozen source timestamps, never wall time,
playback position or a device clock. The labels are synthetic metadata, not a
real VAD/ASR gate.

## Results (all synthetic; overall DEFER)

- 13 cases: 9 pass all applicable surrogate checks, 2 are explicit adverse
  controls, and 2 non-adverse cases miss only the 2 dB synthetic speech-RMS
  tolerance. No candidate is qualified, exposed or compared.
- Identity `9600 -> 9600` byte-exact. `1.25x` `9600 -> 7680`, `1.5x`
  `9600 -> 6400`, `0.8x` `9600 -> 12000`; every duration error is `0` samples.
  `19200 -> 16000` at `1.2x`, `19200 -> 13714` at `1.4x`, `19200 -> 18065`
  for the four-segment drift schedule.
- Pitch proxy: `222.22 -> 222.22 Hz` at 1x and 1.5x; `216.22 Hz` at 1.25x
  (`0.973` scale) and `219.18 Hz` at 0.8x (`0.986`), both inside the 3% proxy
  tolerance. Varispeed adverse control shifts `222.22 -> 280.70 Hz`
  (`1.263` scale) and never qualifies.
- Transient proxy: identity and candidate maximum threshold-crossing width are
  both `7` samples on the synthetic clicks; this is a weak synthetic proxy and
  no listening result.
- Rebuffer at source sample `6400` (`400000000` ns) records a `1600`-sample
  uncompensated playback deficit with no fabricated recovery.
- Final partial input: `12485` samples (`5` partial in the last 160-frame);
  output `9988` samples (`68` partial); final OLA window carries `260` valid
  output samples.
- Protected synthetic speech RMS ratios: `-1.145` to `-1.277` dB at `1.2x`,
  `-1.316` dB for music, `-1.252` dB maximum for drift; the `1.25x` rebuffer
  and final-partial cases measure `-2.346` and `-2.007` dB and therefore miss
  the 2 dB tolerance. These are OLA phase-cancellation observations, not
  listening or candidate results.
- All outputs are finite, peak `<= 0.782`, and no output sample is uncovered or
  clipped.

## Failure controls and explicit non-claims

- **Silence:** pitch is withheld, not imputed; the case does not qualify.
- **Varispeed adverse:** pitch shifts by `1.263x`; recorded as a non-qualifying
  control, not a TSM substitute.
- **Unsmoothed rate-step adverse:** a `1.0x -> 1.5x` step with zero ramp is
  recorded and never qualifies.
- **Missing rebuffer event:** the metric is withheld; no playback gap is
  fabricated.
- Invalid/withheld controls include duplicate JSON key, NaN JSON constant,
  non-object root, nonfinite/infinite/empty/out-of-range samples, missing and
  invalid schedules, nonfinite/zero/oversized/undersized rates, nonmonotone
  schedule, missing origin, negative source position and unknown case.
- No vendor artifact, runtime, source, header, evaluation kit, SLA, license,
  recording, corpus, model, device timing, pacing, CPU, memory, power,
  listening, benchmark, provider registration or release claim is made.

## Exact source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`; override with
`SOURCE_ROOT`. `run.py` and `verify.py` recompute every digest; a missing or
changed pin is a failure, never a skip.

| Pinned source | SHA-256 | Use |
| --- | --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | DIRAC/ZTX vendor boundary, tiers, rate semantics and caveats |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Offline-versus-streaming and licensing provenance only |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Structured candidate record and profile |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` | Human inventory row |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | `rate` acceptance profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Delivery sequence and component tracks |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Installed v0 boundary |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | SDK build and integration notes |

The merged sibling time-stretch evidence packages reviewed for shape and
non-claim discipline are `docs/task-evidence/rubber-band-r3-offline`,
`signalsmith-stretch`, `soundtouch`, `granular-tsm`, `ola-sola`,
`phase-vocoder-baseline`, `psola-praat`, `sonic`, `ffmpeg-atempo` and
`bungee-basic`. They are cited as reviewed context only, not copied, and none
is a DIRAC or ZTX result.

Unchanged public boundary pins:

| Header / file | SHA-256 |
| --- | --- |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |

The mutable board snapshot read at setup is provenance only and is never
hashed, pinned or used as a digest source. Only the stable linked row
(`id, title, repository, mode, component, depends_on`) is gated:
`0c760fb3ae47a947a34b8b354a4c633707884bbaad8c8c1d5fd3a88f5d1ad33a`.
`SOURCES.sha256` pins every local artifact except itself.

## Reproduction

From this task directory (Python 3, stdlib only, no network):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check      # 3x cold-start compare
PYTHONDONTWRITEBYTECODE=1 python3 run.py              # 3x byte-identical write
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m json.tool contract.json >/dev/null
python3 -m json.tool report.json >/dev/null
```

`run.py` refuses to write unless three cold-start rounds are byte-identical, so
regeneration preserves `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` exactly. `verify.py` checks strict JSON (duplicate keys and
nonfinite constants), all pins, artifact pins, the stable board row, canonical
bytes, three cold-start rounds, SPDX coverage, scope, qualification and the
eight blocked gates.

From the worktree root:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-DIRAC-LEGACY-ZTX
git diff --check
git diff --cached --check
```

## Licensing and SPDX

The source-reported vendor path is commercial closed source: ZTX LE is
free-to-use under a signed per-product SLA, and STUDIO/PRO are licensed. That is
a vendor-page claim only; no license text, SLA, evaluation kit, price or local
run is staged or verified. The local files are Apache-2.0 with
`SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes` headers/sidecars.

## Remaining gates (all blocked)

1. **RG-01** Pin the exact licensed legacy DIRAC artifact and approved ZTX
   STUDIO/PRO comparator with immutable vendor/version/platform identity,
   archive or binary SHA-256 and license/SLA references.
2. **RG-02** Admit the runtime in an isolated hash-pinned tree, reproduce
   installation and verify identity with fail-closed absent behavior.
3. **RG-03** Clear license, SLA, redistribution, product-use, derivative-output,
   attribution/notice and patent-indemnity terms for the exact tier.
4. **RG-04** Map exact rate/channel/block/dynamic-rate/content-delay geometry
   into the installed 16 kHz mono float32 160-sample boundary with parity.
5. **RG-05** Qualify on rights-cleared unfamiliar speech and music with
   authorized listening, pitch, transient, duration and speech-preservation
   scoring.
6. **RG-06** Measure state, reset, dynamic rate changes, nonfinite/peak bounds,
   rebuffer/drift recovery and availability at the exact runtime.
7. **RG-07** Measure target-device pacing, fill/flush, buffers, CPU, memory,
   power and deadlines under the intended workload.
8. **RG-08** Complete opt-in provider intake, descriptor/registry review,
   independent exact-head review and default/release approval.

Until every condition in `contract.json.reopen_condition` is closed, both
DIRAC and ZTX stay **DEFER**, **incomplete** and **not_qualified**.

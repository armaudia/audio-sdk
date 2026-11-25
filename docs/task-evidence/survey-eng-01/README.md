# SDK-SURVEY-ENG-01 — Framing, format conversion and resampling

**Disposition: taxonomy and comparison only; no new execution and no release claim.**
`ENG-01` (legacy `F16`) is a `support` category whose purpose is to provide correct
formats and rates to candidates. The original registry records `catalogued`
discovery with `candidate_census_status=not_started` and
`benchmark_status=not_started`; the legacy backlog says to plan discovery across
required source buckets. This map matches those original families, the single
named source lead and the existing historical records to SDK components. It does
not run a candidate, qualify a component or change a board/handoff entry.

Survey owner: `agent-SURVEY-ENG-01`; independent reviewer:
`reviewer-SURVEY-ENG-01`. Claim base: audio-sdk
`c9296ae96a2b58efae559bd22e7760122c886df8`; branch
`swarm/SDK-SURVEY-ENG-01`; worktree:
`/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SURVEY-ENG-01`.
Component IDs come from `plan/INVENTORY.json`; task IDs come from
`plan/swarm/TASKS.json`. “Historical local” means a pinned record documents an
execution in the original workspace; it was not rerun for this survey. The
mapped research controls use the **Evidence** and **Tool** profiles in
`plan/swarm/VERIFICATION.md`.

## Original method families

| Original family | Catalogued text | Component owners and role | Evidence status / missing evidence |
| --- | --- | --- | --- |
| `framing-channel-mapping` | Framing/channel mapping | `typed-frame-resample-and-drift-diagnostics` / `SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS`; `identity-pcm-and-noop-fixtures` / `SDK-IDENTITY-PCM-AND-NOOP-FIXTURES`; `speexdsp-ns-reference` / `SDK-SPEEXDSP-NS-REFERENCE` | A source-local Python conversion/clock model and an installed D=0 identity control exist. No native installed conversion provider, paced workload, device framing path or measured channel-map timing was found. The SpeexDSP component owns a private object build, not a resampling interface. |
| `bandlimited-resampling` | Bandlimited resampling | `numpy-scipy-soundfile-wav-and-resampling` / `SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING`; `speex-resampler` / `SDK-SPEEX-RESAMPLER`; `libsamplerate` / `SDK-LIBSAMPLERATE`; `libsoxr` / `SDK-LIBSOXR` | The SciPy polyphase fixture is offline-only and evaluated. The three upstream resampler leads are `considered` comparator-matrix entries. No pinned executable S42/SpeexDSP comparison, anti-alias/transient control, or measured conversion-cost/content-delay result at an SDK boundary was found. SciPy output is not evidence for SpeexDSP or the other two libraries. |
| `no-ml-requirement` | No ML requirement | none | Not applicable. No ML family, checkpoint or weight search is catalogued for ENG-01, so no ML evidence is missing. No learned quality score is substituted for a conversion control. |

The fixed v0 boundary is unchanged: 16 kHz, mono, float32, 160-sample frames with
`resampling=none` in effective config. `CONTRACTS.md` accepts only that tuple at
the provider boundary, so any rate, channel or format conversion stays outside
the provider ABI. `README.md` lists the three task-local PCM/resampling controls.
Explicit conversions in the typed-frame proposal are **outside** that ABI; they
are not descriptors, defaults or installed behavior.

## Source lead S42

| Registry lead | Mapping and outcome |
| --- | --- |
| **S42 — [SpeexDSP resampler implementation](https://github.com/xiph/speexdsp/blob/master/libspeexdsp/resample.c)** | The registry records `access_scope=direct` for an unpinned `master` URL. The SDK checkout vendors the same upstream project/path at `third_party/speexdsp/libspeexdsp/resample.c`; `UPSTREAM.md` pins upstream revision `7a158783df74efe7c2d1c6ee8363c1e695c71226` (v1.2.1) and a BSD-3-Clause-style notice. This is **not** a byte-equal pin of the registry's `master` URL. `core/providers/speex/provider.cmake` compiles that source into a private `as_speexdsp` object, while `speex_provider.c` exposes fixed-format noise suppression and no resampler API. The component owner for the lead is `speex-resampler` / `SDK-SPEEX-RESAMPLER` (`considered`, `sdk-reference`); `speexdsp-ns-reference` owns the build integration but not a resampling capability. |

**Reported only:** the playback-speed comparator matrix groups libsamplerate /
libsoxr / Speex resampler as varispeed-only, with “Very low” latency/effort and a
“Cheap fallback if pitch shift is acceptable” verdict. It supplies no command,
revision, digest, corpus or local run. Its BSD-2 / LGPL-2.1 / BSD-3 labels are
matrix text, not a rights clearance. **Locally:** the vendored source is present
and compiled, but no resampler executable, rate-pair matrix, anti-alias control
or conversion-delay measurement was found for S42.

## Historical executions

| Record | Comparison inputs and controls | Assets | Local vs reported outcome |
| --- | --- | --- | --- |
| Offline WAV/resampling fixture — `numpy-scipy-soundfile-wav-and-resampling` / `SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING` | 11 frozen synthetic signals (impulse, 1 kHz sine, multitone, silence, noise, ramp, stereo, 3-channel, 8/1/0-frame); 11 caller-owned FLOAT WAV roundtrips; 36 cases from 6 signals to 8/16/22.05/32/44.1/48 kHz. Controls: 16→16 identity bit-exact, expected `ceil(len*up/down)` finite outputs, PCM_16→f32 mismatch (max abs error `2.8767e-05`), malformed/LFS/non-WAV rejection, rate/channel/shape/nonfinite guards, and explicit `missing_optional_selection`. | No audio, model or downloaded binary. Installed NumPy 2.5.4, SciPy 1.18.1, SoundFile 0.14.0 and libsndfile 1.2.2 bytes are pinned in the linked report. | **Local:** 11/11 bit-exact roundtrips, 36/36 finite expected-count resamples, 30 unittest checks and byte-identical regeneration in that task. 16→8 kHz gives 800 frames, 16→48 kHz 4800, 16→44.1 kHz 4410. **Reported:** no upstream quality/latency result. This offline tooling is never SDK runtime timing. |
| Typed frame / resample / drift model — `typed-frame-resample-and-drift-diagnostics` / `SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS` | Three full 48 kHz stereo s16 frames (480 interleaved samples each) plus a partial 45-sample frame; explicit 48 kHz/2ch/s16 → 16 kHz/1ch/f32 selection; one monotonic clock domain (62,500 ns per 16 kHz sample), 10,000 ppm bound. Controls: D=173 source-coordinate impulse delay, gapless intervals `[0,147)`, `[147,307)`, `[307,467)`, `[467,495)`, 13/13 adverse controls including missing selection, drift and tail overrun. | None: stdlib Python model, no weights, audio or download. | **Local:** 495 accepted = 495 delivered valid samples; 800 produced = 495 valid + 173 startup + 132 tail non-content; one drain call; 24 unittest checks in that task. **Reported:** proposal `audio-sdk/typed-frame-resample-drift/0.1` only. No native compile, installed consumer, paced workload or device result. Delay is an integer source-coordinate probe, not acoustic or phase/group delay. |
| Identity PCM/noop baseline — `identity-pcm-and-noop-fixtures` / `SDK-IDENTITY-PCM-AND-NOOP-FIXTURES` | 357 caller-owned exact `k/128` f32 values in 160/160/37 frames, first input sample `2**53+1`, installed fixed v0 D=0. Controls: eight malformed/lifecycle probes, rejected unregistered/missing selections, installed conformance with 35 pass / 0 fail / 2 skip; `registry.busy` and `buffered.flow` remain **skipped**. | Synthetic f32 literals and a task-local C fixture provider; no audio or model. | **Local:** 11/11 native CTest, 1/1 installed consumer test, 7/7 Python fixture checks and canonical report digests in that task. **Reported:** fixed v0 contract behavior only; no built-in identity provider is added and a skip is not a pass. No pacing, deadline, device or quality result. |
| Playback-speed comparator matrix — `speex-resampler` / `SDK-SPEEX-RESAMPLER` (with `libsamplerate`, `libsoxr`) | One matrix row; no frozen corpus, command, revision, digest or local control. | None staged locally for these three leads. | **Reported only:** varispeed fallback verdict and “Very low” latency/effort label. **Local:** no execution, score, conversion-cost measurement or delay measurement. Not a pitch-preserving stretch result and not an SDK-boundary result. |

Comparison inputs, controls, assets and outcomes are also recorded field-by-field
in `report.json`. No speech corpus, human rating, device run, listening test or
public benchmark result is pooled with these synthetic/model/reported layers.

## Bounded feasibility: SDK-ENG-01-SPEEXDSP-RESAMPLER-FEASIBILITY

**Proposed, unassigned, not a board entry, not implemented.** Parent:
`SDK-SURVEY-ENG-01`; consult `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`,
`speex-resampler`, `speexdsp-ns-reference`,
`numpy-scipy-soundfile-wav-and-resampling` and
`typed-frame-resample-and-drift-diagnostics` before any dispatch. No component
currently owns an executable, pinned S42/SpeexDSP bandlimited-resampler
comparison at a named SDK boundary.

- **Smallest reproducible check (not run):** pin the existing vendored
  `resample.c` digest and declared upstream revision; use authored finite f32
  literals only; compare explicit integer rate pairs 48→16 kHz and 16→48 kHz
  with an identity 16→16 kHz control; record exact output frame counts,
  nonfinite failures, source-coordinate delay and malformed-rate rejections.
- **Separation controls:** keep the offline SciPy polyphase output as a distinct
  control, never as a SpeexDSP score; retain missing/invalid rows; do not refit
  intervals or treat padding as content; resampling is not bandwidth extension.
- **Deliverable:** task-local replay and metadata report with frozen inputs,
  digests, reason codes and deterministic rerun equality. Read-only samples; no
  model, speech media, scorer rerun, provider registration, public ABI, default,
  build or CI change.
- **Stop condition:** feasibility only. Any later quality, device, listening,
  public-benchmark or release claim needs a separate scoped decision and frozen
  evidence.

## Release boundary

Keep source-present, local synthetic, installed control and source-reported
evidence separate. Freeze format/rate/channel, source interval, explicit
conversion selection, candidate revision/digest, conversion cost/content delay,
adverse cases and denominators before any future comparison. No missing or
unrun control promotes a candidate. The fixed v0 format and registry defaults
are unchanged; no provider enablement, routing default, public header, ABI,
CMake, package or CI change follows from this map. Historical installed
conformance and offline tooling times are not device availability, callback
scheduling, paced workload or mobile qualification. Scoped document review does
not authorize audio use, playback, redistribution, listening, publication or a
release decision; code, source notices, installed packages, rights and any
future recordings remain distinct. Official cohort/metric and submission
decisions remain with audio-bench; `SDK-FND-AUDIT` and `SDK-FND-EVIDENCE` rules
are in `docs/provider-intake.md`, `docs/evidence-handoff.md` and
`RELEASING.md` at the survey base above.

## Reproduction and checks

The evidence map is generated from pinned documents and metadata by
`build_report.py`. `report.json` is canonical JSON (sorted keys, two-space
indent, terminal newline); `report.json.sha256` is its SHA-256 sidecar.
`SOURCES.sha256` pins every consulted document/metadata byte and every other
generated or source file in this directory (it does not list its own bytes).
`report.json.license`,
`report.json.sha256.license` and `SOURCES.sha256.license` are the SPDX sidecars.

From this directory, with pinned Python 3.12.16 and no bytecode writes:

```sh
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12
PYTHONDONTWRITEBYTECODE=1 "$PY" build_report.py
PYTHONDONTWRITEBYTECODE=1 "$PY" -m unittest -v test_survey_map.py
PYTHONDONTWRITEBYTECODE=1 "$PY" verify.py
```

`build_report.py` regenerates byte-identical outputs. Canonical bytes carry the
board row's claim worktree literal, not the checkout path, so a fresh clone at
any location regenerates the same digest. Workspace lookup for the external
pinned documents tries `AUDIOML_WORKSPACE_ROOT`, then enclosing-directory
markers, then the pinned `audioml` default; that lookup never enters canonical
bytes. `verify.py` is read-only and checks scope, Python pin, pins, board
projection, canonical bytes, report
digest, manifest, SPDX sidecars, family/component coverage, S42 mapping,
historical-record fields, gap bounds, claim gates and text hygiene. From the
enclosing workspace, also run:

```sh
python3 audio-benchmark-platform/plan/swarm/check.py --task SDK-SURVEY-ENG-01
(cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SURVEY-ENG-01 && python3 -m reuse lint)
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SURVEY-ENG-01 diff --check
```

`scripts/ci.py` is unchanged by this documentation-only task. A regression run
with the pinned interpreter and `--output` in a private temp directory passed:
52 repository unit tests, 1 API CTest, 11 native CTest, 14 external-provider
CTest, one fixture-registration CTest in each of two build modes, 5
installed-wheel Python tests, and the packaging/gate probes. This is a
regression check, not ENG-01 evidence: it exercises no bandlimited resampler and
says nothing about device, listening or release status. All source/evidence pins
are listed with digests in
`SOURCES.sha256` and `report.json.source_pins`. A pin identifies the inspected
bytes only; it grants no rights and verifies no audio, model or device.

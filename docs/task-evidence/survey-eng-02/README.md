# SDK-SURVEY-ENG-02 · Clock drift, alignment and reference synchronization

Status: survey only. This is a deterministic, read-only evidence map for the
catalogued `ENG-02` / `F16` family. It matches the original method families,
named source leads and historical executions to existing SDK components. It
does not execute audio, open a device, add an asset, enable a provider, or
change the public ABI, defaults, build or CI. No public benchmark claim is made.

## Scope

The only writable area used by this task is
`docs/task-evidence/survey-eng-02/`. The board row, handoff and reviewer state
are untouched. The feasibility follow-up described below is a proposed,
unassigned, not-run note inside this map; it is not a board task.

Base: `c9296ae96a2b58efae559bd22e7760122c886df8`
Branch: `swarm/SDK-SURVEY-ENG-02`

## Evidence pins and provenance

[`SOURCES.sha256`](SOURCES.sha256) records SHA-256 digests for all document and
metadata pins in workspace-relative form. SDK files are pinned through the
canonical `audio-benchmark-platform/audio-sdk` checkout and are compared
byte-for-byte with this worktree by the builder and verifier. Every quoted
phrase used below must still appear in its pinned source; the builder fails if
a quote or inventory field drifts.

The pins include the registry, taxonomy table, legacy backlog, board row,
verification profiles, inventory, historical AEC and real-corpus reports,
clock-domain implementation record, composition report, SDK contracts,
evidence-handoff rules and the two proposal-only clock fixtures. A digest is a
content pin only: it grants no rights and attests to no media, device or
provider outcome.

## Original catalogue and source leads

`research/category_registry.json` records `ENG-02` as scope `support`,
discovery `catalogued`, candidate census `not_started` and benchmark
`not_started`. Its input/output boundary is
`Audio/timestamps → aligned streams/reference`, and it states that
synchronization belongs to the composition contract and affects AEC and
spatial comparisons. The companion table in `audio_categories.md` and the
legacy `research/task_backlog.json` entry agree.

- **S27 — WebRTC audio processing interface.** URL access is direct but the
  registry does not pin an upstream revision. Mapped to `webrtc-apm`,
  `webrtc-aec3` and `webrtc-apm-ns`. Historical executions are offline AEC
  pilots measuring fixed content alignment, not live sample-clock tracking.
- **S41 — WebRTC NetEq documentation.** URL access is direct. Mapped to
  `webrtc-neteq`, `opus-1-4-standard-decoder-plc` and
  `buffer-occupancy-controller`. No local NetEq trace replay or time-scale run
  appears in the reviewed pins. Receive-side playout timing remains at the
  `SDK-SURVEY-ENG-03` boundary.

## Method-family map

### Delay estimation

Mapped components: `webrtc-aec3`,
`aec-challenge-paired-render-capture-fixtures` and `pesq-polqa-and-3quest`.

Comparison inputs are paired 16 kHz mono far-end render and microphone capture,
the AEC Challenge train-only synthetic and recorded groups, and offline paired
scoring with independently measured content lag. Controls require a declared
layout and rate, rejection of misaligned inputs rather than silent trimming,
and fixed known offsets that are reported separately. Assets are historical
local audio/manifests and installed bindings or weights from those pilots; none
is added here.

Local historical outcomes: AEC3 showed `125–128` samples (about 8 ms) of
content alignment on clean near-only trials, and the real pilot removed a known
8 ms offset before scoring. A stream-delay-hint pilot (`0`, `20`, `40` ms) did
not motivate changing the 0 ms default without recordings that contain known
capture/playback buffer delay. Reported-only outcomes are limited to the named
S27 lead. These records explicitly do not measure capture-clock drift.

### Rate adjustment

Mapped components: `typed-frame-resample-and-drift-diagnostics`,
`duplex-clocks`, `speex-resampler`, `buffer-occupancy-controller` and
`webrtc-neteq`.

Comparison inputs are exact integer source sample indices, declared source
rates and an explicit target rate, plus declared integer ppm drift and
half-open sample intervals. Controls require explicit selection of rate,
channel and format, unique in-domain timestamps, rejection of gaps, overlaps,
duplicate/stale stamps, missing roles, nonfinite input and out-of-bound drift,
and bounded drain with concealment kept separate from content. The only local
assets are the two task-local proposal fixtures.

Local historical model outcomes: the typed-frame proposal reports content
delay `D=173` samples from a source-coordinate impulse with absolute drift
bounded at `10000 ppm`; the duplex-clocks proposal maps `+6250 ppm` capture
drift and rejects discontinuities, while stating that it supplies no live
clock-drift evidence. Both are developer-tool models outside the fixed v0
interface. S41 and the buffer-occupancy control law are reported-only leads;
no local time-scale experiment is claimed.

### Drift compensation

Mapped components: `coreaudio-audiounit-duplex-host`,
`native-capture-recipe-and-render-timeline`,
`typed-frame-resample-and-drift-diagnostics` and `duplex-clocks`.

Comparison inputs are the historical `CLOCK_MONOTONIC_RAW` and CoreAudio Mach
absolute host timestamps, simulated callback frames, and declared sample maps.
Controls include setup-time offset bracketing with carried uncertainty, abort
on failed calibration, simulated `160`/`320`-sample frame splits, and explicit
missing-reference and mismatch reasons. No physical audio device was opened.

Local historical outcomes: the clock-domain audit calibrated a Mach-to-raw
offset but does not refresh it after suspend or restart and does not qualify
discontinuity during a run. A simulated AudioUnit self-test covered frame
splitting, not a hardware callback. The composition report states that delay
contracts are implementation-specific and that matched AEC results lack live
clock-drift and target-device evidence.

### Machine-learning audit

The catalogued ML family is audited: "Learned estimation is optional research,
not required". `cagcrn-joint-aec-and-ns` is a citation/compatibility lead and
`aecmos` is a learned scenario metric applied after known offsets are removed;
neither owns a learned delay or clock-drift estimator here. Missing evidence:
no pinned ML revision or runnable drift checkpoint, no matched render/capture
cohort or drift-labeled target with an independent holdout, and no uncertainty
result. Background papers are citations, not local executions.

## Release boundary and prohibited claims

Historical local, reported-only, proposal-only and not-run outcomes remain
distinct. None is promoted to qualification. No quality, listening, device,
callback, availability, throughput or release result is claimed from this map.
No audio, model, scorer output or licensed asset is added, replayed or
redistributed. No public SDK ABI, descriptor, provider default, engine routing,
build or CI setting is changed. Rights, participant consent and platform clock
evidence remain with the original component owners and release policy.

## Feasibility follow-up for the ownerless gap

Gap id: `SDK-SURVEY-ENG-02-LIVE-CLOCK-DRIFT-FEASIBILITY`. No component owns a
bounded, asset-free replay of declared sample-clock drift plus reference gap or
discontinuity on paired render/capture coordinates. The smallest check would use
authored integer sample-coordinate sequences only: 16 kHz mono maps, one
declared `+6250 ppm` capture drift, one missing segment and one contiguous
control. Expected behaviour is exact impulse mapping under drift, a reason code
and no interpolated value for missing rows, an exact contiguous control, and a
byte-identical rerun.

The deliverable would be task-local replay metadata with frozen fixture digest,
exact intervals and reason codes. Exclusions cover real audio, models, devices,
callbacks, ABI, descriptors, provider enablement, build, CI and all quality or
release claims. Status is `proposed_unassigned_not_run`; owner is absent; there
is no board entry. A later implementation or target-device measurement needs a
separate owner, exact clock-domain policy and task-local qualification under
`SDK-FND-ANALYSIS`.

## Canonical artifacts

- [`report.json`](report.json): canonical UTF-8 JSON, sorted keys, compact
  separators, one trailing newline.
- [`report.json.sha256`](report.json.sha256): SHA-256 of `report.json`.
- [`SOURCES.sha256`](SOURCES.sha256): SHA-256 of every pinned source.
- [`build.py`](build.py): read-only source loader and deterministic builder.
- [`verify.py`](verify.py): strict verifier for scope, pins, report, sidecars,
  family coverage, gap boundary and prohibited claims.
- [`test_evidence_map.py`](test_evidence_map.py): deterministic unit tests.

Report SHA-256: `5b927755513a046cd19ec1855c08b90d9407eb5f8666a028c4ae7c2019883b45`.

## Reproduction

Use pinned Python 3.12.16 at
`/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12` from the worktree
root with `PYTHONDONTWRITEBYTECODE=1`.

    PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 docs/task-evidence/survey-eng-02/build.py
    PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 docs/task-evidence/survey-eng-02/verify.py
    PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 docs/task-evidence/survey-eng-02/test_evidence_map.py -v
    PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output build/ci
    reuse lint
    git diff --check

The builder writes only `report.json`, `report.json.sha256` and
`SOURCES.sha256`. Rerunning it must reproduce the same digest and sidecars.

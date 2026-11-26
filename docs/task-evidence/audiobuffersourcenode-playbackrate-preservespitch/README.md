<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-AUDIOBUFFERSOURCENODE-PLAYBACKRATE-PRESERVESPITCH — DEFER blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`AudioBufferSourceNode.playbackRate` + `preservesPitch`
(`component_id=audiobuffersourcenode-playbackrate-preservespitch`). The
structured inventory assigns the **Rate** acceptance profile
(`verification_profile: rate`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Machine-readable decision: **`DEFER`**;
`status=incomplete`; `proposal_only=true`;
`qualification.status=not_qualified`; `qualifies=false`. No result qualifies.

This package does **not** launch a browser, import a Web Audio implementation,
copy a browser engine, load a runtime, read or play audio, listen, measure a
device, time a callback, run a benchmark or make a release claim. It pins the
provenance that is present, proves that the exact licensed Web Audio
implementation/runtime, its own terms, a pinned browser host and a
rights-cleared playback cohort are absent, reproduces only declared
`playbackRate` duration/pitch arithmetic and deterministic synthetic controls,
and records the exact deferral condition. Only
`docs/task-evidence/audiobuffersourcenode-playbackrate-preservespitch/` is
written; no provider, descriptor, registry, default, installed-v0, ABI,
shared-build, CI, board or handoff file changes.

## Exact blocker

The pinned candidate note records the API only as a **browser-platform**
capability:

> `AudioBufferSourceNode.playbackRate` + `preservesPitch` — Browser platform —
> Yes — Quality and pitch-preservation algorithm are browser-dependent.

(`cpp-library/pipeline-validation/playback-speed-candidates.md:81`; the note
also links MDN property pages at line 320.) That is a research statement, not
an implementation, a version, a licence, a geometry contract or a result. No
browser engine source, Web Audio implementation, `preservesPitch` algorithm
revision, build digest, host profile, automation/lockfile, reference output or
rights-cleared cohort exists in the project workspace. None is fabricated or
downloaded here.

| Required artifact | Recorded local state |
| --- | --- |
| Browser engine build and runtime | No pinned engine name/version/build SHA-256 or host profile; no `data/checkouts/chromium`, `data/runtimes/chromium`, `third_party/webaudio`, `src/webaudio` or equivalent |
| Web Audio implementation source | No `AudioBufferSourceNode` source, `preservesPitch` implementation revision or tree digest |
| Engine/algorithm licence and notice | No licence text, notice bundle, redistribution or output-use decision |
| Browser automation / offline-render host | No Playwright, Puppeteer, Selenium or WebDriver package manifest, lockfile, offline install or render configuration |
| Official property and geometry contract | Only the API name and the browser-dependent note; no pinned specification text, detune interaction, frame/channel handling or final-partial contract |
| Measured browser playback trace | No `playbackRate`/`preservesPitch` run, source/output mapping, duration error, pitch or transient result |
| Rights-cleared playback cohort | No consented speech/music/silence set, metadata or output-use terms |
| Approved scorer and labels | No pitch/transient scorer, preservation labels or human verification |
| Listening and device timing | No panel, protocol, result, target device or timing harness |
| Adapter intake and release review | No opt-in adapter, intake review, benchmark or release decision |

A browser launch, engine import, runtime load and playback call were **not**
attempted. Presence of the research note is not admission, reproducibility or
qualification evidence. Every release gate remains `blocked`.

## Scope and invariants

- Work is confined to `docs/task-evidence/audiobuffersourcenode-playbackrate-preservespitch/`.
  Shared CMake, contracts, public headers, descriptor registry, defaults,
  installed v0 behavior and other tasks are untouched.
- Installed v0 stays 16 kHz / mono / float32 / 160-sample frames. No provider is
  registered, exposed or default-enabled. No adapter code, readiness file or
  registry entry is added.
- The reference is deterministic, model-free and standard-library only. It is
  default OFF, unregistered and not a provider.
- No real speech/music corpus, listening panel, browser engine, Web Audio
  runtime, network download, target-device timing, pitch measurement,
  benchmark or release qualification is used. Every signal is analytic or
  seeded integer noise.
- Missing, invalid, nonfinite, out-of-range, stale, unapproved and
  missing-artifact cases fail closed. No missing result may qualify anything.
- The browser-dependent statement, synthetic arithmetic and the declared
  boundary are reported separately and are never pooled.

## Declared property arithmetic (proposal only, not a browser result)

`reference.py` -> `map_playback()` reproduces only the declared mapping
arithmetic, with exact rational values and no audio processing:

- `output_duration = source_duration / playbackRate`.
- `pitch_ratio = 1` when `preservesPitch` is `true`; `pitch_ratio =
  playbackRate` when it is `false` (varispeed).
- Rate is bounded to `1/8 .. 8` for the synthetic control only; that bound is a
  control guard, not a claimed API range.
- A rate-change schedule is contiguous, source-timestamped and exact-rational.
- The final partial window is computed from the source sample count, not wall
  time or playback position.

This is **`synthetic_contract_control_not_evidence`**. It is not the browser
algorithm, a resampler, a TSM implementation or a measured waveform.

| Control | Source samples | Rate | Preserve pitch | Output duration | Pitch ratio | Identity |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| `identity_1x_preserve` | 16000 | 1 | true | 16000 | 1 | yes |
| `identity_final_partial_preserve` | 16165 | 1 | true | 16165 | 1 | yes |
| `faster_3_2_preserve` | 16000 | 3/2 | true | 32000/3 | 1 | no |
| `slower_3_4_preserve` | 16000 | 3/4 | true | 64000/3 | 1 | no |
| `varispeed_5_4_unpreserved` | 16000 | 5/4 | false | 12800 | 5/4 | no |
| `rate_change_schedule` | 16000 | 1→3/2→3/4 | true | 52000/3 | 1 | no |

The final-partial case uses a 1600-sample control block: 16165 samples leave a
165-sample final window. These are arithmetic identities, not a browser
render, duration measurement or pitch measurement.

## Synthetic frame and local rejection controls

`reference._synthetic_frame()` creates 160 deterministic float samples from a
31-bit LCG, integer amplitudes and exact `/32768` scaling. It is seeded noise,
not speech and not a corpus. `reference.validate_frame()` checks exact length,
numeric type, finiteness, `|x| <= 1` and a stable float32 digest.

Twelve adverse vectors are rejected with exact codes: NaN, positive infinity,
negative infinity, boolean, string, `None`, 159 samples, 161 samples, empty,
out-of-range `8.5`, nested list and a non-list. Every rejection records
`state_unchanged=true` and `qualifies=false`. Nonfinite input is never counted
as silence or as a pass.

## Caller qualification manifest (shape and rejection only)

`reference.validate_manifest()` validates a strict 9-field browser
qualification manifest:

`{schema_id, run_id, browser, algorithm_source, runtime, audio, mapping,
controls, rights}`

It checks exact key sets; browser name/version/build SHA-256, host OS and
architecture; engine/algorithm revision and licence hashes; automation
version, headless/offline/deterministic flags and sample rate; fixture digest,
channels, frame size and total samples; exact `playbackRate` duration and pitch
ratio mapping; six control kinds; and six rights flags. A caller-supplied
manifest is admitted only as a **synthetic schema control**
(`synthetic_schema_control_not_evidence`, `admitted=true`,
`qualifies=false`). It is never a measured result.

`report.json` -> `admission` records one accepted shape-only control and
**56 explicit rejections**, including missing/extra fields, wrong schema,
malformed revisions and digests, unknown browser/automation/licence, unpinned
browser, non-headless/non-offline/non-deterministic runtime, float sample
rates, invalid audio geometry, noninteger and mismatched duration, wrong pitch
ratio, duplicate controls, unpassed controls and false rights. Every case is
`qualifies=false`.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json` -> `rate_profile`; every item is `qualifies=false`.

| Required item | Status here | Evidence |
| --- | --- | --- |
| 1× control | blocked | No measured 1× browser playback. |
| Source/output mapping and rate changes | blocked | Synthetic exact-rational arithmetic only. |
| Duration identity and error | blocked | No measured browser output duration. |
| Pitch | blocked | No rendered waveform, pitch tracker or algorithm result. |
| Transient audibility | blocked | No waveform, transient analysis or listening. |
| Playback buffering, rebuffer and drift | blocked | No browser audio clock, fill/flush or drift run. |
| Unfamiliar speech, music and silence | blocked | No rights-cleared stratified cohort. |
| Final partial window and speech preservation | blocked | Synthetic final-window arithmetic only; no real render or score. |

Pause/filler decisions are tied to source sample timestamps in the synthetic
control, never to wall time or playback position. That is a structural check,
not measured speech preservation.

## Eight blocked release gates

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` browser engine build identity | blocked | Exact browser name/version/build SHA-256, host OS/architecture, launch flags and immutable acquisition record. |
| `RG-02` Web Audio implementation source and licence | blocked | Exact engine/algorithm revision, tree digest, `preservesPitch` implementation identity and complete licence/notice bundle. |
| `RG-03` pinned automation and offline-render host | blocked | Pinned driver version, lockfile, offline install/load proof, render flags and recorded host profile. |
| `RG-04` official property and geometry contract | blocked | Pinned specification reference for `playbackRate`/`preservesPitch`, detune interaction, source/output mapping, channel handling and final partial window. |
| `RG-05` rights-cleared playback cohort | blocked | Immutable consented speech/music/silence cohort with output-use terms and matched controls. |
| `RG-06` rate acceptance profile | blocked | Measured 1×/rate-change/duration/pitch/transient/buffering/rebuffer/drift/final-partial results on the pinned browser host. |
| `RG-07` speech preservation and independent scoring | blocked | Approved preservation labels or scorer, stratified speech results and blind listening. |
| `RG-08` device timing, opt-in intake and release | blocked | Target-device timing/power/resources, separate opt-in adapter intake with OFF default, benchmark review and release approval. |

Each gate is `blocked` with `evidence=null` and `qualifies=false` in
`contract.json` and `report.json`. No synthetic control opens a gate.

## Exact missing artifacts and rights

| Missing artifact | Rights requirement |
| --- | --- |
| Pinned browser engine build and runtime | Engine-specific licence and redistribution terms, build provenance, host profile and written approval to execute |
| Web Audio implementation source and `preservesPitch` algorithm | Exact source revision, tree digest, algorithm licence/notice and derivative-use terms |
| Browser automation and offline-render host | Driver/runtime licences, lockfile, offline install proof and render-host approval |
| Official property and geometry contract | Pinned specification text admitted under the reviewed terms |
| Rights-cleared speech/music/silence cohort | Corpus, participant, device, consent and redistribution rights |
| Approved pitch/transient scorer and labels | Scorer/reference terms, human verification and exact-revision approval |
| Blind listening and target-device timing | Panel, protocol, device and timing-harness approval |
| Opt-in adapter intake and release review | Reviewer, benchmark authority and release-authority approval |

No download, fabrication or substitution was attempted. The research note is
provenance only.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, arithmetic, gates, pins, commands. |
| `contract.json` | Machine-readable contract: profile, pins, artifacts, blockers, gates, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, presence/licence probes, property arithmetic, frame and manifest validators, canonical report. |
| `report.json` | Canonical machine-readable Rate DEFER report; strict JSON, sorted keys, LF, no floats. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, its digest and `SOURCES.sha256`, repeated three times. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no browser, no audio). |
| `verify.py` | Read-only verifier: profile, pins, report bytes/digest, gates, controls, licensing, write scope, three cold starts. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From this directory with Python 3.12 and stdlib only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` reports `repeat=3 byte_identical=true`; all unittest checks
pass with 0 failed and 0 skipped; `verify.py` prints `PASS ... cold_starts=3/3
byte_identical=true profile=Rate status=incomplete decision=DEFER`; REUSE
reports no missing or bad licence; `git diff --check` is clean. `verify.py`
writes only to a temporary directory and never to this package.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; `boundary:` and
`sibling:` paths are relative to this SDK worktree. `SOURCES.sha256` pins these
plus every task-local artifact and excludes its own bytes. The mutable shared
board is **not** pinned; only the stable row projection `{id, title,
repository, mode, depends_on, component, evidence}` is read and gated. The full
mutable `plan/swarm/TASKS.json` bytes are never hashed.

| Input group | Count | Use |
| --- | ---: | --- |
| Plan inventory, verification profile and SDK plan | 3 | Profile and boundary |
| Candidate note | 1 | Browser-platform provenance only |
| SDK boundary files | 7 | Unchanged public/build/CI surface |
| Merged sibling evidence | 8 | Separate prior local artifacts; not pooled |

Key digests:

| Input | SHA-256 |
| --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `boundary:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `boundary:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `boundary:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sibling:docs/task-evidence/granular-tsm/report.json` | `3aefe97a4d6f7ba28ca5ab7111e0e3b83f623afd382bc50ece0f36868e881138` |
| `sibling:docs/task-evidence/phase-vocoder-baseline/report.json` | `555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7` |
| `sibling:docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json` | `57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2` |

## Separation from sibling evidence

`SDK-GRANULAR-TSM` and `SDK-PHASE-VOCODER-BASELINE` are merged rate/TSM
synthetic references; they do not implement the browser API.
`SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE` is a merged Rate DEFER boundary, not
browser playback evidence. `SDK-BUFFER-OCCUPANCY-CONTROLLER` is a merged
buffering controller with no browser engine evidence.
`SDK-APPLE-AND-BROWSER-RUNTIME-QUALIFICATION` explicitly blocks its browser /
AudioWorklet lane, so it is not evidence here either. `SDK-LIBSAMPLERATE` is a
varispeed/resampling reference whose pitch changes with rate.
`SDK-D1-WHOLE-CLIP-DURATION-PLANNER` is a synthetic duration planner. None is
pooled, imported, reused or reinterpreted. In particular, no sibling result is
treated as a `preservesPitch` or Web Audio measurement.

## Non-claims and boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`browser_engine_copied=false`, `browser_launched=false`,
`runtime_imported=false`, `asset_bundled=false`, `weights_vendored=false`,
`audio_read=false`, `audio_played=false`, `pitch_measured=false`,
`listening_conducted=false`, `device_timing_measured=false`,
`benchmark_run=false`, `release_claim=false`.

Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row identity only
(`tasks[id=SDK-AUDIOBUFFERSOURCENODE-PLAYBACKRATE-PRESERVESPITCH]`); the mutable
full `plan/swarm/TASKS.json` is never read into, hashed by or pinned to this
package. No provider, descriptor, registry, installed default, public ABI,
shared build or CI is changed.

## Reopen condition

Supply (a) the exact browser engine build and runtime with immutable version,
full SHA-256, host OS/architecture, launch flags and an acquisition/
redistribution record; (b) the Web Audio `AudioBufferSourceNode`
implementation source at an exact revision, the `preservesPitch` algorithm
identity and the complete engine/algorithm licence and notice bundle; (c) a
pinned browser automation and offline-render host with driver version, lockfile,
offline install/load proof and render flags; (d) the official
`playbackRate`/`preservesPitch` property and geometry contract, including detune
interaction, channel handling and final partial window; (e) a rights-cleared
consented speech/music/silence cohort with output-use terms; (f) an approved
pitch/transient scorer or human labels; (g) measured Rate-profile results,
blind listening and target-device timing; and (h) a separate opt-in adapter
intake with OFF default and exact-head review. Until then this task stays
**DEFER**, **incomplete** and **not qualified**.

## License

All files here are first-party `Apache-2.0`, copyright 2026 Tsakanyan Hovhannes.
Python and Markdown files carry file-level SPDX tags; JSON and digest files are
covered by adjacent `.license` sidecars and the repository `REUSE.toml`
annotation for `docs/**`.

## Expected report digest

`report.json` SHA-256 is recorded in [`report.json.sha256`](report.json.sha256)
and printed by `verify.py`. It is regenerated only by `run.py all`; edit the
README text and regenerate rather than hand-editing the digest.

<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WEBRTC-AEC3-PLUS-APM-NS-LEVELS-1-3 — DEFER blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`webrtc-aec3-plus-apm-ns-levels-1-3` (`component_id=webrtc-aec3-plus-apm-ns-
levels-1-3`). The structured inventory assigns the **Room** acceptance profile
(`verification_profile: room`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Machine-readable decision: **`DEFER`**;
`status=proposal_only_not_qualified`; `completeness=incomplete`;
`qualification.status=not_qualified`; `qualifies=false`. No result qualifies.

This package does **not** import, load, link, execute, copy or download WebRTC
AEC3, WebRTC APM, `pywebrtc-audio`, a wheel, a binary, weights, real room
recordings or a corpus. It does not listen, measure a device, time a callback,
run a benchmark or make a release claim. It pins the research and adapter
provenance that is present, proves that the licensed runtime and the
rights-cleared room cohort are absent, records exactly **one configured synthetic
APM instance and every toggle**, and runs the three APM noise-suppression levels
**independently** on one frozen synthetic duplex fixture. Only
`docs/task-evidence/webrtc-aec3-plus-apm-ns-levels-1-3/` is written; no provider,
descriptor, registry, default, installed-v0, ABI, shared-build, CI, board or
handoff file changes.

## Exact scope and boundary

- Installed v0 stays 16 kHz mono `float32`, 160 samples per frame. There is no C
  boundary, public header, provider registration, descriptor, default,
  `CMakeLists.txt`, CI or installed-behavior change.
- `reference.py` is a stdlib-only deterministic teaching reference, not WebRTC:
  an AEC3-shaped shadow/primary adaptive filter with residual gain, followed by
  a decision-directed spectral suppressor whose strength is selected by one
  frozen level. Every constant and operation is defined locally.
- The three level runs start from fresh state and differ **only** in
  `noise_suppression.level` (1, 2, 3). All other toggles are frozen and recorded.
- The duplex fixture is synthetic: deterministic sines plus seeded integer
  noise, a frozen two-path echo geometry, path change, reference dropout,
  delayed reference and epoch reset. It is not a room, a device or a corpus.
- ERLE, near-SNR and near-energy change are frozen-window **synthetic proxies**.
  They are not WebRTC ERLE, AECMOS, STOI/ESTOI, SI-SDR, listening or accepted
  quality.
- The mutable full `plan/swarm/TASKS.json` is never hashed. Only the stable
  linked-row projection (`id`, title, repository, mode, component, dependencies,
  evidence, base commit, branch) is compared.

## Exact external blocker: absent licensed runtime and room evidence

The research source record is present and pinned, but none of the artifacts
needed to reproduce the candidate are:

1. **No licensed runtime.** The adapter documents `pywebrtc-audio==0.2.0`
   (Apache-2.0) and a local `data/envs/webrtc` environment. That environment is
   absent; `pywebrtc_audio`, `webrtc_audio` and `webrtc_apm` are not importable;
   no WebRTC AEC3/APM checkout, wheel, binary or source revision is staged. No
   download or substitute was attempted.
2. **No exact instance/configuration reference.** The adapter records the
   intended shape (AEC enabled, NS enabled, AGC disabled, levels 1–3) but not a
   pinned upstream revision with its full toggle and stream-delay reference.
3. **No rights-cleared room cohort.** The historical AEC-Challenge pilots are
   training-split subsets with unresolved source-component, participant and
   redistribution terms. They are not bundled, remapped or used as an oracle.
4. **No measured device evidence.** There is no live render/capture loop,
   loudspeaker, delay, clock-drift, buffering or deadline measurement.
5. **No independent no-reference comparison.** The no-reference case here is a
   passthrough control only; it is not an independent suppressor.
6. **No listening, AECMOS, benchmark or release result.** Historical AECMOS
   values are quoted context only and are not reproduced.

**Reopen condition.** A caller supplies the exact immutable WebRTC AEC3+APM
source or wheel with LICENSE/NOTICE and execution approval; a frozen single
instance configuration with every toggle and the three NS levels at that
revision; a rights-cleared paired room cohort with timestamps, device and RIR
metadata; paired echo/near-end/double-talk/path-change measurements; target
device delay, drift and deadline runs; an independent no-reference comparison;
authorized listening; and a separate OFF-by-default provider intake with
independent exact-head review. Until then every release gate stays `blocked`.

## One configured APM instance and all toggles

`report.json` → `configured_apm_instance` records one frozen template. The
three runs instantiate it with only `noise_suppression.level` changed:

| Toggle | Configured value |
| --- | --- |
| `echo_canceller` | enabled; synthetic shadow/primary; 48 taps; stream-delay hint 0 ms; extended filter off |
| `noise_suppression` | enabled; fixed level 1/2/3; oversubtraction 1.2/1.6/2.0; gain floor 0.55/0.40/0.25 |
| `high_pass_filter` | disabled |
| `gain_controller` | disabled |
| `voice_activity_detection` | disabled |
| `residual_echo_detector` | enabled; synthetic hysteresis; enter 0.35; exit 0.70; hangover 2 frames |
| `transient_suppression` | disabled |
| `pre_amplifier` | disabled; fixed gain 1.0 |
| `post_amplifier` | disabled; fixed gain 1.0 |
| `experimental_agc2` | disabled |

The level runs are independent: fresh processor state, same frozen fixture,
same control windows, and a distinct output digest for each level. The
`config_sha256` values in the report pin each level's canonical configuration.

## Synthetic level results (not a ranking, not evidence)

Frozen duplex fixture, 120 frames / 19,200 samples, 16 kHz mono:

| Level | ERLE late dB | Near-SNR late dB | Near energy change dB | Overlap near-SNR dB | Peak |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 8.767 | 6.555 | −4.197 | 0.086 | 0.606148 |
| 2 | 9.461 | 5.216 | −5.668 | 0.064 | 0.557550 |
| 3 | 10.212 | 3.976 | −7.412 | 0.042 | 0.508952 |

Matched controls on the same frozen fixture:

| Control | ERLE late dB | Near-SNR late dB | Peak | Status |
| --- | ---: | ---: | ---: | --- |
| identity | 0.000 | 16.416 | 0.578654 | bit-exact identity |
| fixed attenuation ×0.5 | 6.021 | 5.926 | 0.289327 | fixed control |
| AEC only (NS off) | 6.963 | 10.028 | 0.751942 | AEC-only control |
| no reference | 0.000 | 16.416 | 0.578654 | blocked passthrough |
| delayed reference | 13.237 | 6.468 | 0.337346 | misaligned |
| reference dropout | 8.976 | 6.520 | 0.593728 | partial |
| near-only | 4.990 | 7.346 | 0.176411 | synthetic |
| echo-only | 35.859 | −200.0 sentinel | 0.337346 | synthetic |

The trend is only the local synthetic knob: higher levels raise the frozen
echo-attenuation proxy and reduce near-end preservation. It is **not** a WebRTC
NS ranking and must not be used to choose a level. `ranking.order` is
`not_ranked` and `recommendation` is `null`. Every level's near-SNR and near-
energy deficit relative to AEC-only is retained in `adverse_results`; no adverse
or missing result is hidden or promoted.

## Room profile application

| Room requirement | Status here | Evidence |
| --- | --- | --- |
| Frozen render/reference or measured RIR | synthetic fixture only | Two frozen synthetic echo paths; no measured RIR. |
| Channel/rate/hop | synthetic fixture only | 16 kHz mono, 160-sample hop. |
| Excitation, delay, movement, noise, reset | synthetic fixture only | Seeded sines/noise, 24-sample delayed reference, path change at frame 80, reset at frame 60. |
| Echo-only | synthetic only | Early and late echo-only windows. |
| Near-end-only | synthetic only | Early and late near-only windows. |
| Overlap / double-talk | synthetic only | Two overlap windows. |
| No reference | blocked | Passthrough control only; no independent suppressor. |
| Delayed / missing render | synthetic only | Misaligned and partial statuses; never qualifying. |
| Echo attenuation | synthetic proxy only | Frozen-window ERLE proxy. |
| Near-end damage | synthetic proxy only | Near-SNR and near-energy change. |
| Nonfinite failures | synthetic control only | Invalid/nonfinite rejections and one safety reset. |
| Alignments | synthetic fixture only | Fixture lag proxy, not device timing. |
| Authorized listening | blocked | No panel or MOS assessment. |
| Target-device timing | blocked | No loop, drift or deadline run. |

## Eight blocked release gates

1. Pinned, hash-verified licensed WebRTC AEC3+APM runtime with LICENSE/NOTICE
   and execution approval.
2. One documented APM instance at that revision with every toggle and NS levels
   1–3.
3. Rights-cleared paired render/capture or measured-RIR room cohort with exact
   timing and device metadata.
4. Paired echo attenuation, near-end damage, double-talk, nonlinear echo and
   path-change evaluation for every level.
5. Target-device loop delay, clock drift, buffering, memory and deadline budget.
6. Independent no-reference comparison plus real-runtime missing, delayed,
   dropout and nonfinite controls.
7. Authorized listening or an approved quality assessment.
8. Provider/catalog/license intake, descriptor/public-surface review and
   explicit release approval.

All eight are `blocked` with `evidence: null` and `qualifies: false`.

## Exact missing artifacts and rights

| Missing artifact | Rights requirement |
| --- | --- |
| Pinned WebRTC AEC3+APM source revision or `pywebrtc-audio==0.2.0` wheel/source with SHA-256 | Apache-2.0 LICENSE and NOTICE for the exact revision/binding, redistribution terms, and approval to execute. |
| Exact APM instance/toggle reference at that revision | Public API and configuration documentation for the exact revision. |
| Rights-cleared room cohort (paired render/capture or measured RIR) | Written corpus and participant rights for evaluation and derived outputs. |
| Room/device harness with loop, drift and deadline measurement | Harness license and target-device access approval. |
| Listening/quality and provider release review | Panel, reviewer and release approval. |

No download, fabrication or substitution was attempted.

## Source pins (SHA-256)

Paths are relative to the `audioml` workspace; boundary and sibling paths are
relative to this SDK worktree. `SOURCES.sha256` pins all local artifacts and
excludes itself. The mutable board is **not** pinned; only the stable linked row
gates verification.

| Input group | Count | Use |
| --- | ---: | --- |
| Research, adapter and pilot report provenance | 15 | Documented context and declared runtime/toggle shape |
| Public boundary (`CONTRACTS.md`, both v0 headers) | 3 | Unchanged public surface |
| Merged sibling WebRTC evidence (`webrtc-aec3`, `webrtc-apm-ns`, `webrtc-vad`, `webrtc-apm`) | 8 | Prior task-local evidence, unchanged |

Key digests:

| Input | SHA-256 |
| --- | --- |
| `research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` |
| `adapters/webrtc-aec/README.md` | `c074f84c859dcfb2ac7414a775dbcddcf2f2646deca66810c9241fcf7adec050` |
| `adapters/webrtc-ns/README.md` | `8893bace6b0289135f6d1ccad949a9eba44a824e37f45765f30b4192f82c5992` |
| `adapters/webrtc-ns/adapter.json` | `42aac7a2a0f5709e24785eb87d5922fdd30cabadd54336604ff739dc70fa874a` |
| `reports/webrtc_aec3_ns1_synthetic_pilot_20261028.csv` | `73ed6f1735683566f3929b031b2c2233349840733cafd3544a08a2d0e921adcc` |
| `reports/webrtc_aec3_ns2_synthetic_pilot_20261028.csv` | `c1c1669958d0f57a4db6a3ea3b175ab73b3ebac249cffe7eb4c47da82b89d77c` |
| `reports/webrtc_aec3_ns3_synthetic_pilot_20261028.csv` | `4bbaafcaa6f5564bd7b3f7c150d32774819fa1ec9673f083688c3201df8d6115` |

## Reproduction

Run from this directory on the pinned worktree:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 run.py --sources
python3 run.py --inspect
python3 verify.py
```

`run.py --report` builds the report three times and writes only byte-identical
output; `--sources` prints the exact local manifest; `--inspect` prints a
canonical configured-instance summary. `verify.py` separately launches three
cold starts for each command, checks the exact external/boundary/sibling/local
pins, the stable linked row, canonical bytes, the single instance and all
toggles, the three independent levels, eight blocked gates, adverse/missing/
invalid/nonfinite controls, SPDX annotations, dependency hygiene and task-local
scope containment. JSON is canonical (`sort_keys=True`, compact separators,
`allow_nan=False`) with one trailing newline.

Report digest: see [`report.json.sha256`](report.json.sha256), the canonical
SHA-256 of the byte-identical [`report.json`](report.json). No self-referential
digest is repeated in this README.

## Failure controls and non-claims

- No WebRTC AEC3/APM algorithm, source, wheel, binary or runtime is implemented
  or emulated.
- No real speech, room recording, corpus, weight, model, device timing,
  listening panel or release evidence is present.
- Rejections are explicit: nonfinite/out-of-range/bool microphone, short frame,
  nonfinite/short reference, stale epoch, wrong/negative position, invalid
  configuration and invalid NS level. An invalid call leaves state unchanged;
  a forced nonfinite filter state triggers a finite safety reset.
- Missing, delayed/dropout, no-reference and adverse synthetic results are
  retained with `qualifies: false`; none is promoted.
- Historical AEC-Challenge figures and AECMOS values are source statements only,
  marked `reproduced_here: false`; none is used as a threshold.

## License

All files here are first-party `Apache-2.0`, copyright 2026 Tsakanyan Hovhannes.
Python and Markdown files carry file-level SPDX tags; JSON and digest files are
covered by adjacent `.license` sidecars and the repository `REUSE.toml`
annotation for `docs/**`.

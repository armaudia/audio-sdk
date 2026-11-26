<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-LIVEKIT-TURN-DETECTION — readiness and caller-asset contract

**Status: `proposal_only_incomplete`; qualification `not_qualified`; decision
`DEFER` before any opt-in adapter exposure.**
This package is a deterministic, standard-library-only feasibility record for
LiveKit turn detection. It is **not** a LiveKit runtime, not a package install,
not a weight download, not remote inference, not an SDK provider, not a
registered descriptor and not an accuracy, benchmark, latency or release
qualification. Installed v0 remains 16 kHz mono `float32`, 160 samples.

Pinned base: `b02dbf12499038abc4f9b6b1c06cdecc76a79dcd`. Branch:
`swarm/SDK-LIVEKIT-TURN-DETECTION`. All files live only under
`docs/task-evidence/livekit-turn-detection/`.

## Readiness conclusion

The candidate is **not runnable in this package**. The exact external blocker
is a missing, unpinned and licence-unreviewed model asset plus a missing
runtime and turn-labelled cohort:

- The **v1 multimodal model** is served only on LiveKit Inference. It requires
  network access, a LiveKit Cloud project and `LIVEKIT_API_KEY` /
  `LIVEKIT_API_SECRET`; no public weights, offline runtime or exact revision
  exist for it.
- The **v1-mini multimodal model** is delivered inside `livekit-agents` and
  runs locally on CPU, but obtaining it requires a package install and a
  runtime weight download. Its exact bytes, SHA-256, input geometry and
  preprocessing are not published as values.
- The deprecated **text multilingual model** is an open-weights
  Qwen2.5-0.5B-Instruct derivative (396 MB, ~50–160 ms per turn), requires
  STT transcripts and `livekit-plugins-turn-detector`, and is slated for
  removal in Agents 2.0.
- The text model and v1-mini use the **LiveKit Model License**, not
  Apache-2.0. The licence text and output-use terms were not observed or
  reviewed here.
- No rights-qualified conversational corpus with utterance and turn
  boundaries, mid-turn pauses and explicit unknown regions is staged.
- `docs/acceptance-matrix.md` records S09 (LiveKit host) as **Blocked /
  excluded**: no pinned/tested LiveKit host package pair exists.

No weight, package, model, audio, corpus, recording, listening session,
device measurement, network call or benchmark was produced. `DEFER` remains
in force until every release gate is closed.

## Exact scope and boundary

- Write scope: `docs/task-evidence/livekit-turn-detection/` only. No provider,
  default, ABI, `CONTRACTS.md`, descriptor registry, shared `CMakeLists.txt`,
  CI, board, handoff or other worktree change is included.
- The package emits **endpoint decisions separately from framewise VAD**.
  Activity events and endpoint events have different event types, streams,
  sequences and digests.
- The local control is `synthetic_endpoint_policy_control_not_model_output`.
  It replays a frozen 700-frame synthetic timeline (112,000 samples, 160-sample
  frames, 10 ms) with four turns, mid-turn pauses, quiet speech, idle noise,
  VAD false positives, one maximum-wait fallback and a 40-frame unknown tail.
- The synthetic completion trace is an **uncalibrated control**, not a LiveKit
  posterior, not an accuracy result and not a service claim.
- All detections are advisory: they never gate audio, never alter PCM and are
  never promoted by a missing, rejected, stale or unrun result.

## Model and asset record

| Variant | Kind | Local | Exact asset | Observed SHA-256 |
| --- | --- | --- | --- | --- |
| `v1` | multimodal remote | No | LiveKit Inference only | Absent |
| `v1-mini` | multimodal local CPU | Yes | Runtime-delivered weights | Absent |
| `text-multilingual` | text transcript | Yes | `livekit/turn-detector` (claimed open weights) | Absent |

The package records `asset_sha256: null`, `asset_digest_observed: false`,
`exact_revision: null`, `revision_pin_available: false` and
`license_text_observed: false` for every variant. It does not fabricate a
revision, digest, memory value, latency or threshold.

Documented endpoint defaults are recorded as source-reported only:
`0.3` / `2.5` s with the multimodal detector, `0.5` / `3.0` s otherwise, and a
prediction timeout of about `1.0` s. They are **not measured here**.

## Task geometry

The public SDK v0 geometry is 16 kHz mono `float32`, 160 samples per 10 ms
frame. The LiveKit model geometry is **unestablished**:

- the text model consumes transcript tokens and conversation context, not
  audio frames;
- the v1-mini audio sample rate, hop, front-end features and preprocessing are
  not published as exact values;
- no model latency, startup, memory or availability value is measured.

The only measured geometry is the synthetic control's own 160-sample timeline.

## Caller-supplied asset contract

`caller_asset_contract` in `contract.json` and `report.json` requires a
caller-supplied, non-vendored asset with:

- an exact SHA-256 and positive byte count;
- `LiveKit-Model-License` acknowledgement and no redistribution permission;
- a pinned runtime package/version and Python `3.12.16`;
- 16 kHz mono `float32`, 160-sample frames;
- a declared context mode (`agent-message+audio`, `audio` or `transcript`);
- a per-mille threshold in `1..999` and `max_delay > min_delay`.

Absent, malformed, mislicensed, vendored, redistributable, wrong-geometry or
wrong-variant manifests are rejected before processing. Eighteen adverse
admission cases are exercised and all are rejected; one positive fixture is
accepted to prove the validator is not vacuous. Eight fixed absence probes
cover model, runtime, rights and cohort paths; all are absent.

## Analysis profile application

`plan/swarm/VERIFICATION.md` Analysis row is applied item by item in
`report.json` → `analysis_profile`. No item is satisfied for qualification and
every item has `qualification_effect: none`:

| Required item | Synthetic control evidence |
| --- | --- |
| Timestamped probabilities | 660 scored frames; exact control Brier `3/200` |
| Event boundaries | 4 turns with exact true end-of-turn samples |
| Detections | 4 endpoint decisions per policy |
| Quiet and active speech | `active-speech` and `quiet-speech` strata |
| Idle noise | `idle-noise` stratum with 2 VAD false positives |
| Known positives/negatives | TP 14,400, FN 3,200, FP 3,200, TN 84,800 samples |
| Onset/offset delay | Signed cutoff and end-of-turn delay in samples and ms |
| Stratified FN/FP | Per-stratum speech, nonspeech and unknown counts |
| Validity separate from nonspeech | 6,400 unknown samples excluded; no relabel |
| Independent state | 4 fresh epochs; nonzero reset and isolation checks |
| Exact source intervals | 160-sample half-open partition of `[0, 112000)` |
| Availability | Explicit monotonic clock and fixed availability formulas |
| Dropped/stale events | Duplicate, stale, wrong-clock and nonfinite rejections |
| Cross-hop | `[120,420)` → `40 + 160 + 100 = 300` samples |
| Endpoint separate from VAD | Distinct activity and endpoint event streams |
| Maximum-wait fallback | One forced commit with a −8,000-sample cutoff |

## Synthetic results (control only, not candidate accuracy)

Framewise VAD control: speech miss rate `2/11`, false-alarm rate `2/55`.
Unknown time contributes to no denominator.

| Policy | Decision frames | Signed delays (samples) | Cutoffs | Worst cutoff | Max-wait |
| --- | --- | --- | ---: | ---: | ---: |
| VAD-only silence timer | 69, 189, 319, 369 | −1600, −3200, +8000, −43200 | 3 | −43200 | 0 |
| Gated endpoint policy | 80, 239, 319, 589 | +160, +4800, +8000, −8000 | 1 | −8000 | 1 |

The gated control reduces synthetic cutoffs from three to one and improves the
worst cutoff by 35,200 samples, but the remaining cutoff is caused by the
maximum-wait fallback after a deliberately wrong continuation trace. This is
**not** evidence that LiveKit is accurate; it shows only that endpoint policy
and framewise VAD are separate and measurable.

## Exact external blockers

| ID | Blocker | Reopen condition |
| --- | --- | --- |
| `BLK-01` | No offline weight/asset with an observed SHA-256; install and download required | Digest-pinned caller asset hashing to the declared value |
| `BLK-02` | Full v1 is remote inference only; cloud credentials and network required | Authorized locked inference run, or v1 excluded |
| `BLK-03` | LiveKit Model License text and output-use terms unreviewed | Exact licence text and written rights decision |
| `BLK-04` | No rights-qualified turn-labelled cohort or matched evidence | Frozen speaker/session-disjoint labelled cohort |
| `BLK-05` | Model input geometry and preprocessing unpublished | Exact input contract and preprocessing reproduced |
| `BLK-06` | S09 host pair blocked; Python 3.12.16 compatibility unverified | Reproducible isolated host/runtime pair |
| `BLK-07` | Per-language calibrated thresholds not published as values | Published or reproduced calibration values |
| `BLK-08` | Independent review, hosted CI and release approval absent | Recorded exact-head review, CI and release approval |

All eight release gates `RG-01`…`RG-08` are blocked. `DEFER` is in force until
every gate is closed.

## Reproduction

Python 3.12.16, standard library only. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py
python3.12 -m json.tool report.json > /dev/null
shasum -a 256 report.json report.json.sha256
```

`verify.py` re-checks every source and boundary pin, the strict JSON key sets,
the canonical report and sidecar, the README digest tables, three cold-start
regenerations, SPDX annotations and the merge-base branch scope. It fails
closed with `scope_base_unavailable` when no base ref exists and with
`base_out_of_scope_change:<path>` for any branch-diff path outside this task.

## Source pins (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.
The mutable full `plan/swarm/TASKS.json` is never hashed; only the stable task
row identity gates the report.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/audio-sdk/docs/acceptance-matrix.md` | `2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e` |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` |
| `source:research/category_survey/sources.md` | `9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:docs/acceptance-matrix.md` | `2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Local artifact digests

Every local artifact is pinned by `SOURCES.sha256` and this table.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `33f8f7f3203672217a354e5c785b9f486337528ea70ab036ea988a096be229a2` | 1961 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `955d654b648b63f5ba87b7dfee920542d622802d7662d3be7f30eb544f6dcfbd` | 21929 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `37cd09dc92d8b01fc51bb285705af63e5ba7a081bf5a3b2258ad848d89fe2948` | 76814 |
| `report.json` | `e6f94b97ac407437feb80d35e98c78ac8dd2b3a0ab5673b31536410ae37cc719` | 34406 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `72b4fc320f3a8097c6a012b335b65fd1c7aa892b4a187ef4cc8f5887a025ad73` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `9f0a0bce8f5b42a1f6529decc7f9873ea9ccb9226b5ed58cdceb031d243c0498` | 6204 |
| `test_reference.py` | `30865c192591b11402a60e6ecf3d53ad2c6ad6b49ead4e2b62fa7aac275918b7` | 26765 |
| `verify.py` | `f0083dd1489dd118cd82ff28ef5b76c4921bab5987bb294fb1a49e9275af2420` | 33889 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Non-claims and remaining gates

No LiveKit weight, package, runtime, remote call, real speech, corpus,
recording, listening, device timing, power, memory, latency, benchmark,
parity or release qualification is claimed. S09 remains blocked. No public
surface, installed behavior, board or cross-task change exists; no gate was
weakened. Remaining gates before any opt-in adapter exposure: a digest-pinned
caller asset and licence decision, a reproducible host/runtime pair, exact
input geometry and calibration, a rights-cleared turn-labelled cohort with
unknown regions, matched controls, independent exact-head review, hosted CI
and release approval.

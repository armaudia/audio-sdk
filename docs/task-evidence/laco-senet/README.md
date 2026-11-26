<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-LACO-SENET - LaCo-SENet readiness blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for `laco-senet`
(title "LaCo-SENet", mode `feasibility`, `verification_profile: enhancement`).
It is **not** a LaCo-SENet implementation. No upstream source checkout,
checkpoint, weight byte, Hydra configuration, runtime, corpus, recording,
enhanced waveform, listening result, device timing, benchmark or release claim
is present. **No result here qualifies LaCo-SENet.**

Pinned base: `f006454da9a72fbfd394e2b5bd05105201a9cd29`.
Branch: `swarm/SDK-LACO-SENET`. Owner: `agent-LACO-SENET`.
Reviewer: `reviewer-LACO-SENET`.

## Exact external blocker

The census records one row:

> **LaCo-SENet** | Configurable-lookahead streaming enhancement | Official
> source and VoiceBank+DEMAND checkpoints include nine latency settings and
> three seeds; paper reports causal 12.5 ms PESQ 3.35, increasing with
> lookahead. | High priority for latency/quality curve; compare only within
> this checkpoint's domain and test configuration, then check DNS
> generalization.

`research/noise_suppression_candidate_census.md`, line 22. The candidate
matrix row adds:

> Official MIT model release pins a 5.71 MB 12.5 ms causal checkpoint, but no
> local files/runtime/adapter exist and the author code repository exposes no
> license; no local score.

The readiness audit (`research/voice-enhancement-20261101/agent-laco-readiness/
REPORT.md`) records the pinned model revision, one checkpoint identity, nine
latency settings and three seeds. It also states plainly that the GitHub source
root exposes no `LICENSE` entry, that no source/checkpoint/runtime/adapter is
staged, and that no inference ran.

The exact blocker is therefore the combination of:

1. **Source code terms are unresolved.** The author source repository shows no
   license entry, so no reviewed source license text, notice or per-file
   identity exists. A model-card MIT label does not prove the code license.
2. **No caller-supplied local asset set exists.** Even though one checkpoint
   identity is recorded, no source snapshot, checkpoint byte, Hydra
   config/overrides file, runtime lock, rights record or cohort is present.
3. **No streaming state contract is frozen.** The evidence records nine
   latency settings from 12.5 ms to 200 ms and three seeds, but no chunk,
   frame, hop, STFT, exact per-setting lookahead, reset schedule, tail policy
   or pacing contract.
4. **No rights-cleared 16 kHz matched cohort and no result exist.** No paired
   DNS run, clean-speech diagnostic, preservation, peak, invalid-output,
   alignment, state, memory or timing record was produced.

Missing artifacts are not downloaded, reconstructed, mirrored, substituted or
inferred from adjacent FastEnhancer, DeepFilterNet3, DTLN, GTCRN, ConvFSENet or
other survey evidence.

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The official `yskim3271/LaCo-SENet` source at an immutable 40-hex commit with reviewed license text, notice, per-file SHA-256 and a map from streaming wrapper, model and Hydra configuration to source files. The repository currently exposes no license entry. |
| `BLK-02` | The exact selected checkpoint, Hydra config and overrides with local byte counts, SHA-256 values and checkpoint-specific terms. The recorded M1 12.5 ms identity is not locally present or verified. |
| `BLK-03` | A locked offline runtime with exact interpreter, framework and package versions, wheel hashes, device, determinism settings and a recorded supported platform. Upstream states macOS is untested. |
| `BLK-04` | Reviewed source, checkpoint and training-data terms; corpus and clean-reference permission; output use, redistribution and attribution. |
| `BLK-05` | The frozen streaming state contract: mode, rate, channels, chunk, frame, hop, STFT, exact lookahead per latency setting, reset at utterance boundaries, tail trimming and pacing. |
| `BLK-06` | A rights-cleared 16 kHz mono cohort with paired clean references where permitted, quiet/active and idle-noise strata, onset/offset cases, held-out splits, controls, baseline, paired SI-SDR/STOI, preservation, peaks, invalid outputs, alignment, timing and memory. |

**Reopen condition.** A caller supplies the exact source and its reviewed
license, the exact checkpoint/config/overrides with verified identity and
checkpoint-specific terms, an isolated hash-pinned runtime on a recorded
platform, the frozen streaming state contract, a rights-cleared 16 kHz matched
cohort, a deterministic reproduced Enhancement result set with separate
quality and timing evidence, and an opt-in OFF-by-default provider intake with
independent exact-head review. Until then this task stays `DEFER`.

## Recorded upstream identity (source-reported, not locally verified)

The merged evidence records the following. None of it is a local asset: no
byte is present, opened, hashed or executed here, so the digest, byte count and
revision are labelled recorded-only and cannot qualify the candidate.

| Property | Recorded value | Local status |
| --- | --- | --- |
| Source repository | `https://github.com/yskim3271/LaCo-SENet` | absent; no license entry |
| Model repository | `https://huggingface.co/yskim3271/lacosenet-voicebank-demand` | absent |
| Model revision | `022c7f9190449619be9815629dd905671c193815` | recorded, not locally verified |
| Checkpoint variant | `M1_12.5ms/s2039` | recorded |
| Checkpoint file | `M1_12.5ms/s2039/model_279000.th` | absent |
| Checkpoint bytes | `5707759` | recorded, not locally verified |
| Checkpoint SHA-256 | `4fc07683a0b346630f51c68046cca1a8e547ae816f961aeac57b34ba6696f6a2` | recorded, not locally verified |
| Hydra config | `M1_12.5ms/s2039/.hydra/config.yaml` | absent |
| Hydra overrides | `M1_12.5ms/s2039/.hydra/overrides.yaml` | absent |
| Manifest | `manifest.json` at the pinned revision | absent |
| Model-card license | MIT | recorded, not locally verified |
| Checkpoint-specific terms | not separated from the model-card label | unresolved |
| Latency settings | 9, range 12.5 ms to 200 ms | count and range only |
| Seeds | 3 | reported |
| Checkpoints in release | 27 | reported |
| Parameter count | 1.37 M (paper/census) | reported |
| Reported test metrics (M1 12.5 ms) | PESQ 3.3286; STOI 0.9522; CSIG 4.60; CBAK 3.70; COVL 4.03 | source-reported, not measured here |

These values are retained only to make the future exact-asset check
unambiguous. They are **not** local measurements and must not be compared with
the project DNS2020 results.

## Task geometry

| Property | Reported value | Verified here |
| --- | --- | --- |
| Task | Single-channel speech enhancement / noise suppression | No execution |
| Domain | VoiceBank+DEMAND, 16 kHz | no local cohort |
| Channels | 1 | no local audio |
| Mode | Streaming causal with configurable lookahead | no state contract |
| Latency settings | 9 (12.5 ms to 200 ms), 3 seeds | count/range only; not enumerated |
| Checkpoint count | 27 | reported |
| Chunk / frame / hop / STFT | not recorded | unverified |
| Exact lookahead per setting | not recorded | unverified |
| State reset / tail / pacing | not recorded | unverified |
| SDK v0 installed geometry | 16 kHz, mono, f32, 160 samples/frame | preserved; no LaCo mapping |

The public v0 mono path is rate- and channel-compatible with the reported
domain, but no descriptor, provider, registry, default, ABI, shared build or CI
mapping is added. Rate and channel compatibility is not an adapter.

## What this package verifies

1. **Absence evidence.** 24 fixed workspace, SDK-worktree and home-cache probes
   are checked without a recursive walk. All are absent. The report builder and
   verifier fail if any later appears, so a stale absence claim cannot ship.
2. **Recorded-identity discipline.** The one checkpoint digest and byte count
   are recorded from pinned evidence, marked `locally_verified=false`,
   `admitted_as_result=false` and `qualifies=false`. The seven required
   artifacts keep `sha256`, `revision` and `bytes` null; no local identity is
   invented.
3. **Asset-register absence.** The pinned asset register is parsed strictly:
   20 candidate ids, none for LaCo-SENet. No checkpoint identity is inferred
   from it.
4. **Stable pins and digests.** Every source and boundary input is pinned by
   SHA-256; the README digest tables are validated against live bytes, and
   `SOURCES.sha256` covers all task-local files except itself.
5. **Stable board identity.** Only `id`, `title`, `component`, `mode`,
   `repository` and `depends_on` are projected and gated. The mutable
   `plan/swarm/TASKS.json` bytes are never hashed; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes.
6. **Fail-closed caller-asset validation.** A task-local manifest schema
   requires exact source, checkpoint, config/overrides, runtime, 16 kHz mono
   streaming geometry, input, control and rights fields. Unknown or missing
   fields, duplicate JSON keys, nonfinite values, floats, unsafe paths, an
   unresolved or `NOASSERTION` source license, wrong interpreter, stereo or
   non-16 kHz geometry, offline scope, missing state reset, rate mismatch,
   unconsented input, false controls and false rights are rejected. One
   synthetic schema control is accepted to prove the validator is not
   blanket-rejecting; it is marked `synthetic_schema_control`,
   `qualifies=false` and is not evidence.
7. **Enhancement profile accounting.** Every Enhancement requirement is
   recorded as blocked or documented; no missing result is promoted.
8. **Scope enforcement.** The verifier resolves the newest merge-base against
   `origin/main` and `main`, fails closed with `scope_base_unavailable` when no
   base exists, and reports any branch-added path outside
   `docs/task-evidence/laco-senet/` as `base_out_of_scope_change`. Regression
   tests cover sibling merges, an out-of-scope branch edit and a missing base
   ref.

## Enhancement profile application

| Requirement | Status | Evidence |
| --- | --- | --- |
| Identity/noisy control and task-matched baseline | blocked | No control or baseline output on exact assets. |
| Paired SI-SDR and STOI where permitted clean references exist | blocked | No rights-cleared 16 kHz paired cohort or score. |
| Clean-speech preservation, peaks and invalid outputs | blocked | No preservation, peak, clipping or nonfinite record. |
| Separately labeled predictive screen or authorized listening | blocked | No screen, listener or permission. |
| Alignment, state, memory and content/availability timing | blocked | No runtime, state, chunk timing or content-delay record. |
| Streaming geometry, chunk, frame/hop, STFT, lookahead and reset | blocked | Latency setting count only; no frozen state contract. |
| Quiet/active, idle-noise and onset/offset strata | blocked | No corpus or stratum definition. |
| Separation of paired, unpaired, synthetic, human and source-reported evidence | documented | Upstream VoiceBank metrics are labelled source-reported; no result of any class is promoted. |

## Matched-evidence boundary

`fastenhancer-small-reference`, `dtln-onnx`, `gtcrn-streaming-onnx` and
`convfsenet` are separate components with their own assets, geometry and
blockers. Their fixtures, checkpoints, scores, timings, state models and rights
records are not inherited. The 30-pair DNS2020 results for other candidates are
same-task-context comparators only; they are not LaCo-SENet measurements and
the upstream VoiceBank figures are not comparable to them.

## Reproduction

The canonical bytes were generated with CPython `3.12.16` and
`PYTHONDONTWRITEBYTECODE=1`. From this directory:

```
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py
```

`run.py` regenerates `contract.json`, `report.json`, the report sidecar, the
README digest tables and `SOURCES.sha256` three times and requires
byte-identical output. `verify.py` is read-only and writes only to a temporary
directory. Repository checks are the installed-package `python scripts/ci.py`,
`python -m reuse lint` and `git diff --check`.

## Source pins

<!-- digest-table: source -->
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md` | `5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14` |
| `source:research/voice-enhancement-20261101/agent-denoise-trials/REPORT.md` | `c00e26847c119928f068cb5da00ba88106a2d977b67bf8b325ec27093eca8f4e` |
| `source:research/voice-enhancement-20261101/agent-laco-readiness/REPORT.md` | `7bcf1a55db8e9a93a3f4d70fdb2981dff1723f2287251aa834a1ff5bd2fc90fd` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `source:research/voice-enhancement-20261101/evaluation_records.md` | `962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a` |
| `source:research/voice-enhancement-20261101/findings.md` | `78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c` |
<!-- digest-table: end -->

## Boundary pins

<!-- digest-table: boundary -->
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `30eb70d133a99ee8b9a2c6c84210e31ba06bd32222307c8d3683fbb571c30a03` | 2203 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `39d24fae576ed90fcfc1f8785f011058363f3a3c4a4bd8781ab98a644fdfed59` | 26050 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `3724c9e8f42a43d297fa0c78eea18607192c96f6a792deacad1966fd47ae8316` | 89189 |
| `report.json` | `35fb9d3c321a1d5367d66577679494105bba9c29982552dbbf4ac7b97a53d00a` | 46515 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `4b2c10c7b32eb88e6430f3ed9a62cc417a97270646a2003b8e2f643be09e5676` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `c6f1cb0fd72dcc1b0c8f0a3d41bb25e95eceef90e2da518420ed73a0606cf4f8` | 4903 |
| `test_reference.py` | `be7d38ac5c3249733dd6f584e578a9a329d22f0a0881b9b4cd84ab2f93d03c77` | 30302 |
| `verify.py` | `263531dffedf2da6ea3e310b48b728f9d2c63681f729db666f80d8e01d8b337a` | 28100 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`SOURCES.sha256` also pins `README.md`; a file cannot pin its own bytes, which
is why `SOURCES.sha256` is absent from the artifact table.

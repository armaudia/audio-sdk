<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK — task-local feasibility evidence

Task-local, proposal-only, **incomplete** and **not_qualified** feasibility
evidence for `Source/VAD conditioning for playback`
(`component_id=source-vad-conditioning-for-playback`). The assigned acceptance
profile is **Rate**. Machine-readable decision: **DEFER**;
`status=proposal_only_asset_intake_incomplete_not_qualified`;
`evidence_status=incomplete`; `qualification.status=not_qualified` (field:
`qualification_status` in `report.json`). No result in this package qualifies
the candidate.

This package does **not** import, load, link, execute, copy, vendor or download
a VAD model, ASR gate, syllable-rate estimator, stretcher, research
implementation, audio corpus or listening panel. It does not read, write,
render or play real audio; does not measure a device clock, callback deadline,
FIFO occupancy or pitch/transient audibility; does not benchmark the SDK; and
makes no release claim. Every interval is a half-open coordinate in a synthetic
16000-sample fixture at 16 kHz, mono, float32, with 160-sample source frames.

## Boundary

Installed v0 geometry is unchanged and documented only:
`16000 Hz`, 1 channel, `float32`, 160 samples per call. No provider, default,
descriptor, registry entry, ABI, CONTRACTS, shared-build or CI file is changed.
The adapter/provider remains OFF, unregistered and not exposed. No
caller-supplied asset is embedded, downloaded, parsed as source or executed;
the package only models a strict metadata/byte-hash intake shape. Board,
handoff, reviewer dispatch and release state are untouched.

## Decision, gates and blockers

All gates RG-01 through RG-08 are **blocked** and `qualifies=false`: exact
runnable source; exact assets and rights; installed-v0 boundary intake; typed
content annotations; measured unknown-span behavior; Rate-profile evidence;
playback pacing and listening; and public admission review. `DEFER` is before
`opt_in_adapter_exposure`. Exact blockers B-01 through B-04 and their
reopening conditions are in `report.json` and `contract.json`.

Source-reported claims are kept as provenance only. The pinned design note
describes a VAD + syllable-rate + silence-compression stage and a Vosk batch
gate; the streaming gate remains planned. The pre-screen used three clips, no
listener result, no calibrated block-streaming gate and no pitch/transient
score. None of those numbers is reproduced or promoted here.

## Typed annotation controls

The synthetic envelope uses typed classes `speech`, `silence` and `unknown` in
source-sample coordinates. Speech is never sped above 1x; silence is never
slowed below 1x; unknown spans are retained at rate 1 and are **not deletion**.
A 200 ms minimum dwell follows the pinned 20–50 ms frame / 200–300 ms segment
guidance. Rates are bounded to 3/4–3/2 and output boundaries must be integer
samples; duration closes at 16000 source samples to 16000 output samples. The
identity control is a bit-exact integer sequence, explicitly **not** a
VAD-conditioned result.

Unknown-span behavior is only an annotation-arithmetic counterfactual: treating
the unknown span as silence would remove 800 synthetic samples, while the
retained control keeps all 3200. This is not a measured classifier or deletion
result. Pitch, transients, unfamiliar speech, music, rebuffer, drift, final
partial-window behavior, speech preservation and buffering remain not measured.

## Caller-supplied asset contract (not satisfied)

Six external assets are required for reopening: source revision, VAD weights,
runtime lock, typed annotation schema, rights-cleared cohort manifest and
matched reference output. Each must be caller-owned, referenced by exact id,
byte count and lowercase SHA-256, with licence/consent review sidecars. The
shape-only verifier rejects duplicate keys, field-set drift, missing/empty
identifiers, bad digests, relative or traversal paths, duplicate paths,
embedded storage, absent bytes, byte-count mismatch and hash mismatch. A
hash-matched placeholder is still shape-only and never qualifies. No such
assets are present in the workspace or SDK worktree; absence is not a runtime,
rights or quality result.

## Reproduction

```text
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m reuse lint
git -C ../../../ diff --check
cd ../../..
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output "${TMPDIR:-/tmp}/source-vad-conditioning-ci"
```

`verify.py` is read-only and fails closed on duplicate-key/nonfinite JSON,
stale pins, stale canonical artifacts, stale README digest tables, unexpected
files, license gaps, whitespace damage, unavailable scope base, branch-diff
changes outside this task prefix (`base_out_of_scope_change:<path>`) and a dirty
diff check. The strict scope gate resolves the newest merge-base of HEAD with
`origin/main` or `main`; if neither ref exists it emits `scope_base_unavailable`.
Three scope regression tests cover newest-base preference, `main` fallback and
out-of-scope/missing-base fail-closed behavior.

Canonical artifacts are `report.json`, `report.json.sha256`, `contract.json`
and `SOURCES.sha256`. The board link pins only stable row identity, never the
mutable full `plan/swarm/TASKS.json`.

Base commit: `022a7ad3cedf35aba70ef93b32b71ae51e1e30ca`.
Task ID: `SDK-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK`.

<!-- digest-table: source -->
| Pin key | SHA-256 |
| --- | --- |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `source:adapters/silero-vad/adapter.json` | `45222fd98fe1bd76550d0529cdaa442783807a727880b168d7879eca4f54a60a` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:cpp-library/pipeline-validation/playback-speed/README.md` | `a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f` |
| `source:cpp-library/pipeline-validation/playback-speed/results/report.md` | `9c9383297b1160dbe4f7261f789b493d70354b11930f4d8527b20b0ca8c87c34` |
| `source:cpp-library/pipeline-validation/playback-speed/results/results.json` | `69b5bcc4dc3740bacc182e93419b6a83d5c3eebba7d9b4dfdd8fe4b09813cfc1` |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
| `source:research/voice-enhancement-20261101/agent-vad-chain-followup/REPORT.md` | `4e1de799b62ab7fee1a0def421ed9d152d1ccdb0c966141e9bc09ddb5e6e10b2` |
<!-- digest-table: end -->

<!-- digest-table: boundary -->
| Pin key | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `docs/task-evidence/aix-speed-asr-guided-planner/README.md` | `4a5748b4e8d4c723b5ef2ce606c270c2d14b07beb9930b062520190cf0d8b28c` |
| `docs/task-evidence/aix-speed-asr-guided-planner/report.json` | `a71ce94ad0b701c9d302edf1c74338c7d1586d573a7295510fd3584b26110873` |
| `docs/task-evidence/silero-vad-pause-duration-rules/README.md` | `b6e422c591364dffa8b6ab0d3c9c78a579a6c85c88f831d86ee8c9d27593ab1f` |
| `docs/task-evidence/silero-vad-pause-duration-rules/report.json` | `9aebd32c6dc61cf4c5d3d5e0b38fd82a2f083792a453bf9db9548e52cfa5b22d` |
| `docs/task-evidence/vosk-small-en-us-0-15-playback-gate/README.md` | `1ccece1085e1d6e821891feffb0c19fc494227bfd5e8a656657ffd7081cf959c` |
| `schemas/descriptor.schema.json` | `9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba` |
| `schemas/effective-config.schema.json` | `55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

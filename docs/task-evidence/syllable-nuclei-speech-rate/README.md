<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SYLLABLE-NUCLEI-SPEECH-RATE — task-local feasibility evidence

Task-local, proposal-only, **incomplete** and **not_qualified** feasibility
evidence for `Syllable-nuclei speech rate`
(`component_id=syllable-nuclei-speech-rate`). The assigned acceptance profile
is **Rate**. Machine-readable decision: **DEFER**;
`status=proposal_only_blocked_incomplete_not_qualified`;
`evidence_status=incomplete`; `qualification.status=not_qualified`. No result
in this package qualifies the candidate.

This package does **not** download, copy, import, load, execute, or vendor any
Praat script, syllable-nuclei reimplementation, detector, ASR, runtime, corpus,
or audio asset. It does not read, write, render, or play real audio; does not
measure a device clock, callback deadline, FIFO occupancy, pitch, transient
audibility, or listener preference; does not benchmark the SDK; and makes no
release claim.

## Candidate boundary

The pinned playback-speed candidate note records syllable nuclei as the
de Jong & Wempe 2009 method, with two constraints: the method needs tuning per
language, and the original Praat script is GPL. The matrix recommends
reimplementing the peak-picking method rather than copying the GPL script.
This package records those constraints as source-reported provenance only; it
does not reproduce the method or promote a quality/timing claim.

Installed v0 geometry remains documented only: `16000 Hz`, 1 channel, `float32`,
160 samples per call. No provider, descriptor, registry entry, default, ABI,
CONTRACTS, shared-build, or CI file is changed.

## Decision, gates, blockers

All gates RG-01 through RG-08 are **blocked** and `qualifies=false`: exact
runnable permissive source/runtime, rights/license review, typed per-language
tuning/config contract, exact source-timestamp mapping, matched rate evidence,
failure/control evidence, target-runtime timing, and OFF-by-default opt-in
intake. `DEFER` is before `opt_in_adapter_exposure`.

Exact blockers B-01..B-04 and reopening conditions are in `report.json` and
`contract.json`. Missing evidence never qualifies the candidate.

## Synthetic boundary surrogate

The deterministic stdlib-only surrogate exercises source-timestamp and
syllable-rate arithmetic on typed speech/pause intervals. It is explicitly
`surrogate=true`, `candidate_is_syllable_nuclei=false`, `qualified=false`. It is
not the de Jong & Wempe method, not Praat, not a detector, and not a rate
claim.

## Caller-supplied asset contract (not satisfied)

Any future candidate artifact must be caller-owned and validated by exact id,
absolute path, byte count, SHA-256, reviewed license/notice, and geometry.
The shape-only verifier rejects duplicate keys, field-set drift, missing/empty
identifiers, bad digests, relative/traversal paths, duplicate paths, missing
bytes, byte-count mismatch, hash mismatch, and non-permissive/GPL license ids.
A hash-matched placeholder is still shape-only and never qualifies. No such
assets are present.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SYLLABLE-NUCLEI-SPEECH-RATE diff --check
```

`verify.py` is read-only and fail-closed on duplicate-key/nonfinite JSON, stale
pins, stale canonical artifacts, stale README digest tables, unexpected files,
license gaps, SPDX-token violations, scope changes outside this task prefix, and
whitespace damage.

Board link pins only stable row identity (`component`, `depends_on`, `id`,
`mode`, `repository`, `title`), never the mutable full `plan/swarm/TASKS.json`.

Base commit: `26bc48c58f9d69571571fa651862dcbe0fe1172d`.
Task ID: `SDK-SYLLABLE-NUCLEI-SPEECH-RATE`.

<!-- digest-table: source -->
| Pin key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-bench/EVIDENCE_SPEC.md` | `f37ff1c0083f99387548b5369cdad0f55c2d31a9b75e422073b570cd80ca009c` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
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
| `schemas/descriptor.schema.json` | `9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba` |
| `schemas/effective-config.schema.json` | `55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

<!-- digest-table: artifacts -->
| Pin key | SHA-256 |
| --- | --- |
| `docs/task-evidence/syllable-nuclei-speech-rate/README.md` | `63adc9278a23defd8e08c9b2a8639969b4ff29f22b4261e0622494c8e646e7f2` |
| `docs/task-evidence/syllable-nuclei-speech-rate/SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/syllable-nuclei-speech-rate/contract.json` | `d437a8a52f4e39c395ed032c83b4391dbd5ac947a88c21dc67ed1ca839f77008` |
| `docs/task-evidence/syllable-nuclei-speech-rate/contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/syllable-nuclei-speech-rate/reference.py` | `4ad6bd179aea29b5660e02e73eb5b9142fefa08860f2cac0f66cf876ee625483` |
| `docs/task-evidence/syllable-nuclei-speech-rate/report.json` | `8206509ae41dc10d4844945b14424a7c934c007f35b9bd9b58770895dbfdf838` |
| `docs/task-evidence/syllable-nuclei-speech-rate/report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/syllable-nuclei-speech-rate/report.json.sha256` | `e8b6d4fd83559bc9bcfb429d7b41c4206a98c45bacf0abbd19977d151e5a0447` |
| `docs/task-evidence/syllable-nuclei-speech-rate/report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/syllable-nuclei-speech-rate/run.py` | `bb0f1c3e2b0990c45e8da67e133e5078ecb6b37e772e8fa817009f1d5ce76714` |
| `docs/task-evidence/syllable-nuclei-speech-rate/test_reference.py` | `a7b4f05f723770b85303093ae81fa5053a78fdc31d6acf1cb8466635f9dfe8ba` |
| `docs/task-evidence/syllable-nuclei-speech-rate/verify.py` | `7fd1acdcee5f2dab1be9043a7a290757ae90b90712e8a9aecf7eb8bf7581b81c` |
<!-- digest-table: end -->

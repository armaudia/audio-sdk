<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SOUNDTOUCH-BPMDETECT — SoundTouch BPMDetect caller-supplied-asset boundary

Task-local, proposal-only, `incomplete`, `not_qualified` feasibility and evidence
package for **SoundTouch BPMDetect** (`component_id=soundtouch-bpmdetect`). The
Rate profile is assigned in `plan/swarm/VERIFICATION.md` and `plan/INVENTORY.json`.
Base commit: `022a7ad3cedf35aba70ef93b32b71ae51e1e30ca`; branch:
`swarm/SDK-SOUNDTOUCH-BPMDETECT`. Decision: **DEFER** before
`opt_in_adapter_exposure`; no missing, blocked or synthetic result qualifies the
candidate.

## What this package does and does not do

This package models SoundTouch BPMDetect as a **metadata-only caller-supplied-
asset reference**. It pins the read-only local SoundTouch source checkout at
`f738b1132ec1fd56efc90367898244cf52d9e6a5` and the source-derived integer
geometry: installed **16 kHz**, mono, `float32`, 160-sample frames;
`TARGET_SRATE=1000` with `decimateBy=16`; `INPUT_BLOCK_SIZE=2048`;
`DECIMATED_BLOCK_SIZE=256`; autocorrelation windows `windowLen=1333` and
`windowStart=300`; accepted BPM range 45–190. It validates caller metadata,
absolute paths, byte counts and SHA-256 values and then fails closed with
`BPMDETECT_RUNTIME_IDENTITY_UNPINNED`. It never imports, builds, loads,
downloads or executes SoundTouch or any caller asset.

The header's "approx 500 Hz" decimation prose disagrees with the implementation
constant `TARGET_SRATE=1000`; the implementation value is used for all derived
geometry. The source-reported `SoundTouch 2.4.1` label also disagrees with the
checked-out `configure.ac` version `2.4.0`. Both discrepancies are recorded as
provenance blockers, not resolved by this package.

The only in-memory content is **synthetic, deterministic integer arithmetic**:
inter-onset intervals for 120 BPM and 90 BPM, exact rate mapping at 0.8×, 1× and
1.25×, 160-sample frame aggregation and a final-partial control. These controls
are **not audio, not BPMDetect output and not listening evidence**. There is no
rights-cleared BPM-labeled cohort, no matched baseline, no listening result, no
device timing, no benchmark and no release claim. Time-stretch RTF/WER and
first-output figures in the source records belong to the separate
`SDK-SOUNDTOUCH` component and are explicitly excluded from BPMDetect evidence.

Installed v0 behavior remains unchanged. No provider, adapter, default, ABI,
CONTRACTS, descriptor registry, shared build or CI behavior changes; nothing is
enabled, registered or exposed.

## Exact readiness conclusion

`DEFER` / `incomplete` / `not_qualified`. Gates `RG-01` through `RG-08` are all
`blocked` and non-qualifying. The exact external blockers are:

- **XB-01** — no licensed built SoundTouch runtime identity is pinned. The
  source checkout is pinned, but no immutable library/binary revision, byte
  count and SHA-256 exists, and the LGPL-2.1-or-later versus commercial
  decision is unreviewed.
- **XB-02** — no rights-cleared held-out music/speech with BPM labels, scorer
  or task-matched baseline is staged. Source-reported time-stretch results are
  not BPMDetect results.
- **XB-03** — the 16 kHz mono float32 160-frame boundary, 1000 Hz decimation
  and 1333/300 windows are source-derived only. No rate mapping on the exact
  runtime, final-partial execution, playback buffering or first-output timing
  has been measured.
- **XB-04** — no opt-in intake, independent exact-head review or release
  approval exists. Every adapter and provider remains OFF and unregistered.

Reopening requires an exact licensed runtime identity with notices and a
reviewed license decision; a pinned BPM-labeled held-out cohort with a scorer
and matched baseline; executed geometry and timing telemetry from the exact
caller-clocked boundary; and a separate opt-in intake passed at an exact head
with the default OFF.

## Stable board identity

Only stable row fields (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`) enter canonical bytes and gates. The full mutable
`plan/swarm/TASKS.json` is never hashed. Stable-row SHA-256:
`072abdcae7064d1f9c4dab59aa3165f962f6d0f08208202d041a8567f5c57093`.

## Source pins (SHA-256)

`source:` paths are workspace-relative. Every row is checked by `verify.py`.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/plan/swarm/handoffs/SDK-SOUNDTOUCH.md` | `40a8b52b77dc47df9badd0a82ae7776b24c117f8d80c077ac2a0a69964026dbd` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/CMakeLists.txt` | `a116ea75335f72a6db436bcc19fe980a2a38c02cd0b73c7f97fee17b5abe1aec` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/COPYING.TXT` | `84c6d82dc7de80f5b73f231edfd3ddc5b53513908117452bfa37ea36bb4b7e0a` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/configure.ac` | `fa70c079b3a6fcbdfe8365d0eba163298e82e7d7c1e75601827dd7564c3fc69b` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/include/BPMDetect.h` | `884beb69e3462b9fef718b5c898cd2c5d5627552e83262f40de30de15782f9a0` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/include/FIFOSampleBuffer.h` | `b83e8420e872372ab0a3a60f80222a52c50034f8f8767cdbf9f42fa05a0a3dc7` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/include/STTypes.h` | `ad08fd1ac1b90d9eb87ea71d0c756892750f0a42bf47e41dacd42cbd84251255` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/include/SoundTouch.h` | `b5c49c895630bfb260bc4a8efc607a30345b2de0fa95c7013bdeae243a3451ef` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/readme.md` | `b09474138b9ec26ad370c569c19fb4abbe52ccd1c5150407414655c4c07ee9d2` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp` | `bcb39d3b364e2cc6a6f9bf184ead0ecad374805f074c9dde191dcf0534beccff` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/FIFOSampleBuffer.cpp` | `1d97113ca4848923a258a20515265a6d67820e225f12d02390975b9e2deabe5b` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/PeakFinder.cpp` | `dec269fa55400d252ebe2793088ebf66bb35326468b1bd117c918b13a6959de1` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/PeakFinder.h` | `779238116f28af37a05aab295cfd7fb6600f08e540f510431636ff14fc4c1dd7` |
| `source:data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/SoundTouch.cpp` | `048cba391a501c1713addbcafc88e875ee1b0187478efa811243d991d389d712` |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

Paths are SDK-worktree-relative. All are unchanged and machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `docs/task-evidence/soundtouch/README.md` | `951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550` |
| `docs/task-evidence/soundtouch/report.json` | `83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/soundtouch-bpmdetect/caller-supplied/0.1` is metadata-only. Required
fields are `adapter`, `configuration_id`, `source_checkout`, `source_revision`,
`source_sha256`, `license_id`, `runtime_path`, `runtime_sha256`,
`runtime_byte_count`, `sample_rate_hz`, `channels`, `frame_samples`,
`sample_format`, `input_block_size`, `decimated_block_size`, `target_srate_hz`,
`xcorr_update_sequence`, `moving_average_n`, `overlap_factor`, `min_bpm`,
`max_bpm_range`, `max_bpm_valid`, `label_set_path`, `label_set_sha256`,
`label_set_byte_count` and `rights_review_id`. The validator requires the pinned
source revision and digest, the 16 kHz mono float32 160-frame geometry, the
source-derived constants, absolute asset paths, hash-matched caller files and a
rights review. It still ends in `BPMDETECT_RUNTIME_IDENTITY_UNPINNED`; no asset
is loaded or run.

## Scope gate

`verify.py` resolves the newest merge-base of `HEAD` with `origin/main`, falling
back to `main` only when `origin/main` is unavailable. If no base exists it
emits `scope_base_unavailable`. Any tracked branch difference outside
`docs/task-evidence/soundtouch-bpmdetect/` emits `base_out_of_scope_change` and
fails closed. Three regression tests cover newest-base selection, `main`
fallback and out-of-scope/missing-base rejection.

## Reproduce

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SOUNDTOUCH-BPMDETECT/docs/task-evidence/soundtouch-bpmdetect
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
cd ../..
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output build/ci
```

Canonical JSON uses sorted keys, compact separators, `allow_nan=False` and one
trailing LF. Three fresh builds are byte-identical; comparison is exact
SHA-256 with no tolerance. `report.json.sha256` is the canonical sidecar and
`SOURCES.sha256` pins source, boundary and local artifact bytes.

## Licensing

The pinned SoundTouch source text is LGPL-2.1-or-later with a commercial option.
That alone does not clear a built runtime, its distribution, any BPM label set,
rights records or product use; the license decision remains unreviewed. No
source, runtime, audio, label-set or model bytes are redistributed here. All
package files are Apache-2.0 via SPDX headers and sidecars plus the repository
`REUSE.toml` annotation for `docs/**`.

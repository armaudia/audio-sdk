<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-ROSE-CD-EARS-REVERB-CONFIGURATION — EARS-Reverb caller-supplied-asset boundary

Task-local, proposal-only, `incomplete`, `not_qualified` feasibility and evidence
package for `ROSE-CD EARS-Reverb configuration`
(`component_id=rose-cd-ears-reverb-configuration`). The room acceptance profile
is defined in `plan/swarm/VERIFICATION.md` and assigned by
`plan/INVENTORY.json`. Base commit:
`56eeb134b740d41d770940bf47bd0f035d73f097`; branch:
`swarm/SDK-ROSE-CD-EARS-REVERB-CONFIGURATION`. Decision: **DEFER** before
`opt_in_adapter_exposure`; no missing, blocked or synthetic result qualifies
the candidate.

## What this package does and does not do

This package models an **EARS-Reverb one-step** configuration as a
caller-supplied-asset reference at **16 kHz**, mono, `float32`, 160-sample
frames. It pins the source-derived 510-point / 128-hop STFT geometry and the
source checkout revision, and it validates caller metadata, byte counts and
SHA-256 values before failing closed with
`EARS_CHECKPOINT_IDENTITY_UNPINNED`. It never loads, imports, executes, builds
or downloads a model or checkpoint.

All room/reverb content is **synthetic, deterministic and in-memory**: integer
three-tone excitation, fixed synthetic taps, fixed render offset, no movement
and no noise. These controls are explicitly **not real RIR, not real audio, not
EARS-Reverb data and not listening evidence**. The oracle late gate uses a
known synthetic speech-activity pattern; it is not ROSE-CD and cannot qualify
it. There is no no-reference suppressor score, no device timing, no benchmark
and no release claim.

The linked research (`research/dereverberation_candidates_20261028.md`, line
24) reports upstream EARS-Reverb PESQ 2.69, ESTOI 0.82 and WER 15.78% for a
ROSE-CD one-step model. Those numbers are **cross-domain source-reported
evidence**, not local outputs and not evidence from the pinned
VoiceBank-DEMAND checkpoint. The 1.22 GiB VoiceBank checkpoint is absent, the
exact EARS-Reverb checkpoint identity is unidentified, and the local CPU screen
was too slow to qualify real-time use. The linked EARS material also lacks
reviewed split provenance, RIR terms and product-use rights.

## Exact readiness conclusion

`DEFER` / `incomplete` / `not_qualified`. Gates `RG-01` through `RG-08` are all
blocked and non-qualifying. The exact external blockers are:

- **XB-01** — no EARS-Reverb checkpoint path, revision, byte count or SHA-256
  is pinned; the only pinned checkpoint is the absent VoiceBank-DEMAND one.
- **XB-02** — no locked Python/PyTorch runtime, offline loader or exact
  EARS-Reverb STFT, hop, delay, frame and finalization geometry is staged.
- **XB-03** — no rights-cleared matched EARS-Reverb split, clean/reference
  pair, measured RIR, transcript or pinned scorer is present.
- **XB-04** — no real room outcome, device timing, listening, benchmark,
  opt-in intake or independent release review exists.

Reopening requires the exact checkpoint identity and locked runtime, reviewed
rights, a rights-cleared matched room cohort with pinned scorers, matched
room/quality/timing evidence, and a separate opt-in intake reviewed at an exact
head with the default OFF.

## Stable board identity

Only stable row fields (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`) enter canonical bytes and gates. The full mutable
`plan/swarm/TASKS.json` is never hashed. Stable-row SHA-256:
`b376bc56299b2d4db72c50a43f00cc71da59ee58f668c64d724af67465b4b37f`.

## Source pins (SHA-256)

`source:` paths are workspace-relative. Every row is checked by `verify.py`.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:adapters/rose-cd/README.md` | `988d1d87847910e13f65ce8e5380c3f76ed9f4be924789be6b9e80ab14719b72` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:data/checkouts/ROSE-CD/LICENSE` | `1065d138be7bfe31684e9f1c0bf8446ce7178299a7681746c50d2315f96b0ebd` |
| `source:data/checkouts/ROSE-CD/README.md` | `8ebab9ccee56cac770a3e36a4c8ade1b812a3f6b9736e093b5bf2a9596509fa3` |
| `source:data/checkouts/ROSE-CD/config.json` | `815d6cec4ea0c9492db0b477af30397b92ce577f1823faf43b82d1e7acb2c22a` |
| `source:data/checkouts/ROSE-CD/sgmse/data_module.py` | `fbe913c9fad0b68bebe29058a6943b8115d74dfa2532e7856d890cd87987eb0b` |
| `source:data/checkouts/ROSE-CD/sgmse/util/other.py` | `092efb6e7da82d11c0afa555e5b124dd950e1216237e1c165a3aea8d4551ffd0` |
| `source:data/checkouts/ROSE-CD/scripts/eval_CT.sh` | `3e422ef8f5e8610def9ab59b530f1534cdad534b92b05d1fac946d08f81c069c` |
| `source:research/dereverberation_candidates_20261028.md` | `6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468` |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `source:research/voice-enhancement-20261101/evaluation_records.md` | `962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

Paths are SDK-worktree-relative. All are unchanged and machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `docs/task-evidence/localvqe-dereverberation-probe/README.md` | `ad9706a7eddb0d73945c9944cf4cca90c6e245d13ad5d23c567f64e9a648048f` |
| `docs/task-evidence/localvqe-dereverberation-probe/report.json` | `8ce127dd2e3ac1982d0d6b7426facb2d5f4cbf26b937ae4ec5940301708ee9d8` |
| `docs/task-evidence/rose-cd-one-step/README.md` | `a8d8c9face90e0ff6827331a12ba3ea7f7ebe2186b67df10d9813457fe286629` |
| `docs/task-evidence/rose-cd-one-step/report.json` | `b27062d674d20673fb9b4b917fb323491b11965ada474246def23585ccd94e25` |
| `docs/task-evidence/rose-cd-rms-matched/README.md` | `12922d21b8d90a3d6761c04c8ca8013ec42435d5a6b7331bc31a2c2d5c1e7dd4` |
| `docs/task-evidence/rose-cd-rms-matched/report.json` | `bc40973710ccd9d5e462ce20ebc75027a93d4effe72ce8de4ce54885bf854b90` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/rose-cd-ears-reverb/caller-supplied/0.1` is metadata-only. Required
fields are `adapter`, `configuration_id`, `checkpoint_path`,
`checkpoint_sha256`, `checkpoint_byte_count`, `checkpoint_revision`,
`source_dir`, `source_revision`, `sample_rate_hz`, `channels`, `frame_samples`,
`hop_samples`, `stft_n_fft`, `sampler_type`, `steps` and `runtime_lock_digest`.
The validator requires the pinned source revision, 16 kHz mono 160-sample
format, 510/128 STFT geometry, stochastic one-step sampler, absolute paths and
hash-matched checkpoint bytes. It still ends in
`EARS_CHECKPOINT_IDENTITY_UNPINNED`; no asset is loaded or run.

## Scope gate

`verify.py` resolves the newest merge-base of `HEAD` with `origin/main`, falling
back to `main` only when `origin/main` is unavailable. If no base exists it
emits `scope_base_unavailable`. Any tracked branch difference outside
`docs/task-evidence/rose-cd-ears-reverb-configuration/` emits
`base_out_of_scope_change` and fails closed. Three regression tests cover
newest-base selection, `main` fallback and out-of-scope/missing-base rejection.

## Reproduce

All commands are read-only except for the canonical artifacts in this directory
and the temporary CI output under `build/ci`.

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-ROSE-CD-EARS-REVERB-CONFIGURATION/docs/task-evidence/rose-cd-ears-reverb-configuration
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

The pinned ROSE-CD source checkout is MIT. That alone does not clear the
checkpoint, EARS corpus terms, measured-RIR terms, derivative outputs or
product use. No source, weights, audio or RIR bytes are redistributed here.
All package files are Apache-2.0 via SPDX headers and the repository
`REUSE.toml` annotation for `docs/**`.

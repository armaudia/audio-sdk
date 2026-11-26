<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SEED-VC-V2-ACCENT-AWARE-PATH — Seed-VC V2 caller-supplied-asset boundary

Task-local, proposal-only, `incomplete`, `not_qualified` feasibility and evidence
package for `Seed-VC V2 accent-aware path`
(`component_id=seed-vc-v2-accent-aware-path`). The Voice acceptance profile is
defined in `plan/swarm/VERIFICATION.md` and assigned by `plan/INVENTORY.json`.
Base commit: `a51e49f718500ec9e81242cf2816f0b576333d00`; branch:
`swarm/SDK-SEED-VC-V2-ACCENT-AWARE-PATH`. Decision: **DEFER** before
`opt_in_adapter_exposure`; no missing, blocked or synthetic result qualifies
the candidate.

## What this package does and does not do

This package models the **Seed-VC V2 accent-style conversion path** as a
metadata-only caller-supplied-asset reference. It pins the read-only source
checkout revision and the source-derived V2 geometry: **22050 Hz**, **1024**
FFT/window, **256** hop, **80** mel bands, `center=False`, 30 diffusion steps,
AR `convert_style=true`, `anonymization_only=false`, CFG 0.7/0.7, `top_p=0.9`,
`temperature=1.0`, `repetition_penalty=1.0`, and float16 runtime dtype. It
validates caller metadata, absolute paths, byte counts and SHA-256 values, then
fails closed with `V2_CHECKPOINT_IDENTITY_UNPINNED`. It never imports, builds,
loads, downloads or executes Seed-VC V2 or any caller asset.

The only in-memory content is **synthetic, deterministic integer frame/token
geometry**: a 2 s frame count, 16 kHz content hop arithmetic, the pinned
2580-frame context window and the source n-gram=1 duration-reduction rule.
These controls are **not converted audio, not real audio and not listening
evidence**. There is no consented accent cohort, no real reference voice, no
device timing, no benchmark and no release claim.

The installed v0 format remains **16 kHz**, mono, `float32`, 160-sample frames.
The 22050 Hz V2 geometry is reference-only and is not exposed, registered or
made installable. No provider, default, ABI, CONTRACTS, registry, shared build
or CI behavior changes.

## Distinction from prior Seed-VC packages

The linked accent-conversion record explicitly states that its Seed-VC Realtime
test is **not** the "separate Seed-VC V2 accent-conversion path." Its single
240 ms block, 2.2 s left context, 0.2 s right context, 10 diffusion steps,
254.01 s model load, 22.21 s first block and 92.55× real-time figure belong to
the **v1 GUI path** and are recorded here only as excluded source-reported
evidence. The 25M file-mode result (9.648 s, first RTF 1.32, warm RTF 0.244,
ASR WER 0.00%) is likewise v1 `seed-uvit-tat-xlsr-tiny` evidence. The
`SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER` package is a separate component and
does not clear V2 accent assets. None of these qualifies this task.

## Exact readiness conclusion

`DEFER` / `incomplete` / `not_qualified`. Gates `RG-01` through `RG-08` are all
blocked and non-qualifying. The exact external blockers are:

- **XB-01** — no exact V2 accent asset identity is pinned. The source names
  `v2/cfm_small.pth`, `v2/ar_base.pth`, `bsq32/bsq32_light.pth`,
  `bsq2048/bsq2048_light.pth` and `campplus_cn_common.bin`, plus Whisper,
  HuBERT and BigVGAN snapshots, but none has a pinned revision, byte count or
  SHA-256, and no local artifact is present.
- **XB-02** — no locked Python/PyTorch/Transformers/Hydra/TorchCodec runtime or
  offline loader is staged. The source-derived 22050/1024/256/80, 30-step AR+CFM
  geometry has not been executed.
- **XB-03** — no permitted source/target reference, accent label, speaker/L1
  grouping, consent record, target-accent gold, scorer or listening protocol is
  staged.
- **XB-04** — no real V2 conversion, separated text/semantic, identity/similarity
  and naturalness outcomes, alignment, first-output/tail timing, opt-in intake
  or independent release review exists.

Reopening requires exact licensed asset identities with immutable revisions,
byte counts and SHA-256 values; the locked runtime and reproduced V2 geometry;
a rights-cleared consented accent-labeled cohort with pinned scorers; matched
Voice-profile evidence; and a separate opt-in intake reviewed at an exact head
with the default OFF.

## Stable board identity

Only stable row fields (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`) enter canonical bytes and gates. The full mutable
`plan/swarm/TASKS.json` is never hashed. Stable-row SHA-256:
`af567d24cb88f8f92783bc13e628125b19f361d0a2616ddbab69137d9b875831`.

## Source pins (SHA-256)

`source:` paths are workspace-relative. Every row is checked by `verify.py`.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/plan/swarm/handoffs/SDK-SEED-VC-25M.md` | `9ec8776f476a6296240405bc02418ee668a80f0dc868e95feea2f3cc57e36a6e` |
| `source:audio-benchmark-platform/plan/swarm/handoffs/SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER.md` | `3f82802d41944cb26200f6b7e3b85d0541b5c2d4f2b5f9be3f9f5871bd472c07` |
| `source:research/accent-conversion-20261101/README.md` | `c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c` |
| `source:research/accent-conversion-20261101/run_seedvc_realtime.py` | `9461c7b81cc15dcdb0efa907098b8f8ad6ecd21d1a43b3a15ab5f4bd76193ff2` |
| `source:research/voice-conversion-eval-20261101/README.md` | `b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074` |
| `source:research/voice-conversion-eval-20261101/agent-breadth-audit/REPORT.md` | `ef093eee8c8cd68984d3a7f5602fcc44c9a0262990e7c90c9bd34ecc3d8fadc2` |
| `source:research/voice-conversion-eval-20261101/repos/seed-vc/LICENSE` | `8b1ba204bb69a0ade2bfcf65ef294a920f6bb361b317dba43c7ef29d96332b9b` |
| `source:research/voice-conversion-eval-20261101/repos/seed-vc/README.md` | `293507df928d542341a69b9c93e3b7344f7cc7abe73ac4b2c6395d86527a1ce4` |
| `source:research/voice-conversion-eval-20261101/repos/seed-vc/app_vc_v2.py` | `7f05abbdb25a0c6633fde3dea925dd80866f99624a61406172fe3408ffa17196` |
| `source:research/voice-conversion-eval-20261101/repos/seed-vc/configs/astral_quantization/default_2048.yml` | `ed9bf643b8d58b5da3d1cd7529fad5405c70016e40649727fa3e1244366d6f6f` |
| `source:research/voice-conversion-eval-20261101/repos/seed-vc/configs/astral_quantization/default_32.yml` | `13517744ce35fcc2f5cfd2f629f7fd9fab82099846314a823c3bba146eac9827` |
| `source:research/voice-conversion-eval-20261101/repos/seed-vc/configs/v2/vc_wrapper.yaml` | `2f35157afb40ee03748fdd09b252f14bb8d1c8d7a3d2fd1136641a096c109e6e` |
| `source:research/voice-conversion-eval-20261101/repos/seed-vc/hf_utils.py` | `e189160f5381092936c122bd84de570276772e0aaf4f0004ee57f7366a8be6cc` |
| `source:research/voice-conversion-eval-20261101/repos/seed-vc/inference_v2.py` | `d6fa090d93e86313560cda74eb13e12a02da6540a357c7661155a119ffe2bd59` |
| `source:research/voice-conversion-eval-20261101/repos/seed-vc/modules/v2/vc_wrapper.py` | `85d14d9e2ab96045e7886e9919d32f26bc5004da695f0f303060eec10f149fb9` |
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
| `docs/task-evidence/meanvc/README.md` | `34d358ab134b1942b9a3a030acc3017470135921fe90a3cd71fb61c7fd643e40` |
| `docs/task-evidence/meanvc/report.json` | `e9ce6e224056838848aa5bbe52c2bfa0e1f60abb3ffbf2f7c08449e00c983164` |
| `docs/task-evidence/sanas-accent-translation/README.md` | `c62e7fdda4d50d5aa7719cf17353ecadfba6e33d07c6dda9f134fe3685fcb58c` |
| `docs/task-evidence/seed-vc-xls-r-300m-content-encoder/README.md` | `3ffad57b383c93b98b051d10d8bf7f7ce6a4b7c74940611dfd1853269e103f09` |
| `docs/task-evidence/seed-vc-xls-r-300m-content-encoder/report.json` | `0a661101a938600bf26a07b18b6ae0d1fa2c94e6db6394d169dc052b8b3d19ef` |
| `docs/task-evidence/survey-trn-03/report.json` | `aef09671dd0bf39ec7996096f5a866bff564b0110bc1a1e6340fd5fb993f5fe2` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/seed-vc-v2-accent-aware-path/caller-supplied/0.1` is metadata-only.
Required fields are `adapter`, `configuration_id`, `source_dir`,
`source_revision`, `sample_rate_hz`, `hop_size`, `n_fft`, `win_size`, `num_mels`,
`center`, `convert_style`, `anonymization_only`, `diffusion_steps`,
`length_adjust`, `intelligibility_cfg_rate`, `similarity_cfg_rate`, `top_p`,
`temperature`, `repetition_penalty`, `runtime_lock_digest`, `vocoder_revision`,
`whisper_revision`, `hubert_revision`, `target_reference_path`,
`target_reference_sha256`, `target_reference_byte_count`, `target_accent_label`,
`target_consent_id` and `assets`. The validator requires the pinned source
revision, the source-derived V2 geometry, `convert_style=true`,
`anonymization_only=false`, absolute paths, a consent record and hash-matched
caller assets. It still ends in `V2_CHECKPOINT_IDENTITY_UNPINNED`; no asset is
loaded or run.

## Scope gate

`verify.py` resolves the newest merge-base of `HEAD` with `origin/main`, falling
back to `main` only when `origin/main` is unavailable. If no base exists it
emits `scope_base_unavailable`. Any tracked branch difference outside
`docs/task-evidence/seed-vc-v2-accent-aware-path/` emits
`base_out_of_scope_change` and fails closed. Three regression tests cover
newest-base selection, `main` fallback and out-of-scope/missing-base rejection.

## Reproduce

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SEED-VC-V2-ACCENT-AWARE-PATH/docs/task-evidence/seed-vc-v2-accent-aware-path
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

The pinned Seed-VC source checkout is GPL-3.0. That alone does not clear the
AR/CFM/ASTRAL/CAMPPlus checkpoints, Whisper/HuBERT/BigVGAN snapshots, the
accent corpus, consent records, derivative outputs or product use. No source,
weights, audio or runtime bytes are redistributed here. All package files are
Apache-2.0 via SPDX headers and the repository `REUSE.toml` annotation for
`docs/**`.

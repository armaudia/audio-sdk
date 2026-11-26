<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-TORCHAUDIO-TORCHCODEC-AND-SOUNDFILE-COMPATIBILITY-FOR-LLVC — runtime blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
the `torchaudio-torchcodec-and-soundfile-compatibility-for-llvc` row
(title "TorchAudio, TorchCodec and SoundFile compatibility for LLVC"),
component `torchaudio-torchcodec-and-soundfile-compatibility-for-llvc`,
repository `audio-sdk`. Machine-readable **`decision="DEFER"`**,
`status="incomplete"`, `proposal_only=true`,
`qualification.status="not_qualified"`. Missing evidence never qualifies a
candidate.

This package does **not** install, import, link, download or execute torch,
TorchAudio, TorchCodec, SoundFile, SpeechBrain, Auraloss or LLVC. It contains no
wheel, native library, checkpoint, weight, real corpus audio, model output or
benchmark. It pins the existing LLVC source, the actual evaluation wrapper and
the unchanged SDK boundary by SHA-256; records the exact missing runtime
artifacts and rights; probes a fixed path inventory for absence; statically
checks the wrapper's four overrides and three upstream TorchAudio calls; and
exercises a standard-library model of the wrapper's declared WAV contract with
generated synthetic fixtures only. Only
`docs/task-evidence/torchaudio-torchcodec-and-soundfile-compatibility-for-llvc/`
is written. No provider, registry, descriptor, public header/ABI, shared CMake,
CI workflow, installed v0 behaviour, board or handoff file changes.

## Exact external blocker

The pinned LLVC source and wrapper are **present**. The exact runtime is
**absent and unpinned**:

| Artifact | Required | Local status |
| --- | --- | --- |
| Interpreter | CPython `3.11.5` | Present, but no relevant packages |
| torch | `2.15.0` CPU | Only in an unrelated playback-speed virtualenv; **unqualified** |
| TorchAudio | `2.11.1` CPU | **Absent everywhere**; no wheel, byte count or SHA-256 |
| TorchCodec | the build required by TorchAudio `2.11.1` | **Absent and version unrecorded**; no fabricated version or digest |
| SoundFile | `0.12.1` (upstream `requirements.txt`) | **Absent**; only unrelated `0.14.0` installs |
| SpeechBrain | `1.0.3` | **Absent** |
| Auraloss | `0.4.0` | **Absent** |
| Evaluation environment | `.venv-eval` with a hash-pinned lock | **Removed/absent** |

The exact error for the required interpreter is
`ModuleNotFoundError: No module named 'torchaudio'`; `torchcodec`,
`soundfile`, `speechbrain` and `auraloss` are likewise absent there. The
observed unrelated installations are:

| Interpreter | Packages found | Qualified |
| --- | --- | --- |
| `pyenv:3.12.16` | numpy `2.5.4`, scipy `1.18.1`, soundfile `0.14.0` | no |
| `workspace:playback-speed-venv` | torch `2.15.0`, numpy `2.4.6`, scipy `1.17.1`, soundfile `0.14.0` | no |

No torchaudio or torchcodec `dist-info`, module directory or wheel exists in
either location. The unrelated torch installation does not make the LLVC
runtime present, and the 0.14.0 SoundFile installations do not satisfy the
0.12.1 upstream pin.

**Rights requirement.** Wheel licence/notice review, the separate
**libsndfile** and native-library redistribution decision, approval to install
and execute the runtime, a rights-cleared caller-owned WAV fixture with
recorded consent where applicable, and an explicit derived-output and
redistribution decision are all required before any reproduction, optional tool
or release claim. SoundFile metadata declares BSD-3-Clause; libsndfile terms
are separate and unreviewed.

**Reopen condition.** Stage every exact wheel with file name, byte count and
SHA-256 (including the TorchCodec version), record wheel and native-library
terms, install offline in a clean prefix with an import/version digest, execute
the shim against a rights-cleared fixture and the adverse matrix, measure
import/cold-start/per-file I/O/per-chunk timing, then repeat the Tool profile
and obtain independent exact-head review.

## What is present and pinned

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/…/scripts/run_llvc_eval.py` | `d268eb6dca48f88ae03802efd566f7053ac375be82555bd3dac343d750a5488c` | The actual four-line compatibility wrapper |
| `source:research/…/repos/llvc/infer.py` | `88c47703bcd52e70b8d45887828353be7b8b742fe3d08f81448808ce3b06934b` | Upstream load/Resample/save calls |
| `source:research/…/repos/llvc/requirements.txt` | `e2063e6455751a18895c5daa628a8dc728853f8dd5444c0ce766526bf0418825` | `soundfile==0.12.1` pin |
| `source:research/…/repos/llvc/LICENSE` | `718657c20ba7035b25bb447d80a53304115b44fea7e684df2a1ca240555eae4b` | MIT source licence |
| `source:research/…/repos/llvc/model.py` | `b01626c0b0def1aac3c07c597a15529d9eac98f7bd17b241c1a08b88b92dc4b9` | Model boundary (not loaded) |
| `source:research/…/repos/llvc/experiments/llvc/config.json` | `b5e488ada5267a8c09dd843a547fef8f95e39a49764b99f9bccf6a39be2f256c` | Chunk geometry source |
| `source:research/…/results/llvc_asr.json` | `2d8f31e91ea06efed6611a0aa41edf2babb08625a2da22fe30f4333554115c41` | Historical timing/ASR provenance |
| `source:research/…/README.md` | `b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074` | Compatibility narrative |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Tool profile mapping |
| `source:…/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Tool profile |
| `source:…/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` | Unchanged Python binding |
| `docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` | Intake boundary |
| Merged `llvc` README/report | `f6d663bc…` / `22d30a3c…` | Sibling boundary only, not reused |
| Merged `pytorch-and-speechbrain-adapters` report | `7754c964…` | Sibling boundary only, not reused |
| Merged `numpy-scipy-soundfile-wav-resampling` report | `091b57f3…` | Sibling boundary only, not reused |

The shared board row is read only through the stable projection
`{id, title, mode, repository, component}`. `status`, `owner`, `depends_on`,
`claim`, `review`, `handoff`, `blocked_reason`, `dispatch_priority`, `history`,
`write_scope`, `deliverable`, `acceptance` and `evidence` are excluded from
gating. The mutable `plan/swarm/TASKS.json` bytes are never hashed or pinned.

## The pinned shim, checked statically

The evaluation wrapper supplies exactly four overrides:

1. `torchaudio.list_audio_backends = lambda: ["soundfile"]` — restores the
   backend-list symbol that the evaluation note says TorchAudio 2.11 removed.
2. `sf.read(path, dtype="float32", always_2d=True)` — reads a caller WAV as
   float32 in `(samples, channels)` form.
3. `torch.from_numpy(samples.T.copy())` — returns channels-first
   `(channels, samples)`.
4. `sf.write(path, np.asarray(values).T, sample_rate)` — writes channels-first
   data as interleaved WAV.

The upstream calls requiring the shim are
`torchaudio.load(audio_path)`,
`torchaudio.transforms.Resample(sr, sample_rate)(audio)` and
`torchaudio.save(audio_path, audio, sample_rate)`.
`report.json:shim_reference` records one exact text occurrence for each needle;
`executed=false`. This proves only that the pinned files contain the declared
overrides. It does not prove signature, dtype, shape, backend, subtype,
exception or TorchCodec parity.

## Standard-library WAV contract model (not SoundFile)

`report.json:wav_contract_probe` exercises the wrapper's declared data path
with generated PCM16 WAV bytes using the standard library only. It is harness
plumbing, not a runtime substitute and not candidate output.

| Case | Channels | Samples | Bytes | Peak | RMS | Endpoint-limited | Max error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `silence` | 1 | 160 | 364 | 0.000000 | 0.000000 | 0 | 0.000000 |
| `impulse` | 1 | 160 | 364 | 0.500000 | 0.039528 | 0 | 0.000000 |
| `full_scale` | 1 | 160 | 364 | 1.000000 | 0.999985 | 80 | 0.000031 |
| `ramp` | 1 | 160 | 364 | 0.899994 | 0.520431 | 0 | 0.000015 |
| `stereo` | 2 | 160 | 684 | 0.799988 | 0.385746 | 0 | 0.000015 |

Every case preserves the exact sample count and channels-first orientation,
re-encodes byte-identically, and stays within the one-LSB
`1/32768 = 0.000031` bound including the positive endpoint. The identity
control re-encodes identical bytes and re-decodes identical digests.

Fourteen adverse cases are rejected with no state change: truncated RIFF, bad
magic, non-WAV payload, PCM8, PCM24, empty frames, three channels, zero rate,
nonfinite NaN/Infinity writes, nonnumeric sample, ragged channels, three encode
channels and zero encode rate.

## Fail-closed request evidence

`report.json:adverse` records **23** rejected requests and **6** rejected JSON
documents. Requests are rejected before any runtime call for unknown tool or
field, missing field, wrong Python/torch/TorchAudio/SoundFile pin, a claimed
present TorchCodec, unknown operation, wrong rate/channels/frame/dtype/source,
short sample list, NaN/Infinity, out-of-range, boolean/string samples and
closed/drained lifecycle. A fully valid request still fails closed with
`RUNTIME_ABSENT`; there is no fallback, surrogate or identity substitution.

## Tool acceptance profile

Pinned from `plan/swarm/VERIFICATION.md` and mapped in
`report.json:tool_profile`:

| Required case | Evidence | Status |
| --- | --- | --- |
| Version, install, provenance | runtime absence probe; recorded stack pins | blocked |
| Clean checkout/extracted package | no wheel/package/install exists | not run |
| One typical CLI/API use | stdlib WAV contract model only | synthetic pass |
| Caller-owned inputs | synthetic sample lists, no real fixture | synthetic pass |
| Malformed inputs | 23 requests + 6 JSON + 14 WAV rejections | synthetic pass |
| Missing optional selection | missing runtime/TorchCodec/SoundFile/wrong pin rejected | synthetic pass |
| Compile/build evidence | no build, link, CMake or packaging change | not run |
| Synthetic runtime evidence | no runtime; model is plumbing only | not run |
| Measured workload support | no timing, resource or benchmark result | not run |

The Tool profile is **not satisfied**. No synthetic case is a runtime result.

## Source timing: provenance only, never measured

The historical values are transcribed with their original one-utterance scope:

| Field | Historical value | Local status |
| --- | --- | --- |
| Chunk | 208 samples / 13.0 ms | derived from the pinned config |
| Lookahead | 32 samples | derived from the pinned config |
| Algorithmic offset | 240 samples / 15.0 ms | derived; not device-measured |
| Chunks for 9.6550625 s | 743 | arithmetic on the pinned ASR duration |
| RTF | 0.123 (≈8.1× slower than real time) | **not measured here** |
| End-to-end estimate | 120.785 ms | upstream estimate; not device-measured |
| Derived average inference | 105.691 ms | arithmetic on the source-reported RTF |
| Derived deadline miss | 9.291× the 13 ms chunk | arithmetic, not a measurement |
| WER | 0.0% (one utterance) | historical JSON only |
| Shim overhead, import, cold start | unavailable | **not measured** |

The shim overrides file-level load/save only. It adds no per-chunk I/O to the
streaming loop, so it cannot change the per-chunk model compute that misses the
deadline. That statement is structural, **not** a timing result.

## Eight blocked release gates

| Gate | Blocked reason |
| --- | --- |
| `RG-01` exact runtime artifact pins | No TorchAudio/TorchCodec/SoundFile wheel exists; TorchCodec version and every wheel digest are unpinned. |
| `RG-02` licence, notice and libsndfile review | Wheel terms, bundled native-library terms and redistribution decisions are unreviewed. |
| `RG-03` clean runtime build and install parity | `.venv-eval` and any lockfile are absent; no clean install or import digest exists. |
| `RG-04` shim API semantics parity | The four overrides and three upstream calls are text-checked only. |
| `RG-05` pinned I/O fixture parity | Only a stdlib model exists; no real SoundFile/TorchAudio/subtype parity or rights-cleared fixture. |
| `RG-06` adverse runtime behaviour | Real exceptions, partial writes, backend errors and nonfinite propagation are unmeasured. |
| `RG-07` source timing and deadline impact | Import, cold-start, per-file I/O and per-chunk overhead are not measured. |
| `RG-08` tool intake, optional packaging, review and release | No OFF-by-default optional tool, intake, public-surface decision or independent review exists. |

No synthetic model case or historical value opens a gate.

## Files and reproduction

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, pins, model results, Tool mapping, gates. |
| `LICENSES.md` | Runtime/native/input rights boundary; no vendored third-party bytes. |
| `contract.json` | Machine-readable contract: pins, blocker, eight gates, Tool rows. |
| `reference.py` | Stdlib-only strict JSON, probes, request matrix, WAV model, canonical report. |
| `run.py` | Byte-identical regeneration of report, sidecar, sources and contract. |
| `report.json` | Canonical sorted-key compact JSON; `DEFER`, `incomplete`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of external pins and task-local artifacts. |
| `test_reference.py` | 37 deterministic unittest checks; no skips, network or runtime. |
| `verify.py` | Read-only verifier: pins, canonical bytes, absence, licensing, scope, three cold starts. |
| `*.license` | REUSE sidecars for JSON/digest artifacts. |

From this directory:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py --all
python3 -m unittest -v test_reference.py
python3 verify.py
```

`run.py --all` regenerates every canonical artifact; `verify.py` additionally
runs three cold-start regenerations, checks strict JSON, exact pins, stable
board identity, licensing, task-local git scope and blocker semantics. From the
SDK worktree root, `git diff --check` must also be clean.

Current counts: 23 request rejections, 6 JSON rejections, 14 WAV rejections,
5 model cases, 8 required artifacts (1 present, 7 blocked), 6 exact blockers,
9 Tool rows, 8 blocked gates, **0 qualifying results**.

## Expected digests

- `report.json` SHA-256:
  `3b977a7c2e0f6c28577e68e0b2ccaa394b0c68ff74f4363f278467fea1e6f11e`
- Canonical report object digest:
  `af4aca6487fd8a23fa097adcd86d5ee91eeec620d6b5899e92bae93ab94bf3d0`
- `contract.json` is regenerated after this README; its own digest is not
  embedded here because the contract pins this file (a self-reference).

## Non-claims

No TorchAudio, TorchCodec, SoundFile, torch, SpeechBrain, Auraloss or LLVC
runtime, wheel, native library, checkpoint, weight, corpus or model output is
included, installed, imported or executed. No compatibility, API, byte-level,
timing, callback, memory, listening, benchmark or release result is claimed.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. Historical
values remain source-reported provenance in their original one-utterance scope.

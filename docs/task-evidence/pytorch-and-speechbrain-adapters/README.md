<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PYTORCH-AND-SPEECHBRAIN-ADAPTERS — runtime and asset readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`pytorch-and-speechbrain-adapters` (`component_id=pytorch-and-speechbrain-adapters`,
title "PyTorch and SpeechBrain adapters"). Decision: **DEFER** before
`runtime_integration`; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does **not** import, install, link, download, load or execute
PyTorch, torchaudio, SpeechBrain or HyperPyYAML. It contains no checkpoint,
weight, config, hyperparams file, audio signal, corpus payload, adapter
inference or model output. It pins the existing project adapter sources,
descriptors, runtime lock and protocol by SHA-256, records the exact missing
runtime/checkpoint artifacts and rights, probes a fixed path inventory to
evidence absence, exercises the adapter **envelope** with synthetic bytes only,
and defines a fail-closed admission boundary for a future adapter run. Only
`docs/task-evidence/pytorch-and-speechbrain-adapters/` is written; no provider,
registry, descriptor, public header/ABI, shared CMake, CI workflow or installed
v0 behavior changes.

## Exact external blocker

The exact runtime and both checkpoint byte sets are **absent**:

- The pinned CPython `3.12.16` interpreter exposes no `torch`, `torchaudio`,
  `speechbrain` or `hyperpyyaml` (`find_spec` returns `None`). The exact error
  is `ModuleNotFoundError: No module named 'torch'`.
- The recorded runtime is CPython `3.11.5`, torch `2.14.1`, torchaudio
  `2.11.0`, SpeechBrain `1.0.3`, HyperPyYAML `1.2.3`, plus the isolated
  sentencepiece/PyYAML/ruamel/huggingface-hub/NumPy/SciPy/SoundFile overlay.
  The historical `data/envs/clearvoice` environment is gone; its site-packages
  paths, the Hugging Face model caches and every fixed checkpoint path are
  absent.
- `speechbrain/metricgan-plus-voicebank` at revision
  `be514d321f66b5352c5a8d59c44700f57aa8c8f5` records
  `enhance_model.ckpt` at 7,586,021 bytes and SHA-256 `147bfb86…`,
  `hyperparams.yaml` at `7bcc0835…` and `config.json` at `18cb7139…`. None is
  present.
- `speechbrain/sepformer-dns4-16k-enhancement` at revision
  `e8c258546300102a240fa2595854d473cbfee49a` records `brain.ckpt`,
  `encoder.ckpt`, `masknet.ckpt`, `decoder.ckpt`, `config.json` and
  `hyperparams.yaml` with SHA-256 values in the pinned lock. None is present,
  and the lock does not record byte counts.
- No rights-cleared caller-owned input set, checkpoint training-data review or
  derived-output permission exists. The recorded 30-pair DNS2020 screen is
  provenance only.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | A locked offline CPython `3.11.5` environment with torch `2.14.1`, torchaudio `2.11.0`, SpeechBrain `1.0.3`, HyperPyYAML `1.2.3` and the recorded overlay: wheel names/versions/byte counts/SHA-256, install location, and a clean-room import plus checkpoint-load digest. |
| `BLK-02` | The exact MetricGAN+ revision `be514d32…` files (`enhance_model.ckpt` 7,586,021 bytes / `147bfb86…`, `hyperparams.yaml`, `config.json`) with matching digests, a complete model card/license/notice bundle and an artifact-specific plus training-data terms review. |
| `BLK-03` | The exact SepFormer revision `e8c25854…` six-file set with recorded SHA-256 values and newly recorded byte counts, plus the same terms and training-data review. |
| `BLK-04` | A digest-pinned, rights-reviewed caller-owned input set with corpus, acquisition, evaluation, derived-output and redistribution decisions, checkpoint training-data terms, and an attribution record. |
| `BLK-05` | A fresh offline run of both pinned adapters in the exact runtime, one intra-op and one inter-op thread, deterministic algorithms, no network, per-item input/output hashes, finite/length-preserving checks, exact repeats, peak/RSS and adverse/missing controls. |
| `BLK-06` | A separate versioned OFF-by-default developer tool/adapter or provider intake, mode and platform measured separately, then provider intake and independent exact-head review. |

**Reopen condition.** A caller supplies the locked runtime with wheel hashes and
install/import digest, both exact checkpoint revisions with per-file byte counts
and SHA-256 plus reviewed terms, a rights-cleared input set, a reproduced
deterministic adapter run with controls, the Tool profile re-applied against the
real runtime, and separate mode/platform measurements. Until then this task
stays `DEFER`.

## What is present and pinned

The project adapter sources and protocol are present and pinned by SHA-256:

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/…/evaluation_records.md` | `962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a` | Evidence register for this task |
| `source:…/agent-metricgan-eval/REPORT.md` | `cae46203911914adafb007f6148ca9c1bdc5c1d9eb2875a0fb6205aca7303783` | MetricGAN+ provenance only |
| `source:…/agent-metricgan-eval/adapter.py` | `4f8934d4d83cd3a1042c950dbea1fb1d89c6248f499f2101459ce8b28f4f1f4d` | Pinned adapter source |
| `source:…/agent-metricgan-eval/adapter.json` | `18c53358377bc5882fb5a175ae7084aa64b36accb5825f2c126612c3cbb37d67` | Protocol descriptor |
| `source:…/agent-metricgan-eval/requirements.lock` | `22b5283ab4f920dc16017d545552a46d2706cbade14e1cfa1209f28c255ddc20` | Runtime pins |
| `source:…/agent-sepformer-eval/REPORT.md` | `b7a1e214d0fa402c971e39a4742d54589ce5bd25bd3de4a5bc72be843ec997f4` | SepFormer provenance only |
| `source:…/agent-sepformer-eval/adapter.py` | `9e85412481780ad9b917428bc36d5cf407cfe9c0842a96de8953706041ad3327` | Pinned adapter source |
| `source:…/agent-sepformer-eval/adapter.json` | `b6135146118e303ff335a4418a8906234c9b85d9031836d96b27a524ab0871e5` | Protocol descriptor |
| `source:…/agent-sepformer-eval/adapter.lock.json` | `631685078d2218cb0bdd656be622e6953679e1c51c1662d6a858cf214451aac1` | Six file digests |
| `source:adapters/README.md` | `24d8915f0ff59ee026ef86b396f64f1b3e68d3a5678f98a353273b712f09e1ee` | Adapter protocol and no-download rule |
| `source:adapters/controls/run.py` | `4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66` | Protocol harness |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Tool profile mapping |
| `source:…/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Tool profile |
| `source:…/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` | Unchanged Python binding |
| `docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` | Intake boundary |
| `docs/task-evidence/metricgan-speechbrain-voicebank/README.md` | `0ce5593cda4ed6412d755ecd013c4ef65f3e1c50c4f264a1abb4782b57990f22` | Merged sibling boundary only |
| `docs/task-evidence/metricgan-speechbrain-voicebank/report.json` | `8f04d6f06cea71f6497277131d3b4adcb7b5381c5fc25b4fa646fe91476935e2` | Merged sibling, not reused |

The shared board row is read only through the stable projection
`{id, title, component, mode, repository, depends_on}`. `status`, `owner`,
`claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` are
excluded from gating. The mutable `plan/swarm/TASKS.json` bytes are never
hashed or pinned.

## Proposed developer-facing boundary

`contract.json` declares `audio-sdk/pytorch-and-speechbrain-adapter-run/0.1` as
a task-local admission schema, not an SDK or runtime contract. A future
qualified run would supply exactly:

```text
schema_id, run_id
adapter   {identity, protocol, mode, adapter_sha256, descriptor_sha256}
runtime   {python, torch, torchaudio, speechbrain, hyperpyyaml, device,
           intra_op_threads, interop_op_threads, deterministic_algorithms,
           offline, install_reference, wheel_digests}
command   {cli, request_argument, result_argument, network, downloads}
assets[]  {asset_id, name, byte_count, sha256, terms_sha256, present_at_review}
input     {sample_rate_hz, channels, sample_count, dtype, sha256, finite, peak}
output    {sample_count, sha256, finite, peak, delay_compensation_samples}
controls[] {id, kind}
rights    {adapter_source_terms, runtime_terms, weight_terms, data_terms,
           output_use, review_reference, claims_qualified}
```

Accepted values are exact: `protocol=audioml-adapter/1`, `mode=offline`,
Python `3.11.5`, torch `2.14.1`, torchaudio `2.11.0`, SpeechBrain `1.0.3`,
HyperPyYAML `1.2.3`, CPU, one intra-op and one inter-op thread, deterministic
algorithms on and offline on. The command is the one-attempt
`--request`/`--result` form under `/attempt/<run_id>/`, network and downloads
denied. Assets must match one adapter profile's exact file set and digests; the
SpeechBrain wheel digest must equal
`9859d4c1b1fb3af3b85523c0c89f52e45a04f305622ed55f31aa32dd2fba19e9`. Input
must be mono 16 kHz `f32`, finite with peak ≤ 1; output must be
length-preserving, finite, peak ≤ 1 and delay 0. `claims_qualified` must be
`false`. These are admission bounds, not measured results.

## Fail-closed exercise (synthetic only)

`report.json:admission` records **83** actual rejections across strict JSON,
structure, adapter, runtime, command, asset, input, output, rights, control and
nonfinite groups. Exactly one structural schema control is admitted to prove
the validator is not blanket-rejecting; it is labelled
`synthetic_schema_control_not_evidence` and `qualifies=false`. No admission
case reads audio, loads weights, imports a runtime or invokes a model.

`report.json:protocol_envelope` exercises the adapter envelope with a
deterministic 160-sample binary-fraction frame:

- `--request`-shaped request → copied caller bytes → identity output;
- input/output SHA-256 `ce9de6cc7f8d3bdd9a1e00136b512d7c79f4cc8bb1a2ac59947eb24aa076c85f`,
  640 bytes, peak `0.78125`;
- replay and reset-replay are byte-identical, double close is idempotent and a
  post-close run is rejected with `adapter_closed`;
- **15** malformed/missing/nonfinite/out-of-range envelope cases are rejected
  with zero calls and unchanged state.

This proves protocol plumbing only. It is not a runtime, model, checkpoint,
inference, timing, quality or release result.

## Tool acceptance profile

Pinned from `audio-benchmark-platform/plan/swarm/VERIFICATION.md` and mapped in
`report.json:tool_profile`:

| Required case | Evidence | Status |
| --- | --- | --- |
| Version, install, provenance | runtime absence probe; recorded wheel/environment pins | blocked |
| Clean checkout/extracted package | evidence-only directory; no package or install | not run |
| One typical CLI/API use | synthetic envelope request/result, replay, reset, close | synthetic pass |
| Caller-owned inputs | synthetic bytes copied and digest-checked | synthetic pass |
| Malformed inputs | 83 manifest + 15 envelope + strict JSON rejections | synthetic pass |
| Missing optional selection | missing runtime/network/download/mode/asset rejected | synthetic pass |
| Compile/build evidence | no build, link, CMake or package change | not run |
| Synthetic runtime evidence | no runtime; envelope is protocol plumbing only | not run |
| Measured workload support | no timing, resource, device or benchmark result | not run |

The Tool profile is not satisfied: the runtime is missing and nothing was
measured against a real PyTorch/SpeechBrain runtime.

## Mode and platform, measured separately

`report.json:mode_platform` keeps three rows distinct: offline CPU provenance
on one shared Apple M1 host; streaming as not applicable (both adapters declare
`modes=["offline"]` and process whole waveforms); and target/mobile as blocked
(no phone, NPU, GPU, callback, thermal or battery measurement). Historical RTF
and RSS values are provenance only and are never pooled with a new measurement.

## Historical execution: provenance only

Both recorded runs are transcribed with their original scope and are **not
rerun, not used for evidence and not qualifications**:

| Field | MetricGAN+ | SepFormer DNS4 |
| --- | --- | --- |
| Mode / device | offline / CPU | offline / CPU |
| Valid outputs | 30/30 | 30/30 |
| Mean ΔSNR vs identity | −10.505 dB | −19.432 dB |
| Mean ΔSI-SDR vs identity | −3.538 dB | +8.525 dB |
| Mean ΔSTOI vs identity | −0.00850 | +0.03313 |
| Mean RTF | 0.00443 | 0.693 |
| Peak child RSS | 316,047,360 B | 1,894,531,072 B |
| Intra-op threads | not fixed in adapter | 4 |

The SepFormer run's four intra-op threads do not match this package's
one-thread reference admission policy, so it cannot be promoted without a
rerun. No result here is a quality, parity, product or release claim.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision and license provenance | blocked | Stage both exact model revision archives with complete license/notice/model-card and training-data terms, then record an independent review. |
| `RG-02` pinned runtime and offline install | blocked | Provide the locked CPython 3.11.5 environment with wheel hashes, install location and clean-room import/load digest. |
| `RG-03` checkpoint assets and per-file digests | blocked | Stage every checkpoint/config/hyperparams file for both revisions and verify byte counts and SHA-256. |
| `RG-04` rights-cleared caller inputs | blocked | Freeze a permitted, digest-pinned input set with corpus, evaluation, derived-output and redistribution decisions. |
| `RG-05` adapter execution and output validity | blocked | Execute both adapters offline and record output hashes, finite/length preservation, repeats and resources. |
| `RG-06` Tool profile against the real runtime | blocked | Repeat every Tool-profile case against the installed runtime and both checkpoints. |
| `RG-07` mode, platform, timing and resources | blocked | Measure offline and any future streaming mode separately with p95/p99 timing and resources. |
| `RG-08` provider intake, public surface and release | blocked | Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear. |

No synthetic admission or envelope control opens a gate. No missing result is
promoted.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Runtime/checkpoint/input boundary; no vendored third-party text or bytes. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, Tool rows, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, absence probes, provenance checks, admission validator, synthetic envelope, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | 47 deterministic unittest checks; no skips, network, runtime, checkpoint or audio. |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, scope and three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/pytorch-and-speechbrain-adapters` with the pinned
interpreter and stdlib only:

```sh
export PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` reports `repeat=3 byte_identical=true`; all 47 unittest
checks pass with 0 failed and 0 skipped; `verify.py` prints
`PASS ... cold_starts=3/3 byte_identical=true profile=Tool status=incomplete
decision=DEFER`; REUSE reports no missing or bad license; `git diff --check` is
clean. `verify.py` writes only to a temporary directory.

Current counts: 24 absence probes (16 workspace, 4 SDK worktree, 4 home; 0
present), 25 boundary/source pins, 7 required artifacts (1 source present,
6 blocked), 6 open blockers, 83 manifest rejections plus 1 schema-only control,
15 envelope rejections plus 1 lifecycle control, 9 Tool rows, 3 mode/platform
rows, 8 blocked gates, 0 qualifying results.

## Expected digest

`report.json` SHA-256:
`7754c9647064f89c7d831fd9bd7d3a9f3560c51c00a22bfc8dc9da3aa59e349c`.

`contract.json` object digest:
`02ea68365118e22f4aa112b4148c2143d19c31226411e8d2489cd3b14bb3f2aa`.

## Separation from other evidence

The merged `metricgan-speechbrain-voicebank` package is a different candidate
boundary and its synthetic surrogate, corpus chain and negative result are
never substituted here. `onnx-runtime-reference-runtime`,
`neural-runtime-boundary` and `bench-subprocess-protocol` are separate adapter
or runtime boundaries; none is pooled with this package. The historical
MetricGAN+ and SepFormer reports remain their own offline DNS2020 screens and
are not combined into a PyTorch/SpeechBrain tool qualification.

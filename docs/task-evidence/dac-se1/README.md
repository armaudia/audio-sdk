<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DAC-SE1 - DAC-SE1 source, checkpoint, tokenizer and CUDA-runtime blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DAC-SE1` (`component_id=dac-se1`). The acceptance profile is **Enhancement**,
assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `status=incomplete`, `proposal_only=true` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed DAC-SE1 source, checkpoint, tokenizer/vocoder toolchain,
CUDA-class runtime, immutable revision, generation geometry and numeric output
are **absent**. This package records that exact blocker, applies the Enhancement
profile to a bounded deterministic synthetic protocol envelope, and makes no
enhancement, quality, latency, listening, benchmark or release claim. It is
**not DAC-SE1**: no autoregressive model, codec tokenizer, vocoder, weight file,
native library, real audio, corpus, model, device clock or upstream code is
present, copied, downloaded, loaded, imported or executed. Only this task-local
directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=dac-se1`) is `considered`,
`disposition=sdk-model`, `verification_profile=enhancement`, area `Enhancement`,
with the finding "Autoregressive discrete-audio-token speech enhancement;
high-fidelity, offline GPU reference". Its only evidence link is
`research/noise_suppression_candidate_census.md`, line 68.

That sentence adds two source-reported links,
`https://github.com/ETH-DISCO/DAC-SE1` and
`https://huggingface.co/disco-eth/DAC-SE1`, and reports:

- code and checkpoint both **declare MIT**;
- published inference explicitly moves the model and token IDs to CUDA and uses
  chunked generation;
- the released checkpoint is **1.84 GB**;
- the candidate is **not runnable on the current CPU-only worker as published**;
- an MPS route would be a separate unvalidated backend, and the complete
  tokenizer/toolchain must be verified.

It records no immutable commit or release tag, source file, license text,
`COPYING`/`NOTICE`, checkpoint file name, per-file byte count, SHA-256,
tokenizer or vocoder identity, training-data term or numeric output. A URL is
not a pin and a declared license is not staged license text.

Consequently:

- no DAC-SE1 source, checkpoint, tokenizer, vocoder, config, runtime or adapter
  is staged at `data/checkouts/DAC-SE1`, `data/checkouts/dac-se1`,
  `data/models/dac-se1`, `data/models/disco-eth/DAC-SE1`,
  `data/envs/dac-se1`, `data/envs/dac-se1-cuda` or `adapters/dac-se1`;
- no immutable source/weight hash, build identity, parameter layout, token
  vocabulary, tokenizer/vocoder mapping, chunk size, lookahead, seed, dtype or
  numeric output exists for DAC-SE1 itself;
- no upstream MIT license text, model card, weight terms, training-data
  statement, attribution bundle, corpus rights or product-use review is staged;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream with no
  codec-token, chunked-generation or CUDA-device provider geometry, descriptor,
  registry entry or asset contract;
- no real speech, corpus, noisy/clean pair, consent, held-out split,
  SI-SDR/STOI score, clean-speech preservation result or listening result
  exists;
- no target-device timing, independent review, provider intake or release
  approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-DAC-SE1`, `7b00d762530bb69ca58d4cdb8194a83839e1d58c` |
| Task mode | `feasibility` |
| Acceptance profile | `enhancement` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/tokenizer/chunk asserted |
| Surrogate | fixed 160-sample byte-identity protocol envelope |
| Provider registration, default, ABI, CI | none |

The surrogate is a protocol envelope over one frozen synthetic mono frame. It
is **not DAC-SE1**, is not autoregressive, uses no tokenizer or weights and
cannot qualify the candidate.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied item by item in
`report.json` -> `enhancement_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Identity/noisy control and task-matched baseline | blocked | Only a synthetic identity copy; no noisy control or established baseline is executed |
| Paired SI-SDR and STOI | blocked | No rights-cleared clean references, scorer or candidate output |
| Clean-speech preservation, peaks, invalid outputs | blocked | Only synthetic finite/peak checks on copied bytes |
| Alignment, state, memory, timing | blocked | No exact runtime, chunk recipe, state or timing |
| Unpaired screen or authorized listening | blocked | No protocol, speech or result |
| Quiet/active speech, idle noise, low SNR, onset/offset | blocked | One placeholder frame is not speech evidence |
| Separate evidence categories | documented | Synthetic, admission, source-reported and missing-real sections are kept distinct |

Every real-result row is `qualifies=false`. Synthetic exactness means only that
the fixture is self-consistent.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample.
- Frame: 640 bytes, deterministic binary-fraction values
  `((index * 37) % 201 - 100) / 128`, peak `0.78125`.
- Admission control: one synthetic run manifest with four asset roles
  (`model`, `tokenizer`, `vocoder`, `config`) and five named controls.
- Request/result envelope: `audioml-dac-se1-run/1`, offline only, network and
  downloads denied, writes limited to the attempt directory.

Measured synthetic observations (all unqualified):

| Item | Value |
| --- | ---: |
| Input/output bytes | 640 |
| Input/output SHA-256 | identical |
| Output peak | 0.78125 |
| Replay identity | exact |
| Reset replay identity | exact |
| Rejection cases | 20 |
| Admission rejections | 90 |

The envelope proves finite/peak/length plumbing on copied bytes. It proves no
autoregressive generation, codec-token decoding, enhancement or qualification.

## Adverse, missing and invalid handling

`report.json` records **90** rejected inputs, each with unchanged processing
state. Rejections include duplicate JSON key, `NaN`/`Infinity` constants,
malformed JSON, non-object root, trailing data, byte-order mark,
missing/extra/cleared manifest sections, bad run/schema IDs, missing or
malformed upstream/checkpoint repository and revision, empty license, bad
tokenizer, zero/oversized/string chunk size, negative/oversized seed, empty
padding profile, missing model fields, wrong Python/torch/CUDA versions,
unknown device/dtype, non-deterministic or online execution, empty install
reference, empty/invalid wheel digests, wrong command protocol, non-attempt
paths, allowed network/downloads, empty/too-many/duplicate/missing assets, bad
asset role, zero bytes, bad digests, absent-at-review assets, 8 kHz, stereo,
zero/oversized sample counts, `f64`, invalid input hash, nonfinite input, peak
outside `[0,1]`, output length mismatch, output delay, missing rights text,
`claims_qualified=true`, and control list defects. Missing real recordings,
checkpoints, tokenizer bytes, runtime outputs and labels are `blocked`, never
passes.

The caller asset contract validates declaration identity only. It never reads,
loads, imports or executes a source tree, checkpoint, tokenizer, vocoder or
runtime. A hash-matched placeholder is never accepted as the pinned DAC-SE1
artifact.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision and MIT license provenance | blocked | Stage the DAC-SE1 source snapshot at an immutable revision with complete license, notice and model-card records, then review independently. |
| `RG-02` pinned CUDA-class runtime and offline install | blocked | Provide a locked offline runtime with wheel hashes, install location, clean-room import digest and the exact generation configuration. |
| `RG-03` checkpoint, tokenizer and vocoder assets | blocked | Stage every checkpoint, tokenizer, vocoder, config and metadata file with verified byte counts and SHA-256. |
| `RG-04` rights-cleared inputs and training data | blocked | Freeze a permitted, digest-pinned input set with corpus, evaluation, derived-output and redistribution decisions plus training-data terms. |
| `RG-05` reference execution and output validity | blocked | Execute the pinned checkpoint and tokenizer offline and record output hashes, finite/length preservation, repeats, generation settings and peak/RSS. |
| `RG-06` Enhancement profile against the real runtime | blocked | Run every profile case on a rights-cleared cohort with controls, baseline, SI-SDR/STOI, preservation and timing. |
| `RG-07` mode, platform, timing, resources and listening | blocked | Measure each mode/platform separately with latency, resources, pacing and authorized listening or a labeled screen. |
| `RG-08` provider intake, public surface and release | blocked | Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear. |

No synthetic admission or envelope control opens a gate.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, blockers, counts, commands, gates. |
| `LICENSES.md` | Source/checkpoint/tokenizer/runtime/input boundary; no vendored third-party text or bytes. |
| `contract.json` | Machine-readable contract: pins, source-reported identity, checkpoint scope, artifacts, blockers, eight gates, Enhancement rows, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, board projection, absence probes, inventory/snippet checks, admission validator, synthetic envelope, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks; no skips, network, runtime, checkpoint or audio. |
| `verify.py` | Read-only strict-JSON, pin, digest, reproduction, licensing and scope verifier. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row
is machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:docs/task-evidence/cof-denoising-checkpoints/README.md` | `25ab2dd5de7dd3e1e91cb6af278c2132c00accc4fc488bc9374747fd6ad2a3e4` |
| `sdk:docs/task-evidence/cof-denoising-checkpoints/contract.json` | `b3d6457802ccd0097fcedbd76a20562415a5edbeb148b6573bc77e06fdbd3eea` |
| `sdk:docs/task-evidence/cof-denoising-checkpoints/report.json` | `ff100450d2cabcddfd49c9d3c98ba06dfcc0c2191a71652ffb88485c44490e3a` |
| `sdk:docs/task-evidence/complex-bin2bin-generative-plc/README.md` | `93e595157418491780c1e8a040c9f32fe7b8cfce583a5441f517fee9c23e8d0e` |
| `sdk:docs/task-evidence/complex-bin2bin-generative-plc/contract.json` | `1405fd1716ef944bc41d8fa4d5f0b4c98cc5900df500fa28963a48d24164e2e7` |
| `sdk:docs/task-evidence/complex-bin2bin-generative-plc/report.json` | `6f6214f89eca8009a19e980c3cc5b24af918c600345573e861d18d2da1e54f23` |
| `sdk:docs/task-evidence/clearvoice-mossformergan/README.md` | `4cce8370c8af8bd2a5a83f05bf15e540756f1f7d61f63170b6a9626f65d6bbce` |
| `sdk:docs/task-evidence/clearvoice-mossformergan/report.json` | `5c806186d35c1f39021617dc5649bf32d87030a1a059d26e35492a69ee1a7afc` |
<!-- digest-table: end -->

## Separation from sibling evidence

The merged `cof-denoising-checkpoints` and `complex-bin2bin-generative-plc`
packages are different source/checkpoint/runtime blockers, and
`clearvoice-mossformergan` is a separate enhancement candidate. Their README,
contract and report files are pinned only as read-only boundary references. This
package does not import, pool, score or reuse their source, fixtures, assets,
metrics or results. The census line is source-reported context, not measured
evidence.

## Reproduce

Run from this directory with the pinned interpreter and stdlib only:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DAC-SE1/docs/task-evidence/dac-se1
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py all
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` reports `repeat=3 byte_identical=true`; all test checks pass
with 0 failed and 0 skipped; `verify.py` prints `PASS ... gates=8 blockers=6
... cold_starts=3/3 byte_identical=true profile=Enhancement status=incomplete
decision=DEFER`; REUSE reports no missing or bad license; `git diff --check` is
clean. `verify.py` writes only to a temporary directory.

Current counts: 28 absence probes (16 workspace, 6 SDK worktree, 6 home; 0
present), 23 boundary/source pins, 7 required artifacts (1 evidence register
present, 6 blocked), 6 open blockers, 7 Enhancement rows (6 blocked, 1
documented, 0 real), 3 mode/platform rows, 90 admission rejections plus 1
schema-only control, 20 envelope rejections plus 1 lifecycle control, 8 blocked
gates, 0 qualifying results.

## Expected digest

`report.json` SHA-256:
`e5e9aad4b1d3571a2fe190f7985d1d120091787cbcf5192fe5cb10a621706f9d`.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only (`tasks[id=SDK-DAC-SE1]`,
stable-field digest); the mutable full `plan/swarm/TASKS.json` is never hashed,
pinned or used as a digest source. No provider, descriptor, registry, installed
default, shared build or CI is changed.

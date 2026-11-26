<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FACEBOOK-DENOISER-DNS64: Facebook Denoiser DNS64 model-admission blocker

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local feasibility evidence for
the Facebook Denoiser DNS64 row. It is **not** Facebook Denoiser: no upstream
source, Demucs network definition, pretrained DNS64 checkpoint, runtime, license
text, corpus, candidate audio, listening result, timing measurement, benchmark
or release claim is included. **No result here qualifies the candidate.**

## Exact blocker: source, DNS64 weights, runtime, rights and matched cohort absent

A bounded, read-only search of named workspace paths found **no
`facebookresearch/denoiser` checkout**, **no pretrained DNS64 checkpoint**, **no
pinned PyTorch/demucs/denoiser runtime**, **no local license text** and **no
matched paired clean/noisy cohort**. Nothing was cloned, downloaded, extracted,
converted, imported, loaded or reconstructed.

The pinned research note also records the repository/model license as
**CC-BY-NC 4.0** and recommends research-only comparator use with exclusion from
commercial selection. That reported NonCommercial term is an independent rights
blocker for this product SDK until a written decision explicitly permits the
intended use, redistribution and derived output.

| Item | Status |
| --- | --- |
| Source checkout | **Absent.** No local `facebookresearch/denoiser` copy; revision, tree digest, file count and license file are `null` |
| DNS64 weights | **Absent.** No artifact path, byte count, SHA-256, checkpoint terms or lineage is recorded |
| Runtime | **Absent/unpinned.** `torch`, `torchaudio`, `demucs`, `denoiser`, `numpy`, `soundfile` and `onnxruntime` are not importable in the evidence interpreter; no lock, build record or ABI is pinned |
| License and rights | **Blocked.** CC-BY-NC-4.0 is source-reported only; no byte-identical license text, SHA-256 or written NonCommercial/product/redistribution decision exists |
| Candidate geometry | **Unverified.** The pinned sources record no input rate, channels, normalization, frame/chunk geometry, state, lookahead, output scaling or content delay |
| Matched cohort | **Absent.** No rights-cleared paired clean/noisy task-matched corpus, pinned SI-SDR/STOI scorer or held-out split |
| Candidate execution | **None.** No model load, inference, denoising, preservation, quality or timing run occurred |

The machine-readable record is `report.json` -> `upstream_blocker`
(`status="blocked_source_weights_runtime_license_and_fixture_absent"`, with
every source, weight, runtime, license, fixture and geometry digest `null`),
`required_artifacts` (A1-A6), `artifact_requirement`, `source_probe`,
`weights_probe`, `runtime_probe`, `license_probe`, `fixture_probe`,
`rights_probe`, `geometry`, `asset_contract` and `external_boundary`.
`contract.json` carries the same blocker, the same missing artifacts and all
eight blocked release gates.

## What the pinned evidence records

`research/noise_suppression_candidate_census.md`, line 50, records the
`Facebook Denoiser DNS48 / DNS64` row as **causal waveform Demucs models;
streaming and higher-capacity references**, with an archived official repository
that supplies pretrained DNS models and streaming evaluation, and a
repository/model license of **CC-BY-NC 4.0**. It recommends research-only
comparator use, exclusion from commercial selection, and checking the archived
dependency stack and CPU RTF.

The same row and the same finding are the only evidence for both
`facebook-denoiser-dns64` and `facebook-denoiser-dns48` in
`plan/INVENTORY.json`. That record assigns the **enhancement** profile,
`disposition=sdk-model` and `evidence_status=considered`. The DNS48 row is a
separate sibling task; its work, artifacts, fixtures, metrics and disposition
are not imported, pooled or reused here.

The pinned sources do **not** record an exact upstream revision, checkpoint
name, checkpoint hash, sample rate, channel layout, frame geometry, state,
lookahead, output scaling or content delay. None was inferred. In particular,
the 16 kHz mono 160-sample harness below is **installed v0**, not the candidate
geometry.

## Exact scope

- Work is confined to `docs/task-evidence/facebook-denoiser-dns64/`. Shared
  CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, provider registration, board/handoff files, CI,
  rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  Facebook Denoiser provider, descriptor, installed target or public API/ABI
  change exists. There is no C provider and no adapter source.
- No provider is registered, enabled by default or selected as a default.
  There is no automatic discovery and no fallback.
- No real corpus, checkpoint, weight, graph or vendor file is read. All harness
  stimuli are analytic or seeded synthetic; they are not candidate output.
- No listening, device timing, wall-clock playback, denoising, latency, CPU,
  memory, benchmark or release claim is made.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`, `repository`, `component`). Mutable status, owner, review,
  handoff, priority, claim, history and every other mutable field never enter
  canonical bytes and are never a gate. The mutable full
  `plan/swarm/TASKS.json` is **not hashed** into any artifact.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` assigns the **Enhancement** profile. It requires an
identity/noisy control, an established task-matched baseline, paired SI-SDR and
STOI where permitted clean references exist, clean-speech preservation, peak
and invalid-output checks, an unpaired predictive screen or authorized
listening, and alignment, state, memory and measured content/availability
timing for the exact runtime.

| Profile item | Evidence in `report.json` | Claim limit |
| --- | --- | --- |
| Identity/noisy control | `profile_mapping.identity_noisy_control=blocked_no_candidate_output` | No candidate output |
| Established baseline | `blocked_no_pinned_baseline` | None pinned or run |
| Paired SI-SDR | `blocked_no_permitted_clean_reference` | No permitted cohort |
| Paired STOI | `blocked_no_permitted_clean_reference_or_scorer` | No scorer or cohort |
| Clean-speech preservation | `blocked_no_candidate_output` | Unmeasured |
| Peaks and invalid outputs | `partial_local_harness_rejection_only` | Harness rejection only |
| Unpaired screen or listening | `blocked_no_permitted_cohort` | None |
| Alignment and content delay | `blocked_no_candidate_output` | No delay assumed |
| State, reset, streaming | `blocked_no_candidate_instance` | No instance |
| Runtime availability and memory | `blocked_no_runtime` | No runtime |
| Candidate output | `blocked_source_weights_runtime_license_and_fixture_absent` | None |

A deterministic paired harness control exists only to prove that the fixture and
the float64 SI-SDR scorer are self-consistent on synthetic data. It computes the
identity/noisy SI-SDR, SNR, peaks and `-8/0/+8`-sample shift sensitivity. Its
`candidate_processing` and `qualifies_candidate` flags are both `false`; it is
**not** a Facebook Denoiser result, a denoising comparison or a qualified metric.

Every rejection, missing artifact and nonfinite case is retained with
`qualifies_candidate=false`. Passing the local harness check means only that
this blocker package is self-consistent.

## Caller-supplied asset contract

`audio-sdk/facebook-denoiser-dns64/caller-supplied-asset/0.1` is modelled
metadata only. Required fields are `adapter`, `variant` (`dns64` only for this
task), `source_commit`, `source_sha256`, `model_path`, `model_sha256`,
`weights_sha256`, `runtime` (`pytorch`, `torchscript`, `onnx` or `demucs`),
`runtime_version`, `sample_rate_hz`, `channels`, `frame_samples`, `precision`
(`fp32`, `fp16`, `bf16` or `int8`), `license_id` and
`commercial_use_approved`.

The validator rejects missing/extra fields, the DNS48 sibling variant, unknown
runtimes or precisions, non-hex or wrong-length commits/digests, empty paths,
invalid rates/channels/frames and non-boolean rights flags. Even a structurally
valid manifest is **deferred**: the validator never opens, hashes, loads or
executes the declared path, and a caller declaration is not independent rights
review. The DNS48 variant is deliberately rejected by this task's manifest
schema rather than silently mapped to DNS64.

## Pins

Paths outside `docs/task-evidence/facebook-denoiser-dns64/` are relative to the
`audioml` workspace root unless prefixed `sdk:`; SDK boundary paths are relative
to this SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | Facebook Denoiser DNS48/DNS64 finding, archive, CC-BY-NC and RTF caveat |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component row, enhancement profile and disposition |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Caller-supplied-asset / opt-in adapter sequence |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | Unchanged licensing metadata |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` | Unchanged CI driver |

`SOURCES.sha256` additionally pins every task-local artifact and excludes
itself because a file cannot pin its own bytes. `contract.json` is excluded
from `SOURCES.sha256` because it pins the manifest; it is pinned by the verifier
and by review. `verify.py` fails closed on a missing, stale, malformed,
duplicated or extra pin and on any worktree change outside this directory. It
also checks committed scope against the newest merge-base with `origin/main`
(falling back to `main`), so later merges into `main` never count as this
branch's edits.

## Files

- `contract.json` / `contract.json.license`: machine-readable DEFER contract.
- `reference.py`: stdlib-only deterministic probes, strict validators,
  fail-closed admission gate, harness controls and canonical report builder.
- `run.py`: regenerates report, sidecar, manifest and contract three times and
  fails if any rebuild differs by one byte.
- `report.json` / `report.json.sha256`: canonical evidence and its digest.
- `SOURCES.sha256`: deterministic manifest of pinned inputs and local files.
- `test_reference.py`: unittest acceptance suite.
- `verify.py`: read-only canonical JSON, pin, board-identity, profile,
  licensing, scope and three-cold-start verifier.
- `*.license`: REUSE SPDX sidecars for generated artifacts.

## Reproduction

```sh
cd docs/task-evidence/facebook-denoiser-dns64
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py --all` repeats three times and fails if report, sidecar, manifest or
contract bytes differ. `verify.py` never writes to this directory: it
regenerates in memory, then builds three isolated scratch copies with symlinks
to the pinned read-only inputs and checks cold-start byte identity there.

## Eight blocked release gates

1. `RG-01` exact archived source revision, tree digest, file count and license
   pin.
2. `RG-02` exact immutable DNS64 checkpoint path, byte count, SHA-256,
   checkpoint terms and lineage.
3. `RG-03` CC-BY-NC-4.0 text plus a written NonCommercial, redistribution,
   product-use, derived-output and attribution decision.
4. `RG-04` isolated hash-pinned Python/PyTorch/demucs runtime, ABI, lock or
   build digest and install/import parity.
5. `RG-05` verified candidate input/output geometry, state, lookahead, output
   scaling, content delay and caller-asset output parity.
6. `RG-06` full Enhancement matrix on a rights-cleared task-matched held-out
   paired cohort: identity/noisy control, established baseline, paired SI-SDR
   and STOI, clean preservation, peaks, invalid outputs, alignment and state.
7. `RG-07` target-runtime pacing, availability, deadline, CPU, memory and
   authorized listening and/or a separately labeled predictive screen.
8. `RG-08` opt-in provider intake, descriptor review, benchmark validation,
   independent exact-head review and release approval.

Missing, rejected, adverse or source-reported evidence never qualifies the
candidate. The exact reopen conditions are recorded on each gate and in
`upstream_blocker.reopen`.

**Reopen condition.** Stage the exact archived upstream revision with tree and
license pins; stage the immutable DNS64 checkpoint with path, byte count and
SHA-256; obtain a written CC-BY-NC-4.0 use and redistribution decision; pin an
isolated runtime; verify the exact geometry and content delay; clear the paired
cohort rights; then reproduce output and run the Enhancement matrix with
independent review. Until then the candidate stays **DEFER**, **incomplete** and
**not qualified**.

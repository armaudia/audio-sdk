<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-DTLN-ONNX — task-local synthetic enhancement evidence

Proposal-only, incomplete and **not qualified** evidence for `DTLN ONNX`
(`component_id=dtln-onnx`). The acceptance profile is **Enhancement**, assigned
by `plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, before `processor_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. Missing evidence never qualifies a
candidate.

This package applies the Enhancement profile to a **stdlib-only deterministic
two-stage scalar-gain envelope proxy** over caller-supplied frozen synthetic
signals at the pinned DTLN stream geometry. It is **not** DTLN source, does not
open, load or execute an ONNX graph, does not contain or load weights, does not
read or write real audio, does not invoke a vendor runtime, does not measure a
device clock, does not conduct listening, does not benchmark the SDK and makes
no release claim. Every sample coordinate is a frozen synthetic index. The
evaluation fixture and any future production callback path are distinct; no
production callback is implemented.

## Exact blocker

The upstream identity is pinned: repository `https://github.com/breizhn/DTLN`
at commit `1de1f15a8b5b7e1c44905618ff2ef70ca8277fbc`, its MIT `LICENSE`
(`Copyright (c) 2020 Nils L. Westhausen`), the ONNX runner and model source, the
runtime lock, and both pretrained ONNX graphs, all by SHA-256 from the external
research checkout. The graphs are **not present in this SDK worktree**; the
adapter lock targets **CPython 3.10 / macOS arm64** with **onnxruntime 1.20.1**,
while the pinned evidence interpreter is **CPython 3.12.16**, where
`onnxruntime` is not importable. In addition, product/redistribution rights and
training-data provenance for the pretrained checkpoints are not cleared; the
MIT license covers the upstream repository snapshot as distributed but is not a
product or redistribution clearance, and no legal review exists. Nothing was
copied, vendored, built, downloaded, installed or redistributed. The four exact
blockers are recorded verbatim in `contract.json:exact_blockers` and
`report.json:exact_blockers`; every release gate stays `blocked`.

Reopen condition: place both hash-pinned graphs in an approved isolated runner,
install and pin a 3.12.16-compatible onnxruntime (or record a new 3.10
environment), clear product/redistribution and training-data rights with a
recorded positive decision, and only then open a graph.

## Boundary

- Installed public v0 geometry is documented only and preserved: 16 kHz, mono,
  `f32`, 160 samples per call, zero integer content delay.
- The reference stream geometry is separate from installed v0: 512-sample
  block, 128-sample hop, 257-bin `rfft`, two graphs and a measured
  three-hop/384-sample stream delay that the caller must compensate.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `descriptor_registry_change=false`,
  `shared_cmakelists_change=false`, `installed_v0_behavior_change=false`,
  `processor_exposure=false`, `ci_change=false`.
- No provider registration, no installed-v0/ABI/registry/default/shared-build
  or CI change, no board or handoff write. Only this task-local directory is
  added.
- Configuration, geometry, shape, missing, invalid, nonfinite, epoch,
  position, lifecycle and caller-supplied-asset rejections fail closed without
  advancing state or opening a graph.

## Enhancement profile application

| Profile case | Evidence here | Status |
|---|---|---|
| Identity + noisy control | `controls.identity`, `controls.named_baseline` | synthetic only |
| Established task-matched baseline | named `noisy_input_no_processing` | synthetic only |
| Paired SI-SDR / STOI | per-condition paired clean references | synthetic only |
| Clean-speech preservation | `controls.clean_speech_preservation` | synthetic only |
| Peaks + invalid outputs | per-condition peaks; `adverse` rejections | synthetic only |
| Unpaired speech screen / listening | none | not applicable, not run |
| Alignment, state, memory, timing | raw vs 384-sample-aligned scores; hop state | partial synthetic |

The scorer is a dependency-free port of non-extended pystoi 0.4.1 and the
zero-mean SI-SDR formula, byte-identical apart from `SCORER_ID` to the merged
`online-multichannel-wpe` scorer and cross-checked against the six inherited
vectors. It is not an oracle, is not the audio-bench scorer and carries no
real-speech or listening claim.

## Caller-supplied asset contract

The package documents and validates, but never executes, the exact two-graph
boundary:

- graph 1 (`mask_estimation_graph`): `pretrained_model/model_1.onnx`,
  1,458,237 bytes;
- graph 2 (`signal_estimation_graph`): `pretrained_model/model_2.onnx`,
  2,510,010 bytes;
- two graph inputs and two graph outputs each, matching the pinned runner's
  magnitude/state and estimated-frame/state hand-off; exact recurrent-state
  shapes are runtime-derived and are not asserted here;
- 16 kHz mono, 512-sample block, 128-sample hop, 384-sample measured delay;
- runtime lock `adapters/dtln-onnx/requirements.lock` (CPython 3.10, macOS
  arm64, onnxruntime 1.20.1, numpy 1.26.4, soundfile 0.13.1).

`validate_asset_request` rejects a missing or extra key, wrong source commit,
wrong rate/block/hop, wrong graph count, wrong role/path/hash/size, unknown
runtime, or a runtime/interpreter mismatch. It reports `blocked_asset_absent`,
`blocked_size_mismatch`, `blocked_hash_mismatch`,
`blocked_runtime_unavailable` or `blocked_interpreter_mismatch` without opening
a graph. In the reported environment the real graphs verify by hash, but the
gate is `blocked_runtime_unavailable` and `inference_executed=false`.

## Synthetic surrogate and conditions

The surrogate splits into two explicit stages: a hop gain estimated from
512-sample buffer energy against a slow noise floor, then gain smoothing and
windowed overlap-add, emitting the documented 384-sample stream delay. It is a
scalar-gain envelope proxy, **not** a 257-bin spectral mask, not an LSTM and not
DTLN. Six frozen conditions (`speech`, `unfamiliar_speech`, `music`, `clipped`,
`tail_partial`, `silence`) each use a deterministic paired clean target and
observed input (fixed LCG seeds). `tail_partial` has 15,323 samples: 119 full
hops plus a final hop with 91 valid and 37 padded samples. `silence` has an
all-zero reference, so SI-SDR and STOI are undefined and the condition is
excluded, not counted as a win. Every non-silence condition records baseline,
aligned-candidate and raw-delayed-candidate scores; no losing result is hidden.

## Controls and adverse cases

- `controls.identity`: exact observed-echo; its zero improvement is trivial by
  construction and labeled as such.
- `controls.named_baseline`: plain noisy input, not a DTLN run.
- `controls.candidate`: aligned surrogate on the speech condition.
- `controls.clean_speech_preservation`: surrogate on the clean target.
- `controls.mismatch`: wrong shape, nonfinite, stale epoch, stale position and
  oversized frames are fed and rejected with unchanged state.
- `adverse`: nine config cases, seven frame cases, both lifecycle closures,
  stale/valid reset, and eight caller-supplied asset cases (absent,
  hash-mismatch, wrong commit, wrong geometry, one graph, duplicate graph,
  unknown key, runtime-unavailable) plus a positive gate-logic control.

## Pinned sources

Paths prefixed `source:` in `SOURCES.sha256` are relative to
`/Users/htsakanyan/workspace/audio/audioml`; other paths are SDK-worktree
relative.

SDK, plan and research inputs:

| Source | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | DTLN task/profile assignment. |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | DTLN row and baseline scope. |
| `research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | DTLN identity and priority. |
| `research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Asset ledger, graph hashes and runtime lock. |
| `research/selected_audio_enhancement_candidates.md` | `0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946` | Selected comparator and pilot scope. |
| `research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | 30-pair pilot values; provenance only. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Source-reported component summary. |
| `adapters/dtln-onnx/adapter.json` | `d048fc48252c47b11598dfd1e881878868676434cc7ab6f2a505e34015d60c69` | Adapter identity and required-local weights. |
| `adapters/dtln-onnx/README.md` | `77853cc7606cd789bd0b65df469f98bfc2b9e082540bed115501bc0b89e91a95` | Documented 512/128 stream and 384-sample compensation. |
| `adapters/dtln-onnx/run.py` | `a12d90df72d1bdafe8d2a204741227ecd7c2ca8d410829e2f2f912256168fdd6` | Adapter stream and asset validation behavior. |
| `adapters/dtln-onnx/requirements.lock` | `1195f7e838fd20dc1fff30b3808324131c9f7acbedf63f9bf4084de78aa6a86c` | CPython 3.10/onnxruntime 1.20.1 runtime lock. |

Upstream DTLN provenance, hash-pinned read-only from the external research
checkout (`data/checkouts/DTLN`, commit
`1de1f15a8b5b7e1c44905618ff2ef70ca8277fbc`); no asset is copied into this
package or the SDK repository. The checkout's `origin` URL and `HEAD` are
checked offline against the pinned repository and commit:

| Source | SHA-256 | Use |
| --- | --- | --- |
| `data/checkouts/DTLN/LICENSE` | `aa95acd8c8a7341bfcdb2823694dcbb27a2a4143e860bb52db1ff0f29c85e5a1` | MIT license text. |
| `data/checkouts/DTLN/README.md` | `1f518d30bc8fbd4cdd0cfa5735630162852a33510ad149fd3204f124d3ad51d2` | Upstream setup, results and delay notes. |
| `data/checkouts/DTLN/DTLN_model.py` | `cb5fc13f9d24ff5b98c65ba0a9f814ed4943048526acf310aebef0d4cdf47d55` | Exact two-model definition. |
| `data/checkouts/DTLN/real_time_processing_onnx.py` | `e15f0fc092f03f372dff34770a9a7d1f4b664337f514bf6f0880c0b87f3a2016` | Exact ONNX stream runner. |
| `data/checkouts/DTLN/convert_weights_to_onnx.py` | `a222ff4207a769d2e9d7c2764b2996d76aeb83e10c4ec93c49ac1a4999e4b97b` | ONNX conversion script. |
| `data/checkouts/DTLN/pretrained_model/model_1.onnx` | `22b91cae3855e5a0620e66a917ca6c82c58db0e842c770f58d86751c5e8d4ae3` | Mask-estimation graph, 1,458,237 bytes. |
| `data/checkouts/DTLN/pretrained_model/model_2.onnx` | `e20c92f9233fccf29cddf86970d0d0161a03aebccc26d6f4d5639c4d5ec2e639` | Signal-estimation graph, 2,510,010 bytes. |

`SOURCES.sha256` enumerates every source, boundary, scorer and task-local
artifact pin. `verify.py` fails closed on a missing, stale, malformed,
duplicated or out-of-scope pin, non-canonical JSON, duplicate keys, non-finite
constants, a stale digest sidecar, uncaught invalid cases, an unpinned
interpreter, a non-blocked asset gate, licensing gaps, unpinned task files, any
worktree change outside this directory, and `git diff --check`.

## Canonical artifacts and local digests

| File | SHA-256 |
| --- | --- |
| `contract.json` | `a498c80cdf8f764af8e102f986e6c39a3e4fa8757cdb2e95495a73214324947b` |
| `report.json` | `db37b4c88bf81bca5e0397dd3fcb5d45ffccf95a217cd1f59e198f2fae562bdf` |
| `report.json.sha256` | `ec0d610033e77fb6363ed537b091f92a197de747fa9d089519cc7e7f3beae74d` |
| `reference.py` | `5727e654190a6c50d07f321e373dbb13db33d51799f432146adabdc785cedd58` |
| `scorer.py` | `962b37ad0abd80c55cc2c99a9bfd63eaa8fb10d12a07bbea1af19ec47742b8aa` |
| `run.py` | `e366081d62129b49b0384b66fd26d4842f20046cb300a35a15f1bd97d40ceff2` |
| `verify.py` | `9f0ebb64fa988ead9d8d4862d1c7539cc8ebebd3c5f6bfc57e6c311c4173ae48` |
| `test_reference.py` | `95e187771e88f24023405be3a70c9052d81a395ca1ea36c4fcb398f26d20a023` |

`report.json` is canonical JSON (`sort_keys`, minimal separators, no
`-0.0`/NaN/Infinity, trailing newline). `report.json.sha256` is regenerated
from those exact bytes. `SOURCES.sha256` is a generated manifest of every
pinned boundary, provenance input, scorer and file in this directory except
itself; the README is pinned there and is therefore not listed above.

## Licensing analysis

- Task files are `Apache-2.0` with REUSE SPDX headers/sidecars.
- Upstream repository source and tracked pretrained model files are under the
  pinned MIT `LICENSE` text at the exact commit; the MIT notice obligation is
  preserved by pinning, not by copying any upstream portion.
- No separate model-card, weights or ONNX-runtime terms were found in the
  pinned snapshot. That absence is recorded, not treated as permission.
- Training-data provenance, product use, redistribution and legal review are
  **not established**. The rights gate stays `blocked`; no upstream asset is
  copied, vendored, built, packaged, downloaded or redistributed.

## Source-reported pilot values (provenance only)

The pinned 30-pair DNS2020 pilot records median SNR gain +6.444 dB, median
SI-SDR gain +6.529 dB, STOI 0.9624 and median RTF 0.0324 for this adapter, with
the measured 384-sample stream lag compensated. The pinned upstream README
separately reports DNS-Challenge real-time rank 8/17, a +0.24 MOS gain over the
challenge baseline and a 32 ms model delay. These are source-reported
conditions; they are not reproduced, pooled, assigned to the synthetic
surrogate or used as thresholds here.

## Files

- `contract.json` — task-local proposal manifest, boundary, asset contract, blockers.
- `reference.py` — deterministic stdlib surrogate, frozen signals, asset gate and report model.
- `scorer.py` — pinned dependency-free SI-SDR / non-extended STOI port.
- `run.py` — byte-identical 3x regeneration of contract, report, sidecar and manifest.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — SHA-256 manifest for pinned provenance, boundaries and task files.
- `test_reference.py` — Python unittest acceptance suite.
- `verify.py` — read-only pins/JSON/reproduction/invalid-case/asset-gate/licensing/scope verifier.
- `*.json.license`, `SOURCES.sha256.license` — REUSE sidecars for generated artifacts.

## Reproduction

Run from this directory with `PYTHONDONTWRITEBYTECODE=1` and the pinned
`/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git -C <worktree> diff --check
```

`run.py` accepts `contract.json`, `report.json`, `sources` and `all`; every
target is regenerated three times and refused if any pass differs. The
canonical report digest is the content of `report.json.sha256`; the manifest
digest is the SHA-256 of `SOURCES.sha256` itself.

## Remaining gates (all blocked)

1. Both hash-pinned graphs present in an approved runner plus a pinned
   3.12.16-compatible runtime (or recorded 3.10 environment).
2. Product/redistribution and training-data rights clearance.
3. Rights-cleared held-out real paired cohort with clean references.
4. Independent listening or a separately labeled authorized predictive screen.
5. Target-runtime content/availability timing, memory and deadline evidence.
6. Opt-in provider intake, descriptor and catalog review.
7. Explicit public default selection.
8. Exact approved DTLN reference parity.

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.

<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-FASTENHANCER-SMALL-REFERENCE — FastEnhancer Small readiness blocker

**Status: `proposal_only_incomplete`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory contains bounded,
deterministic, task-local evidence for the FastEnhancer Small reference row. It
is **not** a FastEnhancer Small implementation: no exact 16 kHz Small graph,
pinned Python runtime, caller output, real corpus, listening result, device
measurement, benchmark or release claim is included. **No result here qualifies
FastEnhancer Small.**

## Exact blocker: the 16 kHz graph and pinned runtime are absent

The MIT-licensed **source checkout is present and verified** at an exact
revision. The exact **16 kHz Small ONNX release graph** and the **pinned Python
inference runtime** are **not present**. Nothing was fabricated, reconstructed
or downloaded.

| Item | Status |
| --- | --- |
| Source checkout | **Present and pinned**: `data/checkouts/FastEnhancer`, `aask1357/fastenhancer` commit `49ab55a57e3a064d94c6412cd0f0a383a55ca0f8`, MIT `LICENSE` SHA-256 `38164c22…`, 85 non-`.git` files, tree digest `30e6a40d…` |
| Exact 16 kHz Small graph | **Absent**: `data/models/fastenhancer/fastenhancer_s.onnx`, 832,813 bytes, SHA-256 `d7c937d6b475dbe89a6e6a69853b685fe62d629f4c96077559c556ac6f8aaa2d`, release `onnx-dns-v1.0.0` |
| Local non-admitted Small ONNX | **Present but not admitted**: `cpp-library/.deps/fastenhancer_s.onnx`, 875,885 bytes, SHA-256 `f04ece2b…`, `wav_in` shape `[1,512]`, consistent with the 48 kHz 512-sample-chunk variant; no equivalence proof |
| Exact 16 kHz Tiny ONNX control | **Present but a different model size**: `cpp-library/.deps/fastenhancer_t_16k.onnx`, 125,233 bytes, SHA-256 `a6466367…`; it matches the Tiny ledger row, not Small |
| Pinned Python runtime | **Absent**: `onnxruntime` is not importable; no CPython 3.10 environment with `onnxruntime 1.20.1`, `numpy 1.26.4`, `soundfile 0.13.1` exists at any fixed probe path |
| Local C++ ONNX Runtime | **Present but not the pinned runtime**: `cpp-library/.deps/onnxruntime-osx-arm64-1.31.1`, version `1.31.1`, commit `41d4d61f…`; never imported, loaded or executed |
| Weight terms | **Unresolved**: MIT covers the source checkout only; the release page does not state separate model terms and the ledger records “not specified separately; retain local only” |
| Caller output / cohort | **Absent**: no approved reference output, frozen input vector, rights-cleared paired cohort or permitted listening result |
| Rights requirement | Written model-weight and training-data terms, third-party notices and an explicit redistribution/product-use decision before any reproduction, adapter or release |

The machine-readable record is `report.json` → `source_probe`, `weights_probe`,
`runtime_probe`, `absence_evidence`, `exact_blockers` and `gates`.
`contract.json` carries the same disposition, geometry, pins and all eight
blocked release gates.

Because the exact graph and runtime are missing, **no result qualifies
FastEnhancer Small**, no provider is registered, and release gate `RG-01` stays
blocked.

## Why the local 48 kHz Small export is not used

A `wav_in` shape of `[1,512]` matches the documented 48 kHz Small 512-sample
chunk, while the evaluated 16 kHz DNS row uses a `[1,256]` `wav_in` with a
512-point FFT and 256-sample hop. The local file is a different export with a
different SHA-256 and byte count, no upstream release identity and no
equivalence evidence. It is hashed and its graph metadata is parsed with a
bounded standard-library protobuf reader, but it is **not loaded into a runtime
and no inference is performed**. Substituting it would change the model variant
and break the task evidence chain.

## Exact scope

- Work is confined to `docs/task-evidence/fastenhancer-small-reference/`.
  Shared CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, board/handoff files, CI, rulesets and `main` are
  untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  FastEnhancer provider is installed or registered.
- The documented reference geometry is separate from installed v0: 16 kHz,
  mono, f32, 256-sample stateful chunk, 512-point FFT, 256-sample compensation,
  identity output length and per-utterance cache reset.
- No request is ever processed as FastEnhancer Small. Valid requests fail
  closed because the exact graph and runtime are absent.
- Missing, invalid, nonfinite and out-of-range manifest cases fail closed with
  no metrics. No missing result qualifies the candidate.
- Board linkage is projected from **stable row identity only** (`id`, `title`,
  `component`, `mode`, `repository`, `depends_on`). Mutable status, owner,
  review, handoff, priority, claim and history never enter canonical bytes and
  are never a gate. The full mutable `plan/swarm/TASKS.json` is **not hashed**
  into any canonical artifact.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not a denoiser:

1. **Strict JSON** with duplicate-key, NaN, Infinity, BOM and root-type
   rejection; canonical compact sorted-key bytes with one trailing LF.
2. **Source verification.** It recomputes the digest over every non-`.git` file
   in the pinned checkout and checks the commit, file count and MIT licence pin.
   It never imports or executes upstream code.
3. **Bounded ONNX metadata probe.** It hashes present local ONNX candidates and
   parses only producer strings and graph input/output shapes. It never loads a
   graph or evaluates a tensor.
4. **Runtime probe.** Import-name and fixed-path checks only; no archive is
   opened, no package is installed and no network is used.
5. **Asset admission.** It validates an exact caller-supplied manifest with
   fail-closed geometry, digest, runtime, rights, path and finiteness checks.
   A structural schema control is labeled non-evidence and never qualifies.
6. **Declared framing arithmetic.** `frame_plan()` reproduces the adapter's
   256-sample call count and zero-pad flush for fixed sample counts. These are
   arithmetic facts about the declared interface, **not measurements**.
7. **Stable board identity** from the linked row only.
8. **Canonical report and contract bytes** with `sort_keys=True`, compact
   separators, `allow_nan=False` and exactly one trailing LF.

It does **not** load a graph, create an ONNX session, implement a network,
score quality, run listening or produce audio.

## Historical measurements are not local results

The following values are historical research evidence, retained with their
original scope and explicitly **not reproduced here**:

| Field | Historical value | Scope and status |
| --- | --- | --- |
| DNS2020 pilot | ΔSI-SDR +8.11 dB, ΔSTOI +0.0324, batch RTF 0.0359 | 30 paired no-reverb clips, exploratory; not a frozen benchmark |
| EARS input-preservation | STOI vs input .7453, SI-SDR 5.704 dB, RTF .03059, RSS 67.4 MB | 743 recordings without clean references; alteration proxy only |
| Native Small 48 kHz | WB-PESQ 2.839, STOI .9428, SI-SDR 15.68 dB, lag 341 samples at 16 kHz | Different native variant on 824 VoiceBank+DEMAND pairs |
| Delay | Adapter declares 256 samples; a native Tiny 16 kHz screen measured 512 | Unresolved contract discrepancy; not measured here |

These values never enter `report.json` as floats or as candidate results. They
are labeled `historical_research_not_reproduced_not_qualified`.

## Enhancement acceptance profile application

`plan/swarm/VERIFICATION.md` assigns the Enhancement profile. With the exact
graph and runtime absent, the profile maps as follows:

| Required element | Local status |
| --- | --- |
| Identity/noisy control and task-matched baseline | `blocked_no_candidate_output` |
| Paired SI-SDR / STOI with permitted clean references | `blocked_no_rights_cleared_cohort` |
| Clean-speech preservation, peaks and invalid outputs | `blocked_no_output_samples` |
| Unpaired predictive screen or authorized listening | `blocked_no_screen_or_listening` |
| Alignment, state and memory | `blocked_not_measured` |
| Content/availability timing for the exact runtime | `blocked_not_measured` |

## Eight blocked release gates

| Gate | Blocked reason |
| --- | --- |
| `RG-01` exact 16 kHz Small graph and source pin | The exact 832,813-byte graph is absent; only a non-matching 48 kHz export exists. |
| `RG-02` pinned Python runtime admission | `onnxruntime 1.20.1` and the CPython 3.10 lock environment are absent. |
| `RG-03` artefact rights and training data | Model-weight terms, training provenance and redistribution decisions are unresolved. |
| `RG-04` exact reference parity | No approved output, frozen input vector or digest exists. |
| `RG-05` rights-cleared paired cohort | No frozen paired clean/noisy cohort with clean references exists. |
| `RG-06` independent scoring and permitted listening | No independent SI-SDR/STOI result, preservation check or authorized listening exists. |
| `RG-07` target-runtime timing, memory and streaming parity | No paced workload, resource or content/availability measurement exists. |
| `RG-08` opt-in provider intake and release | No adapter, descriptor, public-surface decision or independent review exists. |

## Reproduction and verification

From this directory, with the pinned interpreter and no bytecode:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
```

`run.py --all` regenerates the canonical report, sidecar and source manifest
three times in one process and requires byte-identical output. `verify.py`
additionally runs three cold-start regenerations in fresh scratch trees, checks
strict JSON, exact pins, stable board identity, licensing, task-local git scope
and blocker semantics.

## Non-claims

No exact FastEnhancer Small 16 kHz graph, weight bytes, model output, runtime,
corpus, consent, listening panel, quality score, latency, callback, benchmark or
release claim is made. No installed v0, public API, C ABI, descriptor, registry,
default, shared build, CI, board or handoff change is made. Historical values
remain labeled with their original scope.

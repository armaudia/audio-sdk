<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-FULLSUBNET — FullSubNet+ readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local evidence for the
FullSubNet+ feasibility row. It is **not** a FullSubNet+ implementation. No
upstream source checkout, `best_model.tar` checkpoint, weight fragment, runtime,
corpus, noisy/clean pair, enhanced waveform, listening result, device
measurement, benchmark or release claim is present. **No result here qualifies
FullSubNet+.**

The structured inventory marks `fullsubnet` as `evidence_status=blocked` with the
**Enhancement** acceptance profile (`verification_profile: enhancement`,
`plan/INVENTORY.json`). The row asks for runnable source, exact assets,
permitted scope, task geometry and matched evidence before a
caller-supplied-asset reference and an opt-in adapter; the exact checkpoint terms
and bytes are not obtainable under the current evidence.

## Exact external blocker

The pinned records establish the official source repository and code revision,
the 16 kHz inference geometry, and a link to one pretrained checkpoint:

- **Source:** `RookieJunChen/FullSubNet-plus` at commit
  `b115416d6e2a983c3724fc77d0cdc3d8896a2855`, reported as Apache-2.0 code for
  the ICASSP 2022 FullSubNet+ implementation. The revision is a pinned
  reference from the workspace adapter and readiness audit, not a local
  checkout; no license text bytes or per-file SHA-256 were verified here.
- **Checkpoint:** `best_model.tar`, linked only from Google Drive file ID
  `1UJSt1G0P_aXry-u79LLU_l9tCnNa2u7C`. Neither the repository nor the Drive
  page states separate weight terms, an immutable artifact revision, a byte
  size or a SHA-256. The file was **not downloaded**.
- **Geometry:** 16 kHz mono, `n_fft=512`, `win_length=512`, `hop_length=256`,
  257 frequency bins, complex CRM mask, look-ahead 2 frames.
- **Runtime:** the upstream sample environment is legacy (PyTorch 1.7.1 /
  torchaudio 0.7 / librosa 0.8); CPU support is stated upstream but no local
  lock, host profile or measurement exists.

The repository's Apache-2.0 code license is **not** evidence for the separately
hosted weights. A checkpoint whose terms, immutable identity and digest cannot
be verified cannot be staged, loaded or scored. Nothing was fabricated,
reconstructed, mirrored, converted or substituted; no other FullSubNet variant
is admissible as a substitute.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout | `RookieJunChen/FullSubNet-plus` at immutable 40-hex commit `b115416`, with the reviewed Apache-2.0 license text bytes and a per-file SHA-256 manifest from a reviewable local tree |
| Checkpoint bundle | The official `best_model.tar` at an immutable artifact identity, with exact byte size and SHA-256, the `config/inference.toml`, and separately reviewed weight terms or a model card |
| Runtime | A locked, reproducible isolated runtime with exact interpreter and package versions, an offline load path, a lock SHA-256 and a recorded host profile |
| Rights | Reviewed weight terms, training-data provenance, corpus rights, clean-reference permission, output use and redistribution |
| Cohort | A frozen, rights-cleared paired noisy/clean 16 kHz cohort with exact durations, language and speaker groups, held-out splits, and identity/noisy, task-matched-baseline, clean-preservation, peak/invalid and unpaired controls |
| Enhancement results | Independent paired SI-SDR and STOI, clean-speech preservation, peaks and invalid (including nonfinite) outputs, authorized listening or a labeled predictive screen, alignment, content delay, chunk/state behavior, memory, availability timing, resources and uncertainty |

The machine-readable record is `report.json` → `source_probe`, `weights_probe`,
`runtime_probe`, `absence_evidence`, `required_artifacts`, `exact_blockers`,
`enhancement_profile` and `gates`. `contract.json` carries the same disposition,
pins, geometry and all eight blocked release gates.

### Reopen condition

Obtain from the authors or a clearly authorized official distribution:
(1) applicable weight license/terms, (2) a versioned or otherwise immutable
artifact identity, (3) the exact byte size and SHA-256, and (4) confirmation that
the published `best_model.tar` is the intended inference checkpoint for the
pinned config. Then stage the pinned source and checkpoint, keep weights-only
deserialization, run a bounded CPU smoke in an isolated worker, and only proceed
to the paired cohort plus clean diagnostics if model load, output validity, time
and memory fit a declared bound.

## What this package verifies

1. **Absence evidence.** Fixed workspace/worktree probes and fixed home-cache
   probes are checked; no recursive walk is performed. All are absent.
   `reference.build_report()` and `verify.py` fail if any probe later appears,
   so a stale "absent" claim cannot be shipped.
2. **Stable pins.** The candidate census, candidate matrix, FullSubNet+
   readiness re-audit, selected-candidate record, workspace adapter, reviewed
   planning records and the SDK boundary files are pinned by SHA-256. These are
   read-only provenance inputs, not model evidence.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository` and `depends_on` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes and never
   gate this package.
4. **Fail-closed admission schema.** A task-local Enhancement cohort manifest
   has a strict schema: unknown/missing fields, duplicate JSON keys, nonfinite
   values, floats, unsafe paths, duplicate or unsorted entries, unresolved
   tokens, non-integral or out-of-range integers, unsupported sample rates,
   non-offline runtimes, unconsented pairs, false rights and any geometry
   mismatch against `512/512/256`, 16 kHz, complex CRM and look-ahead 2 are
   rejected. One synthetic structural control is accepted to prove the
   validator is not blanket-rejecting; it is labelled
   `synthetic_schema_control` and `qualifies=false`.
5. **Enhancement profile accounting.** Identity/noisy control, task-matched
   baseline, paired SI-SDR and STOI, clean-speech preservation, peaks and
   invalid outputs, authorized listening, alignment, content delay, state,
   memory, availability timing and the independent rights gates are each
   recorded as **blocked**.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow and `.gitattributes` are
   pinned by SHA-256 and verified unchanged. Installed v0 remains 16 kHz, mono,
   float32, 160 samples per frame. No FullSubNet+ provider is installed or
   registered; no descriptor, default, ABI, shared build, CI, board or handoff
   change is made.

## Enhancement profile application

| Enhancement requirement | Status here | Evidence |
| --- | --- | --- |
| Identity/noisy control and established task-matched baseline | blocked | No control or DeepFilterNet3/FastEnhancer baseline output exists on the exact assets. |
| Paired SI-SDR and STOI where permitted clean references exist | blocked | No rights-cleared paired cohort and no score. |
| Clean-speech preservation | blocked | No clean-input preservation measurement. |
| Peaks and invalid outputs | blocked | No peak, clipping, nonfinite or invalid-value record; upstream 16-bit peak normalization is not copied here. |
| Unpaired predictive screen or authorized listening | blocked | No screen, listening protocol or panel. |
| Alignment and content delay | blocked | No impulse, speech or content-delay measurement; look-ahead 2 is configuration only. |
| State, memory and measured content/availability timing | blocked | No chunk/state, memory or availability-timing record on the runtime. |
| Independent corpus, clean-reference and output-use gates | blocked | Asset, corpus and output terms are unresolved. |

## Historical and peer boundary

The pinned census, matrix and readiness records contain a verified source and
config reference, a blocked Google Drive checkpoint link and source-reported
context only. There is no local FullSubNet+ run, output, metric, corpus or
runtime. No value is inferred from merged sibling evidence packages:

- `fastenhancer-base-reference` is a named comparison baseline with its own
  absent assets; it supplies no FullSubNet+ weight, runtime or score.
- `gtcrn-dns3-offline`, `dtln-onnx` and `cmgan` are adjacent enhancement
  blockers with different models and only synthetic mechanism evidence.
- `cof-denoising-checkpoints` is a merged unverified-checkpoint blocker; its
  source supplies the merge-base scope-gate pattern only.
- `survey-cln-01` is a merged coverage survey and supplies no measured result.

FullSubNet-original and Spiking-FullSubNet are distinct candidates with their
own tasks and are not substitutes for this row.

## Admission contract (task-local; not an SDK, FullSubNet+ or Enhancement contract)

The schema is `audio-sdk/fullsubnet-enhancement-cohort/0.1`. Unknown and missing
fields, duplicate JSON keys, `NaN`/`Infinity`, floats, unsafe paths, duplicate or
unsorted entries, unresolved tokens, non-integral or out-of-range integers,
unsupported sample rates, non-offline runtimes, unconsented pairs, any false
right and any deviation from the pinned 16 kHz `512/512/256` complex-CRM
geometry with 2-frame look-ahead are rejected. The one accepted control is
synthetic and never qualifies. Admission never reads audio, loads weights or
invokes a model.

## Remaining gates (all blocked)

1. Exact licensed source and checkpoint pinned.
2. Rights-cleared frozen paired cohort and clean references.
3. Identity/noisy control, task-matched baseline and uncertainty.
4. Pinned source, checkpoint, runtime and per-weight terms.
5. Alignment, content delay, state, memory, availability timing and numerical behavior.
6. Authorized listening or labeled predictive screen.
7. Opt-in provider intake and independent review.
8. Release approval.

## Canonical artifacts and local digests

| File | SHA-256 |
| --- | --- |
| `contract.json` | `0a9ecd3571ee95d1f4431d11f539764b2fa7489bfd35ac6834d2710659226c70` |
| `report.json` | `b7622dfc42a67a9a4e0e275245ffa09b717d895f5d3b4c28026af4c993461a41` |
| `report.json.sha256` | `a6a5bc0ff096cf99cd96a57706f3feabd556d8017e57f5014e933a5f999c531c` |
| `reference.py` | `30e7c7d45f537b7da49d3ca656c5184806b1717ffbabba8b5179ee716c0015f9` |
| `run.py` | `b272c22bb95a6d32865350ebcdf56ac2f7305665070b6fd911715d39ec873cbe` |
| `verify.py` | `1327991b7f2e5054d3f5dc8cb2499e8736b59c77871818aacc5570c1c3f44926` |
| `test_reference.py` | `28d711891441bddec7aa22d22064e8632ce4046b050b0370dfc057a14937575d` |

## Reproduction

Run from this directory with the pinned interpreter and bytecode disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py
```

`run.py` writes `contract.json`, canonical `report.json`,
`report.json.sha256`, refreshes this digest table and writes `SOURCES.sha256`
three times, requiring all three passes to be byte-identical. `verify.py`
re-runs three independent cold-start regenerations in scratch trees and fails on
any pin drift, stale README digest, out-of-scope change, missing sidecar,
missing SPDX header or absent blocker. It also gates this branch's merge-base
diff so committed out-of-scope files cannot pass.

Repository-level checks used for this handoff:

```sh
python3.12 scripts/ci.py --output build/ci-fullsubnet
python3 -m reuse lint
git diff --check
```

## Licensing

This package is Apache-2.0; see `LICENSES.md` and the `.license` sidecars. It
contains only text, JSON and Python source. It contains no `.wav`, `.flac`,
`.pt`, `.pth`, `.tar`, `.onnx`, `.safetensors`, binary library, compiled object,
upstream source copy, license text copy or model weight.

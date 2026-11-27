<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-X-VC — blocker evidence

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision `DEFER`; qualification `not_qualified`.** This directory is bounded, deterministic, task-local evidence for the X-VC row. It is **not** the X-VC pipeline: no X-VC checkpoint, GLM-4-Voice-Tokenizer weight, ERes2Net weight, runtime, converted audio, real corpus read, listening result, device measurement, benchmark or release claim is included. **No result here qualifies the candidate.**

## Exact blocker

| Item | Status |
| --- | --- |
| X-VC source checkout | Present and pinned: `research/voice-conversion-eval-20261101/repos/x-vc`, `Jerrister/X-VC` commit `49df8c591eafc48b096e466d96f9839f9c0dd739`, MIT, 82 tracked files |
| GLM-4-Voice-Tokenizer | Absent: `zai-org/glm-4-voice-tokenizer`; no SHA-256 or byte count exists locally |
| ERes2Net speaker encoder | Absent: `iic/speech_eres2net_sv_en_voxceleb_16k`; no SHA-256 or byte count exists locally |
| X-VC checkpoint | Absent: `chenxie95/X-VC` `ckpts/xvc.pt`; config declares `checkpoint: null`; no SHA-256 or byte count exists locally |
| Required runtime | Absent/unpinned: declared versions exist, but no hash-pinned environment/lock/wheel digest and required modules are not importable |
| Checkpoint/runtime memory | Not measured: ledger reports 5.01 GB checkpoint vs 8 GB host budget; joint checkpoint+runtime memory not measured here |
| Rights / consent | Unresolved: source MIT only; weight/model-card terms, source-speaker/target-voice consent, reference availability and output-use scope unreviewed |
| Historical X-VC run | None: ledger says “Not downloaded” and “Blocked” |

Linked ledger row (`research/voice-conversion-eval-20261101/README.md:20`): X-VC blocked; official HF checkpoint 5.01 GB and pipeline also requires GLM-4-Voice and ERes2Net encoders; checkpoint alone exceeds this host's 8 GB memory budget. This is provenance text, not local availability evidence.

## Exact dependency resolution

The request contract accepts exactly the ordered dependency list `["glm-4-voice-tokenizer","eres2net"]`. Missing, extra, reordered, duplicated, non-string or unknown dependency is rejected before any candidate call. A valid request still fails closed with `SOURCE_WEIGHTS_RUNTIME_ABSENT`. There is no partial-dependency, placeholder or surrogate path.

| Dependency | Pinned locator | Local status |
| --- | --- | --- |
| GLM-4-Voice-Tokenizer | `zai-org/glm-4-voice-tokenizer` (`configs/xvc.yaml`) | `blocked_weights_absent` |
| ERes2Net | `pretrained/speech_eres2net_sv_en_voxceleb_16k` (`configs/xvc.yaml`) | `blocked_weights_absent` |
| X-VC checkpoint | `ckpts/xvc.pt` (`scripts/infer_single.sh`) | `blocked_weights_absent` |

## Pinned declared geometry (arithmetic only, not measured)

Config/script declare 16 kHz input, `n_fft=1024`, `win_length=640`, `hop_length=320`, `num_mels=128`, `latent_hop_length=1280`, encoder rates `[2,4,5,8]`, semantic width 1280, speaker embedding 192, chunk 2400 samples / 150 ms, `current=0` offline default, `future=100`, `smooth=20`, `checkpoint: null`. Requirements pin torch/torchaudio 2.5.1, transformers 4.44.1, numpy 1.26.4, soundfile 0.12.1, librosa 0.10.2, scipy 1.12.0. `geometry.measured_here=false`, `geometry.candidate_output=false`.

## Scope / boundaries

- Work confined to `docs/task-evidence/x-vc/`. Shared CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0 behavior, board/handoff, CI, rulesets and `main` untouched.
- Installed v0 remains 16 kHz, mono, float32, 160 samples/frame. No provider installed/registered/enabled/default.
- No C provider, installed target or public API/ABI change.
- No request processed as X-VC; valid requests fail closed with `SOURCE_WEIGHTS_RUNTIME_ABSENT`.
- Missing, invalid, nonfinite, out-of-range requests fail closed with no metrics. No missing result qualifies.
- Board linkage uses stable row identity only (`task_id,title,mode,repository,component`). Mutable board fields never enter canonical bytes/gates. Mutable full `plan/swarm/TASKS.json` is not hashed.

## Release gates (all blocked)

RG-01 exact source+dependency weight pin; RG-02 license/rights/asset review; RG-03 exact runtime/build/install parity; RG-04 dependency geometry/alignment/drain; RG-05 rights-qualified cohort/content/identity/naturalness; RG-06 content preservation/adverse/nonfinite; RG-07 memory/timing/callback/resources; RG-08 provider intake/public surface/review/release. See `report.json`/`contract.json`.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 verify.py
```

`verify.py` is read-only, checks strict JSON/canonical bytes/exact pins/blocker semantics/stable linked-row identity/licensing/prohibited artifacts, enforces task-local newest-merge-base branch-diff scope (`origin/main`→`main`, fail closed `scope_base_unavailable`, emits `base_out_of_scope_change`), and runs three cold-start byte-identical regenerations.

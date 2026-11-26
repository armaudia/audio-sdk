<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-F5-TTS — F5-TTS readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory contains bounded,
deterministic, task-local evidence for the F5-TTS feasibility row. It is **not**
an F5-TTS implementation. No upstream source checkout, pretrained checkpoint,
config, vocab/tokenizer asset, runtime, consent record, reference voice,
generated waveform, listening result, device measurement, benchmark or release
claim is present. **No result here qualifies F5-TTS.**

The structured inventory marks `f5-tts` as `evidence_status=considered` with
the **Voice** acceptance profile (`verification_profile: voice`,
`plan/INVENTORY.json`). The row's plan note asks for consented conditioning,
verified weights, and first-audio/full-response measurement; none of those
prerequisites exists locally.

## Exact external blocker

The exact **SWivid/F5-TTS source**, the **caller-selected pretrained checkpoint
bundle**, and the **isolated runtime** are all absent. Nothing was fabricated,
reconstructed, mirrored, downloaded or substituted. No revision, file name,
byte count or SHA-256 is asserted as verified.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout | `SWivid/F5-TTS` at an immutable 40-hex commit, with the reviewed upstream license text and a per-file SHA-256 manifest from a reviewable tree |
| Checkpoint bundle | The caller-selected F5-TTS checkpoint (for example `F5TTS_v1_Base`) at an immutable 40-hex Hugging Face revision, including every weight, config, vocab/tokenizer asset, model card and terms file, with byte count and SHA-256 per file |
| Runtime | A locked, reproducible isolated Python runtime with exact interpreter and package versions (including `torch`), a lock SHA-256, an offline load path and a recorded host profile |
| Rights | Reviewed weight and model-card terms, training-data provenance, explicit reference-voice consent, reference availability and output-use approval |
| Cohort | A frozen, rights-cleared text and reference-voice cohort with manual transcripts, language/speaker groups, exact target conditions, held-out splits and fixed-voice, mismatched-reference, ignore-reference and content-preservation controls |
| Voice results | Independent content-preservation, identity/similarity, naturalness, listening, alignment, first-output/tail, nonfinite/peak, device-timing, resource and uncertainty results on the exact pinned bundle |

The machine-readable record is `report.json` → `source_probe`,
`weights_probe`, `runtime_probe`, `absence_evidence`, `required_artifacts`,
`exact_blockers`, `voice_profile` and `gates`. `contract.json` carries the same
disposition, pins, geometry and all eight blocked release gates.

## What this package verifies

1. **Absence evidence.** Fixed workspace/worktree probes and fixed home-cache
   probes are checked; no recursive walk is performed. All are absent.
   `reference.build_report()` and `verify.py` fail if any probe later appears,
   so a stale "absent" claim cannot be shipped.
2. **Stable pins.** Reviewed planning records, the category registry, the
   category survey source list, the voice-conversion research README, the
   candidate matrix and the SDK boundary files are pinned by SHA-256. These are
   read-only provenance inputs, not model evidence.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository` and `depends_on` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes and never
   gate this package.
4. **Fail-closed admission schema.** A task-local Voice cohort manifest has a
   strict schema. Missing, invalid, duplicate, nonfinite, aliased, unordered,
   out-of-range, non-integral, unconsented or unresolved cases are rejected
   before any state change. One synthetic structural control is accepted to
   prove the validator is not blanket-rejecting; it is labelled
   `synthetic_schema_control` and `qualifies=false`.
5. **Voice profile accounting.** Permitted inputs/targets, language/speaker
   groups, text/semantic preservation, identity/similarity, naturalness,
   alignment, first-output/tail, exact target condition and independent
   consent/reference/output-use gates are each recorded as **blocked**.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow and `.gitattributes` are
   pinned by SHA-256 and verified unchanged. Installed v0 remains 16 kHz, mono,
   float32, 160 samples per frame. No F5-TTS provider is installed or
   registered; no descriptor, default, ABI, shared build, CI, board or handoff
   change is made.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Freeze permitted input and target references, task and language/speaker groups | blocked | No source, checkpoint, consent record, reference voice or group definition. |
| Preserve text and semantic content | blocked | No manual transcript, semantic adjudication or reproduced content result. |
| Identity/similarity as a separate outcome | blocked | No reference-voice similarity score, independent encoder or human rating. |
| Naturalness as a separate outcome | blocked | No naturalness rating or blinded listening panel. |
| Record alignment | blocked | No word, phoneme, onset or reference-content alignment. |
| Record first-output/tail timing | blocked | No pinned runtime or causal output path. |
| Record the exact target condition | blocked | No reference-voice specification, reference-text policy or cleared condition. |
| Consent, reference availability and output use as independent gates | blocked | Weight terms, training data, consent, availability and output use are unresolved. |

## Historical and peer boundary

The pinned read-only records contain only an F5-TTS **source lead**. There is no
local F5-TTS run, output, metric, reference voice or runtime. No value is
inferred from the merged sibling TTS/vocoder evidence packages:

- `chatterbox-nano` and `cosyvoice-2-0-5b` are adjacent TTS blockers with
  different models, absent or removed weights, and no inherited consent,
  identity, naturalness or device timing.
- `kokoro-82m` is a fixed-voice text-only control, not reference-conditioned
  cloning.
- `neutts-nano-q4` is a gated checkpoint lead with no authenticated access or
  inference.
- `phase-vocoder-baseline` is a vocoder component; it does not generate
  reference-conditioned speech.
- `survey-trn-05` records F5-TTS as considered only and supplies no measured
  result.

## Admission contract (task-local; not an SDK, F5-TTS or Voice contract)

The schema is `audio-sdk/f5-tts-voice-cohort/0.1`. Unknown and missing fields,
duplicate JSON keys, `NaN`/`Infinity`, floats, unsafe paths, duplicate or
unsorted entries, unresolved tokens, non-integral or out-of-range integers,
non-offline runtimes, unconsented references and any false right are rejected.
The one accepted control is synthetic and never qualifies. Admission never
reads audio, loads weights or invokes a model.

## Reproduction

Run from this directory with bytecode disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` writes `contract.json`, canonical `report.json`,
`report.json.sha256` and `SOURCES.sha256` three times and requires all three
cold writes to be byte-identical. `verify.py` re-runs three independent
cold-start regenerations in scratch trees and fails on any pin drift, out-of-
scope change, missing sidecar, missing SPDX header or absent blocker.

Scope verification compares the branch against the newest merge-base between
`HEAD` and `origin/main` (falling back to `main`), not a fixed historical
commit. Commits merged into `main` after this task therefore never count as
this branch's out-of-scope edits. Any changed path outside
`docs/task-evidence/f5-tts/` still fails as `base_out_of_scope_change`, and an
unresolvable base ref fails closed as `scope_base_unavailable`. Uncommitted and
untracked files are still rejected by the status gate, and `git diff --check`
still covers both the working tree and the index.

## Licensing

This package is Apache-2.0; see `LICENSES.md` and the `.license` sidecars. It
contains only text, JSON and Python source. It contains no `.wav`, `.flac`,
`.pt`, `.pth`, `.onnx`, `.safetensors`, binary library, compiled object,
upstream source copy, license text copy or model weight.

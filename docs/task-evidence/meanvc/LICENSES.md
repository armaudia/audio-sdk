# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text artefacts and `.license` sidecars for the JSON files and manifests).

## MeanVC upstream

The exact upstream source checkout is present at
`research/voice-conversion-eval-20261101/repos/meanvc`, revision
`fe5286ae205a26ad4eba64395513130bd5974b46`, tree object
`e80e92c70babd6e1c05d9bda8d3a0852828f860e`, 62 tracked files, with an
Apache-2.0 `LICENSE` (SHA-256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`). The
checkout is referenced read-only and is not copied, built, imported or
executed. It is a research clone, not a reviewed release archive.

No MeanVC checkpoint, weight fragment, embedding, encoder, vocoder config,
runtime wheel, lockfile or surrogate is included. The upstream
`download_ckpt.py` expects `model_200ms.safetensors`, `meanvc_200ms.pt`,
`fastu2++.pt` and `vocos.pt` from the `ASLP-lab/MeanVC` model repository, and
the README additionally requires `wavlm_large_finetune.pth` manually from
Google Drive. None of these files, digests or byte counts is present or
invented in this package.

## Weights, runtime and voices

Weight and model-card terms, training-data and corpus rights, source-speaker
consent, target-voice consent, target-reference provenance and output-use terms
are not reviewed or identified. The shared p360 reference discussed in the
linked note has unverified dataset/license provenance and is not used here.
Those rights decisions are release gates `RG-02`, `RG-03` and `RG-04` and
remain **blocked**.

## Historical evidence

There is **no** MeanVC audio, metric, transcript, identity score, naturalness
rating, listening result, timing record or local execution to preserve. The
linked note records MeanVC as `Not downloaded` and `Not pursued`, superseded by
MeanVC2. A separate MeanVC2 sibling run exists in research; it is a different
model with different assets, cohorts and metrics and is not reused.

## Read-only references

The following workspace and worktree artefacts are referenced by path and
SHA-256 only. They are not copied into this package, not modified, and their
numbers are never reused as MeanVC evidence:

- `audio-benchmark-platform/plan/INVENTORY.json` — the exact `meanvc` row.
- `audio-benchmark-platform/plan/swarm/VERIFICATION.md` — Voice profile.
- `audio-benchmark-platform/plan/audio-sdk/README.md` — SDK delivery boundary.
- `research/voice-conversion-eval-20261101/README.md` — the exact evidence row.
- The pinned `research/voice-conversion-eval-20261101/repos/meanvc` checkout —
  source identity only.
- Merged sibling packages `dualvc-3`, `seed-vc-xls-r-300m-content-encoder`,
  `chatterbox-vc`, `llvc`, `survey-trn-04` and `vocos` — boundary and pattern
  references only. Their assets, cohorts, metrics and dispositions are
  separate.

The shared mutable board `plan/swarm/TASKS.json` is read only through the five
stable linked-row fields (`task_id`, `title`, `mode`, `repository`,
`component`). Its bytes are never hashed or pinned.

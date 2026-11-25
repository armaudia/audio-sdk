<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# License and asset notes — SDK-RT-SEMAMBA-KD1

## Task-local files

All files in `docs/task-evidence/rt-semamba-kd1/` are original task-local work
and are Apache-2.0. The `docs/**` aggregate annotation in the repository
`REUSE.toml` covers them; `.license` sidecars are provided for generated JSON
and text artifacts for readers outside the REUSE aggregate.

## Upstream RT-SEMamba

- Repository: `https://github.com/RoyChao19477/RT-SEMamba`
- Pinned revision: `0c9e8c7c42caadd7badb6cc145c8af93f760863c`
- Declared license: **MIT**. `LICENSE` SHA-256
  `04b1d017b906f5d0c6815e60cadeabb1a3f5b4fb743c1b77343841fd735eb5e8`.
- Paper: `RT-SEMamba: Real-Time Speech Enhancement Mamba via Progressive
  Knowledge Distillation`, Interspeech 2026, `https://arxiv.org/abs/2608.12099`.
- The KD1 student checkpoint `ckpts/g_00766000.pth` (SHA-256
  `7d76e2c5f322cc0dd58abd0b9b371890b29c3710d7833cdfebb46a823961f5cc`,
  4,235,024 bytes) and the KD1 config `recipes/KD1/KD1.yaml` (SHA-256
  `2db65c33e66108d7616d47ca509a3dc46983980cae63a216d1ccb98daf0ee222`) are
  present only in the external research checkout
  `data/checkouts/RT-SEMamba/` at the pinned revision.
- The MIT notice obligations apply if the source, checkpoint or a derived
  binary is redistributed. This package copies no upstream source, checkpoint,
  config, Mamba package or runtime.

## Rights and provenance limits

- The research ledger records the checkpoint as distributed inside the
  MIT-licensed official repository. That is a repository-level declaration, not
  an independently reviewed artifact-specific redistribution or product-use
  grant.
- Upstream reports **VCTK-DEMAND / VoiceBank-DEMAND** as both training and
  evaluation data. The dataset's terms, consent basis and redistribution scope
  are not established here, and the DNS2020 crop screen is a cross-corpus
  check, not a training-matched evaluation.
- No legal review exists.
- Consequently checkpoint redistribution/product-use clearance, runtime
  redistribution clearance, product-use clearance, training-data provenance
  and legal review are all recorded as **false**.

## Runtime

The pinned research adapter runs CPU-only through PyTorch (`>= 2.2`) and the
vendored pure-PyTorch Mamba fallback in
`data/checkouts/RT-SEMamba/mamba_install_mps/`. Neither PyTorch nor the Mamba
package is installed in this SDK worktree, imported, built or executed by this
package.

## Synthetic stimuli

The voiced target, the deterministic PCG64 noise, the three SNR mixtures,
clean-only, noise-only and silence controls and the impulse probe are generated
deterministically by `reference.py`. They are not recorded speech, not a
corpus, not a room capture and not a source-reported RT-SEMamba output.

## Separation from other RT-SEMamba research

The pinned research reports
(`research/voice-enhancement-20261101/agent-semamba-eval/`,
`research/voice-enhancement-20261101/agent-semamba-result-audit/`) and the
research-workspace adapter (`adapters/rt-semamba/`) are external provenance
only. They were not executed, imported, pooled or reinterpreted here.

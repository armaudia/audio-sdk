<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-VOCOS-VOCODER — license and rights boundary

This task-local evidence package contains no Vocos source checkout, no
checkpoint/weights, no runtime lock, no feature cohort, no generated waveform,
and no vendor output. It records only pinned provenance and absence evidence.

## Observed provenance (not admitted)

| Artifact | Observed location | License/terms | Status |
| --- | --- | --- | --- |
| Modified Vocos-derived source copy vendored in MeanVC2 | `research/voice-conversion-eval-20261101/repos/meanvc/vocos/` | MeanVC2 root Apache-2.0; no separate Vocos LICENSE/NOTICE in vendored dir | present, not admitted as exact upstream |
| MeanVC2 repository root | `research/voice-conversion-eval-20261101/repos/meanvc/` | Apache-2.0 (`LICENSE` pinned) | present |
| Historical MeanVC2-bundled `vocos.pt` JIT decoder | removed after historical synthetic benchmark | unknown / not reviewed | absent |
| Exact upstream `gemelo-ai/vocos` source | absent | upstream MIT license/notice not present locally | absent |

## Rights gates (all blocked)

- **Source provenance**: exact upstream Vocos revision, MIT license, copyright
  notice, and complete notice bundle are not present. The vendored modified copy
  cannot be treated as exact upstream admission.
- **Weights/model terms**: no immutable checkpoint/weight identity, digest,
  model card, or reviewed redistribution/commercial/output terms.
- **Runtime terms**: no pinned Torch/JIT runtime lock or install digest.
- **Input/feature rights**: no rights-cleared feature cohort, consent,
  reference availability, or output-use clearance.
- **Output use/listening**: no generated outputs, listening, or human ratings.

No license text is vendored by this package. Missing rights/evidence never
qualifies the candidate.

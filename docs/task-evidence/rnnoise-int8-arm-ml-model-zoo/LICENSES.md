<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the JSON and digest
files). It adds no provider, model, runtime, corpus or license grant.

## Upstream Renesas/Arm material

No Renesas RNNoise reference checkout or Arm ML Zoo source copy is present. The
census links the Renesas RNNoise directory in `ruhmi-model-zoo` and reports that
weights are attributed to Apache-2.0 Arm ML Zoo, but it records no immutable
revision, license text, notice, file list or per-file digest. No upstream source
file, feature extractor, export script, model card or terms file is copied into
this package. The source checkout, exact revision and reviewed license identity
remain open blockers. A reported weight attribution is not a verified grant for
a specific commit or exported C/TFLite artifact.

## INT8 model artifact

No quantized RNNoise model file, tensor schema, quantization parameters, byte
count or SHA-256 is present. The pinned asset register contains only a separate
float `RNNoise-Xiph-default` entry. No model bytes are downloaded, vendored,
mirrored, reconstructed or substituted, and no checkpoint-specific terms are
claimed.

## Evidence inputs and peer paths

Read-only source and boundary inputs are pinned by SHA-256 in `SOURCES.sha256`
and the README digest tables. They are not copied into this package. The
installed float RNNoise v0.2 evidence, the RNNoise speech-probability evidence
and the Xiph RNNoise asset entry remain separate with their own provenance;
nothing from them is inherited as an INT8 Arm result or license clearance.

## Scope

This package contains only deterministic text, JSON and Python source under
`docs/task-evidence/rnnoise-int8-arm-ml-model-zoo/`. It contains no model,
audio, recording, corpus, binary library, compiled object, upstream license
text or other vendored artifact.

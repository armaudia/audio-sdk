<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the JSON files).

## Upstream MarbleNet source

No NVIDIA NeMo source checkout is present in this workspace. The official
source lead is `https://github.com/NVIDIA/NeMo`, but no commit, license
identifier, license text, file list or per-file digest has been admitted or
verified. No upstream source file, model code, feature extractor, test audio or
license text is copied into this package. The source checkout, its commit and
its license remain an exact open blocker.

## MarbleNet model weights and NGC terms

No MarbleNet checkpoint, `.nemo` archive, config, vocabulary/feature asset,
model card or terms file is present, and no NGC snapshot is staged. No weight
fragment, converted tensor, embedding or reconstruction is included, and no
weight file is opened, loaded or executed.

The upstream model leads are
`https://catalog.ngc.nvidia.com/orgs/nvidia/models/vad_marblenet` and the NeMo
model list referenced by the pinned research register. The register says the
general, multilingual and telephony variants exist, that NGC terms apply
unless stated otherwise, and that a caller must pin the exact checkpoint,
model card, terms, runtime and weights hash. No model revision, variant file,
per-file byte count or SHA-256 is asserted here. Weight terms, training-data
provenance, account access, redistribution and product-use decisions remain
blockers.

## No third-party material

The only third-party references in this package are URL strings and
source-reported facts quoted from already-merged, read-only planning records.
No third-party code, weight, model card, corpus, audio or license text is
redistributed. The synthetic fixture is generated integer data, not audio and
not model output.

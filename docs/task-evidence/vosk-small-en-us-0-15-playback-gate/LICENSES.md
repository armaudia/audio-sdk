<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE

This task-local evidence package is authored under Apache-2.0. It contains no
Vosk or Kaldi source, model weight, `libvosk` binary, wheel, audio, transcript,
corpus, model card, license text, notice or third-party artifact. It pins
read-only files outside the package by SHA-256 and records provenance only.

## Present but not admitted

- The `vosk-model-small-en-us-0.15` directory (14 files, 70,898,967 bytes,
  tree SHA-256 `93e9c774f1c1d81633024ffd0a6674e0da4d3ef110f70501fe11dcd11e582cf2`)
  exists only inside the mutable, git-ignored
  `cpp-library/pipeline-validation/playback-speed/models/` prototype area.
  Its `README` states `Copyright 2020 Alpha Cephei Inc` and no license text.
  No `LICENSE`, `NOTICE`, `COPYING` or model card is present. The upstream
  official archive identity, model revision and archive digest are not
  recorded.
- The Python `vosk 0.3.44` runtime (`vosk/__init__.py`, `vosk/vosk_cffi.py`,
  `vosk/libvosk.dyld`, 12,533,472 bytes) exists only inside the same mutable
  prototype `.venv`. Its `dist-info` has no `LICENSE` file and `METADATA`
  records `License: UNKNOWN`; the Apache classifier is not a license grant.
  No wheel archive, lockfile or offline-install record is present.
- No source checkout of `alphacep/vosk-api`, Kaldi or bundled third-party code
  is present at an exact 40-hex revision.

Presence and a SHA-256 pin are **not** an admission, license grant, output-use
decision or qualification. Neither artifact is copied, loaded, imported,
executed or redistributed by this package.

## Absent

No rights-cleared corpus, consent record, human-verified word/filler/pause
label set, reviewable transcript, listener panel, device-timing record,
benchmark bundle or release artifact exists here. The prototype corpus is two
macOS `say` TTS clips plus one AMI stitch with no reference transcript; its
construction-time labels are not human-verified gold.

A future qualified run must supply the exact official model archive and its
terms, the exact source revision and Apache-2.0 notice bundle, a pinned wheel or
sdist archive with a lock and offline load proof, the runtime license text, a
consented and rights-cleared cohort with human-verified spans, independent
content scoring, blind listening and target-device timing. See `BLK-01` through
`BLK-06` and `RG-01` through `RG-08` in `contract.json`. Until then this task
remains `DEFER`, `incomplete` and `not_qualified`.

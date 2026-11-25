<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance notes

This package is original task-local evidence under
`docs/task-evidence/rvc-mlx-realtime/` and is licensed `Apache-2.0`
(`SPDX-License-Identifier: Apache-2.0`). It contains no copied upstream source,
no vendored license file, no weights, no model asset, no audio and no binary.

## Upstream source status

- The pinned checkout at
  `research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime`
  (revision `95a69ae2467738c605762bb5e84e8cdcef09d83d`) has **no**
  `LICENSE`, `LICENSE.txt`, `COPYING`, `NOTICE` or license declaration in its
  README, `pyproject.toml` or source headers.
- The original RVC repository at
  `research/voice-conversion-eval-20261101/repos/rvc` carries an MIT `LICENSE`
  (SHA-256 `bec61ed1…`). It is pinned here for contrast only. MIT requires
  retaining the upstream copyright and permission notice; it does not by
  itself grant rights to this fork's modifications.
- The fork documents adaptation from the Acelogic RVC-MLX engine, w-okada /
  Applio streaming math, ContentVec/HuBERT, RMVPE and several optional pitch
  estimators. Their license/notice terms are **not** staged or reviewed here,
  and no conclusion is drawn about compatibility or redistribution.
- No source file from the checkout is copied into this package. The package
  only pins whole-file hashes, reads two source files as text for declared
  default checks, and hashes one upstream test WAV without decoding it.

## Dependency and asset status

`uv.lock` pins mlx / mlx-metal 0.31.2, numpy 1.26.4, faiss-cpu 1.7.4,
scipy 1.17.1, sounddevice 0.5.5, soxr 1.1.0, librosa 0.11.0, soundfile 0.14.0,
PySide6 6.11.1 and pyworld 0.3.5. Those are version pins, not installed
packages, not wheel-hash completeness claims and not license reviews.

No target checkpoint, ContentVec/HuBERT asset, RMVPE asset or FAISS index is
present. No weight, base-asset or output-use terms are reviewed or granted.
The historical p360 target reference used by the research record has
unconfirmed dataset/license provenance; it is not in this package and not used.

## What is intentionally absent

No `LICENSE`/`NOTICE`/`COPYING` file is added for an upstream project, because
this package does not redistribute that project. The absence of a source
license in the checkout is recorded as blocker `BLK-01`; adding a fabricated
or inferred license text would be incorrect.

The original RVC MIT text is not reproduced here. Reviewers should read the
pinned source file directly. Any future intake must stage the complete,
reviewed license/notice bundle for the fork and every adapted lineage before
`RG-01` can clear.

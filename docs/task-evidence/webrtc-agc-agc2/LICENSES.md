<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licences and rights

## This package

All task-local files in `docs/task-evidence/webrtc-agc-agc2/` are
Apache-2.0. The repository's `REUSE.toml` records `docs/**` as aggregate
Apache-2.0 and `LICENSES/Apache-2.0.txt` holds the canonical text.

## WebRTC Audio Processing Module — absent upstream candidate

- Project: WebRTC Audio Processing Module, legacy AGC (`WebRtcAgc`) and AGC2.
- Expected licence: **Apache-2.0**, subject to the exact revision's `NOTICE`
  and third-party terms.
- Revision: **none pinned**. Three upstream revisions are quoted in the pinned
  research notes as documentation links, but no local file verifies them.
- Source: **not present**. No source tree, header, native library, wheel,
  archive, package substitution or download is included.
- Rights requirement: the exact Apache-2.0 licence and `NOTICE` text for the
  pinned revision, the third-party notice set, a patent-grant review, an
  explicit decision for any embedded or generated weights, and an approved
  redistribution model for the source, native library or binding wheel must be
  reviewed before any wrapper, build, comparison or release can be claimed.

## pywebrtc-audio binding — declared pin only

- `adapters/webrtc-ns/requirements.lock` declares
  `pywebrtc-audio==0.2.0`, expected Apache-2.0.
- The binding is **not installed** here (`data/envs/webrtc` is absent and no
  module is importable). The checked-in adapter explicitly disables AGC, so the
  pin is not evidence that the binding exposes AGC or AGC2 settings.

## Models, weights and audio

No model weights, checkpoints, corpus audio, recordings, listening items or
libraries are included. The package contains only Python source, canonical JSON,
digests and notices.

No upstream licence text is copied, inferred or invented. `check_licensing.py`
fails if a fabricated upstream licence sidecar or binary artifact appears.

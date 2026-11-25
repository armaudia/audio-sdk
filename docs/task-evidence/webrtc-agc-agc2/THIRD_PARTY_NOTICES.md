SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0

# Third-party notices

## WebRTC AGC / AGC2 — absent upstream component

- Project: WebRTC Audio Processing Module, legacy AGC (`WebRtcAgc`) and AGC2.
- Expected licence: Apache-2.0 for the WebRTC source, subject to the exact
  revision's `NOTICE` and third-party terms.
- Revision: **none pinned**. No commit, tag, tree or file digest is verified in
  this workspace. The research note
  `research/level_tone_control_20261028.md:20` quotes three upstream revision
  URLs as documentation; they are not local artifacts and are not treated as
  pins.
- Source: **not present**. No `audio_processing.h`, `gain_control.h`,
  `gain_control.c`, `agc2/` source, native library, `pywebrtc-audio` wheel,
  archive or download is included in this directory.
- Runtime: **not present**. `data/envs/webrtc` is absent and no
  `pywebrtc_audio` or `webrtc_audio_processing` module is importable.
- Local binding pin: `adapters/webrtc-ns/requirements.lock` declares
  `pywebrtc-audio==0.2.0` for noise suppression, but the checked-in adapter
  disables AGC. That pin is not AGC API coverage.
- Rights requirement: the exact Apache-2.0 licence and `NOTICE` text, the
  third-party notice set, a patent-grant review, an explicit decision for any
  embedded or generated weights, and an approved distribution model for the
  source, native library or wheel must be reviewed before any wrapper, build,
  comparison or release can be claimed.
- Local files used: **none**. Every Python file is an independent task-local
  standard-library implementation and is not derived from WebRTC.

The repository's `REUSE.toml` records `docs/**` as aggregate Apache-2.0. This
evidence package itself is Apache-2.0. No upstream Apache-2.0 `NOTICE` or
licence file is included because no upstream artifact exists;
`check_licensing.py` fails if one appears.

No model weights, corpus audio, binaries or downloaded assets are included.

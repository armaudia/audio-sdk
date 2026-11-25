<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# License and rights boundary

## Task-local files

Every file in this directory is original, first-party work licensed
`Apache-2.0` under the repository `REUSE.toml` `docs/**` aggregate. Python files
carry inline SPDX headers; generated JSON/digest artifacts carry `.license`
sidecars. No third-party code, model, weights, audio, trace, packet capture,
archive or license text is copied, vendored or redistributed.

## Upstream artifact status

No upstream artifact is present:

- No WebRTC/libwebrtc/NetEq source checkout, archive or patch.
- No NetEq/Opus codec library, object, dynamic library or install tree.
- No receive trace, RTP packet capture, payload, PCM or media file.
- No upstream `LICENSE`, `COPYING`, `NOTICE` or third-party notice bundle.

WebRTC is normally published under the Chromium BSD-3-Clause license, together
with third-party notices. That is recorded here as a **requirement to verify
against a specific pinned revision**, not as an established fact for any
artifact in this workspace. The exact license file, notice bundle, revision and
redistribution/product-use scope must be supplied and reviewed before any use,
which is why gate `G2` and blocker `BLK-02` remain open.

## Prohibited uses of this package

This package is not a NetEq implementation, adapter, provider, jitter buffer,
playout engine, codec integration or benchmark bundle. It grants no rights to
any upstream artifact and makes no licensing, redistribution or release claim.

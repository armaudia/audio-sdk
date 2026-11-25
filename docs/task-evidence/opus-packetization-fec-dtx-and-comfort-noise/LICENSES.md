<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# License and rights boundary

## Task-local files

Every file in this directory is original, first-party work licensed
`Apache-2.0` under the repository `REUSE.toml` `docs/**` aggregate. Python files
carry inline SPDX headers; generated JSON and digest artifacts carry `.license`
sidecars. No third-party code, model, weights, audio, packet trace, capture,
archive or license text is copied, vendored or redistributed.

## Upstream artifact status

No admitted upstream artifact is present:

- No Xiph.Org Opus / libopus source checkout, archive, patch or submodule.
- No admitted libopus header, static library, dynamic library or install tree.
- No Opus or RTP packet capture, payload corpus, PCM, encoded stream or erasure
  trace.
- No upstream `COPYING`, `LICENSE_PLEASE_READ.txt`, `NOTICE` or third-party
  notice bundle.

Opus is normally distributed under the BSD-3-Clause license together with a
patent/implementation notice bundle. That is recorded here as a **requirement
to verify against a specific pinned revision**, not as an established fact for
any artifact in this workspace. The exact license files, notices, revision and
redistribution/product-use scope must be supplied and reviewed before any use,
which is why gate `G2` and blocker `BLK-02` remain open.

One unqualified `libopus.0.dylib` (version string `libopus 1.6.1`) exists inside
a gitignored PyAV virtualenv of an unrelated pipeline. It ships no Opus license
text or source revision, is not staged or approved, and is recorded only as
provenance. It is not admitted, linked, executed or used for any result in this
package.

## Prohibited uses of this package

This package is not an Opus implementation, codec adapter, provider,
packetizer, FEC engine, DTX/CNG implementation, jitter buffer or benchmark
bundle. It grants no rights to any upstream artifact and makes no licensing,
redistribution, parity or release claim.

SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0

# Third-party notices

## SpeexDSP 1.2.1 (vendored, compiled in place)

- Project: Xiph.Org SpeexDSP
- Revision: `7a158783df74efe7c2d1c6ee8363c1e695c71226`
- License: BSD-3-Clause-style terms in `third_party/speexdsp/COPYING`
- KISS FFT notice: `third_party/speexdsp/COPYING.kissfft`
- Provenance note: `third_party/speexdsp/UPSTREAM.md`
- Local files used: `libspeexdsp/resample.c`, `include/speex/speex_resampler.h`,
  `include/speex/speexdsp_config_types.h`, `libspeexdsp/arch.h`,
  `libspeexdsp/os_support.h`.

The harness includes these files in place. No vendored file is copied,
patched, substituted, relicensed or redistributed from this directory. The
repository's `REUSE.toml` already records `third_party/speexdsp/**` as
BSD-3-Clause. This evidence package itself is Apache-2.0.

No model weights, corpus audio, binaries or downloaded assets are included.

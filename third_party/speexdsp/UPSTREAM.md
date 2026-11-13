# SpeexDSP source provenance

- Upstream project: Xiph.Org SpeexDSP
- Upstream revision: `7a158783df74efe7c2d1c6ee8363c1e695c71226` (v1.2.1)
- Upstream local checkout: `data/checkouts/SpeexDSP`
- Source license: BSD-3-Clause-style terms in [`COPYING`](COPYING)
- Binary/model assets: none
- Local build: floating-point preprocessing with `USE_SMALLFT`; the CMake target includes the preprocessor and its upstream library source dependencies. Denoise is enabled with −20 dB attenuation; AGC, VAD, and dereverb retain their upstream disabled defaults.
- Local integration edit: `include/speex/speex_preprocess.h` marks `speex_preprocess_run` and `include/speex/speex_echo.h` marks `speex_echo_cancellation` with Clang's `[[clang::nonblocking]]` when available. The declarations make the NS direct/callback and AEC scheduled backend processing helpers subject to function-effects call-graph checking; annotations do not alter upstream implementations.
- Local AEC hardening edit: `mdf.c` validates dimensions and checks every state allocation before dereferencing, cleaning up partial state on failure. `fftwrap.c` and `smallft.c` similarly clean up or report partial FFT allocation failure. This changes invalid/oversized AEC initialization to return `NULL` instead of risking overflow or a null dereference. The experimental integration bounds AEC frames to at most 480 samples and filter lengths to at most 12,000 samples; it does not qualify callback safety or production readiness.
- Local preprocessing hardening edit: `preprocess.c` and `filterbank.c` validate initialization and clean up partial allocations when state creation fails. A focused failure-injection test covers the library's floating-point SmallFT build; other FFT configurations and engine budget rollback require separate evidence.

The vendored files are the library's upstream C and header files with their original notices retained. CMake intentionally builds the source into a private static target so the project does not depend on host-installed Speex binaries.

KISS FFT files retain Mark Borgerding and Jean-Marc Valin's separate BSD-style notice in their source headers. `COPYING.kissfft` preserves that notice for source and binary distributions; CMake installs it alongside the SpeexDSP `COPYING` file.

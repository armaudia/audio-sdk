# File-level licensing map

The repository owner approved this outbound licensing map for publication on
14 November 2026. The approval is recorded in
`licensing/decision.json`. The individual CLA is separately published under CLA/individual.md.

| Files | Outbound license |
|---|---|
| `api/**` public C declarations and API build package | Apache-2.0 |
| `core/**` runtime, provider wrappers, internal headers and native tests | MPL-2.0 |
| `bindings/**`, `examples/**`, `conformance/**`, public CMake adapters | Apache-2.0 |
| First-party build/release tools, schemas and documentation | Apache-2.0 |
| `third_party/**` and copied third-party notices | Original terms, unchanged |

The full unmodified license texts are in LICENSES/. SPDX headers and REUSE.toml
record file-level attribution. A directory name does not override a file's
license, and copying core code into an API or proprietary file does not remove
its obligations. This is not a blanket `Apache-2.0 OR MPL-2.0` dual license.

Previously granted MIT rights are not revoked. Existing notices are retained in
`notices/first-party-MIT.txt`; third-party SpeexDSP/FFT notices remain intact.
No model, model weights, recording or dataset rights are granted by this map.

## Distributed core binaries

The native SDK package includes its corresponding covered source under
`share/audio-sdk/source/`, the license texts and a source-location notice. Core
source remains available under MPL-2.0 independently of proprietary larger-work
terms. Consumers distributing modified covered files must preserve the applicable
notices and provide the corresponding covered source under the applicable terms.
Read the official license; this map does not replace it.

## Contributors

External SDK contributions require a verified private acceptance record for the
published individual CLA. An empty approval ledger does not approve contributors;
see CLA/README.md. The beneficiary is Tsakanyan Hovhannes personally.

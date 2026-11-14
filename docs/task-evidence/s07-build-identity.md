# S07 — build-input identity and package sealing work

Status: partial; no new candidate was sealed.

## Implemented

- CMake computes the runtime build ID from the bytes of sorted runtime source,
  header, vendored dependency, lock, and source-allocation inputs, plus compiler,
  build flags, target architecture/system, and deployment-target metadata.
- Configure-time source paths and SHA-256 values are frozen in
  `<build-dir>/runtime-inputs.sha256`; changes to those inputs trigger CMake
  reconfiguration. `scripts/verify_build_inputs.py` refuses stale build inputs.
- `scripts/package.sh` stages under the destination parent, refuses an existing
  candidate path, and renames the fully staged directory into place.

## Checks

```sh
cmake --build build/all -j4
python3 scripts/verify_build_inputs.py "$PWD" build/all
ctest --test-dir build/all --output-on-failure --timeout 45
./scripts/package.sh build/all \
  build/candidates/macos-arm64-20261114-foundation-07
```

Results:

- Build succeeded; freshness check verified all 58 frozen compilation inputs;
  Release CTest passed 10/10.
- Packaging refused to overwrite existing Candidate 07 with exit status 1.
  Candidate 07 remains unchanged and historical.
- Current build ID is
  `audio-sdk/0.1.0+sha256:307f828cafb1328d0872c293ae50e89fcf17411da8e327ed4943a6c3f8a8c9c2`.
  Candidate 07 reports
  `audio-sdk/0.1.0+sha256:fe66742bc610c4a1d27439c127908d803bc14555c6009a98d3339d594dc8d800`.
  The current identity includes a byte-derived runtime-input digest; this
  difference alone does not prove reproducibility.

## Still open

The candidate manifest generator still needs to consume real machine-readable
test reports and actual CMake/toolchain values instead of historical constants.
Atomic staging/sealing has not been exercised to create a new candidate.
Runtime dependency inspection, clean-build reproducibility, Linux x86-64, and
hosted CI remain unverified. No new consumer handoff or artifact adoption is
claimed.

# Validity arithmetic and installed external delay evidence

## Validity regression

The original defect was first captured as a failing test before changing
`src/core/validity.c`:

```text
empty-provider-range-before-content: got offset=160 count=96 produced=160,
expected offset=160 count=0
exit status: 1
```

The case uses `first_input_sample=0`, edge exclusions 0, provider
`source_first=-256`, `produced=160`, `provider_offset=160`,
`provider_count=0`, and `accepted_end=160`.

The fix clips the provider and accepted-content intervals into the output-local
range before intersecting them. Empty intersections remain empty, offsets and
counts remain within `produced`, and edge/content coordinates use saturating
addition/subtraction. Input frame and provider output end coordinates are
rejected if they overflow signed sample coordinates.

`tests/test_validity.c` covers the reproduced case, delay boundaries 0, 1, 159,
160, 161, 256, and 512, every final remainder 1–159, nonzero origin, empty
stream, provider interval overflow, and signed coordinate boundaries.

```sh
cmake --build build/all --target as_test_validity --parallel 2
./build/all/as_test_validity
```

Result: passed. The full Release suite subsequently passed 10/10.

The public stats regression in `tests/test_validity.c` also submits a final
160-sample padded frame with one accepted source sample and requires
`final_padding_samples="159"` (not 160) and
`startup_padding_samples="0"`. Padding counters now count the exact portions
of output intervals before accepted content and after the accepted end,
including worker and drain paths.

```sh
cmake --build build/all --parallel 2
ctest --test-dir build/all --output-on-failure
```

Result: 10/10 passed. The first compile attempt failed because the new public
stats assertion had not included `test_common.h`; adding that test helper
header fixed the build, and the rerun passed.

## Installed external providers

Candidate 04 was installed before compiling the fixture. The fixture uses only
installed public headers/library and installed conformance sources:

```sh
cmake -S build/candidates/macos-arm64-20261114-foundation-04/audio-sdk-0.1.0/share/audio-sdk/conformance/external_provider \
  -B build/external-provider-04 \
  -DCMAKE_PREFIX_PATH="$PWD/build/candidates/macos-arm64-20261114-foundation-04/audio-sdk-0.1.0" \
  -DAUDIO_SDK_CONFORMANCE_DIR="$PWD/build/candidates/macos-arm64-20261114-foundation-04/audio-sdk-0.1.0/share/audio-sdk/conformance"
cmake --build build/external-provider-04 --parallel 2
ctest --test-dir build/external-provider-04 --output-on-failure
```

Result: 10/10 passed, including intentional fault/drain-bound detections and
delays 0, 1, 159, 160, 161, 256 with native hop 256, and 512. The conformance
runner exercises both declared modes 2 and 3 for providers that advertise
them. Candidate archive SHA-256:
`e570d694a50a52c576c53bef7c62a339472a444c91ff126d41ab7ffaf3bd5011`.

An earlier installed run failed at 512 because the conformance raw collector
allocated only five frames; timing, start-position and 321-sample boundary
checks reported capacity exhaustion. Collector capacities now derive from
`max_drain_calls`; the repeated installed run above passed. `buffered.flow`
counts delivered output frames rather than requiring nonzero valid samples,
since a large declared startup delay can legitimately make initial frames
entirely invalid.

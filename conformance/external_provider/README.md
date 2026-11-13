# External provider onboarding fixture

This source tree is the installed-header onboarding template and executable
conformance fixture. It demonstrates the complete v0.1 `create`, `process`,
`reset`, `drain`, and `destroy` table. It is deliberately a delay/fault fixture,
not production DSP; replace its provider implementation and descriptor values
before shipping a provider.

## Clean consumer build

Use an installed SDK prefix. This procedure does not include the SDK source or
private headers:

```sh
cmake -S "$SDK_PREFIX/share/audio-sdk/conformance/external_provider" \
  -B "$CONSUMER_BUILD" \
  -DCMAKE_PREFIX_PATH="$SDK_PREFIX" \
  -DAUDIO_SDK_CONFORMANCE_DIR="$SDK_PREFIX/share/audio-sdk/conformance"
cmake --build "$CONSUMER_BUILD" --parallel 2
ctest --test-dir "$CONSUMER_BUILD" --output-on-failure
```

For onboarding, copy this directory to a clean consumer project, replace the
fixture table and descriptor with the provider's implementation and registered
ID, then retain the installed `checks.c` conformance target. Keep the fault and
delay variants when practical; expected-failure cases must remain marked as
expected failures rather than being mistaken for provider passes.

Conformance establishes the tested API/format/lifecycle behavior only. It does
not establish performance, rights, callback safety, or any other format/host
capability.

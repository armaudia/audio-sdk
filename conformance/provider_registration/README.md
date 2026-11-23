# Source-linked v0 registration fixture

From the extracted native archive, point `SDK_PREFIX` to its `audio-sdk-0.1.0`
directory (an absolute path):

```sh
for enabled in OFF ON; do
  cmake -S "$SDK_PREFIX/share/audio-sdk/conformance/provider_registration" \
    -B "build/registration-$enabled" -DCMAKE_PREFIX_PATH="$SDK_PREFIX" \
    -DAS_ENABLE_FIXTURE_PROVIDER="$enabled"
  cmake --build "build/registration-$enabled" --parallel 2
  ctest --test-dir "build/registration-$enabled" --output-on-failure
done
```

This consumer uses only installed public headers and `AudioSDK::audio_sdk`.
Its default `OFF` build sees both built-ins but not `fixture.caller-asset.v0`.
The `ON` build compiles `src/`, uses the descriptor template in `config/` and
registers explicitly in `tests/`. Both paths use the same unmodified SDK
archive, and a second registry never sees the local registration. The
descriptor hashes the single implementation file and the config file at
configure time. Only synchronous mode 2 is advertised.

The caller generates one test byte in memory. Preparation rejects missing and
tampered bytes; processing still works when the caller changes its buffer
after creation. No models, audio, runtime dependencies or asset files are
included. This is an integration fixture, not a public built-in or a
production DSP provider.

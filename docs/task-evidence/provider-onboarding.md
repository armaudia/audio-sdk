# Installed provider onboarding fixture

The installed `conformance/external_provider/` directory is the starter template.
Its README documents the CMake consumer-only build. The exact documented
commands were run from the SDK root with `SDK_PREFIX` pointing at candidate 07
and a fresh build directory:

```sh
SDK_PREFIX="$PWD/build/candidates/macos-arm64-20261114-foundation-07/audio-sdk-0.1.0"
CONSUMER_BUILD="$PWD/build/onboarding-consumer-07"
cmake -S "$SDK_PREFIX/share/audio-sdk/conformance/external_provider" \
  -B "$CONSUMER_BUILD" \
  -DCMAKE_PREFIX_PATH="$SDK_PREFIX" \
  -DAUDIO_SDK_CONFORMANCE_DIR="$SDK_PREFIX/share/audio-sdk/conformance"
cmake --build "$CONSUMER_BUILD" --parallel 2
ctest --test-dir "$CONSUMER_BUILD" --output-on-failure
```

Result: configure/build succeeded and 10/10 tests passed. The fixture source
came from the installed prefix; its only SDK include/link dependencies were
the installed public target and installed conformance source. This verifies
the documented build path, not an external developer's time-to-first-provider
or production provider suitability. There was no separate human onboarding
participant or assistance session.

# Examples

## C provider switching

Build the top-level project and run `as_example_c`. It processes the same
synthetic impulse with Speex then high-pass in independent sessions and prints
each source interval and validity range:

```sh
cmake -S . -B build/all -DCMAKE_BUILD_TYPE=Release
cmake --build build/all
./build/all/as_example_c
```

## Python WAV switching

The Python binding requires an explicit absolute native-library path. It does
not search the current directory. After building the SDK:

```sh
AUDIO_SDK_LIBRARY="$PWD/build/all/libaudio_sdk.dylib" \
PYTHONPATH="$PWD/bindings/python" \
python3 examples/python/switch_provider.py input-mono-16k-pcm16.wav
```

The example accepts only PCM16 mono 16 kHz WAV input. It decodes each signed
sample by dividing by 32768 and writes PCM16 using ties-to-even rounding of
`x*32768`, clamped to `[-32768,32767]`. There is no hidden resampling.
It prints each provider ID, declared buffering delay, valid output length and
SHA-256 of the raw float32 result. The installed-wheel checks use Python 3.12. The wrapper supports synchronous mode 2; buffered submit/pull is available through C.

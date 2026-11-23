# SDK-FEED-FORWARD-COMPRESSOR — deterministic DSP fixture

**Status: proposal-only / synthetic; `incomplete` where real qualification is
absent.** This directory contains task-local reference evidence for a minimal
feed-forward compressor. It is not an installed SDK change, ABI change,
descriptor, registry default, public release, product recommendation or
qualification result. SDK v0 remains fixed at 16 kHz mono `float32`, 160-sample
frames. Nothing outside this directory was modified.

## Scope and boundary

- `fixture.py` — deterministic, model-free generator and reference model. The
  public v0 frame boundary is represented explicitly: 16 kHz mono f32, 160
  samples per frame, `epoch`, `first_input_sample`, final-frame padding checks,
  rejection without state advance, reset with a strictly greater epoch, and
  per-session state isolation. The frame adapter here is Python-side evidence,
  not a claim of an installed session.
- `provider/` — optional C provider source using only
  `audio_sdk/session_v0.h` / `provider_v0.h`. It is compiled only with the
  task-local opt-in `AS_ENABLE_FEED_FORWARD_COMPRESSOR=ON`, is never registered
  by the SDK default build, and is not linked into the installed library. Its
  C test is a boundary smoke check (registration, mode gating, gain reduction,
  epoch/shape/nonfinite rejection, reset, drain, session isolation); it does
  not claim bit parity with the Python DSP report.
- `report.json` — canonical machine-readable report with all DSP conditions,
  adverse controls, digests, counts and explicit incomplete gates. No missing
  result qualifies a candidate.
- `test_fixture.py` — 26 deterministic Python unittest cases.

The reference algorithm is a causal feed-forward peak-envelope detector with
symmetric one-pole attack/release and a static gain law:

```
envelope[n] += (attack|release) * (|x[n]| - envelope[n-1])
level_db = 20*log10(max(envelope, 1e-12))
gain_db  = makeup_db - (1 - 1/ratio) * max(0, level_db - threshold_dbfs)
y[n] = x[n] * 10^(gain_db/20)
```

Frozen default controls: `threshold_dbfs=-24`, `ratio=4`, `attack_ms=5`,
`release_ms=120`, `makeup_db=0`, `max_abs_input=2`. No lookahead, side-chain,
knee, clipper, model weight or external asset exists.

## Source pins (SHA-256)

All paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. The four
evidence files are the ones named on the task; the two headers pin the public
boundary used by the optional C source.

| Source | SHA-256 |
| --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `api/include/audio_sdk/provider_v0.h` (SDK worktree) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` (SDK worktree) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

Pinned base commit: `0673cb354cceb66f2f71faf9af7703b5a5d2fcfa`; branch
`swarm/SDK-FEED-FORWARD-COMPRESSOR`. The board file is mutable shared state and
is not used as qualification evidence. Tests fail if any pinned file is
missing or changed.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `fixture.py` | `7e7e65aba1342e656990a83c2644478017696bd849cfc6f68bb1b08e96c72513` |
| `report.json` | `72841527b1736e09cd96fd2e3d8efd609e4e2f9a75bb2f4e5b8e417a67343eb9` |
| `test_fixture.py` | `4cee04661983a9c0a33d016aa2169e7b3e9d6a989f7f7c82905b184b004c3c71` |
| `provider/CMakeLists.txt` | `4174cf63c18f1fe2526c3e42676639b2dc166e9eb708f687dd7be99fe280ad7c` |
| `provider/feed_forward_compressor.c` | `fb69e784ab85ab29414a52c4b41e8b908d31f10051f285f5d44553e6211c0769` |
| `provider/config/config.json` | `000c8bf9831e38e9e61010e7cc0175a950a83090a5c9b7fe31d954c8749a5a4b` |
| `provider/config/descriptor.h.in` | `5b4cd6602dd8d90c69ee8617e9f976a60e55765a750072c35d0e28486a76f34f` |
| `provider/tests/test_provider.c` | `38e4f84a3a9ee6ff4dc1a215f4c0135fbfed691be42a74a254bec6c578adc1dc` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`, one terminal LF): 20,037 bytes; SHA-256 as above. Its
`fixture_digest` is
`09a742cb471c5b38b55eef5fd226e2c1fd63c658145198b2796259a7323f14c6`, covering
format, pins, seeds, config and detector definition. All PCM digests are over
IEEE-754 little-endian f32 bytes.

## Exact reproduction

Verified with Python 3.11.5, CMake 3.27.4 and AppleClang 21 on macOS. Use a
fresh scratch directory; builds and generated copies stay outside the worktree.

```sh
audioml=/Users/htsakanyan/workspace/audio/audioml
worktree=$audioml/worktrees/audio-sdk/SDK-FEED-FORWARD-COMPRESSOR
evidence=$worktree/docs/task-evidence/feed-forward-compressor
scratch="${TMPDIR:-/tmp}/ffc-verify-$$"
mkdir -p "$scratch"

# 1. Regenerate and compare the canonical report.
cd "$worktree"
PYTHONDONTWRITEBYTECODE=1 python3 "$evidence/fixture.py" "$scratch/report.json"
cmp "$scratch/report.json" "$evidence/report.json"
shasum -a 256 "$scratch/report.json" "$evidence/report.json"

# 2. Python unittest suite (26 cases) and JSON parse.
cd "$evidence"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
python3 -m json.tool report.json > /dev/null

# 3. Optional C boundary: OFF then ON, both against an SDK installed to scratch.
cmake -S "$worktree" -B "$scratch/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$scratch/sdk-build" --parallel 4
cmake --install "$scratch/sdk-build" --prefix "$scratch/sdk-prefix"
cmake -S "$evidence/provider" -B "$scratch/provider-off" \
  -DCMAKE_PREFIX_PATH="$scratch/sdk-prefix" \
  -DAS_ENABLE_FEED_FORWARD_COMPRESSOR=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build "$scratch/provider-off" --parallel 2
ctest --test-dir "$scratch/provider-off" --output-on-failure
cmake -S "$evidence/provider" -B "$scratch/provider-on" \
  -DCMAKE_PREFIX_PATH="$scratch/sdk-prefix" \
  -DAS_ENABLE_FEED_FORWARD_COMPRESSOR=ON -DCMAKE_BUILD_TYPE=Release
cmake --build "$scratch/provider-on" --parallel 2
ctest --test-dir "$scratch/provider-on" --output-on-failure

# 4. Source pins, local digests, repository hygiene and read-only board check.
shasum -a 256 \
  "$audioml/research/voice-enhancement-20261101/candidate_matrix.csv" \
  "$audioml/REALTIME_COMPONENT_CANDIDATES.md" \
  "$audioml/audio-benchmark-platform/audio-sdk/CONTRACTS.md" \
  "$audioml/audio-benchmark-platform/plan/swarm/VERIFICATION.md" \
  "$worktree/api/include/audio_sdk/provider_v0.h" \
  "$worktree/api/include/audio_sdk/session_v0.h"
shasum -a 256 "$evidence/fixture.py" "$evidence/report.json" "$evidence/test_fixture.py"
cd "$worktree" && git diff --check
cd "$audioml" && python3 audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-FEED-FORWARD-COMPRESSOR
```

Expected: regenerated report byte-identical (digest above); 26/26 Python tests
pass; `json.tool` succeeds; OFF build leaves the provider unlinked and
unregistered with 1/1 ctest pass; ON build registers one caller-local provider,
measures gain reduction, and passes reset/drain/session-isolation with 1/1
ctest pass; all six source-pin digests match; `git diff --check` is silent;
board check exits 0 and prints the claimed base, branch and worktree.

## Counts and key synthetic results

Counts: 12 required result groups (all present, 0 missing), 4 evidence pins,
2 boundary pins, 100 amplitude-sweep points, 39 frequency points, 300
speech-like frames, 100 dense-load frames, 6 interacting configurations,
18 invalid-control cases and 7 invalid-input cases. Python tests: 26. C
boundary test runs: 2 (OFF and ON).

| Condition | Observed synthetic value | Output digest |
| --- | --- | --- |
| Silence, 40 frames | peak 0.0, final gain 0.0 dB | `c65206769723a13afe80c0d925531639ceef9c2eb97eee3b1b542739ec40597f` |
| Impulse (0.9) | peak sample 0 → content delay 0; tails 0.0 | `d71f34d6bf38bfe1bbdba4fad2995090543eacd63f4358df88e540e47ceda482` |
| Step (0.7 at sample 640) | first crossing 0 samples; steady gain −15.67647 dB | `0dd19401e3c181dbd9cfc97ed25df64fcaa95a15fbe8a6b6effe7ff9b2fab268` |
| Amplitude sweep | gain-law RMSE 1.024914 dB vs identity 12.82719 dB | `edb2bca52fb3c8869f8e52d13b64a380efc3551731cc20d44f49f924239b828b` |
| Frequency sweep 200–4000 Hz | gain −9.868703…−9.529513 dB, max deviation 0.627306 dB | `b6647213aa9987dcc026e3fd8bee3815e34102275359b65556de7d39f1123c3c` |
| Burst attack/release | attack 1.3125 ms, release 228.625 ms; `idle->active@3221`, `active->idle@22858` | `f2d607f82738a2b74a5a5457fbe76c6de28c035092f9d55bd04f37514a2db66b` |
| Clean speech-like program | 300 frames; envelope correlation 0.96208 vs hard-clip control 0.841618 | `40964c47688c15837ed9b1436cd5b5484fbdada52ad5e5f1c13d32d94be970b1` |
| Dense load control | 100 frames, 0 nonfinite, peak 0.524593705 | `0dcbcdf604727c9fad3959a4d3834c641d717456d8a29b5e9ab89cadd7d80f96` |
| Peak overshoot | makeup +6 dB / ratio 1: peak 1.795736083, 1 sample > FS; limiter peak 0.98, headroom −0.0 dB | boosted `f3dfb0a4b59ef1f52c2a5a71a90e69fc9860582d8651994819ae5ae4da5d4ff8`, limited `2f2b7438e758e33b761a879a1bfc82b2eb6b7583412cfe82168c60c8aa5126a0` |
| Reset/isolation | old epoch rejected, higher epoch OK; reset matches fresh, sessions isolated; final frame 5 valid, process after final rejected | `a233f980247b9bf776edf0f39802edb9c82d0c26da0963fa9b61e98ab7acaa69` |

Interaction digests: compressor only
`9d67b0286a9e26bf672d1fabee1a9cd7a1abc8d88db32ace0907d03cac9019d3`;
compressor→limiter `287f5db71a92eb83be55b54b3b8850c19aa27a91bf0c95d115132b52a8f2a0b9`;
limiter→compressor `26b6ce36eeb95252c6d225436d78f9eddc67bf1bceb24b6d8358758b39961f64`;
compressor→AGC `210ff81e11f1f6c34b7949c9d0623363bfa72f2a82b866f142dcd4160e528811`;
AGC→compressor `cb2da1748c7cd60455a770f5bbe7ec2b757159b0cd0d5d42f15491d54805a2a8`;
compressor→compressor `9d67b0286a9e26bf672d1fabee1a9cd7a1abc8d88db32ace0907d03cac9019d3`.
The last equals compressor-only because the first stage leaves the frozen
program below the second stage's −12 dB threshold; that is an observed result,
not an omitted configuration. All six have zero nonfinite outputs and peaks below
2.0; only the post-limiter cases are bounded at 0.98.

## Adverse and control results

- Invalid controls (18/18 rejected, recorded by name in `report.json`):
  `threshold` below/above range and nonfinite; `ratio` below/above range;
  `attack` zero, above range and nonfinite; `release` zero and above range;
  `makeup` negative, above range and nonfinite; missing key, `None` config,
  unknown key, string type and boolean type.
- Invalid frames (7 cases): nonfinite sample, 159-sample frame, stale epoch,
  wrong source position, out-of-range magnitude, nonzero final padding, unknown
  flags. State digests before/after rejection are equal; rejection counters are
  recorded. No silent defaulting or acceptance by omission.
- Silence, final partial frames (`valid_count=5`, `source_first_sample=6400`),
  process-after-final rejection, strict reset epoch and session isolation are
  explicit results. The public C boundary additionally rejects mode 1/3,
  missing effective-config bytes, duplicate registration and registration on a
  different registry.

## Blockers, deferrals and reopen gates

`report.json` sets candidate qualification to `not_qualified`; the following
gates are explicitly `incomplete`:

1. **Real speech / listening — blocked.** No rights-cleared corpus, clean
   references, listener panel, STOI/PESQ harness or approved scoring protocol
   was available. The 300-frame speech-like source is analytic and the
   envelope correlation is a developer proxy only. Reopen with a pinned,
   authorized cohort and independent scoring.
2. **Nonlinear-interaction qualification — blocked.** The six cascades are
   synthetic and order-sensitive, but no matched native baseline, production
   configuration, agreed margins or paced workload was available. Reopen with
   the exact pinned runtime chain and independent review.
3. **Target-device timing — blocked.** No device, licensed runtime or measured
   load budget was available. No RTF, deadline, power or thermal claim is made.
4. **Installed SDK change — out of scope.** The C provider is opt-in and
   caller-registered; promotion would require separate contract, descriptor,
   conformance and release-gate work.

Explicit non-claims: no real audio, model weights, downloads, corpora or
licensed runtime; no listening, intelligibility, MOS or preference result; no
device CPU, latency, power or thermal measurement; no installed SDK/ABI/
descriptor/registry/default change; no release approval or baseline parity.
Historical source findings remain historical and are not reproduced or
qualified by this fixture.

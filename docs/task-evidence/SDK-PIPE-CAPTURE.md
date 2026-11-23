# SDK-PIPE-CAPTURE · task evidence

**Status: proposal-only, synthetic, task-local and incomplete.** This task adds
one opt-in recipe/host example under `docs/task-evidence/pipe-capture/`. It
integrates capture/control frames with the ordered path **80 Hz high-pass →
Speex NS policy → sample-peak limiter** and an optional read-only advisory RMS
tap. No public benchmark claim is made.

| Field | Record |
| --- | --- |
| Base / parent | `d665c298e8cce8b4d576dc45f3c7f7d3b3457425` / `dc6b8ecb5c7fa0a6a00072ddf9c6a2e168b68acc` |
| Branch / worktree | `swarm/SDK-PIPE-CAPTURE` / `/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PIPE-CAPTURE` |
| Write scope | Task-local evidence only; no board, plan, CMake, CI, ABI, descriptor, registry, default or shared-source change |
| Evidence class | Deterministic frozen synthetic fixture; model-free, no real audio or assets |
| Reviewer | `reviewer-sdk-pipe-capture` (dispatch after implementation, outside this commit) |

## Delivered fixture

The frozen recipe set contains identity, high-pass-only, NS-only, limiter-only,
base chain, voice-focus with advisory tap, explicit bypass and timeout-control
variants. Activation is `default_enabled=false` and `opt_in_only=true`; no build
target or shared source is added. The base chain runs without the tap, and the
tap never appears in the audio path.

`host.py` validates recipes before session creation, accepts fixed
16 kHz mono f32 160-sample frames, tracks epochs and source intervals, rejects
non-monotonic clocks and timeout overruns, drains accepted frames, and applies
an explicit next-epoch identity bypass after a declared backend failure. No
automatic retry or provider substitution exists.

The Speex stage is a task-local deterministic policy surrogate with the pinned
denoise-only settings, PCM16 quantization and 160-sample buffering delay. It is
not vendored SpeexDSP bit parity and is not presented as a quality result.

## Acceptance coverage

| Requirement | Evidence |
| --- | --- |
| Identity, individual stages, basic and voice-focus variants | Six exact f32 output digests; identity/limiter-only equality on the sub-ceiling paired stimulus is explained by the pinned copy fast path and distinguished on the clipping stimulus. |
| Paired noisy/clean preservation | SI-SDR and clean correlation against the synthetic clean signal, input/output RMS ratio, clipped counts and finite checks for every variant; STOI is explicitly blocked by the missing pinned scorer. |
| Clipped sample counts | Input/output `clipped_or_nonfinite`, peak and ceiling-hit counts; limiter-only output has `0` clipped samples and `42` ceiling hits. |
| Startup/tail and exact valid audio conservation | `357/357` accepted/delivered valid samples per variant with `0` missing and `0` duplicates; startup `160` and final partial tail recorded explicitly. |
| Measured delay | Impulse probe: identity raw offset `0`; base chain raw offset `160`, content lag after declared alignment `0`; declared buffering `160`. |
| Advisory tap | `0` tap events for base, `20` for voice-focus, all `mutates_audio=false`; base and voice-focus audio bytes are identical. |
| Failure bypass | Explicit backend failure at epoch `7`; accepted prefix drained; fresh epoch-8 bypass identity session; `800/800` combined valid samples. |
| Exact pinned comparison and repeats | `7/7` source pins verified, exact dependency lock values, three byte-identical report regenerations and three identical canonical report digests. |
| Default-OFF additive scope | Default disabled, no build/CI wiring, no ABI/default/shared-code changes, no provider substitution, no tolerance widening. |

## Key digests and counts

| Artifact / property | Value |
| --- | --- |
| `recipe.json` file / canonical | `08d5e1fa42327f1830e623c27ccb5ef0b03d40ca84cc7613342d1e3fa8cf8141` / `1766bbc2ff55037fb0502f221cbf6ece429759a4031cd042e3a9356115345f67` |
| `fixtures.json` file / canonical | `23b4d9e589239a8662d28e3c8dbc11371d22ebcbcc4de80d37217936dcc49e30` / `1dfc172da444dce16b30056738e76e700ecd0640ff12a4b9cf162e87b4181868` |
| `report.json` file / canonical | `30734c321a8150cc2adea332e3b2c8daeeea24eb64b733fdfc0d0efd00609a37` / `3c5d380168a7ed221307c383e0513e24c2b830db9de207a7327fcee685bdd8f6` |
| `report.json.sha256` sidecar | `11c8eeedb2d6265c13c80f69a0991b17f64686bd5ff13b356c365c5309987c75` |
| Source pins / dependency pin | `7/7` verified / SpeexDSP `1.2.1` revision `7a158783df74efe7c2d1c6ee8363c1e695c71226` |
| Tests | `22` passed, `0` failed, `0` skipped |
| Byte-identical repeats | `3` report regenerations and `3` internal canonical repeats |
| Task-local files in commit | `9` |

Exact commit SHA, signature, parent and changed-file count are reported in the
local handoff response; evidence bytes do not depend on commit metadata.

## Reproduction

```sh
task=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PIPE-CAPTURE/docs/task-evidence/pipe-capture
cd "$task"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_host.py
PYTHONDONTWRITEBYTECODE=1 python3 generate_report.py
python3 -m json.tool report.json >/dev/null
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-PIPE-CAPTURE
```

## Remaining gates and non-claims

* Independent reviewer dispatch/review is outside this commit.
* Native consumer/build/CTest and exact-head CI conclusions are not claimed.
* Paced workload, deadlines under load, target device, microphone/acoustic path
  and listening quality are `blocked_not_measured`.
* No real audio, model weights, downloads, corpora, build bytes or device data
  are included.
* No real Tiny16 parity or adverse exploratory comparison is claimed without
  S10/protocol clearance, an approved independent reference adapter and a
  permitted case manifest.
* No public benchmark, default promotion, PR, merge or release qualification is
  implied.

See `docs/task-evidence/pipe-capture/README.md` for the full scope, controls,
reproduction details and explicit non-claims.

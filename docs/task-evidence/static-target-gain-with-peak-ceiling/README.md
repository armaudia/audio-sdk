# SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING · deterministic static-gain DSP fixture

**Status: proposal-only, synthetic, developer-only, optional/unregistered.
Real-speech, listening, loudness-standard, native-provider, target-device and
release qualification are frozen as `incomplete`/`blocked`.** This directory
contains a deterministic stdlib reference for static target-RMS gain with a
hard peak ceiling, exposed through a protocol-v1-shaped task-local adapter
boundary. It is **not** an SDK provider, ABI or descriptor change, registry
entry, default provider, benchmark metric, Bench bundle, installed behavior or
qualification result. Fixed SDK v0 stays 16 kHz, mono float32, 160-sample frames.

The reference re-expresses the pinned offline baseline: measure input RMS,
compute `target_linear / max(rms, 1e-8)`, clamp the gain in the linear domain to
`[min_gain_db, max_gain_db]`, convert with `20*log10`, apply one static scale to
the whole reset-delimited segment and hard-clamp every output to `+/- ceiling`.
An explicit `silence_floor_dbfs` bypasses whole segments at or below the floor.
There is no attack, release, lookahead, per-sample adaptation or model.

## Scope and write boundary

Pinned base `d665c298e8cce8b4d576dc45f3c7f7d3b3457425`, branch
`swarm/SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING`, worktree
`/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING`.
Only files in this directory were added. No shared `CMakeLists.txt`,
`CONTRACTS.md`, header, descriptor, registry default, installed behavior,
board file, handoff, ruleset, other worktree/branch/PR or `main` was touched.

## Source pins (SHA-256)

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. Tests fail
whenever a pinned source is missing or does not match; set `AUDIOML_ROOT` if
the checkout lives elsewhere.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/level_tone_control_20261028.md` | `b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44` | Normative static target-RMS/peak-ceiling baseline and its synthetic-only caveat. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Candidate note line 91: local synthetic evaluation; guard against raising noise during pauses. |
| `src/audioml_eval/level_tone.py` | `a0ec2e3b217d877a26ae585402072d6d4ec4d1aa366ef6cd67c5b40176e2f84f` | `rms_db()` and `apply_gain()` with hard peak limit; no standard-conformance claim. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | DSP profile: sweeps, steps, impulses, silence, controls, gain/headroom/delay/numerics/state/interactions. |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Fixed v0 format, provider/session and lifecycle semantics. |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public v0 provider boundary context; not linked or modified. |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public v0 session/epoch/state context; not linked or modified. |
| `adapters/controls/adapter.json` | `3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599` | Public protocol-v1 shape reused by this unregistered local adapter. |
| `adapters/controls/run.py` | `4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66` | Public strict request pattern: explicit refs, duplicate-key and nonfinite-constant rejection. |

`audio-benchmark-platform/plan/swarm/TASKS.json` is mutable shared state. Its
read-time digest `4f33f1bde5978db569e5079eb77c3ed6c72ea6ce726396419010445064f0e030`
is stored only as provenance in `fixtures/stimuli.json`; it is never a gate.

## Files

| Path | SHA-256 | Role |
| --- | --- | --- |
| `adapter.json` | `ee150e7a226ce9ed42fe4216ed227ba9090f35856b8a9db77874cb8b5d571b7d` | Task-local, unregistered protocol-v1 descriptor. Controls: identity, static target gain, fixed gain. |
| `contract.json` | `8ef8c547365382bd863a06825155bd0f403a69ec040c7180810df2d50faa04ea` | Proposal invariants, exact arithmetic and unchanged-v0 statement. |
| `generate.py` | `633d38c831735131cc91ff8206905f5480e4ca5fab6d52118c0ab327b45312b1` | Deterministic spec generator (parameters and pins; no audio assets). |
| `reference.py` | `a20a4cc8682009f226358c79f058890ddd8a97f24085241f70dbd44788c911f3` | Stdlib f32 reference, controls, silence floor, hard ceiling, segment replay. |
| `run.py` | `e73fa9481ed417911d53769e6afe589c8dc780474f92f5a40cad0e4d08635f37` | `inspect`/`run` validation, stimulus generation, session replay and canonical result output. |
| `report.py` | `0543a4046c2bb3cf9221731e9c7f70ed55c8ac906de07847c70988789d738ede` | Builds the canonical report only by driving `run.py` functions. |
| `test_fixture.py` | `8476db8ac196cc00ee6edbd9fb3f10e5c668f44b38d587d27eebe136b413a6b5` | 21 deterministic unittest cases. |
| `fixtures/stimuli.json` | `f386dc8af6ba90958000e370506845ca40ca659ad14ddd4bb2160a20fab70ecb` | Frozen geometry, pins, parameters and eleven synthetic stimulus specifications (3,181 bytes). |
| `fixtures/report.json` | `09500a0414822caef99d1146157b293eea9ebab70e9cf03b2d665c15cea0a3eb` | Canonical machine-readable report (canonical bytes, one terminal LF, 95,614 bytes). |

## Exact reproduction

Python 3.11.5, stdlib only. From the worktree root:

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING
evidence=docs/task-evidence/static-target-gain-with-peak-ceiling

# Regenerate the frozen spec and prove byte identity.
PYTHONDONTWRITEBYTECODE=1 python3 "$evidence/generate.py"
python3 "$evidence/generate.py" --check

# Regenerate the canonical report and prove byte identity.
scratch="${TMPDIR:-/tmp}/static-gain-$$"
mkdir -p "$scratch"
PYTHONDONTWRITEBYTECODE=1 python3 "$evidence/report.py" > "$scratch/report.json"
cmp "$scratch/report.json" "$evidence/fixtures/report.json"
shasum -a 256 "$scratch/report.json" "$evidence/fixtures/report.json"

# All fixture tests, JSON parse checks and source pins.
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "$evidence" -p 'test_*.py' -v
for f in "$evidence/adapter.json" "$evidence/contract.json" \
         "$evidence/fixtures/stimuli.json" "$evidence/fixtures/report.json"; do
  python3 -m json.tool "$f" > /dev/null
done
shasum -a 256 \
  /Users/htsakanyan/workspace/audio/audioml/research/level_tone_control_20261028.md \
  /Users/htsakanyan/workspace/audio/audioml/REALTIME_COMPONENT_CANDIDATES.md \
  /Users/htsakanyan/workspace/audio/audioml/src/audioml_eval/level_tone.py \
  /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/VERIFICATION.md \
  /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/audio-sdk/CONTRACTS.md

git diff --check
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING
```

Expected: `generate.py --check` silent; report byte-identical with SHA-256
`09500a0414822caef99d1146157b293eea9ebab70e9cf03b2d665c15cea0a3eb`;
**21/21 tests pass**; four JSON files parse; nine source-pin digests match;
`git diff --check` silent; board check exits 0 with this task `in_progress` on
the pinned base/branch/worktree.

Optional manual adapter call (writes only to the scratch directory):

```sh
cat > "$scratch/inspect.json" <<'EOF'
{"protocol_version":1,"operation":"inspect","candidate_ref":{"kind":"reference","id":"dsp.static-target-gain-with-peak-ceiling.ref","revision":1},"adapter_ref":{"kind":"adapter","id":"static-target-gain-with-peak-ceiling-reference","revision":1},"configuration":{"control":"static_target_gain_reference","target_dbfs":-24.0,"min_gain_db":-18.0,"max_gain_db":18.0,"ceiling_dbfs":-1.0,"silence_floor_dbfs":-50.0}}
EOF
PYTHONDONTWRITEBYTECODE=1 python3 "$evidence/run.py" \
  --request "$scratch/inspect.json" --result "$scratch/inspect-result.json"
```

## Expected counts and key digests

`fixtures/report.json` reports 11 stimuli, 11 DSP cases, 9 source pins, 17
control-rejection probes, 2 frame-shape probes, 4 epoch/session probes, 9
input-level sweep points, 5 target sweep points, 6 ceiling sweep points, 6
static-chain configurations and 5 blocked qualifications. Status is
`proposal_only_synthetic`; qualification status is `incomplete`.

| Stimulus | Input f32 SHA-256 | Output f32 SHA-256 (default target gain) |
| --- | --- | --- |
| sweep | `11b87f0a08f353493f0c00c19df283fa77b736c92a0cab31029e2e7c1f6f71d6` | `925120721e0c1f04f6e8f47585a2f25f9b9075ec69761f8ed914d1c9498148cc` |
| steps | `df4d9223a379d1cf071b8034cac669d6d99ea20e9d089aa9ee11beaab3d21eb8` | `fdd8a1ab4440d9a10a7760d60d39b6f46759a1da0db2015a9af118656349b414` |
| impulse | `a53de14748214fd307fd5b0990fc73b56e95b9a8ae4fde496528c298c3883f15` | `5526b219130f9627513724a1db316a7a86249244acce13925ab6c4b383793186` |
| silence | `56a43ef88ddfcd0f56f7dd973312c0e73d62f59655c01d7b4e59aaa3be8b3fb6` | `56a43ef88ddfcd0f56f7dd973312c0e73d62f59655c01d7b4e59aaa3be8b3fb6` |
| near-silence below floor | `8eb1df611ee5e23af430e9355790e6a850e07e4be042a19ddd7bf6d8a6dac500` | `56a43ef88ddfcd0f56f7dd973312c0e73d62f59655c01d7b4e59aaa3be8b3fb6` |
| near-silence above floor | `9c1ab65d3aebaa7e04a9a25ca0fd86cb009f68a2214231014fa1111c6d563f54` | `a8fa36d7b85a4e80743174a5aab6ea32194ce6583d7c0a44ef1ba05e34323a71` |
| fixed tone | `865188a0714e78e2f003d4cf2f925151e60df86a1e5b02c32cbe455243857bbe` | `5e0af5553a53dde36d8a48febe9650c6b4d8f2d228850890d37f1300b8c07ba6` |
| clean-speech-like | `cc6b89814daed3e6531ab57c26d3f65d2e9c3f970825e3d6be8a1eb254734922` | `f1858f2a273626dc43768a18e18b6445a438087688ec51646ebf78722583581d` |
| ±9 dB gain-step control | `1f4e6f9290681bd842bc0729331b268786dd0a6f23a95993ae20462d3f1b2e32` | `5ce9932982706c6d66afc4f81b63204f0de2bddb29c66490a4546d770acf2fa7` |
| overshoot | `a6e134c5bdb924697ae389d3406af99e05027017489436618e0435a819d93958` | `cd68e309486e8e314ed58a337ad8108f28ae614d0c4bbd007ac40a8fed6ebcfb` |
| nonfinite | `5bf1d6d5a1d44e5073f5f55a89fbe3f8f5364c9768039388afe54447659b7191` | `d17beff5043ad1e8e05f2cbe9d233b7316869c6107cef9f5c8bb162e8df8e703` |

## Synthetic DSP observations

- **Exact gain arithmetic:** the fixed-tone case measures −27.023 dBFS input
  RMS, derives `+3.023489` dB gain from `target_linear / rms`, emits
  `f32(sample * gain)` and reaches −24.000000 dBFS full-sequence output RMS.
  Independent 1 kHz level and target sweeps match the reported expected gain to
  within 1e-6 dB. Reachable rows hit the target; the −42 dB input row clamps at
  +18 dB, the 0 dB input row clamps at −18 dB, and the −48 dB input row is
  suppressed by the explicit −50 dBFS silence floor. No row at a bound is
  promoted as converged.
- **Headroom and ceiling:** impulse and overshoot cases are run at −1, −6 and
  −12 dBFS ceilings. The impulse clips one sample at each ceiling; measured
  peaks are 0.891250908, 0.501187205 and 0.251188636 with headroom at the
  float32 rounding scale (about 3e-8 or less). No output exceeds its ceiling.
- **Silence and near silence:** exact silence and a −123 dBFS tone bypass
  amplification with exactly zero output. A −43 dBFS tone is not bypassed; its
  desired +23 dB gain clamps to +18 dB and it produces a finite nonzero output
  under the ceiling. This is whole-segment handling only: quiet spans inside an
  active segment are not gated, so raising noise during pauses remains an
  explicit unresolved risk.
- **Response and delay:** eight chirp-band RMS ratios are all −10.373818 dB;
  this is a static nonlinear gain summary, not a linear transfer function. The
  impulse peak is sample 17 in and sample 17 out, so content delay and
  lookahead are both zero. This is not availability latency or acoustic delay.
- **Numerical behavior:** NaN at sample 5 and +Inf at sample 165 are counted as
  two adverse inputs. Finite-only RMS is used for planning; C++-style min/max
  ordering maps both products to the finite ceiling, so there are zero
  nonfinite outputs and two clipped samples. This is an observation, not a
  robustness endorsement.
- **State and sessions:** a reset at frame 10 splits the static measurement
  window into +18 dB and −18 dB segments, while the uninterrupted case applies
  one −16.553 dB gain; outputs differ. A stale epoch is rejected before the
  buffer changes, an advanced epoch clears the buffer, and an unrelated session
  does not leak into a replayed suffix. Because the first segment of a split
  call is computed before later samples exist, only replayed suffixes are
  expected to match the one-shot result; this is stated in the report.
- **Interacting nonlinear configurations:** six in-memory static chains
  (target only, fixed gain only, two orderings, lower-ceiling-then-target and
  identity-then-target) are all present with four distinct digests; identity
  before target is transparent. No native chain or real-time interaction is
  exercised.
- **Energy-matched/identity control:** on synthetic ±9 dB gain-step speech the
  400 ms windowed RMS error is 1.94e-8 dB for the energy-matched fixed gain,
  4.447 dB for identity and 5.308 dB for the fixed target gain. This is a
  synthetic energy comparison only — not STOI, SI-SDR, intelligibility,
  loudness-standard conformance, listening, CPU load or deadline evidence.

## Explicit non-claims and blockers

This fixture supplies no real speech, natural/live microphone capture, licensed
corpus, model weights, download, target device, listening panel, loudness
standard meter, CPU/RTF measurement, paced callback, installed archive, native
provider build or release approval. **No missing, rejected, `not_run` or
incomplete result qualifies a candidate**; every absent real qualification is
blocked in `fixtures/report.json`. Mutable task-board state is provenance only.

Reopen before any default promotion or suitability claim:

1. **real_speech_qualification:** freeze a paired rights-cleared real-speech
   cohort with natural level variation and pauses, split by speaker/session and
   score against an agreed task-matched baseline.
2. **listening_and_loudness_standard:** run an authorized listening or validated
   objective protocol with agreed margins; separately pin and qualify any
   loudness/true-peak standard before making such a claim.
3. **native_provider_and_baseline:** build an optional native provider outside
   this fixture, verify installed-archive behavior and prove frame-by-frame
   parity with this reference on the frozen synthetic cohort.
4. **target_device_and_deadline:** measure paced availability, CPU/memory,
   content delay and failure/deadline accounting on the intended runtime.
5. **pause_noise_and_interaction_realtime:** define and qualify pause/noise-floor
   behavior on real pauses, then verify static-gain/ceiling chain interactions
   in the native real-time runtime.

Any public registration, descriptor or default-provider change requires its own
SDK contract, conformance and release-gate work outside this task scope.

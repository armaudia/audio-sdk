# SDK-ENVELOPE-AGC · deterministic envelope AGC DSP fixture

**Status: proposal-only, synthetic, developer-only, optional/unregistered.
Real-speech/listening and nonlinear-interaction qualification are frozen as
`incomplete`.** This directory contains a deterministic stdlib reference for
causal envelope automatic gain control (AGC), exposed through a protocol-v1-shaped
task-local adapter boundary. It is **not** an SDK provider, ABI or descriptor
change, registry entry, default provider, benchmark metric, Bench bundle,
installed behavior or qualification result. Fixed SDK v0 stays 16 kHz, mono
float32, 160-sample frames.

The reference re-expresses the pinned envelope controller: asymmetric
attack/release envelope smoothing, dBFS target with bounded desired gain,
first-order log-domain gain smoothing and a hard peak ceiling. The gain smoother
is a bilinear-transformed first-order Butterworth section at 8 Hz implemented
with the stdlib only (no NumPy, SciPy, model, weights, corpus or download).

## Scope and write boundary

Pinned base `0673cb354cceb66f2f71faf9af7703b5a5d2fcfa`, branch
`swarm/SDK-ENVELOPE-AGC`, worktree
`/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-ENVELOPE-AGC`.
Only files in this directory were added. No shared `CMakeLists.txt`,
`CONTRACTS.md`, header, descriptor, registry default, installed behavior, board
file, handoff or other PR was touched.

## Source pins (SHA-256)

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. Tests fail
whenever a pinned source is missing or does not match; set `AUDIOML_ROOT` if the
checkout lives elsewhere.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Component record 70: AGC improved 400 ms RMS error but degraded SI-SDR/STOI; synthetic gain ramps only. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Envelope AGC candidate note: causal attack/release, degraded SI-SDR in noisy extension. |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Fixed v0 format, provider/session boundary, state/epoch/lifecycle semantics. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | DSP profile: sweeps, steps, impulses, silence, clean speech, intelligibility/load control, gain/response/attack/release/headroom/delay/numerics/state/nonlinear interactions. |
| `src/audioml_eval/level_tone.py` | `a0ec2e3b217d877a26ae585402072d6d4ec4d1aa366ef6cd67c5b40176e2f84f` | Normative `agc()` behavior re-expressed here: 10 ms attack, 250 ms release, ±18 dB bounds, −24 dBFS target, −1 dBFS ceiling, 8 Hz log-gain smoothing. |
| `research/voice-enhancement-20261101/agent-agc-expanded/REPORT.md` | `cab8ef60b260f4b6af536111204e781c0e03a53b85986c16a271f1a1db004188` | Prior scope: 743 EARS clips, synthetic ±9 dB gain steps; RMS tracking improved while SI-SDR/STOI declined; no live capture or perceptual acceptance. |
| `adapters/controls/adapter.json` | `3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599` | Public protocol-v1 envelope shape reused by this unregistered local adapter. |
| `adapters/controls/run.py` | `4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66` | Public strict request pattern: explicit refs, duplicate-key and nonfinite-constant rejection. |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public v0 provider boundary/format context; not linked or modified. |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public v0 session/epoch/state context; not linked or modified. |

`audio-benchmark-platform/plan/swarm/TASKS.json` is mutable shared state. Its
read-time digest `a858ebf522110d43e3e0b14c61a9705230b8732bb47e8f17819a2977738ea8ad`
is stored as provenance in `fixtures/stimuli.json`; it is never a gate.

## Files

| Path | SHA-256 | Role |
| --- | --- | --- |
| `adapter.json` | `7258da7eaf20ece3d257d10f90a658f9ef8b0abc3a6ba6a7c4d96a8f75737250` | Task-local, unregistered protocol-v1 descriptor. Controls: identity, envelope AGC, static gain, peak limiter, compressor. |
| `contract.json` | `46cb417b5c01e2a12bf8d1a586bf9023df38452ccbb5f3826d5b692a806906df` | Proposal invariants and unchanged-v0 statement. |
| `generate.py` | `42ddcd9a55c322261012b7b0f4e963c5f78c1cdd7d7c7e8db8846fe6a36e1e79` | Deterministic spec generator (parameters and pins; no audio assets). |
| `reference.py` | `297c3acbf327782652e7c0d7a813fc1c78d69368e362df0cd7d6580a4d39c18c` | Stdlib f32 reference, controls, sessions, three nonlinear helper stages. |
| `run.py` | `ddfc251e935ad7d01282537f177e23bf018645a784cbbfd993a3fb009d1b9dc0` | `inspect`/`run` request validation, stimulus generation and canonical result output. |
| `report.py` | `458020a3b34ebacbfea350e007c36715fa977792738dc714cf92fa39688e7936` | Builds the canonical report only by driving `run.py` functions. |
| `test_fixture.py` | `f592539e29342bd6c9c7358fe360046054f88e3583907bd856b25c918287a088` | 21 deterministic unittest cases. |
| `fixtures/stimuli.json` | `12e3377935d0c0ba0ba489c559466c510e48903ce0a6515e1e59926a46aeb5e4` | Frozen geometry, pins and nine synthetic stimulus specifications. |
| `fixtures/report.json` | `f4bdf1862c75ed89cb1ca8c3bc8ee21aeb7831495410a210d4ca6d3e81950fe3` | Canonical machine-readable report (canonical bytes, one terminal LF, 88,812 bytes). |

## Exact reproduction

Python 3.11.5, stdlib only. From the worktree root:

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-ENVELOPE-AGC
evidence=docs/task-evidence/envelope-agc

# Regenerate the frozen spec and prove byte identity.
PYTHONDONTWRITEBYTECODE=1 python3 "$evidence/generate.py"
python3 "$evidence/generate.py" --check

# Regenerate the canonical report and prove byte identity.
scratch="${TMPDIR:-/tmp}/envelope-agc-$$"
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
  /Users/htsakanyan/workspace/audio/audioml/research/voice-enhancement-20261101/candidate_matrix.csv \
  /Users/htsakanyan/workspace/audio/audioml/REALTIME_COMPONENT_CANDIDATES.md \
  /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/audio-sdk/CONTRACTS.md \
  /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/VERIFICATION.md

git diff --check
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-ENVELOPE-AGC
```

Expected: `generate.py --check` silent; report byte-identical with SHA-256
`f4bdf1862c75ed89cb1ca8c3bc8ee21aeb7831495410a210d4ca6d3e81950fe3`;
**21/21 tests pass**; all four JSON files parse; ten source-pin digests match;
`git diff --check` silent; board check exits 0 with this task `in_progress` on
the pinned base/branch/worktree.

Optional manual adapter call (writes only to the scratch directory):

```sh
cat > "$scratch/inspect.json" <<'EOF'
{"protocol_version":1,"operation":"inspect","candidate_ref":{"kind":"reference","id":"dsp.envelope-agc.ref","revision":1},"adapter_ref":{"kind":"adapter","id":"envelope-agc-reference","revision":1},"configuration":{"control":"envelope_agc_reference","target_dbfs":-24.0,"attack_ms":10.0,"release_ms":250.0,"min_gain_db":-18.0,"max_gain_db":18.0,"ceiling_dbfs":-1.0,"gain_smooth_hz":8.0}}
EOF
PYTHONDONTWRITEBYTECODE=1 python3 "$evidence/run.py" \
  --request "$scratch/inspect.json" --result "$scratch/inspect-result.json"
```

## Expected counts and key digests

`fixtures/report.json` reports 9 stimuli, 12 DSP cases, 10 source pins,
16 control-rejection probes, 2 frame-shape probes, 4 epoch/session probes,
7 nonlinear configurations and 5 explicitly blocked qualifications. Status is
`proposal_only_synthetic`; qualification status is `incomplete`.

| Stimulus | Input f32 SHA-256 | Output f32 SHA-256 (default AGC) |
| --- | --- | --- |
| sweep | `11b87f0a08f353493f0c00c19df283fa77b736c92a0cab31029e2e7c1f6f71d6` | `78ce3d92568561aa9ab435f58a65773ea3c2e325699bca1e0ceb361b03ccf4e5` |
| steps | `df4d9223a379d1cf071b8034cac669d6d99ea20e9d089aa9ee11beaab3d21eb8` | `6ae32253c78e42e685024d258606fc02432f77f3398d5d2746909d756376b679` |
| impulse | `a53de14748214fd307fd5b0990fc73b56e95b9a8ae4fde496528c298c3883f15` | `01ebea564a4c9bdb6e694ecb45253d87866bf489b77b8060c9602b3c8dc52056` |
| silence | `56a43ef88ddfcd0f56f7dd973312c0e73d62f59655c01d7b4e59aaa3be8b3fb6` | `56a43ef88ddfcd0f56f7dd973312c0e73d62f59655c01d7b4e59aaa3be8b3fb6` |
| fixed tone | `865188a0714e78e2f003d4cf2f925151e60df86a1e5b02c32cbe455243857bbe` | `813a02753d6195cbe2d71fa356332b9675631d9ac611193f31066c8373faeec5` |
| clean-speech-like | `cc6b89814daed3e6531ab57c26d3f65d2e9c3f970825e3d6be8a1eb254734922` | `e7e7304120ef94ec33bb160482f2d53aacc262d50b048d7684633f87698fe51c` |
| ±9 dB gain-step control | `1f4e6f9290681bd842bc0729331b268786dd0a6f23a95993ae20462d3f1b2e32` | `9d016f05e1c967a63d7eb5f0bec0ac7550146191183cced1bc67dd11c58aea1d` |
| overshoot | `a6e134c5bdb924697ae389d3406af99e05027017489436618e0435a819d93958` | `5ff46b7bd3e74f01d286102b7f7a7c730f08a1ca2a864dbf8e399a93946052e8` |
| nonfinite | `5bf1d6d5a1d44e5073f5f55a89fbe3f8f5364c9768039388afe54447659b7191` | `2377c6f55e3002bbc4746f8b30826caa0d9c3cf7f9a73e0999f51fc606458b9e` |

## Synthetic DSP observations

- **Gain/headroom:** fixed-tone steady-state output RMS is −26.13 dBFS against
  a −24 dBFS target (within the ±3 dB synthetic tolerance); startup envelope
  floor produces an initial 18 dB gain transient and a 0.5004 peak, still below
  the −1 dBFS ceiling. Over-ceiling steps/impulses are bounded at
  `0.8912509084` (`f32(-1 dBFS)`), leaving positive headroom of `2.98e-8`
  against the double-precision ceiling; this is float32 rounding, not overshoot.
- **Response:** eight chirp-band RMS ratios cover the 200–4000 Hz sweep. They
  are nonlinear response summaries, not a linear transfer function.
- **Attack/release:** the quiet-to-loud burst reaches a 6 dB gain reduction at
  sample 1686 (5.375 ms after the loud onset at sample 1600). Recovery to 3 dB
  below the quiet reference was not reached inside the 3200-sample fixture and
  is recorded `not_reached_within_fixture`; no recovery sample is invented.
- **Delay:** impulse peak in sample 17, out sample 17, content delay 0 and
  lookahead 0. This is not availability latency or acoustic group delay.
- **Numerical behavior:** NaN at sample 5 and +Inf at sample 165 are retained;
  C++-style min/max ordering maps both to the finite ceiling. Two nonfinite
  inputs, zero nonfinite outputs. This is observed behavior, not robustness
  endorsement.
- **Silence:** envelope decays to zero, desired gain reaches the 18 dB bound,
  output peak stays exactly 0; raising gain during pauses remains a known risk.
- **State transitions:** `reset_frames=[10]` yields reset_count 1 and final gain
  18 dB; without reset the same sequence ends at −17.7384 dB. Stale epoch is
  rejected before state changes; an advanced epoch resets state; rejoining a
  split session after an unrelated session reproduces the uninterrupted digest.
- **Interacting nonlinearities:** seven configurations (AGC only, limiter only,
  compressor only and four two-stage orders) are all present with six distinct
  digests. AGC→limiter equals AGC only because the AGC ceiling already keeps
  every sample below the 0.98 limiter ceiling; this transparency is recorded,
  not hidden. No native/real-time chain is exercised.
- **Load-specific control:** synthetic ±9 dB gain-step speech has 400 ms windowed
  RMS error 10.646 dB for AGC versus 4.447 dB for both identity and static gain,
  and clean-vs-AGC envelope correlation 0.960 versus 0.974 for identity. This
  reproduces the tracking-versus-fidelity tension in the pinned research at a
  synthetic level only; it is not STOI, SI-SDR, intelligibility or listening.

## Explicit non-claims and blockers

No real speech, natural/live microphone capture, licensed corpus, model weights,
download, target device, listening panel, STOI/SI-SDR qualification, CPU/RTF,
deadline, paced callback, installed archive, native provider build or release
approval is supplied. No result is missing-and-promoted: unreached recovery and
all absent real qualification remain `incomplete`/`blocked` in `report.json`.
The mutable task-board digest is provenance only.

Reopen before any default promotion or suitability claim:

1. Rights-cleared matched real-speech cohort and independently scored
   quality/intelligibility, including natural gain variation and pauses.
2. Listening or validated STOI/SI-SDR protocol with agreed margins and an
   established task-matched baseline on a frozen cohort.
3. Matched native SDK provider build, installed-archive check and frame-by-frame
   parity with this reference.
4. Target-device paced callback, CPU/memory, content-delay and availability
   budgets with explicit failure/deadline accounting.
5. Native and real-time qualification of limiter/compressor interactions and
   interacting nonlinear chains.

Any public registration, descriptor or default-provider change requires its own
SDK contract, conformance and release-gate work outside this task scope.

# SDK-DE-ESSER — task-local synthetic de-esser evidence

**Status: proposal-only / synthetic; candidate `not_qualified`.** This
directory contains task-local reference evidence for a minimal de-esser at the
existing public v0 adapter boundary. It is not an installed SDK change, ABI
change, descriptor/registry default, public release, product recommendation or
qualification result. SDK v0 remains fixed at 16 kHz mono `float32`, 160-sample
frames. Nothing outside `docs/task-evidence/de-esser/` was modified.

## Task record

- ID: `SDK-DE-ESSER`
- Title: `De-esser`
- Mode: `feasibility`
- Owner: `agent-de-esser`
- Reviewer: `reviewer-de-esser`
- Write scope: SDK provider, tool or evidence directory for de-esser and its
  own fixtures. Everything in this change is inside
  `docs/task-evidence/de-esser/`.

## Exact scope and boundary

- `fixture.py` — deterministic, model-free generator, reference model and
  canonical report builder. The public v0 frame boundary is represented
  explicitly: 16 kHz mono f32, 160 samples per frame, `epoch`,
  `first_input_sample`, final-frame padding checks, rejection without state
  advance, strict reset epochs and per-session state isolation. This is Python
  evidence, not an installed session.
- `provider/` — optional C provider source using only
  `audio_sdk/session_v0.h` / `provider_v0.h`. It is compiled only with the
  task-local opt-in `AS_ENABLE_DE_ESSER=ON`, is never registered by the SDK
  default build and is not linked into the installed library. Its C test is a
  boundary smoke test (registration, mode gating, missing config bytes,
  sibilance reduction, low-band preservation, epoch/shape/nonfinite rejection,
  out-of-range fail-closed behavior, reset, drain, session isolation); it does
  not claim bit parity with the Python DSP report.
- `report.json` — canonical machine-readable report with all 15 required
  result groups, adverse controls, digests, acceptance-profile application and
  explicit incomplete gates. **No missing result qualifies a candidate.**
- `test_fixture.py` — 30 deterministic Python unittest cases.
- `SOURCES.sha256` — digests of the local evidence files. The pinned external
  sources are listed with their audioml-relative digests below.

The reference is a causal split-band design. A second-order Butterworth
high-pass (RBJ, Q = 1/sqrt(2)) extracts the detector band. A peak envelope of
that component drives symmetric one-pole attack/release and a static gain law;
only the high-pass component is reduced:

```
high[n]  = HP(x[n])
env[n]  += (attack|release) * (|high[n]| - env[n-1])
level_db = 20*log10(max(env[n], 1e-12))
red_db   = min(max_reduction_db, (1 - 1/ratio) * max(0, level_db - threshold_dbfs))
gain     = 10^((makeup_db - red_db)/20)
y[n]     = x[n] - (1 - gain) * high[n]
```

Frozen controls: `highpass_cutoff_hz=4000`, `threshold_dbfs=-24`, `ratio=6`,
`attack_ms=5`, `release_ms=120`, `max_reduction_db=12`, `makeup_db=0`,
`max_abs_input=2`. No lookahead, model weights, corpus, external asset or
licensed runtime exists. With default controls a non-sibilant analytic program
is reproduced sample-for-sample, which is the synthetic matched-gain/preservation
result; it is not a speech-quality result.

## Pinned source digests (SHA-256)

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. The five
evidence sources are the task evidence and verification profile; the two
headers pin the public boundary used by the optional C source.

| Source | SHA-256 |
| --- | --- |
| `cpp-library/PIPELINE_DESIGN_REPORT.md` | `f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093` |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `api/include/audio_sdk/provider_v0.h` (SDK worktree) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` (SDK worktree) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

Pinned implementation base: `68e3e292b0b2c4b0a96b5f3d3002bb9cb36282d4`;
branch `swarm/SDK-DE-ESSER`. The board state is mutable shared state and is not
qualification evidence. Tests fail if any pinned file is missing or changed.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `fixture.py` | `0e70eb3c33435fa2ac571e10ae9c171d39740000b68335650eef445e1135f86b` |
| `report.json` | `66f5a0d1a0778ec771842162aa38635cd96cbfd8a77b8ad24313304aff67b297` |
| `test_fixture.py` | `fc98fa71150ffea335be83825d036a843ea8c0d95eadae1d734b62fa744de9f8` |
| `provider/CMakeLists.txt` | `6573cac8dbdd8208dadcb513c7443db2ce06c91e3540cf129cabe2c71071d083` |
| `provider/de_esser_provider.c` | `a5c040eddc6dd93171557c90255e3ee540c4e9968d303fd5135cb2d08744af56` |
| `provider/config/config.json` | `0a337a20f699edaa27b647d1f0eb55569659b1521698ac40d44636d5941690e7` |
| `provider/config/descriptor.h.in` | `a26e0e5e0278a183616b4f7dc21cbdb944e43f8dee194fa4cd4ee46ef80621e2` |
| `provider/tests/test_provider.c` | `bd852500f96d04ee5bdf901d4ab831f134c4c65fa771849e88a7151d252d0950` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`, one terminal LF), 13,670 bytes, SHA-256 as above. Its
`fixture_digest` is
`f8a800eeb464687972b6897a40891b2712afc4d129212eaea82584eb4b60a9d6`, covering
format, pins, seeds, controls, band split, detector and output law. All PCM
digests are over IEEE-754 little-endian f32 bytes.

## Acceptance-profile application

The structured inventory names the **DSP** profile for this component; the task
also asks for the **enhancement/voice acceptance profile**. Both are applied at
synthetic scope and recorded in `report.json["acceptance_profiles"]`:

- **DSP (synthetic applied):** silence, impulse, low-band step, tone/noise
  frequency and level sweeps, gain/attack/release, headroom, state transitions,
  numerical behavior and six nonlinear configurations.
- **Enhancement (synthetic subset only):** identity/noisy controls, high-band
  attenuation, low-band preservation, peaks and invalid outputs. Paired speech,
  clean references, STOI and authorized listening are absent and are recorded
  as blockers, not substituted.
- **Voice (synthetic subset only):** fixed synthetic source and analysis
  windows; no speaker/language grouping, semantic, similarity or naturalness
  result. There is no real-speech, listening or release claim.

## Exact reproduction

Verified with Python 3.11.5, CMake 3.27.4 and AppleClang 21 on macOS. Use a
fresh scratch directory; builds and generated copies stay outside the worktree.

```sh
audioml=/Users/htsakanyan/workspace/audio/audioml
worktree=$audioml/worktrees/audio-sdk/SDK-DE-ESSER
evidence=$worktree/docs/task-evidence/de-esser
scratch="${TMPDIR:-/tmp}/deesser-verify-$$"
mkdir -p "$scratch"

# 1. Regenerate and compare the canonical report.
cd "$worktree"
PYTHONDONTWRITEBYTECODE=1 python3 "$evidence/fixture.py" "$scratch/report.json"
cmp "$scratch/report.json" "$evidence/report.json"
shasum -a 256 "$scratch/report.json" "$evidence/report.json"

# 2. Python unittest suite (30 cases) and JSON parse.
cd "$evidence"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
python3 -m json.tool report.json > /dev/null

# 3. SDK baseline ctest, then install to scratch for the opt-in consumer.
cmake -S "$worktree" -B "$scratch/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$scratch/sdk-build" --parallel 4
ctest --test-dir "$scratch/sdk-build" --output-on-failure
cmake --install "$scratch/sdk-build" --prefix "$scratch/sdk-prefix"

# 4. Consumer opt-in OFF then ON.
cmake -S "$evidence/provider" -B "$scratch/provider-off" \
  -DCMAKE_PREFIX_PATH="$scratch/sdk-prefix" \
  -DAS_ENABLE_DE_ESSER=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build "$scratch/provider-off" --parallel 2
ctest --test-dir "$scratch/provider-off" --output-on-failure
cmake -S "$evidence/provider" -B "$scratch/provider-on" \
  -DCMAKE_PREFIX_PATH="$scratch/sdk-prefix" \
  -DAS_ENABLE_DE_ESSER=ON -DCMAKE_BUILD_TYPE=Release
cmake --build "$scratch/provider-on" --parallel 2
ctest --test-dir "$scratch/provider-on" --output-on-failure

# 5. Digests, scope hygiene and local REUSE lint if available.
cd "$evidence" && shasum -a 256 $(find . -type f | sort)
cd "$worktree" && git diff --check
python3 -m reuse lint || echo 'reuse not installed locally; lint not run'
```

Expected: regenerated report byte-identical (digest above); 30/30 Python tests
pass; `json.tool` succeeds; SDK baseline 11/11 ctest pass; OFF build leaves the
provider unlinked and unregistered with 1/1 ctest pass; ON build registers one
caller-local provider, reduces the synthetic sibilance-band tone, preserves the
low band/silence and passes reset/drain/session-isolation with 1/1 ctest pass;
all digests match; `git diff --check` is silent.

## Counts and key synthetic results

Counts: 15 required result groups (all present, 0 missing), 7 source pins,
7 frequency points, 8 level points, 300 speech-like frames, 150 mixed-noise
frames, 100 dense-load frames, 6 interacting configurations, 21 rejected
configurations, 7 rejected frame cases and 4 explicit missing/nonfinite cases.
Python tests: 30. C boundary runs: 3 (SDK baseline plus consumer OFF and ON).

| Condition | Observed synthetic value | Output digest |
| --- | --- | --- |
| Silence, 40 frames | peak 0.0, final gain 0.0 dB | `c65206769723a13afe80c0d925531639ceef9c2eb97eee3b1b542739ec40597f` |
| Impulse (0.9) | content delay 0 samples | `d71f34d6bf38bfe1bbdba4fad2995090543eacd63f4358df88e540e47ceda482` |
| Low-band step (0.7) | crossing 0 samples from onset, low-band attenuation 0.0 dB | `edec72f44335940f3eca8d7aa3e4cb400623e426444eb33f16fe15f7f4dc3d5f` |
| 6.5 kHz bursts in speech-like program | high-band attenuation 5.398/5.307 dB, low-band attenuation 0.094/0.121 dB, min gain −8.496/−8.462 dB | `4a1180f146aa4919beca34a2dc960a033961731b91fe220486f130d8bf9a8a8b` |
| Frequency sweep 4–7.5 kHz | 4 kHz control −0.536 dB (no attenuation); 6.5 kHz +5.788 dB; 7.5 kHz +8.120 dB | `73004f08f32a5a62d4c3a8512588825642f753b6ae1333576df71e3eec94099c` |
| Level sweep 0.04–0.5 | settled gain 0.0 → −12.0 dB, monotonic; no reduction at 0.04 | — |
| Clean synthetic program | 300 frames, bit-identical output, matched gain 0.0 dB, envelope correlation 1.0 | `c4e651231a121ee93f59c7d934286bd9999a0a05b58e831d55fea89ba46a8aac` |
| Broadband matched-gain control | split-band low-band loss 0.094 dB vs broadband control 8.343 dB; high-band loss 5.398 dB vs 7.627 dB | `950444e63859a19f50b110824a83b25b1f0be9f052471c8a4353272e0c7e51e5` |
| Mixed synthetic speech-like + band noise | high-band attenuation 3.125 dB, low-band attenuation 0.024 dB | `79d7b69e9c004f20da6c897f16378e7d4005beef8e89e55e19c7fec17ce68b2a` |
| Dense-load gain stability | gain 0.0 → −9.642 dB, max per-sample step 0.280 dB, max frame step 5.730 dB, 0 nonfinite | `a7419e59fceddb922d66c5727240074b116b9d29ee67dcd930ece3e0de78bbb1` |
| Deliberate +12 dB makeup | boosted peak 1.944 (20 samples > FS), limited peak 0.98 | boosted `f53a847c9ea6184f6dbe952277ad085b4d6cc1383a530a5550620444755fe999`, limited `3338611485d214457e2997a9e7978bf984a71123228a393f4cfb15dd3f3191fb` |
| Reset/isolation/final-frame | old epoch rejected, higher epoch accepted, reset matches fresh, sessions isolated, valid_count 5, process-after-final rejected | `8be9cc645a96cb107f042367cb537124e9ff91d8e8d1728c32d183e28d5e084e` |

Interaction digests: de-esser only
`ff98793b618357c15c4322d46e20520bba9f44c7f1d10af8fc19893f0c1a875c`;
de-esser→limiter `cdd457423785e90608b619e99985185ae44a3f2ec5045cc58f8df03322400eb4`;
limiter→de-esser `a72b769f4d4754acbba603c7e8d168749e74f481ea9e7bf9213d71b7e0987a84`;
de-esser→AGC `d4d4688a7cc4ae91479265ce4832a331da50a1a035c45923c0651119b68d4992`;
AGC→de-esser `7112e448954cb1c7ee19507123b40a7b59bec0e322a386bcffa8b3950f5c4e2d`;
de-esser→de-esser `f8affc9ce7d77238c13c7b47558010e362719c0ba64fdf7663c7f4fd95ddf563`.
All six have zero nonfinite outputs and peaks below 2.0; these are synthetic
cascades, not chain qualification.

## Failure, control and adverse results

- **Crossover control:** at 4 kHz the causal complementary split shows
  −0.536 dB (slightly more) high-band energy, not attenuation. It is recorded
  as a failure/control condition; the synthetic sibilance band is 6–7.5 kHz.
  No claim is made outside that band.
- **Broadband control:** applying the same gains to the whole signal reaches
  more high-band attenuation (7.627 dB) but damages the low band by 8.343 dB,
  versus 0.094 dB for the split-band reference.
- **Invalid controls (21/21 rejected by name in `report.json`):** null/empty
  config, each missing key case, cutoff/ratio/threshold/attack/release/
  max-reduction/makeup below, above or outside range, nonfinite cutoff,
  threshold and attack, unknown key, string type and boolean type.
- **Invalid frames (7 cases):** nonfinite sample, 159-sample frame, stale
  epoch, wrong source position, out-of-range magnitude, nonzero final padding
  and unknown flags. State digests before/after rejection are equal and
  rejection counters are recorded. The C boundary additionally rejects mode
  1/3, missing effective-config bytes, duplicate registration and registration
  on a different registry; out-of-range input fails closed at the provider and
  is surfaced as `AS_BACKEND_FAILURE` with `AS_NEEDS_RESET` until reset.
- **Missing/nonfinite explicit cases:** missing config object, missing frame
  input, nonfinite config and nonfinite sample each have a recorded status.
  A simulated removal of `sibilance_burst` leaves a missing result and
  `candidate_qualifies=false`; completeness is never inferred.
- **Headroom:** the deliberate +12 dB makeup case exceeds full scale and is
  capped by the synthetic limiter control to 0.98; no production limiter is
  implied.

## Blockers, deferrals and remaining release gates

`report.json` sets `candidate_qualification` to `not_qualified`; the following
gates remain open:

1. **Real speech / listening — blocked.** No rights-cleared corpus, clean
   references, listener panel, STOI/PESQ harness, speaker/language groups or
   approved scoring protocol was available. The 300-frame source is analytic
   and sample identity is a developer proxy only. Reopen with a pinned,
   authorized cohort and independent scoring.
2. **Matched baseline and gain target — blocked.** Synthetic sample identity
   is not a loudness or quality result; no established task-matched baseline,
   production config or agreed margin was available. Reopen with a frozen
   baseline and independent measurement on the exact workload.
3. **Target-device timing — blocked.** No device, licensed runtime or paced
   workload was available. No RTF, deadline, power or thermal claim is made.
4. **Installed SDK change — out of scope.** The C provider is opt-in and
   caller-registered; promotion would require separate contract, descriptor,
   conformance and release-gate work.
5. **REUSE lint — not run locally.** The `reuse` tool is not installed in this
   environment; all new files carry valid SPDX headers or are covered by the
   repository `REUSE.toml` `docs/**` annotation. Generated C headers are static
   task-local files with valid SPDX identifiers.

Explicit non-claims: no real audio, model weights, downloads, corpora or
licensed runtime; no listening, STOI, PESQ, MOS, intelligibility or preference
result; no device CPU, latency, power or thermal measurement; no installed
SDK/ABI/descriptor/registry/default change; no release approval, production
suitability or baseline parity. Historical source findings remain historical
and are not reproduced or qualified by this fixture.

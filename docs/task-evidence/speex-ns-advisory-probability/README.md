# SDK-SPEEX-NS-ADVISORY-PROBABILITY — advisory speech-probability evidence

A deterministic, synthetic-only reference/evidence package for Speex-NS-style
**advisory** speech probability at the public audio-sdk v0 adapter boundary.
The optional C provider is task-local, opt-in, unregistered and **not** a
control signal. The audio path is an identity PCM control; the advisory value is
a fixed-point energy surrogate carried through a task-local analysis side
channel. It is not SpeexDSP code, a calibrated posterior, a validated detector,
an accuracy result or a release candidate.

Pinned base: `941cabfc39f7e33f01881b6e50e3a1e49e7eb9ce`.
Branch: `swarm/SDK-SPEEX-NS-ADVISORY-PROBABILITY`.
Provider ID only when a caller explicitly registers it:
`analysis.speex-ns-advisory-reference.v0`.

## Scope and boundary

- Installed v0 stays 16 kHz, mono `f32`, 160-sample frames. The public API,
  ABI, descriptor registry, descriptor defaults, shared `CMakeLists.txt`,
  installed providers and `main` are unchanged.
- `reference.py` is the deterministic model and report generator. It computes
  integer Q15 energy, two-hop timestamped analysis events, exact source
  intervals, availability, detection labels, stratified FN/FP, controls and
  three byte-identical repeats.
- `run.py --report` rewrites `report.json`, `report.json.sha256` and
  `provider/expected_vectors.h` byte-identically.
- `provider/` is a standalone opt-in consumer project. Its only SDK includes
  are `audio_sdk/provider_v0.h` and `audio_sdk/session_v0.h`.
  `AS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY` is **OFF** by default; `ON` compiles
  and lets the caller register one provider. No installed registry entry is
  created.
- The analysis event shape (`audio-sdk/speex-ns-advisory-analysis/0.1`) is a
  task-local side channel, never a public SDK symbol. It records timestamp,
  source interval, epoch, validity and integer milli-value separately; invalid
  is not relabelled nonspeech.
- `SOURCES.sha256` pins every file in this directory except itself.
  `contract.json` records the task contract, exact pins and artifact digests.
  `report.schema.json` and `provider/config/config.schema.json` are strict
  Draft 2020-12 schemas used for the report and fixture config checks.

## Exact source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `cpp-library/PIPELINE_DESIGN_REPORT.md` | `f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093` | Source evidence: one Speex preprocessor supplies NS and speech probability; source-reported paired AMI FN 4.44% / FP 68.84% makes the value advisory only. Historical values are not rerun here. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Analysis acceptance profile: timestamped probabilities, event intervals, valid/detection scoring, state, availability and stale events. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component record `speex-ns-advisory-probability`: analysis profile and no-gating-before-held-out-validation note. |
| `audio-benchmark-platform/plan/swarm/handoffs/SDK-SPEEX-NS-ADVISORY-PROBABILITY.md` | `af7fca22f0592814d9f3d41ca1e55d30b1c7a2ea88f53e30dd2be31a171451b4` | Synthetic/frozen evidence rights, opt-in boundary, exact comparisons and remaining release gates. |
| `audio-benchmark-platform/audio-sdk/third_party/speexdsp/include/speex/speex_preprocess.h` | `7c12339881fce3250c69af7f36b8440a8d8012976b54331b3c980b8074393b25` | Public upstream header exposing `SPEEX_PREPROCESS_GET_PROB`; inspected only. No upstream source is vendored, built or benchmarked. |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Provenance for the public v0 boundary and the invalid-probability rule; no public surface is changed here. |

Unchanged public boundary pins:

| Header | SHA-256 |
| --- | --- |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

## Reproduction

From this task directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
```

Strict schema checks (the available CPython 3.12.16 environment has
`jsonschema` 4.26.0; the default `python3` does not):

```sh
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator
for schema_path, instance_path in (
    ("report.schema.json", "report.json"),
    ("provider/config/config.schema.json", "provider/config/config.json"),
):
    schema = json.loads(Path(schema_path).read_text())
    instance = json.loads(Path(instance_path).read_text())
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(instance))
    print(schema_path, len(errors))
PY
```

Optional C boundary build (SDK build and install stay outside the worktree):

```sh
SDK=<worktree root>
TMP=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/speex-ns-advisory-check
cmake -S "$SDK" -B "$TMP/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMP/sdk-build" --parallel 4
ctest --test-dir "$TMP/sdk-build" --output-on-failure
cmake --install "$TMP/sdk-build" --prefix "$TMP/sdk-prefix"

cmake -S provider -B "$TMP/provider-off" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-off" --parallel 2
ctest --test-dir "$TMP/provider-off" --output-on-failure

cmake -S provider -B "$TMP/provider-on" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY=ON -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-on" --parallel 2
ctest --test-dir "$TMP/provider-on" --output-on-failure
```

Read-only checks from the worktree root:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-SPEEX-NS-ADVISORY-PROBABILITY
git diff --check
```

## Results summary

- Python acceptance suite: **24/24** passed.
- SDK baseline CTest: **11/11** passed.
- Consumer with `AS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY=OFF`: **1/1** passed;
  provider unlinked and unregistered, built-ins unchanged.
- Consumer with `AS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY=ON`: **1/1** passed;
  default-OFF opt-in descriptor/config gating, duplicate rejection, create-time
  rate/channel/frame/mode rejection, nonfinite/short-frame/padding/stale-epoch
  rejection, reset/drain, Python/C PCM and two-hop event parity, and three
  byte-identical pinned repeats.
- Synthetic 16 000-sample stream: 100 frames, 320-sample non-overlapping source
  windows, 50 timestamped events per hop, exact coverage with zero gap/overlap,
  and cross-hop value/interval equality with a 160-sample availability offset.
- Frozen labels and a `500 milli` analysis threshold give TP 1600, FN 1600, FP
  1600, TN 11200; speech miss rate `0.5`, false-alarm rate `0.125`. These are
  deterministic fixture scores only, not candidate accuracy or a gate result.
- Quiet speech is an explicit all-false-negative stratum; loud idle noise is an
  explicit all-false-positive stratum. Active speech has onset/offset delay 0.
  No invalid analysis event is relabelled nonspeech or included in the
  denominator.
- Dropped sequences 1 and 3 are recorded as explicit `[640, 960]` source gaps;
  no events are fabricated. Epoch-0 and post-reset epoch-1 events are rejected.
- Independent state, reset bit-identity, invalid-frame state preservation and
  different-stimulus decoupling all pass.
- Canonical report digest:
  `09a30d721d7bdfc0a9b2223751ecef37ba4936185c0ad5626d30dcca92f96b02`.
- PCM content digest:
  `5fb9c6a2ab395ce7b99378b73b323b385136405ef5266c105a48f7a6d2d16d43`.
- Hop-0 / hop-1 binary event digests:
  `d174a675daeaad467a357db6a23ee88cfd0f63cc40b5e34bc2b4eddf9513a4d0` /
  `755a38233d4fcd6d119fc214518f400cdc7f8d63d69f58bea60a4c0f44a5931f`.

## Local artifact digests (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `reference.py` | `e1d3b7712c60e9431036a6f3af0769d3f687f1595b744e308f6770caccdf9e81` |
| `run.py` | `8e4795e4e46f61bf89d85358d4b69f3d03cbb645fa45f62678f8f4eabbee5fdf` |
| `test_reference.py` | `76f5d98d916958c00d452964fb2787f98f7e793b3a779d50ae0e4072dcf1f4a0` |
| `report.schema.json` | `cf19cb05aa8e856089f41215c479f0930ef85a27c69c357d3f4fd8852036729d` |
| `report.json` (file bytes) | `09a30d721d7bdfc0a9b2223751ecef37ba4936185c0ad5626d30dcca92f96b02` |
| `report.json.sha256` (file bytes) | `26d1c3910e5775d308507481363e0ddfe21e7fdb5ec2c78df962ad89d3bec01c` |
| `provider/CMakeLists.txt` | `129998e78b0d4ae013e2f4dba91ac1afb51844781f9b881d353b5902ccc03861` |
| `provider/config/config.json` | `af3a02eab2f922bc5bfe16ef595c5f538279b079d7e4e1ceae65edad89919c03` |
| `provider/config/config.schema.json` | `fc5b8d83b0ca6fa5cd4a713e49d8ac41f1b0b26d8ebf8ccb0c33b27c8848595f` |
| `provider/config/descriptor.h.in` | `e92f3c51de042191c4f4bb131ed55a7c308ddc23ebfcc633177c26ae434face8` |
| `provider/expected_vectors.h` | `39f93f15b89f93b098b76e3f3f5dae9555d20564fdc5f35c47ca36e73de6e23a` |
| `provider/speex_ns_advisory_analysis.h` | `87702d244598ad68e4146d600f53c2e3649479299fc279e00ca1519f4556686a` |
| `provider/speex_ns_advisory_provider.c` | `b45fca3e58a9c47968b5918c789f36de2691b1687365123a72987c8b4436718d` |
| `provider/tests/test_provider.c` | `58c0efaff3ec8bcb4caa592c7401361f4538ac75db987814f590fe940556b8b8` |

## Adverse cases and explicit non-claims

Status is `synthetic-fixture-only`; candidate status is
`synthetic-reference-only`; boundary status is `opt-in-unregistered`.

- **BLK-01** — No held-out validation of the combined NS/activity settings was
  run. The advisory value is not a suppression, endpointing, cascade or
  registration gate. Reopen with a frozen permitted cohort, agreed metric
  margins, content delay and availability budgets before any control change.
- **BLK-02** — No real speech, device, listening, quality, pacing, CPU, memory,
  deadline, availability SLA or release result is claimed. The stimuli are
  analytic integer surrogates.
- **BLK-03** — No upstream SpeexDSP source, binary, model, weights or runtime
  is vendored or benchmarked here. The probability is a task-local fixed-point
  surrogate, not `SPEEX_PREPROCESS_GET_PROB` output.
- **BLK-04** — The source-reported AMI figures from the pinned design report
  are neither rerun nor used as an oracle and are not pooled with local scores.
- **BLK-05** — The C provider is unregistered and opt-in. Reopen with explicit
  provider intake, license/notice review, a versioned public-surface decision
  and independent exact-head review before registration.
- **BLK-06** — No adverse Tiny16 comparison was made. Reopen only with S10 and
  protocol clearance, an approved independent reference adapter and a
  permitted case manifest.

No board/handoff edit, other-worktree change, push, PR, merge, public benchmark
entry or release claim is included.

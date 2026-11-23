# SDK-FND-GRAPH · Versioned ordered chain/graph contract

**Status: proposal and model-free fixture only.** No public v0 header, ABI,
descriptor, registry entry, default provider, installed behavior, build file or
board/handoff file is changed. The Python executor below is a deterministic
reference model of the proposed contract. It is not an SDK engine plugin,
provider, runtime, device result or audio-quality result.

## Scope and source pins

| Source | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Ordered nodes, one linear audio path, analysis taps, delay/availability separation, lifecycle, fixed v0 format |
| `cpp-library/PIPELINE_DESIGN_REPORT.md` | `f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093` | Analysis stays a control/analysis path; component sums or unpaced Python evidence do not qualify a native chain or device |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Pipeline and Evidence acceptance profiles |
| `audio-benchmark-platform/plan/swarm/TASKS.json` | `42023c726af1189fdc00c30ccb7b585972d155c2a6aaf1b816b9e75b20cafd4e` | Freeze-time task record pin, owner, branch and reviewer (historical value; the live board changes as tasks transition) |

Pinned task base: `3c281b6674f7bf6f48b80a3c247df0241d563ff5`.
Branch: `swarm/SDK-FND-GRAPH`. Owner: `agent-graph`. Reviewer: `reviewer-graph`.
Fixed v0 remains 16 kHz mono `f32`, 160 samples per frame.

## Files

| Path | Role |
| --- | --- |
| `contract.json` | Versioned proposal `audio-sdk/ordered-chain-graph/0.1` and invariants |
| `recipe.schema.json` | JSON Schema draft 2020-12 for a versioned recipe |
| `recipe.json` | Frozen canonical recipe fixture (one audio path plus one analysis tap) |
| `fixture.py` | Deterministic model-free sequential validator/executor and canonical report |
| `test_fixture.py` | 17 offline acceptance tests, including the installed external fixture |
| `build_wheel.py` | Small stdlib-only, byte-reproducible wheel builder for the third-party fixture |
| `third_party/src/ordered_chain_fixture/` | Installable third-party stages and their own recipe copy |
| `third_party/consumer_probe.py` | External consumer run from a directory outside the source tree |
| `report.json` | Canonical report for the three-frame worked example |
| `report.json.sha256` | SHA-256 sidecar for `report.json` |

## Proposed contract

[`contract.json`](contract.json) defines `audio-sdk/ordered-chain-graph/0.1` with
engine `reference.sequential.v0`. A recipe names an ordered `audio_path` of
audio nodes and optional read-only `analysis` taps. Node IDs, provider IDs and
port IDs are unique ASCII identifiers; the audio path must match the declared
port chain. `depends_on` edges plus tap edges form a DAG. The recipe digest is
SHA-256 over restricted canonical JSON (sorted keys, compact separators, ASCII,
no NaN/Infinity); any change to order, settings, cost, delay or extra keys
changes identity.

Three facts stay independent:

* **Order** is the observed transform sequence on produced samples.
* **Delay** is an integer source-coordinate offset accumulated over audio nodes
  only; analysis cost never enters audio delay.
* **Availability** is a declared monotonic nanosecond value, never inferred
  from source timestamps or delay.

Validation rejects cycles, duplicate IDs, unavailable providers, provider/role
or delay/cost metadata mismatch, ambiguous or unknown ports, malformed or
nonfinite settings, and fixed-v0 format changes. Execution rejects duplicate
frames, stale epochs, nonfinite or badly padded input, outstanding-lease reuse,
failing ports, drain overruns and cancellation reuse. No missing result is
promoted to a pass.

## Fixture acceptance

[`fixture.py`](fixture.py) and [`test_fixture.py`](test_fixture.py) verify:

1. **Stage order** changes transform results and observed order while delay and
   availability stay fixed (`gain→limiter` versus `limiter→gain`).
2. **Delay** changes valid offsets from 80 to 100 samples while audio
   availability remains `1_000_675_000 ns` and analysis cost remains
   `40_000 ns`; analysis-only delay is excluded.
3. **Availability** is monotonic per epoch and is not derived from delay;
   nonmonotonic production is rejected.
4. **Partial frames** are conserved exactly: a 160 + 160 + 5-sample input with
   80-sample chain delay produces source intervals `[0,80)`, `[80,240)`,
   `[240,325)` and delivers 325 valid samples.
5. **Reset/drain**: drain releases a bounded tail then repeats EOS; a stricter
   call cap yields `rejected_drain_cap`; reset requires a higher epoch, releases
   side state and clears counters/cancellation state.
6. **Cancellation** records the abandoned half-open interval `[-80,80)` and 80
   valid samples, then blocks process, drain and epoch revival until reset.
7. **Side outputs**: `known` updates hold-last to `0.75`, `unknown` retains a
   `null` value without changing hold-last, nonfinite known values become
   `rejected_invalid_event` with a `null` reported value, and stale-epoch events
   are `rejected_stale_event`.
8. **Installed external fixture**: a reproducible wheel is built with stdlib
   only, installed with `pip --no-index --no-deps`, and consumed by an external
   probe run from a temporary directory; two runs emit byte-identical output.

## Reproduction

From the worktree root:

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-FND-GRAPH
cd docs/task-evidence/ordered-chain-graph
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
for f in contract.json recipe.schema.json recipe.json report.json; do python3 -m json.tool "$f" >/dev/null; done
cd ../..
git add docs/task-evidence/ordered-chain-graph
git diff --cached --check
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-FND-GRAPH
```

Observed result: **17 tests passed** in `0.4 s`; all four JSON files parse;
`git diff --cached --check` is clean; the board check passed and returned this
task as `in_progress` for `agent-graph`.

## Canonical identities

| Artifact | SHA-256 |
| --- | --- |
| `recipe.json` file | `bcdc1e4a63dc8f84a76e52b8e749948d7d8aca63ac7ad80c625e8a2cf14a1ec2` |
| Frozen recipe identity (canonical bytes) | `554a4daef1e7db10bee334a9b90cf7331a42703a952ab3136b83318469676a85` |
| `report.json` / canonical report | `a496d36fdfaae4796ab620065d424e0c03c4738da47875f2b26b84b3c4c013aa` |
| Worked-example output f32 bytes | `c64ff692f31d187f038631e2c203e98f10884039ba67db9b7a5e9f2bba5a483c` |
| Installed fixture wheel | `40fd7dac81f739189ab60d68877e8075ca5146ceb6a1513ed53a40789095cabb` |
| Third-party fixture source | `e35d055d2d9f8446781e8752f2c6bc61672b2c385e9a10d93bdc3fa24ec35859` |

External probe output (twice, identical):

```json
{"contract":"audio-sdk/ordered-chain-graph/0.1","fixture_id":"third-party/ordered-chain-fixture/0.1","installed":true,"fixture_source_digest":"e35d055d2d9f8446781e8752f2c6bc61672b2c385e9a10d93bdc3fa24ec35859","recipe_digest":"554a4daef1e7db10bee334a9b90cf7331a42703a952ab3136b83318469676a85","report_digest":"a496d36fdfaae4796ab620065d424e0c03c4738da47875f2b26b84b3c4c013aa","status":"end_of_stream"}
```

## Explicit controls and adverse cases

| Case | Observed outcome |
| --- | --- |
| `depends_on` cycle and self-cycle | `rejected_cycle` |
| Missing provider | `rejected_unavailable_stage` |
| Provider delay/cost metadata mismatch | `rejected_bad_shape` |
| Duplicate producer port, rewired input, unknown tap port | `rejected_ambiguous_port` / `rejected_unknown_port` |
| Missing root key, extra root key, non-ASCII setting, NaN setting | `rejected_bad_shape` / `rejected_nonfinite` |
| Nonfinite input sample, nonzero final padding, unknown flags | `rejected_nonfinite_input` / `rejected_bad_padding` / `rejected_bad_frame` |
| Stale epoch, process after final input, frame gap | `rejected_stale_epoch` / `rejected_bad_frame` |
| Port failure at frame 1 | `rejected_failing_port` with interval `(160,320)`, port `pcm.gain.out`, then `rejected_needs_reset` |
| Drain beyond configured call cap | `rejected_drain_cap` |
| Nonmonotonic availability and stale side event | `rejected_bad_clock` / `rejected_stale_event` |
| Nonfinite `known` side value | `rejected_invalid_event`; hold-last remains `0.75` |

Skipped by design: native C++ build/CTest, engine or provider registration,
device/token/threaded execution, real audio corpora, weights and downloads.
Skipped by environment: full draft-2020-12 semantic validation with the
`jsonschema` package (not installed offline); schema structure, required keys,
types and all recipe invariants are asserted directly in `test_fixture.py` and
`fixture.py` instead.

## Boundary and reopening

This closes only the versioned contract/reference-fixture question for one
ordered audio path with optional analysis taps. It does not qualify any native
chain, provider, detector, corpus, device, release or target workload. Reopen
when an implementation proposes a real engine/provider set with exact digests,
read-only taps, monotonic availability clocks, reset/cancel policy and a
frozen validity-labeled fixture; whole-chain or device claims additionally
require the native/native-paced evidence the pipeline design report demands.

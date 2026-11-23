# SDK-FND-ENGINE · proposal-only `engine_v1` contract and fixture

**Status: proposal and model-free fixture only.** No public v0 header, ABI,
descriptor, registry entry, default provider, installed behavior, build file or
board/handoff file is changed. The Python executor below is a deterministic
reference model of the proposed contract. It is not an SDK engine plugin,
provider, runtime, device result or audio-quality result.

## Scope and source pins

| Source | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | S11 design input: ownership, admission, FIFO, leases, epoch, cancellation, hooks, stats |
| `cpp-library/PIPELINE_DESIGN_REPORT.md` | `f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093` | Analysis/control path and native-pacing evidence boundary |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Pipeline and Evidence acceptance profiles |
| `audio-benchmark-platform/plan/swarm/TASKS.json` | `df44a7daae66a0f3cfde2f617210184dd4f3bd6ea04d941ac434b3e04a6f1935` | Task record pin at evidence generation; owner and base commit |

Pinned task base: `0673cb354cceb66f2f71faf9af7703b5a5d2fcfa`. Branch:
`swarm/SDK-FND-ENGINE`. Owner: `agent-engine`. Reviewer: `reviewer-engine`.
Fixed v0 remains 16 kHz mono `f32`, 160 samples per frame.

## Files

| Path | Role |
| --- | --- |
| `contract.json` | Versioned proposal `audio-sdk/engine-v1/0.1` and 16 invariants |
| `domain.json` | Frozen deterministic domain configuration and policy |
| `graph.schema.json` | JSON Schema draft 2020-12 for the versioned graph |
| `graph.json` | Canonical graph fixture: gain → delay audio path plus one analysis tap |
| `fixture.py` | Deterministic single-scheduler reference model and canonical report |
| `test_fixture.py` | 20 offline acceptance tests, including the installed external fixture |
| `build_wheel.py` | Stdlib-only, byte-reproducible wheel builder for the third-party fixture |
| `third_party/src/engine_v1_fixture/` | Installed external providers and their own source digest |
| `third_party/consumer_probe.py` | External consumer run from a directory outside the source tree |
| `report.json` | Canonical report for the three-frame worked example |
| `report.json.sha256` | SHA-256 sidecar for `report.json` |

## Proposed contract

[`contract.json`](contract.json) defines `audio-sdk/engine-v1/0.1` with engine
`reference.engine.v1` and ABI version `1.0`. A domain owns exactly one
scheduler, its workers and all queue/scratch memory; graphs and provider
instances are admitted before per-stream state is allocated. Each stream has
one submitter, one output consumer, three input and three output frame slots,
one in-flight processing invocation and at most one output lease. Pull is
nonblocking FIFO; a lease is immutable and released exactly once by name.
Quiesce/cancel/reset require control-thread ownership and a barrier with no
outstanding lease. Stats are caller-buffer JSON with exact decimal strings and
no pointers, paths or wall clocks. Analysis, transition and batch hooks are
admitted only with declared, proven semantics. All identities are SHA-256 over
restricted canonical JSON (sorted keys, compact separators, ASCII, no
NaN/Infinity).

## Fixture acceptance

[`fixture.py`](fixture.py) and [`test_fixture.py`](test_fixture.py) verify:

1. Artifacts parse as JSON and all file/canonical identities are pinned.
2. Worker count, stream cap, policy digest and a second scheduler are rejected;
   wrong submit/pull/control owners cannot mutate a stream.
3. Graph validation rejects cycles, fan-in, undeclared taps, extra keys, format
   changes, descriptor mismatches, hook mismatches and unknown signals.
4. An already-admitted graph/provider set and a domain at `max_streams` reject
   with zero acceptance; separate streams get independent provider state.
5. A full input queue rejects with zero acceptance and never discards an older
   frame.
6. FIFO leases are single-owner: second pull is `BUSY`, wrong/duplicate release
   is `INVALID_ARGUMENT` and frees nothing.
7. A 160 + 160 + 5-sample input with 80-sample delay conserves source intervals
   `[0,80)`, `[80,240)`, `[240,325)`; bounded drain then yields repeatable EOS.
8. A full output queue produces explicit input backpressure and leaves the
   queued input frame intact.
9. A slow stream records a deadline miss; a failing stream requires reset.
10. Quiesce drain, drain timeout and cancel interval accounting are explicit.
11. Reset requires a higher epoch, quiescence and no active lease, and clears
    queues, analysis and counters.
12. In-flight cancellation discards obsolete-epoch output and never delivers it
    to another stream.
13. Two streams share one scheduler with sequence-ordered FIFO leases.
14. Transition hooks require state-preserving proof; `observe` produces full
    audio without committing state; unsupported hooks use the scalar path.
15. Batch lanes have per-lane validity, preflight state/config validation and
    per-lane failure/deadline accounting.
16. Analysis events require the chosen producer/tap/signal/calibration, current
    epoch, bounded source age, finite probability and a monotonic clock.
17. Domain and stream stats use caller buffers, required-size rules and decimal
    strings; fatal worker failure closes admission and reports each stream.
18. The canonical report is byte-stable across independent runs.
19. A stdlib-built wheel is installed with `pip --no-index --no-deps` and
    consumed twice from outside the source tree with identical output.

## Reproduction

From the worktree root:

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-FND-ENGINE
cd docs/task-evidence/engine-v1
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_fixture.py
for f in contract.json domain.json graph.json graph.schema.json report.json; do /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m json.tool "$f" >/dev/null || exit 1; done
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator
here = Path('.')
schema = json.loads((here / 'graph.schema.json').read_text(encoding='ascii'))
graph = json.loads((here / 'graph.json').read_text(encoding='ascii'))
Draft202012Validator.check_schema(schema)
Draft202012Validator(schema).validate(graph)
print('draft2020_schema_ok')
PY
cd ../..
git add docs/task-evidence/engine-v1
git diff --cached --check
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-FND-ENGINE
```

Observed result: **20 tests passed in 0.700 s**; `json_parse_ok: 5/5`;
`draft2020_schema_ok`; three independent canonical replays produced identical
domain, graph, output and report digests; the wheel was byte-identical across
two builds and the installed probe emitted identical JSON twice;
`git diff --cached --check` was clean; the board check passed and returned this
task as `in_progress` for `agent-engine` with the pinned base and branch.

## Canonical identities

| Artifact | SHA-256 |
| --- | --- |
| `contract.json` file | `1e45f0b48696365264115a9c697b009c9e2b1c4db2158feca2b479732dd0db11` |
| `domain.json` file | `80fdce8e8fdebd46b19861fee782769234f908856e44f49ca86c7f73d15d5895` |
| `graph.json` file | `47ad272c8f4911af3e99c17e5947775f590e72b02b513cfbaa7fa0dbee51ff75` |
| `graph.schema.json` file | `0aae8d60ad252cf24952c29ebb3cb40ae97efc853279b2a338c56f311bea8e0e` |
| Frozen domain identity (canonical bytes) | `190dbf721bd18295ec835a34a463cff4232dc1db209e848de320c8aa1518b9ef` |
| Frozen graph identity (canonical bytes) | `91604256df7f75b72a20c3633a9cf775117a1882ab74be72fb895e6009db9f5f` |
| `report.json` / canonical report | `5bee590bd662aa09517ae9e6302e410ee6e55745894fcd2dacdf33fa19d4d724` |
| Worked-example output f32 bytes | `571ae035f4f5f2069b79ba5afa71d9620fadcf8b8b6b73fe3e375ffc9a8e7538` |
| Installed fixture wheel | `f440793f8bff3e1e0e658d03424a34aacdcdf1e831a5c8d15452830a02935807` |
| Third-party fixture source | `8f84f364ad0ff962e61353e75bbecbb94a671b7808566f4d3e1a5df5cf5efa93` |
| `fixture.py` file | `df3099cb1a3a66491d3fa7315d1566c251a960bcabcff6e3a237b8eb17f54b83` |
| `test_fixture.py` file | `ca945775e3013654038ca7bca85398cc4bdfedb7234d124e6968c329c617705b` |

External probe output (twice, identical):

```json
{"contract":"audio-sdk/engine-v1/0.1","domain_digest":"190dbf721bd18295ec835a34a463cff4232dc1db209e848de320c8aa1518b9ef","fixture_id":"third-party/engine-v1-fixture/0.1","fixture_source_digest":"8f84f364ad0ff962e61353e75bbecbb94a671b7808566f4d3e1a5df5cf5efa93","graph_digest":"91604256df7f75b72a20c3633a9cf775117a1882ab74be72fb895e6009db9f5f","installed":true,"report_digest":"5bee590bd662aa09517ae9e6302e410ee6e55745894fcd2dacdf33fa19d4d724","status":"end_of_stream"}
```

## Explicit adverse outcomes

| Case | Observed outcome |
| --- | --- |
| Second scheduler, `worker_count != 1`, bad policy digest | `ValueError` before any stream exists |
| Cycle, audio fan-in, undeclared tap, malformed hook/signal/delay | `INVALID_ARGUMENT` at admission |
| Duplicate graph/provider set, domain at `max_streams` | `RESOURCE_EXHAUSTED`, zero acceptance |
| Input queue full, output queue full | `RESOURCE_EXHAUSTED` / `NOT_READY`, older frames retained |
| Second pull, wrong or duplicate lease release | `BUSY` / `INVALID_ARGUMENT`, no slot freed |
| Slow stream | deadline miss recorded in stream and domain stats |
| Provider failure at frame 1 | `BACKEND_FAILURE`, `NEEDS_RESET`, no process revival |
| Quiesce drain with full output, then after release | `QUIESCE_TIMEOUT`, then `OK` after bounded drain |
| Quiesce cancel | abandoned interval `[80,320)` (240 samples) accounted once |
| In-flight obsolete epoch | output discarded, cancellation recorded, no cross-stream delivery |
| Reset with equal epoch, active lease or unquiesced stream | `INVALID_ARGUMENT` / `BUSY`; only a higher epoch succeeds |
| Batch preflight alias/config conflict | every lane rejected before any lane state changes |
| Batch lane failure, missed deadline | per-lane `BACKEND_FAILURE` / `deadline_miss` |
| Nonfinite, out-of-range, stale or unselected analysis event | explicitly rejected; no counting as accepted |
| Fatal worker failure | admission closed, per-stream failure records, clean close after removal |

Skipped by design: native C++ build/CTest, engine or provider registration,
public v0 ABI/header/registry/default-provider changes, device/token/threaded
execution, real audio corpora, weights/downloads, pacing, release and audio
quality claims. Skipped by environment: hosted CI matrix, `reuse lint` (the
`reuse` CLI is not installed offline) and contributor-intake checks requiring a
GitHub event payload. The local quality checks above are mirrored exactly; no
missing check is promoted to a pass.

## Boundary and reopening

This closes only the versioned proposal/source-independent fixture question for
engine admission, ownership, FIFO, leases, epoch, cancellation, hooks and
stats. It does not qualify any native engine, provider, detector, corpus,
device, release or target workload. Reopen when an implementation proposes a
real engine/provider set with exact digests, ownership and queue semantics,
lease discipline, reset/cancel policy and frozen validity-labeled fixtures;
whole-chain or device claims additionally require the native/native-paced
evidence the pipeline design report demands.

<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Bench subprocess protocol: task-local synthetic evidence

Status: `proposal_only_not_qualified` / `incomplete` / release gate `DEFER`.
This is a developer-facing tool and evidence package, not a benchmark
submission, release claim or production exposure. No case qualifies a
candidate, and a missing result never qualifies one.

## Exact scope

This directory is the only write scope:
`docs/task-evidence/bench-subprocess-protocol/` on the pinned base
`bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`, branch
`swarm/SDK-BENCH-SUBPROCESS-PROTOCOL-SANDBOX-AND-ASSET-IDS`.

No public API, ABI or header changed. Installed v0 remains 16 kHz mono
float32 with 160 samples per frame. No descriptor registry or default,
provider registration, C boundary, installed-v0 behavior, audio-bench source,
board, handoff, ruleset, `main` or other task was changed. `adapter.json` and
`provider.json` are synthetic, evidence-only fixtures: unlinked, unregistered
and default-OFF. No production callback is registered and no SDK session is
created.

Evaluation execution and production callbacks stay distinct. The harness
validates descriptors, requests and synthetic result manifests; it never
resolves the symbolic entrypoint, spawns a subprocess, uses a real runner,
reads a real corpus, invokes a licensed runtime or runs a target-device
workload.

## Bridge descriptor

The descriptor fields are declared in `contract.json` under
`bridge_descriptor_fields` and instantiated in `adapter.json`:

- `descriptor_id`: immutable evidence descriptor identifier.
- `protocol`: only `audioml-adapter/1` is accepted.
- `cli`: one attempt, `--request` then `--result`; no implicit retry.
- `workspace_root`: symbolic `/workspace`; resolution is restricted to
  `workspace_root_relative`.
- `entrypoint`: symbolic, evidence-only path; never resolved or executed.
- `attempt_dir`: symbolic `/attempt/<request_id>` writable root.
- `writable_roots`: explicit allowlist; must contain only the attempt dir.
- `read_grants`: explicit caller-owned input, asset, code and environment
  roots; duplicates, traversal and ungranted paths fail closed.
- `deny_network`: must be true.
- `downloads`: must be `denied`.
- `nested_sandbox_policy`: must be `fail_closed`, with an explicit blocked
  reason when a nested profile is denied.
- `source_paths`: explicit workspace-relative source roots only.
- `production_callback`: must be `none`.

Assets carry `asset_id`, `sha256`, `byte_count`, `rights_ref` and `location`.
The synthetic asset ID is content-derived from deterministic bytes
(`synthetic.asset.frame-0001`); rights are `synthetic://task-local-fixture`.
Hash mismatches, byte-count mismatches, duplicate IDs, unknown IDs, path
escapes, missing rights and download requests are rejected. Optional
selections are omitted rather than defaulted; explicit `null` or unknown
selections are rejected. Result manifest digests and asset IDs/hashes are
validated before any success status.

## Reproducible inputs and controls

`fixture.py` generates 33 cases from integer seeds with a deterministic
xorshift32 stream. No OS entropy, clock, network or real file payload is
used. Cases cover valid requests, omitted optional selections, malformed and
duplicate-key JSON, nonfinite JSON constants and metrics, frame shape
violations, asset identity failures, sandbox escapes, network/download
violations, nested-sandbox failure, production-callback declarations, result
manifest failures, a blocked nested sandbox and a missing result.

Statuses are `ok`, `ok_omitted`, `blocked`, `rejected` and `incomplete`; every
record has `qualified: false`, and the report records
`qualified_candidates: 0`. `missing_result` is `incomplete` with reason
`result_missing`.

`SOURCES.sha256` pins all workspace and task-local inputs with explicit
`workspace:` and `pkg:` prefixes. The pinned protocol source is
`adapters/README.md` at SHA-256
`24d8915f0ff59ee026ef86b396f64f1b3e68d3a5678f98a353273b712f09e1ee`; it
documents the external `audioml worker` command, which is referenced only as
provenance and is not invoked here.

## Tool version, install and provenance

- Name/version: `bench-subprocess-protocol evidence harness` `0.1.0`.
- Authoring runtime: Python `3.11.5` at
  `/Users/htsakanyan/.pyenv/shims/python3`.
- Install: none. Copy or clean-checkout this directory; standard library only.
- Provenance: no third-party package, download, network access, corpus,
  licensed runtime or target-device workload.

`run.py --version` prints the tool profile. `run.py --demo` shows one
typical API validation call.

## Typical CLI and API use

From this directory:

```sh
python3 run.py --report
python3 run.py --sources
python3 run.py --crosscheck
python3 run.py --demo
python3 run.py --version
python3 -m unittest -v test_reference.py
python3 verify.py
python3 check_licensing.py
```

Typical API use validates caller-owned synthetic input before any decision:

```python
import fixture, reference
item = fixture.build_fixture("valid_without_optional")
reference.validate_descriptor(item["descriptor"])
status = reference.validate_request(item["request"], item["descriptor"])
reference.validate_result(item["result"], item["request"], item["descriptor"], status)
decision = reference.evaluate_case(item)  # qualified is always False
```

Callers own request IDs, manifests, frames, asset bytes and grants. The tool
does not copy them into an attempt directory or infer a default selection.
Malformed, nonfinite, unverified, ungranted or missing required inputs are
reported with stable reason codes and never qualify.

## Clean-checkout verification

On a clean checkout of the pinned base with this directory present:

```sh
cd docs/task-evidence/bench-subprocess-protocol
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 run.py --sources
python3 run.py --crosscheck
python3 verify.py
python3 check_licensing.py
```

`verify.py` copies only this package to a temporary directory, reruns the
unit tests, regenerates the report and rechecks source pins; the regenerated
report and sidecar must be byte-identical. `--crosscheck` performs three
cold-start regenerations and byte comparisons. Any JSON file is strict:
duplicate keys, non-object roots and nonfinite constants are rejected.

## Evidence separation

- Compile/build: baseline Release build, install and `ctest` are recorded
  separately as 11/11 passing at the pinned base. This pure-Python package
  adds no compile/install step and claims no consumer opt-in boundary.
- Synthetic runtime: only deterministic in-memory fixtures. No external
  runner, real corpus, licensed runtime or target-device workload was used.
- Measured workload support: `unclaimed`. No latency, throughput,
  speech-quality, device or release measurement is claimed. Release remains
  `DEFER` before any production exposure.

## Digests

Report SHA-256
`01fa0a15917c2cdfd31bf518f85ecc813e9ab16ea1faad3eb49c70118bc48dd2`.
The sidecar is `report.json.sha256`; its digest is regenerated and compared by
`run.py --report`, `run.py --crosscheck` and `verify.py`. Task-local source,
descriptor and evidence digests are listed in `SOURCES.sha256`.

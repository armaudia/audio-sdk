# SDK-SURVEY-ENG-04 — ENG-04 task-local coverage evidence map

Proposal-only, incomplete and **not qualified** coverage evidence for
`ENG-04 — Codec/packetization, FEC, DTX and comfort noise`. This package is a
deterministic crosswalk over already pinned catalog, component and fixture
evidence. It does not load a codec, read audio, open a device, execute a
network trace, listen, benchmark the SDK, or make a release claim.

## Boundary

- Only `docs/task-evidence/survey-eng-04/**` is added. No board, handoff,
  descriptor, provider registry, default, ABI, build option, CMake or CI file is
  changed.
- Public v0 remains 16 kHz mono float32 at 160 samples/call; no SDK callback is
  invoked. `registered=false`, `enabled_by_default=false`,
  `default_selected=false`, `descriptor_settings={}`, and every change flag in
  `report.json.release_boundary` is `false`.
- No RFC body, Opus runtime/dylib, DRED/LACE/NoLACE/deep-PLC asset, SE-NAC or
  Lyra checkpoint, real speech, captured packet trace or device capture is
  vendored, downloaded or generated.
- The one linked follow-up is an **open bounded feasibility question**, not an
  implemented capability and not a new component assignment.

## What is matched

- **Original method families** are taken verbatim from the pinned structured
  catalog: classic `Codec negotiation; packet duration; FEC; silence
  suppression/comfort noise` and ML `Neural codec/redundancy variants are
  conditional leads`. The `report.json.method_family_audit` records each
  family's component match, local outcome, reported outcome and missing
  evidence.
- **Named source leads** S43 (RFC 7587 Opus RTP), S44 (RFC 7874 WebRTC audio
  requirements) and S30 (Opus 1.5 neural enhancement/loss recovery) are matched
  to registered component records. S30 is scoped to the Opus 1.5 family only;
  SE-NAC and the Lyra/Complex-Bin2bin leads come from the local candidate
  inventory and are not attributed to S30. Their URLs and access scopes come
  from the pinned catalog and source ledger; the RFC bodies and codec assets are
  not reproduced here.
- **Historical executions** are separated into existing local fixtures
  (`SDK-FND-ELASTIC`, `SDK-OPUS-1-4-STANDARD-DECODER-PLC`, the synthetic PLC
  controls), a pinned blocked attempt (`SDK-PIPE-RECEIVE`) and pinned
  source-reported research rows. Nothing from a source report is pooled with a
  local record. Candidate-matrix rows 26-30 are cited by their actual row
  numbers: WaveFit (26, out of scope), Lyra (27, blocked), Complex-Bin2bin (28,
  blocked), conventional controls (29) and Opus 1.4 (30).
- **Components** are matched by their registered task IDs, board status and
  plan notes observed at claim time, and each family, lead and historical
  execution carries explicit `component_ids` and a `match_basis`. The mutable
  plan board is not pinned, so board status is provenance rather than a frozen
  input; only the existing local fixture evidence is pinned and byte-checked.
  Components with no local evidence are recorded as considered or blocked, not
  as evaluated.

## Comparison inputs, controls and outcomes

`report.json.comparison_inputs` records session controls, packet fields and
erasure masks that a real codec/packet comparison would require, and lists what
is absent locally. PCM/session controls are kept distinct from encoded packets
and playback state; redundancy-assisted recovery and blind recovery are kept in
different groups.

`report.json.controls` distinguishes identity/no-loss, blind PLC,
redundancy-assisted FEC, DTX/CNG transition and invalid-state rejection. The
existing elastic fixture records a single-erasure XOR parity recovery with
exact timestamp and explicit rejection of a two-packet burst; that is a
model-free packet fixture, **not** codec FEC or RTP evidence. Source-reported
Opus screen values, RTF figures and candidate-matrix conclusions are recorded
only as `source_reported_not_reproduced`.

No outcome was measured in this task. Existing fixture outcomes are labelled
`existing_local_fixture_recorded_in_repo_not_rerun`; absent or externally
reported values are labelled `not_measured_here` or
`source_reported_not_reproduced`. All six reopening gates remain blocked.

## Actionable gap without a component owner

[FEASIBILITY-ENG-04-01](followups/FEASIBILITY-ENG-04-01.md) records the classic
`codec negotiation` family, which has no registered component owner. It is a
bounded question about specifying a negotiation/parameter-agreement state model
at the existing PCM/packet boundary. It requires owner assignment, an exact
packet contract and matched trace, rights clearance and review before any
execution. No capability is implemented by this follow-up.

## Pinned sources and boundary

Paths for `source:` pins are relative to
`/Users/htsakanyan/workspace/audio/audioml`; other paths are relative to the SDK
worktree. `SOURCES.sha256` pins the catalog, readable catalog, backlog, source
ledger, research notes, the blocked receive handoff, SDK boundary files,
existing component evidence and all task-local artifacts. `verify.py` fails
closed on a missing, stale, malformed or duplicated pin, on
non-canonical/non-finite/duplicate-key JSON, on a stale digest sidecar, on
licensing gaps, on forbidden claims, on an unpinned or absent historical path
and on any worktree change outside this directory.

## Files

- `contract.json` — task-local proposal manifest, scope, boundary and gates.
- `reference.py` — frozen catalog crosswalk and canonical report model.
- `run.py` — regenerates `report.json`, its digest sidecar and `SOURCES.sha256`.
- `report.json` / `report.json.sha256` — canonical evidence map and digest.
- `SOURCES.sha256` — SHA-256 manifest for all source, boundary and local files.
- `test_reference.py` — deterministic acceptance tests.
- `verify.py` — read-only strict verifier.
- `followups/FEASIBILITY-ENG-04-01.md` — bounded, unowned feasibility follow-up.
- `*.json.license` / `SOURCES.sha256.license` — REUSE sidecars for generated JSON.

## Reproduction

Run from this directory with the pinned interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-SURVEY-ENG-04
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output <scratch-outside-worktree>
reuse lint
git diff --check
```

`run.py report.json`, `run.py sources` and `run.py all` are idempotent. The
canonical report digest is the content of `report.json.sha256`; the manifest
digest is SHA-256 of `SOURCES.sha256` itself.

## Gates

All gates remain blocked: codec-negotiation owner assignment, codec runtime
rights, captured negotiation/packet/erasure trace, executed FEC/DTX/CNG with
separate redundancy-assisted and blind groups, independent listening, and
target timing plus explicit release decision. Missing evidence never qualifies
a candidate. This package remains
`proposal_only_coverage_map_incomplete` / `not_qualified` / `DEFER`.

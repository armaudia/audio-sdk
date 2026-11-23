# SDK-FND-ANALYSIS · Versioned analysis events

**Status: proposal and model-free fixture only.** No public v0 header, ABI,
descriptor, installed behavior, scoring implementation or runtime default is
changed. The fixture is a deterministic Python model of the proposed typed
analysis surface; it is not an SDK provider or a VAD accuracy result.

## Scope and source pins

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/plans/F02/vad_accuracy_contract.md` | `f6650aa3206cb694dffc4b429e0fe1f34c5ecd097cbfda7e522083cad7be1cec` | Decision intervals, scored/unknown regions, denominators, stale/invalid handling |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `fe1839163b80c899a915c56b371e03228230246de00042ff058d7bcff9a5bf4f` | v0 epoch, source coordinates, availability and read-only PCM boundary |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Analysis profile: validity, exact intervals, availability, dropped/stale events |

Pinned task base: `00cc09c56b34ab49c7db20b177e322eb002c16da`.
The historical VAD corpus is **not** accuracy-ready: unlabeled gaps are unknown,
not nonspeech. No false-alarm or full-accuracy winner is claimed.

## Proposed interface

[`contract.json`](contract.json) defines `audio-sdk/analysis-events/0.1`. Each
event carries `event_id`, `kind`, `producer_id`, `tap_id`, `epoch`,
half-open source interval, `value`, explicit `validity`, monotonic
`available_ns`, clock ID and `config_digest`. Kinds cover speech probability,
speech events, rate events and transcript events. There is no process-global
latest-event register: identity includes producer, tap and epoch.

Read-only PCM is enforced structurally: `AnalysisBus` stores an immutable tuple
and exposes only a snapshot and digest. Publishing analysis does not mutate
speech audio. Known events require finite values and availability; unknown
events are retained but excluded; invalid events are rejected.

## Fixture acceptance

[`fixture.py`](fixture.py) and [`test_fixture.py`](test_fixture.py) verify:

1. A speech event `[150,330)` contributes exact overlaps `10,160,10` to 160-sample frames, with no hop rounding.
2. Lower-epoch and pre-stream-start events are rejected; unknown/invalid handling is explicit; per-clock availability must be monotonic.
3. Audio bytes and digest remain unchanged after analysis publication.
4. VAD scores only inside scored regions: gap-free Boolean hypothesis decisions must cover that union without overlaps or spill. A worked 480-sample case gives `TP=80, FN=140, FP=80, TN=180`.
5. Unknown samples are counted but excluded; zero denominators return `value: null` with `no_scored_speech` or `no_scored_nonspeech`.
6. Reports are canonical JSON with a stable SHA-256 digest.

## Reproduction

```sh
cd docs/task-evidence/analysis-events
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
```

Expected: 8 tests passed.

## Boundary and reopening

This closes only the versioned contract/fixture question. It does not qualify
any detector, corpus, device or target workload. Reopen for implementation when
an exact producer/config digest, read-only tap, monotonic availability clock,
stale/reset policy and frozen validity-labeled fixture are supplied. Full VAD
accuracy additionally needs the corpus coverage statement, rights review and
held-out partition required by the linked contract.

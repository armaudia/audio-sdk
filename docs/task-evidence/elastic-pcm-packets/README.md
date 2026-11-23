# SDK-FND-ELASTIC · Variable-count PCM and packet timing

**Status: proposal and model-free fixture only.** No public v0 header, ABI,
descriptor, provider registry, queue capacity, codec or default behavior
changes. This is a deterministic Python model of a separate versioned
interface.

## Scope and source pins

| Source | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `fe1839163b80c899a915c56b371e03228230246de00042ff058d7bcff9a5bf4f` | Exact counts, explicit buffers, bounded queues, finite drain, no silent fill |
| `cpp-library/include/audio_enhance/audio_enhance_playback.h` | `45ff86b1fd84873519552e507dcd8b82c4079c445e24add80e4717538f8000db` | Playback FIFO counters, bounded occupancy, underrun/concealment separation |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Restoration/pipeline acceptance: erasure bursts, decoded intervals, timing bounds |

Pinned task base: `00cc09c56b34ab49c7db20b177e322eb002c16da`.
The historical local packet-loss screen used synthetic erasures; no network,
mobile device, codec-native PLC or release qualification is reproduced.

## Proposed interface

[`contract.json`](contract.json) defines `audio-sdk/elastic-pcm-packets/0.1`.

- `ElasticStream` admits variable-count contiguous PCM chunks, maps output
  samples to input source samples with an exact `Fraction` ratio, enforces a
  bounded pending-input limit, and pulls finite output until EOS.
- `PacketBlock` keeps timestamped sequence packets and a single-erasure XOR
  parity packet separate from PCM. Recovery preserves sequence and timestamp;
  larger bursts fail explicitly instead of being concealed.

Ratio updates affect only later chunks, so already admitted chunks never move.
Each stream owns its ratio, counters and timeline; there is no shared clock.

## Fixture acceptance

[`fixture.py`](fixture.py) and [`test_fixture.py`](test_fixture.py) verify:

1. Variable 80/160/240-sample chunks at ratio 1 map to identity with source indices `0..479`.
2. Ratio `1 → 2` changes only the second 160-sample chunk; output-to-source mapping stays monotonic.
3. Invalid ratios and noncontiguous source starts are rejected with zero consumption.
4. A full bounded queue rejects new input with `rejected_backpressure` and does not drop older input.
5. Ratio `0.5` produces a finite 320-sample tail, then EOS; no extra flush samples appear.
6. Two streams with different ratios stay independent.
7. One packet erasure is recovered from parity with the exact original timestamp; a two-packet burst is `rejected_unrecoverable`.
8. Packet recovery and PCM admission remain separate, and reports are canonical.

## Reproduction

```sh
cd docs/task-evidence/elastic-pcm-packets
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
```

Expected: 9 tests passed.

## Boundary and reopening

This closes only the versioned contract/fixture question. It does not qualify
Opus PLC, codec operation, jitter buffering, playback-rate engines, device I/O
or any pipeline. Reopen for implementation with a pinned codec/PLC asset or
explicit no-codec scope, declared timestamp domains, bounded buffer policy,
finite flush recipe, erasure/right/rights scope and target-runtime evidence.

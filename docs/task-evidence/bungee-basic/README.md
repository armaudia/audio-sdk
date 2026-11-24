<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Bungee Basic rate-map fixture

Proposal-only offline evidence for `SDK-BUNGEE-BASIC`. The fixture produces
exact source/output intervals for rate schedules, including rate changes and
a final partial window. It models the public v0 geometry (16 kHz mono float32,
160 samples per call); variable output is an offline fixture, not a claim
about what the installed callback accepts. Nothing is registered or enabled.

The linear interpolation control deliberately **changes pitch**. Its tone,
two-tone music proxy, impulse and silence are generated, not real audio.
Cumulative rational duration prevents per-hop rounding drift. The impulse
probe measures position and spread, not audibility. Rebuffer counts come from
a fixed synthetic arrival schedule, not device timing.

Historical Bungee Basic results and MPL-2.0 context are pinned in
`SOURCES.sha256`. No Bungee code, binary, model or real audio is shipped or
invoked; the control is not a substitute or a parity oracle.

## Reproduce

From this directory, with Python 3.12.16:

```sh
python3.12 -B run.py report.json
python3.12 -B -m unittest -v test_reference.py
python3.12 -B verify.py
```

`reference.py` builds the mapping and observations; `run.py` writes the
canonical report and sidecar; `test_reference.py` checks six behaviors,
including three independent cold starts; `verify.py` verifies the pins,
licensing, scope and report reproduction. `report.json.sha256` records the
digest of the exact report bytes.

Native parity, unfamiliar speech/music, transient audibility, paced playback
and provider intake are blocked. See `blocked_gates` in the report for the
evidence each requires. This fixture does not qualify Bungee Basic.

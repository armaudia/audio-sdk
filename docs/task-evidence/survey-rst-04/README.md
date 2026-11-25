<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-RST-04 — packet-loss concealment and gap-recovery evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`RST-04` (Packet-loss concealment and gap recovery, legacy family `F10`). It
matches the catalogued classic and ML method families, both named source leads
(`S30`, `S41`) and the historical local or source-reported executions to
existing components. It creates **no new execution, model, corpus, codec,
checkpoint, provider, processor, ABI, default, build, CI, board, handoff or
release change**.

Survey owner: `agent-SURVEY-RST-04`; independent reviewer:
`reviewer-SURVEY-RST-04`. Claim base: audio-sdk
`39b8885da4fc3ef8e27becf5df5f0658da3baf65`; branch
`swarm/SDK-SURVEY-RST-04`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## Original method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: zero-fill, hold and linear interpolation | `zero-fill-plc` (evaluated): 17 erased frames on a 250-frame frozen cohort, SI-SDR 11.79 dB / STOI 0.877; `linear-interpolation-plc` (evaluated): 9 erased frames, SI-SDR 11.82 dB / STOI 0.950 | Generated 16 kHz stimuli with exact supplied masks; no real speech, codec or device timing |
| Classic: pitch-period repetition and extrapolation | `pitch-period-repeat-plc` (evaluated): 11 erased frames, SI-SDR 22.14 dB / STOI 0.851, with a 0.101 concealed RMSE and explicit unvoiced zero-fill fallback | Causal synthetic reference; not a codec or production PLC |
| Classic: autoregressive forward prediction | `autoregressive-plc` (evaluated): 9 erased frames, SI-SDR 13.15 dB / STOI 0.954; 12-clip EARS codec-matched screen put AR at 3.48/2.23 dB SI-SDR on isolated/burst loss | Order-16 synthetic predictor; the EARS screen includes codec distortion |
| Classic: codec-native decoder concealment | `opus-1-4-standard-decoder-plc` (evaluated): 12-clip EARS screen at 24 kbit/s with Opus 1.4 PLC 2.39/0.92 dB SI-SDR and 0.913/0.848 STOI on 10% isolated/two-packet bursts | `libopus 1.4` runtime is historical provenance; no binary is vendored or invoked here |
| Classic: redundancy-assisted and receive-side gap recovery (separate group) | `opus-dred`, `opus-packetization-fec-dtx-and-comfort-noise`, `webrtc-neteq` (considered): single-erasure XOR parity in `elastic-pcm-packets` recovers one packet and rejects a two-packet burst | Redundancy, jitter buffering and playout are not decoder PLC; no encoded stream, trace or NetEq run |
| ML: neural prediction/resynthesis | `complex-bin2bin-generative-plc`, `lyra-ii-v2-codec-plc` (blocked/considered) | No exact checkpoint, codec-aligned loss benchmark, rights review or local output |
| ML: codec-integrated neural loss recovery (`S30`) | `opus-deep-plc`, `opus-1-5-lace`, `opus-1-5-nolace` (considered); `opus-dred` is redundancy-assisted | Source-reported only; no compatible Opus 1.5 build, feature stream, packet trace or score |

`report.json` holds the full records: both catalogued branches, both source
leads, thirteen censused components, ten comparison inputs, ten controls, five
assets, seven historical executions, six reported outcomes, nine gaps,
sixteen linked board rows and all eight blocked release gates. Historical
numbers are transcribed verbatim from pinned reports with their original
scope; they are **not rerun, pooled into a benchmark or promoted to a pass**.

## Evidence classes and failure envelope

- **Historical local real-audio screen:** the 12-clip EARS codec-matched
  packet-erasure screen is transcribed from
  `research/voice-enhancement-20261101/agent-opus-plc/REPORT.md`. It used
  stateful 20 ms Opus frames at 24 kbit/s, deterministic 10% isolated and
  ~16.7% two-packet erasures, FEC disabled and a compensated 104-sample codec
  delay. Opus 1.4 PLC did not dominate zero-fill or AR on SI-SDR and traded
  STOI by loss pattern; n=12 exploratory intervals overlap.
- **Historical local pilot, not reproduced:** the earlier RST-04 pilot means
  (AR 10.35 dB and pitch-repeat STOI 0.9207 at isolated 10% loss; AR 7.43 dB
  and pitch-repeat STOI 0.8690 at 17% burst loss) are transcribed separately
  from the codec-matched screen. They are not the same scoring and are not
  pooled.
- **Historical local paired synthetic:** the five frozen 250-frame fixtures
  (zero-fill, linear, pitch, AR and the decoder-PLC-style surrogate) use exact
  supplied masks, clean references, 16 kHz/160-sample frames and explicit
  concealed-slot accounting. Every historical row names the censused
  component it exercised.
- **Clean transparency:** identity/no-loss delivery is bit-exact on valid
  content in the local fixtures. SI-SDR against an exact reconstruction is
  `None` with reason `exact_reconstruction`, never invented.
- **Packet parity:** `elastic-pcm-packets` recovers one erasure from a single
  XOR parity packet with its original timestamp and rejects a two-packet burst
  as `rejected_unrecoverable`. PCM admission and packet recovery remain
  separate; this is not codec FEC or DRED.
- **Adverse:** missing, short, wrong-shape, zero-length, nonfinite,
  bad-padding, stale-epoch, duplicate, out-of-order, future, after-final and
  over-burst frames are rejected without changing stream state. Concealed
  slots carry result flag `4` and `valid_count=0` and never count as valid
  content.
- **Source-reported only:** S30 (Opus 1.5 deep PLC/DRED/LACE/NoLACE) and S41
  (WebRTC NetEq) document candidate scope; no compatible build, checkpoint,
  packet trace, playout log or numeric parity follows from a claim.
- **Not present:** human ratings, WER, rights-qualified paired real-speech
  loss cohorts, captured network traces, jitter buffers, codec feature
  streams, redundancy budgets, target-device timing, weights or a new
  execution. The decoder-style fixture is deliberately **not Opus** and makes
  no Opus runtime claim.
- The category boundary is explicit: track which information is available.
  Plausible gap filling does not prove recovery of the original words.

## Bounded gaps and board links

Nine gaps are recorded. `G01`-`G05` link existing feasibility, pipeline and
foundation rows for captured traces, codec-integrated neural recovery,
generative PLC staging, redundancy accounting and NetEq playout. `G06`-`G09`
link existing research-control and foundation rows for real-speech listening,
target-device timing, end-to-end concealed/valid accounting and provider
intake. Those links are scoping leads only: no processor is enabled, no
capability is implemented, and no missing result is promoted. Board status is
excluded from all gates; only linked `id`/`title`/`mode` are projected to a
stable digest. The board file is referenced by path and never hashed into
canonical bytes, so status edits elsewhere in the swarm cannot change this map
or break its digest.

## Release boundary

Keep waveform baselines, codec-native PLC, neural resynthesis and
redundancy-assisted recovery as separate subcases. Keep generated fixtures,
the historical EARS screen, the earlier pilot and source-reported model claims
distinct. No public benchmark, quality, device, listening or release claim is
made. No assets, real audio, codecs, weights, provider enablement, installed
v0 change, ABI, registry, default, shared build or CI change is included. All
files are inside this task directory; board, handoff and reviewers were not
changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical
output, adverse rejections and three cold-start repeats. JSON and manifest
files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-rst-04
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
git diff --check
```

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched.
Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media or codec assets. `AUDIOML_WORKSPACE_ROOT` can point to
the enclosing `audioml` checkout if automatic discovery is unavailable.

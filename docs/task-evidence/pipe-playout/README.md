<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PIPE-PLAYOUT — buffered fixed-rate playback readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`SDK-PIPE-PLAYOUT` ("Buffered fixed-rate playback"). Decision: **DEFER**;
`status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies the
candidate.

This package does not link, import, build, load or execute Bungee Basic, a
native library, an SDK provider or a pacing device. It reads no real audio,
corpus, model, weight or annotation asset. It contains only a deterministic
stdlib reference that validates pipeline admission and an explicit 1× bypass on
small synthetic fixed-point fixtures. The Bungee stage is not admitted, so no
rate change occurs and no rate result exists. Only
`docs/task-evidence/pipe-playout/` is written; no provider, registry,
descriptor, public header/ABI, shared CMake, CI workflow or installed v0
behavior changes.

## Exact external blocker

The recipe is:

```
timestamped PCM -> optional advisory speech/rate annotation ->
explicit fixed-rate Bungee Basic -> peak limiter
```

Bungee Basic **source** and a local static build exist outside the worktree and
are pinned as provenance. They are not an admitted runtime artifact:

- Source revision `61f52bf34be577d189d388772ddfa3696dee77d8`, tree
  `c8edb5f21ad58472d8ce6f635fa3e6c707474ca6`, upstream `LICENSE` pinned.
- Local `build-rel/libbungee.a` is 88,880 bytes, SHA-256
  `bd217d069a458436ed8444bf6cb83a3d79889b4a32bff768b9015f956452fae1`.
- No admitted build recipe/toolchain record, binary-digest approval, MPL-2.0
  notice/source-availability/relink decision or product-use review exists for
  this pipeline. Nothing is linked or invoked here.

The other required artifacts are absent:

- No rights-cleared natural speech, music, transition or silence cohort with
  tagged impulses, source timestamps, terms and an output-use decision. AMI
  research clips are unreviewed and are not read.
- No qualified advisory speech/rate annotation provider, model, asset or
  accuracy result. `SDK-FND-ANALYSIS` defines event shapes only.
- No qualified peak limiter integration for this exact chain.
  `SDK-PEAK-LIMITER-REFERENCE` is a separate approved component.
- No deterministic end-to-end pipeline host/result, listening study,
  target-device timing/resource measurement or provider intake.

Eight blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Admitted Bungee Basic runtime: exact source revision/tree, build recipe/toolchain, binary digest/byte count, MPL-2.0 distribution decision and product-use review. |
| `BLK-02` | Rights-cleared natural speech, music, transition and silence cohort with tagged impulses, source timestamps, digests, terms and output-use decision. |
| `BLK-03` | Qualified advisory annotation provider/policy with pinned assets, coverage/accuracy, confidence/unknown semantics and no-mutation proof. |
| `BLK-04` | Qualified limiter integration for this exact chain with transparency, peak, recovery and finite-output evidence. |
| `BLK-05` | End-to-end host/result for 1×, fixed rates, steps/ramp, finite flush, duration/pitch and tagged-impulse delay. |
| `BLK-06` | Permitted listening/naturalness/transition study and real-audio validation of unknown-annotation no-mutation. |
| `BLK-07` | Paced playback and target-device buffering, rebuffer, drift, underrun, deadline and resource/energy measurement. |
| `BLK-08` | Separate OFF-by-default provider intake with no shared-surface change and independent exact-head review. |

**Reopen condition.** A caller supplies the admitted Bungee runtime and limiter
integration, a rights-cleared playback cohort, a qualified annotation policy,
the deterministic end-to-end host/result, a permitted listening study, paced
target-device measurements, and a separate OFF-by-default intake with
independent review. Until then this task stays `DEFER`.

## What this package actually verifies

`reference.py` models only the admitted bypass policy:

- **Admission:** 16 kHz mono, 160-sample frames, a final partial frame of
  1–160 samples, a positive bounded buffer and a requested fixed rate in
  0.5×–2.5×. Bad geometry, frame length, rate, annotation or nonfinite samples
  are rejected without state advance.
- **1× bypass:** accepted samples are returned bit-exactly, with zero duration
  error, zero gaps and zero tagged-impulse delay. This is a synthetic
  fixed-point control, not an installed float32 SDK or real-audio result.
- **Unknown/missing annotation:** audio is left unedited. Known annotation also
  leaves audio unedited because the Bungee stage is not admitted.
- **Unavailable capability/buffer:** an explicit 1× bypass is recorded with
  `bungee_runtime_not_admitted` or `buffer_unavailable`. A requested rate change
  never executes.
- **Limiter:** a transparent reference placeholder only; no limiter result is
  claimed.
- **Qualification:** every case has `qualifies=false`; the Bungee stage is never
  invoked.

Seventeen deterministic cases: 9 accepted bypasses (including 1×, 1.25×, 1.5×
requests, unknown/missing annotation, speech/music/transition proxies, a final
partial frame and an unavailable buffer) and 8 rejections (invalid/unsupported
annotation, nonfinite sample, missing frames, missing rate, wrong frame length,
bad geometry, rate out of range). Zero qualify.

## Eight blocked release gates

| Gate | Blocked subject |
| --- | --- |
| `RG-01` | Bungee source/runtime provenance, MPL-2.0 distribution and product-use review. |
| `RG-02` | Rights-cleared playback cohort, annotation manifest, tagged impulses and recipe identity. |
| `RG-03` | Admitted Bungee Basic build and qualified limiter integration. |
| `RG-04` | Fixed-rate duration/pitch, rate steps, finite flush, gaps and tagged-impulse delay. |
| `RG-05` | Natural speech, music and transition scoring with adverse/missing/nonfinite controls. |
| `RG-06` | Listening/naturalness/transient study and real-audio unknown-annotation validation. |
| `RG-07` | Paced playback and target-device timing/resources. |
| `RG-08` | Provider intake, public surface and release decision. |

## Reproduce

From this directory, with Python 3.11+ and stdlib only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 -m unittest -v test_reference.py
python3 run.py
python3 verify.py
git diff --check
```

`run.py` regenerates `contract.json`, `report.json`, `report.json.sha256` and
`SOURCES.sha256` three times and fails unless the bytes are identical. To write
to fresh scratch instead:

```sh
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pipe-playout.XXXXXX")
python3 run.py --output "$scratch"
cmp "$scratch/report.json" report.json
cmp "$scratch/report.json.sha256" report.json.sha256
```

Pinned read-only inputs are listed in `SOURCES.sha256`; `source:` paths are
relative to the `audioml` workspace and `boundary:` paths to the SDK worktree.
The mutable shared `TASKS.json` is deliberately **not** pinned or hashed; only
the stable projected row identity (`id`, `title`, `component`, `mode`,
`repository`, `depends_on`) gates this package.

## Non-claims

No Bungee code, native library, real audio, corpus, model, weight, annotation
asset or runtime is read, linked, built, downloaded or executed. No rate change,
time-stretch, pitch-preservation, duration, listening, naturalness, transient,
device-timing, buffering, rebuffer, drift, underrun, benchmark or release result
exists. The 1× bypass is not a substitute for Bungee Basic. The decision is
`DEFER`; no result qualifies and no release claim is made.

## Expected artifact

| Artifact | Expected value |
| --- | --- |
| `report.json` SHA-256 | `20e934caa8315c5cb9a3fbad619b7f1048e7212cb0ee1588b975e42ad53045cd` |
| `report.json.sha256` | ASCII sidecar of that digest |
| Release gates | `8`, all `blocked` |
| Exact blockers | `8`, all `open` |
| Required artifacts | `9` (`1` provenance present, `8` blocked) |
| Synthetic controls | `17` (`9` accepted bypass, `8` rejected), `0` qualified |

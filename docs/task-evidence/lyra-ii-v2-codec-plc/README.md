<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-LYRA-II-V2-CODEC-PLC — readiness blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** feasibility
evidence for `Lyra II / V2 codec PLC`
(`component_id=lyra-ii-v2-codec-plc`). The structured inventory assigns the
**Enhancement** acceptance profile (`verification_profile: enhancement`,
`plan/INVENTORY.json`), defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER** before any implementation or intake step; `status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. Missing evidence
never qualifies a candidate.

This package does **not** contain, import, build, link, download, execute or
reverse-engineer Google Lyra, its codec, decoder, PLC path, models or TFLite
runtime. It reads no audio, encodes or decodes no packet, simulates no loss,
conceals no interval, generates no output, measures no peak, delay or quality,
and makes no listening, timing, benchmark or release claim. It records the exact
missing artifacts, probes a fixed list of task-local paths to evidence their
absence, and defines a fail-closed admission boundary for the packetized cohort
a future qualified run would need. Only
`docs/task-evidence/lyra-ii-v2-codec-plc/` is written; no provider, registry,
descriptor, public header/ABI, shared CMake, CI workflow or installed-v0
behavior changes.

## Exact external blocker

The pinned candidate matrix row is **`Lyra II / Lyra V2 codec PLC`** (matrix
record 26), status **`unavailable/blocked`**: *“No pinned codec/runtime or
packetized loss-trace adapter; waveform PLC proxies do not test Lyra decoder
concealment.”* Its declared baselines are **Opus PLC; identity codec**. The
local research notes cite Google's Lyra repository/releases and the Open Source
blog, and record that release 1.2.0 folds packet-loss handling into
`DecodeSamples()` with decoder PLC, and that Google reports Android speed, a
20 ms codec delay and TFLite artifacts. Those are **source-reported claims, not
local measurements**. The same notes state that release and model terms must be
checked at the exact version before packaging; that check has not happened here.

The inventory row is `lyra-ii-v2-codec-plc` (`evidence_status=blocked`,
`disposition=sdk-model`). No local source revision, archive, model, TFLite
bundle, runtime, encoded stream, packet-loss cohort, loss trace, clean baseline
or score exists. Nothing was downloaded, reconstructed, ported or substituted.
The local notes do not pin whether the intended candidate is Lyra II, Lyra V2,
a specific release or a specific model bundle, so the package records the
variant as unpinned rather than guessing.

**Existing PLC packages are not this candidate.** `opus-deep-plc`,
`opus-1-4-standard-decoder-plc`, `opus-dred`, `complex-bin2bin-generative-plc`,
`autoregressive-plc`, `pitch-period-repeat-plc`, `linear-interpolation-plc`,
`zero-fill-plc` and `elastic-pcm-packets` are separate merged controls or
siblings. Their numbers are pinned as adjacent provenance only and are never
pooled with this package. A waveform PLC proxy does not test a codec decoder's
own concealment state, packet timeline or bitstream behavior.

Six exact blockers, all open:

| Blocker | Missing artifact requirement |
| --- | --- |
| `BLK-01` | Permitted Google Lyra source for the declared Lyra II/V2 variant at an exact 40-hex revision, containing codec, decoder, PLC and packetization entry points, with an immutable archive SHA-256. No such snapshot exists at any fixed probe path. |
| `BLK-02` | Upstream license text, copyright notices, model/weight terms, third-party notices and any patent/use restrictions, with an explicit rights review for acquisition, evaluation, redistribution, derived output and product use. |
| `BLK-03` | Every exact model/weight/TFLite artifact with SHA-256, byte count, tensor-config and precision identity, bitstream/decoder-state definition and permitted-use terms. |
| `BLK-04` | A reproducible pinned codec/TFLite runtime with exact CLI/API, model loader, dependency lock, compiler/accelerator requirements, install location and artifact SHA-256. |
| `BLK-05` | A rights-cleared frozen 16 kHz mono packetized cohort with the exact encoded stream, explicit loss masks/intervals, decoder reset/state policy, strata, clean/source references and an Opus PLC or identity-codec baseline. |
| `BLK-06` | An agreed enhancement harness: paired SI-SDR/STOI, clean-speech preservation, output peaks, invalid/nonfinite outputs, codec alignment, content/availability delay, decoder state/memory, target-runtime timing and authorized listening or a separately labelled predictive screen, with margins and limits. |

Nothing was copied, vendored, built, downloaded or redistributed. `DEFER` is
the only defensible decision: without the exact variant, source, model, runtime,
rights decision, packetized cohort and measurement protocol, this candidate
cannot be reproduced, compared or measured. Inventing a generic neural,
generative or waveform substitute would misstate the boundary. No surrogate is
shipped.

**Reopen condition.** A caller declares the exact Lyra II or V2 variant and
supplies the permitted source revision and archive, the complete
license/notices/model-terms bundle, every model artifact and its geometry, a
reproducible runtime with exact CLI/API, a rights-cleared packetized cohort with
encoded streams and explicit loss intervals, clean/source references and a
task-matched baseline, and the enhancement quality/listening/preservation/
peak/delay/state/runtime harness with agreed budgets; the pinned runtime
reproduces approved reference outputs; and a separate versioned intake task
records opt-in registration, an explicit default decision and independent
review. Until then this task stays `DEFER`.

## Boundary: what the v0 SDK can and cannot say

The shipped public v0 facade processes `as_frame_v0` float frames at 16 kHz,
mono, 160 samples per call. A Lyra adapter would need a pinned codec variant,
model geometry, bitstream and packet-loss timeline; none is present. This
package restates the installed v0 geometry and invokes no SDK callback. It does
not add a frame-loss flag, a packet model, a decoder-state type, a provider
table or a new public type.

## What this package actually verifies

1. **Absence evidence.** 30 fixed probe locations are checked in the workspace
   and the SDK worktree (no recursive workspace walk, no download). All are
   absent. `reference.build_report()` and `verify.py` raise or fail if any probe
   later appears, so a stale “absent” claim cannot be shipped.
2. **Explicit packet-loss intervals.** A future cohort manifest has a strict,
   task-local schema. Loss is represented only by explicit, ordered,
   non-overlapping sample intervals over an encoded stream; loss inferred from
   silence or a sequence gap is rejected. Every missing, unknown, invalid,
   nonfinite, aliased, duplicated, out-of-range or non-integral control is
   rejected before any state change. One structural control is admitted to prove
   the validator is not blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, invokes a codec or simulates loss.
3. **Enhancement profile accounting.** Identity/noisy control, a task-matched
   baseline, paired SI-SDR/STOI, clean-speech preservation, peaks and invalid
   outputs, listening or a labelled screen, and alignment/state/memory/timing
   are each recorded as **blocked**. The structural schema control is not a
   result.
4. **Measurement accounting.** Source/variant/model identity, explicit loss
   intervals, paired quality, preservation, peaks/invalid outputs,
   alignment/delay, decoder state/memory/timing and listening are each recorded
   as **blocked** with `value=null`. No measurement is inferred from the
   admission schema, from a source-reported claim or from another PLC package.
5. **Source-claim separation.** The Google-reported PLC behavior, Android speed,
   20 ms codec delay and TFLite artifacts are retained as
   `source_reported_not_reproduced`, with `local_metrics=null`,
   `reproduced_here=false` and `qualifies_candidate=false`.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README and the cited
   sibling evidence are pinned by SHA-256 and verified unchanged.

## Enhancement profile application

| Enhancement requirement | Status here | Evidence |
| --- | --- | --- |
| Run identity/noisy control and an established task-matched baseline | blocked | No Lyra runtime or codec control exists. |
| Score paired SI-SDR and STOI where permitted clean references exist | blocked | No clean reference, decoded output or pinned paired scorer exists. |
| Measure clean-speech preservation | blocked | No clean speech or decoded output exists. |
| Measure peaks and invalid outputs | blocked | No output samples exist. |
| For unpaired speech use a separately labeled predictive screen or authorized listening | blocked | No listening result or labelled screen exists. |
| Report alignment, state, memory and measured content/availability timing for the exact runtime | blocked | No runtime, decoder-state trace, memory or paced timing exists. |

## Measurement requirements (all blocked)

| ID | Metric | Status | Value |
| --- | --- | --- | --- |
| `MR-01` | exact_source_variant_and_model_identity | blocked | `null` |
| `MR-02` | explicit_packet_loss_intervals | blocked | `null` |
| `MR-03` | paired_si_sdr_and_stoi | blocked | `null` |
| `MR-04` | clean_speech_preservation | blocked | `null` |
| `MR-05` | output_peak_and_invalid_output_count | blocked | `null` |
| `MR-06` | alignment_and_content_availability_delay | blocked | `null` |
| `MR-07` | decoder_state_memory_and_target_runtime_timing | blocked | `null` |
| `MR-08` | independent_listening_or_authorized_screen | blocked | `null` |

No value is promoted from the schema control, from a source-reported claim or
from any sibling PLC task.

## Admission contract (task-local; not an SDK or upstream contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `model`, `geometry`,
  `loss_trace`, `clean_reference`, `score_protocol`. Unknown and missing fields
  are rejected.
- **Model**: exact 40-hex `source_revision`; SHA-256 for source, license, model
  and runtime; canonical absolute paths; `rights_decision` must be `allowed`
  (`denied` is rejected); positive `model_bytes` up to 512 MiB.
- **Geometry**: 16 kHz mono to map to the SDK boundary; positive
  `frame_samples` up to 96,000; positive `packet_samples` up to 96,000;
  `expected_delay_samples` 0–96,000.
- **Loss trace**: canonical path, SHA-256 and non-empty ordered,
  non-overlapping intervals of `first_sample`/`sample_count`. Each value is a
  safe integer; `sample_count` is positive; inferred loss is not admitted.
- **Clean reference**: canonical path, SHA-256, alignment in
  `{sample_exact, declared_offset}` and a non-negative offset;
  `sample_exact` requires zero.
- **Score protocol**: metrics exactly `["si_sdr", "stoi"]`; baseline in
  `{opus_plc, identity_codec}`; `paired_clean_reference=true`;
  `minimum_items` 1–10,000.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Candidate record 26, status `unavailable/blocked` |
| `source:research/voice-enhancement-20261101/findings.md` | `78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c` | PLC/codec context and reopen sequence |
| `source:research/voice-enhancement-20261101/evaluation_records.md` | `962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a` | Lyra II recorded as unevaluated/blocked |
| `source:research/voice-enhancement-20261101/agent-denoise/REPORT.md` | `eb1fef2ab460c11fe382d1a978ef762f91a1c1e93725e7ac443b9b5c05098b07` | Lyra release/repository lead, source claims, not verified locally |
| `source:research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md` | `fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b` | Exact candidate not run; pinned decoder/build, license and packet traces required |
| `source:research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md` | `5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14` | No Lyra checkout, runtime environment or codec-PLC artifact |
| `source:research/voice-enhancement-20261101/agent-matrix-audit/REPORT-followup7.md` | `5865f2f16f1048ae9449ad6e8383728a1e5010a2d78346baa67728fc1c992fbe` | Opus PLC evidence does not evaluate Lyra |
| `source:research/voice-enhancement-20261101/agent-opus-plc/REPORT.md` | `79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b` | Separate Opus baseline; no Lyra result |
| `source:research/voice-enhancement-20261101/agent-opus-plc/provenance-audit.md` | `ab36bab86f58e82ee139adfae011d17f13e23e26c3dba3f5ea80678713428b53` | Opus provenance; not Lyra provenance |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `lyra-ii-v2-codec-plc` component row |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `.gitattributes` | `7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185` | Unchanged Git attributes |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/opus-deep-plc/README.md` | `457346f71005fe76d0b9c9d54fba7625262f69391cfc8e60341607fedef1549d` | Merged neural-PLC blocker, not reused |
| `docs/task-evidence/opus-deep-plc/report.json` | `df8cb2dad636a6d1ded205b872297ddf43936c65dfc75febc5e6c5f4f0415df2` | Merged neural-PLC blocker, not reused |
| `docs/task-evidence/opus-1-4-standard-decoder-plc/report.json` | `ec4c9ea5e46e02d9866920458b4d6365d300d8bcd626d2e05bf7f4c4955a080e` | Merged codec PLC control, not reused |
| `docs/task-evidence/opus-dred/report.json` | `2997dc6cc9e623a762379ca498c178c22a9607591a39ea8bcf6ef2691544a3f2` | Merged redundancy sibling, not reused |
| `docs/task-evidence/complex-bin2bin-generative-plc/report.json` | `6f6214f89eca8009a19e980c3cc5b24af918c600345573e861d18d2da1e54f23` | Merged generative-PLC blocker, not reused |
| `docs/task-evidence/autoregressive-plc/report.json` | `4730ceb74e03782c90dcd78332443c2129cdf56af14ef29bcc89435b68007aec` | Merged AR control, not reused |
| `docs/task-evidence/pitch-period-repeat-plc/report.json` | `114f0107fc06176857157801f127a22e88639204b488cd2267bf80ee9b467445` | Merged pitch control, not reused |
| `docs/task-evidence/linear-interpolation-plc/report.json` | `0a711aa398be0f86559249781f429323cee2eaf31ced1585f5d8fc205248b323` | Merged linear control, not reused |
| `docs/task-evidence/zero-fill-plc/report.json` | `3f23c4453caf289ab34ca61af6c94dacb5e9abe9b31fd71a6922ac305e7281ca` | Merged zero-fill control, not reused |
| `docs/task-evidence/elastic-pcm-packets/README.md` | `15ebaa6b2b7768faa5c1bd2fc45b900db7f71d49b7ad1292685263555953e742` | Merged packet-IO sibling, not reused |
| `docs/task-evidence/survey-rst-04/report.json` | `da399d3192c14ce8471103464530cf3c684a28cde3c62249daeba7f163de6042` | RST-04 map, not reused |
| `docs/task-evidence/survey-eng-04/report.json` | `c11355762f528e51c8ea92782d921414b8221b0eb0b3ecee74227ac735e97583` | ENG-04 map, not reused |

The shared board row is read only by `verify.py`, and only through the stable
projection `{id, title, component, mode, repository, depends_on}`. `status`,
`owner`, `claim`, `review`, `handoff`, `blocked_reason` and
`dispatch_priority` are excluded from gating, so a board state transition
cannot promote or block this package's claims. The full mutable `TASKS.json`
bytes are never hashed.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, boundary, pins, commands, counts, gates. |
| `LICENSES.md` | Upstream/license boundary notes; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pin/absence/projection checks, explicit-loss admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, claims, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/lyra-ii-v2-codec-plc` with Python 3.12 and stdlib only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` reports `repeat=3 byte_identical=true`; all unittest checks
pass with 0 failed and 0 skipped; `verify.py` prints `PASS ... cold_starts=3/3
byte_identical=true profile=Enhancement status=incomplete decision=DEFER`;
REUSE reports no missing or bad license; `git diff --check` is clean.
`verify.py` itself writes only to a temporary directory and never to this
package.

Current counts: 30 absence probes (0 present), 6 required artifacts (0
present), 6 open blockers, 75 rejected admission controls, 1 schema-only
control, 6 blocked enhancement rows, 8 blocked measurement rows, 8 blocked
gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` upstream source and revision pin | blocked | Exact variant, source revision, tree and archive digests recorded from a reviewable source root. |
| `RG-02` license, model terms and notices | blocked | Complete license/notices/model-terms bundle supplied and reviewed. |
| `RG-03` exact codec model and geometry integrity | blocked | Every model artifact pinned by SHA-256 with architecture, precision, bitstream and geometry. |
| `RG-04` reproducible runtime and decoder parity | blocked | Pinned build/install reproduces approved reference outputs with the exact CLI/API and decoder state. |
| `RG-05` rights-cleared matched packetized cohort | blocked | Immutable corpus, encoded streams, explicit loss events, metadata, strata, baseline and clean/source references supplied. |
| `RG-06` enhancement quality and independent listening | blocked | Pinned scorers and an approved listening/screen protocol produce reviewed results. |
| `RG-07` preservation, peaks, invalid outputs, delay, state and resources | blocked | Paced runs record preservation, peaks, invalid outputs, alignment, delay, decoder state, CPU, memory and deadlines against agreed limits. |
| `RG-08` provider intake, public surface and release | blocked | Separate versioned intake with OFF default, explicit public-surface decision and independent exact-head review. |

No synthetic admission control opens a gate. No source-reported claim opens a
gate. No missing result is promoted.

## Separation from other evidence

`opus-deep-plc` is a source/weights/runtime blocker for Opus 1.5+ neural PLC.
`opus-1-4-standard-decoder-plc` is a deterministic decoder-PLC-style synthetic
control and does not execute Opus. `opus-dred` targets transmitted redundancy.
`complex-bin2bin-generative-plc` is a separate generative-PLC blocker.
`autoregressive-plc`, `pitch-period-repeat-plc`, `linear-interpolation-plc` and
`zero-fill-plc` are model-free synthetic waveform controls.
`elastic-pcm-packets` is a PCM/packet fixture. `survey-rst-04` and
`survey-eng-04` are taxonomy maps. None of their numbers is reused, pooled or
reinterpreted here. This package adds no board row, handoff, provider, adapter
or release artifact.

## Expected digest

`report.json` SHA-256:
`620cc90df348c6d1a7598e40d3a99f1f46fe1194cd0ad6a11756ad53eb6bc6b7`.

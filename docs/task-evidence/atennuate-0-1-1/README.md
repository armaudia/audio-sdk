<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-ATENNUATE-0-1-1 — aTENNuate 0.1.1 readiness blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`aTENNuate 0.1.1` (`component_id=atennuate-0-1-1`). The structured inventory
assigns the **Enhancement** acceptance profile
(`verification_profile: enhancement`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER** before any implementation or
intake step; `status=proposal_only_incomplete`, `evidence_status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. Missing evidence
never qualifies a candidate.

This package does **not** contain, import, build, load, download or execute
aTENNuate, the `attenuate==0.1.1` wheel, PyTorch, torchaudio, the
`PeaBrane/aTENNuate` checkpoint, a weight, a real audio file, a corpus or any
other runtime. It reads no audio, denoises no sample, measures no clock and
makes no quality, listening, timing, benchmark or release claim. It records the
exact missing artifacts, probes a fixed list of task-local paths to evidence
their absence, and defines a fail-closed admission boundary for the asset
manifest a future qualified run would need. Only
`docs/task-evidence/atennuate-0-1-1/` is written; no provider, registry,
descriptor, public header/ABI, shared CMake, CI workflow or installed-v0
behavior changes.

## Exact external blocker

The pinned asset ledger identifies the candidate as
`aTENNuate-PyPI-0.1.1`: `attenuate==0.1.1` plus the checkpoint
`data/models/atennuate/weights.pt`. The checkpoint is recorded at immutable
model revision `838e7c3815261ca7c3708330dd28626f41fe9390`, **3,414,586 bytes**,
SHA-256
`0b973c44737db024887edd92beaad87887692743ae284be1f08c84bcd3a8b681`.
The wheel is recorded as SHA-256
`595a35f3118adc709ff430f8162d8f10b7da987f5dd322b25d84bb88f5671c99`
for CPython 3.11 with `torch`/`torchaudio` 2.5.1 CPU.

Those pins are **metadata in an external ledger**, not admitted bytes. The
checkpoint is absent from this workspace, the package is not importable in the
pinned evidence interpreter, and no download is permitted. Six exact blockers,
all open:

| Blocker | Missing artifact requirement |
| --- | --- |
| `BLK-01` | The exact caller-held `weights.pt` at revision `838e7c3815261ca7c3708330dd28626f41fe9390`, 3,414,586 bytes and SHA-256 `0b973c44737db024887edd92beaad87887692743ae284be1f08c84bcd3a8b681`, read from caller storage without a download. |
| `BLK-02` | The exact `attenuate==0.1.1` wheel (SHA-256 `595a35f3118adc709ff430f8162d8f10b7da987f5dd322b25d84bb88f5671c99`), CPython 3.11, `torch`/`torchaudio` 2.5.1 CPU and the recorded transitive lock, installed in an approved isolated environment. |
| `BLK-03` | Artifact-specific code and weight terms, exact training-data provenance, third-party notices and a written redistribution/product-use decision for the exact wheel and checkpoint. |
| `BLK-04` | Approved exact aTENNuate reference outputs on frozen inputs under the pinned runtime and weights, with finite same-length output, identity source mapping and zero delay compensation. |
| `BLK-05` | A rights-cleared task-matched paired clean/noisy cohort with independent SI-SDR/STOI scoring, clean-speech preservation checks and permitted listening. |
| `BLK-06` | Target-runtime timing, memory, throughput, content/availability delay, streaming-capability parity and a separate opt-in provider intake with OFF default. |

The upstream package is a **batch evaluation wrapper**, not an
inference-optimized recurrent implementation. Its adapter is offline only,
returns same-length mono 16 kHz float audio and declares identity source mapping
with no delay compensation. The research model is described as
streaming-capable in the paper, but the PyPI 0.1.1 surface does not expose that
configuration; `SERVICE_RUNTIME_CAPABLE=false` records that boundary. The paper
reports 0.84M parameters, 46.5 ms theoretical latency and DNS1 synthetic
no-reverb PESQ 2.98; these are **source-reported provenance only**, not local
measurements.

**Reopen condition.** The caller supplies the exact checkpoint bytes at the
pinned revision with matching byte count and SHA-256, a pinned and importable
`attenuate==0.1.1`/PyTorch 2.5.1 runtime with every artifact digest, written
artifact-specific rights and a legal/product-use decision, a rights-cleared
paired cohort with clean references, independent SI-SDR/STOI scoring and
permitted listening, approved reference outputs reproduced byte-exactly, and
target-runtime timing/memory/throughput and streaming-parity evidence. A
separate versioned intake task then records opt-in registration, an explicit
default decision and independent review. Until then this task stays `DEFER`.

## What this package actually verifies

1. **Absence evidence.** Eighteen fixed probe locations are checked in the
   workspace and the SDK worktree (no recursive workspace walk). All are
   absent. The evidence interpreter is also probed with
   `importlib.util.find_spec` — without importing or executing anything — for
   `attenuate`, `torch` and `torchaudio`; all three are absent.
   `reference.build_report()` and `verify.py` raise or fail if any probe or
   runtime module later appears, so a stale "absent" claim cannot be shipped.
2. **Admission boundary.** A caller asset manifest has a strict, task-local
   schema. Every malformed, missing, invalid, nonfinite, aliased, duplicated,
   out-of-range or non-integral control is rejected before any state change. One
   structural control is admitted to prove the validator is not
   blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never opens a checkpoint, imports a runtime, reads audio or runs a model.
3. **Enhancement profile accounting.** Identity/noisy controls, task-matched
   baseline, paired SI-SDR and STOI, clean-speech preservation, peaks and
   invalid outputs, unpaired screen/listening, alignment/state/memory and
   measured content/availability timing are each recorded as **blocked**. The
   structural schema control is not a result.
4. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow and the cited merged sibling
   evidence are pinned by SHA-256 and verified unchanged. The installed v0
   geometry (16 kHz mono f32, 160 samples) is restated, not modified.

## Enhancement profile application

| Enhancement requirement | Status here | Evidence |
| --- | --- | --- |
| Identity/noisy control and an established task-matched baseline | blocked | No candidate or control output exists; historical baselines are named but not reproduced. |
| Paired SI-SDR and STOI | blocked | No rights-cleared clean references, pinned scorer or candidate output. |
| Clean-speech preservation, peaks and invalid outputs | blocked | No output samples exist. |
| Unpaired predictive screen or authorized listening | blocked | No screen and no permitted listening result. |
| Alignment, state and memory | blocked | The adapter declares identity mapping and zero delay, but no state or memory was measured. |
| Measured content/availability timing for the exact runtime | blocked | No clock, pacing, deadline, throughput or availability measurement; 46.5 ms is paper-reported. |

No synthetic or schema-control value is promoted into any of these rows.

## Admission contract (task-local; not an SDK or aTENNuate contract)

- **Manifest** fields: `schema_id`, `component_id`, `checkpoint`, `runtime`,
  `rights`, `format`, `reference_output`. Unknown and missing fields are
  rejected.
- **Checkpoint**: exact `model_id="PeaBrane/aTENNuate"`, 40 lower-hex
  `revision`, 64 lower-hex `sha256`, `byte_count` in `(0, 512 MiB]` and equal to
  the pinned 3,414,586 bytes, plus absolute normalized `path`, `license_path`
  and a 64 lower-hex `license_sha256`.
- **Runtime**: exact `package_name="attenuate"`, `package_version="0.1.1"`,
  the pinned `wheel_sha256`, `python_version="3.11"`, `torch_version="2.5.1"`,
  plus absolute normalized `runtime_path` and 64 lower-hex `runtime_sha256`.
- **Rights**: `code_license="Apache-2.0"`, `model_license="Apache-2.0"`, and
  nonempty bounded `training_data_reference` and
  `redistribution_decision_reference`.
- **Format**: 16,000 Hz, one channel, `f32`, 160 frame samples,
  `output_length="identity"`, `source_time_mapping="identity"` and
  `delay_compensation_samples=0`. Streaming, guessed or resampled formats are
  rejected.
- **Reference output**: absolute normalized path, 64 lower-hex SHA-256,
  positive bounded `sample_count`, `finite=true` and a nonempty scorer tag.
  A nonfinite or missing reference cannot be admitted.
- When probing is enabled, checkpoint, license, runtime and reference paths
  must exist and match their digests. Nothing is opened beyond a digest read;
  no audio, weight or runtime is imported or executed.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only the
stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Candidate row `evaluated`, 30-clip pilot RTF 0.345 |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | Raw-waveform state-space description and package limits |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Checkpoint revision, bytes, digest and license metadata |
| `source:research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | Historical 30-pair pilot; not reproduced |
| `source:research/clean_speech_diagnostics_20261027.md` | `c0b39bc33e2a5d9c7ca6a48a1f778de79c7c3e0a52b047beeaa43b09d5253460` | Clean-speech diagnostic row |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Batch RTF and pipeline candidate context |
| `source:adapters/atennuate/adapter.json` | `e38c45287dfd31c427b8716baed8547d3c922676bbf891fb8f8d11f1efa7728a` | Offline adapter identity and weights requirement |
| `source:adapters/atennuate/README.md` | `ff5e2d7b75a346e8d32bcfa598bde6716135e508cef599474146699f2d1d0bf3` | Pins, license caveats and source-location note |
| `source:adapters/atennuate/run.py` | `1fd63f6f8664cd377f57c4e6ee359b4977d30efcce39255c0eb03602a58f70cd` | Config identity, local checkpoint hash and identity mapping |
| `source:adapters/atennuate/requirements.lock` | `acb4233d46fd9277a234d0c8e9f8df8fd63b580f0f8fe2e3e8d9cc3bcb4185ba` | Pinned runtime package set; not installed here |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | Shared license text, unchanged |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `docs/task-evidence/gtcrn-streaming-onnx/report.json` | `34970e44019cf99eddccfebddce2c19de1dbddda7108fe69e77040f2b503163d` | Merged streaming-ONNX sibling, not reused |
| `docs/task-evidence/puresound-dpcrn-mamba-v1/README.md` | `0ce267e5e40d51007b6e31ac41479b875914e84b881e4a6897a10c2f21718457` | Merged caller-asset sibling boundary |
| `docs/task-evidence/puresound-dpcrn-mamba-v1/report.json` | `b6967e090b8aed2e04f0e898e2f6094bc7870ffc3a7b1f0b8dfb2fa582dfbd8c` | Merged caller-asset sibling report |

The shared board row is read only by `verify.py`, and only through the stable
projection `{id, title, component, mode, repository, depends_on}`. `status`,
`owner`, `claim`, `review`, `handoff`, `blocked_reason` and
`dispatch_priority` are excluded from gating, so a board state transition
cannot promote or block this package's claims. The linked dependency rows are
projected the same way.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, pins, commands, counts, gates. |
| `LICENSES.md` | Upstream/license boundary notes; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pin/absence/projection checks, asset admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/atennuate-0-1-1` with Python 3.12 and stdlib only:

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
byte_identical=true profile=Enhancement status=proposal_only_incomplete
decision=DEFER`; REUSE reports no missing or bad license; `git diff --check` is
clean. `verify.py` itself writes only to a temporary directory and never to this
package.

Current counts: 18 absence probes (0 present), 6 required artifacts (0
present), 6 open blockers, 52 rejected admission controls, 1 schema-only
control, 8 blocked gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` exact checkpoint and revision pin | blocked | Caller supplies exact `weights.pt` bytes at the pinned revision, byte count and SHA-256, without a download. |
| `RG-02` pinned runtime admission | blocked | Install the recorded wheel and lock in an isolated environment, record digests and prove import plus one deterministic forward pass. |
| `RG-03` artifact rights and training data | blocked | Written code/weight/training-data terms, notices and a redistribution/product-use decision. |
| `RG-04` exact reference parity | blocked | Approved output digests for frozen inputs reproduced byte-exactly. |
| `RG-05` rights-cleared paired cohort | blocked | Immutable paired cohort, provenance, fidelity metadata and clean references with permission. |
| `RG-06` independent scoring and permitted listening | blocked | Pinned SI-SDR/STOI scorer, preservation results and an approved listening protocol. |
| `RG-07` target-runtime timing, memory and streaming parity | blocked | Paced timing, memory, throughput, peaks, content/availability delay and a proved/rejected streaming claim. |
| `RG-08` opt-in provider intake and release | blocked | Separate versioned intake with OFF default, explicit public-surface decision and independent exact-head review. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

The historical 30-pair DNS2020 pilot (`noise_suppression_pilot_20261027.md`)
reports for `atennuate` median output SNR 14.228 dB, median SNR gain 3.857 dB,
mean ΔSI-SDR +4.1883 dB, median STOI 0.9604, mean adapter time 3.4492 s and
median RTF 0.3450, with 24/0/6 SNR wins/ties/losses. That evidence was gathered
on an engineering subset of paired DNS2020 clips, not a frozen benchmark, and
its model/runtime bytes are absent here. It is **not reproduced**, **not**
pooled with any synthetic value, **not** device timing and **not** a quality or
release claim. The small 2026-10-27 smoke note in the adapter README is likewise
provenance only.

The merged sibling packages (`puresound-dpcrn-mamba-v1`,
`gtcrn-streaming-onnx`) establish the shared caller-asset and streaming-ONNX
boundary patterns. Their results do not transfer to aTENNuate and are not
reused as candidate evidence.

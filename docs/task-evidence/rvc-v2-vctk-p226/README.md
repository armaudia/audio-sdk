<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-RVC-V2-VCTK-P226 — readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`rvc-v2-vctk-p226` (`component_id=rvc-v2-vctk-p226`, title "RVC v2 VCTK p226").
The structured inventory assigns the **Voice** acceptance profile
(`verification_profile: voice`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**; `status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. Missing evidence
never qualifies a candidate.

This package does **not** contain, copy, import, build, link, download, load or
execute an RVC source tree, the p226 checkpoint, a HuBERT/ContentVec or RMVPE
base weight, PyTorch, TorchAudio, NumPy, SoundFile, librosa, Transformers,
FAISS or parselmouth. It decodes, plays and analyzes no audio, converts no
voice, loads no model and measures no content, identity, naturalness,
alignment, first-output/tail, peak, device timing, resource, benchmark or
release result. Only whole-file SHA-256 and byte-count provenance checks are
performed on the pinned historical source/output media, and they are not loaded
as signals. It records the exact missing artifacts and rights, probes a fixed
list of workspace and home-cache paths to evidence their absence, derives the
**declared** pipeline geometry from pinned source constants with exact integer
arithmetic, models the asset admission preconditions, and defines a fail-closed
admission boundary for a future caller-supplied-asset reproducer.

Only `docs/task-evidence/rvc-v2-vctk-p226/` is written; no provider, registry,
descriptor, public header/ABI, installed-v0 behavior, shared CMake, CI workflow
or default changes.

## Exact external blocker

The RVC fork checkout is present at revision
`81eed5e8f68b6bed1789f682fe78cdd324495afc` with an MIT `LICENSE`. It contains
**no checkpoint**, **no base weights** and **no runtime**:

- **No checkpoint.** The whole historical `models` tree is gone. The p226
  checkpoint `Mp226rmvpe.pth` named by the historical runner
  (`models/rvc-vctk/M/p226/rmvpe/Mp226rmvpe.pth`) is absent from every fixed
  workspace probe, and no local or Hugging Face cache copy exists. Nothing was
  downloaded, reconstructed or substituted.
- **No base assets.** `assets/hubert_base` contains only `config.json` and
  `preprocessor_config.json`; there is no `pytorch_model.bin`. `assets/rmvpe`
  is an empty directory; there is no `rmvpe.pt`. The source loader requires
  both (`infer/hubert.py`, `infer/rmvpe.py`).
- **No runtime.** The selected CPython 3.11.5 interpreter cannot import
  `torch`, `torchaudio`, `numpy`, `soundfile`, `librosa`, `transformers`,
  `faiss`, `parselmouth` or `scipy`, and the historical virtual environments
  are gone. The repository's requirements pin a Python 3.12 CPU stack, but a
  requirements file is not an installed runtime, an install digest or a
  verified offline load path.
- **No verified speaker map.** The historical checkpoint has 109 speaker
  embeddings and no `speaker_info` metadata. `speaker_id=1 -> p226` is
  presumed from the path and VCTK ordering, not verified.
- **No reproduced result.** The only historical run is one whole-file CPU
  conversion with retrieval disabled. It is not a cohort, device, listening,
  benchmark or release result and cannot be rerun here.

Seven exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Complete source/archive provenance and reviewed checkpoint/base-asset model-card terms. The MIT source license clears no weight, dataset, voice or output use. |
| `BLK-02` | The immutable `Mp226rmvpe.pth` checkpoint with a 40-hex model revision, byte count, SHA-256 and reviewed weight terms. |
| `BLK-03` | The HuBERT/ContentVec `pytorch_model.bin` (with configs) and the RMVPE `rmvpe.pt`, each with byte count, SHA-256, revision and reviewed terms. |
| `BLK-04` | A locked offline Python 3.12 runtime with the pinned torch 2.4.1 / torchaudio 2.4.1 stack, install digest, recorded threads and an offline import/load path. |
| `BLK-05` | A reviewed 109-entry speaker map with provenance; `speaker_id=1 -> p226` is unverified today. |
| `BLK-06` | Reviewed terms plus source-speaker consent, p226 target-voice consent, a p226 reference with availability, output-use terms and a rights-cleared frozen cohort. The staged p360 FLAC is a different target and has no rights record. |
| `BLK-07` | A caller-supplied-asset reproduction and separate content, identity, naturalness, alignment, first-output/tail, peak/nonfinite, timing, resource and listening results, then a separate OFF-default provider intake. |

**Reopen condition.** A caller supplies the exact licensed source and reviewed
terms, the p226 checkpoint plus HuBERT and RMVPE base assets with digests, a
locked offline runtime with install digest, a verified speaker map, a
rights-cleared p226 reference and cohort, and the agreed Voice
quality/timing/listening protocol. The caller then reproduces the exact
reference as a caller-supplied-asset bundle and records a separate versioned
opt-in intake with an OFF default and independent exact-head review. Until then
this task stays `DEFER`.

## Historical execution: provenance only

The research record contains one successful whole-file CPU conversion. It is
transcribed with its original scope and is **not** rerun, merged task evidence
or a qualification.

| Field | Recorded value |
| --- | --- |
| Candidate | RVC v2 multi-speaker VCTK checkpoint (`Nekochu/RVC-VCTK_Voice-sample`, p226 path) |
| Mode | official RVC PyTorch pipeline, CPU, 4 threads, file input, RMVPE F0, retrieval disabled |
| Speaker | `speaker_id=1` (presumed p226, unverified) |
| Input | one LJ Speech clip, 16 kHz, 9.655 s, 309,006 bytes, SHA-256 `adc9736d…` |
| Output | `source_to_p226.wav`, 40 kHz, 9.64 s, 771,244 bytes, SHA-256 `7fa0516e…` |
| Init + HuBERT | `0.34603404195513576` s |
| Conversion | `7.748765500029549` s; file RTF `0.8038138485507831` |
| Peak / clipping | `0.497772216796875` / `0.0` |
| ASR proxy | Whisper Tiny English WER `0.0` on the one source utterance |
| Checkpoint / HuBERT / RMVPE | absent |
| Device timing, listening, identity, naturalness, cohort | absent |

The source and output are pinned by whole-file SHA-256 and byte count only.
Neither is decoded, played, scored, pooled or promoted. A 0.00 WER proxy is not
a content, semantic, identity or naturalness certificate, and 0.804 file RTF is
not a device latency.

## What this package actually verifies

1. **Source presence and exact pins.** The RVC revision, MIT `LICENSE`, README,
   requirements, v2 VC pipeline and modules, HuBERT and RMVPE loaders, CPU
   config, historical runner/metrics/ASR/output, the source clip and the
   candidate ledger are pinned by SHA-256. This is a source-code provenance
   fact, not a checkpoint, base-asset or runtime qualification.
2. **Declared source facts.** The verifier reads the pinned source and confirms
   the v2 contract declarations: 16 kHz input, 160-sample window, RMVPE
   100 Hz hop, 2× feature upsample, `p_len = samples // 160`, 40 kHz target
   rate from the checkpoint config, 109 speakers from `emb_g`, the `("v2", 1)`
   synthesizer choice and the absent `speaker_info` path. Any drift fails
   closed.
3. **Exact declared geometry.** Integer arithmetic over the **rounded ledger
   durations** (the source file is not decoded) gives 9.655 s at 16 kHz →
   154,480 declared samples → 965 full 160-sample frames with an 80-sample
   remainder; 9.64 s at 40 kHz → 385,600 declared samples → 2,410 frames; the
   rate ratio is exactly 2.5; RMVPE is 100 frames/s; and the CPU `x_pad`,
   `x_query`, `x_center`, `x_max` declarations are 1, 6, 38 and 41 →
   16,000 / 96,000 / 608,000 / 656,000 samples and 40,000 target pad samples.
   Exact decoded sample counts are **not** asserted; these are declared
   bookkeeping values, not measurements.
4. **Absence evidence.** Twenty-six fixed workspace/worktree probes and four
   fixed home-cache probes are checked (no recursive workspace walk). All are
   absent; any later present path makes `reference.build_report()` and
   `verify.py` fail. `assets/rmvpe` (empty) and `assets/hubert_base` (config
   only) are recorded as present-but-insufficient, and any new file there fails
   closed. The runtime probe uses `importlib.util.find_spec` metadata only and
   requires every module absent.
5. **Asset admission model.** A deterministic classifier encodes the v2/f0/
   40 kHz/768-D/109-speaker declarations, the no-embedded-map rule and the
   reviewed-terms requirement. It rejects wrong versions, rates, dimensions,
   speaker counts, out-of-range or boolean speaker IDs, embedded maps,
   unverified maps, missing base weights and unreviewed terms. Every outcome
   has `qualifies=false` and loads nothing.
6. **Reproducer admission boundary.** A caller bundle has a strict task-local
   schema (candidate, checkpoint, base assets, runtime, references, outcomes,
   rights). One hundred malformed, missing, duplicate, aliased, out-of-range,
   non-integral, nonfinite or inconsistent controls are rejected before any
   state change. One synthetic structural control is admitted to prove the
   validator is not blanket-rejecting; it is labelled
   `synthetic_schema_control_not_evidence`, `qualifies=false`, and it never
   reads audio, loads weights or invokes a runtime.
7. **Voice profile accounting.** Permitted inputs/targets, groups, content,
   identity, naturalness, alignment, first-output/tail, target condition and
   independent consent/reference/output-use gates are each recorded as
   **blocked**.
8. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README and merged
   sibling Voice/RVC evidence are pinned by SHA-256 and verified unchanged.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Freeze input/target references, task and groups | blocked | One unconsented LJ Speech clip; p226 target via an unverified speaker map; no p226 reference, language group or frozen condition. |
| Preserve text and semantic content | blocked | The historical WER is a one-utterance proxy, not a manual transcript or semantic result. |
| Identity/similarity separately | blocked | No target-voice score, and the target mapping itself is unverified. |
| Naturalness separately | blocked | No naturalness rating or blinded listening. |
| Record alignment | blocked | No word/phoneme, onset, F0 or source-content alignment. |
| Record first-output/tail timing | blocked | Only whole-file CPU conversion timing exists. |
| Record exact target condition | blocked | Presumed `speaker_id=1` p226 path; map, checkpoint bytes and consent absent. |
| Consent, reference availability and output use | blocked | No consent or output-use record; the staged p360 reference is the wrong target; the MIT source license clears none. |

## Admission contract (task-local; not an SDK, RVC or Voice contract)

- **Manifest** fields: `schema_id`, `experiment_id`, `candidate`, `checkpoint`,
  `base_assets`, `runtime`, `references`, `outcomes`, `rights`. Unknown and
  missing fields are rejected.
- **Candidate**: exact repository, 40-hex revision `81eed5e8…`, canonical
  absolute source/license paths, `license_id="MIT"` and 64-hex license digest.
- **Checkpoint**: name exactly `Mp226rmvpe.pth`, 64-hex SHA-256, 1 B–8 GiB,
  `version="v2"`, `f0=1`, 40 kHz target, exactly 109 speakers, no embedded
  `speaker_info`, a 64-hex reviewed speaker map with
  `speaker_map_verified=true`, and a 64-hex terms digest.
- **Base assets**: exactly `pytorch_model.bin`, `config.json` and `rmvpe.pt`,
  each with canonical path, unique 64-hex SHA-256, positive byte count ≤ 8 GiB
  and 64-hex terms digest.
- **Runtime**: Python `3.12.x`, torch/torchaudio `2.4.1`, numpy `1.26.x`,
  Transformers `4.49.x`, librosa `0.10.x`, optional faiss-cpu `1.x >= 1.13.0`,
  CPU, 1–64 threads, deterministic algorithms and offline load.
- **References**: canonical source/target paths, exactly the historical source
  SHA-256/byte count, 16 kHz, `9.655` s, target speaker exactly `p226`,
  non-empty source and target consent, and an available target reference.
- **Outcomes**: finite WER 0–1, cosine −1–1, MOS 1–5, integer alignment
  ±96,000 samples, first-output/tail 0–10,000 ms, peak 0–4, clipped fraction
  0–1, `nonfinite_count=0`, panel size 0–1000 and `claims_qualified=false`.
  These are admission bounds, not measured results.
- **Rights**: non-empty checkpoint/base-asset/dataset/output-use references and
  slug review/cohort IDs. The schema does not assert that any real right has
  been granted.

## Eight blocked release gates

| Gate | Title | Status |
| --- | --- | --- |
| `RG-01` | source archive and license provenance | blocked |
| `RG-02` | checkpoint, base assets and speaker map | blocked |
| `RG-03` | pinned runtime and offline load | blocked |
| `RG-04` | reference availability and output use | blocked |
| `RG-05` | rights-cleared frozen cohort | blocked |
| `RG-06` | voice content, identity and naturalness | blocked |
| `RG-07` | alignment, timing, peaks and resources | blocked |
| `RG-08` | provider intake, public surface and release | blocked |

No synthetic admission control opens a gate. No missing result is promoted.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only the
stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-conversion-eval-20261101/README.md` | `b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074` | Historical VC/RVC run and caveats |
| `source:…/agent-matrix-crosswalk/REPORT.md` | `b7db9a73b45b3a8918e99453e0de00c9f8f2f64604acee56c3838d3a10e2f9b6` | Crosswalk disposition |
| `source:…/scripts/run_rvc_vctk_eval.py` | `a8f66b2a5af368f4a0573e954022e17577e2d9f0c3778abb0a1a4e65c15877da` | Exact historical invocation |
| `source:…/results/rvc/metrics.json` | `14fc2c08086efadea87ba5a254704e086c3c4c94831a82de8796184168918b36` | Historical timings and peaks |
| `source:…/results/rvc/asr.json` | `2d28a6e4e93e450bc7894e68881926bb315d73dd82cd08bd44e597f7d51fff24` | One-utterance ASR proxy |
| `source:…/results/rvc/source_to_p226.wav` | `7fa0516e7475b6870267da9f4a894d0d18e67714e1081cd9d3c7d63db30bd8c7` | Historical output, hash-only |
| `source:…/data/source_ljspeech_lj001-0001.wav` | `adc9736d0a02b8efe57128b2c6843605e81ab24027f23f6fc7d05bcd6107753b` | Historical input, hash-only |
| `source:…/data/target_rtvc_p360.flac` | `fcfffdbf9b96bdc720f924de1877f515766e438242afe2306f4a919ba6809b44` | Wrong-target reference, not used |
| `source:…/repos/rvc/LICENSE` | `bec61ed1eb9a3748644ddbc50303aa6978e14eeaba46822e59a006c722b52585` | MIT source license, not weight terms |
| `source:…/repos/rvc/infer/vc/pipeline.py` | `df8ccd98ca7f81e38934a0af93cc63b4f79764dc47d932f05914c566e876522a` | Declarations and geometry |
| `source:…/repos/rvc/infer/vc/modules.py` | `7b2e12f56c2b2462d7944d8eda470796ffd4aec50f784c3f6f5169133eaae89b` | Checkpoint/speaker/synthesizer load |
| `source:…/repos/rvc/infer/hubert.py` | `bbfba54d1d83eae3fb634b2909f8f6bf41e6ffe436200ec246867c5c93ebba26` | HuBERT path and v2 return |
| `source:…/repos/rvc/infer/rmvpe.py` | `074171aec63e4b68f04d8691c62af50a1d99b9bc6dc56c4d6749fad4ba64853a` | RMVPE 128/16k/1024/160 declaration |
| `source:…/repos/rvc/configs/config.py` | `f304463184b55898aa256fadeafd50d640ed0f880dbae6f89ad54db358240043` | CPU pad/query/center/max |
| `source:…/repos/rvc/requirments_cpu_py312.txt` | `902338f1c8ef6c38186a34c19dec95e8df56030863b7a584b703a443127ea541` | Declared torch/NumPy generation |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `rvc-v2-vctk-p226` row, Voice profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Voice profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |

Exact digests for all 24 source and 19 boundary pins live in
`reference.SOURCE_PINS`, `reference.BOUNDARY_PINS` and `SOURCES.sha256`. The
shared board row is read only through the stable projection
`{id, title, component, mode, repository, depends_on}`. `status`, `owner`,
`claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` are
excluded from gating, so a board state transition cannot promote or block this
package's claims. The full mutable `TASKS.json` bytes are never hashed.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Source/checkpoint/base-asset/reference boundary; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, declarations, geometry, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, probes, declared geometry, asset model, manifest admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, declarations, geometry, report bytes/digest, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/rvc-v2-vctk-p226` with Python 3.11+ and stdlib only:

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
byte_identical=true profile=Voice status=incomplete decision=DEFER`; REUSE
reports no missing or bad license; `git diff --check` is clean. `verify.py`
itself writes only to a temporary directory and never to this package.

Current counts: 24 source pins and 19 boundary pins, 26 workspace/worktree
absence probes plus 4 home-cache probes (0 present), 2 present-but-insufficient
asset paths, 1 present-but-ineligible wrong-target reference, 7 required
artifacts (1 source present, 6 blocked), 7 open blockers, 100 rejected
admission controls, 1 schema-only control, 8 blocked Voice rows, 3 blocked
quality outcomes, 3 blocked timing rows, 8 blocked gates, 0 qualifying results.

## Non-claims

- No RVC source copy, checkpoint, HuBERT/RMVPE weight, index, runtime,
  captured audio, converted voice or vendor result is present, imported,
  loaded, linked or executed.
- No model inference, audio read/write, voice conversion, listening, target
  similarity, naturalness or content preservation result is produced.
- No microphone/device callback, pacing, first-output, tail, drop, deadline,
  latency, CPU, memory or thermal measurement exists.
- The declared geometry is deterministic bookkeeping over source constants,
  not a signal renderer, model output or timing measurement.
- The historical single-file run is provenance only; it is not rerun, merged
  task evidence or a qualification.
- No provider is registered, exposed, enabled by default or selected as a
  descriptor default; no public API, ABI, registry, installed-v0, shared build
  or CI change is made.
- No missing, synthetic or schema-control result is promoted or treated as
  evidence for the candidate.
- The original RVC MIT license is not treated as a license for the checkpoint,
  base assets, dataset, references or generated output.

## Separation from other evidence

The merged RVC-MLX realtime and RVC FAISS retrieval packages and the Chatterbox,
CosyVoice 2, OpenVoice v2 and Voice survey packages are boundaries only. This
package does not reuse their numbers, status or conclusions. In particular, the
FAISS retrieval package records a retrieval-crash boundary and the RVC-MLX
package records a realtime blocker; neither is a p226 checkpoint, base-asset,
runtime or quality result. Their future results are not pooled here.

## Expected digest

`report.json` SHA-256:
`1bfcb8cbf504b04e11501c5286afb0886d467b12524190a1dd6b6e8b48c8b657`.

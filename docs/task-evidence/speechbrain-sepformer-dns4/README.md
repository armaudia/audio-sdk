<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SPEECHBRAIN-SEPFORMER-DNS4 — readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`speechbrain-sepformer-dns4` (`component_id=speechbrain-sepformer-dns4`,
title "SpeechBrain SepFormer DNS4"). Acceptance profile: **Enhancement**, as
required by the task row and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does **not** contain, import, install, link, build, download, load
or execute PyTorch, torchaudio, SpeechBrain, HyperPyYAML, a SepFormer
checkpoint, a model weight, `config.json`, `hyperparams.yaml`, an audio signal,
a DNS corpus, an output WAV or an inference path. It pins the existing project
research, evaluation and SDK boundary sources by SHA-256, records the exact
missing checkpoint/runtime/corpus artifacts and rights, probes a fixed path
inventory to evidence absence, re-computes the **recorded** per-item aggregates
with exact decimal arithmetic, exercises a synthetic enhancement **envelope**
(identity and bounded unit-peak variants only), and validates a fail-closed
admission boundary for a future caller-supplied enhancement run. Only
`docs/task-evidence/speechbrain-sepformer-dns4/` is written; no provider,
descriptor, registry, default, public header/ABI, shared CMake, CI workflow or
installed-v0 behavior changes.

## Exact external blocker

The exact six-file checkpoint revision, runtime and corpus are **absent**:

- The pinned model is `speechbrain/sepformer-dns4-16k-enhancement` at immutable
  revision `e8c258546300102a240fa2595854d473cbfee49a`. The recorded lock pins
  `brain.ckpt` `33809a02…`, `encoder.ckpt` `33de46bb…`, `masknet.ckpt`
  `cfba4276…`, `decoder.ckpt` `ab10ab1a…`, `config.json` `2aa99b58…` and
  `hyperparams.yaml` `c6987912…`. **None is present**, and the lock records no
  byte counts. The Hub tree was reported at 113 MB; that size is not an exact
  per-file measurement.
- The recorded runtime is CPython `3.11.5`, torch `2.14.1`, torchaudio
  `2.11.0`, SpeechBrain `1.0.3`, HyperPyYAML `1.2.3` with the
  sentencepiece/PyYAML/ruamel/huggingface-hub/NumPy/SciPy/SoundFile overlay.
  The historical `data/envs/clearvoice` environment is gone. The pinned
  interpreter `3.12.16` exposes no `torch` or `speechbrain`; the exact error is
  `ModuleNotFoundError: No module named 'torch'`. The recorded run used four
  intra-op threads, not the one-thread reference policy, and no wheel digest,
  install location or import/load digest was recorded.
- The 30-pair `CLN-01-exploratory` noisy/clean manifests, audio and output WAVs
  are absent. Only per-item **metric rows** and aggregate JSON survive. Their
  manifests' recorded SHA-256 values are
  `d6a1de74f028d3bb435422b6f386b59a96127d2fc4493c101d307ba811518175` and
  `d016c7140d79cfe5c51ffe614c4d7ee56be4298f9a986a622ed6a7f73a1e6b21`;
  the files themselves are not present.
- The Apache-2.0 model-card line is not an artifact-specific license/notice
  bundle, training-data review or derived-output decision. No corpus or output
  rights record exists.
- No reproduced inference, paired metric, clean-preservation, adverse,
  listening, alignment, memory, availability or target-device result exists
  here.

Seven exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The exact six files at `e8c25854…` with verified SHA-256 and newly recorded byte counts, plus a reviewed license/notice/model-card and training-data decision. |
| `BLK-02` | A locked offline CPython `3.11.5` environment with torch `2.14.1`, torchaudio `2.11.0`, SpeechBrain `1.0.3`, HyperPyYAML `1.2.3` and the recorded overlay: wheel names/versions/byte counts/SHA-256, install location, one intra-op and one inter-op thread, deterministic algorithms, offline mode and a clean-room import plus checkpoint-load digest. |
| `BLK-03` | A rights-cleared 30-pair noisy/clean corpus with frozen manifests, per-item input digests and corpus/evaluation/derived-output/redistribution decisions. |
| `BLK-04` | Reproduced offline per-item outputs from the exact checkpoint and runtime, with output digests, finite/length/peak checks, the gain policy and three byte-identical repeats. |
| `BLK-05` | A frozen permitted scorer with identity/noisy and task-matched baseline controls, paired SI-SDR/STOI, clean preservation and missing/adverse/nonfinite rejection cases. |
| `BLK-06` | A separately labeled unpaired predictive screen or authorized listening, plus measured alignment, state, memory, availability and target-device timing. |
| `BLK-07` | A separate OFF-by-default provider intake and independent exact-head review after the prior gates clear. |

**Reopen condition.** A caller supplies the exact six-file revision with byte
counts and reviewed terms, the locked offline runtime with wheel digests, a
rights-cleared corpus, reproduced deterministic outputs, an Enhancement-profile
result with controls, separately labeled listening/timing evidence, and a
separate OFF-by-default intake with independent exact-head review. Until then
this task stays `DEFER`.

## What this package actually verifies

1. **Source/evidence presence and exact pins.** Nineteen workspace sources and
   fourteen SDK boundaries are pinned by SHA-256, including the candidate
   matrix row, the noise-suppression census, the realtime candidate record, the
   readiness/evaluation/audit reports, the adapter, the six-file lock, the three
   recorded result JSON files, the runtime requirements lock, the project
   scorer source, the inventory row, the Enhancement profile and the SDK
   delivery plan. This is provenance, not a weight or runtime qualification.
2. **Absence evidence.** Twelve fixed workspace probes, three SDK-worktree
   probes and four fixed home-cache probes are checked (no recursive workspace
   walk). All are absent. `reference.build_report()` and `verify.py` raise or
   fail if a checkpoint, runtime, corpus or output appears later, so a stale
   "absent" claim cannot ship accidentally.
3. **Runtime absence.** `importlib.util.find_spec` reports no `torch`,
   `torchaudio`, `speechbrain` or `hyperpyyaml`; no runtime is imported. The
   exact error is recorded and the interpreter is the pinned `3.12.16`.
4. **Recorded-provenance arithmetic.** The 30 noisy rows, 30 clean rows and 30
   RMS-matched rows are checked for the frozen ID set, unique outputs, 10 s
   duration, unit normalized peaks and exact-decimal agreement (6 places) with
   their aggregate summaries, including mean/median/p95/max RTF, wins/losses
   and the implied clean STOI identity. This is arithmetic consistency, not a
   reproduced run.
5. **Protocol envelope.** A deterministic 160-sample float32 frame exercises
   identity and bounded unit-peak variants: identity is byte-exact, unit-peak
   preserves length and stays within unit peak, replay and reset-replay are
   identical, close is idempotent and a post-close run is rejected with
   `enhancer_closed`. Eighteen malformed/missing/nonfinite/out-of-range cases
   are rejected with zero calls and unchanged state.
6. **Admission boundary.** A caller-supplied enhancement-run manifest has a
   strict task-local schema. Ninety-five malformed, missing, invalid,
   nonfinite, aliased, duplicated, out-of-range or non-canonical controls are
   rejected before any state change. One structural control is admitted to
   prove the validator is not blanket-rejecting; it is labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`.
7. **Enhancement-profile accounting.** Identity/noisy control, task-matched
   baseline, paired SI-SDR/STOI, clean preservation, peaks/invalid outputs,
   unpaired screen/listening, alignment/state and memory/availability timing
   are each recorded as **blocked**.
8. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers, the shared
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the Python binding, the
   provider intake note and the merged SpeechBrain/CNN/denoiser sibling reports
   are pinned by SHA-256 and verified unchanged.

## Enhancement profile application

| Enhancement requirement | Status here | Evidence |
| --- | --- | --- |
| Identity/noisy control | blocked | No reproduced pair or output exists; the envelope is not an audio control. |
| Established task-matched baseline | blocked | DeepFilterNet3, FastEnhancer Small and ClearVoice FRCRN are recorded names only; no comparator asset or rerun exists. |
| Paired SI-SDR and STOI | blocked | Recorded rows are checked for arithmetic only; no reproduced score exists. |
| Clean-speech preservation | blocked | The 30 clean diagnostics are provenance only; no clean reference or output is present. |
| Peaks and invalid outputs | blocked | Only synthetic envelope peak bounds exist; real nonfinite/clipping/length behavior is unmeasured. |
| Unpaired predictive screen or authorized listening | blocked | Neither was run; no permitted unpaired speech or listening protocol exists. |
| Alignment and state | blocked | Whole-utterance non-causal behavior is declared, but content delay and state are not measured. |
| Memory and content/availability timing | blocked | No per-call CPU, peak RSS, first-output delay, availability deadline or target-device measurement exists. |

## Release gates

All eight gates are blocked and `qualifies=false`:

| Gate | Blocked condition |
| --- | --- |
| `RG-01` | Source revision and complete license/notice/model-card/training-data provenance are absent. |
| `RG-02` | The six checkpoint/config/hyperparams files and byte counts are absent. |
| `RG-03` | No pinned offline runtime with wheel digests and clean-room import/load digest. |
| `RG-04` | No rights-cleared corpus, manifest payload or output file. |
| `RG-05` | No reproduced deterministic inference, output digests or finite/peak checks. |
| `RG-06` | No Enhancement-profile metrics, baselines, clean preservation or adverse controls. |
| `RG-07` | No listening, alignment, state, memory, availability or target-device evidence. |
| `RG-08` | No OFF-by-default provider intake or independent exact-head review. |

## Admission contract (task-local; not an SDK or model contract)

- **Manifest** fields: `schema_id`, `run_id`, `model`, `runtime`, `assets`,
  `corpus`, `outputs`, `metrics`, `controls`, `rights`. Unknown and missing
  fields are rejected.
- **Model**: exactly `speechbrain/sepformer-dns4-16k-enhancement`, revision
  `e8c258546300102a240fa2595854d473cbfee49a`, license `Apache-2.0`, offline
  mode, `streaming_supported=false` and a 64-hex license-review digest.
- **Runtime**: Python `3.11.5`, torch `2.14.1`, torchaudio `2.11.0`,
  SpeechBrain `1.0.3`, HyperPyYAML `1.2.3`, CPU, one intra-op and one inter-op
  thread, deterministic algorithms on, offline on and four 64-hex wheel
  digests. The SpeechBrain wheel must equal
  `9859d4c1b1fb3af3b85523c0c89f52e45a04f305622ed55f31aa32dd2fba19e9`.
- **Assets**: exactly the six pinned names, unique IDs, positive byte counts,
  matching lock digests, 64-hex terms digests and `present_at_review=true`.
- **Corpus**: 30 pairs, mono 16 kHz, 160,000 samples per item, a clean
  reference, and 64-hex item/manifest/terms digests.
- **Outputs**: 30 rows, 64-hex item digest, finite, length-preserving, peak
  ≤ 1, raw peak > 0, zero delay compensation and per-utterance max-absolute
  peak normalization.
- **Metrics**: protocol `CLN-01-exploratory`, 30 pairs, SI-SDR delta in
  `[-60, 60]` dB, STOI delta in `[-1, 1]`, clean STOI in `[0, 1]`, at least 3
  baselines, at least 1,000 bootstrap replicates, zero nonfinite and zero
  invalid outputs, plus a scorer digest. These are admission bounds, not
  measured results.
- **Controls**: exactly one each of `identity_noisy`,
  `task_matched_baseline`, `clean_preservation`, `adverse_missing` and
  `nonfinite_rejection`.
- **Rights**: non-empty weight/runtime/training-data/data/output-use/review
  references and `claims_qualified=false`. The schema does not assert that any
  real right has been granted.

## Historical execution: provenance only

The research record contains one exploratory 30-pair DNS2020 screen plus 30
clean diagnostics. It is transcribed with its original scope and is **not
rerun, not merged task evidence, not used for evidence and not a
qualification**.

| Field | Recorded value |
| --- | --- |
| Candidate | `speechbrain/sepformer-dns4-16k-enhancement` |
| Revision | `e8c258546300102a240fa2595854d473cbfee49a` |
| Mode | offline, whole-utterance, non-causal, no streaming state |
| Runtime | CPython 3.11.5, torch 2.14.1, torchaudio 2.11.0, SpeechBrain 1.0.3, CPU, 4 intra-op threads |
| Protocol | 30 paired DNS2020 no-reverb files + 30 clean diagnostics, 10 s each, 300 s total |
| Valid outputs | 30/30 noisy and 30/30 clean |
| Mean ΔSNR vs noisy identity | `−19.431604` dB |
| Mean ΔSI-SDR vs noisy identity | `+8.525086` dB |
| Mean ΔSTOI vs noisy identity | `+0.033132` |
| Mean / median / p95 / max RTF | `0.692796` / `0.661214` / `0.819204` / `0.828810` |
| Noisy / clean peak child RSS | 1,894,531,072 / 1,970,847,744 bytes |
| Noisy / clean worker wall | 228.032528 / 225.534259 seconds |
| Clean-input mean STOI / ΔSTOI | `0.999850` / `−0.000150` |
| RMS-matched mean ΔSNR | `−16.445336` dB (SI-SDR/STOI effectively unchanged) |
| Upstream DNS4 2022 DNSMOS claim | SIG `2.999`, BAK `3.076`, OVRL `2.437` (source-reported, not local) |
| Listening / device timing / benchmark | absent |

The historical finding is that SepFormer improved scale-invariant metrics but
was slow, memory-heavy, whole-utterance and sensitive to output-level peak
normalization. Those are reasons the task remains deferred, not a local result
or a product claim.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable linked-row projection
`{id, title, component, mode, repository, depends_on}` gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c…` | Candidate row 94 and recorded finding |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e…` | Candidate census record |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fb…` | Realtime candidate note |
| `source:…/agent-sepformer-eval/REPORT.md` | `b7a1e214…` | Evaluation protocol and provenance |
| `source:…/agent-sepformer-eval/adapter.lock.json` | `63168507…` | Six-file checkpoint digests |
| `source:…/agent-sepformer-eval/sepformer_results.json` | `3ca2cf23…` | Recorded noisy rows; arithmetic only |
| `source:…/agent-sepformer-eval/sepformer_clean_results.json` | `c0d53803…` | Recorded clean rows; arithmetic only |
| `source:…/agent-sepformer-eval/sepformer_rms_matched.json` | `9a3b5931…` | Recorded RMS diagnostic; arithmetic only |
| `source:…/agent-sepformer-readiness/REPORT.md` | `1ff9c12c…` | Readiness boundary |
| `source:…/agent-sepformer-result-audit/REPORT.md` | `dca92534…` | Result-integrity audit |
| `source:…/agent-metricgan-eval/requirements.lock` | `22b5283a…` | Recorded runtime pins |
| `source:scripts/evaluate_noise_suppression.py` | `761f0519…` | Project scorer source |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945…` | Component row and Enhancement profile |
| `source:…/plan/swarm/VERIFICATION.md` | `3f263133…` | Enhancement profile |
| `source:…/plan/audio-sdk/README.md` | `f72d6b50…` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f…` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965a…` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74…` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba5…` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc9…` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cd…` | Unchanged CI |
| `bindings/python/audio_sdk/__init__.py` | `3b7d11f0…` | Unchanged Python binding |
| `docs/provider-intake.md` | `e32610ec…` | Intake boundary |
| `docs/task-evidence/metricgan-speechbrain-voicebank/report.json` | `8f04d6f0…` | Merged SpeechBrain sibling, not reused |
| `docs/task-evidence/pytorch-and-speechbrain-adapters/report.json` | `7754c964…` | Merged SpeechBrain sibling, not reused |
| `docs/task-evidence/mobilenetv3-small-on-log-mels/report.json` | `2f179b4b…` | Merged CNN sibling, not reused |
| `docs/task-evidence/small-log-mel-gru/report.json` | `619a4bf0…` | Merged CNN sibling, not reused |
| `docs/task-evidence/gtcrn-dns3-offline/report.json` | `b4768c1e…` | Merged denoiser sibling, not reused |

The complete deterministic list, including every task-local file, is
`SOURCES.sha256`.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Runtime/checkpoint/corpus boundary; no vendored third-party text or bytes. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, Enhancement rows, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, absence probes, runtime absence, recorded arithmetic, synthetic envelope, admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | 51 deterministic unittest checks; no skips, network, runtime, checkpoint or audio. |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, scope and three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/speechbrain-sepformer-dns4` with the pinned interpreter
and standard library only:

```sh
export PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` reports `repeat=3 byte_identical=true`; all 51 unittest
checks pass with 0 failed and 0 skipped; `verify.py` prints
`PASS ... cold_starts=3/3 byte_identical=true profile=Enhancement
status=incomplete decision=DEFER`; REUSE reports no missing or bad license;
`git diff --check` is clean. `verify.py` writes only to a temporary directory.

Current counts: 19 absence probes (12 workspace, 3 SDK worktree, 4 home; 0
present), 33 source/boundary pins, 8 required artifacts (1 source present, 7
blocked), 7 open blockers, 95 admission rejections plus 1 schema-only control,
18 envelope rejections plus 1 lifecycle control, 8 Enhancement rows, 8 blocked
gates, 0 qualifying results.

## Expected digest

`report.json` SHA-256:
`e56b83bde079fca411ca8d98890fcc75e8302834b0df268c0fc87d43b2d32013`.

`contract.json` object digest:
`0443cccff0e709c0893e6821e090fa1145f40fc4f0933600bab256c8dadbcb1e`.

## Non-claims

- No SepFormer checkpoint, weight, config or hyperparams file is present,
  downloaded, loaded or executed.
- No PyTorch, torchaudio, SpeechBrain or HyperPyYAML runtime is imported or
  installed.
- No audio, corpus payload, manifest or output WAV is read or written.
- No inference, separation, enhancement or scoring run is performed.
- Recorded per-item aggregates are checked only for arithmetic consistency;
  that is provenance, not a reproduced enhancement result.
- The synthetic envelope is protocol plumbing with no audio, model, quality,
  timing or release meaning.
- No listening, device timing, benchmark, pipeline or release claim is made.
- No provider, descriptor, registry, default, public ABI, shared build or CI
  change exists.
- The upstream DNS4 2022 DNSMOS values are source-reported and are not local
  scores.
- Whole-utterance processing is not streaming and no delay, state or
  availability result is inferred.

## Separation from other evidence

The merged `metricgan-speechbrain-voicebank` and
`pytorch-and-speechbrain-adapters` packages are separate candidate/runtime
boundaries; their synthetic surrogates, admission manifests and counts are
never substituted here. The merged CNN and denoiser sibling reports
(`mobilenetv3-small-on-log-mels`, `small-log-mel-gru`, `gtcrn-dns3-offline`)
are pinned only as unchanged boundaries; none of their results is pooled. The
recorded SepFormer screen remains its own exploratory DNS2020 evaluation and is
not combined with any sibling into a qualification.

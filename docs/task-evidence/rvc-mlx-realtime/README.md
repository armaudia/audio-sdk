<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-RVC-MLX-REALTIME — readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`rvc-mlx-realtime` (`component_id=rvc-mlx-realtime`, title "RVC-MLX realtime").
Decision: **DEFER** before any implementation or intake step;
`status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does **not** contain, copy, import, build, link, download, load or
execute an RVC-MLX source tree, RVC checkpoint, MLX weight, ContentVec/HuBERT or
RMVPE base asset, FAISS index, MLX/MLX-Metal runtime, Metal device path, audio
device callback, microphone capture, generated voice or benchmark harness. It
does not decode the checkout's test WAV and does not read any audio signal.
Only whole-file SHA-256 and byte-count provenance checks are performed on the
pinned research artifacts. It records the exact missing artifacts and rights,
probes fixed workspace/checkout/home-cache paths to evidence absence, validates
a caller-supplied realtime-bundle manifest with a fail-closed admission
boundary, and implements a deterministic block/SOLA/queue arithmetic reference
with the standard library.

Only `docs/task-evidence/rvc-mlx-realtime/` is written; no provider, registry,
descriptor, public header/ABI, installed-v0 behavior, shared CMake, CI workflow
or default changes.

## Exact external blocker

The source checkout is present at revision
`95a69ae2467738c605762bb5e84e8cdcef09d83d` (68 files, 598,143 bytes,
tree SHA-256 `807c15e4…`). It contains **no license**, **no weights**, **no
runtime** and **no realtime run**:

- **No license.** There is no `LICENSE`, `LICENSE.txt`, `COPYING` or `NOTICE`
  file, and no license declaration in the README, `pyproject.toml` or source
  headers. The original RVC repository's MIT `LICENSE` is present and pinned
  for contrast, but it does not by itself license this fork's modifications,
  the adapted Acelogic RVC-MLX engine, the w-okada/Applio streaming math or the
  redistributed base assets.
- **No weights or shared assets.** `models/` contains only the 669-byte
  `tomorin.json` architecture config. No target `.pth`/`.npz`, no
  `assets/contentvec/pytorch_model.bin`, no `assets/predictors/rmvpe.pt` and no
  `.index` exists at any fixed probe. The documented runtime downloads missing
  base assets from the network; nothing was downloaded.
- **No runtime.** The selected CPython 3.11.5 interpreter cannot import
  `mlx`/`mlx.core`, and no pinned virtual environment exists. `uv.lock` pins
  mlx 0.31.2 / mlx-metal 0.31.2 / numpy 1.26.4 / faiss-cpu 1.7.4 / scipy
  1.17.1 / sounddevice 0.5.5 / soxr 1.1.0, but a lock file is not an installed
  runtime, an install digest or a verified Metal execution path.
- **No realtime evidence.** The research record states the MLX microphone fork
  could not initialize because that host exposed no Metal device. The current
  host reports an Apple M1 with Metal 4 via `system_profiler`, but MLX is not
  installed, so no runtime path was exercised. The only historical RVC run used
  the **PyTorch file pipeline** at file RTF 0.804 with retrieval disabled; it
  is not MLX, not realtime and not rerun.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Complete source license/notice bundle for the fork and every adapted/vendored lineage (Acelogic RVC-MLX, w-okada, Applio, ContentVec, RMVPE), with an explicit reviewed redistribution and product-use decision. No license file exists in the checkout. |
| `BLK-02` | Target RVC v2 40 kHz f0=rmvpe synthesizer weights and JSON config, ContentVec/HuBERT and RMVPE base assets, and optional FAISS index, each with byte count, SHA-256, revision and reviewed weight/redistribution terms. |
| `BLK-03` | A locked offline CPython 3.11 runtime installed from the pinned lock with wheel hashes, an install/import digest, working Metal device access, deterministic settings and an offline load path. |
| `BLK-04` | A rights-cleared input/target cohort with consent, reference-availability and output-use records, manual transcripts, language/speaker groups and identity/target/alternate-target controls. The historical p360 reference provenance is unconfirmed. |
| `BLK-05` | Separate content, identity, naturalness, listening, alignment, first-output/tail, SOLA-join, peak/nonfinite and target-device paced deadline/resource results. No realtime run exists. |
| `BLK-06` | A separate versioned OFF-by-default provider intake with an exact asset descriptor, clean-install proof, no registry/default/shared-build change and independent exact-head review. |

**Reopen condition.** A caller supplies the exact licensed source and adapted
lineage, all target/shared assets and the optional index with digests, a locked
offline MLX runtime with Metal access and install digest, a rights-cleared
realtime cohort, a reproduced outcome/timing/listening bundle on the target
device, then records a separate opt-in intake with an OFF default and
independent exact-head review. Until then this task stays `DEFER`.

## Historical execution: provenance only

Two historical records are transcribed with their original scope. Neither is
rerun, merged task evidence or a qualification.

| Field | RVC-MLX realtime | RVC v2 file pipeline |
| --- | --- | --- |
| Source | `repos/rvc-mlx-realtime` checkout (source only) | `repos/rvc` PyTorch pipeline |
| Weights | absent | `Mp226rmvpe.pth` (now absent) |
| Run | not initialized (recorded: no Metal device) | one LJ Speech file → 40 kHz WAV |
| Retrieval | optional `.index`, absent | disabled; native `index.search` crash recorded separately |
| File RTF | none | `0.8038138485507831` |
| WER | none | `0.0` (Whisper Tiny EN, one utterance) |
| Peak / clip | none | `0.497772216796875` / `0.0` |
| Identity / naturalness / listening | none | none |
| First-output / device timing | none | none |
| Speaker mapping | none | `speaker_id=1 → p226` presumed, unverified |

The repository also documents warm steady-state M5 MacBook Pro figures
(~60 ms fp32 / ~53 ms fp16 per 200 ms block; offline RTF ~0.13/~0.09). They are
different-host, repository-authored context with no logs or build digest and
are **not** reproduced or used as evidence.

## What this package actually verifies

1. **Source presence and exact pins.** The checkout revision, non-`.git` tree
   digest, file count and byte count are recomputed. Twenty-one research/plan
   files and thirteen shared-boundary files are pinned by SHA-256, including
   the realtime stream/controller source, `uv.lock`, engine/realtime docs, the
   original RVC MIT license, the SDK contract and merged LLVC/taxonomy
   siblings. The mutable shared board is **not** pinned; only the stable row
   projection gates anything.
2. **Absence evidence.** Thirty-five fixed workspace/checkout probes and three
   fixed home-cache probes are checked (no recursive workspace walk). All are
   absent; any later present path makes `reference.build_report()` and
   `verify.py` fail. An import probe records that `mlx` is not importable
   without importing it.
3. **Deterministic realtime arithmetic.** Exact integer geometry proves
   200 ms block → 3200 samples, 60 ms crossfade → 960, 12 ms SOLA search → 192,
   300 ms extra → 4800, a 9152-sample (572 ms) window, 2.5× upsample to
   8000/2400/480 target samples, 481 SOLA candidates, 4160 samples (13/50 s) of
   declared block+crossfade buffering and a 32000-sample ring cap.
4. **Exact SOLA alignment reference.** An integer LCG signal with a known
   synthetic shift is aligned by exact `Fraction` normalized cross-correlation
   over offsets `0..search`; the reference recovers lags 0, 7, 12 and 24
   uniquely. This is algorithm arithmetic, not the runtime's float path (the
   runtime's `1e-3` denominator guard is deliberately not modelled) and not
   audio.
5. **Rational resampling and bounded-backlog arithmetic.** Device rates 44.1,
   48, 96 and 192 kHz are reduced exactly to 16 kHz and from 40 kHz; the
   declared 2-block queues plus 4-block ring bound retained audio at 6 blocks
   (48,000 samples / 1200 ms). No thread, callback or resampler runs.
6. **Source-declaration cross-check.** The pinned source bytes are checked for
   the exact declared defaults, the `convert_size` sum, the 2.5 upsample ratio,
   `np.argmax(cor_nom / cor_den)`, `queue.Queue(maxsize=2)` and
   `max_ring = block_out_dev * 4`. Nothing is imported or executed.
7. **Admission boundary.** A caller-supplied realtime-bundle manifest has a
   strict, task-local schema. Sixty-nine malformed, missing, duplicate,
   aliased, out-of-range, non-integral or nonfinite controls are rejected
   before any state change. One synthetic structural control is admitted to
   prove the validator is not blanket-rejecting; it is labelled
   `synthetic_schema_control_not_evidence`, `qualifies=false`, and it never
   reads audio, loads weights or invokes a runtime.
8. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README and merged
   sibling evidence are pinned and verified unchanged.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Freeze permitted input/target references, task and language/speaker groups | blocked | No rights-cleared source, target, consent or group record exists. |
| Preserve text and semantic content | blocked | The historical WER belongs to the PyTorch file path and is one unverified utterance. |
| Measure identity/similarity separately | blocked | No independent encoder, score or perceptual identity rating exists; p226 mapping unverified. |
| Measure naturalness separately | blocked | No naturalness rating or listening exists. |
| Record alignment | blocked | No output, SOLA offset or sample/frame alignment was measured. |
| Record first-output and tail timing | blocked | No callback, block pacing or drain measurement exists; geometry is arithmetic only. |
| Record the exact target condition | blocked | No qualified target condition; historical p360 provenance is unconfirmed. |
| Keep consent, reference availability and output use independent | blocked | No consent, availability or output-use record exists; MIT on original RVC is not a grant for the fork, weights or references. |

## Admission contract (task-local; not an SDK, RVC-MLX or Voice contract)

- **Manifest** fields: `schema_id`, `bundle_id`, `source`, `weights`, `runtime`,
  `realtime`, `references`, `outcomes`, `rights`. Unknown and missing fields
  are rejected.
- **Source**: exactly the pinned 40-hex revision and tree digest, canonical
  relative path, SPDX license ID, canonical license path and 64-hex license
  digest.
- **Weights**: unique names covering `synth_weights`, `synth_config`, `hubert`
  and `rmvpe`, plus optional `faiss_index`; unique 64-hex digests, positive
  byte counts ≤ 4 GiB and 64-hex terms digests.
- **Runtime**: CPython `3.11.x`, mlx/mlx-metal `0.31.2`, numpy `1.26.4`,
  faiss-cpu `1.7.4`, scipy `1.17.1`, sounddevice `0.5.5`, soxr `1.1.0`,
  `device="metal"`, Metal available, offline and deterministic.
- **Realtime**: block 200 ms, crossfade 60 ms, extra 300 ms, SOLA search 12 ms,
  16 kHz in / 40 kHz out, 2-block queues, 4-block ring, and derived
  `block_samples=3200`, `convert_samples=9152`, `target_block_samples=8000`,
  `declared_buffering_samples=4160`, `budget_ms=200`. Every derived field must
  equal the exact integer result.
- **References**: exactly one `source` and one `target`, unique IDs and
  digests, canonical paths, consent/rights references, language and speaker
  group. Paths are probed only for a real bundle; the synthetic control uses
  `probe_paths=False`.
- **Outcomes**: finite WER 0–1, cosine −1–1, MOS 1–5, integer alignment
  ±96,000 samples, first-output/tail 0–10,000 ms, peak 0–4, clipped fraction
  0–1, `nonfinite_count=0` and positive sample count. These are admission
  bounds, not measured results.
- **Rights**: non-empty consent, availability, output-use, terms-review and
  listening-protocol references, panel size 0–1000 and
  `claims_qualified=false`. The schema does not assert that any real right has
  been granted.

## Eight blocked release gates

| Gate | Title | Status |
| --- | --- | --- |
| `RG-01` | source revision and license provenance | blocked |
| `RG-02` | weights and shared assets and terms | blocked |
| `RG-03` | pinned MLX runtime and Metal load | blocked |
| `RG-04` | reference availability and output use | blocked |
| `RG-05` | rights-cleared realtime cohort | blocked |
| `RG-06` | separate content, identity, naturalness and listening | blocked |
| `RG-07` | realtime alignment, first-output/tail, peaks and resources | blocked |
| `RG-08` | provider intake, public surface and release | blocked |

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-conversion-eval-20261101/README.md` | `b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074` | Candidate ledger and recorded blockers |
| `source:…/results/rvc/metrics.json` | `14fc2c08086efadea87ba5a254704e086c3c4c94831a82de8796184168918b36` | Historical PyTorch file run; not rerun |
| `source:…/results/rvc/asr.json` | `2d28a6e4e93e450bc7894e68881926bb315d73dd82cd08bd44e597f7d51fff24` | One-utterance WER context |
| `source:…/scripts/run_rvc_vctk_eval.py` | `a8f66b2a5af368f4a0573e954022e17577e2d9f0c3778abb0a1a4e65c15877da` | Historical PyTorch invocation |
| `source:…/repos/rvc/LICENSE` | `bec61ed1eb9a3748644ddbc50303aa6978e14eeaba46822e59a006c722b52585` | Original RVC MIT license (contrast only) |
| `source:…/repos/rvc-mlx-realtime/README.md` | `11957c429305383782cf793a1672c05b87fe1db01f4f2665fb594d11a6798aa4` | Candidate source README |
| `source:…/repos/rvc-mlx-realtime/pyproject.toml` | `bf08a56975f4561b0c10dba0b422269a39ebb996a5059079db7235bdf7fadf9d` | Declared dependencies |
| `source:…/repos/rvc-mlx-realtime/uv.lock` | `c00f4e8d9f7b0034272d59e3d18d3aac3ef3683de788caf0d6f033c3b210f9c8` | Pinned versions; not an install |
| `source:…/repos/rvc-mlx-realtime/docs/realtime.md` | `f4564c7d6fc4613e446d6e02093de6a32018cfec344bf0d8ed505b625bf2f45d` | Block/SOLA/queue design |
| `source:…/repos/rvc-mlx-realtime/docs/engine.md` | `5c821ec4645e5539e5a563667b0b2f9b8682f5049e6909dbf3c09ebb9c3ccf90` | MLX inference pipeline |
| `source:…/repos/rvc-mlx-realtime/docs/performance.md` | `4afd68f91dc75faa1753b67e0609e2bd11e281682b3c43572fdab388405f2dce` | M5 performance context |
| `source:…/repos/rvc-mlx-realtime/docs/models-and-conversion.md` | `c9841d9f600dcbd37e61e3f5acaf06e86b4b543653724e07d7cf73a5fa9167ef` | Weight/asset requirements |
| `source:…/rvc_mlx_rt/realtime/stream.py` | `b508cb45d43f9d4c614143c2962c5fa30b92c05cc7d0af0568b37535fc99b56d` | Stream/default/SOLA source |
| `source:…/rvc_mlx_rt/realtime/controller.py` | `e762bebacf7910a23bba6e122a0b44c86aa68378a076b32bd944c772a7cb9ba6` | Queue/ring/device source |
| `source:…/rvc_mlx_rt/model_manager.py` | `9a0824f79e61291c0fca908d12c83d6e48c203ec265adeb7f54272e8cc4f8ddc` | Asset resolution/download path |
| `source:…/models/tomorin.json` | `b6a886ba38052adeec2d5ba5e4ad5413b11d5692f42e6dcd676ed20927f2b63d` | Config only; no weights |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `rvc-mlx-realtime` row, Voice profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Voice profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |

## Reproduce and verify

Standard library only. The commands are run from this directory.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` writes `contract.json`, `report.json`, `report.json.sha256` and
`SOURCES.sha256` three times and requires all four outputs to be
byte-identical. `verify.py` checks the committed bytes against a fresh
cold-start copy in a temporary tree, including the pinned source/boundary
symlinks, so path-dependent output cannot pass by accident.

## Non-claims

- No RVC-MLX source copy, RVC checkpoint, MLX weight, ContentVec/HuBERT or
  RMVPE asset, FAISS index, runtime, captured audio, generated voice or vendor
  result is present, imported, loaded, linked or executed.
- No model inference, audio read/write, voice conversion, SOLA join, listening,
  target-similarity, naturalness or content-preservation result is produced.
- No microphone/device callback, pacing, first-output, tail, drop, deadline,
  latency, CPU, memory or thermal measurement exists.
- The synthetic SOLA/correlation, block/queue and resampling arithmetic is a
  deterministic bookkeeping reference, not a signal renderer, model output or
  timing measurement.
- The historical PyTorch RVC file run and repository-authored M5 performance
  figures are provenance only; neither is rerun, merged task evidence or a
  qualification.
- No provider is registered, exposed, enabled by default or selected as a
  descriptor default; no public API, ABI, registry, installed-v0, shared build
  or CI change is made.
- No missing, synthetic or schema-control result is promoted or treated as
  evidence for the candidate.
- The original RVC MIT license is not treated as a license for this fork's
  modifications, adapted code, weights or base assets.

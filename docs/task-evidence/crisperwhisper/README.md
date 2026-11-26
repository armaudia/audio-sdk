<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-CRISPERWHISPER — CrisperWhisper non-commercial verbatim-ASR blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`crisperwhisper` (title "CrisperWhisper"). Decision: **DEFER** before any
implementation or intake step; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. No result qualifies.

The evidence source
([`playback-speed-candidates.md`](../../../../cpp-library/pipeline-validation/playback-speed-candidates.md))
calls CrisperWhisper the best *verbatim* transcript found: it emits `[um]`,
`[uh]` and `[laughter]` tags with word-level timing (~30–41 ms boundaries). The
same note records **code MIT** but **model weights CC-BY-NC-4.0**, says the tool
"cannot ship in a commercial product without a separate licence", and says to
use it only as an **offline oracle to label evaluation data, not as a runtime
dependency**. The inventory row accordingly sets `verification_profile: rate`
and plan note "Treat reported noncommercial weights as an offline annotation
lead subject to terms."

This package does **not** contain, import, clone, build, link, download, load or
execute CrisperWhisper, its weights, a Hugging Face snapshot, PyTorch,
transformers, an audio signal, a transcript, a filler/laughter span, an
annotation or any inference path. It records the exact pinned claims, probes
fixed candidate intake/cache paths to evidence absence, defines a fail-closed
admission boundary for a future verbatim annotation run, implements the exact
verbatim-token and boundary arithmetic that boundary would use, and records one
explicitly synthetic control that can never qualify. Only
`docs/task-evidence/crisperwhisper/` is written; no provider, registry,
descriptor, default, installed-v0, ABI, shared build, CI, board or handoff file
changes.

## Profile mismatch and exact acceptance scope

The task row, `plan/INVENTORY.json` and `plan/swarm/VERIFICATION.md` assign the
**Rate** acceptance profile. Rate is defined as source/output mapping, duration,
pitch and transient audibility, playback buffering, 1× and rate changes,
unfamiliar speech/music/silence, rebuffer/drift/final partial window, and
pause/filler decisions tied to source timestamps. CrisperWhisper is a
**verbatim transcription and tagging tool**, not a time-stretch renderer,
playback controller or streaming processor. Every Rate row is therefore
recorded as **blocked** rather than reinterpreted. A future review must supply
Rate evidence for a composite path that contains a renderer, or record an
explicit, reviewed waiver.

## Exact external blocker: source, weights, runtime and rights are absent

The exact licensed source, weights, runtime and run artifacts are **absent or
unverified**, and the weights are **non-commercial**:

1. **No source revision or complete MIT bundle.** The pinned note records only
   the GitHub URL and "code MIT". No 40-hex source revision, package archive,
   archive digest, `LICENSE`/`NOTICE` text or third-party attribution is
   staged. A licence identifier in a note is not a grant.
2. **No weight identity, digest or model card.** The note records only "weights
   CC-BY-NC-4.0 on Hugging Face". It records **no model ID, no revision, no byte
   count, no SHA-256, no model card and no output-use decision**. The fixed
   Hugging Face cache probes are absent. A non-commercial weight cannot be a
   commercial SDK runtime dependency without a separate negotiated licence.
3. **No pinned runtime or offline load.** The fixed candidate environment paths
   are absent. There is no lockfile, wheel/sdist archive, install digest,
   deterministic thread policy or clean-room offline load trace. No
   `crisperwhisper`, `torch` or `transformers` import was attempted.
4. **No rights-cleared audio or independent verbatim reference.** There is no
   audio, transcript, filler/laughter span set, second annotator, adjudication,
   agreement statistic or reviewed dataset/output-use term. CrisperWhisper
   output cannot be its own gold reference.
5. **No reproduced result.** The note's tags and ~30–41 ms boundary figure are
   **source-reported claims**. There is no local lexical WER, filler/laughter
   recall, boundary error, finite-output scan, matched-token accounting or
   baseline. The note records no run, corpus, crop, scorer or latency at all.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Exact `nyrahealth/CrisperWhisper` source revision, package/archive digest and complete MIT license/notice bundle with independent review. |
| `BLK-02` | Exact weight model ID, revision, byte count and SHA-256, model card, complete CC-BY-NC-4.0 terms and a written commercial/output-use decision or negotiated licence. |
| `BLK-03` | A locked offline Python/torch/transformers runtime with exact package hashes, install/import digests, one thread per pool, deterministic settings and a clean-room offline load. |
| `BLK-04` | Rights-cleared/consented 16 kHz mono audio and a two-annotator adjudicated verbatim reference with filler/laughter spans, agreement and reviewed dataset terms. |
| `BLK-05` | A fresh offline CrisperWhisper run with frozen lexical, filler, laughter and boundary scorers, exact token accounting, finite checks and uniform-timing plus filler-stripped baselines. |
| `BLK-06` | Rate-profile evidence or a reviewed waiver, target-device p50/p95/p99 timing/resources, and a separate OFF-by-default versioned provider/tool intake with independent exact-head review. |

**Reopen condition.** A caller supplies the exact source revision and MIT
bundle, the exact weight identity/digest/model card with reviewed CC-BY-NC-4.0
terms **and a separate commercial-use decision**, a locked offline runtime,
rights-cleared audio with an independent two-annotator verbatim reference,
reproduced lexical/filler/laughter/boundary results with controls, the exact
Rate protocol or a reviewed waiver, target-device measurements, and a separate
opt-in intake with an OFF default and independent exact-head review. Until then
this task stays `DEFER` and all eight release gates stay `blocked`.

## Recorded claims: provenance only

The pinned note records no measured CrisperWhisper execution. The table quotes
the claims with their original scope; nothing is rerun or promoted.

| Field | Recorded value |
| --- | --- |
| Repository | `https://github.com/nyrahealth/CrisperWhisper` |
| Code licence | MIT |
| Weight licence / host | CC-BY-NC-4.0 / Hugging Face |
| Verbatim tags | `[um]`, `[uh]`, `[laughter]` |
| Word boundaries | ~30–41 ms (source-reported) |
| Recorded role | Best verbatim transcript found; offline oracle only |
| Commercial use | Not permitted without a separate licence |
| Recommendation | Do **not** start the component with it |
| Source revision / weight ID / digest / runtime | Not recorded |
| Measured WER / recall / boundary / latency | Not recorded |

The finding is only that the pinned note considers CrisperWhisper a strong
*annotation* lead whose non-commercial weights block product use. It is not an
accuracy result, an independent timing reference, a device latency, a rights
basis or a product claim.

## What this package actually verifies

1. **Source/recipe presence and exact pins.** The candidate note, inventory
   row, Rate profile, SDK plan and merged Whisper/verbatim-ASR sibling packages
   are pinned by SHA-256. `recipe_provenance()` checks that the note still
   contains the exact licence, tag, boundary and "offline oracle" sentences.
   This is provenance, not a model, asset or runtime qualification.
2. **Absence evidence.** Twelve fixed candidate intake/cache probes are checked
   (six workspace, six external; no recursive workspace walk). All are absent.
   `reference.build_report()` and `verify.py` fail if any probe later appears,
   so a stale "absent" claim cannot ship.
3. **Admission boundary.** A caller-supplied future verbatim-annotation
   manifest has a strict, task-local schema. Every malformed, missing, invalid,
   nonfinite, aliased, duplicated, out-of-range or non-integral control is
   rejected before any state change. One structural control is admitted to prove
   the validator is not blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights or invokes a model.
4. **Deterministic verbatim-token arithmetic.** A stdlib-only integer-
   millisecond Levenshtein aligner treats token kind as identity: a filler
   replaced by a lexical word is a deletion plus an insertion, never a
   substitution. On a synthetic ten-token reference/hypothesis pair it returns
   nine matches, one filler deletion, one lexical insertion, lexical WER
   `0.166667`, filler recall `0.666667`, laughter recall `1.000000`, pooled
   boundary MAE `6.388889`, median `5.000000` and `100%` within 50 ms. It
   emits no audio and has no model input; it is arithmetic, not an ASR result.
5. **Rate-profile accounting.** Source/output mapping, duration,
   pitch/transient audibility, playback buffering, 1×/rate changes, unfamiliar
   speech/music/silence, rebuffer/drift/final partial window, timestamp-tied
   pause/filler decisions and the preferred-speed policy are each recorded as
   **blocked**.
6. **Quality and timing accounting.** Lexical WER, filler/laughter recall,
   boundary error, matched-token accounting and baselines are separate blocked
   outcomes; model load/inference, annotation/scoring, device deadlines and
   resources are separate blocked timing rows. No value is inferred from the
   note.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, CI, the SDK README and the merged Whisper +
   MFA and ASR word-timestamp sibling packages are pinned by SHA-256 and
   verified unchanged.

## Admission contract (task-local; not an SDK or CrisperWhisper contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `crisperwhisper`, `runtime`,
  `audio`, `reference`, `controls`, `outcomes`, `rights`. Unknown and missing
  fields are rejected.
- **CrisperWhisper**: exactly the `nyrahealth/CrisperWhisper` repository, a
  40-hex lowercase code revision, code licence `mit`, a slug weight source, a
  namespaced weight model ID, 40-hex weight revision, 64-hex weight SHA-256,
  a positive byte count, weights licence `cc-by-nc-4.0`,
  `commercial_use_granted=false` and a non-empty licence-review reference.
- **Runtime**: non-empty Python/torch/transformers versions, CPU, one intra-op
  and one inter-op thread, deterministic algorithms on and offline on.
- **Audio**: exactly one canonical absolute path, 64-hex digest, `en`,
  speaker slug, 16 kHz, mono, 1–960,000 samples (≤60 s).
- **Reference**: a non-empty independent source label, 64-hex digest, 2–8
  annotators, a positive token count and explicit filler spans.
- **Controls**: exactly one each of `independent_second_annotator`,
  `uniform_word_timing_baseline` and `filler_stripped_transcript_baseline`.
- **Outcomes**: lexical WER, filler recall, laughter recall and the within-50 ms
  fraction in 0–1; boundary MAE/median 0–60,000 ms; nonnegative matched tokens;
  positive reference tokens; `nonfinite_count=0` and `sample_count=1`. These
  are admission bounds, not measured results.
- **Rights**: non-empty dataset/weights/output-use/commercial-decision/review
  references and `claims_qualified=false`. The schema does not assert that any
  real right has been granted; it requires the non-commercial declaration to
  stay explicit.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only the
stable projection `{id, title, component, mode, repository, depends_on}` gates
anything. `plan/swarm/TASKS.json` bytes are never hashed.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Licence, tag, boundary and oracle claims |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `crisperwhisper` row, Rate profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/whisper-tiny-en-mfa/report.json` | `6b9cc69ea2be5cd5cad9509021b7b5e7fb972a4c32c62721f07be995b582710c` | Merged verbatim-ASR sibling boundary |
| `docs/task-evidence/asr-word-timestamps/report.json` | `318bec24c9d388fa122e80974cfc6772b144f7f651e87d5e88ac0677975d437e` | Merged ASR word-timestamp sibling boundary |

The Whisper+MFA and ASR-word-timestamp numbers, manifests, admission rules and
gates are never reused here. This package's links to them are whole-file
boundary pins only.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, profile mismatch, blockers, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Code MIT / non-commercial weights boundary; no vendored license or asset text. |
| `contract.json` | Machine-readable contract: exact models, pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, absence/projection checks, admission validator, synthetic verbatim scorer, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime, no audio). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/crisperwhisper` with Python 3.12 (3.11 also works)
and stdlib only:

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
byte_identical=true profile=Rate status=incomplete decision=DEFER`; REUSE
reports no missing or bad license; `git diff --check` is clean. `verify.py`
itself writes only to a temporary directory and never to this package.

Current counts: 12 absence probes (6 workspace + 6 external, 0 present), 7
required artifacts (1 provenance artifact present, 6 blocked), 6 open blockers,
70 rejected admission controls, 1 schema-only control, 8 blocked Rate rows, 5
blocked quality outcomes, 4 blocked timing rows, 1 synthetic verbatim score
control, 8 blocked gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision and MIT license provenance | blocked | Pin the exact CrisperWhisper source revision and package digest, stage the complete MIT license/notice set and record independent review. |
| `RG-02` weights, model card and non-commercial terms | blocked | Supply the exact weight model ID/revision/byte count/SHA-256, model card and CC-BY-NC-4.0 terms plus a written commercial/output-use decision or negotiated licence. |
| `RG-03` pinned runtime and offline load | blocked | A locked offline runtime loads the exact packages and records deterministic imports, loads and repeats. |
| `RG-04` rights-cleared audio and independent verbatim reference | blocked | Stage rights-cleared audio and a two-annotator adjudicated verbatim reference with filler/laughter spans, agreement and reviewed terms. |
| `RG-05` verbatim, filler and boundary accuracy with controls | blocked | Reproduce lexical WER, filler/laughter recall and boundary errors with token accounting, finite checks and matched baselines. |
| `RG-06` Rate-profile condition coverage | blocked | Score the exact Rate cases for a composite renderer or record a reviewed waiver. |
| `RG-07` target timing, resources and deadlines | blocked | Measure paced p50/p95/p99 latency, CPU/memory/energy and fill/flush on the intended device. |
| `RG-08` provider intake, public surface and release | blocked | A separate versioned OFF-by-default intake with clean-install proof, a commercial-licence decision and independent exact-head review. |

No synthetic admission or score control opens a gate. No missing result is
promoted.

## Separation from other evidence

The merged Whisper tiny.en + MFA package is a different engine and alignment
task; its weight, MFA assets, WER and boundary values are never substituted
here. The merged ASR word-timestamp package is a rate-proxy blocker with present
but unlicensed Vosk/sherpa bytes; those bytes are a different task and are not
reused. Silero, wav2vec2, Vosk, Whisper and sherpa-onnx are boundaries only;
none is pooled or reinterpreted as CrisperWhisper evidence.

## Non-claims

- No CrisperWhisper source, weight, model card, tokenizer or runtime is present.
- No CrisperWhisper, torch or transformers module is imported or executed.
- No audio, transcript, filler span, laughter span or annotation is read.
- No lexical WER, filler/laughter recall, boundary, finite-output or timing
  result exists.
- No provider registration, public ABI, registry/default, shared build or CI
  change exists.
- No listening, device timing, benchmark, pipeline or release claim is made.
- CC-BY-NC-4.0 weights are not a commercial runtime or rights basis.

## Expected digest

`report.json` SHA-256:
`330529b626c0f4b1bc7443446e2d4f79814c53a8e004863a5853cb6faea08614`.

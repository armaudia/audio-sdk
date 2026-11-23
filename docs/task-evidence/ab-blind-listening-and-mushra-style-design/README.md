# Blind A/B and MUSHRA-style comparison evidence

**Disposition: comparison only.** Keep this opt-in metadata replay beside
`audio-bench`; defer media preparation/exposure and human study execution.
This is an evaluation design, not a processor. No SDK provider, ABI, installed
tool, runtime default, bench scorer, or public playback changes. The JSON from
this fixture is not an official `audio-bench` bundle or a leaderboard result.

## What the historical evidence actually shows

- **Exact board source:** `realtime-audio-library/docs/denoiser_default_decision.md`
  (2026-10-31; SHA-256
  `b07872d49657742678cc3f3547c3c64be7fdcbd084124b1e57d1b0ca5632f4cf`).
  The owner found DeepFilterNet3 best and FastEnhancer Small good in both
  example sets. This is source-reported owner preference, not protocol-collected
  blinded ratings, independent holdout performance, or target-device energy
  and deadline evidence. The source's C ABI default did **not** change:
  `AE_BACKEND_PASSTHROUGH` (ID 0) remained the implicit backend. FastEnhancer
  Small was a local adapter, not a qualified C++ integration; optional native
  DPDFNet (ID 3) was experimental, scheduled-only, mono 16 kHz/160 samples, and
  required a host-provided model path.
- **Prepared examples are not blind ratings.** The source links
  `realtime-audio-library/listening_session_20261031/README.md` (generated macOS
  speech) and `realtime-audio-library/listening_session_real_voice_20261031/README.md`
  (one `LJ001-0001.wav` recording, described there as public domain). Both
  used synthetic fan/hum, busy room, and reverberant room; mono 16 kHz PCM
  WAV, fixed sequence with 0.8 s silence. The common order was noisy input,
  C++ Speex NS, FastEnhancer Small, DeepFilterNet3, and VAD-gated Speex NS
  (65/50 start/continue). Reverberation added WPE-only and Speex NS→WPE;
  only the real-voice set also added WPE→DeepFilterNet3→Speex VAD gate.
  Each had a dry reference. The source description does not clear any exact
  derived clip for panel exposure or public playback here.
- **A different prepared set had zero collected ratings.**
  `realtime-audio-library/docs/evaluation_plan.md` (§ Blinded listening pilot)
  and `realtime-audio-library/implementation_record.md` (2026-10-29/30) record
  a private VCTK v3 16 kHz / +5 dB synthetic-pink-noise packet: 12 utterances
  from 12 speakers, randomized A/B/C for raw, direct Speex NS and scheduled
  DPDFNet, aligned to one common valid window and given one common gain per
  item. Its ratings CSV was a blank template and its answer key separate.
  VCTK v3 was already used in engineering screens; this was not an
  independent holdout, nor did its three-way format match the acceptance
  A/B analyzer. VCTK privacy/publicity and exact DPDFNet model provenance
  remained unresolved. The packet builder initially lacked a distinct
  listening rights check; a later fix rejected missing/stale item-bound
  approvals before WAV reads or candidate loading. No exposure approval
  follows from packet existence or from the fix. This task read only text
  sources, not the packet, keys or WAVs.
- **Retain the counter-evidence.** The contemporaneous VCTK v3 objective
  screen (`realtime-audio-library/evaluation/vctk_v3_speex_vs_scheduled_dpdfnet_c_abi_20261029.json`)
  used 58 clips/29 speakers and found a noisy-pair advantage for DPDFNet over
  Speex (+6.778 dB SI-SDR / +0.05536 STOI / +0.814 PESQ), but worse clean-input
  controls (19.70 dB / 0.895 / 3.161 vs 26.36 dB / 0.943 / 4.064, means as
  reported). These are paired objective proxies, not judgments or device
  qualification. No unpaired score, pooled cross-cohort ranking, or new
  preference estimate is derived from them.

## Registered design and data boundaries

- **A/B:** blind raw/noisy or identity against one candidate in each task.
  Offer A, B or no preference; ties count as non-preference, not exclusion.
  Balance sides per item and randomize trial order using a preregistered
  private seed and fixed assignments. Run noise removal and clean preservation
  separately; room/reverb and echo tasks need their own targets and cohorts.
- **MUSHRA-style diagnostic, not ITU conformity or a substitute for A/B:**
  randomize raw/identity, candidate, an established task-matched baseline,
  a hidden copy of the clean target and a hidden deliberately degraded
  anchor (e.g. a preregistered low-pass on that target). The hidden target
  checks the top of the scale without revealing an option's identity; the
  anchor gives a known degraded comparator and checks that scale is used
  meaningfully. Raw is the product comparison control, not a substitute for
  either. Freeze the anchor recipe and target before seeing ratings; if the
  task has no valid aligned target, omit the entire reference-based panel
  as not evaluated, rather than substituting unrelated audio. Score overall
  quality on a separate 0–100 scale with no pooling with A/B. Freeze any
  control-based exclusion rule in advance; never exclude an unfavorable
  preference or score ad hoc.
- **Before collecting:** lock task and condition IDs (including nuisance
  strata), independent source clusters, exact source and effective candidate/
  baseline identities, target definition and source timeline. Use matching
  channels/rate and the same verified nonempty half-open source interval
  for all conditions, excluding startup, tail and padding. Keep levels
  calibrated, log a common per-item safety gain if needed, and do not
  independently normalize away candidate level changes. Retain missing
  output, invalid alignment or clipping, missing responses, and invalid or
  excluded responses with distinct reasons and denominators. Report only
  permitted task/condition aggregates with counts, drops, and listener/source
  uncertainty; an incomplete panel is not a complete rank.
- **Keep three records separate.** A prepared set records stimulus identity,
  validity and assignments; it does not establish ratings or playback rights.
  Ratings require a separate response record with pseudonymous IDs and
  validated assignments; freeze the responses/exclusions before privately
  joining the key. Listener materials must expose only opaque options
  (no role-revealing names, paths, seed, digests, or key). Approved exposure
  or public playback/export must have its own exact-asset, audience and
  scope decision. Permission for local machine evaluation, panel exposure,
  publication of aggregate responses and redistribution/public playback are
  not interchangeable. Unknown scope blocks that use.

## Synthetic fixture and verification

`registration.json` locks the fabricated cohort, panels, named strata
(fan/hum, busy room, reverberant room, clean preservation), and common mono
16 kHz interval `[160,320)`. No speaker, recording, listener, or media paths
exist in the fixture. With seed `20261123`, sort conditions by ascending
SHA-256 digest of ASCII `sha256-rank-v1\n<seed>\n<panel>\n<trial>\n<condition>`
(literal LF separators, no trailing LF), with condition ID as tie-breaker.
Assign A–E in that order. This small replay tests deterministic slot mapping,
not a counterbalanced human schedule. The JSON report is the internal audit
view; its separate slot-only projection demonstrates what a listener could
see, while the combined report and seed/key must never serve as listener input.

From the SDK root, with standard-library Python 3.11.5:

```sh
evidence=docs/task-evidence/ab-blind-listening-and-mushra-style-design
python3 "$evidence/check_fixture.py"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "$evidence" -v
```

Four tests pass. Report stdout SHA-256:
`aee9df5f62738aac9db0e71bec46e42715dedab00c00630e8cb674987dcd0641`.
The report pins the registration, input fixture and scorer by SHA-256.
All six expected trials are retained, with per-trial results only:

| Trial | Metadata plan | Mock response result |
| --- | --- | --- |
| `ab-fan` | Ready; A=candidate, B=raw | A → candidate preferred (`1`) |
| `ab-room` | Ready | Missing response; null |
| `ms-fan` | Ready; A=raw, B=candidate, C=anchor, D=baseline, E=reference | `40,70,20,60,95` in slot order |
| `ms-room` | Missing required anchor | Not run; null |
| `ms-reverb` | Invalid: candidate `[160,319)` instead of `[160,320)` | Not run; null |
| `ms-clean` | Ready | Invalid score `101`; null |

Tests also check seed sensitivity, order independence, rejection of a
substituted/unregistered condition or trial, and a synthetic tie (`0`) versus
malformed responses. Media prepared: **0**; human ratings: **not collected**;
cleared playback: **0**. The values are fabricated and say nothing about
perception, candidate quality, or legal clearance.

## Reopening gates

1. **Before any media access for a panel or recruitment:** obtain separate
   item-bound approval for exact recording/source revision and audio hashes,
   code/runtime/model bytes and transformations (including anchor,
   calibration and derived files), intended listeners and hosting, stored
   rights evidence, participant consent procedures, retention/deletion and
   reporting scope. No redistribution/public playback absent separate
   exact-artifact approval. Review new approvals independently; none is
   supplied by this task.
2. **Before a blinded study:** finish task mapping, calibration, eligibility,
   exclusions, assignment and analysis review. Clear and freeze pilot data
   separately; reserve an untouched, rights-cleared, speaker/session-disjoint
   acceptance cohort with overlap checks. The historical core A/B design
   (`realtime-audio-library/docs/listening_protocol_proposal_20261030.md`)
   is one task per listener, 24 independent source clusters/items per task,
   at least 32 valid listeners per task, and fixed final enrollment set after
   a cleared pilot for ≥80% complete-gate power at 65% true preference, before
   opening acceptance data and without early stopping. The historical
   quality preference gate is ≥60% observed preference and a
   two-sided 95% interval lower bound >50%; preservation tasks have their own
   limits. The high-variation 32-listener/24-cluster simulation gave only
   66.6% complete-gate power, not measured panel power. Analyze per task
   with listener/source-cluster uncertainty and ties as non-preference.
3. **Before any candidate/default promotion:** require independent holdout
   quality and preservation plus valid authorized listening, then pinned
   native streaming/reset and end-to-end evidence on representative devices
   under the approved content delay, availability/deadline, resource and
   energy limits. Resolve applicable WPE over-range policy before WPE
   acceptance. Cite the historical matrix
   `realtime-audio-library/docs/acceptance_targets_v3_20261030.md`; this fixture
   satisfies none of those release gates.

Independent review is pending (`reviewer-listening`).

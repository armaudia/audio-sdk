<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-METRICGAN-SPEECHBRAIN-VOICEBANK — caller-supplied-asset reference

Proposal-only, incomplete and **not qualified** evidence for
`MetricGAN+ SpeechBrain VoiceBank` (`component=metricgan-speechbrain-voicebank`).
Acceptance profile: **Enhancement**, as required by the task record and defined
in `plan/swarm/VERIFICATION.md`. Disposition: **DEFER**, `evidence_status=incomplete`,
`qualification_status=not_qualified`. Missing evidence never qualifies a
candidate.

This directory models the candidate as a **caller-supplied-asset reference**:
the caller must supply the exact checkpoint, runtime and permitted corpus. None
of the three is present in this SDK worktree, and none was downloaded. The
package ships a deterministic synthetic surrogate plus a strict readiness
conclusion instead of a runtime reproduction.

No provider registration, descriptor, registry entry, installed-v0 geometry,
default, ABI, `CONTRACTS.md`, shared build or CI change is made. No weights or
corpus were downloaded, no real audio was read, no listening or device timing
was measured, and no benchmark or release claim is produced.

## Exact external blocker

The full identity and license chain is in [`ASSET-PROVENANCE.md`](ASSET-PROVENANCE.md).
In short, all five blockers are simultaneously open:

1. **Checkpoint assets absent.** `enhance_model.ckpt` (7,586,021 bytes, SHA-256
   `147bfb866bac8264603546e035bf283370e716ed2f4b7412d308d2bcee88304f`),
   `hyperparams.yaml` and `config.json` are not present and no download is
   permitted. The Apache-2.0 model-card line is not an artifact-specific
   clearance.
2. **Pinned runtime absent.** SpeechBrain 1.0.3 (wheel SHA-256
   `9859d4c1b1fb3af3b85523c0c89f52e45a04f305622ed55f31aa32dd2fba19e9`) plus the
   recorded HyperPyYAML/sentencepiece/PyYAML/ruamel overlay is not installed
   here; no wheel was fetched.
3. **Corpus provenance uncleared.** The recorded mirror is
   `JacobLinCool/VoiceBank-DEMAND-16k@4497db342d7312978c45690591fda86117831940`
   (824 pairs, 0.576 h, dataset page CC BY 4.0). The Edinburgh DataShare deposit
   links CC BY 4.0 and CSTR VCTK states ODC-By, but file-level mirror↔deposit
   mapping, attribution and redistribution are unverified and no corpus is
   present.
4. **Recorded quality result is negative.** The pinned local DNS2020 screen
   recorded mean ΔSNR −10.505 dB, ΔSI-SDR −3.538 dB, ΔSTOI −0.00850 versus the
   noisy identity control, below DeepFilterNet3, FastEnhancer Small and
   ClearerVoice FRCRN on the same 30 pairs. Those numbers are provenance only:
   they are not reproduced, pooled, thresholded or treated as a qualification.
5. **No installed adapter.** Only this task-local synthetic harness exists.

Reopen only when all five clear together and independent review plus an explicit
default authorization follow.

## Deterministic surrogate

`reference.py` generates frozen synthetic clean/noisy pairs at 16 kHz mono and
applies declared variants:

| Variant | What it is |
| --- | --- |
| `identity_noisy` | exact passthrough; identity/noisy control |
| `level_only_peak_normalized` | unit-peak scaling only; isolates the recorded `resynthesize` behavior |
| `mask_only` | smoothed magnitude mask, no level change |
| `peak_normalized_mask` | mask then unit-peak normalization — the candidate surrogate |
| `peak_normalized_mask_rms_matched` | documented offline input-RMS-matched diagnostic |
| `wiener_baseline_surrogate` | classical Wiener-shaped local surrogate reference |

`stoi` is the task-local, dependency-free port of pinned pystoi 0.4.1
(non-extended) vendored byte-identically from `docs/task-evidence/stoi-estoi/`;
its cross-check vectors were **not** re-run here and that status is recorded.
Paired SI-SDR and direct SNR are computed directly. All three are synthetic
mechanism numbers, not intelligibility or quality measurements.

## Enhancement profile application

`report.json.enhancement_profile` records the profile source and every required
Enhancement element: paired clean references (synthetic only), identity/noisy
controls, the task-matched baseline (**blocked**, comparators named but not
run), clean-speech preservation, peaks and invalid outputs, alignment
(declared 0 samples; measured `false`), state/memory/timing
(`blocked_unmeasured`), unpaired predictive screen (`blocked_not_run`),
listening (`blocked_not_run`) and resource usage (recorded provenance only).

Two mechanism findings are demonstrated on the synthetic set and deliberately
narrow:

- unit-peak normalization alone produces the recorded **pattern** — a large
  negative direct-SNR delta with unchanged paired SI-SDR and STOI;
- matching output RMS to the caller input recovers level and leaves SI-SDR and
  STOI **exactly** unchanged, so the content deficit remains.

Neither finding is a quality, parity or release result.

## Boundary

- Documented public v0 geometry preserved: 16 kHz, mono, `f32`, 160
  samples/call; fixture windows are 16,000 samples and no callback path exists.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `processor_exposure=false`,
  `shared_build_or_ci_change=false`, `installed_v0_geometry_preserved=true`.
- `CallerAssetReference` fails closed on absent bytes, undeclared identity,
  digest mismatch or a load request; the probe never reads or executes bytes.
- Configuration, rate, channel, geometry, length, nonfinite and lifecycle
  rejections fail closed without advancing harness state.

## Files

`reference.py` is the deterministic generator, surrogate and canonical report
model. `scorer.py` is the vendored pinned STOI port. `run.py` regenerates the
report, digest sidecar and source manifest. `test_reference.py` is the
acceptance suite. `verify.py` is the read-only strict checker.
`check_licensing.py` is the independent SPDX/REUSE check.
`ASSET-PROVENANCE.md` records the checkpoint/runtime/corpus identity and license
chain. `contract.json`, `adapter.json` and `provider.json` are task-local,
unregistered disposition manifests. `SOURCES.sha256` pins external sources,
boundary files and every local artifact except itself.

## Reproduction

Run from this directory with the pinned interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 check_licensing.py
```

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`, negative zero normalized) plus one trailing newline;
`report.json.sha256` records its exact digest. `verify.py` rebuilds the report
and manifest and requires byte-identical output from three cold-start
interpreter processes.

## Gates

Every gate in `report.json.gates` and `contract.json.release_gates` remains
`blocked`. The evidence stays `proposal_only_synthetic_incomplete`,
`incomplete`, `not_qualified` and `DEFER`. The board and handoff files are
untouched; no reviewers were dispatched and no merge was attempted.

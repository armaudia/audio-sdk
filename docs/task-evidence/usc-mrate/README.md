<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-USC-MRATE — task-local Rate-profile blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`USC mrate` (`component_id=usc-mrate`). Acceptance profile: **Rate**, assigned
by `plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, before `opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. No missing result qualifies the candidate.

This package records the exact identity of the extracted 2005 USC SAIL mrate
delivery and audits the fixed workspace paths. The 21-file extracted tree is
present and matches its local SHA-256 pins. The official archive copy, an
explicit license or terms grant, MATLAB 7.01 / SFS `voc19` / ESPS `get_f0`, the
MCR installer, an approved exact-runtime parity vector and a rights-cleared
multi-meeting rate cohort are absent. The package therefore contains a
**stdlib-only deterministic source/asset verifier** and a **synthetic nucleus
rate control**. It does not port, execute or claim the USC algorithm, does not
import NumPy or Octave, does not decode, play or score audio, does not
download, does not use a device clock, does not listen, does not benchmark and
makes no release claim. Source and example bytes are read only for SHA-256. Only this task-local directory is added.

Pinned base: `2f4251b9abc92584b025f9b6ea665d9f3ec6e991`.
Branch: `swarm/SDK-USC-MRATE`.

## Exact blockers

1. **Official archive copy absent.** The published
   `SAIL-speechrate.zip` (SHA-256
   `9b08e76ee826dfcb351f4bd3339870b05a1e9f8e35fc3c829b3a4a496cce4a7b`) is not
   present at `data/checkouts/SAIL-speechrate.zip`. The research run's
   temporary download was not retained, so the extracted tree cannot be tied
   byte-for-byte to the official release.
2. **Source identity unverified.** The extracted `rate/` tree has a stable
   local digest
   `246fae3af23bdca2f2eb61e90bcf91c15598efcf014b193a4a96b96e01efb59f`
   over 21 files, but there is no upstream revision, signature or archive
   cross-check.
3. **Explicit license absent.** The delivered README says "temporary
   delivery", lists contact addresses and contains no `LICENSE`, `COPYING`,
   `NOTICE`, copyright or redistribution grant. Silence is not permission for
   the MATLAB source, the bundled example speech or derivative use.
4. **Exact runtime absent.** The README requires MATLAB 7.01 on Windows XP SP2
   and references `utils/MCRInstaller.exe`. No MATLAB, Octave, MCR installer or
   Windows XP runtime is present at a fixed workspace path.
5. **Exact front end absent.** Original preprocessing needs SFS `voc19` for 19
   sub-band absolute energies and ESPS `get_f0` for pitch. Neither is present.
   The research front end is an approximate Bark-spaced Butterworth substitute,
   not a bit-exact SFS reproduction.
6. **Approved parity absent.** The merged research port agrees with the bundled
   `.rat` output on 321/331 frames and 12/12 events, with five 1–2 frame
   differences and invalid-sqrt warnings in some windows. This is unapproved
   source-output parity against the program's own output, not independent
   syllable truth and not an exact-runtime parity vector.
7. **Rights-cleared rate cohort absent.** A 210-window EN2003a manifest and the
   corresponding 4-second audio are present, but reuse rights are not recorded.
   Labels are CMUdict 1.1.1 counts derived from one meeting's AMI forced
   alignments, not manual syllabification, and only one meeting is covered.
8. **Opt-in surface absent.** No provider, adapter, descriptor, registry entry,
   default selection or release decision exists. The candidate remains off by
   default and external to the installed v0 path.

## Asset audit (fixed paths, no network)

| Artifact | Required pin | Observation |
| --- | --- | --- |
| Official archive | `9b08e76e…ce4a7b` at `data/checkouts/SAIL-speechrate.zip` | **Absent** |
| Extracted source tree | `246fae3a…efb59f`, 21 files | **Present and hash-matched** at `data/checkouts/mrate-usc-sail/rate`; unqualified |
| License / terms | Explicit grant | **Absent**; README has no license text |
| MATLAB runtime | 7.01 / Windows XP SP2 | **Absent** |
| SFS `voc19` | Pinned binary and version | **Absent** |
| ESPS `get_f0` | Pinned binary and version | **Absent** |
| MCR installer | `rate/utils/MCRInstaller.exe` | **Absent** |
| Approved parity vector | `data/runs/mrate-usc-sail-exact-parity/parity.json` | **Absent**; only unqualified source-output parity exists |
| Rate manifest | 210-window EN2003a manifest | **Present**, hash-pinned; rights and labels unapproved |
| Rate audio | 210 corresponding WAV files | **Present**; not read or scored here |

The audit reads source and example bytes only for SHA-256. It never extracts
an archive, imports a runtime, executes a `.m` file, decodes or plays audio, or
follows a symlink.

## Reference protocol and Rate-profile controls

`reference.py` implements a deterministic synthetic control at the rate
boundary:

- 16 kHz mono, 160 samples per 10 ms frame, 400 full frames plus a 77-sample
  final partial frame: 64,077 samples and 401 frames.
- 12 caller-supplied synthetic nucleus peaks at frames
  `5,40,77,114,151,188,225,262,299,336,373,400`; two deliberate sub-threshold
  spikes at frames `20` and `250`; a 5-frame minimum separation.
- A thresholded local-maximum detector maps accepted nuclei to exact half-open
  source intervals `[index*160, min((index+1)*160, total))`.
- Count and rate use exact integers and `Fraction`: 12 nuclei over 48,000
  active samples is exactly `4` syllables/s. The final partial frame hosts a
  nucleus and ends at sample 64,077, not at a padded 64,160.
- Silence yields zero events. A 100/102-frame peak pair yields one event,
  proving the refractory rule. A missing trace value, missing truth count,
  `NaN`, infinity, boolean, string, out-of-range value, wrong count, wrong
  threshold, wrong separation, wrong geometry or over-cap length is rejected.
- 29 adverse controls are actually invoked and all fail closed.

The trace is labelled
`caller_supplied_synthetic_control_trace_not_usc_output`. It is not USC mrate
output, not a real cohort result and cannot qualify the candidate.

## Eight blocked release gates

All eight gates remain `blocked`:

1. `exact_asset_identity`
2. `runtime_admission`
3. `artifact_rights`
4. `exact_reference_parity`
5. `rate_cohort_and_scoring`
6. `frontend_core_separation`
7. `opt_in_provider_intake`
8. `public_default_and_release`

## Boundary

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `production_callback_registered=false`.
- `source_bundled=false`, `asset_bundled=false`, `weights_vendored=false`.
- No descriptor, registry, shared CMake, default, installed-v0 behavior, CI,
  board or handoff change.
- No adapter is added; the opt-in SDK surface remains blocked behind the gates.

## Source-reported context

The merged research record reports a default approximate-front-end held-out
rate MAE of `1.80` syllables/s (r=.569) on 210 EN2003a windows, and a
development-tuned result of MAE `.87`, RMSE `1.12`, r=.744. The tuning selected
a 100 Hz low-pass rather than the documented 50 Hz, so it is exploratory rather
than a canonical reproduction. The bundled source-output parity is 321/331
frames with 12/12 events. These values are copied as
`source_reported_not_measured_here`; they are not reproduced, re-scored or
promoted.

## Files

- `reference.py` — stdlib-only source/asset audit, exact frame mapping,
  synthetic nucleus control, caller-manifest validation and report model.
- `run.py` — regenerates `report.json`, its SHA-256 sidecar and `SOURCES.sha256`.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — fail-closed SHA-256 manifest for sources, boundaries and
  package files. It never pins the mutable full `plan/swarm/TASKS.json`; only
  the linked-row stable identity is gated.
- `contract.json` — task contract, scope, boundary, blockers and eight gates.
- `test_reference.py` — 58 Python unittest acceptance checks.
- `verify.py` — read-only pins/JSON/identity/assets/licensing/reproduction/scope
  verifier, including three cold regenerations.
- `*.json.license`, `*.sha256.license` — SPDX sidecars for generated artifacts.

Canonical report SHA-256:
`d74c03b0e93c9e6c729fb5f10d17dc253e828dfade2579b9e3b586b11c02f246`.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py sources
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-USC-MRATE
git diff --check
```

`run.py report.json`, `run.py sources` and `run.py --check` are idempotent.
`verify.py` runs three fresh interpreter regenerations in a private scratch
directory and requires byte-identical report and sidecar output. When the
package is copied out of the worktree, set `SDK_ROOT` to the SDK checkout and
`SOURCE_ROOT` to the common workspace root. Appearance of the official archive,
an explicit rights record, the exact runtime or an approved parity vector makes
`verify.py` fail closed so the blocker must be re-evaluated rather than silently
promoted.

## Non-claims

No USC source execution, MATLAB/Octave/MCR call, SFS/ESPS call, real rate
estimate, audio decode, corpus score, accuracy, count error, latency, memory, RTF,
device timing, listening result, public benchmark or release claim is made. The
extracted-tree observation is a hash and path audit only. Missing evidence never
qualifies this candidate.

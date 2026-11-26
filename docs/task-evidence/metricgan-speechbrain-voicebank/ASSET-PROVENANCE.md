<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# Asset, runtime and corpus provenance — SDK-METRICGAN-SPEECHBRAIN-VOICEBANK

This file records the *external* identities and license chain for the candidate
boundary. **Nothing listed here is bundled, downloaded, vendored, copied,
extracted or redistributed by this task.** All digests are quoted from pinned
workspace provenance (`research/voice-enhancement-20261101/agent-metricgan-eval/`)
and were not recomputed against bytes, because the bytes are absent.

## 1. Model checkpoint and configuration

| Field | Value | Status |
| --- | --- | --- |
| Model repository | `speechbrain/metricgan-plus-voicebank` | quoted |
| Repository revision | `be514d321f66b5352c5a8d59c44700f57aa8c8f5` | quoted |
| Checkpoint file | `enhance_model.ckpt` | quoted |
| Checkpoint SHA-256 | `147bfb866bac8264603546e035bf283370e716ed2f4b7412d308d2bcee88304f` | quoted, **not verified locally** |
| Checkpoint size | 7,586,021 bytes | quoted |
| `hyperparams.yaml` SHA-256 | `7bcc0835243c27f78907de0df27bc5f33d533a675787ab2eff34188404ea225a` | quoted, **not verified locally** |
| `config.json` SHA-256 | `18cb713936f15ae4acf84f0fab863e617bfd6faba362bcf5752d85aa1f16f833` | quoted, **not verified locally** |
| Model-card license | Apache-2.0 | quoted |
| Artifact-specific terms review | none completed | **blocker** |
| Bytes present in this worktree | no | **blocker** |

The model card's Apache-2.0 line is an upstream statement. It is not a product,
redistribution or deployment clearance for this project and no legal review
exists. Missing approval is never substituted by the synthetic surrogate.

Upstream references (not fetched by this task):

- Model card and files: <https://huggingface.co/speechbrain/metricgan-plus-voicebank/tree/be514d321f66b5352c5a8d59c44700f57aa8c8f5>
- Inference API: <https://speechbrain.readthedocs.io/en/latest/API/speechbrain.inference.enhancement.html>

## 2. Runtime

| Field | Value | Status |
| --- | --- | --- |
| Toolkit | SpeechBrain 1.0.3 | quoted |
| Wheel SHA-256 | `9859d4c1b1fb3af3b85523c0c89f52e45a04f305622ed55f31aa32dd2fba19e9` | quoted |
| Overlay pins | HyperPyYAML 1.2.3, sentencepiece 0.2.2, PyYAML 6.0.3, ruamel.yaml 0.18.17, ruamel.yaml.clib 0.2.15 | quoted |
| Recorded base environment | CPython 3.11.5, PyTorch 2.14.1, torchaudio 2.11.0, huggingface-hub 2.3.0, NumPy 1.26.4, SciPy 1.17.1, SoundFile 0.12.1 | quoted |
| Installed in this worktree | no | **blocker** |

The recorded run needed a torchaudio-compatibility shim (torchaudio 2.11.0
removed `list_audio_backends`, which SpeechBrain 1.0.3 imports) and forced
`weights_only=True` checkpoint deserialization inside a deny-by-default worker.
No such worker, shim or installation exists here.

## 3. Corpus: VoiceBank + DEMAND

| Field | Value | Status |
| --- | --- | --- |
| Mirror used by recorded project evidence | `JacobLinCool/VoiceBank-DEMAND-16k` | quoted |
| Mirror revision | `4497db342d7312978c45690591fda86117831940` | quoted |
| Test split | 824 clean/noisy pairs, mono 16 kHz, 0.576 h | quoted |
| Mirror license statement | CC BY 4.0 (dataset page) | quoted |
| Primary deposit | University of Edinburgh DataShare, VoiceBank+DEMAND | quoted |
| Deposit end-user license | CC BY 4.0 | quoted |
| Source speech | CSTR VCTK; the 96 kHz deposit states ODC-By | quoted |
| File-level mirror↔deposit mapping | not established | **blocker** |
| Attribution manifest for redistribution | none | **blocker** |
| Corpus present in this worktree | no | **blocker** |

The license chain is recorded, not assumed: the Edinburgh deposit describes a
clean/noisy parallel set derived from CSTR VCTK, links a CC BY 4.0 end-user
license, and the VCTK 96 kHz deposit states ODC-By. That makes the source
corpora potentially usable with attribution, but it does **not** prove that each
file in the third-party 16 kHz mirror is byte-identical to the deposit, nor does
it settle attribution, storage, derived-output or redistribution questions for
this project. Training-data terms for the checkpoint, and any overlap between
VoiceBank-DEMAND training material and a future evaluation cohort, are separate
unresolved questions.

Upstream references (not fetched by this task):

- VoiceBank+DEMAND deposit: <https://datashare.ed.ac.uk/items/6ed35425-bf14-4d2b-93a1-0a4984952757>
- CC BY 4.0 license text: <https://creativecommons.org/licenses/by/4.0/legalcode>
- CSTR VCTK (96 kHz) deposit: <https://datashare.ed.ac.uk/items/04ff7c17-bfaf-432d-ae0f-79bdeee24bf8/full>

## 4. What this package does instead

`reference.py` provides a **deterministic synthetic surrogate** that emulates
two structural properties only: whole-utterance single-pass processing, and a
unit-peak output normalization matching the recorded `resynthesize` behavior.
It uses generated harmonic-plus-noise speech proxies and generated maskers at
frozen SNRs. It is not the candidate model, not a trained system, not a
VoiceBank result and not a quality or parity claim.

`CallerAssetReference` accepts a caller-supplied asset descriptor and fails
closed on absent bytes, an undeclared identity, a digest mismatch or a load
request. No code path in this package opens, downloads or deserializes an
external asset.

## 5. Reopen condition

Reopen only with: exact approved checkpoint/hyperparams/config bytes whose
digests match this file, an approved pinned runtime install, a file-level
mapped and attributed VoiceBank+DEMAND test split with written clearance, a new
rights-cleared matched-cohort result that clears the enhancement gates, and
independent review. The recorded negative local screen
(mean ΔSI-SDR −3.538 dB, ΔSTOI −0.00850 versus noisy identity) is provenance,
not a qualification and not a reproduction.

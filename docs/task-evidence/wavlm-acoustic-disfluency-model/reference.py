# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-WAVLM-ACOUSTIC-DISFLUENCY-MODEL.

This module is standard-library only and deterministic. It contains no WavLM
weight, backbone state dict, PyTorch/Transformers runtime, audio signal,
transcript, frame label, inference path or model result. It records the exact
third-party source, checkpoint digest, label set and the historical
inference-only smoke from the pinned research bundle; probes a fixed list of
workspace/home paths to evidence that the checkpoint, backbone and runtime are
absent; verifies that the upstream checkout declares no license; validates a
caller-supplied frame-level disfluency cohort with a fail-closed admission
boundary; and builds the canonical report.

The historical smoke loaded the complete `disfluency_acoustic.pt` checkpoint
into a WavLM Base+ configuration, ran one 4 s AMI crop and produced 199 frame
outputs for FP/RP/RV/RS/PW. It has no accuracy score because AMI supplies no
matching framewise disfluency labels. That run is recorded as provenance only.
This package does not reproduce, confirm or extend it, and no result here
qualifies the candidate.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-WAVLM-ACOUSTIC-DISFLUENCY-MODEL"
COMPONENT_ID = "wavlm-acoustic-disfluency-model"
TASK_TITLE = "WavLM acoustic disfluency model"
CONTRACT_ID = "audio-sdk/wavlm-acoustic-disfluency-model-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/wavlm-disfluency-frame-cohort/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "implementation"
BASE_COMMIT = "56d3736c6f4274bde419325d3892465018d6bfdb"
BRANCH = "swarm/SDK-WAVLM-ACOUSTIC-DISFLUENCY-MODEL"
WRITE_SCOPE = "docs/task-evidence/wavlm-acoustic-disfluency-model/ only"
TASK_PREFIX = "docs/task-evidence/wavlm-acoustic-disfluency-model/"
DISPOSITION = (
    "Caller-supplied WavLM acoustic disfluency source/weights/runtime "
    "readiness blocker; no implementation, adapter, asset or result.")

UPSTREAM_REPO = "amritkromana/disfluency_detection_from_audio"
UPSTREAM_COMMIT = "a2512e5fa0d2bf200861f049a2f08a2600c3f27c"
UPSTREAM_LICENSE = None
UPSTREAM_LICENSE_STATUS = "not_declared"
CHECKPOINT_FILE = "acoustic.pt"
CHECKPOINT_PRESERVED_NAME = "disfluency_acoustic.pt"
CHECKPOINT_DRIVE_ID = "1wWrmopvvdhlBw-cL7EDyih9zn_IJu5Wr"
CHECKPOINT_BYTES = 377639565
CHECKPOINT_SHA256 = (
    "8724aaac4da9ae4d6e04f55dc394650a2517fbf529f5f4cd00b1353c74547036")
BACKBONE_REPO = "microsoft/wavlm-base"
SMOKE_CONFIG_REPO = "microsoft/wavlm-base-plus"
SMOKE_CONFIG_REVISION = "4c66d4806a428f2e922ccfa1a962776e232d487b"
SMOKE_CONFIG_BYTES = 2232
SMOKE_CONFIG_SHA256 = (
    "fea6df1c2700a3954fc07e70588aecc9055eeb28db2ff57151a2db0d19180ed4")
SMOKE_CONFIG_LICENSE = None
LABELS = ("FP", "RP", "RV", "RS", "PW")
FRAME_INTERVAL_MS = 20
FRAME_RATE_HZ = 50
SAMPLE_RATE_HZ = 16000
SAMPLE_ID = "EN2003a_0004"
DURATION_S = "4.0"
FRAME_COUNT = 199
CPU_MODEL_ONLY_MS = "180.35912496270612"
POSITIVE_FRAMES = {"FP": 0, "RP": 10, "RV": 0, "RS": 0, "PW": 3}
RUNTIME_PYTHON = "3.10.13"
RUNTIME_TORCH = "2.2.2"
RUNTIME_TRANSFORMERS = "4.40.2"
HISTORICAL_REPO_RUNTIME = {
    "python": "3.10.13",
    "torch": "2.2.2",
    "transformers": "4.40.2",
}
REPO_DECLARED_REQUIREMENTS = {
    "pandas": "1.5.0",
    "torch": "1.12.1",
    "torchaudio": "0.12.1",
    "transformers": "4.22.2",
    "whisper_timestamped": "1.14.4",
    "gdown": "5.1.0",
}

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    """Locate the audioml workspace without a recursive walk or network use."""
    override = os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

# Immutable read-only inputs. `source:` rows are workspace-relative; the rest
# are SDK-worktree-relative. The mutable shared board is deliberately excluded
# from the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-neural/REPORT.md":
        "f2f1b55234364eceff8b0626411590fbb97476cac918d9bf34138babc5820b73",
    "research/tsm-followup-20261101/agent-neural/run/"
    "run_acoustic_disfluency_smoke.py":
        "b748fdc624436d5023b9fbc961519093fcbc2bbcb4fcae5b5baa2c80d9b991cb",
    "research/tsm-followup-20261101/agent-neural/run/"
    "disfluency_acoustic_smoke.json":
        "a97735dad820b98feab91118e5da84ff0c2f76a2777f6c92b5d70b5f2dfe5bd1",
    "research/tsm-followup-20261101/agent-neural/run/"
    "wavlm-base-plus_source.json":
        "5210619f683caf2da4ee0c5e0973dba62fca8db8e06f47a215bdec54efe868d1",
    "research/tsm-followup-20261101/agent-neural/run/syl_eval_manifest.json":
        "3c7b3731cf6d2312e42e3333cae03bc631f6d1dbf557b773e134468c867897e2",
    "data/checkouts/disfluency_detection_from_audio/README.md":
        "1b6cb8825ba9fb96d81c57c2d7961ebf82ca6a82da56fbd66cf855b95c4e8d5d",
    "data/checkouts/disfluency_detection_from_audio/models.py":
        "8b079699094e478ca78fc4cf73239707f9d60e5f676f05bbd95bd23612d8a7a4",
    "data/checkouts/disfluency_detection_from_audio/demo.py":
        "e526d9fedd2721b13b544b75bd93c6e5ccd774bb2441a554eb24b6ef5b10b908",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/dynamic-int8-wav2vec2-base/README.md":
        "3da6772383eb9b44ccd8eeab4272bf69e4dbd2640f045e42c4fa6ed24f275533",
    "docs/task-evidence/dynamic-int8-wav2vec2-base/report.json":
        "6f166a5bc05a31064780f0957e5d1fb2046d5939180175b40b72f70a36e856c9",
    "docs/task-evidence/distil-wav2vec2-adult-child-ridge/README.md":
        "adb751885024bcaab88a373602f3d19326cee356559d62b0cc334cbc25afceca",
    "docs/task-evidence/distil-wav2vec2-adult-child-ridge/report.json":
        "ff7b70f389b8c7908c917aa2488728d7f972a8acd22bf66c56d9a671cd5a65d4",
    "docs/task-evidence/silero-vad-pause-duration-rules/README.md":
        "b6e422c591364dffa8b6ab0d3c9c78a579a6c85c88f831d86ee8c9d27593ab1f",
    "docs/task-evidence/silero-vad-pause-duration-rules/report.json":
        "9aebd32c6dc61cf4c5d3d5e0b38fd82a2f083792a453bf9db9548e52cfa5b22d",
    "docs/task-evidence/usc-mrate/README.md":
        "28f837e31edeb8010e978d989fed1310946b61ebe50368234a3b23a2e4c16be1",
    "docs/task-evidence/usc-mrate/report.json":
        "d74c03b0e93c9e6c729fb5f10d17dc253e828dfade2579b9e3b586b11c02f246",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
                  "SDK-FND-PROVIDER")

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "research_provenance_bundle",
        "present": True,
        "verified": True,
        "blocked": False,
        "revision": UPSTREAM_COMMIT,
        "sha256": None,
        "requirement": (
            "The pinned research scorecard, detailed neural report, exact "
            "inference-smoke runner and output, WavLM Base+ source record and "
            "shared 210-window AMI manifest."),
    },
    {
        "id": "ART-02",
        "kind": "licensed_upstream_source",
        "present": True,
        "verified": True,
        "blocked": True,
        "revision": UPSTREAM_COMMIT,
        "sha256": None,
        "requirement": (
            "A reviewed license/terms grant for the repository at commit "
            "a2512e5fa0d2bf200861f049a2f08a2600c3f27c. The checkout has no "
            "LICENSE file and the README declares no license."),
    },
    {
        "id": "ART-03",
        "kind": "weights_checkpoint",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "The exact 377,639,565-byte acoustic.pt checkpoint with SHA-256 "
            "8724aaac4da9ae4d6e04f55dc394650a2517fbf529f5f4cd00b1353c74547036 "
            "and reviewed weight terms."),
    },
    {
        "id": "ART-04",
        "kind": "backbone_config_and_weights",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": SMOKE_CONFIG_REVISION,
        "sha256": None,
        "requirement": (
            "The exact WavLM backbone configuration/weights required to "
            "instantiate the architecture (microsoft/wavlm-base per the "
            "repository, or the recorded Base+ smoke configuration), with "
            "per-file digests and reviewed terms."),
    },
    {
        "id": "ART-05",
        "kind": "pinned_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "A locked offline runtime with Python 3.10.13, torch 2.2.2, "
            "transformers 4.40.2, numpy/soundfile loaders and an install/import "
            "digest."),
    },
    {
        "id": "ART-06",
        "kind": "rights_cleared_frame_labeled_cohort",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "A rights-cleared speech cohort with per-frame FP/RP/RV/RS/PW "
            "labels, reviewed Switchboard/LDC and annotation terms, speaker/"
            "meeting groups and source timestamps."),
    },
    {
        "id": "ART-07",
        "kind": "frame_level_quality_results",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "Reproduced per-label precision/recall/F1, onset/offset delay, "
            "stratified FN/FP, nonspeech separation, and missing/adverse/"
            "nonfinite controls on the qualified cohort."),
    },
    {
        "id": "ART-08",
        "kind": "rate_timing_and_provider_intake",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "Rate-profile mapping, pause/filler timestamp and preservation "
            "evidence, target-device timing/resources, and a separate "
            "OFF-by-default provider intake after all prior gates clear."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "linked_gates": ["RG-01", "RG-08"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "The upstream checkout at commit a2512e5fa0d2bf200861f049a2f08a2600c3f27c "
            "contains no LICENSE, LICENCE, COPYING or NOTICE file, and its "
            "README, demo and model definition declare no license, terms or "
            "redistribution grant. The Google Drive payload description also "
            "declares no terms. The exact source is present but unlicensed."),
        "required_action": (
            "Supply a written, reviewed license/terms grant covering the source "
            "code and the Google Drive checkpoint, plus a product-use and "
            "redistribution decision, before treating the candidate as usable."),
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "linked_gates": ["RG-02"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "The 377,639,565-byte disfluency_acoustic.pt checkpoint is absent. "
            "Only its documented SHA-256 8724aaac... and Google Drive id "
            "1wWrmopvvdhlBw-cL7EDyih9zn_IJu5Wr are recorded. No local file "
            "exists at the runner path, the checkout demo_models path, the "
            "model directories or the Hugging Face/torch caches, and nothing "
            "was downloaded or reconstructed."),
        "required_action": (
            "Supply the immutable checkpoint with exact byte count and SHA-256 "
            "8724aaac4da9ae4d6e04f55dc394650a2517fbf529f5f4cd00b1353c74547036, "
            "an acquisition record and reviewed weight terms."),
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "linked_gates": ["RG-02", "RG-03"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "The repository constructs WavLMModel.from_pretrained("
            "'microsoft/wavlm-base'); the smoke instantiated the architecture "
            "from a local microsoft/wavlm-base-plus config at revision "
            "4c66d48... because the checkpoint supplies all state. Neither the "
            "Base nor Base+ config/weights are present locally, and the "
            "Base+ model card records a null license field."),
        "required_action": (
            "Pin the exact backbone configuration and weights used at training "
            "or prove the smoke configuration compatible, with per-file "
            "digests, the 40-hex revision and reviewed terms."),
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "linked_gates": ["RG-03"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "The Python 3.10.13 / torch 2.2.2 / transformers 4.40.2 runtime is "
            "absent. data/envs is absent, the pinned interpreter exposes no "
            "torch or transformers, and the repository declares a different "
            "dependency set (torch 1.12.1, transformers 4.22.2, torchaudio "
            "0.12.1, gdown 5.1.0). No import or inference was attempted."),
        "required_action": (
            "Supply a locked offline environment with exact Python/torch/"
            "transformers versions, wheel hashes, an install/import digest and "
            "a clean-room deterministic load of the pinned checkpoint."),
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "linked_gates": ["RG-04", "RG-06"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No rights-cleared frame-labeled disfluency cohort is staged. The "
            "historical run used one AMI EN2003a crop as an unlabeled smoke; "
            "AMI provides no matching framewise FP/RP/RV/RS/PW labels. The "
            "upstream labels derive from Switchboard and a corrected "
            "annotation archive whose LDC/annotation terms are not reviewed "
            "here, and no audio byte was read for this package."),
        "required_action": (
            "Freeze a permitted, speaker/meeting-disjoint cohort with verified "
            "per-frame labels for all five categories, reviewed corpus and "
            "annotation terms, language/speaker groups and timestamps."),
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "linked_gates": ["RG-05", "RG-06", "RG-07", "RG-08"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No accuracy, onset/offset, stratified error or finite-output "
            "result was reproduced. The smoke reports 199 frame outputs and "
            "positive RP=10 / PW=3 counts on one crop with no reference "
            "labels; it is not precision, recall, F1 or a qualifying result. "
            "No Rate-profile, device-timing, listening or provider intake "
            "evidence exists."),
        "required_action": (
            "Reproduce the detector on the qualified cohort with a frozen "
            "scorer, per-label precision/recall/F1, onset/offset delay, "
            "stratified FN/FP, nonspeech separation and missing/adverse/"
            "nonfinite controls, then complete Rate-profile, target-device "
            "timing and a separate OFF-by-default intake."),
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_and_license_provenance",
        "status": "blocked",
        "statement": (
            "The repository commit is pinned and present, but no license or "
            "terms are declared for the source or the checkpoint."),
        "reopen_condition": (
            "Pin the exact source tree and commit and stage a reviewed license/"
            "terms grant plus a product-use and redistribution decision."),
    },
    {
        "id": "RG-02",
        "title": "weights_checkpoint_and_backbone_assets",
        "status": "blocked",
        "statement": (
            "The 377,639,565-byte checkpoint and the WavLM backbone config/"
            "weights are absent; only digests and a null-license source record "
            "exist."),
        "reopen_condition": (
            "Supply the immutable checkpoint and exact backbone assets with "
            "per-file byte counts, SHA-256, revisions and reviewed terms."),
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_and_offline_load",
        "status": "blocked",
        "statement": (
            "The exact Python/torch/transformers runtime is absent and no "
            "offline load was executed."),
        "reopen_condition": (
            "Provide a locked offline runtime, load the pinned checkpoint with "
            "networking disabled, verify all state keys and record deterministic "
            "repeat outputs."),
    },
    {
        "id": "RG-04",
        "title": "rights_cleared_frame_labeled_cohort",
        "status": "blocked",
        "statement": (
            "No permitted cohort with framewise FP/RP/RV/RS/PW labels is "
            "staged; AMI lacks matching frame labels."),
        "reopen_condition": (
            "Freeze a permitted, speaker/meeting-disjoint cohort with verified "
            "frame labels, reviewed corpus/annotation terms and timestamps."),
    },
    {
        "id": "RG-05",
        "title": "frame_level_detection_quality_and_controls",
        "status": "blocked",
        "statement": (
            "No precision, recall, F1, onset/offset delay, stratified error or "
            "missing/adverse/nonfinite control result exists."),
        "reopen_condition": (
            "Reproduce the detector with a frozen scorer and report per-label "
            "quality, onset/offset delay, stratified FN/FP, nonspeech "
            "separation, finite-output and baseline/adverse controls."),
    },
    {
        "id": "RG-06",
        "title": "rate_profile_condition_coverage_and_preservation",
        "status": "blocked",
        "statement": (
            "The Rate profile is not exercised: no mapping, duration, "
            "pitch/transient, buffering, rate-change, unfamiliar speech/music/"
            "silence, rebuffer/drift, final-partial-window or timestamp-tied "
            "pause/filler preservation evidence exists."),
        "reopen_condition": (
            "Score the exact Rate-profile cases with separate source references "
            "and a reviewed timestamp-tied pause/filler policy that preserves "
            "speech."),
    },
    {
        "id": "RG-07",
        "title": "target_timing_resources_and_deadlines",
        "status": "blocked",
        "statement": (
            "No target-device p50/p95/p99 latency, RTF, resource, thermal or "
            "deadline measurement exists; the single historical 180 ms CPU "
            "smoke is context only."),
        "reopen_condition": (
            "Measure the exact installed candidate under paced workload with "
            "p50/p95/p99 latency, RTF, CPU/memory/energy and deadline behavior "
            "on the intended device."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "statement": (
            "No provider, adapter, descriptor or intake exists; the installed "
            "v0 geometry and shared build remain untouched."),
        "reopen_condition": (
            "Open a separate versioned, OFF-by-default provider intake with an "
            "exact descriptor/config, clean-install proof and independent "
            "exact-head review after all prior gates clear."),
    },
)

RATE_PROFILE_ROWS = (
    {
        "id": "RATE-01",
        "requirement": "Measure source/output mapping and duration.",
        "status": "blocked",
        "evidence": (
            "The candidate is a frame-level classifier, not a TSM renderer; no "
            "source/output mapping or rendered duration exists."),
    },
    {
        "id": "RATE-02",
        "requirement": "Measure pitch and transient audibility.",
        "status": "blocked",
        "evidence": (
            "No rendered output, F0/transient metric or listening result "
            "exists."),
    },
    {
        "id": "RATE-03",
        "requirement": "Measure playback buffering.",
        "status": "blocked",
        "evidence": (
            "No playback chain, queue, fill/flush or buffering measurement "
            "exists."),
    },
    {
        "id": "RATE-04",
        "requirement": "Include 1x and rate changes.",
        "status": "blocked",
        "evidence": (
            "No 1x or rate-change comparison exists; frame probabilities are "
            "not a speed factor."),
    },
    {
        "id": "RATE-05",
        "requirement": "Include unfamiliar speech, music and silence.",
        "status": "blocked",
        "evidence": (
            "The historical smoke is one AMI speech crop; no unfamiliar "
            "speech, language, music or silence coverage was tested."),
    },
    {
        "id": "RATE-06",
        "requirement": "Include rebuffer, drift and the final partial window.",
        "status": "blocked",
        "evidence": (
            "No stream, rebuffer, clock-drift or partial-window behavior was "
            "measured."),
    },
    {
        "id": "RATE-07",
        "requirement": (
            "Keep pause or filler decisions tied to source timestamps and "
            "measure speech preservation."),
        "status": "blocked",
        "evidence": (
            "The smoke emits frame logits without source-timestamp decisions, "
            "a deletion policy or any speech-preservation measurement."),
    },
    {
        "id": "RATE-08",
        "requirement": (
            "Map estimated rate to a reviewed preferred-speed policy."),
        "status": "blocked",
        "evidence": (
            "A disfluency detector is not a rate estimator, and no preference "
            "or acceptability labels map detections to a preferred speed."),
    },
)

QUALITY_ROWS = (
    {
        "id": "QUAL-01",
        "outcome": "per_label_frame_precision_recall_f1",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No reference frame labels or reproduced precision/recall/F1 "
            "exist; the smoke positive counts are not scores."),
    },
    {
        "id": "QUAL-02",
        "outcome": "label_onset_offset_delay",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No aligned frame labels or onset/offset timing comparison exists."),
    },
    {
        "id": "QUAL-03",
        "outcome": "stratified_false_negatives_false_positives",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No quiet/active, speaker, label, or nonspeech stratification "
            "exists."),
    },
    {
        "id": "QUAL-04",
        "outcome": "missing_adverse_nonfinite_controls",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No missing-input, malformed-input, nonfinite-audio or all-negative "
            "control was exercised against the real model."),
    },
)

TIMING_ROWS = (
    {
        "id": "TIME-01",
        "metric": "model_latency_p50_p95_per_4s_clip",
        "status": "blocked",
        "value": None,
        "evidence": (
            "Only one historical 180.36 ms model-only CPU observation exists; "
            "no local p50/p95 measurement was made."),
    },
    {
        "id": "TIME-02",
        "metric": "real_time_factor",
        "status": "blocked",
        "value": None,
        "evidence": "No local RTF was measured.",
    },
    {
        "id": "TIME-03",
        "metric": "device_deadline_and_callback",
        "status": "blocked",
        "value": None,
        "evidence": "No device, pacing or callback deadline was measured.",
    },
    {
        "id": "TIME-04",
        "metric": "cpu_memory_energy",
        "status": "blocked",
        "value": None,
        "evidence": "No resource, thermal or energy measurement exists.",
    },
)

NON_CLAIMS = (
    "No WavLM weight, disfluency checkpoint or backbone asset is present.",
    "No torch, transformers or other model runtime is imported or executed.",
    "No audio, transcript or frame disfluency label is read or scored.",
    "No precision, recall, F1, onset/offset or finite-output result is reproduced.",
    "No listening, device timing, benchmark, pipeline or release claim is made.",
    "No provider, registry, descriptor, public ABI, shared build or CI change exists.",
    "A frame-level disfluency probability is not a speed factor or a TSM setting.",
)

REQUIRED_RESULTS = (
    "Reviewed license/terms for the source repository and the checkpoint.",
    "The exact checkpoint with byte count and SHA-256, plus backbone assets.",
    "Locked offline Python 3.10.13/torch 2.2.2/transformers 4.40.2 runtime.",
    "Rights-cleared cohort with verified framewise FP/RP/RV/RS/PW labels.",
    "Per-label precision/recall/F1, onset/offset delay and stratified errors.",
    "Missing, adverse, all-negative and nonfinite controls against the model.",
    "Rate-profile mapping, pause/filler timestamp and preservation evidence.",
    "Target-device p50/p95/p99 timing, resources and deadline behavior.",
    "Separate OFF-by-default provider intake and independent exact-head review.",
)

PROFILE_PHRASES = (
    "Measure source/output mapping, duration, pitch, transient audibility and "
    "playback buffering",
    "Include 1×, rate changes, unfamiliar speech, music, silence, rebuffer, "
    "drift and the final partial window",
    "Keep pause or filler decisions tied to source timestamps and measure "
    "speech preservation",
)

ABSENCE_PROBES = (
    "data/checkouts/disfluency_detection_from_audio/disfluency_acoustic.pt",
    "research/tsm-followup-20261101/agent-neural/disfluency_acoustic.pt",
    "research/tsm-followup-20261101/agent-neural/acoustic.pt",
    "data/models/speech-rate-encoders/wavlm-base-plus",
    "data/models/speech-rate-encoders/wavlm-base-plus/config.json",
    "data/models/speech-rate-encoders/wavlm-base",
    "data/models/wavlm-base-plus",
    "data/envs/sylnet-py310",
    "data/envs",
    "data/checkouts/disfluency_detection_from_audio/demo_models",
    "data/checkouts/disfluency_detection_from_audio/demo_models/acoustic.pt",
    "data/checkouts/disfluency_detection_from_audio/pretrained_models",
    "data/models/speech-rate-encoders/disfluency",
    "data/models/disfluency",
    "research/tsm-followup-20261101/agent-neural/weights",
)

HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--microsoft--wavlm-base-plus",
    "~/.cache/huggingface/hub/models--microsoft--wavlm-base",
    "~/.cache/huggingface/hub/models--microsoft--wavlm-base-plus/snapshots",
    "~/.cache/torch/hub/checkpoints",
)

SOURCE_SNIPPETS = (
    "WavLMModel.from_pretrained('microsoft/wavlm-base')",
    "self.linear = nn.Linear(768, 5)",
    "self.basemodel.encoder(feats, return_dict=True)[0]",
    "gdown --id 1wWrmopvvdhlBw-cL7EDyih9zn_IJu5Wr -O acoustic.pt",
    "filled pauses, partial words, repetitions, revisions, and restarts",
    "labels_framelevel",
)

SMOKE_SNIPPETS = (
    "from transformers import WavLMConfig, WavLMModel, Wav2Vec2FeatureExtractor",
    "config=WavLMConfig.from_pretrained(str(ROOT/'data/models/speech-rate-"
    "encoders/wavlm-base-plus'))",
    "state=torch.load(ROOT/'research/tsm-followup-20261101/agent-neural/"
    "disfluency_acoustic.pt',map_location='cpu')",
    "prob=logits.sigmoid()[0]",
    "pred=(prob>0.5).int()",
    "labels=['FP','RP','RV','RS','PW']",
)

MANIFEST_FIELDS = ("schema_id", "cohort_id", "source", "weights", "backbone",
                   "runtime", "feature_extractor", "labels", "audio",
                   "controls", "outcomes", "rights")
SOURCE_FIELDS = ("repo_id", "commit", "license_id", "license_reference")
WEIGHTS_FIELDS = ("file", "sha256", "byte_count", "terms_reference")
BACKBONE_FIELDS = ("repo_id", "revision", "config_sha256", "license_id")
RUNTIME_FIELDS = ("python", "torch", "transformers", "device", "offline")
FEATURE_FIELDS = ("sample_rate_hz", "frame_ms", "normalize")
LABEL_FIELDS = ("names", "frame_label_source", "human_verified")
AUDIO_FIELDS = ("id", "path", "sha256", "language", "speaker_group",
                "meeting_id", "start_s", "end_s", "sample_rate_hz")
CONTROL_FIELDS = ("id", "kind")
OUTCOME_FIELDS = ("frame_count", "nonfinite_count", "per_label")
PER_LABEL_FIELDS = ("label", "precision", "recall", "f1", "onset_delay_ms")
RIGHTS_FIELDS = ("dataset_terms_reference", "source_terms_reference",
                 "weights_terms_reference", "label_terms_reference",
                 "output_use_reference", "review_reference",
                 "claims_qualified")
CONTROL_KINDS = ("human_frame_label_baseline", "candidate",
                 "all_negative_baseline")
BACKBONE_REPOS = (BACKBONE_REPO, SMOKE_CONFIG_REPO)
MANIFEST_LABELS = tuple(LABELS)
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
LANGUAGE = re.compile(r"^[a-z]{2,3}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ABSOLUTE = re.compile(r"^/[A-Za-z0-9._/-]+$")
MAX_WEIGHT_BYTES = 4 * 1024 * 1024 * 1024
MAX_AUDIO_WINDOWS = 4096
MAX_FRAME_COUNT = 100000
MAX_DELAY_MS = 5000.0


# --------------------------------------------------------------------------
# Strict JSON, canonical bytes, pins
# --------------------------------------------------------------------------
def _reject_constant(value: str) -> None:
    raise ValueError("nonfinite_json_constant:" + value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def loads_strict(text: str) -> dict:
    """Parse a strict JSON object; reject duplicate keys, NaN and Infinity."""
    if text.startswith("\ufeff"):
        raise ValueError("json_byte_order_mark")
    parsed = json.loads(text, object_pairs_hook=_unique_object,
                        parse_constant=_reject_constant)
    if not isinstance(parsed, dict):
        raise ValueError("json_root_not_object")
    return parsed


def read_strict_json(path: Path) -> dict:
    return loads_strict(Path(path).read_text(encoding="utf-8"))


def canonical_text(document: Any) -> str:
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False) + "\n"


def canonical_bytes(document: Any) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: Any) -> str:
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _no_floats(value: Any, path: str = "") -> None:
    if isinstance(value, float):
        raise ValueError("float_in_canonical_report:" + (path or "<root>"))
    if isinstance(value, dict):
        for key in sorted(value):
            _no_floats(value[key], (path + "." + str(key)).lstrip("."))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _no_floats(item, f"{path}[{index}]")


def _decimal_string(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("nonfinite_decimal")
    text = repr(float(value))
    if "e" in text or "E" in text:
        text = format(float(value), ".17f").rstrip("0").rstrip(".")
    if text in {"-0", "-0.0"}:
        text = "0"
    if text.startswith("+"):
        text = text[1:]
    return text


def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for relative in sorted(pins):
        path = root / relative
        if not path.is_file():
            raise ValueError("pin_target_missing:" + relative)
        actual = sha256_file(path)
        if actual != pins[relative]:
            raise ValueError("pin_digest_mismatch:" + relative)
        rows[relative] = {"sha256": pins[relative], "actual": actual,
                          "verified": True}
    return rows


def board_row_projection(path: Path) -> dict:
    board = read_strict_json(path)
    rows = [row for row in board.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise ValueError("board_row_not_unique:" + TASK)
    return {field: rows[0].get(field) for field in BOARD_ROW_FIELDS}


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def linked_rows(path: Path | None = None) -> list[dict]:
    board = read_strict_json(path or (AUDIO_ROOT / BOARD_TASK_ROW))
    by_id = {row.get("id"): row for row in board.get("tasks", [])
             if isinstance(row, dict)}
    rows: list[dict] = []
    for row_id in LINKED_ROW_IDS:
        row = by_id.get(row_id)
        if row is None:
            raise ValueError("linked_row_missing:" + row_id)
        rows.append({field: row.get(field) for field in BOARD_ROW_FIELDS})
    return rows


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return object_digest(rows if rows is not None else linked_rows())


def absence_probes(audio_root: Path, probes: tuple[str, ...] = ABSENCE_PROBES,
                   worktree: Path | None = None) -> list[dict]:
    """Return the fixed probe inventory; any present path blocks shipping."""
    sdk_root = WORKTREE if worktree is None else worktree
    rows: list[dict] = []
    for relative in probes:
        workspace_path = Path(audio_root) / relative
        sdk_candidate = sdk_root / relative
        if workspace_path.exists() or sdk_candidate.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_workspace": True,
                     "searched_sdk_worktree": True, "present": False})
    return rows


def home_absence_probes(probes: tuple[str, ...] = HOME_ABSENCE_PROBES) -> list[dict]:
    rows: list[dict] = []
    home = Path.home()
    for relative in probes:
        path = home / relative[2:] if relative.startswith("~/") else Path(relative)
        if path.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_home_cache": True,
                     "present": False})
    return rows


def absence_summary(rows: list[dict], home_rows: list[dict]) -> dict:
    all_rows = rows + home_rows
    return {
        "probe_count": len(all_rows),
        "workspace_probe_count": len(rows),
        "home_probe_count": len(home_rows),
        "present_count": sum(1 for row in all_rows if row["present"]),
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "source_or_runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "all_probes_absent": all(not row["present"] for row in all_rows),
    }


def repository_head(repository: Path) -> str:
    """Read the checked-out commit from .git without invoking git or a network."""
    git_dir = repository / ".git"
    head = git_dir / "HEAD"
    if not head.is_file():
        raise ValueError("repository_head_missing")
    text = head.read_text(encoding="ascii").strip()
    if text.startswith("ref: "):
        reference = text[5:].strip()
        ref_path = git_dir / reference
        if ref_path.is_file():
            return ref_path.read_text(encoding="ascii").strip()
        packed = git_dir / "packed-refs"
        if packed.is_file():
            for line in packed.read_text(encoding="ascii").splitlines():
                parts = line.split()
                if len(parts) == 2 and parts[1] == reference:
                    return parts[0]
        raise ValueError("repository_ref_missing:" + reference)
    return text


def source_inventory() -> dict:
    repository = AUDIO_ROOT / "data/checkouts/disfluency_detection_from_audio"
    if not repository.is_dir():
        raise ValueError("upstream_repository_missing")
    head = repository_head(repository)
    if head != UPSTREAM_COMMIT:
        raise ValueError("upstream_commit_mismatch")
    text = (repository / "README.md").read_text(encoding="utf-8")
    model_text = (repository / "models.py").read_text(encoding="utf-8")
    combined = text + "\n" + model_text
    snippets = {snippet: (snippet in combined) for snippet in SOURCE_SNIPPETS}
    missing = [snippet for snippet, present in snippets.items() if not present]
    if missing:
        raise ValueError("source_snippet_missing:" + missing[0])
    license_files = [
        name for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE",
                          "LICENCE.md", "COPYING", "NOTICE")
        if (repository / name).exists()
    ]
    if license_files:
        raise ValueError("upstream_license_appeared_reopen_required")
    files = []
    for relative in ("README.md", "models.py", "demo.py"):
        path = repository / relative
        files.append({
            "path": ("data/checkouts/disfluency_detection_from_audio/" +
                     relative),
            "sha256": sha256_file(path),
            "byte_count": path.stat().st_size,
        })
    return {
        "repository_path": "data/checkouts/disfluency_detection_from_audio",
        "repo_id": UPSTREAM_REPO,
        "declared_commit": UPSTREAM_COMMIT,
        "head_commit": head,
        "head_matches": head == UPSTREAM_COMMIT,
        "license": UPSTREAM_LICENSE,
        "license_status": UPSTREAM_LICENSE_STATUS,
        "license_files_present": license_files,
        "license_declared_in_readme": "license" in text.lower(),
        "files": files,
        "source_snippets_present": len(snippets),
        "source_snippets_required": len(SOURCE_SNIPPETS),
        "model_definition": {
            "module": "models.AcousticModel",
            "backbone": BACKBONE_REPO,
            "backbone_class": "WavLMModel",
            "head": "torch.nn.Linear(768,5)",
            "label_count": len(LABELS),
            "labels": list(LABELS),
            "activation": "sigmoid",
            "threshold": "0.5",
            "frame_interval_ms": FRAME_INTERVAL_MS,
        },
        "terms_reviewed": False,
        "vendored": False,
        "downloaded": False,
    }


def documented_smoke() -> dict:
    """Read the pinned smoke output and return provenance-only decimal strings."""
    relative = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "disfluency_acoustic_smoke.json")
    data = read_strict_json(AUDIO_ROOT / relative)
    if data.get("repo_commit") != UPSTREAM_COMMIT:
        raise ValueError("documented_smoke_commit_mismatch")
    if data.get("weight_bytes") != CHECKPOINT_BYTES \
            or data.get("weight_sha256") != CHECKPOINT_SHA256:
        raise ValueError("documented_smoke_weight_mismatch")
    if data.get("sample") != SAMPLE_ID:
        raise ValueError("documented_smoke_sample_mismatch")
    if data.get("duration_s") != float(DURATION_S):
        raise ValueError("documented_smoke_duration_mismatch")
    if data.get("frame_count") != FRAME_COUNT:
        raise ValueError("documented_smoke_frame_count_mismatch")
    if data.get("labels") != list(LABELS):
        raise ValueError("documented_smoke_labels_mismatch")
    if data.get("positive_frame_count_per_label") != POSITIVE_FRAMES:
        raise ValueError("documented_smoke_positive_mismatch")
    if data.get("missing_keys") != [] or data.get("unexpected_keys") != []:
        raise ValueError("documented_smoke_state_mismatch")
    config = data.get("config", "")
    if SMOKE_CONFIG_REPO not in config:
        raise ValueError("documented_smoke_config_mismatch")
    elapsed = data.get("cpu_model_only_ms")
    if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) \
            or not math.isfinite(float(elapsed)):
        raise ValueError("documented_smoke_timing_nonfinite")
    warning = data.get("warning", "")
    if "no LICENSE" not in warning:
        raise ValueError("documented_smoke_warning_mismatch")
    return {
        "source_path": relative,
        "source_sha256": SOURCE_PINS[relative],
        "candidate": data.get("candidate"),
        "repo_commit": UPSTREAM_COMMIT,
        "weight_bytes": str(CHECKPOINT_BYTES),
        "weight_sha256": CHECKPOINT_SHA256,
        "config": config,
        "sample": SAMPLE_ID,
        "duration_s": DURATION_S,
        "frame_count": FRAME_COUNT,
        "frame_interval_ms": FRAME_INTERVAL_MS,
        "cpu_model_only_ms": _decimal_string(float(elapsed)),
        "labels": list(LABELS),
        "positive_frame_count_per_label": dict(POSITIVE_FRAMES),
        "missing_keys": 0,
        "unexpected_keys": 0,
        "warning": warning,
        "provenance_only": True,
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
        "why_not_reproduced": [
            "The 377,639,565-byte checkpoint is absent.",
            "The WavLM backbone configuration/weights are absent.",
            "The Python 3.10.13/torch 2.2.2/transformers 4.40.2 runtime is "
            "absent.",
            "AMI supplies no matching framewise FP/RP/RV/RS/PW labels.",
            "The source and checkpoint declare no license or terms.",
        ],
    }


def smoke_runner_provenance() -> dict:
    relative = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "run_acoustic_disfluency_smoke.py")
    text = (AUDIO_ROOT / relative).read_text(encoding="utf-8")
    found = {snippet: (snippet in text) for snippet in SMOKE_SNIPPETS}
    missing = [snippet for snippet, present in found.items() if not present]
    if missing:
        raise ValueError("smoke_snippet_missing:" + missing[0])
    source_record_relative = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "wavlm-base-plus_source.json")
    source = read_strict_json(AUDIO_ROOT / source_record_relative)
    if source.get("repo_id") != SMOKE_CONFIG_REPO \
            or source.get("revision") != SMOKE_CONFIG_REVISION \
            or source.get("license") is not None:
        raise ValueError("smoke_config_source_mismatch")
    files = source.get("files", {}).get("config.json", {})
    if files.get("bytes") != SMOKE_CONFIG_BYTES \
            or files.get("sha256") != SMOKE_CONFIG_SHA256:
        raise ValueError("smoke_config_file_record_mismatch")
    return {
        "runner_path": relative,
        "runner_sha256": SOURCE_PINS[relative],
        "snippets_present": len(found),
        "snippets_required": len(SMOKE_SNIPPETS),
        "config_repo_id": SMOKE_CONFIG_REPO,
        "config_revision": SMOKE_CONFIG_REVISION,
        "config_bytes": str(SMOKE_CONFIG_BYTES),
        "config_sha256": SMOKE_CONFIG_SHA256,
        "config_license": None,
        "config_license_status": "not_declared",
        "config_source_sha256": SOURCE_PINS[source_record_relative],
        "executed_here": False,
        "network_used": False,
        "downloaded": False,
    }


def source_presence() -> dict:
    repository = AUDIO_ROOT / "data/checkouts/disfluency_detection_from_audio"
    license_files = [
        name for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE",
                          "LICENCE.md", "COPYING", "NOTICE")
        if (repository / name).exists()
    ]
    return {
        "upstream_repository_present": repository.is_dir(),
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_license_present": bool(license_files),
        "upstream_license_files": license_files,
        "source_terms_reviewed": False,
        "checkpoint_present": False,
        "backbone_config_present": False,
        "backbone_weights_present": False,
        "runtime_present": False,
        "audio_clip_recorded_in_research_bundle": True,
        "frame_labels_present": False,
        "exact_source_weights_runtime_licensed_conjunction_present": False,
        "weights_used": False,
        "runtime_imported": False,
        "audio_read": False,
        "model_executed": False,
        "downloaded_or_reconstructed": False,
    }


# --------------------------------------------------------------------------
# Fail-closed caller-supplied frame-level cohort admission (task-local only)
# --------------------------------------------------------------------------
def _type_name(value: Any) -> str:
    return type(value).__name__


def _require_object(value: Any, path: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{path}:not_object:{_type_name(value)}")
    return value


def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> dict:
    obj = _require_object(value, path)
    actual = set(obj)
    if actual != set(expected):
        missing = sorted(set(expected) - actual)
        extra = sorted(actual - set(expected))
        raise ValueError(f"{path}:keys:missing={missing},extra={extra}")
    return obj


def _text(obj: dict, key: str, path: str,
          pattern: re.Pattern | None = None, maximum: int = 512) -> str:
    value = obj.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{path}.{key}:not_string:{_type_name(value)}")
    if not value or len(value) > maximum:
        raise ValueError(f"{path}.{key}:empty_or_too_long")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise ValueError(f"{path}.{key}:pattern")
    return value


def _int(obj: dict, key: str, path: str, minimum: int,
         maximum: int) -> int:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path}.{key}:not_integer:{_type_name(value)}")
    if value < minimum or value > maximum:
        raise ValueError(f"{path}.{key}:out_of_range")
    return value


def _number(obj: dict, key: str, path: str, minimum: float,
            maximum: float) -> float:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{path}.{key}:not_number:{_type_name(value)}")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{path}.{key}:nonfinite")
    if number < minimum or number > maximum:
        raise ValueError(f"{path}.{key}:out_of_range")
    return number


def _boolean(obj: dict, key: str, path: str,
             expected: bool | None = None) -> bool:
    value = obj.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{path}.{key}:not_boolean:{_type_name(value)}")
    if expected is not None and value is not expected:
        raise ValueError(f"{path}.{key}:expected_{expected}")
    return value


def _hex(obj: dict, key: str, path: str) -> str:
    return _text(obj, key, path, HEX64)


def _nonzero_hex(obj: dict, key: str, path: str) -> str:
    value = _hex(obj, key, path)
    if value == "0" * 64:
        raise ValueError(f"{path}.{key}:zero_digest")
    return value


def validate_manifest(manifest: dict) -> None:
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root["schema_id"] != ADMISSION_SCHEMA_ID:
        raise ValueError("manifest.schema_id:mismatch")
    _text(root, "cohort_id", "manifest", SLUG)

    source = _exact_keys(root["source"], SOURCE_FIELDS, "manifest.source")
    if source["repo_id"] != UPSTREAM_REPO:
        raise ValueError("manifest.source.repo_id:mismatch")
    if source["commit"] != UPSTREAM_COMMIT:
        raise ValueError("manifest.source.commit:mismatch")
    license_id = _text(source, "license_id", "manifest.source", maximum=96)
    if license_id.lower() in {"none", "null", "unlicensed", "unknown"}:
        raise ValueError("manifest.source.license_id:not_declared")
    _text(source, "license_reference", "manifest.source", maximum=512)

    weights = _exact_keys(root["weights"], WEIGHTS_FIELDS, "manifest.weights")
    if weights["file"] != CHECKPOINT_FILE:
        raise ValueError("manifest.weights.file:mismatch")
    if weights["sha256"] != CHECKPOINT_SHA256:
        raise ValueError("manifest.weights.sha256:mismatch")
    if _int(weights, "byte_count", "manifest.weights", 1,
            MAX_WEIGHT_BYTES) != CHECKPOINT_BYTES:
        raise ValueError("manifest.weights.byte_count:mismatch")
    _text(weights, "terms_reference", "manifest.weights", maximum=512)

    backbone = _exact_keys(root["backbone"], BACKBONE_FIELDS,
                           "manifest.backbone")
    if backbone["repo_id"] not in BACKBONE_REPOS:
        raise ValueError("manifest.backbone.repo_id:mismatch")
    _text(backbone, "revision", "manifest.backbone", HEX40)
    _nonzero_hex(backbone, "config_sha256", "manifest.backbone")
    _text(backbone, "license_id", "manifest.backbone", maximum=96)

    runtime = _exact_keys(root["runtime"], RUNTIME_FIELDS, "manifest.runtime")
    if runtime["python"] != RUNTIME_PYTHON:
        raise ValueError("manifest.runtime.python:mismatch")
    if runtime["torch"] != RUNTIME_TORCH:
        raise ValueError("manifest.runtime.torch:mismatch")
    if runtime["transformers"] != RUNTIME_TRANSFORMERS:
        raise ValueError("manifest.runtime.transformers:mismatch")
    if runtime["device"] != "cpu":
        raise ValueError("manifest.runtime.device:mismatch")
    _boolean(runtime, "offline", "manifest.runtime", True)

    feature = _exact_keys(root["feature_extractor"], FEATURE_FIELDS,
                          "manifest.feature_extractor")
    if _int(feature, "sample_rate_hz", "manifest.feature_extractor", 1,
            SAMPLE_RATE_HZ) != SAMPLE_RATE_HZ:
        raise ValueError("manifest.feature_extractor.sample_rate_hz:mismatch")
    if _int(feature, "frame_ms", "manifest.feature_extractor", 1,
            FRAME_INTERVAL_MS) != FRAME_INTERVAL_MS:
        raise ValueError("manifest.feature_extractor.frame_ms:mismatch")
    _boolean(feature, "normalize", "manifest.feature_extractor", True)

    labels = _exact_keys(root["labels"], LABEL_FIELDS, "manifest.labels")
    names = labels["names"]
    if not isinstance(names, list) or names != list(MANIFEST_LABELS):
        raise ValueError("manifest.labels.names:mismatch")
    _text(labels, "frame_label_source", "manifest.labels", maximum=512)
    _boolean(labels, "human_verified", "manifest.labels", True)

    audio = root["audio"]
    if not isinstance(audio, list):
        raise ValueError("manifest.audio:not_list:" + _type_name(audio))
    if not 1 <= len(audio) <= MAX_AUDIO_WINDOWS:
        raise ValueError("manifest.audio:count")
    seen_ids: set[str] = set()
    for index, item in enumerate(audio):
        path = f"manifest.audio[{index}]"
        record = _exact_keys(item, AUDIO_FIELDS, path)
        identifier = _text(record, "id", path, SLUG)
        if identifier in seen_ids:
            raise ValueError(f"{path}.id:duplicate")
        seen_ids.add(identifier)
        _text(record, "path", path, ABSOLUTE, maximum=1024)
        _nonzero_hex(record, "sha256", path)
        _text(record, "language", path, LANGUAGE)
        _text(record, "speaker_group", path, SLUG)
        _text(record, "meeting_id", path, SLUG)
        start = _number(record, "start_s", path, 0.0, 1e9)
        end = _number(record, "end_s", path, 0.0, 1e9)
        if not math.isclose(end - start, float(DURATION_S), abs_tol=1e-9):
            raise ValueError(f"{path}:duration_mismatch")
        if _int(record, "sample_rate_hz", path, 1, SAMPLE_RATE_HZ) \
                != SAMPLE_RATE_HZ:
            raise ValueError(f"{path}.sample_rate_hz:mismatch")

    controls = root["controls"]
    if not isinstance(controls, list) or len(controls) != len(CONTROL_KINDS):
        raise ValueError("manifest.controls:count")
    seen_controls: set[str] = set()
    kinds: list[str] = []
    for index, item in enumerate(controls):
        path = f"manifest.controls[{index}]"
        record = _exact_keys(item, CONTROL_FIELDS, path)
        identifier = _text(record, "id", path, SLUG)
        if identifier in seen_controls:
            raise ValueError(f"{path}.id:duplicate")
        seen_controls.add(identifier)
        kind = _text(record, "kind", path, maximum=64)
        if kind not in CONTROL_KINDS:
            raise ValueError(f"{path}.kind:mismatch")
        kinds.append(kind)
    if tuple(kinds) != CONTROL_KINDS:
        raise ValueError("manifest.controls:kinds")

    outcomes = _exact_keys(root["outcomes"], OUTCOME_FIELDS,
                           "manifest.outcomes")
    _int(outcomes, "frame_count", "manifest.outcomes", 1, MAX_FRAME_COUNT)
    if _int(outcomes, "nonfinite_count", "manifest.outcomes", 0,
            MAX_FRAME_COUNT) != 0:
        raise ValueError("manifest.outcomes.nonfinite_count:nonzero")
    per_label = outcomes["per_label"]
    if not isinstance(per_label, list) or len(per_label) != len(LABELS):
        raise ValueError("manifest.outcomes.per_label:count")
    ordered_labels: list[str] = []
    for index, item in enumerate(per_label):
        path = f"manifest.outcomes.per_label[{index}]"
        record = _exact_keys(item, PER_LABEL_FIELDS, path)
        label = _text(record, "label", path, maximum=8)
        if label not in LABELS:
            raise ValueError(f"{path}.label:mismatch")
        ordered_labels.append(label)
        _number(record, "precision", path, 0.0, 1.0)
        _number(record, "recall", path, 0.0, 1.0)
        _number(record, "f1", path, 0.0, 1.0)
        _number(record, "onset_delay_ms", path, -MAX_DELAY_MS, MAX_DELAY_MS)
    if ordered_labels != list(LABELS):
        raise ValueError("manifest.outcomes.per_label:labels")

    rights = _exact_keys(root["rights"], RIGHTS_FIELDS, "manifest.rights")
    for key in RIGHTS_FIELDS[:-1]:
        _text(rights, key, "manifest.rights", maximum=512)
    _boolean(rights, "claims_qualified", "manifest.rights", False)


def _synthetic_digest(label: str) -> str:
    return hashlib.sha256(("synthetic-admission-control:" + label)
                          .encode("utf-8")).hexdigest()


def control_manifest() -> dict:
    """A structure-only control; never evidence and never a real asset."""
    audio = []
    for index in range(2):
        identifier = f"syn-{index + 1:04d}"
        audio.append({
            "id": identifier,
            "path": f"/synthetic/cohort/{identifier}.wav",
            "sha256": _synthetic_digest("audio-" + identifier),
            "language": "en",
            "speaker_group": f"speaker-{'ab'[index]}",
            "meeting_id": f"meeting-{'ab'[index]}",
            "start_s": float(index * 4),
            "end_s": float((index + 1) * 4),
            "sample_rate_hz": SAMPLE_RATE_HZ,
        })
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "cohort_id": "synthetic-admission-control",
        "source": {
            "repo_id": UPSTREAM_REPO,
            "commit": UPSTREAM_COMMIT,
            "license_id": "reviewed-permission-001",
            "license_reference": "review://synthetic/source-terms",
        },
        "weights": {
            "file": CHECKPOINT_FILE,
            "sha256": CHECKPOINT_SHA256,
            "byte_count": CHECKPOINT_BYTES,
            "terms_reference": "review://synthetic/weight-terms",
        },
        "backbone": {
            "repo_id": BACKBONE_REPO,
            "revision": "0" * 39 + "1",
            "config_sha256": _synthetic_digest("backbone-config"),
            "license_id": "reviewed-permission-001",
        },
        "runtime": {
            "python": RUNTIME_PYTHON,
            "torch": RUNTIME_TORCH,
            "transformers": RUNTIME_TRANSFORMERS,
            "device": "cpu",
            "offline": True,
        },
        "feature_extractor": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "frame_ms": FRAME_INTERVAL_MS,
            "normalize": True,
        },
        "labels": {
            "names": list(LABELS),
            "frame_label_source": "synthetic-human-frame-labels",
            "human_verified": True,
        },
        "audio": audio,
        "controls": [
            {"id": "ctl-01", "kind": "human_frame_label_baseline"},
            {"id": "ctl-02", "kind": "candidate"},
            {"id": "ctl-03", "kind": "all_negative_baseline"},
        ],
        "outcomes": {
            "frame_count": FRAME_COUNT,
            "nonfinite_count": 0,
            "per_label": [
                {"label": label, "precision": 0.5, "recall": 0.5,
                 "f1": 0.5, "onset_delay_ms": 0.0}
                for label in LABELS
            ],
        },
        "rights": {
            "dataset_terms_reference": "review://synthetic/dataset-terms",
            "source_terms_reference": "review://synthetic/source-terms",
            "weights_terms_reference": "review://synthetic/weight-terms",
            "label_terms_reference": "review://synthetic/label-terms",
            "output_use_reference": "review://synthetic/output-use",
            "review_reference": "review://synthetic/review",
            "claims_qualified": False,
        },
    }


def _mutation_cases() -> list[tuple[str, str, Any]]:
    cases: list[tuple[str, str, Any]] = []

    def add(case_id: str, description: str, mutate: Any) -> None:
        cases.append((case_id, description, mutate))

    add("ADM-01", "Reject a non-object manifest.",
        lambda m: None)
    add("ADM-02", "Reject a missing top-level field.",
        lambda m: m.pop("rights"))
    add("ADM-03", "Reject an extra top-level field.",
        lambda m: m.update({"unexpected": True}))
    add("ADM-04", "Reject a non-string schema id.",
        lambda m: m.update({"schema_id": 1}))
    add("ADM-05", "Reject a wrong schema id.",
        lambda m: m.update({"schema_id": "audio-sdk/other/0.1"}))
    add("ADM-06", "Reject an empty cohort id.",
        lambda m: m.update({"cohort_id": ""}))
    add("ADM-07", "Reject a missing source field.",
        lambda m: m["source"].pop("license_reference"))
    add("ADM-08", "Reject an extra source field.",
        lambda m: m["source"].update({"note": "x"}))
    add("ADM-09", "Reject a different source repository.",
        lambda m: m["source"].update({"repo_id": "other/repo"}))
    add("ADM-10", "Reject a different source commit.",
        lambda m: m["source"].update({"commit": "0" * 40}))
    add("ADM-11", "Reject an uppercase source commit.",
        lambda m: m["source"].update(
            {"commit": UPSTREAM_COMMIT.upper()}))
    add("ADM-12", "Reject a missing source license id.",
        lambda m: m["source"].update({"license_id": ""}))
    add("ADM-13", "Reject an explicitly unlicensed source.",
        lambda m: m["source"].update({"license_id": "none"}))
    add("ADM-14", "Reject an unknown source license id.",
        lambda m: m["source"].update({"license_id": "unlicensed"}))
    add("ADM-15", "Reject an empty source license reference.",
        lambda m: m["source"].update({"license_reference": ""}))
    add("ADM-16", "Reject a missing weight field.",
        lambda m: m["weights"].pop("terms_reference"))
    add("ADM-17", "Reject an extra weight field.",
        lambda m: m["weights"].update({"note": "x"}))
    add("ADM-18", "Reject a different checkpoint filename.",
        lambda m: m["weights"].update({"file": "pytorch_model.bin"}))
    add("ADM-19", "Reject a wrong checkpoint digest.",
        lambda m: m["weights"].update({"sha256": "0" * 64}))
    add("ADM-20", "Reject a short checkpoint digest.",
        lambda m: m["weights"].update({"sha256": "0" * 63}))
    add("ADM-21", "Reject a wrong checkpoint byte count.",
        lambda m: m["weights"].update(
            {"byte_count": CHECKPOINT_BYTES + 1}))
    add("ADM-22", "Reject a boolean checkpoint byte count.",
        lambda m: m["weights"].update({"byte_count": True}))
    add("ADM-23", "Reject a negative checkpoint byte count.",
        lambda m: m["weights"].update({"byte_count": -1}))
    add("ADM-24", "Reject an empty weight terms reference.",
        lambda m: m["weights"].update({"terms_reference": ""}))
    add("ADM-25", "Reject a different backbone repository.",
        lambda m: m["backbone"].update({"repo_id": "microsoft/wavlm-large"}))
    add("ADM-26", "Reject a short backbone revision.",
        lambda m: m["backbone"].update({"revision": "0" * 39}))
    add("ADM-27", "Reject a wrong backbone config digest.",
        lambda m: m["backbone"].update({"config_sha256": "0" * 64}))
    add("ADM-28", "Reject an empty backbone license id.",
        lambda m: m["backbone"].update({"license_id": ""}))
    add("ADM-29", "Reject a different Python runtime.",
        lambda m: m["runtime"].update({"python": "3.11.5"}))
    add("ADM-30", "Reject a different torch runtime.",
        lambda m: m["runtime"].update({"torch": "1.12.1"}))
    add("ADM-31", "Reject a different transformers runtime.",
        lambda m: m["runtime"].update({"transformers": "4.22.2"}))
    add("ADM-32", "Reject a non-CPU device.",
        lambda m: m["runtime"].update({"device": "cuda"}))
    add("ADM-33", "Reject offline disabled.",
        lambda m: m["runtime"].update({"offline": False}))
    add("ADM-34", "Reject a boolean Python version.",
        lambda m: m["runtime"].update({"python": True}))
    add("ADM-35", "Reject a wrong feature sample rate.",
        lambda m: m["feature_extractor"].update({"sample_rate_hz": 8000}))
    add("ADM-36", "Reject a wrong frame interval.",
        lambda m: m["feature_extractor"].update({"frame_ms": 10}))
    add("ADM-37", "Reject normalization disabled.",
        lambda m: m["feature_extractor"].update({"normalize": False}))
    add("ADM-38", "Reject a missing label field.",
        lambda m: m["labels"].pop("human_verified"))
    add("ADM-39", "Reject reordered labels.",
        lambda m: m["labels"].update({"names": list(reversed(LABELS))}))
    add("ADM-40", "Reject a missing label.",
        lambda m: m["labels"].update({"names": list(LABELS[:-1])}))
    add("ADM-41", "Reject unverified human labels.",
        lambda m: m["labels"].update({"human_verified": False}))
    add("ADM-42", "Reject an empty label source.",
        lambda m: m["labels"].update({"frame_label_source": ""}))
    add("ADM-43", "Reject a non-list audio field.",
        lambda m: m.update({"audio": {}}))
    add("ADM-44", "Reject an empty audio list.",
        lambda m: m.update({"audio": []}))
    add("ADM-45", "Reject a duplicate audio id.",
        lambda m: m["audio"][1].update({"id": m["audio"][0]["id"]}))
    add("ADM-46", "Reject a relative audio path.",
        lambda m: m["audio"][0].update({"path": "relative.wav"}))
    add("ADM-47", "Reject a short audio digest.",
        lambda m: m["audio"][0].update({"sha256": "0" * 63}))
    add("ADM-48", "Reject a wrong language code.",
        lambda m: m["audio"][0].update({"language": "english"}))
    add("ADM-49", "Reject a wrong audio sample rate.",
        lambda m: m["audio"][0].update({"sample_rate_hz": 8000}))
    add("ADM-50", "Reject a negative audio start.",
        lambda m: m["audio"][0].update({"start_s": -0.5}))
    add("ADM-51", "Reject a nonfinite audio start.",
        lambda m: m["audio"][0].update({"start_s": float("nan")}))
    add("ADM-52", "Reject a nonfinite audio end.",
        lambda m: m["audio"][0].update({"end_s": float("inf")}))
    add("ADM-53", "Reject a non-four-second audio window.",
        lambda m: m["audio"][0].update({"end_s": 3.0}))
    add("ADM-54", "Reject an empty speaker group.",
        lambda m: m["audio"][0].update({"speaker_group": ""}))
    add("ADM-55", "Reject an empty meeting id.",
        lambda m: m["audio"][0].update({"meeting_id": ""}))
    add("ADM-56", "Reject a boolean window start.",
        lambda m: m["audio"][0].update({"start_s": True}))
    add("ADM-57", "Reject a missing control.",
        lambda m: m["controls"].pop())
    add("ADM-58", "Reject a duplicate control kind.",
        lambda m: m["controls"][1].update({"kind": "candidate"})
        or m["controls"][2].update({"kind": "candidate"}))
    add("ADM-59", "Reject an unknown control kind.",
        lambda m: m["controls"][0].update({"kind": "other_control"}))
    add("ADM-60", "Reject a duplicate control id.",
        lambda m: m["controls"][1].update({"id": "ctl-01"}))
    add("ADM-61", "Reject a missing outcomes field.",
        lambda m: m["outcomes"].pop("per_label"))
    add("ADM-62", "Reject zero frame count.",
        lambda m: m["outcomes"].update({"frame_count": 0}))
    add("ADM-63", "Reject a boolean frame count.",
        lambda m: m["outcomes"].update({"frame_count": True}))
    add("ADM-64", "Reject a nonzero nonfinite count.",
        lambda m: m["outcomes"].update({"nonfinite_count": 1}))
    add("ADM-65", "Reject a missing per-label row.",
        lambda m: m["outcomes"]["per_label"].pop())
    add("ADM-66", "Reject reordered per-label rows.",
        lambda m: m["outcomes"].update(
            {"per_label": list(reversed(m["outcomes"]["per_label"]))}))
    add("ADM-67", "Reject a duplicate per-label row.",
        lambda m: m["outcomes"]["per_label"][1].update(
            {"label": m["outcomes"]["per_label"][0]["label"]}))
    add("ADM-68", "Reject nonfinite precision.",
        lambda m: m["outcomes"]["per_label"][0].update(
            {"precision": float("nan")}))
    add("ADM-69", "Reject out-of-range precision.",
        lambda m: m["outcomes"]["per_label"][0].update({"precision": 1.5}))
    add("ADM-70", "Reject negative recall.",
        lambda m: m["outcomes"]["per_label"][0].update({"recall": -0.1}))
    add("ADM-71", "Reject out-of-range F1.",
        lambda m: m["outcomes"]["per_label"][0].update({"f1": 2}))
    add("ADM-72", "Reject nonfinite onset delay.",
        lambda m: m["outcomes"]["per_label"][0].update(
            {"onset_delay_ms": float("-inf")}))
    add("ADM-73", "Reject out-of-range onset delay.",
        lambda m: m["outcomes"]["per_label"][0].update(
            {"onset_delay_ms": MAX_DELAY_MS + 1}))
    add("ADM-74", "Reject a missing rights field.",
        lambda m: m["rights"].pop("review_reference"))
    add("ADM-75", "Reject an empty rights reference.",
        lambda m: m["rights"].update({"output_use_reference": ""}))
    add("ADM-76", "Reject a qualified claim.",
        lambda m: m["rights"].update({"claims_qualified": True}))
    add("ADM-77", "Reject a non-boolean qualified claim.",
        lambda m: m["rights"].update({"claims_qualified": 1}))
    return cases


def admission_cases() -> list[dict]:
    control = control_manifest()
    cases: list[dict] = []
    for case_id, description, mutate in _mutation_cases():
        candidate = copy.deepcopy(control)
        if case_id == "ADM-01":
            candidate = []
        else:
            mutate(candidate)
        before = copy.deepcopy(candidate)
        try:
            validate_manifest(candidate)
        except ValueError as error:
            code = str(error)
        else:
            raise RuntimeError("mutation_not_rejected:" + case_id)
        if candidate != before:
            raise RuntimeError("mutation_changed_state:" + case_id)
        cases.append({
            "id": case_id,
            "description": description,
            "status": "rejected",
            "code": code,
            "qualifies": False,
            "state_unchanged": True,
        })
    return cases


def build_admission() -> dict:
    control = copy.deepcopy(control_manifest())
    before = copy.deepcopy(control)
    validate_manifest(control)
    if control != before:
        raise RuntimeError("admission_control_mutated")
    cases = admission_cases()
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "boundary": "task_local_manifest_admission_only_not_a_runtime",
        "control": {
            "id": "ADM-ACCEPT-01",
            "accepted": True,
            "qualifies": False,
            "label": "synthetic_schema_control_not_evidence",
            "state_unchanged": True,
            "audio_records": len(control["audio"]),
        },
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "rejected_count": sum(1 for case in cases
                                  if case["status"] == "rejected"),
            "accepted_schema_controls": 1,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "runtime_invoked": False,
            "audio_read": False,
            "weights_loaded": False,
            "model_executed": False,
            "network_used": False,
        },
    }


# --------------------------------------------------------------------------
# Contract and report
# --------------------------------------------------------------------------
def build_contract() -> dict:
    row = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = linked_rows()
    qualification = {
        "status": "not_qualified",
        "readiness": "incomplete",
        "not_qualified": True,
        "real_result_present": False,
        "source_present": True,
        "source_licensed": False,
        "weights_present": False,
        "backbone_present": False,
        "runtime_present": False,
        "frame_labels_present": False,
        "accuracy_result": False,
        "detection_quality_result": False,
        "onset_delay_result": False,
        "device_timing_result": False,
        "rate_profile_result": False,
        "listening_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "all_release_gates_blocked": True,
    }
    gates = [dict(gate, qualifies=False, linked_row=row)
             for gate in RELEASE_GATES]
    return {
        "schema_id": CONTRACT_ID,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification": qualification,
        "qualification_status": "not_qualified",
        "disposition": DISPOSITION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "scope": {
            "write_scope": WRITE_SCOPE,
            "task_local_only": True,
            "provider_registered": False,
            "adapter_implemented": False,
            "public_abi_changed": False,
            "registry_or_default_changed": False,
            "shared_build_or_ci_changed": False,
            "real_assets_used": False,
            "network_used": False,
            "listening_performed": False,
            "device_timing_measured": False,
            "benchmark_run": False,
            "release_claim": False,
        },
        "boundary": {
            "linked_row_identity_only": True,
            "board_file_pinned": False,
            "mutable_board_fields_gate": False,
            "projected_fields": list(BOARD_ROW_FIELDS),
            "linked_row": row,
            "linked_row_sha256": board_row_digest(row),
            "linked_rows_sha256": linked_rows_digest(rows),
            "linked_rows": rows,
        },
        "public_v0_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_format": "float32",
            "frame_samples": 160,
            "changed": False,
        },
        "exact_source": {
            "repo_id": UPSTREAM_REPO,
            "commit": UPSTREAM_COMMIT,
            "license": UPSTREAM_LICENSE,
            "license_status": UPSTREAM_LICENSE_STATUS,
            "license_file_present": False,
            "license_declared_in_readme": False,
            "terms_reviewed": False,
            "repository_present": True,
            "downloaded": False,
        },
        "exact_model": {
            "checkpoint": {
                "file": CHECKPOINT_FILE,
                "preserved_name": CHECKPOINT_PRESERVED_NAME,
                "drive_id": CHECKPOINT_DRIVE_ID,
                "byte_count": str(CHECKPOINT_BYTES),
                "sha256": CHECKPOINT_SHA256,
                "locally_present": False,
                "terms_reviewed": False,
                "downloaded_or_reconstructed": False,
            },
            "backbone": {
                "repo_id": BACKBONE_REPO,
                "smoke_config_repo_id": SMOKE_CONFIG_REPO,
                "smoke_config_revision": SMOKE_CONFIG_REVISION,
                "smoke_config_bytes": str(SMOKE_CONFIG_BYTES),
                "smoke_config_sha256": SMOKE_CONFIG_SHA256,
                "smoke_config_license": SMOKE_CONFIG_LICENSE,
                "smoke_config_license_status": "not_declared",
                "config_present": False,
                "weights_present": False,
            },
            "architecture": {
                "module": "models.AcousticModel",
                "backbone_class": "WavLMModel",
                "head": "torch.nn.Linear(768,5)",
                "label_count": len(LABELS),
                "activation": "sigmoid",
                "threshold": "0.5",
                "frame_interval_ms": FRAME_INTERVAL_MS,
                "frame_rate_hz": FRAME_RATE_HZ,
                "frame_count_for_4s": FRAME_COUNT,
            },
            "labels": list(LABELS),
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "sample": SAMPLE_ID,
            "duration_s": DURATION_S,
            "positive_frames_per_label": dict(POSITIVE_FRAMES),
            "state_keys_loaded": "all",
            "missing_keys": 0,
            "unexpected_keys": 0,
            "locally_present": False,
            "downloaded_or_reconstructed": False,
        },
        "historical_smoke": {
            "recorded_only": True,
            "executed_here": False,
            "network_used": False,
            "source_path": (
                "research/tsm-followup-20261101/agent-neural/run/"
                "disfluency_acoustic_smoke.json"),
        },
        "required_artifacts": [dict(row) for row in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(row) for row in EXACT_BLOCKERS],
        "release_gates": gates,
        "rate_profile_requirements": [dict(row) for row in RATE_PROFILE_ROWS],
        "quality_outcomes": [dict(row) for row in QUALITY_ROWS],
        "timing_requirements": [dict(row) for row in TIMING_ROWS],
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "fields": list(MANIFEST_FIELDS),
            "source_fields": list(SOURCE_FIELDS),
            "weights_fields": list(WEIGHTS_FIELDS),
            "backbone_fields": list(BACKBONE_FIELDS),
            "runtime_fields": list(RUNTIME_FIELDS),
            "feature_fields": list(FEATURE_FIELDS),
            "label_fields": list(LABEL_FIELDS),
            "audio_fields": list(AUDIO_FIELDS),
            "control_fields": list(CONTROL_FIELDS),
            "outcome_fields": list(OUTCOME_FIELDS),
            "per_label_fields": list(PER_LABEL_FIELDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "labels_required": list(LABELS),
            "exact_repo_id_required": UPSTREAM_REPO,
            "exact_commit_required": UPSTREAM_COMMIT,
            "exact_weight_sha256_required": CHECKPOINT_SHA256,
            "exact_weight_bytes_required": str(CHECKPOINT_BYTES),
            "window_seconds_required": DURATION_S,
            "sample_rate_hz_required": SAMPLE_RATE_HZ,
            "frame_ms_required": FRAME_INTERVAL_MS,
            "runtime_required": {
                "python": RUNTIME_PYTHON,
                "torch": RUNTIME_TORCH,
                "transformers": RUNTIME_TRANSFORMERS,
                "device": "cpu",
                "offline": True,
            },
            "admission_only": True,
            "qualifies": False,
        },
        "non_claims": list(NON_CLAIMS),
        "required_results": list(REQUIRED_RESULTS),
        "licensing": {
            "package_license": "Apache-2.0",
            "vendored_third_party_bytes": False,
            "upstream_license_reviewed": False,
            "weight_terms_reviewed": False,
            "corpus_terms_reviewed": False,
            "annotation_terms_reviewed": False,
        },
    }


def build_report() -> dict:
    contract = build_contract()
    pins = {
        "source": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary": pin_rows(BOUNDARY_PINS, WORKTREE),
    }
    workspace_probes = absence_probes(AUDIO_ROOT)
    home_probes = home_absence_probes()
    smoke = documented_smoke()
    presence = source_presence()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "profile": PROFILE,
        "profile_key": PROFILE,
        "mode": MODE,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "qualification": contract["qualification"],
        "disposition": DISPOSITION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "contract_sha256": object_digest(contract),
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "exact_source": contract["exact_source"],
        "exact_model": contract["exact_model"],
        "historical_smoke": smoke,
        "smoke_runner_provenance": smoke_runner_provenance(),
        "source_inventory": source_inventory(),
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "rate_profile": {
            "profile": PROFILE,
            "label": PROFILE_LABEL,
            "rows": contract["rate_profile_requirements"],
            "blocked_rows": len(contract["rate_profile_requirements"]),
        },
        "quality_outcomes": {
            "rows": contract["quality_outcomes"],
            "blocked_rows": len(contract["quality_outcomes"]),
        },
        "timing": {
            "rows": contract["timing_requirements"],
            "blocked_rows": len(contract["timing_requirements"]),
        },
        "source_presence": presence,
        "absence_evidence": {
            "workspace_probes": workspace_probes,
            "home_probes": home_probes,
            "summary": absence_summary(workspace_probes, home_probes),
        },
        "admission": build_admission(),
        "source_pins": pins["source"],
        "boundary_pins": pins["boundary"],
        "linked_row_identity": {
            "projection": board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW),
            "sha256": board_row_digest(
                board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)),
            "linked_rows": linked_rows(),
            "linked_rows_sha256": linked_rows_digest(),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
        },
        "non_claims": contract["non_claims"],
        "required_results": contract["required_results"],
        "reproduction": {
            "regeneration": "run.py all (repeat=3, byte-identical)",
            "tests": "python3 -m unittest -v test_reference.py",
            "verifier": "python3 verify.py",
            "stdlib_only": True,
            "network_used": False,
        },
    }


def canonical_report(document: dict) -> tuple[str, str]:
    text = canonical_text(document)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema_id") != CONTRACT_ID:
        raise ValueError("contract_schema")
    if contract.get("task") != TASK:
        raise ValueError("contract_task")
    if contract.get("decision") != "DEFER":
        raise ValueError("contract_decision")
    if contract.get("status") != "incomplete":
        raise ValueError("contract_status")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification")
    gates = contract.get("release_gates", [])
    if len(gates) != 8:
        raise ValueError("contract_gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}":
            raise ValueError("contract_gate_id")
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            raise ValueError("contract_gate_not_blocked")
        if not gate.get("reopen_condition"):
            raise ValueError("contract_gate_reopen")
    artifacts = contract.get("required_artifacts", [])
    if len(artifacts) != len(REQUIRED_ARTIFACTS):
        raise ValueError("contract_artifact_count")
    if artifacts[0].get("id") != "ART-01" \
            or artifacts[0].get("present") is not True \
            or artifacts[0].get("blocked") is not False:
        raise ValueError("contract_provenance_artifact")
    if artifacts[1].get("id") != "ART-02" \
            or artifacts[1].get("present") is not True \
            or artifacts[1].get("blocked") is not True:
        raise ValueError("contract_unlicensed_source_artifact")
    for row in artifacts[2:]:
        if row.get("present") is not False or row.get("blocked") is not True:
            raise ValueError("contract_artifact_not_blocked")
    source = contract.get("exact_source", {})
    if source.get("license_status") != "not_declared" \
            or source.get("license_file_present") is not False:
        raise ValueError("contract_source_license")
    model = contract.get("exact_model", {})
    checkpoint = model.get("checkpoint", {})
    if checkpoint.get("locally_present") is not False \
            or checkpoint.get("sha256") != CHECKPOINT_SHA256 \
            or checkpoint.get("byte_count") != str(CHECKPOINT_BYTES):
        raise ValueError("contract_checkpoint")
    blockers = contract.get("exact_blockers", [])
    if len(blockers) != len(EXACT_BLOCKERS):
        raise ValueError("contract_blocker_count")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            raise ValueError("contract_blocker_not_open")
    for section, expected in (
            ("rate_profile_requirements", RATE_PROFILE_ROWS),
            ("quality_outcomes", QUALITY_ROWS),
            ("timing_requirements", TIMING_ROWS)):
        rows = contract.get(section, [])
        if len(rows) != len(expected):
            raise ValueError("contract_section_count:" + section)
        for row in rows:
            if row.get("status") != "blocked":
                raise ValueError("contract_section_not_blocked:" + section)
    qualification = contract.get("qualification", {})
    if qualification.get("not_qualified") is not True \
            or qualification.get("missing_result_promoted") is not False \
            or qualification.get("release_claim") is not False:
        raise ValueError("contract_qualification_flags")
    if qualification.get("all_release_gates_blocked") is not True:
        raise ValueError("contract_gate_flag")
    if qualification.get("source_licensed") is not False:
        raise ValueError("contract_source_licensed")

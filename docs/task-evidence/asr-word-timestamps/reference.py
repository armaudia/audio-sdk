# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-ASR-WORD-TIMESTAMPS.

Standard-library only and deterministic. This module contains no ASR engine,
model weight, tokenizer, inference path, audio signal, transcript, word span,
runtime import or model result. It records the exact research inputs, pins the
unlicensed model/runtime bytes that happen to exist in a mutable scratch tree,
defines a fail-closed admission boundary for a future word-timestamp run,
implements the exact word-count-to-speech-rate arithmetic used by that boundary,
and builds the canonical contract/report.

The evidence source calls ASR word timestamps ("words/min") the most robust
speech-rate proxy when an ASR path already exists. It does not name a licensed
engine, weight or runtime. Vosk small-en-us-0.15 and the sherpa-onnx Whisper
tiny.en scorer are present as unlicensed scratch bytes; neither is reviewed,
qualified or executed here. Every result remains blocked.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from typing import Any

TASK = "SDK-ASR-WORD-TIMESTAMPS"
COMPONENT_ID = "asr-word-timestamps"
TASK_TITLE = "ASR word timestamps"
CONTRACT_ID = "audio-sdk/asr-word-timestamps-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/asr-word-timestamps-cohort/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "feasibility"
BASE_COMMIT = "f245d81f86b556dca4bcdb1b7afb2ea898065ed7"
BRANCH = "swarm/SDK-ASR-WORD-TIMESTAMPS"
WRITE_SCOPE = "docs/task-evidence/asr-word-timestamps/ only"
TASK_PREFIX = "docs/task-evidence/asr-word-timestamps/"
DISPOSITION = (
    "ASR word-timestamp speech-rate proxy feasibility blocker; no ASR engine, "
    "adapter, licensed weight, runtime or result.")

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                  "SDK-FND-PROVIDER")

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
MAX_MANIFEST_WORDS = 100000
MAX_MANIFEST_CONTROLS = 16
MAX_MANIFEST_PACKAGES = 64
MAX_DURATION_S = Decimal("3600")
HASH_HEX = re.compile(r"^[0-9a-f]{64}$")
REVISION_HEX = re.compile(r"^[0-9a-f]{40}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
VERSION = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}$")
CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
ABSOLUTE = re.compile(r"[\\/]")

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
        board = candidate / BOARD_TASK_ROW
        if board.is_file() and (candidate / "cpp-library").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

# Immutable read-only inputs. `source:` rows are workspace-relative; boundary
# and sibling rows are SDK-worktree relative. The mutable shared board is
# deliberately excluded from the pin set; only its stable row identity gates.
SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "cpp-library/pipeline-validation/playback-speed/README.md":
        "a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f",
    "cpp-library/pipeline-validation/playback-speed/run_validation.py":
        "d9b7eacf76cfbcb623e79eda3a0577ceb4b0284d1a388e0fa0c29fd2f23b2814",
    "cpp-library/pipeline-validation/playback-speed/generate_corpus.py":
        "05442e1be54d7a408eac55c62ac6eb48fdee3f76543602228bf6ec61a0e96a27",
    "cpp-library/pipeline-validation/playback-speed/audio/corpus.json":
        "7e3533b2256b1904cae4020a3b5c75e2814c1e2057ec99cd5cc9fbd40fa74fd1",
    "cpp-library/pipeline-validation/playback-speed/results/results.json":
        "69b5bcc4dc3740bacc182e93419b6a83d5c3eebba7d9b4dfdd8fe4b09813cfc1",
    "cpp-library/pipeline-validation/playback-speed/results/report.md":
        "9c9383297b1160dbe4f7261f789b493d70354b11930f4d8527b20b0ca8c87c34",
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
}

SIBLING_PINS = {
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/README.md":
        "1ccece1085e1d6e821891feffb0c19fc494227bfd5e8a656657ffd7081cf959c",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/contract.json":
        "ee23e6cc21f9f3293a48dab7008a4c41f129074cafa3eb6b273f2f3ef413d694",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json":
        "57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2",
    "docs/task-evidence/whisper-tiny-en-mfa/README.md":
        "7c24422f782bf934d22e2a752e2be2ead2d184cfd8728452c7f7a5dd68f25c7f",
    "docs/task-evidence/whisper-tiny-en-mfa/contract.json":
        "fddc819bdcbb34a4d47f605efa8c0632573eaa2b77d0681d2a82f5c58e98687e",
    "docs/task-evidence/whisper-tiny-en-mfa/report.json":
        "6b9cc69ea2be5cd5cad9509021b7b5e7fb972a4c32c62721f07be995b582710c",
    "docs/task-evidence/wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge/README.md":
        "870a665c5da0f75dea01de767388cd40fdd45a0cd5d55f07fa1010861e9dd371",
    "docs/task-evidence/wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge/contract.json":
        "f4429f3afde1096d29068f51ddace56c591a290d793097a671a125f4ff7a9a68",
    "docs/task-evidence/wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge/report.json":
        "1ce7faa0b87faa8a8782083bd23ba6dd5803f9bd45ae5ef2db9a8692b0858f48",
    "docs/task-evidence/3d-microphone-spatial-time-alignment/README.md":
        "514636b719e6579651bf941a6ac3cb93740cc9a40e3f2b4bcd39c2ddea610264",
    "docs/task-evidence/3d-microphone-spatial-time-alignment/contract.json":
        "c7b0f4ac8191abe114b4f77ae17c803ffbda1fe4012e12d42808ca798d0afb88",
    "docs/task-evidence/3d-microphone-spatial-time-alignment/report.json":
        "5d3623c835a1b19d79867a64ba1b6dff18e8593918a8173cff91550c1c532f03",
}

# Present-but-unlicensed scratch bytes. These paths are outside the SDK and
# are never imported, loaded or executed. A tree digest is SHA-256 over sorted
# "relative\0file_sha256\0byte_count\n" rows.
SCRATCH_ROOT = "cpp-library/pipeline-validation/playback-speed"

VOSK_MODEL = {
    "relative": SCRATCH_ROOT + "/models/vosk-model-small-en-us-0.15",
    "file_count": 14,
    "byte_count": 70898967,
    "tree_sha256":
        "8d6008c80499a5724a91d53ec99e6df0c41064df4443e063af79d9e247bb14bb",
    "files": {
        "README": "c0cf286e4f7783306c5f6469b37db69228fb16803b03cae661edb2d7bba64ebb",
        "am/final.mdl": "75370a0137f9daf8f469dedd7daa4513ae7a621f03240c6e512e2b50b656a7b6",
        "conf/mfcc.conf": "1e2228006d01d805ad1c267fee9f79709ca87ac51bd82b0e3f5c69ba543f0fc4",
        "conf/model.conf": "8f14cb1eeb07c762c371db648c6be688d347236155ca0f64fb13b6567a8ce81f",
        "graph/Gr.fst": "023c8b7e30704a9e37765c635c252e608a02f361235bf94abdcf2a5225d85b20",
        "graph/HCLr.fst": "5caafba3081e1646545ac6bff0dd7a318e53dcbdc86f237909ce1d2ac1293d34",
        "graph/disambig_tid.int": "9ad87cc166d0998f08f758f47a6223a120dfffcbee805c4849c3aa5e6bb3c0fc",
        "graph/phones/word_boundary.int": "da199d9c991e0e84681ddbb34627b915b26302d50a8fdaa23c51e2bc3a50b5c3",
        "ivector/final.dubm": "8c5d7dd69d2122313baaf19f61f35dd3fa18b70c62ac0687e311e1c46e6daca7",
        "ivector/final.ie": "3f37faf90c375b9e4740b569398b5829ed9cc07d19be6d441f72c3b71d7efcc6",
        "ivector/final.mat": "ddd83586dc5f928cda8738b922c85ffe38fc789cb5f9151a712ca12f37265382",
        "ivector/global_cmvn.stats": "33be09afcc80059847a275c3d043b51f1ab954c7c2438ddbbf4745e8ba144ff9",
        "ivector/online_cmvn.conf": "a2f3571754b64297cb7efb2e7ca3df61995c5a45fcbb97188f90613552bb2dfe",
        "ivector/splice.conf": "9f0c5f7c82d18eaf25d8bce470efa9f7741f88411fe428774bc0a9bb69a24756",
    },
}

SHERPA_MODEL = {
    "relative": SCRATCH_ROOT + "/models/sherpa-onnx-whisper-tiny.en",
    "file_count": 9,
    "byte_count": 256603197,
    "tree_sha256":
        "fae72e5493c2c9d09e1f2725332ba278952ba2489923fe695e040ecd6ee08da5",
    "files": {
        "test_wavs/0.wav": "6bc58a4efdf20daac252b6b1502632601a71efe0308f6757dc1eda34891a7e4f",
        "test_wavs/1.wav": "5143a6ba93c4b274e2c4ac22deb75c2c48936c853f0519add1de828b6c79cc5a",
        "test_wavs/8k.wav": "f6f3c8b33e2534cdc154fe773ad2750f1f6a2ca5096179cdf037ae782456613e",
        "test_wavs/trans.txt": "b9ac44e7b794abb1a2d5faf0005e98a665971e7ac2ed15435832cc34edaa9100",
        "tiny.en-decoder.int8.onnx": "06c0e6ff6348d427e51839219d1c886c18cfdf411e629e33f5e1679bff9c1527",
        "tiny.en-decoder.onnx": "54d5a5fd2a757175aeb70a837a8404fc9c31b659610724694f5a0e2c51715f94",
        "tiny.en-encoder.int8.onnx": "0ce578b827c94a961aacb8fa14b02f096504b337e5c94be37c36238cbe3e8bc6",
        "tiny.en-encoder.onnx": "dc7de696432d97a3d64387800b230ac69d18e5e4efea0eec0613209dd8b7b0c9",
        "tiny.en-tokens.txt": "306cd27f03c1a714eca7108e03d66b7dc042abe8c258b44c199a7ed9838dd930",
    },
}

RUNTIME_FILES = {
    ".venv/lib/python3.11/site-packages/vosk/__init__.py":
        "3e29f285cdeec3793ab3c566e9205db1bc26ef75f1bd8b9781728f90841f96d7",
    ".venv/lib/python3.11/site-packages/vosk/vosk_cffi.py":
        "94180ec83bd96eee4ef8835ef3fea6d2a955ff1dc8bdb69d5b398727007e6478",
    ".venv/lib/python3.11/site-packages/vosk/libvosk.dyld":
        "82fdfba0dde392a7dbba70f9c1a17f6e3da27a50444a9f53939508525a1e6fdf",
    ".venv/lib/python3.11/site-packages/vosk-0.3.44.dist-info/METADATA":
        "ea20f0c3c548e68d9b08ccc2a9aa5fef42754915a70d5e67098e2dcd6bec4746",
    ".venv/lib/python3.11/site-packages/sherpa_onnx/__init__.py":
        "f99e43cc249dbfef58acaa02348892984e4c7dfa07923d9144bec5b51639d8ef",
    ".venv/lib/python3.11/site-packages/sherpa_onnx_core-2.0.1.dist-info/METADATA":
        "f1af234dcfeca76f7ab4e16bdc903311e76069419b8b67c1806a7bf149d8945d",
    ".venv/lib/python3.11/site-packages/faster_whisper-1.2.1.dist-info/METADATA":
        "b85622132a43897972924db98e024c0d40dcec19c577b1ee5640f1bc1b59aada",
    ".venv/lib/python3.11/site-packages/ctranslate2-4.8.5.dist-info/METADATA":
        "0e14d8a651496ed06c1277a530c134e8d84f9f16750dbb5c77ab85da46d90606",
    ".venv/lib/python3.11/site-packages/onnxruntime-1.31.1.dist-info/METADATA":
        "82f146c3aad08fd55eadf57e410022535697a858bd6bf760320b2328301d41cf",
}

RECORDED_WORD_SPANS = (
    {"clip": "tts_lecture_fast", "word_count": 121,
     "gate_wall_s": "2.3259067499893717",
     "gate_cpu_s": "2.3226299999999998",
     "gate_rtf_wall": "0.06749021229335544"},
    {"clip": "tts_lecture_fillers", "word_count": 122,
     "gate_wall_s": "2.442162499995902",
     "gate_cpu_s": "2.441951000000003",
     "gate_rtf_wall": "0.05239694156951658"},
    {"clip": "ami_stitched", "word_count": 86,
     "gate_wall_s": "2.2006125830230303",
     "gate_cpu_s": "2.2005350000000305",
     "gate_rtf_wall": "0.05613807609752628"},
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "research_report_scripts_and_recorded_spans",
        "requirement": (
            "The exact research report, playback-speed README, validation and "
            "corpus scripts, corpus labels, recorded Vosk word spans and "
            "results, pinned by whole-file SHA-256."),
        "present": True,
        "verified": True,
        "blocked": False,
        "sha256": None,
        "revision": None,
    },
    {
        "id": "ART-02",
        "kind": "asr_source_revision_and_license",
        "requirement": (
            "Exact 40-hex source revisions and complete license/notice/"
            "attribution sets for the selected ASR engine (Vosk/Kaldi or "
            "sherpa-onnx/Whisper plus onnxruntime/CTranslate2), including "
            "bundled third-party notices."),
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
    },
    {
        "id": "ART-03",
        "kind": "model_weights_tokenizer_and_rights",
        "requirement": (
            "Official model archives and tokenizer with archive byte counts and "
            "digests, a model card, license/notice text, attribution, "
            "commercial/output-use terms and an independent rights review."),
        "present": True,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
    },
    {
        "id": "ART-04",
        "kind": "pinned_offline_runtime",
        "requirement": (
            "Locked offline environments with exact wheel/sdist/conda hashes, "
            "archives, install/import digests, deterministic thread settings "
            "and a clean-room offline load trace."),
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_audio_and_independent_word_reference",
        "requirement": (
            "Rights-cleared/consented speech audio plus adjudicated human word, "
            "filler and pause spans from at least two independent annotators, "
            "with agreement, transcript, meeting/channel mapping and reviewed "
            "output-use terms."),
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
    },
    {
        "id": "ART-06",
        "kind": "reproduced_word_timestamp_and_rate_results",
        "requirement": (
            "A fresh offline word-timestamp extraction and scoring run with "
            "frozen scorer, exact matched-word accounting, finite checks, "
            "uniform-timing and no-alignment baselines and adverse/missing "
            "controls."),
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
    },
    {
        "id": "ART-07",
        "kind": "provider_tool_intake",
        "requirement": (
            "A separate versioned OFF-by-default SDK provider/tool intake with "
            "exact descriptor/config, empty default settings, no registry/"
            "default/shared-build change and independent exact-head review."),
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "linked_gates": ["RG-01"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No ASR source tree is staged at an exact 40-hex revision. The "
            "Vosk model README only states 'Copyright 2020 Alpha Cephei Inc'; "
            "the installed vosk 0.3.44 dist-info has no LICENSE and METADATA "
            "says 'License: UNKNOWN'. The sherpa-onnx 2.0.1 METADATA says "
            "Apache-2.0 but no upstream source revision or complete notice "
            "bundle is staged. A classifier or metadata string is not a grant."),
        "required_action": (
            "Pin the exact Vosk/Kaldi or sherpa-onnx/Whisper source revisions, "
            "stage the complete license, notice and attribution texts for the "
            "engine and bundled third parties, and record an independent "
            "license review."),
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "linked_gates": ["RG-02"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "Model bytes are present but not licensed for this use. The Vosk "
            "tree has 14 files and no LICENSE, NOTICE or model card. The "
            "sherpa-onnx Whisper tiny.en tree has 9 files (including test "
            "wavs) and no LICENSE, README or model card. Neither has an "
            "official archive digest, source revision, commercial/output-use "
            "decision or reviewed attribution."),
        "required_action": (
            "Supply the official model archives and tokenizer with byte counts "
            "and verified SHA-256, model cards, license/notice text, "
            "attribution and a written output-use and redistribution decision."),
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "linked_gates": ["RG-03"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "The runtime is a mutable, git-ignored .venv. There is no lockfile, "
            "wheel/sdist archive, install digest, deterministic thread policy "
            "or offline-load trace. No model or runtime was imported or "
            "executed here, so no load or inference result exists."),
        "required_action": (
            "Provide locked offline environments with exact package/wheel "
            "hashes, archives, install and import digests, deterministic "
            "threads and a clean-room offline load trace."),
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "linked_gates": ["RG-04"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No rights-cleared audio with an independent word timing reference "
            "is staged. The two TTS clips carry construction-time labels from "
            "one synthetic voice; the AMI stitch has no transcript. There is "
            "no second annotator, adjudication, agreement statistic or "
            "reviewed AMI/CC BY 4.0 output-use decision. TTS labels are not an "
            "independent gold reference."),
        "required_action": (
            "Freeze a consented/rights-cleared cohort with adjudicated human "
            "word, filler and pause spans from at least two independent "
            "annotators, agreement, transcript and a reviewed output-use "
            "decision."),
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "linked_gates": ["RG-05", "RG-06"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No word-timestamp or speech-rate result was reproduced. Recorded "
            "Vosk spans (121, 122 and 86 words) and batch gate times are "
            "provenance only. The study reports no words/min, boundary error, "
            "matched-word accounting, finite-output scan, uniform-timing "
            "baseline or timestamp-tied pause/filler preservation result."),
        "required_action": (
            "Reproduce offline extraction and scoring with a frozen scorer, "
            "exact word/token accounting, finite checks, uniform-timing and "
            "no-alignment baselines, adverse/missing controls and a "
            "timestamp-tied pause/filler policy."),
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "linked_gates": ["RG-07", "RG-08"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No provider, tool, adapter or intake exists. There is no target-"
            "device streaming measurement, callback deadline, first-output or "
            "dropped/stale-event result, no OFF-by-default surface and no "
            "release review. The recorded batch gate wall time is not a "
            "device-timing result."),
        "required_action": (
            "After model/data/runtime/quality gates clear, measure the exact "
            "paced workload, open a separate versioned OFF-by-default intake "
            "and obtain independent exact-head review."),
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_and_license_provenance",
        "statement": (
            "Only research inputs are pinned. No ASR source revision is staged "
            "and no complete license/notice/attribution bundle is reviewed for "
            "Vosk/Kaldi, sherpa-onnx/Whisper or their bundled dependencies."),
        "reopen_condition": (
            "Pin exact source revisions and stage complete license, notice and "
            "attribution sets with an independent review."),
        "status": "blocked",
    },
    {
        "id": "RG-02",
        "title": "weights_tokenizer_and_digests",
        "statement": (
            "Present model bytes are pinned by file and tree SHA-256, but the "
            "official archive digests, model cards, license text, attribution "
            "and output-use decision are absent."),
        "reopen_condition": (
            "Supply official archives/tokenizer with verified byte counts and "
            "digests, model cards and reviewed rights."),
        "status": "blocked",
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_and_offline_load",
        "statement": (
            "No locked offline runtime, package archives, import digests, "
            "deterministic thread policy or clean-room model load exists."),
        "reopen_condition": (
            "Provide locked offline environments and a clean-room offline load "
            "trace with exact package/import digests."),
        "status": "blocked",
    },
    {
        "id": "RG-04",
        "title": "rights_cleared_audio_and_independent_word_reference",
        "statement": (
            "No rights-cleared cohort with adjudicated multi-annotator word/"
            "filler/pause spans and transcript exists; TTS construction labels "
            "and unlabeled AMI audio do not satisfy this gate."),
        "reopen_condition": (
            "Stage the rights-cleared cohort, independent human reference, "
            "agreement statistics and output-use review."),
        "status": "blocked",
    },
    {
        "id": "RG-05",
        "title": "word_timestamp_and_rate_accuracy_with_controls",
        "statement": (
            "No reproduced boundary error, matched-word accounting, words/min "
            "rate estimate, finite/adverse scan or matched control baseline "
            "exists."),
        "reopen_condition": (
            "Reproduce extraction and scoring with frozen scorers, exact "
            "accounting, finite checks and uniform/no-alignment baselines."),
        "status": "blocked",
    },
    {
        "id": "RG-06",
        "title": "rate_profile_and_timestamp_tied_policy",
        "statement": (
            "The Rate profile is not exercised: no source/output mapping, "
            "duration, pitch/transient, buffering, rate change, unfamiliar "
            "speech/music/silence, rebuffer/drift, final partial window or "
            "timestamp-tied pause/filler preservation result exists."),
        "reopen_condition": (
            "Exercise the Rate profile on a composite path or record a reviewed "
            "waiver, and define a timestamp-tied pause/filler policy with a "
            "preservation metric."),
        "status": "blocked",
    },
    {
        "id": "RG-07",
        "title": "target_runtime_timing_resources_and_deadlines",
        "statement": (
            "No target-device streaming latency, first-output, callback "
            "deadline, resource, thermal/energy or dropped/stale-event "
            "measurement exists; recorded batch times are context only."),
        "reopen_condition": (
            "Measure the installed candidate under paced workload with p50/p95/"
            "p99 latency, resources, deadlines and availability."),
        "status": "blocked",
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "statement": (
            "No provider/tool intake or public-surface decision exists. The "
            "installed v0 geometry, registry, default, shared build and CI are "
            "untouched."),
        "reopen_condition": (
            "Open a separate versioned OFF-by-default opt-in intake with exact "
            "descriptor/config, clean-install proof and exact-head review."),
        "status": "blocked",
    },
)

RATE_PROFILE_ROWS = (
    {"id": "RATE-01", "requirement": "Measure source/output mapping and duration.",
     "status": "blocked",
     "evidence": "No rendered audio or source/output mapping exists."},
    {"id": "RATE-02", "requirement": "Measure pitch and transient audibility.",
     "status": "blocked",
     "evidence": "No waveform, F0 or transient metric exists."},
    {"id": "RATE-03", "requirement": "Measure playback buffering.",
     "status": "blocked",
     "evidence": "No playback chain, queue or fill/flush measurement exists."},
    {"id": "RATE-04", "requirement": "Include 1x and rate changes.",
     "status": "blocked",
     "evidence": "Word timestamps are a rate proxy, not a stretcher."},
    {"id": "RATE-05", "requirement": "Include unfamiliar speech, music and silence.",
     "status": "blocked",
     "evidence": "Only two synthetic TTS clips and one unlabeled AMI stitch exist."},
    {"id": "RATE-06",
     "requirement": "Include rebuffer, drift and the final partial window.",
     "status": "blocked",
     "evidence": "No stream, rebuffer, drift or partial-window measurement exists."},
    {"id": "RATE-07",
     "requirement": ("Keep pause or filler decisions tied to source timestamps "
                     "and measure speech preservation."),
     "status": "blocked",
     "evidence": "No controller, source-timestamp policy or preservation metric exists."},
    {"id": "RATE-08", "requirement": "Map output to a reviewed preferred-speed policy.",
     "status": "blocked",
     "evidence": "Words/min alone is not a preferred-speed or acceptability policy."},
)

QUALITY_ROWS = (
    {"id": "QUAL-01", "outcome": "word_boundary_error",
     "status": "blocked", "value": None,
     "evidence": "No reproduced boundary MAE, median or within-50 ms result."},
    {"id": "QUAL-02", "outcome": "word_filler_pause_segmentation",
     "status": "blocked", "value": None,
     "evidence": "No human reference or segmentation IoU/F1 result."},
    {"id": "QUAL-03", "outcome": "transcript_word_error_rate",
     "status": "blocked", "value": None,
     "evidence": "Recorded study WER is provenance only and has no local run."},
    {"id": "QUAL-04", "outcome": "words_per_minute_rate_accuracy",
     "status": "blocked", "value": None,
     "evidence": "The study reports no words/min; only a synthetic arithmetic control exists."},
    {"id": "QUAL-05", "outcome": "matched_word_finite_and_control_accounting",
     "status": "blocked", "value": None,
     "evidence": "No matched-word accounting, finite scan or matched baseline exists."},
)

TIMING_ROWS = (
    {"id": "TIME-01", "metric": "model_load_and_word_extraction_latency",
     "status": "blocked", "value": None,
     "evidence": "No local model load or extraction was performed."},
    {"id": "TIME-02", "metric": "streaming_first_output_and_availability",
     "status": "blocked", "value": None,
     "evidence": "The recorded gate ran one batch call; no streaming timing exists."},
    {"id": "TIME-03", "metric": "device_deadline_callback_and_stale_events",
     "status": "blocked", "value": None,
     "evidence": "No device, callback or dropped/stale-event measurement exists."},
    {"id": "TIME-04", "metric": "cpu_memory_energy",
     "status": "blocked", "value": None,
     "evidence": "No CPU, memory, thermal or energy measurement exists."},
)

NON_CLAIMS = (
    "No ASR engine, model weight, tokenizer or runtime is imported, loaded or executed.",
    "No audio, transcript, word span or annotation is read as a signal or scored.",
    "No word timestamp, words/min, boundary, WER or finite-output result is reproduced.",
    "No provider, registry, descriptor, public ABI, shared build or CI change exists.",
    "No listening, device timing, benchmark, pipeline or release claim is made.",
    "Recorded Vosk word counts and batch times are provenance, not evidence.",
    "The synthetic arithmetic control can never qualify a candidate.",
)

REQUIRED_RESULTS = (
    "Exact ASR source revisions with complete license/notice/attribution bundles.",
    "Official model/tokenizer archives with verified byte counts and SHA-256.",
    "Reviewed model cards and commercial/output-use decisions.",
    "Locked offline runtimes with package and import digests.",
    "Rights-cleared audio with adjudicated multi-annotator word/pause spans.",
    "Reproduced word timestamps, boundary errors and words/min with matched-word accounting.",
    "Uniform-timing and no-alignment baselines plus adverse/missing controls.",
    "Rate-profile coverage or a reviewed waiver and a timestamp-tied pause/filler policy.",
    "Target-device streaming timing, resources and deadlines.",
    "Separate OFF-by-default provider/tool intake and independent exact-head review.",
)

MANIFEST_FIELDS = ("schema_id", "run_id", "asr", "runtime", "audio",
                   "reference", "hypothesis", "controls", "outcomes", "rights")
ASR_FIELDS = ("engine", "version", "source_revision", "model_id",
              "model_tree_sha256", "tokenizer_sha256", "weight_byte_count",
              "license_id", "terms_accepted")
RUNTIME_FIELDS = ("python", "packages", "device", "intra_op_threads",
                  "inter_op_threads", "deterministic", "offline")
PACKAGE_FIELDS = ("name", "version", "sha256")
AUDIO_FIELDS = ("id", "path", "sha256", "sample_rate_hz", "channels",
                "samples", "duration_s")
REFERENCE_FIELDS = ("kind", "path", "sha256", "word_count",
                    "annotator_count", "independent_of_asr")
HYPOTHESIS_FIELDS = ("words", "word_count")
WORD_FIELDS = ("text", "start_s", "end_s")
CONTROL_FIELDS = ("id", "kind")
OUTCOME_FIELDS = ("wer", "boundary_mae_ms", "boundary_median_abs_error_ms",
                  "boundary_within_50ms_fraction", "words_per_minute_total",
                  "words_per_minute_speech", "pause_ratio", "matched_words",
                  "reference_words", "nonfinite_count", "sample_count")
RIGHTS_FIELDS = ("audio_terms_reference", "model_terms_reference",
                 "output_use_reference", "review_reference",
                 "claims_qualified")
WORD_FIELDS_ORDER = WORD_FIELDS
CONTROL_KINDS = ("uniform_timing_baseline", "no_alignment_baseline",
                 "oracle_reference", "adverse_silence",
                 "adverse_missing_words", "nonfinite_rejection")
REFERENCE_KINDS = ("human_verified", "adjudicated_human",
                   "construction_label", "forced_alignment")
ADMISSION_REFERENCE_KINDS = ("human_verified", "adjudicated_human")
DEVICES = ("cpu", "gpu", "npu")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_digest(root: Path) -> tuple[str, int, int]:
    """Return (tree_sha256, file_count, byte_count) for a directory tree."""
    rows: list[tuple[str, str, int]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        rows.append((relative, sha256_file(path), path.stat().st_size))
    digest = hashlib.sha256()
    for relative, file_sha, size in rows:
        digest.update(
            (relative + "\0" + file_sha + "\0" + str(size) + "\n").encode())
    return digest.hexdigest(), len(rows), sum(size for _, _, size in rows)


def canonical_text(document: dict) -> str:
    text = json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return text + "\n"


def canonical_bytes(document: dict) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: dict) -> str:
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def _no_floats(value: Any, path: str = "document") -> None:
    if isinstance(value, float):
        raise ValueError("float:" + path)
    if isinstance(value, dict):
        for key, item in value.items():
            _no_floats(item, path + "." + str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _no_floats(item, path + f"[{index}]")


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise ValueError("nonfinite_json:" + token)


def read_strict_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    value = json.loads(text, object_pairs_hook=_strict_pairs,
                       parse_constant=_reject_constant)
    if not isinstance(value, dict):
        raise ValueError("json_not_object")
    return value


def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for relative, expected in sorted(pins.items()):
        actual = sha256_file(root / relative)
        if actual != expected:
            raise ValueError("pin_mismatch:" + relative)
        rows[relative] = {"sha256": expected, "actual": actual,
                          "verified": True}
    return rows


def board_row_projection(board_path: Path, task: str = TASK) -> dict:
    document = read_strict_json(board_path)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    matches = [row for row in tasks if isinstance(row, dict)
               and row.get("id") == task]
    if len(matches) != 1:
        raise ValueError("board_row_count:" + task)
    row = matches[0]
    return {field: copy.deepcopy(row.get(field)) for field in BOARD_ROW_FIELDS}


def board_row_digest(row: dict) -> str:
    return hashlib.sha256(canonical_bytes(row)).hexdigest()


def linked_rows() -> list[dict]:
    document = read_strict_json(AUDIO_ROOT / BOARD_TASK_ROW)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    index = {row.get("id"): row for row in tasks if isinstance(row, dict)}
    rows = []
    for task_id in LINKED_ROW_IDS:
        row = index.get(task_id)
        if row is None:
            raise ValueError("linked_row_missing:" + task_id)
        rows.append({field: copy.deepcopy(row.get(field))
                     for field in BOARD_ROW_FIELDS})
    return rows


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return hashlib.sha256(canonical_bytes(
        rows if rows is not None else linked_rows())).hexdigest()


# ---------------------------------------------------------------------------
# Exact speech-rate arithmetic
# ---------------------------------------------------------------------------

def _decimal(value: Any, path: str) -> Decimal:
    if not isinstance(value, str) or not DECIMAL.match(value):
        raise ValueError("decimal_format:" + path)
    try:
        number = Decimal(value)
    except InvalidOperation:
        raise ValueError("decimal_parse:" + path) from None
    if not number.is_finite():
        raise ValueError("nonfinite:" + path)
    return number


def _bounded_decimal(value: Any, path: str, low: Decimal,
                     high: Decimal) -> Decimal:
    number = _decimal(value, path)
    if number < low or number > high:
        raise ValueError("decimal_range:" + path)
    return number


def format_rate(value: Fraction) -> str:
    """Render a nonnegative Fraction as a fixed three-decimal string."""
    if value < 0:
        raise ValueError("negative_rate")
    scaled = (value * 1000).__round__()
    return (Decimal(scaled) / Decimal(1000)).quantize(Decimal("0.001"))


def format_duration(value: Decimal) -> str:
    """Render a nonnegative Decimal without trailing zeros, keeping .0."""
    text = format(value.normalize(), "f")
    if "." not in text:
        text += ".0"
    return text


def word_rate(words: list[dict], total_duration_s: str) -> dict:
    """Compute exact words/min and pause ratio from validated word spans.

    `words` entries may use int/float/string times; the admission validator
    passes only canonical decimal strings. Speech duration is the union of the
    half-open word intervals, so overlapping words are rejected upstream.
    """
    duration = _bounded_decimal(total_duration_s, "duration_s",
                                Decimal("0.001"), MAX_DURATION_S)
    if not isinstance(words, list) or not 1 <= len(words) <= MAX_MANIFEST_WORDS:
        raise ValueError("word_count_range")
    spans: list[tuple[Decimal, Decimal]] = []
    for index, word in enumerate(words):
        if not isinstance(word, dict):
            raise ValueError(f"word_type:[{index}]")
        start = _bounded_decimal(word.get("start_s"), f"[{index}].start_s",
                                 Decimal("0"), duration)
        end = _bounded_decimal(word.get("end_s"), f"[{index}].end_s",
                               Decimal("0"), duration)
        if start >= end:
            raise ValueError(f"word_order:[{index}]")
        if spans and start < spans[-1][1]:
            raise ValueError(f"word_overlap:[{index}]")
        spans.append((start, end))
    speech = sum((end - start for start, end in spans), Decimal("0"))
    if speech <= 0:
        raise ValueError("speech_duration_zero")
    count = Fraction(len(words))
    total_rate = count * 60 / Fraction(duration)
    speech_rate = count * 60 / Fraction(speech)
    pause_ratio = Fraction(duration - speech) / Fraction(duration)
    return {
        "word_count": len(words),
        "total_duration_s": format_duration(duration),
        "speech_duration_s": format_duration(speech),
        "words_per_minute_total": str(format_rate(total_rate)),
        "words_per_minute_speech": str(format_rate(speech_rate)),
        "pause_ratio": str(format_rate(pause_ratio)),
    }


# ---------------------------------------------------------------------------
# Fail-closed admission boundary for a future run manifest
# ---------------------------------------------------------------------------

def _require_object(value: Any, path: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError("object:" + path)
    return value


def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> dict:
    obj = _require_object(value, path)
    if set(obj) != set(expected):
        raise ValueError("keys:" + path)
    return obj


def _text(value: Any, path: str, pattern: re.Pattern | None = None,
          maximum: int = 1024) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ValueError("text:" + path)
    if CONTROL_CHARS.search(value):
        raise ValueError("text_control:" + path)
    if pattern is not None and not pattern.match(value):
        raise ValueError("text_pattern:" + path)
    return value


def _integer(value: Any, path: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("integer:" + path)
    if value < minimum or value > maximum:
        raise ValueError("integer_range:" + path)
    return value


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError("boolean:" + path)
    return value


def _sha(value: Any, path: str) -> str:
    return _text(value, path, HASH_HEX, 64)


def _relative(value: Any, path: str) -> str:
    text = _text(value, path, None, 512)
    if text.startswith("/") or ABSOLUTE.search(text.replace("\\", "/")):
        if text.startswith("/") or ".." in text.split("/"):
            raise ValueError("path_absolute:" + path)
    if "\\" in text:
        raise ValueError("path_backslash:" + path)
    parts = text.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("path_segment:" + path)
    return text


def _decimal_outcome(value: Any, path: str, low: str, high: str) -> Decimal:
    return _bounded_decimal(value, path, Decimal(low), Decimal(high))


def validate_manifest(manifest: dict) -> None:
    """Validate a caller-supplied word-timestamp run manifest, fail closed."""
    document = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if document["schema_id"] != ADMISSION_SCHEMA_ID:
        raise ValueError("schema_id")
    _text(document["run_id"], "run_id", SLUG, 64)

    asr = _exact_keys(document["asr"], ASR_FIELDS, "asr")
    _text(asr["engine"], "asr.engine", SLUG, 64)
    _text(asr["version"], "asr.version", VERSION, 32)
    _text(asr["source_revision"], "asr.source_revision", REVISION_HEX, 40)
    _text(asr["model_id"], "asr.model_id", SLUG, 96)
    _sha(asr["model_tree_sha256"], "asr.model_tree_sha256")
    _sha(asr["tokenizer_sha256"], "asr.tokenizer_sha256")
    _integer(asr["weight_byte_count"], "asr.weight_byte_count", 1, 1 << 40)
    _text(asr["license_id"], "asr.license_id", None, 64)
    if not _boolean(asr["terms_accepted"], "asr.terms_accepted"):
        raise ValueError("terms_not_accepted")

    runtime = _exact_keys(document["runtime"], RUNTIME_FIELDS, "runtime")
    _text(runtime["python"], "runtime.python", VERSION, 16)
    packages = runtime["packages"]
    if not isinstance(packages, list) or not 1 <= len(packages) <= MAX_MANIFEST_PACKAGES:
        raise ValueError("runtime.packages")
    names: set[str] = set()
    for index, package in enumerate(packages):
        row = _exact_keys(package, PACKAGE_FIELDS, f"runtime.packages[{index}]")
        name = _text(row["name"], f"runtime.packages[{index}].name", SLUG, 64)
        if name in names:
            raise ValueError("runtime.package_duplicate")
        names.add(name)
        _text(row["version"], f"runtime.packages[{index}].version",
              VERSION, 32)
        _sha(row["sha256"], f"runtime.packages[{index}].sha256")
    if runtime["device"] not in DEVICES:
        raise ValueError("runtime.device")
    _integer(runtime["intra_op_threads"], "runtime.intra_op_threads", 1, 1024)
    _integer(runtime["inter_op_threads"], "runtime.inter_op_threads", 1, 1024)
    if not _boolean(runtime["deterministic"], "runtime.deterministic"):
        raise ValueError("runtime.not_deterministic")
    if not _boolean(runtime["offline"], "runtime.offline"):
        raise ValueError("runtime.not_offline")

    audio = _exact_keys(document["audio"], AUDIO_FIELDS, "audio")
    _text(audio["id"], "audio.id", SLUG, 64)
    _relative(audio["path"], "audio.path")
    _sha(audio["sha256"], "audio.sha256")
    if audio["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ValueError("audio.sample_rate")
    if isinstance(audio["sample_rate_hz"], bool):
        raise ValueError("audio.sample_rate")
    if audio["channels"] != CHANNELS:
        raise ValueError("audio.channels")
    duration = _bounded_decimal(audio["duration_s"], "audio.duration_s",
                                Decimal("0.001"), MAX_DURATION_S)
    samples = _integer(audio["samples"], "audio.samples", 1, 1 << 40)
    expected_samples = int((duration * SAMPLE_RATE_HZ).to_integral_value())
    if samples != expected_samples:
        raise ValueError("audio.samples_mismatch")

    reference = _exact_keys(document["reference"], REFERENCE_FIELDS,
                            "reference")
    if reference["kind"] not in ADMISSION_REFERENCE_KINDS:
        raise ValueError("reference.kind")
    _relative(reference["path"], "reference.path")
    _sha(reference["sha256"], "reference.sha256")
    reference_words = _integer(reference["word_count"],
                               "reference.word_count", 1,
                               MAX_MANIFEST_WORDS)
    annotators = _integer(reference["annotator_count"],
                          "reference.annotator_count", 2, 64)
    if annotators < 2:
        raise ValueError("reference.annotator_count")
    if not _boolean(reference["independent_of_asr"],
                    "reference.independent_of_asr"):
        raise ValueError("reference.not_independent")

    hypothesis = _exact_keys(document["hypothesis"], HYPOTHESIS_FIELDS,
                             "hypothesis")
    words = hypothesis["words"]
    if not isinstance(words, list) or not 1 <= len(words) <= MAX_MANIFEST_WORDS:
        raise ValueError("hypothesis.words")
    if _integer(hypothesis["word_count"], "hypothesis.word_count", 1,
                MAX_MANIFEST_WORDS) != len(words):
        raise ValueError("hypothesis.word_count_mismatch")
    previous_end = Decimal("0")
    seen: set[tuple[str, str, str]] = set()
    for index, word in enumerate(words):
        row = _exact_keys(word, WORD_FIELDS, f"words[{index}]")
        text = _text(row["text"], f"words[{index}].text", None, 128)
        start = _bounded_decimal(row["start_s"], f"words[{index}].start_s",
                                 Decimal("0"), duration)
        end = _bounded_decimal(row["end_s"], f"words[{index}].end_s",
                               Decimal("0"), duration)
        if start >= end:
            raise ValueError("words.order")
        if start < previous_end:
            raise ValueError("words.overlap")
        identity = (text, str(start), str(end))
        if identity in seen:
            raise ValueError("words.duplicate")
        seen.add(identity)
        previous_end = end

    controls = document["controls"]
    if not isinstance(controls, list) or not 2 <= len(controls) <= MAX_MANIFEST_CONTROLS:
        raise ValueError("controls.count")
    control_ids: set[str] = set()
    control_kinds: set[str] = set()
    for index, control in enumerate(controls):
        row = _exact_keys(control, CONTROL_FIELDS, f"controls[{index}]")
        control_id = _text(row["id"], f"controls[{index}].id", SLUG, 64)
        if control_id in control_ids:
            raise ValueError("controls.duplicate")
        control_ids.add(control_id)
        if row["kind"] not in CONTROL_KINDS:
            raise ValueError("controls.kind")
        control_kinds.add(row["kind"])
    for required in ("uniform_timing_baseline", "no_alignment_baseline"):
        if required not in control_kinds:
            raise ValueError("controls.missing:" + required)

    outcomes = _exact_keys(document["outcomes"], OUTCOME_FIELDS, "outcomes")
    wer = _decimal_outcome(outcomes["wer"], "outcomes.wer", "0", "1")
    _decimal_outcome(outcomes["boundary_mae_ms"],
                     "outcomes.boundary_mae_ms", "0", "10000")
    _decimal_outcome(outcomes["boundary_median_abs_error_ms"],
                     "outcomes.boundary_median_abs_error_ms", "0", "10000")
    _decimal_outcome(outcomes["boundary_within_50ms_fraction"],
                     "outcomes.boundary_within_50ms_fraction", "0", "1")
    total_rate = _decimal_outcome(outcomes["words_per_minute_total"],
                                  "outcomes.words_per_minute_total",
                                  "0.001", "600")
    _decimal_outcome(outcomes["words_per_minute_speech"],
                     "outcomes.words_per_minute_speech", "0.001", "1200")
    _decimal_outcome(outcomes["pause_ratio"], "outcomes.pause_ratio",
                     "0", "1")
    matched = _integer(outcomes["matched_words"], "outcomes.matched_words",
                       0, MAX_MANIFEST_WORDS)
    if _integer(outcomes["reference_words"], "outcomes.reference_words",
                1, MAX_MANIFEST_WORDS) != reference_words:
        raise ValueError("outcomes.reference_words_mismatch")
    if matched > len(words) or matched > reference_words:
        raise ValueError("outcomes.matched_words_range")
    if _integer(outcomes["nonfinite_count"], "outcomes.nonfinite_count",
                0, MAX_MANIFEST_WORDS) != 0:
        raise ValueError("outcomes.nonfinite")
    _integer(outcomes["sample_count"], "outcomes.sample_count", 1, 1 << 40)
    expected_total = Fraction(len(words)) * 60 / Fraction(duration)
    if abs(total_rate - Decimal(format_rate(expected_total))) > Decimal("0.001"):
        raise ValueError("outcomes.rate_mismatch")
    del wer

    rights = _exact_keys(document["rights"], RIGHTS_FIELDS, "rights")
    for field in RIGHTS_FIELDS[:-1]:
        _text(rights[field], "rights." + field, None, 512)
    if _boolean(rights["claims_qualified"], "rights.claims_qualified"):
        raise ValueError("rights.claims_qualified")


# ---------------------------------------------------------------------------
# Synthetic controls (explicitly not evidence)
# ---------------------------------------------------------------------------

SYNTHETIC_WORDS = (
    {"text": "alpha", "start_s": "0.0", "end_s": "0.2"},
    {"text": "bravo", "start_s": "0.25", "end_s": "0.45"},
    {"text": "charlie", "start_s": "0.5", "end_s": "0.7"},
    {"text": "delta", "start_s": "2.0", "end_s": "2.2"},
    {"text": "echo", "start_s": "2.3", "end_s": "2.5"},
)


def rate_control() -> dict:
    """Deterministic arithmetic control: 5 words in 4.0 s, 1.0 s speech."""
    result = word_rate(list(SYNTHETIC_WORDS), "4.0")
    expected = {
        "word_count": 5,
        "total_duration_s": "4.0",
        "speech_duration_s": "1.0",
        "words_per_minute_total": "75.000",
        "words_per_minute_speech": "300.000",
        "pause_ratio": "0.750",
    }
    if result != expected:
        raise ValueError("synthetic_rate_control_mismatch")
    return {
        "id": "SYNTH-RATE-01",
        "kind": "synthetic_arithmetic_control_not_evidence",
        "input_words": [dict(word) for word in SYNTHETIC_WORDS],
        "total_duration_s": "4.0",
        "expected": expected,
        "observed": dict(result),
        "matches": result == expected,
        "qualifies": False,
        "note": (
            "Hand-constructed arithmetic only. No ASR engine, audio or human "
            "reference is involved and no candidate can qualify from it."),
    }


def _synthetic_digest(label: str) -> str:
    return hashlib.sha256(("synthetic-control:" + label).encode()).hexdigest()


def control_manifest() -> dict:
    words = [
        {"text": "the", "start_s": "0.0", "end_s": "0.2"},
        {"text": "quick", "start_s": "0.2", "end_s": "0.45"},
        {"text": "brown", "start_s": "0.45", "end_s": "0.7"},
        {"text": "fox", "start_s": "1.5", "end_s": "1.75"},
    ]
    duration = "2.0"
    rate = word_rate(words, duration)
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "run_id": "synthetic-shape-control",
        "asr": {
            "engine": "synthetic-word-clock",
            "version": "0.0.1",
            "source_revision": "0" * 40,
            "model_id": "synthetic-word-clock",
            "model_tree_sha256": _synthetic_digest("model"),
            "tokenizer_sha256": _synthetic_digest("tokenizer"),
            "weight_byte_count": 1,
            "license_id": "Apache-2.0",
            "terms_accepted": True,
        },
        "runtime": {
            "python": "3.11.5",
            "packages": [
                {"name": "synthetic-clock", "version": "0.0.1",
                 "sha256": _synthetic_digest("package")},
            ],
            "device": "cpu",
            "intra_op_threads": 1,
            "inter_op_threads": 1,
            "deterministic": True,
            "offline": True,
        },
        "audio": {
            "id": "synthetic-tone",
            "path": "synthetic/tone.wav",
            "sha256": _synthetic_digest("audio"),
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "samples": 32000,
            "duration_s": duration,
        },
        "reference": {
            "kind": "adjudicated_human",
            "path": "synthetic/reference.json",
            "sha256": _synthetic_digest("reference"),
            "word_count": 4,
            "annotator_count": 2,
            "independent_of_asr": True,
        },
        "hypothesis": {"words": words, "word_count": len(words)},
        "controls": [
            {"id": "uniform", "kind": "uniform_timing_baseline"},
            {"id": "no-alignment", "kind": "no_alignment_baseline"},
        ],
        "outcomes": {
            "wer": "0.0",
            "boundary_mae_ms": "10.0",
            "boundary_median_abs_error_ms": "8.0",
            "boundary_within_50ms_fraction": "1.0",
            "words_per_minute_total": rate["words_per_minute_total"],
            "words_per_minute_speech": rate["words_per_minute_speech"],
            "pause_ratio": rate["pause_ratio"],
            "matched_words": 4,
            "reference_words": 4,
            "nonfinite_count": 0,
            "sample_count": 32000,
        },
        "rights": {
            "audio_terms_reference": "synthetic/terms.txt",
            "model_terms_reference": "synthetic/terms.txt",
            "output_use_reference": "synthetic/output-use.txt",
            "review_reference": "synthetic/review.txt",
            "claims_qualified": False,
        },
    }


def _mutate(base: dict, path: tuple[str, ...], value: Any) -> dict:
    document = copy.deepcopy(base)
    target = document
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return document


def _delete(base: dict, path: tuple[str, ...]) -> dict:
    document = copy.deepcopy(base)
    target = document
    for key in path[:-1]:
        target = target[key]
    del target[path[-1]]
    return document


def admission_cases() -> list[dict]:
    base = control_manifest()
    words = base["hypothesis"]["words"]

    cases: list[tuple[str, dict, str, str]] = [
        ("valid_shape_control", base, "accepted", "structurally_admissible"),
        ("missing_run_id", _delete(base, ("run_id",)), "rejected", "keys"),
        ("extra_field", _mutate(base, ("extra",), 1), "rejected", "keys"),
        ("wrong_schema_id",
         _mutate(base, ("schema_id",), "audio-sdk/other/0.1"),
         "rejected", "schema_id"),
        ("invalid_run_id", _mutate(base, ("run_id",), "Bad Id"),
         "rejected", "text_pattern"),
        ("nan_start", _mutate(base, ("hypothesis", "words", 0, "start_s"),
                              "NaN"), "rejected", "decimal_format"),
        ("infinite_end", _mutate(base, ("hypothesis", "words", 0, "end_s"),
                                 "Infinity"), "rejected", "decimal_format"),
        ("float_time", _mutate(base, ("hypothesis", "words", 0, "start_s"),
                               0.0), "rejected", "decimal_format"),
        ("negative_start", _mutate(base, ("hypothesis", "words", 0, "start_s"),
                                   "-0.1"), "rejected", "decimal_format"),
        ("zero_length_word", _mutate(base, ("hypothesis", "words", 0, "end_s"),
                                     "0.0"), "rejected", "words.order"),
        ("overlapping_words", _mutate(base, ("hypothesis", "words", 1, "start_s"),
                                      "0.1"), "rejected", "words.overlap"),
        ("end_beyond_duration",
         _mutate(base, ("hypothesis", "words", 3, "end_s"), "2.5"),
         "rejected", "decimal_range"),
        ("word_count_mismatch",
         _mutate(base, ("hypothesis", "word_count"), 5),
         "rejected", "hypothesis.word_count_mismatch"),
        ("duplicate_word_span",
         _mutate(base, ("hypothesis", "words", 1), dict(words[0])),
         "rejected", "words.overlap"),
        ("uppercase_hash",
         _mutate(base, ("audio", "sha256"), _synthetic_digest("audio").upper()),
         "rejected", "text_pattern"),
        ("absolute_audio_path",
         _mutate(base, ("audio", "path"), "/tmp/tone.wav"),
         "rejected", "path_absolute"),
        ("parent_traversal",
         _mutate(base, ("audio", "path"), "../tone.wav"),
         "rejected", "path_absolute"),
        ("stereo_audio", _mutate(base, ("audio", "channels"), 2),
         "rejected", "audio.channels"),
        ("wrong_sample_rate", _mutate(base, ("audio", "sample_rate_hz"), 8000),
         "rejected", "audio.sample_rate"),
        ("boolean_sample_rate",
         _mutate(base, ("audio", "sample_rate_hz"), True),
         "rejected", "audio.sample_rate"),
        ("sample_count_mismatch", _mutate(base, ("audio", "samples"), 16000),
         "rejected", "audio.samples_mismatch"),
        ("nonfinite_count",
         _mutate(base, ("outcomes", "nonfinite_count"), 1),
         "rejected", "outcomes.nonfinite"),
        ("boundary_nan",
         _mutate(base, ("outcomes", "boundary_mae_ms"), "NaN"),
         "rejected", "decimal_format"),
        ("pause_ratio_out_of_range",
         _mutate(base, ("outcomes", "pause_ratio"), "1.5"),
         "rejected", "decimal_range"),
        ("rate_mismatch",
         _mutate(base, ("outcomes", "words_per_minute_total"), "12.000"),
         "rejected", "outcomes.rate_mismatch"),
        ("matched_words_overflow",
         _mutate(base, ("outcomes", "matched_words"), 9),
         "rejected", "outcomes.matched_words_range"),
        ("terms_not_accepted", _mutate(base, ("asr", "terms_accepted"), False),
         "rejected", "terms_not_accepted"),
        ("offline_false", _mutate(base, ("runtime", "offline"), False),
         "rejected", "runtime.not_offline"),
        ("nondeterministic_runtime",
         _mutate(base, ("runtime", "deterministic"), False),
         "rejected", "runtime.not_deterministic"),
        ("reference_not_independent",
         _mutate(base, ("reference", "independent_of_asr"), False),
         "rejected", "reference.not_independent"),
        ("single_annotator",
         _mutate(base, ("reference", "annotator_count"), 1),
         "rejected", "reference.annotator_count"),
        ("construction_label_reference",
         _mutate(base, ("reference", "kind"), "construction_label"),
         "rejected", "reference.kind"),
        ("missing_uniform_baseline",
         _mutate(base, ("controls",), [{"id": "no-alignment",
                                        "kind": "no_alignment_baseline"}]),
         "rejected", "controls.count"),
        ("missing_no_alignment_baseline",
         _mutate(base, ("controls",), [{"id": "uniform",
                                        "kind": "uniform_timing_baseline"}]),
         "rejected", "controls.count"),
        ("duplicate_control_id",
         _mutate(base, ("controls",),
                 [{"id": "same", "kind": "uniform_timing_baseline"},
                  {"id": "same", "kind": "no_alignment_baseline"}]),
         "rejected", "controls.duplicate"),
        ("claims_qualified_true",
         _mutate(base, ("rights", "claims_qualified"), True),
         "rejected", "rights.claims_qualified"),
        ("empty_rights_reference",
         _mutate(base, ("rights", "review_reference"), ""),
         "rejected", "text:rights.review_reference"),
    ]

    rows = []
    for case_id, manifest, expected, reason in cases:
        observed = "accepted"
        error = None
        try:
            validate_manifest(manifest)
        except ValueError as failure:
            observed = "rejected"
            error = str(failure)
        rows.append({
            "id": case_id,
            "expected": expected,
            "observed": observed,
            "expected_reason": reason,
            "observed_reason": error,
            "matches": observed == expected,
            "qualifies": False,
        })
    if not all(row["matches"] for row in rows):
        raise ValueError("admission_case_failure")
    return rows


# ---------------------------------------------------------------------------
# Readiness record
# ---------------------------------------------------------------------------

def exact_models() -> dict:
    return {
        "vosk": {
            "role": "streaming_word_boundary_gate_reference",
            "present_bytes": True,
            "model": "vosk-model-small-en-us-0.15",
            "model_tree_sha256": VOSK_MODEL["tree_sha256"],
            "model_file_count": VOSK_MODEL["file_count"],
            "model_byte_count": VOSK_MODEL["byte_count"],
            "copyright_notice_present": True,
            "license_text_present": False,
            "notice_or_model_card_present": False,
            "official_archive_sha256": None,
            "source_revision": None,
            "runtime": "vosk 0.3.44",
            "runtime_metadata_license": "UNKNOWN",
            "runtime_license_file_present": False,
            "license_recorded_in_study": "Apache-2.0 (code; model terms unverified)",
            "digests_verified": True,
            "rights_verified": False,
            "terms_reviewed": False,
            "output_use_defined": False,
            "loaded_or_executed_here": False,
            "qualifies": False,
        },
        "sherpa_whisper_tiny_en": {
            "role": "offline_transcript_scorer_reference",
            "present_bytes": True,
            "model": "sherpa-onnx-whisper-tiny.en",
            "model_tree_sha256": SHERPA_MODEL["tree_sha256"],
            "model_file_count": SHERPA_MODEL["file_count"],
            "model_byte_count": SHERPA_MODEL["byte_count"],
            "copyright_notice_present": False,
            "license_text_present": False,
            "notice_or_model_card_present": False,
            "official_archive_sha256": None,
            "source_revision": None,
            "runtime": "sherpa_onnx 2.0.1",
            "runtime_metadata_license": "Apache-2.0",
            "runtime_license_file_present": False,
            "license_recorded_in_study": "MIT code / OpenAI model terms (evaluation only)",
            "digests_verified": True,
            "rights_verified": False,
            "terms_reviewed": False,
            "output_use_defined": False,
            "loaded_or_executed_here": False,
            "qualifies": False,
        },
    }


def documented_context() -> dict:
    return {
        "source_finding": (
            "ASR word timestamps (words/min) are the most robust speech-rate "
            "proxy when an ASR path already exists; licence and commercial use "
            "depend on the chosen ASR."),
        "study": (
            "Semantic playback-speed chain prevalidation; Vosk gate plus "
            "Signalsmith/Bungee/Sonic actuators, Whisper tiny.en WER proxy."),
        "recorded_word_spans": [dict(row) for row in RECORDED_WORD_SPANS],
        "study_reported_words_per_minute": False,
        "reproduced_here": False,
        "provenance_only": True,
        "used_for_evidence": False,
        "qualifies": False,
    }


def licensing() -> dict:
    return {
        "package_license": "Apache-2.0",
        "vendored_third_party_bytes": False,
        "vosk_model_license_recorded": "Apache-2.0 code / model terms unverified",
        "vosk_model_terms_reviewed": False,
        "vosk_runtime_metadata_license": "UNKNOWN",
        "vosk_runtime_license_file_present": False,
        "sherpa_whisper_model_license_recorded": "MIT code / OpenAI model terms",
        "sherpa_whisper_model_terms_reviewed": False,
        "ami_license_recorded": "CC BY 4.0",
        "ami_terms_reviewed": False,
        "tts_construction_labels": "synthetic; not an independent gold reference",
        "output_use_defined": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": "float32",
        "frame_samples": FRAME_SAMPLES,
        "changed": False,
    }


def scope() -> dict:
    return {
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
    }


def qualification() -> dict:
    return {
        "status": "not_qualified",
        "readiness": "incomplete",
        "not_qualified": True,
        "real_result_present": False,
        "source_present": True,
        "model_bytes_present": True,
        "licensed_model_present": False,
        "runtime_present": False,
        "word_timestamp_result": False,
        "rate_result": False,
        "boundary_result": False,
        "finite_output_result": False,
        "device_timing_result": False,
        "rate_profile_result": False,
        "listening_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "all_release_gates_blocked": True,
    }


def boundary() -> dict:
    row = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = linked_rows()
    return {
        "linked_row_identity_only": True,
        "board_file_pinned": False,
        "mutable_board_fields_gate": False,
        "projected_fields": list(BOARD_ROW_FIELDS),
        "linked_row": row,
        "linked_row_sha256": board_row_digest(row),
        "linked_rows_sha256": linked_rows_digest(rows),
        "linked_rows": rows,
    }


def build_contract() -> dict:
    link = boundary()
    gates = [dict(gate, qualifies=False, linked_row=link["linked_row"])
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
        "qualification": qualification(),
        "qualification_status": "not_qualified",
        "disposition": DISPOSITION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "scope": scope(),
        "boundary": link,
        "public_v0_geometry": public_v0_geometry(),
        "exact_models": exact_models(),
        "documented_context": documented_context(),
        "required_artifacts": [dict(row) for row in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(row) for row in EXACT_BLOCKERS],
        "release_gates": gates,
        "rate_profile_requirements": [dict(row) for row in RATE_PROFILE_ROWS],
        "quality_outcomes": [dict(row) for row in QUALITY_ROWS],
        "timing_requirements": [dict(row) for row in TIMING_ROWS],
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "fields": list(MANIFEST_FIELDS),
            "asr_fields": list(ASR_FIELDS),
            "runtime_fields": list(RUNTIME_FIELDS),
            "package_fields": list(PACKAGE_FIELDS),
            "audio_fields": list(AUDIO_FIELDS),
            "reference_fields": list(REFERENCE_FIELDS),
            "hypothesis_fields": list(HYPOTHESIS_FIELDS),
            "word_fields": list(WORD_FIELDS),
            "control_fields": list(CONTROL_FIELDS),
            "outcome_fields": list(OUTCOME_FIELDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "reference_kinds": list(REFERENCE_KINDS),
            "admission_reference_kinds": list(ADMISSION_REFERENCE_KINDS),
            "max_words": MAX_MANIFEST_WORDS,
            "max_controls": MAX_MANIFEST_CONTROLS,
            "max_packages": MAX_MANIFEST_PACKAGES,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "admission_only": True,
            "qualifies": False,
        },
        "non_claims": list(NON_CLAIMS),
        "required_results": list(REQUIRED_RESULTS),
        "licensing": licensing(),
    }


def present_assets() -> dict:
    return {
        "scratch_root": SCRATCH_ROOT,
        "probed_by_this_session": True,
        "downloaded_or_reconstructed": False,
        "imported_or_executed": False,
        "vosk_model": {
            "relative": VOSK_MODEL["relative"],
            "tree_sha256": VOSK_MODEL["tree_sha256"],
            "file_count": VOSK_MODEL["file_count"],
            "byte_count": VOSK_MODEL["byte_count"],
            "files": dict(sorted(VOSK_MODEL["files"].items())),
        },
        "sherpa_whisper_model": {
            "relative": SHERPA_MODEL["relative"],
            "tree_sha256": SHERPA_MODEL["tree_sha256"],
            "file_count": SHERPA_MODEL["file_count"],
            "byte_count": SHERPA_MODEL["byte_count"],
            "files": dict(sorted(SHERPA_MODEL["files"].items())),
        },
        "runtime_files": dict(sorted(RUNTIME_FILES.items())),
        "tree_digest_rule": (
            "SHA-256 over sorted 'relative\\0file_sha256\\0byte_count\\n'"),
    }


def build_report() -> dict:
    contract = build_contract()
    pins = {
        "source": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary": pin_rows(BOUNDARY_PINS, WORKTREE),
        "sibling": pin_rows(SIBLING_PINS, WORKTREE),
    }
    cases = admission_cases()
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
        "exact_models": contract["exact_models"],
        "documented_context": contract["documented_context"],
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
        "present_assets": present_assets(),
        "admission": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "cases": cases,
            "case_count": len(cases),
            "accepted_count": sum(1 for row in cases
                                  if row["observed"] == "accepted"),
            "rejected_count": sum(1 for row in cases
                                  if row["observed"] == "rejected"),
            "all_cases_match": all(row["matches"] for row in cases),
            "structural_only": True,
            "qualifies": False,
            "note": (
                "The accepted shape case is a synthetic control manifest. "
                "Acceptance is structural admission only; every release gate "
                "remains blocked and no candidate qualifies."),
        },
        "scorer_control": rate_control(),
        "source_pins": pins["source"],
        "boundary_pins": pins["boundary"],
        "sibling_pins": pins["sibling"],
        "linked_row_identity": {
            "projection": contract["boundary"]["linked_row"],
            "sha256": contract["boundary"]["linked_row_sha256"],
            "linked_rows": contract["boundary"]["linked_rows"],
            "linked_rows_sha256": contract["boundary"]["linked_rows_sha256"],
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
    _no_floats(document)
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
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal_only")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification")
    if contract["qualification"].get("not_qualified") is not True:
        raise ValueError("contract_not_qualified")
    gates = contract.get("release_gates")
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gates")
    if [gate.get("id") for gate in gates] != [f"RG-{i:02d}"
                                              for i in range(1, 9)]:
        raise ValueError("contract_gate_ids")
    for gate in gates:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            raise ValueError("contract_gate_blocked")
        if gate.get("linked_row") != contract["boundary"]["linked_row"]:
            raise ValueError("contract_gate_row")
    if len(contract.get("exact_blockers", [])) != 6:
        raise ValueError("contract_blockers")
    if len(contract.get("required_artifacts", [])) != 7:
        raise ValueError("contract_artifacts")
    for row in contract.get("rate_profile_requirements", []):
        if row.get("status") != "blocked":
            raise ValueError("contract_rate_row")
    _no_floats(contract)

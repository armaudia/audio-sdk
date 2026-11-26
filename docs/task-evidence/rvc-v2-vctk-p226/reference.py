# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-RVC-V2-VCTK-P226.

Standard-library only and deterministic. This module contains no RVC source
copy, checkpoint weight, HuBERT/RMVPE base weight, runtime, waveform decoder,
converted waveform, listening result or model result. It records the exact
external blocker, pins the source files that declare the model and pipeline
shape, probes a fixed list of workspace and home-cache paths to evidence the
absence of the checkpoint, base assets and runtime, models the declared
pipeline geometry and asset admission preconditions as exact integer
arithmetic, validates a caller-supplied reproduction bundle with a fail-closed
admission boundary, and builds the canonical report.

The RVC fork checkout is present at an exact revision with an MIT licence. That
source-code presence is pinned, but it is not a checkpoint grant, a base-asset
grant, a runtime, a verified speaker map, a converted waveform or a
qualification. The p226 checkpoint (`Mp226rmvpe.pth`), the HuBERT
`pytorch_model.bin`, the RMVPE `rmvpe.pt` and the PyTorch runtime are absent.
Nothing was downloaded, loaded or executed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-RVC-V2-VCTK-P226"
COMPONENT_ID = "rvc-v2-vctk-p226"
TASK_TITLE = "RVC v2 VCTK p226"
CONTRACT_ID = "audio-sdk/rvc-v2-vctk-p226-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "voice"
PROFILE_LABEL = "Voice"
MODE = "implementation"
BASE_COMMIT = "37633ac33fd798512b1a30845a1334134ab1384e"
BRANCH = "swarm/SDK-RVC-V2-VCTK-P226"
WRITE_SCOPE = "docs/task-evidence/rvc-v2-vctk-p226/ only"
TASK_PREFIX = "docs/task-evidence/rvc-v2-vctk-p226/"

SOURCE_REVISION = "81eed5e8f68b6bed1789f682fe78cdd324495afc"
SOURCE_REPOSITORY = "RVC-Project/Retrieval-based-Voice-Conversion-WebUI"
SOURCE_DISTRIBUTION = "Retrieval-based-Voice-Conversion-WebUI"
SOURCE_LICENSE = "MIT"

CHECKPOINT_NAME = "Mp226rmvpe.pth"
HUBERT_MODEL_NAME = "pytorch_model.bin"
HUBERT_CONFIG_NAME = "config.json"
HUBERT_PREPROCESSOR_NAME = "preprocessor_config.json"
RMVPE_MODEL_NAME = "rmvpe.pt"

FEATURE_VERSION = "v2"
HUBERT_HIDDEN_SIZE = 768
SPEAKER_COUNT = 109
SELECTED_SPEAKER_ID = 1
INPUT_SAMPLE_RATE_HZ = 16000
OUTPUT_SAMPLE_RATE_HZ = 40000
WINDOW_SAMPLES = 160
RMVPE_HOP_SAMPLES = 160
F0_MIN_HZ = 50
F0_MAX_HZ = 1100
CPU_X_PAD = 1
CPU_X_QUERY = 6
CPU_X_CENTER = 38
CPU_X_MAX = 41

SOURCE_AUDIO_PATH = (
    "research/voice-conversion-eval-20261101/data/"
    "source_ljspeech_lj001-0001.wav")
SOURCE_AUDIO_SHA256 = (
    "adc9736d0a02b8efe57128b2c6843605e81ab24027f23f6fc7d05bcd6107753b")
SOURCE_AUDIO_BYTES = 309006
SOURCE_DURATION_SECONDS = "9.655"
OUTPUT_SHA256 = (
    "7fa0516e7475b6870267da9f4a894d0d18e67714e1081cd9d3c7d63db30bd8c7")
OUTPUT_BYTES = 771244
OUTPUT_DURATION_SECONDS = "9.64"

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
VC_ROOT = "research/voice-conversion-eval-20261101"
RVC_ROOT = "research/voice-conversion-eval-20261101/repos/rvc"

# Immutable read-only inputs. `source:` rows are workspace-relative; the rest
# are SDK-worktree-relative. The mutable shared board is deliberately excluded
# from the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/"
    "REPORT.md":
        "b7db9a73b45b3a8918e99453e0de00c9f8f2f64604acee56c3838d3a10e2f9b6",
    "research/voice-conversion-eval-20261101/scripts/run_rvc_vctk_eval.py":
        "a8f66b2a5af368f4a0573e954022e17577e2d9f0c3778abb0a1a4e65c15877da",
    "research/voice-conversion-eval-20261101/results/rvc/metrics.json":
        "14fc2c08086efadea87ba5a254704e086c3c4c94831a82de8796184168918b36",
    "research/voice-conversion-eval-20261101/results/rvc/asr.json":
        "2d28a6e4e93e450bc7894e68881926bb315d73dd82cd08bd44e597f7d51fff24",
    "research/voice-conversion-eval-20261101/results/rvc/source_to_p226.wav":
        "7fa0516e7475b6870267da9f4a894d0d18e67714e1081cd9d3c7d63db30bd8c7",
    "research/voice-conversion-eval-20261101/data/"
    "source_ljspeech_lj001-0001.wav":
        "adc9736d0a02b8efe57128b2c6843605e81ab24027f23f6fc7d05bcd6107753b",
    "research/voice-conversion-eval-20261101/data/target_rtvc_p360.flac":
        "fcfffdbf9b96bdc720f924de1877f515766e438242afe2306f4a919ba6809b44",
    "research/voice-conversion-eval-20261101/repos/rvc/LICENSE":
        "bec61ed1eb9a3748644ddbc50303aa6978e14eeaba46822e59a006c722b52585",
    "research/voice-conversion-eval-20261101/repos/rvc/README.md":
        "6ae347c0cc60836f1e7fd2b73ee73327746e66c32a5dd4270d02a096810bca8b",
    "research/voice-conversion-eval-20261101/repos/rvc/infer/vc/pipeline.py":
        "df8ccd98ca7f81e38934a0af93cc63b4f79764dc47d932f05914c566e876522a",
    "research/voice-conversion-eval-20261101/repos/rvc/infer/vc/modules.py":
        "7b2e12f56c2b2462d7944d8eda470796ffd4aec50f784c3f6f5169133eaae89b",
    "research/voice-conversion-eval-20261101/repos/rvc/infer/vc/utils.py":
        "6c8900146c0b00752cc54eabd69f0e1683e3045f6eb64ce76fc34b3500ec2620",
    "research/voice-conversion-eval-20261101/repos/rvc/infer/hubert.py":
        "bbfba54d1d83eae3fb634b2909f8f6bf41e6ffe436200ec246867c5c93ebba26",
    "research/voice-conversion-eval-20261101/repos/rvc/infer/rmvpe.py":
        "074171aec63e4b68f04d8691c62af50a1d99b9bc6dc56c4d6749fad4ba64853a",
    "research/voice-conversion-eval-20261101/repos/rvc/configs/config.py":
        "f304463184b55898aa256fadeafd50d640ed0f880dbae6f89ad54db358240043",
    "research/voice-conversion-eval-20261101/repos/rvc/assets/hubert_base/"
    "config.json":
        "0346950779dfb7f9316fa74ed846e2b8a22a08eedfdc5387b73f327cb1a4a7cf",
    "research/voice-conversion-eval-20261101/repos/rvc/assets/hubert_base/"
    "preprocessor_config.json":
        "7c1976a680fb7acc757cd36fb08eef878fa36c70b4c9d2d595df9c608bbbbf0e",
    "research/voice-conversion-eval-20261101/repos/rvc/"
    "requirments_cpu_py312.txt":
        "902338f1c8ef6c38186a34c19dec95e8df56030863b7a584b703a443127ea541",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
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
    "docs/task-evidence/chatterbox-vc/README.md":
        "7a624864df916ef87b32655e6e0894bfe00c3da94ca6969352be68654ee1443c",
    "docs/task-evidence/chatterbox-vc/report.json":
        "321fe22b052823b43d772871b5b694df03c0586c6754c04491d40406055b3dee",
    "docs/task-evidence/cosyvoice-2-0-5b/README.md":
        "2cdc7f47c5cd232d17ca28514f7efcc896cb393a8141f57abf39cc0234d0f099",
    "docs/task-evidence/cosyvoice-2-0-5b/report.json":
        "aee352f4b45d3ad11af6372886a5f2a1e6458ef8d0d89d597f4c8379787b75f2",
    "docs/task-evidence/openvoice-v2/README.md":
        "bcd58494af03ffee38b65ac4926ae0aed8768dd45ad966617629cfd6c9a10226",
    "docs/task-evidence/openvoice-v2/report.json":
        "27986b993beca10ae2d9e354fca4102db8795e10d845f3b89d8273fa9531b9c8",
    "docs/task-evidence/survey-trn-04/README.md":
        "e0b4ea4d92b122e9820b9857da5e4813db29b048468f2b0383e67ef4264eccae",
    "docs/task-evidence/survey-trn-04/report.json":
        "fb34a1129db91808c450cf9ce90d68a2f2ff34734b26891763ede6b0915f0446",
    "docs/task-evidence/rvc-mlx-realtime/README.md":
        "5519ba8a9e71b2d3f845f3bb2aea9496e59d74aadd0909a2d5e2170679447177",
    "docs/task-evidence/rvc-mlx-realtime/report.json":
        "f69377fd201bcd0b76b87d3ea79789c6ef7bf2ec0447690643e7d68216e1f9d6",
    "docs/task-evidence/rvc-faiss-retrieval/README.md":
        "eba9740ac25712fb99644ac481ec86139acf45eea1c0e81acdecd218f66518ca",
    "docs/task-evidence/rvc-faiss-retrieval/report.json":
        "da64f7ac95942bbff2e015dcd9a79334b8024aa11eefdb19a4a932e6cdf99727",
}

# Only stable, non-mutable identity fields are projected. `status`, `owner`,
# `claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` never
# enter canonical bytes and never gate this package.
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_PROJECTION = {
    "id": TASK,
    "title": TASK_TITLE,
    "component": COMPONENT_ID,
    "mode": MODE,
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
                   "SDK-FND-PROVIDER"],
}
LINKED_ROWS = (
    BOARD_ROW_PROJECTION,
    {
        "id": "SDK-FND-AUDIT",
        "title": "Public provider intake and asset boundary",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
    {
        "id": "SDK-FND-EVIDENCE",
        "title": "Task-matched conformance and reproducible benchmark evidence",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
    {
        "id": "SDK-FND-NN",
        "title": "Optional neural and offline runtime boundary",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-FND-PROVIDER",
        "title": "Provider integration boundaries and build fragments",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-TIMING"],
    },
    {
        "id": "SDK-RVC-MLX-REALTIME",
        "title": "RVC-MLX realtime",
        "component": "rvc-mlx-realtime",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
                       "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-RVC-FAISS-RETRIEVAL",
        "title": "RVC FAISS retrieval",
        "component": "rvc-faiss-retrieval",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
)

# Fixed, bounded absence probes. No recursive workspace walk is performed and
# no download is attempted. Any present path blocks report generation.
ABSENCE_PROBES = (
    "research/voice-conversion-eval-20261101/models",
    "research/voice-conversion-eval-20261101/models/rvc-vctk",
    "research/voice-conversion-eval-20261101/models/rvc-vctk/M",
    "research/voice-conversion-eval-20261101/models/rvc-vctk/M/p226",
    "research/voice-conversion-eval-20261101/models/rvc-vctk/M/p226/rmvpe",
    "research/voice-conversion-eval-20261101/models/rvc-vctk/M/p226/rmvpe/"
    "Mp226rmvpe.pth",
    "research/voice-conversion-eval-20261101/checkpoints/rvc",
    "research/voice-conversion-eval-20261101/checkpoints/rvc/"
    "Mp226rmvpe.pth",
    "research/voice-conversion-eval-20261101/.venv-eval",
    "research/voice-conversion-eval-20261101/.venv-chatterbox",
    "research/voice-conversion-eval-20261101/repos/rvc/.venv",
    "research/voice-conversion-eval-20261101/repos/rvc/venv",
    "research/voice-conversion-eval-20261101/repos/rvc/assets/rmvpe/rmvpe.pt",
    "research/voice-conversion-eval-20261101/repos/rvc/assets/hubert_base/"
    "pytorch_model.bin",
    "research/voice-conversion-eval-20261101/repos/rvc/logs",
    "data/assets/rvc-v2-vctk-p226",
    "data/assets/rvc-v2-vctk-p226/Mp226rmvpe.pth",
    "data/assets/rvc-v2-vctk-p226/hubert_base/pytorch_model.bin",
    "data/assets/rvc-v2-vctk-p226/rmvpe.pt",
    "third_party/rvc",
    "third_party/rvc-v2-vctk-p226",
    "deps/rvc",
    "adapters/rvc-v2-vctk-p226",
    "LICENSES/RVC-VCTK-weights.txt",
    "LICENSES/RVC-VCTK-checkpoint.txt",
    "docs/task-evidence/rvc-v2-vctk-p226/weights",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--Nekochu--RVC-VCTK_Voice-sample",
    "~/.cache/huggingface/hub/models--Nekochu--RVC-VCTK_Voice-sample/blobs",
    "~/.cache/huggingface/hub/models--Nekochu--RVC-VCTK_Voice-sample/snapshots",
    "~/.cache/huggingface/hub/models--lj1995--VoiceConversionWebUI",
)

OBSERVED_INCOMPLETE_PATHS = (
    {
        "path": "research/voice-conversion-eval-20261101/repos/rvc/assets/rmvpe",
        "present": True,
        "entry_count": 0,
        "usable_weights_present": False,
        "note": "Directory exists but is empty; no RMVPE weight is staged.",
    },
    {
        "path": "research/voice-conversion-eval-20261101/repos/rvc/assets/"
                "hubert_base",
        "present": True,
        "entry_count": 2,
        "usable_weights_present": False,
        "note": "Config JSON files only; no HuBERT pytorch_model.bin is staged.",
    },
)

OBSERVED_UNUSABLE_REFERENCES = (
    {
        "path": "research/voice-conversion-eval-20261101/data/"
                "target_rtvc_p360.flac",
        "sha256":
            "fcfffdbf9b96bdc720f924de1877f515766e438242afe2306f4a919ba6809b44",
        "byte_count": 69398,
        "role": "historical_realtime_p360_reference",
        "target_match": False,
        "consent_present": False,
        "reference_availability_present": False,
        "output_use_present": False,
        "decoded": False,
        "eligible_as_p226_reference": False,
        "note": (
            "A p360 reference from a different historical realtime experiment. "
            "It is not p226, has no consent or availability record, and is not "
            "decoded or used."),
    },
)

RUNTIME_PROBE_MODULES = ("torch", "torchaudio", "numpy", "soundfile",
                         "librosa", "transformers", "faiss", "parselmouth",
                         "scipy")
RUNTIME_PROBE = {
    "probe": "importlib.util.find_spec metadata only; no import performed",
    "import_performed": False,
    "model_executed": False,
    "weights_loaded": False,
    "audio_decoded": False,
    "all_runtime_modules_absent": True,
}

SOURCE_PRESENCE = {
    "path": "research/voice-conversion-eval-20261101/repos/rvc",
    "repository": SOURCE_REPOSITORY,
    "distribution": SOURCE_DISTRIBUTION,
    "revision": SOURCE_REVISION,
    "license_id": SOURCE_LICENSE,
    "license_path": (
        "research/voice-conversion-eval-20261101/repos/rvc/LICENSE"),
    "license_sha256":
        "bec61ed1eb9a3748644ddbc50303aa6978e14eeaba46822e59a006c722b52585",
    "present": True,
    "verified": True,
    "admitted": False,
    "model_executed": False,
    "weights_used": False,
    "present_components": [
        "source_code_and_mit_license",
        "pinned_v2_synthesizer_and_pipeline_declarations",
        "pinned_hubert_rmvpe_base_asset_paths",
        "historical_output_and_metric_provenance",
    ],
    "absent_components": [
        "checkpoint_weights_Mp226rmvpe_pth",
        "hubert_base_pytorch_model_bin",
        "rmvpe_base_rmvpe_pt",
        "pytorch_and_transformers_runtime",
        "verified_speaker_map",
        "source_speaker_and_target_voice_rights",
    ],
    "exact_source_weights_runtime_conjunction_present": False,
    "reason": (
        "The RVC checkout is present at the pinned 40-hex revision with an MIT "
        "LICENSE, and the v2 synthesizer, HuBERT/RMVPE loading, F0 and "
        "pipeline declarations are pinned. That source-code presence grants no "
        "checkpoint, base-asset, dataset, voice, consent or output-use right. "
        "The p226 checkpoint, both base weights and the PyTorch runtime are "
        "absent, so the source/weights/runtime conjunction is not present."),
}

# Exact declarations read from the pinned source. These are static facts, not
# executed behaviour. Line numbers are re-checked by verify.py.
SOURCE_DECLARATIONS = {
    "pipeline": {
        "path": "research/voice-conversion-eval-20261101/repos/rvc/infer/vc/"
                "pipeline.py",
        "sha256":
            "df8ccd98ca7f81e38934a0af93cc63b4f79764dc47d932f05914c566e876522a",
        "input_sample_rate_line": 54,
        "input_sample_rate_fragment": "self.sr = 16000",
        "window_line": 55,
        "window_fragment": "self.window = 160",
        "rmvpe_call_line": 106,
        "rmvpe_call_fragment": "self.model_rmvpe.infer_from_audio(x, thred=0.03)",
        "feature_upsample_line": 198,
        "feature_upsample_fragment": "scale_factor=2",
        "content_length_line": 204,
        "content_length_fragment": "p_len = audio0.shape[0] // self.window",
    },
    "modules": {
        "path": "research/voice-conversion-eval-20261101/repos/rvc/infer/vc/"
                "modules.py",
        "sha256":
            "7b2e12f56c2b2462d7944d8eda470796ffd4aec50f784c3f6f5169133eaae89b",
        "target_rate_line": 175,
        "target_rate_fragment": 'self.tgt_sr = self.cpt["config"][-1]',
        "speaker_count_line": 176,
        "speaker_count_fragment":
            'self.cpt["config"][-3] = self.cpt["weight"]["emb_g.weight"]'
            ".shape[0]",
        "v2_synthesizer_line": 183,
        "v2_synthesizer_fragment": '("v2", 1): SynthesizerTrnMs768NSFsid,',
        "speaker_info_line": 202,
        "speaker_info_fragment":
            "speaker_info = normalized_speaker_info(self.cpt, n_spk)",
        "speaker_info_field": "speaker_info",
    },
    "hubert": {
        "path": "research/voice-conversion-eval-20261101/repos/rvc/infer/"
                "hubert.py",
        "sha256":
            "bbfba54d1d83eae3fb634b2909f8f6bf41e6ffe436200ec246867c5c93ebba26",
        "model_path_line": 22,
        "model_path_fragment":
            'HUBERT_MODEL_PATH = (PROJECT_ROOT / "assets" / "hubert_base")'
            ".resolve()",
        "version_check_line": 75,
        "version_check_fragment": 'if version not in {"v1", "v2"}:',
        "v2_return_fragment": "last_hidden_state",
    },
    "rmvpe": {
        "path": "research/voice-conversion-eval-20261101/repos/rvc/infer/"
                "rmvpe.py",
        "sha256":
            "074171aec63e4b68f04d8691c62af50a1d99b9bc6dc56c4d6749fad4ba64853a",
        "constructor_line": 510,
        "constructor_fragment": "is_half, 128, 16000, 1024, 160, None, 30, 8000",
    },
    "config": {
        "path": "research/voice-conversion-eval-20261101/repos/rvc/configs/"
                "config.py",
        "sha256":
            "f304463184b55898aa256fadeafd50d640ed0f880dbae6f89ad54db358240043",
        "cpu_x_pad_line": 261,
        "cpu_x_pad_fragment": "x_pad = 1",
        "cpu_x_query_line": 262,
        "cpu_x_query_fragment": "x_query = 6",
        "cpu_x_center_line": 263,
        "cpu_x_center_fragment": "x_center = 38",
        "cpu_x_max_line": 264,
        "cpu_x_max_fragment": "x_max = 41",
    },
}

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "source_code_snapshot",
        "present": True,
        "verified": True,
        "blocked": False,
        "revision": SOURCE_REVISION,
        "sha256": None,
        "requirement": (
            "Exact RVC source at a 40-hex revision with its MIT license text "
            "and per-file SHA-256 pins, including the v2 synthesizer, HuBERT "
            "and RMVPE loaders, F0 path, pipeline geometry and CPU config."),
    },
    {
        "id": "ART-02",
        "kind": "checkpoint_snapshot",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "The exact p226 RVC v2 checkpoint `Mp226rmvpe.pth` with a 40-hex "
            "model revision, byte count, SHA-256, declared version v2, "
            "f0=rmvpe, target rate 40 kHz, 109 speakers and reviewed terms."),
    },
    {
        "id": "ART-03",
        "kind": "base_asset_snapshots",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "The ContentVec/HuBERT base `assets/hubert_base/pytorch_model.bin` "
            "with its config and preprocessor config, and the RMVPE base "
            "`rmvpe.pt`, each with byte count, SHA-256, revision and reviewed "
            "weight terms."),
    },
    {
        "id": "ART-04",
        "kind": "pinned_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "A reproducible isolated runtime with Python 3.12, torch 2.4.1, "
            "torchaudio 2.4.1, numpy 1.26.x, soundfile, librosa, "
            "transformers 4.49.x and optional faiss-cpu >= 1.13.0, recorded "
            "thread counts, a lock/install digest and a fail-closed offline "
            "load path."),
    },
    {
        "id": "ART-05",
        "kind": "verified_speaker_map",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "A reviewed 109-entry speaker map. The historical checkpoint has "
            "no speaker_info metadata and `speaker_id=1 -> p226` is explicitly "
            "unverified."),
    },
    {
        "id": "ART-06",
        "kind": "rights_and_voice_cohort",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "Reviewed checkpoint/base-asset/dataset terms, source-speaker "
            "consent, target-voice consent, reference availability, output-use "
            "terms, a rights-cleared frozen cohort with manual transcripts and "
            "the agreed Voice quality/timing/listening protocol."),
    },
    {
        "id": "ART-07",
        "kind": "reproduced_reference_outcome_bundle",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "A caller-supplied-asset reproduction on the pinned runtime: exact "
            "input/target references, deterministic settings, output bytes, "
            "separate content, identity, naturalness, alignment, "
            "first-output/tail, peak/nonfinite and resource results, and a "
            "declared Voice comparison."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-01",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-01"],
        "statement": (
            "The MIT LICENSE covers the present RVC source revision only. The "
            "exact upstream archive/tree provenance and the checkpoint "
            "model-card terms are not reviewed. Source presence is not a "
            "weight, base-asset, dataset or voice grant."),
        "required_action": (
            "Supply complete source/archive provenance and the reviewed "
            "checkpoint and base-asset terms bundle with notice references."),
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-02",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-02", "RG-06"],
        "statement": (
            "The exact p226 checkpoint is absent from every fixed probe. The "
            "historical runner names "
            "models/rvc-vctk/M/p226/rmvpe/Mp226rmvpe.pth; the whole models "
            "tree is gone and no local or Hugging Face cache copy exists. "
            "Nothing was downloaded or reconstructed."),
        "required_action": (
            "Supply the immutable `Mp226rmvpe.pth` snapshot with a 40-hex "
            "model revision, byte count, SHA-256 and reviewed weight terms."),
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-03",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-02"],
        "statement": (
            "The HuBERT base weight and the RMVPE base weight are absent. "
            "`assets/hubert_base` contains only config JSON files and "
            "`assets/rmvpe` is empty. No ContentVec or RMVPE bytes are "
            "staged."),
        "required_action": (
            "Supply `pytorch_model.bin`, `rmvpe.pt` and their configs with "
            "byte counts, SHA-256, revisions and reviewed terms."),
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-04",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-03"],
        "statement": (
            "The PyTorch runtime is absent: the current interpreter has no "
            "torch, torchaudio, numpy, soundfile, librosa, transformers, faiss "
            "or parselmouth module, and the historical venvs are gone."),
        "required_action": (
            "Stage a locked Python 3.12 runtime with the pinned torch 2.4.1 / "
            "torchaudio 2.4.1 main stack, install digest, recorded threads and "
            "an offline import/load path."),
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-02", "RG-06"],
        "statement": (
            "The historical checkpoint has 109 speaker embeddings but no "
            "speaker_info map. `speaker_id=1` was presumed to be p226 from the "
            "folder name and VCTK ordering; that mapping is unverified, so "
            "target identity is not attributable."),
        "required_action": (
            "Supply a reviewed 109-entry speaker map with provenance and "
            "select the verified p226 index."),
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-04", "RG-05"],
        "statement": (
            "No checkpoint/base-asset/dataset terms review and no source-"
            "speaker or target-voice consent, reference-availability, output-"
            "use or cohort record exists. The available p360 reference is a "
            "different target with no rights record. The MIT source license "
            "clears none of these."),
        "required_action": (
            "Stage the reviewed terms bundle, signed consents, a p226 "
            "reference with availability, output-use terms and a frozen "
            "rights-cleared cohort."),
    },
    {
        "id": "BLK-07",
        "artifact_id": "ART-07",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-05", "RG-07", "RG-08"],
        "statement": (
            "No caller-supplied-asset reproduction, output, content, identity, "
            "naturalness, alignment, first-output/tail, peak/nonfinite, "
            "device-timing, resource, listening or benchmark result exists. "
            "No provider/adapter intake is proposed."),
        "required_action": (
            "Reproduce the exact checkpoint/assets/runtime and record separate "
            "Voice outcomes and timing on the target, then open a separate "
            "versioned OFF-default provider intake with exact-head review."),
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_archive_and_license_provenance",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "The RVC fork revision and MIT license are pinned, but the exact "
            "upstream archive/tree provenance and the checkpoint/base-asset "
            "model-card terms are not reviewed."),
        "reopen_condition": (
            "Both source archives, 40-hex revisions, tree digests and complete "
            "license/notice/checkpoint/base-asset terms are supplied and "
            "reviewed."),
    },
    {
        "id": "RG-02",
        "title": "checkpoint_base_assets_and_speaker_map",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "The p226 checkpoint, the HuBERT and RMVPE base weights and the "
            "verified 109-entry speaker map are absent; only names and "
            "configs survive."),
        "reopen_condition": (
            "Immutable checkpoint/base-asset bytes, digests, metadata and a "
            "verified speaker map are staged and reviewed."),
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_and_offline_load",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "No torch, torchaudio, numpy, soundfile, librosa, transformers, "
            "faiss or parselmouth runtime is present; no install digest or "
            "offline load path exists."),
        "reopen_condition": (
            "A locked runtime with install digest loads the pinned checkpoint "
            "and base assets offline with recorded threads and deterministic "
            "settings."),
    },
    {
        "id": "RG-04",
        "title": "reference_availability_and_output_use",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "No source-speaker consent, p226 target-voice consent, reference "
            "availability or output-use record exists. The staged p360 "
            "reference is the wrong target and has no rights record."),
        "reopen_condition": (
            "Signed source/target consents, a rights-cleared p226 reference "
            "with availability and explicit output-use terms are staged."),
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_frozen_cohort",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "No frozen cohort, manual transcripts, language/speaker groups, "
            "target-identity control or alternate-target control exists."),
        "reopen_condition": (
            "A frozen rights-cleared cohort with manual transcripts, groups "
            "and target/alternate-target controls is supplied and reviewed."),
    },
    {
        "id": "RG-06",
        "title": "voice_content_identity_and_naturalness",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "No reproduced content, identity/similarity or naturalness result "
            "exists. The historical single-utterance Whisper WER proxy is not "
            "a manual transcript or perceptual identity rating."),
        "reopen_condition": (
            "Pinned content, identity and naturalness scorers with an approved "
            "blinded listening protocol produce separate results on the "
            "rights-cleared cohort."),
    },
    {
        "id": "RG-07",
        "title": "alignment_timing_peaks_and_resources",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "No alignment, first-output/tail, peak/nonfinite, device-timing, "
            "CPU/memory or benchmark result exists. The historical RTF is "
            "whole-file CPU conversion only."),
        "reopen_condition": (
            "Paced target-device runs record alignment, first-output/tail, "
            "peaks, nonfinite counts, deadline margin and resources."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "No provider, descriptor, registry, installed-v0, ABI, shared "
            "build, CI or default change is made or proposed by this package."),
        "reopen_condition": (
            "A separate versioned intake records opt-in OFF-default "
            "registration, a public-surface decision and independent exact-"
            "head review."),
    },
)

VOICE_PROFILE_ROWS = (
    {
        "id": "V-01",
        "requirement": (
            "Freeze permitted input and target references, task and "
            "language/speaker groups."),
        "status": "blocked",
        "evidence": (
            "One unconsented LJ Speech clip is pinned as historical input; the "
            "target is p226 via an unverified speaker_id=1 mapping and no p226 "
            "reference, language group or frozen condition is staged."),
    },
    {
        "id": "V-02",
        "requirement": "Preserve text and semantic content.",
        "status": "blocked",
        "evidence": (
            "The historical one-utterance Whisper Tiny WER of 0.0 is a proxy, "
            "not a manual transcript or semantic-content result, and it was "
            "not rerun here."),
    },
    {
        "id": "V-03",
        "requirement": "Measure identity/similarity as a separate outcome.",
        "status": "blocked",
        "evidence": (
            "No target-voice similarity metric or scored output exists, and "
            "the p226 speaker mapping itself is unverified."),
    },
    {
        "id": "V-04",
        "requirement": "Measure naturalness as a separate outcome.",
        "status": "blocked",
        "evidence": "No naturalness rating or blinded listening was run.",
    },
    {
        "id": "V-05",
        "requirement": "Record alignment.",
        "status": "blocked",
        "evidence": (
            "No word/phoneme, onset, F0 or source-content alignment exists; "
            "the historical output was not aligned or rerun."),
    },
    {
        "id": "V-06",
        "requirement": "Record first-output and tail timing.",
        "status": "blocked",
        "evidence": (
            "Only whole-file CPU conversion timing exists; first-output, tail, "
            "streaming and device pacing are absent."),
    },
    {
        "id": "V-07",
        "requirement": "Record the exact target condition.",
        "status": "blocked",
        "evidence": (
            "The target condition is the presumed p226 speaker_id=1 path; the "
            "speaker map, checkpoint bytes and target consent are absent."),
    },
    {
        "id": "V-08",
        "requirement": (
            "Keep consent, reference availability and output use as "
            "independent gates."),
        "status": "blocked",
        "evidence": (
            "No source-speaker consent, target-voice consent, reference-"
            "availability or output-use record exists; the MIT source license "
            "clears none of them."),
    },
)

QUALITY_OUTCOME_ROWS = (
    {
        "id": "QO-01",
        "outcome": "content_preservation",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No manual transcript, semantic adjudication or reproduced "
            "content metric exists."),
    },
    {
        "id": "QO-02",
        "outcome": "identity_similarity",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No target-voice similarity score, independent encoder or human "
            "identity rating exists."),
    },
    {
        "id": "QO-03",
        "outcome": "naturalness",
        "status": "blocked",
        "value": None,
        "evidence": "No naturalness score or independent listening exists.",
    },
)

TIMING_ROWS = (
    {
        "id": "TM-01",
        "metric": "alignment_samples",
        "status": "blocked",
        "value": None,
        "evidence": "No aligned output exists.",
    },
    {
        "id": "TM-02",
        "metric": "first_output_and_tail_ms",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No chunk/segment first-output or tail measurement exists; the "
            "historical control is whole-file."),
    },
    {
        "id": "TM-03",
        "metric": "device_timing_and_resources",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No target-device paced run, deadline margin, CPU, memory, RSS or "
            "nonfinite/peak observation exists."),
    },
)

HISTORICAL_EXECUTION = {
    "id": "HE-1",
    "candidate": (
        "RVC v2 multi-speaker VCTK checkpoint "
        "(Nekochu/RVC-VCTK_Voice-sample, p226 path)"),
    "source": "research/voice-conversion-eval-20261101/README.md",
    "crosswalk_path": (
        "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/"
        "REPORT.md"),
    "runner_path": (
        "research/voice-conversion-eval-20261101/scripts/"
        "run_rvc_vctk_eval.py"),
    "metrics_path": (
        "research/voice-conversion-eval-20261101/results/rvc/metrics.json"),
    "asr_path": (
        "research/voice-conversion-eval-20261101/results/rvc/asr.json"),
    "output_path": (
        "research/voice-conversion-eval-20261101/results/rvc/"
        "source_to_p226.wav"),
    "source_audio_path": SOURCE_AUDIO_PATH,
    "source_audio_sha256": SOURCE_AUDIO_SHA256,
    "output_sha256": OUTPUT_SHA256,
    "output_byte_count": OUTPUT_BYTES,
    "output_sample_rate_hz": OUTPUT_SAMPLE_RATE_HZ,
    "output_duration_seconds_decimal": OUTPUT_DURATION_SECONDS,
    "checkpoint_path_historical": (
        "research/voice-conversion-eval-20261101/models/rvc-vctk/M/p226/"
        "rmvpe/Mp226rmvpe.pth"),
    "checkpoint_present": False,
    "hubert_base_present": False,
    "rmvpe_base_present": False,
    "mode": (
        "official RVC PyTorch VC pipeline, CPU, 4 threads, file input, RMVPE "
        "F0, retrieval disabled"),
    "retrieval_enabled": False,
    "index_assigned": False,
    "speaker_id": SELECTED_SPEAKER_ID,
    "speaker_map_verified": False,
    "model_and_hubert_load_seconds_decimal": "0.34603404195513576",
    "conversion_wall_seconds_decimal": "7.748765500029549",
    "file_rtf_decimal": "0.8038138485507831",
    "peak_abs_decimal": "0.497772216796875",
    "clipped_sample_fraction_decimal": "0.0",
    "asr_wer_decimal": "0.0",
    "not_rerun": True,
    "merged_task_evidence": False,
    "used_for_evidence": False,
    "qualifies": False,
    "manual_transcript_present": False,
    "listening_performed": False,
    "device_timing_present": False,
    "identity_similarity_measured": False,
    "naturalness_measured": False,
    "multi_utterance_present": False,
    "limitations": [
        "One file conversion is not a cohort, benchmark, device or release "
        "result.",
        "The checkpoint, both base weights and the runtime are absent, so the "
        "run cannot be reproduced or extended here.",
        "The speaker_id=1 -> p226 mapping is presumed from the path and VCTK "
        "order; the checkpoint has no speaker_info map.",
        "The source/target consent, dataset reference and output-use terms "
        "are not staged; the available p360 reference is a different target.",
        "One Whisper Tiny WER proxy is not a manual transcript, semantic, "
        "identity, naturalness or listening result.",
        "Whole-file CPU conversion time is not first-output/tail or device "
        "timing.",
    ],
}

REQUIRED_RESULTS = {
    "source_present": True,
    "checkpoint_present": False,
    "hubert_base_present": False,
    "rmvpe_base_present": False,
    "runtime_present": False,
    "verified_speaker_map_present": False,
    "reference_result_present": False,
    "quality_result_present": False,
    "identity_similarity_result_present": False,
    "naturalness_result_present": False,
    "alignment_result_present": False,
    "first_output_or_tail_result_present": False,
    "device_timing_result_present": False,
    "listening_result_present": False,
    "benchmark_result_present": False,
    "source_speaker_consent_present": False,
    "target_voice_consent_present": False,
    "no_result_qualifies": True,
    "release_claim": False,
}

NON_CLAIMS = (
    "No RVC, torch, torchaudio, numpy, soundfile, librosa, transformers, faiss "
    "or parselmouth module is imported, loaded, linked, built or executed.",
    "No checkpoint, HuBERT/RMVPE weight, index, waveform, model, inference or "
    "conversion is loaded or produced.",
    "No audio is decoded or played; the historical source and output are "
    "pinned by whole-file SHA-256 and byte count only and are not used as "
    "evidence.",
    "No provider, descriptor, registry, default, installed-v0, public API, "
    "ABI, shared build or CI change is made or proposed.",
    "No real corpus, consent record, checkpoint weight, base asset or runtime "
    "is supplied, downloaded, reconstructed or substituted.",
    "No listening, voice conversion, device timing, benchmark or release "
    "claim is made.",
    "No sibling RVC-MLX realtime, FAISS retrieval, Chatterbox, CosyVoice 2, "
    "OpenVoice or survey result is pooled or reinterpreted as p226 evidence.",
    "The historical single-file conversion is provenance only, not a "
    "qualified p226 result.",
)

PROFILE_PHRASES = (
    "Freeze permitted input and target references, task and language/speaker "
    "groups.",
    "Preserve text and semantic content, identity/similarity and naturalness "
    "as separate outcomes.",
    "Record alignment, first-output/tail timing and the exact target "
    "condition.",
    "Consent, reference availability and output use are independent gates.",
)

# The reproduction manifest is a task-local schema, not an SDK, RVC or Voice
# contract. It admits metadata only and never reads audio or loads weights.
MANIFEST_SCHEMA_ID = "audio-sdk/rvc-v2-vctk-p226-reproducer/0.1"
MANIFEST_FIELDS = (
    "schema_id",
    "experiment_id",
    "candidate",
    "checkpoint",
    "base_assets",
    "runtime",
    "references",
    "outcomes",
    "rights",
)
CANDIDATE_FIELDS = ("repository", "revision", "path", "license_id",
                    "license_path", "license_sha256", "distribution")
CHECKPOINT_FIELDS = ("name", "path", "sha256", "byte_count", "version", "f0",
                     "tgt_sr", "speaker_count", "speaker_info_present",
                     "speaker_map_sha256", "speaker_map_verified",
                     "terms_sha256")
ASSET_FIELDS = ("name", "path", "sha256", "byte_count", "terms_sha256")
BASE_ASSET_FIELDS = ("hubert_model", "hubert_config", "rmvpe_model")
RUNTIME_FIELDS = ("python_version", "torch_version", "torchaudio_version",
                  "numpy_version", "soundfile_version",
                  "transformers_version", "librosa_version", "faiss_version",
                  "device", "threads", "omp_threads",
                  "deterministic_algorithms", "offline_load")
REFERENCE_FIELDS = ("source_audio_path", "source_audio_sha256",
                    "source_audio_byte_count", "source_sample_rate_hz",
                    "source_duration_seconds_decimal", "target_speaker",
                    "target_reference_path", "target_reference_sha256",
                    "target_reference_available", "source_consent",
                    "target_consent")
OUTCOME_FIELDS = ("content_wer_decimal", "identity_cosine_decimal",
                  "naturalness_mos_decimal", "alignment_samples",
                  "first_output_ms", "tail_ms", "peak_abs_decimal",
                  "clipped_fraction_decimal", "nonfinite_count",
                  "listening_panel_size", "claims_qualified")
RIGHTS_FIELDS = ("checkpoint_terms", "base_asset_terms", "dataset_reference",
                 "output_use", "review_id", "cohort_id")

SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PYTHON_VERSION = re.compile(r"^3\.12\.[0-9]+$")
TORCH_VERSION = re.compile(r"^2\.4\.1$")
NUMPY_VERSION = re.compile(r"^1\.26\.[0-9]+$")
TRANSFORMERS_VERSION = re.compile(r"^4\.49\.[0-9]+$")
LIBROSA_VERSION = re.compile(r"^0\.10\.[0-9]+$")
FAISS_VERSION = re.compile(r"^1\.([0-9]{1,2})\.([0-9]{1,2})$")
MAX_CHECKPOINT_BYTES = 8 * 1024 * 1024 * 1024
MAX_ASSET_BYTES = 8 * 1024 * 1024 * 1024
MAX_OUTPUT_BYTES = 8 * 1024 * 1024 * 1024
MAX_THREADS = 64
MAX_TEXT_LENGTH = 200
ADMISSION_CASE_COUNT = 100


# --------------------------------------------------------------------------
# Strict JSON and digests
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


# --------------------------------------------------------------------------
# Pins, board identity and absence probes
# --------------------------------------------------------------------------
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


def linked_rows_digest(rows: tuple[dict, ...] = LINKED_ROWS) -> str:
    return object_digest([{field: row.get(field) for field in BOARD_ROW_FIELDS}
                          for row in rows])


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


def observed_incomplete_paths(audio_root: Path,
                              rows: tuple[dict, ...] = OBSERVED_INCOMPLETE_PATHS
                              ) -> list[dict]:
    result: list[dict] = []
    for row in rows:
        path = Path(audio_root) / row["path"]
        entries = sorted(child.name for child in path.iterdir()) \
            if path.is_dir() else []
        if row["path"].endswith("/assets/rmvpe") and entries:
            raise ValueError("artifact_present_reopen_required:" + row["path"])
        if row["path"].endswith("/assets/hubert_base") and (
                set(entries) - {"config.json", "preprocessor_config.json"}):
            raise ValueError("artifact_present_reopen_required:" + row["path"])
        result.append(dict(row, entry_count=len(entries), entries=entries))
    return result


def observed_unusable_references(audio_root: Path,
                                 rows: tuple[dict, ...] =
                                 OBSERVED_UNUSABLE_REFERENCES) -> list[dict]:
    result: list[dict] = []
    for row in rows:
        path = Path(audio_root) / row["path"]
        if not path.is_file():
            raise ValueError("unusable_reference_missing:" + row["path"])
        actual = sha256_file(path)
        if actual != row["sha256"] or path.stat().st_size != row["byte_count"]:
            raise ValueError("unusable_reference_drift:" + row["path"])
        result.append(dict(row, present=True, verified=True,
                           eligible_for_target=False))
    return result


def runtime_probe() -> dict:
    """Report runtime module presence without importing any module."""
    modules = {name: importlib.util.find_spec(name) is not None
               for name in RUNTIME_PROBE_MODULES}
    all_absent = not any(modules.values())
    return dict(RUNTIME_PROBE, modules=modules,
                all_runtime_modules_absent=all_absent)


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
        "audio_decoded": False,
        "model_executed": False,
        "all_probes_absent": all(not row["present"] for row in all_rows),
    }


# --------------------------------------------------------------------------
# Declared pipeline geometry (exact integer arithmetic; no execution)
# --------------------------------------------------------------------------
def pipeline_geometry() -> dict:
    """Derive the declared pipeline geometry from pinned source constants.

    This is bookkeeping over declared integers, not a measured result. The
    HuBERT frame count is deliberately not asserted because it depends on the
    runtime convolution/feature-extractor path; only the declaration-level
    `p_len = samples // 160` and the source/output durations are exact.
    """
    source_samples = INPUT_SAMPLE_RATE_HZ * 9655 // 1000
    output_samples = OUTPUT_SAMPLE_RATE_HZ * 964 // 100
    content_frames = source_samples // WINDOW_SAMPLES
    result = {
        "input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
        "window_samples": WINDOW_SAMPLES,
        "window_ms_decimal": "10.0",
        "source_duration_seconds_decimal": SOURCE_DURATION_SECONDS,
        "declared_source_samples_16k": source_samples,
        "declared_source_frames_floor": content_frames,
        "declared_source_remainder_samples": source_samples - content_frames
        * WINDOW_SAMPLES,
        "rmvpe_hop_samples": RMVPE_HOP_SAMPLES,
        "rmvpe_frame_rate_hz": INPUT_SAMPLE_RATE_HZ // RMVPE_HOP_SAMPLES,
        "feature_upsample_factor": 2,
        "hubert_hidden_size": HUBERT_HIDDEN_SIZE,
        "output_sample_rate_hz": OUTPUT_SAMPLE_RATE_HZ,
        "output_duration_seconds_decimal": OUTPUT_DURATION_SECONDS,
        "declared_output_samples_40k": output_samples,
        "declared_output_frames": output_samples // WINDOW_SAMPLES,
        "upsample_ratio_decimal": "2.5",
        "cpu_x_pad": CPU_X_PAD,
        "cpu_x_query": CPU_X_QUERY,
        "cpu_x_center": CPU_X_CENTER,
        "cpu_x_max": CPU_X_MAX,
        "pad_samples_16k": INPUT_SAMPLE_RATE_HZ * CPU_X_PAD,
        "query_samples_16k": INPUT_SAMPLE_RATE_HZ * CPU_X_QUERY,
        "center_samples_16k": INPUT_SAMPLE_RATE_HZ * CPU_X_CENTER,
        "max_samples_16k": INPUT_SAMPLE_RATE_HZ * CPU_X_MAX,
        "pad_samples_40k": OUTPUT_SAMPLE_RATE_HZ * CPU_X_PAD,
        "speaker_count": SPEAKER_COUNT,
        "selected_speaker_id": SELECTED_SPEAKER_ID,
        "duration_basis": "rounded_declared_decimal_not_decoded",
        "exact_decoded_sample_counts_asserted": False,
        "declared_shape_only": True,
        "measured": False,
        "model_executed": False,
        "audio_decoded": False,
    }
    if source_samples != 154480 or output_samples != 385600:
        raise ValueError("geometry_duration_mismatch")
    if output_samples // WINDOW_SAMPLES != 2410:
        raise ValueError("geometry_frame_mismatch")
    if OUTPUT_SAMPLE_RATE_HZ * 2 != INPUT_SAMPLE_RATE_HZ * 5:
        raise ValueError("geometry_rate_ratio_mismatch")
    return result


# --------------------------------------------------------------------------
# Asset/reproduction precondition model (deterministic; no runtime)
# --------------------------------------------------------------------------
def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return (isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value)))


def _nonfinite_path(value: Any, path: str = "") -> str | None:
    if isinstance(value, float) and not math.isfinite(value):
        return path or "<root>"
    if isinstance(value, dict):
        for key in sorted(value):
            found = _nonfinite_path(value[key],
                                    (path + "." + str(key)).lstrip("."))
            if found:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = _nonfinite_path(item, f"{path}[{index}]")
            if found:
                return found
    return None


def _positive_decimal(value: Any, allow_zero: bool = False) -> bool:
    if not isinstance(value, str) or not value or len(value) > 64:
        return False
    if not re.match(r"^[0-9]+(\.[0-9]+)?$", value):
        return False
    parsed = float(value)
    if not math.isfinite(parsed):
        return False
    return parsed >= 0 if allow_zero else parsed > 0


def _bounded_decimal(value: Any, minimum: float, maximum: float) -> bool:
    if not isinstance(value, str) or not value or len(value) > 64:
        return False
    if not re.match(r"^-?[0-9]+(\.[0-9]+)?$", value) or value == "-0":
        return False
    parsed = float(value)
    return math.isfinite(parsed) and minimum <= parsed <= maximum


def _path_is_canonical(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value:
        return False
    if not os.path.isabs(value):
        return False
    if ".." in Path(value).parts or "~" in value:
        return False
    return os.path.normpath(value) == value


def _exact_object(value: Any, fields: tuple[str, ...]) -> str:
    if not isinstance(value, dict):
        return "invalid_object"
    if set(value) != set(fields):
        return ("missing_field" if set(fields) - set(value) else "unknown_field")
    return ""


def _sha(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX64.match(value))


def _text(value: Any, limit: int = MAX_TEXT_LENGTH) -> bool:
    return (isinstance(value, str) and bool(value.strip())
            and len(value) <= limit
            and not any(ord(char) < 32 for char in value))


def _slug(value: Any) -> bool:
    return isinstance(value, str) and bool(SLUG.match(value))


def evaluate_asset_contract(
    *,
    version: str,
    f0: int,
    tgt_sr: int,
    hubert_hidden_size: int,
    speaker_count: int,
    speaker_id: int,
    speaker_info_present: bool,
    speaker_map_verified: bool,
    hubert_model_present: bool,
    rmvpe_model_present: bool,
    terms_reviewed: bool,
) -> dict:
    """Classify the declared model/asset preconditions without loading anything.

    This models the pinned source contract: RVC v2, f0 synthesizer, 40 kHz
    target, 768-D HuBERT features, 109 speaker embeddings with no embedded map,
    both base weights, and reviewed terms. Acceptance is structural only and
    never qualifies a result.
    """
    base = {"qualifies": False, "state_unchanged": True,
            "model_loaded": False, "weights_loaded": False,
            "runtime_invoked": False, "audio_decoded": False}
    if version != FEATURE_VERSION:
        return dict(base, accepted=False, code="invalid_version")
    if not _is_int(f0) or f0 != 1:
        return dict(base, accepted=False, code="invalid_f0")
    if not _is_int(tgt_sr) or tgt_sr != OUTPUT_SAMPLE_RATE_HZ:
        return dict(base, accepted=False, code="invalid_target_rate")
    if not _is_int(hubert_hidden_size) \
            or hubert_hidden_size != HUBERT_HIDDEN_SIZE:
        return dict(base, accepted=False, code="invalid_hubert_dimension")
    if not _is_int(speaker_count) or speaker_count != SPEAKER_COUNT:
        return dict(base, accepted=False, code="invalid_speaker_count")
    if not _is_int(speaker_id) or not 0 <= speaker_id < SPEAKER_COUNT:
        return dict(base, accepted=False, code="speaker_id_out_of_range")
    if speaker_info_present is not False:
        return dict(base, accepted=False, code="unexpected_speaker_info")
    if speaker_map_verified is not True:
        return dict(base, accepted=False, code="unverified_speaker_map")
    if hubert_model_present is not True:
        return dict(base, accepted=False, code="missing_hubert_model")
    if rmvpe_model_present is not True:
        return dict(base, accepted=False, code="missing_rmvpe_model")
    if terms_reviewed is not True:
        return dict(base, accepted=False, code="unreviewed_terms")
    return dict(base, accepted=True,
                code="structurally_admissible_for_reproducer",
                speaker_count=SPEAKER_COUNT, speaker_id=speaker_id,
                target_rate_hz=OUTPUT_SAMPLE_RATE_HZ,
                hubert_hidden_size=HUBERT_HIDDEN_SIZE)


# --------------------------------------------------------------------------
# Reproduction admission validator (task-local; never a runtime boundary)
# --------------------------------------------------------------------------
def _reject(code: str, field: str = "") -> dict:
    return {"accepted": False, "code": code, "field": field,
            "checks": 0, "state_unchanged": True}


def _accept(checks: int) -> dict:
    return {"accepted": True, "code": "ok", "field": "", "checks": checks,
            "state_unchanged": True}


def _validate_asset(value: object, field: str) -> str:
    code = _exact_object(value, ASSET_FIELDS)
    if code:
        return field + ":" + code
    asset = value  # type: ignore[assignment]
    if not _text(asset["name"], 120):
        return field + ":invalid_name"
    if not _path_is_canonical(asset["path"]):
        return field + ":invalid_path"
    if not _sha(asset["sha256"]):
        return field + ":invalid_sha"
    if not _is_int(asset["byte_count"]) \
            or not 1 <= asset["byte_count"] <= MAX_ASSET_BYTES:
        return field + ":invalid_bytes"
    if not _sha(asset["terms_sha256"]):
        return field + ":invalid_terms"
    return ""


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    """Fail-closed reproduction admission. No audio is read and no weight is
    loaded."""
    checks = 0
    nonfinite = _nonfinite_path(document)
    if nonfinite:
        return _reject("nonfinite_value", nonfinite)
    if not isinstance(document, dict):
        return _reject("manifest_not_object")

    if set(document) != set(MANIFEST_FIELDS):
        missing = sorted(set(MANIFEST_FIELDS) - set(document))
        extra = sorted(set(document) - set(MANIFEST_FIELDS))
        return _reject("missing_field" if missing else "unknown_field",
                       missing[0] if missing else extra[0])
    checks += 1

    if document["schema_id"] != MANIFEST_SCHEMA_ID:
        return _reject("invalid_schema", "schema_id")
    if not _slug(document["experiment_id"]):
        return _reject("invalid_value", "experiment_id")
    checks += 2

    candidate = document["candidate"]
    code = _exact_object(candidate, CANDIDATE_FIELDS)
    if code:
        return _reject(code, "candidate")
    if candidate["repository"] != SOURCE_REPOSITORY:
        return _reject("invalid_value", "candidate.repository")
    if candidate["distribution"] != SOURCE_DISTRIBUTION:
        return _reject("invalid_value", "candidate.distribution")
    if not isinstance(candidate["revision"], str) \
            or not HEX40.match(candidate["revision"]) \
            or candidate["revision"] != SOURCE_REVISION:
        return _reject("invalid_value", "candidate.revision")
    if not _path_is_canonical(candidate["path"]):
        return _reject("invalid_path", "candidate.path")
    if candidate["license_id"] != SOURCE_LICENSE:
        return _reject("invalid_value", "candidate.license_id")
    if not _path_is_canonical(candidate["license_path"]):
        return _reject("invalid_path", "candidate.license_path")
    if not _sha(candidate["license_sha256"]):
        return _reject("invalid_value", "candidate.license_sha256")
    if probe_paths:
        for field in ("path", "license_path"):
            if not Path(candidate[field]).is_file():
                return _reject("probe_missing", "candidate." + field)
    checks += 7

    checkpoint = document["checkpoint"]
    code = _exact_object(checkpoint, CHECKPOINT_FIELDS)
    if code:
        return _reject(code, "checkpoint")
    if checkpoint["name"] != CHECKPOINT_NAME:
        return _reject("invalid_value", "checkpoint.name")
    if not _path_is_canonical(checkpoint["path"]):
        return _reject("invalid_path", "checkpoint.path")
    if not _sha(checkpoint["sha256"]):
        return _reject("invalid_value", "checkpoint.sha256")
    if not _is_int(checkpoint["byte_count"]) \
            or not 1 <= checkpoint["byte_count"] <= MAX_CHECKPOINT_BYTES:
        return _reject("invalid_value", "checkpoint.byte_count")
    if checkpoint["version"] != FEATURE_VERSION:
        return _reject("invalid_value", "checkpoint.version")
    if not _is_int(checkpoint["f0"]) or checkpoint["f0"] != 1:
        return _reject("invalid_value", "checkpoint.f0")
    if checkpoint["tgt_sr"] != OUTPUT_SAMPLE_RATE_HZ:
        return _reject("invalid_value", "checkpoint.tgt_sr")
    if checkpoint["speaker_count"] != SPEAKER_COUNT:
        return _reject("invalid_value", "checkpoint.speaker_count")
    if checkpoint["speaker_info_present"] is not False:
        return _reject("invalid_value", "checkpoint.speaker_info_present")
    if not _sha(checkpoint["speaker_map_sha256"]):
        return _reject("invalid_value", "checkpoint.speaker_map_sha256")
    if checkpoint["speaker_map_verified"] is not True:
        return _reject("invalid_value", "checkpoint.speaker_map_verified")
    if not _sha(checkpoint["terms_sha256"]):
        return _reject("invalid_value", "checkpoint.terms_sha256")
    if probe_paths and not Path(checkpoint["path"]).is_file():
        return _reject("probe_missing", "checkpoint.path")
    checks += 12

    base_assets = document["base_assets"]
    code = _exact_object(base_assets, BASE_ASSET_FIELDS)
    if code:
        return _reject(code, "base_assets")
    expected_names = {
        "hubert_model": HUBERT_MODEL_NAME,
        "hubert_config": HUBERT_CONFIG_NAME,
        "rmvpe_model": RMVPE_MODEL_NAME,
    }
    for field in BASE_ASSET_FIELDS:
        asset = base_assets[field]
        problem = _validate_asset(asset, "base_assets." + field)
        if problem:
            reason = problem.rsplit(":", 1)[-1]
            code = "invalid_path" if reason == "invalid_path" \
                else "invalid_value"
            return _reject(code, problem)
        if asset["name"] != expected_names[field]:
            return _reject("invalid_value", "base_assets." + field + ".name")
    digests = [base_assets[field]["sha256"] for field in BASE_ASSET_FIELDS]
    if len(set(digests)) != len(digests):
        return _reject("invalid_value", "base_assets.duplicate_digest")
    if probe_paths:
        for field in BASE_ASSET_FIELDS:
            if not Path(base_assets[field]["path"]).is_file():
                return _reject("probe_missing", "base_assets." + field + ".path")
    checks += len(BASE_ASSET_FIELDS) * len(ASSET_FIELDS)

    runtime = document["runtime"]
    code = _exact_object(runtime, RUNTIME_FIELDS)
    if code:
        return _reject(code, "runtime")
    if not isinstance(runtime["python_version"], str) \
            or not PYTHON_VERSION.match(runtime["python_version"]):
        return _reject("invalid_value", "runtime.python_version")
    if runtime["torch_version"] != "2.4.1":
        return _reject("invalid_value", "runtime.torch_version")
    if runtime["torchaudio_version"] != "2.4.1":
        return _reject("invalid_value", "runtime.torchaudio_version")
    if not isinstance(runtime["numpy_version"], str) \
            or not NUMPY_VERSION.match(runtime["numpy_version"]):
        return _reject("invalid_value", "runtime.numpy_version")
    if not _text(runtime["soundfile_version"], 40):
        return _reject("invalid_value", "runtime.soundfile_version")
    if not isinstance(runtime["transformers_version"], str) \
            or not TRANSFORMERS_VERSION.match(runtime["transformers_version"]):
        return _reject("invalid_value", "runtime.transformers_version")
    if not isinstance(runtime["librosa_version"], str) \
            or not LIBROSA_VERSION.match(runtime["librosa_version"]):
        return _reject("invalid_value", "runtime.librosa_version")
    faiss_version = runtime["faiss_version"]
    if faiss_version is not None:
        if not isinstance(faiss_version, str) \
                or not FAISS_VERSION.match(faiss_version):
            return _reject("invalid_value", "runtime.faiss_version")
        parts = FAISS_VERSION.match(faiss_version)
        if (int(parts.group(1)), int(parts.group(2))) < (13, 0):
            return _reject("invalid_value", "runtime.faiss_version")
    if runtime["device"] != "cpu":
        return _reject("invalid_value", "runtime.device")
    for field in ("threads", "omp_threads"):
        if not _is_int(runtime[field]) \
                or not 1 <= runtime[field] <= MAX_THREADS:
            return _reject("invalid_value", "runtime." + field)
    if runtime["deterministic_algorithms"] is not True:
        return _reject("invalid_value", "runtime.deterministic_algorithms")
    if runtime["offline_load"] is not True:
        return _reject("invalid_value", "runtime.offline_load")
    checks += len(RUNTIME_FIELDS)

    references = document["references"]
    code = _exact_object(references, REFERENCE_FIELDS)
    if code:
        return _reject(code, "references")
    if not _path_is_canonical(references["source_audio_path"]):
        return _reject("invalid_path", "references.source_audio_path")
    if references["source_audio_sha256"] != SOURCE_AUDIO_SHA256:
        return _reject("invalid_value", "references.source_audio_sha256")
    if references["source_audio_byte_count"] != SOURCE_AUDIO_BYTES:
        return _reject("invalid_value",
                       "references.source_audio_byte_count")
    if references["source_sample_rate_hz"] != INPUT_SAMPLE_RATE_HZ:
        return _reject("invalid_value", "references.source_sample_rate_hz")
    if references["source_duration_seconds_decimal"] != SOURCE_DURATION_SECONDS:
        return _reject("invalid_value",
                       "references.source_duration_seconds_decimal")
    if references["target_speaker"] != "p226":
        return _reject("invalid_value", "references.target_speaker")
    if not _path_is_canonical(references["target_reference_path"]):
        return _reject("invalid_path", "references.target_reference_path")
    if not _sha(references["target_reference_sha256"]):
        return _reject("invalid_value",
                       "references.target_reference_sha256")
    if references["target_reference_available"] is not True:
        return _reject("invalid_value",
                       "references.target_reference_available")
    for field in ("source_consent", "target_consent"):
        if not _text(references[field]):
            return _reject("invalid_value", "references." + field)
    if probe_paths:
        for field in ("source_audio_path", "target_reference_path"):
            if not Path(references[field]).is_file():
                return _reject("probe_missing", "references." + field)
    checks += len(REFERENCE_FIELDS)

    outcomes = document["outcomes"]
    code = _exact_object(outcomes, OUTCOME_FIELDS)
    if code:
        return _reject(code, "outcomes")
    if not _bounded_decimal(outcomes["content_wer_decimal"], 0.0, 1.0):
        return _reject("invalid_value", "outcomes.content_wer_decimal")
    if not _bounded_decimal(outcomes["identity_cosine_decimal"], -1.0, 1.0):
        return _reject("invalid_value", "outcomes.identity_cosine_decimal")
    if not _bounded_decimal(outcomes["naturalness_mos_decimal"], 1.0, 5.0):
        return _reject("invalid_value", "outcomes.naturalness_mos_decimal")
    if not _is_int(outcomes["alignment_samples"]) \
            or not -96000 <= outcomes["alignment_samples"] <= 96000:
        return _reject("invalid_value", "outcomes.alignment_samples")
    for field in ("first_output_ms", "tail_ms"):
        if not _is_int(outcomes[field]) or not 0 <= outcomes[field] <= 10000:
            return _reject("invalid_value", "outcomes." + field)
    if not _bounded_decimal(outcomes["peak_abs_decimal"], 0.0, 4.0):
        return _reject("invalid_value", "outcomes.peak_abs_decimal")
    if not _bounded_decimal(outcomes["clipped_fraction_decimal"], 0.0, 1.0):
        return _reject("invalid_value", "outcomes.clipped_fraction_decimal")
    if outcomes["nonfinite_count"] != 0:
        return _reject("invalid_value", "outcomes.nonfinite_count")
    if not _is_int(outcomes["listening_panel_size"]) \
            or not 0 <= outcomes["listening_panel_size"] <= 1000:
        return _reject("invalid_value", "outcomes.listening_panel_size")
    if outcomes["claims_qualified"] is not False:
        return _reject("invalid_value", "outcomes.claims_qualified")
    checks += len(OUTCOME_FIELDS)

    rights = document["rights"]
    code = _exact_object(rights, RIGHTS_FIELDS)
    if code:
        return _reject(code, "rights")
    for field in ("checkpoint_terms", "base_asset_terms", "dataset_reference",
                  "output_use"):
        if not _text(rights[field]):
            return _reject("invalid_value", "rights." + field)
    for field in ("review_id", "cohort_id"):
        if not _slug(rights[field]):
            return _reject("invalid_value", "rights." + field)
    checks += len(RIGHTS_FIELDS)

    return _accept(checks)


def _manifest_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "experiment_id": "synthetic-schema-control",
        "candidate": {
            "repository": SOURCE_REPOSITORY,
            "revision": SOURCE_REVISION,
            "path": "/caller/rvc",
            "license_id": "MIT",
            "license_path": "/caller/rvc/LICENSE",
            "license_sha256": "a" * 64,
            "distribution": SOURCE_DISTRIBUTION,
        },
        "checkpoint": {
            "name": CHECKPOINT_NAME,
            "path": "/caller/models/" + CHECKPOINT_NAME,
            "sha256": "b" * 64,
            "byte_count": 1000,
            "version": FEATURE_VERSION,
            "f0": 1,
            "tgt_sr": OUTPUT_SAMPLE_RATE_HZ,
            "speaker_count": SPEAKER_COUNT,
            "speaker_info_present": False,
            "speaker_map_sha256": "c" * 64,
            "speaker_map_verified": True,
            "terms_sha256": "d" * 64,
        },
        "base_assets": {
            "hubert_model": {
                "name": HUBERT_MODEL_NAME,
                "path": "/caller/assets/hubert_base/" + HUBERT_MODEL_NAME,
                "sha256": "e" * 64,
                "byte_count": 1000,
                "terms_sha256": "1" * 64,
            },
            "hubert_config": {
                "name": HUBERT_CONFIG_NAME,
                "path": "/caller/assets/hubert_base/" + HUBERT_CONFIG_NAME,
                "sha256": "f" * 64,
                "byte_count": 1000,
                "terms_sha256": "2" * 64,
            },
            "rmvpe_model": {
                "name": RMVPE_MODEL_NAME,
                "path": "/caller/assets/rmvpe/" + RMVPE_MODEL_NAME,
                "sha256": "3" * 64,
                "byte_count": 1000,
                "terms_sha256": "4" * 64,
            },
        },
        "runtime": {
            "python_version": "3.12.8",
            "torch_version": "2.4.1",
            "torchaudio_version": "2.4.1",
            "numpy_version": "1.26.4",
            "soundfile_version": "0.13.1",
            "transformers_version": "4.49.0",
            "librosa_version": "0.10.2",
            "faiss_version": "1.13.0",
            "device": "cpu",
            "threads": 4,
            "omp_threads": 1,
            "deterministic_algorithms": True,
            "offline_load": True,
        },
        "references": {
            "source_audio_path": "/caller/data/source_ljspeech_lj001-0001.wav",
            "source_audio_sha256": SOURCE_AUDIO_SHA256,
            "source_audio_byte_count": SOURCE_AUDIO_BYTES,
            "source_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
            "source_duration_seconds_decimal": SOURCE_DURATION_SECONDS,
            "target_speaker": "p226",
            "target_reference_path": "/caller/data/p226_reference.wav",
            "target_reference_sha256": "5" * 64,
            "target_reference_available": True,
            "source_consent": "consent-source",
            "target_consent": "consent-target",
        },
        "outcomes": {
            "content_wer_decimal": "0.0",
            "identity_cosine_decimal": "0.5",
            "naturalness_mos_decimal": "3.0",
            "alignment_samples": 0,
            "first_output_ms": 0,
            "tail_ms": 0,
            "peak_abs_decimal": "0.0",
            "clipped_fraction_decimal": "0.0",
            "nonfinite_count": 0,
            "listening_panel_size": 0,
            "claims_qualified": False,
        },
        "rights": {
            "checkpoint_terms": "terms-checkpoint",
            "base_asset_terms": "terms-base-assets",
            "dataset_reference": "dataset-vctk-reference",
            "output_use": "research-only",
            "review_id": "review-a",
            "cohort_id": "cohort-a",
        },
    }


def admission_controls() -> dict:
    """Build the frozen structural control and adverse rejection matrix."""
    control = _manifest_control()
    accepted = validate_manifest(control, probe_paths=False)
    cases: list[dict] = []

    def mutate(case_id: str, function) -> None:
        document = _manifest_control()
        function(document)
        result = validate_manifest(document, probe_paths=False)
        cases.append({
            "id": case_id,
            "status": "rejected" if not result["accepted"] else "accepted",
            "code": result["code"],
            "field": result["field"],
            "qualifies": False,
            "state_unchanged": result["state_unchanged"],
        })

    def set_top(field: str, value: Any):
        def apply(document: dict) -> None:
            document[field] = value
        return apply

    def del_top(field: str):
        def apply(document: dict) -> None:
            del document[field]
        return apply

    def set_nested(path: tuple, value: Any):
        def apply(document: dict) -> None:
            target = document
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = value
        return apply

    def del_nested(path: tuple):
        def apply(document: dict) -> None:
            target = document
            for part in path[:-1]:
                target = target[part]
            del target[path[-1]]
        return apply

    def add_nested(path: tuple, key: str, value: Any):
        def apply(document: dict) -> None:
            target = document
            for part in path:
                target = target[part]
            target[key] = value
        return apply

    mutate("A001-schema-missing", del_top("schema_id"))
    mutate("A002-schema-unknown", set_top("unexpected", 1))
    mutate("A003-schema-value", set_top("schema_id", "wrong/0.1"))
    mutate("A004-experiment-empty", set_top("experiment_id", ""))
    mutate("A005-experiment-upper", set_top("experiment_id", "UPPER"))
    mutate("A006-candidate-object", set_top("candidate", []))
    mutate("A007-candidate-missing", del_nested(("candidate", "repository")))
    mutate("A008-candidate-unknown",
           add_nested(("candidate",), "extra", "x"))
    mutate("A009-repository",
           set_nested(("candidate", "repository"), "other/rvc"))
    mutate("A010-revision-short",
           set_nested(("candidate", "revision"), "81eed5e8"))
    mutate("A011-revision-wrong",
           set_nested(("candidate", "revision"), "a" * 40))
    mutate("A012-candidate-path-relative",
           set_nested(("candidate", "path"), "rvc"))
    mutate("A013-license", set_nested(("candidate", "license_id"), "BSD-3"))
    mutate("A014-license-path",
           set_nested(("candidate", "license_path"), "/caller/../LICENSE"))
    mutate("A015-license-sha",
           set_nested(("candidate", "license_sha256"), "zz"))
    mutate("A016-distribution",
           set_nested(("candidate", "distribution"), "other"))
    mutate("A017-checkpoint-object", set_top("checkpoint", "x"))
    mutate("A018-checkpoint-missing", del_nested(("checkpoint", "name")))
    mutate("A019-checkpoint-unknown",
           add_nested(("checkpoint",), "extra", "x"))
    mutate("A020-checkpoint-name",
           set_nested(("checkpoint", "name"), "other.pth"))
    mutate("A021-checkpoint-path",
           set_nested(("checkpoint", "path"), "/caller/~"))
    mutate("A022-checkpoint-sha",
           set_nested(("checkpoint", "sha256"), "0" * 63))
    mutate("A023-checkpoint-bytes-zero",
           set_nested(("checkpoint", "byte_count"), 0))
    mutate("A024-checkpoint-bytes-bool",
           set_nested(("checkpoint", "byte_count"), True))
    mutate("A025-checkpoint-version",
           set_nested(("checkpoint", "version"), "v1"))
    mutate("A026-checkpoint-f0",
           set_nested(("checkpoint", "f0"), 0))
    mutate("A027-checkpoint-f0-bool",
           set_nested(("checkpoint", "f0"), True))
    mutate("A028-checkpoint-rate",
           set_nested(("checkpoint", "tgt_sr"), 48000))
    mutate("A029-speaker-count",
           set_nested(("checkpoint", "speaker_count"), 108))
    mutate("A030-speaker-count-bool",
           set_nested(("checkpoint", "speaker_count"), True))
    mutate("A031-speaker-info",
           set_nested(("checkpoint", "speaker_info_present"), True))
    mutate("A032-speaker-map-sha",
           set_nested(("checkpoint", "speaker_map_sha256"), "nope"))
    mutate("A033-speaker-map-unverified",
           set_nested(("checkpoint", "speaker_map_verified"), False))
    mutate("A034-terms-sha",
           set_nested(("checkpoint", "terms_sha256"), "nope"))
    mutate("A035-assets-object", set_top("base_assets", []))
    mutate("A036-assets-missing", del_nested(("base_assets", "rmvpe_model")))
    mutate("A037-assets-unknown",
           add_nested(("base_assets",), "extra", {}))
    mutate("A038-asset-object",
           set_nested(("base_assets", "hubert_model"), "x"))
    mutate("A039-asset-missing-field",
           del_nested(("base_assets", "hubert_model", "sha256")))
    mutate("A040-asset-unknown-field",
           add_nested(("base_assets", "hubert_config"), "extra", 1))
    mutate("A041-asset-name",
           set_nested(("base_assets", "hubert_model", "name"), "model.bin"))
    mutate("A042-asset-path",
           set_nested(("base_assets", "rmvpe_model", "path"), "rmvpe.pt"))
    mutate("A043-asset-sha",
           set_nested(("base_assets", "rmvpe_model", "sha256"), "nope"))
    mutate("A044-asset-bytes-zero",
           set_nested(("base_assets", "rmvpe_model", "byte_count"), 0))
    mutate("A045-asset-bytes-bool",
           set_nested(("base_assets", "hubert_config", "byte_count"), True))
    mutate("A046-asset-terms",
           set_nested(("base_assets", "hubert_config", "terms_sha256"), "x"))
    mutate("A047-assets-duplicate",
           set_nested(("base_assets", "rmvpe_model", "sha256"), "e" * 64))
    mutate("A048-runtime-object", set_top("runtime", None))
    mutate("A049-runtime-missing", del_nested(("runtime", "device")))
    mutate("A050-runtime-unknown", add_nested(("runtime",), "extra", 1))
    mutate("A051-python-version",
           set_nested(("runtime", "python_version"), "3.11.5"))
    mutate("A052-torch-version",
           set_nested(("runtime", "torch_version"), "2.15.0"))
    mutate("A053-torchaudio-version",
           set_nested(("runtime", "torchaudio_version"), "2.11.1"))
    mutate("A054-numpy-version",
           set_nested(("runtime", "numpy_version"), "2.0.0"))
    mutate("A055-soundfile-empty",
           set_nested(("runtime", "soundfile_version"), ""))
    mutate("A056-transformers-version",
           set_nested(("runtime", "transformers_version"), "5.0.0"))
    mutate("A057-librosa-version",
           set_nested(("runtime", "librosa_version"), "0.11.0"))
    mutate("A058-faiss-old",
           set_nested(("runtime", "faiss_version"), "1.12.0"))
    mutate("A059-faiss-bad",
           set_nested(("runtime", "faiss_version"), "faiss"))
    mutate("A060-device",
           set_nested(("runtime", "device"), "cuda"))
    mutate("A061-threads-zero",
           set_nested(("runtime", "threads"), 0))
    mutate("A062-threads-over",
           set_nested(("runtime", "threads"), 65))
    mutate("A063-omp-zero",
           set_nested(("runtime", "omp_threads"), 0))
    mutate("A064-deterministic",
           set_nested(("runtime", "deterministic_algorithms"), False))
    mutate("A065-offline-load",
           set_nested(("runtime", "offline_load"), False))
    mutate("A066-references-object", set_top("references", []))
    mutate("A067-references-missing",
           del_nested(("references", "target_consent")))
    mutate("A068-references-unknown",
           add_nested(("references",), "extra", 1))
    mutate("A069-source-path-relative",
           set_nested(("references", "source_audio_path"), "source.wav"))
    mutate("A070-source-sha",
           set_nested(("references", "source_audio_sha256"), "a" * 64))
    mutate("A071-source-bytes",
           set_nested(("references", "source_audio_byte_count"), 1))
    mutate("A072-source-rate",
           set_nested(("references", "source_sample_rate_hz"), 44100))
    mutate("A073-source-duration",
           set_nested(("references", "source_duration_seconds_decimal"),
                      "10.0"))
    mutate("A074-target-speaker",
           set_nested(("references", "target_speaker"), "p360"))
    mutate("A075-target-path",
           set_nested(("references", "target_reference_path"),
                      "p226_reference.wav"))
    mutate("A076-target-sha",
           set_nested(("references", "target_reference_sha256"), "nope"))
    mutate("A077-target-unavailable",
           set_nested(("references", "target_reference_available"), False))
    mutate("A078-source-consent-empty",
           set_nested(("references", "source_consent"), ""))
    mutate("A079-target-consent-empty",
           set_nested(("references", "target_consent"), ""))
    mutate("A080-outcomes-object", set_top("outcomes", "x"))
    mutate("A081-outcomes-missing",
           del_nested(("outcomes", "naturalness_mos_decimal")))
    mutate("A082-outcomes-unknown",
           add_nested(("outcomes",), "extra", 1))
    mutate("A083-content-wer-over",
           set_nested(("outcomes", "content_wer_decimal"), "1.5"))
    mutate("A084-content-wer-text",
           set_nested(("outcomes", "content_wer_decimal"), "nan"))
    mutate("A085-identity-over",
           set_nested(("outcomes", "identity_cosine_decimal"), "1.1"))
    mutate("A086-mos-under",
           set_nested(("outcomes", "naturalness_mos_decimal"), "0.5"))
    mutate("A087-alignment-float",
           set_nested(("outcomes", "alignment_samples"), 1.0))
    mutate("A088-alignment-over",
           set_nested(("outcomes", "alignment_samples"), 96001))
    mutate("A089-first-output-negative",
           set_nested(("outcomes", "first_output_ms"), -1))
    mutate("A090-tail-over",
           set_nested(("outcomes", "tail_ms"), 10001))
    mutate("A091-peak-negative",
           set_nested(("outcomes", "peak_abs_decimal"), "-0.1"))
    mutate("A092-clipped-over",
           set_nested(("outcomes", "clipped_fraction_decimal"), "1.1"))
    mutate("A093-nonfinite-count",
           set_nested(("outcomes", "nonfinite_count"), 1))
    mutate("A094-panel-over",
           set_nested(("outcomes", "listening_panel_size"), 1001))
    mutate("A095-claims-qualified",
           set_nested(("outcomes", "claims_qualified"), True))
    mutate("A096-rights-object", set_top("rights", []))
    mutate("A097-rights-missing",
           del_nested(("rights", "output_use")))
    mutate("A098-rights-unknown", add_nested(("rights",), "extra", 1))
    mutate("A099-rights-cohort",
           set_nested(("rights", "cohort_id"), ""))
    mutate("A100-nonfinite-json",
           set_nested(("outcomes", "naturalness_mos_decimal"), "inf"))

    rejected = sum(1 for case in cases if case["status"] == "rejected")
    return {
        "summary": {
            "case_count": len(cases),
            "rejected_count": rejected,
            "accepted_schema_controls": 1 if accepted["accepted"] else 0,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "runtime_invoked": False,
            "audio_decoded": False,
            "weights_loaded": False,
            "model_executed": False,
            "network_used": False,
        },
        "control": {
            "id": "A000-accepted-schema-control",
            "accepted": accepted["accepted"],
            "code": accepted["code"],
            "checks": accepted["checks"],
            "label": "synthetic_schema_control_not_evidence",
            "qualifies": False,
            "audio_decoded": False,
            "weights_loaded": False,
        },
        "cases": cases,
    }


def admission_contract_block() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "scope": "task_local_reproduction_metadata_only",
        "manifest_fields": list(MANIFEST_FIELDS),
        "candidate_fields": list(CANDIDATE_FIELDS),
        "checkpoint_fields": list(CHECKPOINT_FIELDS),
        "asset_fields": list(ASSET_FIELDS),
        "base_asset_fields": list(BASE_ASSET_FIELDS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "reference_fields": list(REFERENCE_FIELDS),
        "outcome_fields": list(OUTCOME_FIELDS),
        "rights_fields": list(RIGHTS_FIELDS),
        "required_checkpoint_name": CHECKPOINT_NAME,
        "required_hubert_model_name": HUBERT_MODEL_NAME,
        "required_hubert_config_name": HUBERT_CONFIG_NAME,
        "required_rmvpe_model_name": RMVPE_MODEL_NAME,
        "required_feature_version": FEATURE_VERSION,
        "required_f0": 1,
        "required_target_rate_hz": OUTPUT_SAMPLE_RATE_HZ,
        "required_hubert_hidden_size": HUBERT_HIDDEN_SIZE,
        "required_speaker_count": SPEAKER_COUNT,
        "required_source_audio_sha256": SOURCE_AUDIO_SHA256,
        "required_source_audio_byte_count": SOURCE_AUDIO_BYTES,
        "required_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
        "required_duration_seconds_decimal": SOURCE_DURATION_SECONDS,
        "required_target_speaker": "p226",
        "required_torch_version": "2.4.1",
        "required_torchaudio_version": "2.4.1",
        "minimum_faiss_version": "1.13.0",
        "rejections": (
            "unknown/missing field, non-object, duplicate key, nonfinite JSON, "
            "non-canonical path, bad SHA-256, wrong revision/version/rate/"
            "speaker count, unverified or embedded speaker map, duplicate "
            "asset digest, wrong runtime generation, out-of-range outcome, "
            "nonzero nonfinite count, claimed qualification and empty rights "
            "references"),
    }


# --------------------------------------------------------------------------
# Contract/report static blocks
# --------------------------------------------------------------------------
def _public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "model_input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
        "model_native_sample_rate_hz": OUTPUT_SAMPLE_RATE_HZ,
        "preserved": True,
        "provider_created": False,
        "sdk_callback_invoked": False,
    }


def _scope() -> dict:
    return {
        "task_local_only": True,
        "source_present": True,
        "checkpoint_present": False,
        "hubert_base_present": False,
        "rmvpe_base_present": False,
        "runtime_present": False,
        "model_executed": False,
        "weights_loaded": False,
        "audio_decoded": False,
        "voice_conversion": False,
        "reference_output_present": False,
        "listening": False,
        "device_timing": False,
        "benchmark": False,
        "quality_scored": False,
        "identity_similarity_scored": False,
        "naturalness_scored": False,
        "real_corpus": False,
        "network_used": False,
        "download_attempted": False,
        "provider_registration": False,
        "installed_v0_change": False,
        "abi_change": False,
        "shared_build_change": False,
        "ci_change": False,
        "release_claim": False,
    }


def _boundary() -> dict:
    return {
        "task_local_only": True,
        "files_outside_task_directory_written": False,
        "source_present": True,
        "real_weights_or_runtime": False,
        "torch_or_transformers_loaded": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "enabled_by_default": False,
        "processor_exposure": False,
        "installed_v0_behavior_change": False,
        "public_api_abi_change": False,
        "shared_cmakelists_change": False,
        "ci_workflow_change": False,
        "voice_conversion": False,
        "listening": False,
    }


def _disposition() -> dict:
    return {
        "decision": "DEFER",
        "status": "incomplete",
        "incomplete": True,
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "not_qualified": True,
        "registered": False,
        "default_enabled": False,
        "expose_as_processor": False,
        "production_exposure": "DEFER",
        "promotion": "defer",
        "missing_result_qualifies": False,
        "inventory_disposition": "sdk-model",
        "reopen_condition": (
            "Supply the pinned p226 checkpoint, HuBERT and RMVPE base assets, "
            "locked PyTorch runtime, verified 109-entry speaker map, reviewed "
            "terms and consents, a rights-cleared p226 reference and cohort, "
            "and the agreed Voice quality/timing/listening protocol. Then "
            "reproduce the exact reference as a caller-supplied-asset bundle "
            "and review the result at an exact head. Until then this task "
            "stays DEFER."),
    }


def _qualification() -> dict:
    return {
        "status": "not_qualified",
        "not_qualified": True,
        "readiness": "incomplete",
        "real_result_present": False,
        "source_present": True,
        "checkpoint_present": False,
        "hubert_base_present": False,
        "rmvpe_base_present": False,
        "runtime_present": False,
        "verified_speaker_map_present": False,
        "reference_result": False,
        "quality_result": False,
        "identity_similarity_result": False,
        "naturalness_result": False,
        "alignment_result": False,
        "first_output_or_tail_result": False,
        "device_timing_result": False,
        "listening_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "all_release_gates_blocked": True,
    }


def build_contract() -> dict:
    board_path = AUDIO_ROOT / BOARD_TASK_ROW
    projection = board_row_projection(board_path)
    if projection != BOARD_ROW_PROJECTION:
        raise ValueError("board_projection_mismatch")
    admission = admission_controls()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_key": PROFILE,
        "profile_source": (
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md#profiles-by-"
            "task"),
        "profile_phrases": list(PROFILE_PHRASES),
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "exact_scope": (
            "Task-local, proposal-only, incomplete and not-qualified evidence "
            "for RVC v2 VCTK p226: pinned source declarations, fail-closed "
            "absence and runtime probes, exact declared pipeline geometry, a "
            "deterministic asset admission model and a strict admission "
            "schema for a future caller-supplied-asset reproducer. No "
            "checkpoint, base weight, runtime, audio, conversion, listening, "
            "timing or release result."),
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "disposition": _disposition(),
        "qualification": _qualification(),
        "scope": _scope(),
        "boundary": _boundary(),
        "public_v0_geometry": _public_v0_geometry(),
        "source_presence": dict(SOURCE_PRESENCE),
        "source_declarations": {
            key: dict(value) for key, value in SOURCE_DECLARATIONS.items()},
        "pipeline_geometry": pipeline_geometry(),
        "asset_contract": evaluate_asset_contract(
            version=FEATURE_VERSION, f0=1, tgt_sr=OUTPUT_SAMPLE_RATE_HZ,
            hubert_hidden_size=HUBERT_HIDDEN_SIZE, speaker_count=SPEAKER_COUNT,
            speaker_id=SELECTED_SPEAKER_ID, speaker_info_present=False,
            speaker_map_verified=True, hubert_model_present=True,
            rmvpe_model_present=True, terms_reviewed=True),
        "source_revision": SOURCE_REVISION,
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "board_row_fields": list(BOARD_ROW_FIELDS),
        "board_row_projection": projection,
        "board_row_sha256": board_row_digest(projection),
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
        "absence_policy": {
            "fixed_probe_list_only": True,
            "any_present_probe_blocks_shipping": True,
            "recursive_workspace_walk": False,
            "download_attempted": False,
            "network_used": False,
        },
        "absence_probes": list(ABSENCE_PROBES),
        "home_absence_probes": list(HOME_ABSENCE_PROBES),
        "observed_incomplete_paths": list(OBSERVED_INCOMPLETE_PATHS),
        "observed_unusable_references": list(OBSERVED_UNUSABLE_REFERENCES),
        "runtime_probe_modules": list(RUNTIME_PROBE_MODULES),
        "required_artifacts": [dict(row) for row in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(row) for row in EXACT_BLOCKERS],
        "release_gates": [dict(row) for row in RELEASE_GATES],
        "voice_profile_requirements": [dict(row) for row in VOICE_PROFILE_ROWS],
        "quality_outcomes": [dict(row) for row in QUALITY_OUTCOME_ROWS],
        "timing_requirements": [dict(row) for row in TIMING_ROWS],
        "required_results": dict(REQUIRED_RESULTS),
        "historical_execution": dict(HISTORICAL_EXECUTION),
        "non_claims": list(NON_CLAIMS),
        "admission_contract": admission_contract_block(),
        "admission_summary": admission["summary"],
        "admission_control": admission["control"],
    }


CONTRACT_FIELDS = (
    "schema_id", "contract_id", "task", "title", "component", "mode",
    "profile", "profile_key", "profile_source", "profile_phrases",
    "base_commit", "branch", "write_scope", "exact_scope", "decision",
    "status", "proposal_only", "qualification_status", "disposition",
    "qualification", "scope", "boundary", "public_v0_geometry",
    "source_presence", "source_declarations", "pipeline_geometry",
    "asset_contract", "source_revision", "source_pins", "boundary_pins",
    "board_file_pinned", "board_status_is_observation_only",
    "board_row_fields", "board_row_projection", "board_row_sha256",
    "linked_rows", "linked_rows_sha256", "absence_policy", "absence_probes",
    "home_absence_probes", "observed_incomplete_paths",
    "observed_unusable_references", "runtime_probe_modules",
    "required_artifacts", "exact_blockers", "release_gates",
    "voice_profile_requirements", "quality_outcomes", "timing_requirements",
    "required_results", "historical_execution", "non_claims",
    "admission_contract", "admission_summary", "admission_control",
)


def validate_contract(document: dict) -> None:
    if not isinstance(document, dict):
        raise ValueError("contract_not_object")
    if set(document) != set(CONTRACT_FIELDS):
        missing = sorted(set(CONTRACT_FIELDS) - set(document))
        extra = sorted(set(document) - set(CONTRACT_FIELDS))
        raise ValueError("contract_fields:" + ",".join(missing or extra))
    if document["schema_id"] != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema")
    if document["task"] != TASK or document["component"] != COMPONENT_ID:
        raise ValueError("contract_identity")
    if document["decision"] != "DEFER" or document["status"] != "incomplete":
        raise ValueError("contract_decision")
    if document["qualification_status"] != "not_qualified":
        raise ValueError("contract_qualification")
    if document["proposal_only"] is not True:
        raise ValueError("contract_proposal_only")
    if len(document["release_gates"]) != 8:
        raise ValueError("gate_count")
    for index, gate in enumerate(document["release_gates"], start=1):
        if gate.get("id") != f"RG-{index:02d}":
            raise ValueError("gate_id")
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            raise ValueError("gate_not_blocked")
        if gate.get("linked_row") != BOARD_ROW_PROJECTION:
            raise ValueError("gate_linked_row")
    if len(document["required_artifacts"]) != 7:
        raise ValueError("artifact_count")
    if document["required_artifacts"][0].get("present") is not True:
        raise ValueError("source_artifact")
    for artifact in document["required_artifacts"][1:]:
        if artifact.get("present") is not False \
                or artifact.get("blocked") is not True:
            raise ValueError("artifact_not_blocked")
    if len(document["exact_blockers"]) != 7:
        raise ValueError("blocker_count")
    artifact_ids = {row["id"] for row in document["required_artifacts"]}
    gate_ids = {row["id"] for row in document["release_gates"]}
    for blocker in document["exact_blockers"]:
        if blocker.get("status") != "open" \
                or blocker.get("qualifies") is not False:
            raise ValueError("blocker_not_open")
        if blocker.get("artifact_id") not in artifact_ids:
            raise ValueError("blocker_artifact")
        for gate in blocker.get("linked_gates", []):
            if gate not in gate_ids:
                raise ValueError("blocker_gate")
    summary = document["admission_summary"]
    if summary.get("case_count") != ADMISSION_CASE_COUNT \
            or summary.get("rejected_count") != ADMISSION_CASE_COUNT:
        raise ValueError("admission_case_count")
    if summary.get("accepted_schema_controls") != 1:
        raise ValueError("admission_control_count")
    if summary.get("qualifying_results") != 0:
        raise ValueError("admission_qualifying")
    if document["admission_control"].get("qualifies") is not False:
        raise ValueError("admission_control_qualifies")
    if document["historical_execution"].get("qualifies") is not False:
        raise ValueError("historical_qualifies")
    if document["asset_contract"].get("qualifies") is not False:
        raise ValueError("asset_contract_qualifies")
    if document["pipeline_geometry"].get("measured") is not False:
        raise ValueError("geometry_marked_measured")
    if document["board_row_sha256"] != board_row_digest(BOARD_ROW_PROJECTION):
        raise ValueError("board_digest")
    if document["linked_rows_sha256"] != linked_rows_digest():
        raise ValueError("linked_digest")


def build_report() -> dict:
    contract = build_contract()
    validate_contract(contract)
    workspace_rows = absence_probes(AUDIO_ROOT)
    home_rows = home_absence_probes()
    runtime = runtime_probe()
    if runtime["all_runtime_modules_absent"] is not True:
        raise ValueError("runtime_module_present_reopen_required")
    admission = admission_controls()
    for case in admission["cases"]:
        if case["status"] != "rejected":
            raise ValueError("admission_case_not_rejected:" + case["id"])
    if admission["summary"]["rejected_count"] != len(admission["cases"]):
        raise ValueError("admission_summary_mismatch")
    if admission["control"]["accepted"] is not True:
        raise ValueError("admission_control_rejected")
    observed = observed_incomplete_paths(AUDIO_ROOT)
    unusable = observed_unusable_references(AUDIO_ROOT)
    board_path = AUDIO_ROOT / BOARD_TASK_ROW
    projection = board_row_projection(board_path)
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "task_id": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "component_id": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_key": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "exact_scope": contract["exact_scope"],
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "disposition": contract["disposition"],
        "qualification": contract["qualification"],
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "source_presence": contract["source_presence"],
        "source_declarations": contract["source_declarations"],
        "pipeline_geometry": contract["pipeline_geometry"],
        "asset_contract": contract["asset_contract"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "voice_profile": {
            "profile": PROFILE_LABEL,
            "profile_key": PROFILE,
            "rows": contract["voice_profile_requirements"],
        },
        "quality_outcomes": {
            "rows": contract["quality_outcomes"],
            "no_value_inferred": True,
        },
        "timing": {
            "rows": contract["timing_requirements"],
            "no_value_inferred": True,
        },
        "historical_execution": contract["historical_execution"],
        "required_results": contract["required_results"],
        "non_claims": contract["non_claims"],
        "absence_evidence": {
            "summary": absence_summary(workspace_rows, home_rows),
            "workspace_probes": workspace_rows,
            "home_probes": home_rows,
            "observed_incomplete_paths": observed,
            "observed_unusable_references": unusable,
            "policy": contract["absence_policy"],
        },
        "runtime_probe": runtime,
        "source_pins": contract["source_pins"],
        "boundary_pins": contract["boundary_pins"],
        "linked_row_identity": {
            "projection": projection,
            "sha256": board_row_digest(projection),
            "linked_rows": contract["linked_rows"],
            "linked_rows_sha256": contract["linked_rows_sha256"],
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "projection_fields": list(BOARD_ROW_FIELDS),
        },
        "admission": {
            "summary": admission["summary"],
            "control": admission["control"],
            "contract": contract["admission_contract"],
            "cases": admission["cases"],
        },
        "contract_sha256": object_digest(contract),
    }
    _no_floats(report)
    return report


def canonical_report(document: dict | None = None) -> tuple[str, str]:
    report = build_report() if document is None else document
    _no_floats(report)
    text = canonical_text(report)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()

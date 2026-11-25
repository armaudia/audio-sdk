# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-RVC-FAISS-RETRIEVAL.

This module is standard-library only and deterministic. It contains no RVC
source copy, checkpoint weight, FAISS index, FAISS/Torch runtime, waveform
decoder, converted waveform, listening result or model result. It records the
exact external blocker, pins the retrieval call sites that the historical
observation reached, probes a fixed list of workspace and home-cache paths to
evidence the absence of the checkpoint, index and runtime, validates a
caller-supplied retrieval reproducer bundle with a fail-closed admission
boundary, models the pinned retrieval/control branch contract without executing
FAISS, and builds the canonical report.

The RVC checkout is present at an exact revision with an MIT licence. That
source-code presence is pinned, but it is not a checkpoint grant, an index
grant, a runtime, a verified speaker map, a retained crash trace or a
qualification. The checkpoint (`Mp226rmvpe.pth`), the 137 MB
`added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index`, the FAISS/Torch runtime and
the original crash trace are absent. Nothing was downloaded, loaded or
executed. The locally observed retrieval crash is represented as an
unreproduced, unlocalized historical observation; it is not a result.
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

TASK = "SDK-RVC-FAISS-RETRIEVAL"
COMPONENT_ID = "rvc-faiss-retrieval"
TASK_TITLE = "RVC FAISS retrieval"
CONTRACT_ID = "audio-sdk/rvc-faiss-retrieval-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "voice"
PROFILE_LABEL = "Voice"
MODE = "implementation"
BASE_COMMIT = "ab7ce893032ea7771d9d367638e8d09076ff5db3"
BRANCH = "swarm/SDK-RVC-FAISS-RETRIEVAL"
WRITE_SCOPE = "docs/task-evidence/rvc-faiss-retrieval/ only"
TASK_PREFIX = "docs/task-evidence/rvc-faiss-retrieval/"

SOURCE_REVISION = "81eed5e8f68b6bed1789f682fe78cdd324495afc"
SOURCE_REPOSITORY = "RVC-Project/Retrieval-based-Voice-Conversion-WebUI"
SOURCE_DISTRIBUTION = "Retrieval-based-Voice-Conversion-WebUI"
SOURCE_LICENSE = "MIT"

CHECKPOINT_NAME = "Mp226rmvpe.pth"
INDEX_NAME = "added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index"
INDEX_TYPE = "IndexIVFFlat"
INDEX_DIMENSION = 768
INDEX_NLIST = 1161
INDEX_NPROBE = 1
INDEX_SPEAKERS = 109
SEARCH_K = 8
SOURCE_AUDIO_SHA256 = (
    "adc9736d0a02b8efe57128b2c6843605e81ab24027f23f6fc7d05bcd6107753b")
SOURCE_AUDIO_BYTES = 309006

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
    "research/voice-conversion-eval-20261101/repos/rvc/infer/cli.py":
        "8e321cd606bfa1f4756685db897e90df2278e77d3e58869bc83d4735ff7b7387",
    "research/voice-conversion-eval-20261101/repos/rvc/infer/rtrvc.py":
        "c04d2f2d38ed67ca5c1846f4b392befdf0cf7a6172cffe679a81c039dc1642bc",
    "research/voice-conversion-eval-20261101/repos/rvc/train/train_index.py":
        "9377e10716ce2ba63d4fb346fe36792b1543803b01a18a782563f6f47713e5a1",
    "research/voice-conversion-eval-20261101/repos/rvc/"
    "requirments_cpu_py312.txt":
        "902338f1c8ef6c38186a34c19dec95e8df56030863b7a584b703a443127ea541",
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
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
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
        "id": "SDK-RVC-V2-VCTK-P226",
        "title": "RVC v2 VCTK p226",
        "component": "rvc-v2-vctk-p226",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
                       "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-SURVEY-TRN-04",
        "title": "Review coverage for Speech-to-speech voice conversion",
        "component": None,
        "mode": "taxonomy",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
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
    "research/voice-conversion-eval-20261101/models/rvc-vctk/M/p226/rmvpe/"
    "added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index",
    "research/voice-conversion-eval-20261101/checkpoints/rvc",
    "research/voice-conversion-eval-20261101/checkpoints/rvc/Mp226rmvpe.pth",
    "research/voice-conversion-eval-20261101/checkpoints/rvc/"
    "added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index",
    "research/voice-conversion-eval-20261101/.venv-eval",
    "research/voice-conversion-eval-20261101/.venv-chatterbox",
    "research/voice-conversion-eval-20261101/repos/rvc/.venv",
    "research/voice-conversion-eval-20261101/repos/rvc/venv",
    "research/voice-conversion-eval-20261101/repos/rvc/assets/rmvpe/rmvpe.pt",
    "research/voice-conversion-eval-20261101/repos/rvc/assets/hubert_base/"
    "pytorch_model.bin",
    "research/voice-conversion-eval-20261101/repos/rvc/logs",
    "data/assets/rvc-faiss-retrieval",
    "data/assets/rvc-faiss-retrieval/Mp226rmvpe.pth",
    "data/assets/rvc-faiss-retrieval/"
    "added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index",
    "third_party/rvc",
    "third_party/rvc-faiss-retrieval",
    "deps/rvc",
    "adapters/rvc-faiss-retrieval",
    "LICENSES/RVC-VCTK-weights.txt",
    "docs/task-evidence/rvc-faiss-retrieval/weights",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--Nekochu--RVC-VCTK_Voice-sample",
    "~/.cache/huggingface/hub/models--Nekochu--RVC-VCTK_Voice-sample/blobs",
    "~/.cache/huggingface/hub/models--Nekochu--RVC-VCTK_Voice-sample/snapshots",
    "~/.cache/huggingface/hub/models--Nekochu--RVC-VCTK_Voice-sample/refs",
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

RUNTIME_PROBE_MODULES = ("faiss", "torch", "torchaudio", "numpy", "soundfile")
RUNTIME_PROBE = {
    "probe": "importlib.util.find_spec metadata only; no import performed",
    "import_performed": False,
    "model_executed": False,
    "faiss_executed": False,
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
        "pinned_offline_and_realtime_retrieval_call_sites",
        "historical_no_retrieval_output_provenance",
    ],
    "absent_components": [
        "checkpoint_weights_Mp226rmvpe_pth",
        "faiss_index_added_IVF1161_Flat_nprobe_1",
        "faiss_and_torch_runtime",
        "retained_crash_trace_and_exit_signal",
        "verified_speaker_map",
        "source_speaker_and_target_voice_rights",
    ],
    "exact_source_weights_runtime_conjunction_present": False,
    "reason": (
        "The RVC checkout is present at the pinned 40-hex revision with an MIT "
        "LICENSE, and the offline/realtime retrieval call sites are pinned. "
        "That source-code presence grants no checkpoint, index, dataset, "
        "voice, consent or output-use right. The p226 checkpoint, the matching "
        "137 MB IVF1161 Flat index, the FAISS/Torch runtime and the original "
        "crash trace are absent, so the source/weights/runtime conjunction is "
        "not present."),
}

RETRIEVAL_ISOLATION = {
    "id": "RI-1",
    "offline_path": {
        "path": "research/voice-conversion-eval-20261101/repos/rvc/infer/vc/"
                "pipeline.py",
        "sha256":
            "df8ccd98ca7f81e38934a0af93cc63b4f79764dc47d932f05914c566e876522a",
        "search_line": 186,
        "search_call": "score, ix = index.search(npy, k=8)",
        "search_k": SEARCH_K,
        "weight_line": 187,
        "weight_expression": "np.square(1 / score)",
        "read_index_line": 279,
        "reconstruct_line": 280,
        "fallback_line": 283,
        "query_origin": (
            "extract_hubert_features(...)[0].cpu().numpy(); cast to float32 "
            "when the model is half precision"),
        "search_exception_handling": "none_at_call_site",
        "read_index_exception_handling": (
            "read_index and reconstruct_n are inside a bare except that prints "
            "the traceback and degrades to index = index_vectors = None"),
        "retained_success_exercised": False,
        "crash_observation_reached": True,
        "note": (
            "The retained successful run passed an empty index and "
            "index_rate=0.0, so the retrieval branch was not taken there. The "
            "separate prose crash observation is reported to have reached "
            "index.search, but no trace survives."),
    },
    "realtime_path": {
        "path": "research/voice-conversion-eval-20261101/repos/rvc/infer/"
                "rtrvc.py",
        "sha256":
            "c04d2f2d38ed67ca5c1846f4b392befdf0cf7a6172cffe679a81c039dc1642bc",
        "search_line": 253,
        "search_call": "score, ix = self.index.search(npy, k=8)",
        "handler_line": 274,
        "handler": "except Exception:",
        "report_line": 275,
        "report_call": "traceback.print_exc()",
        "search_exception_handling": "caught_and_traceback_printed",
        "retained_success_exercised": False,
        "crash_observation_reached": False,
        "note": (
            "The realtime path catches search exceptions and prints a "
            "traceback; a native abort inside FAISS would not be caught. The "
            "realtime path was not exercised because the fork has no Metal "
            "device on this host."),
    },
    "index_builder": {
        "path": "research/voice-conversion-eval-20261101/repos/rvc/train/"
                "train_index.py",
        "sha256":
            "9377e10716ce2ba63d4fb346fe36792b1543803b01a18a782563f6f47713e5a1",
        "factory_line": 209,
        "factory_call": "faiss.index_factory(",
        "dimension_fragment": "256 if version == \"v1\" else 768",
        "factory_fragment": "\"IVF%s,Flat\"",
        "nprobe_line": 201,
        "nprobe_value": INDEX_NPROBE,
        "name_fragment": "added_IVF%s_Flat_nprobe_%s_",
        "note": (
            "The historical name added_IVF1161_Flat_nprobe_1_..._v2 is "
            "consistent with the pinned builder: v2 uses 768 dimensions, "
            "IVF1161 Flat and nprobe=1."),
    },
    "resolver": {
        "path": "research/voice-conversion-eval-20261101/repos/rvc/infer/"
                "cli.py",
        "sha256":
            "8e321cd606bfa1f4756685db897e90df2278e77d3e58869bc83d4735ff7b7387",
        "zero_rate_line": 141,
        "zero_rate_fragment": "if index_rate == 0:",
        "retrieval_path_fragment": "if index_rate == 0:",
        "conversion_default": (
            "An empty index path or index_rate=0 selects the no-retrieval "
            "conditioning control."),
    },
    "crash_observation": {
        "observed_in": (
            "research/voice-conversion-eval-20261101/README.md and "
            "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/"
            "REPORT.md"),
        "observed_statement": (
            "Enabling the matching 137 MB FAISS index crashes inside native "
            "index.search(); retrieval was disabled for the retained output."),
        "mechanism": "native_index_search_crash",
        "original_traceback_retained": False,
        "original_stderr_retained": False,
        "exit_signal_recorded": False,
        "faiss_version_recorded": False,
        "index_metadata_recorded": False,
        "reproduced": False,
        "root_cause": "unlocalized",
        "reproduction_attempted_here": False,
        "isolation_status": "call_site_pinned_but_root_cause_unlocalized",
        "note": (
            "Only prose preserves the observation. No traceback, signal, "
            "stderr, FAISS build string or index metadata was retained, and "
            "the checkpoint/index/runtime are absent. Re-running is "
            "impossible here; the crash cannot be promoted to a reproducible "
            "defect signature."),
    },
}

FAILURE_AND_CONTROL = {
    "failure": {
        "id": "FC-FAIL-1",
        "condition": "retrieval_enabled",
        "observed": "native_crash_inside_index_search",
        "evidence_class": "historical_prose_only",
        "status": "not_reproduced",
        "retained_traceback": False,
        "retained_stderr": False,
        "retained_index_bytes": False,
        "retained_checkpoint": False,
        "reproduced": False,
        "root_cause": "unlocalized",
        "qualifies": False,
        "statement": (
            "The local evaluation recorded a crash when the matching index "
            "was enabled, but the trace, signal, index and runtime were not "
            "retained. This package records the boundary, not a crash result."),
    },
    "control": {
        "id": "FC-CTRL-1",
        "condition": "retrieval_disabled",
        "observed": "file_conversion_success",
        "evidence_class": "historical_unpaired_observation",
        "index_path": "",
        "index_rate_decimal": "0.0",
        "index_assigned": False,
        "output_sha256":
            "7fa0516e7475b6870267da9f4a894d0d18e67714e1081cd9d3c7d63db30bd8c7",
        "output_byte_count": 771244,
        "sample_rate_hz": 40000,
        "file_rtf_decimal": "0.8038138485507831",
        "paired_with_failure": False,
        "same_runtime_verified": False,
        "same_artifacts_verified": False,
        "status": "unpaired_historical_control",
        "qualifies": False,
        "statement": (
            "The retained 40 kHz output was produced with retrieval disabled. "
            "It is a conditioning control candidate, not a paired control: the "
            "retrieval-enabled counterpart has no retained bytes, timing or "
            "trace, and the runtime is absent."),
    },
    "isolation": {
        "status": "incomplete",
        "call_site_pinned": True,
        "root_cause_localized": False,
        "minimal_reproducer_present": False,
        "control_pair_present": False,
        "adverse_query_contract_modelled": True,
        "faiss_executed": False,
        "model_executed": False,
        "qualifies": False,
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
            "and per-file SHA-256 pins, including the offline and realtime "
            "retrieval call sites, index builder and resolver."),
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
            "model revision, byte count, SHA-256 and reviewed weight terms."),
    },
    {
        "id": "ART-03",
        "kind": "faiss_index_snapshot",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "The matching 137 MB `added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2."
            "index` with byte count, SHA-256, 768 dimensions, IVF1161 Flat "
            "type, nlist=1161, nprobe=1 and L2 metric."),
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
            "A reproducible isolated runtime with Python 3.11, torch 2.15.0, "
            "torchaudio 2.11.1, a faiss-cpu build >= 1.13.0, numpy 1.26.x, "
            "recorded OMP/OpenBLAS thread counts, a lock/install digest and a "
            "fail-closed offline load path."),
    },
    {
        "id": "ART-05",
        "kind": "crash_and_control_record",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "A retained retrieval-enabled crash record (stdout, stderr, "
            "traceback or native stack, exit code/signal, exact invocation, "
            "index/checkpoint/query digests, FAISS build) plus a paired "
            "identical-artifact no-retrieval control."),
    },
    {
        "id": "ART-06",
        "kind": "verified_speaker_map",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "A reviewed 109-entry speaker map for the checkpoint. The "
            "historical checkpoint has no speaker_info metadata and the "
            "`speaker_id=1 -> p226` mapping is explicitly unverified."),
    },
    {
        "id": "ART-07",
        "kind": "rights_and_voice_cohort",
        "present": False,
        "verified": False,
        "blocked": True,
        "revision": None,
        "sha256": None,
        "requirement": (
            "Reviewed checkpoint/index/dataset terms, source-speaker consent, "
            "target-voice consent, reference availability, output-use terms, "
            "a rights-cleared frozen cohort with manual transcripts and the "
            "agreed Voice quality/timing/listening protocol."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-02", "RG-04"],
        "statement": (
            "The exact p226 checkpoint is absent from every fixed probe. The "
            "historical runner points at "
            "models/rvc-vctk/M/p226/rmvpe/Mp226rmvpe.pth, the whole models "
            "tree is gone, and no local or Hugging Face cache copy exists. "
            "Nothing was downloaded or reconstructed."),
        "required_action": (
            "Supply the immutable `Mp226rmvpe.pth` snapshot with a 40-hex "
            "revision, byte count, SHA-256 and reviewed weight terms."),
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-02", "RG-04"],
        "statement": (
            "The matching 137 MB FAISS index is absent. The historical runner "
            "names added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index; no index "
            "bytes, index metadata or index terms are staged."),
        "required_action": (
            "Supply the immutable index with byte count, SHA-256 and recorded "
            "d=768, IndexIVFFlat, nlist=1161, nprobe=1, metric=L2, ntotal."),
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-03"],
        "statement": (
            "The FAISS and Torch runtime is absent: the current interpreter "
            "has no faiss, torch, torchaudio, numpy or soundfile module, and "
            "the historical venvs are gone. The historical FAISS version and "
            "build string were never recorded."),
        "required_action": (
            "Stage a locked Python 3.11 runtime with the documented "
            "torch 2.15.0 / torchaudio 2.11.1 main stack and a pinned "
            "faiss-cpu build, including OMP/OpenBLAS thread settings."),
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-04"],
        "statement": (
            "No crash artifact survives. The research record says retrieval "
            "crashed inside native index.search(), but there is no traceback, "
            "stderr, signal, exit code, FAISS build string or minimal query "
            "case to localize the fault."),
        "required_action": (
            "Retain the exact invocation and full stdout/stderr/native stack, "
            "exit code or signal, and a minimized failing query/index bundle; "
            "reproduce it twice on the pinned runtime."),
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-05"],
        "statement": (
            "The retained successful output is an unpaired no-retrieval "
            "observation. It was not produced in the same session, from the "
            "same staged artifacts or against the retrieval-enabled failure, "
            "and its runtime cannot be reconstructed."),
        "required_action": (
            "Run the identical input, checkpoint, index and runtime twice: "
            "index_rate=0 control and index_rate>0 retrieval, and retain both "
            "outputs, logs and timings."),
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-02", "RG-06"],
        "statement": (
            "The checkpoint has 109 speaker embeddings but no speaker_info "
            "map. `speaker_id=1` was presumed to be p226 from the folder name "
            "and VCTK ordering; that mapping is unverified, so retrieval and "
            "target identity are not attributable."),
        "required_action": (
            "Supply a reviewed 109-entry speaker map with provenance and use "
            "the verified p226 index for p226."),
    },
    {
        "id": "BLK-07",
        "artifact_id": "ART-07",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-06", "RG-07"],
        "statement": (
            "No checkpoint/index/dataset terms review and no source-speaker or "
            "target-voice consent, reference-availability, output-use or "
            "cohort record exists. The MIT source license clears none of "
            "these."),
        "required_action": (
            "Stage the reviewed terms bundle, signed consents, frozen "
            "rights-cleared cohort and the agreed Voice quality/timing/"
            "listening protocol."),
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_archive_and_license_provenance",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "The RVC fork revision and MIT license are pinned, but the exact "
            "upstream archive/tree provenance, checkpoint model-card terms and "
            "index provenance are not reviewed. Source-code presence is not a "
            "weight, index or rights grant."),
        "reopen_condition": (
            "Both source archives, 40-hex revisions, tree digests, complete "
            "license/notice sets and checkpoint/index terms are supplied and "
            "reviewed."),
    },
    {
        "id": "RG-02",
        "title": "checkpoint_index_assets_and_metadata",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "The p226 checkpoint, the matching IVF1161 Flat index and the "
            "verified 109-entry speaker map are absent; only their names "
            "survive in the pinned runner."),
        "reopen_condition": (
            "Immutable checkpoint and index bytes, digests, index metadata and "
            "a verified speaker map are staged and reviewed."),
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_and_offline_load",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "No faiss-cpu, torch or torchaudio runtime is present; the "
            "historical FAISS version/build and thread environment were not "
            "recorded."),
        "reopen_condition": (
            "A locked runtime with install digest loads the pinned checkpoint "
            "and index offline with recorded OMP/OpenBLAS threads and "
            "deterministic settings."),
    },
    {
        "id": "RG-04",
        "title": "retained_crash_evidence_and_root_cause",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "The crash is prose only. No traceback, signal, stderr, FAISS "
            "build or minimized query/index case exists, so the native "
            "failure remains unlocalized."),
        "reopen_condition": (
            "The exact reproducer, full crash artifact, minimal failing case "
            "and a localized root cause are reproduced on the pinned runtime."),
    },
    {
        "id": "RG-05",
        "title": "paired_no_retrieval_conditioning_control",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "The historical no-retrieval output is unpaired. There is no "
            "same-artifact, same-runtime retrieval-enabled counterpart and no "
            "equivalence or divergence result."),
        "reopen_condition": (
            "A same-input, same-checkpoint, same-index, same-runtime pair of "
            "runs (index_rate=0 vs index_rate>0) is retained with outputs, "
            "logs, timings and a declared comparison."),
    },
    {
        "id": "RG-06",
        "title": "verified_speaker_map_rights_and_cohort",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "The speaker map is presumed, the checkpoint/index/dataset terms "
            "are unreviewed, and no source-speaker or target-voice consent or "
            "reference-availability record exists."),
        "reopen_condition": (
            "A verified speaker map, reviewed terms and signed consents plus a "
            "rights-cleared frozen cohort are staged and reviewed."),
    },
    {
        "id": "RG-07",
        "title": "voice_quality_timing_and_listening",
        "status": "blocked",
        "qualifies": False,
        "linked_row": BOARD_ROW_PROJECTION,
        "statement": (
            "No content, identity, naturalness, alignment, first-output/tail, "
            "device-timing, resource or listening result exists for retrieval-"
            "enabled conversion."),
        "reopen_condition": (
            "Pinned scorers, an approved blinded listening protocol and paced "
            "target-device runs produce separate content, identity, "
            "naturalness, alignment, timing and resource results."),
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
            "The historical source is one unconsented LJ Speech clip and the "
            "target is p226 via an unverified speaker_id=1 mapping; no rights "
            "record, language group or frozen target condition is staged."),
    },
    {
        "id": "V-02",
        "requirement": "Preserve text and semantic content.",
        "status": "blocked",
        "evidence": (
            "The historical one-utterance Whisper Tiny WER of 0.0 is a proxy, "
            "not a manual transcript or semantic-content result, and it was "
            "not rerun for retrieval."),
    },
    {
        "id": "V-03",
        "requirement": "Measure identity/similarity as a separate outcome.",
        "status": "blocked",
        "evidence": (
            "No target-voice similarity metric or scored retrieval-enabled "
            "output exists, and the target mapping itself is unverified."),
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
            "No word/phoneme, onset or source-content alignment exists; the "
            "retrieval path alters features before synthesis and was not run "
            "successfully."),
    },
    {
        "id": "V-06",
        "requirement": "Record first-output and tail timing.",
        "status": "blocked",
        "evidence": (
            "Only whole-file conversion timing exists for the no-retrieval "
            "control; retrieval-enabled first-output/tail timing is absent."),
    },
    {
        "id": "V-07",
        "requirement": "Record the exact target condition.",
        "status": "blocked",
        "evidence": (
            "The target condition is the presumed p226 speaker_id=1 path with "
            "the matching index, but the speaker map, index bytes and target "
            "consent are absent."),
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
            "content metric exists for retrieval-enabled conversion."),
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
        "evidence": "No aligned retrieval-enabled output exists.",
    },
    {
        "id": "TM-02",
        "metric": "first_output_and_tail_ms",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No retrieval-enabled chunk/segment timing or tail measurement "
            "exists; the retained control is whole-file."),
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
    "output_sha256":
        "7fa0516e7475b6870267da9f4a894d0d18e67714e1081cd9d3c7d63db30bd8c7",
    "output_byte_count": 771244,
    "output_sample_rate_hz": 40000,
    "output_duration_seconds_decimal": "9.64",
    "checkpoint_path_historical": (
        "research/voice-conversion-eval-20261101/models/rvc-vctk/M/p226/"
        "rmvpe/Mp226rmvpe.pth"),
    "index_path_historical": (
        "research/voice-conversion-eval-20261101/models/rvc-vctk/M/p226/"
        "rmvpe/added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index"),
    "checkpoint_present": False,
    "index_present": False,
    "mode": (
        "official RVC PyTorch VC pipeline, CPU, 4 threads, file input, RMVPE "
        "F0, retrieval disabled"),
    "retrieval_enabled": False,
    "index_rate_decimal": "0.0",
    "speaker_id": 1,
    "speaker_map_verified": False,
    "model_and_hubert_load_seconds_decimal": "0.34603404195513576",
    "conversion_wall_seconds_decimal": "7.748765500029549",
    "file_rtf_decimal": "0.8038138485507831",
    "peak_abs_decimal": "0.497772216796875",
    "clipped_sample_fraction_decimal": "0.0",
    "asr_wer_decimal": "0.0",
    "retrieval_crash_observed": True,
    "crash_traceback_retained": False,
    "crash_reproduced": False,
    "paired_control": False,
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
        "The retained output used retrieval disabled; it is not a retrieval-"
        "enabled result and not a successful FAISS path.",
        "The retrieval-enabled run crashed inside native index.search() and "
        "no traceback, signal, stderr, index metadata or runtime build was "
        "retained.",
        "The checkpoint, index and runtime are absent, so neither the crash "
        "nor the control can be rerun or paired here.",
        "The speaker_id=1 -> p226 mapping is presumed from the path and VCTK "
        "order; the checkpoint has no speaker_info map.",
        "The source/target consent, dataset reference and output-use terms "
        "are not staged.",
        "One Whisper Tiny WER proxy is not a manual transcript, semantic, "
        "identity, naturalness or listening result.",
        "The run is whole-file CPU conversion, not device timing, streaming, "
        "real-time, benchmark or release evidence.",
    ],
}

REQUIRED_RESULTS = {
    "source_present": True,
    "weights_present": False,
    "index_present": False,
    "runtime_present": False,
    "crash_reproduction_result_present": False,
    "crash_root_cause_result_present": False,
    "paired_control_result_present": False,
    "query_validity_result_present": False,
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
    "No FAISS, Torch, torchaudio, numpy, soundfile, RVC, checkpoint, index or "
    "waveform is imported, loaded, linked, built or executed.",
    "No retrieval-enabled conversion, FAISS search, crash reproduction, root "
    "cause, retrieval benefit, speaker attribution, quality score or timing "
    "result is produced.",
    "No audio is decoded or played; the historical output is pinned by whole-"
    "file SHA-256 and byte count only and is not used as evidence.",
    "No provider, descriptor, registry, default, installed-v0, public API, "
    "ABI, shared build or CI change is made or proposed.",
    "No real corpus, consent record, checkpoint weight, index or runtime is "
    "supplied, downloaded, reconstructed or substituted.",
    "No listening, voice conversion, device timing, benchmark or release "
    "claim is made.",
    "No Chatterbox, CosyVoice 2, OpenVoice, MeanVC2, Seed-VC, LLVC, RVC-MLX "
    "or other sibling result is pooled or reinterpreted as retrieval evidence.",
    "The historical crash is an unreproduced prose observation, not a "
    "qualified defect signature.",
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

# The reproducer manifest is a task-local schema, not an SDK, RVC or Voice
# contract. It admits metadata only and never reads audio or invokes FAISS.
MANIFEST_SCHEMA_ID = "audio-sdk/rvc-faiss-retrieval-reproducer/0.1"
MANIFEST_FIELDS = (
    "schema_id",
    "experiment_id",
    "candidate",
    "checkpoint",
    "index",
    "runtime",
    "query",
    "observations",
    "control",
    "rights",
)
CANDIDATE_FIELDS = ("repository", "revision", "path", "license_id",
                    "license_path", "license_sha256", "distribution")
CHECKPOINT_FIELDS = ("name", "path", "sha256", "byte_count", "speaker_count",
                     "speaker_info_present", "speaker_map_sha256",
                     "speaker_map_verified", "terms_sha256")
INDEX_FIELDS = ("name", "path", "sha256", "byte_count", "index_type",
                "dimension", "ntotal", "nlist", "nprobe", "metric",
                "read_index_seconds_decimal",
                "reconstruct_seconds_decimal")
RUNTIME_FIELDS = ("python_version", "torch_version", "torchaudio_version",
                  "faiss_version", "faiss_build", "numpy_version", "device",
                  "threads", "omp_threads", "openblas_threads",
                  "deterministic_algorithms")
QUERY_FIELDS = ("source_audio_path", "source_audio_sha256",
                "source_audio_byte_count", "sample_rate_hz",
                "duration_seconds_decimal", "feature_dim", "frame_count",
                "dtype", "all_finite", "query_sha256")
OBSERVATION_FIELDS = ("retrieval_enabled", "index_assigned", "search_returned",
                      "exit_kind", "exit_code", "signal", "traceback_path",
                      "traceback_sha256", "stderr_sha256", "stdout_sha256",
                      "wall_seconds_decimal", "score_finite", "result_sha256",
                      "result_nonfinite_count")
CONTROL_FIELDS = ("retrieval_enabled", "index_rate_decimal", "index_assigned",
                  "output_path", "output_sha256", "output_byte_count",
                  "wall_seconds_decimal", "paired", "same_artifacts")
RIGHTS_FIELDS = ("checkpoint_terms", "index_terms", "source_speaker_consent",
                 "target_voice_consent", "dataset_reference", "output_use",
                 "review_id", "cohort_id")

EXIT_KINDS = ("native_crash", "uncaught_exception", "clean")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PYTHON_VERSION = re.compile(r"^3\.11\.[0-9]+$")
FAISS_VERSION = re.compile(r"^1\.([0-9]{1,2})\.([0-9]{1,2})$")
NUMPY_VERSION = re.compile(r"^1\.26\.[0-9]+$")
MAX_CHECKPOINT_BYTES = 8 * 1024 * 1024 * 1024
MAX_INDEX_BYTES = 2 * 1024 * 1024 * 1024
MAX_OUTPUT_BYTES = 8 * 1024 * 1024 * 1024
MAX_TOTAL_VECTORS = 1000000000
MAX_FRAME_COUNT = 1000000
MAX_THREADS = 64
MAX_TEXT_LENGTH = 200


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
        "index_loaded": False,
        "faiss_executed": False,
        "model_executed": False,
        "audio_read": False,
        "all_probes_absent": all(not row["present"] for row in all_rows),
    }


# --------------------------------------------------------------------------
# Retrieval/control branch contract model (deterministic; no FAISS)
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


def evaluate_query_contract(
    *,
    index_rate: float,
    dimension: int,
    frame_count: int,
    dtype: str,
    all_finite: bool,
    index_dimension: int,
    ntotal: int,
    nlist: int,
    nprobe: int,
    search_k: int = SEARCH_K,
) -> dict:
    """Model the pinned retrieval/control branch contract without FAISS.

    This is a deterministic classification of the exact preconditions at the
    pinned `Pipeline.vc` call site. It never loads an index, allocates a matrix
    or runs a search. `index_rate=0` is the no-retrieval conditioning control.
    """
    if not _is_number(index_rate) or not 0.0 <= float(index_rate) <= 1.0:
        return {"accepted": False, "code": "invalid_index_rate",
                "retrieval_attempted": False, "qualifies": False,
                "state_unchanged": True}
    if float(index_rate) == 0.0:
        return {"accepted": True, "code": "control_skipped",
                "retrieval_attempted": False, "search_k": None,
                "qualifies": False, "state_unchanged": True}
    if not _is_int(search_k) or search_k != SEARCH_K:
        return {"accepted": False, "code": "invalid_search_k",
                "retrieval_attempted": False, "qualifies": False,
                "state_unchanged": True}
    if not _is_int(dimension) or dimension not in (256, 768):
        return {"accepted": False, "code": "invalid_dimension",
                "retrieval_attempted": False, "qualifies": False,
                "state_unchanged": True}
    if dimension != index_dimension:
        return {"accepted": False, "code": "dimension_mismatch",
                "retrieval_attempted": False, "qualifies": False,
                "state_unchanged": True}
    if not _is_int(frame_count) or not 1 <= frame_count <= MAX_FRAME_COUNT:
        return {"accepted": False, "code": "frame_count_out_of_range",
                "retrieval_attempted": False, "qualifies": False,
                "state_unchanged": True}
    if dtype != "float32":
        return {"accepted": False, "code": "invalid_dtype",
                "retrieval_attempted": False, "qualifies": False,
                "state_unchanged": True}
    if all_finite is not True:
        return {"accepted": False, "code": "nonfinite_query",
                "retrieval_attempted": False, "qualifies": False,
                "state_unchanged": True}
    for name, value in (("ntotal", ntotal), ("nlist", nlist)):
        if not _is_int(value) or not 1 <= value <= MAX_TOTAL_VECTORS:
            return {"accepted": False, "code": name + "_out_of_range",
                    "retrieval_attempted": False, "qualifies": False,
                    "state_unchanged": True}
    if nlist > ntotal:
        return {"accepted": False, "code": "nlist_exceeds_ntotal",
                "retrieval_attempted": False, "qualifies": False,
                "state_unchanged": True}
    if not _is_int(nprobe) or not 1 <= nprobe <= nlist:
        return {"accepted": False, "code": "nprobe_out_of_range",
                "retrieval_attempted": False, "qualifies": False,
                "state_unchanged": True}
    return {"accepted": True, "code": "accepted_for_reproducer",
            "retrieval_attempted": True, "search_k": SEARCH_K,
            "qualifies": False, "state_unchanged": True}


# --------------------------------------------------------------------------
# Reproducer admission validator (task-local; never a runtime boundary)
# --------------------------------------------------------------------------
def _reject(code: str, field: str = "") -> dict:
    return {"accepted": False, "code": code, "field": field,
            "checks": 0, "state_unchanged": True}


def _accept(checks: int) -> dict:
    return {"accepted": True, "code": "ok", "field": "", "checks": checks,
            "state_unchanged": True}


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    """Fail-closed retrieval reproducer admission. No audio is read; no model
    or FAISS index is loaded."""
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
            or not HEX40.match(candidate["revision"]):
        return _reject("invalid_value", "candidate.revision")
    if candidate["revision"] != SOURCE_REVISION:
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
    if checkpoint["speaker_count"] != INDEX_SPEAKERS:
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
    checks += 10

    index = document["index"]
    code = _exact_object(index, INDEX_FIELDS)
    if code:
        return _reject(code, "index")
    if index["name"] != INDEX_NAME:
        return _reject("invalid_value", "index.name")
    if not _path_is_canonical(index["path"]):
        return _reject("invalid_path", "index.path")
    if not _sha(index["sha256"]):
        return _reject("invalid_value", "index.sha256")
    if not _is_int(index["byte_count"]) \
            or not 1 <= index["byte_count"] <= MAX_INDEX_BYTES:
        return _reject("invalid_value", "index.byte_count")
    if index["index_type"] != INDEX_TYPE:
        return _reject("invalid_value", "index.index_type")
    if index["dimension"] != INDEX_DIMENSION:
        return _reject("invalid_value", "index.dimension")
    if not _is_int(index["ntotal"]) \
            or not 1 <= index["ntotal"] <= MAX_TOTAL_VECTORS:
        return _reject("invalid_value", "index.ntotal")
    if index["nlist"] != INDEX_NLIST:
        return _reject("invalid_value", "index.nlist")
    if index["nlist"] > index["ntotal"]:
        return _reject("invalid_value", "index.nlist_vs_ntotal")
    if index["nprobe"] != INDEX_NPROBE:
        return _reject("invalid_value", "index.nprobe")
    if index["metric"] != "l2":
        return _reject("invalid_value", "index.metric")
    for field in ("read_index_seconds_decimal",
                  "reconstruct_seconds_decimal"):
        if not _positive_decimal(index[field], allow_zero=True):
            return _reject("invalid_value", "index." + field)
    if probe_paths and not Path(index["path"]).is_file():
        return _reject("probe_missing", "index.path")
    checks += 12

    runtime = document["runtime"]
    code = _exact_object(runtime, RUNTIME_FIELDS)
    if code:
        return _reject(code, "runtime")
    if not isinstance(runtime["python_version"], str) \
            or not PYTHON_VERSION.match(runtime["python_version"]):
        return _reject("invalid_value", "runtime.python_version")
    if runtime["torch_version"] != "2.15.0":
        return _reject("invalid_value", "runtime.torch_version")
    if runtime["torchaudio_version"] != "2.11.1":
        return _reject("invalid_value", "runtime.torchaudio_version")
    if not isinstance(runtime["faiss_version"], str) \
            or not FAISS_VERSION.match(runtime["faiss_version"]):
        return _reject("invalid_value", "runtime.faiss_version")
    faiss_parts = FAISS_VERSION.match(runtime["faiss_version"])
    if (int(faiss_parts.group(1)), int(faiss_parts.group(2))) < (13, 0):
        return _reject("invalid_value", "runtime.faiss_version")
    if not _text(runtime["faiss_build"], 120):
        return _reject("invalid_value", "runtime.faiss_build")
    if not isinstance(runtime["numpy_version"], str) \
            or not NUMPY_VERSION.match(runtime["numpy_version"]):
        return _reject("invalid_value", "runtime.numpy_version")
    if runtime["device"] != "cpu":
        return _reject("invalid_value", "runtime.device")
    for field in ("threads", "omp_threads", "openblas_threads"):
        if not _is_int(runtime[field]) \
                or not 1 <= runtime[field] <= MAX_THREADS:
            return _reject("invalid_value", "runtime." + field)
    if runtime["deterministic_algorithms"] is not True:
        return _reject("invalid_value", "runtime.deterministic_algorithms")
    checks += len(RUNTIME_FIELDS)

    query = document["query"]
    code = _exact_object(query, QUERY_FIELDS)
    if code:
        return _reject(code, "query")
    if not _path_is_canonical(query["source_audio_path"]):
        return _reject("invalid_path", "query.source_audio_path")
    if query["source_audio_sha256"] != SOURCE_AUDIO_SHA256:
        return _reject("invalid_value", "query.source_audio_sha256")
    if query["source_audio_byte_count"] != SOURCE_AUDIO_BYTES:
        return _reject("invalid_value", "query.source_audio_byte_count")
    if query["sample_rate_hz"] != 16000:
        return _reject("invalid_value", "query.sample_rate_hz")
    if query["duration_seconds_decimal"] != "9.655":
        return _reject("invalid_value", "query.duration_seconds_decimal")
    if query["feature_dim"] != INDEX_DIMENSION:
        return _reject("invalid_value", "query.feature_dim")
    if not _is_int(query["frame_count"]) \
            or not 1 <= query["frame_count"] <= MAX_FRAME_COUNT:
        return _reject("invalid_value", "query.frame_count")
    if query["dtype"] != "float32":
        return _reject("invalid_value", "query.dtype")
    if query["all_finite"] is not True:
        return _reject("invalid_value", "query.all_finite")
    if not _sha(query["query_sha256"]):
        return _reject("invalid_value", "query.query_sha256")
    if probe_paths and not Path(query["source_audio_path"]).is_file():
        return _reject("probe_missing", "query.source_audio_path")
    checks += len(QUERY_FIELDS)

    observations = document["observations"]
    code = _exact_object(observations, OBSERVATION_FIELDS)
    if code:
        return _reject(code, "observations")
    if observations["retrieval_enabled"] is not True:
        return _reject("invalid_value", "observations.retrieval_enabled")
    if observations["index_assigned"] is not True:
        return _reject("invalid_value", "observations.index_assigned")
    if not isinstance(observations["search_returned"], bool):
        return _reject("invalid_value", "observations.search_returned")
    exit_kind = observations["exit_kind"]
    if exit_kind not in EXIT_KINDS:
        return _reject("invalid_value", "observations.exit_kind")
    if not _positive_decimal(observations["wall_seconds_decimal"]):
        return _reject("invalid_value", "observations.wall_seconds_decimal")
    if observations["stderr_sha256"] is not None \
            and not _sha(observations["stderr_sha256"]):
        return _reject("invalid_value", "observations.stderr_sha256")
    if observations["stdout_sha256"] is not None \
            and not _sha(observations["stdout_sha256"]):
        return _reject("invalid_value", "observations.stdout_sha256")
    if observations["traceback_path"] is not None \
            and not _path_is_canonical(observations["traceback_path"]):
        return _reject("invalid_path", "observations.traceback_path")
    if observations["traceback_sha256"] is not None \
            and not _sha(observations["traceback_sha256"]):
        return _reject("invalid_value", "observations.traceback_sha256")
    exit_code = observations["exit_code"]
    signal = observations["signal"]
    if exit_code is not None and (not _is_int(exit_code)
                                  or not -255 <= exit_code <= 255):
        return _reject("invalid_value", "observations.exit_code")
    if signal is not None and (not _is_int(signal)
                               or not 1 <= signal <= 31):
        return _reject("invalid_value", "observations.signal")
    if exit_kind == "clean":
        if exit_code != 0 or signal is not None:
            return _reject("invalid_value", "observations.exit_code")
        if observations["search_returned"] is not True:
            return _reject("invalid_value", "observations.search_returned")
        if observations["score_finite"] is not True:
            return _reject("invalid_value", "observations.score_finite")
        if not _sha(observations["result_sha256"]):
            return _reject("invalid_value", "observations.result_sha256")
        if observations["result_nonfinite_count"] != 0:
            return _reject("invalid_value",
                           "observations.result_nonfinite_count")
        if observations["traceback_path"] is not None \
                or observations["traceback_sha256"] is not None:
            return _reject("invalid_value", "observations.traceback_path")
    else:
        if observations["search_returned"] is not False:
            return _reject("invalid_value", "observations.search_returned")
        if observations["score_finite"] is not None \
                or observations["result_sha256"] is not None \
                or observations["result_nonfinite_count"] is not None:
            return _reject("invalid_value", "observations.result_sha256")
        if observations["traceback_path"] is None \
                or observations["traceback_sha256"] is None:
            return _reject("invalid_value", "observations.traceback_path")
        if exit_kind == "native_crash":
            if signal is None or exit_code is None:
                return _reject("invalid_value", "observations.signal")
            if exit_code not in (-signal, 128 + signal):
                return _reject("invalid_value", "observations.exit_code")
        elif exit_kind == "uncaught_exception":
            if signal is not None or exit_code in (None, 0):
                return _reject("invalid_value", "observations.exit_code")
    checks += len(OBSERVATION_FIELDS) + 6

    control = document["control"]
    code = _exact_object(control, CONTROL_FIELDS)
    if code:
        return _reject(code, "control")
    if control["retrieval_enabled"] is not False:
        return _reject("invalid_value", "control.retrieval_enabled")
    if control["index_rate_decimal"] != "0.0":
        return _reject("invalid_value", "control.index_rate_decimal")
    if control["index_assigned"] is not False:
        return _reject("invalid_value", "control.index_assigned")
    if not _path_is_canonical(control["output_path"]):
        return _reject("invalid_path", "control.output_path")
    if not _sha(control["output_sha256"]):
        return _reject("invalid_value", "control.output_sha256")
    if not _is_int(control["output_byte_count"]) \
            or not 1 <= control["output_byte_count"] <= MAX_OUTPUT_BYTES:
        return _reject("invalid_value", "control.output_byte_count")
    if not _positive_decimal(control["wall_seconds_decimal"]):
        return _reject("invalid_value", "control.wall_seconds_decimal")
    if control["paired"] is not True:
        return _reject("invalid_value", "control.paired")
    if control["same_artifacts"] is not True:
        return _reject("invalid_value", "control.same_artifacts")
    checks += len(CONTROL_FIELDS)

    rights = document["rights"]
    code = _exact_object(rights, RIGHTS_FIELDS)
    if code:
        return _reject(code, "rights")
    for field in ("checkpoint_terms", "index_terms",
                  "source_speaker_consent", "target_voice_consent",
                  "dataset_reference", "output_use"):
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
            "speaker_count": INDEX_SPEAKERS,
            "speaker_info_present": False,
            "speaker_map_sha256": "c" * 64,
            "speaker_map_verified": True,
            "terms_sha256": "d" * 64,
        },
        "index": {
            "name": INDEX_NAME,
            "path": "/caller/models/" + INDEX_NAME,
            "sha256": "e" * 64,
            "byte_count": 1000,
            "index_type": INDEX_TYPE,
            "dimension": INDEX_DIMENSION,
            "ntotal": 4096,
            "nlist": INDEX_NLIST,
            "nprobe": INDEX_NPROBE,
            "metric": "l2",
            "read_index_seconds_decimal": "0.5",
            "reconstruct_seconds_decimal": "0.5",
        },
        "runtime": {
            "python_version": "3.11.5",
            "torch_version": "2.15.0",
            "torchaudio_version": "2.11.1",
            "faiss_version": "1.13.0",
            "faiss_build": "cpu-avx2",
            "numpy_version": "1.26.4",
            "device": "cpu",
            "threads": 4,
            "omp_threads": 1,
            "openblas_threads": 1,
            "deterministic_algorithms": True,
        },
        "query": {
            "source_audio_path": "/caller/data/source_ljspeech_lj001-0001.wav",
            "source_audio_sha256": SOURCE_AUDIO_SHA256,
            "source_audio_byte_count": SOURCE_AUDIO_BYTES,
            "sample_rate_hz": 16000,
            "duration_seconds_decimal": "9.655",
            "feature_dim": INDEX_DIMENSION,
            "frame_count": 950,
            "dtype": "float32",
            "all_finite": True,
            "query_sha256": "f" * 64,
        },
        "observations": {
            "retrieval_enabled": True,
            "index_assigned": True,
            "search_returned": False,
            "exit_kind": "native_crash",
            "exit_code": 139,
            "signal": 11,
            "traceback_path": "/caller/logs/crash.txt",
            "traceback_sha256": "1" * 64,
            "stderr_sha256": "2" * 64,
            "stdout_sha256": "3" * 64,
            "wall_seconds_decimal": "2.0",
            "score_finite": None,
            "result_sha256": None,
            "result_nonfinite_count": None,
        },
        "control": {
            "retrieval_enabled": False,
            "index_rate_decimal": "0.0",
            "index_assigned": False,
            "output_path": "/caller/out/control.wav",
            "output_sha256": "4" * 64,
            "output_byte_count": 1000,
            "wall_seconds_decimal": "2.0",
            "paired": True,
            "same_artifacts": True,
        },
        "rights": {
            "checkpoint_terms": "terms-checkpoint",
            "index_terms": "terms-index",
            "source_speaker_consent": "consent-source",
            "target_voice_consent": "consent-target",
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
    mutate("A025-speaker-count",
           set_nested(("checkpoint", "speaker_count"), 108))
    mutate("A026-speaker-info",
           set_nested(("checkpoint", "speaker_info_present"), True))
    mutate("A027-speaker-map-sha",
           set_nested(("checkpoint", "speaker_map_sha256"), "nope"))
    mutate("A028-speaker-map-unverified",
           set_nested(("checkpoint", "speaker_map_verified"), False))
    mutate("A029-terms-sha",
           set_nested(("checkpoint", "terms_sha256"), "nope"))
    mutate("A030-index-object", set_top("index", 3))
    mutate("A031-index-missing", del_nested(("index", "dimension")))
    mutate("A032-index-unknown", add_nested(("index",), "extra", 1))
    mutate("A033-index-name", set_nested(("index", "name"), "trained.index"))
    mutate("A034-index-path",
           set_nested(("index", "path"), "models/index"))
    mutate("A035-index-sha",
           set_nested(("index", "sha256"), "0" * 64 + "0"))
    mutate("A036-index-bytes-zero",
           set_nested(("index", "byte_count"), 0))
    mutate("A037-index-type",
           set_nested(("index", "index_type"), "IndexFlatL2"))
    mutate("A038-index-dimension",
           set_nested(("index", "dimension"), 256))
    mutate("A039-index-ntotal-zero",
           set_nested(("index", "ntotal"), 0))
    mutate("A040-index-nlist-zero",
           set_nested(("index", "nlist"), 0))
    mutate("A041-index-nlist-over",
           set_nested(("index", "nlist"), 5000))
    mutate("A042-index-nprobe",
           set_nested(("index", "nprobe"), 2))
    mutate("A043-index-metric",
           set_nested(("index", "metric"), "ip"))
    mutate("A044-index-read-text",
           set_nested(("index", "read_index_seconds_decimal"), "fast"))
    mutate("A045-index-read-negative",
           set_nested(("index", "read_index_seconds_decimal"), "-1.0"))
    mutate("A046-index-reconstruct-text",
           set_nested(("index", "reconstruct_seconds_decimal"), "abc"))
    mutate("A047-runtime-object", set_top("runtime", None))
    mutate("A048-runtime-missing", del_nested(("runtime", "device")))
    mutate("A049-runtime-unknown", add_nested(("runtime",), "extra", 1))
    mutate("A050-python-version",
           set_nested(("runtime", "python_version"), "3.12.1"))
    mutate("A051-torch-version",
           set_nested(("runtime", "torch_version"), "2.4.1"))
    mutate("A052-torchaudio-version",
           set_nested(("runtime", "torchaudio_version"), "2.6.0"))
    mutate("A053-faiss-old",
           set_nested(("runtime", "faiss_version"), "1.12.0"))
    mutate("A054-faiss-bad",
           set_nested(("runtime", "faiss_version"), "faiss"))
    mutate("A055-faiss-build-empty",
           set_nested(("runtime", "faiss_build"), ""))
    mutate("A056-numpy-version",
           set_nested(("runtime", "numpy_version"), "2.0.0"))
    mutate("A057-device",
           set_nested(("runtime", "device"), "cuda"))
    mutate("A058-threads-zero",
           set_nested(("runtime", "threads"), 0))
    mutate("A059-threads-over",
           set_nested(("runtime", "threads"), 65))
    mutate("A060-omp-zero",
           set_nested(("runtime", "omp_threads"), 0))
    mutate("A061-openblas-over",
           set_nested(("runtime", "openblas_threads"), 65))
    mutate("A062-deterministic",
           set_nested(("runtime", "deterministic_algorithms"), False))
    mutate("A063-query-object", set_top("query", []))
    mutate("A064-query-missing", del_nested(("query", "dtype")))
    mutate("A065-query-unknown", add_nested(("query",), "extra", 1))
    mutate("A066-source-path-relative",
           set_nested(("query", "source_audio_path"), "source.wav"))
    mutate("A067-source-sha",
           set_nested(("query", "source_audio_sha256"), "a" * 64))
    mutate("A068-source-bytes",
           set_nested(("query", "source_audio_byte_count"), 1))
    mutate("A069-sample-rate",
           set_nested(("query", "sample_rate_hz"), 44100))
    mutate("A070-duration",
           set_nested(("query", "duration_seconds_decimal"), "10.0"))
    mutate("A071-feature-dim",
           set_nested(("query", "feature_dim"), 256))
    mutate("A072-frame-count-zero",
           set_nested(("query", "frame_count"), 0))
    mutate("A073-frame-count-bool",
           set_nested(("query", "frame_count"), False))
    mutate("A074-dtype",
           set_nested(("query", "dtype"), "float64"))
    mutate("A075-all-finite",
           set_nested(("query", "all_finite"), False))
    mutate("A076-query-sha",
           set_nested(("query", "query_sha256"), "nope"))
    mutate("A077-observations-object", set_top("observations", "x"))
    mutate("A078-observations-missing",
           del_nested(("observations", "exit_kind")))
    mutate("A079-observations-unknown",
           add_nested(("observations",), "extra", 1))
    mutate("A080-retrieval-disabled",
           set_nested(("observations", "retrieval_enabled"), False))
    mutate("A081-index-not-assigned",
           set_nested(("observations", "index_assigned"), False))
    mutate("A082-search-returned-int",
           set_nested(("observations", "search_returned"), 0))
    mutate("A083-exit-kind",
           set_nested(("observations", "exit_kind"), "segfault"))
    mutate("A084-native-signal-none",
           set_nested(("observations", "signal"), None))
    mutate("A085-native-exit-none",
           set_nested(("observations", "exit_code"), None))
    mutate("A086-native-exit-mismatch",
           set_nested(("observations", "exit_code"), 1))
    mutate("A087-native-traceback-none",
           set_nested(("observations", "traceback_path"), None))
    mutate("A088-native-traceback-sha-none",
           set_nested(("observations", "traceback_sha256"), None))
    mutate("A089-native-score-finite",
           set_nested(("observations", "score_finite"), True))
    mutate("A090-native-result-sha",
           set_nested(("observations", "result_sha256"), "9" * 64))
    mutate("A091-uncaught-signal",
           set_nested(("observations", "exit_kind"), "uncaught_exception"))
    mutate("A092-uncaught-exit-zero",
           set_nested(("observations", "exit_kind"), "uncaught_exception"))
    mutate("A093-clean-exit-crash",
           set_nested(("observations", "exit_kind"), "clean"))
    mutate("A094-control-object", set_top("control", []))
    mutate("A095-control-missing", del_nested(("control", "paired")))
    mutate("A096-control-unknown", add_nested(("control",), "extra", 1))
    mutate("A097-control-enabled",
           set_nested(("control", "retrieval_enabled"), True))
    mutate("A098-control-rate",
           set_nested(("control", "index_rate_decimal"), "0.5"))
    mutate("A099-control-index",
           set_nested(("control", "index_assigned"), True))
    mutate("A100-control-path",
           set_nested(("control", "output_path"), "out.wav"))
    mutate("A101-control-sha",
           set_nested(("control", "output_sha256"), "nope"))
    mutate("A102-control-bytes",
           set_nested(("control", "output_byte_count"), 0))
    mutate("A103-control-wall",
           set_nested(("control", "wall_seconds_decimal"), "nan"))
    mutate("A104-control-paired",
           set_nested(("control", "paired"), False))
    mutate("A105-control-same-artifacts",
           set_nested(("control", "same_artifacts"), False))
    mutate("A106-rights-object", set_top("rights", "x"))
    mutate("A107-rights-missing", del_nested(("rights", "output_use")))
    mutate("A108-rights-unknown", add_nested(("rights",), "extra", 1))
    mutate("A109-rights-checkpoint-terms",
           set_nested(("rights", "checkpoint_terms"), ""))
    mutate("A110-rights-consent",
           set_nested(("rights", "source_speaker_consent"), ""))
    mutate("A111-rights-output-use",
           set_nested(("rights", "output_use"), "x" * 201))
    mutate("A112-rights-review",
           set_nested(("rights", "review_id"), "Bad"))
    mutate("A113-rights-cohort",
           set_nested(("rights", "cohort_id"), ""))
    mutate("A114-exit-code-float",
           set_nested(("observations", "exit_code"), 1.5))
    mutate("A115-ntotal-float",
           set_nested(("index", "ntotal"), 4096.0))
    mutate("A116-duration-float",
           set_nested(("query", "duration_seconds_decimal"), 9.655))
    mutate("A117-wall-zero",
           set_nested(("observations", "wall_seconds_decimal"), "0"))
    mutate("A118-traceback-relative",
           set_nested(("observations", "traceback_path"), "logs/crash.txt"))
    mutate("A119-signal-range",
           set_nested(("observations", "signal"), 32))
    mutate("A120-speaker-count-bool",
           set_nested(("checkpoint", "speaker_count"), True))

    rejected = sum(1 for case in cases if case["status"] == "rejected")
    return {
        "summary": {
            "case_count": len(cases),
            "rejected_count": rejected,
            "accepted_schema_controls": 1 if accepted["accepted"] else 0,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "runtime_invoked": False,
            "audio_read": False,
            "weights_loaded": False,
            "index_loaded": False,
            "faiss_executed": False,
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
            "audio_read": False,
            "weights_loaded": False,
            "faiss_executed": False,
        },
        "cases": cases,
    }


def admission_contract_block() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "scope": "task_local_retrieval_reproducer_metadata_only",
        "manifest_fields": list(MANIFEST_FIELDS),
        "candidate_fields": list(CANDIDATE_FIELDS),
        "checkpoint_fields": list(CHECKPOINT_FIELDS),
        "index_fields": list(INDEX_FIELDS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "query_fields": list(QUERY_FIELDS),
        "observation_fields": list(OBSERVATION_FIELDS),
        "control_fields": list(CONTROL_FIELDS),
        "rights_fields": list(RIGHTS_FIELDS),
        "required_checkpoint_name": CHECKPOINT_NAME,
        "required_index_name": INDEX_NAME,
        "required_index_type": INDEX_TYPE,
        "required_index_dimension": INDEX_DIMENSION,
        "required_index_nlist": INDEX_NLIST,
        "required_index_nprobe": INDEX_NPROBE,
        "required_speaker_count": INDEX_SPEAKERS,
        "required_search_k": SEARCH_K,
        "required_source_audio_sha256": SOURCE_AUDIO_SHA256,
        "required_source_audio_byte_count": SOURCE_AUDIO_BYTES,
        "required_sample_rate_hz": 16000,
        "required_duration_seconds_decimal": "9.655",
        "required_dtype": "float32",
        "required_torch_version": "2.15.0",
        "required_torchaudio_version": "2.11.1",
        "minimum_faiss_version": "1.13.0",
        "exit_kinds": list(EXIT_KINDS),
        "control_index_rate_decimal": "0.0",
        "rejections": (
            "unknown/missing field, non-object, duplicate key, nonfinite JSON, "
            "non-canonical path, bad SHA-256, wrong revision/dimension/metric, "
            "unverified speaker map, out-of-range index metadata or thread "
            "count, inconsistent exit kind/signal/exit code, non-paired "
            "control and empty rights references"),
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
        "model_native_sample_rate_hz": 40000,
        "preserved": True,
        "provider_created": False,
        "sdk_callback_invoked": False,
    }


def _scope() -> dict:
    return {
        "task_local_only": True,
        "source_present": True,
        "weights_present": False,
        "index_present": False,
        "runtime_present": False,
        "faiss_executed": False,
        "model_executed": False,
        "weights_loaded": False,
        "audio_read": False,
        "voice_conversion": False,
        "retrieval_enabled_conversion": False,
        "crash_reproduced": False,
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
        "faiss_or_torch_loaded": False,
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
        "inventory_disposition": "sdk-tool",
        "reopen_condition": (
            "Supply the pinned p226 checkpoint, IVF1161 Flat index, locked "
            "FAISS/Torch runtime, retained crash artifact and paired "
            "no-retrieval control, verified 109-entry speaker map, reviewed "
            "terms and consents, rights-cleared cohort and the agreed Voice "
            "quality/timing/listening protocol. Then reproduce the exact "
            "failure and control on the pinned runtime and review the result "
            "at an exact head. Until then this task stays DEFER."),
    }


def _qualification() -> dict:
    return {
        "status": "not_qualified",
        "not_qualified": True,
        "readiness": "incomplete",
        "real_result_present": False,
        "source_present": True,
        "weights_present": False,
        "index_present": False,
        "runtime_present": False,
        "crash_reproduction_result": False,
        "crash_root_cause_result": False,
        "paired_control_result": False,
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
            "for RVC FAISS retrieval: pinned source/retrieval call sites, "
            "fail-closed absence and runtime probes, a deterministic model of "
            "the retrieval/control branch contract, and a strict admission "
            "schema for a future crash reproducer. No checkpoint, index, "
            "runtime, audio, retrieval, conversion, listening, timing or "
            "release result."),
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
        "retrieval_isolation": dict(RETRIEVAL_ISOLATION),
        "failure_and_control": dict(FAILURE_AND_CONTROL),
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
    "source_presence", "retrieval_isolation", "failure_and_control",
    "source_revision", "source_pins", "boundary_pins", "board_file_pinned",
    "board_status_is_observation_only", "board_row_fields",
    "board_row_projection", "board_row_sha256", "linked_rows",
    "linked_rows_sha256", "absence_policy", "absence_probes",
    "home_absence_probes", "observed_incomplete_paths",
    "runtime_probe_modules", "required_artifacts", "exact_blockers",
    "release_gates", "voice_profile_requirements", "quality_outcomes",
    "timing_requirements", "required_results", "historical_execution",
    "non_claims", "admission_contract", "admission_summary",
    "admission_control",
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
        if artifact.get("present") is not False or artifact.get("blocked") is not True:
            raise ValueError("artifact_not_blocked")
    if len(document["exact_blockers"]) != 7:
        raise ValueError("blocker_count")
    artifact_ids = {row["id"] for row in document["required_artifacts"]}
    gate_ids = {row["id"] for row in document["release_gates"]}
    for blocker in document["exact_blockers"]:
        if blocker.get("status") != "open" or blocker.get("qualifies") is not False:
            raise ValueError("blocker_not_open")
        if blocker.get("artifact_id") not in artifact_ids:
            raise ValueError("blocker_artifact")
        for gate in blocker.get("linked_gates", []):
            if gate not in gate_ids:
                raise ValueError("blocker_gate")
    summary = document["admission_summary"]
    if summary.get("case_count") != 120 or summary.get("rejected_count") != 120:
        raise ValueError("admission_case_count")
    if summary.get("accepted_schema_controls") != 1:
        raise ValueError("admission_control_count")
    if summary.get("qualifying_results") != 0:
        raise ValueError("admission_qualifying")
    if document["admission_control"].get("qualifies") is not False:
        raise ValueError("admission_control_qualifies")
    if document["historical_execution"].get("qualifies") is not False:
        raise ValueError("historical_qualifies")
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
        "retrieval_isolation": contract["retrieval_isolation"],
        "failure_and_control": contract["failure_and_control"],
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

# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen fixture surface for the online multichannel WPE evidence package.

Signal definitions live in ``reference.py``; this module exposes read-only
digests, canonical serialization and the three-repeat check used by
``verify.py``. It reads no audio files and imports no external DSP package.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
TASK_PREFIX = "docs/task-evidence/online-multichannel-wpe/"
REPORT_FILE = HERE / "report.json"
SIDECAR_FILE = HERE / "report.json.sha256"
CONTRACT_FILE = HERE / "contract.json"
ADAPTER_FILE = HERE / "adapter.json"
PROVIDER_FILE = HERE / "provider.json"
PINS_FILE = HERE / "SOURCES.sha256"
CROSSCHECK_FILE = HERE / "crosscheck_vectors.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return reference.canonical_report(report)[0].encode("utf-8") + b"\n"


def frozen_digests() -> Dict[str, str]:
    """Digests of pinned generated signals, never of recorded audio."""
    digests: Dict[str, str] = {
        "clean_source": reference.tensor_digest(reference.clean_source()),
        "far_end_source": reference.tensor_digest(reference.far_end_source()),
    }
    for name, spec in reference.ROOM_SPECS.items():
        first, second = reference.synthetic_rir_pair(spec)
        digests[name + "_rir_mic0"] = reference.tensor_digest(first)
        digests[name + "_rir_mic1"] = reference.tensor_digest(second)
    return digests


def repeat_probe() -> Dict[str, Any]:
    """Three cold-start passes over one pinned 2x160-sample-grid probe."""
    probe = reference.causal_probe_pair()
    digests: List[str] = []
    for _ in range(3):
        status, output = reference.process_whole_clip(probe)
        if status is not reference.Status.OK:
            raise RuntimeError("repeat probe failed: " + status.value)
        digests.append(reference.tensor_digest(output))
    return {
        "input_samples": len(probe[0]),
        "input_channels": reference.INPUT_CHANNELS,
        "input_digests": [reference.tensor_digest(probe[0]),
                          reference.tensor_digest(probe[1])],
        "runs": 3,
        "output_digests": digests,
        "byte_identical": len(set(digests)) == 1,
    }

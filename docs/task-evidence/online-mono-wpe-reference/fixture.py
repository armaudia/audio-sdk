# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen fixture surface for the online mono WPE evidence package.

The signal definitions live in ``reference.py`` (preserved from the partial
work); this module exposes only read-only digests, canonical serialization and
the three-repeat check used by ``verify.py``. It generates no assets, reads no
audio files and does not import numpy, scipy or pystoi.
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
BASE_COMMIT = "549dec7fd6e0d9a930a968c77b7415d3c6158710"
TASK_PREFIX = "docs/task-evidence/online-mono-wpe-reference/"
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
    """Digests of the pinned generated signals, never of recorded audio."""
    digests = {"clean_source": reference.tensor_digest(reference.clean_source())}
    for name, spec in reference.ROOM_SPECS.items():
        rir = reference.synthetic_rir(spec["rt60_ms"], spec["dr_db"], spec["seed"])
        digests[name + "_rir"] = reference.tensor_digest(rir)
    return digests


def repeat_probe() -> Dict[str, Any]:
    """Three cold-start passes over one pinned 160-sample-grid probe."""
    probe = reference.causal_probe_signal()
    digests: List[str] = []
    for _ in range(3):
        status, output = reference.process_whole_clip(probe)
        if status is not reference.Status.OK:
            raise RuntimeError("repeat probe failed: " + status.value)
        digests.append(reference.tensor_digest(output))
    return {
        "input_samples": len(probe),
        "input_digest": reference.tensor_digest(probe),
        "runs": 3,
        "output_digests": digests,
        "byte_identical": len(set(digests)) == 1,
    }

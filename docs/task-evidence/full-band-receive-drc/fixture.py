# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only frozen fixture surface for the receive DRC evidence package.

Signal definitions and the DRC engine live in ``reference.py``. This module
only exposes canonical serialization, read-only digests, pinned source paths
and the three cold-start repeat probe used by verification. It writes nothing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
TASK_PREFIX = "docs/task-evidence/full-band-receive-drc/"
REPORT_FILE = HERE / "report.json"
SIDECAR_FILE = HERE / "report.json.sha256"
CONTRACT_FILE = HERE / "contract.json"
ADAPTER_FILE = HERE / "adapter.json"
PROVIDER_FILE = HERE / "provider.json"
PINS_FILE = HERE / "SOURCES.sha256"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return reference.canonical_report(report)[0].encode("utf-8") + b"\n"


def frozen_digests() -> Dict[str, Any]:
    """Digests of generated synthetic signals; no recorded audio is involved."""
    digests = {name: reference.tensor_digest(generator())
               for name, generator in reference.fixture_generators().items()}
    return {
        "fixture_digest": reference.fixture_digest(),
        "tensor_digests": digests,
    }


def repeat_probe() -> Dict[str, Any]:
    return reference.repeat_probe()

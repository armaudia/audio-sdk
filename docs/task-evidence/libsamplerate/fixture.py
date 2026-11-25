# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only frozen fixture surface for the task-local rate evidence package.

Signal generation and the reference converter live in ``reference.py``. This
module exposes only canonical report bytes, fixture digests and the three
cold-start repeat probe. It writes no file and never touches a real corpus.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path("/Users/htsakanyan/workspace/audio/audioml")
TASK_PREFIX = reference.TASK_PREFIX
BASE_COMMIT = reference.BASE_COMMIT
REPORT_FILE = HERE / "report.json"
SIDECAR_FILE = HERE / "report.json.sha256"
CONTRACT_FILE = HERE / "contract.json"
ADAPTER_FILE = HERE / "adapter.json"
PROVIDER_FILE = HERE / "provider.json"
PINS_FILE = HERE / "SOURCES.sha256"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    text, _canonical_digest = reference.canonical_report(report)
    return text.encode("utf-8") + b"\n"


def frozen_digests() -> Dict[str, Any]:
    payload = {
        name: {
            "samples": len(generator()),
            "sha256": reference.scorer.tensor_digest(generator()),
        }
        for name, generator in sorted(reference.fixture_generators().items())
    }
    return {
        "fixture_digest": reference.fixture_digest(),
        "tensor_digests": payload,
    }


def repeat_probe() -> Dict[str, Any]:
    return reference.repeat_probe()

"""Installed third-party fixture for SDK-FND-ENGINE (proposal-only, model-free)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable

from .providers import Activity, Gain, Outcome, Transition

FIXTURE_ID = "third-party/engine-v1-fixture/0.1"
FIXTURE_VERSION = "0.1.0"


def installed_provider_factories() -> dict[str, Callable[[str], Any]]:
    """Factories supplied only by the installed external package."""
    return {
        "third_party.gain.v0": lambda instance_id: Gain("third_party.gain.v0", instance_id),
        "third_party.transition.v0": lambda instance_id: Transition(
            "third_party.transition.v0", instance_id),
        "third_party.activity.v0": lambda instance_id: Activity(
            "third_party.activity.v0", instance_id),
    }


def installed_provider_ids() -> tuple[str, ...]:
    return tuple(sorted(installed_provider_factories()))


def source_digest() -> str:
    """Stable digest over this installed package's Python sources."""
    package = Path(__file__).resolve().parent
    payload = b"".join(path.read_bytes() for path in sorted(package.glob("*.py")))
    return hashlib.sha256(payload).hexdigest()


__all__ = [
    "FIXTURE_ID",
    "FIXTURE_VERSION",
    "Activity",
    "Gain",
    "Outcome",
    "Transition",
    "installed_provider_factories",
    "installed_provider_ids",
    "source_digest",
]

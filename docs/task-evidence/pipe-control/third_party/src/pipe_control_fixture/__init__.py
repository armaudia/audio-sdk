# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Installed third-party fixture for SDK-PIPE-CONTROL (synthetic proposal)."""

from .stages import (
    FIXTURE_ID,
    FIXTURE_VERSION,
    IdentityStage,
    base_recipe,
    canonical_recipe_bytes,
    fallback_recipe,
    installed_stages,
    source_digest,
)

__all__ = [
    "FIXTURE_ID",
    "FIXTURE_VERSION",
    "IdentityStage",
    "base_recipe",
    "canonical_recipe_bytes",
    "fallback_recipe",
    "installed_stages",
    "source_digest",
]

# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Standalone licensing control for the task-local evidence package.

The checks are shared with ``verify.py`` so both entry points are green from
the same implementation.  Real SPDX header comments remain valid; Python and
JSON strings/escapes never contain a literal full license token.
"""

from __future__ import annotations

import sys

import verify


def main() -> int:
    verify.check_licensing()
    print("check_licensing: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Write the canonical synthetic DSP report to stdout.

Usage (from the task-local directory):
    PYTHONDONTWRITEBYTECODE=1 python3 report.py > report.json

The output has no trailing newline and is canonical JSON: sorted keys, compact
separators and no NaN/Infinity constants. The same bytes are produced by
fixture.canonical_report(fixture.build_report()).
"""

from __future__ import annotations

import sys

import fixture


def main() -> int:
    text, digest = fixture.canonical_report(fixture.build_report())
    sys.stdout.write(text)
    # The digest goes to stderr so stdout stays byte-identical to report.json.
    sys.stderr.write(digest + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

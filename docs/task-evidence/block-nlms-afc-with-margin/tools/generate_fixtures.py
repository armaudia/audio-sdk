"""Generate the pinned synthetic f32 fixtures for the AFC-margin evidence.

Usage (from the task-local directory):
    PYTHONDONTWRITEBYTECODE=1 python3 tools/generate_fixtures.py

Writes only files under ../fixtures and refreshes ../fixtures/FIXTURES.sha256.
Every sample comes from fixture.py; no recording, model or download is used.
"""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
TASK = TOOLS.parent
FIXTURES = TASK / "fixtures"
sys.path.insert(0, str(TASK))

import fixture  # noqa: E402


def write_f32(path: Path, values) -> None:
    data = b"".join(struct.pack("<f", float(value)) for value in values)
    path.write_bytes(data)


def main() -> int:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    samples = fixture.synthetic_fixtures()
    digests = []
    for name in sorted(samples):
        path = FIXTURES / name
        write_f32(path, samples[name])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        digests.append(f"{digest}  {name}\n")
    manifest = "".join(digests)
    (FIXTURES / "FIXTURES.sha256").write_text(manifest, encoding="utf-8")
    sys.stdout.write(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate or check the pinned deterministic synthetic fixtures."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import struct

import afc_reference as afc

TASK = Path(__file__).resolve().parents[1]
FIXTURES = TASK / "fixtures"
MANIFEST = FIXTURES / "FIXTURES.sha256"


def generators() -> dict[str, tuple[float, ...]]:
    """All fixtures are analytic or seeded LCG; no external input is read."""
    playback = afc.speech_like(30, seed=4242)
    return {
        "playback_a.f32": afc.speech_like(200, seed=20261028),
        "playback_b.f32": afc.speech_like(160, seed=555),
        "near_end.f32": afc.speech_like(160, seed=777),
        "reference_asset.f32": afc.make_asset(playback),
        "impulse.f32": afc.impulse(8),
        "step.f32": afc.step(12, onset_frame=4),
        "silence.f32": (0.0,) * (40 * afc.FRAME_SAMPLES),
    }


def f32_bytes(values: tuple[float, ...]) -> bytes:
    return b"".join(struct.pack("<f", float(value)) for value in values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify existing fixtures and manifest, write nothing")
    args = parser.parse_args()

    payloads = {name: f32_bytes(values) for name, values in generators().items()}
    digests = {name: hashlib.sha256(data).hexdigest()
               for name, data in payloads.items()}
    manifest_text = "".join("%s  %s\n" % (digests[name], name)
                            for name in sorted(digests))

    if args.check:
        for name, data in payloads.items():
            if (FIXTURES / name).read_bytes() != data:
                raise SystemExit("fixture drift: %s" % name)
        if MANIFEST.read_text(encoding="utf-8") != manifest_text:
            raise SystemExit("fixture manifest drift")
        print("fixtures and manifest verified")
        return 0

    FIXTURES.mkdir(parents=True, exist_ok=True)
    for name, data in payloads.items():
        (FIXTURES / name).write_bytes(data)
    MANIFEST.write_text(manifest_text, encoding="utf-8")
    print(manifest_text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

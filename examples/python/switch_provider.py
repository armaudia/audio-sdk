# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Process the same WAV with each built-in provider and write two outputs."""
from __future__ import annotations

import argparse
import hashlib
import struct

from audio_sdk import FRAME_SAMPLES, Registry
from wav import read_mono16k, write_mono16k


def run(provider: str, source: list[float]) -> list[float]:
    output = []
    registry = Registry()
    try:
        with registry.session(provider) as session:
            for first in range(0, len(source), FRAME_SAMPLES):
                block = source[first:first + FRAME_SAMPLES]
                valid = len(block)
                if valid < FRAME_SAMPLES:
                    block.extend([0.0] * (FRAME_SAMPLES - valid))
                enhanced, result = session.process(
                    block, valid_count=valid,
                    final=valid < FRAME_SAMPLES)
                output.extend(enhanced[result.valid_offset:
                                       result.valid_offset + result.valid_count])
            for enhanced, result in session.drain():
                output.extend(enhanced[result.valid_offset:
                                       result.valid_offset + result.valid_count])
    finally:
        registry.close()
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--speex", default="speex.wav")
    parser.add_argument("--highpass", default="highpass.wav")
    args = parser.parse_args()
    source = read_mono16k(args.input)
    if not source:
        raise ValueError("input WAV is empty")
    for provider, path, delay in (
        ("speex.ns.v0", args.speex, 160),
        ("dsp.highpass80.v0", args.highpass, 0),
    ):
        samples = run(provider, source)
        write_mono16k(path, samples)
        digest = hashlib.sha256(
            b"".join(struct.pack("<f", sample) for sample in samples)
        ).hexdigest()
        print(
            f"{provider}: contract=0.1 buffering_delay={delay} "
            f"output_samples={len(samples)} sha256={digest} file={path}"
        )


if __name__ == "__main__":
    main()

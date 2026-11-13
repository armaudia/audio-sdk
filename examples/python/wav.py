"""Minimal PCM16 mono/16 kHz WAV reader/writer using only the standard library."""
from __future__ import annotations

import wave


def read_mono16k(path: str) -> list[float]:
    with wave.open(path, "rb") as source:
        if (source.getnchannels(), source.getframerate(), source.getsampwidth()) != (
            1, 16000, 2
        ):
            raise ValueError("input WAV must be PCM16 mono at 16 kHz")
        raw = source.readframes(source.getnframes())
    return [int.from_bytes(raw[i:i + 2], "little", signed=True) / 32768.0
            for i in range(0, len(raw), 2)]


def write_mono16k(path: str, samples) -> None:
    with wave.open(path, "wb") as target:
        target.setnchannels(1)
        target.setframerate(16000)
        target.setsampwidth(2)
        pcm = bytearray()
        for sample in samples:
            value = max(-1.0, min(1.0, float(sample)))
            integer = max(-32768, min(32767, round(value * 32768.0)))
            pcm.extend(int(integer).to_bytes(2, "little", signed=True))
        target.writeframes(pcm)

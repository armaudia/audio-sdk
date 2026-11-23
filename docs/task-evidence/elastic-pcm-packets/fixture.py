"""Model-free fixture for the proposed elastic PCM and packet interface.

PCM timing and timestamped packet recovery are deliberately separate. The
fixture uses exact rational ratios and finite flush; it adds no SDK runtime,
provider, codec, concealment policy or public ABI change.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Optional, Sequence

CONTRACT_ID = "audio-sdk/elastic-pcm-packets/0.1"
SAMPLE_RATE_HZ = 16000
NS_PER_SAMPLE = 62500


class Status(str, Enum):
    OK = "ok"
    NOT_READY = "not_ready"
    END_OF_STREAM = "end_of_stream"
    REJECTED_RATIO = "rejected_ratio"
    REJECTED_SOURCE_GAP = "rejected_source_gap"
    REJECTED_BACKPRESSURE = "rejected_backpressure"
    REJECTED_PACKET = "rejected_packet"
    REJECTED_UNRECOVERABLE = "rejected_unrecoverable"
    CLOSED = "closed"


def parse_ratio(value: str | Fraction) -> Fraction:
    ratio = value if isinstance(value, Fraction) else Fraction(value)
    if ratio <= 0:
        raise ValueError("ratio must be positive")
    return ratio


@dataclass(frozen=True)
class PcmChunk:
    source_start: int
    samples: tuple[float, ...]

    def check(self) -> Optional[Status]:
        if self.source_start < 0 or not self.samples:
            return Status.REJECTED_SOURCE_GAP
        if any(not math.isfinite(sample) for sample in self.samples):
            return Status.REJECTED_SOURCE_GAP
        return None


@dataclass
class TimeSegment:
    output_start: int
    source_start: int
    ratio: Fraction
    samples: tuple[float, ...]
    released: bool = False

    @property
    def output_count(self) -> int:
        return len(self.samples) // self.ratio

    @property
    def output_end(self) -> int:
        return self.output_start + self.output_count

    def source_index(self, output_index: int) -> int:
        return self.source_start + int((output_index - self.output_start) * self.ratio)

    def sample(self, output_index: int) -> float:
        return self.samples[self.source_index(output_index) - self.source_start]


@dataclass(frozen=True)
class PullResult:
    status: Status
    samples: tuple[float, ...]
    source_indices: tuple[int, ...]
    consumed_count: int
    produced_count: int


class ElasticStream:
    """Bounded variable-count PCM timeline with exact source mapping."""

    def __init__(self, stream_id: str, ratio: str | Fraction = "1",
                 max_queued_samples: int = 1024,
                 clock_id: str = "monotonic-reference-v0") -> None:
        if max_queued_samples < 1:
            raise ValueError("max_queued_samples must be positive")
        self.stream_id = stream_id
        self.ratio = parse_ratio(ratio)
        self.max_queued_samples = max_queued_samples
        self.clock_id = clock_id
        self._segments: list[TimeSegment] = []
        self._source_cursor = 0
        self._output_cursor = 0
        self._pulled = 0
        self._pending_input_samples = 0
        self.consumed_count = 0
        self.produced_count = 0
        self.eos = False
        self.closed = False

    @property
    def available_output(self) -> int:
        return self._output_cursor - self._pulled

    def set_ratio(self, ratio: str | Fraction) -> Status:
        if self.closed or self.eos:
            return Status.CLOSED
        try:
            self.ratio = parse_ratio(ratio)
        except (ValueError, ZeroDivisionError):
            return Status.REJECTED_RATIO
        return Status.OK

    def push(self, chunk: PcmChunk) -> Status:
        if self.closed or self.eos:
            return Status.CLOSED
        if chunk.check() is not None:
            return Status.REJECTED_SOURCE_GAP
        if chunk.source_start != self._source_cursor:
            return Status.REJECTED_SOURCE_GAP
        if self._pending_input_samples + len(chunk.samples) > self.max_queued_samples:
            return Status.REJECTED_BACKPRESSURE
        segment = TimeSegment(self._output_cursor, chunk.source_start,
                              self.ratio, chunk.samples)
        self._segments.append(segment)
        self._output_cursor += segment.output_count
        self._source_cursor += len(chunk.samples)
        self._pending_input_samples += len(chunk.samples)
        self.consumed_count += len(chunk.samples)
        return Status.OK

    def pull(self, limit_samples: int) -> PullResult:
        if self.closed:
            return PullResult(Status.CLOSED, (), (), self.consumed_count,
                              self.produced_count)
        if limit_samples < 1:
            return PullResult(Status.NOT_READY, (), (), self.consumed_count,
                              self.produced_count)
        if self.available_output == 0:
            status = Status.END_OF_STREAM if self.eos else Status.NOT_READY
            return PullResult(status, (), (), self.consumed_count,
                              self.produced_count)
        count = min(limit_samples, self.available_output)
        samples: list[float] = []
        indices: list[int] = []
        for output_index in range(self._pulled, self._pulled + count):
            segment = next(segment for segment in self._segments
                           if segment.output_start <= output_index < segment.output_end)
            samples.append(segment.sample(output_index))
            indices.append(segment.source_index(output_index))
        self._pulled += count
        self.produced_count += count
        for segment in self._segments:
            if not segment.released and self._pulled >= segment.output_end:
                segment.released = True
                self._pending_input_samples -= len(segment.samples)
        return PullResult(Status.OK, tuple(samples), tuple(indices),
                          self.consumed_count, self.produced_count)

    def flush(self) -> Status:
        if self.closed:
            return Status.CLOSED
        self.eos = True
        return Status.OK

    def close(self) -> None:
        self.closed = True
        self.eos = True
        self._segments.clear()
        self._pending_input_samples = 0


@dataclass(frozen=True)
class Packet:
    seq: int
    timestamp_ns: int
    payload: tuple[int, ...]
    kind: str

    def check(self) -> Optional[Status]:
        if self.seq < 0 or self.timestamp_ns < 0 or not self.payload:
            return Status.REJECTED_PACKET
        if any(not isinstance(value, int) or not 0 <= value <= 255
               for value in self.payload):
            return Status.REJECTED_PACKET
        if self.kind not in ("data", "parity", "recovered"):
            return Status.REJECTED_PACKET
        return None


@dataclass(frozen=True)
class PacketBlock:
    block_id: int
    packets: tuple[Packet, ...]
    parity: Packet

    def recover(self, missing_seqs: Sequence[int]) -> tuple[Status, tuple[Packet, ...]]:
        missing = tuple(sorted(set(missing_seqs)))
        if not missing:
            return Status.OK, ()
        if len(missing) > 1:
            return Status.REJECTED_UNRECOVERABLE, ()
        known = {packet.seq: packet for packet in self.packets}
        if missing[0] not in known:
            return Status.REJECTED_PACKET, ()
        parity_bytes = list(self.parity.payload)
        for seq, packet in known.items():
            if seq == missing[0]:
                continue
            parity_bytes = [a ^ b for a, b in zip(parity_bytes, packet.payload)]
        recovered = Packet(known[missing[0]].seq, known[missing[0]].timestamp_ns,
                           tuple(parity_bytes), "recovered")
        return Status.OK, (recovered,)


def make_block(block_id: int, first_seq: int, payloads: Sequence[Sequence[int]],
               first_timestamp_ns: int) -> tuple[Status, PacketBlock | None]:
    if not payloads or any(not payload for payload in payloads):
        return Status.REJECTED_PACKET, None
    width = len(payloads[0])
    if any(len(payload) != width for payload in payloads):
        return Status.REJECTED_PACKET, None
    packets = tuple(
        Packet(first_seq + index, first_timestamp_ns + index * NS_PER_SAMPLE,
               tuple(payload), "data")
        for index, payload in enumerate(payloads)
    )
    parity_bytes = [0] * width
    for packet in packets:
        parity_bytes = [a ^ b for a, b in zip(parity_bytes, packet.payload)]
    parity = Packet(first_seq + len(packets),
                    packets[-1].timestamp_ns + NS_PER_SAMPLE,
                    tuple(parity_bytes), "parity")
    return Status.OK, PacketBlock(block_id, packets, parity)


def canonical_report(stream: ElasticStream,
                     pull: PullResult,
                     recovered: Sequence[Packet]) -> tuple[str, str]:
    payload = {
        "contract": CONTRACT_ID,
        "stream_id": stream.stream_id,
        "ratio": str(stream.ratio),
        "consumed_count": pull.consumed_count,
        "produced_count": pull.produced_count,
        "source_indices": list(pull.source_indices),
        "recovered": [
            {"seq": packet.seq, "timestamp_ns": packet.timestamp_ns}
            for packet in recovered
        ],
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()

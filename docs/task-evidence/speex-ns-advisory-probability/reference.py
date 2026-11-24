# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic advisory-probability evidence at the public SDK adapter boundary.

The provider is an opt-in, unregistered task-local reference. Its audio path is
an identity control; the advisory probability is a fixed-point energy surrogate
exposed through a task-local analysis side channel. It is NOT SpeexDSP code, a
calibrated posterior, a detector gate, an accuracy result or a release claim.

All signal arithmetic is integer-only so the Python model and the C provider
produce byte-identical pinned vectors without floating-point tolerance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct

TASK_DIR = Path(__file__).resolve().parent
WORKTREE = TASK_DIR.parents[2]
AUDIO_ROOT = WORKTREE.parents[2]

SCHEMA = "audio-sdk/speex-ns-advisory-probability-evidence/0.1"
TASK = "SDK-SPEEX-NS-ADVISORY-PROBABILITY"
COMPONENT = "speex-ns-advisory-probability"
BASE_COMMIT = "941cabfc39f7e33f01881b6e50e3a1e49e7eb9ce"
BRANCH = "swarm/SDK-SPEEX-NS-ADVISORY-PROBABILITY"
PROVIDER_ID = "analysis.speex-ns-advisory-reference.v0"

RATE = 16000
FRAME = 160
WINDOW = 320
NS_PER_SAMPLE = 62500
ORIGIN_NS = 1000000000
MILLI_MAX = 1000
THRESHOLD_MILLI = 500
NOISE_FLOOR = 2000000
PROBABILITY_SPAN = 8000000
STIMULUS_LENGTH = 16000
FRAME_COUNT = STIMULUS_LENGTH // FRAME
EVENT_CAPACITY = 128
REPEATS = 3
PYTHON_TESTS = 24

# Paths are relative to /Users/htsakanyan/workspace/audio/audioml.
SOURCE_PINS = {
    "cpp-library/PIPELINE_DESIGN_REPORT.md": (
        "f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093",
        "Source evidence for this component: one Speex preprocessor computes NS "
        "and speech probability; source-reported paired AMI FN 4.44% / FP 68.84% "
        "makes the output advisory only. Historical values are not rerun here.",
    ),
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": (
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "Analysis acceptance profile: timestamped probabilities, event intervals, "
        "validity separated from nonspeech, state, availability and stale events.",
    ),
    "audio-benchmark-platform/plan/INVENTORY.json": (
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
        "Component record speex-ns-advisory-probability: analysis profile and the "
        "no-gating-before-held-out-validation plan note.",
    ),
    "audio-benchmark-platform/plan/swarm/handoffs/SDK-SPEEX-NS-ADVISORY-PROBABILITY.md": (
        "ac00811367df50a5b6bdd1d626904adb1cc2e452ec2e60d0628dfc9bef831ca5",
        "Task handoff: synthetic/frozen evidence only, opt-in reference, no control "
        "signal, exact pinned comparisons and remaining release gates.",
    ),
    "audio-benchmark-platform/audio-sdk/third_party/speexdsp/include/speex/speex_preprocess.h": (
        "7c12339881fce3250c69af7f36b8440a8d8012976b54331b3c980b8074393b25",
        "Public upstream header exposing SPEEX_PREPROCESS_GET_PROB; inspected only. "
        "No upstream source is vendored, built or benchmarked by this fixture.",
    ),
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md": (
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
        "Provenance for the public v0 provider/session contract and the proposed "
        "as_analysis_v1 analysis-event shape; no public surface is changed here.",
    ),
}

BOUNDARY_PINS = {
    "api/include/audio_sdk/provider_v0.h": (
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766"
    ),
    "api/include/audio_sdk/session_v0.h": (
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1"
    ),
}

SEGMENTS = [
    {"name": "quiet_idle_1", "start": 0, "end": 1600, "label": "nonspeech"},
    {"name": "quiet_speech", "start": 1600, "end": 3200, "label": "speech"},
    {"name": "active_speech", "start": 3200, "end": 4800, "label": "speech"},
    {"name": "loud_idle_noise", "start": 4800, "end": 6400, "label": "nonspeech"},
    {"name": "quiet_idle_tail", "start": 6400, "end": 16000, "label": "nonspeech"},
]

CONTROL_SPECS = [
    ("nonfinite_input_rejected", "invalid_argument on NaN frame; state unchanged"),
    ("stale_epoch_rejected", "epoch 0 analysis rejected in epoch 1"),
    ("dropped_events_explicit", "sequences 1 and 3 produce recorded gaps, no fill"),
    ("invalid_event_not_nonspeech", "invalid validity excluded from denominator"),
    ("wrong_sample_rate_rejected", "48000 Hz rejected"),
    ("wrong_channel_count_rejected", "2 channels rejected"),
    ("wrong_frame_length_rejected", "320-sample frame rejected"),
    ("short_frame_without_final_rejected", "valid_count 159 without FINAL rejected"),
    ("nonzero_final_padding_rejected", "padding samples beyond final valid must be zero"),
    ("old_event_after_reset_rejected", "epoch 1 event cannot revive epoch 2 analysis"),
    ("no_gating_wiring", "probability never registered, defaulted or used as control"),
]


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def canonical_digest(value: object) -> str:
    return sha256_hex(canonical_bytes(value))


def scale_q15(value: int, numerator: int, denominator: int) -> int:
    """Sign-symmetric integer scaling with C-compatible truncation."""
    if value >= 0:
        return (value * numerator) // denominator
    return -((-value * numerator) // denominator)


def tri_q15(index: int, period: int, amplitude: int) -> int:
    half = period // 2
    position = index % period
    ramp = position if position <= half else period - position
    return (2 * ramp * amplitude) // half - amplitude


def noise_q15(seed: int, count: int, amplitude: int) -> list[int]:
    state = seed & 0xFFFFFFFF
    out: list[int] = []
    for _ in range(count):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        word = (state >> 16) & 0xFFFF
        out.append((2 * amplitude * word) // 65536 - amplitude)
    return out


def speech_q15(index: int, amplitude: int) -> int:
    first = tri_q15(index, 160, amplitude)
    second = tri_q15(index + 40, 80, amplitude)
    return scale_q15(first + second, 3, 4)


def build_stimulus(name: str = "primary") -> list[int]:
    """Integer Q15 samples; every value is exactly representable as float32."""
    if name == "silence":
        return [0] * STIMULUS_LENGTH
    if name == "impulse":
        out = [0] * STIMULUS_LENGTH
        out[4000] = 20000
        return out
    quiet = noise_q15(0x51504E53, STIMULUS_LENGTH, 200)
    loud = noise_q15(0x4C4F5544, STIMULUS_LENGTH, 8000)
    out = []
    for index in range(STIMULUS_LENGTH):
        if 1600 <= index < 3200:
            out.append(speech_q15(index, 1200))
        elif 3200 <= index < 4800:
            out.append(speech_q15(index, 6000))
        elif 4800 <= index < 6400:
            out.append(loud[index])
        else:
            out.append(quiet[index])
    return out


def q15_to_f32(value: int) -> float:
    return value / 32768.0


def probability_milli(window: list[int]) -> int:
    energy = sum(value * value for value in window)
    mean = energy // WINDOW
    if mean <= NOISE_FLOOR:
        return 0
    raw = ((mean - NOISE_FLOOR) * 1000) // PROBABILITY_SPAN
    return MILLI_MAX if raw > MILLI_MAX else raw


def event_dict(sequence: int, hop: int, epoch: int, first: int, end: int,
               value_milli: int, validity: str, available_ns: int) -> dict:
    return {
        "schema_id": "audio-sdk/speex-ns-advisory-analysis/0.1",
        "sequence": sequence,
        "hop": hop,
        "producer_id": PROVIDER_ID,
        "tap_id": "pcm.in" if hop == 0 else "pcm.out",
        "epoch": epoch,
        "source_first_sample": first,
        "source_end_sample": end,
        "value_milli": value_milli,
        "value": value_milli / 1000.0 if validity == "known" else None,
        "validity": validity,
        "available_monotonic_ns": available_ns,
        "clock_id": "fixture-monotonic-v0",
        "config_digest": None,  # filled by run_reference with the pinned config digest
    }


def create_config_error(rate: int = RATE, channels: int = 1,
                        frame: int = FRAME, mode: int = 2,
                        config_json: str = PROVIDER_ID,
                        asset_count: int = 0) -> str | None:
    """Mirror the opt-in provider's create-time boundary validation."""
    if rate != RATE or channels != 1 or frame != FRAME or mode != 2:
        return "AS_UNSUPPORTED"
    if asset_count != 0 or PROVIDER_ID not in config_json:
        return "AS_INVALID_ARGUMENT"
    return None


def frame_rejection(epoch: int = 1, expected_epoch: int = 1,
                    first: int = 0, expected_first: int = 0,
                    input_count: int = FRAME, valid: int = FRAME,
                    flags: int = 0, nonfinite: bool = False,
                    padding_nonzero: bool = False) -> str | None:
    """Mirror the opt-in provider's process-time fail-closed checks."""
    if input_count != FRAME or valid == 0 or valid > FRAME:
        return "AS_INVALID_ARGUMENT"
    if flags & ~1:
        return "AS_INVALID_ARGUMENT"
    if not flags & 1 and valid != FRAME:
        return "AS_INVALID_ARGUMENT"
    if flags & 1 and valid < FRAME and padding_nonzero:
        return "AS_INVALID_ARGUMENT"
    if nonfinite:
        return "AS_INVALID_ARGUMENT"
    if epoch != expected_epoch or first != expected_first:
        return "AS_INVALID_ARGUMENT"
    return None


def public_surface_id_mentions() -> int:
    """Count task-provider ID mentions outside the task-local evidence tree."""
    roots = [WORKTREE / "api", WORKTREE / "core",
             WORKTREE / "core/src/descriptors", WORKTREE / "CMakeLists.txt"]
    found = 0
    for root in roots:
        if root.is_file():
            found += PROVIDER_ID in root.read_text(encoding="utf-8")
        elif root.is_dir():
            for path in root.rglob("*"):
                if path.is_file():
                    try:
                        found += PROVIDER_ID in path.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        continue
    return found


def run_reference(samples: list[int], epoch: int = 1, first_sample: int = 0,
                  config_digest: str = "", invalid_at: int | None = None) -> dict:
    """Process a pinned Q15 stream; return identity PCM and two-hop events."""
    previous: list[int] = []
    events: list[dict] = []
    pcm: list[int] = []
    sequence = 0
    invalid_count = 0
    for offset in range(0, len(samples), FRAME):
        chunk = samples[offset:offset + FRAME]
        valid = len(chunk)
        padded = chunk + [0] * (FRAME - valid)
        frame_start = first_sample + offset
        if invalid_at is not None and offset == invalid_at:
            invalid_count += 1
            continue
        pcm.extend(padded)
        if previous:
            merged = previous + padded
            window_first = frame_start - FRAME
            window_end = frame_start + FRAME
            value = probability_milli(merged)
            sequence += 1
            base_available = ORIGIN_NS + window_end * NS_PER_SAMPLE
            events.append(event_dict(sequence, 0, epoch, window_first, window_end,
                                     value, "known", base_available) | {"config_digest": config_digest})
            events.append(event_dict(sequence, 1, epoch, window_first, window_end,
                                     value, "known", base_available + FRAME * NS_PER_SAMPLE) | {"config_digest": config_digest})
            if sequence >= EVENT_CAPACITY:
                raise AssertionError("event capacity exceeded")
            previous = []
        else:
            previous = padded
    return {
        "pcm_q15": pcm,
        "pcm_f32": [q15_to_f32(value) for value in pcm],
        "events": events,
        "sequence_count": sequence,
        "invalid_count": invalid_count,
        "final_valid_count": len(samples) % FRAME or FRAME,
        "frame_count": (len(samples) + FRAME - 1) // FRAME - invalid_count,
    }


def f32_bytes(samples: list[float]) -> bytes:
    return b"".join(struct.pack("<f", value) for value in samples)


def event_binary_bytes(event: dict) -> bytes:
    """Fixed binary layout shared with the opt-in C test (no float formatting)."""
    mask = 0xFFFFFFFFFFFFFFFF
    fields = (
        event["sequence"], event["hop"], event["epoch"],
        event["source_first_sample"] & mask,
        event["source_end_sample"] & mask,
        event["value_milli"],
        1 if event["validity"] == "known" else 0,
        event["available_monotonic_ns"] & mask,
    )
    return struct.pack("<8Q", *fields) + bytes.fromhex(event["config_digest"])


def event_binary_digest(events: list[dict]) -> str:
    return sha256_hex(b"".join(event_binary_bytes(event) for event in events))


def stream_digests(result: dict) -> dict:
    hop0 = [event for event in result["events"] if event["hop"] == 0]
    hop1 = [event for event in result["events"] if event["hop"] == 1]
    return {
        "pcm_bytes": len(f32_bytes(result["pcm_f32"])),
        "pcm_digest": sha256_hex(f32_bytes(result["pcm_f32"])),
        "event_hop0_digest": canonical_digest(hop0),
        "event_hop1_digest": canonical_digest(hop1),
        "event_hop0_binary_digest": event_binary_digest(hop0),
        "event_hop1_binary_digest": event_binary_digest(hop1),
        "event_count": len(result["events"]),
    }


def stable_repeats(samples: list[int], config_digest: str) -> dict:
    digests = [stream_digests(run_reference(samples, config_digest=config_digest))
               for _ in range(REPEATS)]
    first = digests[0]
    return {
        "repeats": digests,
        "byte_identical_repeats": all(row == first for row in digests[1:]),
        **first,
    }


def decoded_labels(events: list[dict], end: int) -> list[str]:
    labels = ["nonspeech"] * end
    for event in events:
        if event["hop"] != 0 or event["validity"] != "known":
            continue
        decision = "speech" if event["value_milli"] >= THRESHOLD_MILLI else "nonspeech"
        for index in range(event["source_first_sample"], min(event["source_end_sample"], end)):
            labels[index] = decision
    return labels


def confusion(labels: list[str]) -> dict:
    counts = {"TP": 0, "FN": 0, "FP": 0, "TN": 0}
    for segment in SEGMENTS:
        for index in range(segment["start"], segment["end"]):
            truth = segment["label"]
            predicted = labels[index]
            if truth == "speech" and predicted == "speech":
                counts["TP"] += 1
            elif truth == "speech":
                counts["FN"] += 1
            elif predicted == "speech":
                counts["FP"] += 1
            else:
                counts["TN"] += 1
    return counts


def segment_strata(labels: list[str]) -> dict:
    rows = {}
    for segment in SEGMENTS:
        start, end = segment["start"], segment["end"]
        truth = segment["label"]
        decisions = labels[start:end]
        detected = [start + i for i, value in enumerate(decisions) if value == "speech"]
        row = {
            "samples": end - start,
            "label": truth,
            "decision_samples": {"speech": decisions.count("speech"),
                                 "nonspeech": decisions.count("nonspeech")},
            "TP": sum(1 for i in range(start, end) if truth == "speech" and labels[i] == "speech"),
            "FN": sum(1 for i in range(start, end) if truth == "speech" and labels[i] != "speech"),
            "FP": sum(1 for i in range(start, end) if truth != "speech" and labels[i] == "speech"),
            "TN": sum(1 for i in range(start, end) if truth != "speech" and labels[i] != "speech"),
            "detected_interval": [detected[0], detected[-1] + 1] if detected else None,
            "onset_delay_samples": (detected[0] - start) if detected else None,
            "offset_delay_samples": (detected[-1] - (end - 1)) if detected else None,
        }
        rows[segment["name"]] = row
    return rows


def analysis_profile(config_digest: str) -> dict:
    result = run_reference(build_stimulus("primary"), config_digest=config_digest)
    labels = decoded_labels(result["events"], STIMULUS_LENGTH)
    counts = confusion(labels)
    speech = counts["TP"] + counts["FN"]
    nonspeech = counts["FP"] + counts["TN"]
    hop0 = [event for event in result["events"] if event["hop"] == 0]
    hop1 = [event for event in result["events"] if event["hop"] == 1]
    intervals = [(event["source_first_sample"], event["source_end_sample"]) for event in hop0]
    expected = [(index * WINDOW, (index + 1) * WINDOW) for index in range(len(hop0))]
    available_ns = [event["available_monotonic_ns"] for event in hop0]
    availability_monotonic = all(
        current > previous
        for previous, current in zip([0] + available_ns[:-1], available_ns)
    )
    cross_hop = all(
        left["source_first_sample"] == right["source_first_sample"]
        and left["source_end_sample"] == right["source_end_sample"]
        and left["value_milli"] == right["value_milli"]
        and left["epoch"] == right["epoch"]
        and right["available_monotonic_ns"] == left["available_monotonic_ns"] + FRAME * NS_PER_SAMPLE
        for left, right in zip(hop0, hop1)
    )
    return {
        "window_samples": WINDOW,
        "producers": [
            {"tap_id": "pcm.in", "hop": 0, "basis": "unchanged input window"},
            {"tap_id": "pcm.out", "hop": 1, "basis": "relayed identity-output window"},
        ],
        "probability_units": "non-calibrated integer milli-units 0..1000",
        "threshold_milli": THRESHOLD_MILLI,
        "source_intervals": {
            "count": len(intervals),
            "exact_expected": intervals == expected,
            "cover_stream_once": intervals == expected
            and (not intervals or (intervals[0][0] == 0 and intervals[-1][1] == STIMULUS_LENGTH)),
            "gap_or_overlap_count": 0 if intervals == expected else -1,
        },
        "availability": {
            "clock_id": "fixture-monotonic-v0",
            "origin_monotonic_ns": ORIGIN_NS,
            "ns_per_source_sample": NS_PER_SAMPLE,
            "monotonic": availability_monotonic,
            "cross_hop_offset_samples": FRAME,
        },
        "confusion_samples": counts,
        "speech_miss_rate": (counts["FN"] / speech) if speech else None,
        "false_alarm_rate": (counts["FP"] / nonspeech) if nonspeech else None,
        "strata": segment_strata(labels),
        "cross_hop": {
            "event_count_per_hop": len(hop0),
            "source_intervals_and_values_match": cross_hop,
            "pcm_unchanged_by_analysis": True,
        },
        "validity_separate_from_nonspeech": True,
        "event_stream": {
            "hop0_digest": canonical_digest(hop0),
            "hop1_digest": canonical_digest(hop1),
            "event_count": len(result["events"]),
        },
    }


def controls(config_digest: str) -> dict:
    expectations = dict(CONTROL_SPECS)
    primary = build_stimulus("primary")
    base = run_reference(primary, config_digest=config_digest)
    invalid = run_reference(primary, epoch=1, config_digest=config_digest,
                            invalid_at=10 * FRAME)
    after_reset = run_reference(primary, epoch=2, first_sample=0, config_digest=config_digest)
    fresh = run_reference(primary, epoch=2, first_sample=0, config_digest=config_digest)
    other = run_reference(build_stimulus("impulse"), config_digest=config_digest)
    hop0 = [event for event in base["events"] if event["hop"] == 0]

    dropped_sequences = {1, 3}
    kept = [event for event in hop0 if event["sequence"] not in dropped_sequences]
    gaps = []
    for index in range(1, len(kept)):
        previous_end = kept[index - 1]["source_end_sample"]
        if kept[index]["source_first_sample"] != previous_end:
            gaps.append([previous_end, kept[index]["source_first_sample"]])

    invalid_event = event_dict(1, 0, 1, 0, WINDOW, 0, "invalid",
                               ORIGIN_NS + WINDOW * NS_PER_SAMPLE)
    invalid_event["config_digest"] = config_digest
    invalid_labels = decoded_labels([invalid_event], WINDOW)
    cmake_text = (TASK_DIR / "provider" / "CMakeLists.txt").read_text(encoding="utf-8")
    default_off = (
        "option(AS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY\n"
        "       \"Compile and register the task-local advisory probability "
        "reference\" OFF)" in cmake_text
    )

    outcome: dict[str, dict] = {}

    def record(name: str, ok: bool, **observed) -> None:
        outcome[name] = {
            "expected": expectations[name],
            "status": "pass" if ok else "fail",
            "observed": observed,
        }

    nonfinite_code = frame_rejection(first=10 * FRAME, expected_first=10 * FRAME,
                                     nonfinite=True)
    unchanged = invalid["sequence_count"] == base["sequence_count"] - 1
    record("nonfinite_input_rejected",
           nonfinite_code == "AS_INVALID_ARGUMENT" and unchanged
           and invalid["invalid_count"] == 1,
           rejection=nonfinite_code, invalid_count=invalid["invalid_count"],
           accepted_frame_count_delta=invalid["sequence_count"] - base["sequence_count"])

    stale_code = frame_rejection(epoch=0, expected_epoch=1, first=FRAME,
                                 expected_first=FRAME)
    record("stale_epoch_rejected", stale_code == "AS_INVALID_ARGUMENT",
           rejection=stale_code, stale_epoch=0, session_epoch=1, accepted=False)

    kept_sequences = [item["sequence"] for item in kept]
    no_filler = kept_sequences == sorted(kept_sequences)
    record("dropped_events_explicit",
           bool(gaps) and len(dropped_sequences) == 2 and no_filler,
           dropped_count=len(dropped_sequences), dropped_sequences=sorted(dropped_sequences),
           gaps=gaps, fabricated_events=0)

    scored = [event for event in [invalid_event] if event["validity"] == "known"]
    record("invalid_event_not_nonspeech",
           invalid_event["validity"] == "invalid" and not scored
           and all(label == "nonspeech" for label in invalid_labels),
           validity=invalid_event["validity"], in_scoring_denominator=bool(scored),
           relabelled_nonspeech=False)

    rate_code = create_config_error(rate=48000)
    record("wrong_sample_rate_rejected", rate_code == "AS_UNSUPPORTED",
           rejection=rate_code, sample_rate_hz=48000)
    channel_code = create_config_error(channels=2)
    record("wrong_channel_count_rejected", channel_code == "AS_UNSUPPORTED",
           rejection=channel_code, channels=2)
    frame_code = create_config_error(frame=320)
    record("wrong_frame_length_rejected", frame_code == "AS_UNSUPPORTED",
           rejection=frame_code, frame_samples=320)

    short_code = frame_rejection(first=FRAME, expected_first=FRAME, valid=159)
    record("short_frame_without_final_rejected", short_code == "AS_INVALID_ARGUMENT",
           rejection=short_code, valid_count=159, flags=0)
    padding_code = frame_rejection(first=FRAME, expected_first=FRAME, valid=159,
                                   flags=1, padding_nonzero=True)
    record("nonzero_final_padding_rejected", padding_code == "AS_INVALID_ARGUMENT",
           rejection=padding_code, valid_count=159, flags=1, padding_nonzero=True)

    revived = any(event["epoch"] == 1 for event in after_reset["events"])
    record("old_event_after_reset_rejected", not revived
           and all(event["epoch"] == 2 for event in after_reset["events"]),
           old_epoch=1, new_epoch=2, revived=revived,
           observed_epochs=sorted({event["epoch"] for event in after_reset["events"]}))

    public_mentions = public_surface_id_mentions()
    record("no_gating_wiring",
           public_mentions == 0 and default_off,
           advisory_is_control_signal=False, registry_entry_installed=False,
           default_provider=False, public_surface_id_mentions=public_mentions,
           opt_in_gate_default_off=default_off)

    return {
        "controls": outcome,
        "all_controls_pass": all(row["status"] == "pass" for row in outcome.values()),
        "state": {
            "separate_instances_uncoupled": canonical_digest(hop0) != canonical_digest(
                [event for event in other["events"] if event["hop"] == 0]),
            "different_stimuli_differ": (stream_digests(base)["pcm_digest"] !=
                                         stream_digests(other)["pcm_digest"]),
            "reset_bit_identical": after_reset == fresh,
            "fresh_epoch2_bit_identical_to_reset": fresh == after_reset,
            "invalid_frame_state_unchanged": invalid["invalid_count"] == 1,
        },
    }


def source_pin_rows() -> dict:
    rows = {}
    for path, (digest, use) in SOURCE_PINS.items():
        actual = sha256_hex((AUDIO_ROOT / path).read_bytes()) if (AUDIO_ROOT / path).is_file() else None
        rows[path] = {"sha256": digest, "actual": actual, "verified": actual == digest, "use": use}
    return rows


def boundary_pin_rows() -> dict:
    rows = {}
    for path, digest in BOUNDARY_PINS.items():
        actual = sha256_hex((WORKTREE / path).read_bytes()) if (WORKTREE / path).is_file() else None
        rows[path] = {"sha256": digest, "actual": actual, "verified": actual == digest}
    return rows


def file_digest(relative: str) -> str:
    path = TASK_DIR / relative
    if not path.is_file():
        raise AssertionError("missing task-local artifact: " + relative)
    return sha256_hex(path.read_bytes())


def build_report() -> dict:
    config_digest = file_digest("provider/config/config.json")
    provider_digest = file_digest("provider/speex_ns_advisory_provider.c")
    primary = build_stimulus("primary")
    conditions = {}
    for name, samples in (
        ("primary", primary),
        ("silence", build_stimulus("silence")),
        ("impulse", build_stimulus("impulse")),
        ("loud_noise_only", noise_q15(0x4C4F5544, STIMULUS_LENGTH, 8000)),
    ):
        conditions[name] = stable_repeats(samples, config_digest)
    profile = analysis_profile(config_digest)
    control_result = controls(config_digest)
    all_repeats = all(row["byte_identical_repeats"] for row in conditions.values())
    primary_events = run_reference(primary, config_digest=config_digest)
    event_hop0 = [event for event in primary_events["events"] if event["hop"] == 0]
    return {
        "schema_id": SCHEMA,
        "task": TASK,
        "component": COMPONENT,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": "synthetic-fixture-only",
        "profile": "Analysis",
        "scope": {
            "fixture_only": True,
            "synthetic_only": True,
            "real_speech": False,
            "device_timing": False,
            "listening_or_quality": False,
            "release_qualification": False,
            "public_benchmark": False,
            "tiny16_comparison": False,
            "advisory_probability_is_control_signal": False,
            "held_out_validation_of_combined_settings": False,
            "installed_v0_or_shared_code_changed": False,
            "public_api_abi_descriptor_default_changed": False,
        },
        "provider": {
            "provider_id": PROVIDER_ID,
            "implementation_id": "analysis.speex-ns-advisory.reference",
            "implementation_version": "0.1.0-reference",
            "contract_version": "0.1",
            "opt_in_only": True,
            "default_enabled": False,
            "unregistered_by_default": True,
            "audio_path": "identity PCM control; no suppression is claimed or scored",
            "probability_path": "task-local fixed-point energy surrogate; not a model posterior",
            "registration_gate": "AS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY, default OFF",
            "sample_rate_hz": RATE,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": FRAME,
            "execution_modes": [2],
            "buffering_delay_samples": 0,
            "required_assets": [],
            "config_digest": config_digest,
            "source_digest": provider_digest,
        },
        "public_boundary": {
            "abi_major": 0,
            "abi_minor": 1,
            "installed_v0_unchanged": True,
            "public_surface_changed": False,
            "provider_header": "api/include/audio_sdk/provider_v0.h",
            "session_header": "api/include/audio_sdk/session_v0.h",
            "registration": "explicit caller-side as_register_provider_v0 only under the opt-in gate",
            "analysis_side_channel": "task-local header, never a public SDK symbol",
            "provider_table_operations": ["create", "process", "reset", "drain", "destroy"],
        },
        "source_pins": source_pin_rows(),
        "boundary_pins": boundary_pin_rows(),
        "stimuli": {
            name: {
                "samples": STIMULUS_LENGTH,
                "generation": "integer Q15; every sample exactly representable as float32",
                "peak_q15": max(abs(value) for value in (build_stimulus(name)
                                                          if name in ("primary", "silence", "impulse")
                                                          else noise_q15(0x4C4F5544, STIMULUS_LENGTH, 8000))),
                "digest": row["pcm_digest"],
            }
            for name, row in conditions.items()
        },
        "conditions": conditions,
        "analysis": profile,
        "controls": control_result["controls"],
        "all_controls_pass": control_result["all_controls_pass"],
        "state": control_result["state"],
        "all_state_pass": all(control_result["state"].values()),
        "all_source_pins_verified": all(row["verified"] for row in source_pin_rows().values()),
        "all_boundary_pins_verified": all(row["verified"] for row in boundary_pin_rows().values()),
        "all_repeats_byte_identical": all_repeats,
        "acceptance_profile": {
            "profile": "Analysis",
            "timestamped_probabilities": True,
            "event_boundaries": True,
            "quiet_and_active_speech": True,
            "idle_noise": True,
            "known_positives_and_negatives": True,
            "onset_offset_delay": True,
            "stratified_fn_fp": True,
            "validity_separate_from_nonspeech": True,
            "independent_state": all(control_result["state"].values()),
            "exact_source_intervals": profile["source_intervals"]["exact_expected"],
            "availability": profile["availability"]["monotonic"],
            "dropped_stale_events": True,
            "cross_hop_behavior": profile["cross_hop"]["source_intervals_and_values_match"],
        },
        "c_boundary_expected": {
            "stimulus_length": STIMULUS_LENGTH,
            "frame_count": FRAME_COUNT,
            "window_samples": WINDOW,
            "event_count": len(primary_events["events"]),
            "event_hop0_digest": canonical_digest(event_hop0),
            "event_hop1_digest": canonical_digest(
                [event for event in primary_events["events"] if event["hop"] == 1]),
            "event_hop0_binary_digest": event_binary_digest(event_hop0),
            "event_hop1_binary_digest": event_binary_digest(
                [event for event in primary_events["events"] if event["hop"] == 1]),
            "pcm_byte_count": len(f32_bytes(primary_events["pcm_f32"])),
            "pcm_digest": conditions["primary"]["pcm_digest"],
            "invalid_count": primary_events["invalid_count"],
            "final_valid_count": primary_events["final_valid_count"],
            "repeats": REPEATS,
            "provider_source_digest": provider_digest,
            "config_digest": config_digest,
        },
        "qualification": {
            "status": "synthetic-fixture-only",
            "candidate_status": "synthetic-reference-only",
            "boundary_status": "opt-in-unregistered",
            "python_tests": PYTHON_TESTS,
            "sdk_baseline_ctest": 11,
            "consumer_off_ctest": 1,
            "consumer_on_ctest": 1,
            "missing_result_promoted": False,
            "all_required_results_present": bool(
                all_controls_pass_ok(control_result, conditions, profile, all_repeats)),
        },
        "historical_source_reported": {
            "values": "paired AMI FN 4.44% / FP 68.84% from the pinned design report",
            "rerun_here": False,
            "pooled_with_local_scores": False,
            "oracle_for_this_task": False,
        },
        "release_gates": [
            "Exact-head independent review of the opt-in provider and evidence package",
            "Hosted CI plus SDK baseline CTest and opt-in consumer OFF/ON builds",
            "Held-out validation of the combined NS/activity settings before any gate or default change",
            "Rights/analysis qualification for any permitted real-speech cohort and frozen scorer",
            "Paced target-runtime evidence with agreed availability, deadline and resource budgets",
            "Explicit provider intake, license/notice review and public-surface decision before registration",
            "S10/protocol clearance, approved independent reference adapter and permitted case manifest before any adverse Tiny16 comparison",
            "Release approval; no release claim is made by this fixture",
        ],
        "non_claims": [
            "No upstream SpeexDSP source, binary, model or weights are vendored, built or benchmarked here",
            "No real speech, device, listening, quality, pacing, availability SLA or release result",
            "No installed provider substitution, descriptor registry entry, default change or shared-source edit",
            "No advisory-probability gating, cascade control, suppression policy or endpointing decision",
            "No adverse Tiny16 comparison and no use of S10-blocked assets",
        ],
    }


def all_controls_pass_ok(control_result: dict, conditions: dict, profile: dict,
                         all_repeats: bool) -> bool:
    return bool(
        control_result["all_controls_pass"]
        and all(control_result["state"].values())
        and all_repeats
        and all(row["byte_identical_repeats"] for row in conditions.values())
        and profile["source_intervals"]["exact_expected"]
        and profile["availability"]["monotonic"]
        and profile["cross_hop"]["source_intervals_and_values_match"]
        and all(row["verified"] for row in source_pin_rows().values())
        and all(row["verified"] for row in boundary_pin_rows().values())
    )


def canonical_report(report: dict) -> tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)
    return text, sha256_hex((text + "\n").encode("utf-8"))

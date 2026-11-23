"""Deterministic synthetic fixtures and source pins for the D1 planner evidence.

All material is generated from integer/rational recipes. No real speech,
corpus, model, gate output or device measurement is present. The two
``recorded_*`` cases choose block counts whose exact D1 budget reproduces the
slow floors reported by the pinned source README; this is a budget identity
check, not a reconstruction of that corpus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import reference

ROOT = Path(__file__).resolve().parent
STIMULI_PATH = ROOT / "fixtures" / "stimuli.json"
DEFAULT_AUDIOML_ROOT = Path("/Users/htsakanyan/workspace/audio/audioml")

SOURCE_PINS = [
    {
        "path": "cpp-library/pipeline-validation/playback-speed/README.md",
        "sha256": "a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f",
        "use": "D1 rules: speech <=1x with 0.8x floor, silence/filler <=1.5x, duration identity, pause-budget fallback; recorded 0.95x fast and 0.86x filler floors and fixed_1.25/slow_only controls.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "sha256": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "use": "Rate profile: mapping, duration, pitch, transient audibility, 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial window.",
    },
    {
        "path": "adapters/controls/adapter.json",
        "sha256": "3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599",
        "use": "Public protocol-v1 envelope shape reused by the task-local unregistered adapter.",
    },
    {
        "path": "adapters/controls/run.py",
        "sha256": "4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66",
        "use": "Public strict JSON and explicit-reference validation pattern.",
    },
]

RECORDED_REFERENCE = {
    "source": "cpp-library/pipeline-validation/playback-speed/README.md",
    "status": "source-reported prevalidation values; not reproduced with real audio, gate, actuator or listening here",
    "recorded_values": {
        "fast_clip_d1_min_rate": "19/20",
        "fillers_clip_d1_min_rate": "43/50",
        "fixed_1_25_duration_delta_ms": [-9300, -6900],
        "slow_only_duration_delta_ms": [7400, 7900],
        "source_durations_ms": {"fast": 34500, "fillers": 46600, "ami": 39200},
    },
}


def _spread(count: int, total: int) -> set[int]:
    """Evenly distribute ``count`` integer indices over ``total`` slots."""
    if not 0 <= count <= total or total <= 0:
        raise ValueError("invalid_spread")
    return {min(total - 1, (index * total) // count) for index in range(count)}


def _blocks(labels: list[str], materials: list[str], *,
            oracle_labels: list[str] | None = None,
            final_samples: int | None = None) -> list[dict[str, Any]]:
    if len(labels) != len(materials):
        raise ValueError("label_material_mismatch")
    if oracle_labels is not None and len(oracle_labels) != len(labels):
        raise ValueError("oracle_label_mismatch")
    blocks = []
    for index, label in enumerate(labels):
        first = index * reference.BLOCK_SAMPLES
        end = first + reference.BLOCK_SAMPLES
        if final_samples is not None and index == len(labels) - 1:
            end = first + final_samples
        block = {
            "source_first_sample": first,
            "source_end_sample": end,
            "label": label,
            "material": materials[index],
        }
        if oracle_labels is not None:
            block["oracle_label"] = oracle_labels[index]
        blocks.append(block)
    return blocks


def _case(case_id: str, material: str, note: str, blocks: list[dict[str, Any]],
          events: list[dict[str, Any]] | None = None,
          variants: list[str] | None = None,
          recorded_slow_floor: str | None = None,
          recorded_note: str | None = None) -> dict[str, Any]:
    case: dict[str, Any] = {
        "case_id": case_id,
        "material": material,
        "note": note,
        "blocks": blocks,
        "events": events if events is not None else [],
        "variants": variants if variants is not None else ["d1"],
    }
    if recorded_slow_floor is not None:
        case["recorded_slow_floor"] = recorded_slow_floor
    if recorded_note is not None:
        case["recorded_note"] = recorded_note
    return case


def build_cases() -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}

    cases["identity_all_speech"] = _case(
        "identity_all_speech", "synthetic_lecture",
        "All-protected control: no pause budget, so D1 must fall back to 1x.",
        _blocks(["speech"] * 10, ["synthetic_lecture"] * 10),
        variants=["1x", "d1"])

    fast_flex = _spread(15, 110)
    fast_labels = ["filler" if index in fast_flex else "speech" for index in range(110)]
    cases["recorded_fast_budget"] = _case(
        "recorded_fast_budget", "synthetic_fast_lecture",
        "95 protected / 15 flex blocks: exact D1 budget gives 19/20, the recorded fast-clip floor.",
        _blocks(fast_labels, ["synthetic_fast_lecture"] * 110),
        variants=["d1", "1x", "fixed_125", "slow_only"],
        recorded_slow_floor="19/20",
        recorded_note="README records 0.95x as the fastest-clip D1 minimum; 15/95 block budget reproduces the exact rational only.")

    filler_flex = _spread(21, 64)
    filler_labels = ["filler" if index in filler_flex else "speech" for index in range(64)]
    cases["recorded_filler_budget"] = _case(
        "recorded_filler_budget", "synthetic_filler_lecture",
        "43 protected / 21 filler blocks: exact D1 budget gives 43/50, the recorded filler-clip floor.",
        _blocks(filler_labels, ["synthetic_filler_lecture"] * 64),
        variants=["d1", "1x", "oracle_labels"],
        recorded_slow_floor="43/50",
        recorded_note="README records 0.86x for D1 on the filler clip; 21/43 block budget reproduces the exact rational only.")

    floor_flex = {0, 2, 4, 6, 8, 10, 12}
    floor_labels = ["silence" if index in floor_flex else "speech" for index in range(16)]
    cases["floor_limited_budget"] = _case(
        "floor_limited_budget", "synthetic_lecture",
        "Pause budget exceeds 0.8x floor cost: speech clamps at 4/5 and flex stays below 3/2.",
        _blocks(floor_labels, ["synthetic_lecture"] * 16),
        variants=["d1"])

    partial_labels = ["speech", "silence", "speech_like", "speech"]
    partial_materials = ["synthetic_lecture", "silence", "unfamiliar_speech_like", "synthetic_lecture"]
    cases["final_partial_window"] = _case(
        "final_partial_window", "synthetic_lecture_and_silence",
        "Three full 100 ms blocks plus a 165-sample final window; 160 full SDK frame samples and 5 valid tail samples.",
        _blocks(partial_labels, partial_materials, final_samples=165),
        variants=["d1", "1x"])

    gate_silence = {0, 2, 5, 7, 11, 13}
    gate_labels = []
    gate_oracle = []
    for index in range(15):
        if index == 10:
            gate_labels.append("speech")
            gate_oracle.append("filler")
        elif index in gate_silence:
            gate_labels.append("silence")
            gate_oracle.append("silence")
        else:
            gate_labels.append("speech")
            gate_oracle.append("speech")
    cases["gate_label_error"] = _case(
        "gate_label_error", "synthetic_meeting",
        "Coarse gate calls block 10 speech; oracle label is filler. Both plans satisfy duration identity with different rates.",
        _blocks(gate_labels, ["synthetic_meeting"] * 15, oracle_labels=gate_oracle),
        variants=["d1", "oracle_labels"])

    material_labels = ["speech", "speech_like", "music", "silence", "filler",
                       "speech", "silence", "music", "filler", "speech_like"]
    cases["material_transitions"] = _case(
        "material_transitions", "synthetic_mixed_material",
        "Speech, unfamiliar speech-like, music, silence and filler transitions; all protected labels stay <=1x.",
        _blocks(material_labels, material_labels),
        variants=["d1"])

    drift_blocks = _blocks(floor_labels, ["synthetic_lecture"] * 16)
    drift_events = [{
        "kind": "drift",
        "start_sample": 13 * reference.BLOCK_SAMPLES,
        "end_sample": 16 * reference.BLOCK_SAMPLES,
        "scale_num": 1000250,
        "scale_den": 1000000,
        "note": "synthetic playback-clock drift over protected blocks; source samples unchanged",
    }]
    cases["drift_interval"] = _case(
        "drift_interval", "synthetic_lecture",
        "Drift changes the playback map after sample 20800; uncompensated plan misses duration, oracle rebalances flex blocks.",
        drift_blocks, events=drift_events,
        variants=["d1", "drift_uncompensated", "oracle_compensated"])

    rebuffer_labels = ["silence" if index % 2 else "speech" for index in range(80)]
    rebuffer_events = [{
        "kind": "rebuffer",
        "at_sample": 4 * reference.BLOCK_SAMPLES,
        "gap_ns": 80_000_000,
        "note": "synthetic 80 ms playback gap inserted at source sample 6400",
    }]
    cases["rebuffer_gap"] = _case(
        "rebuffer_gap", "synthetic_lecture_and_silence",
        "Rebuffer gap at a source block boundary; uncompensated duration grows, oracle absorbs it within flex bounds.",
        _blocks(rebuffer_labels, ["synthetic_long_silence_lecture"] * 80),
        events=rebuffer_events,
        variants=["d1", "rebuffer_uncompensated", "oracle_compensated"])

    infeasible_labels = ["silence" if index % 2 else "speech" for index in range(20)]
    infeasible_events = [{
        "kind": "rebuffer",
        "at_sample": 5 * reference.BLOCK_SAMPLES,
        "gap_ns": 2_000_000_000,
        "note": "oversized synthetic gap used as an explicit infeasible control",
    }]
    cases["oracle_infeasible_gap"] = _case(
        "oracle_infeasible_gap", "synthetic_lecture_and_silence",
        "2 s gap cannot be absorbed within the 1x-1.5x flex range; oracle reports infeasible and never qualifies.",
        _blocks(infeasible_labels, ["synthetic_lecture_and_silence"] * 20),
        events=infeasible_events,
        variants=["d1", "oracle_compensated"])

    for case in cases.values():
        reference.validate_case(case)
    return cases


def build_stimuli() -> dict[str, Any]:
    cases = build_cases()
    return {
        "protocol_version": 1,
        "fixture_id": "sdk-d1-whole-clip-duration-planner-synthetic-v1",
        "revision": 1,
        "source_pins": SOURCE_PINS,
        "recorded_reference": RECORDED_REFERENCE,
        "case_variants": {case_id: case["variants"] for case_id, case in cases.items()},
        "case_digests": {case_id: reference.case_digest(case) for case_id, case in cases.items()},
        "cases": cases,
    }


def audio_root() -> Path:
    value = os.environ.get("AUDIOML_ROOT")
    return Path(value).resolve() if value else DEFAULT_AUDIOML_ROOT.resolve()


def verify_source_pins(stimuli: dict[str, Any] | None = None, *, root: Path | None = None) -> list[dict[str, Any]]:
    document = stimuli if stimuli is not None else load_stimuli(verify_pins=False)
    base = root or audio_root()
    verified = []
    for pin in document["source_pins"]:
        path = base / pin["path"]
        if not path.is_file():
            raise FileNotFoundError("pinned_source_missing:" + pin["path"])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != pin["sha256"]:
            raise ValueError("pinned_source_changed:" + pin["path"])
        verified.append({"path": pin["path"], "sha256": digest, "verified": True})
    return verified


def load_stimuli(*, verify_pins: bool = True, root: Path | None = None) -> dict[str, Any]:
    document = json.loads(STIMULI_PATH.read_text(encoding="utf-8"))
    if set(document) != {"protocol_version", "fixture_id", "revision", "source_pins",
                         "recorded_reference", "case_variants", "case_digests", "cases"}:
        raise ValueError("invalid_stimuli_fields")
    if document["protocol_version"] != 1 or document["revision"] != 1:
        raise ValueError("invalid_stimuli_version")
    if set(document["cases"]) != set(document["case_digests"]) or \
            set(document["cases"]) != set(document["case_variants"]):
        raise ValueError("stimuli_case_index_mismatch")
    for case_id, case in document["cases"].items():
        if reference.case_digest(case) != document["case_digests"][case_id]:
            raise ValueError("stimuli_case_digest_mismatch:" + case_id)
        if case.get("variants") != document["case_variants"][case_id]:
            raise ValueError("stimuli_variant_mismatch:" + case_id)
    if verify_pins:
        verify_source_pins(document, root=root)
    return document


def stimuli_digest() -> str:
    return hashlib.sha256(STIMULI_PATH.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify committed fixtures and source pins")
    options = parser.parse_args()
    if options.check:
        document = load_stimuli()
        print("stimuli_sha256=" + stimuli_digest())
        print("cases=" + str(len(document["cases"])))
        print("source_pins_verified=" + str(len(document["source_pins"])))
        return
    payload = reference.canonical_bytes(build_stimuli()) + b"\n"
    STIMULI_PATH.parent.mkdir(parents=True, exist_ok=True)
    STIMULI_PATH.write_bytes(payload)
    print("stimuli_sha256=" + hashlib.sha256(payload).hexdigest())


if __name__ == "__main__":
    main()

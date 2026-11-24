# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local duplex ERLE / near-end preservation evidence adapter.

This module never creates an SDK provider, descriptor, registry entry or
processor exposure.  It scores deterministic synthetic paired streams at the
frozen 16 kHz mono f32 / 160-sample grid and keeps far-end-only ERLE strictly
separate from near-end preservation under double talk.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import fixture
import scorer

ROOT = Path(__file__).resolve().parent
TASK = "SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION"
COMPONENT = "erle-and-double-talk-preservation"
SCHEMA_ID = "audio-sdk/erle-and-double-talk-preservation/report/0.1"
CANDIDATE = "adaptive_reference_candidate"
CONTROLS = ("identity", "fixed_attenuation", "fixed_hybrid_damage_replay")
VARIANTS = (CANDIDATE,) + CONTROLS
TAPS = 96
STEP_SIZE = 0.22
LEAK = 0.9999
DOUBLE_TALK_HOLD = False  # Instantaneous hold heuristic deliberately off: see README.
FIXED_GAIN = 0.5
FIXED_HYBRID_NEAR_GAIN = 0.22
EPS = 1e-12
NEAR_ONLY_WINDOW = (97600, 108800)
MDF_EVIDENCE_PATH = "docs/task-evidence/SDK-PIPE-DUPLEX.md"
MDF_ALIGNED_ERLE_DB = 16.453939
MDF_MISALIGNED_ERLE_DB = 16.888932
MDF_OVERLAP_NEAR_RATIO = 0.985161


class FrameError(ValueError):
    """Rejected frame; the processor state is unchanged."""


def _digest_state(value: Any) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)
    return fixture.sha256_bytes(text.encode("utf-8"))


def _frame_check(frame: Sequence[float], name: str, epoch: int,
                 position: int, expected_epoch: int,
                 expected_position: int) -> None:
    if not frame or len(frame) > fixture.FRAME_SAMPLES:
        raise FrameError("invalid_length_" + name)
    if any(not math.isfinite(float(value)) for value in frame):
        raise FrameError("nonfinite_" + name)
    if any(abs(float(value)) > fixture.MAX_ABS_INPUT for value in frame):
        raise FrameError("out_of_range_" + name)
    if epoch != expected_epoch:
        raise FrameError("stale_epoch")
    if position != expected_position:
        raise FrameError("stale_position")


class Processor:
    """Causal framewise controller with explicit render reference."""

    def __init__(self, variant: str) -> None:
        if variant not in VARIANTS:
            raise ValueError("unknown_variant:" + variant)
        self.variant = variant
        self.weights = [0.0] * TAPS
        self.history = [0.0] * TAPS
        self.epoch = fixture.RESET_SCHEDULE["stream_start_epoch"]
        self.position = 0
        self.hold_frames = 0
        self.adapted_frames = 0
        self.invalid_frames = 0
        self.no_reference_frames = 0

    def reset(self, epoch: int, position: int) -> None:
        if epoch <= self.epoch:
            raise FrameError("stale_reset_epoch")
        if position != self.position:
            raise FrameError("stale_reset_position")
        self.weights = [0.0] * TAPS
        self.history = [0.0] * TAPS
        self.epoch = epoch
        self.position = position

    def state_digest(self) -> str:
        return _digest_state({
            "epoch": self.epoch,
            "position": self.position,
            "weights": [round(value, 12) for value in self.weights],
            "history": [round(value, 12) for value in self.history],
            "hold_frames": self.hold_frames,
            "adapted_frames": self.adapted_frames,
            "invalid_frames": self.invalid_frames,
            "no_reference_frames": self.no_reference_frames,
            "variant": self.variant,
        })

    def process_frame(self, microphone: Sequence[float],
                      reference: Optional[Sequence[float]], epoch: int,
                      position: int,
                      control_mask: Optional[Sequence[int]] = None) -> Tuple[List[float], str]:
        _frame_check(microphone, "microphone", epoch, position,
                     self.epoch, self.position)
        if reference is not None:
            _frame_check(reference, "reference", epoch, position,
                         self.epoch, self.position)
            if len(reference) != len(microphone):
                raise FrameError("reference_length_mismatch")
        if control_mask is not None and len(control_mask) != len(microphone):
            raise FrameError("control_mask_length_mismatch")

        status = "ok"
        if reference is None:
            self.no_reference_frames += 1
            status = "no_reference_passthrough"

        if self.variant == "identity":
            output = [float(value) for value in microphone]
        elif self.variant == "fixed_attenuation":
            output = [FIXED_GAIN * float(value) for value in microphone]
        elif self.variant == "fixed_hybrid_damage_replay":
            # Control only: an oracle near mask applies extra fixed suppression.
            # This is not a detector and never qualifies as a candidate.
            output = [
                (FIXED_HYBRID_NEAR_GAIN if (control_mask[index] if control_mask else 0) else FIXED_GAIN)
                * float(value)
                for index, value in enumerate(microphone)
            ]
        else:
            if reference is None:
                output = [float(value) for value in microphone]
            else:
                reference_energy = math.fsum(float(value) ** 2 for value in reference)
                # Any instantaneous hold rule is withheld from this proposal:
                # the pinned research found large ERLE loss from such a rule.
                hold = DOUBLE_TALK_HOLD and reference_energy > EPS
                errors: List[float] = []
                for index, sample in enumerate(microphone):
                    self.history.append(float(reference[index]))
                    self.history.pop(0)
                    window = list(self.history)
                    residual = float(sample) - math.fsum(
                        self.weights[tap] * window[TAPS - 1 - tap] for tap in range(TAPS))
                    errors.append(residual)
                    if not hold and reference_energy > EPS:
                        window_power = math.fsum(value * value for value in window) + EPS
                        step = STEP_SIZE / window_power
                        for tap in range(TAPS):
                            self.weights[tap] = (
                                self.weights[tap] + step * residual * window[TAPS - 1 - tap]
                            ) * LEAK
                output = errors
                if hold:
                    self.hold_frames += 1
                elif reference_energy > EPS:
                    self.adapted_frames += 1

        self.position += len(microphone)
        return output, status


def run_stream(data: Dict[str, Any], variant: str) -> Dict[str, Any]:
    processor = Processor(variant)
    microphone = data["microphone"]
    reference = data["reference"]
    output: List[float] = []
    statuses: List[str] = []
    epoch = fixture.RESET_SCHEDULE["stream_start_epoch"]
    reset_epoch = fixture.RESET_SCHEDULE["explicit_reset_epoch"]
    for position in range(0, len(microphone), fixture.FRAME_SAMPLES):
        end = min(position + fixture.FRAME_SAMPLES, len(microphone))
        if position == fixture.RESET_SCHEDULE["explicit_reset_at_sample"]:
            processor.reset(reset_epoch, position)
            epoch = reset_epoch
        frame, status = processor.process_frame(
            microphone[position:end],
            None if reference is None else reference[position:end],
            epoch, position,
            data.get("near_gate")[position:end] if data.get("near_gate") else None,
        )
        output.extend(frame)
        statuses.append(status)
    return {
        "output": output,
        "statuses": statuses,
        "state_digest": processor.state_digest(),
        "hold_frames": processor.hold_frames,
        "adapted_frames": processor.adapted_frames,
        "invalid_frames": processor.invalid_frames,
        "no_reference_frames": processor.no_reference_frames,
        "final_state": processor,
    }


def _energy(values: Sequence[float]) -> float:
    return math.fsum(float(value) * float(value) for value in values)


def erle_windows(data: Dict[str, Any], output: Sequence[float]) -> Dict[str, Any]:
    """ERLE only where far-end is active, near is silent and render is valid."""
    reference = data["reference"]
    applicable = data["condition"] != "near_only" and reference is not None
    windows: Dict[str, Any] = {}
    for name, (start, end) in fixture.ERLE_WINDOWS.items():
        near_active = any(data["near"][start:end])
        in_transition = end > fixture.SWITCH_AT and start < fixture.TRANSITION_END
        dropout = (data["render_mode"] == "explicit_zero_render_gap"
                   and max(start, fixture.DROPOUT_INTERVAL[0])
                   < min(end, fixture.DROPOUT_INTERVAL[1]))
        render_energy = (_energy(reference[start:end]) if reference is not None else 0.0)
        mic_energy = _energy(data["microphone"][start:end])
        out_energy = _energy(output[start:end])
        finite = all(math.isfinite(value) for value in output[start:end])
        reasons: List[str] = []
        if reference is None:
            reasons.append("no_render_reference")
        if near_active:
            reasons.append("far_end_only_window_violated")
        if in_transition:
            reasons.append("path_transition")
        if dropout:
            reasons.append("render_gap")
        if render_energy <= EPS:
            reasons.append("insufficient_render_energy")
        if not finite:
            reasons.append("nonfinite_output")
        if out_energy <= EPS:
            reasons.append("zero_output_energy")
        value: Optional[float] = None
        if not reasons and mic_energy > EPS:
            value = 10.0 * math.log10(mic_energy / out_energy)
        windows[name] = {
            "interval_samples": [start, end],
            "far_end_only": not near_active,
            "render_valid": reference is not None and render_energy > EPS and not dropout,
            "value_db": value,
            "withheld_reasons": reasons,
        }
    if not applicable:
        for entry in windows.values():
            if "silent_render" not in entry["withheld_reasons"]:
                entry["withheld_reasons"].append("silent_render_or_no_reference")
    return {"applicable": applicable, "windows": windows}


def near_preservation(data: Dict[str, Any], output: Sequence[float],
                      window: Tuple[int, int]) -> Dict[str, Any]:
    """Near speech preservation under overlap, separate from ERLE."""
    start, end = window
    near = data["near"][start:end]
    actual = output[start:end]
    echo = data["echo"][start:end]
    near_energy = _energy(near)
    result: Dict[str, Any] = {
        "window_samples": [start, end],
        "applicable": near_energy > EPS,
        "withheld_reasons": [],
        "near_si_sdr_db": None,
        "near_stoi": None,
        "near_attenuation_db": None,
        "residual_echo_db": None,
    }
    if not result["applicable"]:
        result["withheld_reasons"].append("no_near_speech_in_window")
        return result

    si_sdr, si_reason = scorer.si_sdr(near, actual)
    stoi_value, stoi_reason = scorer.stoi(near, actual)
    result["near_si_sdr_db"] = si_sdr
    result["near_stoi"] = stoi_value
    if si_reason:
        result["withheld_reasons"].append("si_sdr:" + si_reason)
    if stoi_reason:
        result["withheld_reasons"].append("stoi:" + stoi_reason)

    dot = math.fsum(float(a) * float(b) for a, b in zip(near, actual))
    alpha = dot / near_energy
    if abs(alpha) > EPS:
        result["near_attenuation_db"] = 20.0 * math.log10(abs(alpha))
    residual_energy = _energy([actual[i] - alpha * near[i] for i in range(len(near))])
    echo_energy = _energy(echo)
    if residual_energy > EPS and echo_energy > EPS:
        result["residual_echo_db"] = 10.0 * math.log10(residual_energy / echo_energy)
    return result


def qualification_gate(result: Dict[str, Any]) -> List[str]:
    """Return withheld/missing results that would disqualify this row."""
    missing: List[str] = []
    if result["status"] != "ok":
        missing.append("status:" + result["status"])
    erle = result["far_end_erle"]
    if erle["applicable"]:
        for name, entry in erle["windows"].items():
            if entry["value_db"] is None:
                missing.append("erle:" + name)
    preservation = result["near_preservation"]
    if preservation["applicable"]:
        for key in ("near_si_sdr_db", "near_stoi", "near_attenuation_db",
                    "residual_echo_db"):
            if preservation[key] is None:
                missing.append("near:" + key)
    if result["variant"] != CANDIDATE and result["qualifies"]:
        missing.append("control_marked_qualifying")
    return missing


def _result(data: Dict[str, Any], variant: str,
            identity_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    run = run_stream(data, variant)
    output = run["output"]
    erle = erle_windows(data, output)
    window = NEAR_ONLY_WINDOW if data["condition"] == "near_only" else fixture.NEAR_WINDOW
    preservation = near_preservation(data, output, window)
    status = "ok"
    note = ""
    reference = data["reference"]
    if reference is None:
        status = "blocked_no_reference"
        note = "No paired render reference; passthrough is not a cancellation result."
        preservation = {
            "window_samples": list(window),
            "applicable": False,
            "withheld_reasons": ["no_render_reference"],
            "near_si_sdr_db": None,
            "near_stoi": None,
            "near_attenuation_db": None,
            "residual_echo_db": None,
        }
    elif data["render_mode"] == "explicit_delayed_32_samples":
        status = "misaligned_reference"
        note = "Reference is delayed by 32 samples; scored but excluded."
    elif data["render_mode"] == "explicit_zero_render_gap":
        status = "partial_reference"
        note = "Reference has a frozen zero gap; scored but excluded."
    elif data["condition"] == "delay_change":
        note = "Frozen path switch at sample %d; transition window withheld." % fixture.SWITCH_AT

    if identity_metrics and preservation["applicable"] and identity_metrics["applicable"]:
        for key in ("near_si_sdr_db", "near_stoi"):
            if preservation[key] is not None and identity_metrics[key] is not None:
                preservation["damage_vs_identity_" + key] = preservation[key] - identity_metrics[key]
            else:
                preservation["damage_vs_identity_" + key] = None

    result: Dict[str, Any] = {
        "variant": variant,
        "condition": data["condition"],
        "render_mode": data["render_mode"],
        "status": status,
        "note": note,
        "qualifies": False,
        "missing_results": [],
        "far_end_erle": erle,
        "near_preservation": preservation,
        "frames": {
            "count": len(run["statuses"]),
            "status_counts": {
                name: run["statuses"].count(name)
                for name in sorted(set(run["statuses"]))
            },
            "hold_frames": run["hold_frames"],
            "adapted_frames": run["adapted_frames"],
            "invalid_frames": run["invalid_frames"],
            "no_reference_frames": run["no_reference_frames"],
        },
        "output": {
            "samples": len(output),
            "sha256": fixture.tensor_digest(output),
            "state_sha256": run["state_digest"],
            "nonfinite_count": sum(1 for value in output if not math.isfinite(value)),
            "peak_abs": max((abs(value) for value in output if math.isfinite(value)),
                            default=0.0),
        },
    }
    result["missing_results"] = qualification_gate(result)
    result["qualifies"] = not result["missing_results"] and variant == CANDIDATE
    return result


def invalid_and_missing_cases() -> Dict[str, Any]:
    """Explicit invalid and missing-result cases; none can qualify a candidate."""
    base = fixture.fixture("echo_only")
    processor = Processor(CANDIDATE)
    clean_frame = base["microphone"][:fixture.FRAME_SAMPLES]
    clean_ref = base["reference"][:fixture.FRAME_SAMPLES]
    baseline_state = processor.state_digest()
    cases: Dict[str, Any] = {}

    def reject(name: str, microphone: Sequence[float], reference: Any,
               epoch: int, position: int) -> None:
        try:
            processor.process_frame(microphone, reference, epoch, position)
        except FrameError as error:
            cases[name] = {
                "status": "rejected",
                "reason": str(error),
                "state_unchanged": processor.state_digest() == baseline_state,
                "metrics": None,
                "qualifies": False,
            }
        else:
            raise AssertionError("unexpectedly accepted " + name)

    bad = list(clean_frame)
    bad[3] = float("nan")
    reject("nonfinite_microphone", bad, clean_ref, 1, 0)
    bad = list(clean_frame)
    bad[3] = 1.5
    reject("out_of_range_microphone", bad, clean_ref, 1, 0)
    reject("short_microphone", clean_frame[:-1], clean_ref, 1, 0)
    reject("reference_length_mismatch", clean_frame, clean_ref[:-1], 1, 0)
    reject("stale_epoch", clean_frame, clean_ref, 9, 0)
    reject("stale_position", clean_frame, clean_ref, 1, fixture.FRAME_SAMPLES)

    cases["missing_near_reference"] = {
        "status": "withheld_missing_reference",
        "reason": "no clean near-end reference for this stratum",
        "metrics": None,
        "qualifies": False,
    }
    cases["missing_far_end_only_window"] = {
        "status": "withheld_no_valid_far_end_only_window",
        "reason": "near-only render cannot yield an ERLE window",
        "metrics": None,
        "qualifies": False,
    }
    if not all(case["qualifies"] is False for case in cases.values()):
        raise AssertionError("invalid case qualified")
    return cases


def build_report() -> Dict[str, Any]:
    contract = json.loads((ROOT / "contract.json").read_text(encoding="utf-8"))
    scorer_digest = fixture.sha256_bytes((ROOT / "scorer.py").read_bytes())
    invalid_cases = invalid_and_missing_cases()
    data_by_condition = {name: fixture.fixture(name) for name in fixture.CONDITIONS}
    results: Dict[str, Any] = {}
    for name, data in data_by_condition.items():
        identity = _result(data, "identity")
        results[name] = {"identity": identity}
        if name == "no_reference":
            results[name][CANDIDATE] = _result(data, CANDIDATE)
            continue
        preservation = identity["near_preservation"]
        for variant in (CANDIDATE,) + CONTROLS[1:]:
            results[name][variant] = _result(data, variant, preservation)

    missing_by_row = {
        "%s/%s" % (condition, variant): row["missing_results"]
        for condition, variants in results.items()
        for variant, row in variants.items()
        if row["missing_results"]
    }
    qualifying_rows = [
        "%s/%s" % (condition, variant)
        for condition, variants in results.items()
        for variant, row in variants.items()
        if row["qualifies"]
    ]
    report: Dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "mode": "research-control",
        "verification_profile": "evidence with frozen room controls",
        "disposition": "proposal_only_incomplete_not_qualified",
        "status": "proposal_only_incomplete_not_qualified",
        "decision": {
            "direction": "defer",
            "proposal_only": True,
            "incomplete": True,
            "release_qualification": "not_qualified",
            "processor_exposure": "none",
            "paired_processor": "none",
            "before_any_processor_exposure": True,
            "rationale": [
                "Only seeded synthetic paired signals and analytic echo paths are measured.",
                "No licensed recorded render/capture, clean near speech, AECMOS, ASR or listening evidence exists here.",
                "No measured loop gain, target-device timing, deadline or resource result exists here.",
                "Provider, license and catalog intake has not been performed.",
            ],
        },
        "format": {
            "channels": fixture.CHANNELS,
            "frame_samples": fixture.FRAME_SAMPLES,
            "sample_format": fixture.SAMPLE_FORMAT,
            "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
        },
        "fixture_digest": fixture.fixture_digest(),
        "fixture_spec": fixture.fixture_spec(),
        "candidate_settings": {
            "algorithm": "causal samplewise NLMS on explicit render reference",
            "step_size": STEP_SIZE,
            "leak": LEAK,
            "taps": TAPS,
            "double_talk_hold": DOUBLE_TALK_HOLD,
            "hold_note": "Instantaneous hold disabled: pinned research showed sharp ERLE loss; no detector is proposed.",
        },
        "source_pins": contract["source_pins"],
        "boundary_pins": contract["boundary_pins"],
        "mutable_provenance": contract["mutable_provenance"],
        "streams": {
            name: data["streams_sha256"] for name, data in data_by_condition.items()
        },
        "results": results,
        "controls": {
            "separation": "ERLE windows, near preservation and fixed controls are reported in separate fields; fixed/identity rows never qualify.",
            "historical_fixed_hybrid": contract["historical_control"],
            "synthetic_fixed_hybrid_replay": {
                "note": "Oracle-gated fixed gain replay on the frozen synthetic fixture; not a replay of the pinned real-recording scores.",
                "control": "fixed_hybrid_damage_replay",
            },
        },
        "acceptance_profile": {
            "profile": "evidence",
            "room_controls_applied": True,
            "scorer_pin_sha256": scorer_digest,
            "corpus": "frozen seeded synthetic signals only; no external corpus, model, WAV or download",
            "cohort": list(fixture.CONDITIONS),
            "cohort_size": len(fixture.CONDITIONS),
            "aggregation": "Exact per-window and per-condition scalar metrics; no cross-condition averaging, tolerance widening or provider substitution.",
            "control_variants": list(CONTROLS),
            "failed_items": sorted(invalid_cases),
            "failed_item_count": len(invalid_cases),
        },
        "bundle_validation": {
            "entrypoint": "python3 run.py --request <json>",
            "representative_valid_result": {
                "condition": "overlap_50",
                "variant": CANDIDATE,
                "expected_qualifies": True,
            },
            "invalid_or_missing_case": {
                "condition": "no_reference",
                "variant": CANDIDATE,
                "expected_status": "blocked_no_reference",
                "expected_qualifies": False,
            },
            "rule": "Adapter responses for both requests must match the checked-in report row on status, metrics, missing_results and qualifies.",
        },
        "mdf_limitation_disclosure": {
            "source": MDF_EVIDENCE_PATH,
            "status": "merged_speex_mdf_tool_observation_not_reproduced_here",
            "aligned_erle_db": MDF_ALIGNED_ERLE_DB,
            "misaligned_erle_db": MDF_MISALIGNED_ERLE_DB,
            "overlap_near_ratio": MDF_OVERLAP_NEAR_RATIO,
            "note": "The merged MDF reference measured higher ERLE on a one-frame misaligned render than on the aligned render, and its small-overlap near-ratio window contains residual echo. ERLE is not an alignment detector and overlap near-ratio is not a double-talk quality result.",
        },
        "invalid_and_missing_cases": invalid_cases,
        "qualification": {
            "no_missing_result_may_qualify": True,
            "rule": "A row qualifies only when its status is ok and every applicable ERLE and near-preservation metric is present; missing or withheld results force qualifies=false.",
            "qualifying_rows": qualifying_rows,
            "rows_with_missing_results": missing_by_row,
            "missing_result_count": sum(len(value) for value in missing_by_row.values()),
            "candidate_rows_with_all_required_metrics": sorted(
                condition for condition, variants in results.items()
                if variants[CANDIDATE]["status"] == "ok"
                and not variants[CANDIDATE]["missing_results"]
            ),
        },
        "release_gates": contract["release_gates"],
        "non_claims": [
            "No real recording, room impulse response, measured device buffer or clock drift.",
            "No AECMOS, ASR word accuracy, MOS, pystoi production scorer or authorized listening result.",
            "No loudspeaker/microphone loop, loop gain or gain-before-feedback measurement.",
            "No target-device CPU, memory, pacing, deadline or availability timing.",
            "No SDK processor, provider registration, descriptor, catalog entry, default or installed-v0 change.",
            "No historical source-reported score is reproduced or treated as local evidence.",
            "No Tiny16 comparison was run; there is no S10/protocol clearance, approved independent reference adapter or permitted case manifest here.",
            "ERLE does not validate render alignment; see mdf_limitation_disclosure.",
        ],
    }
    core = dict(report)
    repeat_digests = [fixture.sha256_bytes(fixture.canonical_bytes(core)) for _ in range(3)]
    report["repeat_runs"] = {
        "three_repeats": 3,
        "byte_identical": len(set(repeat_digests)) == 1,
        "canonical_digests": repeat_digests,
        "note": "Canonical digests of the report core without repeat_runs; verify.py also performs three byte-identical CLI regenerations.",
    }
    return report

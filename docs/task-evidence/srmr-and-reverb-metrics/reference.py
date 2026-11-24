# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen synthetic cohort and canonical report for SRMR/reverb evidence.

No audio files, RIRs, device captures, listening results or benchmark payloads
are stored. Every signal is regenerated from the integer seeds, tap table and
LCG pinned below. SRMR is scored only by the pinned task-local scorer; the
early-to-late RIR energy ratio is explicitly a synthetic C50-style proxy, not
an official REVERB Challenge result.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Any, Dict, List, Optional, Sequence, Tuple

import scorer

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
CONTRACT_ID = "audio-sdk/srmr-reverb-evidence/0.1"
REPORT_SCHEMA_ID = "audio-sdk/srmr-reverb-evidence-report/0.1"
BASE_COMMIT = "a64e1096905f0d05a46303fc0167b6f356027765"
TASK_ID = "SDK-SRMR-AND-REVERB-METRICS"
TASK_PREFIX = "docs/task-evidence/srmr-and-reverb-metrics/"
REPORT_FILE = HERE / "report.json"
SIDECAR_FILE = HERE / "report.json.sha256"
PINS_FILE = HERE / "SOURCES.sha256"
CROSSCHECK_FILE = HERE / "crosscheck_vectors.json"
CONTRACT_FILE = HERE / "contract.json"
ADAPTER_FILE = HERE / "adapter.json"
PROVIDER_FILE = HERE / "provider.json"

SAMPLE_RATE_HZ = 16000
CLIP_SAMPLES = 32000
CLIP_SECONDS = 2.0
RIR_SAMPLES = int(0.8 * SAMPLE_RATE_HZ)
EARLY_WINDOW_MS = 50
EARLY_WINDOW_SAMPLES = int(round(EARLY_WINDOW_MS * SAMPLE_RATE_HZ / 1000.0))
LN1000 = math.log(1000.0)
SYLLABLE_COUNT = 8
SYLLABLE_SAMPLES = 3200
SYLLABLE_STEP_SAMPLES = 4000
SOURCE_NOISE_SEED = 20261124
SOURCE_NOISE_AMPLITUDE = 0.004
SOURCE_PEAK = 0.9
MIN_SAMPLES_FOR_INVALID = scorer.MIN_SAMPLES
EARLY_TAPS_MS = (5.0, 11.0, 19.0, 29.0, 41.0, 53.0)
EARLY_TAPS_AMPLITUDE = (0.70, 0.50, 0.35, 0.25, 0.18, 0.12)
TAIL_START_MS = 2.0
TAIL_AMPLITUDE = 0.10
CONVOLUTION_DECIMALS = 15

ROOM_SPECS: Dict[str, Dict[str, int]] = {
    "short_rt60": {"rt60_ms": 250, "seed": 8101},
    "medium_rt60": {"rt60_ms": 550, "seed": 8102},
    "long_rt60": {"rt60_ms": 900, "seed": 8103},
}

# Metadata pins; byte digests are repeated in SOURCES.sha256 and checked by verify.py.
EXTERNAL_PINS: Dict[str, Dict[str, Any]] = {
    "srmrpy": {
        "url": "https://github.com/jfsantos/SRMRpy/archive/"
               "fee009779cef96bed34db3a7e31d10f3ad1ea133.tar.gz",
        "commit": "fee009779cef96bed34db3a7e31d10f3ad1ea133",
        "implementation": "srmrpy.srmr.srmr(fast=True, norm=False)",
        "license": "MIT",
        "archive_sha256": "9163eb964e77a6e42ada5b7320869036f3e553eef018c9be457e86c51084703a",
        "source_file_sha256": {
            "srmrpy/srmr.py": "ed23aa832c6b470d1c7069b419ff8d4a5be0ec69f45aeb1fe71992c3fbebdbbc",
            "srmrpy/modulation_filters.py": "372ac4a17f281b7d652a7a68581788b1ee84c858db5dc92e2414905e3a7978dc",
            "srmrpy/segmentaxis.py": "c727c9710b7a1c25d25b650fabe04db064870378461af9b48a46a034adf9fdf0",
        },
    },
    "gammatone": {
        "url": "https://files.pythonhosted.org/packages/de/37/9beb1eec3e3a62e3da9128a83d78516f5d911009f5e3b7ebf6fea19f9ebc/"
               "Gammatone-1.0.3-py3-none-any.whl",
        "version": "1.0.3",
        "implementation": "gammatone.fftweight.fft_gtgram",
        "license": "BSD-3-Clause",
        "wheel_sha256": "410a07344bacac651c3d8d466e25888e1925f00458f054871485c0aa22d78061",
        "source_file_sha256": {
            "gammatone/fftweight.py": "b3ee20916b8e1a85851130b6d139f8e4624668158bd63fcb11eb2a7afc84a55d",
            "gammatone/filters.py": "a79826d6e4904c394e957d8555df6c40ac12bec710704271798130c6c5d85422",
            "gammatone/gtgram.py": "cd2da79aa9209da6b12f228e695f0774c86a4e987ca7d3413aad37e328f4ba3e",
        },
    },
}

CROSSCHECK_RUNTIME = {
    "python": "3.12.16",
    "numpy": "2.5.4",
    "scipy": "1.18.1",
    "mode": "external scratch environment; upstream SRMRpy plus Gammatone 1.0.3 "
            "were loaded from the exact bytes pinned in EXTERNAL_PINS",
}


class RequestError(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, sha256(text.encode("utf-8"))


def tensor_digest(values: Sequence[float]) -> str:
    """Bit-exact digest over IEEE-754 little-endian f32 sample words."""
    return sha256(b"".join(struct.pack("<f", float(value)) for value in values))


def object_digest(value: Any) -> str:
    return sha256(canonical_bytes(value))


def file_digest(path: Path) -> str:
    return sha256(path.read_bytes())


def read_source_pins() -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for raw in PINS_FILE.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("#"):
            continue
        digest, path = raw.split("  ", 1)
        if path.startswith("external:"):
            continue
        pins[path] = digest
    return pins


class _LCG:
    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def uniform(self) -> float:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state / 4294967296.0


def _lcg_stream(seed: int):
    generator = _LCG(seed)
    while True:
        yield generator.uniform()


def clean_source() -> List[float]:
    """Eight synthetic voiced syllables plus pinned low-level LCG noise."""
    uniform = _lcg_stream(SOURCE_NOISE_SEED)
    values = [0.0] * CLIP_SAMPLES
    for syllable in range(SYLLABLE_COUNT):
        start = syllable * SYLLABLE_STEP_SAMPLES
        fundamental = 100.0 + 10.0 * (syllable % 3)
        for index in range(SYLLABLE_SAMPLES):
            envelope = math.sin(math.pi * index / (SYLLABLE_SAMPLES - 1)) ** 2
            t = index / SAMPLE_RATE_HZ
            harmonic = (
                math.sin(2.0 * math.pi * fundamental * t)
                + 0.5 * math.sin(2.0 * math.pi * 2.0 * fundamental * t)
                + 0.25 * math.sin(2.0 * math.pi * 3.0 * fundamental * t)
            )
            values[start + index] += envelope * harmonic
    values = [value + SOURCE_NOISE_AMPLITUDE * (next(uniform) * 2.0 - 1.0)
              for value in values]
    peak = max(abs(value) for value in values)
    return [value * SOURCE_PEAK / peak for value in values]


def synthetic_rir(rt60_ms: int, seed: int) -> List[float]:
    """Six signed early taps and an exponentially decaying LCG diffuse tail."""
    uniform = _lcg_stream(seed)
    tau = (rt60_ms / 1000.0) / LN1000
    taps = [0.0] * RIR_SAMPLES
    taps[0] = 1.0
    for delay_ms, amplitude in zip(EARLY_TAPS_MS, EARLY_TAPS_AMPLITUDE):
        index = int(round(delay_ms * SAMPLE_RATE_HZ / 1000.0))
        sign = 1.0 if next(uniform) < 0.5 else -1.0
        taps[index] += sign * amplitude
    tail_start = int(round(TAIL_START_MS * SAMPLE_RATE_HZ / 1000.0))
    for index in range(tail_start, RIR_SAMPLES):
        t = index / SAMPLE_RATE_HZ
        taps[index] += TAIL_AMPLITUDE * math.exp(-t / tau) * (next(uniform) * 2.0 - 1.0)
    energy = math.fsum(value * value for value in taps)
    scale = 1.0 / math.sqrt(energy)
    return [value * scale for value in taps]


def convolve_source(rir: Sequence[float], early_only: bool = False) -> List[float]:
    taps = list(rir[:EARLY_WINDOW_SAMPLES]) if early_only else list(rir)
    source = clean_source()
    unscaled = scorer.fft_convolve(source, taps, CLIP_SAMPLES)
    peak = max(abs(value) for value in unscaled)
    return [value * SOURCE_PEAK / peak for value in unscaled]


def early_to_late_db(rir: Sequence[float]) -> float:
    early = math.fsum(value * value for value in rir[:EARLY_WINDOW_SAMPLES])
    late = math.fsum(value * value for value in rir[EARLY_WINDOW_SAMPLES:])
    return 10.0 * math.log10(early / late)


def fixture_samples(case_id: str) -> List[float]:
    """Resolve a pinned fixture name to the same bytes used in the report."""
    if case_id == "dry_source":
        return clean_source()
    for name, spec in ROOM_SPECS.items():
        rir = synthetic_rir(spec["rt60_ms"], spec["seed"])
        if case_id == name + "_input":
            return convolve_source(rir)
        if case_id == name + "_early_target":
            return convolve_source(rir, early_only=True)
    raise RequestError("unknown_fixture_case")


def _round(value: float, digits: int = 12) -> float:
    return round(float(value), digits)


def fixture_spec(source_digest: str, rir_digests: Dict[str, str]) -> Dict[str, Any]:
    return {
        "contract": CONTRACT_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "sample_format": "f32-shaped finite values generated as f64, digested as f32",
        "clip_samples": CLIP_SAMPLES,
        "source_noise_seed": SOURCE_NOISE_SEED,
        "source_noise_amplitude": SOURCE_NOISE_AMPLITUDE,
        "syllable_count": SYLLABLE_COUNT,
        "syllable_samples": SYLLABLE_SAMPLES,
        "syllable_step_samples": SYLLABLE_STEP_SAMPLES,
        "source_digest": source_digest,
        "rir_samples": RIR_SAMPLES,
        "early_window_ms": EARLY_WINDOW_MS,
        "early_window_samples": EARLY_WINDOW_SAMPLES,
        "early_taps_ms": list(EARLY_TAPS_MS),
        "early_taps_amplitude": list(EARLY_TAPS_AMPLITUDE),
        "tail_start_ms": TAIL_START_MS,
        "tail_amplitude": TAIL_AMPLITUDE,
        "lcg": "state=(1664525*state+1013904223) mod 2^32; uniform=state/2^32",
        "convolution": "radix-2 FFT, inverse output rounded to 15 decimal places",
        "convolution_decimals": CONVOLUTION_DECIMALS,
        "rooms": ROOM_SPECS,
        "rir_digests": rir_digests,
    }


def _crosscheck() -> Dict[str, Any]:
    vectors = json.loads(CROSSCHECK_FILE.read_text(encoding="utf-8"))
    if not isinstance(vectors, dict) or "vectors" not in vectors:
        raise RequestError("invalid_crosscheck_file")
    return vectors


def build_report() -> Dict[str, Any]:
    source = clean_source()
    source_digest = tensor_digest(source)
    dry_score, dry_reason = scorer.srmr(source)
    if dry_score is None or dry_reason:
        raise RuntimeError("dry source control missing: " + str(dry_reason))

    conditions: Dict[str, Any] = {}
    rir_digests: Dict[str, str] = {}
    for name, spec in ROOM_SPECS.items():
        rir = synthetic_rir(spec["rt60_ms"], spec["seed"])
        rir_digest = tensor_digest(rir)
        rir_digests[name] = rir_digest
        reverberant = convolve_source(rir)
        early_target = convolve_source(rir, early_only=True)
        reverberant_score, reverberant_reason = scorer.srmr(reverberant)
        early_score, early_reason = scorer.srmr(early_target)
        if (reverberant_score is None or reverberant_reason
                or early_score is None or early_reason):
            raise RuntimeError("missing representative result in " + name)
        c50 = early_to_late_db(rir)
        conditions[name] = {
            "rt60_ms": spec["rt60_ms"],
            "rir_seed": spec["seed"],
            "rir_digest": rir_digest,
            "c50_early_to_late_db_proxy": _round(c50),
            "reverberant_input_digest": tensor_digest(reverberant),
            "reverberant_input_srmr": _round(reverberant_score),
            "early_target_digest": tensor_digest(early_target),
            "early_target_srmr": _round(early_score),
            "delta_early_minus_reverberant_srmr": _round(early_score - reverberant_score),
            "scored_region": [0, CLIP_SAMPLES],
            "source_digest": source_digest,
        }

    scores = [condition["reverberant_input_srmr"] for condition in conditions.values()]
    c50_values = [condition["c50_early_to_late_db_proxy"] for condition in conditions.values()]
    deltas = [condition["delta_early_minus_reverberant_srmr"]
              for condition in conditions.values()]
    scores_sorted = sorted(scores)
    c50_sorted = sorted(c50_values)
    deltas_sorted = sorted(deltas)

    representative = conditions["medium_rt60"]
    representative_samples = convolve_source(
        synthetic_rir(ROOM_SPECS["medium_rt60"]["rt60_ms"],
                      ROOM_SPECS["medium_rt60"]["seed"]))
    repeat_scores: List[Optional[float]] = []
    for _ in range(3):
        value, reason = scorer.srmr(representative_samples)
        if reason:
            raise RuntimeError("representative repeat failed: " + reason)
        repeat_scores.append(value)

    invalid_cases = {
        "missing_samples": scorer.srmr(None),
        "empty_samples": scorer.srmr([]),
        "nonfinite_samples": scorer.srmr([0.0] * MIN_SAMPLES_FOR_INVALID
                                         + [float("nan")]),
        "silence": scorer.srmr([0.0] * scorer.MIN_SAMPLES),
        "unsupported_sample_rate": scorer.srmr(source, 48000),
    }
    invalid_report = {
        name: {"status": "rejected" if reason else "unexpected_score",
               "reason": reason, "score": score}
        for name, (score, reason) in invalid_cases.items()
    }
    if any(row["status"] != "rejected" for row in invalid_report.values()):
        raise RuntimeError("invalid control unexpectedly scored")

    crosscheck = _crosscheck()
    crosscheck_digest = file_digest(CROSSCHECK_FILE)
    max_delta = max(abs(vector["abs_delta"]) for vector in crosscheck["vectors"])
    if max_delta > scorer.CROSSCHECK_ABS_TOLERANCE:
        raise RuntimeError("crosscheck exceeds pinned tolerance")

    pins = read_source_pins()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "contract": CONTRACT_ID,
        "status": "proceed_adapter_defer_processor",
        "task": TASK_ID,
        "base_commit": BASE_COMMIT,
        "decision": {
            "evidence_adapter": "proceed",
            "sdk_processor": "defer",
            "registration": "none",
            "rationale": (
                "The pinned SRMR implementation and matched synthetic cohort are "
                "reproducible and the proxy behaves as expected across pinned RT60, "
                "but there is no rights-cleared real input, paired quality result "
                "or blind listening result. Retain an opt-in developer/evidence "
                "adapter only; do not expose a processor or make a selection."),
        },
        "scope": (
            "synthetic matched cohort only; no real RIR, device capture, listening "
            "study, quality claim, pacing claim, release gate or public benchmark "
            "result"),
        "evidence_kinds": {
            "paired_synthetic": {
                "status": "present",
                "description": "each RT60 condition pairs full-RIR and 50 ms early-target convolutions of one pinned source",
                "condition_count": len(conditions),
            },
            "unpaired_synthetic": {
                "status": "none",
                "description": "no independent unpaired corpus is used; dry source is a scored control, not an outcome cohort",
            },
            "synthetic": {
                "status": "present",
                "description": "analytic syllables, explicit early taps, LCG diffuse tail and FFT convolution",
            },
            "human": {
                "status": "none",
                "description": "no listeners, MUSHRA, MOS, transcripts or subjective ratings",
            },
            "source_reported": {
                "status": "excluded_from_results",
                "description": "research document quotes upstream NeMo/ROSE/Stream.FM scores; they are not reproduced or compared here",
                "source_pin": "source:research/dereverberation_candidates_20261028.md",
            },
            "real_rir_or_device": {"status": "none", "description": "no measured RIR or microphone capture"},
            "public_benchmark": {
                "status": "none",
                "description": "REVERB Challenge material is not staged locally; no official REVERB score is claimed",
            },
        },
        "fixture": object_digest(fixture_spec(source_digest, rir_digests)),
        "fixture_spec": fixture_spec(source_digest, rir_digests),
        "source_pins": pins,
        "external_pins": EXTERNAL_PINS,
        "board_snapshot": {
            "path": "source:audio-benchmark-platform/plan/swarm/TASKS.json",
            "sha256_at_read": pins["source:audio-benchmark-platform/plan/swarm/TASKS.json"],
            "mutable": True,
        },
        "scorer": {
            "scorer_id": scorer.SCORER_ID,
            "upstream_scorer_id": scorer.UPSTREAM_SCORER_ID,
            "upstream_gammatone_id": scorer.UPSTREAM_GAMMATONE_ID,
            "algorithm": "SRMRpy fast path, norm=False, 23 cochlear filters, 4-128 Hz modulation filters",
            "approval": {
                "scope": "task-local evidence reproduction only",
                "status": "pinned_for_evidence",
                "sdk_release_intake": "pending",
            },
            "sample_rate_hz": scorer.SAMPLE_RATE_HZ,
            "min_samples": scorer.MIN_SAMPLES,
            "crosscheck_abs_tolerance": scorer.CROSSCHECK_ABS_TOLERANCE,
            "crosscheck_file_sha256": crosscheck_digest,
            "crosscheck_runtime": CROSSCHECK_RUNTIME,
            "crosschecks": crosscheck["vectors"],
            "crosscheck_max_abs_delta": _round(max_delta, 18),
        },
        "cohort": {
            "dry_source": {
                "digest": source_digest,
                "srmr": _round(dry_score),
                "note": "source-dependent control; never compared across corpora",
            },
            "conditions": conditions,
        },
        "aggregation": {
            "method": "median across the three pinned RT60 conditions; descriptive only",
            "median_reverberant_srmr": _round(scores_sorted[1]),
            "median_c50_early_to_late_db_proxy": _round(c50_sorted[1]),
            "median_delta_early_minus_reverberant_srmr": _round(deltas_sorted[1]),
            "selection_threshold": None,
            "selection_performed": False,
        },
        "interpretation": (
            "On this matched synthetic cohort, SRMR falls as pinned RT60 rises and "
            "the C50-style proxy falls with it. This is source-dependent non-intrusive "
            "dereverberation evidence only. SRMR is complementary to paired quality "
            "metrics and blind listening and must not be used alone to select a "
            "processor or make a quality claim."),
        "controls": {
            "representative_valid": {
                "case": "medium_rt60",
                "digest": representative["reverberant_input_digest"],
                "srmr": representative["reverberant_input_srmr"],
                "status": "scored",
            },
            "invalid_and_missing": invalid_report,
            "identity": {
                "first": _round(repeat_scores[0]),
                "second": _round(repeat_scores[1]),
                "third": _round(repeat_scores[2]),
                "byte_identical_scores": len({_round(value, 18) for value in repeat_scores}) == 1,
            },
            "upstream_crosscheck": {
                "case_count": len(crosscheck["vectors"]),
                "max_abs_delta": _round(max_delta, 18),
                "within_pinned_tolerance": max_delta <= scorer.CROSSCHECK_ABS_TOLERANCE,
            },
        },
        "failed_items": [
            {
                "id": "official_reverb_benchmark",
                "status": "not_run",
                "reason": "LDC-gated material is not staged; no official REVERB score is claimed",
            },
            {
                "id": "real_rir_and_device",
                "status": "not_run",
                "reason": "rights-cleared RIR/speech inputs and device path are outside synthetic evidence scope",
            },
            {
                "id": "blind_listening",
                "status": "not_run",
                "reason": "no human cohort, protocol or ratings",
            },
            {
                "id": "source_reported_upstream_scores",
                "status": "excluded",
                "reason": "quoted upstream figures are not reproducible from pinned local inputs",
            },
            {
                "id": "tiny16_adverse_comparison",
                "status": "not_applicable",
                "reason": "no S10/protocol clearance, approved independent reference adapter or permitted case manifest",
            },
        ],
        "qualification": {
            "status": "not_qualified",
            "required_results_present": True,
            "no_missing_result_may_qualify": True,
            "excluded_from_qualification": [
                "invalid and missing cases",
                "source-reported upstream scores",
                "dry source control",
                "REVERB Challenge references",
            ],
            "remaining_gates": [
                "exact-head independent review",
                "hosted CI",
                "scorer license and version intake",
                "rights-cleared RIR and speech inputs",
                "paired quality metrics with fixed protocol",
                "blind listening",
                "release approval before any processor exposure",
            ],
        },
    }

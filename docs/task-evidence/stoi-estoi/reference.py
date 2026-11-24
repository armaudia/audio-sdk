# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen STOI/ESTOI comparison and canonical report construction.

The report is paired synthetic developer evidence under the ``evidence``
acceptance profile.  It pins the scorer sources, the synthetic cohort, the
aggregation, the missing/invalid controls and the opt-in adapter validation.
No result here qualifies a processor, a corpus, a listener or a release.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from statistics import fmean
from typing import Any, Dict, List, Optional, Tuple

import fixture
import scorer

ROOT = Path(__file__).resolve().parent
CROSSCHECK_PATH = ROOT / "crosscheck_vectors.json"
PROTOCOL = "sdk.stoi-estoi-evidence.v1"
DECISION = "defer"
METRICS = ("stoi", "estoi")
RESEARCH_SOURCE = "research/listening_intelligibility_20261028.md"
RESEARCH_SHA256 = "f29de5cdb58676b6f61ac8489ff5af44a88b2125c2022920436a6f064405992a"
VERIFICATION_SOURCE = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
VERIFICATION_SHA256 = "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910"
TASK_SOURCE = "audio-benchmark-platform/plan/swarm/TASKS.json"
TASK_SHA256_AT_READ = "7cd94ec7a32f3ff8ff8df1c7a8e40db0f888c31634721ec2e58bd147d2605a53"
BASE_COMMIT = "a64e1096905f0d05a46303fc0167b6f356027765"

INTERPRETATION = (
    "STOI is the non-extended, per-band temporal-envelope correlation score; "
    "ESTOI applies row/column normalization to the same 1/3-octave envelope "
    "segments and is intended to be less sensitive to masker envelope "
    "modulation. On this synthetic cohort the two scores therefore disagree "
    "most under the 4 Hz gated masker: ESTOI is higher than STOI at -5 and "
    "0 dB there, while STOI is higher under the steady masker. This is a "
    "scorer-behavior comparison on generated signals, not a claim about speech "
    "intelligibility, listening effort, enhancement benefit or any candidate."
)


def read_strict_json(path: Path) -> Dict[str, Any]:
    """Load JSON without duplicate keys, NaN/Infinity constants or non-object roots."""
    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise ValueError("nonfinite_json_constant:" + token)

    value = json.loads(path.read_text(encoding="utf-8"),
                       object_pairs_hook=pairs, parse_constant=constant)
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    return value


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def score_variant(clean: List[float], row: Optional[Dict[str, Any]]
                  ) -> Dict[str, Any]:
    """Score one matched variant with explicit blocked/failed/invalid reasons."""
    if row is None:
        return {"status": "blocked", "reason": "missing_input",
                "digest": None, "metrics": None}
    values = row["values"]
    if len(values) != fixture.SAMPLES:
        return {"status": "failed", "reason": "invalid_geometry",
                "digest": row["digest"], "metrics": None}
    if not all(math.isfinite(value) for value in values):
        return {"status": "invalid", "reason": "nonfinite_input",
                "digest": row["digest"], "metrics": None}
    results = scorer.scores(clean, values, fixture.RATE_HZ)
    metrics: Dict[str, Any] = {}
    reasons: List[str] = []
    for name in METRICS:
        value, reason = results[name]
        metrics[name] = {"value": value, "reason": reason}
        if reason:
            reasons.append(reason)
    if reasons:
        return {"status": "invalid", "reason": reasons[0],
                "digest": row["digest"], "metrics": None}
    return {"status": "scored", "reason": None,
            "digest": row["digest"], "metrics": metrics}


def build_score_rows(items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    clean = fixture.target()
    rows: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for item in items:
        rows[item["item_id"]] = {
            name: score_variant(clean, item["variants"][name])
            for name in fixture.VARIANTS
        }
    return rows


def _delta(candidate: Dict[str, Any], identity: Dict[str, Any], metric: str
           ) -> Tuple[Optional[float], Optional[str]]:
    first = candidate["metrics"][metric]["value"] if candidate["metrics"] else None
    second = identity["metrics"][metric]["value"] if identity["metrics"] else None
    if first is None or second is None:
        return None, candidate["reason"] or identity["reason"]
    return first - second, None


def summaries(items: List[Dict[str, Any]], rows: Dict[str, Dict[str, Dict[str, Any]]]
              ) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for variant in fixture.VARIANTS:
        if variant == "identity_noisy":
            continue
        result[variant] = {}
        for metric in METRICS:
            deltas: Dict[str, float] = {}
            excluded: Dict[str, Dict[str, Optional[str]]] = {}
            by_kind: Dict[str, List[float]] = {kind: [] for kind in fixture.MASKER_KINDS}
            for item in items:
                item_id = item["item_id"]
                delta, reason = _delta(rows[item_id][variant],
                                       rows[item_id]["identity_noisy"], metric)
                if delta is None:
                    excluded[item_id] = {
                        "candidate": rows[item_id][variant]["reason"],
                        "identity": rows[item_id]["identity_noisy"]["reason"],
                        "detail": reason,
                    }
                else:
                    deltas[item_id] = delta
                    by_kind[item["masker_kind"]].append(delta)
            result[variant][metric] = {
                "eligible": len(items),
                "paired": len(deltas),
                "paired_delta": deltas,
                "excluded": excluded,
                "mean_delta": fmean(deltas.values()) if deltas else None,
                "mean_delta_by_masker_kind": {
                    kind: fmean(values) if values else None
                    for kind, values in by_kind.items()
                },
                "coverage": "complete" if not excluded else (
                    "partial_diagnostic" if deltas else "unavailable"),
            }
    return result


def metric_difference(items: List[Dict[str, Any]],
                      rows: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """ESTOI minus STOI on identical matched pairs (same unit interval scale)."""
    per_item: Dict[str, Dict[str, Optional[float]]] = {}
    for item in items:
        item_id = item["item_id"]
        per_item[item_id] = {}
        for variant in fixture.VARIANTS:
            row = rows[item_id][variant]
            if row["metrics"] is None:
                per_item[item_id][variant] = None
                continue
            value = row["metrics"]["estoi"]["value"] - row["metrics"]["stoi"]["value"]
            per_item[item_id][variant] = value
    by_kind = {
        kind: fmean([
            per_item[item["item_id"]]["identity_noisy"]
            for item in items if item["masker_kind"] == kind
        ])
        for kind in fixture.MASKER_KINDS
    }
    return {
        "definition": "estoi_value - stoi_value on the same paired signal",
        "per_item": per_item,
        "identity_noisy_mean_by_masker_kind": by_kind,
        "note": "Synthetic scores are not clamped; a negative value is reported as computed by the pinned port.",
    }


def crosscheck_summary() -> Dict[str, Any]:
    vectors = read_strict_json(CROSSCHECK_PATH)
    maximum = {
        metric: max(vector["abs_delta_" + metric] for vector in vectors["vectors"])
        for metric in METRICS
    }
    return {
        "source_pystoi_version": vectors["pystoi_version"],
        "source_numpy_version": vectors["numpy_version"],
        "source_scipy_version": vectors["scipy_version"],
        "source_sha256": vectors["source_sha256"],
        "vectors_sha256": hashlib.sha256(CROSSCHECK_PATH.read_bytes()).hexdigest(),
        "vector_count": len(vectors["vectors"]),
        "max_abs_delta": maximum,
        "oracle_use": "external cross-check only; never an acceptance threshold or candidate oracle",
    }


def build_report() -> Dict[str, Any]:
    items, pinned = fixture.cohort()
    rows = build_score_rows(items)
    report: Dict[str, Any] = {
        "protocol": PROTOCOL,
        "evidence_kind": "paired_synthetic_developer_only",
        "task": "SDK-STOI-ESTOI",
        "component": "stoi-estoi",
        "verification_profile": "evidence",
        "base_commit": BASE_COMMIT,
        "decision": {
            "promotion": DECISION,
            "expose_as_processor": False,
            "registered": False,
            "default_enabled": False,
            "basis": "Only frozen synthetic STOI/ESTOI scores are available. No held-out speech, listener, rights, device, license or release gate is cleared.",
        },
        "source_pins": {
            "research": {"path": RESEARCH_SOURCE, "sha256": RESEARCH_SHA256,
                         "use": "historical CLN-12 source-reported screen; not reproduced here"},
            "verification_profile": {"path": VERIFICATION_SOURCE, "sha256": VERIFICATION_SHA256,
                                     "use": "evidence acceptance profile"},
            "board_snapshot": {"path": TASK_SOURCE, "sha256_at_read": TASK_SHA256_AT_READ,
                               "mutable": True},
        },
        "scorer": {
            "scorer_id": scorer.SCORER_ID,
            "pystoi_version": scorer.PYSTOI_VERSION,
            "algorithm_pins": list(scorer.PYSTOI_ALGORITHM_PINS),
            "source_sha256": dict(scorer.PYSTOI_SOURCE_SHA256),
            "rate_hz": fixture.RATE_HZ,
            "metrics": list(METRICS),
            "dither": "deterministic no-dither port; cross-check deltas recorded",
            "audio_bench_metric": False,
        },
        "fixture": pinned,
        "aggregation": {
            "unit": "one paired candidate-minus-identity delta per item and metric",
            "mean": "arithmetic mean with equal item weight; no sample pooling, bootstrap or ranking",
            "coverage": "complete only when every planned item is paired; partial rows are diagnostics",
            "failed_items": [
                item_id for item_id, row in rows.items()
                if any(row[name]["status"] != "scored" for name in
                       ("identity_noisy", "less_masker", "more_masker", "tilt", "gain_only"))
            ],
        },
        "items": [
            {
                "item_id": item["item_id"],
                "masker_kind": item["masker_kind"],
                "snr_db": item["snr_db"],
                "clean_digest": item["clean_digest"],
                "masker_digest": item["masker_digest"],
                "clean_rms": item["clean_rms"],
                "masker_rms": item["masker_rms"],
                "mixture_rms": item["mixture_rms"],
                "mixture_peak": item["mixture_peak"],
                "variants": {
                    name: {
                        "status": rows[item["item_id"]][name]["status"],
                        "reason": rows[item["item_id"]][name]["reason"],
                        "digest": rows[item["item_id"]][name]["digest"],
                        "metrics": rows[item["item_id"]][name]["metrics"],
                    }
                    for name in fixture.VARIANTS
                },
            }
            for item in items
        ],
        "summaries": summaries(items, rows),
        "metric_difference": metric_difference(items, rows),
        "crosscheck": crosscheck_summary(),
        "interpretation": INTERPRETATION,
        "source_reported_context": {
            "path": RESEARCH_SOURCE,
            "status": "historical source-reported, not reproduced or used as an oracle",
            "note": "The historical screen used EARS/VADToolkit speech, STOI/ESTOI and a bootstrap interval crossing zero for fixed tilt; it clears no rights and establishes no listener benefit.",
        },
        "claims_not_made": [
            "No real-speech, corpus, listening, MOS, intelligibility or quality claim.",
            "No device, CPU, deadline, pacing, availability or content-delay claim.",
            "No public benchmark, leaderboard, default, ABI, installed-provider or release claim.",
            "No Tiny16 comparison, S10 protocol clearance or permitted case manifest.",
        ],
    }
    return report

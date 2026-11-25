#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Rebuild the canonical ENG-02 survey report and its digests from pinned sources.

Read-only with respect to every pinned source. The only outputs are the three
task-local files report.json, report.json.sha256 and SOURCES.sha256.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]

SCHEMA_ID = "audio-sdk/survey-evidence-map/0.1"
BASE_COMMIT = "c9296ae96a2b58efae559bd22e7760122c886df8"
BRANCH = "swarm/SDK-SURVEY-ENG-02"
WORKTREE = "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SURVEY-ENG-02"
GAP_ID = "SDK-SURVEY-ENG-02-LIVE-CLOCK-DRIFT-FEASIBILITY"

# Workspace-relative paths. SDK files are pinned through the canonical checkout
# path and must be byte-identical to the copy in this worktree.
PINS: dict[str, str] = {
    "audio_categories.md": "Companion category row: families, boundary and named leads",
    "research/category_registry.json": "Original ENG-02 catalogue fields, S27/S41 leads and statuses",
    "research/task_backlog.json": "Legacy backlog state for ENG-02 / F16",
    "audio-benchmark-platform/plan/swarm/TASKS.json": "Board row, write scope, dependency and dispatch claim",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "Evidence, Room, Rate and Tool acceptance profiles",
    "audio-benchmark-platform/plan/INVENTORY.json": "Component IDs, tasks, evidence status and verification profile",
    "research/aec_research_20261028.md": "Historical paired render/capture pilots, alignment and explicit drift limit",
    "research/voice-enhancement-20261101/agent-hybrid-aec-real/REPORT.md": "Recorded-real loader: no extra delay compensation",
    "REALTIME_COMPONENT_CANDIDATES.md": "AEC3 historical alignment and no live clock-drift/device test",
    "realtime-audio-library/implementation_record.md": "Clock-domain calibration audit and hardware limitation",
    "cpp-library/PIPELINE_DESIGN_REPORT.md": "Delay-contract and live-clock-drift boundary for chains",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md": "Fixed v0 sample/clock coordinates; no implicit conversion",
    "audio-benchmark-platform/audio-sdk/docs/evidence-handoff.md": "Exact interval, clock and denominator rules for future evidence",
    "audio-benchmark-platform/audio-sdk/docs/task-evidence/duplex-clocks/README.md": "Proposal-only render/capture clock fixture",
    "audio-benchmark-platform/audio-sdk/docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md": "Proposal-only source clock map, ppm bound and impulse delay probe",
    "audio-benchmark-platform/audio-sdk/RELEASING.md": "Release policy: no qualification follows from this map",
}

# Every quotation must be present verbatim in the named pin. This keeps the
# survey from silently drifting away from the evidence it cites.
QUOTES: tuple[tuple[str, str], ...] = (
    ("audio_categories.md", "| **ENG-02 — Clock drift, alignment and reference synchronization** |"),
    ("audio_categories.md", "Delay estimation; rate adjustment; drift compensation"),
    ("audio_categories.md", "Learned estimation is optional research, not required"),
    ("research/aec_research_20261028.md", "Reject misaligned inputs rather than silently trimming them."),
    ("research/aec_research_20261028.md", "content alignment of 125–128 samples (about 8 ms)"),
    ("research/aec_research_20261028.md", "known model/content offsets are removed before scoring (LocalVQE 16 ms, WebRTC 8 ms)"),
    ("research/aec_research_20261028.md", "does not measure capture-clock drift"),
    ("research/aec_research_20261028.md", "real-recording clock-drift tests"),
    ("research/voice-enhancement-20261101/agent-hybrid-aec-real/REPORT.md", "It applies no extra delay compensation."),
    ("REALTIME_COMPONENT_CANDIDATES.md", "No live clock-drift or device test."),
    ("realtime-audio-library/implementation_record.md", "The offset is not automatically refreshed after suspend or a device restart"),
    ("realtime-audio-library/implementation_record.md", "clock discontinuity during a run is not qualified"),
    ("realtime-audio-library/implementation_record.md", "no physical AudioUnit or CoreAudio device callback evidence"),
    ("cpp-library/PIPELINE_DESIGN_REPORT.md", "Results lack blind-set, live clock-drift and target-device evidence."),
    ("cpp-library/PIPELINE_DESIGN_REPORT.md", "Delay contracts are implementation-specific."),
    ("cpp-library/PIPELINE_DESIGN_REPORT.md", "Jitter-buffer delay is unmeasured."),
    ("audio-benchmark-platform/audio-sdk/CONTRACTS.md", "At 16 kHz one sample is exactly 62,500 ns"),
    ("audio-benchmark-platform/audio-sdk/CONTRACTS.md", "Use a single monotonic clock domain for measured intervals and an explicit stream origin"),
    ("audio-benchmark-platform/audio-sdk/docs/evidence-handoff.md", "Sample positions, clock ticks"),
    ("audio-benchmark-platform/audio-sdk/docs/evidence-handoff.md", "available_monotonic_ns"),
    ("audio-benchmark-platform/audio-sdk/docs/task-evidence/duplex-clocks/README.md", "explicitly lacks live clock-drift"),
    ("audio-benchmark-platform/audio-sdk/docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md", "Absolute drift is bounded at 10000 ppm."),
    ("audio-benchmark-platform/audio-sdk/docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md", "source timestamp subtraction or acoustic-phase fitting."),
    ("audio-benchmark-platform/plan/swarm/VERIFICATION.md", "Pin the scorer, corpus and cohort, aggregation, failed items and controls."),
)

# Declared component identity is checked against the inventory record itself.
COMPONENTS: dict[str, dict[str, str]] = {
    "webrtc-aec3": {"task": "SDK-WEBRTC-AEC3", "evidence_status": "evaluated", "verification_profile": "room"},
    "webrtc-apm": {"task": "SDK-WEBRTC-APM", "evidence_status": "considered", "verification_profile": "rate"},
    "webrtc-neteq": {"task": "SDK-WEBRTC-NETEQ", "evidence_status": "considered", "verification_profile": "tool"},
    "aec-challenge-paired-render-capture-fixtures": {"task": "SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES", "evidence_status": "evaluated", "verification_profile": "evidence"},
    "typed-frame-resample-and-drift-diagnostics": {"task": "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS", "evidence_status": "source-local", "verification_profile": "tool"},
    "coreaudio-audiounit-duplex-host": {"task": "SDK-COREAUDIO-AUDIOUNIT-DUPLEX-HOST", "evidence_status": "partial", "verification_profile": "tool"},
    "native-capture-recipe-and-render-timeline": {"task": "PRO-NATIVE-CAPTURE-RECIPE-AND-RENDER-TIMELINE", "evidence_status": "native-local", "verification_profile": "tool"},
    "pesq-polqa-and-3quest": {"task": "SDK-PESQ-POLQA-AND-3QUEST", "evidence_status": "partial", "verification_profile": "evidence"},
    "buffer-occupancy-controller": {"task": "SDK-BUFFER-OCCUPANCY-CONTROLLER", "evidence_status": "considered", "verification_profile": "rate"},
    "opus-1-4-standard-decoder-plc": {"task": "SDK-OPUS-1-4-STANDARD-DECODER-PLC", "evidence_status": "evaluated", "verification_profile": "enhancement"},
    "cagcrn-joint-aec-and-ns": {"task": "SDK-CAGCRN-JOINT-AEC-AND-NS", "evidence_status": "considered", "verification_profile": "room"},
    "aecmos": {"task": "SDK-AECMOS", "evidence_status": "evaluated", "verification_profile": "evidence"},
}

SOURCE_LEADS = [
    {
        "id": "S27",
        "registry_title": "WebRTC audio processing interface",
        "url": "https://webrtc.googlesource.com/src/+/refs/heads/main/api/audio/audio_processing.h",
        "access_scope": "direct",
        "mapped_components": ["webrtc-apm", "webrtc-aec3", "webrtc-apm-ns"],
        "historical_executions": [
            "WebRTC AEC3 12-scenario synthetic training pilot: measured 125–128-sample (~8 ms) content alignment, fixed 128-sample scoring offset.",
            "WebRTC AEC3 real training pilot: known 8 ms content offset removed before AECMOS scoring; no capture-clock-drift measurement.",
            "Recorded-real hybrid AEC loader trims far-end/capture to common sample count and applies no extra delay compensation.",
        ],
        "limits": [
            "The registry records a direct URL without a pinned revision or a local checkout; it is a source lead, not local source evidence.",
            "Measured content alignment is an offline scoring offset, not sample-clock tracking, device latency or synchronization qualification.",
        ],
    },
    {
        "id": "S41",
        "registry_title": "WebRTC NetEq documentation",
        "url": "https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_coding/neteq/g3doc/index.md",
        "access_scope": "direct",
        "mapped_components": ["webrtc-neteq", "opus-1-4-standard-decoder-plc", "buffer-occupancy-controller"],
        "historical_executions": [
            "Opus 1.4 PLC pilot reported a fixed 104-sample / 6.5 ms codec alignment with jitter-buffer delay unmeasured.",
            "No local NetEq trace replay, time-scale control run or drift record is present in the reviewed pins.",
        ],
        "limits": [
            "S41 is a documentation lead. Inventory marks WebRTC NetEq as considered with a registry-only evidence path.",
            "Receive-side jitter buffering and adaptive playout belong to SDK-SURVEY-ENG-03; rate adjustment starts here only at the source-clock/contract boundary.",
        ],
    },
]

CLASSICAL = [
    {
        "family": "Delay estimation",
        "component_ids": ["webrtc-aec3", "aec-challenge-paired-render-capture-fixtures", "pesq-polqa-and-3quest"],
        "comparison_inputs": [
            "Paired 16 kHz mono far-end render and microphone capture, 12 synthetic train scenarios from the AEC Challenge source revision 8f861f0f8ffca26a3d1d16f17f2594ea89abe7ac.",
            "12 recorded device groups from the same challenge training tree (108 files); no blind test audio.",
            "Offline paired clean/noisy scoring replay with independently measured content lag; kept separate from render/capture pilots.",
        ],
        "controls": [
            "Declared render/capture rate and channel layout; misaligned inputs are rejected rather than silently trimmed.",
            "Known content offsets: AEC3 125–128 samples (~8 ms), LocalVQE one 256-sample hop (16 ms), 0/20/40 ms stream-delay-hint pilot.",
            "Fixed 128-sample AEC3 scoring offset and separately reported model offsets; no adaptive clock tracking was run.",
        ],
        "assets": [
            "Historical local AEC Challenge train-only audio and per-file manifests (ignored workspace data, not redistributed).",
            "Installed pywebrtc-audio 0.2.0 binding, local SpeexDSP library and compact LocalVQE weights from the cited pilots.",
            "AECMOS v4 ONNX weights used as a learned metric, not as a delay estimator.",
        ],
        "local_outcomes": [
            {"status": "local_historical", "finding": "AEC3 content alignment was measured at 125–128 samples (about 8 ms) on clean near-only trials; the real pilot removed a known 8 ms offset before scoring.", "pin": "research/aec_research_20261028.md"},
            {"status": "local_historical", "finding": "A stream-delay-hint pilot (0, 20, 40 ms) showed little near-end change; 0 ms remained the default pending recordings with known capture/playback buffer delay.", "pin": "research/aec_research_20261028.md"},
        ],
        "reported_outcomes": [
            {"status": "reported_only", "finding": "S27 names the WebRTC processing interface; the registry does not pin an upstream drift or alignment result.", "pin": "research/category_registry.json"},
        ],
        "limits": [
            "These are fixed offsets on historical local pilots. No component measures or compensates live capture-clock drift in these records.",
            "AEC Challenge training data are not cleared for redistribution or acceptance; no audio is added by this survey.",
        ],
    },
    {
        "family": "Rate adjustment",
        "component_ids": ["typed-frame-resample-and-drift-diagnostics", "duplex-clocks", "speex-resampler", "buffer-occupancy-controller", "webrtc-neteq"],
        "comparison_inputs": [
            "Exact integer source sample indices, declared source rates (48/32/16 kHz) and an explicit target rate; no audio media.",
            "Declared integer ppm drift, half-open sample intervals and one monotonic clock domain.",
        ],
        "controls": [
            "Exact rational 48 kHz→16 kHz impulse mapping; explicit selection required; missing rate/channel/format selection is rejected.",
            "Duplicate/stale timestamps, gaps, overlaps, missing roles, nonfinite input and drift beyond the declared bound are rejected as distinct states.",
            "Bounded drain and finite tail accounted as non-content; concealment never satisfies conservation.",
        ],
        "assets": [
            "Task-local proposal fixtures only (typed-frame and duplex-clocks directories); no weights, corpora or recordings are introduced.",
        ],
        "local_outcomes": [
            {"status": "local_historical_model", "finding": "Typed-frame proposal reports content delay D=173 samples measured by a source-coordinate impulse, with absolute drift bounded at 10000 ppm; it is a developer-tool model, not an SDK provider.", "pin": "audio-benchmark-platform/audio-sdk/docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md"},
            {"status": "local_historical_model", "finding": "Duplex-clocks proposal maps a declared +6250 ppm capture drift and rejects gaps, overlaps and missing roles; the fixture explicitly does not supply live clock-drift evidence.", "pin": "audio-benchmark-platform/audio-sdk/docs/task-evidence/duplex-clocks/README.md"},
        ],
        "reported_outcomes": [
            {"status": "reported_only", "finding": "S41 documentation supplies a time-scale/rate-adjustment lead; no local NetEq time-scale experiment is recorded here.", "pin": "research/category_registry.json"},
            {"status": "reported_only", "finding": "Buffer occupancy is a control law, not an estimator; catch-up/slow-down timing belongs to the rate and playout boundary.", "pin": "cpp-library/PIPELINE_DESIGN_REPORT.md"},
        ],
        "limits": [
            "Both clock fixtures are proposal-only and outside the fixed v0 ABI; no native build, installed provider or paced device workload was run for them here.",
            "This survey does not implement or enable rate conversion, resampling, buffering or time-scale control.",
        ],
    },
    {
        "family": "Drift compensation",
        "component_ids": ["coreaudio-audiounit-duplex-host", "native-capture-recipe-and-render-timeline", "typed-frame-resample-and-drift-diagnostics", "duplex-clocks"],
        "comparison_inputs": [
            "CLOCK_MONOTONIC_RAW worker timestamps and CoreAudio Mach absolute host timestamps on the historical macOS host.",
            "Synthetic 48 kHz/480-sample callback frames split across 160- and 320-sample invocations; no opened audio device.",
            "Declared sample-coordinate ppm maps from the two proposal fixtures.",
        ],
        "controls": [
            "Setup-time Mach-to-raw offset bracket with bounded arithmetic and carried calibration uncertainty; calibration failure aborts before streaming.",
            "Simulated callback topology checks and 160/320-sample frame split; host-only CTest coverage, not a device test.",
            "Explicit missing-reference state and rejected stale/future/sample-offset/uncertainty mismatch in the provisional render-reference path.",
        ],
        "assets": [
            "Historical macOS host toolchain and simulated AudioUnit callback path; no microphone access and no written audio in the cited self-test.",
            "No new asset, device entitlement or provider registration is introduced by this survey.",
        ],
        "local_outcomes": [
            {"status": "local_historical", "finding": "The clock-domain audit calibrated a Mach-to-raw offset and carried interval uncertainty; the offset is not refreshed after suspend or restart, and clock discontinuity during a run is not qualified.", "pin": "realtime-audio-library/implementation_record.md"},
            {"status": "local_historical", "finding": "The AudioUnit self-test exercised a 160/320-sample frame split in simulation; no physical AudioUnit or CoreAudio device callback evidence was available.", "pin": "realtime-audio-library/implementation_record.md"},
        ],
        "reported_outcomes": [
            {"status": "reported_only", "finding": "The composition report states that delay contracts are implementation-specific and that matched AEC results lack live clock-drift and target-device evidence.", "pin": "cpp-library/PIPELINE_DESIGN_REPORT.md"},
        ],
        "limits": [
            "No live drift tracking, suspend/restart recovery, device clock recovery or blind-set result exists in the reviewed pins.",
            "M2 render-reference work in the historical record remained capability-discovery disabled and is not a public SDK capability.",
        ],
    },
]

ML_AUDIT = {
    "catalogued_text": "Learned estimation is optional research, not required",
    "audited": True,
    "component_ids": ["cagcrn-joint-aec-and-ns", "aecmos"],
    "result": "no_owned_estimator_component",
    "findings": [
        "The registry audits an ML family but marks learned estimation optional. No catalogued component implements a learned delay/clock-drift estimator for ENG-02.",
        "CAGCRN is cited in AEC research for delay alignment and requires paired reference input; only a paper lead and compatibility work are recorded, not a local drift run.",
        "AECMOS is a learned, scenario-aware metric applied after known 8/16 ms content offsets are removed; it is not a learned alignment or drift estimator.",
    ],
    "missing_evidence": [
        "No pinned ML source revision, runnable checkpoint or matched render/capture cohort for clock-drift estimation.",
        "No drift-labeled target, independent holdout or uncertainty result; background AEC papers are citations, not local executions.",
        "The legacy backlog records ENG-02/F16 as catalogued with next action 'Plan discovery across required source buckets'; it does not authorize a learned implementation.",
    ],
}

GAP = {
    "id": GAP_ID,
    "parent_task": "SDK-SURVEY-ENG-02",
    "category_id": "ENG-02",
    "status": "proposed_unassigned_not_run",
    "owner": None,
    "board_entry": False,
    "dependencies": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    "consult": ["SDK-WEBRTC-AEC3", "SDK-COREAUDIO-AUDIOUNIT-DUPLEX-HOST", "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS", "SDK-FND-DUPLEX", "SDK-WEBRTC-NETEQ"],
    "gap": "No component owns a bounded, asset-free replay of declared sample-clock drift plus reference gap/discontinuity on paired render/capture coordinates. Historical AEC pilots fixed offsets; clock-domain calibration was setup-only; the two clock fixtures are proposals.",
    "smallest_check": {
        "inputs": "Authored integer sample-coordinate sequences only: 16 kHz mono render/capture maps, one declared +6250 ppm capture drift, one declared missing segment and one contiguous control.",
        "expected": "Known impulse maps to the declared target coordinate under drift; missing/gap rows return a reason and no interpolated value; contiguous control remains exact; all attempts are retained with distinct reason codes.",
        "deliverable": "Task-local replay and canonical metadata report with frozen fixture digest, exact sample intervals, reason codes and byte-identical rerun.",
        "exclusions": "No real audio, model, device, callback, ABI, descriptor, provider enablement, build or CI change; no quality, listening, latency or release claim.",
    },
    "stop_boundary": "Feasibility only. A later implementation or target-device measurement requires a separate owner, exact clock-domain policy and task-local qualification under SDK-FND-ANALYSIS.",
}

PROHIBITED_CLAIMS = {
    "public_benchmark_claim": "not_made",
    "quality_or_listening_claim": "not_made",
    "device_qualification_claim": "not_made",
    "release_or_publication_claim": "not_made",
    "provider_enablement": "not_made",
    "default_abi_build_or_ci_change": "not_made",
    "asset_or_real_audio_added": "not_made",
    "implemented_clock_drift_capability": "not_made",
}


def find_workspace(root: Path) -> Path:
    for candidate in (root, *root.parents):
        if ((candidate / "research" / "category_registry.json").is_file()
                and (candidate / "audio_categories.md").is_file()
                and (candidate / "audio-benchmark-platform" / "plan" / "INVENTORY.json").is_file()):
            return candidate
    raise RuntimeError("cannot locate enclosing audioml workspace")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(workspace: Path, path: str) -> str:
    target = workspace / path
    return target.read_text(encoding="utf-8")


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def build_report(workspace: Path) -> tuple[bytes, dict[str, str]]:
    """Reconstruct the canonical report bytes and source digests.

    The function is deliberately free of output writes so the verifier and
    tests can rebuild the same artifact without mutating pinned sources.
    """
    texts = {path: read_text(workspace, path) for path in PINS}
    for path, quote in QUOTES:
        if quote not in texts[path]:
            raise RuntimeError(f"missing pinned quotation in {path}: {quote!r}")

    for sdk_path in ("CONTRACTS.md", "docs/evidence-handoff.md",
                     "docs/task-evidence/duplex-clocks/README.md",
                     "docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md"):
        pin = f"audio-benchmark-platform/audio-sdk/{sdk_path}"
        if (workspace / pin).read_bytes() != (SDK_ROOT / sdk_path).read_bytes():
            raise RuntimeError(f"SDK worktree copy differs from pinned path: {sdk_path}")

    registry = json.loads(texts["research/category_registry.json"])
    backlog = json.loads(texts["research/task_backlog.json"])
    board = json.loads(texts["audio-benchmark-platform/plan/swarm/TASKS.json"])
    inventory = json.loads(texts["audio-benchmark-platform/plan/INVENTORY.json"])

    category = next(item for item in registry["categories"] if item["id"] == "ENG-02")
    sources = {item["id"]: item for item in registry["sources"]}
    backlog_entry = next(item for item in backlog["entries"] if item["category_id"] == "ENG-02")
    task = next(item for item in board["tasks"] if item["id"] == "SDK-SURVEY-ENG-02")
    components = {item["id"]: item for item in inventory["components"]}
    for component_id, expected in COMPONENTS.items():
        record = components[component_id]
        for key, value in expected.items():
            if record.get(key) != value:
                raise RuntimeError(f"inventory drift for {component_id}.{key}: {record.get(key)!r} != {value!r}")
    if any(item.get("id") == GAP_ID for item in board["tasks"]):
        raise RuntimeError("feasibility gap must not be a board task")

    digests = {path: sha256_bytes((workspace / path).read_bytes()) for path in sorted(PINS)}
    source_pins = [{"path": path, "sha256": digests[path], "use": use} for path, use in sorted(PINS.items())]

    report = {
        "schema_id": SCHEMA_ID,
        "task_id": task["id"],
        "task_title": task["title"],
        "mode": task["mode"],
        "repository": task["repository"],
        "owner": task["owner"],
        "reviewer": task["claim"]["reviewer"],
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": WORKTREE,
        "dependencies": task["depends_on"],
        "write_scope": task["write_scope"],
        "disposition": "survey_only: read-only taxonomy and comparison map; no execution or qualification claim",
        "catalogue": {
            "registry_source": "research/category_registry.json",
            "taxonomy_revision": registry["taxonomy_revision"],
            "survey_date": registry["survey_date"],
            "category": category,
            "companion_row_source": "audio_categories.md",
            "companion_row": next(line for line in texts["audio_categories.md"].splitlines()
                                  if line.startswith("| **ENG-02 —")),
            "legacy_backlog_source": "research/task_backlog.json",
            "legacy_backlog": backlog_entry,
            "legacy_backlog_snapshot": backlog["snapshot"],
        },
        "board_deliverable": task["deliverable"],
        "board_acceptance": task["acceptance"],
        "source_leads": [
            {
                **{key: sources[lead["id"]][key] for key in ("id", "title", "url", "researcher", "access_scope")},
                "mapped_components": lead["mapped_components"],
                "historical_executions": lead["historical_executions"],
                "limits": lead["limits"],
            }
            for lead in SOURCE_LEADS
        ],
        "component_matches": [
            {
                "component_id": component_id,
                "name": components[component_id]["name"],
                "task": components[component_id]["task"],
                "evidence_status": components[component_id]["evidence_status"],
                "verification_profile": components[component_id]["verification_profile"],
                "repository": components[component_id]["repository"],
                "disposition": components[component_id]["disposition"],
            }
            for component_id in COMPONENTS
        ],
        "method_families": {
            "classic": {"catalogued_text": category["method_families"]["classic"], "entries": CLASSICAL},
            "ml": {"catalogued_text": category["method_families"]["ml"], **ML_AUDIT},
        },
        "comparison_boundary": {
            "input_output": category["input_output"],
            "live_or_comparison_boundary": category["live_or_comparison_boundary"],
            "controls_profile": "Evidence profile pins scorer, corpus/cohort, controls and failed items; Room/Rate/Tool profiles remain separate.",
            "denominators": "Exact integer sample intervals, consumed/produced counts, availability clock and reason codes must be frozen before any later run.",
            "release_boundary": [
                "Historical local, reported-only, proposal-only and not-run outcomes are kept separate; none is promoted to a public benchmark.",
                "No quality, listening, device, callback, availability, throughput or release result is claimed from this map.",
                "No audio, model, scorer output or licensed asset is added, replayed or redistributed here.",
                "No public SDK ABI, descriptor, provider default, engine routing, build or CI setting is changed.",
                "Rights, participant consent and platform clock evidence remain with the original component owners and release policy.",
            ],
        },
        "coverage_audit": {
            "classical_families_audited": [item["family"] for item in CLASSICAL],
            "ml_family_audited": True,
            "source_leads_covered": [lead["id"] for lead in SOURCE_LEADS],
            "historical_executions_covered": True,
            "missing_evidence_reasons": [
                "Registry discovery is catalogued while candidate census and benchmark remain not_started.",
                "Legacy backlog records only a discover/plan next action, with no matched ENG-02 cohort or scorer.",
                "AEC pilots measured fixed content offsets and explicitly did not measure capture-clock drift.",
                "Clock-domain calibration was setup-only; discontinuity during a run was not qualified and no hardware was available.",
                "Clock fixtures are proposal-only models; NetEq has registry-only evidence; ML learned estimation is optional with no owned component.",
            ],
        },
        "gap": GAP,
        "prohibited_claims": PROHIBITED_CLAIMS,
        "source_pin_policy": {
            "sidecar": "SOURCES.sha256",
            "paths": "workspace-relative; SDK paths use the canonical audio-benchmark-platform/audio-sdk checkout and are compared byte-for-byte with this worktree",
            "meaning": "Document/metadata digests only; a pin grants no rights and verifies no media, device or provider claim",
        },
        "source_pins": source_pins,
        "reproduction": {
            "python": "3.12.16",
            "env": "PYTHONDONTWRITEBYTECODE=1",
            "builder": "python3 build.py",
            "verifier": "python3 verify.py",
            "tests": "python3 docs/task-evidence/survey-eng-02/test_evidence_map.py -v",
            "repo_checks": ["scripts/ci.py --output build/ci", "reuse lint", "git diff --check"],
        },
    }
    return canonical(report), digests


def write_outputs() -> tuple[str, str]:
    """Write only the three canonical task-local output files."""
    workspace = find_workspace(SDK_ROOT)
    report_bytes, digests = build_report(workspace)
    (TASK_DIR / "report.json").write_bytes(report_bytes)
    report_digest = sha256_bytes(report_bytes)
    (TASK_DIR / "report.json.sha256").write_text(f"{report_digest}  report.json\n", encoding="utf-8")
    sources_sidecar = "".join(f"{digests[path]}  {path}\n" for path in sorted(digests))
    (TASK_DIR / "SOURCES.sha256").write_text(sources_sidecar, encoding="utf-8")
    return report_digest, sha256_bytes(sources_sidecar.encode("utf-8"))


def main() -> None:
    report_digest, sources_digest = write_outputs()
    print(f"report.json  {report_digest}")
    print(f"SOURCES.sha256  {sources_digest}")


if __name__ == "__main__":
    main()

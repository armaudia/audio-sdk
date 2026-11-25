#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Generate the canonical SDK-SURVEY-ENG-01 evidence map and pin manifest."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
# The canonical bytes must not depend on where the checkout lives. This literal
# is the board row's claim worktree; verify.py checks it against the board.
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SURVEY-ENG-01"
)
PINNED_WORKSPACE = Path("/Users/htsakanyan/workspace/audio/audioml")


def _find_workspace() -> Path:
    """Locate the pinned audioml workspace without affecting canonical bytes."""
    override = os.environ.get("AUDIOML_WORKSPACE_ROOT")
    candidates = [Path(override)] if override else []
    candidates.extend(HERE.parents)
    candidates.append(PINNED_WORKSPACE)
    for candidate in candidates:
        if (
            (candidate / "research/category_registry.json").is_file()
            and (candidate / "audio-benchmark-platform/plan/INVENTORY.json").is_file()
        ):
            return candidate
    raise RuntimeError("audioml workspace not found; set AUDIOML_WORKSPACE_ROOT")


WORKSPACE = _find_workspace()
PLATFORM = WORKSPACE / "audio-benchmark-platform"
TASK_ID = "SDK-SURVEY-ENG-01"
CATEGORY_ID = "ENG-01"
BASE_COMMIT = "c9296ae96a2b58efae559bd22e7760122c886df8"
BRANCH = f"swarm/{TASK_ID}"
REVIEWER = "reviewer-SURVEY-ENG-01"

ROOTS = {
    "workspace": WORKSPACE,
    "platform": PLATFORM,
    "sdk": WORKTREE,
}

# Pins are documents or metadata only. No audio, model, image or other asset is
# downloaded, copied, generated or made part of this evidence directory.
PIN_SPECS = (
    ("workspace:audio_categories.md", "workspace", "audio_categories.md",
     "Readable category catalog; ENG-01 family and comparison boundary."),
    ("workspace:research/category_registry.json", "workspace", "research/category_registry.json",
     "Machine-readable ENG-01 record, S42 lead and catalog statuses."),
    ("workspace:research/task_backlog.json", "workspace", "research/task_backlog.json",
     "Legacy F16 backlog state and next action."),
    ("workspace:research/category_survey/sources.md", "workspace",
     "research/category_survey/sources.md", "S42 access scope and named URL."),
    ("workspace:cpp-library/pipeline-validation/playback-speed-candidates.md", "workspace",
     "cpp-library/pipeline-validation/playback-speed-candidates.md",
     "Reported comparator matrix for libsamplerate / libsoxr / Speex resampler."),
    ("workspace:src/audioml_eval/audio.py", "workspace", "src/audioml_eval/audio.py",
     "Offline WAV/resampling boundary mirrored by the evaluated tool fixture."),
    ("platform:plan/INVENTORY.json", "platform", "plan/INVENTORY.json",
     "Component IDs, owners, dispositions and evidence status."),
    ("platform:plan/swarm/VERIFICATION.md", "platform", "plan/swarm/VERIFICATION.md",
     "Evidence and Tool acceptance profiles used by the reviewed fixtures."),
    ("sdk:CONTRACTS.md", "sdk", "CONTRACTS.md",
     "Fixed v0 format, explicit resampling=none and interval/epoch contract."),
    ("sdk:README.md", "sdk", "README.md",
     "Host-owned sample-rate conversion and task-local PCM/resampling controls."),
    ("sdk:core/providers/speex/provider.cmake", "sdk", "core/providers/speex/provider.cmake",
     "Vendored resample.c compiled into a private object; no resampler API is exported."),
    ("sdk:core/providers/speex/speex_provider.c", "sdk", "core/providers/speex/speex_provider.c",
     "Speex NS provider uses fixed 16 kHz/mono/f32 frames and no resampling path."),
    ("sdk:third_party/speexdsp/UPSTREAM.md", "sdk", "third_party/speexdsp/UPSTREAM.md",
     "Vendored SpeexDSP revision, provenance and source license notice."),
    ("sdk:third_party/speexdsp/libspeexdsp/resample.c", "sdk",
     "third_party/speexdsp/libspeexdsp/resample.c",
     "Local source counterpart to the S42 upstream path; not an executable run."),
    ("sdk:docs/task-evidence/numpy-scipy-soundfile-wav-resampling/report.json", "sdk",
     "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/report.json",
     "Evaluated offline WAV/resampling Tool-profile fixture report."),
    ("sdk:docs/task-evidence/typed-frame-resample-and-drift-diagnostics/report.json", "sdk",
     "docs/task-evidence/typed-frame-resample-and-drift-diagnostics/report.json",
     "Source-local explicit conversion, delay and finite-tail model report."),
    ("sdk:docs/task-evidence/identity-pcm-and-noop-fixtures/README.md", "sdk",
     "docs/task-evidence/identity-pcm-and-noop-fixtures/README.md",
     "Installed identity PCM/noop baseline and its adverse controls."),
    ("sdk:docs/task-evidence/quality-impairment-taxonomy/README.md", "sdk",
     "docs/task-evidence/quality-impairment-taxonomy/README.md",
     "Survey precedent for taxonomy-only mapping and bounded feasibility handoff."),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def pin_path(key: str) -> Path:
    for label, root, relative, _ in PIN_SPECS:
        if label == key:
            return ROOTS[root] / relative
    raise KeyError(key)


def board_projection() -> dict:
    board = json.loads((PLATFORM / "plan/swarm/TASKS.json").read_text(encoding="utf-8"))
    rows = [row for row in board["tasks"] if row["id"] == TASK_ID]
    if len(rows) != 1:
        raise RuntimeError(f"expected one board row for {TASK_ID}")
    row = rows[0]
    stable_fields = (
        "id", "title", "repository", "mode", "owner", "depends_on",
        "write_scope", "deliverable", "acceptance", "evidence", "claim",
    )
    projection = {field: row[field] for field in stable_fields}
    projection_bytes = json.dumps(
        projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return {
        "fields": list(stable_fields),
        "projection_sha256": sha256_bytes(projection_bytes),
        "note": "Mutable review/handoff fields are excluded; the claim pin is included.",
    }


def build_pins() -> list[dict]:
    return [
        {
            "key": key,
            "path": key,
            "sha256": sha256_file(pin_path(key)),
            "use": use,
        }
        for key, _root, _relative, use in PIN_SPECS
    ]


def build_report() -> dict:
    pins = build_pins()
    digest_by_key = {row["key"]: row["sha256"] for row in pins}
    return {
        "schema_id": "audio-sdk.survey-eng-01.evidence-map/v1",
        "task_id": TASK_ID,
        "category_id": CATEGORY_ID,
        "legacy_family_id": "F16",
        "title": "Framing, format conversion and resampling",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "survey_owner": "agent-SURVEY-ENG-01",
        "reviewer": REVIEWER,
        "disposition": "taxonomy_and_comparison_only",
        "qualification_status": "not_started_no_new_execution",
        "claim_gate": {
            "no_missing_result_qualifies_candidate": True,
            "public_benchmark": False,
            "quality": False,
            "device": False,
            "listening": False,
            "release": False,
            "provider_enablement": False,
            "real_audio_or_assets": False,
            "default_abi_build_or_ci_change": False,
        },
        "scope": {
            "purpose": "Provide correct formats and rates to candidates.",
            "scope_label": "support",
            "output_kind": "engineering",
            "input_output": "PCM formats/rates -> normalized interface",
            "live_or_comparison_boundary": (
                "Resampling is not bandwidth restoration; include conversion cost and delay "
                "in chain accounting."
            ),
            "fixed_v0_boundary": {
                "sample_rate_hz": 16000,
                "channels": 1,
                "sample_format": "f32",
                "frame_samples": 160,
                "effective_config_resampling": "none",
                "conversion_location": "host/or developer tooling outside the provider ABI",
            },
            "board_dependencies": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
            "board_write_scope": ["Category evidence map and bounded gap handoff"],
        },
        "original_method_families": {
            "classic": [
                {
                    "id": "framing-channel-mapping",
                    "registry_text": "Framing/channel mapping",
                    "mapped_components": [
                        "typed-frame-resample-and-drift-diagnostics",
                        "identity-pcm-and-noop-fixtures",
                        "speexdsp-ns-reference",
                    ],
                    "evidence_status": "source-local_model_and_installed_identity_control",
                    "missing_evidence": (
                        "No native installed provider or measured device framing/channel path "
                        "was run; the explicit-conversion model is Python-only and outside v0."
                    ),
                },
                {
                    "id": "bandlimited-resampling",
                    "registry_text": "Bandlimited resampling",
                    "mapped_components": [
                        "numpy-scipy-soundfile-wav-and-resampling",
                        "speex-resampler",
                        "libsamplerate",
                        "libsoxr",
                    ],
                    "evidence_status": "offline_tool_evaluated_upstream_leads_considered",
                    "missing_evidence": (
                        "No pinned executable S42/SpeexDSP resampler comparison, no anti-alias "
                        "or transient control, and no measured conversion cost/delay at an SDK "
                        "boundary. NumPy/SciPy polyphase output is not evidence for SpeexDSP."
                    ),
                },
            ],
            "ml": {
                "id": "no-ml-requirement",
                "registry_text": "No ML requirement",
                "mapped_components": [],
                "status": "not_applicable",
                "missing_evidence": (
                    "No ML family is catalogued for ENG-01. No model, checkpoint, weight "
                    "search or learned-quality result is expected; no ML evidence is missing."
                ),
            },
        },
        "source_leads": [
            {
                "id": "S42",
                "title": "SpeexDSP resampler implementation",
                "registry_url": (
                    "https://github.com/xiph/speexdsp/blob/master/libspeexdsp/resample.c"
                ),
                "registry_access_scope": "direct",
                "registry_revision_pin": "unpinned master URL",
                "local_counterpart": {
                    "pin_key": "sdk:third_party/speexdsp/libspeexdsp/resample.c",
                    "sha256": digest_by_key[
                        "sdk:third_party/speexdsp/libspeexdsp/resample.c"
                    ],
                    "upstream_revision": "7a158783df74efe7c2d1c6ee8363c1e695c71226 (v1.2.1)",
                    "license": "BSD-3-Clause-style notice in third_party/speexdsp/COPYING",
                    "relation": (
                        "Same upstream project and path; not a byte-equal pin of the unpinned "
                        "master URL recorded by the registry."
                    ),
                },
                "component_mapping": [
                    {
                        "component_id": "speex-resampler",
                        "task_id": "SDK-SPEEX-RESAMPLER",
                        "evidence_status": "considered",
                        "disposition": "sdk-reference",
                    },
                    {
                        "component_id": "speexdsp-ns-reference",
                        "task_id": "SDK-SPEEXDSP-NS-REFERENCE",
                        "evidence_status": "integrated",
                        "disposition": "sdk-reference",
                        "relation": (
                            "Owns the private SpeexDSP object build, including resample.c, "
                            "but exposes a fixed-format NS provider and no resampling API."
                        ),
                    },
                ],
                "local_outcome": (
                    "Source is present and compiled into a private object; no local bandlimited "
                    "resampler execution, rate-pair matrix or conversion cost result was found."
                ),
                "reported_outcome": (
                    "Playback-speed matrix labels libsamplerate / libsoxr / Speex resampler as "
                    "varispeed-only with very low latency/effort and a cheap fallback if pitch "
                    "shift is acceptable; no local measurement supports that label."
                ),
            }
        ],
        "component_map": [
            {
                "component_id": "typed-frame-resample-and-drift-diagnostics",
                "task_id": "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS",
                "evidence_status": "source-local",
                "disposition": "sdk-tool",
                "family": "framing-channel-mapping",
                "role": "Explicit conversion, clock map, delay and finite-tail proposal only.",
            },
            {
                "component_id": "identity-pcm-and-noop-fixtures",
                "task_id": "SDK-IDENTITY-PCM-AND-NOOP-FIXTURES",
                "evidence_status": "integrated",
                "disposition": "sdk-reference",
                "family": "framing-channel-mapping",
                "role": "Bit-exact D=0 PCM control at the installed fixed v0 boundary.",
            },
            {
                "component_id": "numpy-scipy-soundfile-wav-and-resampling",
                "task_id": "SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING",
                "evidence_status": "evaluated",
                "disposition": "sdk-tool",
                "family": "bandlimited-resampling",
                "role": "Offline FLOAT WAV and scipy.signal.resample_poly fixture; never SDK runtime timing.",
            },
            {
                "component_id": "speex-resampler",
                "task_id": "SDK-SPEEX-RESAMPLER",
                "evidence_status": "considered",
                "disposition": "sdk-reference",
                "family": "bandlimited-resampling",
                "role": "Named upstream lead only; no local resampler execution owner.",
            },
            {
                "component_id": "libsamplerate",
                "task_id": "SDK-LIBSAMPLERATE",
                "evidence_status": "considered",
                "disposition": "sdk-reference",
                "family": "bandlimited-resampling",
                "role": "Reported comparator-matrix lead; no local execution.",
            },
            {
                "component_id": "libsoxr",
                "task_id": "SDK-LIBSOXR",
                "evidence_status": "considered",
                "disposition": "sdk-reference",
                "family": "bandlimited-resampling",
                "role": "Reported comparator-matrix lead; no local execution.",
            },
        ],
        "historical_executions": [
            {
                "id": "numpy-scipy-offline-wav-resampling",
                "component_id": "numpy-scipy-soundfile-wav-and-resampling",
                "task_id": "SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING",
                "evidence_pin_key": (
                    "sdk:docs/task-evidence/numpy-scipy-soundfile-wav-resampling/report.json"
                ),
                "evidence_layer": "local_synthetic_tool_offline",
                "inputs": [
                    "11 frozen synthetic signals: impulse, 1 kHz sine, multitone, silence, noise, ramp, stereo, 3-channel, 8-frame, 1-frame and 0-frame",
                    "FLOAT WAV write/read roundtrips on caller-owned paths",
                    "36 resampling cases from 6 signals to 6 target rates (8, 16, 22.05, 32, 44.1 and 48 kHz)",
                    "2-D f32 arrays with explicit source and target rates",
                ],
                "controls": [
                    "16->16 kHz identity bit-exact with up=down=1",
                    "expected ceil(len*up/down) output frames and finite output on every case",
                    "PCM_16 read through the f32 adapter is not bit-exact (max abs error 2.8767e-05)",
                    "Git LFS pointer, empty/truncated/non-WAV files and missing path rejected",
                    "rate, channel, shape, non-finite, interval and non-positive-rate guards",
                    "blocked numpy/scipy/soundfile reported as missing_optional_selection with no fallback",
                ],
                "assets": [
                    "none: no audio corpus, model, weight or downloaded binary",
                    "installed NumPy 2.5.4, SciPy 1.18.1, SoundFile 0.14.0 and libsndfile 1.2.2 bytes pinned in the linked report",
                ],
                "local_outcomes": [
                    "11/11 FLOAT WAV roundtrips bit-exact; 36/36 resampling cases finite with expected counts",
                    "16->8 kHz 800 frames; 16->48 kHz 4800 frames; 16->44.1 kHz 4410 frames",
                    "30 unittest checks and a byte-identical regeneration were recorded by that task",
                    "Paced SDK session, deadline, device, speech-quality and listening results are absent",
                ],
                "reported_outcomes": [
                    "No upstream quality or latency result is attached to this fixture; installed-wheel provenance only",
                ],
                "limits": [
                    "Offline developer tooling is never included in SDK runtime timing",
                    "No real speech, perceptual score or public benchmark is used",
                ],
            },
            {
                "id": "typed-frame-resample-drift-model",
                "component_id": "typed-frame-resample-and-drift-diagnostics",
                "task_id": "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS",
                "evidence_pin_key": (
                    "sdk:docs/task-evidence/typed-frame-resample-and-drift-diagnostics/report.json"
                ),
                "evidence_layer": "local_synthetic_model_free_proposal",
                "inputs": [
                    "three full 48 kHz stereo s16 frames (480 interleaved source samples each) plus one partial 45-sample frame",
                    "explicit 48 kHz/2ch/s16 -> 16 kHz/1ch/f32 selection",
                    "one declared monotonic clock domain; 16 kHz sample = 62500 ns; drift bound 10000 ppm",
                ],
                "controls": [
                    "integer content delay D=173 samples measured in source coordinates",
                    "13/13 adverse controls: rate, channels, shape, nonfinite, clock map, missing selection, config, epoch, duplicate timestamp, drift, tail overrun and finite-tail accounting",
                    "gapless non-overlapping source intervals [0,147), [147,307), [307,467), [467,495)",
                    "concealment frames never satisfy conservation; post-input decay and padding are non-content",
                ],
                "assets": ["none: stdlib Python model, no model, weights, audio or download"],
                "local_outcomes": [
                    "495 accepted = 495 delivered valid samples; 800 produced = 495 valid + 173 startup + 132 tail",
                    "one drain call; 24 unittest checks recorded by that task",
                    "no native compile, installed consumer, paced workload or target-device result",
                ],
                "reported_outcomes": [
                    "Contract proposal audio-sdk/typed-frame-resample-drift/0.1 only; no external benchmark claim",
                ],
                "limits": [
                    "Delay is an integer source-coordinate impulse probe, not acoustic or phase/group delay",
                    "Explicit conversions sit outside the fixed v0 ABI and are not defaults",
                ],
            },
            {
                "id": "identity-pcm-installed-baseline",
                "component_id": "identity-pcm-and-noop-fixtures",
                "task_id": "SDK-IDENTITY-PCM-AND-NOOP-FIXTURES",
                "evidence_pin_key": "sdk:docs/task-evidence/identity-pcm-and-noop-fixtures/README.md",
                "evidence_layer": "local_installed_consumer_synthetic_control",
                "inputs": [
                    "357 caller-owned exact k/128 f32 values in 160/160/37 frames",
                    "first input sample 9007199254740993 (2**53+1)",
                    "installed fixed v0 boundary 16 kHz/mono/f32/160 with D=0",
                ],
                "controls": [
                    "8 malformed/lifecycle probes returned zero-valid AS_INVALID_ARGUMENT",
                    "unregistered provider/mode/asset selections rejected",
                    "35 pass, 0 fail, 2 skip of 37 installed checks; registry.busy and buffered.flow remain skipped",
                    "identity source and harness descriptor bytes pinned by that task",
                ],
                "assets": ["none: synthetic f32 values and task-local C fixture provider; no audio or model"],
                "local_outcomes": [
                    "11/11 native CTest and 1/1 installed consumer test passed in that task",
                    "Python fixture tests 7/7 passed; canonical report digests recorded by that task",
                    "no pacing, CPU/memory, deadline, device, real-audio or release evidence",
                ],
                "reported_outcomes": [
                    "Fixed v0 contract behavior only; no built-in identity provider is added by this survey",
                ],
                "limits": [
                    "Bit-exact identity is a control, not a resampler or a quality result",
                    "A skipped check is not promoted to a pass",
                ],
            },
            {
                "id": "playback-speed-comparator-matrix",
                "component_id": "speex-resampler",
                "task_id": "SDK-SPEEX-RESAMPLER",
                "evidence_pin_key": (
                    "workspace:cpp-library/pipeline-validation/playback-speed-candidates.md"
                ),
                "evidence_layer": "reported_comparator_matrix_only",
                "inputs": [
                    "single matrix row for libsamplerate / libsoxr / Speex resampler",
                ],
                "controls": [
                    "no frozen corpus, revision, command, digest or local run accompanies the row",
                ],
                "assets": ["none locally staged for these three resampler leads"],
                "local_outcomes": [
                    "no local execution, score, conversion-cost measurement or delay measurement",
                ],
                "reported_outcomes": [
                    "Varispeed only; reported 'Very low' latency/effort and 'Cheap fallback if pitch shift is acceptable'",
                    "Reported licences BSD-2 / LGPL-2.1 / BSD-3 are matrix labels, not local rights clearance",
                ],
                "limits": [
                    "Not a pitch-preserving time-stretch result and not an SDK boundary result",
                ],
            },
        ],
        "comparison_inputs": {
            "synthetic_signals": [
                "impulse", "1 kHz sine", "multitone", "silence", "noise", "ramp",
                "stereo and 3-channel layouts", "8/1/0-frame sequences",
                "48 kHz stereo s16 interleaved frames plus a 45-sample partial frame",
                "357 exact k/128 f32 identity values in 160/160/37 frames",
            ],
            "formats_and_rates": {
                "tooling_rates_hz": [8000, 16000, 22050, 32000, 44100, 48000],
                "tooling_channels": [1, 2, 3],
                "explicit_conversion": "48 kHz/2ch/s16 -> 16 kHz/1ch/f32",
                "sdk_v0": "16 kHz/1ch/f32/160",
            },
            "source_intervals": "[0,147), [147,307), [307,467), [467,495)",
            "real_speech_or_public_cohort": None,
        },
        "controls": {
            "identity": "16->16 kHz bit-exact and D=0 bit-exact PCM baseline",
            "invalid": "rate/channel/shape/nonfinite/interval/epoch/timestamp/drift/tail rejections retained",
            "missing": "missing optional library or selection returns explicit status, never a fallback",
            "padding_and_concealment": "startup/tail padding and concealment are non-content",
            "quantization": "PCM_16 -> f32 mismatch pinned as 2.8767e-05 max abs error",
            "skipped": ["registry.busy", "buffered.flow"],
        },
        "assets": {
            "real_audio": [],
            "models_or_weights": [],
            "images_or_binaries": [],
            "downloads": [],
            "pinned_installed_tooling": [
                "numpy 2.5.4", "scipy 1.18.1", "soundfile 0.14.0", "libsndfile 1.2.2",
            ],
            "vendored_source": [
                "third_party/speexdsp/libspeexdsp/resample.c (source only; BSD-3-Clause-style notice)",
            ],
        },
        "local_vs_reported": [
            {
                "topic": "SciPy polyphase resampling",
                "local": "36 synthetic cases with finite outputs and expected counts",
                "reported": "no upstream quality or rate-conversion claim",
                "separation": "local offline tool result only",
            },
            {
                "topic": "SpeexDSP resampler / S42",
                "local": "vendored source compiled into a private object; no executable comparison",
                "reported": "comparator matrix calls it a cheap varispeed fallback",
                "separation": "reported label is not a local result",
            },
            {
                "topic": "framing/channel mapping",
                "local": "stdlib Python explicit-conversion model; installed D=0 identity control",
                "reported": "no public-benchmark or device result",
                "separation": "model and installed control answer different questions",
            },
        ],
        "release_boundary": {
            "fixed_v0_unchanged": True,
            "no_default_abi_build_or_ci_change": True,
            "no_provider_enablement_or_registry_default": True,
            "no_public_benchmark_quality_device_listening_or_release_claim": True,
            "quality_and_publication_decision_owner": "audio-bench",
            "rights_and_asset_decisions": "separate from this survey; no rights are inferred from a pin",
            "reopen_conditions": [
                "exact candidate source revision and digest",
                "frozen rate/channel/format comparison inputs and controls",
                "independent local executable evidence at the named boundary",
                "measured conversion cost, content delay and adverse cases",
                "separate rights, workload and release decisions",
            ],
        },
        "missing_evidence": [
            {
                "family": "framing-channel-mapping",
                "reason": "source-local proposal and installed identity control only; no native conversion path, paced workload or device evidence",
            },
            {
                "family": "bandlimited-resampling",
                "reason": "offline SciPy fixture and considered upstream leads only; no pinned S42 executable, anti-alias/transient control or boundary cost/delay measurement",
            },
            {
                "family": "no-ml-requirement",
                "reason": "not applicable; no ML family or model evidence is catalogued",
            },
        ],
        "gap_followup": {
            "id": "SDK-ENG-01-SPEEXDSP-RESAMPLER-FEASIBILITY",
            "status": "proposed_unassigned_not_a_board_entry",
            "parent_task": TASK_ID,
            "dependencies_to_consult": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
            "components_to_consult": [
                "speex-resampler", "speexdsp-ns-reference",
                "numpy-scipy-soundfile-wav-and-resampling",
                "typed-frame-resample-and-drift-diagnostics",
            ],
            "gap": (
                "No component owns an executable, pinned S42/SpeexDSP bandlimited-resampler "
                "comparison at a named SDK boundary."
            ),
            "smallest_check_not_run": [
                "Pin the existing vendored resample.c digest and declare its upstream revision",
                "Use authored finite synthetic f32 literals only; no speech corpus or download",
                "Compare explicit integer rate pairs 48->16 kHz and 16->48 kHz with identity at 16->16 kHz",
                "Record exact output frame counts, nonfinite failures, source-coordinate delay and adverse malformed-rate inputs",
                "Keep an offline SciPy polyphase result as a separate control, not a SpeexDSP score",
            ],
            "deliverable": "task-local replay and metadata report only; no implementation, provider, default, ABI, build or CI change",
            "stop_condition": "feasibility only; stop before any quality, device, listening, benchmark or release claim",
        },
        "non_claims": [
            "No public benchmark, corpus score, ranking or quality result",
            "No real audio, image, model, weight or other asset",
            "No device, microphone, playback, listening or human-panel result",
            "No provider enablement, registration, descriptor default or routing change",
            "No public header, ABI, build flag, CMake, package or CI change",
            "No release, publication or rights-clearance decision",
        ],
        "source_pin_verification": {
            "count": len(pins),
            "all_recomputed": True,
            "board": board_projection(),
        },
        "source_pins": pins,
        "reproduction": {
            "python": "3.12.16",
            "python_environment": "PYTHONDONTWRITEBYTECODE=1",
            "generator": "PYTHONDONTWRITEBYTECODE=1 <pinned-python> build_report.py",
            "tests": "PYTHONDONTWRITEBYTECODE=1 <pinned-python> -m unittest -v test_survey_map.py",
            "verifier": "PYTHONDONTWRITEBYTECODE=1 <pinned-python> verify.py",
            "board_check": "python3 audio-benchmark-platform/plan/swarm/check.py --task SDK-SURVEY-ENG-01",
            "installed_package_ci": (
                "regression only, not ENG-01 evidence: scripts/ci.py is unchanged and a "
                "pinned-Python run with --output in a private temp directory passed 52 "
                "repository unit tests, 1 API CTest, 11 native CTest, 14 external-provider "
                "CTest, one fixture-registration CTest in each build mode, 5 installed-wheel "
                "Python tests and the packaging/gate probes; it exercises no bandlimited "
                "resampler and does not qualify a device, listening or release result"
            ),
            "licensing": "python3 -m reuse lint (from the SDK worktree root)",
            "whitespace": "git diff --check",
        },
    }


def local_artifact_paths() -> list[Path]:
    return sorted(
        (
            path for path in HERE.iterdir()
            if path.is_file()
            and path.name not in {"SOURCES.sha256"}
            and "__pycache__" not in path.name
        ),
        key=lambda path: path.name,
    )


def build_manifest() -> str:
    lines: list[tuple[str, str]] = []
    for key, _root, _relative, _use in PIN_SPECS:
        lines.append((key, sha256_file(pin_path(key))))
    for path in local_artifact_paths():
        lines.append((f"local:{path.name}", sha256_file(path)))
    lines.sort(key=lambda row: row[0])
    return "".join(f"{digest}  {label}\n" for label, digest in lines)


def main() -> None:
    report_text = canonical_json(build_report())
    report_bytes = report_text.encode("utf-8")
    (HERE / "report.json").write_bytes(report_bytes)
    report_digest = sha256_bytes(report_bytes)
    (HERE / "report.json.sha256").write_text(
        f"{report_digest}  report.json\n", encoding="utf-8"
    )
    (HERE / "SOURCES.sha256").write_text(build_manifest(), encoding="utf-8")
    print(f"report.json  {report_digest}")
    print(f"pins  {len(PIN_SPECS)}")


if __name__ == "__main__":
    main()

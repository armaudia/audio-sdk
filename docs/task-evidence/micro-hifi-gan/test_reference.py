# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only tests for the Micro-HiFi-GAN evidence package.

No network, no downloads, no weights, no skips.  Every check runs against the
synthetic feature-frame boundary model only; nothing here qualifies the
candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run as cli  # noqa: E402

SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SIDECAR = f"{SPDX_C}\n{SPDX_L}\n"
SIDECAR_FILES = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
EXPECTED_GATES = {
    "exact_asset_identity",
    "runtime_admission",
    "artifact_rights",
    "exact_reference_parity",
    "rights_cleared_voice_cohort",
    "independent_scoring_and_listening",
    "target_runtime_timing",
    "provider_intake_and_default_selection",
}
EXPECTED_CONFIG = {
    "wrong_model_id": "model_id_mismatch",
    "wrong_sample_rate": "sample_rate_hz_mismatch",
    "wrong_channels": "channels_mismatch",
    "wrong_sample_format": "sample_format_mismatch",
    "wrong_feature_bins": "feature_bins_mismatch",
    "wrong_feature_hop": "feature_hop_mismatch",
    "wrong_lookahead": "lookahead_frames_mismatch",
    "wrong_buffering_delay": "buffering_delay_mismatch",
    "wrong_state_layout": "state_layout_mismatch",
    "wrong_target_condition": "target_condition_mismatch",
    "wrong_consent_scope": "consent_scope_mismatch",
    "caller_asset_unavailable": "asset_not_admitted",
    "surrogate_without_opt_in": "surrogate_opt_in_required",
    "wrong_asset_identity": "asset_identity_mismatch",
    "wrong_asset_bytes": "asset_identity_mismatch",
}
EXPECTED_STREAMS = {
    "empty_stream": "rejected:stream_empty",
    "oversized_stream": "rejected:stream_oversized",
    "wrong_frame_shape": "rejected:frame_shape_invalid",
    "nonfinite_frame": "rejected:feature_nonfinite",
    "infinite_frame": "rejected:feature_nonfinite",
    "string_stream": "rejected:stream_type_invalid",
    "boolean_feature": "rejected:feature_type_invalid",
    "negative_feature": "rejected:feature_out_of_range",
    "out_of_range_feature": "rejected:feature_out_of_range",
    "second_stream": "rejected:stream_already_complete",
    "after_close": "rejected:session_closed",
}
EXPECTED_FRAMES = {
    "wrong_frame_length": "rejected:frame_shape_invalid",
    "wrong_frame_type": "rejected:frame_type_invalid",
    "nonfinite_frame": "rejected:feature_nonfinite",
    "out_of_range_frame": "rejected:feature_out_of_range",
    "wrong_state_set": "rejected:state_layout_mismatch",
    "wrong_state_shape": "rejected:state_layout_mismatch",
    "nonfinite_state": "rejected:state_nonfinite",
    "boolean_state": "rejected:state_type_invalid",
}


def _no_duplicates(pairs):
    seen = set()
    for key, _value in pairs:
        if key in seen:
            raise ValueError("duplicate key: " + key)
        seen.add(key)
    return dict(pairs)


def load_strict(name: str):
    return json.loads(
        (HERE / name).read_text(encoding="ascii"),
        object_pairs_hook=_no_duplicates,
    )


def report() -> dict:
    return reference.build_report()


class TestCanonicalJson(unittest.TestCase):
    def test_canonical_bytes_sorted_compact(self):
        value = {"b": 1, "a": [2, 3]}
        self.assertEqual(reference.canonical_bytes(value), b'{"a":[2,3],"b":1}')

    def test_negative_zero_normalized(self):
        self.assertEqual(reference.canonical_bytes({"x": -0.0}), b'{"x":0.0}')

    def test_nonfinite_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                reference.canonical_bytes({"x": bad})

    def test_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dup.json"
            path.write_text('{"a":1,"a":2}\n', encoding="ascii")
            with self.assertRaises(ValueError):
                json.loads(
                    path.read_text(encoding="ascii"),
                    object_pairs_hook=_no_duplicates,
                )

    def test_report_bytes_end_with_single_newline(self):
        payload = reference.canonical_report_bytes(report())
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))
        payload.decode("ascii")


class TestTaskIdentity(unittest.TestCase):
    def test_stable_digest_is_stable_and_excludes_mutable_fields(self):
        identity = reference.task_identity()
        self.assertEqual(identity["stable_sha256"], reference.stable_identity_digest())
        for key in ("status", "owner", "claim", "review", "handoff", "blocked_reason"):
            self.assertNotIn(key, identity)
        self.assertFalse(identity["board_full_file_hashed"])
        self.assertEqual(identity["id"], reference.TASK)
        self.assertEqual(identity["component"], reference.SLUG)
        self.assertEqual(identity["mode"], "feasibility")
        self.assertEqual(
            identity["depends_on"],
            ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
        )
        self.assertEqual(
            identity["evidence"], ["research/accent-conversion-20261101/README.md"]
        )

    def test_stable_digest_ignores_reordered_input(self):
        reordered = dict(reversed(list(reference.STABLE_TASK_IDENTITY.items())))
        self.assertEqual(
            reference.stable_identity_digest(reordered),
            reference.stable_identity_digest(),
        )

    def test_mutable_board_file_is_not_pinned(self):
        text = (
            "\n".join(reference.SOURCE_PINS)
            + "\n"
            + "\n".join(reference.BOUNDARY_PINS)
            + "\n"
            + "\n".join(reference.SIBLING_PINS)
        )
        self.assertNotIn("plan/swarm/TASKS.json", text)
        self.assertFalse(report()["pins"]["board_file_pinned"])
        self.assertFalse(report()["pins"]["board_full_file_hashed"])

    def test_live_board_stable_projection_matches(self):
        path = (
            reference.SOURCE_ROOT
            / "audio-benchmark-platform/plan/swarm/TASKS.json"
        )
        self.assertTrue(path.is_file())
        board = load_strict_from(path)
        rows = [row for row in board["tasks"] if row.get("id") == reference.TASK]
        self.assertEqual(len(rows), 1)
        projected = reference.project_board_row(rows[0])
        for field in reference.PROJECTED_BOARD_FIELDS:
            self.assertEqual(
                projected[field], reference.STABLE_TASK_IDENTITY[field], field
            )
        payload = report()
        self.assertEqual(
            payload["board_row"]["stable_sha256"],
            reference.stable_row_digest(payload["board_row"]["stable_fields"]),
        )

    def test_project_board_row_rejects_missing_fields(self):
        with self.assertRaises(ValueError):
            reference.project_board_row({"id": reference.TASK})


def load_strict_from(path: Path):
    text = path.read_text(encoding="utf-8")
    value = json.loads(text, object_pairs_hook=_no_duplicates)
    if not isinstance(value, dict):
        raise ValueError("board is not an object")
    return value


class TestAssetBoundary(unittest.TestCase):
    def test_exact_candidate_identity_is_unpinned(self):
        ref = reference.asset_ref()
        self.assertEqual(ref["asset_id"], reference.ASSET_ID)
        self.assertIsNone(ref["byte_count"])
        self.assertIsNone(ref["sha256"])
        self.assertFalse(ref["pinned"])
        self.assertFalse(ref["ledger_entry_present"])
        self.assertFalse(ref["rights_entry_present"])
        self.assertIsNone(ref["source_repository"])
        self.assertIsNone(ref["source_revision"])
        self.assertIsNone(ref["runtime_package"])
        self.assertIsNone(ref["runtime_wheel_sha256"])
        self.assertEqual(ref["storage"], "external")

    def test_candidate_admission_blocked(self):
        admission = reference.asset_admission()
        self.assertEqual(admission["status"], "blocked")
        self.assertEqual(
            admission["reason_codes"],
            [
                "source_and_identity_unpinned",
                "weights_not_supplied",
                "runtime_unpinned",
                "license_terms_unresolved",
                "consent_not_recorded",
                "voice_task_fit_vocoder_only_no_checkpoint",
                "redistribution_rights_unknown",
            ],
        )
        self.assertEqual(admission["qualification_effect"], "none")
        self.assertFalse(admission["asset_bytes_read"])
        self.assertFalse(admission["download_attempted"])
        self.assertFalse(admission["vocoder_invoked"])

    def test_candidate_bytes_absent_from_sdk_worktree(self):
        self.assertFalse(
            reference.asset_ref()["bytes_present_in_sdk_worktree"]
        )
        self.assertFalse(
            (reference.SDK_ROOT / reference.ASSET_LEDGER_PATH).exists()
        )

    def test_all_exact_source_and_asset_probes_are_absent(self):
        ref = reference.asset_ref()
        self.assertEqual(len(ref["workspace_probes"]), len(reference.FIXED_ASSET_PROBES))
        self.assertFalse(any(ref["workspace_probes"].values()))
        audit = reference.absence_audit()
        self.assertTrue(audit["all_absence_probes_absent"])
        self.assertEqual(
            audit["probe_count"],
            len(reference.FIXED_ASSET_PROBES) + len(reference.HOME_ASSET_PROBES),
        )

    def test_home_cache_probes_absent(self):
        self.assertFalse(any(reference.asset_ref()["home_probes"].values()))

    def test_no_workspace_copies_are_admitted(self):
        self.assertEqual(reference.workspace_copies(), [])
        self.assertEqual(report()["workspace_observations"]["admitted_copy_count"], 0)

    def test_synthetic_admission_control_is_not_candidate(self):
        control = reference.synthetic_admission_control()
        self.assertEqual(control["status"], "admitted_synthetic_control")
        self.assertFalse(control["candidate_asset"])
        self.assertEqual(control["qualification_effect"], "none")
        self.assertFalse(control["asset_bytes_read"])
        self.assertFalse(control["vocoder_invoked"])

    def test_synthetic_asset_is_derived_not_model_bytes(self):
        ref = reference.synthetic_asset_ref()
        self.assertEqual(ref["sha256"], hashlib.sha256(reference.SYNTHETIC_ASSET_BYTES).hexdigest())
        self.assertFalse(ref["candidate_asset"])
        self.assertIn(b"synthetic-boundary-control", reference.SYNTHETIC_ASSET_BYTES)

    def test_rights_and_consent_are_unresolved(self):
        rights = reference.rights_status()
        self.assertFalse(rights["entry_present"])
        for scope in (
            "acquisition",
            "evaluation",
            "redistribution",
            "customer_deployment",
            "public_playback",
        ):
            self.assertEqual(rights[scope], "unknown")
        self.assertEqual(rights["consent"], "not_recorded")
        self.assertEqual(rights["speaker_reference_permission"], "unknown")
        self.assertEqual(rights["output_use"], "unknown")
        self.assertFalse(rights["evaluation_only"])
        self.assertFalse(rights["packaging_permitted"])


class TestReferenceInterface(unittest.TestCase):
    def test_no_candidate_geometry_is_fabricated(self):
        interface = reference.reference_interface()
        self.assertFalse(interface["candidate_geometry_known"])
        for key in (
            "candidate_sample_rate_hz",
            "candidate_feature_bins",
            "candidate_hop_samples",
            "candidate_window",
            "candidate_feature_contract",
            "candidate_upsample_layout",
            "candidate_lookahead_frames",
            "candidate_pruning_schedule",
            "candidate_state_layout",
        ):
            self.assertIsNone(interface[key], key)
        self.assertFalse(interface["model_bytes_read"])

    def test_surrogate_fixture_is_explicit(self):
        fixture = reference.reference_interface()["surrogate_fixture"]
        self.assertEqual(fixture["feature_bins"], reference.FEATURE_BINS)
        self.assertEqual(
            fixture["feature_hop_samples"], reference.FEATURE_HOP_SAMPLES
        )
        self.assertEqual(
            fixture["lookahead_frames"], reference.SURROGATE_LOOKAHEAD_FRAMES
        )
        self.assertEqual(
            fixture["buffering_delay_samples"], reference.BUFFERING_DELAY_SAMPLES
        )

    def test_no_native_fixture_supplies_parity(self):
        native = reference.native_evidence_status()
        self.assertFalse(native["candidate_native_reference_present"])
        self.assertEqual(native["model_parity"], "not_available")
        self.assertEqual(native["model_quality"], "not_assessed")
        self.assertFalse(native["used_for_qualification"])


class TestConfigRejections(unittest.TestCase):
    def test_matrix_exact_statuses(self):
        cases = reference.config_rejection_matrix()
        for name, reason in EXPECTED_CONFIG.items():
            self.assertEqual(cases[name]["status"], "rejected", name)
            self.assertIn(reason, cases[name]["reason_codes"], name)
            self.assertFalse(cases[name]["processing_attempted"], name)
        self.assertEqual(
            cases["synthetic_admission_control"]["status"],
            "admitted_synthetic_control",
        )
        self.assertFalse(
            cases["synthetic_admission_control"]["candidate_asset"]
        )

    def test_unknown_key_rejected(self):
        config = reference.default_config()
        config["extra"] = 1
        result = reference.admit_config(config)
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason_codes"], ["config_keys_mismatch"])

    def test_non_dict_config_rejected(self):
        self.assertEqual(
            reference.admit_config(["not", "a", "config"])["reason_codes"],
            ["config_type_invalid"],
        )

    def test_candidate_config_never_creates(self):
        config = reference.default_config()
        result = reference.admit_config(config)
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason_codes"], ["asset_not_admitted"])
        self.assertFalse(result["processing_attempted"])
        session = reference.StreamingSession(config)
        self.assertFalse(session.created)
        self.assertTrue(
            session.process_frames([[0.0] * reference.FEATURE_BINS])["status"].startswith(
                "rejected:not_admitted"
            )
        )

    def test_synthetic_requires_opt_in(self):
        config = reference.synthetic_config()
        config["surrogate_opt_in"] = False
        self.assertEqual(
            reference.admit_config(config)["reason_codes"],
            ["surrogate_opt_in_required"],
        )
        config = reference.synthetic_config()
        config["asset_sha256"] = "0" * 64
        self.assertEqual(
            reference.admit_config(config)["reason_codes"],
            ["synthetic_asset_mismatch"],
        )


class TestStreamRejections(unittest.TestCase):
    def test_matrix_exact_statuses_and_state_unchanged(self):
        cases = reference.stream_rejection_matrix()
        for name, status in EXPECTED_STREAMS.items():
            self.assertEqual(cases[name]["status"], status, name)
            self.assertTrue(cases[name]["state_unchanged"], name)
            self.assertEqual(cases[name]["output_samples"], 0, name)

    def test_boundary_lengths(self):
        session = reference.StreamingSession(reference.synthetic_config())
        one = session.process_frames([[0.01] * reference.FEATURE_BINS])
        self.assertEqual(one["status"], "ok_synthetic")
        self.assertEqual(one["output_samples"], reference.FEATURE_HOP_SAMPLES)

    def test_feature_range_boundary(self):
        session = reference.StreamingSession(reference.synthetic_config())
        accepted = session.process_frames(
            [[reference.MAX_ABS_FEATURE] * reference.FEATURE_BINS]
        )
        self.assertEqual(accepted["status"], "ok_synthetic")
        session = reference.StreamingSession(reference.synthetic_config())
        rejected = session.process_frames(
            [[reference.MAX_ABS_FEATURE + 1e-9] * reference.FEATURE_BINS]
        )
        self.assertEqual(rejected["status"], "rejected:feature_out_of_range")

    def test_rejection_after_success_does_not_advance(self):
        session = reference.StreamingSession(reference.synthetic_config())
        first = session.process_frames([[0.01] * reference.FEATURE_BINS])
        self.assertEqual(first["status"], "ok_synthetic")
        before = session.state_digest()
        rejected = session.process_frames([[0.01] * reference.FEATURE_BINS])
        self.assertEqual(rejected["status"], "rejected:stream_already_complete")
        self.assertEqual(session.state_digest(), before)


class TestFrameRejections(unittest.TestCase):
    def test_matrix_exact_statuses(self):
        cases = reference.frame_rejection_matrix()
        for name, status in EXPECTED_FRAMES.items():
            self.assertEqual(cases[name]["status"], status, name)
            self.assertTrue(cases[name]["state_unchanged"], name)
            self.assertTrue(cases[name]["state_payload_unchanged"], name)
            self.assertEqual(cases[name]["output_samples"], 0, name)

    def test_frame_api_step_and_state_shapes(self):
        session = reference.StreamingSession(reference.synthetic_config())
        first = session.process_frame([0.01] * reference.FEATURE_BINS)
        self.assertEqual(first["status"], "ok_synthetic")
        self.assertEqual(first["output_samples"], reference.FEATURE_HOP_SAMPLES)
        self.assertEqual(
            session.state_view()["state_sha256"],
            reference.sha256(reference.canonical_bytes(session.state)),
        )
        self.assertEqual(
            reference._shape_of(session.state["feature_delay"]),
            reference.STATE_LAYOUT[0],
        )


class TestSyntheticSurrogate(unittest.TestCase):
    def test_deterministic_outputs(self):
        for condition in reference.CONDITIONS:
            target, observed, frames = reference.synth(condition)
            first = reference.surrogate_stream(frames)
            second = reference.surrogate_stream(frames)
            self.assertEqual(reference.output_digest(first), reference.output_digest(second))
            self.assertEqual(len(first), len(observed))
            self.assertEqual(len(target), len(observed))

    def test_chunk_loop_matches_stream(self):
        _target, _observed, frames = reference.synth("active_speech")
        self.assertEqual(
            reference.output_digest(reference.surrogate_stream(frames)),
            reference.output_digest(reference.surrogate_chunk_loop_control(frames)),
        )

    def test_split_halves_not_equivalent(self):
        _target, _observed, frames = reference.synth("active_speech")
        whole = reference.surrogate_stream(frames)
        split = reference.surrogate_split_halves(frames)
        self.assertNotEqual(
            reference.output_digest(whole), reference.output_digest(split)
        )

    def test_prefix_is_stable(self):
        _target, _observed, frames = reference.synth("active_speech")
        whole = reference.surrogate_stream(frames)
        prefix_frames = 96
        prefix = reference.surrogate_stream(frames[:prefix_frames])
        self.assertEqual(
            prefix, whole[: prefix_frames * reference.FEATURE_HOP_SAMPLES]
        )

    def test_partial_tail_length(self):
        _target, _observed, frames = reference.synth("active_speech")
        output = reference.surrogate_stream(frames[:7])
        self.assertEqual(
            len(output), 7 * reference.FEATURE_HOP_SAMPLES
        )

    def test_drain_bounds(self):
        self.assertLessEqual(
            reference.DRAIN_FLUSH_FRAMES, reference.MAX_DRAIN_CALLS
        )
        self.assertLessEqual(
            reference.DRAIN_FLUSH_FRAMES * reference.FEATURE_HOP_SAMPLES,
            reference.MAX_DRAIN_PRODUCED_SAMPLES,
        )
        semantics = reference.streaming_semantics()
        self.assertTrue(semantics["drain_within_bounds"])

    def test_impulse_delay_preserved(self):
        semantics = reference.streaming_semantics()
        self.assertTrue(semantics["impulse_delay_preserved"])
        self.assertEqual(
            semantics["impulse_output_first_nonzero_sample"],
            semantics["impulse_expected_first_nonzero_sample"],
        )

    def test_startup_is_declared_padding(self):
        _target, _observed, frames = reference.synth("active_speech")
        session = reference.StreamingSession(reference.synthetic_config())
        first = session.process_frame(frames[0])
        second = session.process_frame(frames[1])
        third = session.process_frame(frames[2])
        self.assertEqual(first["output"], [0.0] * reference.FEATURE_HOP_SAMPLES)
        self.assertEqual(second["output"], [0.0] * reference.FEATURE_HOP_SAMPLES)
        self.assertTrue(any(value != 0.0 for value in third["output"]))

    def test_outputs_finite_and_peak_bounded(self):
        for condition in reference.CONDITIONS:
            _target, _observed, frames = reference.synth(condition)
            output = reference.surrogate_stream(frames)
            self.assertTrue(all(math.isfinite(value) for value in output))
            self.assertLessEqual(max(abs(value) for value in output), 1.0)

    def test_identity_is_exact_passthrough(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            self.assertTrue(results[condition]["identity_exact"], condition)
            self.assertTrue(results[condition]["chunk_loop_matches_stream"], condition)
            if condition != "silence":
                self.assertTrue(results[condition]["split_halves_differs"], condition)

    def test_silence_has_no_target_metrics(self):
        results = reference.synthetic_results()
        self.assertTrue(results["silence"]["target_all_zero"])
        self.assertIsNone(results["silence"]["surrogate_stream"]["surrogate_snr_db"])

    def test_metrics_are_finite_or_none(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            for variant in (
                "identity_passthrough",
                "noisy_control",
                "surrogate_stream",
                "surrogate_chunk_loop_control",
                "surrogate_split_halves",
            ):
                metrics = results[condition][variant]
                for key, value in metrics.items():
                    if isinstance(value, float):
                        self.assertTrue(math.isfinite(value), (condition, variant, key))


class TestSessionLifecycle(unittest.TestCase):
    def test_one_stream_close_and_replay(self):
        _target, _observed, frames = reference.synth("active_speech")
        session = reference.StreamingSession(reference.synthetic_config())
        first = session.process_frames(frames)
        self.assertEqual(first["status"], "ok_synthetic")
        second = session.process_frames(frames)
        self.assertEqual(second["status"], "rejected:stream_already_complete")
        reset = session.reset()
        self.assertEqual(reset["status"], "ok_reset")
        replay = session.process_frames(frames)
        self.assertEqual(replay["status"], "ok_synthetic")
        self.assertEqual(first["output"], replay["output"])
        session.close()
        self.assertTrue(session.closed)
        self.assertEqual(
            session.process_frames(frames)["status"], "rejected:session_closed"
        )

    def test_reset_replay_identical_and_state_zeroed(self):
        semantics = reference.streaming_semantics()
        self.assertTrue(semantics["replay_bit_identical"])
        self.assertTrue(semantics["reset_state_zeroed"])
        self.assertEqual(semantics["reset_epoch"], 1)

    def test_state_digest_deterministic(self):
        session = reference.StreamingSession(reference.synthetic_config())
        self.assertEqual(session.state_digest(), session.state_digest())
        session.process_frame([0.01] * reference.FEATURE_BINS)
        self.assertEqual(session.state_digest(), session.state_digest())


class TestFeasibility(unittest.TestCase):
    def test_pinned_negative_run_record(self):
        decision = reference.feasibility_decision()
        self.assertEqual(decision["inventory_record"], "micro-hifi-gan")
        self.assertEqual(decision["research_line"], 169)
        self.assertEqual(decision["research_status"], "Not run")
        self.assertIn("No compatible checkpoint acquired", decision["finding"])
        self.assertFalse(decision["source_revision_pin_available"])
        self.assertFalse(decision["weights_available"])
        self.assertFalse(decision["runtime_available"])
        self.assertFalse(decision["matched_evidence_present"])
        self.assertEqual(decision["proceed_defer"], "DEFER")

    def test_voice_task_fit_is_vocoder_component_only(self):
        self.assertEqual(
            reference.voice_profile(reference.synthetic_results())["task_fit"],
            "vocoder_component_only_no_checkpoint",
        )
        self.assertIn("cannot perform an accent conversion", reference.RESEARCH_TASK_FIT)


class TestReportDisposition(unittest.TestCase):
    def test_machine_readable_disposition(self):
        payload = report()
        self.assertEqual(payload["decision"], "DEFER")
        self.assertEqual(payload["status"], "proposal_only_incomplete")
        self.assertEqual(payload["evidence_status"], "incomplete")
        self.assertEqual(payload["qualification"]["status"], "not_qualified")
        self.assertFalse(payload["qualification"]["qualified"])
        self.assertFalse(payload["qualification"]["candidate_qualified"])
        self.assertFalse(payload["qualification"]["missing_result_may_qualify"])

    def test_exactly_eight_blocked_gates(self):
        payload = report()
        self.assertEqual(payload["release_gate_count"], 8)
        self.assertEqual(len(payload["release_gates"]), 8)
        self.assertEqual(
            {gate["name"] for gate in payload["release_gates"]}, EXPECTED_GATES
        )
        for gate in payload["release_gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["evidence"])
            self.assertTrue(gate["reopen"])

    def test_no_claim_is_true(self):
        for key, value in report()["claims"].items():
            self.assertIs(value, False, key)

    def test_boundary_preserved(self):
        boundary = report()["boundary"]
        for key, value in boundary.items():
            if key == "installed_v0_geometry_preserved":
                self.assertIs(value, True, key)
            else:
                self.assertIs(value, False, key)

    def test_voice_profile_unmeasured_fields(self):
        voice = report()["voice_profile"]
        self.assertEqual(voice["profile"], "voice")
        self.assertFalse(voice["candidate_result_present"])
        self.assertTrue(voice["synthetic_only"])
        self.assertEqual(voice["consent"], "not_recorded")
        self.assertEqual(voice["permitted_reference_input"], "absent")
        for key in (
            "semantic_preservation",
            "speaker_identity_similarity",
            "naturalness",
            "first_output_tail_timing",
        ):
            self.assertEqual(voice[key], "blocked_unmeasured")
        self.assertEqual(voice["listening"], "not_run")
        self.assertEqual(voice["output_use"], "blocked")
        self.assertFalse(voice["real_runtime"])

    def test_report_has_no_self_digest(self):
        text = (HERE / "report.json").read_text(encoding="ascii")
        payload = json.loads(text)
        self.assertNotIn("report_sha256", payload)
        self.assertNotIn("self_sha256", payload)


class TestRegeneration(unittest.TestCase):
    def test_report_sha256_sidecar_and_contract_pins(self):
        payload = (HERE / "report.json").read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            f"{digest}  report.json\n",
        )
        contract = load_strict("contract.json")
        self.assertEqual(contract["artifact_pins"], cli.contract_pins())
        self.assertNotIn("contract.json", contract["artifact_pins"])
        self.assertIn("README.md", contract["artifact_pins"])

    def test_manifest_pins_and_no_board_hash(self):
        text = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        pin_lines = [
            line for line in text.splitlines() if line and not line.startswith("#")
        ]
        for line in pin_lines:
            self.assertNotIn("plan/swarm/TASKS.json", line)
        self.assertIn("worktree:docs/task-evidence/micro-hifi-gan/reference.py", text)
        self.assertIn("source:research/accent-conversion-20261101/README.md", text)
        self.assertIn(
            "worktree:docs/task-evidence/hifi-gan-vocoder/README.md", text
        )
        self.assertEqual(cli.manifest_bytes(), (HERE / "SOURCES.sha256").read_bytes())

    def test_readme_digest_table_matches(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        block = text.split("<!-- DIGEST_TABLE_START -->", 1)[1].split(
            "<!-- DIGEST_TABLE_END -->", 1
        )[0]
        for name in cli.TABLE_FILES:
            payload = (HERE / name).read_bytes()
            row = f"| `{name}` | `{hashlib.sha256(payload).hexdigest()}` | {len(payload)} |"
            self.assertIn(row, block, name)

    def test_three_cold_start_regenerations_byte_identical(self):
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        digests = []
        for _ in range(3):
            result = subprocess.run(
                [sys.executable, str(HERE / "run.py"), "--digest"],
                cwd=str(HERE),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            digests.append(result.stdout.strip())
        self.assertEqual(len(set(digests)), 1)
        self.assertEqual(
            digests[0],
            (HERE / "report.json.sha256").read_text(encoding="ascii").split()[0],
        )


class TestLicensingAndScope(unittest.TestCase):
    def test_python_spdx_headers(self):
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            head = (HERE / name).read_text(encoding="utf-8").splitlines()[:2]
            self.assertEqual(head, ["# " + SPDX_C, "# " + SPDX_L], name)

    def test_markdown_spdx_header(self):
        head = (HERE / "README.md").read_text(encoding="utf-8").splitlines()[:2]
        self.assertEqual(head, ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"])

    def test_sidecars(self):
        for name in SIDECAR_FILES:
            self.assertEqual(
                (HERE / name).read_text(encoding="utf-8"), SIDECAR, name
            )

    def test_fail_closed_local_set(self):
        present = {
            path.relative_to(HERE).as_posix()
            for path in HERE.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        self.assertEqual(present, set(reference.LOCAL_FILES) | {"SOURCES.sha256"})

    def test_no_network_or_download_imports(self):
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            text = (HERE / name).read_text(encoding="utf-8")
            for token in (
                "import " + "requests",
                "import " + "urllib",
                "import " + "socket",
                "url" + "open",
                "url" + "retrieve",
                "pip " + "install",
            ):
                self.assertNotIn(token, text, name)

    def test_no_asset_path_access_in_reference(self):
        text = (HERE / "reference.py").read_text(encoding="utf-8")
        for token in ("data/models/micro-hifi-gan/generator.pt",):
            self.assertNotIn('open("' + token, text)
        self.assertNotIn("Path.open(", text)
        self.assertNotIn("read_text(", text)


if __name__ == "__main__":
    unittest.main()

# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only tests for the HiFi-GAN evidence package.

No network, no downloads, no weights, no skips.  Every check runs against the
synthetic boundary model only; nothing here qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
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
    "wrong_native_hop": "native_hop_mismatch",
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
    "nonfinite_sample": "rejected:sample_nonfinite",
    "infinite_sample": "rejected:sample_nonfinite",
    "string_stream": "rejected:stream_type_invalid",
    "boolean_sample": "rejected:sample_type_invalid",
    "out_of_range_sample": "rejected:sample_out_of_range",
    "second_stream": "rejected:stream_already_complete",
    "after_close": "rejected:session_closed",
}
EXPECTED_CHUNKS = {
    "wrong_chunk_length": "rejected:chunk_shape_invalid",
    "wrong_chunk_type": "rejected:chunk_type_invalid",
    "nonfinite_chunk": "rejected:sample_nonfinite",
    "out_of_range_chunk": "rejected:sample_out_of_range",
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
    return json.loads((HERE / name).read_text(encoding="ascii"), object_pairs_hook=_no_duplicates)


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
                json.loads(path.read_text(encoding="ascii"), object_pairs_hook=_no_duplicates)

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
        self.assertEqual(identity["mode"], "research-control")
        self.assertEqual(identity["depends_on"], ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"])

    def test_stable_digest_ignores_reordered_input(self):
        reordered = dict(reversed(list(reference.STABLE_TASK_IDENTITY.items())))
        self.assertEqual(
            reference.stable_identity_digest(reordered),
            reference.stable_identity_digest(),
        )

    def test_mutable_board_file_is_not_pinned(self):
        text = "\n".join(reference.SOURCE_PINS) + "\n" + "\n".join(reference.BOUNDARY_PINS)
        self.assertNotIn("plan/swarm/TASKS.json", text)
        self.assertFalse(report()["pins"]["board_file_pinned"])


class TestAssetBoundary(unittest.TestCase):
    def test_exact_candidate_identity_is_unpinned(self):
        ref = reference.asset_ref()
        self.assertEqual(ref["asset_id"], reference.ASSET_ID)
        self.assertIsNone(ref["byte_count"])
        self.assertIsNone(ref["sha256"])
        self.assertFalse(ref["pinned"])
        self.assertFalse(ref["ledger_entry_present"])
        self.assertFalse(ref["rights_entry_present"])
        self.assertEqual(ref["storage"], "external")
        self.assertIsNone(ref["source_repository"])
        self.assertIsNone(ref["source_revision"])
        self.assertEqual(ref["candidate_release_tags"], [])
        self.assertIsNone(ref["runtime_package"])
        self.assertIsNone(ref["runtime_wheel_sha256"])
        self.assertFalse(ref["runtime_available"])
        self.assertFalse(ref["evaluation_allowed"])
        self.assertFalse(ref["redistribution_cleared"])
        self.assertFalse(ref["asset_bytes_read"])
        self.assertFalse(ref["digest_recomputed"])

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
                "voice_task_fit_out_of_scope",
                "redistribution_rights_unknown",
            ],
        )
        self.assertFalse(admission["download_attempted"])
        self.assertFalse(admission["model_runtime_invoked"])
        self.assertFalse(admission["vocoder_invoked"])
        self.assertEqual(admission["qualification_effect"], "none")

    def test_candidate_bytes_absent_from_sdk_worktree(self):
        self.assertFalse((reference.SDK_ROOT / reference.ASSET_LEDGER_PATH).is_file())
        self.assertFalse(reference.asset_ref()["bytes_present_in_sdk_worktree"])

    def test_all_exact_source_and_asset_probes_are_absent(self):
        probes = reference.asset_ref()["workspace_probes"]
        self.assertEqual(set(probes), set(reference.FIXED_ASSET_PROBES))
        self.assertFalse(any(probes.values()), probes)

    def test_home_cache_probes_absent(self):
        probes = reference.asset_ref()["home_probes"]
        self.assertEqual(set(probes), set(reference.HOME_ASSET_PROBES))
        self.assertFalse(any(probes.values()), probes)

    def test_observed_copies_are_not_admitted(self):
        copies = reference.workspace_copies()
        self.assertEqual(len(copies), len(reference.OBSERVED_COPIES))
        for copy in copies:
            with self.subTest(project=copy["project"]):
                self.assertTrue(copy["present"])
                self.assertFalse(copy["exact_upstream"])
                self.assertFalse(copy["admitted"])
                self.assertFalse(copy["weights_present"])
                self.assertEqual(copy["revision"], reference.OBSERVED_COPIES[
                    copies.index(copy)]["revision"])
        report_value = report()["workspace_observations"]
        self.assertEqual(report_value["admitted_copy_count"], 0)
        self.assertFalse(report_value["exact_official_source_present"])

    def test_synthetic_admission_control_is_not_candidate(self):
        control = reference.synthetic_admission_control()
        self.assertEqual(control["status"], "admitted_synthetic_control")
        self.assertFalse(control["candidate_asset"])
        self.assertFalse(control["model_runtime_invoked"])
        self.assertFalse(control["vocoder_invoked"])
        self.assertEqual(control["qualification_effect"], "none")
        self.assertNotEqual(control["asset_id"], reference.ASSET_ID)

    def test_synthetic_asset_is_derived_not_model_bytes(self):
        self.assertEqual(
            reference.SYNTHETIC_ASSET_SHA256,
            hashlib.sha256(reference.SYNTHETIC_ASSET_BYTES).hexdigest(),
        )
        self.assertLess(len(reference.SYNTHETIC_ASSET_BYTES), 100_000)
        self.assertNotIn(b"ONNX", reference.SYNTHETIC_ASSET_BYTES)

    def test_rights_and_consent_are_unresolved(self):
        rights = reference.rights_status()
        self.assertFalse(rights["entry_present"])
        for scope in ("evaluation", "acquisition", "redistribution",
                      "customer_deployment", "public_playback",
                      "speaker_reference_permission", "output_use"):
            self.assertEqual(rights[scope], "unknown", scope)
        self.assertEqual(rights["consent"], "not_recorded")
        self.assertFalse(rights["evaluation_only"])
        self.assertTrue(rights["blocked"])


class TestReferenceInterface(unittest.TestCase):
    def test_no_candidate_geometry_is_fabricated(self):
        interface = reference.reference_interface()
        self.assertEqual(interface["model_id"], "hifigan_unpinned_voice_candidate")
        self.assertFalse(interface["candidate_geometry_known"])
        for key in ("candidate_sample_rate_hz", "candidate_hop_samples", "candidate_window",
                    "candidate_feature_contract", "candidate_upsample_layout",
                    "candidate_state_layout"):
            self.assertIsNone(interface[key], key)
        self.assertFalse(interface["model_bytes_read"])

    def test_surrogate_fixture_is_explicit(self):
        fixture = reference.reference_interface()["surrogate_fixture"]
        self.assertEqual(fixture["hop_samples"], reference.SURROGATE_HOP_SAMPLES)
        self.assertEqual(fixture["hop_samples"], reference.V0_FRAME_SAMPLES)
        self.assertEqual(fixture["state_names"], list(reference.STATE_NAMES))
        self.assertEqual(fixture["state_layout"], [[160], [1]])

    def test_no_native_fixture_supplies_parity(self):
        native = reference.native_evidence_status()
        self.assertFalse(native["candidate_native_reference_present"])
        self.assertEqual(native["model_parity"], "not_available")
        self.assertEqual(native["model_quality"], "not_assessed")
        self.assertFalse(native["used_for_qualification"])


class TestConfigRejections(unittest.TestCase):
    def test_matrix_exact_statuses(self):
        cases = reference.config_rejection_matrix()
        self.assertEqual(set(cases), set(EXPECTED_CONFIG) | {"synthetic_admission_control"})
        for name, reason in EXPECTED_CONFIG.items():
            with self.subTest(name=name):
                self.assertEqual(cases[name]["status"], "rejected")
                self.assertEqual(cases[name]["reason_codes"], [reason])
                self.assertFalse(cases[name]["processing_attempted"])
        self.assertEqual(cases["synthetic_admission_control"]["status"], "admitted_synthetic_control")

    def test_unknown_key_rejected(self):
        config = reference.default_config()
        config["unknown"] = 1
        self.assertEqual(reference.admit_config(config)["reason_codes"], ["config_keys_mismatch"])

    def test_non_dict_config_rejected(self):
        self.assertEqual(reference.admit_config([])["reason_codes"], ["config_type_invalid"])

    def test_candidate_config_never_creates(self):
        session = reference.StreamingSession()
        self.assertFalse(session.created)
        result = session.process_stream([0.0] * reference.SURROGATE_HOP_SAMPLES)
        self.assertEqual(result["status"], "rejected:not_admitted")
        self.assertFalse(result["qualifies"])

    def test_synthetic_requires_opt_in(self):
        config = reference.synthetic_config()
        config["surrogate_opt_in"] = False
        result = reference.admit_config(config)
        self.assertEqual(result["reason_codes"], ["surrogate_opt_in_required"])


class TestStreamRejections(unittest.TestCase):
    def test_matrix_exact_statuses_and_state_unchanged(self):
        cases = reference.stream_rejection_matrix()
        self.assertEqual(set(cases), set(EXPECTED_STREAMS))
        for name, status in EXPECTED_STREAMS.items():
            with self.subTest(name=name):
                self.assertEqual(cases[name]["status"], status)
                self.assertTrue(cases[name]["state_unchanged"])
                self.assertEqual(cases[name]["output_samples"], 0)

    def test_boundary_lengths(self):
        session = reference.StreamingSession(reference.synthetic_config())
        result = session.process_stream([0.0] * reference.MAX_STREAM_SAMPLES)
        self.assertEqual(result["status"], "ok_synthetic")
        self.assertEqual(result["output_samples"], reference.MAX_STREAM_SAMPLES)

    def test_max_abs_boundary(self):
        session = reference.StreamingSession(reference.synthetic_config())
        result = session.process_stream([reference.MAX_ABS_INPUT] + [0.0] * 159)
        self.assertEqual(result["status"], "ok_synthetic")
        session = reference.StreamingSession(reference.synthetic_config())
        result = session.process_stream([reference.MAX_ABS_INPUT + 1e-6] + [0.0] * 159)
        self.assertEqual(result["status"], "rejected:sample_out_of_range")

    def test_rejection_after_success_does_not_advance(self):
        session = reference.StreamingSession(reference.synthetic_config())
        first = session.process_stream([0.01] * reference.SURROGATE_HOP_SAMPLES)
        self.assertEqual(first["status"], "ok_synthetic")
        digest = session.state_digest()
        for bad in ([], "x", [float("nan")], [True]):
            result = session.process_stream(bad)
            self.assertTrue(result["status"].startswith("rejected:"))
            self.assertEqual(session.state_digest(), digest)


class TestChunkRejections(unittest.TestCase):
    def test_matrix_exact_statuses(self):
        cases = reference.chunk_rejection_matrix()
        self.assertEqual(set(cases), set(EXPECTED_CHUNKS))
        for name, status in EXPECTED_CHUNKS.items():
            with self.subTest(name=name):
                self.assertEqual(cases[name]["status"], status)
                self.assertTrue(cases[name]["state_unchanged"])
                self.assertTrue(cases[name]["state_payload_unchanged"])
                self.assertEqual(cases[name]["output_samples"], 0)

    def test_chunk_api_step_and_state_shapes(self):
        session = reference.StreamingSession(reference.synthetic_config())
        result = session.process_chunk([0.01] * reference.SURROGATE_HOP_SAMPLES)
        self.assertEqual(result["status"], "ok_synthetic")
        self.assertEqual(len(result["output"]), reference.SURROGATE_HOP_SAMPLES)
        self.assertIsNone(reference.validate_state(result["state_out"]))
        self.assertEqual(set(result["state_out"]), set(reference.STATE_NAMES))


class TestSyntheticSurrogate(unittest.TestCase):
    def test_deterministic_outputs(self):
        _target, observed = reference.synth("active_speech")
        first = reference.surrogate_stream(observed)
        second = reference.surrogate_stream(observed)
        self.assertEqual(first, second)
        self.assertEqual(reference.output_digest(first), reference.output_digest(second))

    def test_chunk_loop_matches_stream(self):
        _target, observed = reference.synth("active_speech")
        self.assertEqual(
            reference.surrogate_chunk_loop_control(observed),
            reference.surrogate_stream(observed),
        )

    def test_split_halves_not_equivalent(self):
        _target, observed = reference.synth("active_speech")
        self.assertNotEqual(
            reference.surrogate_split_halves(observed),
            reference.surrogate_stream(observed),
        )

    def test_prefix_is_stable(self):
        _target, observed = reference.synth("active_speech")
        whole = reference.surrogate_stream(observed)
        prefix = reference.surrogate_stream(observed[:15_360])
        self.assertEqual(prefix, whole[:15_360])

    def test_partial_tail_length(self):
        semantics = reference.streaming_semantics()
        self.assertEqual(semantics["partial_tail_input_samples"], 1_093)
        self.assertEqual(semantics["partial_tail_output_samples"], 1_093)

    def test_drain_bounds(self):
        semantics = reference.streaming_semantics()
        self.assertTrue(semantics["drain_within_bounds"])
        self.assertEqual(semantics["drain_calls"], 1)
        self.assertEqual(semantics["drain_produced_samples"], 160)
        self.assertLessEqual(semantics["drain_calls"], reference.MAX_DRAIN_CALLS)
        self.assertLessEqual(
            semantics["drain_produced_samples"], reference.MAX_DRAIN_PRODUCED_SAMPLES
        )

    def test_impulse_peak_preserved(self):
        semantics = reference.streaming_semantics()
        self.assertTrue(semantics["impulse_peak_preserved"])
        self.assertEqual(semantics["impulse_output_peak_index"], 4_000)

    def test_outputs_finite_and_peak_bounded(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            for variant in ("identity_passthrough", "noisy_control", "surrogate_stream",
                            "surrogate_chunk_loop_control", "surrogate_split_halves"):
                with self.subTest(condition=condition, variant=variant):
                    metrics = results[condition][variant]
                    self.assertEqual(metrics["nonfinite_count"], 0)
                    self.assertEqual(metrics["output_samples"], reference.SAMPLES)
                    self.assertLessEqual(metrics["peak_abs"], 1.0)

    def test_identity_is_exact_passthrough(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            self.assertTrue(results[condition]["identity_exact"])
            self.assertEqual(
                results[condition]["identity_passthrough"]["output_sha256"],
                results[condition]["noisy_control"]["output_sha256"],
            )

    def test_silence_has_no_target_metrics(self):
        metrics = reference.synthetic_results()["silence"]["surrogate_stream"]
        self.assertIsNone(metrics["noisy_snr_db"])
        self.assertIsNone(metrics["surrogate_snr_db"])
        self.assertIsNone(metrics["delta_snr_db"])

    def test_metrics_are_finite_or_none(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            for variant, metrics in results[condition].items():
                if not isinstance(metrics, dict):
                    continue
                for key, value in metrics.items():
                    if isinstance(value, float):
                        self.assertTrue(math.isfinite(value), f"{condition}/{variant}/{key}")


class TestSessionLifecycle(unittest.TestCase):
    def test_one_stream_close_and_replay(self):
        _target, observed = reference.synth("active_speech")
        session = reference.StreamingSession(reference.synthetic_config())
        first = session.process_stream(observed)
        self.assertEqual(first["status"], "ok_synthetic")
        self.assertEqual(first["startup_invalid_samples"], 160)
        digest = session.state_digest()
        second = session.process_stream(observed)
        self.assertEqual(second["status"], "rejected:stream_already_complete")
        self.assertEqual(session.state_digest(), digest)
        session.close()
        session.close()
        self.assertTrue(session.closed)
        after = session.process_stream(observed)
        self.assertEqual(after["status"], "rejected:session_closed")

    def test_reset_replay_identical_and_state_zeroed(self):
        semantics = reference.streaming_semantics()
        self.assertTrue(semantics["replay_bit_identical"])
        self.assertTrue(semantics["reset_state_zeroed"])
        self.assertEqual(semantics["reset_epoch"], 1)
        self.assertFalse(semantics["cross_stream_state_carried"])

    def test_state_digest_deterministic(self):
        _target, observed = reference.synth("quiet_speech")
        one = reference.StreamingSession(reference.synthetic_config())
        two = reference.StreamingSession(reference.synthetic_config())
        one.process_stream(observed)
        two.process_stream(observed)
        self.assertEqual(one.state_digest(), two.state_digest())


class TestResearchControl(unittest.TestCase):
    def test_pinned_out_of_scope_decision(self):
        value = report()["research_control"]
        self.assertEqual(value["inventory_record"], "hifi-gan-vocoder")
        self.assertEqual(value["candidate_matrix_record"], 53)
        self.assertEqual(value["candidate_matrix_line"], 54)
        self.assertEqual(value["record_status"], "out of scope")
        self.assertIn("do not independently transform", value["finding"])
        self.assertFalse(value["comparison_retained"])
        self.assertFalse(value["comparison_reproduced"])
        self.assertEqual(value["proceed_defer"], "DEFER")
        self.assertTrue(value["required_for_proceed"])

    def test_voice_task_fit_is_out_of_scope(self):
        profile = report()["voice_profile"]
        self.assertEqual(profile["task_fit"], "out_of_scope_vocoder_only")
        self.assertTrue(profile["synthetic_only"])
        self.assertFalse(profile["candidate_result_present"])


class TestReportDisposition(unittest.TestCase):
    def test_machine_readable_disposition(self):
        value = report()
        self.assertEqual(value["decision"], "DEFER")
        self.assertEqual(value["defer_before"], "processor_exposure")
        self.assertEqual(value["status"], "proposal_only_incomplete")
        self.assertEqual(value["evidence_status"], "incomplete")
        self.assertEqual(value["qualification"]["status"], "not_qualified")
        self.assertFalse(value["qualification"]["qualified"])
        self.assertFalse(value["qualification"]["missing_result_may_qualify"])

    def test_exactly_eight_blocked_gates(self):
        value = report()
        gates = value["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual(value["release_gate_count"], 8)
        self.assertEqual({gate["name"] for gate in gates}, EXPECTED_GATES)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["evidence"])
            self.assertTrue(gate["reopen"])
        self.assertEqual(value["counts"]["release_gates_blocked"], 8)

    def test_no_claim_is_true(self):
        for name, claimed in report()["claims"].items():
            with self.subTest(claim=name):
                self.assertFalse(claimed)

    def test_boundary_preserved(self):
        boundary = report()["boundary"]
        for name in ("registered", "enabled_by_default", "default_selected",
                     "public_api_abi_change", "provider_registration",
                     "descriptor_registry_change", "installed_v0_behavior_change",
                     "shared_build_or_ci_change", "processor_exposure",
                     "task_board_or_handoff_write", "adapter_json_added",
                     "readiness_json_added", "asset_bundled", "weights_vendored",
                     "model_runtime_invoked", "vocoder_invoked", "sdk_data_dir_added"):
            self.assertFalse(boundary[name], name)
        self.assertTrue(boundary["installed_v0_geometry_preserved"])

    def test_voice_profile_unmeasured_fields(self):
        profile = report()["voice_profile"]
        self.assertEqual(profile["semantic_preservation"], "blocked_unmeasured")
        self.assertEqual(profile["speaker_identity_similarity"], "blocked_unmeasured")
        self.assertEqual(profile["naturalness"], "blocked_unmeasured")
        self.assertEqual(profile["first_output_tail_timing"], "blocked_unmeasured")
        self.assertEqual(profile["consent"], "not_recorded")
        self.assertEqual(profile["permitted_reference_input"], "absent")
        self.assertEqual(profile["output_use"], "blocked")
        self.assertEqual(profile["listening"], "not_run")
        self.assertFalse(profile["real_runtime"])
        self.assertFalse(profile["candidate_result_present"])
        self.assertEqual(profile["task_fit"], "out_of_scope_vocoder_only")

    def test_report_has_no_self_digest(self):
        value = report()
        self.assertNotIn("report_sha256", value)
        self.assertNotIn("artifact_pins", value)


class TestRegeneration(unittest.TestCase):
    def test_report_sha256_sidecar_and_contract_pins(self):
        value = report()
        payload = reference.canonical_report_bytes(value)
        digest = hashlib.sha256(payload).hexdigest()
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, f"{digest}  report.json\n")
        self.assertEqual((HERE / "report.json").read_bytes(), payload)

        pins = cli.contract_pins()
        self.assertNotIn("contract.json", pins)
        self.assertIn("README.md", pins)
        contract = load_strict("contract.json")
        self.assertEqual(contract["artifact_pins"], pins)
        for name, pinned in pins.items():
            self.assertEqual(reference.sha256_file(HERE / name), pinned)

    def test_manifest_pins_and_no_board_hash(self):
        lines = (HERE / "SOURCES.sha256").read_text(encoding="utf-8").splitlines()
        self.assertTrue(lines[0].startswith("#"))
        entries = [line for line in lines[1:] if line]
        paths = [line.split("  ", 1)[1] for line in entries]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertNotIn("plan/swarm/TASKS.json", "\n".join(paths))
        self.assertNotIn("source:audio-benchmark-platform/plan/swarm/TASKS.json", paths)
        for line in entries:
            digest, path = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            if path.startswith("source:"):
                self.assertEqual(
                    reference.sha256_file(reference.SOURCE_ROOT / path[len("source:"):]),
                    digest,
                )
            elif path.startswith("worktree:"):
                self.assertEqual(
                    reference.sha256_file(reference.SDK_ROOT / path[len("worktree:"):]),
                    digest,
                )

    def test_readme_digest_table_matches(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        block = text.split("<!-- DIGEST_TABLE_START -->", 1)[1].split("<!-- DIGEST_TABLE_END -->", 1)[0]
        for name in cli.TABLE_FILES:
            payload = (HERE / name).read_bytes()
            row = f"| `{name}` | `{hashlib.sha256(payload).hexdigest()}` | {len(payload)} |"
            self.assertIn(row, block)

    def test_three_cold_start_regenerations_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "evidence"
            shutil.copytree(
                HERE,
                copy,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            baseline = {
                name: (HERE / name).read_bytes()
                for name in reference.LOCAL_FILES
                if (HERE / name).is_file()
            }
            baseline["SOURCES.sha256"] = (HERE / "SOURCES.sha256").read_bytes()
            env = dict(os.environ)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["SDK_ROOT"] = str(reference.SDK_ROOT)
            env["SOURCE_ROOT"] = str(reference.SOURCE_ROOT)
            snapshots = []
            for _ in range(3):
                result = subprocess.run(
                    [sys.executable, str(copy / "run.py"), "--all"],
                    cwd=str(copy),
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                snapshot = {}
                for name in sorted(baseline):
                    snapshot[name] = (copy / name).read_bytes()
                snapshots.append(snapshot)
            self.assertEqual(snapshots[0], snapshots[1])
            self.assertEqual(snapshots[1], snapshots[2])
            self.assertEqual(snapshots[0], baseline)


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
            self.assertEqual((HERE / name).read_text(encoding="utf-8"), SIDECAR, name)

    def test_fail_closed_local_set(self):
        present = {
            path.relative_to(HERE).as_posix()
            for path in HERE.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        expected = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
        self.assertEqual(present, expected)

    def test_no_network_or_download_imports(self):
        forbidden = ("import " + "requests", "import " + "urllib", "import " + "socket",
                     "import " + "http.client", "url" + "open", "url" + "retrieve",
                     "pip " + "install")
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            text = (HERE / name).read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, f"{name}: {token}")

    def test_no_asset_path_access_in_reference(self):
        text = (HERE / "reference.py").read_text(encoding="utf-8")
        self.assertIn("(SDK_ROOT / ASSET_LEDGER_PATH).is_file()", text)
        self.assertNotIn("ASSET_LEDGER_PATH).read", text)
        self.assertNotIn("open(ASSET_LEDGER_PATH", text)
        for token in ("import torch", "import onnxruntime", "InferenceSession(", "subprocess.run"):
            self.assertNotIn(token, text, token)


if __name__ == "__main__":
    unittest.main(verbosity=2)

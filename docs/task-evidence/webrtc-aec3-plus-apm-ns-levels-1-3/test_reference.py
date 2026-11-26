# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only tests for the task-local evidence package."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import reference as ref

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
WORKSPACE = WORKTREE.parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PinTests(unittest.TestCase):
    def test_source_pins_are_exact(self) -> None:
        self.assertEqual(len(ref.SOURCE_PINS), 15)
        for name, expected in ref.SOURCE_PINS.items():
            self.assertRegex(expected, r"^[0-9a-f]{64}$")
            path = WORKSPACE / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(sha(path), expected, name)

    def test_boundary_pins_are_exact(self) -> None:
        self.assertEqual(len(ref.BOUNDARY_PINS), 3)
        for name, expected in ref.BOUNDARY_PINS.items():
            path = WORKTREE / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(sha(path), expected, name)

    def test_sibling_pins_are_exact(self) -> None:
        self.assertEqual(len(ref.SIBLING_PINS), 8)
        for name, expected in ref.SIBLING_PINS.items():
            path = WORKTREE / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(sha(path), expected, name)

    def test_mutable_board_is_not_hashed(self) -> None:
        self.assertFalse(ref.MUTABLE_PROVENANCE["hashed"])
        self.assertFalse(ref.MUTABLE_PROVENANCE["gate"])
        self.assertNotIn("audio-benchmark-platform/plan/swarm/TASKS.json",
                         ref.SOURCE_PINS)
        self.assertNotIn("audio-benchmark-platform/plan/swarm/TASKS.json",
                         ref.BOUNDARY_PINS)
        self.assertNotIn("audio-benchmark-platform/plan/swarm/TASKS.json",
                         ref.SIBLING_PINS)

    def test_task_row_identity(self) -> None:
        self.assertEqual(ref.TASK_ROW_IDENTITY["id"], ref.TASK_ID)
        self.assertEqual(ref.TASK_ROW_IDENTITY["component"], ref.COMPONENT)
        self.assertEqual(ref.TASK_ROW_IDENTITY["base_commit"], ref.BASE_COMMIT)
        self.assertEqual(ref.TASK_ROW_IDENTITY["branch"], ref.BRANCH)
        self.assertEqual(ref.TASK_ROW_IDENTITY["evidence"],
                         ["research/aec_research_20261028.md"])

    def test_scope_is_synthetic_and_local(self) -> None:
        self.assertTrue(ref.SCOPE["task_local_only"])
        self.assertTrue(ref.SCOPE["synthetic_only"])
        self.assertFalse(ref.SCOPE["real_webrtc_aec3_source_or_runtime"])
        self.assertFalse(ref.SCOPE["real_webrtc_apm_source_or_runtime"])
        self.assertFalse(ref.SCOPE["downloads"])
        self.assertFalse(ref.SCOPE["release_claim"])

    def test_public_surface_is_unchanged(self) -> None:
        self.assertTrue(ref.PUBLIC_SURFACE)
        self.assertTrue(all(value is False for value in ref.PUBLIC_SURFACE.values()))


class ConfigTests(unittest.TestCase):
    def test_one_instance_records_all_toggles(self) -> None:
        payload = ref.configured_apm_payload()
        self.assertEqual(payload["instance_count"], 1)
        self.assertEqual(payload["toggle_names"], list(ref.APM_TOGGLE_NAMES))
        self.assertEqual(set(payload["toggles"]), set(ref.APM_TOGGLE_NAMES))
        self.assertEqual(len(payload["toggle_matrix"]), len(ref.APM_TOGGLE_NAMES))
        self.assertFalse(payload["qualifies"])

    def test_exactly_three_levels(self) -> None:
        self.assertEqual(list(ref.NS_LEVELS), [1, 2, 3])
        payload = ref.configured_apm_payload()
        self.assertEqual(payload["levels_benchmarked"], [1, 2, 3])

    def test_only_ns_level_changes(self) -> None:
        first = ref.apm_instance(1)
        second = ref.apm_instance(2)
        third = ref.apm_instance(3)
        self.assertEqual(first["toggles"]["echo_canceller"],
                         second["toggles"]["echo_canceller"])
        self.assertEqual(second["toggles"]["echo_canceller"],
                         third["toggles"]["echo_canceller"])
        self.assertNotEqual(first["toggles"]["noise_suppression"],
                            second["toggles"]["noise_suppression"])
        for name in ref.APM_TOGGLE_NAMES:
            if name == "noise_suppression":
                continue
            self.assertEqual(first["toggles"][name], third["toggles"][name])

    def test_rejects_invalid_levels(self) -> None:
        for value in (0, 4, -1, True, 1.0, "1", None, [1]):
            with self.assertRaises(ref.ReferenceError):
                ref.apm_instance(value)  # type: ignore[arg-type]

    def test_rejects_unknown_toggle(self) -> None:
        config = ref.apm_instance(1)
        config["toggles"]["made_up"] = {"enabled": True}
        with self.assertRaises(ref.ReferenceError):
            ref.validate_instance_config(config)

    def test_rejects_missing_toggle(self) -> None:
        config = ref.apm_instance(1)
        del config["toggles"]["high_pass_filter"]
        with self.assertRaises(ref.ReferenceError):
            ref.validate_instance_config(config)

    def test_rejects_wrong_sample_rate(self) -> None:
        config = ref.apm_instance(1)
        config["sample_rate_hz"] = 8000
        with self.assertRaises(ref.ReferenceError):
            ref.validate_instance_config(config)

    def test_rejects_nonfinite_toggle(self) -> None:
        config = ref.apm_instance(2)
        config["toggles"]["noise_suppression"]["gain_floor"] = float("nan")
        with self.assertRaises(ref.ReferenceError):
            ref.validate_instance_config(config)

    def test_config_digest_is_stable(self) -> None:
        self.assertEqual(ref.sha256_bytes(ref.canonical_bytes(ref.apm_instance(2))),
                         ref.sha256_bytes(ref.canonical_bytes(ref.apm_instance(2))))

    def test_aec_only_is_a_control_not_a_level(self) -> None:
        config = ref.aec_only_instance()
        self.assertFalse(config["toggles"]["noise_suppression"]["enabled"])
        self.assertEqual(config["toggles"]["noise_suppression"]["level"], 0)
        with self.assertRaises(ref.ReferenceError):
            ref.validate_instance_config(config)


class FixtureTests(unittest.TestCase):
    def test_geometry(self) -> None:
        spec = ref.fixture_payload()
        self.assertEqual(spec["sample_rate_hz"], 16000)
        self.assertEqual(spec["frame_samples"], 160)
        self.assertEqual(spec["frames"], 120)
        self.assertEqual(spec["samples"], 19200)

    def test_deterministic(self) -> None:
        first = ref.build_fixture("duplex")
        second = ref.build_fixture("duplex")
        self.assertEqual(ref.digest_values(first["microphone"]),
                         ref.digest_values(second["microphone"]))

    def test_conditions_differ(self) -> None:
        duplex = ref.build_fixture("duplex")
        near = ref.build_fixture("near_only")
        echo = ref.build_fixture("echo_only")
        self.assertNotEqual(ref.digest_values(duplex["microphone"]),
                            ref.digest_values(near["microphone"]))
        self.assertNotEqual(ref.digest_values(duplex["microphone"]),
                            ref.digest_values(echo["microphone"]))

    def test_delayed_reference_is_shifted(self) -> None:
        duplex = ref.build_fixture("duplex")
        delayed = ref.build_fixture("delayed_render")
        self.assertEqual(delayed["reference"][:ref.DELAYED_REFERENCE_SAMPLES],
                         [0.0] * ref.DELAYED_REFERENCE_SAMPLES)
        self.assertEqual(delayed["reference"][ref.DELAYED_REFERENCE_SAMPLES],
                         duplex["reference"][0])

    def test_no_reference_is_none(self) -> None:
        self.assertIsNone(ref.build_fixture("no_reference")["reference"])

    def test_dropout_and_reset_bounds(self) -> None:
        self.assertEqual(ref.build_fixture("reference_dropout")["dropout"],
                         (ref.DROP_START_FRAME, ref.DROP_END_FRAME))
        self.assertEqual(ref.build_fixture("reset")["reset_frame"], ref.RESET_FRAME)

    def test_unknown_condition_rejected(self) -> None:
        with self.assertRaises(ref.ReferenceError):
            ref.build_fixture("unknown")


class ProcessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = ref.build_fixture("duplex")
        self.mic = tuple(self.data["microphone"][:ref.FRAME_SAMPLES])
        self.ref = tuple(self.data["reference"][:ref.FRAME_SAMPLES])

    def test_rejects_short_frame(self) -> None:
        with self.assertRaises(ref.ReferenceError):
            ref.ApmAecNs(1).process_frame(self.mic[:-1], self.ref)

    def test_rejects_nonfinite_microphone(self) -> None:
        bad = tuple([float("nan")] + list(self.mic[1:]))
        with self.assertRaises(ref.ReferenceError):
            ref.ApmAecNs(1).process_frame(bad, self.ref)

    def test_rejects_out_of_range_microphone(self) -> None:
        bad = tuple([9.0] + list(self.mic[1:]))
        with self.assertRaises(ref.ReferenceError):
            ref.ApmAecNs(1).process_frame(bad, self.ref)

    def test_rejects_bool_microphone(self) -> None:
        bad = tuple([True] + list(self.mic[1:]))
        with self.assertRaises(ref.ReferenceError):
            ref.ApmAecNs(1).process_frame(bad, self.ref)

    def test_rejects_short_reference(self) -> None:
        with self.assertRaises(ref.ReferenceError):
            ref.ApmAecNs(1).process_frame(self.mic, self.ref[:8])

    def test_rejects_nonfinite_reference(self) -> None:
        bad = tuple([float("inf")] + list(self.ref[1:]))
        with self.assertRaises(ref.ReferenceError):
            ref.ApmAecNs(1).process_frame(self.mic, bad)

    def test_rejects_stale_epoch(self) -> None:
        engine = ref.ApmAecNs(1)
        with self.assertRaises(ref.ReferenceError):
            engine.process_frame(self.mic, self.ref, epoch=0, position=0)

    def test_rejects_wrong_position(self) -> None:
        engine = ref.ApmAecNs(1)
        with self.assertRaises(ref.ReferenceError):
            engine.process_frame(self.mic, self.ref, epoch=1, position=999)

    def test_invalid_frame_leaves_state_unchanged(self) -> None:
        engine = ref.ApmAecNs(1)
        before = engine.state_digest()
        with self.assertRaises(ref.ReferenceError):
            engine.process_frame(self.mic[:8], self.ref)
        self.assertEqual(engine.state_digest(), before)

    def test_reset_rejects_stale_epoch(self) -> None:
        engine = ref.ApmAecNs(1)
        with self.assertRaises(ref.ReferenceError):
            engine.reset(1, 0)

    def test_reset_rejects_negative_position(self) -> None:
        engine = ref.ApmAecNs(1)
        with self.assertRaises(ref.ReferenceError):
            engine.reset(2, -1)

    def test_reset_replay_is_identical(self) -> None:
        payload = ref.reset_replay()
        self.assertTrue(payload["byte_identical"])
        self.assertNotEqual(payload["continued_state_digest"], "")
        self.assertEqual(len(payload["invalid_reset_rejections"]), 2)

    def test_chunk_identity(self) -> None:
        payload = ref.causality_payload()
        self.assertEqual(len(set(payload["chunk_identity"].values())), 1)

    def test_zero_algorithmic_delay(self) -> None:
        payload = ref.causality_payload()
        self.assertEqual(payload["algorithmic_delay_samples"], 0)
        self.assertEqual(payload["buffering_delay_samples"], 0)
        self.assertFalse(payload["future_frame_reads"])
        self.assertEqual(payload["silence_peak_abs"], 0.0)

    def test_no_reference_passthrough(self) -> None:
        engine = ref.ApmAecNs(1)
        result = engine.process_frame(self.mic, None)
        self.assertEqual(result["status"], "passthrough_no_reference")
        self.assertEqual(tuple(result["samples"]), self.mic)
        self.assertEqual(engine.no_reference_frames, 1)

    def test_nonfinite_state_safety_reset(self) -> None:
        engine = ref.ApmAecNs(1)
        engine.main[0] = float("nan")
        result = engine.process_frame(self.mic, self.ref)
        self.assertEqual(engine.safety_resets, 1)
        self.assertTrue(all(math.isfinite(value) for value in result["samples"]))

    def test_state_digest_changes_with_input(self) -> None:
        engine = ref.ApmAecNs(1)
        before = engine.state_digest()
        engine.process_frame(self.mic, self.ref)
        self.assertNotEqual(engine.state_digest(), before)

    def test_memory_accounting_is_finite(self) -> None:
        self.assertGreater(ref.ApmAecNs(3).memory_floats(), 0)

    def test_level_zero_constructor_rejected(self) -> None:
        with self.assertRaises(ref.ReferenceError):
            ref.ApmAecNs(0)


class RunTests(unittest.TestCase):
    def test_three_level_runs_are_independent(self) -> None:
        rows = ref.per_level_runs()
        self.assertEqual([row["ns_level"] for row in rows], [1, 2, 3])
        self.assertEqual(len({row["output_sha256"] for row in rows}), 3)
        for row in rows:
            self.assertFalse(row["qualifies"])
            self.assertTrue(row["level_isolation"].startswith("fresh state"))

    def test_level_metrics_are_finite(self) -> None:
        for row in ref.per_level_runs():
            metrics = row["metrics"]
            self.assertEqual(metrics["nonfinite_count"], 0)
            self.assertTrue(math.isfinite(metrics["erle_late_db"]))
            self.assertTrue(math.isfinite(metrics["near_snr_late_db"]))
            self.assertLessEqual(metrics["peak_abs"], ref.MAX_ABS_INPUT)

    def test_aec_only_control_runs(self) -> None:
        row = ref.control_runs()["aec_only"]
        self.assertFalse(row["qualifies"])
        self.assertEqual(row["metrics"]["nonfinite_count"], 0)

    def test_missing_reference_is_blocked(self) -> None:
        row = ref.control_runs()["no_reference_passthrough"]
        self.assertEqual(row["status"], "blocked_no_reference")
        self.assertFalse(row["qualifies"])

    def test_delayed_render_is_misaligned(self) -> None:
        row = ref.control_runs()["delayed_render"]
        self.assertEqual(row["status"], "misaligned_reference")
        self.assertFalse(row["qualifies"])

    def test_dropout_is_partial(self) -> None:
        row = ref.control_runs()["reference_dropout"]
        self.assertEqual(row["status"], "partial_reference")
        self.assertFalse(row["qualifies"])

    def test_identity_is_bit_exact(self) -> None:
        data = ref.build_fixture("duplex")
        result = ref.run_stream(data, mode="identity")
        self.assertEqual(tuple(result["output"]), tuple(data["microphone"]))

    def test_unknown_mode_rejected(self) -> None:
        with self.assertRaises(ref.ReferenceError):
            ref.run_stream(ref.build_fixture("duplex"), mode="mystery")

    def test_invalid_chunk_rejected(self) -> None:
        with self.assertRaises(ref.ReferenceError):
            ref.run_stream(ref.build_fixture("duplex"), chunk_frames=0)


class JsonTests(unittest.TestCase):
    def _write(self, payload: str) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                             encoding="utf-8")
        handle.write(payload)
        handle.close()
        return Path(handle.name)

    def test_strict_json_rejects_nan(self) -> None:
        path = self._write('{"x": NaN}')
        with self.assertRaises(ValueError):
            ref.read_strict_json(path)
        path.unlink()

    def test_strict_json_rejects_duplicate_keys(self) -> None:
        path = self._write('{"x": 1, "x": 2}')
        with self.assertRaises(ValueError):
            ref.read_strict_json(path)
        path.unlink()

    def test_strict_json_rejects_non_object(self) -> None:
        path = self._write('[1, 2, 3]')
        with self.assertRaises(ValueError):
            ref.read_strict_json(path)
        path.unlink()

    def test_canonical_bytes_reject_nonfinite(self) -> None:
        with self.assertRaises(ValueError):
            ref.canonical_bytes({"x": float("nan")})


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = ref.build_report()

    def test_report_key_set(self) -> None:
        self.assertEqual(set(self.report), ref.REPORT_KEYS)

    def test_decision_and_status(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_not_qualified")
        self.assertEqual(self.report["completeness"], "incomplete")

    def test_qualification_is_not_qualified(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["qualifies"])
        self.assertTrue(qualification["incomplete"])
        self.assertFalse(qualification["missing_result_promoted"])

    def test_eight_release_gates_all_blocked(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertTrue(all(gate["qualifies"] is False for gate in gates))
        self.assertTrue(all(gate["evidence"] is None for gate in gates))

    def test_per_level_rows(self) -> None:
        rows = self.report["per_level_runs"]
        self.assertEqual([row["ns_level"] for row in rows], [1, 2, 3])
        self.assertTrue(all(row["qualifies"] is False for row in rows))
        self.assertTrue(all(row["ns_enabled"] is True for row in rows))

    def test_level_isolation(self) -> None:
        rows = self.report["per_level_runs"]
        for row in rows:
            self.assertEqual(row["toggles_delta"],
                             {"noise_suppression.level": row["ns_level"]})

    def test_level_ablation(self) -> None:
        ablation = self.report["level_ablation"]
        self.assertEqual(len(ablation), 3)
        self.assertTrue(all(row["independent_level_run"] for row in ablation))
        self.assertTrue(all(row["only_ns_level_differs"] for row in ablation))
        self.assertTrue(all(row["qualifies"] is False for row in ablation))

    def test_controls_cover_room_cases(self) -> None:
        controls = self.report["controls"]
        for name in ("identity", "fixed_attenuation", "aec_only",
                     "no_reference_passthrough", "delayed_render",
                     "reference_dropout", "near_only", "echo_only", "reset"):
            self.assertIn(name, controls)
            self.assertFalse(controls[name]["qualifies"])
        self.assertTrue(controls["reset"]["reset_replay"]["byte_identical"])

    def test_acceptance_profile_all_nonqualifying(self) -> None:
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "room")
        self.assertFalse(profile["all_qualify"])
        self.assertFalse(profile["qualifies"])
        self.assertTrue(all(item["qualifies"] is False
                            for item in profile["items"]))

    def test_adverse_results_retained(self) -> None:
        adverse = self.report["adverse_results"]
        self.assertTrue(adverse)
        self.assertTrue(all(row["qualifies"] is False for row in adverse))

    def test_missing_results_not_promoted(self) -> None:
        missing = self.report["missing_results"]
        self.assertTrue(missing)
        for row in missing:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["metrics"])
            self.assertFalse(row["qualifies"])

    def test_artifact_assessment_blocked(self) -> None:
        assessment = self.report["artifact_assessment"]
        self.assertTrue(assessment["all_required_absent"])
        self.assertFalse(assessment["runtime_presence"]["present"])
        self.assertFalse(assessment["package_assets"]["present"])
        self.assertTrue(assessment["conclusion"].startswith("BLOCKED:"))

    def test_failure_controls(self) -> None:
        controls = self.report["failure_controls"]
        self.assertTrue(controls["all_explicit"])
        self.assertTrue(all(controls["checks"].values()))
        self.assertGreaterEqual(controls["rejected_count"], 10)
        self.assertGreaterEqual(controls["blocked_count"], 1)

    def test_observed_provenance_is_not_reproduced(self) -> None:
        provenance = self.report["observed_provenance"]
        self.assertFalse(provenance["reproduced_here"])
        self.assertFalse(provenance["qualifies"])
        self.assertTrue(all(not row["reproduced_here"]
                            for row in provenance["documented_context"]))

    def test_ranking_is_not_a_recommendation(self) -> None:
        ranking = self.report["ranking"]
        self.assertEqual(ranking["order"], "not_ranked")
        self.assertIsNone(ranking["recommendation"])
        self.assertFalse(ranking["qualifies"])

    def test_no_qualifying_true_anywhere(self) -> None:
        def walk(value):
            if isinstance(value, dict):
                if "qualifies" in value:
                    self.assertIs(value["qualifies"], False)
                for item in value.values():
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
        walk(self.report)

    def test_regeneration_is_three_identical(self) -> None:
        regeneration = self.report["regeneration"]
        self.assertEqual(regeneration["runs"], 3)
        self.assertTrue(regeneration["byte_identical"])
        self.assertEqual(len(set(regeneration["canonical_digests"])), 1)

    def test_canonical_report_roundtrip(self) -> None:
        payload, digest, _ = ref.render_report()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertEqual(hashlib.sha256(payload).hexdigest(), digest)
        parsed = json.loads(payload)
        self.assertEqual(parsed["decision"], "DEFER")

    def test_fixture_hashes_are_sha256(self) -> None:
        fixture = self.report["fixture"]
        for key in ("render_sha256", "near_sha256", "echo_sha256",
                    "microphone_sha256", "reference_sha256"):
            self.assertRegex(fixture[key], r"^[0-9a-f]{64}$")

    def test_task_row_and_pins(self) -> None:
        self.assertEqual(self.report["task_row"], ref.TASK_ROW_IDENTITY)
        self.assertEqual(self.report["mutable_provenance"],
                         ref.MUTABLE_PROVENANCE)
        self.assertEqual(self.report["source_pins"], ref.SOURCE_PINS)
        self.assertEqual(self.report["boundary_pins"], ref.BOUNDARY_PINS)
        self.assertEqual(self.report["sibling_pins"], ref.SIBLING_PINS)

    def test_configured_instance_hashes(self) -> None:
        payload = self.report["configured_apm_instance"]
        for row in payload["per_level"]:
            expected = ref.sha256_bytes(ref.canonical_bytes(ref.apm_instance(row["level"])))
            self.assertEqual(row["config_sha256"], expected)
            self.assertEqual(row["only_delta"],
                             {"noise_suppression.level": row["level"]})

    def test_non_claims(self) -> None:
        self.assertTrue(self.report["non_claims"])
        self.assertIn("No provider is registered, exposed or default-enabled.",
                      self.report["non_claims"])


class ContractFileTests(unittest.TestCase):
    def test_contract_file_exists_and_matches(self) -> None:
        path = ROOT / "contract.json"
        self.assertTrue(path.is_file())
        contract = ref.read_strict_json(path)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["completeness"], "incomplete")
        self.assertEqual(contract["qualification"]["status"], "not_qualified")
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in contract["release_gates"]))
        self.assertEqual(contract["task_row"], ref.TASK_ROW_IDENTITY)


if __name__ == "__main__":
    unittest.main()

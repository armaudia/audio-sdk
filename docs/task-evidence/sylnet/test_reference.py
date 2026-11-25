# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance suite for the task-local SDK-SYLNET evidence package."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
PYTHON = Path("/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12")
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.strict_loads(REPORT.read_text(encoding="utf-8"))
        cls.contract = reference.strict_loads(CONTRACT.read_text(encoding="utf-8"))
        cls.generated = reference.canonical_report_bytes(reference.build_report())

    def test_01_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_bytes(), f"{digest}  report.json\n".encode("ascii"))

    def test_03_disposition_is_defer_incomplete_not_qualified(self) -> None:
        for key, expected in (
                ("status", "proposal_only_synthetic_incomplete"),
                ("evidence_status", "incomplete"),
                ("qualification_status", "not_qualified"),
                ("decision", "DEFER"),
                ("defer_before", "processor_exposure")):
            self.assertEqual(self.report[key], expected, key)
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_04_rate_profile_applied_with_no_render_claim(self) -> None:
        self.assertEqual(self.report["profile"], "rate")
        rate = self.report["rate_profile"]
        self.assertEqual(rate["profile"], "rate")
        self.assertFalse(rate["renderer_executed"])
        self.assertFalse(rate["duration_measured"])
        self.assertEqual(rate["pitch"], "not_measured_no_rendered_audio")
        self.assertEqual(rate["transient_audibility"], "not_measured_no_listening")

    def test_05_boundary_is_opt_in_unregistered_and_unchanged(self) -> None:
        keys = ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "descriptor_registry_change", "shared_cmakelists_change",
                "installed_v0_behavior_change", "processor_exposure", "ci_change")
        for key in keys:
            self.assertIs(self.report["boundary"][key], False, key)
            self.assertIs(self.contract["boundary"][key], False, key)
        self.assertEqual(self.report["boundary"]["descriptor_settings"], {})

    def test_06_public_v0_geometry_and_window_preserved(self) -> None:
        fmt = self.report["format"]
        self.assertEqual(fmt["sample_rate_hz"], 16000)
        self.assertEqual(fmt["channels"], 1)
        self.assertEqual(fmt["sample_format"], "f32")
        self.assertEqual(fmt["frame_samples"], 160)
        self.assertEqual(fmt["window_samples"], 64000)
        self.assertEqual(fmt["final_partial_samples"], 37)
        self.assertFalse(fmt["sdk_callback_invoked"])

    def test_07_no_prohibited_real_model_audio_device_or_release_claim(self) -> None:
        for key, value in self.report["negative_claims"].items():
            self.assertIs(value, False, key)
        for key in ("sylnet_source", "sylnet_checkpoint_loaded", "model_weights",
                    "real_audio", "real_labels", "vendor_runtime_invoked",
                    "device_timing", "listening_result", "rendered_playback",
                    "benchmark_claim", "release_claim", "registered_provider"):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["surrogate"]["is_sylnet_source"], False)

    def test_08_base_commit_and_branch_pinned(self) -> None:
        self.assertEqual(self.report["base_commit"],
                         "66b9f8d8724ed95e80ff2598781ff80fb5359988")
        self.assertEqual(self.report["branch"], "swarm/SDK-SYLNET")

    def test_09_required_keys_present(self) -> None:
        for key in ("schema_id", "task_id", "base_commit", "profile", "conditions",
                    "controls", "adverse", "rate_profile", "repeatability",
                    "playback_buffering", "regressions", "gates", "missing_evidence",
                    "exact_blockers", "source_reported", "source_pins", "boundary_pins",
                    "model_provenance", "licensing_analysis", "negative_claims",
                    "tool_provenance"):
            self.assertIn(key, self.report)

    def test_10_contract_is_task_local_and_digest_matches(self) -> None:
        self.assertEqual(self.contract["task"], reference.TASK)
        self.assertEqual(self.contract["profile"], "rate")
        self.assertEqual(CONTRACT.read_bytes(), reference.contract_bytes())
        self.assertEqual(self.report["contract_sha256"],
                         hashlib.sha256(CONTRACT.read_bytes()).hexdigest())

    def test_11_source_pins_match_constants_and_files(self) -> None:
        self.assertEqual(self.report["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(self.contract["source_pins"], reference.SOURCE_PINS)
        for path, digest in reference.SOURCE_PINS.items():
            actual = hashlib.sha256((reference.SOURCE_ROOT / path).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, path)

    def test_12_boundary_pins_match_constants_and_files(self) -> None:
        self.assertEqual(self.report["boundary_pins"], reference.BOUNDARY_PINS)
        for path, digest in reference.BOUNDARY_PINS.items():
            actual = hashlib.sha256((SDK_ROOT / path).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, path)

    def test_13_manifest_is_deterministic_and_complete(self) -> None:
        self.assertEqual(PINS.read_bytes(), reference.sources_bytes())
        names = {line.split("  ", 1)[1] for line in PINS.read_text(encoding="ascii").splitlines()
                 if line and not line.startswith("#") and "  " in line}
        for path in HERE.iterdir():
            if path.is_file() and path.name != "SOURCES.sha256":
                self.assertIn(reference.TASK_PREFIX + path.name, names, path.name)

    def test_14_strict_json_rejects_duplicates_nonfinite_and_arrays(self) -> None:
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}',
                     '{"a":-Infinity}', '[1,2]'):
            with self.assertRaises(ValueError):
                reference.strict_loads(text)

    def test_15_pin_parser_rejects_malformed_duplicate_and_escaping(self) -> None:
        for text in ("not-a-line", "a" * 64 + "  ../escape",
                     "a" * 64 + "  docs/task-evidence/sylnet/unknown",
                     "\n".join(["0" * 64 + "  CONTRACTS.md",
                                "0" * 64 + "  CONTRACTS.md"])):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(text)

    def test_16_all_conditions_and_rate_cases_scored(self) -> None:
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for cases in self.report["conditions"].values():
            self.assertEqual(set(cases), set(reference.RATE_CASES))

    def test_17_windows_are_exact_64000_samples(self) -> None:
        for cases in self.report["conditions"].values():
            for case in cases.values():
                self.assertEqual(case["source_interval"], [0, 64000])
                self.assertEqual([pair[0] for pair in case["event_intervals"]],
                                 list(range(0, 64000, 160)))
                self.assertEqual(case["event_intervals"][-1][1], 64000)
                self.assertEqual(case["source_frame_count"], 400)
                self.assertEqual(case["accepted_frame_count"], 400)
                self.assertEqual(case["rejections"], [])

    def test_18_final_partial_coordinates_exact(self) -> None:
        for condition, cases in self.report["conditions"].items():
            expected_valid = 37 if condition == "tail_partial" else 160
            for case in cases.values():
                partial = case["final_partial"]
                self.assertEqual(partial["source"], [64000 - 160, 64000])
                self.assertEqual(partial["valid_count"], expected_valid)
                self.assertTrue(partial["final_flag"])
                self.assertEqual(partial["available_ns"],
                                 reference.FIXTURE_EPOCH_NS + 64000 * reference.NS_PER_SAMPLE)

    def test_19_count_and_rate_errors_recomputed(self) -> None:
        for cases in self.report["conditions"].values():
            for case in cases.values():
                self.assertEqual(case["nuclei_count"], len(case["nuclei_intervals"]))
                self.assertEqual(case["count_abs_error"],
                                 abs(case["nuclei_count"] - case["frozen_target_count"]))
                self.assertEqual(case["rate_estimate"],
                                 str(reference.Fraction(
                                     case["nuclei_count"] * 16000, 64000)))
                self.assertFalse(case["renderer_executed"])
                self.assertFalse(case["duration_measured"])

    def test_20_specified_target_durations_are_exact_fractions(self) -> None:
        expected = {"rate_1x": "64000", "rate_0_8x": "80000", "rate_1_25x": "51200"}
        for cases in self.report["conditions"].values():
            for name, case in cases.items():
                self.assertEqual(case["target_output_samples"], expected[name])

    def test_21_unknown_frames_retained_not_counted(self) -> None:
        case = self.report["conditions"]["unfamiliar_speech"]["rate_1x"]
        self.assertGreater(case["unknown_frames"], 0)
        self.assertEqual(case["unknown_counted"], 0)
        self.assertTrue(self.report["adverse"]["validity"]["unknown_retained_not_counted"])

    def test_22_controls_present_and_identity_exact(self) -> None:
        controls = self.report["controls"]
        self.assertTrue(controls["all_present"])
        self.assertEqual(controls["identity"]["count_abs_error"], 0)
        self.assertEqual(controls["named_baseline"]["name"], "frozen_constant_count_control")

    def test_23_mismatch_control_rejects_without_state_change(self) -> None:
        mismatch = self.report["controls"]["mismatch"]
        self.assertTrue(mismatch["all_rejected"])
        self.assertTrue(mismatch["all_state_unchanged"])
        for value in mismatch["cases"].values():
            self.assertEqual(value["status"], "rejected")
            self.assertTrue(value["state_unchanged"])

    def test_24_config_rejections_are_real(self) -> None:
        for _, config in reference._invalid_configs():
            with self.assertRaises(reference.Rejected):
                reference.Surrogate(config)
        for value in self.report["adverse"]["config_rejections"].values():
            self.assertEqual(value["status"], "rejected")
            self.assertFalse(value["controller_created"])

    def test_25_frame_rejections_preserve_state(self) -> None:
        surrogate = reference.Surrogate()
        before = surrogate.state_digest()
        for _, frame in reference._invalid_frames():
            outcome = surrogate.process(frame)
            self.assertEqual(outcome["status"], "rejected")
            self.assertEqual(outcome["state_digest"], before)
        self.assertTrue(self.report["adverse"]["frame_rejections"]["dsp_state_unchanged"])

    def test_26_missing_frame_rejected_without_state_change(self) -> None:
        surrogate = reference.Surrogate()
        for frame in reference.frozen_frames("speech")[:-1]:
            self.assertEqual(surrogate.process(frame)["status"], "accepted")
        before = surrogate.state_digest()
        with self.assertRaises(reference.Rejected):
            surrogate.finish()
        self.assertEqual(surrogate.state_digest(), before)
        self.assertEqual(self.report["adverse"]["missing_frame"]["status"], "rejected")

    def test_27_lifecycle_rejections(self) -> None:
        closed = reference.Surrogate()
        closed.close()
        finished = reference.Surrogate()
        for frame in reference.frozen_frames("speech"):
            self.assertEqual(finished.process(frame)["status"], "accepted")
        finished.finish()
        frame = reference.frozen_frames("speech")[0]
        self.assertEqual(closed.process(frame)["reason"], "rejected_session")
        self.assertEqual(finished.process(frame)["reason"], "rejected_session")

    def test_28_source_reported_metrics_not_promoted(self) -> None:
        source = self.report["source_reported"]
        self.assertEqual(source["status"], "source_reported_not_reproduced")
        self.assertFalse(source["used_for_qualification"])
        values = {row["metric"]: row["value"] for row in source["findings"]}
        self.assertEqual(values["rate_mae_syllables_per_second"], 0.69)
        self.assertEqual(values["rate_pearson_r"], 0.894)

    def test_29_exact_blockers_recorded(self) -> None:
        self.assertEqual(self.report["exact_blockers"], self.contract["exact_blockers"])
        text = " ".join(self.report["exact_blockers"]).lower()
        for token in ("checkpoint", "config", "license"):
            self.assertIn(token, text)

    def test_30_all_gates_blocked(self) -> None:
        self.assertEqual([gate["name"] for gate in self.report["gates"]],
                         list(reference.GATE_NAMES))
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen_condition"])

    def test_31_repeatability_byte_identical(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)
        self.assertEqual(repeat["digests"], reference.repeatability()["digests"])

    def test_32_playback_buffering_is_fixture_only(self) -> None:
        self.assertEqual(set(self.report["playback_buffering"]), set(reference.CONDITIONS))
        for model in self.report["playback_buffering"].values():
            self.assertEqual(model["clock_id"], "fixture-monotonic-not-device")
            self.assertFalse(model["deadline_measured"])
            self.assertFalse(model["device_clock_drift_measured"])

    def test_33_no_negative_zero_or_trailing_whitespace(self) -> None:
        self.assertNotIn(b"-0.0", self.generated)
        for path in sorted(HERE.iterdir()):
            if path.is_file() and path.suffix in {".py", ".json", ".md", ".sha256", ".license"}:
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")

    def test_34_worktree_changes_are_task_local(self) -> None:
        result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                                 "--untracked-files=all"], capture_output=True, text=True,
                                check=True)
        for line in result.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(reference.TASK_PREFIX), path)

    def test_35_fresh_scratch_regeneration_is_byte_identical(self) -> None:
        interpreter = str(PYTHON) if PYTHON.is_file() else sys.executable
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        with tempfile.TemporaryDirectory(prefix="sylnet-evidence-") as scratch:
            target = Path(scratch) / "package"
            target.mkdir()
            for path in HERE.iterdir():
                if path.is_file():
                    shutil.copyfile(path, target / path.name)
            outputs = []
            for _ in range(3):
                subprocess.run([interpreter, "run.py", "all"], cwd=target,
                               capture_output=True, text=True, check=True, env=env)
                outputs.append((
                    (target / "contract.json").read_bytes(),
                    (target / "report.json").read_bytes(),
                    (target / "report.json.sha256").read_bytes(),
                    (target / "SOURCES.sha256").read_bytes(),
                ))
            self.assertEqual(len(set(outputs)), 1)
            self.assertEqual(outputs[0][0], CONTRACT.read_bytes())
            self.assertEqual(outputs[0][1], REPORT.read_bytes())
            self.assertEqual(outputs[0][2], SIDECAR.read_bytes())
            self.assertEqual(outputs[0][3], PINS.read_bytes())

    def test_36_licensing_headers_and_sidecars_present(self) -> None:
        license_line = "SPDX" "-License-Identifier: Apache-2.0"
        copyright_line = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(license_line, head, path.name)
            self.assertIn(copyright_line, head, path.name)
        for name in ("SOURCES.sha256.license", "contract.json.license",
                     "report.json.license", "report.json.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(license_line, text, name)
            self.assertIn(copyright_line, text, name)

    def test_37_upstream_source_version_and_license_pinned(self) -> None:
        prov = self.report["model_provenance"]
        self.assertEqual(prov, reference.MODEL_PROVENANCE)
        self.assertEqual(prov["upstream_repository"],
                         "https://github.com/shjang-97/SylNet")
        self.assertEqual(prov["upstream_commit"],
                         "29eb34d614907073735f9c2d8c31da22c1be2282")
        self.assertEqual(prov["upstream_license"], "MIT")
        self.assertEqual(prov["upstream_license_sha256"],
                         reference.SOURCE_PINS[reference.UPSTREAM_LICENSE_PATH])
        checkpoint = prov["checkpoint"]
        self.assertEqual(checkpoint["sha256"],
                         reference.SOURCE_PINS[reference.UPSTREAM_CHECKPOINT_PATH])
        self.assertEqual(checkpoint["bytes"], 33_806_412)
        self.assertTrue(checkpoint["tracked_in_upstream_commit"])
        self.assertFalse(checkpoint["present_in_sdk_worktree"])
        self.assertFalse(checkpoint["loaded_or_executed"])
        self.assertFalse(prov["source_snapshot_in_sdk_worktree"])
        self.assertEqual(self.contract["model_provenance"], prov)

    def test_38_licensing_analysis_keeps_rights_gate_blocked(self) -> None:
        licensing = self.report["licensing_analysis"]
        self.assertEqual(licensing, reference.LICENSING_ANALYSIS)
        self.assertEqual(licensing["task_files_license"], "Apache-2.0")
        self.assertEqual(licensing["upstream_repository_license"], "MIT")
        self.assertTrue(licensing["upstream_license_text_pinned"])
        for key in ("training_data_provenance_established",
                    "separate_weights_terms_established",
                    "redistribution_clearance", "product_use_clearance",
                    "legal_review_completed",
                    "asset_copied_vendored_built_or_downloaded"):
            self.assertIs(licensing[key], False, key)
        self.assertEqual(licensing["blocked_gate"], "exact_checkpoint_config_rights")
        self.assertEqual(self.contract["licensing_analysis"], licensing)
        gates = {gate["name"]: gate for gate in self.report["gates"]}
        self.assertEqual(gates["exact_checkpoint_config_rights"]["status"], "blocked")

    def test_39_detailed_pilot_is_provenance_only(self) -> None:
        detailed = self.report["source_reported"]["detailed_pilot"]
        self.assertEqual(detailed["status"], "source_reported_not_reproduced")
        self.assertFalse(detailed["used_for_qualification"])
        values = {row["metric"]: row["value"] for row in detailed["findings"]}
        self.assertEqual(values["rate_mae_syllables_per_second"], 0.661)
        self.assertEqual(values["rate_pearson_r"], 0.896)
        self.assertNotIn(0.661, [row["value"] for row in
                                 self.report["source_reported"]["findings"]])


if __name__ == "__main__":
    unittest.main()

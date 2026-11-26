# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the SDK-DPCRN-DNS3-TFLITE blocker package."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import reference
import scorer

HERE = Path(__file__).resolve().parent
REPORT = HERE / "report.json"
CONTRACT = HERE / "contract.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"


def _report() -> dict:
    return reference.strict_json(REPORT)


class DpcrnDns3TfliteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = _report()
        cls.contract = reference.strict_json(CONTRACT)

    def test_01_report_is_canonical_with_sidecar(self) -> None:
        payload = REPORT.read_bytes()
        self.assertEqual(payload, reference.canonical_report_bytes(self.report))
        self.assertIs(reference.contains_negative_zero(payload), False)
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual(SIDECAR.read_text(encoding="ascii"),
                         f"{digest}  report.json\n")

    def test_02_contract_is_canonical(self) -> None:
        self.assertEqual(CONTRACT.read_bytes(), reference.contract_bytes())
        self.assertIs(reference.contains_negative_zero(CONTRACT.read_bytes()), False)

    def test_03_strict_json_rejects_duplicates_and_nonfinite(self) -> None:
        for payload in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}',
                        '{"a":-Infinity}'):
            with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                             delete=False) as handle:
                handle.write(payload)
                path = Path(handle.name)
            try:
                with self.assertRaises(ValueError):
                    reference.strict_json(path)
            finally:
                path.unlink()

    def test_04_pin_parser_rejects_bad_lines(self) -> None:
        for text in (
                "not-a-line",
                "Z" * 64 + "  CONTRACTS.md",
                "a" * 64 + "  ../escape",
                "a" * 64 + "  unknown/x",
                "\n".join(["0" * 64 + "  CONTRACTS.md",
                           "0" * 64 + "  CONTRACTS.md"])):
            with self.assertRaises(ValueError, msg=text):
                reference.parse_pin_lines(text)

    def test_05_source_pins_match_files(self) -> None:
        for raw, digest in reference.SOURCE_PINS.items():
            path = reference.pin_path(raw)
            self.assertTrue(path.is_file(), raw)
            self.assertEqual(reference.sha256(path.read_bytes()), digest, raw)
        for raw, digest in reference.BOUNDARY_PINS.items():
            path = reference.pin_path(raw)
            self.assertTrue(path.is_file(), raw)
            self.assertEqual(reference.sha256(path.read_bytes()), digest, raw)

    def test_06_task_row_projection_matches_inventory(self) -> None:
        inventory = reference.strict_json(
            reference.SOURCE_ROOT / "audio-benchmark-platform/plan/INVENTORY.json")
        component = next(item for item in inventory["components"]
                         if item["id"] == reference.COMPONENT_ID)
        evidence = component["evidence"][0]
        projection = {
            "task_id": component["task"],
            "component_id": component["id"],
            "name": component["name"],
            "repository": component["repository"],
            "verification_profile": component["verification_profile"],
            "disposition": component["disposition"],
            "evidence_status": component["evidence_status"],
            "evidence_path": evidence["path"],
            "evidence_line": evidence["line"],
        }
        self.assertEqual(projection, reference.TASK_ROW_PROJECTION)
        self.assertEqual(evidence["record_name"], reference.CENSUS_RECORD_NAME)
        self.assertEqual(reference.sha256(reference.canonical_bytes(projection)),
                         reference.TASK_ROW_PROJECTION_SHA256)
        self.assertEqual(self.report["task_identity"]["row_projection"], projection)

    def test_07_mutable_task_board_is_not_pinned(self) -> None:
        for line in PINS.read_text(encoding="ascii").splitlines():
            if not line or line.startswith("#"):
                continue
            self.assertFalse(line.endswith("TASKS.json"), line)
        for path in reference.SOURCE_PINS:
            self.assertNotIn("TASKS.json", path)
        self.assertIs(self.report["task_identity"]["board_policy"]["full_tasks_json_pinned"],
                      False)

    def test_08_candidate_accounting_is_blocked_and_unverified(self) -> None:
        path = reference.SOURCE_ROOT / reference.ACCOUNTING_PATH
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        row = next(item for item in rows if item["id"] == "candidate-dpcrn-dns3")
        self.assertEqual(row["eligibility"], "blocked")
        self.assertEqual(row["weights"], reference.LOCATOR_STATUS)
        self.assertIn("pin/hash", row["reason"])
        self.assertIn("checkpoint licensing", row["reason"])
        self.assertIn("TensorFlow 1.x", row["reason"])
        self.assertIn("TFLite", row["reason"])

    def test_09_no_dpcrn_dns3_asset_or_pilot_result(self) -> None:
        ledger = reference.strict_json(
            reference.SOURCE_ROOT / "research/noise_suppression_assets_20261027.json")
        for candidate in ledger["candidates"]:
            self.assertNotIn("dpcrn-dns3", str(candidate.get("id", "")).lower())
            for artifact in candidate.get("artifacts", []):
                self.assertNotIn("dpcrn_dns3", str(artifact.get("path", "")).lower())
        pilot = (reference.SOURCE_ROOT
                 / "research/noise_suppression_pilot_20261027.md").read_text(
                     encoding="utf-8").lower()
        self.assertNotIn("dpcrn_dns3", pilot)
        self.assertNotIn("dpcrn dns3", pilot)
        self.assertNotIn("dpcrn-dns3", pilot)

    def test_10_exact_pins_are_deliberately_absent(self) -> None:
        self.assertIsNone(reference.UPSTREAM_COMMIT)
        self.assertIsNone(reference.UPSTREAM_LICENSE)
        self.assertIsNone(reference.UPSTREAM_ARTIFACT_PATH)
        self.assertIsNone(reference.UPSTREAM_ARTIFACT_SHA256)
        self.assertIsNone(reference.UPSTREAM_ARTIFACT_BYTES)
        provenance = self.report["model_provenance"]
        self.assertEqual(provenance["locator_status"], "located_unverified")
        for key in ("upstream_commit", "upstream_license"):
            self.assertIsNone(provenance[key])
        for section in ("artifact", "checkpoint"):
            for key in ("path", "bytes", "sha256", "license_terms"):
                self.assertIsNone(provenance[section][key], section + ":" + key)
        self.assertEqual(self.report["asset_boundary"]["expected_files"], [])
        self.assertIs(self.report["asset_boundary"]["admitted_artifact_descriptor_exists"],
                      False)

    def test_11_model_geometry_is_surrogate_and_unverified(self) -> None:
        geometry = self.report["model_geometry"]
        self.assertEqual(geometry["processing_mode"], "offline_whole_utterance")
        self.assertEqual(geometry["n_fft"], 512)
        self.assertEqual(geometry["hop_samples"], 256)
        self.assertEqual(geometry["stft_bins"], 257)
        self.assertEqual(geometry["surrogate_frequency_chunks"], 16)
        self.assertEqual(geometry["content_delay_samples"], 0)
        self.assertIs(geometry["real_time_causal"], False)
        self.assertIs(geometry["exact_artifact_geometry_verified"], False)
        self.assertIsNone(geometry["exact_artifact_stream_delay_samples"])
        self.assertEqual(geometry["streaming_state"], "none_offline_whole_utterance")

    def test_12_frame_count_and_output_length(self) -> None:
        for samples in (2, 255, 256, 257, 8192, 8195):
            self.assertEqual(reference.frame_count(samples), 1 + samples // 256)
            observed = [0.01 * math.sin(0.01 * index) for index in range(samples)]
            output, meta = reference.run_offline(observed)
            self.assertEqual(meta["status"], "ok")
            self.assertEqual(len(output), samples)
            self.assertEqual(meta["frames"], reference.frame_count(samples))

    def test_13_identity_reconstruction_is_exact(self) -> None:
        record = reference.identity_reconstruction()
        self.assertEqual(record, self.report["identity_reconstruction"])
        self.assertIs(record["reconstruction_exact"], True)
        self.assertLessEqual(record["max_abs_error"], 1e-12)
        self.assertIs(record["output_length_matches"], True)

    def test_14_surrogate_is_not_model_runtime_or_tflite(self) -> None:
        output, meta = reference.run_offline(reference.synth("speech")[1])
        self.assertIsNotNone(output)
        self.assertIs(meta["inference_executed"], False)
        self.assertIs(meta["model_loaded"], False)
        self.assertIs(meta["runtime_invoked"], False)
        self.assertIs(meta["asset_opened"], False)
        self.assertIs(meta["exact_artifact_geometry_verified"], False)
        self.assertEqual(meta["mode"], "offline_surrogate")
        for module in ("tensorflow", "tflite_runtime", "ai_edge_litert"):
            self.assertNotIn(module, sys.modules)

    def test_15_conditions_are_measured(self) -> None:
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for name in reference.CONDITIONS:
            case = self.report["conditions"][name]
            if name == "silence":
                continue
            self.assertEqual(case["status"], "measured_synthetic", name)
            self.assertEqual(case["offline_run"]["status"], "ok", name)
            self.assertEqual(case["offline_run"]["samples"], case["samples"], name)
            self.assertEqual(case["offline_run"]["delay_compensation_samples"], 0)
            self.assertIsNone(case["alignment"]["exact_artifact_delay_samples"], name)

    def test_16_silence_is_excluded_not_a_win(self) -> None:
        case = self.report["conditions"]["silence"]
        self.assertEqual(case["status"], "excluded_no_reference")
        self.assertIsNone(case["candidate_metrics"]["si_sdr_db"])
        self.assertIsNone(case["candidate_metrics"]["stoi"])
        self.assertEqual(case["candidate_metrics"]["peak_abs_output"], 0.0)

    def test_17_candidate_outputs_are_finite(self) -> None:
        for name in reference.CONDITIONS:
            case = self.report["conditions"][name]
            self.assertEqual(case["candidate_metrics"]["nonfinite_count"], 0, name)
            if name != "silence":
                self.assertIsNotNone(case["candidate_metrics"]["peak_abs_output"], name)

    def test_18_controls_are_present(self) -> None:
        controls = self.report["controls"]
        self.assertIs(controls["all_present"], True)
        self.assertEqual(controls["identity"]["name"], "identity_no_processing")
        self.assertEqual(controls["named_baseline"]["name"], "noisy_input_no_processing")
        for name in ("identity", "named_baseline", "candidate"):
            self.assertEqual(controls[name]["metrics"]["status"],
                             "measured_synthetic", name)
        self.assertEqual(controls["clean_speech_preservation"]["metrics"]["status"],
                         "measured_synthetic")

    def test_19_clean_preservation_is_reported_with_baseline(self) -> None:
        clean = self.report["controls"]["clean_speech_preservation"]
        self.assertIn("baseline_metrics", clean)
        self.assertIsNotNone(clean["baseline_metrics"]["si_sdr_db"])
        self.assertIsNotNone(clean["metrics"]["si_sdr_db"])

    def test_20_invalid_configs_are_rejected(self) -> None:
        waveform = reference.synth("speech")[1]
        for name, config in reference._invalid_configs():
            output, meta = reference.run_offline(waveform, config)
            self.assertIsNone(output, name)
            self.assertTrue(meta["status"].startswith("rejected"), name)
            self.assertIs(meta["inference_executed"], False, name)

    def test_21_invalid_signals_are_rejected(self) -> None:
        for name, signal in reference._invalid_signals():
            output, meta = reference.run_offline(signal)
            self.assertIsNone(output, name)
            self.assertTrue(meta["status"].startswith("rejected"), name)
            self.assertIs(meta["model_loaded"], False, name)
            self.assertIs(meta["asset_opened"], False, name)

    def test_22_real_path_fails_closed_without_fallback(self) -> None:
        waveform = reference.synth("speech")[1]
        output, meta = reference.run_offline(
            waveform, {"mode": reference.REAL_MODE,
                       "asset": reference.ASSET_REFERENCE})
        self.assertIsNone(output)
        self.assertEqual(meta["status"], "rejected_unpinned_artifact")
        self.assertIs(meta["runtime_invoked"], False)
        self.assertIs(meta["asset_opened"], False)

    def test_23_artifact_gate_cases_fail_closed(self) -> None:
        adverse = self.report["adverse"]
        expected = {
            "absent": "blocked_asset_absent",
            "malformed_not_dict": "blocked_invalid_request",
            "missing_key": "blocked_invalid_request",
            "wrong_repository": "blocked_wrong_repository",
            "wrong_geometry": "blocked_wrong_geometry",
            "wrong_runtime": "blocked_runtime_unavailable",
            "missing_files": "blocked_invalid_request",
            "bad_hash_format": "blocked_invalid_request",
            "bad_size": "blocked_invalid_request",
            "duplicate_file": "blocked_duplicate_file",
            "path_traversal": "blocked_invalid_request",
            "runtime_unavailable": "blocked_runtime_unavailable",
            "fabricated_pins": "blocked_unpinned_artifact",
        }
        self.assertEqual(set(adverse["asset_gate"]), set(expected))
        for name, reason in expected.items():
            self.assertEqual(adverse["asset_gate"][name]["status"], "blocked", name)
            self.assertEqual(adverse["asset_gate"][name]["reason"], reason, name)
            self.assertIs(adverse["asset_gate"][name]["artifact_opened"], False, name)
            self.assertIs(adverse["asset_gate"][name]["download_attempted"], False, name)

    def test_24_there_is_no_fabricated_positive_control(self) -> None:
        gate = self.report["caller_supplied_artifact_gate"]
        self.assertIsNone(gate["positive_control"])
        self.assertEqual(gate["positive_control_status"], "unavailable_no_canonical_pins")
        self.assertIsNone(self.report["adverse"]["asset_gate_control"])

    def test_25_fabricated_request_is_blocked(self) -> None:
        rejected = reference.validate_asset_request(
            reference._asset_request(), asset_present=True, runtime_available=True)
        self.assertEqual(rejected["status"], "blocked")
        self.assertEqual(rejected["reason"], "blocked_unpinned_artifact")
        self.assertEqual(set(rejected["reason_codes"]),
                         set(reference.ARTIFACT_REQUIREMENT["unresolved_fields"]))

    def test_26_report_disposition(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["status"],
                         "proposal_only_synthetic_blocker_incomplete")
        self.assertEqual(self.report["task_mode"], "feasibility")
        self.assertEqual(self.report["defer_before"], "artifact_admission")
        self.assertIs(self.report["no_missing_result_qualifies_candidate"], True)
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertIs(qualification["qualifies"], False)
        self.assertIs(qualification["proposal_only"], True)
        self.assertIs(qualification["incomplete"], True)
        self.assertIs(qualification["real_runtime_used"], False)
        self.assertIs(qualification["real_model_used"], False)

    def test_27_boundary_and_scope_are_unchanged(self) -> None:
        for key, value in self.report["boundary"].items():
            if key == "descriptor_settings":
                self.assertEqual(value, {})
            elif key == "installed_v0_geometry_preserved":
                self.assertIs(value, True, key)
            else:
                self.assertIs(value, False, key)
        for key, value in self.report["scope"].items():
            self.assertIs(value, False, key)
        for key, value in self.report["negative_claims"].items():
            self.assertIs(value, False, key)

    def test_28_rights_gap_is_blocked(self) -> None:
        rights = self.report["rights_gap"]
        self.assertIs(rights["blocked"], True)
        self.assertIs(rights["exact_upstream_source_verified"], False)
        self.assertIs(rights["model_weight_terms_verified"], False)
        self.assertIs(rights["training_data_provenance_verified"], False)
        self.assertIs(rights["tflite_redistribution_terms_verified"], False)
        licensing = self.report["licensing_analysis"]
        self.assertEqual(licensing["blocked_gate"],
                         "weight_runtime_and_training_data_rights_cleared")
        self.assertIsNone(licensing["upstream_code_license"])
        self.assertIs(licensing["asset_copied_vendored_built_or_downloaded"], False)

    def test_29_readiness_is_strict(self) -> None:
        readiness = self.report["readiness"]
        self.assertEqual(readiness["conclusion"], "not_ready")
        self.assertEqual(readiness["decision"], "DEFER")
        for key in ("artifact_available", "exact_artifact_identity_pinned",
                    "runtime_available", "rights_cleared"):
            self.assertIs(readiness[key], False, key)
        self.assertIs(readiness["synthetic_surrogate_only"], True)
        self.assertGreaterEqual(len(readiness["exact_external_blocker"].split()), 12)
        self.assertGreaterEqual(len(readiness["reopen_condition"].split()), 12)

    def test_30_all_eight_gates_are_blocked(self) -> None:
        self.assertEqual(len(self.report["gates"]), 8)
        self.assertEqual([item["name"] for item in self.report["gates"]],
                         list(reference.GATE_NAMES))
        for item in self.report["gates"]:
            self.assertEqual(item["status"], "blocked", item["name"])
            self.assertTrue(item["reopen_condition"], item["name"])
        self.assertEqual(len(self.contract["gates"]), 8)
        self.assertEqual(self.contract["gates"], reference.gates())

    def test_31_prior_pilot_and_timing_are_absent_provenance(self) -> None:
        prior = self.report["prior_pilot_provenance"]
        self.assertEqual(prior["status"], "not_available")
        self.assertIs(prior["measured_here"], False)
        self.assertIs(prior["used_for_qualification"], False)
        self.assertEqual(prior["reported"], {})
        timing = self.report["independent_timing_evidence"]
        self.assertIs(timing["used_for_qualification"], False)
        self.assertIs(timing["target_device"], False)
        self.assertEqual(timing["reported"], {})
        related = self.report["related_models_not_pooled"]
        self.assertIs(related["metrics_used_for_qualification"], False)

    def test_32_three_cold_start_passes(self) -> None:
        code = ("import sys; sys.path.insert(0, " + repr(str(HERE)) + "); "
                "import reference; sys.stdout.write("
                "reference.sha256(reference.canonical_report_bytes(reference.build_report())))")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        digests = []
        for _ in range(3):
            result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                    capture_output=True, text=True, check=True)
            digests.append(result.stdout.strip())
        self.assertEqual(len(set(digests)), 1)
        self.assertEqual(digests[0], hashlib.sha256(REPORT.read_bytes()).hexdigest())
        self.assertEqual(self.report["repeatability"], reference.repeatability())
        self.assertNotEqual(digests[0], self.report["repeatability"]["digests"][0])

    def test_33_readme_digest_table_matches_committed_files(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        rows = reference.readme_artifact_digests(text)
        self.assertEqual(set(rows), set(reference.README_ARTIFACT_FILES))
        for name, digest in rows.items():
            self.assertEqual(digest, reference.sha256((HERE / name).read_bytes()), name)

    def test_34_readme_gate_list_matches_contract(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        items = reference.readme_gate_items(text)
        self.assertEqual(len(items), 8)
        for index, (name, item) in enumerate(zip(reference.GATE_NAMES, items), start=1):
            self.assertTrue(item.startswith(f"{index}. `{name}`"), item)

    def test_35_readme_parsers_fail_closed(self) -> None:
        bad_digest = (
            reference.README_DIGEST_SECTION + "\n\n"
            "| File | SHA-256 |\n| --- | --- |\n"
            "| `report.json` | `" + "a" * 64 + "` |\n"
            "| malformed | row |\n")
        with self.assertRaises(ValueError):
            reference.readme_artifact_digests(bad_digest)
        duplicate = (
            reference.README_DIGEST_SECTION + "\n\n"
            "| `report.json` | `" + "a" * 64 + "` |\n"
            "| `report.json` | `" + "b" * 64 + "` |\n")
        with self.assertRaises(ValueError):
            reference.readme_artifact_digests(duplicate)
        bad_gates = reference.README_GATES_SECTION + "\n\n1. one\n3. three\n"
        with self.assertRaises(ValueError):
            reference.readme_gate_items(bad_gates)

    def test_36_license_sidecars(self) -> None:
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license", "SOURCES.sha256.license"):
            self.assertEqual((HERE / name).read_text(encoding="utf-8"),
                             reference.LICENSE_TEXT, name)

    def test_37_scorer_is_pinned_port(self) -> None:
        prior = (reference.SDK_ROOT
                 / "docs/task-evidence/online-multichannel-wpe/scorer.py")
        expected = prior.read_text(encoding="utf-8").replace(
            'SCORER_ID = "audio-sdk/online-multichannel-wpe-scoring/0.1"',
            f'SCORER_ID = "{scorer.SCORER_ID}"')
        self.assertEqual((HERE / "scorer.py").read_text(encoding="utf-8"), expected)
        self.assertEqual(self.report["scorer"]["scorer_id"], scorer.SCORER_ID)
        self.assertIs(self.report["scorer"]["used_as_oracle"], False)

    def test_38_interpreter_is_pinned(self) -> None:
        self.assertTrue(reference.interpreter_is_pinned(), sys.version)
        for module in ("tensorflow", "tflite_runtime", "ai_edge_litert"):
            self.assertIsNone(importlib.util.find_spec(module), module)

    def test_39_contract_and_report_pins_agree(self) -> None:
        self.assertEqual(self.report["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(self.report["boundary_pins"], reference.BOUNDARY_PINS)
        self.assertEqual(self.report["artifact_pins"],
                         reference.report_artifact_pins())
        self.assertEqual(self.contract["artifact_pins"],
                         reference.base_artifact_pins())
        self.assertEqual(self.report["contract_sha256"],
                         reference.sha256(reference.contract_bytes()))
        self.assertEqual(self.contract["task_identity"],
                         self.report["task_identity"])

    def test_40_adverse_and_valid_signal(self) -> None:
        adverse = self.report["adverse"]
        self.assertIs(adverse["all_rejected"], True)
        self.assertIs(adverse["all_outputs_finite"], True)
        self.assertEqual(adverse["valid_signal"]["status"], "ok")
        self.assertEqual(adverse["lifecycle"]["valid_run"], "ok")
        self.assertEqual(adverse["lifecycle"]["real_mode"],
                         "rejected_unpinned_artifact")

    def test_41_regressions_are_verbatim(self) -> None:
        self.assertEqual(self.report["regressions"],
                         reference.regressions(self.report["conditions"]))
        for row in self.report["regressions"]:
            self.assertIn(row["condition"], reference.CONDITIONS)
            self.assertTrue(row["si_sdr_delta_db"] < 0.0
                            or row["stoi_delta"] < 0.0)

    def test_42_surrogate_limitations_are_explicit(self) -> None:
        limitations = " ".join(self.report["surrogate_limitations"]).lower()
        for token in ("not dpcrn", "no convolutions", "not speech",
                      "not verified", "no tflite"):
            self.assertIn(token, limitations)
        self.assertEqual(self.report["surrogate_parameters"]["frequency_chunks"], 16)
        self.assertIs(self.report["surrogate_parameters"]["learned_weights"], False)
        self.assertIs(self.report["surrogate_parameters"]["tflite_invoked"], False)


if __name__ == "__main__":
    unittest.main()

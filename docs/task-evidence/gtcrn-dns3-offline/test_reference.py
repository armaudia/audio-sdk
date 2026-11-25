# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the SDK-GTCRN-DNS3-OFFLINE evidence package."""

from __future__ import annotations

import hashlib
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


def _report() -> dict:
    return reference.strict_json(REPORT)


class GtcrnDns3OfflineTests(unittest.TestCase):
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

    def test_03_manifests_are_canonical(self) -> None:
        for name, builder in (("adapter.json", reference.adapter),
                              ("provider.json", reference.provider),
                              ("asset.json", reference.asset)):
            self.assertEqual((HERE / name).read_bytes(),
                             reference.canonical_bytes(builder()) + b"\n", name)

    def test_04_strict_json_rejects_duplicates_and_nonfinite(self) -> None:
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

    def test_05_pin_parser_rejects_bad_lines(self) -> None:
        for text in (
                "not-a-line",
                "Z" * 64 + "  CONTRACTS.md",
                "a" * 64 + "  ../escape",
                "a" * 64 + "  unknown/x",
                "\n".join(["0" * 64 + "  CONTRACTS.md",
                           "0" * 64 + "  CONTRACTS.md"])):
            with self.assertRaises(ValueError, msg=text):
                reference.parse_pin_lines(text)

    def test_06_source_pins_match_files(self) -> None:
        for raw, digest in reference.SOURCE_PINS.items():
            path = reference.pin_path(raw)
            self.assertTrue(path.is_file(), raw)
            self.assertEqual(reference.sha256(path.read_bytes()), digest, raw)

    def test_07_asset_pins_match_ledger(self) -> None:
        ledger = reference.strict_json(
            reference.SOURCE_ROOT / "research/noise_suppression_assets_20261027.json")
        candidate = next(item for item in ledger["candidates"]
                         if item["id"] == "GTCRN-DNS3")
        artifacts = {item["path"]: item for item in candidate["artifacts"]}
        for expected in reference.EXPECTED_ASSET_FILES:
            path = f"{reference.UPSTREAM_SNAPSHOT}/{expected['path']}"
            self.assertEqual(artifacts[path]["sha256"], expected["sha256"], path)
            self.assertEqual(artifacts[path]["bytes"], expected["bytes"], path)
        self.assertEqual(candidate["source_revision"], reference.UPSTREAM_COMMIT)
        self.assertNotIn("model_license", candidate)
        self.assertNotIn("model_terms", candidate)

    def test_08_model_geometry(self) -> None:
        geometry = self.report["model_geometry"]
        self.assertEqual(geometry["processing_mode"], "offline_whole_utterance")
        self.assertEqual(geometry["n_fft"], 512)
        self.assertEqual(geometry["hop_samples"], 256)
        self.assertEqual(geometry["stft_bins"], 257)
        self.assertEqual(geometry["content_delay_samples"], 0)
        self.assertIs(geometry["real_time_causal"], False)
        self.assertEqual(geometry["streaming_state"], "none_offline_whole_utterance")

    def test_09_frame_count_and_output_length(self) -> None:
        for samples in (2, 255, 256, 257, 9728, 9819):
            self.assertEqual(reference.frame_count(samples), 1 + samples // 256)
            observed = [0.01 * math.sin(0.01 * index) for index in range(samples)]
            output, meta = reference.run_offline(observed)
            self.assertEqual(meta["status"], "ok")
            self.assertEqual(len(output), samples)
            self.assertEqual(meta["frames"], reference.frame_count(samples))

    def test_10_identity_reconstruction_is_exact(self) -> None:
        record = reference.identity_reconstruction()
        self.assertEqual(record, self.report["identity_reconstruction"])
        self.assertIs(record["reconstruction_exact"], True)
        self.assertLessEqual(record["max_abs_error"], 1e-12)
        self.assertIs(record["output_length_matches"], True)

    def test_11_surrogate_is_not_model_or_runtime(self) -> None:
        output, meta = reference.run_offline(reference.synth("speech")[1])
        self.assertIsNotNone(output)
        self.assertIs(meta["inference_executed"], False)
        self.assertIs(meta["model_loaded"], False)
        self.assertIs(meta["runtime_invoked"], False)
        self.assertEqual(meta["mode"], "offline_surrogate")
        self.assertNotIn("torch", sys.modules)

    def test_12_conditions_are_measured(self) -> None:
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for name in reference.CONDITIONS:
            case = self.report["conditions"][name]
            if name == "silence":
                continue
            self.assertEqual(case["status"], "measured_synthetic", name)
            self.assertEqual(case["offline_run"]["status"], "ok", name)
            self.assertEqual(case["offline_run"]["samples"], case["samples"], name)
            self.assertEqual(case["offline_run"]["delay_compensation_samples"], 0)

    def test_13_silence_is_excluded_not_a_win(self) -> None:
        case = self.report["conditions"]["silence"]
        self.assertEqual(case["status"], "excluded_no_reference")
        self.assertIsNone(case["candidate_metrics"]["si_sdr_db"])
        self.assertIsNone(case["candidate_metrics"]["stoi"])
        self.assertEqual(case["candidate_metrics"]["peak_abs_output"], 0.0)

    def test_14_candidate_outputs_are_finite(self) -> None:
        for name in reference.CONDITIONS:
            case = self.report["conditions"][name]
            self.assertEqual(case["candidate_metrics"]["nonfinite_count"], 0, name)
            if name != "silence":
                self.assertIsNotNone(case["candidate_metrics"]["peak_abs_output"], name)

    def test_15_controls_are_present(self) -> None:
        controls = self.report["controls"]
        self.assertIs(controls["all_present"], True)
        self.assertEqual(controls["identity"]["name"], "identity_no_processing")
        self.assertEqual(controls["named_baseline"]["name"], "noisy_input_no_processing")
        for name in ("identity", "named_baseline", "candidate"):
            self.assertEqual(controls[name]["metrics"]["status"],
                             "measured_synthetic", name)
        self.assertEqual(controls["clean_speech_preservation"]["metrics"]["status"],
                         "measured_synthetic")

    def test_16_clean_preservation_is_reported_with_baseline(self) -> None:
        clean = self.report["controls"]["clean_speech_preservation"]
        self.assertIn("baseline_metrics", clean)
        self.assertIsNotNone(clean["baseline_metrics"]["si_sdr_db"])
        self.assertIsNotNone(clean["metrics"]["si_sdr_db"])

    def test_17_invalid_configs_are_rejected(self) -> None:
        waveform = reference.synth("speech")[1]
        for name, config in reference._invalid_configs():
            output, meta = reference.run_offline(waveform, config)
            self.assertIsNone(output, name)
            self.assertTrue(meta["status"].startswith("rejected"), name)
            self.assertIs(meta["inference_executed"], False, name)

    def test_18_invalid_signals_are_rejected(self) -> None:
        for name, signal in reference._invalid_signals():
            output, meta = reference.run_offline(signal)
            self.assertIsNone(output, name)
            self.assertTrue(meta["status"].startswith("rejected"), name)
            self.assertIs(meta["model_loaded"], False, name)

    def test_19_real_path_fails_closed_without_fallback(self) -> None:
        waveform = reference.synth("speech")[1]
        output, meta = reference.run_offline(
            waveform, {"mode": reference.REAL_MODE,
                       "asset": reference.ASSET_REFERENCE})
        self.assertIsNone(output)
        self.assertEqual(meta["status"], "rejected_asset_unavailable")
        self.assertIs(meta["runtime_invoked"], False)

    def test_20_asset_gate_cases_fail_closed(self) -> None:
        adverse = self.report["adverse"]
        expected = {
            "absent": "blocked_asset_absent",
            "hash_mismatch": "blocked_hash_mismatch",
            "size_mismatch": "blocked_size_mismatch",
            "wrong_commit": "blocked_wrong_commit",
            "wrong_geometry": "blocked_wrong_geometry",
            "one_file": "blocked_wrong_file_count",
            "unknown_key": "blocked_invalid_request",
            "wrong_runtime": "blocked_runtime_unavailable",
            "runtime_unavailable": "blocked_runtime_unavailable",
        }
        self.assertEqual(set(adverse["asset_gate"]), set(expected))
        for name, reason in expected.items():
            self.assertEqual(adverse["asset_gate"][name]["status"], "blocked", name)
            self.assertEqual(adverse["asset_gate"][name]["reason"], reason, name)
            self.assertIs(adverse["asset_gate"][name]["asset_opened"], False, name)

    def test_21_asset_gate_positive_control_never_infers(self) -> None:
        control = self.report["adverse"]["asset_gate_control"]
        self.assertEqual(control["status"], "ready_for_caller_execution")
        self.assertIs(control["inference_executed"], False)
        self.assertIs(control["asset_opened"], False)

    def test_22_report_disposition(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["defer_before"], "provider_registration")
        self.assertIs(self.report["no_missing_result_qualifies_candidate"], True)

    def test_23_boundary_and_scope_are_unchanged(self) -> None:
        for key, value in self.report["boundary"].items():
            if key == "descriptor_settings":
                self.assertEqual(value, {})
            elif key in ("evaluation_path", "production_callback_path"):
                self.assertIsInstance(value, str)
            elif key in ("installed_v0_geometry_preserved", "real_asset_required"):
                self.assertIs(value, True, key)
            else:
                self.assertIs(value, False, key)
        for key, value in self.report["scope"].items():
            self.assertIs(value, False, key)
        for key, value in self.report["negative_claims"].items():
            self.assertIs(value, False, key)

    def test_24_rights_gap_is_blocked(self) -> None:
        rights = self.report["rights_gap"]
        self.assertIs(rights["blocked"], True)
        self.assertIs(rights["model_weight_terms_verified"], False)
        self.assertIs(rights["training_data_provenance_verified"], False)
        self.assertIs(rights["torch_redistribution_terms_verified"], False)
        licensing = self.report["licensing_analysis"]
        self.assertEqual(licensing["blocked_gate"], "weight_and_runtime_rights_cleared")
        self.assertIs(licensing["asset_copied_vendored_built_or_downloaded"], False)

    def test_25_readiness_is_strict(self) -> None:
        readiness = self.report["readiness"]
        self.assertEqual(readiness["conclusion"], "not_ready")
        self.assertEqual(readiness["decision"], "DEFER")
        for key in ("asset_available", "runtime_available", "rights_cleared"):
            self.assertIs(readiness[key], False, key)
        self.assertIs(readiness["synthetic_surrogate_only"], True)
        self.assertGreaterEqual(len(readiness["exact_external_blocker"].split()), 12)
        self.assertGreaterEqual(len(readiness["reopen_condition"].split()), 12)

    def test_26_all_seven_gates_are_blocked(self) -> None:
        self.assertEqual(len(self.report["gates"]), 7)
        self.assertEqual([item["name"] for item in self.report["gates"]],
                         list(reference.GATE_NAMES))
        for item in self.report["gates"]:
            self.assertEqual(item["status"], "blocked", item["name"])
            self.assertTrue(item["reopen_condition"], item["name"])
        self.assertEqual(self.contract["gates"], list(reference.GATE_NAMES))

    def test_27_prior_pilot_is_provenance_not_qualification(self) -> None:
        prior = self.report["prior_pilot_provenance"]
        self.assertEqual(prior["status"], "source_reported_not_reproduced")
        self.assertIs(prior["measured_here"], False)
        self.assertIs(prior["used_for_qualification"], False)
        self.assertEqual(prior["reported"]["median_snr_gain_db"], 5.381)
        self.assertEqual(prior["reported"]["median_stoi"], 0.9484)
        timing = self.report["independent_timing_evidence"]
        self.assertIs(timing["used_for_qualification"], False)
        self.assertIs(timing["target_device"], False)

    def test_28_three_cold_start_passes(self) -> None:
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

    def test_29_readme_digest_table_matches_committed_files(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        rows = reference.readme_artifact_digests(text)
        self.assertEqual(set(rows), set(reference.README_ARTIFACT_FILES))
        for name, digest in rows.items():
            self.assertEqual(digest, reference.sha256((HERE / name).read_bytes()), name)

    def test_30_readme_gate_list_matches_contract(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        items = reference.readme_gate_items(text)
        self.assertEqual(len(items), len(reference.GATE_NAMES))
        for name, item in zip(reference.GATE_NAMES, items):
            self.assertTrue(item.startswith(f"{reference.GATE_NAMES.index(name) + 1}. `{name}`"), item)

    def test_31_readme_parsers_fail_closed(self) -> None:
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

    def test_32_license_sidecars(self) -> None:
        for name in ("contract.json.license", "adapter.json.license",
                     "provider.json.license", "asset.json.license",
                     "report.json.license", "report.json.sha256.license",
                     "SOURCES.sha256.license"):
            self.assertEqual((HERE / name).read_text(encoding="utf-8"),
                             reference.LICENSE_TEXT, name)

    def test_33_scorer_is_pinned_port(self) -> None:
        prior = (reference.SDK_ROOT
                 / "docs/task-evidence/online-multichannel-wpe/scorer.py")
        expected = prior.read_text(encoding="utf-8").replace(
            'SCORER_ID = "audio-sdk/online-multichannel-wpe-scoring/0.1"',
            f'SCORER_ID = "{scorer.SCORER_ID}"')
        self.assertEqual((HERE / "scorer.py").read_text(encoding="utf-8"), expected)
        self.assertEqual(self.report["scorer"]["scorer_id"], scorer.SCORER_ID)
        self.assertIs(self.report["scorer"]["used_as_oracle"], False)

    def test_34_interpreter_is_pinned(self) -> None:
        self.assertTrue(reference.interpreter_is_pinned(), sys.version)

    def test_35_contract_and_report_pins_agree(self) -> None:
        self.assertEqual(self.report["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(self.report["boundary_pins"], reference.BOUNDARY_PINS)
        self.assertEqual(self.report["asset_pins"], reference.ASSET_PINS)
        self.assertEqual(self.report["artifact_pins"],
                         reference.report_artifact_pins())
        self.assertEqual(self.contract["artifact_pins"],
                         reference.base_artifact_pins())
        self.assertEqual(self.report["contract_sha256"],
                         reference.sha256(reference.contract_bytes()))

    def test_36_adverse_and_valid_signal(self) -> None:
        adverse = self.report["adverse"]
        self.assertIs(adverse["all_rejected"], True)
        self.assertIs(adverse["all_outputs_finite"], True)
        self.assertEqual(adverse["valid_signal"]["status"], "ok")
        self.assertEqual(adverse["lifecycle"]["valid_run"], "ok")
        self.assertEqual(adverse["lifecycle"]["real_mode"],
                         "rejected_asset_unavailable")

    def test_37_regressions_are_verbatim(self) -> None:
        self.assertEqual(self.report["regressions"],
                         reference.regressions(self.report["conditions"]))
        for row in self.report["regressions"]:
            self.assertIn(row["condition"], reference.CONDITIONS)
            self.assertTrue(row["si_sdr_delta_db"] < 0.0
                            or row["stoi_delta"] < 0.0)

    def test_38_surrogate_limitations_are_explicit(self) -> None:
        limitations = " ".join(self.report["surrogate_limitations"]).lower()
        for token in ("not the gtcrn", "no learned weights", "not speech",
                      "no device clock"):
            self.assertIn(token, limitations)
        self.assertNotIn("torch", sys.modules)


if __name__ == "__main__":
    unittest.main()

# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the SDK-DTLN-ONNX task-local evidence package."""

from __future__ import annotations

import hashlib
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
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
REQUIRED_KEYS = {
    "schema_id", "task_id", "title", "component_id", "base_commit", "branch",
    "profile", "status", "evidence_status", "qualification_status", "decision",
    "defer_before", "no_missing_result_qualifies_candidate", "scope",
    "negative_claims", "boundary", "format", "stream", "contract_id",
    "contract_sha256", "source_pins", "boundary_pins", "scorer_pins",
    "model_provenance", "caller_supplied_asset_gate", "licensing_analysis",
    "tool_provenance", "surrogate", "acceptance_profile", "conditions",
    "controls", "adverse", "regressions", "source_reported", "exact_blockers",
    "gates", "missing_evidence", "evidence_classes", "repeatability",
}


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.strict_json(REPORT)
        cls.contract = reference.strict_json(CONTRACT)
        cls.generated = reference.canonical_report_bytes(reference.build_report())

    def test_01_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_text(encoding="utf-8"), f"{digest}  report.json\n")

    def test_03_status_and_qualification(self) -> None:
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_04_boundary_is_fail_closed(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration",
                    "descriptor_registry_change", "shared_cmakelists_change",
                    "installed_v0_behavior_change", "processor_exposure", "ci_change"):
            self.assertIs(boundary[key], False)
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_05_installed_v0_and_reference_geometry(self) -> None:
        fmt = self.report["format"]
        self.assertEqual(fmt["sample_rate_hz"], 16000)
        self.assertEqual(fmt["channels"], 1)
        self.assertEqual(fmt["sample_format"], "f32")
        self.assertEqual(fmt["frame_samples"], 160)
        self.assertEqual(fmt["hop_samples"], 160)
        self.assertEqual(fmt["content_delay_samples"], 0)
        self.assertIs(fmt["public_v0_geometry_preserved"], True)
        stream = self.report["stream"]
        self.assertEqual((stream["block_samples"], stream["hop_samples"]), (512, 128))
        self.assertEqual(stream["delay_samples"], 384)
        self.assertEqual(stream["delay_hops"], 3)
        self.assertEqual(stream["magnitude_bins"], 257)
        self.assertIs(stream["installed_v0_behavior_changed"], False)

    def test_06_required_keys_present(self) -> None:
        self.assertFalse(REQUIRED_KEYS - set(self.report))

    def test_07_identity_and_pins(self) -> None:
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["component_id"], "dtln-onnx")
        self.assertEqual(self.report["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(self.report["boundary_pins"], reference.BOUNDARY_PINS)
        self.assertEqual(self.report["scorer_pins"], reference.SCORER_PINS)
        self.assertEqual(self.report["contract_sha256"],
                         reference.sha256(reference.contract_bytes()))

    def test_08_all_conditions_present_and_scored(self) -> None:
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for name, case in self.report["conditions"].items():
            if name == "silence":
                self.assertEqual(case["status"], "excluded_no_reference")
                self.assertEqual(case["candidate_metrics"]["status"], "excluded")
                self.assertIsNone(case["candidate_metrics"]["si_sdr_db"])
                continue
            self.assertEqual(case["status"], "measured_synthetic")
            for key in ("baseline_metrics", "candidate_metrics",
                        "candidate_raw_metrics", "frame_run"):
                self.assertIn(key, case)
            self.assertEqual(case["candidate_metrics"]["nonfinite_count"], 0)
            self.assertLessEqual(case["candidate_metrics"]["peak_abs_output"], 1.0)

    def test_09_tail_partial_exact_coordinates(self) -> None:
        case = self.report["conditions"]["tail_partial"]
        self.assertEqual(case["samples"], 15323)
        run = case["frame_run"]
        self.assertEqual(run["final_hop"], {
            "source": [15232, 15323], "valid_count": 91,
            "padded_count": 37, "final_flag": True,
        })
        self.assertEqual(run["padded_samples"], 37)

    def test_10_delay_alignment_and_raw_control(self) -> None:
        for name in ("speech", "unfamiliar_speech", "music", "clipped", "tail_partial"):
            case = self.report["conditions"][name]
            self.assertEqual(case["delay_compensation_samples"], 384)
            self.assertLess(case["candidate_raw_metrics"]["si_sdr_db"],
                            case["candidate_metrics"]["si_sdr_db"])

    def test_11_controls_all_present(self) -> None:
        controls = self.report["controls"]
        self.assertTrue(controls["all_present"])
        self.assertEqual(controls["identity"]["name"], "identity_no_processing")
        self.assertEqual(controls["named_baseline"]["name"], "noisy_input_no_processing")
        self.assertEqual(controls["candidate"]["metrics"]["status"], "measured_synthetic")
        self.assertEqual(controls["clean_speech_preservation"]["metrics"]["status"],
                         "measured_synthetic")
        self.assertTrue(controls["mismatch"]["all_rejected"])
        self.assertTrue(controls["mismatch"]["all_state_unchanged"])

    def test_12_adverse_cases_fail_closed(self) -> None:
        adverse = self.report["adverse"]
        self.assertTrue(adverse["all_rejected"])
        for value in adverse["config_rejections"].values():
            self.assertTrue(value["status"].startswith("rejected"))
            self.assertFalse(value["controller_created"])
        for name, value in adverse["frame_rejections"].items():
            if name != "dsp_state_unchanged":
                self.assertTrue(value["status"].startswith("rejected"), name)
                self.assertTrue(value["state_unchanged"], name)
        self.assertIs(adverse["frame_rejections"]["dsp_state_unchanged"], True)
        for name, value in adverse["lifecycle"].items():
            if name == "valid_reset":
                self.assertEqual(value, "ok")
            else:
                self.assertEqual(value["status"], "rejected", name)

    def test_13_asset_gate_is_blocked_and_never_executes(self) -> None:
        gate = self.report["caller_supplied_asset_gate"]
        self.assertEqual(gate["status"], "blocked")
        self.assertIs(gate["inference_executed"], False)
        self.assertIs(gate["onnxruntime_importable"], False)
        self.assertEqual(gate["validation"]["reason"], "blocked_runtime_unavailable")
        self.assertIs(gate["asset_root_in_sdk_worktree"], False)
        self.assertEqual(len(gate["required_graphs"]), 2)
        for graph in gate["required_graphs"]:
            self.assertFalse(graph["path"].startswith("docs/"))
            self.assertEqual(len(graph["sha256"]), 64)

    def test_14_asset_gate_rejects_invalid_requests(self) -> None:
        real = lambda relative: (reference.SOURCE_ROOT / reference.UPSTREAM_SNAPSHOT
                                 / relative).read_bytes()
        base = reference._asset_request()
        self.assertEqual(reference.validate_asset_request(base)["reason"],
                         "blocked_asset_absent")
        cases = {
            "wrong_commit": reference._asset_request(source_commit="0" * 40),
            "wrong_geometry": reference._asset_request(hop_samples=160),
            "one_graph": reference._asset_request(graphs=base["graphs"][:1]),
            "duplicate": reference._asset_request(graphs=[base["graphs"][0]] * 2),
            "unknown_key": {**base, "extra": True},
            "bad_runtime": reference._asset_request(
                runtime={**base["runtime"], "version": "9.9.9"}),
        }
        for name, request in cases.items():
            outcome = reference.validate_asset_request(request, real)
            self.assertEqual(outcome["status"], "rejected", name)
        fake = lambda relative: b"z" * (
            reference.ASSET_SPECS[0]["bytes"] if "model_1" in relative
            else reference.ASSET_SPECS[1]["bytes"])
        self.assertEqual(reference.validate_asset_request(base, fake)["reason"],
                         "blocked_hash_mismatch")
        self.assertEqual(reference.validate_asset_request(base, real)["reason"],
                         "blocked_runtime_unavailable")
        ready = reference._asset_request(interpreter="3.10")
        ready["runtime"] = dict(ready["runtime"], available=True)
        self.assertEqual(reference.validate_asset_request(ready, real)["status"],
                         "ready_for_caller_execution")

    def test_15_repeatability_is_byte_identical(self) -> None:
        repeats = self.report["repeatability"]
        self.assertEqual(repeats["count"], 3)
        self.assertTrue(repeats["byte_identical"])
        self.assertEqual(len(set(repeats["digests"])), 1)

    def test_16_regressions_recorded_verbatim(self) -> None:
        self.assertIsInstance(self.report["regressions"], list)
        self.assertTrue(any(row["metric"] == "raw_lag_penalty_db"
                            for row in self.report["regressions"]))
        self.assertTrue(any(row["metric"] == "score_undefined"
                            for row in self.report["regressions"]))
        for item in self.report["regressions"]:
            self.assertIn("condition", item)
            self.assertIn("candidate", item)
            self.assertIn("baseline", item)

    def test_17_gates_and_blockers_are_blocked(self) -> None:
        self.assertTrue(self.report["gates"])
        self.assertTrue(all(gate["status"] == "blocked" for gate in self.report["gates"]))
        self.assertEqual({gate["name"] for gate in self.report["gates"]},
                         set(reference.GATE_NAMES))
        self.assertEqual(self.report["exact_blockers"], self.contract["exact_blockers"])
        self.assertEqual(len(self.report["exact_blockers"]), 4)
        self.assertIn("onnxruntime", self.report["exact_blockers"][0])

    def test_18_no_negative_zero_or_nonfinite_in_report(self) -> None:
        self.assertNotIn(b"-0.0", self.generated)
        self.assertNotIn(b"NaN", self.generated)
        self.assertNotIn(b"Infinity", self.generated)

    def test_19_manifest_covers_task_files(self) -> None:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
        names = {Path(raw.split(":", 1)[-1]).name for _, raw in pins}
        for path in sorted(HERE.iterdir()):
            if path.is_file() and path.name != "SOURCES.sha256":
                self.assertIn(path.name, names)
        self.assertEqual(PINS.read_bytes(), reference.sources_bytes())

    def test_20_no_trailing_whitespace(self) -> None:
        suffix = {".py", ".json", ".md", ".sha256", ".license"}
        for path in sorted(HERE.iterdir()):
            if path.is_file() and path.suffix in suffix:
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")

    def test_21_deterministic_surrogate(self) -> None:
        _, observed = reference.synth("speech")
        first = reference.run_frames(observed)[1]
        second = reference.run_frames(observed)[1]
        self.assertEqual(first, second)
        self.assertEqual(reference.synth("speech"), reference.synth("speech"))

    def test_22_scope_is_task_local(self) -> None:
        result = subprocess.run(
            ["git", "-C", str(reference.SDK_ROOT), "status", "--porcelain=v1",
             "--untracked-files=all"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(reference.TASK_PREFIX), path)

    def test_23_pin_parser_rejects_invalid_lines(self) -> None:
        for bad in ("not-a-line", "Z" * 64 + "  docs/x", "a" * 64 + "  ../escape",
                    "a" * 64 + "  unknown/x"):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(bad)
        duplicate = "\n".join([f"{'a' * 64}  CONTRACTS.md", f"{'a' * 64}  CONTRACTS.md"])
        with self.assertRaises(ValueError):
            reference.parse_pin_lines(duplicate)

    def test_24_contract_and_scorer_consistency(self) -> None:
        self.assertEqual(self.contract["verification_profile"], "enhancement")
        self.assertEqual(self.contract["format"]["frame_samples"], 160)
        self.assertFalse(self.contract["format"]["public_v0_geometry_preserved"] is False)
        self.assertEqual(CONTRACT.read_bytes(), reference.contract_bytes())
        prior = reference.SDK_ROOT / "docs/task-evidence/online-multichannel-wpe/scorer.py"
        expected = prior.read_text(encoding="utf-8").replace(
            'SCORER_ID = "audio-sdk/online-multichannel-wpe-scoring/0.1"',
            f'SCORER_ID = "{scorer.SCORER_ID}"')
        self.assertEqual((HERE / "scorer.py").read_text(encoding="utf-8"), expected)
        self.assertEqual(self.report["acceptance_profile"]["profile"], "enhancement")
        for case in ("identity_noisy_control", "established_task_matched_baseline",
                     "paired_si_sdr_stoi", "clean_speech_preservation",
                     "peaks_and_invalid_outputs", "unpaired_speech",
                     "alignment_state_memory_timing"):
            self.assertIn(case, self.report["acceptance_profile"]["mapped_cases"])

    def test_25_rights_and_source_reported_gaps(self) -> None:
        licensing = self.report["licensing_analysis"]
        for key in ("training_data_provenance_established", "separate_weights_terms_established",
                    "onnx_runtime_redistribution_terms_established", "redistribution_clearance",
                    "product_use_clearance", "legal_review_completed",
                    "asset_copied_vendored_built_or_downloaded"):
            self.assertIs(licensing[key], False)
        self.assertEqual(licensing["blocked_gate"], "exact_graphs_runtime_and_rights")
        self.assertEqual(self.report["source_reported"]["status"],
                         "source_reported_not_reproduced")
        self.assertIs(self.report["source_reported"]["used_for_qualification"], False)
        for key, value in self.report["negative_claims"].items():
            self.assertIs(value, False, key)

    def test_26_three_cold_start_passes(self) -> None:
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

    def test_27_strict_json_rejects_duplicates_and_nonfinite(self) -> None:
        for payload in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}'):
            with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                             delete=False) as handle:
                handle.write(payload)
                path = Path(handle.name)
            try:
                with self.assertRaises(ValueError):
                    reference.strict_json(path)
            finally:
                path.unlink()

    def test_28_invalid_configs_are_rejected(self) -> None:
        for name, config in reference._invalid_configs():
            try:
                reference.Controller(config)
            except reference.Rejected:
                continue
            self.fail("invalid config accepted: " + name)

    def test_29_upstream_identity(self) -> None:
        identity = reference.upstream_git_identity()
        self.assertEqual(identity["normalized_remote"], reference.UPSTREAM_REPOSITORY)
        self.assertEqual(identity["commit"], reference.UPSTREAM_COMMIT)
        self.assertTrue(identity["pinned_commit_present"])

    def test_30_license_sidecars(self) -> None:
        expected = (f"SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
                    "SPDX-License" "-Identifier: Apache-2.0\n")
        for name in ("SOURCES.sha256.license", "contract.json.license",
                     "report.json.license", "report.json.sha256.license"):
            self.assertEqual((HERE / name).read_text(encoding="utf-8"), expected)

    def test_31_interpreter_is_pinned(self) -> None:
        self.assertTrue(reference.interpreter_is_pinned(), sys.version)


if __name__ == "__main__":
    unittest.main()

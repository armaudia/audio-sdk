# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance suite for the task-local Rate-profile evidence package."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
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


def strict_json(path: Path):
    def reject(value: str):
        raise ValueError("nonfinite:" + value)
    payload = json.loads(path.read_text(encoding="utf-8"),
                         parse_constant=reject)
    assert isinstance(payload, dict)
    return payload


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = strict_json(REPORT)
        cls.generated = reference.canonical_report_bytes(reference.build_report())

    def test_01_report_regenerates_byte_identically(self):
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self):
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_bytes(), f"{digest}  report.json\n".encode("ascii"))

    def test_03_status_and_qualification(self):
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_04_profile_is_rate(self):
        self.assertEqual(self.report["profile"], "rate")
        self.assertEqual(self.report["rate_profile"]["profile"], "rate")
        self.assertFalse(self.report["rate_profile"]["rate_stretcher_executed"])

    def test_05_boundary_is_opt_in_and_unregistered(self):
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration",
                    "descriptor_registry_change", "shared_cmakelists_change",
                    "installed_v0_behavior_change", "processor_exposure"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_06_public_v0_geometry_untouched(self):
        fmt = self.report["format"]
        self.assertEqual(fmt["sample_rate_hz"], 16000)
        self.assertEqual(fmt["channels"], 1)
        self.assertEqual(fmt["sample_format"], "f32")
        self.assertEqual(fmt["frame_samples"], 160)
        self.assertTrue(fmt["public_v0_geometry_preserved"])
        self.assertFalse(fmt["sdk_callback_invoked"])

    def test_07_no_real_model_runtime_audio_device_listening_or_release(self):
        for key, value in self.report["scope"].items():
            if key not in ("synthetic_probability_trace_only", "task_local_only"):
                self.assertIs(value, False, key)

    def test_08_base_commit_pinned(self):
        self.assertEqual(self.report["base_commit"],
                         "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d")

    def test_09_required_keys_present(self):
        for key in ("schema_id", "task_id", "base_commit", "profile", "conditions",
                    "controls", "adverse", "playback_buffering", "rate_profile",
                    "repeatability", "regressions", "gates", "missing_evidence",
                    "scope", "tool_provenance", "source_pins", "boundary_pins"):
            self.assertIn(key, self.report)

    def test_10_contract_is_rate_and_task_local(self):
        contract = strict_json(CONTRACT)
        self.assertEqual(contract["profile"], "rate")
        self.assertEqual(contract["task"], "SDK-SILERO-VAD-PAUSE-DURATION-RULES")
        self.assertIs(contract["boundary"]["registered"], False)
        self.assertIs(contract["boundary"]["enabled_by_default"], False)
        self.assertEqual(self.report["contract_sha256"],
                         hashlib.sha256(CONTRACT.read_bytes()).hexdigest())

    def test_11_source_pins_match_constants_and_files(self):
        self.assertEqual(self.report["source_pins"], reference.SOURCE_PINS)
        for path, digest in reference.SOURCE_PINS.items():
            self.assertEqual(hashlib.sha256((reference.SOURCE_ROOT / path).read_bytes()).hexdigest(),
                             digest, path)

    def test_12_boundary_pins_match_files(self):
        self.assertEqual(self.report["boundary_pins"], reference.BOUNDARY_PINS)
        for path, digest in reference.BOUNDARY_PINS.items():
            self.assertEqual(hashlib.sha256((SDK_ROOT / path).read_bytes()).hexdigest(), digest, path)

    def test_13_manifest_is_deterministic_and_complete(self):
        self.assertEqual(PINS.read_bytes(), reference.sources_bytes())
        names = {line.split("  ", 1)[1].rsplit("/", 1)[-1]
                 for line in PINS.read_text(encoding="utf-8").splitlines()
                 if line and not line.startswith("#") and "  " in line}
        for path in HERE.iterdir():
            if path.is_file() and path.name != "SOURCES.sha256":
                self.assertIn(path.name, names, path.name)

    def test_14_all_conditions_and_rates_scored(self):
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for cases in self.report["conditions"].values():
            self.assertEqual(set(cases), set(reference.RATE_CASES))

    def test_15_source_intervals_are_frame_exact(self):
        for condition, cases in self.report["conditions"].items():
            stop = reference.total_samples(condition)
            for case in cases.values():
                self.assertEqual(case["source_interval"], [0, stop])
                self.assertEqual([pair[0] for pair in case["event_intervals"]],
                                 list(range(0, stop, 160)))
                self.assertEqual(case["event_intervals"][-1][1], stop)

    def test_16_output_mapping_is_contiguous(self):
        for condition, cases in self.report["conditions"].items():
            stop = reference.total_samples(condition)
            for case in cases.values():
                mapping = case["mapping"]
                self.assertEqual(mapping[0]["source"][0], 0)
                self.assertEqual(mapping[0]["output"][0], 0)
                trims = sorted(tuple(row["trim"]) for row in case["pause_decisions"]
                               if row["trim"] is not None)
                gaps = []
                if mapping[0]["source"][0] != 0:
                    gaps.append((0, mapping[0]["source"][0]))
                for left, right in zip(mapping, mapping[1:]):
                    self.assertEqual(left["output"][1], right["output"][0])
                    if left["source"][1] != right["source"][0]:
                        gaps.append((left["source"][1], right["source"][0]))
                if mapping[-1]["source"][1] != stop:
                    gaps.append((mapping[-1]["source"][1], stop))
                self.assertEqual(gaps, trims)
                self.assertEqual(mapping[-1]["output"][1], case["output_interval"][1])

    def test_17_rate_factors_are_exact(self):
        for cases in self.report["conditions"].values():
            for name, case in cases.items():
                self.assertEqual(case["rate"], str(reference.RATE_CASES[name]))
                self.assertGreater(len(case["mapping"]), 0)

    def test_18_final_partial_window_exact(self):
        for condition, cases in self.report["conditions"].items():
            stop = reference.total_samples(condition)
            for case in cases.values():
                partial = case["final_partial"]
                self.assertEqual(partial["source"], [stop - 37, stop])
                self.assertEqual(partial["valid_count"], 37)
                self.assertTrue(partial["final_flag"])
                self.assertEqual(partial["available_ns"],
                                 1767225600000000000 + stop * 62500)

    def test_19_pitch_and_transients_not_measured(self):
        for cases in self.report["conditions"].values():
            for case in cases.values():
                self.assertIsNone(case["pitch_proxy_hz"])
                self.assertEqual(case["pitch_status"], "not_measured_no_rendered_audio")
                self.assertEqual(case["transient_audibility"], "not_measured_no_listening")

    def test_20_pause_decisions_tied_to_source_timestamps(self):
        for condition, cases in self.report["conditions"].items():
            for case in cases.values():
                self.assertTrue(case["pause_decisions"])
                for decision in case["pause_decisions"]:
                    self.assertLess(decision["source_start"], decision["source_end"])
                    if decision["trim"] is not None:
                        self.assertGreaterEqual(decision["trim"][0], decision["source_start"])
                        self.assertLessEqual(decision["trim"][1], decision["source_end"])

    def test_21_unknown_validity_retained_fail_closed(self):
        case = self.report["conditions"]["unknown_validity"]["rate_1x"]
        unknown = [row for row in case["pause_decisions"] if row["label"] == "unknown"]
        self.assertEqual(len(unknown), 2)
        self.assertTrue(all(row["decision"] == "retained_unknown_fail_closed" for row in unknown))

    def test_22_controls_all_present(self):
        controls = self.report["controls"]
        self.assertTrue(controls["all_present"])
        self.assertEqual(controls["identity"]["word_span_overlap_samples"], 0)
        self.assertGreater(controls["named_baseline"]["word_span_overlap_samples"], 0)
        self.assertIn("candidate", controls)

    def test_23_published_reference_not_promoted(self):
        published = self.report["controls"]["named_baseline"]["published_source_report"]
        self.assertEqual(published["status"], "source_reported_not_reproduced")

    def test_24_regressions_recorded_verbatim(self):
        metrics = {row["metric"] for row in self.report["regressions"]}
        self.assertIn("unguarded_baseline_word_span_overlap_samples", metrics)
        self.assertIn("pause_compression_tradeoff_samples", metrics)

    def test_25_config_rejections_are_real(self):
        for _, config in reference._invalid_configs():
            with self.assertRaises(reference.Rejected):
                reference.PauseController(config)
        self.assertTrue(all(row["controller_created"] is False for row in
                            self.report["adverse"]["config_rejections"].values()))

    def test_26_frame_rejections_preserve_state(self):
        controller = reference.PauseController()
        before = controller.state_digest()
        for _, frame, _ in reference._invalid_frames():
            result = controller.process(frame)
            self.assertEqual(result["status"], "rejected")
            self.assertEqual(result["state_digest"], before)
        self.assertTrue(self.report["adverse"]["frame_rejections"]["dsp_state_unchanged"])

    def test_27_lifecycle_rejections(self):
        closed = reference.PauseController()
        closed.close()
        finished = reference.PauseController()
        finished.finish()
        frame = reference.frames("speech")[0]
        self.assertEqual(closed.process(frame)["reason"], "rejected_session")
        self.assertEqual(finished.process(frame)["reason"], "rejected_session")

    def test_28_final_partial_accepted(self):
        controller = reference.PauseController()
        for frame in reference.frames("speech"):
            self.assertEqual(controller.process(frame)["status"], "accepted")
        self.assertEqual(controller.events[-1]["source_last"], reference.total_samples("speech"))

    def test_29_all_invalid_cases_rejected(self):
        self.assertTrue(self.report["adverse"]["all_rejected"])

    def test_30_repeatability_byte_identical(self):
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)
        self.assertEqual(repeat["digests"], reference.repeatability()["digests"])

    def test_31_gates_all_blocked(self):
        self.assertEqual([gate["name"] for gate in self.report["gates"]],
                         reference.GATE_NAMES)
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen_condition"])

    def test_32_playback_buffering_is_fixture_only(self):
        self.assertEqual(set(self.report["playback_buffering"]), set(reference.CONDITIONS))
        for model in self.report["playback_buffering"].values():
            self.assertEqual(model["clock_id"], "fixture-monotonic-not-device")
            self.assertFalse(model["deadline_measured"])

    def test_33_no_negative_zero(self):
        self.assertNotIn(b"-0.0", self.generated)

    def test_34_no_trailing_whitespace(self):
        for path in sorted(HERE.iterdir()):
            if path.is_file() and path.suffix in {".py", ".json", ".md", ".sha256", ".license"}:
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")

    def test_35_scope_is_task_local(self):
        result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                                 "--untracked-files=all"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(reference.TASK_PREFIX), path)

    def test_36_fresh_scratch_regeneration_is_byte_identical(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        with tempfile.TemporaryDirectory(prefix="silero-pause-evidence-") as scratch:
            target = Path(scratch) / "package"
            target.mkdir()
            for path in HERE.iterdir():
                if path.is_file():
                    shutil.copyfile(path, target / path.name)
            digests = []
            for _ in range(3):
                subprocess.run([str(PYTHON), "run.py", "all"], cwd=target,
                               capture_output=True, text=True, check=True, env=env)
                digests.append((hashlib.sha256((target / "report.json").read_bytes()).hexdigest(),
                                hashlib.sha256((target / "SOURCES.sha256").read_bytes()).hexdigest(),
                                (target / "report.json").read_bytes(),
                                (target / "SOURCES.sha256").read_bytes()))
            self.assertEqual(len(set(digests)), 1)
            self.assertEqual(digests[0][2], REPORT.read_bytes())
            self.assertEqual(digests[0][3], PINS.read_bytes())

    def test_37_licensing_headers_present(self):
        license_line = "SPDX" "-License-Identifier: Apache-2.0"
        copyright_line = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(license_line, head, path.name)
            self.assertIn(copyright_line, head, path.name)
        for name in ("SOURCES.sha256.license", "contract.json.license",
                     "report.json.license", "report.json.sha256.license"):
            self.assertIn(license_line, (HERE / name).read_text())


if __name__ == "__main__":
    unittest.main()

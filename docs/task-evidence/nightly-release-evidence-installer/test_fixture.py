# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the nightly-release / installer evidence package.

Run with the pinned interpreter:

    PYTHONDONTWRITEBYTECODE=1 <PY312> -m unittest -v test_fixture.py

No skips, no network, no native build is invoked by this suite.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import unittest
from pathlib import Path

import fixture as fx
import tooling

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
REPORT = HERE / "report.json"
REPORT_SHA = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
PY_FILES = ("fixture.py", "tooling.py", "run.py", "test_fixture.py", "verify.py")


def strict_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"),
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError("nonfinite JSON " + value)))


def pin_lines() -> list[tuple[str, str]]:
    out = []
    for line in PINS.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        digest, raw = line.split("  ", 1)
        out.append((digest, raw))
    return out


class PinTests(unittest.TestCase):
    def test_01_external_pins_match_recorded_bytes(self) -> None:
        for pin in fx.SOURCE_PINS:
            with self.subTest(path=pin["path"]):
                root = SOURCE_ROOT if pin["root"] == "source" else SDK_ROOT
                path = root / pin["path"]
                self.assertTrue(path.is_file(), f"missing {path}")
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                                 pin["sha256"])

    def test_02_releasing_pin_is_exact_and_present(self) -> None:
        pin = next(p for p in fx.SOURCE_PINS if p["path"].endswith("RELEASING.md"))
        self.assertEqual(pin["sha256"],
                         "67e996fc8b1e4bc3e1e90b6bf8e60a98287a9f64177eda2c409f15187a9c65d3")
        self.assertIn("source:audio-benchmark-platform/audio-sdk/RELEASING.md",
                      PINS.read_text(encoding="utf-8"))

    def test_03_code_artifact_pins_match_committed_files(self) -> None:
        for pin in fx.task_artifact_pins():
            with self.subTest(path=pin["path"]):
                self.assertEqual(hashlib.sha256(
                    (HERE / pin["path"]).read_bytes()).hexdigest(),
                    pin["sha256"])

    def test_04_manifest_covers_all_pins_and_reports(self) -> None:
        lines = pin_lines()
        expected = len(fx.SOURCE_PINS) + len(fx.task_artifact_pins()) + 3
        self.assertEqual(len(lines), expected)
        for digest, raw in lines:
            self.assertEqual(len(digest), 64)
            if raw.startswith("source:"):
                path = SOURCE_ROOT / raw.split(":", 1)[1]
            elif raw.startswith("worktree:"):
                path = SDK_ROOT / raw.split(":", 1)[1]
            else:
                self.fail("unprefixed manifest path: " + raw)
            self.assertTrue(path.is_file(), f"missing {path}")
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
        text = PINS.read_text(encoding="utf-8")
        for name in ("report.json", "report.json.sha256", "README.md"):
            self.assertIn("worktree:" + fx.TASK_PREFIX + name, text)
        self.assertNotIn("SOURCES.sha256  ", text)

    def test_05_spdx_headers_on_every_new_python_file(self) -> None:
        for name in PY_FILES:
            with self.subTest(path=name):
                head = "\n".join((HERE / name).read_text(
                    encoding="utf-8").splitlines()[:4])
                self.assertIn(SPDX_LICENSE, head)
                self.assertIn(SPDX_COPYRIGHT, head)

    def test_06_no_trailing_whitespace_in_new_files(self) -> None:
        for path in sorted(HERE.glob("*")):
            if not path.is_file():
                continue
            with self.subTest(path=path.name):
                for line in path.read_text(encoding="utf-8").splitlines():
                    self.assertEqual(line, line.rstrip())


class DeterminismTests(unittest.TestCase):
    def test_07_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(fx.canonical_report_bytes(fx.build_report()),
                         REPORT.read_bytes())

    def test_08_report_sha256_sidecar_matches(self) -> None:
        expected = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(REPORT_SHA.read_text(encoding="utf-8").strip(),
                         expected + "  report.json")

    def test_09_synthetic_generator_is_seed_stable(self) -> None:
        frames = fx.synthetic_frames()
        flat = fx.flatten(frames)
        self.assertEqual(len(frames), fx.SYNTHETIC_FRAMES)
        self.assertEqual(len(flat), fx.SYNTHETIC_SAMPLES)
        self.assertEqual(fx.tensor_digest(flat),
                         fx.tensor_digest(fx.flatten(fx.synthetic_frames())))
        self.assertEqual(fx.tensor_digest(flat),
                         fx.OBSERVED["synthetic_runtime_probe"]["input_digest_f32"])
        self.assertTrue(all(math.isfinite(v) for v in flat))

    def test_10_spec_digest_is_stable(self) -> None:
        self.assertEqual(strict_json(REPORT)["spec_digest"],
                         fx.build_report()["spec_digest"])

    def test_11_strict_finite_json(self) -> None:
        report = strict_json(REPORT)
        self.assertIsInstance(report, dict)
        self.assertEqual(report["base_commit"], fx.BASE_COMMIT)


class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)

    def test_12_tool_profile_and_status(self) -> None:
        self.assertEqual(self.report["profile"], "Tool")
        self.assertEqual(self.report["candidate_status"],
                         "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_13_public_geometry_unchanged(self) -> None:
        fmt = self.report["format"]
        self.assertEqual((fmt["sample_rate_hz"], fmt["channels"],
                          fmt["sample_format"], fmt["frame_samples"]),
                         (16000, 1, "f32", 160))
        self.assertFalse(fmt["advertised_runtime_change"])
        boundary = self.report["boundary"]
        self.assertFalse(boundary["registered"])
        self.assertFalse(boundary["enabled_by_default"])
        self.assertEqual(boundary["descriptor_settings"], {})
        for provider in fx.PROVIDER_BOUNDARY.values():
            self.assertFalse(provider["registered_by_this_task"])
            self.assertFalse(provider["enabled_by_default_by_this_task"])
            self.assertEqual(provider["descriptor_settings"], {})

    def test_14_tool_profile_required_coverage(self) -> None:
        coverage = self.report["profile_coverage"]
        self.assertEqual(coverage["version_install_provenance"],
                         fx.OBSERVED["compile_build"]["build_id"])
        self.assertIn("clean pinned checkout", coverage["clean_checkout_or_package"])
        self.assertTrue(coverage["caller_owned_inputs"])
        self.assertEqual(set(coverage["malformed_inputs"]),
                         {"short_frame", "nonnumeric_valid_count",
                          "negative_epoch"})
        self.assertEqual(set(coverage["missing_optional_selections"]),
                         {"unknown_provider_id", "unset_library_env",
                          "wrong_library_path"})

    def test_15_support_classes_separated(self) -> None:
        separation = self.report["support_separation"]
        self.assertEqual(set(separation), {"compile_build", "synthetic_runtime",
                                           "measured_workload"})
        self.assertEqual(separation["compile_build"]["status"], "observed_local")
        self.assertEqual(separation["synthetic_runtime"]["status"],
                         "observed_local")
        self.assertFalse(separation["synthetic_runtime"]["qualifying"])
        self.assertEqual(separation["measured_workload"]["status"], "blocked")
        self.assertFalse(separation["measured_workload"]["qualifying"])
        classes = {row["support_class"] for row in self.report["matrix"]}
        self.assertEqual(classes, set(separation))

    def test_16_matrix_extends_existing_records_without_support_widening(self) -> None:
        rows = {row["id"]: row for row in self.report["matrix"]}
        expected = ("M01-clean-checkout", "M02-native-configure-build", "M03-ctest",
                    "M04-installed-c-cpp-consumer", "M05-installed-conformance",
                    "M06-python-wheel-install", "M07-installed-python-tests",
                    "M08-synthetic-runtime-probe",
                    "M09-malformed-and-missing-optional",
                    "M10-measured-workload", "M11-nightly-publication",
                    "M12-signing-attestation", "M13-target-platform-breadth",
                    "M14-release-claim")
        self.assertEqual(set(rows), set(expected))
        for row in rows.values():
            self.assertEqual(row["advertised_support_delta"], "none")
            self.assertTrue(row["extends"])
            self.assertIn(row["status"], ("observed_local", "blocked"))
        for name in expected[9:]:
            self.assertEqual(rows[name]["status"], "blocked")

    def test_17_explicit_blocked_gates(self) -> None:
        blocked = {item["id"]: item for item in self.report["blockers"]}
        for gate in ("actual_nightly_publication", "signing_and_attestation",
                     "target_platform_breadth", "release_claim",
                     "measured_workload_support",
                     "sealed_archive_reproducibility"):
            self.assertIn(gate, blocked)
            self.assertEqual(blocked[gate]["status"], "blocked")
            self.assertTrue(blocked[gate]["reason"])
            self.assertTrue(blocked[gate]["reopen"])

    def test_18_observed_digests_are_consistent(self) -> None:
        observed = self.report["observed"]
        self.assertEqual(observed["compile_build"]["build_id"],
                         "audio-sdk/0.1.0+sha256:0bc71dcab04880033a4ad4c1c"
                         "fcebb8a05eccb11a20a786b9c844e394c035972")
        self.assertEqual(len(observed["compile_build"]["build_id"]
                             .split("sha256:")[1]), 64)
        self.assertEqual(observed["compile_build"]["ctest_pass"], 11)
        self.assertEqual(observed["compile_build"]["ctest_total"], 11)
        self.assertEqual(observed["python_wheel"]["installed_tests_pass"], 5)
        for provider in observed["installed_conformance"].values():
            self.assertEqual(provider["checks_pass"], 40)
            self.assertEqual(provider["checks_fail"], 0)
            self.assertEqual(provider["checks_skip"], 0)
        self.assertEqual(observed["synthetic_runtime_probe"]["runs"], 2)
        self.assertTrue(observed["synthetic_runtime_probe"][
            "byte_identical_across_runs"])

    def test_19_wheel_nonreproducibility_recorded_verbatim(self) -> None:
        wheel = self.report["observed"]["python_wheel"]
        self.assertFalse(wheel["byte_reproducible_across_builds"])
        self.assertNotEqual(wheel["wheel_sha256"], wheel["second_build_sha256"])
        self.assertNotEqual(wheel["wheel_sha256"],
                            wheel["third_build_sha256_from_tooling_run"])
        self.assertNotEqual(wheel["second_build_sha256"],
                            wheel["third_build_sha256_from_tooling_run"])
        self.assertTrue(any(item["id"] == "wheel_archive_not_byte_reproducible"
                            for item in self.report["regressions"]))

    def test_20_evidence_classes_no_release_or_workload_claim(self) -> None:
        classes = self.report["evidence_classes"]
        self.assertEqual(classes["measured_workload"], "none")
        self.assertEqual(classes["real_audio_or_listening"], "none")
        self.assertEqual(classes["release_or_publication"], "none")
        self.assertEqual(classes["synthetic_runtime"][:20], "Deterministic seeded")


class BoundaryTests(unittest.TestCase):
    def test_21_reference_crosscheck_passes(self) -> None:
        checked = fx.crosscheck(fx.reference_probe())
        self.assertTrue(checked["all_pass"])
        self.assertTrue(all(checked["checks"].values()))
        for provider in checked["per_provider"].values():
            self.assertTrue(provider["all_metadata_matches"])
            self.assertTrue(provider["native_dsp_not_modelled"])
            self.assertNotEqual(provider["native_output_digest_f32"],
                                provider["model_identity_output_digest_f32"])

    def test_22_declared_delay_and_source_mapping(self) -> None:
        reference = fx.reference_probe()
        for name, provider in reference["providers"].items():
            delay = fx.PROVIDER_BOUNDARY[name]["declared_delay_samples"]
            self.assertEqual(provider["source_first_samples"][0], -delay)
            self.assertEqual(provider["source_first_samples"],
                             [-delay + i * fx.FRAME_SAMPLES
                              for i in range(fx.SYNTHETIC_FRAMES)])
            self.assertEqual(provider["valid_samples"],
                             (fx.SYNTHETIC_FRAMES - (1 if delay else 0))
                             * fx.FRAME_SAMPLES)
            self.assertEqual(provider["drain_frames"], 1 if delay else 0)

    def test_23_malformed_inputs_reject_without_state_change(self) -> None:
        reference = fx.reference_probe()
        for case in reference["malformed"].values():
            self.assertEqual(case["status"], "ValueError")
            self.assertTrue(case["state_intact"])
        with self.assertRaises(fx.BoundaryError):
            fx.ReferenceSession("dsp.highpass80.v0").process(
                fx.FrameCall(0, (0.0,) * (fx.FRAME_SAMPLES - 1)))
        with self.assertRaises(fx.BoundaryError):
            fx.ReferenceSession("dsp.highpass80.v0").process(
                fx.FrameCall(0, (float("nan"),) * fx.FRAME_SAMPLES))

    def test_24_missing_optional_selections_are_rejected(self) -> None:
        for name in ("unknown_provider_id", "unset_library_env",
                     "wrong_library_path"):
            with self.assertRaises(fx.MissingOptionalError):
                fx.ReferenceSession(name)
        observed = fx.OBSERVED["synthetic_runtime_probe"]["missing_optional"]
        self.assertEqual(observed["unknown_provider_id"]["status"], "RuntimeError")
        self.assertEqual(observed["unset_library_env"]["status"], "OSError")
        self.assertEqual(observed["wrong_library_path"]["status"], "OSError")

    def test_25_caller_owned_inputs_uncoupled_sessions(self) -> None:
        frames = fx.synthetic_frames()
        a = fx.ReferenceSession("dsp.highpass80.v0")
        b = fx.ReferenceSession("dsp.highpass80.v0")
        before = tuple(frames[2])  # non-zero step frame: distinct scaled digest
        ra = a.process(fx.FrameCall(0, frames[2]))
        rb = b.process(fx.FrameCall(0, tuple(0.7 * v for v in frames[2])))
        self.assertEqual(frames[2], before)
        self.assertTrue(ra["caller_inputs_unchanged"])
        self.assertNotEqual(ra["input_digest_f32"], rb["input_digest_f32"])
        a.close()
        with self.assertRaises(fx.BoundaryError):
            a.process(fx.FrameCall(0, frames[2]))
        b.close()

    def test_26_no_missing_result_can_qualify_candidate(self) -> None:
        report = strict_json(REPORT)
        damaged = dict(report)
        damaged["crosscheck"] = dict(report["crosscheck"])
        damaged["crosscheck"]["all_pass"] = False
        self.assertEqual(fx.qualification_state(damaged), "not_qualified")
        with self.assertRaises(ValueError):
            fx.qualification_state({**report,
                                    "no_missing_result_qualifies_candidate": False})

    def test_27_tooling_plan_is_reproducible_and_scoped(self) -> None:
        self.assertEqual(tooling.PY, fx.PINNED_PYTHON)
        self.assertEqual(len(tooling.COMMANDS), 14)
        plan = tooling.render(HERE)
        self.assertEqual(len(plan), len(tooling.COMMANDS))
        self.assertTrue(all("--no-index" in command or "--no-build-isolation" in command
                            or "pip" not in command for command in plan))
        self.assertTrue(any(fx.PINNED_PYTHON in command for command in plan))
        self.assertFalse(any("python3.11" in command or "3.11" in command
                             for command in plan))
        self.assertTrue(any(command.startswith("cmake -S " + str(SDK_ROOT))
                            for command in plan))
        self.assertIn("31337", tooling.PROBE_SOURCE)  # frozen seed literal
        with self.assertRaises(SystemExit):
            tooling.run(HERE)

    def test_28_pinned_interpreter_is_31216(self) -> None:
        self.assertIn("3.12.16", fx.TOOL_PINS["python"])
        self.assertTrue(pathlib.Path(fx.PINNED_PYTHON).exists())


if __name__ == "__main__":
    unittest.main()

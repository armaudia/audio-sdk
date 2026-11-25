# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the SDK-FFMPEG-AFWTDN evidence package."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import unittest
from pathlib import Path

import reference
import scorer

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
PROVIDER = HERE / "provider.json"
PROVENANCE = HERE / "tool-provenance.json"
TASK_PREFIX = "docs/task-evidence/ffmpeg-afwtdn/"
SPDX_PIN = ("source:audio-benchmark-platform/audio-sdk/docs/task-evidence/"
            "classical-wiener-denoising/scorer.py")


def strict_json(path: Path) -> dict:
    def reject(value: str):
        raise ValueError("non-finite JSON " + value)
    payload = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)
    assert isinstance(payload, dict)
    return payload


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = strict_json(REPORT)
        cls.contract = strict_json(CONTRACT)
        cls.provider = strict_json(PROVIDER)
        cls.provenance = strict_json(PROVENANCE)
        cls.generated = reference.canonical_report_bytes(reference.build_report())

    def test_01_report_regenerates_byte_identically(self):
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self):
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_text(encoding="utf-8").strip(), f"{digest}  report.json")

    def test_03_status_and_qualification_defer(self):
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_04_boundary_opt_in(self):
        boundary = self.report["boundary"]
        self.assertFalse(boundary["registered"])
        self.assertFalse(boundary["enabled_by_default"])
        self.assertFalse(boundary["default_selected"])
        self.assertEqual(boundary["descriptor_settings"], {})
        self.assertFalse(boundary["public_api_abi_change"])
        self.assertFalse(boundary["provider_registration"])

    def test_05_public_v0_geometry(self):
        fmt = self.report["format"]
        self.assertEqual(fmt, {"sample_rate_hz": 16000, "channels": 1,
                               "sample_format": "f32", "frame_samples": 160})

    def test_06_required_keys_present(self):
        for key in ("schema_id", "task_id", "base_commit", "profile", "conditions",
                    "controls", "adverse", "repeat_runs", "regressions", "gates",
                    "missing_evidence", "scope", "source_pins", "boundary_pins",
                    "acceptance_profile", "qualification"):
            self.assertIn(key, self.report)

    def test_07_base_commit_pinned(self):
        self.assertEqual(self.report["base_commit"], "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d")
        self.assertEqual(self.contract["base_commit"], self.report["base_commit"])

    def test_08_all_conditions_scored(self):
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for value in self.report["conditions"].values():
            self.assertIn("baseline_metrics", value)
            self.assertIn("candidate_metrics", value)
            self.assertEqual(value["samples"], 9600)

    def test_09_controls_all_present(self):
        controls = self.report["controls"]
        self.assertTrue(controls["all_present"])
        for name in ("identity", "noisy_identity", "task_matched_baseline", "candidate"):
            self.assertIn(name, controls)

    def test_10_identity_control_bit_exact(self):
        identity = self.report["controls"]["identity"]
        self.assertTrue(identity["identity_is_bit_exact"])
        self.assertEqual(identity["status"], "control_exact")
        self.assertTrue(identity["excluded_from_qualification"])

    def test_11_paired_scores_finite(self):
        for name in ("identity", "noisy_control", "low_snr", "burst_noise"):
            metrics = self.report["conditions"][name]["candidate_metrics"]
            self.assertIsNotNone(metrics["si_sdr_db"], name)
            self.assertIsNotNone(metrics["stoi"], name)
            self.assertTrue(math.isfinite(metrics["si_sdr_db"]))
            self.assertTrue(math.isfinite(metrics["stoi"]))

    def test_12_silence_scores_explicitly_undefined(self):
        metrics = self.report["conditions"]["silence"]["candidate_metrics"]
        self.assertIsNone(metrics["si_sdr_db"])
        self.assertEqual(metrics["si_sdr_undefined_reason"], "zero_reference_energy")
        self.assertIsNone(metrics["stoi"])
        self.assertEqual(metrics["stoi_undefined_reason"], "insufficient_active_speech")

    def test_13_config_rejections_fail_closed(self):
        cases = self.report["adverse"]["config_rejections"]
        self.assertEqual(set(cases), {"none", "missing_key", "unknown_key", "wrong_type",
                                      "nonfinite", "out_of_range"})
        for value in cases.values():
            self.assertTrue(value["status"].startswith("rejected"), value)
            self.assertFalse(value["controller_created"])
        self.assertEqual(cases["nonfinite"]["status"], "rejected_nonfinite")
        self.assertEqual(cases["missing_key"]["status"], "rejected_missing")

    def test_14_frame_rejections_fail_closed(self):
        cases = dict(self.report["adverse"]["frame_rejections"])
        cases.pop("dsp_state_unchanged")
        self.assertEqual(set(cases), {"wrong_shape", "nonfinite", "out_of_range",
                                      "stale_epoch", "stale_position", "missing_samples"})
        for status in cases.values():
            self.assertTrue(status.startswith("rejected"), status)
        self.assertEqual(cases["stale_epoch"], "rejected_epoch")
        self.assertEqual(cases["stale_position"], "rejected_position")

    def test_15_dsp_state_unchanged_after_rejections(self):
        self.assertTrue(self.report["adverse"]["frame_rejections"]["dsp_state_unchanged"])
        controller = reference.Controller(reference.DEFAULT_CONFIG)
        controller.process_frame([0.01] * 160)
        before = controller.state_digest()
        with self.assertRaises(reference.FrameRejection):
            controller.process_frame([float("nan")] * 160)
        self.assertEqual(controller.state_digest(), before)

    def test_16_lifecycle_rejections(self):
        lifecycle = self.report["adverse"]["lifecycle"]
        self.assertEqual(lifecycle["close_then_process"], "rejected_session")
        self.assertEqual(lifecycle["finish_then_process"], "rejected_session")

    def test_17_validity_unknown_not_nonspeech(self):
        validity = self.report["adverse"]["validity"]
        self.assertTrue(validity["unknown_never_counted_as_nonspeech"])
        self.assertTrue(validity["invalid_excluded"])

    def test_18_repeatability_byte_identical(self):
        repeats = self.report["repeat_runs"]
        core = dict(self.report)
        core.pop("repeat_runs")
        digest = hashlib.sha256(reference.canonical_bytes(core)).hexdigest()
        self.assertEqual(repeats["three_repeats"], 3)
        self.assertTrue(repeats["byte_identical"])
        self.assertEqual(repeats["canonical_digests"], [digest] * 3)

    def test_19_regressions_recorded_verbatim(self):
        self.assertIsInstance(self.report["regressions"], list)
        for item in self.report["regressions"]:
            self.assertEqual(set(item), {"condition", "variant", "metric", "candidate",
                                         "baseline", "interpretation"})

    def test_20_gates_all_blocked(self):
        self.assertTrue(self.report["gates"])
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reason"])
            self.assertTrue(gate["reopen"])

    def test_21_no_negative_zero(self):
        self.assertNotIn(b"-0.0", self.generated)
        for value in (0.0, -0.0):
            self.assertEqual(reference.canonical_bytes({"v": value}), b'{"v":0.0}')

    def test_22_manifest_covers_task_files(self):
        lines = PINS.read_text(encoding="utf-8").splitlines()
        entries = {}
        for line in lines:
            if not line or line.startswith("#"):
                continue
            digest, raw = line.split("  ", 1)
            entries[raw] = digest
            self.assertEqual(len(digest), 64)
        self.assertNotIn("SOURCES.sha256", entries)
        local = {raw.split(":", 1)[1] for raw in entries if raw.startswith("local:")}
        self.assertEqual(local, set(reference.local_files()))
        for name in local:
            self.assertEqual(entries["local:" + name],
                             hashlib.sha256((HERE / name).read_bytes()).hexdigest())

    def test_23_no_trailing_whitespace(self):
        for path in sorted(HERE.iterdir()):
            if path.is_file() and path.suffix in {".py", ".json", ".md", ".sha256", ".license"}:
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")

    def test_24_deterministic_transform(self):
        _, observed = reference.synth("identity")
        first = reference.candidate_transform(observed)
        second = reference.candidate_transform(observed)
        self.assertEqual(first, second)
        self.assertTrue(all(math.isfinite(value) for value in first))

    def test_25_chunked_matches_whole(self):
        _, observed = reference.synth("noisy_control")
        self.assertEqual(reference.process_signal(observed), reference.candidate_transform(observed))
        alignment = self.report["alignment_and_state"]["chunking_equivalence"]
        self.assertTrue(alignment["equal"])
        self.assertEqual(alignment["stream_digest"], alignment["whole_digest"])

    def test_26_partial_final_frame(self):
        _, observed = reference.synth("low_snr")
        output = reference.process_signal(observed[: 160 * 3 + 37])
        self.assertEqual(len(output), 160 * 3 + 37)
        self.assertTrue(self.report["alignment_and_state"]["partial_final_frame"]["equal_duration"])

    def test_27_reset_replay(self):
        self.assertTrue(self.report["alignment_and_state"]["reset"]["replay_matches_original"])
        _, observed = reference.synth("noisy_control")
        frames = [observed[i:i + 160] for i in range(0, 480, 160)]
        controller = reference.Controller(reference.DEFAULT_CONFIG)
        original = [controller.process_frame(list(frame)) for frame in frames]
        controller.reset(epoch=3)
        replay = [controller.process_frame(list(frame), epoch=3) for frame in frames]
        self.assertEqual(original, replay)

    def test_28_session_independence(self):
        independence = self.report["alignment_and_state"]["session_independence"]
        self.assertTrue(independence["first_matches_fresh_replay"])
        self.assertTrue(independence["second_matches_fresh_replay"])
        self.assertTrue(independence["state_isolated"])

    def test_29_scorer_pin(self):
        local = hashlib.sha256((HERE / "scorer.py").read_bytes()).hexdigest()
        pinned = hashlib.sha256(reference.resolve_pin(SPDX_PIN).read_bytes()).hexdigest()
        self.assertEqual(local, pinned)
        self.assertEqual(self.report["scorer"]["local_scorer_digest"], local)

    def test_30_no_ffmpeg_invocation_in_sources(self):
        for name in ("reference.py", "scorer.py", "run.py"):
            source = (HERE / name).read_text(encoding="utf-8")
            for token in ("subprocess", "os.system", "Popen"):
                self.assertNotIn(token, source, (name, token))

    def test_31_tool_provenance_blocked(self):
        self.assertEqual(self.provenance["status"], "blocked")
        self.assertEqual(self.provenance["exact_runtime"]["version"], "7.1")
        self.assertEqual(self.provenance["exact_runtime"]["license"], "GPL-2.0-or-later")
        self.assertFalse(self.provenance["exact_runtime"]["configuration_available_locally"])
        self.assertFalse(self.provenance["numeric_parity_with_ffmpeg"])
        self.assertEqual(self.provenance["synthetic_afwtdn_invocation"]["status"], "not_run")

    def test_32_contract_defer(self):
        self.assertEqual(self.contract["qualification"]["decision"], "DEFER")
        self.assertFalse(self.contract["qualification"]["qualifies"])
        for value in self.contract["public_surface"].values():
            self.assertFalse(value)
        for key, value in self.contract["scope"].items():
            if key in ("synthetic_only", "task_local_only"):
                self.assertTrue(value)
            elif key == "installed_v0_format":
                self.assertEqual(value, "16 kHz mono float32, 160 samples")
            else:
                self.assertFalse(value, key)

    def test_33_provider_unregistered(self):
        self.assertFalse(self.provider["registered"])
        self.assertFalse(self.provider["default_enabled"])
        self.assertTrue(self.provider["opt_in_required"])
        self.assertFalse(self.provider["processor_exposure"])
        self.assertEqual(self.provider["decision"], "DEFER")
        self.assertEqual(self.provider["boundary"]["format"], reference.FORMAT)

    def test_34_scope_task_local(self):
        result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                                 "--untracked-files=all"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(TASK_PREFIX), path)

    def test_35_source_pins_exact(self):
        self.assertEqual(self.report["source_pins"], reference.source_pins())
        self.assertEqual(self.contract["source_pins"], reference.source_pins())
        self.assertEqual(self.report["boundary_pins"], reference.boundary_pins())

    def test_36_license_sidecars(self):
        for name in ("report.json.license", "report.json.sha256.license", "SOURCES.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes", text)
            self.assertIn("SPDX-License" + "-Identifier: Apache-2.0", text)

    def test_37_no_binary_media_files(self):
        for path in HERE.iterdir():
            self.assertFalse(path.name in ("ffmpeg", "ffmpeg.exe", "ffmpeg-macos-aarch64-v7.1"))
            self.assertFalse(path.suffix.lower() in
                             (".wav", ".mp3", ".flac", ".ogg", ".bin", ".exe",
                              ".dylib", ".so", ".dll", ".a", ".o"))

    def test_38_adverse_invalid_count_positive(self):
        self.assertGreater(self.report["adverse"]["invalid_count_delta"], 0)

    def test_39_acceptance_profile_complete(self):
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "Enhancement")
        for key in ("identity_control", "noisy_control", "matched_noisy_identity_baseline",
                    "paired_si_sdr", "stoi", "clean_speech_preservation",
                    "peaks_and_invalid_outputs", "alignment_and_state",
                    "nonfinite_and_edge_rejections"):
            self.assertTrue(profile[key], key)
        for key in ("task_matched_external_baseline", "content_and_availability_timing",
                    "exact_runtime"):
            self.assertFalse(profile[key], key)

    def test_40_no_numeric_parity_claim(self):
        self.assertFalse(self.report["numeric_parity_with_ffmpeg"])
        self.assertFalse(self.report["ffmpeg_invoked"])
        self.assertFalse(self.contract["scope"]["numeric_parity_with_ffmpeg"])
        self.assertFalse(self.provider["ffmpeg_invocation"])
        self.assertFalse(scorer is None)


if __name__ == "__main__":
    unittest.main()

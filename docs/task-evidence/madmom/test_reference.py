# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local madmom blocker package."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
import unittest

import reference

HERE = Path(__file__).resolve().parent


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _valid_manifest() -> dict:
    sha = "a" * 64
    return {
        "channels": 1,
        "cohort_manifest_path": "/tmp/madmom/cohort.json",
        "cohort_manifest_sha256": sha,
        "commercial_grant_path": "/tmp/madmom/jku-grant.json",
        "commercial_grant_sha256": sha,
        "commercial_use_permitted": True,
        "license_record_path": "/tmp/madmom/license.json",
        "license_record_sha256": sha,
        "model_config_path": "/tmp/madmom/model_config.json",
        "model_config_sha256": sha,
        "model_license_id": "CC-BY-NC-SA-4.0",
        "model_license_text_path": "/tmp/madmom/model-license.txt",
        "model_license_text_sha256": sha,
        "parity_vector_path": "/tmp/madmom/parity.json",
        "parity_vector_sha256": sha,
        "rights_record_path": "/tmp/madmom/rights.json",
        "rights_record_sha256": sha,
        "runtime_lock_path": "/tmp/madmom/requirements.lock",
        "runtime_lock_sha256": sha,
        "sample_rate_hz": 16000,
        "source_checkout_path": "/tmp/madmom/source",
        "source_manifest_sha256": sha,
        "source_revision": "b" * 40,
        "weights_byte_count": 12_345_678,
        "weights_path": "/tmp/madmom/weights.pkl",
        "weights_sha256": sha,
    }


class JsonTests(unittest.TestCase):
    def test_canonical_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"value": math.nan})

    def test_strict_rejects_duplicate_key(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_rejects_infinity(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":Infinity}')

    def test_strict_requires_object(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads("[1,2]")

    def test_canonical_normalizes_negative_zero(self) -> None:
        self.assertEqual(reference.canonical_bytes({"z": -0.0}),
                         b'{"z":0.0}')

    def test_signal_digest_is_deterministic(self) -> None:
        signal = [0.0, 0.5, -0.5]
        self.assertEqual(reference.signal_digest(signal),
                         reference.signal_digest(list(signal)))
        self.assertEqual(len(reference.signal_digest(signal)), 64)


class IdentityTests(unittest.TestCase):
    def test_live_board_matches_pinned_stable_row(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"], reference.STABLE_FIELDS)
        self.assertEqual(identity["stable_sha256"], reference.STABLE_SHA256)
        self.assertEqual(identity["stable_sha256"],
                         _sha(reference.canonical_bytes(
                             identity["stable_fields"])))
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertFalse(identity["whole_file_hashed"])

    def test_mutable_fields_are_excluded(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(set(identity["excluded_mutable_fields"]),
                         set(reference.MUTABLE_TASK_FIELDS))
        for field in reference.MUTABLE_TASK_FIELDS:
            self.assertNotIn(field, identity["stable_fields"])

    def test_claim_and_commit_identity(self) -> None:
        self.assertRegex(reference.BASE_COMMIT, r"^[0-9a-f]{40}$")
        self.assertEqual(reference.task_row_identity()["claim"]["base_commit"],
                         reference.BASE_COMMIT)
        self.assertEqual(reference.task_row_identity()["claim"]["branch"],
                         reference.BRANCH)
        self.assertIsNone(reference.UPSTREAM_REVISION)
        self.assertFalse(reference.SOURCE_REVISION_PIN_AVAILABLE)


class ContractTests(unittest.TestCase):
    def test_contract_validates(self) -> None:
        contract = reference.build_contract()
        reference.validate_contract(contract)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "proposal_only_incomplete")
        self.assertEqual(contract["qualification"]["status"], "not_qualified")
        self.assertFalse(contract["qualification"]["candidate_qualified"])
        self.assertTrue(contract["proposal_only"])

    def test_eight_blocked_gates(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(len(contract["gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in contract["gates"]))
        self.assertEqual(contract["qualification"]["blocked_gate_count"], 8)
        self.assertEqual(
            contract["qualification"]["blocked_gate_ids"],
            [gate["id"] for gate in contract["gates"]])

    def test_eight_exact_blockers(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(len(contract["exact_blockers"]), 8)
        self.assertTrue(all(row["status"] == "blocked"
                            and row["qualifies"] is False
                            for row in contract["exact_blockers"]))
        self.assertTrue(all(row["requirement"]
                            for row in contract["exact_blockers"]))
        restricted = [row for row in contract["exact_blockers"]
                      if row["id"] == "pretrained_model_rights_noncommercial"]
        self.assertEqual(len(restricted), 1)
        self.assertEqual(restricted[0]["state"], "restrictive")
        self.assertIn("CC BY-NC-SA 4.0", restricted[0]["requirement"])
        self.assertIn("JKU", restricted[0]["requirement"])

    def test_contract_has_no_model_claims(self) -> None:
        contract = reference.build_contract()
        licensing = contract["licensing"]
        self.assertFalse(licensing["license_verified"])
        self.assertFalse(licensing["commercial_use_permitted"])
        self.assertFalse(licensing["commercial_grant_present"])
        self.assertFalse(licensing["upstream_weights_present"])
        self.assertFalse(contract["upstream_identity"]["reported_geometry_asserted"])
        self.assertIsNone(contract["upstream_identity"]["revision"])
        self.assertEqual(contract["exact_scope"]["write_scope"],
                         "docs/task-evidence/madmom/ only")

    def test_artifact_requirements_are_all_absent(self) -> None:
        contract = reference.build_contract()
        requirements = contract["artifact_requirements"]
        self.assertEqual(len(requirements), 10)
        ids = [row["id"] for row in requirements]
        self.assertIn("inference_models", ids)
        self.assertIn("model_license_or_grant", ids)
        self.assertTrue(all(row["status"] == "absent"
                            and row["required"] is True
                            and row["sha256"] is None
                            and row["revision"] is None
                            for row in requirements))

    def test_contract_canonical_bytes_are_stable(self) -> None:
        first = reference.canonical_contract_bytes()
        second = reference.canonical_contract_bytes()
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))

    def test_contract_file_matches_generated_when_present(self) -> None:
        path = HERE / "contract.json"
        if path.is_file():
            self.assertEqual(path.read_bytes(),
                             reference.canonical_contract_bytes())


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_report_is_canonical_and_deterministic(self) -> None:
        first = reference.canonical_report_bytes(self.report)
        second = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))

    def test_report_disposition(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification"]["status"],
                         "not_qualified")
        self.assertFalse(self.report["qualification"]["candidate_qualified"])
        self.assertTrue(self.report["qualification"]
                        ["all_release_gates_blocked"])

    def test_report_contract_digest(self) -> None:
        self.assertEqual(
            self.report["contract_sha256"],
            reference.object_digest(reference.build_contract()))

    def test_report_and_contract_identity_match(self) -> None:
        contract = reference.build_contract()
        for key in ("exact_scope", "installed_v0", "licensing", "scope",
                    "upstream_identity", "artifact_requirements", "board_row",
                    "gates", "blockers", "remaining_gates", "non_claims",
                    "reproduction", "caller_asset_contract"):
            if key == "blockers":
                self.assertEqual(self.report[key], contract["exact_blockers"])
            else:
                self.assertEqual(self.report[key], contract[key])

    def test_report_has_eight_blocked_gates(self) -> None:
        self.assertEqual(len(self.report["gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in self.report["gates"]))
        self.assertEqual(len(self.report["blockers"]), 8)
        self.assertTrue(all(row["status"] == "blocked"
                            and row["qualifies"] is False
                            for row in self.report["blockers"]))

    def test_absence_audit_is_closed(self) -> None:
        audit = self.report["absence_audit"]
        self.assertTrue(audit["all_absence_probes_absent"])
        self.assertEqual(audit["probe_count"], len(reference.ABSENCE_PROBES))
        self.assertTrue(all(probe["exists"] is False
                            for probe in audit["probes"]))
        self.assertFalse(audit["source_checkout_present"])
        self.assertFalse(audit["weights_present"])
        self.assertFalse(audit["runtime_present"])
        self.assertFalse(audit["license_record_present"])
        self.assertFalse(audit["model_license_record_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["parity_manifest_present"])

    def test_upstream_identity_is_not_overclaimed(self) -> None:
        upstream = self.report["upstream_identity"]
        self.assertEqual(upstream["name"], "madmom")
        self.assertEqual(upstream["reported_models_license"],
                         "CC BY-NC-SA 4.0 (models, source-reported)")
        self.assertEqual(upstream["reported_commercial_use"],
                         "No with shipped models")
        self.assertIsNone(upstream["revision"])
        self.assertFalse(upstream["revision_pin_available"])
        self.assertFalse(upstream["license_verified"])
        self.assertFalse(upstream["model_license_file_present"])
        self.assertEqual(upstream["task_geometry_status"], "unestablished")
        self.assertFalse(upstream["reported_geometry_asserted"])
        self.assertIsNone(upstream["reported_sample_rate_hz"])
        self.assertIsNone(upstream["reported_channels"])

    def test_pins_are_verified(self) -> None:
        for rows in (self.report["source_pins"],
                     self.report["boundary_pins"]):
            self.assertTrue(rows)
            self.assertTrue(all(row["verified"] is True
                                and row["sha256"] == row["actual"]
                                for row in rows.values()))

    def test_profile_scoring_passes_only_synthetic(self) -> None:
        scoring = self.report["profile_scoring"]
        self.assertTrue(scoring["passed"])
        self.assertEqual(scoring["failed_checks"], [])
        self.assertEqual(scoring["scope"],
                         "synthetic fixture only; not release qualification")
        self.assertTrue(all(row["passed"] is True
                            for row in scoring["checks"]))
        self.assertEqual(len(scoring["checks"]), 31)

    def test_report_sidecar_matches_when_present(self) -> None:
        report_path = HERE / "report.json"
        sidecar_path = HERE / "report.json.sha256"
        if report_path.is_file() and sidecar_path.is_file():
            digest = _sha(report_path.read_bytes())
            self.assertEqual(sidecar_path.read_bytes(),
                             f"{digest}  report.json\n".encode("ascii"))


class SyntheticTests(unittest.TestCase):
    def test_stimuli_validate(self) -> None:
        reference.validate_stimuli(reference.STIMULI)

    def test_signals_are_finite_bounded_and_deterministic(self) -> None:
        for name, spec in sorted(reference.STIMULI.items()):
            first, gaps = reference.generate_signal(spec)
            second, second_gaps = reference.generate_signal(spec)
            self.assertEqual(first, second, name)
            self.assertEqual(gaps, second_gaps, name)
            self.assertEqual(len(first), spec["length_samples"], name)
            self.assertTrue(all(math.isfinite(value) for value in first), name)
            self.assertTrue(all(abs(value) <= 1.0 for value in first), name)

    def test_expected_tempi(self) -> None:
        expected = {
            "music_like_1x": "10000",
            "rate_0_8": "8000",
            "rate_1_2": "12000",
            "rebuffer": "10000",
        }
        for name, bpm in expected.items():
            analysis = reference.analyze(reference.STIMULI[name])
            self.assertEqual(analysis["tempo"]["status"], "stable", name)
            self.assertEqual(analysis["tempo"]["bpm_x100"], bpm, name)

    def test_exact_duration_mapping(self) -> None:
        for name in ("music_like_1x", "rate_0_8", "rate_1_2"):
            analysis = reference.analyze(reference.STIMULI[name])
            frames = analysis["onset_frames"]
            period = reference.STIMULI[name]["period_samples"]
            self.assertEqual((frames[-1] - frames[0]) * reference.FRAME_SAMPLES,
                             (len(frames) - 1) * period, name)

    def test_silence_has_no_onsets(self) -> None:
        analysis = reference.analyze(reference.STIMULI["silence"])
        self.assertEqual(analysis["tempo"]["status"], "no_onsets")
        self.assertEqual(analysis["onset_frames"], [])
        self.assertEqual(analysis["meter"]["status"], "insufficient_onsets")

    def test_out_of_range_and_unfamiliar_are_not_stable(self) -> None:
        for name in ("tempo_out_of_range_adverse",
                     "speech_like_unfamiliar"):
            tempo = reference.analyze(reference.STIMULI[name])["tempo"]
            self.assertNotEqual(tempo["status"], "stable", name)
            self.assertIsNone(tempo["bpm_x100"], name)

    def test_drift_is_monotonic_and_not_stable(self) -> None:
        analysis = reference.analyze(reference.STIMULI["drift"])
        tempo = analysis["tempo"]
        iois = [int(value) for value in tempo["ioi_frames"]]
        self.assertGreaterEqual(len(iois), 4)
        self.assertTrue(all(later < earlier
                            for earlier, later in zip(iois, iois[1:])))
        self.assertNotEqual(tempo["status"], "stable")
        self.assertIsNone(tempo["bpm_x100"])
        self.assertEqual(analysis["meter"]["status"], "no_accented_downbeats")

    def test_rebuffer_gap_is_excluded(self) -> None:
        analysis = reference.analyze(reference.STIMULI["rebuffer"])
        self.assertEqual(analysis["tempo"]["excluded_ioi_count"], "1")
        self.assertEqual(len(analysis["gaps"]), 1)

    def test_meter_surrogate(self) -> None:
        analysis = reference.analyze(reference.STIMULI["music_like_1x"])
        meter = analysis["meter"]
        self.assertEqual(meter["status"], "stable_meter")
        self.assertEqual(meter["meter_beats"], "4")
        self.assertEqual(meter["downbeat_count"], "3")
        self.assertEqual(meter["downbeat_phase_onset_frame"], "0")
        self.assertEqual(meter["accent_period_onsets"], ["4", "4"])
        self.assertEqual(meter["accent_indices"], ["0", "4", "8"])
        self.assertGreaterEqual(
            int(meter["strength_spread_milli"]),
            reference.ACCENT_MIN_DELTA_MILLI)

    def test_rate_changed_surrogate_keeps_meter(self) -> None:
        for name in ("rate_0_8", "rate_1_2"):
            analysis = reference.analyze(reference.STIMULI[name])
            self.assertEqual(analysis["meter"]["status"], "stable_meter", name)
            self.assertEqual(analysis["meter"]["meter_beats"], "4", name)
            self.assertEqual(analysis["meter"]["downbeat_phase_onset_frame"],
                             "0", name)

    def test_unfamiliar_speech_has_no_stable_meter(self) -> None:
        analysis = reference.analyze(reference.STIMULI["speech_like_unfamiliar"])
        self.assertNotEqual(analysis["meter"]["status"], "stable_meter")

    def test_final_partial_window(self) -> None:
        analysis = reference.analyze(reference.STIMULI["final_partial"])
        self.assertEqual(len(analysis["signal"]), reference.FINAL_PARTIAL_SAMPLES)
        self.assertEqual(analysis["final_valid_count"],
                         reference.FINAL_PARTIAL_VALID)
        self.assertEqual(len(analysis["events"]), 1)
        event = analysis["events"][0]
        self.assertEqual(event.source_start, 96000)
        self.assertEqual(event.source_end, reference.FINAL_PARTIAL_SAMPLES)
        self.assertFalse(event.source_end > reference.FINAL_PARTIAL_SAMPLES)
        self.assertEqual(event.source_start
                         - reference.STIMULI["final_partial"]["onset_sample"],
                         -30)

    def test_availability_margin_is_one_frame(self) -> None:
        analysis = reference.analyze(reference.STIMULI["music_like_1x"])
        margins = {
            event.available_monotonic_ns - event.capture_first_ns
            for event in analysis["events"]
        }
        self.assertEqual(margins, {reference.FRAME_NS})


class AdverseTests(unittest.TestCase):
    def test_all_adverse_cases_are_explicit_and_nonqualifying(self) -> None:
        cases = reference._adverse_cases()
        self.assertTrue(cases)
        self.assertTrue(all(case["qualifies"] is False for case in cases))
        self.assertTrue(all(case["status"] in ("rejected", "recorded")
                            for case in cases))
        ids = {case["id"] for case in cases}
        for expected in ("MISS-01", "INV-01", "INV-02", "INV-03",
                         "INV-04", "INV-05", "INV-06", "INV-07",
                         "INV-08", "INV-09", "INV-10", "CFG-01",
                         "CFG-02", "CFG-03", "CFG-04", "CFG-05"):
            self.assertIn(expected, ids)

    def test_rejected_cases_do_not_advance_state(self) -> None:
        for case in reference._adverse_cases():
            if case["status"] == "rejected":
                self.assertTrue(case["state_unchanged"], case["id"])
                self.assertEqual(case["onset_count"], "0", case["id"])
                self.assertTrue(case["code"], case["id"])

    def test_direct_missing_invalid_nonfinite_rejections(self) -> None:
        for kwargs in (
            {"samples": None},
            {"samples": [0.0] * 159},
            {"samples": [float("nan")] + [0.0] * 159},
            {"samples": [float("inf")] + [0.0] * 159},
            {"samples": [0.0] * 160, "input_count": 159},
            {"samples": [0.0] * 160, "epoch": 0},
            {"samples": [0.0] * 160, "valid_count": 0},
            {"samples": [0.0] * 37 + [0.5] + [0.0] * 122,
             "valid_count": 37},
        ):
            analyzer = reference.Analyzer()
            before = analyzer.state_digest
            arguments = dict(kwargs)
            samples = arguments.pop("samples")
            with self.assertRaises(reference.Reject):
                analyzer.process_frame(samples, **arguments)
            self.assertEqual(analyzer.state_digest, before)
            self.assertEqual(analyzer.events, [])

    def test_invalid_configs_reject(self) -> None:
        for kwargs in (
            {"sample_rate_hz": 44100},
            {"channels": 2},
            {"frame_samples": 512},
            {"sample_format": "float64"},
            {"epoch": -1},
        ):
            with self.assertRaises(reference.Reject):
                reference.Analyzer(**kwargs)


class AssetManifestTests(unittest.TestCase):
    def test_valid_manifest_is_accepted_for_shape_only(self) -> None:
        result = reference.validate_asset_manifest(_valid_manifest())
        self.assertEqual(result["status"], "accepted_for_shape_only")
        self.assertFalse(result["executed"])
        self.assertFalse(result["model_loaded"])
        self.assertFalse(result["qualifies"])
        self.assertTrue(result["commercial_use_metadata"])
        self.assertFalse(result["upstream_revision_pinned_by_this_package"])

    def test_commercial_flag_false_is_echoed_without_qualifying(self) -> None:
        manifest = _valid_manifest()
        manifest["commercial_use_permitted"] = False
        result = reference.validate_asset_manifest(manifest)
        self.assertFalse(result["commercial_use_metadata"])
        self.assertFalse(result["qualifies"])

    def test_missing_field_rejects(self) -> None:
        manifest = _valid_manifest()
        del manifest["weights_sha256"]
        with self.assertRaises(reference.Reject):
            reference.validate_asset_manifest(manifest)

    def test_extra_field_rejects(self) -> None:
        manifest = _valid_manifest()
        manifest["extra"] = True
        with self.assertRaises(reference.Reject):
            reference.validate_asset_manifest(manifest)

    def test_relative_and_null_paths_reject(self) -> None:
        for value in ("relative/weights.pkl", "", None, "/tmp/\x00bad"):
            manifest = _valid_manifest()
            manifest["weights_path"] = value
            with self.assertRaises(reference.Reject):
                reference.validate_asset_manifest(manifest)

    def test_revision_shape_rejects(self) -> None:
        for value in ("A" * 40, "a" * 39, "a" * 41, "g" * 40, None):
            manifest = _valid_manifest()
            manifest["source_revision"] = value
            with self.assertRaises(reference.Reject):
                reference.validate_asset_manifest(manifest)

    def test_sha_shape_rejects(self) -> None:
        for value in ("A" * 64, "a" * 63, "g" * 64, None, 1):
            manifest = _valid_manifest()
            manifest["weights_sha256"] = value
            with self.assertRaises(reference.Reject):
                reference.validate_asset_manifest(manifest)

    def test_model_license_id_rejects(self) -> None:
        for value in ("", "CC BY-NC-SA 4.0", "-bad", "a" * 65, None, 7):
            manifest = _valid_manifest()
            manifest["model_license_id"] = value
            with self.assertRaises(reference.Reject):
                reference.validate_asset_manifest(manifest)

    def test_commercial_flag_type_rejects(self) -> None:
        for value in (0, 1, "true", None, 1.0):
            manifest = _valid_manifest()
            manifest["commercial_use_permitted"] = value
            with self.assertRaises(reference.Reject):
                reference.validate_asset_manifest(manifest)

    def test_numeric_ranges_reject(self) -> None:
        cases = (
            ("sample_rate_hz", 7999),
            ("sample_rate_hz", 192001),
            ("sample_rate_hz", float("nan")),
            ("sample_rate_hz", float("inf")),
            ("sample_rate_hz", "16000"),
            ("sample_rate_hz", True),
            ("channels", 0),
            ("channels", 3),
            ("channels", True),
            ("weights_byte_count", 0),
            ("weights_byte_count", 536870913),
            ("weights_byte_count", 1.5),
            ("weights_byte_count", True),
        )
        for field, value in cases:
            manifest = _valid_manifest()
            manifest[field] = value
            with self.assertRaises(reference.Reject):
                reference.validate_asset_manifest(manifest)


class PackageTests(unittest.TestCase):
    def test_absence_probes_are_sorted_and_unique(self) -> None:
        self.assertEqual(list(reference.ABSENCE_PROBES),
                         sorted(set(reference.ABSENCE_PROBES)))

    def test_sources_manifest_is_deterministic_and_excludes_board(self) -> None:
        import run
        first = run.sources_bytes()
        second = run.sources_bytes()
        self.assertEqual(first, second)
        self.assertNotIn(b"plan/swarm/TASKS.json", first)
        self.assertIn(b"source:cpp-library/pipeline-validation/"
                      b"playback-speed-candidates.md", first)
        self.assertIn(b"docs/task-evidence/madmom/report.json", first)

    def test_no_forbidden_artifacts(self) -> None:
        forbidden = {
            ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".h5", ".mat",
            ".model", ".mp3", ".npy", ".npz", ".o", ".ogg", ".onnx", ".pkl",
            ".pt", ".pth", ".pyc", ".so", ".wav", ".wasm", ".weights",
        }
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertFalse(path.name.startswith("LICENSE"), path.name)
            self.assertNotIn(path.name,
                             {"CMakeLists.txt", "provider.json", "adapter.json"})

    def test_no_contiguous_spdx_token_outside_headers(self) -> None:
        token = "SPDX-License-" "Identifier: Apache-2.0"
        for path in sorted(HERE.glob("*.py")):
            for number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), start=1):
                if token in line and not line.lstrip().startswith("#"):
                    self.fail(f"{path.name}:{number} embeds the raw REUSE token")


if __name__ == "__main__":
    unittest.main()

# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only tests for the NeMo Schrödinger-bridge package.

No network, no downloads, no weights, no skips.  Every check runs against the
synthetic whole-clip boundary model only; nothing here qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
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
    "exact_source_checkpoint_and_config_identity",
    "pinned_runtime_and_offline_load",
    "artifact_and_output_rights",
    "whole_utterance_geometry_and_sampler",
    "exact_reference_parity",
    "rights_cleared_paired_cohort",
    "independent_scoring_and_listening",
    "target_timing_and_opt_in_provider",
}
EXPECTED_ASSET_REASONS = [
    "checkpoint_identity_not_verified",
    "license_scope_unresolved",
    "rights_register_entry_absent",
    "runtime_not_pinned",
    "upstream_revision_not_verified",
]
BOARD_RELATIVE = "audio-benchmark-platform/plan/swarm/TASKS.json"


def _no_duplicates(pairs):
    seen = set()
    for key, _value in pairs:
        if key in seen:
            raise ValueError("duplicate key: " + key)
        seen.add(key)
    return dict(pairs)


def load_strict(name: str):
    return json.loads(
        (HERE / name).read_text(encoding="utf-8"),
        object_pairs_hook=_no_duplicates,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError("nonfinite:" + token)
        ),
    )


class TestCanonicalJson(unittest.TestCase):
    def test_canonical_bytes_sorted_compact(self):
        self.assertEqual(
            reference.canonical_bytes({"b": 1, "a": [2, 3]}),
            b'{"a":[2,3],"b":1}\n',
        )

    def test_negative_zero_normalized(self):
        self.assertEqual(
            reference.canonical_bytes({"x": -0.0}), b'{"x":0.0}\n'
        )

    def test_nonfinite_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                reference.canonical_bytes({"x": bad})

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}', object_pairs_hook=_no_duplicates)

    def test_report_bytes_end_with_single_newline(self):
        payload = reference.canonical_report_bytes(reference.build_report())
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))
        payload.decode("utf-8")


class TestTaskIdentity(unittest.TestCase):
    def test_stable_digest_is_stable_and_excludes_mutable_fields(self):
        identity = reference.task_identity()
        self.assertEqual(
            identity["stable_sha256"], reference.stable_identity_digest()
        )
        for key in reference.MUTABLE_BOARD_FIELDS:
            self.assertNotIn(key, identity)
        self.assertFalse(identity["board_full_file_hashed"])
        self.assertEqual(identity["id"], reference.TASK)
        self.assertEqual(identity["component"], reference.COMPONENT)
        self.assertEqual(identity["mode"], "feasibility")
        self.assertEqual(
            identity["depends_on"],
            ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
        )
        self.assertEqual(
            identity["evidence"],
            ["adapters/nemo-dereverb/README.md", "adapters/nemo-dereverb/README.md"],
        )

    def test_digest_ignores_input_order(self):
        reordered = dict(reversed(list(reference.STABLE_TASK_IDENTITY.items())))
        self.assertEqual(
            reference.stable_identity_digest(reordered),
            reference.stable_identity_digest(),
        )

    def test_mutable_board_file_is_not_pinned(self):
        text = (
            "\n".join(reference.SOURCE_PINS)
            + "\n"
            + "\n".join(reference.BOUNDARY_PINS)
            + "\n"
            + "\n".join(reference.SIBLING_PINS)
        )
        self.assertNotIn("plan/swarm/TASKS.json", text)
        report = reference.build_report()
        self.assertFalse(report["pins"]["board_file_pinned"])
        self.assertFalse(report["pins"]["board_full_file_hashed"])

    def test_live_board_stable_projection_matches(self):
        path = reference.SOURCE_ROOT / BOARD_RELATIVE
        self.assertTrue(path.is_file())
        board = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_no_duplicates,
        )
        rows = [row for row in board["tasks"] if row.get("id") == reference.TASK]
        self.assertEqual(len(rows), 1)
        projected = reference.project_board_row(rows[0])
        expected = {
            field: reference.STABLE_TASK_IDENTITY[field]
            for field in reference.PROJECTED_BOARD_FIELDS
        }
        self.assertEqual(projected, expected)
        self.assertEqual(
            reference.stable_row_digest(projected), reference.stable_identity_digest()
        )


class TestFixture(unittest.TestCase):
    def test_fixture_is_deterministic(self):
        first = reference.build_fixture()
        second = reference.build_fixture()
        self.assertEqual(first, second)

    def test_fixture_geometry(self):
        fixture = reference.build_fixture()
        self.assertEqual(len(fixture["reverb_float"]), reference.FIXTURE_SAMPLES)
        self.assertEqual(len(fixture["early"]), reference.FIXTURE_SAMPLES)
        self.assertEqual(len(fixture["late"]), reference.FIXTURE_SAMPLES)
        self.assertEqual(len(fixture["noise"]), reference.FIXTURE_SAMPLES)
        self.assertEqual(fixture["channels"], 1)
        self.assertEqual(fixture["sample_rate_hz"], 16000)

    def test_fixture_decomposition_is_exact(self):
        fixture = reference.build_fixture()
        for index in range(0, reference.FIXTURE_SAMPLES, 257):
            total = (
                fixture["early"][index]
                + fixture["late"][index]
                + fixture["noise"][index]
            )
            self.assertAlmostEqual(
                total, fixture["reverb_float"][index], places=12
            )

    def test_silence_stratum_is_exact_zero(self):
        fixture = reference.build_fixture()
        self.assertTrue(all(value == 0.0 for value in fixture["reverb_float"][:3200]))
        self.assertTrue(
            any(value != 0.0 for value in fixture["reverb_float"][-1600:])
        )


class TestSurrogate(unittest.TestCase):
    def setUp(self):
        self.fixture = reference.build_fixture()
        self.samples = list(self.fixture["reverb_float"])
        self.result = reference.process_utterance(self.samples, dict(reference.CONFIG))

    def test_output_is_deterministic(self):
        again = reference.process_utterance(self.samples, dict(reference.CONFIG))
        self.assertEqual(self.result["output"], again["output"])

    def test_output_is_finite_and_bounded(self):
        self.assertTrue(all(math.isfinite(value) for value in self.result["output"]))
        self.assertLessEqual(
            max(abs(value) for value in self.result["output"]),
            reference.MAX_ABS_AUDIO,
        )
        self.assertEqual(
            sum(
                1
                for value in self.result["output"]
                if abs(value) >= reference.MAX_ABS_AUDIO
            ),
            0,
        )

    def test_output_length_is_conserved(self):
        self.assertEqual(self.result["input_samples"], reference.FIXTURE_SAMPLES)
        self.assertEqual(self.result["output_samples"], reference.FIXTURE_SAMPLES)
        self.assertFalse(self.result["streaming"])

    def test_silence_stays_exact_zero(self):
        silence = reference.process_utterance(
            [0.0] * reference.FIXTURE_SAMPLES, dict(reference.CONFIG)
        )
        self.assertTrue(all(value == 0.0 for value in silence["output"]))

    def test_sampler_strings_are_exercised(self):
        ode = dict(reference.CONFIG)
        ode["sampler"] = "ode"
        ode_result = reference.process_utterance(self.samples, ode)
        one = dict(reference.CONFIG)
        one["sampler_steps"] = 1
        one_result = reference.process_utterance(self.samples, one)
        self.assertNotEqual(self.result["output"], ode_result["output"])
        self.assertNotEqual(self.result["output"], one_result["output"])

    def test_report_results_match_surrogate(self):
        results = reference.build_report()["results"]
        self.assertTrue(results["deterministic_repeat_equal"])
        self.assertTrue(results["output_samples_equal_input"])
        self.assertTrue(results["silence_exact_zero"])
        self.assertEqual(results["nonfinite_output_count"], 0)
        self.assertEqual(results["clipped_output_count"], 0)
        self.assertEqual(results["input_samples"], reference.FIXTURE_SAMPLES)


class TestConfigAdverse(unittest.TestCase):
    def test_every_adverse_config_is_rejected_with_exact_reason(self):
        results = reference.config_adverse_control()
        names = [name for name in results if not name.endswith(":expected")]
        self.assertGreaterEqual(len(names), 14)
        for name in names:
            self.assertEqual(
                results[name], results[name + ":expected"], msg=name
            )

    def test_missing_extra_and_wrong_types_are_rejected(self):
        bad_cases = []
        missing = dict(reference.CONFIG)
        del missing["model_id"]
        bad_cases.append(missing)
        extra = dict(reference.CONFIG)
        extra["x"] = 1
        bad_cases.append(extra)
        wrong = dict(reference.CONFIG)
        wrong["channels"] = True
        bad_cases.append(wrong)
        for config in bad_cases:
            with self.assertRaises(ValueError):
                reference.validate_config(config)

    def test_valid_config_is_accepted(self):
        reference.validate_config(dict(reference.CONFIG))


class TestInputAdverse(unittest.TestCase):
    def test_every_adverse_input_is_rejected_with_exact_reason(self):
        fixture = reference.build_fixture()
        results = reference.input_adverse_control(fixture)
        names = [name for name in results if not name.endswith(":expected")]
        self.assertGreaterEqual(len(names), 11)
        for name in names:
            self.assertEqual(
                results[name], results[name + ":expected"], msg=name
            )

    def test_valid_utterance_is_accepted(self):
        fixture = reference.build_fixture()
        reference.validate_utterance(list(fixture["reverb_float"]))

    def test_nonfinite_rejected_before_output(self):
        fixture = reference.build_fixture()
        samples = list(fixture["reverb_float"])
        samples[0] = float("nan")
        with self.assertRaises(ValueError) as context:
            reference.process_utterance(samples, dict(reference.CONFIG))
        self.assertEqual(str(context.exception), "sample_nonfinite")


class TestStreaming(unittest.TestCase):
    def test_full_clip_accepted_and_chunks_rejected(self):
        fixture = reference.build_fixture()
        samples = list(fixture["reverb_float"])
        result = reference.process_chunks([samples], dict(reference.CONFIG))
        self.assertEqual(result["output_samples"], reference.FIXTURE_SAMPLES)
        self.assertTrue(result["one_shot"])
        with self.assertRaises(ValueError) as context:
            reference.process_chunks(
                [samples[:8000], samples[8000:]], dict(reference.CONFIG)
            )
        self.assertEqual(str(context.exception), "utterance_level_offline_only")
        with self.assertRaises(ValueError) as context:
            reference.process_chunks([samples[:1]], dict(reference.CONFIG))
        self.assertEqual(str(context.exception), "utterance_length_mismatch")

    def test_streaming_control_flags(self):
        fixture = reference.build_fixture()
        control = reference.streaming_control(fixture)
        self.assertFalse(control["candidate_streaming_api"])
        self.assertFalse(control["streaming_claimed"])
        self.assertTrue(control["one_shot_accepted"])
        self.assertEqual(control["full_clip_output_samples"], reference.FIXTURE_SAMPLES)


def _synthetic_manifest(root: Path) -> dict:
    unit = b"audio-sdk/nemo-schr-dinger-bridge-dereverberation/test/v1\n"
    source = unit * 8
    checkpoint = unit * 32
    config = unit * 4
    runtime = unit * 16
    (root / "source.bin").write_bytes(source)
    (root / "checkpoint.bin").write_bytes(checkpoint)
    (root / "config.bin").write_bytes(config)
    (root / "runtime.bin").write_bytes(runtime)
    return {
        "asset_id": "synthetic-nemo-test-control-not-nemo",
        "candidate_asset": False,
        "checkpoint_bytes": len(checkpoint),
        "checkpoint_path": str(root / "checkpoint.bin"),
        "checkpoint_sha256": hashlib.sha256(checkpoint).hexdigest(),
        "channels": 1,
        "config_path": str(root / "config.bin"),
        "config_sha256": hashlib.sha256(config).hexdigest(),
        "license_id": "synthetic-control",
        "nemo_version": "not-a-runtime",
        "rights_entry_present": False,
        "runtime_lock_sha256": "0" * 64,
        "runtime_path": str(root / "runtime.bin"),
        "runtime_sha256": hashlib.sha256(runtime).hexdigest(),
        "sample_format": "f32",
        "sample_rate_hz": 16000,
        "sampler": "sde",
        "sampler_steps": 4,
        "source_commit": "0" * 40,
        "source_path": str(root / "source.bin"),
        "storage": "external",
        "torch_version": "not-a-runtime",
    }


class TestAssetAdmission(unittest.TestCase):
    def test_synthetic_control_is_structurally_accepted_but_never_admitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _synthetic_manifest(Path(tmp).resolve())
            structural = reference.validate_caller_asset(manifest)
            admission = reference.admit_candidate_asset(manifest)
        self.assertEqual(structural["status"], "accepted_structure")
        self.assertTrue(structural["asset_bytes_hashed"])
        self.assertFalse(structural["asset_bytes_read"])
        self.assertFalse(structural["loaded"])
        self.assertFalse(structural["executed"])
        self.assertFalse(structural["imported"])
        self.assertEqual(admission["status"], "rejected")
        self.assertEqual(admission["reason_codes"], ["synthetic_control_not_candidate"])

    def test_candidate_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _synthetic_manifest(Path(tmp).resolve())
            manifest["asset_id"] = "nemo-se-der-sb-16k-small-unpinned"
            manifest["candidate_asset"] = True
            result = reference.admit_candidate_asset(manifest)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["admitted"])
        self.assertEqual(result["reason_codes"], EXPECTED_ASSET_REASONS)
        self.assertFalse(result["loaded"])
        self.assertFalse(result["executed"])

    def test_structural_rejections_are_exact(self):
        control = reference.asset_admission_control()
        results = control["rejection_controls"]
        names = [name for name in results if not name.endswith(":expected")]
        self.assertGreaterEqual(len(names), 18)
        for name in names:
            self.assertEqual(
                results[name], results[name + ":expected"], msg=name
            )

    def test_manifest_fields_are_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _synthetic_manifest(Path(tmp).resolve())
            self.assertEqual(set(manifest), reference.REQUIRED_ASSET_FIELDS)
            missing = dict(manifest)
            del missing["runtime_sha256"]
            with self.assertRaises(ValueError):
                reference.validate_caller_asset(missing)
            extra = dict(manifest)
            extra["x"] = 1
            with self.assertRaises(ValueError):
                reference.validate_caller_asset(extra)

    def test_report_asset_is_unpinned(self):
        report = reference.build_report()
        asset = report["asset_boundary"]["asset"]
        self.assertIsNone(asset["byte_count"])
        self.assertIsNone(asset["sha256"])
        self.assertFalse(asset["pinned"])
        self.assertFalse(asset["rights_entry_present"])
        self.assertFalse(asset["ledger_entry_present"])
        self.assertEqual(asset["storage"], "external")
        self.assertIsNone(asset["source_revision"])
        self.assertIsNone(asset["runtime_package"])
        self.assertFalse(asset["asset_bytes_read"])
        self.assertFalse(asset["digest_recomputed"])


class TestAbsence(unittest.TestCase):
    def test_all_fixed_probes_are_absent(self):
        fixture = reference.build_fixture()
        self.assertEqual(len(fixture["reverb_float"]), reference.FIXTURE_SAMPLES)
        audit = reference.build_report()["absence_audit"]
        self.assertTrue(audit["all_absence_probes_absent"])
        self.assertFalse(any(audit["fixed_probes"].values()))
        self.assertFalse(any(audit["home_probes"].values()))
        for key in (
            "download_performed",
            "network_used",
            "source_checkout_present",
            "weights_present",
            "runtime_present",
            "runtime_lock_present",
            "license_record_present",
            "rights_record_present",
            "cohort_manifest_present",
            "parity_manifest_present",
        ):
            self.assertFalse(audit[key], msg=key)

    def test_adapter_readme_is_present_provenance_only(self):
        report = reference.build_report()
        copies = report["asset_boundary"]["asset"]["workspace_copies"]
        self.assertEqual(len(copies), 1)
        copy = copies[0]
        self.assertTrue(copy["present"])
        self.assertFalse(copy["admitted"])
        self.assertFalse(copy["exact_candidate"])
        self.assertFalse(copy["weights_present"])
        path = reference.SOURCE_ROOT / copy["path"]
        self.assertTrue(path.is_file())
        self.assertEqual(reference.sha256_file(path), copy["sha256"])


class TestReportContract(unittest.TestCase):
    def test_disposition_is_defer_incomplete_not_qualified(self):
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["defer_before"], "offline_checkpoint_staging_and_asset_admission")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(report["qualification"]["qualified"])
        self.assertFalse(report["qualification"]["missing_result_may_qualify"])
        self.assertFalse(report["qualification"]["missing_result_promoted"])
        self.assertFalse(report["qualification"]["candidate_result_present"])
        self.assertFalse(report["qualification"]["release_claim"])

    def test_eight_blocked_release_gates(self):
        report = reference.build_report()
        self.assertEqual(report["release_gate_count"], 8)
        self.assertEqual(len(report["release_gates"]), 8)
        self.assertEqual(
            {gate["name"] for gate in report["release_gates"]}, EXPECTED_GATES
        )
        for gate in report["release_gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["evidence"])
            self.assertTrue(gate["reopen"])
        self.assertEqual(report["counts"]["release_gates_blocked"], 8)

        contract = reference.contract_payload()
        self.assertEqual(contract["release_gate_count"], 8)
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertEqual(
            {gate["name"] for gate in contract["release_gates"]}, EXPECTED_GATES
        )
        for gate in contract["release_gates"]:
            self.assertFalse(gate["qualifies"])
            self.assertEqual(gate["status"], "blocked")

    def test_no_claim_or_boundary_is_promoted(self):
        report = reference.build_report()
        for key, value in reference.CLAIMS.items():
            self.assertIs(report["claims"][key], value, msg=key)
        for key, value in reference.BOUNDARY.items():
            self.assertIs(report["boundary"][key], value, msg=key)
        self.assertTrue(report["boundary"]["installed_v0_geometry_preserved"])
        self.assertFalse(report["streaming_semantics"]["streaming_claimed"])
        self.assertFalse(report["streaming_semantics"]["v0_frame_adapter_implemented"])
        self.assertFalse(report["reference_interface"]["candidate_geometry_known"])
        self.assertIsNone(report["reference_interface"]["candidate_sampler"])
        self.assertIsNone(report["reference_interface"]["candidate_sampler_steps"])
        self.assertIsNone(report["reference_interface"]["candidate_config"])
        self.assertIsNone(report["reference_interface"]["candidate_algorithmic_latency_samples"])

    def test_upstream_scores_are_context_not_results(self):
        report = reference.build_report()
        context = report["source_reported_context"]
        self.assertEqual(context["model_id"], "nvidia/se_der_sb_16k_small")
        self.assertEqual(context["reported_license"], "CC-BY-NC-SA-4.0")
        self.assertEqual(context["reported_si_sdr_db"]["sde"], 7.4)
        self.assertEqual(context["reported_pesq"]["sde"], 2.79)
        self.assertIn("not local measurements", context["note"])
        self.assertFalse(report["claims"]["quality_claim"])
        self.assertFalse(report["claims"]["exact_parity_claim"])

    def test_rights_are_unresolved(self):
        rights = reference.build_report()["rights"]
        self.assertFalse(rights["entry_present"])
        self.assertTrue(rights["blocked"])
        for key in (
            "acquisition",
            "evaluation",
            "redistribution",
            "customer_deployment",
            "public_playback",
            "output_use",
        ):
            self.assertEqual(rights[key], "unknown", msg=key)
        self.assertTrue(rights["noncommercial"])
        self.assertTrue(rights["share_alike"])
        self.assertFalse(rights["packaging_permitted"])
        self.assertEqual(rights["license_review"], "upstream_reported_not_reviewed")


class TestPackaging(unittest.TestCase):
    def test_local_file_set(self):
        present = {
            path.name
            for path in HERE.iterdir()
            if path.is_file() and path.suffix != ".pyc"
        }
        expected = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
        self.assertEqual(present, expected)

    def test_report_and_contract_are_deterministic(self):
        self.assertEqual(
            cli.report_bytes(), (HERE / "report.json").read_bytes()
        )
        self.assertEqual(
            cli.contract_bytes(cli.contract_pins()),
            (HERE / "contract.json").read_bytes(),
        )
        self.assertEqual(
            cli.manifest_bytes(), (HERE / "SOURCES.sha256").read_bytes()
        )

    def test_report_sidecar_and_three_cold_starts(self):
        digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            f"{digest}  report.json\n",
        )
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        digests = []
        for _ in range(3):
            result = subprocess.run(
                [sys.executable, "-B", str(HERE / "run.py"), "--digest"],
                cwd=str(HERE),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            digests.append(result.stdout.strip())
        self.assertEqual(len(set(digests)), 1)
        self.assertEqual(digests[0], digest)

    def test_sidecars_and_headers(self):
        for name in SIDECAR_FILES:
            self.assertEqual(
                (HERE / name).read_text(encoding="ascii"), SIDECAR
            )
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            head = (HERE / name).read_text(encoding="utf-8").splitlines()[:2]
            self.assertEqual(head, ["# " + SPDX_C, "# " + SPDX_L], msg=name)
        head = (HERE / "README.md").read_text(encoding="utf-8").splitlines()[:2]
        self.assertEqual(
            head, ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"]
        )

    def test_readme_phrases_and_digest_table(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        for phrase in (
            "DEFER",
            "not_qualified",
            "incomplete",
            "eight",
            "caller-supplied",
            "no candidate",
            "blocked",
            "rights",
        ):
            self.assertIn(phrase, text)
        block = text.split("<!-- DIGEST_TABLE_START -->", 1)[1].split(
            "<!-- DIGEST_TABLE_END -->", 1
        )[0]
        for name in cli.TABLE_FILES:
            payload = (HERE / name).read_bytes()
            row = (
                f"| `{name}` | `{hashlib.sha256(payload).hexdigest()}` | "
                f"{len(payload)} |"
            )
            self.assertIn(row, block)

    def test_pins_exist_and_match(self):
        for raw, digest in reference.SOURCE_PINS.items():
            path = reference.SOURCE_ROOT / raw
            self.assertTrue(path.is_file(), msg=raw)
            self.assertEqual(reference.sha256_file(path), digest, msg=raw)
        for raw, digest in reference.BOUNDARY_PINS.items():
            path = reference.SDK_ROOT / raw
            self.assertTrue(path.is_file(), msg=raw)
            self.assertEqual(reference.sha256_file(path), digest, msg=raw)
        for raw, digest in reference.SIBLING_PINS.items():
            path = reference.SDK_ROOT / raw
            self.assertTrue(path.is_file(), msg=raw)
            self.assertEqual(reference.sha256_file(path), digest, msg=raw)

    def test_no_forbidden_network_tokens(self):
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            text = (HERE / name).read_text(encoding="utf-8")
            for token in (
                "import " + "requests",
                "import " + "urllib",
                "import " + "socket",
                "url" + "open",
                "url" + "retrieve",
                "pip " + "install",
            ):
                self.assertNotIn(token, text, msg=name + ":" + token)

    def test_report_has_no_mutable_board_field_in_stable_identity(self):
        report = reference.build_report()
        identity = report["task_identity"]
        for key in reference.MUTABLE_BOARD_FIELDS:
            self.assertNotIn(key, identity)
        self.assertNotIn("plan/swarm/TASKS.json", json.dumps(report["pins"]))
        self.assertFalse(report["board_policy"]["full_file_hashed"])
        self.assertTrue(report["board_policy"]["stable_fields_only"])


if __name__ == "__main__":
    unittest.main()

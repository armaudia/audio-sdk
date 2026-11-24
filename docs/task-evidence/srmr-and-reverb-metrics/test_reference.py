# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local evidence tests; stdlib only, no network or installed scorer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import reference
import run
import scorer

HERE = Path(__file__).resolve().parent
ADAPTER_REF = {"kind": "task-local", "id": "srmr-reverb-evidence-adapter/0.1", "revision": 1}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class EvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = _read_json(reference.REPORT_FILE)
        cls.crosscheck = _read_json(reference.CROSSCHECK_FILE)
        cls.source = reference.clean_source()
        spec = reference.ROOM_SPECS["medium_rt60"]
        cls.medium_rir = reference.synthetic_rir(spec["rt60_ms"], spec["seed"])
        cls.medium_input = reference.convolve_source(cls.medium_rir)

    def test_fixture_digests_and_representative_result(self) -> None:
        spec = self.report["fixture_spec"]
        self.assertEqual(self.report["cohort"]["dry_source"]["digest"],
                         reference.tensor_digest(self.source))
        self.assertEqual(spec["rir_digests"]["medium_rt60"],
                         reference.tensor_digest(self.medium_rir))
        representative = self.report["controls"]["representative_valid"]
        self.assertEqual(representative["digest"],
                         reference.tensor_digest(self.medium_input))
        score, reason = scorer.srmr(self.medium_input)
        self.assertIsNone(reason)
        self.assertEqual(reference._round(score), representative["srmr"])

    def test_crosscheck_vectors_are_reproduced(self) -> None:
        for vector in self.crosscheck["vectors"]:
            samples = (self.source if vector["case_id"] == "dry_source"
                       else self.medium_input)
            self.assertEqual(vector["input_f32_sha256"],
                             reference.tensor_digest(samples))
            score, reason = scorer.srmr(samples)
            self.assertIsNone(reason)
            self.assertLessEqual(abs(score - vector["port_score"]), 1e-12)
            self.assertLessEqual(vector["abs_delta"],
                                 scorer.CROSSCHECK_ABS_TOLERANCE)

    def test_invalid_missing_and_opt_in_cases_rejected(self) -> None:
        self.assertEqual(scorer.srmr(None), (None, "missing_samples"))
        self.assertEqual(scorer.srmr([]), (None, "empty_samples"))
        self.assertEqual(scorer.srmr([0.0] * scorer.MIN_SAMPLES),
                         (None, "zero_energy"))
        self.assertEqual(scorer.srmr(self.source, 48000),
                         (None, "unsupported_sample_rate"))
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(json.dumps({
                "protocol_version": 1,
                "operation": "score",
                "adapter_ref": ADAPTER_REF,
                "configuration": {"opt_in": False, "sample_rate_hz": 16000},
                "case_id": "medium_rt60_input",
                "samples": None,
            }), encoding="utf-8")
            with self.assertRaises(run.RequestError):
                run.process_file(request_path, result_path)
            request_path.write_text(json.dumps({
                "protocol_version": 1,
                "operation": "score",
                "adapter_ref": ADAPTER_REF,
                "configuration": {"opt_in": True, "sample_rate_hz": 16000},
                "case_id": "not_a_fixture",
                "samples": None,
            }), encoding="utf-8")
            self.assertEqual(run.process_file(request_path, result_path)["reason"],
                             "unknown_fixture_case")

    def test_manifests_are_off_unregistered_and_private(self) -> None:
        adapter = _read_json(reference.ADAPTER_FILE)
        provider = _read_json(reference.PROVIDER_FILE)
        contract = _read_json(reference.CONTRACT_FILE)
        self.assertFalse(adapter["default_enabled"])
        self.assertTrue(adapter["opt_in_required"])
        self.assertEqual(adapter["registration"], "unregistered-developer-only")
        self.assertFalse(provider["default_enabled"])
        self.assertFalse(provider["registered"])
        self.assertFalse(provider["processor_exposure"])
        self.assertFalse(contract["public_boundary"]["public_api_abi_changed"])
        self.assertEqual(contract["verification_profile"], "evidence")

    def test_evidence_kinds_and_failed_items_are_pinned(self) -> None:
        kinds = self.report["evidence_kinds"]
        self.assertEqual(kinds["paired_synthetic"]["status"], "present")
        self.assertEqual(kinds["human"]["status"], "none")
        self.assertEqual(kinds["source_reported"]["status"], "excluded_from_results")
        self.assertEqual(kinds["public_benchmark"]["status"], "none")
        self.assertEqual(len(self.report["failed_items"]), 5)
        self.assertFalse(self.report["aggregation"]["selection_performed"])
        self.assertEqual(self.report["decision"]["sdk_processor"], "defer")

    def test_report_regeneration_is_byte_identical(self) -> None:
        original_report = run.REPORT_PATH
        original_digest = run.DIGEST_PATH
        committed = reference.REPORT_FILE.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "report.json"
            digest_path = Path(directory) / "report.json.sha256"
            run.REPORT_PATH = report_path
            run.DIGEST_PATH = digest_path
            try:
                digests = [run.generate_report() for _ in range(3)]
                payloads = [report_path.read_bytes() for _ in range(1)]
                sidecar = digest_path.read_text(encoding="ascii")
            finally:
                run.REPORT_PATH = original_report
                run.DIGEST_PATH = original_digest
        self.assertEqual(len(set(digests)), 1)
        self.assertEqual(payloads[0], committed)
        self.assertEqual(sidecar, digests[0] + "\n")


if __name__ == "__main__":
    unittest.main()

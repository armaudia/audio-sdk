# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the ASR word-timestamp evidence package.

No network, no ASR engine, no model, no runtime and no audio are used. Every
check is standard-library only.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".joblib", ".lib",
    ".m4a", ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus",
    ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so",
    ".wasm", ".wav", ".weights", ".zip", ".dict", ".TextGrid",
}
FORBIDDEN_IMPORTS = {
    "numpy", "scipy", "soundfile", "librosa", "onnxruntime", "torch", "vosk",
    "sherpa_onnx", "faster_whisper", "ctranslate2", "transformers",
    "requests", "urllib3", "httpx", "aiohttp",
}


class StrictJsonTests(unittest.TestCase):
    def _read(self, payload: str) -> dict:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "doc.json"
            path.write_text(payload, encoding="utf-8")
            return reference.read_strict_json(path)

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._read('{"a":1,"a":2}')

    def test_nan_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._read('{"a":NaN}')

    def test_infinity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._read('{"a":Infinity}')

    def test_non_object_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._read("[]")

    def test_canonical_bytes_are_stable(self) -> None:
        document = {"b": 2, "a": [3, 1]}
        self.assertEqual(reference.canonical_bytes(document),
                         reference.canonical_bytes(copy.deepcopy(document)))
        self.assertTrue(reference.canonical_text(document).endswith("\n"))

    def test_float_rejected_in_canonical_report(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_report({"value": 1.5})


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_validates(self) -> None:
        reference.validate_contract(self.contract)

    def test_machine_readable_disposition(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.contract["qualification"]["not_qualified"])
        self.assertFalse(self.contract["qualification"]["real_result_present"])
        self.assertTrue(
            self.contract["qualification"]["all_release_gates_blocked"])

    def test_eight_blocked_release_gates(self) -> None:
        gates = self.contract["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             self.contract["boundary"]["linked_row"])

    def test_required_artifacts(self) -> None:
        artifacts = self.contract["required_artifacts"]
        self.assertEqual(len(artifacts), 7)
        self.assertTrue(artifacts[0]["present"])
        self.assertTrue(artifacts[0]["verified"])
        self.assertFalse(artifacts[0]["blocked"])
        for artifact in artifacts[1:]:
            self.assertTrue(artifact["blocked"])
            self.assertFalse(artifact["verified"])
        # Model bytes exist but rights are unverified: present yet blocked.
        model = next(row for row in artifacts if row["id"] == "ART-03")
        self.assertTrue(model["present"])
        self.assertFalse(model["verified"])
        self.assertTrue(model["blocked"])

    def test_exact_blockers(self) -> None:
        blockers = self.contract["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        artifact_ids = {row["id"] for row in
                        self.contract["required_artifacts"]}
        gate_ids = {row["id"] for row in self.contract["release_gates"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertTrue(blocker["required_action"])
            for gate in blocker["linked_gates"]:
                self.assertIn(gate, gate_ids)

    def test_rate_profile_rows_all_blocked(self) -> None:
        rows = self.contract["rate_profile_requirements"]
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertEqual(row["status"], "blocked")
        self.assertEqual(self.contract["profile"], "rate")
        self.assertEqual(self.report["rate_profile"]["blocked_rows"], 8)

    def test_boundary_uses_stable_identity_only(self) -> None:
        boundary = self.contract["boundary"]
        self.assertTrue(boundary["linked_row_identity_only"])
        self.assertFalse(boundary["board_file_pinned"])
        self.assertFalse(boundary["mutable_board_fields_gate"])
        self.assertEqual(set(boundary["projected_fields"]),
                         set(reference.BOARD_ROW_FIELDS))
        self.assertNotIn("status", boundary["linked_row"])
        self.assertNotIn("owner", boundary["linked_row"])
        self.assertNotIn("review", boundary["linked_row"])
        self.assertEqual(boundary["linked_row_sha256"],
                         reference.board_row_digest(boundary["linked_row"]))
        self.assertEqual(len(boundary["linked_rows"]), 4)

    def test_model_bytes_present_but_unqualified(self) -> None:
        models = self.contract["exact_models"]
        self.assertEqual(set(models), {"vosk", "sherpa_whisper_tiny_en"})
        for model in models.values():
            self.assertTrue(model["present_bytes"])
            self.assertTrue(model["digests_verified"])
            self.assertFalse(model["rights_verified"])
            self.assertFalse(model["terms_reviewed"])
            self.assertFalse(model["output_use_defined"])
            self.assertFalse(model["loaded_or_executed_here"])
            self.assertFalse(model["qualifies"])
            self.assertIsNone(model["source_revision"])

    def test_report_is_deterministic(self) -> None:
        first = reference.canonical_report(self.report)
        second = reference.canonical_report(reference.build_report())
        self.assertEqual(first, second)
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_admission_has_one_accepted_shape_only(self) -> None:
        admission = self.report["admission"]
        self.assertTrue(admission["all_cases_match"])
        self.assertTrue(admission["structural_only"])
        self.assertFalse(admission["qualifies"])
        self.assertEqual(admission["accepted_count"], 1)
        accepted = [row for row in admission["cases"]
                    if row["observed"] == "accepted"]
        self.assertEqual(accepted[0]["id"], "valid_shape_control")
        for row in admission["cases"]:
            self.assertFalse(row["qualifies"])

    def test_synthetic_rate_control_is_not_evidence(self) -> None:
        control = self.report["scorer_control"]
        self.assertTrue(control["matches"])
        self.assertFalse(control["qualifies"])
        self.assertEqual(control["kind"],
                         "synthetic_arithmetic_control_not_evidence")
        self.assertEqual(control["observed"]["words_per_minute_total"],
                         "75.000")
        self.assertEqual(control["observed"]["words_per_minute_speech"],
                         "300.000")
        self.assertEqual(control["observed"]["pause_ratio"], "0.750")


class ArithmeticTests(unittest.TestCase):
    def test_exact_rate_control(self) -> None:
        control = reference.rate_control()
        self.assertEqual(control["expected"], control["observed"])

    def test_overlap_rejected(self) -> None:
        words = [
            {"start_s": "0.0", "end_s": "0.5"},
            {"start_s": "0.4", "end_s": "0.9"},
        ]
        with self.assertRaises(ValueError):
            reference.word_rate(words, "1.0")

    def test_zero_length_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.word_rate([{"start_s": "0.5", "end_s": "0.5"}], "1.0")

    def test_negative_and_nonfinite_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.word_rate([{"start_s": "-0.1", "end_s": "0.2"}], "1.0")
        with self.assertRaises(ValueError):
            reference.word_rate([{"start_s": "NaN", "end_s": "0.2"}], "1.0")
        with self.assertRaises(ValueError):
            reference.word_rate([{"start_s": "0.0", "end_s": "0.2"}],
                                "Infinity")

    def test_beyond_duration_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.word_rate([{"start_s": "0.0", "end_s": "1.5"}], "1.0")


class ManifestTests(unittest.TestCase):
    def test_control_manifest_admissible(self) -> None:
        reference.validate_manifest(reference.control_manifest())

    def test_every_admission_case_matches(self) -> None:
        cases = reference.admission_cases()
        self.assertEqual(len(cases), 37)
        for row in cases:
            self.assertEqual(row["observed"], row["expected"], row["id"])
            self.assertFalse(row["qualifies"])

    def test_adverse_mutations_rejected(self) -> None:
        base = reference.control_manifest()
        mutations = (
            ("nan", ("outcomes", "boundary_mae_ms"), "NaN"),
            ("infinity", ("hypothesis", "words", 0, "end_s"), "Infinity"),
            ("missing", ("reference", "independent_of_asr"), False),
            ("qualified", ("rights", "claims_qualified"), True),
            ("stereo", ("audio", "channels"), 2),
        )
        for name, path, value in mutations:
            document = copy.deepcopy(base)
            target = document
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.assertRaises(ValueError, msg=name):
                reference.validate_manifest(document)

    def test_nonfinite_literal_rejected_by_parser(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.json"
            path.write_text('{"a":Infinity}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)


class PinTests(unittest.TestCase):
    def test_source_pins_match(self) -> None:
        for relative, expected in reference.SOURCE_PINS.items():
            self.assertEqual(
                reference.sha256_file(reference.AUDIO_ROOT / relative),
                expected, relative)

    def test_boundary_and_sibling_pins_match(self) -> None:
        for group in (reference.BOUNDARY_PINS, reference.SIBLING_PINS):
            for relative, expected in group.items():
                self.assertEqual(
                    reference.sha256_file(reference.WORKTREE / relative),
                    expected, relative)

    def test_present_model_bytes_if_present(self) -> None:
        for model in (reference.VOSK_MODEL, reference.SHERPA_MODEL):
            root = reference.AUDIO_ROOT / model["relative"]
            if not root.is_dir():
                continue
            digest, count, size = reference.tree_digest(root)
            self.assertEqual(digest, model["tree_sha256"])
            self.assertEqual(count, model["file_count"])
            self.assertEqual(size, model["byte_count"])
            for relative, expected in model["files"].items():
                self.assertEqual(
                    reference.sha256_file(root / relative), expected)

    def test_runtime_files_if_present(self) -> None:
        root = reference.AUDIO_ROOT / reference.SCRATCH_ROOT
        for relative, expected in reference.RUNTIME_FILES.items():
            path = root / relative
            if not path.is_file():
                continue
            self.assertEqual(reference.sha256_file(path), expected)

    def test_sources_manifest_excludes_mutable_board(self) -> None:
        payload = run.sources_bytes().decode("ascii")
        self.assertNotIn("plan/swarm/TASKS.json", payload)
        self.assertIn("source:cpp-library/pipeline-validation/"
                      "playback-speed-candidates.md", payload)

    def test_contract_and_report_are_canonical(self) -> None:
        payload, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(hashlib.sha256(payload.encode()).hexdigest(), digest)
        self.assertEqual(
            payload,
            reference.canonical_text(json.loads(payload)))
        contract_payload = reference.canonical_bytes(reference.build_contract())
        self.assertEqual(contract_payload,
                         reference.canonical_bytes(
                             json.loads(contract_payload)))


class ContentHygieneTests(unittest.TestCase):
    def test_no_forbidden_suffixes_in_task_directory(self) -> None:
        for path in HERE.rglob("*"):
            if path.is_file():
                self.assertNotIn(path.suffix, FORBIDDEN_SUFFIXES, path.name)

    def test_no_forbidden_imports(self) -> None:
        for name in ("reference.py", "run.py", "verify.py",
                     "test_reference.py"):
            text = (HERE / name).read_text(encoding="utf-8")
            for root in FORBIDDEN_IMPORTS:
                for prefix in (f"import {root}", f"from {root}"):
                    self.assertNotIn(prefix, text, name + ":" + root)

    def test_no_network_calls(self) -> None:
        tokens = ("url" + "open", "url" + "retrieve", "requests" + ".get",
                  "wg" + "et", "cu" + "rl ")
        for name in ("reference.py", "run.py", "verify.py",
                     "test_reference.py"):
            text = (HERE / name).read_text(encoding="utf-8")
            for token in tokens:
                self.assertNotIn(token, text, name + ":" + token)

    def test_decimal_normalisation(self) -> None:
        self.assertEqual(
            reference.format_duration(Decimal("1.00")), "1.0")
        self.assertEqual(
            reference.format_duration(Decimal("4.0")), "4.0")


if __name__ == "__main__":
    unittest.main()

# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for SDK-NEUTTS-AIR-GATED-CHECKPOINT-LEAD.

Standard library only. No network, no model, no runtime, no audio decoding and
no filesystem writes outside the interpreter's own test process. Every test
must pass; there are no skips.
"""

from __future__ import annotations

import copy
import hashlib
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

TASK_DIR = HERE

SPDX_LICENSE_LINE = "SPDX-License-" "Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX-FileCopyright" "Text: 2026 Tsakanyan Hovhannes"


def control() -> dict:
    return reference._manifest_control()


def fresh_control() -> dict:
    return copy.deepcopy(control())


def rejected(document) -> dict:
    return reference.validate_manifest(document, probe_paths=False)


class StrictJsonTests(unittest.TestCase):
    def test_rejects_nan(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"x": NaN}')

    def test_rejects_infinity(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"x": Infinity}')

    def test_rejects_negative_infinity(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"x": -Infinity}')

    def test_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"x": 1, "x": 2}')

    def test_rejects_byte_order_mark(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('\ufeff{"x": 1}')

    def test_rejects_non_object_root(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict("[1, 2, 3]")

    def test_canonical_sorts_and_compacts(self) -> None:
        text = reference.canonical_text({"b": 2, "a": 1})
        self.assertEqual(text, '{"a":1,"b":2}\n')

    def test_canonical_rejects_nonfinite(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_text({"x": float("nan")})

    def test_canonical_is_stable(self) -> None:
        document = {"z": [1, 2], "a": {"y": True, "x": None}}
        first = reference.canonical_bytes(document)
        second = reference.canonical_bytes(document)
        self.assertEqual(first, second)
        self.assertEqual(hashlib.sha256(first).hexdigest(),
                         reference.object_digest(document))

    def test_no_floats_rejects_nested_nan(self) -> None:
        with self.assertRaises(ValueError):
            reference._no_floats({"a": [{"b": 1.5}]})

    def test_no_floats_accepts_ints_and_none(self) -> None:
        reference._no_floats({"a": [1, None, True, "x"]})

    def test_sha256_file_matches_hashlib(self) -> None:
        target = TASK_DIR / "reference.py"
        self.assertEqual(reference.sha256_file(target),
                         hashlib.sha256(target.read_bytes()).hexdigest())


class ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = reference.build_contract()

    def test_identity_and_disposition(self) -> None:
        self.assertEqual(self.contract["task"],
                         "SDK-NEUTTS-AIR-GATED-CHECKPOINT-LEAD")
        self.assertEqual(self.contract["component"],
                         "neutts-air-gated-checkpoint-lead")
        self.assertEqual(self.contract["title"],
                         "NeuTTS Air / gated checkpoint lead")
        self.assertEqual(self.contract["mode"], "feasibility")
        self.assertEqual(self.contract["profile"], "Voice")
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.contract["proposal_only"])

    def test_board_not_pinned(self) -> None:
        self.assertFalse(self.contract["board_file_pinned"])
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)

    def test_board_projection_is_stable_fields_only(self) -> None:
        self.assertEqual(set(self.contract["board_row_projection"]),
                         set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(
            self.contract["board_row_sha256"],
            reference.board_row_digest(reference.BOARD_ROW_PROJECTION))
        self.assertEqual(
            self.contract["linked_rows_sha256"],
            reference.linked_rows_digest())

    def test_eight_blocked_gates(self) -> None:
        gates = self.contract["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             reference.BOARD_ROW_PROJECTION)

    def test_six_artifacts_one_source_five_blocked(self) -> None:
        artifacts = self.contract["required_artifacts"]
        self.assertEqual(len(artifacts), 6)
        self.assertTrue(artifacts[0]["present"])
        self.assertFalse(artifacts[0]["blocked"])
        for artifact in artifacts[1:]:
            self.assertFalse(artifact["present"])
            self.assertFalse(artifact["verified"])
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])

    def test_five_open_blockers(self) -> None:
        blockers = self.contract["exact_blockers"]
        self.assertEqual(len(blockers), 5)
        artifact_ids = {row["id"] for row in
                        self.contract["required_artifacts"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertTrue(blocker["required_action"])
            self.assertTrue(blocker["linked_gates"])

    def test_voice_rows_are_blocked(self) -> None:
        rows = self.contract["voice_profile_requirements"]
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertEqual(row["status"], "blocked")
        self.assertEqual(len(self.contract["quality_outcomes"]), 3)
        self.assertEqual(len(self.contract["timing_requirements"]), 3)

    def test_checkpoint_gate_is_closed(self) -> None:
        gate = self.contract["checkpoint_gate"]
        self.assertEqual(gate["recorded_http_status"], 401)
        self.assertEqual(
            gate["repositories"],
            ["neuphonic/neutts-air", "neuphonic/neutts-air-q4-gguf",
             "neuphonic/neutts-air-q8-gguf"])
        self.assertFalse(gate["access_grant_present"])
        self.assertFalse(gate["weights_present"])
        self.assertIsNone(gate["revision"])
        self.assertFalse(gate["admitted"])

    def test_license_conflict_is_open(self) -> None:
        review = self.contract["license_review"]
        self.assertTrue(review["conflict"])
        self.assertFalse(review["resolved"])
        self.assertEqual(review["readme_air_claim"], "Apache-2.0")
        self.assertEqual(review["repository_license_id"],
                         "NeuTTS-Open-License-1.0")
        self.assertIsNone(review["resolved_license_id"])

    def test_admission_contract_block(self) -> None:
        block = self.contract["admission_contract"]
        self.assertEqual(block["exact_source_revision"],
                         "ac69851f28fc63a487917e7c2e27f0d75c759cba")
        self.assertEqual(block["exact_llama_cpp"], "0.3.36")
        self.assertEqual(block["exact_transformers"], "5.1.0")
        self.assertEqual(block["backends"], ["torch", "gguf"])
        self.assertTrue(block["license_id_is_caller_declaration_only"])
        self.assertFalse(block["audio_read"])
        self.assertFalse(block["model_executed"])
        self.assertFalse(block["network_used"])

    def test_scope_and_boundary_claims_false(self) -> None:
        self.assertTrue(self.contract["scope"]["task_local_only"])
        self.assertTrue(self.contract["scope"]["source_present"])
        for key, value in self.contract["scope"].items():
            if key not in ("task_local_only", "source_present"):
                self.assertIs(value, False, key)
        for key, value in self.contract["boundary"].items():
            if key == "task_local_only":
                self.assertIs(value, True, key)
            else:
                self.assertIs(value, False, key)

    def test_validate_contract_accepts(self) -> None:
        reference.validate_contract(self.contract)

    def test_validate_contract_rejects_bad_disposition(self) -> None:
        broken = dict(self.contract, decision="PASS")
        with self.assertRaises(ValueError):
            reference.validate_contract(broken)

    def test_validate_contract_rejects_extra_field(self) -> None:
        broken = dict(self.contract)
        broken["extra"] = True
        with self.assertRaises(ValueError):
            reference.validate_contract(broken)


class AdmissionTests(unittest.TestCase):
    def test_control_is_accepted(self) -> None:
        result = reference.validate_manifest(control(), probe_paths=False)
        self.assertTrue(result["accepted"], result)
        self.assertGreater(result["checks"], 20)
        self.assertTrue(result["state_unchanged"])

    def test_all_adverse_cases_rejected(self) -> None:
        matrix = reference.admission_controls()
        self.assertTrue(matrix["control"]["accepted"])
        self.assertFalse(matrix["control"]["qualifies"])
        self.assertGreaterEqual(len(matrix["cases"]), 120)
        for case in matrix["cases"]:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertFalse(case["qualifies"], case["id"])
            self.assertTrue(case["state_unchanged"], case["id"])
            self.assertTrue(case["code"], case["id"])
        summary = matrix["summary"]
        self.assertEqual(summary["rejected_count"], summary["case_count"])
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertFalse(summary["audio_read"])
        self.assertFalse(summary["weights_loaded"])
        self.assertFalse(summary["model_executed"])
        self.assertFalse(summary["network_used"])

    def test_case_ids_are_unique(self) -> None:
        matrix = reference.admission_controls()
        ids = [case["id"] for case in matrix["cases"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_root_types_rejected(self) -> None:
        for payload in ([], None, "x", 7):
            self.assertFalse(rejected(payload)["accepted"])

    def test_missing_and_extra_top_fields_rejected(self) -> None:
        document = fresh_control()
        del document["rights"]
        self.assertEqual(rejected(document)["code"], "missing_field")
        document = fresh_control()
        document["extra"] = True
        self.assertEqual(rejected(document)["code"], "unknown_field")

    def test_nonfinite_outcome_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            document = fresh_control()
            document["outcomes"]["text_semantic_wer"] = value
            self.assertEqual(rejected(document)["code"], "nonfinite_value")

    def test_wrong_source_revision_rejected(self) -> None:
        document = fresh_control()
        document["source"]["revision"] = "0" * 40
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_open_license_id_rejected(self) -> None:
        document = fresh_control()
        document["source"]["license_id"] = "NeuTTS-Open-License-1.0"
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_model_card_required(self) -> None:
        document = fresh_control()
        del document["source"]["model_card_sha256"]
        self.assertEqual(rejected(document)["code"], "missing_field")
        document = fresh_control()
        document["source"]["model_card_sha256"] = "bad"
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_path_traversal_rejected(self) -> None:
        document = fresh_control()
        document["source"]["path"] = "/caller/../src"
        self.assertEqual(rejected(document)["code"], "invalid_path")

    def test_null_byte_path_rejected(self) -> None:
        document = fresh_control()
        document["references"][0]["path"] = "/caller/ref\x00.wav"
        self.assertEqual(rejected(document)["code"], "invalid_path")

    def test_duplicate_weight_name_rejected(self) -> None:
        document = fresh_control()
        document["weights"].append(dict(document["weights"][0]))
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_missing_backbone_rejected(self) -> None:
        document = fresh_control()
        document["weights"] = [document["weights"][1]]
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_missing_codec_rejected(self) -> None:
        document = fresh_control()
        document["weights"] = [row for row in document["weights"]
                               if "neucodec" not in row["name"]]
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_safetensors_backbone_accepted(self) -> None:
        document = fresh_control()
        document["weights"] = [
            {"name": "neutts-air.safetensors", "sha256": "5" * 64,
             "byte_count": 1000, "terms_sha256": "6" * 64},
            document["weights"][1],
        ]
        self.assertTrue(rejected(document)["accepted"])

    def test_torch_backend_without_llama_accepted(self) -> None:
        document = fresh_control()
        document["runtime"]["backend"] = "torch"
        document["runtime"]["llama_cpp_version"] = None
        self.assertTrue(rejected(document)["accepted"])

    def test_torch_backend_with_llama_rejected(self) -> None:
        document = fresh_control()
        document["runtime"]["backend"] = "torch"
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_gguf_backend_without_llama_rejected(self) -> None:
        document = fresh_control()
        document["runtime"]["llama_cpp_version"] = None
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_nonintegral_byte_count_rejected(self) -> None:
        for value in (1.5, True, "1000", None):
            document = fresh_control()
            document["weights"][0]["byte_count"] = value
            self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_out_of_range_byte_count_rejected(self) -> None:
        for value in (0, -1, reference.MAX_WEIGHT_BYTES + 1):
            document = fresh_control()
            document["weights"][0]["byte_count"] = value
            self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_bad_weight_sha_rejected(self) -> None:
        document = fresh_control()
        document["weights"][0]["sha256"] = "A" * 64
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_wrong_llama_cpp_rejected(self) -> None:
        document = fresh_control()
        document["runtime"]["llama_cpp_version"] = "0.3.35"
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_old_torch_rejected(self) -> None:
        document = fresh_control()
        document["runtime"]["torch_version"] = "2.7.1"
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_old_neucodec_rejected(self) -> None:
        document = fresh_control()
        document["runtime"]["neucodec_version"] = "0.0.3"
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_wrong_transformers_rejected(self) -> None:
        document = fresh_control()
        document["runtime"]["transformers_version"] = "5.2.0"
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_bad_python_version_rejected(self) -> None:
        for value in ("3.9.18", "3.14.0", 3.11):
            document = fresh_control()
            document["runtime"]["python_version"] = value
            self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_nondeterministic_rejected(self) -> None:
        document = fresh_control()
        document["runtime"]["deterministic_algorithms"] = False
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_seed_bounds_and_type(self) -> None:
        for value in (-1, reference.MAX_SEED + 1, True, 1.0):
            document = fresh_control()
            document["runtime"]["seed"] = value
            self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_thread_bounds_and_type(self) -> None:
        for value in (0, reference.MAX_THREADS + 1, True):
            document = fresh_control()
            document["runtime"]["threads"] = value
            self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_duplicate_reference_id_rejected(self) -> None:
        document = fresh_control()
        document["references"].append(dict(document["references"][0]))
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_text_reference_digest_mismatch_rejected(self) -> None:
        document = fresh_control()
        document["texts"][0]["reference_sha256"] = "0" * 64
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_text_too_long_rejected(self) -> None:
        document = fresh_control()
        document["texts"][0]["text"] = "a" * (reference.MAX_TEXT_LENGTH + 1)
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_missing_control_kind_rejected(self) -> None:
        document = fresh_control()
        document["controls"] = [row for row in document["controls"]
                                if row["kind"] != "ignore_reference"]
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_duplicate_control_kind_rejected(self) -> None:
        document = fresh_control()
        document["controls"][1]["kind"] = "fixed_voice"
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_mismatched_control_needs_declared_reference(self) -> None:
        document = fresh_control()
        document["controls"][1]["reference_id"] = "ref-missing"
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_fixed_control_must_not_name_reference(self) -> None:
        document = fresh_control()
        document["controls"][0]["reference_id"] = "ref-a"
        self.assertEqual(rejected(document)["code"], "invalid_value")

    def test_outcome_bounds_rejected(self) -> None:
        cases = (
            ("text_semantic_wer", -0.1), ("text_semantic_wer", 1.1),
            ("identity_similarity_cosine", -1.1),
            ("identity_similarity_cosine", 1.1),
            ("naturalness_mos", 0.9), ("naturalness_mos", 5.1),
            ("peak_abs", -0.1), ("peak_abs", reference.MAX_PEAK + 0.1),
            ("clipped_fraction", 1.1), ("nonfinite_count", 1),
        )
        for field, value in cases:
            document = fresh_control()
            document["outcomes"][field] = value
            self.assertEqual(rejected(document)["code"], "invalid_value", field)

    def test_nonintegral_outcomes_rejected(self) -> None:
        for field, value in (("alignment_samples", 1.5),
                             ("sample_count", 16000.0),
                             ("sample_count", True)):
            document = fresh_control()
            document["outcomes"][field] = value
            self.assertEqual(rejected(document)["code"], "invalid_value", field)

    def test_empty_rights_rejected(self) -> None:
        for field in reference.RIGHTS_FIELDS[:-1]:
            document = fresh_control()
            document["rights"][field] = ""
            self.assertEqual(rejected(document)["code"], "invalid_value", field)

    def test_panel_bounds_rejected(self) -> None:
        for value in (0, reference.MAX_PANEL + 1, True):
            document = fresh_control()
            document["rights"]["listening_panel_size"] = value
            self.assertEqual(rejected(document)["code"], "invalid_value")


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = reference.build_report()

    def test_report_rebuild_is_deterministic(self) -> None:
        again = reference.build_report()
        self.assertEqual(reference.canonical_bytes(self.report),
                         reference.canonical_bytes(again))

    def test_report_no_floats(self) -> None:
        reference._no_floats(self.report)

    def test_report_disposition(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["proposal_only"])

    def test_report_contract_digest(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(reference.build_contract()))

    def test_absent_evidence_all_absent(self) -> None:
        summary = self.report["absence_evidence"]["summary"]
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["network_used"])
        self.assertFalse(summary["weights_loaded"])
        self.assertFalse(summary["model_executed"])
        self.assertFalse(summary["audio_read"])

    def test_hf_cache_absent(self) -> None:
        cache = self.report["absence_evidence"]["observed_hf_cache"]
        self.assertFalse(cache["weights_present"])
        self.assertFalse(cache["snapshots_present"])
        self.assertFalse(cache["admitted"])
        self.assertFalse(cache["used_for_evidence"])

    def test_repository_assets_hash_only(self) -> None:
        media = self.report["absence_evidence"]["repository_bundled_assets"]
        self.assertFalse(media["admitted"])
        self.assertFalse(media["used_for_evidence"])
        self.assertFalse(media["audio_read"])
        self.assertFalse(media["decoded"])
        self.assertFalse(media["signal_loaded"])
        self.assertTrue(media["byte_hash_only"])

    def test_checkpoint_gate_closed(self) -> None:
        gate = self.report["checkpoint_gate"]
        self.assertFalse(gate["access_grant_present"])
        self.assertFalse(gate["weights_present"])
        self.assertFalse(gate["admitted"])
        self.assertEqual(gate["recorded_http_status"], 401)

    def test_license_not_resolved(self) -> None:
        review = self.report["license_review"]
        self.assertTrue(review["conflict"])
        self.assertFalse(review["resolved"])

    def test_historical_execution_not_evidence(self) -> None:
        execution = self.report["historical_execution"]
        self.assertTrue(execution["not_rerun"])
        self.assertFalse(execution["used_for_evidence"])
        self.assertFalse(execution["merged_task_evidence"])
        self.assertFalse(execution["qualifies"])
        self.assertFalse(execution["acquisition_succeeded"])
        self.assertFalse(execution["inference_attempted"])
        self.assertFalse(execution["output_present"])
        self.assertFalse(execution["runtime_build_historical_success"])
        self.assertEqual(execution["acquisition_http_status"], 401)

    def test_linked_identity(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest(
                             reference.BOARD_ROW_PROJECTION))

    def test_required_results_none_present(self) -> None:
        for key, value in self.report["required_results"].items():
            if key == "no_result_qualifies":
                self.assertTrue(value)
            else:
                self.assertFalse(value, key)

    def test_pins_verified(self) -> None:
        for rows, pins in ((self.report["source_pins"],
                            reference.SOURCE_PINS),
                           (self.report["boundary_pins"],
                            reference.BOUNDARY_PINS)):
            self.assertEqual(set(rows), set(pins))
            for path, row in rows.items():
                self.assertEqual(row["sha256"], pins[path])
                self.assertEqual(row["actual"], pins[path])
                self.assertTrue(row["verified"])

    def test_committed_report_matches_rebuild(self) -> None:
        committed = (TASK_DIR / "report.json").read_bytes()
        self.assertEqual(committed,
                         reference.canonical_bytes(self.report))

    def test_committed_sidecar_matches_report(self) -> None:
        payload = (TASK_DIR / "report.json").read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        sidecar = (TASK_DIR / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, f"{digest}  report.json\n")

    def test_report_strict_json_round_trip(self) -> None:
        text = (TASK_DIR / "report.json").read_text(encoding="utf-8")
        parsed = reference.loads_strict(text)
        self.assertEqual(parsed, self.report)

    def test_contract_strict_json_round_trip(self) -> None:
        text = (TASK_DIR / "contract.json").read_text(encoding="utf-8")
        parsed = reference.loads_strict(text)
        reference.validate_contract(parsed)
        self.assertEqual(parsed, reference.build_contract())


class PackageHygieneTests(unittest.TestCase):
    def test_no_binary_or_model_artifacts(self) -> None:
        forbidden = {".gguf", ".onnx", ".pt", ".pth", ".wav", ".flac", ".mp3",
                     ".so", ".dylib", ".dll", ".bin", ".npy", ".npz",
                     ".safetensors"}
        for path in TASK_DIR.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertFalse(path.is_symlink(), path.name)

    def test_python_spdx_headers(self) -> None:
        for path in sorted(TASK_DIR.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_LICENSE_LINE, head, path.name)
            self.assertIn(SPDX_COPYRIGHT_LINE, head, path.name)

    def test_license_sidecars(self) -> None:
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license", "SOURCES.sha256.license"):
            text = (TASK_DIR / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_LICENSE_LINE, text)

    def test_sources_manifest_excludes_self_and_board(self) -> None:
        text = (TASK_DIR / "SOURCES.sha256").read_text(encoding="ascii")
        names = [line.split("  ", 1)[1] for line in text.splitlines()
                 if line and not line.startswith("#")]
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", names)
        self.assertNotIn(reference.BOARD_TASK_ROW, names)
        self.assertNotIn("source:" + reference.BOARD_TASK_ROW, names)
        for relative in reference.SOURCE_PINS:
            self.assertIn("source:" + relative, names)
        for relative in reference.BOUNDARY_PINS:
            self.assertIn(relative, names)
        for name in run.LOCAL_PIN_FILES:
            self.assertIn(reference.TASK_PREFIX + name, names)

    def test_required_deliverables_present(self) -> None:
        for name in ("README.md", "LICENSES.md", "contract.json",
                     "reference.py", "report.json", "report.json.sha256",
                     "SOURCES.sha256", "verify.py", "test_reference.py",
                     "run.py"):
            self.assertTrue((TASK_DIR / name).is_file(), name)

    def test_board_row_unique(self) -> None:
        board = reference.AUDIO_ROOT / reference.BOARD_TASK_ROW
        projection = reference.board_row_projection(board)
        self.assertEqual(projection, reference.BOARD_ROW_PROJECTION)

    def test_admission_control_is_not_evidence(self) -> None:
        matrix = reference.admission_controls()
        self.assertEqual(matrix["control"]["evidence_class"],
                         "synthetic_schema_control_not_evidence")
        self.assertTrue(matrix["control"]["accepted"])
        self.assertFalse(matrix["control"]["qualifies"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

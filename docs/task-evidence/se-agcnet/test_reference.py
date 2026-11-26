# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Task-local tests for SDK-SE-AGCNET blocker evidence."""

from __future__ import annotations

import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

    def test_nonfinite_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                reference.loads_strict('{"a":' + token + '}')

    def test_float_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1.5}')

    def test_root_must_be_object(self) -> None:
        with self.assertRaises(ValueError):
            reference.read_strict_json(Path(__file__))

    def test_canonical_bytes_stable(self) -> None:
        value = {"b": [1, 2], "a": {"d": True, "c": None}}
        self.assertEqual(reference.canonical_bytes(value), b'{"a":{"c":null,"d":true},"b":[1,2]}')
        self.assertEqual(reference.object_digest(value), hashlib.sha256(reference.canonical_bytes(value)).hexdigest())


class BoardIdentityTests(unittest.TestCase):
    def test_projection_fields(self) -> None:
        projection = reference.board_row_projection()
        self.assertEqual(tuple(projection.keys()), reference.BOARD_ROW_FIELDS)
        self.assertEqual(projection["id"], reference.TASK)
        self.assertEqual(projection["component"], reference.COMPONENT_ID)

    def test_linked_rows_cover_task_and_dependencies(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual([r["id"] for r in rows], list(reference.LINKED_ROW_IDS))

    def test_mutable_fields_do_not_change_projection(self) -> None:
        row = copy.deepcopy(reference.board_row_projection())
        changed = copy.deepcopy(row)
        changed["status"] = "done"
        changed["owner"] = "other"
        changed["review"] = {"ok": True}
        self.assertEqual(reference._project(row, True), reference._project({**changed, "id": row["id"], "title": row["title"], "component": row["component"], "mode": row["mode"], "repository": row["repository"], "depends_on": row["depends_on"]}, True))

    def test_stable_identity_change_changes_projection(self) -> None:
        row = reference.board_row_projection()
        changed = copy.deepcopy(row)
        changed["title"] = "changed"
        self.assertNotEqual(reference.board_row_digest(row), reference.board_row_digest(changed))

    def test_mutable_board_not_pinned(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        self.assertNotIn(reference.BOARD_TASK_ROW, text)


class AbsenceTests(unittest.TestCase):
    def test_all_fixed_probes_absent(self) -> None:
        probes = reference.all_probes()
        self.assertEqual([p["path"] for p in probes if p["present"]], [])
        summary = reference.absence_summary(probes)
        self.assertTrue(summary["all_probes_absent"])
        self.assertEqual(summary["present_count"], 0)
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["network_used"])

    def test_probe_counts(self) -> None:
        summary = reference.absence_summary()
        self.assertEqual(summary["probe_count"], 18)
        self.assertEqual(summary["workspace_probe_count"], 10)
        self.assertEqual(summary["worktree_probe_count"], 5)
        self.assertEqual(summary["home_probe_count"], 3)

    def test_present_probe_would_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x"
            p.write_text("x", encoding="utf-8")
            summary = reference.absence_summary([{"path": str(p), "present": True, "searched_workspace": True, "searched_sdk_worktree": False, "searched_home_cache": False}])
            self.assertEqual(summary["present_count"], 1)
            self.assertFalse(summary["all_probes_absent"])


class EvidenceTests(unittest.TestCase):
    def test_evidence_inputs_pinned(self) -> None:
        rows = reference.evidence_inputs()
        self.assertEqual(len(rows), len(reference.SOURCE_PINS))
        for row in rows:
            self.assertEqual(row["sha256"], reference.SOURCE_PINS[row["path"]])
            self.assertFalse(row["admitted_as_result"])

    def test_recorded_identity_not_local(self) -> None:
        ident = reference.recorded_identity_block()
        self.assertFalse(ident["locally_present"])
        self.assertFalse(ident["locally_verified"])
        self.assertFalse(ident["admitted_as_result"])
        self.assertIsNone(ident["model_revision"])

    def test_reported_metrics_not_qualifying(self) -> None:
        metrics = reference.reported_metrics_block()
        self.assertFalse(metrics["admitted_as_result"])
        self.assertFalse(metrics["qualifies"])
        self.assertIsNone(metrics["pesq"])


class ManifestTests(unittest.TestCase):
    def test_control_accepted_not_qualified(self) -> None:
        result = reference.validate_manifest(reference._manifest_control())
        self.assertEqual(result["status"], "accepted")
        self.assertFalse(result["qualifies"])
        self.assertTrue(result["synthetic_schema_control"])

    def test_admission_cases_cover_rejections(self) -> None:
        admission = reference.admission_controls()
        summary = admission["summary"]
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertGreaterEqual(summary["rejected_count"], 10)
        for case in admission["cases"]:
            self.assertFalse(case["qualifies"], case["id"])
            if case["id"] != "accept_synthetic_control":
                self.assertEqual(case["status"], "rejected", case["id"])
                self.assertTrue(case["state_unchanged"], case["id"])

    def test_missing_field(self) -> None:
        m = reference._manifest_control()
        m.pop("source")
        self.assertEqual(reference.validate_manifest(m)["code"], "missing_field")

    def test_unknown_field(self) -> None:
        m = reference._manifest_control()
        m["extra"] = 1
        self.assertEqual(reference.validate_manifest(m)["code"], "unknown_field")

    def test_stereo_rejected(self) -> None:
        m = reference._manifest_control()
        m["geometry"]["channels"] = 2
        self.assertEqual(reference.validate_manifest(m)["code"], "invalid_channels")

    def test_wrong_rate_rejected(self) -> None:
        m = reference._manifest_control()
        m["geometry"]["sample_rate_hz"] = 48000
        self.assertEqual(reference.validate_manifest(m)["code"], "invalid_sample_rate_hz")

    def test_wrong_frame_rejected(self) -> None:
        m = reference._manifest_control()
        m["geometry"]["frame_samples"] = 320
        self.assertEqual(reference.validate_manifest(m)["code"], "invalid_frame_samples")

    def test_bad_digest_rejected(self) -> None:
        m = reference._manifest_control()
        m["checkpoint"]["sha256"] = "bad"
        self.assertEqual(reference.validate_manifest(m)["code"], "invalid_digest")

    def test_python_mismatch_rejected(self) -> None:
        m = reference._manifest_control()
        m["runtime"]["python_version"] = "3.11.0"
        self.assertEqual(reference.validate_manifest(m)["code"], "invalid_python_version")


class ReportTests(unittest.TestCase):
    def test_contract_and_report_disposition(self) -> None:
        contract = reference.build_contract()
        report = reference.build_report()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertTrue(contract["proposal_only"])
        self.assertTrue(contract["incomplete"])
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["contract_sha256"], reference.object_digest(contract))

    def test_all_gates_blocked(self) -> None:
        report = reference.build_report()
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["gates"]))

    def test_artifacts_blocked(self) -> None:
        report = reference.build_report()
        self.assertEqual(len(report["required_artifacts"]), 7)
        for a in report["required_artifacts"]:
            self.assertFalse(a["present"])
            self.assertFalse(a["verified"])
            self.assertTrue(a["blocked"])
            self.assertIsNone(a["sha256"])

    def test_blockers_open(self) -> None:
        report = reference.build_report()
        self.assertEqual(len(report["exact_blockers"]), 6)
        for b in report["exact_blockers"]:
            self.assertEqual(b["status"], "open")
            self.assertFalse(b["qualifies"])

    def test_canonical_report_digest(self) -> None:
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        self.assertEqual(digest, report["canonical_report"]["canonical_digest"])
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(), digest)

    def test_no_forbidden_files(self) -> None:
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), reference.FORBIDDEN_SUFFIXES, path.name)


if __name__ == "__main__":
    unittest.main()

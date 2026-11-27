# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for SDK-WAVEFIT blocker evidence."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


class WaveFitReferenceTest(unittest.TestCase):
    def test_contract_canonical(self):
        c = reference.build_contract()
        reference.validate_contract(c)
        self.assertEqual(c["decision"], "DEFER")
        self.assertEqual(c["status"], "incomplete")
        self.assertEqual(c["qualification_status"], "not_qualified")

    def test_report_canonical(self):
        r = reference.build_report()
        text, digest = reference.canonical_report(r)
        self.assertTrue(text.endswith("}"))
        self.assertEqual(len(digest), 64)
        text2, digest2 = reference.canonical_report(r)
        self.assertEqual(digest2, digest)

    def test_eight_gates_blocked(self):
        r = reference.build_report()
        self.assertEqual(len(r["gates"]), 8)
        for g in r["gates"]:
            self.assertEqual(g["status"], "blocked")
            self.assertFalse(g["qualifies"])

    def test_five_blockers_open(self):
        r = reference.build_report()
        self.assertEqual(len(r["exact_blockers"]), 5)
        for b in r["exact_blockers"]:
            self.assertEqual(b["status"], "open")
            self.assertFalse(b["qualifies"])

    def test_required_artifacts_blocked_except_research(self):
        r = reference.build_report()
        arts = r["required_artifacts"]
        self.assertEqual(len(arts), 6)
        self.assertTrue(arts[0]["present"])
        for a in arts[1:]:
            self.assertFalse(a["present"])
            self.assertTrue(a["blocked"])

    def test_board_projection_gated_not_mutable(self):
        c = reference.build_contract()
        self.assertFalse(c["board_file_pinned"])
        self.assertEqual(c["board_row_projection"]["id"], "SDK-WAVEFIT")
        self.assertEqual(c["board_row_sha256"], reference.board_row_digest())

    def test_absence_probes_all_absent(self):
        probes = reference.absence_probes(reference.AUDIO_ROOT)
        home = reference.home_absence_probes()
        summary = reference.absence_summary(probes, home)
        self.assertTrue(summary["all_probes_absent"])
        self.assertEqual(summary["present_count"], 0)
        self.assertFalse(summary["recursive_workspace_walk"])

    def test_admission_control_accepts_schema_control(self):
        adm = reference.admission_controls()
        self.assertTrue(adm["control"]["accepted"])
        self.assertEqual(adm["summary"]["qualifying_results"], 0)
        self.assertFalse(adm["summary"]["model_executed"])

    def test_admission_rejects_missing_fields(self):
        for field in reference.MANIFEST_FIELDS:
            d = reference._manifest_control()
            del d[field]
            res = reference.validate_manifest(d, probe_paths=False)
            self.assertFalse(res["accepted"], field)

    def test_admission_rejects_unknown_field(self):
        d = reference._manifest_control()
        d["extra"] = "x"
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])
        self.assertEqual(res["code"], "unknown_field")

    def test_admission_rejects_bad_schema(self):
        d = reference._manifest_control()
        d["schema_id"] = "wrong"
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_non_cpu(self):
        d = reference._manifest_control()
        d["runtime"]["device"] = "cuda"
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_non_deterministic(self):
        d = reference._manifest_control()
        d["runtime"]["deterministic_algorithms"] = False
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_missing_wavefit_token(self):
        d = reference._manifest_control()
        d["weights"][0]["name"] = "decoder.pt"
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_bad_weight_suffix(self):
        d = reference._manifest_control()
        d["weights"][0]["name"] = "wavefit.bin"
        d["weights"][0]["format"] = "onnx"
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_nonfinite_outcome(self):
        d = reference._manifest_control()
        d["outcomes"]["si_sdr_db"] = float("nan")
        nf = reference._nonfinite_path(d)
        self.assertIsNotNone(nf)

    def test_admission_rejects_inf_outcome(self):
        d = reference._manifest_control()
        d["outcomes"]["stoi"] = float("inf")
        self.assertIsNotNone(reference._nonfinite_path(d))

    def test_admission_rejects_nonfinite_count(self):
        d = reference._manifest_control()
        d["outcomes"]["nonfinite_count"] = 1
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_bad_sample_rate(self):
        d = reference._manifest_control()
        d["features"][0]["sample_rate_hz"] = 32000
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_missing_control_kind(self):
        d = reference._manifest_control()
        d["controls"] = [c for c in d["controls"] if c["kind"] != "identity"]
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_duplicate_control_kind(self):
        d = reference._manifest_control()
        d["controls"][1]["kind"] = "identity"
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_relative_path(self):
        d = reference._manifest_control()
        d["source"]["path"] = "relative/path"
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_traversal_path(self):
        d = reference._manifest_control()
        d["features"][0]["path"] = "/a/../b.wav"
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_bool_int(self):
        d = reference._manifest_control()
        d["runtime"]["threads"] = True
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_oversized_weight(self):
        d = reference._manifest_control()
        d["weights"][0]["byte_count"] = reference.MAX_WEIGHT_BYTES + 1
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_bad_output_rate(self):
        d = reference._manifest_control()
        d["outcomes"]["output_sample_rate_hz"] = 32000
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_admission_rejects_panel_zero(self):
        d = reference._manifest_control()
        d["rights"]["listening_panel_size"] = 0
        res = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(res["accepted"])

    def test_local_pin_files_present(self):
        for name in ("README.md","LICENSES.md","contract.json","reference.py","report.json","report.json.sha256","SOURCES.sha256","verify.py","test_reference.py","run.py"):
            self.assertTrue((HERE/name).is_file(), name)

    def test_sources_has_local_files(self):
        src = reference.sources_bytes().decode("utf-8")
        self.assertIn(reference.TASK_PREFIX + "reference.py", src)

    def test_contract_field_set_exact(self):
        c = reference.build_contract()
        self.assertEqual(set(c.keys()), set(reference.CONTRACT_FIELDS))

    def test_no_floats_in_report(self):
        r = reference.build_report()
        reference._no_floats(r)

    def test_enhancement_profile_blocked(self):
        r = reference.build_report()
        for row in r["enhancement_profile"]["rows"]:
            self.assertEqual(row["status"], "blocked")
        self.assertEqual(len(r["enhancement_profile"]["rows"]), 5)

    def test_timing_blocked(self):
        r = reference.build_report()
        for row in r["timing"]["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])

    def test_sources_bytes_contains_pins(self):
        src = reference.sources_bytes().decode("utf-8")
        self.assertIn("source:research/voice-enhancement-20261101/candidate_matrix.csv", src)
        self.assertIn("CONTRACTS.md", src)
        self.assertIn(reference.TASK_PREFIX + "report.json", src)

    def test_report_sha256_matches_sidecar(self):
        r = reference.build_report()
        text, digest = reference.canonical_report(r)
        side = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(side.strip(), f"{digest}  report.json")

    def test_canonical_bytes_deterministic(self):
        c = reference.build_contract()
        b1 = reference.canonical_bytes(c)
        b2 = reference.canonical_bytes(copy.deepcopy(c))
        self.assertEqual(b1, b2)

    def test_source_presence_no_execution(self):
        r = reference.build_report()
        sp = r["source_presence"]
        self.assertFalse(sp["weights_used"])
        self.assertFalse(sp["model_executed"])
        self.assertFalse(sp["exact_upstream_source_present"])

    def test_linked_rows_digest_stable(self):
        d1 = reference.linked_rows_digest()
        d2 = reference.linked_rows_digest()
        self.assertEqual(d1, d2)
        self.assertEqual(len(d1), 64)


if __name__ == "__main__":
    unittest.main()

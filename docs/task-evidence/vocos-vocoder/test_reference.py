# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for SDK-VOCOS-VOCODER evidence package."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

TASK_DIR = HERE
# REUSE-IgnoreStart
SPDX_LICENSE_LINE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX-" + "FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd


def control() -> dict:
    return reference._manifest_control()


class StrictJsonTests(unittest.TestCase):
    def test_rejects_nan(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('{"x": NaN}')

    def test_rejects_infinity(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('{"x": Infinity}')

    def test_rejects_duplicate_keys(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('{"x": 1, "x": 2}')

    def test_rejects_bom(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('\ufeff{"x": 1}')

    def test_rejects_non_object_root(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('[1]')

    def test_canonical(self):
        self.assertEqual(reference.canonical_text({"b": 2, "a": 1}), '{"a":1,"b":2}\n')

    def test_canonical_rejects_nonfinite(self):
        with self.assertRaises(ValueError):
            reference.canonical_text({"x": float("nan")})

    def test_no_floats(self):
        with self.assertRaises(ValueError):
            reference._no_floats({"a": 1.5})
        reference._no_floats({"a": [1, None, True, "x"]})


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = reference.build_contract()

    def test_identity(self):
        c = self.contract
        self.assertEqual(c["task"], "SDK-VOCOS-VOCODER")
        self.assertEqual(c["component"], "vocos-vocoder")
        self.assertEqual(c["title"], "Vocos vocoder")
        self.assertEqual(c["profile"], "Voice")
        self.assertEqual(c["mode"], "research-control")
        self.assertEqual(c["decision"], "DEFER")
        self.assertEqual(c["status"], "incomplete")
        self.assertEqual(c["qualification_status"], "not_qualified")
        self.assertTrue(c["proposal_only"])

    def test_board_not_pinned(self):
        self.assertFalse(self.contract["board_file_pinned"])
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)
        self.assertEqual(set(self.contract["board_row_projection"]), set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(self.contract["board_row_sha256"], reference.board_row_digest(reference.BOARD_ROW_PROJECTION))

    def test_gates_blockers_artifacts(self):
        gates = self.contract["release_gates"]
        self.assertEqual([g["id"] for g in gates], [f"RG-{i:02d}" for i in range(1, 9)])
        for g in gates:
            self.assertEqual(g["status"], "blocked")
            self.assertFalse(g["qualifies"])
            self.assertEqual(g["linked_row"], reference.BOARD_ROW_PROJECTION)
        arts = self.contract["required_artifacts"]
        self.assertEqual(len(arts), 6)
        self.assertTrue(arts[0]["present"] and arts[0]["verified"] and not arts[0]["blocked"])
        for a in arts[1:]:
            self.assertFalse(a["present"])
            self.assertFalse(a["verified"])
            self.assertTrue(a["blocked"])
            self.assertIsNone(a["sha256"])
        blockers = self.contract["exact_blockers"]
        self.assertEqual(len(blockers), 5)
        for b in blockers:
            self.assertEqual(b["status"], "open")
            self.assertFalse(b["qualifies"])
            self.assertTrue(b["required_action"])

    def test_voice_and_scope(self):
        self.assertEqual(len(self.contract["voice_profile_requirements"]), 8)
        self.assertEqual(len(self.contract["quality_outcomes"]), 4)
        self.assertEqual(len(self.contract["timing_requirements"]), 4)
        for r in self.contract["voice_profile_requirements"]:
            self.assertEqual(r["status"], "blocked")
        self.assertTrue(self.contract["scope"]["task_local_only"])
        self.assertTrue(self.contract["scope"]["source_present"])
        for k, v in self.contract["scope"].items():
            if k not in ("task_local_only", "source_present"):
                self.assertIs(v, False, k)
        for k, v in self.contract["boundary"].items():
            self.assertIs(v, True if k == "task_local_only" else False, k)

    def test_validate_contract(self):
        reference.validate_contract(self.contract)
        bad = dict(self.contract, decision="PASS")
        with self.assertRaises(ValueError):
            reference.validate_contract(bad)
        bad = dict(self.contract)
        bad["extra"] = True
        with self.assertRaises(ValueError):
            reference.validate_contract(bad)


class AdmissionTests(unittest.TestCase):
    def test_control_accepted(self):
        r = reference.validate_manifest(control(), probe_paths=False)
        self.assertTrue(r["accepted"])
        self.assertFalse(r.get("qualifies", False))
        self.assertGreater(r["checks"], 20)

    def test_adverse_matrix(self):
        matrix = reference.admission_controls()
        self.assertTrue(matrix["control"]["accepted"])
        self.assertFalse(matrix["control"]["qualifies"])
        self.assertEqual(matrix["control"]["evidence_class"], "synthetic_schema_control_not_evidence")
        self.assertGreaterEqual(len(matrix["cases"]), 100)
        ids = [c["id"] for c in matrix["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        for c in matrix["cases"]:
            self.assertEqual(c["status"], "rejected", c["id"])
            self.assertFalse(c["qualifies"])
            self.assertTrue(c["state_unchanged"])
            self.assertTrue(c["code"])
        s = matrix["summary"]
        self.assertEqual(s["rejected_count"], s["case_count"])
        self.assertEqual(s["qualifying_results"], 0)
        self.assertEqual(s["accepted_schema_controls"], 1)
        for k in ("state_advanced_on_rejection", "runtime_invoked", "audio_read", "feature_input_read", "weights_loaded", "model_executed", "network_used"):
            self.assertFalse(s[k])

    def test_root_and_nonfinite(self):
        for payload in ([], None, "x", 7, True):
            self.assertFalse(reference.validate_manifest(payload, probe_paths=False)["accepted"])
        d = control(); d["outcomes"]["intelligibility_wer"] = float("nan")
        self.assertEqual(reference.validate_manifest(d, probe_paths=False)["code"], "nonfinite_value")

    def test_key_rejections(self):
        checks = [
            ("missing-rights", lambda d: d.pop("rights"), "missing_field"),
            ("unknown-top", lambda d: d.__setitem__("extra", 1), "unknown_field"),
            ("wrong-source-rev", lambda d: d["source"].__setitem__("revision", "0" * 40), "invalid_value"),
            ("wrong-license", lambda d: d["source"].__setitem__("license_id", "MIT"), "invalid_value"),
            ("path-traversal", lambda d: d["features"][0].__setitem__("path", "/a/../b.npy"), "invalid_path"),
            ("dup-weight", lambda d: d["weights"].append(dict(d["weights"][0])), "invalid_value"),
            ("missing-vocos-token", lambda d: d["weights"][0].__setitem__("name", "decoder.pt"), "invalid_value"),
            ("bad-suffix", lambda d: d["weights"][0].__setitem__("name", "vocos.gguf"), "invalid_value"),
            ("byte-bool", lambda d: d["weights"][0].__setitem__("byte_count", True), "invalid_value"),
            ("byte-float", lambda d: d["weights"][0].__setitem__("byte_count", 1.5), "invalid_value"),
            ("byte-huge", lambda d: d["weights"][0].__setitem__("byte_count", reference.MAX_WEIGHT_BYTES + 1), "invalid_value"),
            ("python-old", lambda d: d["runtime"].__setitem__("python_version", "3.9.1"), "invalid_value"),
            ("nondet", lambda d: d["runtime"].__setitem__("deterministic_algorithms", False), "invalid_value"),
            ("seed-neg", lambda d: d["runtime"].__setitem__("seed", -1), "invalid_value"),
            ("feature-dup", lambda d: d["features"].append(dict(d["features"][0])), "invalid_value"),
            ("controls-missing-kind", lambda d: d.__setitem__("controls", [r for r in d["controls"] if r["kind"] != "zero_features"]), "invalid_value"),
            ("matched-unknown", lambda d: d["controls"][0].__setitem__("feature_id", "mel-missing"), "invalid_value"),
            ("zero-with-id", lambda d: d["controls"][2].__setitem__("feature_id", "mel-a"), "invalid_value"),
            ("wer-high", lambda d: d["outcomes"].__setitem__("intelligibility_wer", 1.1), "invalid_value"),
            ("nonfinite-count", lambda d: d["outcomes"].__setitem__("nonfinite_count", 1), "invalid_value"),
            ("panel-bool", lambda d: d["rights"].__setitem__("listening_panel_size", True), "invalid_value"),
        ]
        for name, fn, code in checks:
            d = control()
            fn(d)
            r = reference.validate_manifest(d, probe_paths=False)
            self.assertEqual(r["code"], code, name)
            self.assertFalse(r["accepted"], name)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.report = reference.build_report()

    def test_deterministic_no_floats(self):
        again = reference.build_report()
        self.assertEqual(reference.canonical_bytes(self.report), reference.canonical_bytes(again))
        reference._no_floats(self.report)

    def test_disposition_and_contract(self):
        r = self.report
        self.assertEqual(r["decision"], "DEFER")
        self.assertEqual(r["status"], "incomplete")
        self.assertEqual(r["qualification_status"], "not_qualified")
        self.assertTrue(r["proposal_only"])
        self.assertEqual(r["contract_sha256"], reference.object_digest(reference.build_contract()))

    def test_absence_and_source(self):
        s = self.report["absence_evidence"]["summary"]
        self.assertEqual(s["present_count"], 0)
        self.assertTrue(s["all_probes_absent"])
        for k in ("download_attempted", "network_used", "recursive_workspace_walk", "source_or_runtime_imported", "weights_loaded", "model_executed", "audio_read", "feature_input_read"):
            self.assertFalse(s[k])
        p = self.report["source_presence"]
        self.assertTrue(p["present"] and p["verified"])
        self.assertFalse(p["admitted"] or p["model_executed"] or p["weights_used"])
        self.assertFalse(p["exact_upstream_source_present"])
        self.assertFalse(p["exact_source_weights_runtime_conjunction_present"])

    def test_historical_not_evidence(self):
        h = self.report["historical_execution"]
        for k in ("not_rerun",):
            self.assertTrue(h[k])
        for k in ("used_for_evidence", "merged_task_evidence", "qualifies", "weights_present_now", "runtime_present_now", "output_present_now", "model_quality_measured", "drop_in_replacement_claim"):
            self.assertFalse(h[k], k)
        self.assertEqual(h["evidence_class"], "historical_provenance_only")

    def test_gates_rows_results(self):
        self.assertEqual(len(self.report["gates"]), 8)
        for g in self.report["gates"]:
            self.assertEqual(g["status"], "blocked")
            self.assertFalse(g["qualifies"])
        self.assertEqual(len(self.report["voice_profile"]["rows"]), 8)
        self.assertEqual(len(self.report["quality_outcomes"]["rows"]), 4)
        self.assertEqual(len(self.report["timing"]["rows"]), 4)
        for row in self.report["voice_profile"]["rows"]:
            self.assertEqual(row["status"], "blocked")
        for row in self.report["quality_outcomes"]["rows"] + self.report["timing"]["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
        for k, v in self.report["required_results"].items():
            self.assertIs(v, True if k == "no_result_qualifies" else False, k)

    def test_linked_identity(self):
        li = self.report["linked_row_identity"]
        self.assertEqual(li["gating"], "stable_identity_only")
        self.assertFalse(li["board_file_pinned"])
        self.assertFalse(li["board_status_gates_anything"])
        self.assertEqual(li["projection"], reference.BOARD_ROW_PROJECTION)
        self.assertEqual(li["sha256"], reference.board_row_digest(reference.BOARD_ROW_PROJECTION))

    def test_pins_and_committed_bytes(self):
        for rows, pins in ((self.report["source_pins"], reference.SOURCE_PINS), (self.report["boundary_pins"], reference.BOUNDARY_PINS)):
            self.assertEqual(set(rows), set(pins))
            for p, row in rows.items():
                self.assertEqual(row["sha256"], pins[p])
                self.assertTrue(row["verified"])
        committed = (TASK_DIR / "report.json").read_bytes()
        self.assertEqual(committed, reference.canonical_bytes(self.report))
        digest = hashlib.sha256(committed).hexdigest()
        self.assertEqual((TASK_DIR / "report.json.sha256").read_text(encoding="ascii"), f"{digest}  report.json\n")
        parsed = reference.loads_strict((TASK_DIR / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(parsed, self.report)
        contract = reference.read_strict_json(TASK_DIR / "contract.json")
        reference.validate_contract(contract)
        self.assertEqual(contract, reference.build_contract())


class PackageTests(unittest.TestCase):
    def test_required_files_and_hygiene(self):
        for name in ("README.md", "LICENSES.md", "contract.json", "reference.py", "report.json", "report.json.sha256", "SOURCES.sha256", "verify.py", "test_reference.py", "run.py"):
            self.assertTrue((TASK_DIR / name).is_file(), name)
        for name in ("contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license"):
            text = (TASK_DIR / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_LICENSE_LINE, text)
        for p in sorted(TASK_DIR.glob("*.py")):
            head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_LICENSE_LINE, head, p.name)
            self.assertIn(SPDX_COPYRIGHT_LINE, head, p.name)
        forbidden = {".gguf", ".onnx", ".pt", ".pth", ".wav", ".flac", ".mp3", ".so", ".dylib", ".dll", ".bin", ".npy", ".npz", ".safetensors"}
        for p in TASK_DIR.iterdir():
            self.assertNotIn(p.suffix.lower(), forbidden, p.name)
            self.assertFalse(p.is_symlink(), p.name)

    def test_sources_manifest(self):
        text = (TASK_DIR / "SOURCES.sha256").read_text(encoding="ascii")
        names = [line.split("  ", 1)[1] for line in text.splitlines() if line and not line.startswith("#")]
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", names)
        self.assertNotIn(reference.BOARD_TASK_ROW, names)
        for rel in reference.SOURCE_PINS:
            self.assertIn("source:" + rel, names)
        for rel in reference.BOUNDARY_PINS:
            self.assertIn(rel, names)
        for name in run.LOCAL_PIN_FILES:
            self.assertIn(reference.TASK_PREFIX + name, names)

    def test_admission_not_evidence(self):
        m = reference.admission_controls()
        self.assertEqual(m["control"]["evidence_class"], "synthetic_schema_control_not_evidence")
        self.assertFalse(m["control"]["qualifies"])
        self.assertEqual(m["summary"]["qualifying_results"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

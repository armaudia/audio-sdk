# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for the portable evidence handoff creator and validator."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evidence_bundle.py"
FIXTURES = ROOT / "conformance" / "evidence"


def run(*args: str) -> tuple[int, dict]:
    result = subprocess.run([sys.executable, str(SCRIPT), *args],
                            capture_output=True, text=True, check=False)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise AssertionError(result.stdout + result.stderr)
    return result.returncode, payload


class EvidenceBundleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def create(self, case: str = "positive", name: str | None = None,
               input_path: Path | None = None) -> Path:
        output = self.root / (name or case)
        code, payload = run(
            "create", "--input", str(input_path or FIXTURES / case / "input.json"),
            "--artifacts", str(FIXTURES / case / "artifacts"),
            "--output", str(output))
        self.assertEqual(code, 0, payload)
        self.assertTrue(payload["ok"])
        return output

    def load_input(self, case: str = "positive") -> dict:
        return json.loads((FIXTURES / case / "input.json").read_text())

    def write_input(self, record: dict, name: str = "input.json") -> Path:
        path = self.root / name
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def assert_cannot_seal(self, record: dict, diagnostic: str) -> None:
        output = self.root / "invalid"
        code, payload = run(
            "create", "--input", str(self.write_input(record)),
            "--artifacts", str(FIXTURES / "positive" / "artifacts"),
            "--output", str(output))
        self.assertEqual(code, 1, payload)
        self.assertTrue(any(diagnostic in error for error in payload["errors"]), payload)
        self.assertFalse(output.exists())

    def test_positive_create_and_validate(self) -> None:
        bundle = self.create()
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["status"], "complete")
        self.assertFalse(payload["incomplete"])
        self.assertTrue((bundle / "handoff.json").is_file())
        canonical = (bundle / "handoff.json").read_text()
        self.assertNotIn("\n  ", canonical)
        self.assertFalse(canonical.endswith("\n"))

    def test_negative_result_is_preserved(self) -> None:
        bundle = self.create("negative")
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["status"], "complete")
        self.assertEqual(payload["failed_checks"], ["quality"])

    def test_accepted_but_undelivered_samples_are_accounted_for(self) -> None:
        record = self.load_input("negative")
        for check in record["checks"]:
            check["denominator"].update(accepted="352", failed="7", dropped="5")
        bundle = self.create("negative", input_path=self.write_input(record))
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["failed_checks"], ["quality"])

    def test_incomplete_bundle_requires_allow_flag(self) -> None:
        bundle = self.create("incomplete")
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 1, payload)
        self.assertEqual(payload["status"], "incomplete")
        self.assertTrue(payload["incomplete"])
        code, payload = run("validate", str(bundle), "--allow-incomplete")
        self.assertEqual(code, 0, payload)
        self.assertTrue(payload["incomplete"])

    def test_tampered_artifact_hash_fails(self) -> None:
        bundle = self.create()
        artifact = next((bundle / "artifacts").rglob("*"))
        artifact.write_text("tampered\n", encoding="utf-8")
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 1, payload)
        self.assertTrue(any("sha256" in error for error in payload["errors"]),
                        payload)

    def test_missing_artifact_fails(self) -> None:
        bundle = self.create()
        artifact = next((bundle / "artifacts").rglob("*"))
        artifact.unlink()
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 1, payload)
        self.assertTrue(any("missing" in error for error in payload["errors"]),
                        payload)

    def test_unlisted_extra_artifact_fails(self) -> None:
        bundle = self.create()
        (bundle / "artifacts" / "extra.txt").write_text("extra\n", encoding="utf-8")
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 1, payload)
        self.assertTrue(any("unlisted" in error for error in payload["errors"]),
                        payload)

    def test_unlisted_file_at_bundle_root_fails(self) -> None:
        bundle = self.create()
        (bundle / "extra.txt").write_text("extra\n", encoding="utf-8")
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 1, payload)
        self.assertIn("bundle must contain exactly handoff.json and artifacts/", payload["errors"])

    def test_impossible_frame_counts_fail(self) -> None:
        for key, value in (("consumed_count", "17"), ("produced_count", "161")):
            with self.subTest(key=key):
                record = self.load_input()
                record["trace"]["entries"][1][key] = value
                self.assert_cannot_seal(record, key)

    def test_full_valid_tail_cannot_claim_padding(self) -> None:
        record = self.load_input()
        record["trace"]["entries"][-1]["flags"] = ["final_padding"]
        self.assert_cannot_seal(record, "trailing invalid region")

    def test_valid_output_must_be_inside_accepted_range(self) -> None:
        record = self.load_input()
        for check in record["checks"]:
            check["denominator"].update(accepted="0", delivered="0")
        self.assert_cannot_seal(record, "exceeds accepted source samples")

        record = self.load_input()
        for entry in record["trace"]["entries"]:
            for key in ("source_first_sample", "source_end_sample"):
                entry[key] = str(int(entry[key]) - 1)
        self.assert_cannot_seal(record, "valid interval falls outside accepted source")

    def test_schema_invalid_provenance_cannot_be_sealed(self) -> None:
        for section, key, value in (
                ("toolchain", "source_revision", "x"),
                ("provenance", "created_utc", "2026-11-20"),
                ("provenance", "created_utc", "2026-11-20T00:00:00")):
            with self.subTest(value=value):
                record = self.load_input()
                record[section][key] = value
                self.assert_cannot_seal(record, key)

    def test_duplicate_check_id_fails(self) -> None:
        record = self.load_input()
        record["checks"].append(dict(record["checks"][0]))
        path = self.write_input(record)
        code, payload = run(
            "create", "--input", str(path),
            "--artifacts", str(FIXTURES / "positive" / "artifacts"),
            "--output", str(self.root / "duplicate-check"))
        self.assertEqual(code, 1, payload)
        self.assertTrue(any("duplicate" in error for error in payload["errors"]),
                        payload)

    def test_impossible_trace_fails(self) -> None:
        record = self.load_input()
        record["trace"]["entries"][1]["available_monotonic_ns"] = "999999999"
        path = self.write_input(record)
        code, payload = run(
            "create", "--input", str(path),
            "--artifacts", str(FIXTURES / "positive" / "artifacts"),
            "--output", str(self.root / "impossible"))
        self.assertEqual(code, 1, payload)
        self.assertTrue(any("negative availability" in error
                            for error in payload["errors"]), payload)

    def test_exact_clock_above_2_pow_53_round_trips(self) -> None:
        record = self.load_input()
        base = 2**53 + 1
        trace = record["trace"]
        delta = base - int(trace["origin_monotonic_ns"])
        trace["origin_monotonic_ns"] = str(base)
        for entry in trace["entries"]:
            entry["available_monotonic_ns"] = str(int(entry["available_monotonic_ns"]) + delta)
        path = self.write_input(record)
        bundle = self.create("positive", "large", path)
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 0, payload)
        handoff = json.loads((bundle / "handoff.json").read_text())
        self.assertEqual(handoff["trace"]["origin_monotonic_ns"], str(base))

    def test_existing_output_is_left_untouched(self) -> None:
        bundle = self.create()
        original = (bundle / "handoff.json").read_bytes()
        code, payload = run(
            "create", "--input", str(FIXTURES / "positive" / "input.json"),
            "--artifacts", str(FIXTURES / "positive" / "artifacts"),
            "--output", str(bundle))
        self.assertEqual(code, 1, payload)
        self.assertEqual((bundle / "handoff.json").read_bytes(), original)

    def test_noncanonical_record_fails(self) -> None:
        bundle = self.create()
        manifest = bundle / "handoff.json"
        manifest.write_bytes(manifest.read_bytes() + b"\n")
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 1, payload)
        self.assertIn("handoff.json: not stored as canonical JSON", payload["errors"])

    def test_duplicate_json_keys_fail(self) -> None:
        bundle = self.create()
        handoff = bundle / "handoff.json"
        text = handoff.read_text().replace(
            '"profile":"DSP"', '"profile":"DSP","profile":"DSP"', 1)
        handoff.write_text(text, encoding="utf-8")
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 1, payload)
        self.assertTrue(any("duplicate key" in error for error in payload["errors"]),
                        payload)

    def test_tampered_content_breaks_identity(self) -> None:
        bundle = self.create()
        handoff = bundle / "handoff.json"
        text = handoff.read_text().replace(
            "\"support_scope\":\"Synthetic fixed-frame evidence handoff; no workload claim.\"",
            "\"support_scope\":\"tampered\"", 1)
        handoff.write_text(text, encoding="utf-8")
        code, payload = run("validate", str(bundle))
        self.assertEqual(code, 1, payload)
        self.assertTrue(any("identity" in error for error in payload["errors"]),
                        payload)

    def test_schema_document_is_valid_json(self) -> None:
        schema = json.loads((ROOT / "schemas/evidence-handoff.schema.json").read_text())
        self.assertEqual(schema["$id"], "audio-sdk/evidence-handoff/0.1")
        self.assertFalse(schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()

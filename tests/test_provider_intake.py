# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Policy tests for scripts/check_provider_intake.py."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_provider_intake.py"
DIGEST = "sha256:" + "a" * 64


def decision(value: str = "allowed") -> dict:
    if value != "allowed":
        return {"decision": value}
    return {
        "decision": "allowed",
        "evidence_ref": "docs/task-evidence/provider-intake.md",
        "reviewer": "reviewer-audit",
        "review_date": "2026-11-20",
    }


def rights(value: str = "allowed") -> dict:
    return {
        "acquisition": decision(value),
        "evaluation": decision(value),
        "redistribution": decision(value),
        "public_playback": decision(value),
    }


def record() -> dict:
    return {
        "schema_id": "audio-sdk/provider-intake/0.1",
        "provider_id": "dsp.example.v0",
        "implementation_version": "1.0.0",
        "contract_version": "0.1",
        "source_revision": "4c3b3be864c3ecdcf48a94358c6dde229aecb703",
        "source_digest": DIGEST,
        "distribution": "source-linked",
        "packages_assets": False,
        "assets": [],
        "rights": rights(),
        "runtime": {
            "kind": "none",
            "optional_dependency": "none",
            "platforms": ["arm64", "x86_64"],
        },
        "evaluation": {
            "task": "identity conformance",
            "evidence_ref": "docs/task-evidence/provider-intake.md",
            "paired_quality": "not-supported",
            "runtime_claim": "not-supported",
        },
        "customer_scope": "allowed",
        "playback_scope": "denied",
        "review": {
            "reviewer": "reviewer-audit",
            "review_date": "2026-11-20",
            "decision": "approved",
        },
    }


def asset(identifier: str = "model.f32", klass: str = "public") -> dict:
    return {
        "id": identifier,
        "sha256": DIGEST,
        "byte_count": 1,
        "class": klass,
        "rights": rights(),
    }


class IntakePolicyTest(unittest.TestCase):
    def run_check(self, value: dict) -> tuple[int, list[str]]:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "intake.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--record", str(path)],
                capture_output=True, text=True, check=False)
            payload = json.loads(result.stdout)
            return result.returncode, payload["errors"]

    def test_valid_no_model_provider(self) -> None:
        status, errors = self.run_check(record())
        self.assertEqual(status, 0, errors)
        self.assertEqual(errors, [])

    def test_valid_restricted_caller_supplied_asset(self) -> None:
        value = record()
        value["runtime"]["kind"] = "cpu"
        value["runtime"]["optional_dependency"] = "caller-supplied checkpoint"
        value["assets"] = [asset("model.f32", "restricted")]
        value["rights"]["redistribution"] = {"decision": "denied"}
        value["rights"]["public_playback"] = {"decision": "denied"}
        value["customer_scope"] = "denied"
        status, errors = self.run_check(value)
        self.assertEqual(status, 0, errors)

    def test_missing_digest_fails(self) -> None:
        value = record()
        value["source_digest"] = "not-a-digest"
        status, errors = self.run_check(value)
        self.assertNotEqual(status, 0)
        self.assertTrue(any("source_digest" in error for error in errors), errors)

    def test_closed_asset_in_public_package_fails(self) -> None:
        value = record()
        value["packages_assets"] = True
        value["assets"] = [asset("model.f32", "closed")]
        status, errors = self.run_check(value)
        self.assertNotEqual(status, 0)
        self.assertTrue(any("packages_assets" in error for error in errors), errors)
        self.assertTrue(any("closed" in error for error in errors), errors)

    def test_unknown_rights_denies_customer_use(self) -> None:
        value = record()
        value["rights"]["evaluation"] = {"decision": "unknown"}
        status, errors = self.run_check(value)
        self.assertNotEqual(status, 0)
        self.assertTrue(any("customer_scope" in error for error in errors), errors)

    def test_duplicate_asset_id_fails(self) -> None:
        value = record()
        value["assets"] = [asset("model.f32"), asset("model.f32")]
        status, errors = self.run_check(value)
        self.assertNotEqual(status, 0)
        self.assertTrue(any("duplicate" in error for error in errors), errors)

    def test_package_with_restricted_asset_fails(self) -> None:
        value = record()
        value["packages_assets"] = True
        value["assets"] = [asset("model.f32", "restricted")]
        status, errors = self.run_check(value)
        self.assertNotEqual(status, 0)
        self.assertTrue(any("non-public" in error for error in errors), errors)

    def test_allowed_decision_needs_evidence(self) -> None:
        value = record()
        value["rights"]["evaluation"] = {"decision": "allowed"}
        status, errors = self.run_check(value)
        self.assertNotEqual(status, 0)
        self.assertTrue(any("needs evidence_ref" in error for error in errors), errors)

    def test_schema_document_is_valid_json(self) -> None:
        schema = json.loads((ROOT / "schemas/provider-intake.schema.json").read_text())
        self.assertEqual(schema["$id"], "audio-sdk/provider-intake/0.1")
        self.assertFalse(schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()

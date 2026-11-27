# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for SDK-X-VC blocker evidence package."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import run  # noqa: E402


class TestXVCReference(unittest.TestCase):
    def test_report_schema_and_status(self) -> None:
        r = reference.build_report()
        self.assertEqual(r["schema_id"], "audio-sdk/x-vc-reference-report/0.1")
        self.assertEqual(r["task"], "SDK-X-VC")
        self.assertEqual(r["decision"], "DEFER")
        self.assertEqual(r["status"], "proposal_only_not_qualified")
        self.assertEqual(r["qualification_status"], "not_qualified")
        self.assertEqual(r["qualification"]["readiness"], "incomplete")
        self.assertFalse(r["qualification"]["candidate_qualified"])
        self.assertTrue(r["no_missing_result_qualifies_candidate"])

    def test_all_release_gates_blocked(self) -> None:
        r = reference.build_report()
        self.assertEqual(len(r["release_gates"]), 8)
        self.assertEqual([g["id"] for g in r["release_gates"]], [f"RG-0{i}" for i in range(1, 9)])
        self.assertTrue(all(g["status"] == "blocked" for g in r["release_gates"]))
        self.assertEqual(r["remaining_gates"], [f"RG-0{i}" for i in range(1, 9)])

    def test_upstream_blocker_absent(self) -> None:
        r = reference.build_report()
        b = r["upstream_blocker"]
        self.assertEqual(b["status"], "blocked_weights_and_runtime_absent")
        self.assertEqual(b["source"]["status"], "present_pinned")
        self.assertEqual(b["source"]["revision"], reference.SOURCE_REVISION)
        self.assertEqual(b["weights"]["status"], "absent")
        for k in ("x_vc_checkpoint", "glm_4_voice_tokenizer", "eres2net"):
            self.assertIsNone(b["weights"][k]["sha256"])
            self.assertIsNone(b["weights"][k]["byte_count"])
            self.assertFalse(b["weights"][k]["present"])
        self.assertEqual(b["runtime"]["status"], "absent_unpinned")
        self.assertIsNone(b["runtime_digest"])
        self.assertTrue(b["no_upstream_parity_claim"])

    def test_dependency_resolution_blocked(self) -> None:
        r = reference.build_report()
        d = r["dependency_resolution"]
        self.assertEqual(d["glm_4_voice_tokenizer"]["status"], "blocked_weights_absent")
        self.assertEqual(d["eres2net"]["status"], "blocked_weights_absent")
        self.assertEqual(d["x_vc_checkpoint"]["status"], "blocked_weights_absent")
        self.assertFalse(d["joint_memory"]["measured_here"])

    def test_valid_request_fails_closed(self) -> None:
        req = {
            "candidate": "x-vc", "epoch": 0, "execution_mode": "cli_sim",
            "input_position_samples": 0, "lifecycle": "open",
            "sample_rate_hz": 16000, "channels": 1, "frame_samples": 160,
            "samples": [0.0] * 160, "target_condition": "target_unspecified",
            "dependencies": ["glm-4-voice-tokenizer", "eres2net"],
        }
        out = reference.evaluate_request(req)
        self.assertFalse(out["accepted"])
        self.assertEqual(out["error"], "SOURCE_WEIGHTS_RUNTIME_ABSENT")
        self.assertIsNone(out["metrics"])
        self.assertFalse(out["qualifies_candidate"])

    def test_invalid_requests_rejected(self) -> None:
        adverse = reference._adverse_cases()
        self.assertTrue(adverse["all_rejected"])
        self.assertEqual(adverse["accepted_count"], 0)
        self.assertGreaterEqual(adverse["dependency_case_count"], 7)
        self.assertGreaterEqual(adverse["case_count"], 30)

    def test_strict_json_rejects_duplicate_and_nonfinite(self) -> None:
        adverse = reference._json_adverse_cases()
        self.assertTrue(adverse["all_rejected"])
        with self.assertRaises(Exception):
            reference.stable_json_loads('{"a":1,"a":2}')
        with self.assertRaises(Exception):
            reference.stable_json_loads('[NaN]')

    def test_reset_cases_match(self) -> None:
        reset = reference._reset_cases()
        self.assertTrue(reset["matches_expectation"])
        self.assertEqual(reset["expected_accepted_count"], 1)

    def test_stable_board_link_identity_only(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(links, [{
            "task_id": "SDK-X-VC", "title": "X-VC", "mode": "feasibility",
            "repository": "audio-sdk", "component": "x-vc",
        }])
        self.assertEqual(digest, reference.sha256_bytes(reference.canonical_bytes(links)))
        r = reference.build_report()
        self.assertEqual(r["board_link_projection_sha256"], digest)
        self.assertIn("status", r["board_mutable_fields_excluded"])
        self.assertIn("owner", r["board_mutable_fields_excluded"])

    def test_inventory_and_evidence_entry(self) -> None:
        r = reference.build_report()
        self.assertEqual(r["inventory_link"]["task"], "SDK-X-VC")
        self.assertEqual(r["inventory_link"]["verification_profile"], "voice")
        self.assertEqual(r["evidence_entry"]["line"], 20)
        self.assertIn("5.01 GB", r["evidence_entry"]["text"])

    def test_geometry_declared_not_measured(self) -> None:
        g = reference.geometry()
        self.assertFalse(g["measured_here"])
        self.assertFalse(g["candidate_output"])
        self.assertEqual(g["semantic_tokenizer_repository"], "zai-org/glm-4-voice-tokenizer")
        self.assertEqual(g["speaker_embedding_dim"], 192)
        self.assertEqual(g["semantic_feature_width"], 1280)
        self.assertEqual(g["candidate_checkpoint_path"], "ckpts/xvc.pt")
        self.assertEqual(g["declared_requirements"]["torch"], "2.5.1")

    def test_boundary_preserved(self) -> None:
        b = reference.boundary()
        self.assertTrue(b["installed_v0_unchanged"])
        self.assertFalse(b["public_api_abi_changed"])
        self.assertFalse(b["provider_registered"])
        self.assertFalse(b["enabled_by_default"])
        self.assertFalse(b["shared_cmake_changed"])
        self.assertFalse(b["ci_changed"])
        self.assertEqual(b["format"], {"channels": 1, "frame_samples": 160, "sample_format": "float32", "sample_rate_hz": 16000})

    def test_source_probe_pinned(self) -> None:
        s = reference.source_probe()
        self.assertTrue(s["present"])
        self.assertEqual(s["status"], "present_pinned")
        self.assertEqual(s["revision"], reference.SOURCE_REVISION)
        self.assertEqual(s["license"], "MIT")
        self.assertEqual(s["file_count"], 82)

    def test_weights_and_runtime_absent(self) -> None:
        w = reference.weights_probe()
        self.assertFalse(w["present"])
        self.assertEqual(w["status"], "blocked_weights_absent")
        rt = reference.runtime_probe()
        self.assertFalse(rt["pinned"])
        self.assertEqual(rt["status"], "blocked_runtime_unpinned")

    def test_report_is_canonical_and_deterministic(self) -> None:
        a = reference.report_bytes()
        b = reference.report_bytes()
        self.assertEqual(a, b)
        self.assertTrue(a.endswith(b"\n"))
        self.assertFalse(a.endswith(b"\n\n"))
        obj = reference.strict_json_loads(a.decode("utf-8"))
        self.assertEqual(reference.canonical_bytes(obj) + b"\n", a)

    def test_run_verify_repro(self) -> None:
        # build artifacts then verify in-memory
        run.write_report(); run.write_sources(); run.write_contract()
        rc = run.verify_reproduction()
        self.assertEqual(rc, 0)

    # --- scope enforcement regression tests (required by prompt) ---

    def _init_git_repo(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "t@t"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True, capture_output=True)
        (root / "base.txt").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "base.txt"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "base"], check=True, capture_output=True)

    def test_scope_base_newest_merge_base_origin_main_main(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_git_repo(root)
            base = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            subprocess.run(["git", "-C", str(root), "branch", "origin/main", base], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "checkout", "-q", "-b", "mainline"], check=True, capture_output=True)
            (root / "main.txt").write_text("main\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "main.txt"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "main"], check=True, capture_output=True)
            main_sha = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            subprocess.run(["git", "-C", str(root), "branch", "-f", "main", main_sha], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "checkout", "-q", "-b", "feature"], check=True, capture_output=True)
            (root / "docs/task-evidence/x-vc").mkdir(parents=True)
            (root / "docs/task-evidence/x-vc/report.json").write_text("{}\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "feat"], check=True, capture_output=True)
            got = reference.scope_base(root)
            self.assertEqual(got, main_sha)

    def test_scope_base_unavailable_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_git_repo(root)
            got = reference.scope_base(root, refs=("origin/does-not-exist", "main-missing"))
            self.assertIsNone(got)

    def test_scope_base_out_of_scope_change_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_git_repo(root)
            base = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            subprocess.run(["git", "-C", str(root), "checkout", "-q", "-b", "mainline"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "branch", "-f", "main", base], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "checkout", "-q", "-b", "feature"], check=True, capture_output=True)
            (root / "docs/task-evidence/x-vc").mkdir(parents=True)
            (root / "docs/task-evidence/x-vc/report.json").write_text("{}\n", encoding="utf-8")
            (root / "README.md").write_text("oops\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "feat"], check=True, capture_output=True)
            b = reference.scope_base(root)
            self.assertIsNotNone(b)
            paths = reference.scope_changed_paths(root, b)
            violations = reference.scope_violations(paths)
            self.assertIn("README.md", violations)
            self.assertNotIn("docs/task-evidence/x-vc/report.json", violations)


if __name__ == "__main__":
    unittest.main()

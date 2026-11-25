# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import probe


class ProbeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.prefix = self.root / "prefix"
        self.out = self.root / "out"

    def package(self, target="Emscripten-x86"):
        for name, contents in {
            "include/audio_sdk/session_v0.h": "header",
            "lib/libaudio_sdk.a": "library",
            "share/audio-sdk/build-info.json": json.dumps({
                "schema_id": "audio-sdk/build-info/0.1", "target": target, "version": "0.1.0",
            }),
        }.items():
            path = self.prefix / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents)

    def invoke(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            code = probe.main(["--output", str(self.out), *args])
        return code, json.loads((self.out / "report.json").read_text())

    def test_omitted_selection_never_passes(self):
        code, report = self.invoke()
        self.assertEqual(code, 0)
        self.assertEqual(report["apple_native"]["status"], "unavailable")
        self.assertEqual(report["emscripten_node"]["status"], "unavailable")
        self.assertEqual(report["workload_support"], "not_assessed")
        self.assertEqual(self.out.stat().st_mode & 0o777, 0o700)

    @patch.object(probe.shutil, "which", return_value=None)
    def test_explicit_selection_missing_tools_is_unsuccessful(self, _which):
        code, report = self.invoke("--wasm-prefix", str(self.prefix))
        self.assertEqual(code, 1)
        self.assertIn("emcc, node", report["emscripten_node"]["reason"])
        self.assertEqual(report["emscripten_node"]["status"], "unavailable")

    @patch.object(probe.shutil, "which", side_effect=lambda name: f"/tools/{name}")
    def test_wrong_target_fails_before_running_anything(self, _which):
        self.package("Darwin-arm64")
        code, report = self.invoke("--wasm-prefix", str(self.prefix))
        self.assertEqual(code, 1)
        self.assertEqual(report["emscripten_node"]["status"], "failed")
        self.assertEqual(report["emscripten_node"]["steps"], [])

    def completed(self, args, *, cwd, **_kwargs):
        if "-o" in args:
            for name in ("smoke.js", "smoke.wasm"):
                (cwd / name).write_text("mock output")
        return subprocess.CompletedProcess(args, 0, "", "")

    @patch.object(probe.shutil, "which", side_effect=lambda name: f"/tools/{name}")
    @patch.object(probe.subprocess, "run")
    def test_runtime_failure_is_not_a_compile_failure(self, run, _which):
        self.package()
        def fail_runtime(args, **kwargs):
            return (subprocess.CompletedProcess(args, 1, "", "failed at runtime")
                    if args[0].endswith("node") and "--version" not in args
                    else self.completed(args, **kwargs))
        run.side_effect = fail_runtime
        code, report = self.invoke("--wasm-prefix", str(self.prefix))
        result = report["emscripten_node"]
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "failed")
        self.assertEqual([(step["phase"], step["returncode"]) for step in result["steps"][-2:]],
                         [("compile-link", 0), ("synthetic-runtime", 1)])

    @patch.object(probe.shutil, "which", side_effect=lambda name: f"/tools/{name}")
    @patch.object(probe.subprocess, "run")
    def test_node_success_does_not_promote_any_other_lane(self, run, _which):
        self.package()
        run.side_effect = self.completed
        code, report = self.invoke("--wasm-prefix", str(self.prefix))
        self.assertEqual(code, 0)
        self.assertEqual(report["emscripten_node"]["status"], "passed")
        self.assertEqual(set(report["emscripten_node"]["outputs_sha256"]), {"smoke.js", "smoke.wasm"})
        self.assertEqual(report["apple_native"]["status"], "unavailable")
        self.assertEqual(report["browser_audio_worklet"]["status"], "blocked")
        self.assertEqual(report["device_scheduling"]["status"], "blocked")
        self.assertEqual(report["workload_support"], "not_assessed")

    def test_malformed_cli_and_existing_output_refused(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as bad:
                probe.main(["--output", str(self.out), "--wasm-prefix"])
            self.assertEqual(bad.exception.code, 2)
            self.assertFalse(self.out.exists())
            self.out.mkdir()
            old = self.out / "report.json"
            old.write_text("preserved")
            with self.assertRaises(SystemExit) as exists:
                probe.main(["--output", str(self.out)])
            self.assertEqual(exists.exception.code, 2)
        self.assertEqual(old.read_text(), "preserved")

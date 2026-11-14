# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Publishing policy refuses mutations before identity and CI preconditions pass."""
import importlib.util
import json
import hashlib
import os
import runpy
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import contextmanager


path = Path(__file__).resolve().parents[1] / "scripts/github_admin.py"
spec = importlib.util.spec_from_file_location("github_admin", path)
admin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin)


@contextmanager
def working_directory(path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


class AdministrationPreconditions(unittest.TestCase):
    def test_pending_ci_cannot_change_settings(self):
        methods = []

        def fake_run(command, **kwargs):
            method = command[command.index("--method") + 1]
            methods.append(method)
            payload = ({"private": False, "permissions": {"admin": True}}
                       if command[-1] == "repos/armaudia/audio-sdk" else
                       {"check_runs": [{"name": "quality", "app": {"slug": "github-actions"},
                                        "conclusion": None}]})
            return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")

        with patch("sys.argv", [str(path), "--repo", "audio-sdk"]), \
                patch.object(subprocess, "run", side_effect=fake_run), \
                patch.object(subprocess, "check_output", return_value="a" * 40):
            with self.assertRaisesRegex(RuntimeError, "must pass GitHub Actions"):
                admin.main()
        self.assertEqual(methods, ["GET", "GET"])

    def test_private_code_cannot_be_configured_as_public(self):
        response = subprocess.CompletedProcess([], 0, json.dumps({"private": False}), "")
        with patch("sys.argv", [str(path), "--repo", "audio-pro"]), \
                patch.object(subprocess, "run", return_value=response) as invoked:
            with self.assertRaisesRegex(RuntimeError, "visibility"):
                admin.main()
        self.assertEqual(invoked.call_count, 1)


class ImmutableReleasePublication(unittest.TestCase):
    def test_assets_are_attached_before_release_is_published(self):
        script = path.parent / "publish_release.py"
        with tempfile.TemporaryDirectory() as temporary, working_directory(temporary):
            assets = Path("release-assets")
            assets.mkdir()
            for name in ("linux.tar.gz", "macos.tar.gz", "windows.zip", "wasm.zip"):
                archive = assets / name
                archive.write_bytes(name.encode())
                archive.with_name(archive.name + ".sha256").write_text(
                    hashlib.sha256(archive.read_bytes()).hexdigest())
            with patch.dict(os.environ, {"TAG": "v0.1.0-rc.1"}), \
                    patch.object(subprocess, "run") as invoked:
                runpy.run_path(str(script), run_name="__main__")
            commands = [call.args[0] for call in invoked.call_args_list]
            self.assertEqual(len(commands), 2)
            self.assertIn("--draft", commands[0])
            self.assertIn("--draft=false", commands[1])
            self.assertIn("--latest=false", commands[1])

    def test_missing_platform_archive_never_publishes(self):
        with tempfile.TemporaryDirectory() as temporary, working_directory(temporary):
            Path("release-assets").mkdir()
            with patch.object(subprocess, "run") as invoked:
                with self.assertRaisesRegex(SystemExit, "Linux, macOS, Windows and WebAssembly"):
                    runpy.run_path(str(path.parent / "publish_release.py"), run_name="__main__")
            invoked.assert_not_called()


if __name__ == "__main__":
    unittest.main()

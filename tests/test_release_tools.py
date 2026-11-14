"""Publishing policy refuses mutations before identity and CI preconditions pass."""
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch


path = Path(__file__).resolve().parents[1] / "scripts/github_admin.py"
spec = importlib.util.spec_from_file_location("github_admin", path)
admin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin)


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


if __name__ == "__main__":
    unittest.main()

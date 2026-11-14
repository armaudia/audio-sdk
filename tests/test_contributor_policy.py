# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
import hashlib
import importlib.util
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location("contributor_policy", Path(__file__).resolve().parents[1] / "scripts/check_contributors.py")
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class ContributorPolicyTests(unittest.TestCase):
    def test_external_contributor_needs_a_current_private_record(self):
        agreement = b"unit-test agreement; not a legal acceptance"
        digest = hashlib.sha256(agreement).hexdigest()
        ledger = {"agreement_sha256": digest, "approved_contributors": []}
        with self.assertRaisesRegex(ValueError, "private CLA acceptance"):
            policy.check_sdk(agreement, ledger, 123)
        ledger["approved_contributors"] = [{"github_user_id": 123,
            "agreement_sha256": digest, "private_record_id": "unit-test-only"}]
        policy.check_sdk(agreement, ledger, 123)
        with self.assertRaisesRegex(ValueError, "version/hash"):
            policy.check_sdk(b"changed agreement", ledger, 123)

    def test_maintainer_exemption_is_not_a_signature(self):
        agreement = b"test"
        policy.check_sdk(agreement, {"agreement_sha256": hashlib.sha256(agreement).hexdigest()}, policy.MAINTAINER_USER_ID)

    def test_each_dco_commit_must_be_signed_off(self):
        signed = "Change\n\nSigned-off-by: Test Contributor <test@example.invalid>\n"
        policy.check_dco([signed])
        with self.assertRaises(ValueError):
            policy.check_dco([signed, "Unsigned change"])


if __name__ == "__main__":
    unittest.main()

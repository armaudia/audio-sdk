# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Check a trusted-base CLA ledger or per-commit DCO sign-offs; never create signatures."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


MAINTAINER_USER_ID = 6400032


def check_sdk(agreement: bytes, ledger: dict, user_id: int) -> None:
    digest = hashlib.sha256(agreement).hexdigest()
    if ledger.get("agreement_sha256") != digest:
        raise ValueError("CLA version/hash must be updated together")
    if user_id == MAINTAINER_USER_ID:
        return
    records = ledger.get("approved_contributors", [])
    if not any(record.get("github_user_id") == user_id
               and record.get("agreement_sha256") == digest
               and isinstance(record.get("private_record_id"), str)
               and record["private_record_id"].strip() for record in records):
        raise ValueError("A verified private CLA acceptance must be recorded by the maintainer before merge")


def check_dco(messages: list[str]) -> None:
    if not messages or any(not re.search(
            r"^Signed-off-by:\s+\S.*<[^\s<>@]+@[^\s<>]+>\s*$", message,
            re.MULTILINE | re.IGNORECASE) for message in messages):
        raise ValueError("Every contributed commit needs its contributor's DCO Signed-off-by trailer")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", choices=("sdk", "bench"), required=True)
    parser.add_argument("--event", type=Path, required=True)
    args = parser.parse_args()
    event = json.loads(args.event.read_text())
    pull = event.get("pull_request")
    if pull is None:
        print("No pull request: contributor intake does not apply")
        return
    base, head = pull["base"]["sha"], pull["head"]["sha"]
    if not all(re.fullmatch(r"[0-9a-f]{40}", sha) for sha in (base, head)):
        raise ValueError("Expected immutable Git commit identities")
    if args.policy == "sdk":
        agreement = subprocess.check_output(["git", "show", f"{base}:CLA/individual.md"])
        ledger = json.loads(subprocess.check_output(["git", "show", f"{base}:CLA/approvals.json"]))
        check_sdk(agreement, ledger, pull["user"]["id"])
        print("CLA policy passed: maintainer-owned work or existing verified private acceptance")
    else:
        commits = subprocess.check_output(["git", "rev-list", f"{base}..{head}"], text=True).splitlines()
        messages = [subprocess.check_output(["git", "show", "-s", "--format=%B", sha], text=True) for sha in commits]
        check_dco(messages)
        print(f"DCO trailers present on {len(commits)} commits; authority still requires review")


if __name__ == "__main__":
    main()

# SDK-FND-AUDIT evidence · public provider intake and asset boundary

| Field | Value |
| --- | --- |
| Repository and scope | `audio-sdk`; `docs/**`, `schemas/**`, `scripts/**`, `tests/**`, `core/tests/test_assets.c` |
| Owner / reviewer | `agent-audit` / `reviewer-audit` |
| Base | `4c3b3be864c3ecdcf48a94358c6dde229aecb703` (`origin/main`) |
| Branch | `swarm/SDK-FND-AUDIT` |
| Outcome | Implemented; no release or model qualification claimed |

## Deliverables

- [`docs/provider-intake.md`](../provider-intake.md): normative intake checklist and
  fail-closed asset boundary.
- [`schemas/provider-intake.schema.json`](../../schemas/provider-intake.schema.json):
  Draft 2020-12 intake record schema.
- [`scripts/check_provider_intake.py`](../../scripts/check_provider_intake.py):
  policy checker with duplicate-key detection, exact key sets, asset class rules,
  rights-scope gating and public-package isolation.
- [`tests/test_provider_intake.py`](../../tests/test_provider_intake.py): nine
  positive/negative policy cases.
- [`core/tests/test_assets.c`](../../core/tests/test_assets.c): the runtime
  missing-asset path now asserts the `assets` error field and message.

## Reproduction

All commands ran from the task worktree on macOS arm64, 2026-11-20.

```sh
python3 scripts/check_provider_intake.py \
  --record docs/task-evidence/provider-intake.example.json
# exit 0; {"ok": true, "errors": []}

python3 -m unittest tests.test_provider_intake -v
# Ran 9 tests ... OK

cmake -S . -B build/fnd-audit -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_LIBDIR=lib
cmake --build build/fnd-audit --parallel 2
ctest --test-dir build/fnd-audit --output-on-failure --timeout 60
# 11/11 tests passed, including as_test_assets
```

The no-model installability control is the released baseline: SpeexDSP noise
suppression and the 80 Hz high-pass require no external assets, and all eleven
native/conformance tests pass with no model files present. The full installed
archive and external-provider checks are exercised by `scripts/ci.py` and the
hosted CI matrix.

## Boundary results

| Case | Result |
| --- | --- |
| Public no-model provider with complete rights | accepted |
| Restricted caller-supplied asset with complete approved evaluation scope | accepted |
| Missing or malformed `source_digest` | rejected, field named |
| Closed asset with public package flag | rejected |
| Restricted asset with public package flag | rejected |
| `unknown` evaluation right with `customer_scope=allowed` | rejected |
| Duplicate asset ID | rejected |
| `allowed` right without evidence/reviewer/date | rejected |
| Required external asset omitted at session creation | `AS_INVALID_ARGUMENT`, field `assets` |
| Required external asset with wrong ID or digest | `AS_INVALID_ARGUMENT` (existing cases) |

## Limits and next action

This task publishes the intake policy and proves the fail-closed boundary. It
does not admit any model or restricted asset, and it does not replace a legal
review. The checker validates policy shape and references; it is not a general
JSON Schema engine, so CI also keeps the schema in review. Reopen when a real
model or restricted provider is proposed: attach its completed intake record,
exact checkpoint digests, runtime and evidence references, then run the checker
and the installed conformance matrix.

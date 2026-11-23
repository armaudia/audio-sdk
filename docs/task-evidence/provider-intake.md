# SDK-FND-AUDIT evidence · public provider intake and asset boundary

| Field | Value |
| --- | --- |
| Repository and scope | `audio-sdk`; intake docs, schema, checker, packaging, and scoped tests |
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
- [`tests/test_provider_intake.py`](../../tests/test_provider_intake.py): positive
  and negative policy, provenance, and public catalog cases.
- [`core/tests/test_assets.c`](../../core/tests/test_assets.c): the runtime
  missing-asset path now asserts the `assets` error field and message.

## Reproduction

Run from the task worktree:

```sh
python3 scripts/check_provider_intake.py \
  --record docs/task-evidence/provider-intake.example.json
# exits 1: unknown acquisition and evaluation, pending review

python3 -m unittest tests.test_provider_intake -v

cmake -S . -B build/fnd-audit -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_LIBDIR=lib
cmake --build build/fnd-audit --parallel 2
ctest --test-dir build/fnd-audit --output-on-failure --timeout 60
```

The non-admitted example uses the real high-pass descriptor and source digests
and a checked source manifest, but records no approval. SpeexDSP noise
suppression and the 80 Hz high-pass are the no-model installability controls:
both shipped before this intake policy and require no external assets. The full
installed archive and external-provider checks are exercised by `scripts/ci.py`
with `requirements-build.txt`.

## Boundary results

| Case | Result |
| --- | --- |
| Synthetic no-model provider with complete rights | accepted |
| Restricted caller-supplied asset with approved execution scope | passes scoped checker; rejected from public catalog |
| Same descriptor with public vs restricted/closed asset classification | public policy check passes with complete intake; restricted/closed intake is denied |
| Missing, extra, or changed installed descriptor | catalog rejected; both package modes refuse to seal when Speex is missing |
| Untracked file under `docs/` | not exported into the release source |
| Missing, malformed or zero `source_digest`; nonexistent or mutable Git revision; missing or mismatched source manifest/evidence | rejected, field named |
| Closed asset with public package flag | rejected |
| Restricted asset with public package flag | rejected |
| Rejected review or denied/unknown permissions needed for execution, customer use, playback or packaging | rejected |
| Duplicate asset ID | rejected |
| `allowed` right without evidence/reviewer/date | rejected |
| Required external asset omitted at session creation | `AS_INVALID_ARGUMENT`, field `assets` |
| Required external asset with wrong ID or digest | `AS_INVALID_ARGUMENT` (existing cases) |

## Limits and next action

The native tarball and Wasm ZIP share a gate that checks staged public
discovery descriptors against the generated built-in registry. The C runtime
still checks caller-supplied assets, not rights records; the missing-asset C
test is not evidence of rights enforcement. No model or restricted asset is
admitted, and these checks are not a legal review. Reopen with a completed
intake record, exact checkpoint digests, runtime and evidence references, then
run the checker and the installed conformance matrix.

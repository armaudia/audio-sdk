# Required acceptance matrix

Updated 2026-11-14. “Implemented” is not a release/acceptance pass. No S01–S08
task is marked complete while a mandatory row remains open.

| Task / row | State | Evidence or exact blocker |
|---|---|---|
| S01 provenance, source allocation, notices | Implemented; partial | `docs/task-evidence/s01.md`; rights review/release-license decision remains unapproved |
| S02 timing regression | Tested | Existing timing evidence plus `docs/task-evidence/validity-and-installed-delays.md` |
| S03 header/schema/registry | Implemented; partial | C11/C++20 installed consumer passed; schemas checked in `docs/task-evidence/schema-meta-validation.md`; compatibility target/layout acceptance incomplete |
| S04 lifecycle/worker | Implemented; partial | Mode-3 submit/pull are lock-free ring operations; Release, ASan/UBSan, and TSan each pass 10/10; deterministic input/output saturation, 1,000 sequential create/reset/close cycles, reset cancellation counts, and worker failed-interval counters pass. Complete source-range accounting and concurrent lifecycle overlap remain open; see `docs/task-evidence/s04.md` |
| S05 providers | Tested locally | Installed Speex/high-pass conformance passed; local macOS arm64 only |
| S06 install/conformance | Tested locally | Candidate 07 installed consumers and builtin conformance passed; installed external fixtures 10/10 passed |
| S07 package/CI | Partial | `docs/task-evidence/s07-build-identity.md`: byte-derived runtime build ID, frozen configure-time input hashes, package freshness check, staging and overwrite refusal. No new sealed candidate; Linux x86-64/hosted CI, evidence-driven manifest, and clean-build reproducibility remain open |
| S08 Python/examples | Partial | CPython 3.12.16 wheel installed into owned venv; 4/4 tests and copied installed example passed; full exact-integer/native layout and install packaging rows remain open |
| S09 LiveKit host | Blocked / excluded | No pinned/tested LiveKit host package pair; no claim |
| S10 Tiny16 neural reference | Blocked / not implemented | Metadata only; model-specific evaluation grant, exact authorized bytes/runtime and real-weight reference traces absent; see `docs/task-evidence/s10-model-gate.md` |
| S11 engine ABI/fixture | Not implemented / excluded | No public engine ABI or independently installed engine fixture |
| S12 broader formats/hosts | Excluded | Not claimed or advertised |
| S-T01 build/install | Tested locally | Release CTest 10/10; installed C11/C++20; macOS arm64 only |
| S-T02 timing | Tested for provider delays | External installed delays 0, 1, 159, 160, 161, 256 (native hop 256), 512; sync and buffered paths; see evidence |
| S-T03 boundaries/drain | Partial | In-tree timing checks all 1–159 remainders; exact 159-sample final padding and validity arithmetic are tested; reset cancellation sample/interval counts are checked, but full interval conservation across cancel/reset/close remains open |
| S-T04 registry/layout | Partial | Existing registry tests pass; legacy ABI compatibility not implemented; Python ctypes layouts lack independent full offset/size probe |
| S-T05 invalid processing | Partial | Existing invalid-call/provider checks pass; full backend non-invocation/state-snapshot suite not complete |
| S-T06 lifecycle/failure | Partial | Worker failure enters needs_reset and reports the failed interval/sample counts; failed-reset/close-race/full worker fault accounting matrix incomplete |
| S-T07 concurrency | Partial | Deterministic stalled-worker input and output saturation, plus 1,000 sequential lifecycle cycles pass under TSan; concurrent reset/close overlap stress remains open |
| S-T08 provider state | Partial | Builtin conformance; full separate-instance/reset bit-identity matrix incomplete |
| S-T09 external install | Tested locally | C11/C++20 consumers and external provider fixture use installed candidate; no isolated sibling-unavailable runner |
| S-T10 Python | Partial | CPython 3.12 wheel, reset/process/drain/close, and 161-sample WAV switching example passed; missing-library/error and exact byte/layout comparisons incomplete |
| S-T11 LiveKit | Excluded | S09 blocked |
| S-T12 package/export | Partial | Archive hashes and local install passed; Linux dependency inspection, second-host reproducibility and rights review open |
| S-T13 exact integers | Partial | Native interval overflow boundaries tested; canonical JSON correctly rejects integers outside ±(2^53−1); Python exact-clock round trip not yet exercised |
| S-T14 callback safety | Excluded | Mode 1 is not advertised; allocation/lock instrumentation not run |

## Platform results

- macOS arm64 Release: 10/10 CTest; installed C11/C++20 consumers; built-in
  providers passed; installed independent external conformance 10/10.
- macOS arm64 ASan/UBSan: 10/10 CTest.
- macOS arm64 TSan: 10/10 CTest. This is not the unimplemented 1,000-cycle
  reset/close stress test.
- CPython 3.12.16: wheel installed into `build/acceptance/python312`; four
  installed-package unit tests passed; clean copied example processed a
  161-sample PCM16 WAV through both providers and wrote two 161-sample WAVs.
- Linux x86-64 and hosted CI: not run; no authorized infrastructure was
  available in this execution.

Provider onboarding procedure and exact clean-consumer commands/results:
[`docs/task-evidence/provider-onboarding.md`](task-evidence/provider-onboarding.md).

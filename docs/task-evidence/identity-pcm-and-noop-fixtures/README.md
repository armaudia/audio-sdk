# SDK-IDENTITY-PCM-AND-NOOP-FIXTURES · identity PCM and noop baseline

**Reference-verification / Tool profile.** This is a task-local, deterministic
control for follow-on SDK timing and chain work. It keeps the installed fixed
v0 behavior unchanged: 16 kHz, mono, float32, 160-sample frames, one provider
per session, D=0 identity PCM. No public API, header, descriptor, registry,
default provider, board file, handoff or installed behavior is changed. No
model, real audio, device, pacing, release or quality qualification is claimed.

The installed SDK at this pin has **no built-in identity/noop provider**. The
pinned `identity.cpp` is a legacy private stage and `adapter.json` is a harness
control descriptor. This fixture therefore registers an explicit, caller-owned
identity provider on a private registry through the installed public C
boundary. Registration is opt-in and registry-local.

## Scope and source pins

| Source | SHA-256 | Summary |
| --- | --- | --- |
| `cpp-library/src/stages/identity.cpp` | `5fff7e319c32485a541fec5785fefb11ca0d9ad4139d77e7126c1cf963811a44` | `IdentityStage` is a passthrough stage: `is_passthrough()` is true, `process()` rejects null input/output and `memcpy`s `frames*channels` floats, `reset()` is a no-op, factory ignores `PrepareContext`. This is source evidence only, not an installed SDK provider. |
| `adapters/controls/adapter.json` | `3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599` | `harness-controls-v1`, protocol 1, waveform input, waveform/annotation output, offline `CLN-01`/`DET-01`, controls `identity`, `all_speech`, `no_speech`, Python entrypoint. `identity` here is a harness control, not a provider registration or default. |

Task base: `3e2192f5676ffe9d54fd5fc5b7c3710b4bb87f41`.
Branch: `swarm/SDK-IDENTITY-PCM-AND-NOOP-FIXTURES`.
Task-local write scope:
`docs/task-evidence/identity-pcm-and-noop-fixtures/`.

## Task-local evidence

| Path | Purpose |
| --- | --- |
| `fixture.py` | Deterministic caller-owned PCM generator (357 exact `k/128` float32 values in 160/160/37 frames), canonical JSON and source pins |
| `test_fixture.py` | Seven deterministic unit checks, including optional byte verification of both source pins |
| `identity_provider.c` | Task-local D=0 identity/noop provider table; mode 2 only, no assets, no faults |
| `config/config.json`, `config/descriptor.h.in` | Canonical config and descriptor template with configure-time source/config digests |
| `main.c` | Installed-prefix consumer: one typical API use, eight malformed/lifecycle probes, missing/unadvertised selections, installed conformance invocation |
| `CMakeLists.txt` | Clean consumer build against installed `AudioSDK::audio_sdk` and installed `checks.c` |
| `canonicalize.py` | Canonical report normalization and SHA-256 sidecars |
| `run_installed.sh` | Clean checkout build → scoped package → extract → installed consumer → reports; all outputs outside the worktree |
| `stage_scoped.py`, `package_scoped.sh` | Task-local release staging with an explicit source list: shared `SOURCE_PATHS` except broad `docs`, plus `docs/migration/source-allocation.csv` and this task's evidence tree; all shared verification steps are retained |
| `.gitattributes` | Marks this README `export-ignore` in release archives so its recorded digests cannot alter the archive digest they describe; the README remains committed in the repository and PR |

## Exact commands

Use the clean post-commit SDK worktree at the exact head under test. The
compiler embeds absolute source paths in the release binaries, so the same worktree
path is part of reproducing these archive digests:

```sh
task_dir=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-IDENTITY-PCM-AND-NOOP-FIXTURES/docs/task-evidence/identity-pcm-and-noop-fixtures
scratch=$(mktemp -d /private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/identity-pcm.XXXXXX)
for run in run-a run-b; do
  "$task_dir/run_installed.sh" "$scratch/$run" \
    /Users/htsakanyan/workspace/audio/audioml > "$scratch/$run.log" 2>&1
done
diff -r "$scratch/run-a/reports" "$scratch/run-b/reports"
python3 -m json.tool "$scratch/run-a/reports/summary.canonical.json" >/dev/null
python3 -m json.tool "$scratch/run-a/reports/consumer-report.canonical.json" >/dev/null
python3 -m json.tool "$scratch/run-a/reports/conformance-report.canonical.json" >/dev/null
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-IDENTITY-PCM-AND-NOOP-FIXTURES diff --check
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-IDENTITY-PCM-AND-NOOP-FIXTURES
```

The fixture tests skip only the two source-byte pin assertions if
`IDENTITY_CPP` / `ADAPTER_JSON` are not supplied; the run above supplies both.
No generated build, report or `__pycache__` file is written inside the worktree.

## Measured run (macOS arm64, AppleClang 21.0.0, CMake 3.27.4, Python 3.11.5)

All digests below were produced from the clean post-commit SDK worktree at the
exact head of this change, twice, with byte-identical canonical reports. The
release archive is explicitly scoped by `stage_scoped.py`: it keeps every shared
source path except broad `docs`, then adds only
`docs/migration/source-allocation.csv` and this task's evidence subtree, so
unrelated merged docs cannot change its bytes; the merged `analysis-events`,
`elastic-pcm-packets` and `neural-runtime-boundary` trees are verified absent
from the archive. The digest-bearing README is `export-ignore`d by the task-local
`.gitattributes`, so its own values cannot
perturb the archive digest; all fixture code and tests remain in the archive.
The commit uses fixed author/committer date `2026-11-23T00:00:00Z` so archive
tar timestamps are also reproducible. The conformance digest stays
`d4286e9cd4c40231c698d22995bd0a6021c5ca9e563465fd7b4a87d2b6bf530a` because it
covers the unchanged fixture-provider conformance report, not the archive. Only
the archive-dependent consumer and summary digests changed from the earlier
pre-commit run.

Installed version and provenance:

- Version `0.1.0`; build ID
  `audio-sdk/0.1.0+sha256:0bc71dcab04880033a4ad4c1cfcebb8a05eccb11a20a786b9c844e394c035972`.
- Clean post-commit checkout at the exact head of this change, native Release
  build, normalized extracted archive.
- Archive SHA-256
  `740ce666c8f351b65a53e5bffabb77a18ef73aaf5c12f590456ced3cd5b0b423`.
- Measured install prefix: `<scratch>/run-a/extracted/audio-sdk-0.1.0` in the
  reproduction above; `run_installed.sh` prints the concrete path.
- Fixture provider descriptor digest
  `ab014c584db1d66527a31e3b7ea68165c5979d930d761a8463574d3edd095d08`;
  descriptor source digest
  `0daeabcc8b178310f79f0896772deb4a7ffb229b29297b33d3f494513c015e60`;
  config digest
  `4bba6f787b749ef5a5f3913dcd229b6068f7e69b442f46665ddf878dd4cbff8f`.

### Compile/build evidence

- SDK configure, build and native CTest: **11/11 passed** (including built-in
  high-pass and Speex conformance).
- `scripts/package.sh` and archive extraction: passed; archive digest above.
- Installed consumer configure and build against `AudioSDK::audio_sdk`: passed.
- Installed consumer CTest `identity_pcm_exact_baseline`: **1/1 passed**.

### Synthetic runtime evidence

- Fixture payload digest (canonical JSON, 4074 bytes):
  `4e5255802e2be73b84599979855d59d03a4f06eff8e439d23ab7ee09e95be459`.
- Caller-owned 357-sample stream (160/160/37, first source sample
  `9007199254740993 = 2**53+1`) processed with byte-identical output, D=0
  metadata, zero-padded final frame and clean EOS drain.
- Installed `checks.c` conformance for `fixture.identity-pcm.v0`:
  **35 pass, 0 fail, 2 skip** of 37 checks. The 40-check installed delay0
  fixture remains a separate historical control; this task-local provider
  declares mode 2 only, which changes the expected check set.
- Python fixture tests: **7/7 passed**, including both source-pin digests.
- Canonical report digests (newline-terminated files; digests cover canonical
  JSON without the terminal newline):
  - `consumer-report.canonical.json` —
    `e72ee021231151fe3ef26061c8e9d9aea2d0994fc980d8037b8623034b25a58b`
  - `conformance-report.canonical.json` —
    `d4286e9cd4c40231c698d22995bd0a6021c5ca9e563465fd7b4a87d2b6bf530a`
  - `summary.canonical.json` —
    `87ac3fab2ffae8cf275a7205b844933aa2288b4ba5d38b54c5856170778d9bd5`
  - `.sha256` sidecars are emitted beside each report.

### Explicit invalid, missing and adverse controls

- Eight malformed/lifecycle probes returned zero-valid `AS_INVALID_ARGUMENT`:
  partial frame without `FINAL_INPUT`, nonfinite sample, stale epoch, wrong
  position, null input, short output capacity, short struct header, and
  process after final input.
- Missing/unadvertised selections returned `AS_UNSUPPORTED` or
  `AS_INVALID_ARGUMENT`: unregistered provider ID, unadvertised mode 1 and
  mode 3, unregistered session create, and an unrequested asset (descriptor
  declares zero assets).
- Installed conformance negative checks passed (`create.reject.*`,
  `args.invalid`, `registry.*`, `drain.eos`, `reset.epoch`).
- **Skipped, not passed:** `registry.busy` (external providers are not
  installed in a second registry) and `buffered.flow` (mode 3 is not declared
  by this fixture). The summary is therefore intentionally `incomplete`; a
  skip is never counted as a qualifying result.
- No failed case remains in the final run.

### Measured workload support

**Not measured.** No pacing, CPU load, deadline, queue-under-load, device,
microphone, model inference, real-audio quality or release evidence was
collected. Source timestamp subtraction and this synthetic conformance suite
do not establish physical availability delay. The fixed v0 contract remains a
control only.

## Boundary and reopen conditions

This closes only the task-local identity PCM/noop fixture question. It does not
add a built-in identity provider, a chain/graph API, a callback-safe path, a
new descriptor, a default behavior change or a release candidate. Reopen when
one of the following has an exact scoped decision: promotion of identity/noop
to a built-in provider; a versioned public chain/graph interface needing a
bit-exact two-stage baseline; mode 3 conformance for this fixture; measured
installed workload/pacing and target-device evidence; or any change to the two
pinned source files above.

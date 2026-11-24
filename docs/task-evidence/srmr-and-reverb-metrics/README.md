# SRMR and reverb metrics — task-local evidence adapter

Task: `SDK-SRMR-AND-REVERB-METRICS`. Base: `a64e1096905f0d05a46303fc0167b6f356027765`.

## Decision

- **Proceed** with an opt-in, unregistered, disabled-by-default developer/evidence adapter.
- **Defer** any SDK processor exposure. No provider is registered, no descriptor or
  default changes, no public API/ABI change, no Bench bundle and no build bytes are added.
- SRMR is reported as **complementary, non-intrusive dereverb evidence** alongside
  paired quality metrics and blind listening. It is never a selection criterion alone.

## Exact scope

Synthetic/frozen evidence only: one analytic eight-syllable source, three deterministic
synthetic RIRs from pinned seeds, and a C50-style early-to-late RIR energy proxy. There
is no real RIR, device capture, listening study, quality claim, pacing claim, release
gate or public-benchmark claim. REVERB Challenge material is cited in the research
source but is not staged or scored here. No Tiny16 adverse comparison is made.

## Pinning

- SRMR scorer: SRMRpy commit `fee009779cef96bed34db3a7e31d10f3ad1ea133`, fast path,
  `norm=False`, MIT. Pinned archive SHA-256
  `9163eb964e77a6e42ada5b7320869036f3e553eef018c9be457e86c51084703a`.
- Dependency: Gammatone `1.0.3` `fft_gtgram`, BSD-3-Clause. Pinned wheel SHA-256
  `410a07344bacac651c3d8d466e25888e1925f00458f054871485c0aa22d78061`.
- The runtime scorer is a dependency-free stdlib port. Two upstream cross-checks on the
  pinned synthetic cohort agree with a maximum absolute delta of `1.1546e-14` against a
  pinned tolerance of `1e-9`. The upstream implementation is not installed or imported
  by the adapter.
- All source, provenance and implementation digests are in `SOURCES.sha256`. External
  lines are provenance metadata; verification is offline and never downloads anything.
- `contract.json`, `adapter.json` and `provider.json` pin the evidence profile,
  opt-in/unregistered boundary and default-OFF state.

## Pinned results

| Case | RT60 (ms) | C50 proxy (dB) | Full-RIR SRMR | Early-target SRMR |
| --- | ---: | ---: | ---: | ---: |
| short_rt60 | 250 | 15.872107323614 | 8.841079147552 | 11.391122657889 |
| medium_rt60 | 550 | 7.379982952271 | 5.875231208862 | 15.087643725732 |
| long_rt60 | 900 | 3.502427779020 | 3.925665600942 | 8.175056584125 |

Dry-source control SRMR: `5.937336690169`. The source-dependent control is not an
outcome cohort. The matched synthetic pattern is decreasing SRMR and C50 proxy with
increasing pinned RT60. The aggregate median full-RIR SRMR is `5.875231208862`; no
threshold, selection or ranking claim is made.

Invalid/missing cases (`missing_samples`, `empty_samples`, `nonfinite_samples`,
`silence`, `unsupported_sample_rate`) are rejected with explicit reasons. The
`medium_rt60_input` representative result, identity repeats and upstream cross-checks
are recorded in `report.json`. Source-reported upstream model scores and all human,
real-input and official-benchmark evidence are separated and excluded from results.

## Commands

Run from this directory. Only Python 3 standard library is required at runtime.

```sh
python3 run.py --report                 # rewrite report.json and report.json.sha256
python3 -m unittest discover -v         # 6 task-local tests
python3 verify.py                       # read-only byte, pin, schema, repeat, scope checks
```

Three consecutive `python3 run.py --report` passes produced identical canonical
digests `86fc93af0ee80ebcdb9e6a35dd8174e99c4d5513caa7778451746781647dbd42` and
identical file bytes `291897aaacb9d16a40bb68a64dfb84d2c03a559ca9997a9e5fb1c718d633b979`.
`verify.py` also rebuilds the report three times in memory without writing and compares
those bytes to the committed report.

SDK baseline verification was run outside the worktree with a temporary build tree:
CMake configure and Release build succeeded, and CTest passed `11/11` tests.

Board check was run read-only from the main repository:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-SRMR-AND-REVERB-METRICS
```

## Remaining gates

Exact-head independent review, hosted CI, scorer license/version intake, rights-cleared
RIR and speech inputs, paired quality metrics under a fixed protocol, blind listening,
and release approval before any processor exposure.

## Report digests

- Canonical report SHA-256 (`report.json.sha256`):
  `86fc93af0ee80ebcdb9e6a35dd8174e99c4d5513caa7778451746781647dbd42`
- `report.json` file SHA-256 including its trailing LF:
  `291897aaacb9d16a40bb68a64dfb84d2c03a559ca9997a9e5fb1c718d633b979`
- `SOURCES.sha256` file SHA-256: see verification output and the final task report.

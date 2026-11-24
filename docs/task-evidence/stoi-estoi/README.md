# STOI / ESTOI task-local evidence

Owner: `agent-stoi-estoi` · Base: `a64e1096905f0d05a46303fc0167b6f356027765` · Decision: **defer** processor exposure.

## Scope

This directory retains a reproducible, opt-in STOI/ESTOI comparison for
`SDK-STOI-ESTOI`. It is task-local developer evidence under the `evidence`
acceptance profile. It adds no SDK provider, descriptor, registry entry,
CMake target, public API/ABI, default, shared code or audio-bench metric.
The adapter is Python-only, unregistered and default-off by construction.

Everything here is synthetic. No recording, corpus, model, device, listener,
network fetch, asset or report from a public benchmark is required to
regenerate the result. External pystoi 0.4.1 was used only in a scratch venv
outside the worktree to record the cross-check vectors; it is never an oracle,
threshold or candidate result.

## Pins

- pystoi 0.4.1 source `pystoi/stoi.py`: `482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658`
- pystoi 0.4.1 source `pystoi/utils.py`: `0222df0354a248ccc7f8525eda9bda9da815e5d60106f611a5f4750d1ba7f321`
- Algorithm pins: `pystoi-0.4.1.non-extended.algorithm-port.no-dither`, `pystoi-0.4.1.extended.algorithm-port.no-dither`
- Fixture `stoi-estoi-synthetic-target-masker-v1`: 16 kHz mono, 9,600 samples/item, seed `20261124`, clean digest `6f0420bafb9f5a77af6de01b8fc8dc6ee645cbe8da4c2d73c091c64fbfbf92ca`
- Masker digests: steady `b6567fbeb780f01f687a513df02407d953f18a5f5697679a9fd4bff03502a386`; modulated `8861ea2ad4d8de64dc83c9ded3e0e466f4f1e0c53b55961f28c091a52059e9b6`
- Cross-check vectors SHA-256: `b31018f150c1b8e852f48d621c32217e57279c4eee72d692844e736a03ca4546`
- Canonical report SHA-256: `1557ea1b0079f4ad5856e15f54add1af5d4fb09f5a0a863ede7f346369598ead`
- Report file SHA-256 (trailing newline): `a74820ff3e42f80d5ab06038de6ec70989876c6d91b98b34dc059ed2a6858f82`

The only intentional difference from upstream pystoi is omission of its
machine-epsilon Gaussian dither in `row_col_normalize`, so repeated scores are
byte-identical. The 12 recorded external comparisons have exact recorded
absolute deltas of `2.1510571102112408e-15` for STOI and `1.0075273948473296e-14`
for ESTOI; no acceptance tolerance is defined or widened.

## Matched comparison

Six paired items: two deterministic masker realizations (steady and 4 Hz
gated) at −5, 0 and +5 dB. Each item reuses one clean target and one masker
across `identity_noisy`, `less_masker`, `more_masker`, `tilt`, `gain_only`,
`missing`, `nonfinite` and `short`. The first five are scored; the last three
are failure controls. Deltas are candidate minus `identity_noisy` per item and
metric, then averaged with equal item weight. There is no bootstrap, ranking,
pooling or threshold.

| Variant | Mean Δ STOI | Mean Δ ESTOI | Paired |
| --- | ---: | ---: | ---: |
| `less_masker` | +0.147642 | +0.054286 | 6/6 |
| `more_masker` | −0.082749 | −0.026072 | 6/6 |
| `tilt` | +0.001623 | +0.001005 | 6/6 |
| `gain_only` | −0.022182 | −0.007044 | 6/6 |

All six identity-noisy pairs are scored. `missing` is blocked
(`missing_input`) in all six, `nonfinite` is invalid (`nonfinite_input`) in all
six, and `short` fails (`invalid_geometry`) in all six. Failed items list is
empty because the three controls are not candidate comparisons. Adapter bundle
validation covers one representative valid result, one missing case and the
developer-only inspect response; all three checks pass.

## Interpretation

STOI is the non-extended per-band temporal-envelope correlation. ESTOI applies
row/column normalization to the same 1/3-octave envelope segments and is
intended to be less sensitive to masker envelope modulation. On this synthetic
cohort the ESTOI-minus-STOI identity mean is `−0.204047` under the steady
masker and `+0.004584` under the modulated masker. That is a scorer-behavior
difference on generated signals, not evidence of speech intelligibility,
listening benefit, enhancement quality or processor superiority.

The historical CLN-12 screen in `research/listening_intelligibility_20261028.md`
reported source means for fixed tilt of STOI `0.7006` and ESTOI `0.5760`
versus identity `0.6897` and `0.5719`, with a bootstrap interval crossing zero.
It used EARS/VADToolkit material and is retained only as provenance; it is not
reproduced here, clears no rights and establishes no listener result.

## Reproduction

Run from this directory. Python 3.11+ and the standard library are sufficient.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
```

`test_reference.py` has 9 cases, including three cold-start `run.py --report`
repetitions asserted byte-identical. `verify.py` rechecks strict JSON, the
source manifest, canonical bytes, three in-process repeats, exact recorded
cross-check deltas, opt-in scope and fixture pins. The board check is run
read-only from the separate platform repository:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-STOI-ESTOI
```

## Remaining gates

Exact-head independent review; hosted CI; rights-cleared held-out inputs with
pinned provenance and a declared protocol; approved independent reference
adapter plus S10/protocol clearance and a permitted case manifest before any
adverse Tiny16 comparison; pystoi/runtime scorer license and version intake;
release approval. No processor, default or public benchmark change is proposed
by this evidence.

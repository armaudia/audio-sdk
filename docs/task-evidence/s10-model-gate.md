# S10 Tiny16 gate: evidence and exact prerequisites

## What was checked

The read-only consumer artifact
`../audio-pro/processors/fastenhancer_tiny16/model-contract.json` identifies
ONNX SHA-256
`a64663672b31bd1445502ee23328d291af13fb312e11bb574c010e7261a5ee7d`, a
16 kHz mono model with 512-point periodic-Hann STFT, 256-sample hop, 16-frame
recurrent cache, and graph cache inputs `cache_in_0` through `cache_in_3`.
Its timing fields report 256 samples buffering delay, 256 invalid startup
samples, two flush hops, and a finite drain bound of four calls. These are
inspected metadata; they are not runtime observations.

The upstream primary source is
[`aask1357/fastenhancer`](https://github.com/aask1357/fastenhancer). Its
README calls it the official repository, links the FastEnhancer paper and says
ONNX models are provided in releases with streaming inference documented
separately. GitHub labels the repository as MIT-licensed. That repository
license/release listing does not, by itself, establish a model-specific grant
for these ONNX bytes or their converted weights. The model-specific grant and
scope remain unknown; no external party was contacted.

`../audio-pro/docs/rights-register.md` separately marks acquisition,
evaluation, redistribution, customer deployment, and public playback for both
Tiny16 ONNX and derived native weights as unknown. The model must not be
executed, repackaged, or represented as approved on the basis of possession,
metadata inspection, synthetic tests, or the engine-source MIT license.

## Exact remaining inputs

1. A recorded model-owner/upstream license or grant tied to the exact ONNX
   digest, explicitly allowing evaluation. This is needed before loading real
   weights or claiming parity.
2. Separate explicit rights decisions for redistribution of ONNX and converted
   weights, customer deployment, and public playback; an evaluation grant does
   not imply any of those.
3. The exact model bytes and their integrity-verified conversion output in the
   authorized evaluation environment.
4. A pinned inference runtime/build for execution, plus upstream/reference
   traces or an independently runnable reference path to verify tensor values,
   state, preprocessing, 256-sample hop, declared delay, and finite drain.

No Tiny16 runtime/reference trace was fabricated here. S10 remains blocked;
synthetic/zero-weight behavior is not parity evidence.

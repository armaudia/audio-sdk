<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-CHATTERBOX-NANO

This task-local evidence package is authored under Apache-2.0. It includes no
vendored Chatterbox source, generated waveform, binary, model weight, tokenizer
asset, runtime, license text, notice or corpus from Resemble AI or any third
party. It pins read-only files by SHA-256 and records provenance only.

The upstream Chatterbox code checkout is present at revision
`5de7a54aa4e5e2baadb0182dde554908b48b85c2` and carries an MIT `LICENSE`
(SHA-256 `4248e910a928849fe5815a0f9236e17fa07768d95b9193212752c464b93d6caa`).
That MIT text is **not copied** into this directory. The code license is a
source-code grant only: it does not establish terms for the
`ResembleAI/chatterbox-nano` weights, tokenizer assets, model card, reference
voices, consent, training data or generated-output use.

No weight, model-card, reference-voice, consent or output-use term has been
staged or reviewed. The historical run used one LJ Speech clip as a prompt; the
research record describes LJ Speech as public domain, but this package treats
that as an unverified provenance note, not a consent or output-use clearance.
The historical p360 target belongs to a different voice-conversion task and is
not used here.

No file in this directory may be treated as an upstream license grant, a weight
term, a reference-voice consent record or a product-use decision. A future
qualified run must stage the exact weight/model-card terms, the complete notice
bundle and explicit consent, reference-availability and output-use records
before any artifact is used (see `BLK-01`, `BLK-03` and `RG-02`/`RG-04` in
`contract.json`).

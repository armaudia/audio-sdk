<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the JSON and manifest
files). It contains only text, JSON and Python source.

## Neural and Kalman source, algorithm and parameters

No neural network implementation, weight loader, inference path, Kalman
filter, covariance update or parameter/config file is present. The pinned
feedback-control census names the neural/Kalman hybrid family and cites
NeuralKalmanAHS, HybridAHS and AHS_2023, but records no repository carrying
source at a revision, no license text, entry point, per-file digest or tuning
constants. No upstream source, header, test or license text is copied into this
package. The source, algorithm and license terms remain exact open blockers.

## Model weights and checkpoints

The hybrid family requires trained weights. No checkpoint, weight fragment,
converted tensor, training script or reconstruction is included, and no weight
file is opened, loaded or executed. The named public leads were observed to
expose demo material only and no release asset was listed. Mere local possession
would not be treated as rights evidence. Checkpoint SHA-256, byte count, format,
provenance and weight terms remain independent open blockers.

## Corpus, loop references and outputs

No microphone recording, playback reference, target speech, measured impulse
response, calibrated loop gain, delay, saturation record or output-use grant is
present. AMI and SMARD are cited only through pinned research reports; they are
not staged, redistributed, decoded, played or admitted here. Corpus,
closed-loop, held-out physical path and output rights remain independent open
gates.

## No vendored media or weights

This directory contains no `.wav`, `.flac`, `.pt`, `.pth`, `.onnx`,
`.safetensors`, binary library or compiled object, and no vendored upstream
license text.

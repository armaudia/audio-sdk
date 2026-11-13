# audio-sdk repository handoff

Planned public repository. This directory currently contains implementation instructions, not a working SDK or an initialized Git repository.

Read [the shared handoff](../plan/implementation_handoff_20261113.md), then [implementation steps](IMPLEMENTATION_PLAN.md), [the v0 contract](CONTRACTS.md) and [test plan](TEST_PLAN.md). This repository owns runtime/provider contracts, descriptors, reference correctness and standalone conformance. It must build without audio-bench, audio-pro or a network catalog.

Initial deliverable: fixed-rate mono 16 kHz C/Python SDK, SpeexDSP and high-pass provider switching, sequential engine and optional LiveKit integration. Binary plugin stability and external engines are separate later releases.

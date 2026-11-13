# Legacy `ae_*_v1` migration status

This SDK currently provides a fresh C11 v0 facade. It does **not** export the
original `ae_*_v1` symbols or preserve the original ABI layouts. The previous
application API remains in the sibling `cpp-library` repository and was not
copied into this SDK.

Consumers must migrate to `as_registry_v0` / `as_session_v0` and the v0
provider descriptors. This is an outstanding breaking change, not a
compatibility shim. Do not claim binary or source compatibility with
`audio_enhance` 1.x. A deliberate adapter requires a separate task and ABI
review; it must not rename, reinterpret, or mock the old structures.

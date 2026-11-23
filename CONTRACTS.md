# Normative source-linked v0 contract

Contract revision `0.1`, 2026-11-13. The public declarations are implemented under api/include/audio_sdk; core implementation files are under core/. Function names below are the implemented source-linked v0 interface. They do not replace the layout of `ae_*_v1` types in the original application header. A compiled header and installed consumer are required before claiming compatibility.

## C boundary and types

Create `api/include/audio_sdk/provider_v0.h` and `api/include/audio_sdk/session_v0.h`. Use C11-compatible declarations, `extern "C"` under C++, SDK export visibility and `AS_CALL` (`__cdecl` on Windows, empty on supported Unix). Do not pack structs. Every request/result/table begins with `uint32_t struct_size, abi_major, abi_minor`; ABI major/minor values are `0,1`. Reject another major or a size smaller than the known mandatory prefix. Accept larger structures from the same minor only when unknown trailing bytes and reserved fields are zero. An unsupported minor fails `AS_UNSUPPORTED`; do not guess optional semantics. Initialize all known result fields, even on failure. Add helpers for each initializer. No bitfields, `bool`, `long`, STL, C++ references, exceptions or variadic functions.

Use `int32_t as_status_v0`; assign explicit constants: `AS_OK=0`, `AS_INVALID_ARGUMENT=1`, `AS_UNSUPPORTED=2`, `AS_RESOURCE_EXHAUSTED=3`, `AS_BACKEND_FAILURE=4`, `AS_NEEDS_RESET=5`, `AS_NOT_READY=6`, `AS_END_OF_STREAM=7`, `AS_BUSY=8`, `AS_CLOSED=9`, `AS_DUPLICATE=10`. `END_OF_STREAM` means a completed drain, never an ordinary successful process frame. Result validity is zero on every non-OK status. Map these to legacy `ae_status` only in a documented adapter; do not assume equal numeric values.

Opaque types: `as_registry_v0`, `as_session_v0`; provider instances are `void *` owned and freed by their provider. No unloading API exists in v0. Code/function table lifetimes extend until registry destruction after its last session closes. The registry copies descriptor/configuration bytes; callers may release those input bytes after successful control calls.

All byte-string inputs are `(const char *, uint32_t length)` with no implicit NUL. Length excludes NUL. UTF-8 text is validated; IDs are ASCII `[a-z0-9][a-z0-9._-]{0,95}`. Config/descriptor control payload maximum is 64 KiB. Error struct: header, status, `char message[256]`, `char field[96]`; terminate both, truncate safely, never include secrets/local asset paths in exported errors. Required process diagnostics use status/counters, never log from real-time code.

`as_asset_v0`: header; asset ID bytes/length; SHA-256 raw 32 bytes; immutable data pointer; `uint64_t byte_count`. The descriptor declares every external asset as `{byte_count,id,sha256,storage:"external"}`. The caller supplies exactly those assets in descriptor order; ID, size, configured hash, and actual bytes must all match. The facade copies bytes during preparation, verifies the digest, and retains owned copies through provider destruction (maximum 512 MiB total external assets per session). Caller buffers may be released after create returns. Embedded assets are not supported by contract 0.1 and must not appear in `required_assets`; a later contract revision may define them. Providers may retain immutable asset pointers only for the session lifetime. No provider file access or model download is permitted in process/drain. Empty asset arrays are used by the initial DSP providers.

`as_create_config_v0`: header; `uint32_t sample_rate_hz, channels, frame_samples, execution_mode`; `uint64_t epoch`; `int64_t first_input_sample`; canonical effective-config bytes/length; pointer/count of immutable assets. Mode constants: `1=inline_callback`, `2=processing_thread`, `3=buffered_worker`. v0 accepts only 16000/1/160 and nonnegative first input sample. Asset count maximum 16. Invalid/unknown settings fail before instance creation.

`as_frame_v0`: header; `const float *input`; `uint32_t input_count, input_valid_count, flags`; `uint64_t epoch`; `int64_t first_input_sample`. Process input_count is exactly 160. input_valid_count is 160 normally; 1–159 only with `AS_FINAL_INPUT=1`. The final frame is zero-padded by the caller; the facade verifies padding is zero. Zero-length streams go directly to drain. Other flag bits fail. After FINAL_INPUT no further process is admitted. All valid input values must be finite, with no undocumented clipping at the facade boundary.

`as_output_v0`: header; `float *samples`; `uint32_t capacity`; capacity must be at least 160. Buffers have natural float alignment, cannot overlap input or provider state. Extra capacity is unused. Provider never retains caller input/output pointers. Payload beyond produced_count is not read. On failure the facade zeros the first min(capacity,160) samples only after output alignment/capacity/non-overlap validation succeeds; invalid pointers or overlap never trigger a speculative memory write.

`as_result_v0`: header; status; `uint32_t consumed_count, produced_count, valid_offset, valid_count, flags`; `uint64_t epoch`; `int64_t source_first_sample`; `uint32_t queue_depth, reserved[3]`. Valid samples are `[valid_offset, valid_offset+valid_count)` within the produced output. `source_first_sample` maps samples[0] into the source coordinate system; it may be negative during startup. The first valid source position is source_first_sample+valid_offset. Flags are `1=startup_padding`, `2=final_padding`, `4=concealment`; flags are independent of value being zero. Concealment always has valid_count=0. Separate session counters track rejections, errors, submitted/accepted/produced/delivered valid samples and discarded intervals. These are uint64 internally, exported as exact decimal strings.

## Provider table and operations

The provider table contains the common header, zero reserved fields, and these required function pointers, with `AS_CALL` and no throwing implementation:

```c
as_status_v0 create(const as_create_config_v0 *config,
                    void **out_instance, as_error_v0 *error);
as_status_v0 process(void *instance, const as_frame_v0 *frame,
                     const as_output_v0 *output, as_result_v0 *result);
as_status_v0 reset(void *instance, uint64_t epoch,
                   int64_t first_input_sample, as_error_v0 *error);
as_status_v0 drain(void *instance, const as_output_v0 *output,
                   as_result_v0 *result);
void destroy(void *instance);
```

`as_register_provider_v0(registry, table, descriptor_bytes, length, error)` copies immutable descriptor/table on the control thread. Duplicate provider ID is rejected, even if table bytes match. `as_query_provider_v0(registry, id, id_length, buffer, capacity, required_size)` returns descriptor bytes; null buffer/capacity=0 reports required size, insufficient capacity returns RESOURCE_EXHAUSTED without partial output. Registry mutation is forbidden after its first session is created; no global mutable default registry.

Linking an external provider does not register it. The application opts in by
registering it on its own registry before the first session, then selecting its
ID and a mode advertised by its descriptor. Unregistered IDs and unadvertised
modes return `AS_UNSUPPORTED`; there is no automatic discovery or fallback.
Public release admission is separate from application-local registration.

Create sets *out_instance=NULL before validation. Success means fully prepared state and all scratch allocated. A separate prepare function is intentionally absent: creation performs preparation. If creation fails, no live instance or leaked allocation remains. Session wrappers catch all C++ exceptions and convert them to status. Provider implementations must also contain their own language exceptions; the facade cannot safely catch a foreign language unwind across C.

Process has one caller per instance. It must synchronously consume 160 padded samples and produce 160 samples on success, including explicit invalid startup/final padding; valid_count may be less than 160. It verifies epoch and exact next input position. Wrong counts, pointers, capacity, flags, nonfinite input, stale epoch or invalid lifecycle fail without invoking the backend or advancing state. AS_BACKEND_FAILURE may have advanced private state, so the facade enters NEEDS_RESET and admits no more process/drain until reset. A provider returning inconsistent counts/intervals or nonfinite output is treated as backend failure. AS_NOT_READY is not legal from a successfully prepared synchronous provider's process; the facade reserves it for buffered pull with no output.

Reset is quiesced control work; it may allocate and fail. It requires a strictly greater epoch and nonnegative first position. Success clears recurrent/filter state, all sample counters for the new epoch and pending outputs; weights may remain shared. Failed reset leaves NEEDS_RESET. Destroy runs after quiescence, frees with the provider's own allocator and accepts NULL. Facade close takes `as_session_v0 **`, nulls the caller handle, and is harmless for an already-null handle. Calling with a stale freed handle is invalid caller behavior; the contract does not promise to detect use-after-free.

## Session facade and scheduling ownership

Expose registry create/close, provider query/register, session create, synchronous process, buffered submit/pull, begin-drain, drain-next, reset, get-info/get-stats and close under `as_*_v0`. All functions use initialized versioned structs and explicit buffer capacities. Session create receives a registry, provider ID and create config. One provider is sufficient for the initial engine; ordered chains are supported by internal adapters only after all component timing/drain tests pass. No graph, engine plugin, reference audio, batch or dynamic loader entry point is implied.

The public session signatures to implement are:

```c
as_status_v0 AS_CALL as_registry_create_v0(as_registry_v0 **out, as_error_v0 *error);
as_status_v0 AS_CALL as_registry_close_v0(as_registry_v0 **registry);
as_status_v0 AS_CALL as_session_create_v0(as_registry_v0 *registry,
    const char *provider_id, uint32_t provider_id_length,
    const as_create_config_v0 *config, as_session_v0 **out, as_error_v0 *error);
as_status_v0 AS_CALL as_session_process_v0(as_session_v0 *session,
    const as_frame_v0 *frame, const as_output_v0 *output, as_result_v0 *result);
as_status_v0 AS_CALL as_session_submit_v0(as_session_v0 *session,
    const as_frame_v0 *frame, as_result_v0 *acceptance);
as_status_v0 AS_CALL as_session_pull_v0(as_session_v0 *session,
    const as_output_v0 *output, as_result_v0 *result);
as_status_v0 AS_CALL as_session_begin_drain_v0(as_session_v0 *session);
as_status_v0 AS_CALL as_session_drain_next_v0(as_session_v0 *session,
    const as_output_v0 *output, as_result_v0 *result);
as_status_v0 AS_CALL as_session_reset_v0(as_session_v0 *session,
    uint64_t epoch, int64_t first_input_sample, as_error_v0 *error);
as_status_v0 AS_CALL as_session_get_info_v0(as_session_v0 *session,
    char *buffer, uint32_t capacity, uint32_t *required_size);
as_status_v0 AS_CALL as_session_get_stats_v0(as_session_v0 *session,
    char *buffer, uint32_t capacity, uint32_t *required_size);
as_status_v0 AS_CALL as_session_close_v0(as_session_v0 **session);
```

Submit success reports consumed_count=160 (padded frame size), produced_count=valid_count=0; accepted source count is input_valid_count. Pull reports consumed_count=0. Synchronous process is unsupported in buffered mode; submit/pull are unsupported in inline modes. Begin-drain is a control call after the submitter has stopped. Drain-next calls provider drain in inline modes and is equivalent to nonblocking pull in buffered mode, returning NOT_READY while still draining and EOS only after worker completion and empty output queue. It does not block the callback. Caller-buffer JSON info/stats queries use the provider-query required-size rules. Info fields are schema/contract, provider/descriptor/config IDs, format, D, edge exclusions, mode and bounds; stats fields are epoch, submitted/accepted/rejected/delivered valid samples, produced/delivered valid counts, padding counts, cancelled interval/sample counts, failed interval/sample counts, backend failures, queue high-water marks and lifecycle state. Each count uses exact decimal string JSON. Snapshot fields are explicitly versioned/closed; no arbitrary backend metadata.

The reference sequential engine calls one provider synchronously with no worker or hidden queue in modes 1/2. Mode 1 only admits a provider whose descriptor declares callback-safe and whose complete reachable path passes instrumentation; mode 2 permits worker-thread-only inference. Neither mode creates threads. Mode 3 owns exactly one input SPSC queue and one output SPSC queue, capacity three frames each, and one worker per session. The provider cannot create another scheduler for v0. Input queue has one submitter, output queue one consumer. Queue index publication uses release/acquire atomics; submit/pull do not lock, signal, wait, allocate or destroy. Creation rejects mode 3 if required callback-path atomics are not lock-free. The worker consumes one input only after reserving space in the output queue; it never drops a completed output. All queue and scratch memory is allocated during creation. A full output queue stops worker consumption and leads to explicit input backpressure.

`submit` copies the 160 samples and frame metadata; success means acceptance. Full input queue returns RESOURCE_EXHAUSTED with consumed_count=0. It never discards an older frame. `pull` returns the next complete output in FIFO order; empty returns NOT_READY and valid_count=0. The host may request flagged zero concealment via its delivery adapter, but concealment is not a produced provider frame and cannot satisfy sample conservation. Record a missing deadline even if that frame arrives later; late recovery does not erase a miss.

The final marker is stored with the final input; for an exact multiple of 160, `begin_drain` stores the last accepted end position after closing input admission. No end marker competes for a full queue slot: keep an atomic admission-closed/end-position field. The worker finishes queued inputs, drains and marks completed; consumer continues pulling. Shutdown control code joins the worker outside the callback. Never join, wait, allocate or run destruction in submit/pull.

One atomic processing/closing guard rejects concurrent process/reset with AS_BUSY. Applications must stop new callback invocations before close; facade close prevents new admission, requests stop, waits for the worker/current entered processing call on the control thread and then destroys state. Callers retain a session reference for every in-flight invocation; close releases owner reference after these finish. Registry close is AS_BUSY until all sessions close. No stale descriptor/code/state can be freed while referenced.

Lifecycle is `prepared -> processing -> draining -> drained`; creation includes preparation. Backend failure enters `needs_reset`. Reset is permitted from prepared, processing (quiesced), drained or needs_reset; reset during draining is a deliberate cancellation and records abandoned accepted intervals in the old epoch before clearing. Repeated drain after drained returns END_OF_STREAM with zero produced/valid count. Process after drain begins is INVALID_ARGUMENT. Close may cancel without drain; abandoned content is explicit, never called a clean completed stream. Switching means finish/drain/close A and create B with a new epoch; no hot swap or automatic fallback.

## Content mapping, finalization and delay

Use half-open source sample intervals and exact integer arithmetic. For the initial provider, create binds an integer buffering/content-position delay 0 <= D <=16000 samples; a descriptor needing more is unsupported by v0. For process input beginning n, output source_first_sample=n−D. Valid source samples are the intersection of this output interval with accepted source content, excluding only declared fixed edge exclusions. Negative startup coordinates and zero-padded final input are invalid. In a chain, add buffering offsets and intersect validity at every stage; do not count analysis-only delay as audio delay.

This mapping describes buffering and content position, not frequency-dependent acoustic phase/group delay. The high-pass has D=0 buffering; its frequency response remains part of the transformation. Never force a frequency-shaped DSP output to resemble identity by fitting a per-utterance lag. Speex D comes from the isolated pinned library fixture and its documented frame buffering; store the tested integer in the descriptor and fix wrapper metadata if inconsistent. No generic impulse-only estimator determines every model's mapping.

Drain internally supplies provider-specific padding to release accepted source positions up to end_of_input. It reports consumed_count=0 (padding is not newly accepted audio), produced_count from 0 to 160, and valid interval clipped to source end. It can emit AS_OK with output, then END_OF_STREAM; AS_OK with zero output is allowed only within declared max_drain_calls. Cap calls at descriptor max_drain_calls (<=1024); exceeding it is failure. Exclude post-input IIR decay/reverberation tails from wanted content in v0; record their samples as non-content rather than claiming infinite stream duration. Neural wrappers declare their finite padding recipe and maximum calls. Empty input drains immediately.

Example: 320 accepted samples, D=160. First process returns 160 invalid startup samples, second returns source [0,160), drain returns [160,320), then EOS. For 165 accepted samples, second input carries 5 valid +155 zero padding; drain delivers only the remaining accepted range. Unit tests cover D not divisible by 160 and every final input length 1–159. End-to-end conservation is interval union equality with no overlaps, not merely matching total counts.

For legacy ABI evidence before the extension exists, a benchmark adapter may feed a declared number of zero flush frames, discard all positions >=original end and mark the protocol `legacy_zero_flush`. It cannot claim native drain support or extend accepted-audio denominators with those zeros. If independent mapping fails, quality alignment is blocked.

## Descriptor and effective configuration schemas

Create `schemas/descriptor.schema.json` and `schemas/effective-config.schema.json`, Draft 2020-12, schema IDs `audio-sdk/descriptor/0.1` and `audio-sdk/effective-config/0.1`. Close objects with additionalProperties=false. Unknown extensions are rejected in v0; a later schema must explicitly admit namespaced extensions.

Descriptor required fields: schema_id; provider_id; implementation_id; implementation_version; source_revision (immutable commit or null for a content-manifest snapshot); source_digest; contract_version; supported_formats (only f32/16000/mono/160 initially); native_hop_samples; buffering_delay_samples; edge_exclusions (start/end counts); max_drain_calls; callback_safe; execution_modes; configuration_schema_digest; required_assets (IDs/hashes/byte lengths); upstream attribution/license/notice references; platform/CPU requirements. Descriptor is for one immutable package/build, so source/artifact digests are concrete. Do not include the enclosing package's digest inside its own shipped descriptor: package digest is an external release-manifest field. All required scalar limits are nonnegative bounded integers; unsupported capability flags are absent or false.

Effective config required fields: schema_id; application_contract; provider_contract; descriptor_digest; ordered processor IDs/settings/asset hashes; engine=`reference.sequential.v0`; execution_mode; input format/rate/frame; precision; worker_count (0 or 1); input/output queue capacities (0 or 3); adaptation=`off`; batching=false; resampling=`none`; clipping/float-to-int policy. Explicit defaults enter identity. IDs and keys are ASCII; exact nonintegral values are canonical decimal strings (`"80"`, `"0.7071067811865476"`) with schema-declared units. No exponential notation, leading +, redundant leading/trailing zeros or negative zero in decimal configuration strings. Native serializer supports this restricted string/bool/safe-integer/array/object subset with ASCII keys and ASCII runtime configuration string values and deterministic ordering; test its output against RFC 8785 vectors for the admitted subset. Bench uses full JCS to validate/hash received effective config. Reject inputs outside the declared subset instead of silently normalizing Unicode or unsafe numbers. SHA-256 identities cover canonical bytes; volatile paths, clocks and secrets never enter config.

## Timing records

Epoch/sample indices and monotonic nanoseconds serialize as decimal strings, not JSON numbers. Samples are int64, epoch/counters uint64; validate bounds and overflow before arithmetic. Signed canonical pattern is `0|-?[1-9][0-9]*`, disallow `-0`; unsigned omits minus. Runtime C uses integers; JS transport uses BigInt. At 16 kHz one sample is exactly 62,500 ns; source frame k begins at t0+k*10,000,000; it is complete and scheduled for submission at t0+(k+1)*10,000,000. Use a single monotonic clock domain for measured intervals and an explicit stream origin; wall UTC is provenance only. Clock mapping uncertainty is separate from service timing.

SDK conformance verifies sample mapping with identity/delay fixtures and DSP-specific transfer fixtures. Bench owns pacing, CPU accounting and qualification; source timestamp subtraction alone never proves physical availability delay. The above-2^53 round-trip test crosses native trace, Python collection, canonical JSON, export and browser display.

## Follow-on engine v1 design input for S11

This section fixes the initial engine implementation shape so P07–P09 do not depend on an unspecified private API. It is a reviewed-design input to implement/test in S11, not an already stable shipped ABI. Header `engine_v1.h` uses the same C boundary rules, major/minor=1/0, and opaque `as_engine_domain_v1`, `as_engine_stream_v1`. Any change to the following ownership/signatures requires an explicit contract revision and matching conformance update before pro consumes it.

The domain owns workers, input/output queues and all scheduling memory. The common facade delegates admission/enqueue/pull/reset to the domain and adds no queue/pool. Each stream has capacity three input and three output frames, one processing invocation in flight, and at most one output lease held by the caller. The domain creates providers using SDK-approved factories/tables, with independent provider state per stream; providers cannot mutate graph topology or hold domain queues. Engine handles hold provider/registry/code references through quiesced destruction.

`as_domain_config_v1` fields: common header; worker_count (1 initially, 1–8 only when tested); max_streams (1–64); input/output frame capacities (3); max_nodes_per_graph (16); quiesce_timeout_ms (5000); canonical policy bytes/length; allowed provider descriptor IDs; clock callback table (single monotonic domain, no candidate-selected wall clock). Preallocate for max_streams at create; insufficient memory fails admission/preparation, never allocates in processing.

`as_graph_v1` is a control-plane validated descriptor: ordered nodes with stable ID, public provider descriptor/config digest, role (`audio` or `analysis`), and audio/analysis dependency IDs. Initially permit one linear audio path and analysis taps on its nodes; reject audio fan-in, cycles, unsatisfied rate/hop/capability, >16 nodes, unknown required signal and unsupported engine extension. Analysis dependencies must refer to a graph tap and declare max_age_samples. Topology/configuration is immutable while started. Arbitrary DAG/parallel audio mixing is a later capability, never silently accepted/ignored.

Required engine table operation signatures (all return as_status_v0, all AS_CALL):

- `domain_create(config, as_engine_domain_v1 **out, error)` and `domain_close(as_engine_domain_v1 **domain, error)` on control thread; close fails BUSY with live streams, or caller first cancels/removes each stream.
- `stream_admit(domain, graph, as_create_config_v0 *format_epoch_assets, as_engine_stream_v1 **out, error)` allocates/validates provider state before start; deterministic stream ID assigned by facade, separate from pointer addresses.
- `stream_enqueue(stream, as_frame_v0 *input, int64_t capture_first_ns, int64_t deadline_ns, as_result_v0 *acceptance)` copies input on success, owns no caller pointer and returns immediately. Full input/capacity deadline failure is explicit zero acceptance; no input consumed on error.
- `stream_pull(stream, as_output_lease_v1 *out)` is nonblocking FIFO: NOT_READY if empty, EOS only after complete drain. A lease contains immutable samples pointer, result/source metadata, actual output-ready monotonic time, opaque lease_id and domain/stream identity. Caller must release before another pull on that stream. Lease cannot survive stream removal.
- `stream_release(stream, uint64_t lease_id)` returns the output slot without allocation/wait; wrong/duplicate ID is an explicit invalid status, never frees another slot. The facade copies/consumes output before release.
- `stream_end_input(stream, int64_t accepted_source_end, error)` closes admission and schedules bounded drain after queued work. Only control/submit owner calls it after stopping new submission. No fake accepted audio while flushing.
- `stream_quiesce(stream, uint32_t policy, error)` on control thread waits for in-flight work; policy=drain waits until completion while the application keeps pulling, policy=cancel discards queued/unleased work with interval accounting. Drain requires a timeout from config (initial5s); timeout fails and caller may cancel. Never call quiesce from a callback.
- `stream_reset(stream, uint64_t new_epoch, int64_t first_sample, error)` requires no active lease and quiesced state; clears queues/providers and records cancelled old intervals. Unquiesced reset returns BUSY.
- `stream_remove(as_engine_stream_v1 **stream, error)` after quiescence/no lease frees provider state and drops domain references; null repeated remove harmless. `domain_stats`/`stream_stats` are caller-buffer control JSON queries using v0 sizing rules.

Cancellation of a lane/job already in process waits at the control barrier; its output is discarded with reason if its epoch is obsolete. It is never delivered to another stream. A lease outstanding at reset/remove returns BUSY, not a dangling buffer. Domain service failures set affected stream needs_reset; a fatal worker failure closes admission for all affected streams and surfaces their failures independently. No process-global last-analysis flag.

Timed analysis sample type `as_analysis_v1`: common header; producer/provider/tap IDs; stream ID; epoch; source_start/end int64; available_monotonic_ns int64; signal kind (speech_probability initially); float value; uint32 validity; calibration/config digest. Invalid/nonfinite/out-of-range probability is invalid analysis, not nonspeech. Engine compares age in source samples and epoch; it does not choose the newest wall-clock event from an unrelated producer. Fix the chosen source/tap in policy config. No analysis update after stream reset can revive an old event.

Optional public provider transition table uses capability flags; unsupported hooks remain NULL and the engine runs full processing. Hooks are `policy_query(instance, out_bounds)`, `process_mode(instance, frame, output, result, mode)` and `resume_prepare(instance, retained_history, out_warm_frames)` with the same state/buffer contracts as process. Modes full/cheap/observe have exact output/source validity; observe must produce full audio. Bounds declare cheap-state semantics (full-state-update, mathematically equivalent reduced update, or explicit reset-required), finite history/warm samples, crossfade compatibility and invariant D. A hook lacking state/quality proof cannot enable auto skipping. Resume preparation is worker work on preallocated buffers, never callback allocation. Providers without safe transition support are still fully usable by all engines through scalar process.

Optional batch table declares exact model/asset/precision/tensor-state schema IDs, max_batch (2/4 initially), and `process_batch(items,count,results)`. Items carry independent instance/frame/output pointers; incompatible or aliased state fails before any lane changes. Each lane preserves scalar content mapping and lifecycle; no concurrent scalar call to a batched instance. Batch results/failure are per lane; the domain validates each one. Batch wait is part of measured availability/deadline, never excluded as preparation.

S11 must ship a source-independent engine fixture exercising all signatures and provider hooks, including a test provider whose cheap update is provably state-preserving, lease misuse, reset during queued work, slow/failing stream and public/private-compatible combinations. Only then may P07/P08/P09 consume this contract. The scalar v0 reference path remains supported independently.

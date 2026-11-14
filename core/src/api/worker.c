/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
#include "core/as_internal.h"

#include <math.h>
#include <string.h>
#include <time.h>

static uint32_t queue_depth(_Atomic uint32_t *read_index,
                            _Atomic uint32_t *write_index) {
    const uint32_t read =
        atomic_load_explicit(read_index, memory_order_acquire);
    const uint32_t write =
        atomic_load_explicit(write_index, memory_order_acquire);
    return write - read;
}

static int output_has_space(as_session_v0 *session) {
    return queue_depth(&session->output_read, &session->output_write) <
           AS_QUEUE_FRAMES;
}

static void push_output(as_session_v0 *session, const float *samples,
                        const as_result_v0 *result) {
    const uint32_t write =
        atomic_load_explicit(&session->output_write, memory_order_relaxed);
    const uint32_t index = write % AS_QUEUE_FRAMES;
    as_output_slot *slot = &session->output_queue[index];
    memcpy(slot->samples, samples, sizeof(slot->samples));
    slot->result = *result;
    atomic_store_explicit(&session->output_write, write + 1u,
                          memory_order_release);
    const uint32_t depth = queue_depth(&session->output_read,
                                       &session->output_write);
    const uint32_t high = atomic_load_explicit(&session->output_high_water,
                                               memory_order_relaxed);
    if (depth > high)
        atomic_store_explicit(&session->output_high_water, depth,
                              memory_order_relaxed);
}

static void fail_worker(as_session_v0 *session, uint32_t failed_intervals,
                        uint32_t failed_samples) {
    session->worker_failed = 1;
    session->admission_closed = 1;
    session->drain_complete = 1;
    atomic_fetch_add(&session->c_failed_intervals, failed_intervals);
    atomic_fetch_add(&session->c_failed_valid, failed_samples);
    if (failed_intervals != 0)
        atomic_fetch_add(&session->c_backend_failures, 1u);
    atomic_store(&session->lifecycle, AS_LIFE_NEEDS_RESET);
}

static void process_input_slot(as_session_v0 *session,
                               const as_frame_slot *slot) {
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = slot->samples;
    frame.input_count = AS_FRAME_SAMPLES;
    frame.input_valid_count = slot->valid_count;
    frame.flags = slot->flags;
    frame.epoch = slot->epoch;
    frame.first_input_sample = slot->first_input_sample;

    float produced[AS_FRAME_SAMPLES];
    as_output_v0 output;
    as_output_v0_init(&output);
    output.samples = produced;
    output.capacity = AS_FRAME_SAMPLES;
    as_result_v0 result;
    as_result_v0_init(&result);
    const as_status_v0 status =
        as_provider_process_frame(session, &frame, &output, &result);
    if (status != AS_OK) {
        fail_worker(session, 1u, slot->valid_count);
        return;
    }
    as_compute_validity(session, result.source_first_sample, result.produced_count,
                        result.valid_offset, result.valid_count,
                        slot->accepted_end_after,
                        (slot->flags & AS_FRAME_FINAL_INPUT)
                            ? AS_RESULT_FINAL_PADDING
                            : 0u,
                        &result);
    result.status = AS_OK;
    result.consumed_count = AS_FRAME_SAMPLES;
    result.epoch = slot->epoch;
    result.queue_depth = 0;
    session->next_output_sample =
        result.source_first_sample + (int64_t)result.produced_count;
    atomic_fetch_add(&session->c_produced_valid, result.valid_count);
    uint32_t startup_padding = 0;
    uint32_t final_padding = 0;
    as_compute_padding_counts(
        session, result.source_first_sample, result.produced_count,
        slot->accepted_end_after,
        (slot->flags & AS_FRAME_FINAL_INPUT) != 0, &startup_padding,
        &final_padding);
    atomic_fetch_add(&session->c_startup_padding, startup_padding);
    atomic_fetch_add(&session->c_final_padding, final_padding);

    push_output(session, produced, &result);
}

static void drain_one(as_session_v0 *session) {
    if (session->drain_calls >= session->max_drain_calls) {
        atomic_store(&session->lifecycle, AS_LIFE_NEEDS_RESET);
        atomic_fetch_add(&session->c_backend_failures, 1u);
        fail_worker(session, 0u, 0u);
        return;
    }
    session->drain_calls++;
    float produced[AS_FRAME_SAMPLES];
    memset(produced, 0, sizeof(produced));
    as_output_v0 output;
    as_output_v0_init(&output);
    output.samples = produced;
    output.capacity = AS_FRAME_SAMPLES;
    as_result_v0 result;
    as_result_v0_init(&result);
    const as_status_v0 status = as_drain_provider_frame(session, &output, &result);
    if (status == AS_END_OF_STREAM) {
        session->drain_complete = 1;
        return;
    }
    if (status != AS_OK) {
        atomic_fetch_add(&session->c_backend_failures, 1u);
        fail_worker(session, 0u, 0u);
        return;
    }
    as_compute_validity(session, result.source_first_sample, result.produced_count,
                        result.valid_offset, result.valid_count,
                        session->accepted_end, AS_RESULT_FINAL_PADDING, &result);
    result.status = AS_OK;
    result.consumed_count = 0;
    result.epoch = session->epoch;
    result.queue_depth = 0;
    if (result.valid_count > 0) {
        atomic_fetch_add(&session->c_produced_valid, result.valid_count);
        atomic_fetch_add(&session->c_drain_frames, 1u);
        uint32_t final_padding = 0;
        as_compute_padding_counts(session, result.source_first_sample,
                                  result.produced_count,
                                  session->accepted_end, 1, NULL,
                                  &final_padding);
        atomic_fetch_add(&session->c_final_padding, final_padding);
        push_output(session, produced, &result);
    }
}

void *as_worker_main(void *argument) {
    as_session_v0 *session = (as_session_v0 *)argument;
    pthread_mutex_lock(&session->queue_mutex);
    for (;;) {
        if (session->worker_stop) break;
        const uint32_t input_read =
            atomic_load_explicit(&session->input_read, memory_order_relaxed);
        const uint32_t input_write =
            atomic_load_explicit(&session->input_write, memory_order_acquire);
        const int has_input = input_read != input_write;
        if (has_input && output_has_space(session) && !session->worker_failed) {
            const as_frame_slot slot =
                session->input_queue[input_read % AS_QUEUE_FRAMES];
            atomic_store_explicit(&session->input_read, input_read + 1u,
                                  memory_order_release);
            pthread_mutex_unlock(&session->queue_mutex);
            process_input_slot(session, &slot);
            pthread_mutex_lock(&session->queue_mutex);
            continue;
        }
        if (session->admission_closed && !has_input && !session->worker_failed &&
            !session->drain_complete && output_has_space(session)) {
            pthread_mutex_unlock(&session->queue_mutex);
            drain_one(session);
            pthread_mutex_lock(&session->queue_mutex);
            continue;
        }
        struct timespec wake;
        (void)clock_gettime(CLOCK_REALTIME, &wake);
        wake.tv_nsec += 1000000L;
        if (wake.tv_nsec >= 1000000000L) {
            wake.tv_sec++;
            wake.tv_nsec -= 1000000000L;
        }
        (void)pthread_cond_timedwait(&session->queue_cond,
                                     &session->queue_mutex, &wake);
    }
    pthread_mutex_unlock(&session->queue_mutex);
    return NULL;
}

as_status_v0 as_worker_start(as_session_v0 *session, as_error_v0 *error) {
    pthread_mutex_lock(&session->queue_mutex);
    session->worker_stop = 0;
    session->worker_failed = 0;
    session->drain_complete = 0;
    pthread_mutex_unlock(&session->queue_mutex);
    if (pthread_create(&session->worker, NULL, as_worker_main, session) != 0) {
        as_error_set(error, AS_RESOURCE_EXHAUSTED, "worker",
                     "worker thread creation failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    session->worker_started = 1;
    return AS_OK;
}

as_status_v0 as_worker_stop(as_session_v0 *session) {
    if (!session->worker_started) return AS_OK;
    pthread_mutex_lock(&session->queue_mutex);
    session->worker_stop = 1;
    pthread_cond_broadcast(&session->queue_cond);
    pthread_mutex_unlock(&session->queue_mutex);
    pthread_join(session->worker, NULL);
    session->worker_started = 0;
    return AS_OK;
}

/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
#include "test_common.h"
#include "core/as_internal.h"

#include <pthread.h>
#include <time.h>

static pthread_mutex_t g_barrier_mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t g_barrier_cond = PTHREAD_COND_INITIALIZER;
static int g_process_entered;
static int g_release_process;
static int g_fail_process;
static int g_overflow_drain;
static int g_fail_reset;
static int g_block_reset;
static int g_reset_entered;
static int g_release_reset;
static as_session_v0 *g_observe_destroy;
static uint64_t g_closed_samples;
static uint64_t g_closed_intervals;

typedef struct blocking_instance {
    uint64_t epoch;
} blocking_instance;

static as_status_v0 AS_CALL blocking_create(const as_create_config_v0 *config,
                                             void **out,
                                             as_error_v0 *error) {
    (void)error;
    blocking_instance *instance =
        (blocking_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    instance->epoch = config->epoch;
    *out = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL blocking_process(void *opaque,
                                             const as_frame_v0 *frame,
                                             const as_output_v0 *output,
                                             as_result_v0 *result) {
    blocking_instance *instance = (blocking_instance *)opaque;
    pthread_mutex_lock(&g_barrier_mutex);
    g_process_entered = 1;
    pthread_cond_broadcast(&g_barrier_cond);
    while (!g_release_process)
        pthread_cond_wait(&g_barrier_cond, &g_barrier_mutex);
    pthread_mutex_unlock(&g_barrier_mutex);

    if (g_fail_process && frame->first_input_sample == 160)
        return AS_BACKEND_FAILURE;
    memcpy(output->samples, frame->input, AS_FRAME_SAMPLES * sizeof(float));
    instance->epoch = frame->epoch;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_count = AS_FRAME_SAMPLES;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL blocking_reset(void *opaque, uint64_t epoch,
                                            int64_t first,
                                            as_error_v0 *error) {
    (void)first;
    (void)error;
    pthread_mutex_lock(&g_barrier_mutex);
    if (g_block_reset) {
        g_reset_entered = 1;
        pthread_cond_broadcast(&g_barrier_cond);
        while (!g_release_reset)
            pthread_cond_wait(&g_barrier_cond, &g_barrier_mutex);
    }
    pthread_mutex_unlock(&g_barrier_mutex);
    if (g_fail_reset) return AS_BACKEND_FAILURE;
    ((blocking_instance *)opaque)->epoch = epoch;
    return AS_OK;
}

typedef struct reset_args { as_session_v0 *session; as_status_v0 status; } reset_args;
static void *reset_thread(void *opaque) {
    reset_args *args = (reset_args *)opaque;
    as_error_v0 error; as_error_v0_init(&error);
    args->status = as_session_reset_v0(args->session, 4001, 0, &error);
    return NULL;
}
typedef struct close_args { as_session_v0 *session; as_status_v0 status; } close_args;
static void *close_thread(void *opaque) {
    close_args *args = (close_args *)opaque;
    args->status = as_session_close_v0(&args->session);
    return NULL;
}

typedef struct process_args { as_session_v0 *session; uint64_t epoch; int ok; } process_args;
static void *process_thread(void *opaque) {
    process_args *args = (process_args *)opaque;
    as_result_v0 result;
    args->ok = test_process(args->session, args->epoch, 0, &result);
    return NULL;
}

static as_status_v0 AS_CALL blocking_drain(void *opaque,
                                            const as_output_v0 *output,
                                            as_result_v0 *result) {
    if (g_overflow_drain) {
        as_result_v0_init(result);
        result->epoch = ((blocking_instance *)opaque)->epoch;
        result->source_first_sample = INT64_MAX;
        result->produced_count = 1;
        output->samples[0] = 0.0f;
        return AS_OK;
    }
    return AS_END_OF_STREAM;
}

static void AS_CALL blocking_destroy(void *opaque) {
    if (g_observe_destroy != NULL) {
        g_closed_samples = atomic_load(&g_observe_destroy->c_cancelled_valid);
        g_closed_intervals = atomic_load(&g_observe_destroy->c_cancelled_intervals);
    }
    free(opaque);
}

static const as_provider_table_v0 kBlockingTable = {
    (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
    blocking_create, blocking_process, blocking_reset, blocking_drain,
    blocking_destroy, {0, 0, 0, 0}};

static const char kDescriptor[] =
    "{\"buffering_delay_samples\":0,\"callback_safe\":false,"
    "\"configuration_schema_digest\":\"sha256:"
    "0000000000000000000000000000000000000000000000000000000000000000\","
    "\"contract_version\":\"0.1\","
    "\"edge_exclusions\":{\"end_samples\":0,\"start_samples\":0},"
    "\"execution_modes\":[2,3],\"implementation_id\":\"test.blocking\","
    "\"implementation_version\":\"1.0.0\",\"max_drain_calls\":1,"
    "\"native_hop_samples\":160,"
    "\"platform\":{\"architectures\":[\"arm64\",\"x86_64\"],"
    "\"cpu_requirements\":\"baseline\"},"
    "\"provider_id\":\"test.blocking.v0\",\"required_assets\":[],"
    "\"schema_id\":\"audio-sdk/descriptor/0.1\","
    "\"source_digest\":\"sha256:"
    "1111111111111111111111111111111111111111111111111111111111111111\","
    "\"source_revision\":null,"
    "\"supported_formats\":[{\"channels\":1,\"frame_samples\":160,"
    "\"sample_format\":\"f32\",\"sample_rate_hz\":16000}],"
    "\"upstream\":{\"license\":\"MIT\",\"name\":\"first-party test\","
    "\"notice_path\":\"licenses/first-party-MIT.txt\"}}";

static int wait_for_close(as_session_v0 *session) {
    const struct timespec poll = {0, 100000L};
    for (unsigned attempt = 0; attempt < 2000; ++attempt) {
        if (atomic_load(&session->closing)) return 1;
        nanosleep(&poll, NULL);
    }
    return 0;
}

static int check_reset_close(as_registry_v0 *registry, as_create_config_v0 *create) {
    as_error_v0 error;
    as_error_v0_init(&error);
    create->epoch = 4000;
    for (unsigned cycle = 0; cycle < 1000; ++cycle) {
        as_session_v0 *session = NULL;
        CHECK(as_session_create_v0(registry, "test.blocking.v0", 16, create,
                                   &session, &error) == AS_OK);
        g_block_reset = 1;
        g_reset_entered = 0;
        g_release_reset = 0;
        reset_args reset = {session, AS_BACKEND_FAILURE};
        pthread_t reset_id;
        CHECK(pthread_create(&reset_id, NULL, reset_thread, &reset) == 0);
        pthread_mutex_lock(&g_barrier_mutex);
        while (!g_reset_entered)
            pthread_cond_wait(&g_barrier_cond, &g_barrier_mutex);
        pthread_mutex_unlock(&g_barrier_mutex);
        if (cycle == 0) {
            float samples[AS_FRAME_SAMPLES] = {0};
            as_frame_v0 frame;
            as_frame_v0_init(&frame);
            frame.input = samples;
            frame.epoch = create->epoch;
            as_output_v0 output;
            as_output_v0_init(&output);
            output.samples = samples;
            as_result_v0 result;
            as_result_v0_init(&result);
            CHECK(as_session_submit_v0(session, &frame, &result) == AS_CLOSED);
            CHECK(result.consumed_count == 0 && result.valid_count == 0);
            CHECK(as_session_pull_v0(session, &output, &result) == AS_CLOSED);
            CHECK(result.produced_count == 0 && result.valid_count == 0);
            uint32_t required = 1;
            CHECK(as_session_get_stats_v0(session, NULL, 0, &required) == AS_BUSY);
            CHECK(required == 0);
            CHECK(as_session_reset_v0(session, 4002, 0, &error) == AS_BUSY);
        }
        close_args close = {session, AS_BACKEND_FAILURE};
        pthread_t close_id;
        CHECK(pthread_create(&close_id, NULL, close_thread, &close) == 0);
        /* The blocked reset pins the object while the close guard is observed. */
        CHECK(wait_for_close(session));
        pthread_mutex_lock(&g_barrier_mutex);
        g_release_reset = 1;
        pthread_cond_broadcast(&g_barrier_cond);
        pthread_mutex_unlock(&g_barrier_mutex);
        CHECK(pthread_join(reset_id, NULL) == 0);
        CHECK(pthread_join(close_id, NULL) == 0);
        CHECK(reset.status == AS_OK);
        CHECK(close.status == AS_OK && close.session == NULL);
        CHECK(as_session_close_v0(&close.session) == AS_OK);
    }
    g_block_reset = 0;
    return 0;
}

int main(void) {
    as_registry_v0 *registry = NULL;
    as_session_v0 *session = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    CHECK(as_registry_create_v0(&registry, &error) == AS_OK);
    CHECK(as_register_provider_v0(
              registry, &kBlockingTable, kDescriptor,
              (uint32_t)sizeof(kDescriptor) - 1u, &error) == AS_OK);

    char config[4096];
    uint32_t required = 0;
    CHECK(as_effective_config_create_v0(
              registry, "test.blocking.v0", 16, AS_MODE_BUFFERED_WORKER,
              config, (uint32_t)sizeof(config), &required, &error) == AS_OK);
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_BUFFERED_WORKER;
    create.epoch = 1;
    create.config_json = config;
    create.config_json_length = required - 1u;
    CHECK(as_session_create_v0(registry, "test.blocking.v0", 16, &create,
                               &session, &error) == AS_OK);

    float input[AS_FRAME_SAMPLES];
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i)
        input[i] = (float)i / (float)AS_FRAME_SAMPLES;
    input[0] = 1.0f;
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 1;
    as_result_v0 acceptance;
    as_result_v0_init(&acceptance);
    CHECK(as_session_submit_v0(session, &frame, &acceptance) == AS_OK);

    /* The worker has removed frame 0 and is held inside provider process. */
    pthread_mutex_lock(&g_barrier_mutex);
    while (!g_process_entered)
        pthread_cond_wait(&g_barrier_cond, &g_barrier_mutex);
    pthread_mutex_unlock(&g_barrier_mutex);

    for (uint32_t i = 1; i <= 3; ++i) {
        input[0] = (float)(i + 1);
        as_frame_v0_init(&frame);
        frame.input = input;
        frame.epoch = 1;
        frame.first_input_sample = (int64_t)i * AS_FRAME_SAMPLES;
        as_result_v0_init(&acceptance);
        CHECK(as_session_submit_v0(session, &frame, &acceptance) == AS_OK);
    }
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 1;
    frame.first_input_sample = 4 * AS_FRAME_SAMPLES;
    memset(input, 0, sizeof(input));
    input[0] = 5.0f;
    frame.flags = AS_FRAME_FINAL_INPUT;
    frame.input_valid_count = 5;
    as_result_v0_init(&acceptance);
    CHECK(as_session_submit_v0(session, &frame, &acceptance) ==
          AS_RESOURCE_EXHAUSTED);
    CHECK(acceptance.consumed_count == 0 && acceptance.valid_count == 0);

    char stats[4096];
    uint32_t stats_size = 0;
    CHECK(as_session_get_stats_v0(session, stats, (uint32_t)sizeof(stats),
                                  &stats_size) == AS_OK);
    CHECK(strstr(stats, "\"input_queue_depth\":\"3\"") != NULL);
    CHECK(strstr(stats, "\"input_queue_high_water\":\"3\"") != NULL);

    pthread_mutex_lock(&g_barrier_mutex);
    g_release_process = 1;
    pthread_cond_broadcast(&g_barrier_cond);
    pthread_mutex_unlock(&g_barrier_mutex);
    const struct timespec poll = {0, 1000000L};
    for (uint32_t attempt = 0; attempt < 2000; ++attempt) {
        CHECK(as_session_get_stats_v0(session, stats, (uint32_t)sizeof(stats),
                                      &stats_size) == AS_OK);
        if (strstr(stats, "\"output_queue_high_water\":\"3\"") != NULL &&
            strstr(stats, "\"output_queue_depth\":\"3\"") != NULL)
            break;
        nanosleep(&poll, NULL);
    }
    CHECK(strstr(stats, "\"output_queue_high_water\":\"3\"") != NULL);
    CHECK(strstr(stats, "\"output_queue_depth\":\"3\"") != NULL);
    CHECK(strstr(stats, "\"input_queue_depth\":\"1\"") != NULL);

    uint32_t frames = 0;
    uint64_t valid_samples = 0;
    int ended = 0;
    for (unsigned attempt = 0; !ended && attempt < 2000; ++attempt) {
        float output_samples[AS_FRAME_SAMPLES];
        as_output_v0 output;
        as_output_v0_init(&output);
        output.samples = output_samples;
        as_result_v0 result;
        as_result_v0_init(&result);
        const as_status_v0 status =
            as_session_pull_v0(session, &output, &result);
        if (status == AS_NOT_READY) {
            nanosleep(&poll, NULL);
            continue;
        }
        if (status == AS_END_OF_STREAM) {
            CHECK(result.produced_count == 0 && result.valid_count == 0);
            ended = 1;
            continue;
        }
        CHECK(status == AS_OK);
        CHECK(frames < 5);
        CHECK(result.source_first_sample ==
              (int64_t)frames * AS_FRAME_SAMPLES);
        CHECK(result.produced_count == AS_FRAME_SAMPLES);
        CHECK(result.consumed_count == 0 && result.valid_offset == 0);
        CHECK(output_samples[0] == (float)(frames + 1));
        CHECK(result.valid_count == (frames < 4 ? AS_FRAME_SAMPLES : 5));
        CHECK(result.flags == (frames < 4 ? 0 : AS_RESULT_FINAL_PADDING));
        if (frames == 0) {
            /* Retrying the same final source interval must not skip or duplicate it. */
            CHECK(as_session_submit_v0(session, &frame, &acceptance) == AS_OK);
        }
        valid_samples += result.valid_count;
        ++frames;
    }
    CHECK(ended && frames == 5 && valid_samples == 4u * AS_FRAME_SAMPLES + 5u);
    CHECK(as_session_get_stats_v0(session, stats, sizeof(stats), &stats_size) == AS_OK);
    CHECK(strstr(stats, "\"accepted_valid_samples\":\"645\"") != NULL);
    CHECK(strstr(stats, "\"delivered_valid_samples\":\"645\"") != NULL);
    CHECK(strstr(stats, "\"rejected_valid_samples\":\"5\"") != NULL);
    CHECK(strstr(stats, "\"final_padding_samples\":\"155\"") != NULL);
    CHECK(as_session_close_v0(&session) == AS_OK);

    create.epoch = 2000;
    CHECK(as_session_create_v0(registry, "test.blocking.v0", 16, &create,
                               &session, &error) == AS_OK);
    for (uint32_t i = 0; i < 3; ++i) {
        as_frame_v0_init(&frame);
        frame.input = input;
        frame.epoch = 2000;
        frame.first_input_sample = (int64_t)i * AS_FRAME_SAMPLES;
        as_result_v0_init(&acceptance);
        CHECK(as_session_submit_v0(session, &frame, &acceptance) == AS_OK);
    }
    g_fail_reset = 1;
    CHECK(as_session_reset_v0(session, 2001, 0, &error) == AS_BACKEND_FAILURE);
    CHECK(error.status == AS_BACKEND_FAILURE);
    CHECK(as_session_begin_drain_v0(session) == AS_NEEDS_RESET);
    g_fail_reset = 0;
    CHECK(as_session_reset_v0(session, 2001, 0, &error) == AS_OK);
    CHECK(as_session_get_stats_v0(session, stats, (uint32_t)sizeof(stats),
                                  &stats_size) == AS_OK);
    CHECK(strstr(stats, "\"cancelled_valid_samples\":\"480\"") != NULL);
    CHECK(strstr(stats, "\"cancelled_intervals\":\"3\"") != NULL);
    CHECK(as_session_close_v0(&session) == AS_OK);

    create.epoch = 3000;
    CHECK(as_session_create_v0(registry, "test.blocking.v0", 16, &create,
                               &session, &error) == AS_OK);
    g_fail_process = 1;
    g_release_process = 1;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 3000;
    as_result_v0_init(&acceptance);
    CHECK(as_session_submit_v0(session, &frame, &acceptance) == AS_OK);
    for (uint32_t attempt = 0; attempt < 2000; ++attempt) {
        CHECK(as_session_get_stats_v0(session, stats, sizeof(stats), &stats_size) == AS_OK);
        if (strstr(stats, "\"output_queue_depth\":\"1\"") != NULL) break;
        nanosleep(&poll, NULL);
    }
    CHECK(strstr(stats, "\"output_queue_depth\":\"1\"") != NULL);
    pthread_mutex_lock(&g_barrier_mutex);
    g_process_entered = 0;
    g_release_process = 0;
    pthread_mutex_unlock(&g_barrier_mutex);
    frame.first_input_sample = 160;
    CHECK(as_session_submit_v0(session, &frame, &acceptance) == AS_OK);
    pthread_mutex_lock(&g_barrier_mutex);
    while (!g_process_entered)
        pthread_cond_wait(&g_barrier_cond, &g_barrier_mutex);
    pthread_mutex_unlock(&g_barrier_mutex);
    frame.first_input_sample = 320;
    frame.flags = AS_FRAME_FINAL_INPUT;
    frame.input_valid_count = 5;
    CHECK(as_session_submit_v0(session, &frame, &acceptance) == AS_OK);
    pthread_mutex_lock(&g_barrier_mutex);
    g_release_process = 1;
    pthread_cond_broadcast(&g_barrier_cond);
    pthread_mutex_unlock(&g_barrier_mutex);
    for (uint32_t attempt = 0; attempt < 2000; ++attempt) {
        CHECK(as_session_get_stats_v0(session, stats, (uint32_t)sizeof(stats),
                                      &stats_size) == AS_OK);
        if (strstr(stats, "\"lifecycle\":\"needs_reset\"") != NULL) break;
        nanosleep(&poll, NULL);
    }
    CHECK(strstr(stats, "\"lifecycle\":\"needs_reset\"") != NULL);
    CHECK(strstr(stats, "\"failed_intervals\":\"1\"") != NULL);
    CHECK(strstr(stats, "\"failed_valid_samples\":\"160\"") != NULL);
    CHECK(strstr(stats, "\"backend_failures\":\"1\"") != NULL);
    float failed_output_samples[AS_FRAME_SAMPLES];
    as_output_v0 failed_output;
    as_output_v0_init(&failed_output);
    failed_output.samples = failed_output_samples;
    as_result_v0 failed_result;
    as_result_v0_init(&failed_result);
    CHECK(as_session_pull_v0(session, &failed_output, &failed_result) ==
          AS_NEEDS_RESET);
    CHECK(as_session_reset_v0(session, 3001, 0, &error) == AS_OK);
    CHECK(as_session_get_stats_v0(session, stats, sizeof(stats), &stats_size) == AS_OK);
    /* [0,160) was queued output, [160,320) failed, [320,325) was queued input. */
    CHECK(strstr(stats, "\"cancelled_valid_samples\":\"165\"") != NULL);
    CHECK(strstr(stats, "\"cancelled_intervals\":\"2\"") != NULL);
    g_fail_process = 0;
    CHECK(as_session_close_v0(&session) == AS_OK);

    create.epoch = 3500;
    CHECK(as_session_create_v0(registry, "test.blocking.v0", 16, &create,
                                &session, &error) == AS_OK);
    g_process_entered = 0;
    g_release_process = 0;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = create.epoch;
    CHECK(as_session_submit_v0(session, &frame, &acceptance) == AS_OK);
    pthread_mutex_lock(&g_barrier_mutex);
    while (!g_process_entered)
        pthread_cond_wait(&g_barrier_cond, &g_barrier_mutex);
    pthread_mutex_unlock(&g_barrier_mutex);
    frame.first_input_sample = 160;
    frame.flags = AS_FRAME_FINAL_INPUT;
    frame.input_valid_count = 5;
    CHECK(as_session_submit_v0(session, &frame, &acceptance) == AS_OK);
    CHECK(as_registry_close_v0(&registry) == AS_BUSY);
    g_observe_destroy = session;
    close_args close = {session, AS_BACKEND_FAILURE};
    pthread_t close_id;
    CHECK(pthread_create(&close_id, NULL, close_thread, &close) == 0);
    CHECK(wait_for_close(session));
    pthread_mutex_lock(&g_barrier_mutex);
    g_release_process = 1;
    pthread_cond_broadcast(&g_barrier_cond);
    pthread_mutex_unlock(&g_barrier_mutex);
    CHECK(pthread_join(close_id, NULL) == 0);
    CHECK(close.status == AS_OK && close.session == NULL);
    CHECK(g_closed_samples == 165 && g_closed_intervals == 2);
    g_observe_destroy = NULL;

    CHECK(check_reset_close(registry, &create) == 0);

    CHECK(as_effective_config_create_v0(
              registry, "test.blocking.v0", 16, AS_MODE_PROCESSING_THREAD,
              config, sizeof(config), &required, &error) == AS_OK);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.config_json_length = required - 1;
    CHECK(as_session_create_v0(registry, "test.blocking.v0", 16, &create,
                               &session, &error) == AS_OK);
    g_process_entered = 0;
    g_release_process = 0;
    process_args process = {session, create.epoch, 0};
    pthread_t process_id;
    CHECK(pthread_create(&process_id, NULL, process_thread, &process) == 0);
    pthread_mutex_lock(&g_barrier_mutex);
    while (!g_process_entered)
        pthread_cond_wait(&g_barrier_cond, &g_barrier_mutex);
    pthread_mutex_unlock(&g_barrier_mutex);
    CHECK(as_session_reset_v0(session, create.epoch + 1, 0, &error) == AS_BUSY);
    CHECK(as_session_begin_drain_v0(session) == AS_BUSY);
    close = (close_args){session, AS_BACKEND_FAILURE};
    CHECK(pthread_create(&close_id, NULL, close_thread, &close) == 0);
    CHECK(wait_for_close(session));
    pthread_mutex_lock(&g_barrier_mutex);
    g_release_process = 1;
    pthread_cond_broadcast(&g_barrier_cond);
    pthread_mutex_unlock(&g_barrier_mutex);
    CHECK(pthread_join(process_id, NULL) == 0 && process.ok);
    CHECK(pthread_join(close_id, NULL) == 0);
    CHECK(close.status == AS_OK && close.session == NULL);

    create.first_input_sample = INT64_MAX - 160;
    CHECK(as_session_create_v0(registry, "test.blocking.v0", 16, &create,
                               &session, &error) == AS_OK);
    CHECK(test_process(session, create.epoch, create.first_input_sample, &failed_result));
    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    g_overflow_drain = 1;
    CHECK(as_session_drain_next_v0(session, &failed_output, &failed_result) ==
          AS_BACKEND_FAILURE);
    CHECK(failed_result.produced_count == 0 && failed_result.valid_count == 0);
    CHECK(as_session_begin_drain_v0(session) == AS_NEEDS_RESET);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}

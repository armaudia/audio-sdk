#include "test_common.h"

#include <pthread.h>
#include <sched.h>

static pthread_mutex_t g_barrier_mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t g_barrier_cond = PTHREAD_COND_INITIALIZER;
static int g_process_entered;
static int g_release_process;

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
    ((blocking_instance *)opaque)->epoch = epoch;
    return AS_OK;
}

static as_status_v0 AS_CALL blocking_drain(void *opaque,
                                            const as_output_v0 *output,
                                            as_result_v0 *result) {
    (void)opaque;
    (void)output;
    (void)result;
    return AS_END_OF_STREAM;
}

static void AS_CALL blocking_destroy(void *opaque) { free(opaque); }

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
    as_result_v0_init(&acceptance);
    CHECK(as_session_submit_v0(session, &frame, &acceptance) ==
          AS_RESOURCE_EXHAUSTED);

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
    CHECK(as_session_begin_drain_v0(session) == AS_OK);

    uint32_t frames = 0;
    uint64_t valid_samples = 0;
    while (frames < 4) {
        float output_samples[AS_FRAME_SAMPLES];
        as_output_v0 output;
        as_output_v0_init(&output);
        output.samples = output_samples;
        as_result_v0 result;
        as_result_v0_init(&result);
        const as_status_v0 status =
            as_session_pull_v0(session, &output, &result);
        if (status == AS_NOT_READY) {
            sched_yield();
            continue;
        }
        CHECK(status == AS_OK);
        CHECK(result.source_first_sample ==
              (int64_t)frames * AS_FRAME_SAMPLES);
        CHECK(result.produced_count == AS_FRAME_SAMPLES);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        valid_samples += result.valid_count;
        ++frames;
    }
    CHECK(valid_samples == 4u * AS_FRAME_SAMPLES);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}

# Task-local, opt-in SpeexDSP AGC + advisory activity reference adapter.
#
# Nothing here is added to the installed SDK build. This standalone project is
# configured only by a caller that explicitly opts in. It compiles the exact
# vendored SpeexDSP sources pinned by deps/lock.json; no source is copied,
# edited, substituted or given a relaxed tolerance. Exactly one
# SpeexPreprocessState is used per stream and the activity output is advisory:
# the VAD flag changes only the return value of speex_preprocess_run(), never
# the audio path.
cmake_minimum_required(VERSION 3.20)
project(audio_sdk_speex_agc_activity_reference LANGUAGES C)

option(AS_ENABLE_SPEEX_AGC_ACTIVITY_REFERENCE
       "Build the task-local Speex AGC + advisory activity reference CLI" OFF)

if(AS_ENABLE_SPEEX_AGC_ACTIVITY_REFERENCE)
    get_filename_component(AS_TASK_SDK_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../../.." ABSOLUTE)
    set(AS_ACTIVITY_SPEEX_DIR "${AS_TASK_SDK_ROOT}/third_party/speexdsp")

    set(AS_ACTIVITY_SOURCES
        "${AS_ACTIVITY_SPEEX_DIR}/libspeexdsp/preprocess.c"
        "${AS_ACTIVITY_SPEEX_DIR}/libspeexdsp/mdf.c"
        "${AS_ACTIVITY_SPEEX_DIR}/libspeexdsp/fftwrap.c"
        "${AS_ACTIVITY_SPEEX_DIR}/libspeexdsp/filterbank.c"
        "${AS_ACTIVITY_SPEEX_DIR}/libspeexdsp/smallft.c"
        "${AS_ACTIVITY_SPEEX_DIR}/libspeexdsp/kiss_fft.c"
        "${AS_ACTIVITY_SPEEX_DIR}/libspeexdsp/kiss_fftr.c")

    add_executable(speexagc_activity_cli
        "${CMAKE_CURRENT_LIST_DIR}/src/speexagc_activity_cli.c"
        ${AS_ACTIVITY_SOURCES})
    target_include_directories(speexagc_activity_cli PRIVATE
        "${AS_ACTIVITY_SPEEX_DIR}/include"
        "${AS_ACTIVITY_SPEEX_DIR}/libspeexdsp")
    # Exact floating-point flags used by the installed Speex provider
    # (core/providers/speex/provider.cmake); FLOATING_POINT is required for AGC.
    target_compile_definitions(speexagc_activity_cli PRIVATE
        FLOATING_POINT USE_SMALLFT EXPORT= DISABLE_WARNINGS)
    target_compile_options(speexagc_activity_cli PRIVATE -w)
    target_link_libraries(speexagc_activity_cli PRIVATE m)

    enable_testing()
    add_test(NAME speexagc_activity_cli_smoke
             COMMAND speexagc_activity_cli --self-test)
endif()

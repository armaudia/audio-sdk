# Task-local, opt-in Speex MDF residual postfilter reference adapter.
#
# Nothing here is added to the installed SDK build, descriptor registry,
# catalog or default provider set. This standalone project is configured only
# by a caller that explicitly opts in. It compiles the exact vendored SpeexDSP
# sources pinned by deps/lock.json and legacy commit
# 3e2446fc58886fc02b099b54651adc9a10a65454; no source is copied or replaced.
cmake_minimum_required(VERSION 3.20)
project(audio_sdk_speex_mdf_residual_postfilter LANGUAGES C)

option(AS_ENABLE_SPEEX_MDF_RESIDUAL_POSTFILTER
       "Build the task-local Speex MDF residual postfilter reference CLI" OFF)

if(AS_ENABLE_SPEEX_MDF_RESIDUAL_POSTFILTER)
    get_filename_component(AS_TASK_SDK_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../../.." ABSOLUTE)
    set(AS_PF_SPEEX_DIR "${AS_TASK_SDK_ROOT}/third_party/speexdsp")

    set(AS_PF_SOURCES
        "${AS_PF_SPEEX_DIR}/libspeexdsp/preprocess.c"
        "${AS_PF_SPEEX_DIR}/libspeexdsp/mdf.c"
        "${AS_PF_SPEEX_DIR}/libspeexdsp/fftwrap.c"
        "${AS_PF_SPEEX_DIR}/libspeexdsp/filterbank.c"
        "${AS_PF_SPEEX_DIR}/libspeexdsp/smallft.c"
        "${AS_PF_SPEEX_DIR}/libspeexdsp/kiss_fft.c"
        "${AS_PF_SPEEX_DIR}/libspeexdsp/kiss_fftr.c")

    add_executable(mdf_postfilter_cli
        "${CMAKE_CURRENT_LIST_DIR}/src/mdf_postfilter_cli.c"
        ${AS_PF_SOURCES})
    target_include_directories(mdf_postfilter_cli PRIVATE
        "${AS_PF_SPEEX_DIR}/include"
        "${AS_PF_SPEEX_DIR}/libspeexdsp")
    # Exact flags used by the installed Speex provider (core/providers/speex/provider.cmake).
    target_compile_definitions(mdf_postfilter_cli PRIVATE
        FLOATING_POINT USE_SMALLFT EXPORT= DISABLE_WARNINGS)
    target_compile_options(mdf_postfilter_cli PRIVATE -w)
    target_link_libraries(mdf_postfilter_cli PRIVATE m)

    enable_testing()
    add_test(NAME mdf_postfilter_cli_smoke
             COMMAND mdf_postfilter_cli --self-test)
    add_test(NAME mdf_postfilter_cli_postfilter_smoke
             COMMAND mdf_postfilter_cli --self-test-postfilter)
endif()

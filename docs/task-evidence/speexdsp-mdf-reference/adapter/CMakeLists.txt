# Task-local, opt-in SpeexDSP MDF reference adapter.
#
# Nothing here is added to the installed SDK build. This standalone project is
# configured only by a caller that explicitly opts in. It compiles the exact
# vendored SpeexDSP sources pinned by deps/lock.json and by legacy commit
# 3e2446fc58886fc02b099b54651adc9a10a65454; no source is copied or replaced.
cmake_minimum_required(VERSION 3.20)
project(audio_sdk_speexdsp_mdf_reference LANGUAGES C)

option(AS_ENABLE_SPEEXDSP_MDF_REFERENCE
       "Build the task-local SpeexDSP MDF reference CLI" OFF)

if(AS_ENABLE_SPEEXDSP_MDF_REFERENCE)
    get_filename_component(AS_TASK_SDK_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../../.." ABSOLUTE)
    set(AS_MDF_SPEEX_DIR "${AS_TASK_SDK_ROOT}/third_party/speexdsp")

    set(AS_MDF_SOURCES
        "${AS_MDF_SPEEX_DIR}/libspeexdsp/mdf.c"
        "${AS_MDF_SPEEX_DIR}/libspeexdsp/fftwrap.c"
        "${AS_MDF_SPEEX_DIR}/libspeexdsp/filterbank.c"
        "${AS_MDF_SPEEX_DIR}/libspeexdsp/smallft.c"
        "${AS_MDF_SPEEX_DIR}/libspeexdsp/kiss_fft.c"
        "${AS_MDF_SPEEX_DIR}/libspeexdsp/kiss_fftr.c")

    add_executable(mdf_reference_cli
        "${CMAKE_CURRENT_LIST_DIR}/src/mdf_reference_cli.c"
        ${AS_MDF_SOURCES})
    target_include_directories(mdf_reference_cli PRIVATE
        "${AS_MDF_SPEEX_DIR}/include"
        "${AS_MDF_SPEEX_DIR}/libspeexdsp")
    # Exact flags used by the installed Speex provider (core/providers/speex/provider.cmake).
    target_compile_definitions(mdf_reference_cli PRIVATE
        FLOATING_POINT USE_SMALLFT EXPORT= DISABLE_WARNINGS)
    target_compile_options(mdf_reference_cli PRIVATE -w)
    target_link_libraries(mdf_reference_cli PRIVATE m)

    enable_testing()
    add_test(NAME mdf_reference_cli_smoke
             COMMAND mdf_reference_cli --self-test)
endif()

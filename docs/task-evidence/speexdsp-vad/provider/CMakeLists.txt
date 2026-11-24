cmake_minimum_required(VERSION 3.20)
project(audio_sdk_speexdsp_vad_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_SPEEXDSP_VAD "Compile and register the task-local SpeexDSP VAD reference provider" OFF)

add_executable(as_speexdsp_vad_test tests/test_provider.c)
target_link_libraries(as_speexdsp_vad_test PRIVATE AudioSDK::audio_sdk)
target_include_directories(as_speexdsp_vad_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

if(AS_ENABLE_SPEEXDSP_VAD)
    if(NOT AS_SPEEXDSP_SOURCE_DIR OR NOT IS_DIRECTORY "${AS_SPEEXDSP_SOURCE_DIR}")
        message(FATAL_ERROR "AS_SPEEXDSP_SOURCE_DIR must point at the pinned vendored third_party/speexdsp directory")
    endif()
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        speexdsp_vad_provider.c config/config.json speexdsp_vad_observe.h)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/speexdsp_vad_provider.c" VAD_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" VAD_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in speexdsp_vad_descriptor.h @ONLY)

    # Compile the exact vendored SpeexDSP sources into this caller-local test.
    # These objects are never installed and never enter the SDK library.
    add_library(as_speexdsp_vad_upstream OBJECT
        "${AS_SPEEXDSP_SOURCE_DIR}/libspeexdsp/preprocess.c"
        "${AS_SPEEXDSP_SOURCE_DIR}/libspeexdsp/fftwrap.c"
        "${AS_SPEEXDSP_SOURCE_DIR}/libspeexdsp/filterbank.c"
        "${AS_SPEEXDSP_SOURCE_DIR}/libspeexdsp/smallft.c"
        "${AS_SPEEXDSP_SOURCE_DIR}/libspeexdsp/kiss_fft.c"
        "${AS_SPEEXDSP_SOURCE_DIR}/libspeexdsp/kiss_fftr.c"
        "${AS_SPEEXDSP_SOURCE_DIR}/libspeexdsp/resample.c")
    target_include_directories(as_speexdsp_vad_upstream PRIVATE
        "${AS_SPEEXDSP_SOURCE_DIR}/include" "${AS_SPEEXDSP_SOURCE_DIR}/libspeexdsp")
    target_compile_definitions(as_speexdsp_vad_upstream PRIVATE
        FLOATING_POINT USE_SMALLFT EXPORT= DISABLE_WARNINGS)
    target_compile_options(as_speexdsp_vad_upstream PRIVATE -w)
    set_target_properties(as_speexdsp_vad_upstream PROPERTIES C_VISIBILITY_PRESET hidden)

    target_sources(as_speexdsp_vad_test PRIVATE speexdsp_vad_provider.c)
    target_include_directories(as_speexdsp_vad_test PRIVATE
        "${CMAKE_CURRENT_BINARY_DIR}" "${AS_SPEEXDSP_SOURCE_DIR}/include")
    target_link_libraries(as_speexdsp_vad_test PRIVATE as_speexdsp_vad_upstream)
    target_compile_definitions(as_speexdsp_vad_test PRIVATE AS_ENABLE_SPEEXDSP_VAD)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_speexdsp_vad_test PRIVATE m)
endif()

enable_testing()
add_test(NAME speexdsp_vad_registration COMMAND as_speexdsp_vad_test)

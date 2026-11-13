cmake_minimum_required(VERSION 3.20)
project(audio_sdk_external_provider_conformance LANGUAGES C)

if(NOT DEFINED AUDIO_SDK_CONFORMANCE_DIR)
    message(FATAL_ERROR
        "Set AUDIO_SDK_CONFORMANCE_DIR to <prefix>/share/audio-sdk/conformance")
endif()

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
add_executable(audio_sdk_external_conformance
    main.c
    provider.c
    "${AUDIO_SDK_CONFORMANCE_DIR}/checks.c")
target_include_directories(audio_sdk_external_conformance PRIVATE
    "${AUDIO_SDK_CONFORMANCE_DIR}")
target_compile_definitions(audio_sdk_external_conformance PRIVATE
    _POSIX_C_SOURCE=200809L AS_STATIC)
target_link_libraries(audio_sdk_external_conformance PRIVATE AudioSDK::audio_sdk)

enable_testing()
add_test(NAME external_delayed_identity
    COMMAND audio_sdk_external_conformance --provider fixture.delayed.v0
            --report "${CMAKE_CURRENT_BINARY_DIR}/delayed-report.json")
add_test(NAME external_fault_is_detected
    COMMAND audio_sdk_external_conformance --provider fixture.fault.v0
            --report "${CMAKE_CURRENT_BINARY_DIR}/fault-report.json")
set_tests_properties(external_fault_is_detected PROPERTIES WILL_FAIL TRUE)
add_test(NAME external_drain_bound_is_detected
    COMMAND audio_sdk_external_conformance --provider fixture.drainbound.v0
            --report "${CMAKE_CURRENT_BINARY_DIR}/drainbound-report.json")
set_tests_properties(external_drain_bound_is_detected PROPERTIES WILL_FAIL TRUE)
foreach(delay IN ITEMS 0 1 159 160 161 512)
    add_test(NAME external_delay_${delay}
        COMMAND audio_sdk_external_conformance --provider fixture.delay${delay}.v0
                --report "${CMAKE_CURRENT_BINARY_DIR}/delay-${delay}-report.json")
endforeach()
add_test(NAME external_delay_256_native_hop_256
    COMMAND audio_sdk_external_conformance --provider fixture.delay256hop.v0
            --report "${CMAKE_CURRENT_BINARY_DIR}/delay-256-hop-256-report.json")

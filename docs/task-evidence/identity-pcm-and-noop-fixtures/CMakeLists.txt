# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.20)
project(audio_sdk_identity_pcm_fixture LANGUAGES C)

if(NOT DEFINED AUDIO_SDK_CONFORMANCE_DIR)
    message(FATAL_ERROR
        "Set AUDIO_SDK_CONFORMANCE_DIR to <prefix>/share/audio-sdk/conformance")
endif()

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    identity_provider.c config/config.json config/descriptor.h.in)
file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/identity_provider.c" IDENTITY_SOURCE_DIGEST)
file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" IDENTITY_CONFIG_DIGEST)
configure_file(config/descriptor.h.in fixture_descriptor.h @ONLY)

add_executable(audio_sdk_identity_pcm
    main.c
    identity_provider.c
    "${AUDIO_SDK_CONFORMANCE_DIR}/checks.c")
target_include_directories(audio_sdk_identity_pcm PRIVATE
    "${AUDIO_SDK_CONFORMANCE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}")
target_compile_definitions(audio_sdk_identity_pcm PRIVATE
    AS_STATIC _POSIX_C_SOURCE=200809L)
target_link_libraries(audio_sdk_identity_pcm PRIVATE AudioSDK::audio_sdk)
if(UNIX AND NOT APPLE)
    target_link_libraries(audio_sdk_identity_pcm PRIVATE m)
endif()

set(IDENTITY_ARCHIVE_ARGS "")
if(DEFINED IDENTITY_ARCHIVE_SHA256 AND NOT "${IDENTITY_ARCHIVE_SHA256}" STREQUAL "")
    set(IDENTITY_ARCHIVE_ARGS --archive-sha256 "${IDENTITY_ARCHIVE_SHA256}")
endif()

enable_testing()
add_test(NAME identity_pcm_exact_baseline
    COMMAND audio_sdk_identity_pcm
        --report "${CMAKE_CURRENT_BINARY_DIR}/consumer-report.json"
        --conformance-report "${CMAKE_CURRENT_BINARY_DIR}/conformance-report.json"
        ${IDENTITY_ARCHIVE_ARGS})

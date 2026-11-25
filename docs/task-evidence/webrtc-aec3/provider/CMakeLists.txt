# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.20)
project(audio_sdk_webrtc_aec3_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_WEBRTC_AEC3 "Compile and register the task-local synthetic reference provider" OFF)

add_executable(as_webrtc_aec3_test tests/test_provider.c)
target_include_directories(as_webrtc_aec3_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
target_link_libraries(as_webrtc_aec3_test PRIVATE AudioSDK::audio_sdk)

if(AS_ENABLE_WEBRTC_AEC3)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        webrtc_aec3_provider.c config/config.json)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/webrtc_aec3_provider.c" WEBRTC_AEC3_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" WEBRTC_AEC3_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in webrtc_aec3_descriptor.h @ONLY)
    target_sources(as_webrtc_aec3_test PRIVATE webrtc_aec3_provider.c)
    target_include_directories(as_webrtc_aec3_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_webrtc_aec3_test PRIVATE AS_ENABLE_WEBRTC_AEC3)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_webrtc_aec3_test PRIVATE m)
endif()

enable_testing()
add_test(NAME webrtc_aec3_registration COMMAND as_webrtc_aec3_test)

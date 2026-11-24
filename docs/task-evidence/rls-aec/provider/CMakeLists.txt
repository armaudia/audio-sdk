# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.20)
project(audio_sdk_rls_aec_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_RLS_AEC
       "Compile and register the task-local reference provider" OFF)

add_executable(as_rls_aec_test tests/test_provider.c)
target_include_directories(as_rls_aec_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
target_link_libraries(as_rls_aec_test PRIVATE AudioSDK::audio_sdk)

if(AS_ENABLE_RLS_AEC)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        rls_aec_provider.c config/config.json)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/rls_aec_provider.c"
         RLS_AEC_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json"
         RLS_AEC_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in rls_aec_descriptor.h @ONLY)
    target_sources(as_rls_aec_test PRIVATE rls_aec_provider.c)
    target_include_directories(as_rls_aec_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_rls_aec_test PRIVATE AS_ENABLE_RLS_AEC)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_rls_aec_test PRIVATE m)
endif()

enable_testing()
add_test(NAME rls_aec_registration COMMAND as_rls_aec_test)

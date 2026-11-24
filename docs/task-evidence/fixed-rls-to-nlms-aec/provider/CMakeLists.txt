# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.20)
project(audio_sdk_fixed_rls_nlms_aec_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_FIXED_RLS_NLMS_AEC
       "Compile and register the task-local reference provider" OFF)

add_executable(as_fixed_rls_nlms_aec_test tests/test_provider.c)
target_include_directories(as_fixed_rls_nlms_aec_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
target_link_libraries(as_fixed_rls_nlms_aec_test PRIVATE AudioSDK::audio_sdk)

if(AS_ENABLE_FIXED_RLS_NLMS_AEC)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        fixed_rls_nlms_provider.c config/config.json)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/fixed_rls_nlms_provider.c"
         FIXED_RLS_NLMS_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json"
         FIXED_RLS_NLMS_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in fixed_rls_nlms_descriptor.h @ONLY)
    target_sources(as_fixed_rls_nlms_aec_test PRIVATE fixed_rls_nlms_provider.c)
    target_include_directories(as_fixed_rls_nlms_aec_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_fixed_rls_nlms_aec_test PRIVATE AS_ENABLE_FIXED_RLS_NLMS_AEC)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_fixed_rls_nlms_aec_test PRIVATE m)
endif()

enable_testing()
add_test(NAME fixed_rls_nlms_aec_registration COMMAND as_fixed_rls_nlms_aec_test)

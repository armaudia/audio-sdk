# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.20)
project(audio_sdk_raii_evidence LANGUAGES C)

# Default OFF: the guard test is the only target and never links or includes
# the SDK. ON is an explicit opt-in build of the task-local synthetic harness.
option(AS_RAII_EVIDENCE_ENABLE_C_BOUNDARY
       "Build the task-local RAII C harness against an installed AudioSDK" OFF)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
enable_testing()

if(AS_RAII_EVIDENCE_ENABLE_C_BOUNDARY)
    find_package(AudioSDK 0.1 CONFIG REQUIRED)
    add_executable(as_raii_harness raii_harness.c)
    target_include_directories(as_raii_harness PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
    target_link_libraries(as_raii_harness PRIVATE AudioSDK::audio_sdk)
    target_compile_definitions(as_raii_harness PRIVATE AS_RAII_EVIDENCE_OPTION=1)
    add_test(NAME raii_boundary_on COMMAND as_raii_harness)
else()
    add_executable(as_raii_guard off_guard.c)
    target_compile_definitions(as_raii_guard PRIVATE AS_RAII_EVIDENCE_OPTION=0)
    add_test(NAME raii_boundary_off COMMAND as_raii_guard)
endif()

# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.20)
project(audio_sdk_soundtouch_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_SOUNDTOUCH_REFERENCE "Compile and register the task-local reference provider" OFF)

add_executable(as_soundtouch_reference_test tests/test_provider.c)
target_link_libraries(as_soundtouch_reference_test PRIVATE AudioSDK::audio_sdk)
target_include_directories(as_soundtouch_reference_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

if(AS_ENABLE_SOUNDTOUCH_REFERENCE)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        soundtouch_reference_provider.c config/config.json expected_vectors.h)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/soundtouch_reference_provider.c" SOUNDTOUCH_REFERENCE_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" SOUNDTOUCH_REFERENCE_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in soundtouch_reference_descriptor.h @ONLY)
    target_sources(as_soundtouch_reference_test PRIVATE soundtouch_reference_provider.c)
    target_include_directories(as_soundtouch_reference_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_soundtouch_reference_test PRIVATE AS_ENABLE_SOUNDTOUCH_REFERENCE)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_soundtouch_reference_test PRIVATE m)
endif()

enable_testing()
add_test(NAME soundtouch_reference_registration COMMAND as_soundtouch_reference_test)

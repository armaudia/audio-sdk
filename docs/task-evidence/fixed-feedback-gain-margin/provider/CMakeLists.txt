cmake_minimum_required(VERSION 3.20)
project(audio_sdk_fixed_feedback_margin_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_FIXED_FEEDBACK_MARGIN
       "Compile and register the task-local reference provider" OFF)

add_executable(as_fixed_feedback_margin_test tests/test_provider.c)
target_link_libraries(as_fixed_feedback_margin_test PRIVATE AudioSDK::audio_sdk)

if(AS_ENABLE_FIXED_FEEDBACK_MARGIN)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        fixed_gain_provider.c config/config.json)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/fixed_gain_provider.c" FIXED_MARGIN_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" FIXED_MARGIN_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in fixed_margin_descriptor.h @ONLY)
    target_sources(as_fixed_feedback_margin_test PRIVATE fixed_gain_provider.c)
    target_include_directories(as_fixed_feedback_margin_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_fixed_feedback_margin_test PRIVATE AS_ENABLE_FIXED_FEEDBACK_MARGIN)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_fixed_feedback_margin_test PRIVATE m)
endif()

enable_testing()
add_test(NAME fixed_feedback_margin_registration COMMAND as_fixed_feedback_margin_test)

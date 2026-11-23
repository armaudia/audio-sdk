cmake_minimum_required(VERSION 3.20)
project(audio_sdk_notch_margin_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_NOTCH_MARGIN "Compile and register the task-local reference provider" OFF)

add_executable(as_notch_margin_test tests/test_provider.c)
target_link_libraries(as_notch_margin_test PRIVATE AudioSDK::audio_sdk)

if(AS_ENABLE_NOTCH_MARGIN)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        margin_provider.c config/config.json)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/margin_provider.c" MARGIN_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" MARGIN_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in margin_descriptor.h @ONLY)
    target_sources(as_notch_margin_test PRIVATE margin_provider.c)
    target_include_directories(as_notch_margin_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_notch_margin_test PRIVATE AS_ENABLE_NOTCH_MARGIN)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_notch_margin_test PRIVATE m)
endif()

enable_testing()
add_test(NAME notch_margin_registration COMMAND as_notch_margin_test)

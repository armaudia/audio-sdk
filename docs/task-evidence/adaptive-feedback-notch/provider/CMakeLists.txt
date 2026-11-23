cmake_minimum_required(VERSION 3.20)
project(audio_sdk_adaptive_notch_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_ADAPTIVE_NOTCH "Compile and register the task-local reference provider" OFF)

add_executable(as_adaptive_notch_test tests/test_provider.c)
target_link_libraries(as_adaptive_notch_test PRIVATE AudioSDK::audio_sdk)

if(AS_ENABLE_ADAPTIVE_NOTCH)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        adaptive_notch_provider.c config/config.json)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/adaptive_notch_provider.c" ADAPTIVE_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" ADAPTIVE_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in adaptive_descriptor.h @ONLY)
    target_sources(as_adaptive_notch_test PRIVATE adaptive_notch_provider.c)
    target_include_directories(as_adaptive_notch_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_adaptive_notch_test PRIVATE AS_ENABLE_ADAPTIVE_NOTCH)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_adaptive_notch_test PRIVATE m)
endif()

enable_testing()
add_test(NAME adaptive_notch_registration COMMAND as_adaptive_notch_test)

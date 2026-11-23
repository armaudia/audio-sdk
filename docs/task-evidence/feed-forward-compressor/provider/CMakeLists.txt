cmake_minimum_required(VERSION 3.20)
project(audio_sdk_feed_forward_compressor_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_FEED_FORWARD_COMPRESSOR
       "Compile and register the task-local reference provider" OFF)

add_executable(as_feed_forward_compressor_test tests/test_provider.c)
target_link_libraries(as_feed_forward_compressor_test PRIVATE AudioSDK::audio_sdk)

if(AS_ENABLE_FEED_FORWARD_COMPRESSOR)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        feed_forward_compressor.c config/config.json)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/feed_forward_compressor.c" FFC_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" FFC_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in compressor_descriptor.h @ONLY)
    target_sources(as_feed_forward_compressor_test PRIVATE feed_forward_compressor.c)
    target_include_directories(as_feed_forward_compressor_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_feed_forward_compressor_test PRIVATE AS_ENABLE_FEED_FORWARD_COMPRESSOR)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_feed_forward_compressor_test PRIVATE m)
endif()

enable_testing()
add_test(NAME feed_forward_compressor_registration COMMAND as_feed_forward_compressor_test)

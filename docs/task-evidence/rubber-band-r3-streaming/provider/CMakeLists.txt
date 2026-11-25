cmake_minimum_required(VERSION 3.20)
project(audio_sdk_rubber_band_r3_streaming_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_RUBBER_BAND_R3_STREAMING
       "Compile and register the task-local synthetic streaming TSM reference" OFF)

add_executable(as_rb3_test tests/test_provider.c)
target_link_libraries(as_rb3_test PRIVATE AudioSDK::audio_sdk)
target_include_directories(as_rb3_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

if(AS_ENABLE_RUBBER_BAND_R3_STREAMING)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        rubber_band_r3_streaming_provider.c config/config.json expected_vectors.h)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/rubber_band_r3_streaming_provider.c"
         RB3_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" RB3_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in rubber_band_r3_streaming_descriptor.h @ONLY)
    target_sources(as_rb3_test PRIVATE rubber_band_r3_streaming_provider.c)
    target_include_directories(as_rb3_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_rb3_test PRIVATE AS_ENABLE_RUBBER_BAND_R3_STREAMING)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_rb3_test PRIVATE m)
endif()

enable_testing()
add_test(NAME rubber_band_r3_streaming_registration COMMAND as_rb3_test)

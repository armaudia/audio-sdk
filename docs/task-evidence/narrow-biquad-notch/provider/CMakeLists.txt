cmake_minimum_required(VERSION 3.20)
project(audio_sdk_narrow_notch_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_NARROW_NOTCH "Compile the task-local narrow notch reference provider" OFF)

add_executable(as_narrow_notch_test tests/test_provider.c)
target_link_libraries(as_narrow_notch_test PRIVATE AudioSDK::audio_sdk)
target_include_directories(as_narrow_notch_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

if(AS_ENABLE_NARROW_NOTCH)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        narrow_notch_provider.c config/config.json)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/narrow_notch_provider.c" NN_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" NN_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in narrow_notch_descriptor.h @ONLY)
    target_sources(as_narrow_notch_test PRIVATE narrow_notch_provider.c)
    target_include_directories(as_narrow_notch_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_narrow_notch_test PRIVATE AS_ENABLE_NARROW_NOTCH)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_narrow_notch_test PRIVATE m)
endif()

enable_testing()
add_test(NAME narrow_notch_registration COMMAND as_narrow_notch_test)

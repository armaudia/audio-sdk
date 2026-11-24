cmake_minimum_required(VERSION 3.20)
project(audio_sdk_signalsmith_stretch_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_SIGNALSMITH_STRETCH "Compile and register the task-local reference provider" OFF)

add_executable(as_signalsmith_stretch_test tests/test_provider.c)
target_link_libraries(as_signalsmith_stretch_test PRIVATE AudioSDK::audio_sdk)
target_include_directories(as_signalsmith_stretch_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

if(AS_ENABLE_SIGNALSMITH_STRETCH)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        signalsmith_stretch_provider.c config/config.json expected_vectors.h)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/signalsmith_stretch_provider.c" SIGNALSMITH_STRETCH_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" SIGNALSMITH_STRETCH_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in signalsmith_stretch_descriptor.h @ONLY)
    target_sources(as_signalsmith_stretch_test PRIVATE signalsmith_stretch_provider.c)
    target_include_directories(as_signalsmith_stretch_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_signalsmith_stretch_test PRIVATE AS_ENABLE_SIGNALSMITH_STRETCH)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_signalsmith_stretch_test PRIVATE m)
endif()

enable_testing()
add_test(NAME signalsmith_stretch_registration COMMAND as_signalsmith_stretch_test)

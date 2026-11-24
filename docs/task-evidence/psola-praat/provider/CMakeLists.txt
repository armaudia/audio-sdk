cmake_minimum_required(VERSION 3.20)
project(audio_sdk_psola_praat_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_PSOLA_PRAAT "Compile and register the task-local reference provider" OFF)

add_executable(as_psola_praat_test tests/test_provider.c)
target_link_libraries(as_psola_praat_test PRIVATE AudioSDK::audio_sdk)
target_include_directories(as_psola_praat_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

if(AS_ENABLE_PSOLA_PRAAT)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        psola_praat_provider.c config/config.json expected_vectors.h)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/psola_praat_provider.c" PSOLA_PRAAT_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" PSOLA_PRAAT_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in psola_praat_descriptor.h @ONLY)
    target_sources(as_psola_praat_test PRIVATE psola_praat_provider.c)
    target_include_directories(as_psola_praat_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_psola_praat_test PRIVATE AS_ENABLE_PSOLA_PRAAT)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_psola_praat_test PRIVATE m)
endif()

enable_testing()
add_test(NAME psola_praat_registration COMMAND as_psola_praat_test)

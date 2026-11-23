cmake_minimum_required(VERSION 3.20)
project(audio_sdk_cascade_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_ADAPTIVE_ENERGY_TO_SILERO_CASCADE
       "Compile and register the task-local model-free cascade stub provider" OFF)

add_executable(as_cascade_reference_test tests/test_provider.c)
target_link_libraries(as_cascade_reference_test PRIVATE AudioSDK::audio_sdk)

if(AS_ENABLE_ADAPTIVE_ENERGY_TO_SILERO_CASCADE)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        src/cascade_provider.c config/config.json config/descriptor.h.in)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/src/cascade_provider.c" CASCADE_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" CASCADE_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in cascade_descriptor.h @ONLY)
    target_sources(as_cascade_reference_test PRIVATE src/cascade_provider.c)
    target_include_directories(as_cascade_reference_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_cascade_reference_test PRIVATE
        AS_ENABLE_ADAPTIVE_ENERGY_TO_SILERO_CASCADE)
endif()

enable_testing()
add_test(NAME adaptive_energy_to_silero_cascade_registration
         COMMAND as_cascade_reference_test)

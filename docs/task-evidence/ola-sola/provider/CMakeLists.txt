cmake_minimum_required(VERSION 3.20)
project(audio_sdk_ola_sola_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_OLA_SOLA "Compile and register the task-local reference provider" OFF)

add_executable(as_ola_sola_test tests/test_provider.c)
target_link_libraries(as_ola_sola_test PRIVATE AudioSDK::audio_sdk)
target_include_directories(as_ola_sola_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

if(AS_ENABLE_OLA_SOLA)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        ola_sola_provider.c config/config.json expected_vectors.h)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/ola_sola_provider.c" OLA_SOLA_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" OLA_SOLA_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in ola_sola_descriptor.h @ONLY)
    target_sources(as_ola_sola_test PRIVATE ola_sola_provider.c)
    target_include_directories(as_ola_sola_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_ola_sola_test PRIVATE AS_ENABLE_OLA_SOLA)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_ola_sola_test PRIVATE m)
endif()

enable_testing()
add_test(NAME ola_sola_registration COMMAND as_ola_sola_test)

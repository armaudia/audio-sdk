cmake_minimum_required(VERSION 3.20)
project(audio_sdk_provider_registration LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)
option(AS_ENABLE_FIXTURE_PROVIDER "Link the caller-asset fixture into this consumer" OFF)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
add_executable(as_fixture_registration tests/test_registration.c)
target_link_libraries(as_fixture_registration PRIVATE AudioSDK::audio_sdk)

if(AS_ENABLE_FIXTURE_PROVIDER)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        src/provider.c config/config.json)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/src/provider.c" FIXTURE_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" FIXTURE_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in fixture_descriptor.h @ONLY)
    target_sources(as_fixture_registration PRIVATE src/provider.c)
    target_include_directories(as_fixture_registration PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_fixture_registration PRIVATE AS_ENABLE_FIXTURE_PROVIDER)
endif()

enable_testing()
add_test(NAME fixture_registration COMMAND as_fixture_registration)

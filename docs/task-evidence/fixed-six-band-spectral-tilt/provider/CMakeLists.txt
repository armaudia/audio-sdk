cmake_minimum_required(VERSION 3.20)
project(audio_sdk_sixband_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

# Optional by design: OFF is the default and proves the unlinked task-local
# provider is absent from an otherwise unmodified installed SDK.
option(AS_ENABLE_SIXBAND_PROVIDER "Link and register the task-local six-band tilt provider" OFF)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

get_filename_component(SIXBAND_TASK_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/.." ABSOLUTE)
set(SIXBAND_PROVIDER_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/sixband_provider.c")
set(SIXBAND_CONFIG "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json")
set(SIXBAND_DESCRIPTOR_TEMPLATE "${CMAKE_CURRENT_SOURCE_DIR}/config/descriptor.h.in")
set(SIXBAND_CLI_SOURCE "${SIXBAND_TASK_ROOT}/tools/sixband_cli.c")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    ${SIXBAND_PROVIDER_SOURCE} ${SIXBAND_CONFIG} ${SIXBAND_DESCRIPTOR_TEMPLATE} ${SIXBAND_CLI_SOURCE})

file(SHA256 ${SIXBAND_PROVIDER_SOURCE} SIXBAND_SOURCE_DIGEST)
file(SHA256 ${SIXBAND_CONFIG} SIXBAND_CONFIG_DIGEST)
configure_file(${SIXBAND_DESCRIPTOR_TEMPLATE} sixband_descriptor.h @ONLY)

add_executable(sixband_registration tests/test_sixband_provider.c)
target_link_libraries(sixband_registration PRIVATE AudioSDK::audio_sdk)
target_include_directories(sixband_registration PRIVATE
    "${CMAKE_CURRENT_BINARY_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/src")

enable_testing()
add_test(NAME sixband_registration COMMAND sixband_registration)

if(AS_ENABLE_SIXBAND_PROVIDER)
    target_sources(sixband_registration PRIVATE ${SIXBAND_PROVIDER_SOURCE})
    target_compile_definitions(sixband_registration PRIVATE AS_ENABLE_SIXBAND_PROVIDER)

    add_executable(sixband_cli ${SIXBAND_CLI_SOURCE} ${SIXBAND_PROVIDER_SOURCE})
    target_link_libraries(sixband_cli PRIVATE AudioSDK::audio_sdk)
    target_include_directories(sixband_cli PRIVATE
        "${CMAKE_CURRENT_BINARY_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/src")
endif()

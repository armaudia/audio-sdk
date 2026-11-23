cmake_minimum_required(VERSION 3.20)
project(audio_sdk_css_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

# Optional by design: OFF is the default and only proves that the unlinked
# task-local provider is absent from an otherwise unmodified installed SDK.
option(AS_ENABLE_CSS_PROVIDER "Link and register the task-local CSS provider" OFF)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

get_filename_component(CSS_TASK_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/.." ABSOLUTE)
set(CSS_PROVIDER_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/css_provider.c")
set(CSS_CONFIG "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json")
set(CSS_PROFILE "${CSS_TASK_ROOT}/fixtures/noise_profile.f32")
set(CSS_DESCRIPTOR_TEMPLATE "${CMAKE_CURRENT_SOURCE_DIR}/config/descriptor.h.in")
set(CSS_CLI_SOURCE "${CSS_TASK_ROOT}/tools/css_cli.c")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    ${CSS_PROVIDER_SOURCE} ${CSS_CONFIG} ${CSS_PROFILE} ${CSS_DESCRIPTOR_TEMPLATE} ${CSS_CLI_SOURCE})

file(SHA256 ${CSS_PROVIDER_SOURCE} CSS_SOURCE_DIGEST)
file(SHA256 ${CSS_CONFIG} CSS_CONFIG_DIGEST)
file(SHA256 ${CSS_PROFILE} CSS_PROFILE_DIGEST)
configure_file(${CSS_DESCRIPTOR_TEMPLATE} css_descriptor.h @ONLY)

add_executable(css_registration tests/test_css_provider.c)
target_link_libraries(css_registration PRIVATE AudioSDK::audio_sdk)
target_include_directories(css_registration PRIVATE
    "${CMAKE_CURRENT_BINARY_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/src")

enable_testing()
add_test(NAME css_registration COMMAND css_registration)

if(AS_ENABLE_CSS_PROVIDER)
    target_sources(css_registration PRIVATE ${CSS_PROVIDER_SOURCE})
    target_compile_definitions(css_registration PRIVATE AS_ENABLE_CSS_PROVIDER)

    add_executable(css_cli ${CSS_CLI_SOURCE} ${CSS_PROVIDER_SOURCE})
    target_link_libraries(css_cli PRIVATE AudioSDK::audio_sdk)
    target_include_directories(css_cli PRIVATE
        "${CMAKE_CURRENT_BINARY_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/src")
endif()

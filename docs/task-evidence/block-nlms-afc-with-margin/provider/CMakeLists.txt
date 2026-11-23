cmake_minimum_required(VERSION 3.20)
project(audio_sdk_afc_margin_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

# Optional by design: OFF is the default and only proves that the unlinked
# task-local provider is absent from an otherwise unmodified installed SDK.
option(AS_ENABLE_AFC_MARGIN_PROVIDER
       "Link and register the task-local block-NLMS AFC margin provider" OFF)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

get_filename_component(AFC_TASK_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/.." ABSOLUTE)
set(AFC_PROVIDER_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/afc_provider.c")
set(AFC_CONFIG "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json")
set(AFC_REFERENCE "${AFC_TASK_ROOT}/fixtures/reference_loop.f32")
set(AFC_DESCRIPTOR_TEMPLATE "${CMAKE_CURRENT_SOURCE_DIR}/config/descriptor.h.in")
set(AFC_CLI_SOURCE "${AFC_TASK_ROOT}/tools/afc_cli.c")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    ${AFC_PROVIDER_SOURCE} ${AFC_CONFIG} ${AFC_REFERENCE}
    ${AFC_DESCRIPTOR_TEMPLATE} ${AFC_CLI_SOURCE})

file(SHA256 ${AFC_PROVIDER_SOURCE} AFC_SOURCE_DIGEST)
file(SHA256 ${AFC_CONFIG} AFC_CONFIG_DIGEST)
file(SHA256 ${AFC_REFERENCE} AFC_ASSET_DIGEST)
file(SIZE ${AFC_REFERENCE} AFC_ASSET_BYTES)
configure_file(${AFC_DESCRIPTOR_TEMPLATE} afc_descriptor.h @ONLY)

add_executable(afc_registration tests/test_provider.c)
target_link_libraries(afc_registration PRIVATE AudioSDK::audio_sdk)
target_include_directories(afc_registration PRIVATE
    "${CMAKE_CURRENT_BINARY_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/src")

enable_testing()
add_test(NAME afc_registration COMMAND afc_registration)

if(AS_ENABLE_AFC_MARGIN_PROVIDER)
    target_sources(afc_registration PRIVATE ${AFC_PROVIDER_SOURCE})
    target_compile_definitions(afc_registration PRIVATE
        AS_ENABLE_AFC_MARGIN_PROVIDER
        AFC_MIC_PATH="${AFC_TASK_ROOT}/fixtures/mic_loop.f32"
        AFC_EXPECTED_OUTPUT_DIGEST="8255cfecc6e02a4f61f6e89c4e8fae0d1b6107a7dd1f717dad514c80a4232503")

    add_executable(afc_cli ${AFC_CLI_SOURCE} ${AFC_PROVIDER_SOURCE})
    target_link_libraries(afc_cli PRIVATE AudioSDK::audio_sdk)
    target_include_directories(afc_cli PRIVATE
        "${CMAKE_CURRENT_BINARY_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/src")
endif()

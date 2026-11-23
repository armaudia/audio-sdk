cmake_minimum_required(VERSION 3.20)
project(audio_sdk_block_nlms_afc_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

# Optional by design: OFF is the default and proves the task-local provider is
# absent from an otherwise unmodified installed SDK.
option(AS_ENABLE_BLOCK_NLMS_AFC "Link and register the task-local AFC reference" OFF)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

get_filename_component(AFC_TASK_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/.." ABSOLUTE)
set(AFC_PROVIDER_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/block_nlms_afc_provider.c")
set(AFC_CONFIG "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json")
set(AFC_REFERENCE "${AFC_TASK_ROOT}/fixtures/reference_asset.f32")
set(AFC_DESCRIPTOR_TEMPLATE "${CMAKE_CURRENT_SOURCE_DIR}/config/descriptor.h.in")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    ${AFC_PROVIDER_SOURCE} ${AFC_CONFIG} ${AFC_REFERENCE} ${AFC_DESCRIPTOR_TEMPLATE})

file(SHA256 ${AFC_PROVIDER_SOURCE} AFC_SOURCE_DIGEST)
file(SHA256 ${AFC_CONFIG} AFC_CONFIG_DIGEST)
file(SHA256 ${AFC_REFERENCE} AFC_REFERENCE_DIGEST)
file(SIZE ${AFC_REFERENCE} AFC_REFERENCE_BYTES)
configure_file(${AFC_DESCRIPTOR_TEMPLATE} afc_descriptor.h @ONLY)

add_executable(afc_registration tests/test_provider.c)
target_link_libraries(afc_registration PRIVATE AudioSDK::audio_sdk)
target_include_directories(afc_registration PRIVATE
    "${CMAKE_CURRENT_BINARY_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/src")
target_compile_definitions(afc_registration PRIVATE
    AFC_REFERENCE_PATH="${AFC_REFERENCE}")

if(AS_ENABLE_BLOCK_NLMS_AFC)
    target_sources(afc_registration PRIVATE ${AFC_PROVIDER_SOURCE})
    target_compile_definitions(afc_registration PRIVATE AS_ENABLE_BLOCK_NLMS_AFC)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(afc_registration PRIVATE m)
endif()

enable_testing()
add_test(NAME block_nlms_afc_registration COMMAND afc_registration)

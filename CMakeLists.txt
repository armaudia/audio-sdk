cmake_minimum_required(VERSION 3.20)

project(audio_sdk
    VERSION 0.1.0
    DESCRIPTION "Fixed-rate mono 16 kHz voice-enhancement SDK runtime and providers"
    LANGUAGES C CXX)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
option(AS_BUILD_CORE "Build the MPL-2.0 runtime (disable for the standalone Apache API)" ON)
add_subdirectory(api)
if(NOT AS_BUILD_CORE)
    return()
endif()
find_package(Threads REQUIRED)

option(AS_BUILD_TESTS "Build SDK tests" ON)
option(AS_BUILD_CONFORMANCE "Build the standalone conformance executable" ON)
option(AS_BUILD_EXAMPLES "Build C examples" ON)
option(AS_BUILD_SHARED "Build the shared runtime library" ON)
option(AS_ENABLE_SANITIZERS "Build with address/undefined sanitizers" OFF)
option(AS_ENABLE_TSAN "Build with the thread sanitizer" OFF)
option(AS_WARNINGS_AS_ERRORS "Treat project warnings as errors" ON)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)
add_compile_definitions(_POSIX_C_SOURCE=200809L)

if(AS_ENABLE_SANITIZERS AND AS_ENABLE_TSAN)
    message(FATAL_ERROR "AS_ENABLE_SANITIZERS and AS_ENABLE_TSAN are mutually exclusive")
endif()
if(AS_ENABLE_SANITIZERS)
    add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address,undefined)
elseif(AS_ENABLE_TSAN)
    add_compile_options(-fsanitize=thread -fno-omit-frame-pointer)
    add_link_options(-fsanitize=thread)
endif()

set(AS_WARNING_FLAGS -Wall -Wextra -Wpedantic -Wshadow)
if(AS_WARNINGS_AS_ERRORS)
    list(APPEND AS_WARNING_FLAGS -Werror)
endif()

file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/docs/migration/source-allocation.csv"
    AS_SOURCE_ALLOCATION_DIGEST)
file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/deps/lock.json"
    AS_DEPENDENCY_LOCK_DIGEST)
file(GLOB_RECURSE AS_RUNTIME_INPUTS CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/core/src/*.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/core/src/*.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/core/providers/*.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/core/providers/*.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/api/include/audio_sdk/*.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/third_party/speexdsp/*.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/third_party/speexdsp/*.h")
list(APPEND AS_RUNTIME_INPUTS
    "${CMAKE_CURRENT_SOURCE_DIR}/CMakeLists.txt"
    "${CMAKE_CURRENT_SOURCE_DIR}/api/CMakeLists.txt"
    "${CMAKE_CURRENT_SOURCE_DIR}/deps/lock.json"
    "${CMAKE_CURRENT_SOURCE_DIR}/docs/migration/source-allocation.csv")
list(SORT AS_RUNTIME_INPUTS)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    ${AS_RUNTIME_INPUTS})
set(AS_RUNTIME_INPUTS_IDENTITY "")
set(AS_RUNTIME_INPUT_MANIFEST "${CMAKE_CURRENT_BINARY_DIR}/runtime-inputs.sha256")
file(WRITE "${AS_RUNTIME_INPUT_MANIFEST}" "")
foreach(input IN LISTS AS_RUNTIME_INPUTS)
    file(SHA256 "${input}" input_digest)
    file(RELATIVE_PATH input_relative "${CMAKE_CURRENT_SOURCE_DIR}" "${input}")
    file(TO_CMAKE_PATH "${input_relative}" input_relative)
    string(LENGTH "${input_relative}" input_relative_length)
    string(APPEND AS_RUNTIME_INPUTS_IDENTITY
        "${input_relative_length}:${input_relative}:${input_digest}\n")
    file(APPEND "${AS_RUNTIME_INPUT_MANIFEST}"
        "${input_digest}  ${input_relative}\n")
endforeach()
string(SHA256 AS_RUNTIME_INPUTS_DIGEST "${AS_RUNTIME_INPUTS_IDENTITY}")
string(JOIN " " AS_WARNING_FLAGS_TEXT ${AS_WARNING_FLAGS})
string(TOUPPER "${CMAKE_BUILD_TYPE}" AS_BUILD_TYPE_UPPER)
set(AS_BUILD_FLAGS_METADATA
    "${CMAKE_C_FLAGS}|${CMAKE_C_FLAGS_${AS_BUILD_TYPE_UPPER}}|${AS_WARNING_FLAGS_TEXT}|${CMAKE_CXX_FLAGS}|${CMAKE_CXX_FLAGS_${AS_BUILD_TYPE_UPPER}}|AS_ENABLE_SANITIZERS=${AS_ENABLE_SANITIZERS}|AS_ENABLE_TSAN=${AS_ENABLE_TSAN}|AS_WARNINGS_AS_ERRORS=${AS_WARNINGS_AS_ERRORS}|AS_BUILD_CONFORMANCE=${AS_BUILD_CONFORMANCE}|AS_BUILD_SHARED=${AS_BUILD_SHARED}")
string(SHA256 AS_BUILD_FLAGS_DIGEST "${AS_BUILD_FLAGS_METADATA}")
set(AS_BUILD_METADATA
    "${PROJECT_VERSION}|${CMAKE_C_COMPILER_ID}|${CMAKE_C_COMPILER_VERSION}|${CMAKE_CXX_COMPILER_ID}|${CMAKE_CXX_COMPILER_VERSION}|${CMAKE_BUILD_TYPE}|${CMAKE_SYSTEM_NAME}|${CMAKE_SYSTEM_PROCESSOR}|${CMAKE_OSX_ARCHITECTURES}|${CMAKE_OSX_DEPLOYMENT_TARGET}|${CMAKE_C_COMPILER_TARGET}|${CMAKE_CXX_COMPILER_TARGET}|${CMAKE_SYSROOT}|${AS_BUILD_FLAGS_DIGEST}|${AS_RUNTIME_INPUTS_DIGEST}|${AS_SOURCE_ALLOCATION_DIGEST}|${AS_DEPENDENCY_LOCK_DIGEST}|speexdsp-7a158783df74efe7c2d1c6ee8363c1e695c71226")
string(SHA256 AS_BUILD_METADATA_DIGEST "${AS_BUILD_METADATA}")
set(AS_BUILD_ID "audio-sdk/${PROJECT_VERSION}+sha256:${AS_BUILD_METADATA_DIGEST}")
configure_file(cmake/build-info.json.in
    "${CMAKE_CURRENT_BINARY_DIR}/build-info.json" @ONLY)

# ---------------------------------------------------------------------------
# Vendored SpeexDSP (BSD-3-Clause). Exact inventoried source; see
# third_party/speexdsp/UPSTREAM.md and docs/migration/source-allocation.csv.
# ---------------------------------------------------------------------------
set(AS_SPEEXDSP_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/speexdsp")
add_library(as_speexdsp OBJECT
    "${AS_SPEEXDSP_DIR}/libspeexdsp/preprocess.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/mdf.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/fftwrap.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/filterbank.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/smallft.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/kiss_fft.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/kiss_fftr.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/resample.c")
target_include_directories(as_speexdsp
    PUBLIC "${AS_SPEEXDSP_DIR}/include"
    PRIVATE "${AS_SPEEXDSP_DIR}/libspeexdsp")
target_compile_definitions(as_speexdsp PRIVATE
    FLOATING_POINT USE_SMALLFT EXPORT= DISABLE_WARNINGS)
target_compile_options(as_speexdsp PRIVATE -w)
set_target_properties(as_speexdsp PROPERTIES
    C_VISIBILITY_PRESET hidden POSITION_INDEPENDENT_CODE ON)

# ---------------------------------------------------------------------------
# Core runtime
# ---------------------------------------------------------------------------
set(AS_CORE_SOURCES
    core/src/core/sha256.c
    core/src/core/json.c
    core/src/core/common.c
    core/src/core/descriptor.c
    core/src/core/registry.c
    core/src/core/config.c
    core/src/core/effective.c
    core/src/core/validity.c
    core/src/api/provider_call.c
    core/src/api/session.c
    core/src/api/worker.c
    core/providers/speex/speex_provider.c
    core/providers/highpass/highpass_provider.c
    core/src/descriptors/descriptors.c)

add_library(audio-sdk-core STATIC ${AS_CORE_SOURCES} $<TARGET_OBJECTS:as_speexdsp>)
set(AS_LIBRARY_TARGETS audio-sdk-core)
if(AS_BUILD_SHARED)
    add_library(audio_sdk_shared SHARED ${AS_CORE_SOURCES} $<TARGET_OBJECTS:as_speexdsp>)
    list(APPEND AS_LIBRARY_TARGETS audio_sdk_shared)
endif()
add_library(AudioSDK::audio_sdk ALIAS audio-sdk-core)
add_library(AudioSDK::core ALIAS audio-sdk-core)
add_library(audio_sdk_static ALIAS audio-sdk-core)

foreach(target IN LISTS AS_LIBRARY_TARGETS)
    target_include_directories(${target}
        PUBLIC
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/api/include>
            $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
        PRIVATE
            "${CMAKE_CURRENT_SOURCE_DIR}/core/src"
            "${AS_SPEEXDSP_DIR}/include")
    target_compile_options(${target} PRIVATE ${AS_WARNING_FLAGS})
    target_compile_definitions(${target} PRIVATE
        AS_BUILDING_LIBRARY
        "AS_BUILD_ID=\"${AS_BUILD_ID}\"")
    target_link_libraries(${target} PUBLIC audio-sdk-api PRIVATE Threads::Threads m)
endforeach()
set_target_properties(audio-sdk-core PROPERTIES
    OUTPUT_NAME audio_sdk
    EXPORT_NAME audio_sdk)
if(AS_BUILD_SHARED)
    set_target_properties(audio_sdk_shared PROPERTIES
        OUTPUT_NAME audio_sdk
        EXPORT_NAME audio_sdk_shared
        VERSION ${PROJECT_VERSION}
        SOVERSION ${PROJECT_VERSION_MAJOR}
        C_VISIBILITY_PRESET hidden)
endif()
target_compile_definitions(audio-sdk-core INTERFACE AS_STATIC)
if(APPLE)
    find_package(Python3 COMPONENTS Interpreter REQUIRED)
    find_program(AS_LIBTOOL_EXECUTABLE libtool REQUIRED)
    add_custom_command(TARGET audio-sdk-core POST_BUILD
        COMMAND "${Python3_EXECUTABLE}"
                "${CMAKE_CURRENT_SOURCE_DIR}/scripts/normalize_macos_archive.py"
                "$<TARGET_FILE:audio-sdk-core>"
                "${CMAKE_AR}"
                "${AS_LIBTOOL_EXECUTABLE}"
        DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/scripts/normalize_macos_archive.py"
        COMMENT "Normalizing static archive member timestamps"
        VERBATIM)
endif()

# ---------------------------------------------------------------------------
# Conformance executable
# ---------------------------------------------------------------------------
if(AS_BUILD_CONFORMANCE)
    add_library(as_conformance_checks STATIC conformance/checks.c)
    target_include_directories(as_conformance_checks
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/conformance")
    target_link_libraries(as_conformance_checks PUBLIC audio-sdk-core)
    target_compile_options(as_conformance_checks PRIVATE ${AS_WARNING_FLAGS})

    add_executable(audio_sdk_conformance conformance/main.c)
    target_link_libraries(audio_sdk_conformance PRIVATE as_conformance_checks)
    target_include_directories(audio_sdk_conformance
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/conformance")
    target_compile_options(audio_sdk_conformance PRIVATE ${AS_WARNING_FLAGS})
    if(AS_BUILD_TESTS)
        add_test(NAME as_conformance_speex
            COMMAND audio_sdk_conformance --provider speex.ns.v0
                    --report "${CMAKE_CURRENT_BINARY_DIR}/conformance-speex.json")
        add_test(NAME as_conformance_highpass
            COMMAND audio_sdk_conformance --provider dsp.highpass80.v0
                    --report "${CMAKE_CURRENT_BINARY_DIR}/conformance-highpass.json")
    endif()
endif()

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
if(AS_BUILD_TESTS)
    enable_testing()
    function(as_add_test name source)
        add_executable(${name} ${source})
        target_link_libraries(${name} PRIVATE audio-sdk-core)
        target_include_directories(${name}
            PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/core/src"
                    "${CMAKE_CURRENT_SOURCE_DIR}/conformance")
        target_compile_options(${name} PRIVATE ${AS_WARNING_FLAGS})
        add_test(NAME ${name} COMMAND ${name})
    endfunction()

    as_add_test(as_test_canonical core/tests/test_canonical.c)
    as_add_test(as_test_registry core/tests/test_registry.c)
    as_add_test(as_test_session core/tests/test_session.c)
    as_add_test(as_test_timing core/tests/test_timing.c)
    as_add_test(as_test_providers core/tests/test_providers.c)
    as_add_test(as_test_queues core/tests/test_queues.c)
    as_add_test(as_test_assets core/tests/test_assets.c)
    set_tests_properties(as_test_queues PROPERTIES TIMEOUT 45)
    as_add_test(as_test_validity core/tests/test_validity.c)
    as_add_test(as_test_cxx core/tests/test_cxx.cpp)
endif()

if(AS_BUILD_EXAMPLES)
    add_executable(as_example_c examples/c/switch_provider.c)
    target_link_libraries(as_example_c PRIVATE audio-sdk-core)
    target_include_directories(as_example_c PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/api/include")
endif()

# ---------------------------------------------------------------------------
# Install/export
# ---------------------------------------------------------------------------
install(TARGETS ${AS_LIBRARY_TARGETS}
    EXPORT AudioSDKTargets
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")

if(AS_BUILD_CONFORMANCE)
    install(TARGETS audio_sdk_conformance RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")
    install(DIRECTORY conformance/ DESTINATION "${CMAKE_INSTALL_DATADIR}/audio-sdk/conformance"
        FILES_MATCHING PATTERN "legacy_timing_probe.c" EXCLUDE
        PATTERN "*.c" PATTERN "*.h" PATTERN "CMakeLists.txt" PATTERN "*.md")
endif()

install(DIRECTORY schemas/ DESTINATION "${CMAKE_INSTALL_DATADIR}/audio-sdk/schemas"
    FILES_MATCHING PATTERN "*.json")
install(DIRECTORY notices/ DESTINATION "${CMAKE_INSTALL_DATADIR}/audio-sdk/licenses"
    FILES_MATCHING PATTERN "*.txt")
install(FILES notices/NOTICE
    DESTINATION "${CMAKE_INSTALL_DATADIR}/audio-sdk/licenses")
install(FILES LICENSE.md SOURCE_LOCATION.md
    DESTINATION "${CMAKE_INSTALL_DATADIR}/audio-sdk/licenses")
install(DIRECTORY LICENSES/ DESTINATION "${CMAKE_INSTALL_DATADIR}/audio-sdk/licenses")
install(FILES third_party/speexdsp/UPSTREAM.md
    DESTINATION "${CMAKE_INSTALL_DATADIR}/audio-sdk/licenses/third-party")
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/build-info.json"
    deps/lock.json
    deps/speexdsp-files.sha256
    docs/migration/source-allocation.csv
    docs/provider-v0.md
    docs/timing-regression.md
    docs/migration/legacy-abi.md
    DESTINATION "${CMAKE_INSTALL_DATADIR}/audio-sdk")

install(EXPORT AudioSDKTargets
    FILE AudioSDKTargets.cmake
    NAMESPACE AudioSDK::
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/AudioSDK")
configure_package_config_file(
    cmake/AudioSDKConfig.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/AudioSDKConfig.cmake"
    INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/AudioSDK")
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/AudioSDKConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion)
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/AudioSDKConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/AudioSDKConfigVersion.cmake"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/AudioSDK")

configure_file(cmake/audio-sdk.pc.in
    "${CMAKE_CURRENT_BINARY_DIR}/audio-sdk.pc" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/audio-sdk.pc"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/pkgconfig")

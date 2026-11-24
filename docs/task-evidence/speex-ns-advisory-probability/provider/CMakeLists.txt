cmake_minimum_required(VERSION 3.20)
project(audio_sdk_speex_ns_advisory_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY
       "Compile and register the task-local advisory probability reference" OFF)

add_executable(as_speex_ns_advisory_test tests/test_provider.c)
target_link_libraries(as_speex_ns_advisory_test PRIVATE AudioSDK::audio_sdk)
target_include_directories(as_speex_ns_advisory_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

if(AS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        speex_ns_advisory_provider.c config/config.json expected_vectors.h
        speex_ns_advisory_analysis.h)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/speex_ns_advisory_provider.c"
         SPEEX_NS_ADVISORY_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json"
         SPEEX_NS_ADVISORY_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in speex_ns_advisory_descriptor.h @ONLY)
    target_sources(as_speex_ns_advisory_test PRIVATE speex_ns_advisory_provider.c)
    target_include_directories(as_speex_ns_advisory_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_speex_ns_advisory_test PRIVATE AS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_speex_ns_advisory_test PRIVATE m)
endif()

enable_testing()
add_test(NAME speex_ns_advisory_probability_registration
         COMMAND as_speex_ns_advisory_test)

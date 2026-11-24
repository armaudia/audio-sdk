cmake_minimum_required(VERSION 3.20)
project(audio_sdk_de_esser_reference LANGUAGES C)

find_package(AudioSDK 0.1 CONFIG REQUIRED)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

option(AS_ENABLE_DE_ESSER
       "Compile and register the task-local reference provider" OFF)

add_executable(as_de_esser_test tests/test_provider.c)
target_link_libraries(as_de_esser_test PRIVATE AudioSDK::audio_sdk)

if(AS_ENABLE_DE_ESSER)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        de_esser_provider.c config/config.json)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/de_esser_provider.c" DE_SOURCE_DIGEST)
    file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/config/config.json" DE_CONFIG_DIGEST)
    configure_file(config/descriptor.h.in deesser_descriptor.h @ONLY)
    target_sources(as_de_esser_test PRIVATE de_esser_provider.c)
    target_include_directories(as_de_esser_test PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_compile_definitions(as_de_esser_test PRIVATE AS_ENABLE_DE_ESSER)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(as_de_esser_test PRIVATE m)
endif()

enable_testing()
add_test(NAME de_esser_registration COMMAND as_de_esser_test)

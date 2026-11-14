# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.20)
project(audio_sdk_api VERSION 0.1.0 LANGUAGES C)
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

add_library(audio-sdk-api INTERFACE)
add_library(AudioSDK::api ALIAS audio-sdk-api)
set_target_properties(audio-sdk-api PROPERTIES EXPORT_NAME api)
target_include_directories(audio-sdk-api INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)
install(TARGETS audio-sdk-api EXPORT AudioSDKAPITargets)
install(FILES LICENSE NOTICE DESTINATION ${CMAKE_INSTALL_DATADIR}/audio-sdk-api)
install(DIRECTORY include/audio_sdk DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(EXPORT AudioSDKAPITargets NAMESPACE AudioSDK::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/AudioSDKAPI)
configure_package_config_file(cmake/AudioSDKAPIConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/AudioSDKAPIConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/AudioSDKAPI)
write_basic_package_version_file(${CMAKE_CURRENT_BINARY_DIR}/AudioSDKAPIConfigVersion.cmake
    VERSION ${PROJECT_VERSION} COMPATIBILITY SameMajorVersion)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/AudioSDKAPIConfig.cmake
              ${CMAKE_CURRENT_BINARY_DIR}/AudioSDKAPIConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/AudioSDKAPI)
configure_file(cmake/audio-sdk-api.pc.in ${CMAKE_CURRENT_BINARY_DIR}/audio-sdk-api.pc @ONLY)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/audio-sdk-api.pc
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    enable_testing()
    add_executable(audio_sdk_api_header_smoke tests/header_smoke.c)
    target_link_libraries(audio_sdk_api_header_smoke PRIVATE AudioSDK::api)
    set_target_properties(audio_sdk_api_header_smoke PROPERTIES C_STANDARD 11)
    add_test(NAME public_api_without_core COMMAND audio_sdk_api_header_smoke)
endif()

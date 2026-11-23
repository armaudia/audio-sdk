foreach(target IN LISTS AS_LIBRARY_TARGETS)
    target_sources(${target} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/highpass_provider.c")
endforeach()

if(AS_BUILD_TESTS)
    as_add_test(as_test_providers "${CMAKE_CURRENT_LIST_DIR}/tests/test_highpass.c")
    target_include_directories(as_test_providers PRIVATE "${PROJECT_SOURCE_DIR}/core/tests")
    if(AS_BUILD_CONFORMANCE)
        add_test(NAME as_conformance_highpass
            COMMAND audio_sdk_conformance --provider dsp.highpass80.v0
                    --report "${CMAKE_CURRENT_BINARY_DIR}/conformance-highpass.json")
    endif()
endif()

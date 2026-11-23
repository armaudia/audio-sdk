# Exact vendored inputs; see third_party/speexdsp/UPSTREAM.md.
set(AS_SPEEXDSP_DIR "${PROJECT_SOURCE_DIR}/third_party/speexdsp")
add_library(as_speexdsp OBJECT
    "${AS_SPEEXDSP_DIR}/libspeexdsp/preprocess.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/mdf.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/fftwrap.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/filterbank.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/smallft.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/kiss_fft.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/kiss_fftr.c"
    "${AS_SPEEXDSP_DIR}/libspeexdsp/resample.c")
target_include_directories(as_speexdsp PRIVATE
    "${AS_SPEEXDSP_DIR}/include" "${AS_SPEEXDSP_DIR}/libspeexdsp")
target_compile_definitions(as_speexdsp PRIVATE
    FLOATING_POINT USE_SMALLFT EXPORT= DISABLE_WARNINGS)
target_compile_options(as_speexdsp PRIVATE -w)
set_target_properties(as_speexdsp PROPERTIES C_VISIBILITY_PRESET hidden)

set_source_files_properties("${CMAKE_CURRENT_LIST_DIR}/speex_provider.c"
    PROPERTIES INCLUDE_DIRECTORIES "${AS_SPEEXDSP_DIR}/include")
foreach(target IN LISTS AS_LIBRARY_TARGETS)
    target_sources(${target} PRIVATE
        "${CMAKE_CURRENT_LIST_DIR}/speex_provider.c" $<TARGET_OBJECTS:as_speexdsp>)
endforeach()

if(AS_BUILD_TESTS AND AS_BUILD_CONFORMANCE)
    add_test(NAME as_conformance_speex
        COMMAND audio_sdk_conformance --provider speex.ns.v0
                --report "${CMAKE_CURRENT_BINARY_DIR}/conformance-speex.json")
endif()

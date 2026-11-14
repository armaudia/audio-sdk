/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0 */
#include <stdint.h>

const char as_speex_descriptor[] = "{\"buffering_delay_samples\":160,\"callback_safe\":false,\"configuration_schema_digest\":\"sha256:3abd42cbab659edd846c2d1d3c6eb3d3921f95fc715ce26469ed34eddc418494\",\"contract_version\":\"0.1\",\"edge_exclusions\":{\"end_samples\":0,\"start_samples\":0},\"execution_modes\":[2,3],\"implementation_id\":\"speex.preprocess.floating.smallft\",\"implementation_version\":\"1.0.0\",\"max_drain_calls\":2,\"native_hop_samples\":160,\"platform\":{\"architectures\":[\"arm64\",\"x86_64\"],\"cpu_requirements\":\"baseline\"},\"provider_id\":\"speex.ns.v0\",\"required_assets\":[],\"schema_id\":\"audio-sdk/descriptor/0.1\",\"source_digest\":\"sha256:4f324b89c5dfa81001fe55759e09b939eb964ef3b7dd74f9e89caa4630ae647b\",\"source_revision\":\"7a158783df74efe7c2d1c6ee8363c1e695c71226\",\"supported_formats\":[{\"channels\":1,\"frame_samples\":160,\"sample_format\":\"f32\",\"sample_rate_hz\":16000}],\"upstream\":{\"license\":\"BSD-3-Clause\",\"name\":\"Xiph.Org SpeexDSP\",\"notice_path\":\"licenses/third-party/speexdsp-COPYING.txt\"}}";

const uint32_t as_speex_descriptor_length = 936u;

const char as_highpass_descriptor[] = "{\"buffering_delay_samples\":0,\"callback_safe\":false,\"configuration_schema_digest\":\"sha256:988b0eda43c6156b5c34173c32c0be5c0a3251ccc300e4ffed25c35dae79eed3\",\"contract_version\":\"0.1\",\"edge_exclusions\":{\"end_samples\":0,\"start_samples\":0},\"execution_modes\":[2,3],\"implementation_id\":\"dsp.highpass.biquad.f64\",\"implementation_version\":\"1.0.0\",\"max_drain_calls\":1,\"native_hop_samples\":160,\"platform\":{\"architectures\":[\"arm64\",\"x86_64\"],\"cpu_requirements\":\"baseline\"},\"provider_id\":\"dsp.highpass80.v0\",\"required_assets\":[],\"schema_id\":\"audio-sdk/descriptor/0.1\",\"source_digest\":\"sha256:9da5ab40e8795dd32b4228674e7d851e054cfbe798034e76944a96e8cbf2538f\",\"source_revision\":null,\"supported_formats\":[{\"channels\":1,\"frame_samples\":160,\"sample_format\":\"f32\",\"sample_rate_hz\":16000}],\"upstream\":{\"license\":\"MPL-2.0\",\"name\":\"audio-sdk first-party high-pass\",\"notice_path\":\"licenses/MPL-2.0.txt\"}}";

const uint32_t as_highpass_descriptor_length = 880u;

#ifndef AS_BUILD_ID
#define AS_BUILD_ID "audio-sdk/0.1.0+unconfigured"
#endif
const char as_build_identity[] = AS_BUILD_ID;

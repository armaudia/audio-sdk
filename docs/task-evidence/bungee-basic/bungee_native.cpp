// SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
// SPDX-License-Identifier: Apache-2.0
//
// Task-local developer reference only. This file is ours; it includes the
// public headers of a separately staged, pinned Bungee Basic checkout. No
// Bungee source, header, binary or audio asset is copied into this repository.
// It is not built by the SDK, registered, enabled by default, or an SDK ABI.

#include <bungee/Bungee.h>
#include <bungee/Stream.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <limits>
#include <numeric>
#include <string>
#include <vector>

namespace {

struct Options {
  std::string mode = "stream";
  std::string input;
  std::string output;
  std::string json;
  std::string schedule = "0:1";
  std::string chunks = "160";
  double speed = 1.0;
  int tail_samples = 0;
  int max_grains = 4096;
  int max_drain_calls = 128;
};

[[noreturn]] void fail(const std::string &message) {
  std::fprintf(stderr, "bungee_native: %s\n", message.c_str());
  std::exit(2);
}

uint32_t readU32(const unsigned char *p) {
  return uint32_t(p[0]) | (uint32_t(p[1]) << 8) | (uint32_t(p[2]) << 16) |
         (uint32_t(p[3]) << 24);
}

void writeU16(std::vector<char> &out, uint16_t value) {
  out.push_back(char(value & 0xff));
  out.push_back(char((value >> 8) & 0xff));
}

void writeU32(std::vector<char> &out, uint32_t value) {
  for (int shift = 0; shift < 32; shift += 8)
    out.push_back(char((value >> shift) & 0xff));
}

std::vector<float> readWav(const std::string &path, int &sampleRate) {
  std::ifstream file(path, std::ios::binary);
  if (!file)
    fail("cannot open input WAV: " + path);
  std::vector<char> bytes((std::istreambuf_iterator<char>(file)),
                          std::istreambuf_iterator<char>());
  if (bytes.size() < 44 || std::memcmp(bytes.data(), "RIFF", 4) ||
      std::memcmp(bytes.data() + 8, "WAVE", 4))
    fail("input is not RIFF/WAVE");

  size_t position = 12;
  int format = 0, channels = 0, bits = 0;
  std::vector<float> samples;
  bool haveData = false;
  while (position + 8 <= bytes.size()) {
    const char *id = bytes.data() + position;
    const uint32_t length = readU32(
        reinterpret_cast<const unsigned char *>(bytes.data() + position + 4));
    position += 8;
    if (position + length > bytes.size())
      fail("truncated WAV chunk");
    if (!std::memcmp(id, "fmt ", 4) && length >= 16) {
      const auto *p = reinterpret_cast<const unsigned char *>(bytes.data() + position);
      format = int(p[0]) | (int(p[1]) << 8);
      channels = int(p[2]) | (int(p[3]) << 8);
      sampleRate = int(readU32(p + 4));
      bits = int(p[14]) | (int(p[15]) << 8);
    } else if (!std::memcmp(id, "data", 4)) {
      if (format != 3 || channels != 1 || bits != 32 || length % 4)
        fail("expected mono 32-bit float WAV");
      samples.resize(length / 4);
      std::memcpy(samples.data(), bytes.data() + position, length);
      haveData = true;
    }
    position += length + (length & 1u);
  }
  if (!haveData || sampleRate != 16000 || samples.empty())
    fail("expected nonempty 16 kHz mono float32 WAV");
  for (float value : samples)
    if (!std::isfinite(value))
      fail("nonfinite input sample");
  return samples;
}

void writeWav(const std::string &path, const std::vector<float> &samples) {
  std::vector<char> bytes;
  const uint32_t dataBytes = uint32_t(samples.size()) * 4;
  const auto appendText = [&](const char *text, size_t length) {
    bytes.insert(bytes.end(), text, text + length);
  };
  appendText("RIFF", 4);
  writeU32(bytes, 36 + dataBytes);
  appendText("WAVEfmt ", 8);
  writeU32(bytes, 16);
  writeU16(bytes, 3);
  writeU16(bytes, 1);
  writeU32(bytes, 16000);
  writeU32(bytes, 64000);
  writeU16(bytes, 4);
  writeU16(bytes, 32);
  appendText("data", 4);
  writeU32(bytes, dataBytes);
  for (float value : samples) {
    uint32_t bits;
    std::memcpy(&bits, &value, 4);
    writeU32(bytes, bits);
  }
  std::ofstream file(path, std::ios::binary);
  if (!file || !file.write(bytes.data(), std::streamsize(bytes.size())))
    fail("cannot write output WAV: " + path);
}

std::string quote(const std::string &value) {
  std::string result = "\"";
  for (char c : value) {
    if (c == '"' || c == '\\')
      result += '\\';
    result += c;
  }
  return result + '"';
}

std::string number(double value, int precision = 6) {
  char buffer[64];
  std::snprintf(buffer, sizeof(buffer), "%.*f", precision, value);
  return buffer;
}

struct Knot {
  int start;
  double speed;
};

std::vector<Knot> parseSchedule(const std::string &text) {
  std::vector<Knot> knots;
  size_t begin = 0;
  while (begin <= text.size()) {
    const size_t comma = text.find(',', begin);
    const std::string item =
        text.substr(begin, comma == std::string::npos ? std::string::npos : comma - begin);
    const size_t colon = item.find(':');
    if (colon == std::string::npos)
      fail("bad schedule item: " + item);
    char *end = nullptr;
    const long start = std::strtol(item.c_str(), &end, 10);
    if (end != item.c_str() + colon || start < 0)
      fail("bad schedule offset: " + item);
    const double speed = std::strtod(item.c_str() + colon + 1, &end);
    if (end != item.c_str() + item.size() || !(speed > 0.0) || speed > 100.0)
      fail("bad schedule speed: " + item);
    if (!knots.empty() && start <= knots.back().start)
      fail("schedule offsets must increase");
    knots.push_back({int(start), speed});
    if (comma == std::string::npos)
      break;
    begin = comma + 1;
  }
  if (knots.empty() || knots.front().start != 0)
    fail("schedule must start at source sample zero");
  return knots;
}

std::vector<int> parseChunks(const std::string &text) {
  std::vector<int> chunks;
  size_t begin = 0;
  while (begin <= text.size()) {
    const size_t comma = text.find(',', begin);
    const std::string item =
        text.substr(begin, comma == std::string::npos ? std::string::npos : comma - begin);
    char *end = nullptr;
    const long value = std::strtol(item.c_str(), &end, 10);
    if (end != item.c_str() + item.size() || value <= 0 || value > 4096)
      fail("bad chunk size: " + item);
    chunks.push_back(int(value));
    if (comma == std::string::npos)
      break;
    begin = comma + 1;
  }
  if (chunks.empty())
    fail("empty chunk schedule");
  return chunks;
}

struct Timeline {
  std::vector<Knot> knots;

  double speedAt(int source) const {
    double speed = knots.front().speed;
    for (const auto &knot : knots)
      if (source >= knot.start)
        speed = knot.speed;
      else
        break;
    return speed;
  }

  int targetAt(int source) const {
    long double total = 0;
    for (size_t i = 0; i < knots.size(); ++i) {
      const int start = knots[i].start;
      const int end = i + 1 < knots.size() ? knots[i + 1].start : source;
      if (source <= start)
        break;
      total += static_cast<long double>(std::min(end, source) - start) /
               static_cast<long double>(knots[i].speed);
    }
    return int(std::round(total));
  }

  bool chunkCrossesKnot(int start, int count) const {
    for (const auto &knot : knots)
      if (knot.start > start && knot.start < start + count)
        return true;
    return false;
  }
};

std::string runStream(const Options &options, const std::vector<float> &x) {
  const auto chunks = parseChunks(options.chunks);
  const Timeline timeline{parseSchedule(options.schedule)};
  const int maxChunk = *std::max_element(chunks.begin(), chunks.end());

  Bungee::Stretcher<Bungee::Basic> stretcher({16000, 16000}, 1);
  Bungee::Stream<Bungee::Basic> stream(stretcher, maxChunk * 2, 1);
  std::vector<float> outputBuffer(8192), inputBuffer(maxChunk, 0.f);
  float *inputPointers[1]{inputBuffer.data()};
  float *outputPointers[1]{outputBuffer.data()};

  std::vector<float> y;
  std::string mapping;
  const int n = int(x.size());
  const int target = timeline.targetAt(n) + options.tail_samples;
  int consumed = 0, produced = 0, chunkIndex = 0, drainCalls = 0, drainSamples = 0;
  bool finite = true;
  double maxAbs = 0.0;

  const auto append = [&](int count) {
    for (int i = 0; i < count; ++i) {
      const float value = outputBuffer[i];
      if (!std::isfinite(value))
        finite = false;
      maxAbs = std::max(maxAbs, double(std::fabs(value)));
      y.push_back(value);
    }
  };

  while (consumed < n) {
    const int chunk = std::min(n - consumed, chunks[chunkIndex % chunks.size()]);
    if (timeline.chunkCrossesKnot(consumed, chunk))
      fail("chunk crosses a rate knot; align the chunk schedule");
    const double speed = timeline.speedAt(consumed);
    for (int i = 0; i < chunk; ++i)
      inputBuffer[i] = x[consumed + i];
    const int want = int(std::round(timeline.targetAt(consumed + chunk))) - produced;
    if (want < 0)
      fail("negative output request");
    const int made = stream.process(inputPointers, outputPointers, chunk, want, 1.0);
    if (made < 0 || made > 8192)
      fail("invalid produced count");
    const double endPosition = stream.outputPosition();
    const double beginPosition = endPosition - made * speed;
    if (!mapping.empty())
      mapping += ',';
    char record[512];
    std::snprintf(record, sizeof(record),
                  "{\"source\":[%d,%d],\"speed\":%s,\"output\":[%d,%d],"
                  "\"native_source_begin\":%s,\"native_source_end\":%s,"
                  "\"latency_input_frames\":%s}",
                  consumed, consumed + chunk, number(speed).c_str(), produced, produced + made,
                  std::isfinite(beginPosition) ? number(beginPosition).c_str() : "null",
                  std::isfinite(endPosition) ? number(endPosition).c_str() : "null",
                  number(stream.latency()).c_str());
    mapping += record;
    append(made);
    produced += made;
    consumed += chunk;
    ++chunkIndex;
  }

  while (produced < target && drainCalls < options.max_drain_calls) {
    const int want = std::min(maxChunk, target - produced);
    const int made = stream.process(nullptr, outputPointers, want, want, 1.0);
    append(made);
    produced += made;
    drainSamples += made;
    ++drainCalls;
    if (made == 0)
      break;
  }

  writeWav(options.output, y);
  std::string result;
  char head[512];
  std::snprintf(head, sizeof(head),
                "{\"mode\":\"stream\",\"edition\":\"Basic\",\"version\":%s,"
                "\"source_frames\":%d,\"output_frames\":%d,\"target_frames\":%d,"
                "\"chunk_cycle\":%s,\"schedule\":%s,\"caller_zero_tail_samples\":%d,"
                "\"mapping\":[",
                quote(Bungee::Stretcher<Bungee::Basic>::version()).c_str(), n, produced,
                target, quote(options.chunks).c_str(), quote(options.schedule).c_str(),
                options.tail_samples);
  result += head + mapping;
  char tail[512];
  std::snprintf(tail, sizeof(tail),
                "],\"drain\":{\"calls\":%d,\"samples\":%d,\"finite\":%s},"
                "\"final_latency_input_frames\":%s,\"max_input_frame_count\":%d,"
                "\"finite_output\":%s,\"max_abs\":%s,\"output_sha256_wav_bytes\":%zu}",
                drainCalls, drainSamples, drainCalls < options.max_drain_calls ? "true" : "false",
                number(stream.latency()).c_str(), stretcher.maxInputFrameCount(),
                finite ? "true" : "false", number(maxAbs, 9).c_str(),
                y.size() * 4 + 44);
  result += tail;
  return result;
}

std::string runGranular(const Options &options, const std::vector<float> &x) {
  Bungee::Stretcher<Bungee::Basic> stretcher({16000, 16000}, 1);
  Bungee::Request request{};
  request.position = 0.0;
  request.speed = options.speed;
  request.pitch = 1.0;
  request.reset = false;
  stretcher.preroll(request);

  std::vector<float> input(stretcher.maxInputFrameCount() + 64, 0.f);
  std::vector<float> output(4096, 0.f);
  const int n = int(x.size());
  int grains = 0, produced = 0;
  bool finite = true, flushed = false;
  double maxAbs = 0.0;
  std::vector<float> y;
  const double limit = std::ceil(double(n) / options.speed) + 4096;

  while (grains < options.max_grains) {
    const Bungee::InputChunk chunk = stretcher.specifyGrain(request);
    const int head = std::max(0, -chunk.begin);
    const int tail = std::max(0, chunk.end - n);
    for (int i = chunk.begin; i < chunk.end; ++i) {
      const int offset = i - chunk.begin;
      input[offset] = (i >= 0 && i < n) ? x[i] : 0.f;
    }
    stretcher.analyseGrain(input.data(), 1, head, tail);
    Bungee::Request begin{}, end{};
    Bungee::OutputChunk result{};
    result.data = output.data();
    result.channelStride = output.size();
    result.request[0] = &begin;
    result.request[1] = &end;
    stretcher.synthesiseGrain(result);
    for (int i = 0; i < result.frameCount; ++i) {
      if (!std::isfinite(result.data[i]))
        finite = false;
      maxAbs = std::max(maxAbs, double(std::fabs(result.data[i])));
      y.push_back(result.data[i]);
    }
    produced += result.frameCount;
    stretcher.next(request);
    ++grains;
    if (request.position >= n && !std::isnan(request.position))
      request.position = std::numeric_limits<double>::quiet_NaN();
    if (stretcher.isFlushed()) {
      flushed = true;
      break;
    }
    if (produced > limit)
      fail("granular output exceeded bounded limit");
  }

  writeWav(options.output, y);
  char buffer[512];
  std::snprintf(buffer, sizeof(buffer),
                "{\"mode\":\"granular\",\"edition\":\"Basic\",\"version\":%s,"
                "\"source_frames\":%d,\"speed\":%s,\"grains\":%d,"
                "\"output_frames_including_preroll\":%d,\"is_flushed\":%s,"
                "\"bounded_by_grains\":%s,\"finite_output\":%s,\"max_abs\":%s,"
                "\"max_input_frame_count\":%d}",
                quote(Bungee::Stretcher<Bungee::Basic>::version()).c_str(), n,
                number(options.speed).c_str(), grains, produced, flushed ? "true" : "false",
                grains < options.max_grains ? "true" : "false",
                finite ? "true" : "false", number(maxAbs, 9).c_str(),
                stretcher.maxInputFrameCount());
  return buffer;
}

Options parseOptions(int argc, char **argv) {
  Options options;
  for (int i = 1; i < argc; ++i) {
    const std::string key = argv[i];
    if (i + 1 >= argc)
      fail("missing value for " + key);
    const std::string value = argv[++i];
    if (key == "--mode")
      options.mode = value;
    else if (key == "--input")
      options.input = value;
    else if (key == "--output")
      options.output = value;
    else if (key == "--json")
      options.json = value;
    else if (key == "--schedule")
      options.schedule = value;
    else if (key == "--chunks")
      options.chunks = value;
    else if (key == "--speed")
      options.speed = std::strtod(value.c_str(), nullptr);
    else if (key == "--tail-samples")
      options.tail_samples = std::atoi(value.c_str());
    else if (key == "--max-grains")
      options.max_grains = std::atoi(value.c_str());
    else if (key == "--max-drain-calls")
      options.max_drain_calls = std::atoi(value.c_str());
    else
      fail("unknown option: " + key);
  }
  if (options.input.empty() || options.output.empty() || options.json.empty())
    fail("usage: bungee_native --mode stream|granular --input IN.wav --output OUT.wav "
         "--json OUT.json [--schedule S] [--chunks C] [--speed S] [--tail-samples N]");
  if (options.mode != "stream" && options.mode != "granular")
    fail("unknown mode: " + options.mode);
  if (options.tail_samples < 0 || options.max_grains <= 0 || options.max_drain_calls <= 0)
    fail("invalid bound");
  return options;
}

}  // namespace

int main(int argc, char **argv) {
  const Options options = parseOptions(argc, argv);
  int sampleRate = 0;
  const std::vector<float> x = readWav(options.input, sampleRate);
  (void)sampleRate;
  const std::string json =
      options.mode == "stream" ? runStream(options, x) : runGranular(options, x);
  std::ofstream file(options.json, std::ios::binary);
  if (!file || !(file << json << '\n'))
    fail("cannot write JSON: " + options.json);
  return 0;
}

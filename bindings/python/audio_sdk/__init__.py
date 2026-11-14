# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Thin stdlib-only ctypes binding for audio-sdk v0.1.

The C ABI remains authoritative. The wrapper performs ownership and buffer
management but does not reinterpret timestamps or resample audio.
"""
from __future__ import annotations

import ctypes as C
import os
from pathlib import Path

AS_OK = 0
AS_END_OF_STREAM = 7
AS_MODE_PROCESSING_THREAD = 2
AS_MODE_BUFFERED_WORKER = 3
FRAME_SAMPLES = 160


class Error(C.Structure):
    _fields_ = [
        ("struct_size", C.c_uint32), ("abi_major", C.c_uint32),
        ("abi_minor", C.c_uint32), ("status", C.c_int32),
        ("message", C.c_char * 256), ("field", C.c_char * 96),
    ]


class Asset(C.Structure):
    _fields_ = [
        ("struct_size", C.c_uint32), ("abi_major", C.c_uint32),
        ("abi_minor", C.c_uint32), ("asset_id", C.c_char_p),
        ("asset_id_length", C.c_uint32), ("reserved0", C.c_uint32),
        ("sha256", C.c_uint8 * 32), ("data", C.c_void_p),
        ("byte_count", C.c_uint64),
    ]


class CreateConfig(C.Structure):
    _fields_ = [
        ("struct_size", C.c_uint32), ("abi_major", C.c_uint32),
        ("abi_minor", C.c_uint32), ("sample_rate_hz", C.c_uint32),
        ("channels", C.c_uint32), ("frame_samples", C.c_uint32),
        ("execution_mode", C.c_uint32), ("reserved0", C.c_uint32),
        ("epoch", C.c_uint64), ("first_input_sample", C.c_int64),
        ("config_json", C.c_char_p), ("config_json_length", C.c_uint32),
        ("reserved1", C.c_uint32), ("assets", C.POINTER(Asset)),
        ("asset_count", C.c_uint32), ("reserved", C.c_uint32 * 3),
    ]


class Frame(C.Structure):
    _fields_ = [
        ("struct_size", C.c_uint32), ("abi_major", C.c_uint32),
        ("abi_minor", C.c_uint32), ("input", C.POINTER(C.c_float)),
        ("input_count", C.c_uint32), ("input_valid_count", C.c_uint32),
        ("flags", C.c_uint32), ("reserved0", C.c_uint32),
        ("epoch", C.c_uint64), ("first_input_sample", C.c_int64),
    ]


class Output(C.Structure):
    _fields_ = [
        ("struct_size", C.c_uint32), ("abi_major", C.c_uint32),
        ("abi_minor", C.c_uint32), ("samples", C.POINTER(C.c_float)),
        ("capacity", C.c_uint32), ("reserved0", C.c_uint32),
    ]


class Result(C.Structure):
    _fields_ = [
        ("struct_size", C.c_uint32), ("abi_major", C.c_uint32),
        ("abi_minor", C.c_uint32), ("status", C.c_int32),
        ("consumed_count", C.c_uint32), ("produced_count", C.c_uint32),
        ("valid_offset", C.c_uint32), ("valid_count", C.c_uint32),
        ("flags", C.c_uint32), ("epoch", C.c_uint64),
        ("source_first_sample", C.c_int64), ("queue_depth", C.c_uint32),
        ("reserved", C.c_uint32 * 3),
    ]


def _load_library() -> C.CDLL:
    explicit = os.environ.get("AUDIO_SDK_LIBRARY")
    if not explicit:
        raise OSError("set AUDIO_SDK_LIBRARY to an explicit SDK library path")
    path = Path(explicit)
    if not path.is_absolute() or not path.is_file():
        raise OSError("AUDIO_SDK_LIBRARY must name an existing absolute path")
    return C.CDLL(str(path))


_lib = _load_library()
_lib.as_error_v0_init.argtypes = [C.POINTER(Error)]
_lib.as_contract_version_v0.restype = C.c_char_p
_lib.as_build_id_v0.restype = C.c_char_p
_lib.as_registry_create_v0.argtypes = [C.POINTER(C.c_void_p), C.POINTER(Error)]
_lib.as_registry_close_v0.argtypes = [C.POINTER(C.c_void_p)]
_lib.as_effective_config_create_v0.argtypes = [
    C.c_void_p, C.c_char_p, C.c_uint32, C.c_uint32, C.c_char_p,
    C.c_uint32, C.POINTER(C.c_uint32), C.POINTER(Error),
]
_lib.as_session_create_v0.argtypes = [
    C.c_void_p, C.c_char_p, C.c_uint32, C.POINTER(CreateConfig),
    C.POINTER(C.c_void_p), C.POINTER(Error),
]
_lib.as_session_process_v0.argtypes = [
    C.c_void_p, C.POINTER(Frame), C.POINTER(Output), C.POINTER(Result),
]
_lib.as_session_begin_drain_v0.argtypes = [C.c_void_p]
_lib.as_session_drain_next_v0.argtypes = [
    C.c_void_p, C.POINTER(Output), C.POINTER(Result),
]
_lib.as_session_reset_v0.argtypes = [
    C.c_void_p, C.c_uint64, C.c_int64, C.POINTER(Error),
]
_lib.as_session_close_v0.argtypes = [C.POINTER(C.c_void_p)]
_lib.as_status_name_v0.argtypes = [C.c_int32]
_lib.as_status_name_v0.restype = C.c_char_p

_contract = _lib.as_contract_version_v0().decode("ascii")
_build_id = _lib.as_build_id_v0().decode("ascii")
_expected_build = os.environ.get("AUDIO_SDK_EXPECTED_BUILD_ID")
if _contract != "0.1" or not _build_id or (
    _expected_build is not None and _expected_build != _build_id
):
    raise ImportError(
        f"audio-sdk identity mismatch: contract={_contract!r}, build={_build_id!r}"
    )


def _error() -> Error:
    error = Error()
    _lib.as_error_v0_init(C.byref(error))
    return error


def _raise(status: int, error: Error | None = None) -> None:
    if status == AS_OK:
        return
    name = _lib.as_status_name_v0(status).decode("ascii", "replace")
    if error is None:
        raise RuntimeError(name)
    message = bytes(error.message).split(b"\0", 1)[0].decode("utf-8", "replace")
    field = bytes(error.field).split(b"\0", 1)[0].decode("utf-8", "replace")
    raise RuntimeError(f"{name}: {message} ({field})")


def _integer(value: int, name: str, maximum: int) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [0, {maximum}]")
    return value


class Registry:
    def __init__(self) -> None:
        self._handle = C.c_void_p()
        error = _error()
        _raise(_lib.as_registry_create_v0(C.byref(self._handle), C.byref(error)),
               error)

    def close(self) -> None:
        if self._handle:
            _raise(_lib.as_registry_close_v0(C.byref(self._handle)))

    def session(self, provider_id: str, mode: int = AS_MODE_PROCESSING_THREAD,
                epoch: int = 1, first_input_sample: int = 0) -> "Session":
        if type(mode) is not int or mode != AS_MODE_PROCESSING_THREAD:
            raise ValueError("the Python binding supports synchronous mode 2; use the C API for buffered workers")
        _integer(epoch, "epoch", 2**64 - 1)
        _integer(first_input_sample, "first_input_sample", 2**63 - 1)
        provider = provider_id.encode("ascii")
        effective = C.create_string_buffer(4096)
        required = C.c_uint32()
        error = _error()
        status = _lib.as_effective_config_create_v0(
            self._handle, provider, len(provider), mode, effective,
            len(effective), C.byref(required), C.byref(error))
        _raise(status, error)

        config = CreateConfig()
        config.struct_size = C.sizeof(config)
        config.abi_major = 0
        config.abi_minor = 1
        config.sample_rate_hz = 16000
        config.channels = 1
        config.frame_samples = FRAME_SAMPLES
        config.execution_mode = mode
        config.epoch = epoch
        config.first_input_sample = first_input_sample
        config.config_json = C.cast(effective, C.c_char_p)
        config.config_json_length = required.value - 1
        handle = C.c_void_p()
        status = _lib.as_session_create_v0(
            self._handle, provider, len(provider), C.byref(config),
            C.byref(handle), C.byref(error))
        _raise(status, error)
        return Session(handle, provider_id, epoch, first_input_sample)


class Session:
    def __init__(self, handle: C.c_void_p, provider_id: str, epoch: int,
                 first: int) -> None:
        self._handle = handle
        self.provider_id = provider_id
        self.epoch = epoch
        self.next_sample = first

    def process(self, samples, valid_count: int = FRAME_SAMPLES,
                final: bool = False) -> tuple[list[float], Result]:
        if len(samples) != FRAME_SAMPLES:
            raise ValueError("each frame must contain exactly 160 samples")
        _integer(valid_count, "valid_count", FRAME_SAMPLES)
        if valid_count == 0 or type(final) is not bool:
            raise ValueError("valid_count must be positive and final must be a bool")
        data = (C.c_float * FRAME_SAMPLES)(*samples)
        output_data = (C.c_float * FRAME_SAMPLES)()
        frame = Frame()
        frame.struct_size = C.sizeof(frame)
        frame.abi_major = 0
        frame.abi_minor = 1
        frame.input = data
        frame.input_count = FRAME_SAMPLES
        frame.input_valid_count = valid_count
        frame.flags = 1 if final else 0
        frame.epoch = self.epoch
        frame.first_input_sample = self.next_sample
        output = Output()
        output.struct_size = C.sizeof(output)
        output.abi_major = 0
        output.abi_minor = 1
        output.samples = output_data
        output.capacity = FRAME_SAMPLES
        result = Result()
        result.struct_size = C.sizeof(result)
        result.abi_major = 0
        result.abi_minor = 1
        status = _lib.as_session_process_v0(
            self._handle, C.byref(frame), C.byref(output), C.byref(result))
        _raise(status)
        self.next_sample += FRAME_SAMPLES
        return list(output_data), result

    def drain(self) -> list[tuple[list[float], Result]]:
        _raise(_lib.as_session_begin_drain_v0(self._handle))
        frames = []
        while True:
            data = (C.c_float * FRAME_SAMPLES)()
            output = Output()
            output.struct_size = C.sizeof(output)
            output.abi_major = 0
            output.abi_minor = 1
            output.samples = data
            output.capacity = FRAME_SAMPLES
            result = Result()
            result.struct_size = C.sizeof(result)
            result.abi_major = 0
            result.abi_minor = 1
            status = _lib.as_session_drain_next_v0(
                self._handle, C.byref(output), C.byref(result))
            if status == AS_END_OF_STREAM:
                return frames
            _raise(status)
            frames.append((list(data), result))

    def reset(self, epoch: int, first_input_sample: int = 0) -> None:
        _integer(epoch, "epoch", 2**64 - 1)
        _integer(first_input_sample, "first_input_sample", 2**63 - 1)
        error = _error()
        _raise(_lib.as_session_reset_v0(
            self._handle, epoch, first_input_sample, C.byref(error)), error)
        self.epoch = epoch
        self.next_sample = first_input_sample

    def close(self) -> None:
        if self._handle:
            _raise(_lib.as_session_close_v0(C.byref(self._handle)))

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()


__all__ = [
    "AS_MODE_BUFFERED_WORKER", "AS_MODE_PROCESSING_THREAD", "FRAME_SAMPLES",
    "Registry", "Session",
]

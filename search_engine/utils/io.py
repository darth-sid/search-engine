from collections.abc import Collection
from typing import BinaryIO, Any
import msgspec
import struct


def write_bin(
    file: BinaryIO, data: Collection, pos: int | None = None, delimited: bool = False
) -> int:
    """serializes a sequence and writes it to a given file + returns size of written chunk"""
    if pos is not None and pos != file.tell():
        file.seek(pos)
    if not delimited:
        serialized = msgspec.msgpack.encode(data)
    else:
        bin_data = []
        for elem in data:
            serialized = msgspec.msgpack.encode(elem)
            size = len(serialized)
            bin_data.append(struct.pack("<I", size))
            bin_data.append(serialized)
        serialized = b"".join(bin_data)
    file.write(serialized)
    return len(serialized)


def read_bin(file: BinaryIO, *, format: type[msgspec.Struct] | None = None) -> Any:
    chunk = file.read()
    return decode(chunk, format=format)


def read_bin_chunk(
    file: BinaryIO, pos: int = 0, *, format: type[msgspec.Struct] | None = None
) -> tuple[Any, int]:
    file.seek(pos)
    size = struct.unpack("<I", file.read(4))[0]
    chunk = file.read(size)
    return decode(chunk, format=format), size + 4


def read_bin_sized(
    file: BinaryIO,
    pos: int = 0,
    size: int = -1,
    *,
    format: type[msgspec.Struct] | None = None,
) -> Any:
    file.seek(pos)
    if size < 0:
        chunk = file.read()
    else:
        chunk = file.read(size)
    return decode(chunk, format=format)


def decode(encoded: bytes, *, format: type[msgspec.Struct] | None = None) -> Any:
    if format is None:
        return msgspec.msgpack.decode(encoded)
    else:
        return msgspec.msgpack.decode(encoded, type=format)


def read_json(path: str) -> dict[str, str]:
    """extracts html content from file"""
    with open(path, "r") as file:
        return msgspec.json.decode(file.read())

# SPDX-License-Identifier: GPL-3.0-only

"""Read, patch, and re-encode compiled macOS NIBArchive resources."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from nibarchive import NIBArchive, NIBArchiveParser, NIBValueType


@dataclass(frozen=True)
class PatchResult:
    source: Path
    destination: Path
    changes: Tuple[Tuple[str, str], ...]


def encode_varint(value: int) -> bytes:
    """Encode NIBArchive's little-endian varint with a final high bit."""
    if value < 0:
        raise ValueError(f"negative varint: {value}")

    result = bytearray()
    while value > 0x7F:
        result.append(value & 0x7F)
        value >>= 7
    result.append(value | 0x80)
    return bytes(result)


def _encode_value(value) -> bytes:
    value_type = value.type
    if value_type == NIBValueType.NIBARCHIVE:
        payload = encode_archive(value.data)
        return (
            encode_varint(value.key_index)
            + bytes([NIBValueType.DATA.value])
            + encode_varint(len(payload))
            + payload
        )

    prefix = encode_varint(value.key_index) + bytes([value_type.value])
    data = value.data
    if value_type in (
        NIBValueType.BOOL_TRUE,
        NIBValueType.BOOL_FALSE,
        NIBValueType.NIL,
    ):
        return prefix
    if value_type == NIBValueType.INT8:
        return prefix + bytes([data])
    if value_type == NIBValueType.INT16:
        return prefix + struct.pack("<h", data)
    if value_type in (NIBValueType.INT32, NIBValueType.OBJECT_REF):
        return prefix + struct.pack("<i", data)
    if value_type == NIBValueType.INT64:
        return prefix + struct.pack("<q", data)
    if value_type == NIBValueType.FLOAT:
        return prefix + struct.pack("<f", data)
    if value_type == NIBValueType.DOUBLE:
        return prefix + struct.pack("<d", data)
    if value_type == NIBValueType.DATA:
        if isinstance(data, list):
            data = b"\x07" + struct.pack("<" + "d" * len(data), *data)
        return prefix + encode_varint(len(data)) + data
    raise ValueError(f"unsupported NIB value type: {value_type}")


def encode_archive(archive: NIBArchive) -> bytes:
    """Encode a parsed NIBArchive while recalculating every section offset."""
    objects = b"".join(
        encode_varint(obj.class_name_index)
        + encode_varint(obj.values_index)
        + encode_varint(obj.value_count)
        for obj in archive.objects
    )
    keys = b"".join(
        encode_varint(len(key.name.encode("utf-8"))) + key.name.encode("utf-8")
        for key in archive.keys
    )
    values = b"".join(_encode_value(value) for value in archive.values)

    class_name_parts: List[bytes] = []
    for class_name in archive.class_names:
        name = class_name.name.encode("utf-8") + b"\0"
        extras = (
            struct.pack("<" + "i" * len(class_name.extras), *class_name.extras)
            if class_name.extras
            else b""
        )
        class_name_parts.append(
            encode_varint(len(name)) + encode_varint(len(class_name.extras)) + extras + name
        )
    class_names = b"".join(class_name_parts)

    offset_objects = 50
    offset_keys = offset_objects + len(objects)
    offset_values = offset_keys + len(keys)
    offset_class_names = offset_values + len(values)
    header = struct.pack(
        "<10i",
        archive.header.unknown_1,
        archive.header.unknown_2,
        len(archive.objects),
        offset_objects,
        len(archive.keys),
        offset_keys,
        len(archive.values),
        offset_values,
        len(archive.class_names),
        offset_class_names,
    )
    return b"NIBArchive" + header + objects + keys + values + class_names


def patch_nib(
    source: Path,
    destination: Path,
    translations: Dict[str, str],
) -> PatchResult:
    """Patch exact NSString values in one NIB and validate the result."""
    with source.open("rb") as stream:
        archive = NIBArchiveParser().parse(stream)

    changes: List[Tuple[str, str]] = []
    for obj in archive.objects:
        if archive.get_class_name(obj).name != "NSString":
            continue
        for value in archive.get_object_values(obj):
            key = archive.get_value_key(value).name
            if (
                key != "NS.bytes"
                or value.type != NIBValueType.DATA
                or not isinstance(value.data, bytes)
            ):
                continue
            try:
                original = value.data.decode("utf-8")
            except UnicodeDecodeError:
                continue
            translated = translations.get(original)
            if translated and translated != original:
                value.data = translated.encode("utf-8")
                changes.append((original, translated))

    if changes:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(encode_archive(archive))
        with destination.open("rb") as stream:
            NIBArchiveParser().parse(stream)

    return PatchResult(source, destination, tuple(changes))


def patch_resources(
    resources: Path,
    output: Path,
    translations: Dict[str, str],
) -> List[PatchResult]:
    """Patch all changed top-level NIB files in a Ghostty resource folder."""
    results = []
    for source in sorted(resources.glob("*.nib")):
        result = patch_nib(source, output / source.name, translations)
        if result.changes:
            results.append(result)
    return results

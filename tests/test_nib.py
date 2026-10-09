# SPDX-License-Identifier: GPL-3.0-only

import io
import tempfile
import unittest
from pathlib import Path

from nibarchive import (
    ClassName,
    NIBArchive,
    NIBArchiveHeader,
    NIBArchiveParser,
    NIBKey,
    NIBObject,
    NIBValue,
    NIBValueType,
    varint,
)

from ghostty_macos_zh.nib import encode_archive, encode_varint, patch_nib


def string_archive(value: str) -> NIBArchive:
    return NIBArchive(
        header=NIBArchiveHeader(1, 10, 1, 50, 1, 0, 1, 0, 1, 0),
        objects=[NIBObject(0, 0, 1)],
        keys=[NIBKey(len("NS.bytes"), "NS.bytes")],
        values=[NIBValue(0, NIBValueType.DATA, value.encode("utf-8"))],
        class_names=[ClassName(len("NSString") + 1, 0, "NSString")],
    )


class NIBEncodingTests(unittest.TestCase):
    def test_varint_round_trip(self):
        for value in (0, 1, 127, 128, 255, 2677, 65535):
            decoded, count = varint(io.BytesIO(encode_varint(value)))
            self.assertEqual(value, decoded)
            self.assertEqual(len(encode_varint(value)), count)

    def test_archive_round_trip(self):
        archive = string_archive("New Window")
        parsed = NIBArchiveParser().parse(io.BytesIO(encode_archive(archive)))
        self.assertEqual(b"New Window", parsed.values[0].data)
        self.assertEqual("NSString", parsed.class_names[0].name)

    def test_patch_nib(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "MainMenu.nib"
            destination = root / "localized" / "MainMenu.nib"
            source.write_bytes(encode_archive(string_archive("New Window")))

            result = patch_nib(source, destination, {"New Window": "新建窗口"})

            self.assertEqual((("New Window", "新建窗口"),), result.changes)
            with destination.open("rb") as stream:
                parsed = NIBArchiveParser().parse(stream)
            self.assertEqual("新建窗口", parsed.values[0].data.decode("utf-8"))

    def test_unchanged_nib_is_not_written(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "MainMenu.nib"
            destination = root / "localized" / "MainMenu.nib"
            source.write_bytes(encode_archive(string_archive("TechnicalIdentifier")))

            result = patch_nib(source, destination, {"New Window": "新建窗口"})

            self.assertFalse(result.changes)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()

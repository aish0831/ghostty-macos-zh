# SPDX-License-Identifier: GPL-3.0-only

import unittest

from ghostty_macos_zh.translations import MANUAL_TRANSLATIONS


class TranslationTests(unittest.TestCase):
    def test_critical_native_menu_strings_are_covered(self):
        expected = {
            "File": "文件",
            "Edit": "编辑",
            "View": "显示",
            "Window": "窗口",
            "Help": "帮助",
            "Preferences…": "设置…",
        }
        for source, translation in expected.items():
            self.assertEqual(translation, MANUAL_TRANSLATIONS[source])


if __name__ == "__main__":
    unittest.main()

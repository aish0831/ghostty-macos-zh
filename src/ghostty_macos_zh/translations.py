# SPDX-License-Identifier: GPL-3.0-only

"""Translation catalog loading and macOS-specific fallback strings."""

from __future__ import annotations

import gettext
from pathlib import Path
from typing import Dict

# Ghostty's official zh_CN catalog currently targets its GTK frontend. These
# strings fill the native macOS menu labels that are absent from that catalog.
MANUAL_TRANSLATIONS: Dict[str, str] = {
    "About Ghostty": "关于 Ghostty",
    "Bring All to Front": "前置全部窗口",
    "Change Tab Title...": "更改标签页标题…",
    "Change Terminal Title...": "更改终端标题…",
    "Check for Updates...": "检查更新…",
    "Clipboard Confirmation": "剪贴板确认",
    "Close All Windows": "关闭所有窗口",
    "Decrease Font Size": "缩小字体",
    "Edit": "编辑",
    "Equalize Splits": "均分窗格",
    "File": "文件",
    "Find": "查找",
    "Find...": "查找…",
    "Find Next": "查找下一个",
    "Find Previous": "查找上一个",
    "Float on Top": "置于顶层",
    "Ghostty Help": "Ghostty 帮助",
    "Help": "帮助",
    "Hide Find Bar": "隐藏查找栏",
    "Hide Ghostty": "隐藏 Ghostty",
    "Hide Others": "隐藏其他",
    "Increase Font Size": "放大字体",
    "Jump to Selection": "跳到所选内容",
    "Main Menu": "主菜单",
    "Make Ghostty the Default Terminal": "将 Ghostty 设为默认终端",
    "Minimize": "最小化",
    "Move Divider Down": "下移分隔线",
    "Move Divider Left": "左移分隔线",
    "Move Divider Right": "右移分隔线",
    "Move Divider Up": "上移分隔线",
    "Paste Selection": "粘贴所选内容",
    "Preferences": "设置…",
    "Preferences…": "设置…",
    "Quick Terminal": "快速终端",
    "Quit Ghostty": "退出 Ghostty",
    "Redo": "重做",
    "Reset Font Size": "重置字体大小",
    "Resize Split": "调整窗格大小",
    "Return To Default Size": "恢复默认大小",
    "Secure Keyboard Entry": "安全键盘输入",
    "Select All": "全选",
    "Select Next Split": "选择下一个窗格",
    "Select Previous Split": "选择上一个窗格",
    "Select Split": "选择窗格",
    "Select Split Above": "选择上方窗格",
    "Select Split Below": "选择下方窗格",
    "Select Split Left": "选择左侧窗格",
    "Select Split Right": "选择右侧窗格",
    "Services": "服务",
    "Show All": "全部显示",
    "Show/Hide All Terminals": "显示/隐藏所有终端",
    "Terminal Read-only": "终端只读",
    "Toggle Full Screen": "切换全屏",
    "Undo": "撤销",
    "Use as Default": "设为默认",
    "Use Selection for Find": "使用所选内容查找",
    "View": "显示",
    "Window": "窗口",
    "Zoom": "缩放",
    "Zoom Split": "缩放窗格",
}


def load_translations(catalog_path: Path) -> Dict[str, str]:
    """Load Ghostty's bundled zh_CN catalog and add macOS menu strings."""
    with catalog_path.open("rb") as stream:
        catalog = gettext.GNUTranslations(stream)._catalog

    translations = {
        key: value
        for key, value in catalog.items()
        if isinstance(key, str) and key and isinstance(value, str)
    }
    translations.update(MANUAL_TRANSLATIONS)
    return translations

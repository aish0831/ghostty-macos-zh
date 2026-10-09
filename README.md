# Ghostty macOS 简体中文补丁

[English](README.en.md)

这是一个非官方、可审计、仅在本机生成的 Ghostty macOS 简体中文资源补丁。项目不会分发 Ghostty 应用、签名产物、上游 NIB 文件或用户配置。

当前已在 **Ghostty 1.3.1** 上验证。工具复用官方应用自带的 `zh_CN` gettext 词库，并补齐 macOS 原生菜单缺少的中文翻译。

> 本项目与 Ghostty 官方及其维护者无隶属关系。遇到补丁问题请在本仓库反馈，不要向 Ghostty 上游提交由本补丁产生的崩溃报告。

## 能做什么

- 汉化 Ghostty 的 macOS 主菜单、剪贴板确认窗口和配置错误窗口。
- 从用户已经安装的官方 `Ghostty.app` 本地生成独立的 `Ghostty 中文版.app`。
- 使用独立 Bundle ID，可与官方版本同时安装。
- 对生成副本进行本机临时签名，并验证应用包完整性。
- 保持官方 `Ghostty.app` 不变。

目前不保证所有运行时动态界面都已汉化。未包含在 NIB 中、且未接入 Ghostty gettext 的 macOS Swift/AppKit 文本仍可能显示英文。

## 安全边界

生成的应用使用本机临时签名，不再具有 Ghostty 官方 Developer ID 签名。因为临时签名没有 Team ID，构建工具只对生成副本加入 `disable-library-validation` entitlement，使其可以加载同一副本中的 Sparkle 框架。

- 不会关闭 SIP 或 Gatekeeper。
- 不会修改系统级安全设置。
- 不会修改官方 Ghostty 应用。
- 默认验证源应用代码签名及 Ghostty 官方 Team ID `24VZTF6M5V`。
- 不建议分发构建完成的 `.app`；每位用户都应从自己的官方安装本地构建。
- 生成副本会关闭 Sparkle 自动更新。升级官方 Ghostty 后，请使用匹配的新补丁版本重新构建。

## 环境要求

- macOS 13 或更高版本
- 官方 Ghostty 1.3.1，默认位于 `/Applications/Ghostty.app`
- Python 3.9 或更高版本
- Apple Command Line Tools 提供的 `codesign`、`ditto` 和 `plutil`

## 快速开始

```bash
git clone https://github.com/aish0831/ghostty-macos-zh.git
cd ghostty-macos-zh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
ghostty-macos-zh build
```

默认输出：

```text
dist/Ghostty 中文版.app
```

先验证并试运行：

```bash
codesign --verify --deep --strict --verbose=2 'dist/Ghostty 中文版.app'
open -n 'dist/Ghostty 中文版.app'
```

确认无误后，可以在 Finder 中把生成的应用拖入“应用程序”目录。它使用独立 Bundle ID `com.mitchellh.ghostty.zh-cn`，不会替换官方版本。

## 命令

仅生成发生变化的 NIB 资源：

```bash
ghostty-macos-zh generate \
  --app /Applications/Ghostty.app \
  --output dist/resources
```

生成完整独立应用：

```bash
ghostty-macos-zh build \
  --app /Applications/Ghostty.app \
  --output 'dist/Ghostty 中文版.app'
```

工具默认拒绝覆盖已有输出，也拒绝未经验证的 Ghostty 版本或非官方签名源应用。只有在审查过上游 NIB 变化后，才应使用 `--allow-untested-version`。仅当你亲自编译并信任源应用时，才应使用 `--allow-unofficial-source`。

## 实现原理

1. 读取 Ghostty 自带的 `locale/zh_CN/LC_MESSAGES/com.mitchellh.ghostty.mo`。
2. 解析 macOS 编译后的 `NIBArchive`。
3. 只替换精确匹配的 `NSString` 用户界面文本。
4. 重新计算 NIB 各区段偏移并重新编码。
5. 重新解析生成文件，确认结构有效。
6. 复制官方应用，在副本中安装修改后的 NIB。
7. 设置独立 Bundle ID，对副本及嵌套组件进行本机签名并验证。

## 开发

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
ruff check .
python -m unittest discover -s tests -v
```

详细要求见 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [PRIVACY.md](PRIVACY.md)。

## 许可证与上游项目

补丁源码使用 [GPL-3.0-only](LICENSE) 许可证，因为运行时依赖 GPLv3 的 [`nibarchive`](https://pypi.org/project/nibarchive/)。

- Ghostty：MIT 许可证，版权归 Ghostty 贡献者所有。
- Ghostty 官方中文词库：从用户自己的 Ghostty 安装中读取，不在本仓库重新分发。
- `nibarchive`：GPLv3，用于解析 NIBArchive。

更多说明见 [NOTICE](NOTICE) 和 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

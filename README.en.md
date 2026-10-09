# Ghostty macOS Simplified Chinese Patch

[简体中文](README.md)

An unofficial, auditable, local-only Simplified Chinese resource patcher for Ghostty on macOS. The repository does not distribute Ghostty binaries, signed app bundles, upstream NIB files, or user configuration.

The current release is validated against **Ghostty 1.3.1**. It reuses the official `zh_CN` gettext catalog bundled with the user's Ghostty installation and fills the native macOS menu strings that the catalog does not yet cover.

## What it does

- Localizes the macOS main menu, clipboard confirmation window, and configuration error window.
- Builds a separate `Ghostty 中文版.app` from the user's official app.
- Uses a distinct bundle identifier so the localized and official apps can coexist.
- Ad-hoc signs and verifies the generated local copy.
- Leaves the official `Ghostty.app` untouched.

Some dynamic Swift/AppKit strings may remain in English when they are neither stored in NIB resources nor connected to Ghostty's gettext layer.

## Security model

The generated app is ad-hoc signed and no longer carries Ghostty's official Developer ID signature. Ad-hoc code has no Team ID, so the generated copy receives the `disable-library-validation` entitlement solely to load its bundled Sparkle framework.

The tool does not disable SIP or Gatekeeper, change system security settings, or modify the official app. It verifies the source app's code signature and official Ghostty Team ID `24VZTF6M5V` by default. Do not redistribute built app bundles; build locally from an official Ghostty installation instead. Automatic Sparkle updates are disabled in the generated copy.

## Requirements

- macOS 13+
- Official Ghostty 1.3.1 at `/Applications/Ghostty.app`
- Python 3.9+
- Apple Command Line Tools

## Quick start

```bash
git clone https://github.com/aish0831/ghostty-macos-zh.git
cd ghostty-macos-zh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
ghostty-macos-zh build
codesign --verify --deep --strict --verbose=2 'dist/Ghostty 中文版.app'
open -n 'dist/Ghostty 中文版.app'
```

The default output is `dist/Ghostty 中文版.app`. The tool refuses to overwrite existing output and rejects untested Ghostty versions or unofficially signed source apps. Use `--allow-untested-version` only after reviewing upstream NIB changes, and `--allow-unofficial-source` only for a self-built source app you trust.

## Development

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
ruff check .
python -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [PRIVACY.md](PRIVACY.md), [SECURITY.md](SECURITY.md), [NOTICE](NOTICE), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.

## License

Patch source code is licensed under [GPL-3.0-only](LICENSE) because it depends on the GPLv3 `nibarchive` package. Ghostty remains subject to its upstream MIT license and copyrights.

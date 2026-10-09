# Contributing

Thanks for helping improve the project.

## Before opening a change

- Search existing issues and pull requests.
- Keep changes focused on the macOS localization patcher.
- Use consistent Simplified Chinese terminology.
- Do not commit `.app` bundles, compiled NIB files, upstream binaries, credentials, crash reports, or personal configuration.
- Do not add employer, internal organization, corporate email, local path, or automated tool attribution metadata.
- Use a GitHub noreply commit address unless you intentionally want another address to be public.
- Do not report patch-generated crashes to Ghostty upstream unless reproduced with the unmodified official app.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Before submitting:

```bash
ruff check .
ruff format --check src tests
python -m unittest discover -s tests -v
scripts/privacy-audit.sh
```

Changes that add support for a new Ghostty release must document the upstream version, review changed NIB strings, update `SUPPORTED_VERSIONS`, and include test evidence from a locally generated app.

By contributing, you agree that your contribution is licensed under GPL-3.0-only.

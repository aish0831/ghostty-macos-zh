# Security Policy

## Supported versions

Only the latest project release and the Ghostty versions listed in `SUPPORTED_VERSIONS` are supported.

## Reporting a vulnerability

Please use the repository's [private security advisory interface](https://github.com/aish0831/ghostty-macos-zh/security/advisories/new). Do not include private keys, credentials, host definitions, terminal history, or unredacted local paths.

For ordinary build failures and translation mistakes, use the public bug report template instead.

## Trust model

This project produces an ad-hoc signed local derivative of an official Ghostty installation. The builder verifies the source signature and Ghostty Team ID by default. Users should not install prebuilt localized app bundles from third parties.

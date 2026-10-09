# SPDX-License-Identifier: GPL-3.0-only

"""Build a standalone, locally signed Ghostty Simplified Chinese app."""

from __future__ import annotations

import json
import plistlib
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List

from . import __version__
from .nib import PatchResult, patch_resources
from .translations import load_translations

SUPPORTED_VERSIONS = {"1.3.1"}
EXPECTED_TEAM_ID = "24VZTF6M5V"


@dataclass(frozen=True)
class BuildResult:
    output: Path
    upstream_version: str
    replacements: int
    patched_files: int


def _run(args: List[str]) -> None:
    subprocess.run(args, check=True)


def _read_info(app: Path) -> dict:
    with (app / "Contents/Info.plist").open("rb") as stream:
        return plistlib.load(stream)


def app_version(app: Path) -> str:
    return str(_read_info(app)["CFBundleShortVersionString"])


def _source_team_id(app: Path) -> str:
    _run(["codesign", "--verify", "--deep", "--strict", str(app)])
    result = subprocess.run(
        ["codesign", "-d", "--verbose=2", str(app)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("TeamIdentifier="):
            return line.partition("=")[2]
    return ""


def validate_source_app(
    app: Path,
    allow_untested_version: bool = False,
    allow_unofficial_source: bool = False,
) -> str:
    if sys.platform != "darwin":
        raise RuntimeError("building a localized app requires macOS")
    if not (app / "Contents/MacOS/ghostty").is_file():
        raise FileNotFoundError(f"not a Ghostty app bundle: {app}")

    team_id = _source_team_id(app)
    if team_id != EXPECTED_TEAM_ID and not allow_unofficial_source:
        raise RuntimeError(
            f"source app Team ID is {team_id or 'missing'}, expected {EXPECTED_TEAM_ID}. "
            "Refusing a modified or unofficial source; use --allow-unofficial-source "
            "only if you built Ghostty yourself and trust that build."
        )

    version = app_version(app)
    if version not in SUPPORTED_VERSIONS and not allow_untested_version:
        supported = ", ".join(sorted(SUPPORTED_VERSIONS))
        raise RuntimeError(
            f"Ghostty {version} is untested; supported: {supported}. "
            "Pass --allow-untested-version only after reviewing upstream NIB changes."
        )
    return version


def _write_entitlements(path: Path) -> None:
    entitlements = {
        "com.apple.security.automation.apple-events": True,
        "com.apple.security.cs.disable-library-validation": True,
        "com.apple.security.device.audio-input": True,
        "com.apple.security.device.camera": True,
        "com.apple.security.personal-information.addressbook": True,
        "com.apple.security.personal-information.calendars": True,
        "com.apple.security.personal-information.location": True,
        "com.apple.security.personal-information.photos-library": True,
    }
    with path.open("wb") as stream:
        plistlib.dump(entitlements, stream, fmt=plistlib.FMT_XML)


def _patch_info(app: Path, display_name: str, bundle_id: str) -> None:
    info_path = app / "Contents/Info.plist"
    with info_path.open("rb") as stream:
        info = plistlib.load(stream)
    info["CFBundleDisplayName"] = display_name
    info["CFBundleName"] = display_name
    info["CFBundleIdentifier"] = bundle_id
    info["SUEnableAutomaticChecks"] = False
    info["SUAutomaticallyUpdate"] = False
    with info_path.open("wb") as stream:
        plistlib.dump(info, stream, fmt=plistlib.FMT_BINARY, sort_keys=False)


def _sign(app: Path, entitlements: Path) -> None:
    # First normalize all nested code to the same local ad-hoc identity.
    _run(
        [
            "codesign",
            "--force",
            "--deep",
            "--sign",
            "-",
            "--preserve-metadata=entitlements,flags,runtime",
            str(app),
        ]
    )
    # Ad-hoc nested frameworks have no Team ID. The app therefore needs this
    # entitlement to load the bundled Sparkle framework under Hardened Runtime.
    _run(
        [
            "codesign",
            "--force",
            "--sign",
            "-",
            "--options",
            "runtime",
            "--entitlements",
            str(entitlements),
            str(app),
        ]
    )
    _run(["codesign", "--verify", "--deep", "--strict", "--verbose=2", str(app)])


def generate_resources(
    app: Path,
    output: Path,
    allow_untested_version: bool = False,
    allow_unofficial_source: bool = False,
) -> List[PatchResult]:
    validate_source_app(app, allow_untested_version, allow_unofficial_source)
    resources = app / "Contents/Resources"
    catalog = resources / "locale/zh_CN/LC_MESSAGES/com.mitchellh.ghostty.mo"
    if not catalog.is_file():
        raise FileNotFoundError(f"Ghostty zh_CN catalog not found: {catalog}")
    return patch_resources(resources, output, load_translations(catalog))


def build_app(
    source_app: Path,
    output_app: Path,
    display_name: str = "Ghostty 中文版",
    bundle_id: str = "com.mitchellh.ghostty.zh-cn",
    allow_untested_version: bool = False,
    allow_unofficial_source: bool = False,
) -> BuildResult:
    version = validate_source_app(source_app, allow_untested_version, allow_unofficial_source)
    if output_app.exists():
        raise FileExistsError(
            f"refusing to overwrite existing output: {output_app}. "
            "Choose a new path or remove it explicitly."
        )
    output_app.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="ghostty-macos-zh-") as temp:
        temp_root = Path(temp)
        work_app = temp_root / output_app.name
        _run(["ditto", str(source_app), str(work_app)])

        resources = work_app / "Contents/Resources"
        catalog = resources / "locale/zh_CN/LC_MESSAGES/com.mitchellh.ghostty.mo"
        results = patch_resources(resources, resources, load_translations(catalog))
        replacements = sum(len(result.changes) for result in results)
        if not results:
            raise RuntimeError("no translatable NIB strings were found")

        _patch_info(work_app, display_name, bundle_id)
        marker = {
            "project": "ghostty-macos-zh",
            "patch_version": __version__,
            "upstream_version": version,
            "patched_files": [result.source.name for result in results],
            "replacements": replacements,
        }
        (resources / "GhosttyChinesePatch.json").write_text(
            json.dumps(marker, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        entitlements = temp_root / "entitlements.plist"
        _write_entitlements(entitlements)
        _sign(work_app, entitlements)
        _run(["ditto", str(work_app), str(output_app)])
        _run(
            [
                "codesign",
                "--verify",
                "--deep",
                "--strict",
                "--verbose=2",
                str(output_app),
            ]
        )

    return BuildResult(output_app, version, replacements, len(results))

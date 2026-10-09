# SPDX-License-Identifier: GPL-3.0-only

"""Command-line interface."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence

from . import __version__
from .builder import build_app, generate_resources

DEFAULT_APP = Path("/Applications/Ghostty.app")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ghostty-macos-zh",
        description="Build an unofficial Simplified Chinese Ghostty app locally.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser(
        "generate", help="generate only the changed localized NIB resources"
    )
    generate.add_argument("--app", type=Path, default=DEFAULT_APP)
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--allow-untested-version", action="store_true")
    generate.add_argument("--allow-unofficial-source", action="store_true")

    build = subparsers.add_parser("build", help="build and locally sign a standalone localized app")
    build.add_argument("--app", type=Path, default=DEFAULT_APP)
    build.add_argument("--output", type=Path, default=Path("dist/Ghostty 中文版.app"))
    build.add_argument("--display-name", default="Ghostty 中文版")
    build.add_argument("--bundle-id", default="com.mitchellh.ghostty.zh-cn")
    build.add_argument("--allow-untested-version", action="store_true")
    build.add_argument("--allow-unofficial-source", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            results = generate_resources(
                args.app,
                args.output,
                args.allow_untested_version,
                args.allow_unofficial_source,
            )
            replacements = sum(len(result.changes) for result in results)
            print(
                f"Generated {len(results)} localized NIB files "
                f"with {replacements} replacements in {args.output}"
            )
            return 0

        result = build_app(
            source_app=args.app,
            output_app=args.output,
            display_name=args.display_name,
            bundle_id=args.bundle_id,
            allow_untested_version=args.allow_untested_version,
            allow_unofficial_source=args.allow_unofficial_source,
        )
        print(
            f"Built {result.output} from Ghostty {result.upstream_version}: "
            f"{result.replacements} replacements in {result.patched_files} files"
        )
        return 0
    except (
        FileNotFoundError,
        FileExistsError,
        RuntimeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

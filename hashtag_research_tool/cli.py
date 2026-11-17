"""Command-line interface for the Hashtag Research Tool.

Commands:

* ``generate`` — build a balanced hashtag set for a niche + platform
* ``check``    — check a list of hashtags for banned/spammy/problem tags
* ``analyze``  — analyse the hashtags inside a caption
* ``niches``   — list the niches in the built-in database
* ``custom-add`` / ``custom-list`` — manage your own saved hashtags

Examples::

    hashtag-tool generate --niche fitness --platform instagram --count 20
    hashtag-tool generate --niche food --platform tiktok --count 5 --output tags.txt
    hashtag-tool check "#fitness #follow4follow #gym"
    hashtag-tool analyze --file examples/sample_caption.txt
    hashtag-tool niches
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .checker import analyze_caption, check_tags, parse_tags
from .database import PLATFORM_LIMITS, list_niches, tags_for_niche
from .exporter import export_set
from .generator import generate_set
from .user_tags import add_custom_tags, custom_tags_for, list_custom_tags


def _print_report(report: dict) -> None:
    """Print a check/analyse report in plain, readable text."""
    print(f"Tags found: {report['total']} ({report['unique']} unique)")
    if report.get("tier_counts"):
        tiers = report["tier_counts"]
        print(
            "Tier mix: "
            + ", ".join(f"{tier}: {n}" for tier, n in tiers.items() if n)
        )
    if report.get("count_issue"):
        print(f"! {report['count_issue']}")
    bad = [t for t in report["tags"] if t["issues"]]
    if not bad and not report.get("count_issue"):
        print("All tags look good — no problems found.")
    for entry in bad:
        print(f"  {entry['tag']}:")
        for issue in entry["issues"]:
            print(f"    - {issue}")
    print(f"Verdict: {report['verdict']}")


def _cmd_generate(args: argparse.Namespace) -> int:
    extra = custom_tags_for(args.niche)
    if args.extra:
        extra = extra + [t for t in args.extra if t not in extra]
    try:
        result = generate_set(
            args.niche, count=args.count, platform=args.platform, extra_tags=extra
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Hashtag set for {result['niche']} on {result['platform']}:")
    print()
    print(result["copy_paste"])
    print()
    tiers = result["tier_counts"]
    print(
        "Mix: "
        + ", ".join(f"{tier} {n}" for tier, n in tiers.items() if n)
    )
    if args.output:
        fmt = args.format or args.output.rsplit(".", 1)[-1]
        try:
            path = export_set(result, args.output, fmt)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        print(f"Saved to {path}")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    tags = parse_tags(" ".join(args.tags))
    if not tags:
        print("Error: give at least one hashtag to check.", file=sys.stderr)
        return 2
    _print_report(check_tags(tags, args.platform))
    return 0


def _cmd_analyze(args: argparse.Namespace) -> int:
    if args.file:
        text = open(args.file, encoding="utf-8").read()
    else:
        text = args.text or ""
    if not text.strip():
        print("Error: give a caption with --text or --file.", file=sys.stderr)
        return 2
    _print_report(analyze_caption(text, args.platform))
    return 0


def _cmd_niches(_args: argparse.Namespace) -> int:
    print("Available niches (tag count in brackets):")
    for niche in list_niches():
        print(f"  {niche} ({len(tags_for_niche(niche))} tags)")
    return 0


def _cmd_custom_add(args: argparse.Namespace) -> int:
    saved = add_custom_tags(args.niche, args.tags)
    print(f"Saved for {args.niche.lower()}: {', '.join('#' + t for t in saved)}")
    return 0


def _cmd_custom_list(_args: argparse.Namespace) -> int:
    data = list_custom_tags()
    if not data:
        print("No custom hashtags saved yet. Add some with `custom-add`.")
        return 0
    for niche, tags in sorted(data.items()):
        print(f"{niche}: {', '.join('#' + t for t in tags)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hashtag-tool",
        description="Research hashtags, check them for problems, and "
        "export ready-to-paste sets.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Build a balanced hashtag set.")
    gen.add_argument("--niche", required=True, help="Niche, e.g. fitness, food, travel")
    gen.add_argument("--platform", default="instagram",
                     choices=sorted(PLATFORM_LIMITS),
                     help="Platform to optimise for (default: instagram)")
    gen.add_argument("--count", type=int, default=20,
                     help="How many hashtags (default: 20)")
    gen.add_argument("--extra", nargs="*", default=[],
                     help="Extra tags to include first, e.g. #myshop #lahore")
    gen.add_argument("--output", help="Save the set to a file (.txt, .csv or .json)")
    gen.add_argument("--format", choices=["txt", "csv", "json"],
                     help="Export format (defaults to the output file's extension)")
    gen.set_defaults(func=_cmd_generate)

    chk = sub.add_parser("check", help="Check hashtags for banned/spammy tags.")
    chk.add_argument("tags", nargs="+", help="Hashtags to check, e.g. #fitness #gym")
    chk.add_argument("--platform", default="instagram", choices=sorted(PLATFORM_LIMITS))
    chk.set_defaults(func=_cmd_check)

    ana = sub.add_parser("analyze", help="Analyse the hashtags in a caption.")
    ana.add_argument("--text", help="Caption text to analyse")
    ana.add_argument("--file", help="File holding the caption text")
    ana.add_argument("--platform", default="instagram", choices=sorted(PLATFORM_LIMITS))
    ana.set_defaults(func=_cmd_analyze)

    nic = sub.add_parser("niches", help="List the niches in the database.")
    nic.set_defaults(func=_cmd_niches)

    add = sub.add_parser("custom-add", help="Save your own hashtags for a niche.")
    add.add_argument("--niche", required=True)
    add.add_argument("tags", nargs="+")
    add.set_defaults(func=_cmd_custom_add)

    lst = sub.add_parser("custom-list", help="Show your saved custom hashtags.")
    lst.set_defaults(func=_cmd_custom_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

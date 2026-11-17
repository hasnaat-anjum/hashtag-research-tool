"""Check hashtags for problems before you post them.

Checks performed:

* banned or spammy tags (see :data:`database.BANNED_OR_SPAMMY`)
* tags longer than Instagram's 30-character limit
* tags with characters Instagram does not allow (letters, digits and
  underscores only — no spaces, dashes or emoji)
* duplicates (same tag used twice)
* overused generic tags (broad tags with over 50 million posts)
* total count above the platform limit
"""

from __future__ import annotations

import re

from .database import BANNED_OR_SPAMMY, MAX_TAG_LENGTH, PLATFORM_LIMITS, lookup_tag

# A valid Instagram hashtag: letters, digits and underscores only.
_VALID_TAG = re.compile(r"^[A-Za-z0-9_]+$")

# Broad tags with more than this many posts are so crowded that a small
# account's post is unlikely to be seen in them.
OVERUSED_THRESHOLD = 50_000_000


def clean_tag(raw: str) -> str:
    """Normalise one tag: drop a leading '#', trim, lower-case."""
    return raw.strip().lstrip("#").strip().lower()


def parse_tags(text: str) -> list[str]:
    """Pull every hashtag out of free text (caption, comma list, ...)."""
    found = re.findall(r"#([A-Za-z0-9_]+)", text)
    # Also accept plain comma/space separated tags without '#'.
    if not found:
        found = [clean_tag(part) for part in re.split(r"[,\s]+", text) if part]
    return [tag.lower() for tag in found if tag]


def check_tags(tags: list[str], platform: str = "instagram") -> dict:
    """Check a list of tags and return a report dict.

    ``tags`` may include or omit the leading '#'. The report contains
    a per-tag list of issues plus a short verdict: ``ok``, ``warnings``
    or ``problems``.
    """
    platform = platform.lower()
    limit = PLATFORM_LIMITS.get(platform, PLATFORM_LIMITS["instagram"])["limit"]

    cleaned = [clean_tag(tag) for tag in tags if clean_tag(tag)]
    seen: set[str] = set()
    tag_reports: list[dict] = []

    for tag in cleaned:
        issues: list[str] = []
        if tag in BANNED_OR_SPAMMY:
            issues.append("banned or spammy — remove it, it can hide your post")
        if len(tag) > MAX_TAG_LENGTH:
            issues.append(f"too long ({len(tag)} chars; max {MAX_TAG_LENGTH})")
        if not _VALID_TAG.match(tag):
            issues.append("invalid characters (use letters, digits, underscores only)")
        if tag in seen:
            issues.append("duplicate")
        seen.add(tag)

        found = lookup_tag(tag)
        if found and found[1] == "broad" and found[2] >= OVERUSED_THRESHOLD:
            issues.append(
                f"overused ({found[2] / 1_000_000:.0f}M posts) — hard to get seen"
            )
        tag_reports.append({"tag": f"#{tag}", "issues": issues})

    problems = [r for r in tag_reports if r["issues"]]
    count_issue = None
    if len(cleaned) > limit:
        count_issue = (
            f"too many tags: {len(cleaned)} (max {limit} on {platform})"
        )

    if any("banned" in i for r in tag_reports for i in r["issues"]) or count_issue:
        verdict = "problems"
    elif problems:
        verdict = "warnings"
    else:
        verdict = "ok"

    return {
        "platform": platform,
        "total": len(cleaned),
        "unique": len(seen),
        "verdict": verdict,
        "count_issue": count_issue,
        "tags": tag_reports,
        "problem_count": len(problems),
    }


def analyze_caption(text: str, platform: str = "instagram") -> dict:
    """Analyse the hashtags inside a caption and return a report.

    Adds a tier breakdown (broad / medium / niche / unknown) on top of
    the normal tag checks, so you can see whether the caption's mix is
    balanced or all broad tags.
    """
    tags = parse_tags(text)
    report = check_tags(tags, platform)
    tier_counts = {"broad": 0, "medium": 0, "niche": 0, "unknown": 0}
    for tag in set(t.lower() for t in tags):
        found = lookup_tag(tag)
        tier_counts[found[1] if found else "unknown"] += 1
    report["tier_counts"] = tier_counts
    report["caption_tags"] = [f"#{t}" for t in tags]
    return report

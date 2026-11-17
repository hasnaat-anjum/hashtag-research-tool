"""Build balanced hashtag sets from the curated database.

A balanced set mixes reach tiers so a post can be discovered by big
audiences *and* by the small, targeted audiences most likely to engage:

* broad  — 30% of the set (big reach, hard to rank in)
* medium — 40% of the set (the sweet spot for discovery)
* niche  — 30% of the set (small, but highly targeted)

Tags are picked deterministically (sorted, then rotated by a seed) so the
same request always gives the same set — no surprises, easy to test.
"""

from __future__ import annotations

import hashlib

from .database import PLATFORM_LIMITS, lookup_tag, tags_for_niche

# Default mix: share of the set that comes from each tier.
TIER_MIX: dict[str, float] = {"broad": 0.30, "medium": 0.40, "niche": 0.30}


def _seeded_offset(seed_text: str, size: int) -> int:
    """Stable starting offset derived from the request text (0..size-1)."""
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % max(size, 1)


def generate_set(
    niche: str,
    count: int = 20,
    platform: str = "instagram",
    extra_tags: list[str] | None = None,
) -> dict:
    """Generate a balanced hashtag set for a niche and platform.

    Returns a dict with the tags (``#``-prefixed), the per-tier counts,
    the platform, and the niche. Raises ``ValueError`` for an unknown
    niche or platform, or a count outside the platform's limit.
    """
    platform = platform.lower()
    if platform not in PLATFORM_LIMITS:
        raise ValueError(
            f"Unknown platform {platform!r}. Choose from: "
            + ", ".join(sorted(PLATFORM_LIMITS))
        )
    limit = PLATFORM_LIMITS[platform]["limit"]
    if count < 1 or count > limit:
        raise ValueError(
            f"Count must be 1..{limit} for {platform} (you asked for {count})."
        )

    rows = tags_for_niche(niche)
    if not rows:
        raise ValueError(f"Unknown niche {niche!r}. Run `niches` to see the list.")

    # Group the niche's tags by tier, sorted for deterministic output.
    by_tier: dict[str, list[str]] = {"broad": [], "medium": [], "niche": []}
    for tag, tier, _posts in rows:
        by_tier[tier].append(tag)
    for tier in by_tier:
        by_tier[tier].sort()

    # Work out how many tags to take from each tier, then fill any
    # shortfall from the tiers that still have tags left.
    wanted = {
        tier: max(1, round(count * share)) for tier, share in TIER_MIX.items()
    }
    # Fix rounding so the parts add up exactly to `count`.
    while sum(wanted.values()) > count:
        biggest = max(wanted, key=wanted.get)
        wanted[biggest] -= 1
    while sum(wanted.values()) < count:
        smallest = min(wanted, key=wanted.get)
        wanted[smallest] += 1

    chosen: list[str] = []
    for tier in ("broad", "medium", "niche"):
        pool = by_tier[tier]
        take = min(wanted[tier], len(pool))
        start = _seeded_offset(f"{niche}:{tier}:{count}", len(pool))
        for i in range(take):
            chosen.append(pool[(start + i) % len(pool)])

    # Top up from any tier that still has unused tags.
    if len(chosen) < count:
        remaining = [
            tag
            for tier in ("broad", "medium", "niche")
            for tag in by_tier[tier]
            if tag not in chosen
        ]
        chosen.extend(remaining[: count - len(chosen)])

    # User-supplied extra tags go first; duplicates are dropped.
    final: list[str] = []
    for raw in (extra_tags or []):
        tag = raw.lstrip("#").strip().lower()
        if tag and tag not in final:
            final.append(tag)
    for tag in chosen:
        if tag not in final:
            final.append(tag)
    final = final[:count]

    tier_counts = {"broad": 0, "medium": 0, "niche": 0, "custom": 0}
    for tag in final:
        found = lookup_tag(tag)
        tier_counts[found[1] if found else "custom"] += 1

    return {
        "niche": niche.lower(),
        "platform": platform,
        "count": len(final),
        "tags": [f"#{tag}" for tag in final],
        "tier_counts": tier_counts,
        "copy_paste": " ".join(f"#{tag}" for tag in final),
    }

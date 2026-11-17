"""Your own custom hashtags, kept in a small JSON file at home.

Custom tags are added with ``hashtag-tool custom-add`` and are always
offered first when you generate a set for their niche, so your brand
and location tags travel with every post.
"""

from __future__ import annotations

import json
from pathlib import Path

# Kept in the user's home folder so it survives reinstalls of the tool.
STORE_PATH = Path.home() / ".hashtag-research-tool" / "user_tags.json"


def _load() -> dict[str, list[str]]:
    if not STORE_PATH.exists():
        return {}
    try:
        data = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k).lower(): [str(t).lower() for t in v] for k, v in data.items()}


def _save(data: dict[str, list[str]]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def add_custom_tags(niche: str, tags: list[str]) -> list[str]:
    """Add tags to a niche's custom list. Returns the niche's full list."""
    data = _load()
    niche = niche.lower()
    current = data.get(niche, [])
    for raw in tags:
        tag = raw.strip().lstrip("#").strip().lower()
        if tag and tag not in current:
            current.append(tag)
    data[niche] = current
    _save(data)
    return current


def custom_tags_for(niche: str) -> list[str]:
    """Return the custom tags stored for a niche (or [])."""
    return _load().get(niche.lower(), [])


def list_custom_tags() -> dict[str, list[str]]:
    """Return all stored custom tags, grouped by niche."""
    return _load()

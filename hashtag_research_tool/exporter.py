"""Export a generated hashtag set to a file.

Formats:

* ``txt``  — one copy-paste line, ready to paste under a post
* ``csv``  — one tag per row, with tier and post count
* ``json`` — the full generated-set dict, for other tools to read
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .database import lookup_tag


def export_set(result: dict, path: str | Path, fmt: str) -> Path:
    """Write ``result`` (from :func:`generator.generate_set`) to ``path``.

    ``fmt`` is one of ``txt``, ``csv`` or ``json``. Returns the path
    that was written. Raises ``ValueError`` for an unknown format.
    """
    path = Path(path)
    fmt = fmt.lower()
    tags = [tag.lstrip("#") for tag in result["tags"]]

    if fmt == "txt":
        path.write_text(result["copy_paste"] + "\n", encoding="utf-8")
    elif fmt == "csv":
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["hashtag", "tier", "approx_posts"])
            for tag in tags:
                found = lookup_tag(tag)
                tier = found[1] if found else "custom"
                posts = found[2] if found else ""
                writer.writerow([f"#{tag}", tier, posts])
    elif fmt == "json":
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        raise ValueError(f"Unknown format {fmt!r}. Choose txt, csv or json.")
    return path

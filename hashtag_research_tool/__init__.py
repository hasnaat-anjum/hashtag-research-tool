"""Hashtag Research Tool — find, check and export the right hashtags."""

__version__ = "1.0.0"

from .checker import analyze_caption, check_tags, parse_tags
from .database import list_niches
from .exporter import export_set
from .generator import generate_set

__all__ = [
    "__version__",
    "analyze_caption",
    "check_tags",
    "export_set",
    "generate_set",
    "list_niches",
    "parse_tags",
]

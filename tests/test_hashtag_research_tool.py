"""Tests for the Hashtag Research Tool.

Run with:  python -m unittest discover -s tests -v
"""

import csv
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Make the package importable when tests run from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hashtag_research_tool import (  # noqa: E402
    analyze_caption,
    check_tags,
    export_set,
    generate_set,
    list_niches,
    parse_tags,
)
from hashtag_research_tool.database import (  # noqa: E402
    BANNED_OR_SPAMMY,
    PLATFORM_LIMITS,
    tags_for_niche,
)


class TestDatabase(unittest.TestCase):
    def test_niches_exist(self):
        niches = list_niches()
        self.assertGreaterEqual(len(niches), 10)
        for expected in ("fitness", "food", "fashion", "travel", "business"):
            self.assertIn(expected, niches)

    def test_every_niche_has_all_tiers(self):
        for niche in list_niches():
            tiers = {tier for _tag, tier, _posts in tags_for_niche(niche)}
            self.assertEqual(
                tiers, {"broad", "medium", "niche"}, f"{niche} is missing a tier"
            )

    def test_no_duplicate_tags_within_a_niche(self):
        for niche in list_niches():
            tags = [tag for tag, _t, _p in tags_for_niche(niche)]
            self.assertEqual(len(tags), len(set(tags)), f"duplicate in {niche}")

    def test_all_tags_are_valid(self):
        for niche in list_niches():
            for tag, _tier, posts in tags_for_niche(niche):
                self.assertRegex(tag, r"^[a-z0-9_]+$", f"bad tag {tag!r}")
                self.assertLessEqual(len(tag), 30, f"tag too long: {tag!r}")
                self.assertGreater(posts, 0)

    def test_platform_limits_sane(self):
        for platform, limits in PLATFORM_LIMITS.items():
            self.assertLessEqual(limits["recommended"], limits["limit"])


class TestGenerator(unittest.TestCase):
    def test_default_set_has_20_tags(self):
        result = generate_set("fitness")
        self.assertEqual(len(result["tags"]), 20)
        self.assertEqual(result["count"], 20)

    def test_tags_are_unique_and_prefixed(self):
        result = generate_set("food", count=12)
        self.assertEqual(len(result["tags"]), len(set(result["tags"])))
        self.assertTrue(all(tag.startswith("#") for tag in result["tags"]))

    def test_mix_contains_all_tiers(self):
        result = generate_set("travel", count=20)
        counts = result["tier_counts"]
        self.assertGreater(counts["broad"], 0)
        self.assertGreater(counts["medium"], 0)
        self.assertGreater(counts["niche"], 0)

    def test_copy_paste_matches_tags(self):
        result = generate_set("tech", count=10)
        self.assertEqual(result["copy_paste"], " ".join(result["tags"]))

    def test_deterministic(self):
        first = generate_set("fashion", count=15)
        second = generate_set("fashion", count=15)
        self.assertEqual(first["tags"], second["tags"])

    def test_platform_count_respected(self):
        result = generate_set("fitness", count=5, platform="tiktok")
        self.assertEqual(len(result["tags"]), 5)
        result = generate_set("business", count=2, platform="x")
        self.assertEqual(len(result["tags"]), 2)

    def test_unknown_niche_raises(self):
        with self.assertRaises(ValueError):
            generate_set("underwater-basket-weaving")

    def test_count_over_platform_limit_raises(self):
        with self.assertRaises(ValueError):
            generate_set("fitness", count=31, platform="instagram")

    def test_extra_tags_come_first(self):
        result = generate_set("fitness", count=10, extra_tags=["myshop", "lahore"])
        self.assertEqual(result["tags"][0], "#myshop")
        self.assertEqual(result["tags"][1], "#lahore")


class TestChecker(unittest.TestCase):
    def test_clean_set_is_ok(self):
        # Niche/medium tags under the 50M "overused" line: no issues at all.
        report = check_tags(["#homeworkout", "#gymtips", "#beginnerfitness"])
        self.assertEqual(report["verdict"], "ok")
        self.assertEqual(report["problem_count"], 0)

    def test_banned_tag_is_a_problem(self):
        report = check_tags(["#fitness", "#follow4follow"])
        self.assertEqual(report["verdict"], "problems")
        flagged = {t["tag"]: t["issues"] for t in report["tags"] if t["issues"]}
        self.assertIn("#follow4follow", flagged)
        self.assertTrue(any("banned" in i for i in flagged["#follow4follow"]))

    def test_every_banned_tag_is_flagged(self):
        for banned in ("follow4follow", "like4like", "f4f", "freefollowers"):
            report = check_tags([f"#{banned}"])
            self.assertNotEqual(report["verdict"], "ok", banned)

    def test_duplicate_is_flagged(self):
        report = check_tags(["#gym", "#Gym", "#fitness"])
        self.assertEqual(report["unique"], 2)
        self.assertEqual(report["verdict"], "warnings")

    def test_too_many_tags_is_a_problem(self):
        tags = [f"#tag{i}" for i in range(31)]
        report = check_tags(tags, platform="instagram")
        self.assertEqual(report["verdict"], "problems")
        self.assertIsNotNone(report["count_issue"])

    def test_too_long_tag_is_flagged(self):
        report = check_tags(["#" + "a" * 31])
        self.assertEqual(report["verdict"], "warnings")

    def test_parse_tags_from_caption(self):
        tags = parse_tags("Morning run done! #fitness #gymlife feeling great")
        self.assertEqual(tags, ["fitness", "gymlife"])

    def test_analyze_caption_tier_mix(self):
        report = analyze_caption("New drop! #fashion #ootd #capsulewardrobe #style")
        self.assertEqual(report["total"], 4)
        self.assertGreater(report["tier_counts"]["broad"], 0)
        self.assertGreater(report["tier_counts"]["niche"], 0)


class TestExporter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.result = generate_set("food", count=6)

    def tearDown(self):
        self.tmp.cleanup()

    def test_txt_export(self):
        path = export_set(self.result, Path(self.tmp.name) / "tags.txt", "txt")
        self.assertEqual(path.read_text().strip(), self.result["copy_paste"])

    def test_csv_export(self):
        path = export_set(self.result, Path(self.tmp.name) / "tags.csv", "csv")
        with path.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0]["hashtag"], self.result["tags"][0])

    def test_json_export_round_trip(self):
        path = export_set(self.result, Path(self.tmp.name) / "tags.json", "json")
        data = json.loads(path.read_text())
        self.assertEqual(data["tags"], self.result["tags"])

    def test_unknown_format_raises(self):
        with self.assertRaises(ValueError):
            export_set(self.result, Path(self.tmp.name) / "tags.xml", "xml")


class TestCli(unittest.TestCase):
    def test_generate_cli_runs(self):
        from hashtag_research_tool.cli import main

        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out.txt")
            code = main(
                ["generate", "--niche", "fitness", "--count", "5",
                 "--output", out]
            )
            self.assertEqual(code, 0)
            self.assertTrue(Path(out).exists())
            self.assertEqual(len(Path(out).read_text().split()), 5)

    def test_check_cli_flags_banned(self):
        from hashtag_research_tool.cli import main

        code = main(["check", "#fitness", "#follow4follow"])
        self.assertEqual(code, 0)

    def test_unknown_niche_cli_returns_error(self):
        from hashtag_research_tool.cli import main

        code = main(["generate", "--niche", "nope"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()

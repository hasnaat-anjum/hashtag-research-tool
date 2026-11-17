"""Hashtag Research Tool.

Find the right hashtags for your posts, check them for banned or spammy
tags, and export ready-to-paste hashtag sets.

Every hashtag in the built-in database is tagged with a reach tier:

* ``broad``  — over 10 million posts (huge reach, hard to stand out)
* ``medium`` — 1 to 10 million posts (good balance of reach and visibility)
* ``niche``  — under 1 million posts (small audience, but highly targeted)

A good set mixes all three tiers: broad tags bring reach, medium tags
bring discovery, and niche tags bring people who actually care about
your topic. That is exactly what ``generate`` builds for you.

The database ships with curated, real hashtags for 10 popular niches.
Post counts are approximate, rounded figures used only to place each tag
in a tier — they are not live Instagram data.
"""

from __future__ import annotations

# (tag, tier, approximate post count)
# Tags are stored without the leading "#".
NICHE_HASHTAGS: dict[str, list[tuple[str, str, int]]] = {
    "fitness": [
        ("fitness", "broad", 520_000_000),
        ("gym", "broad", 310_000_000),
        ("workout", "broad", 290_000_000),
        ("fit", "broad", 180_000_000),
        ("fitnessmotivation", "medium", 95_000_000),
        ("gymlife", "medium", 88_000_000),
        ("healthylifestyle", "medium", 72_000_000),
        ("strengthtraining", "medium", 21_000_000),
        ("homeworkout", "niche", 9_400_000),
        ("beginnerfitness", "niche", 640_000),
        ("gymtips", "niche", 880_000),
        ("fitnesstrainerlife", "niche", 310_000),
        ("cardio", "broad", 95_000_000),
        ("weightloss", "broad", 120_000_000),
        ("crossfit", "medium", 68_000_000),
        ("yoga", "medium", 98_000_000),
        ("protein", "medium", 44_000_000),
        ("personaltrainer", "niche", 7_200_000),
        ("legday", "niche", 6_800_000),
        ("gymmotivation", "niche", 9_900_000),
    ],
    "food": [
        ("food", "broad", 480_000_000),
        ("foodie", "broad", 260_000_000),
        ("foodporn", "broad", 230_000_000),
        ("instafood", "broad", 210_000_000),
        ("homemade", "medium", 96_000_000),
        ("foodblogger", "medium", 58_000_000),
        ("recipeoftheday", "medium", 12_000_000),
        ("easyrecipes", "medium", 9_800_000),
        ("desifood", "niche", 2_100_000),
        ("streetfoodlove", "niche", 1_400_000),
        ("weeknightdinner", "niche", 940_000),
        ("mealprepsunday", "niche", 720_000),
        ("foodstagram", "broad", 105_000_000),
        ("delicious", "broad", 130_000_000),
        ("baking", "medium", 66_000_000),
        ("veganrecipes", "medium", 8_900_000),
        ("foodlover", "medium", 54_000_000),
        ("pakistanifood", "niche", 1_900_000),
        ("biryani", "niche", 3_300_000),
        ("bbqlover", "niche", 1_100_000),
    ],
    "fashion": [
        ("fashion", "broad", 540_000_000),
        ("style", "broad", 430_000_000),
        ("ootd", "broad", 380_000_000),
        ("fashionblogger", "broad", 120_000_000),
        ("streetstyle", "medium", 98_000_000),
        ("outfitinspo", "medium", 34_000_000),
        ("fashionista", "medium", 27_000_000),
        ("mensfashion", "medium", 19_000_000),
        ("capsulewardrobe", "niche", 3_200_000),
        ("thriftedstyle", "niche", 1_900_000),
        ("modestfashion", "niche", 8_700_000),
        ("ootdstyle", "niche", 6_100_000),
        ("fashionstyle", "broad", 96_000_000),
        ("styleinspo", "medium", 21_000_000),
        ("winterfashion", "medium", 7_600_000),
        ("outfitoftheday", "medium", 68_000_000),
        ("shoplocal", "medium", 18_000_000),
        ("kurti", "niche", 2_400_000),
        ("easternwear", "niche", 980_000),
        ("fashiontips", "niche", 4_500_000),
    ],
    "beauty": [
        ("beauty", "broad", 460_000_000),
        ("makeup", "broad", 380_000_000),
        ("skincare", "broad", 150_000_000),
        ("makeupartist", "broad", 130_000_000),
        ("glowingskin", "medium", 28_000_000),
        ("beautytips", "medium", 24_000_000),
        ("selfcare", "medium", 95_000_000),
        ("haircare", "medium", 41_000_000),
        ("glassskin", "niche", 4_600_000),
        ("makeuptutorial", "niche", 9_100_000),
        ("skincareroutine", "niche", 7_800_000),
        ("naturalmakeup", "niche", 6_400_000),
        ("skincaretips", "medium", 11_000_000),
        ("beautyproducts", "medium", 16_000_000),
        ("nails", "medium", 74_000_000),
        ("hair", "broad", 190_000_000),
        ("lipstick", "medium", 23_000_000),
        ("mehndi", "niche", 6_700_000),
        ("bridalmakeup", "niche", 5_100_000),
        ("skincareproducts", "niche", 3_800_000),
    ],
    "travel": [
        ("travel", "broad", 610_000_000),
        ("wanderlust", "broad", 140_000_000),
        ("travelphotography", "broad", 120_000_000),
        ("vacation", "broad", 110_000_000),
        ("travelblogger", "medium", 42_000_000),
        ("backpacking", "medium", 11_000_000),
        ("solotravel", "medium", 9_300_000),
        ("travelgram", "medium", 63_000_000),
        ("budgettravel", "niche", 5_800_000),
        ("hiddenplaces", "niche", 1_200_000),
        ("mountainlife", "niche", 8_900_000),
        ("traveldiaries", "niche", 4_700_000),
        ("traveler", "broad", 98_000_000),
        ("adventure", "broad", 160_000_000),
        ("nature", "broad", 340_000_000),
        ("roadtrip", "medium", 33_000_000),
        ("beachlife", "medium", 27_000_000),
        ("northernareas", "niche", 640_000),
        ("hunza", "niche", 1_300_000),
        ("travelphotographer", "niche", 7_100_000),
    ],
    "tech": [
        ("technology", "broad", 130_000_000),
        ("tech", "broad", 120_000_000),
        ("gadgets", "broad", 45_000_000),
        ("ai", "broad", 110_000_000),
        ("coding", "medium", 38_000_000),
        ("programming", "medium", 29_000_000),
        ("webdevelopment", "medium", 8_400_000),
        ("machinelearning", "medium", 12_000_000),
        ("pythonprogramming", "niche", 2_300_000),
        ("learntocode", "niche", 4_100_000),
        ("techstartup", "niche", 1_800_000),
        ("aitools", "niche", 3_900_000),
        ("innovation", "broad", 64_000_000),
        ("software", "broad", 58_000_000),
        ("developer", "medium", 31_000_000),
        ("datascience", "medium", 14_000_000),
        ("cybersecurity", "medium", 9_200_000),
        ("javascript", "niche", 8_800_000),
        ("webdesign", "niche", 9_400_000),
        ("aiautomation", "niche", 1_700_000),
    ],
    "business": [
        ("business", "broad", 180_000_000),
        ("entrepreneur", "broad", 140_000_000),
        ("motivation", "broad", 320_000_000),
        ("success", "broad", 210_000_000),
        ("smallbusiness", "medium", 68_000_000),
        ("entrepreneurship", "medium", 54_000_000),
        ("businessowner", "medium", 22_000_000),
        ("startup", "medium", 47_000_000),
        ("sidehustle", "niche", 9_600_000),
        ("freelancelife", "niche", 3_400_000),
        ("onlineshop", "niche", 8_200_000),
        ("smallbizowner", "niche", 2_700_000),
        ("marketing", "broad", 150_000_000),
        ("money", "broad", 120_000_000),
        ("digitalmarketing", "medium", 41_000_000),
        ("branding", "medium", 36_000_000),
        ("ecommerce", "medium", 27_000_000),
        ("workfromhome", "niche", 9_200_000),
        ("dropshipping", "niche", 6_900_000),
        ("reseller", "niche", 2_200_000),
    ],
    "education": [
        ("education", "broad", 95_000_000),
        ("learning", "broad", 110_000_000),
        ("study", "broad", 88_000_000),
        ("studentlife", "broad", 42_000_000),
        ("studytips", "medium", 6_800_000),
        ("onlinelearning", "medium", 9_100_000),
        ("studygram", "medium", 12_000_000),
        ("educationmatters", "medium", 3_100_000),
        ("studymotivation", "niche", 7_400_000),
        ("learnenglish", "niche", 5_200_000),
        ("examseason", "niche", 1_600_000),
        ("csspreparation", "niche", 240_000),
        ("knowledge", "broad", 78_000_000),
        ("school", "broad", 110_000_000),
        ("teacher", "medium", 38_000_000),
        ("studyabroad", "medium", 7_900_000),
        ("englishlearning", "medium", 4_600_000),
        ("onlinetutor", "niche", 1_100_000),
        ("studynotes", "niche", 2_800_000),
        ("matric", "niche", 310_000),
    ],
    "photography": [
        ("photography", "broad", 620_000_000),
        ("photooftheday", "broad", 390_000_000),
        ("photographer", "broad", 180_000_000),
        ("portrait", "broad", 210_000_000),
        ("streetphotography", "medium", 52_000_000),
        ("landscapephotography", "medium", 24_000_000),
        ("naturephotography", "medium", 47_000_000),
        ("goldenhour", "medium", 38_000_000),
        ("mobilephotography", "niche", 9_800_000),
        ("portraitphotography", "niche", 8_600_000),
        ("photoediting", "niche", 4_300_000),
        ("beginnerphotographer", "niche", 1_100_000),
        ("photo", "broad", 410_000_000),
        ("instaphoto", "broad", 96_000_000),
        ("weddingphotography", "medium", 19_000_000),
        ("cameralife", "medium", 6_700_000),
        ("photoshoot", "medium", 28_000_000),
        ("dslr", "niche", 8_100_000),
        ("lightroom", "niche", 5_600_000),
        ("photographylovers", "niche", 4_900_000),
    ],
    "music": [
        ("music", "broad", 420_000_000),
        ("musician", "broad", 110_000_000),
        ("singer", "broad", 95_000_000),
        ("newmusic", "broad", 88_000_000),
        ("livemusic", "medium", 31_000_000),
        ("musicproducer", "medium", 14_000_000),
        ("songwriter", "medium", 9_700_000),
        ("guitarist", "medium", 11_000_000),
        ("indiemusic", "niche", 6_200_000),
        ("musiccover", "niche", 5_400_000),
        ("bedroomproducer", "niche", 980_000),
        ("newartist", "niche", 4_800_000),
        ("songs", "broad", 130_000_000),
        ("singersongwriter", "medium", 6_300_000),
        ("concert", "medium", 42_000_000),
        ("playlist", "medium", 18_000_000),
        ("rap", "medium", 33_000_000),
        ("qawwali", "niche", 420_000),
        ("cokestudio", "niche", 1_800_000),
        ("ghazal", "niche", 380_000),
        ("musiclife", "niche", 7_900_000),
    ],
}

# Hashtags Instagram has banned at some point, or that mark a post as spam.
# Using them can hide your post from search or hurt your reach.
BANNED_OR_SPAMMY: set[str] = {
    # Banned / restricted on Instagram (known cases).
    "adulting", "babe", "beautyblogger", "desk", "dm", "dogsofinstagram",
    "elevator", "hardworkpaysoff", "instagood", "like", "master",
    "models", "newyearsday", "popular", "pushups", "snapchat",
    "tagforlikes", "tgif", "todayimwearing", "valentinesday",
    # Spam / engagement-bait tags. They attract bots, not customers.
    "follow4follow", "followforfollow", "f4f", "like4like", "l4l",
    "likeforlike", "followme", "followback", "instafollow",
    "followforfollowback", "freefollowers", "gainfollowers",
    "followtrain", "likesforlikes", "comment4comment", "shoutout4shoutout",
}

# Platform guidance: recommended tag count and hard limit.
# "recommended" is the sweet spot marketers use; "limit" is the platform cap.
PLATFORM_LIMITS: dict[str, dict[str, int]] = {
    "instagram": {"recommended": 20, "limit": 30},
    "tiktok": {"recommended": 5, "limit": 100},
    "linkedin": {"recommended": 4, "limit": 30},
    "x": {"recommended": 2, "limit": 10},
    "facebook": {"recommended": 4, "limit": 30},
}

# Instagram allows at most 30 characters in a single hashtag.
MAX_TAG_LENGTH = 30


def list_niches() -> list[str]:
    """Return the niche names in the built-in database, sorted."""
    return sorted(NICHE_HASHTAGS)


def tags_for_niche(niche: str) -> list[tuple[str, str, int]]:
    """Return the (tag, tier, posts) rows for a niche, or [] if unknown."""
    return list(NICHE_HASHTAGS.get(niche.lower(), []))


def lookup_tag(tag: str) -> tuple[str, str, int] | None:
    """Look a tag up in the database (without the leading "#").

    Returns ``(tag, tier, posts)`` or ``None`` when the tag is not known.
    """
    clean = tag.lstrip("#").lower()
    for rows in NICHE_HASHTAGS.values():
        for row in rows:
            if row[0] == clean:
                return row
    return None

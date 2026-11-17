# Hashtag Research Tool

Find the right hashtags for your posts, check them for banned or spammy tags, and export ready-to-paste hashtag sets — no account, no API key, no internet needed.

## What it does

Posting with the wrong hashtags is the fastest way to get ignored: huge tags like `#fitness` (520M posts) bury a small account, and banned or spammy tags like `#follow4follow` can hide a post from search entirely. This tool fixes that in seconds:

- **Generate balanced hashtag sets** — a mix of broad (reach), medium (discovery) and niche (targeted) tags for your niche and platform, so your post can actually be found.
- **Check any hashtags** — flags banned/spammy tags, duplicates, tags over 30 characters, invalid characters, and overused tags with 50M+ posts.
- **Analyse a caption** — pulls the hashtags out of your caption and shows the tier mix, so you can see at a glance whether it is balanced or all broad tags.
- **Save your own tags** — your brand and location tags (e.g. `#myshop`, `#lahore`) are stored once and added to every set you generate.
- **Export** — copy-paste `.txt`, spreadsheet `.csv`, or `.json`.

## Who it helps

- **Freelancers and small business owners** promoting their work on Instagram, TikTok, LinkedIn, X or Facebook.
- **Social media marketers** who plan posts for clients and need a fast, repeatable hashtag workflow.
- **Creators** who want more reach without paying for tools or guessing at tags.

## Installation

Requires Python 3.10 or newer. No third-party dependencies — the standard library only.

```bash
git clone https://github.com/hasnaat-anjum/hashtag-research-tool.git
cd hashtag-research-tool
pip install -e .
```

Or run it without installing:

```bash
python -m hashtag_research_tool generate --niche fitness
```

## How to use

### Generate a hashtag set

```bash
hashtag-tool generate --niche fitness --platform instagram --count 20
hashtag-tool generate --niche food --platform tiktok --count 5
hashtag-tool generate --niche business --platform linkedin --count 4
```

Add your own tags first, and save the set to a file:

```bash
hashtag-tool generate --niche travel --extra "#mytravelblog #pakistan" --output my-tags.txt
hashtag-tool generate --niche fashion --output tags.csv --format csv
```

### Check hashtags before you post

```bash
hashtag-tool check "#fitness #follow4follow #gym"
```

```
Tags found: 3 (3 unique)
  #fitness:
    - overused (520M posts) — hard to get seen
  #follow4follow:
    - banned or spammy — remove it, it can hide your post
  #gym:
    - overused (310M posts) — hard to get seen
Verdict: problems
```

### Analyse a caption

```bash
hashtag-tool analyze --text "Morning run done! #fitness #gymlife #homeworkout"
hashtag-tool analyze --file my-caption.txt
```

### List niches and manage your own tags

```bash
hashtag-tool niches
hashtag-tool custom-add --niche fitness "#myshop" "#lahore"
hashtag-tool custom-list
```

## Niches included

10 niches, 20+ curated hashtags each: `fitness`, `food`, `fashion`, `beauty`, `travel`, `tech`, `business`, `education`, `photography`, `music`.

Post counts in the database are approximate, rounded figures used only to place each tag in a reach tier — they are not live Instagram data.

## Platform guidance

| Platform  | Recommended tags | Max tags |
|-----------|-----------------|----------|
| Instagram | 20              | 30       |
| TikTok    | 5               | 100      |
| LinkedIn  | 4               | 30       |
| X         | 2               | 10       |
| Facebook  | 4               | 30       |

## Features

- Balanced broad / medium / niche mix (30% / 40% / 30%)
- Banned and spammy hashtag detection (40+ known tags)
- Duplicate, length and invalid-character checks
- Overused-tag warnings (50M+ posts)
- Caption analysis with tier breakdown
- Custom hashtags saved per niche (`~/.hashtag-research-tool/user_tags.json`)
- Export to `.txt`, `.csv`, `.json`
- Deterministic output — the same request always gives the same set
- Works fully offline, standard library only

## Project structure

```
hashtag-research-tool/
├── hashtag_research_tool/
│   ├── __init__.py       # public API
│   ├── __main__.py       # `python -m hashtag_research_tool`
│   ├── cli.py            # command-line interface
│   ├── database.py       # curated hashtag database + platform limits
│   ├── generator.py      # balanced set builder
│   ├── checker.py        # tag checks + caption analysis
│   ├── exporter.py       # txt / csv / json export
│   └── user_tags.py      # your saved custom hashtags
├── tests/
│   └── test_hashtag_research_tool.py   # 29 tests
├── examples/
│   ├── sample_caption.txt   # caption used in the demo
│   ├── sample_output.txt    # a generated food set (Instagram, 20 tags)
│   └── sample_tags.csv      # a generated fitness set (TikTok, 5 tags)
├── README.md
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

## Tests

```bash
python -m unittest discover -s tests -v
```

29 tests, covering the database, the generator (counts, mix, determinism, platform limits), the checker (banned tags, duplicates, limits, caption analysis), the exporter (all three formats) and the CLI.

## Demo

```bash
# A balanced 20-tag set for a fitness post on Instagram
python -m hashtag_research_tool generate --niche fitness --platform instagram --count 20

# Check a caption before posting it
python -m hashtag_research_tool analyze --file examples/sample_caption.txt
```

## Technologies

Python 3.10+, standard library only (argparse, csv, json, hashlib, re, pathlib). No external packages, no API keys, no network calls.

## License

MIT — see [LICENSE](LICENSE).

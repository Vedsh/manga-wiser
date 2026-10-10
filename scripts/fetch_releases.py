import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

RSS_URL = "https://www.mangaupdates.com/rss"
CATALOG_FILE = Path("data/anilist-catalog.json")
OUTPUT_FILE = Path("data/latest-releases.json")


def fetch_url(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "MangaWiser/1.0",
            "Accept": "application/rss+xml, application/xml, text/xml",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def clean_html(value):
    value = unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(value.split())


def get_release_type(title):
    has_volume = re.search(r"\bv\.?\s*\d+", title, re.I)
    has_chapter = re.search(r"\bc\.?\s*\d+", title, re.I)

    if has_volume and has_chapter:
        return "Volume + Chapter"
    if has_volume:
        return "Volume"
    if has_chapter:
        return "Chapter"
    return "Other"


def main():
    print("Fetching MangaUpdates releases...")
    root = ET.fromstring(fetch_url(RSS_URL))
    items = root.findall(".//item")

    try:
        catalog = json.loads(
            CATALOG_FILE.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        catalog = {"categories": {}}

    # Build a lookup from the existing AniList catalog.
    catalog_lookup = {}

    for category, entries in catalog.get("categories", {}).items():
        for entry in entries:
            for title in entry.get("title", {}).values():
                if title:
                    catalog_lookup[title.strip().casefold()] = {
                        "category": category,
                        "coverImage": entry.get("coverImage", {}),
                        "siteUrl": entry.get("siteUrl", ""),
                    }

    releases = []
    seen = set()

    for item in items:
        raw_title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        description = item.findtext("description", default="")

        if not raw_title or not link:
            continue

        # Extract the series title after the scanlation group.
        series_title = re.sub(r"^\[[^\]]*\]\s*", "", raw_title)
        series_title = re.sub(
            r"\s+(?:v\.?\s*\d+)?\s*c\.?\s*\d+.*$",
            "",
            series_title,
            flags=re.I,
        ).strip()

        if link in seen:
            continue
        seen.add(link)

        date_match = re.search(
            r"\b\d{4}-\d{2}-\d{2}\b", description
        )
        release_date = date_match.group(0) if date_match else ""

        matched = catalog_lookup.get(series_title.casefold(), {})

        releases.append({
            "title": raw_title,
            "seriesTitle": series_title,
            "releaseType": get_release_type(raw_title),
            "date": release_date,
            "link": link,
            "category": matched.get("category", "unknown"),
            "coverImage": matched.get("coverImage", {}),
            "siteUrl": matched.get("siteUrl", ""),
            "source": "MangaUpdates",
        })

    data = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "MangaUpdates RSS",
        "count": len(releases),
        "releases": releases,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Saved {len(releases)} releases to {OUTPUT_FILE}")
    print("Release types:", {
        kind: sum(r["releaseType"] == kind for r in releases)
        for kind in ("Chapter", "Volume", "Volume + Chapter", "Other")
    })
    print("Catalog matches:", sum(
        r["category"] != "unknown" for r in releases
    ))


if __name__ == "__main__":
    main()

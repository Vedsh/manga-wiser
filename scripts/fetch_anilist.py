
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://graphql.anilist.co"
OUTPUT_FILE = Path("data/anilist-catalog.json")

QUERY = """
query ($page: Int, $country: CountryCode, $format: MediaFormat) {
  Page(page: $page, perPage: 25) {
    media(
      type: MANGA
      countryOfOrigin: $country
      format: $format
      sort: POPULARITY_DESC
    ) {
      id
      title {
        romaji
        english
        native
      }
      description(asHtml: false)
      coverImage {
        large
        extraLarge
      }
      genres
      status
      format
      countryOfOrigin
      startDate {
        year
        month
        day
      }
      chapters
      volumes
      averageScore
      siteUrl
    }
  }
}
"""

CATEGORIES = {
    "manga": [("JP", "MANGA")],
    "manhwa": [("KR", "MANGA")],
    "manhua": [("CN", "MANGA")],
    "novel": [
        ("JP", "NOVEL"),
        ("KR", "NOVEL"),
        ("CN", "NOVEL"),
    ],
    "oneshot": [
        ("JP", "ONE_SHOT"),
        ("KR", "ONE_SHOT"),
        ("CN", "ONE_SHOT"),
    ],
}


def fetch_page(country_code, media_format):
    payload = {
        "query": QUERY,
        "variables": {
            "page": 1,
            "country": country_code,
            "format": media_format,
        },
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "MangaWiser/1.0",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    if "errors" in result:
        raise RuntimeError(
            json.dumps(result["errors"], ensure_ascii=False)
        )

    return result["data"]["Page"]["media"]


def main():
    catalog = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "AniList",
        "test_batch": True,
        "categories": {},
    }

    for category, searches in CATEGORIES.items():
        print(f"Fetching {category}...")
        items_by_id = {}

        for country_code, media_format in searches:
            print(f"  Country: {country_code}, Format: {media_format}")

            items = fetch_page(country_code, media_format)

            for item in items:
                items_by_id[item["id"]] = item

            print(f"  Fetched {len(items)} titles.")
            time.sleep(2)

        catalog["categories"][category] = list(items_by_id.values())
        print(
            f"Total {category} titles: "
            f"{len(catalog['categories'][category])}"
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    total = sum(
        len(items) for items in catalog["categories"].values()
    )

    print(f"Success! Saved {total} titles to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

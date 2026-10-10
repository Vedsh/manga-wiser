
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://graphql.anilist.co"
OUTPUT_FILE = Path("data/anilist-catalog.json")

QUERY = """
query ($page: Int, $country: CountryCode) {
  Page(page: $page, perPage: 25) {
    pageInfo {
      currentPage
      hasNextPage
    }
    media(
      type: MANGA
      countryOfOrigin: $country
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
    "manga": "JP",
    "manhwa": "KR",
    "manhua": "CN",
}


def fetch_page(country_code):
    payload = {
        "query": QUERY,
        "variables": {
            "page": 1,
            "country": country_code,
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

    return result["data"]["Page"]


def main():
    catalog = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "AniList",
        "test_batch": True,
        "categories": {},
    }

    for category, country_code in CATEGORIES.items():
        print(f"Fetching {category} ({country_code})...")

        try:
            page_data = fetch_page(country_code)
            catalog["categories"][category] = page_data["media"]
            print(
                f"Fetched {len(page_data['media'])} {category} titles."
            )
        except Exception as error:
            print(f"Could not fetch {category}: {error}")
            raise

        time.sleep(2)

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

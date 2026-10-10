import urllib.request
import xml.etree.ElementTree as ET

RSS_URL = "https://www.mangaupdates.com/rss"


def main():
    print("Checking MangaUpdates RSS feed...")

    request = urllib.request.Request(
        RSS_URL,
        headers={
            "User-Agent": "MangaWiser/1.0",
            "Accept": "application/rss+xml, application/xml, text/xml",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()
            print("HTTP status:", response.status)

        root = ET.fromstring(content)
        items = root.findall(".//item")

        if not items:
            print("No RSS items found.")
            print("Root element:", root.tag)
            print("Response preview:", content[:500].decode(
                "utf-8", errors="replace"
            ))
            return

        print(f"Found {len(items)} RSS entries.\n")

        for number, item in enumerate(items[:10], start=1):
            title = item.findtext("title", default="No title")
            link = item.findtext("link", default="No link")
            description = item.findtext(
                "description", default="No description"
            )

            print(f"Entry {number}")
            print("Title:", title)
            print("Link:", link)
            print("Description:", description)
            print("-" * 50)

    except Exception as error:
        print("RSS test failed:", repr(error))


if __name__ == "__main__":
    main()

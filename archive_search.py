
import requests

ARCHIVE_API = "https://archive.org/advancedsearch.php"
ARCHIVE_DETAILS = "https://archive.org/details/"

DEFAULT_LIMIT = 25
MAX_LIMIT = 500
REQUEST_TIMEOUT = 15


def search_texts(keyword, limit=DEFAULT_LIMIT):
    """
    Search Internet Archive for text-based media.

    Returns a list of dictionaries containing:
    title, identifier, description, downloads, mediatype, and url.
    """

    keyword = str(keyword).strip()

    if not keyword:
        raise ValueError("Search keyword cannot be empty.")

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        raise ValueError("Result limit must be a number.")

    if limit < 1 or limit > MAX_LIMIT:
        raise ValueError(f"Result limit must be between 1 and {MAX_LIMIT}.")

    params = {
        "q": f"({keyword}) AND mediatype:texts",
        "fl[]": [
            "identifier",
            "title",
            "description",
            "mediatype",
            "downloads"
        ],
        "rows": limit,
        "page": 1,
        "sort[]": "downloads desc",
        "output": "json"
    }

    try:
        response = requests.get(
            ARCHIVE_API,
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException as error:
        raise ConnectionError(
            f"Internet Archive request failed: {error}"
        ) from error

    except ValueError as error:
        raise ValueError(
            "Internet Archive returned invalid JSON."
        ) from error

    try:
        documents = data["response"]["docs"]
    except (KeyError, TypeError):
        raise ValueError("Unexpected Internet Archive response format.")

    results = []

    for item in documents:
        identifier = item.get("identifier")

        if not identifier:
            continue

        results.append({
            "title": item.get("title", "Untitled"),
            "identifier": identifier,
            "description": item.get("description", ""),
            "mediatype": item.get("mediatype", "texts"),
            "downloads": item.get("downloads", 0),
            "url": f"{ARCHIVE_DETAILS}{identifier}"
        })

    return results


def display_results(results):
    """Display search results in the terminal."""

    if not results:
        print("\nNo results found.")
        return

    print(f"\nFound {len(results)} results:\n")

    for index, item in enumerate(results, start=1):
        print(f"[{index}] {item['title']}")
        print(f"Identifier: {item['identifier']}")
        print(f"Downloads: {item['downloads']}")
        print(f"Link: {item['url']}")
        print("-" * 60)


def main():
    """Standalone terminal interface for testing the search engine."""

    print("=== VSTG ARCHIVE ENGINE ===")

    keyword = input("Search keyword: ").strip()
    limit = input(f"Result count (default {DEFAULT_LIMIT}): ").strip()

    if not limit:
        limit = DEFAULT_LIMIT

    try:
        results = search_texts(keyword, limit)
        display_results(results)

    except (ValueError, ConnectionError) as error:
        print(f"\n[ARCHIVE ERROR] {error}")

    print("\n=== ARCHIVE ENGINE CLOSED ===")


if __name__ == "__main__":
    main()

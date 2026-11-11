import requests

print("=== ADVANCED ARCHIVE SEARCH ===")

keyword = input("Keyword: ")
rows = input("How many results? (default 50): ")

if rows == "":
    rows = 50

base_url = "https://archive.org/advancedsearch.php"

# Better search query
query = f'({keyword}) OR title:({keyword}) OR description:({keyword})'

params = {
    "q": query,
    "fl[]": [
        "identifier",
        "title",
        "description",
        "mediatype"
    ],
    "rows": rows,
    "page": 1,
    "sort[]": "downloads desc",
    "output": "json"
}

response = requests.get(base_url, params=params)

data = response.json()

results = data["response"]["docs"]
filtered_results = []

for item in results:

    media = str(item.get("mediatype", "")).lower()

    if media == "texts":
        filtered_results.append(item)

results = filtered_results

if not results:
    print("\nNo results found.")

else:
    print(f"\nFound {len(results)} results:\n")

    for i, item in enumerate(results):

        title = item.get("title", "No Title")
        identifier = item.get("identifier", "Unknown")
        media = item.get("mediatype", "unknown")

        link = f"https://archive.org/details/{identifier}"

        print(f"[{i+1}] {title}")
        print(f"Type: {media}")
        print(f"Link: {link}")
        print("-" * 60)

print("=== TEXT ARCHIVE SEARCH ===")

keyword = input("Keyword: ")
rows = input("How many results? (default 50): ")

if rows == "":
    rows = 50

base_url = "https://archive.org/advancedsearch.php"

# Search only text-based media
query = f'''
({keyword})
AND mediatype:texts
AND NOT mediatype:movies
AND NOT mediatype:audio
AND NOT mediatype:web
'''

params = {
    "q": query,
    "fl[]": [
        "identifier",
        "title",
        "description"
    ],
    "rows": rows,
    "page": 1,
    "sort[]": "downloads desc",
    "output": "json"
}

response = requests.get(base_url, params=params)

data = response.json()

results = data["response"]["docs"]

if not results:
    print("\nNo results found.")

else:
    print(f"\nFound {len(results)} text results:\n")

    for i, item in enumerate(results):

        title = item.get("title", "No Title")
        identifier = item.get("identifier", "Unknown")

        link = f"https://archive.org/details/{identifier}"

        print(f"[{i+1}] {title}")
        print(f"Link: {link}")
        print("-" * 60)
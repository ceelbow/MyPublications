"""Fetch an author's works from OpenAlex by ORCID.

Usage: python3 -X utf8 fetch_papers.py <orcid> [output_prefix]

Writes:
  <prefix>.json - full works data (venue, year, type, link, citations by year)
  <prefix>.csv  - title, year, venue, type, co-authors, for a manual check
"""
import csv
import json
import sys
import time
import urllib.request
import urllib.error

API = "https://api.openalex.org/works"


def fetch_all(orcid, mailto="celbon2@uw.edu"):
    works = []
    cursor = "*"
    while cursor:
        url = (
            f"{API}?filter=author.orcid:{orcid}&per-page=200"
            f"&cursor={cursor}&mailto={mailto}"
        )
        for attempt in range(5):
            try:
                with urllib.request.urlopen(url) as resp:
                    data = json.load(resp)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 4:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise
        works.extend(data["results"])
        cursor = data["meta"].get("next_cursor")
    return works


def simplify(work):
    venue = None
    loc = work.get("primary_location") or {}
    source = loc.get("source") or {}
    venue = source.get("display_name")

    co_authors = [
        a["author"]["display_name"]
        for a in work.get("authorships", [])
    ]

    counts_by_year = {
        str(c["year"]): c["cited_by_count"]
        for c in work.get("counts_by_year", [])
    }

    return {
        "title": work.get("title"),
        "year": work.get("publication_year"),
        "venue": venue,
        "type": work.get("type"),
        "doi": work.get("doi"),
        "cited_by_count": work.get("cited_by_count"),
        "counts_by_year": counts_by_year,
        "co_authors": co_authors,
    }


def load_exclusions(path="exclusions.json"):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"exclude_types": [], "exclude_titles": []}


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_papers.py <orcid> [output_prefix]")
        sys.exit(1)
    orcid = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else "papers"

    exclusions = load_exclusions()
    exclude_types = set(exclusions.get("exclude_types", []))
    exclude_titles = set(exclusions.get("exclude_titles", []))

    raw = fetch_all(orcid)
    works = [simplify(w) for w in raw]
    works = [
        w for w in works
        if w["type"] not in exclude_types and w["title"] not in exclude_titles
    ]
    works.sort(key=lambda w: (w["year"] or 0), reverse=True)

    with open(f"{prefix}.json", "w", encoding="utf-8") as f:
        json.dump(works, f, indent=2, ensure_ascii=False)

    with open(f"{prefix}.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "year", "venue", "type", "co_authors"])
        for w in works:
            writer.writerow([
                w["title"], w["year"], w["venue"], w["type"],
                "; ".join(w["co_authors"]),
            ])

    by_type = {}
    for w in works:
        by_type[w["type"]] = by_type.get(w["type"], 0) + 1

    print(f"Fetched {len(works)} works for ORCID {orcid}")
    for t, n in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t}: {n}")


if __name__ == "__main__":
    main()

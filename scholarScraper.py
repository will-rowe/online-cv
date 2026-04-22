#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""
Fetch publication data from the Semantic Scholar public API and write
_data/googleScholar.yaml for the Astro CV site.

Usage:
    uv run scholarScraper.py

To update S2 author IDs: search https://api.semanticscholar.org/graph/v1/author/search?query=Will+Rowe
and update S2_AUTHOR_IDS in the Config section below.
"""
import datetime
import json
import time
import urllib.request
import urllib.parse
import yaml

# ── Config ──────────────────────────────────────────────────────────────────
# S2 author IDs (run `python3 -c "..."` to find them via author search if they change)
S2_AUTHOR_IDS = ["48530874", "2286751976"]   # both profiles for Will P. M. Rowe
AUTHOR_NAMES = ["WPM Rowe", "W Rowe", "W. Rowe", "Will Rowe", "Will P. M. Rowe", "W. P. M. Rowe"]
BASE_URL = "https://scholar.google.co.uk"
OUT_FILE = "./_data/googleScholar.yaml"
MAX_PAPERS = 100
S2_API = "https://api.semanticscholar.org/graph/v1"
# Optional: set SEMANTIC_SCHOLAR_API_KEY env var for higher rate limits
import os
API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

# ── Helpers ──────────────────────────────────────────────────────────────────
def s2_get(path: str, params: dict | None = None) -> dict:
    url = f"{S2_API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"x-api-key": API_KEY} if API_KEY else {})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def bold_author(authors_str: str) -> str:
    for name in AUTHOR_NAMES:
        authors_str = authors_str.replace(name, f"<strong>{name}</strong>")
    return authors_str


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 1. Fetch stats and papers from all known S2 profiles, then merge
    total_citations = 0
    hindex = 0
    raw_papers_by_id: dict = {}  # paperId → paper, to deduplicate across profiles

    fields = "title,authors,year,venue,citationCount,externalIds,publicationDate"
    for i, author_id in enumerate(S2_AUTHOR_IDS):
        print(f"Fetching S2 author {author_id} ...")
        author_data = s2_get(f"/author/{author_id}", {"fields": "name,citationCount,hIndex"})
        print(f"  {author_data.get('name')} — {author_data.get('citationCount', 0)} citations, h-index {author_data.get('hIndex', 0)}")
        if i == 0:  # use primary profile stats only (avoid double-counting citations)
            total_citations = author_data.get("citationCount", 0)
            hindex = author_data.get("hIndex", 0)

        papers_resp = s2_get(
            f"/author/{author_id}/papers",
            {"fields": fields, "limit": MAX_PAPERS},
        )
        for p in papers_resp.get("data", []):
            pid = p.get("paperId", "")
            if pid and pid not in raw_papers_by_id:
                raw_papers_by_id[pid] = p

    raw_papers = list(raw_papers_by_id.values())
    print(f"  Total unique papers across all profiles: {len(raw_papers)}")

    # 3. Build output
    timestamp = datetime.datetime.now()
    last_updated = f"{timestamp.day}.{timestamp.month}.{timestamp.year}"
    introduction = (
        f"{total_citations} citations, h-index {hindex}. "
        f"Please click on the abstract links for more information. "
        f"Data fetched from Semantic Scholar on {last_updated}."
    )

    all_papers = []
    first_author_papers = []

    for p in raw_papers:
        title = p.get("title", "")
        authors_list = [a["name"] for a in p.get("authors", [])]
        raw_authors = ", ".join(authors_list)
        year = str(p.get("year") or "")
        venue = p.get("venue") or ""
        cites = p.get("citationCount", 0)

        doi = (p.get("externalIds") or {}).get("DOI")
        url = f"https://doi.org/{doi}" if doi else f"https://www.semanticscholar.org/paper/{p.get('paperId', '')}"

        authors = bold_author(raw_authors)
        entry = {
            "title": title,
            "authors": authors,
            "journal": venue,
            "year": year,
            "cites": cites,
            "link": url,
        }
        all_papers.append(entry)
        # first author = first name in list matches known author names
        first = authors_list[0].lower() if authors_list else ""
        if first and any(n.lower() in first or first in n.lower() for n in AUTHOR_NAMES):
            first_author_papers.append(entry)

    # Sort by year descending
    all_papers.sort(key=lambda x: int(x["year"]) if x["year"].isdigit() else 0, reverse=True)
    first_author_papers.sort(key=lambda x: int(x["year"]) if x["year"].isdigit() else 0, reverse=True)

    data = {
        "title": "Papers",
        "introduction": introduction,
        "papers": all_papers,
        "firstAuthorPapers": first_author_papers,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\nWrote {len(all_papers)} papers ({len(first_author_papers)} first-author) → {OUT_FILE}")

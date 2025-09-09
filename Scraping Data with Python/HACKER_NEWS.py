# ============================================
# Project: Hacker News Top Stories Scraper
# Author: You :)
# Description:
#   Fetches top Hacker News stories across N pages,
#   filters by minimum vote threshold, sorts by votes,
#   and prints a neat list. Uses the updated `.titleline > a`
#   selector (Hacker News changed from `.storylink`).
# ============================================

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import sys

# --------- Simple Config (tweak these) ----------
NUM_PAGES = 2          # how many HN pages to fetch (1..5 is sensible)
MIN_VOTES = 100        # only include stories with at least this many points
EXPORT_JSON = False    # set True to also save results to hn_top_stories.json
# ------------------------------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HN-Scraper/1.0; +https://news.ycombinator.com/)"
}
BASE_URL = "https://news.ycombinator.com/news"

def fetch_page(page: int = 1) -> Optional[BeautifulSoup]:
    """Fetch a Hacker News page and return a BeautifulSoup object."""
    try:
        url = BASE_URL if page == 1 else f"{BASE_URL}?p={page}"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"[WARN] Failed to fetch page {page}: {e}", file=sys.stderr)
        return None

def parse_stories_from_soup(soup: BeautifulSoup) -> List[Dict]:
    """
    Robustly parse stories by walking each 'tr.athing' row (a single HN story row),
    then grabbing its next 'tr' sibling (contains subtext like score, author).
    """
    results = []
    for story_row in soup.select("tr.athing"):
        # Title & link: inside .titleline > a
        title_link = story_row.select_one(".titleline > a")
        if not title_link:
            continue
        title = title_link.get_text(strip=True)
        link = title_link.get("href", "")

        # Subtext is in the next row
        subtext_row = story_row.find_next_sibling("tr")
        if not subtext_row:
            continue
        score_el = subtext_row.select_one(".score")
        if not score_el:
            # no votes yet
            continue

        # Extract numeric points like "123 points"
        try:
            points = int(score_el.get_text(strip=True).split()[0])
        except Exception:
            continue

        results.append({"title": title, "link": link, "votes": points})
    return results

def dedupe_stories(stories: List[Dict]) -> List[Dict]:
    """Deduplicate by (title, link) combo while preserving highest vote entry."""
    seen = {}
    for s in stories:
        key = (s["title"], s["link"])
        if key not in seen or s["votes"] > seen[key]["votes"]:
            seen[key] = s
    return list(seen.values())

def collect_stories(num_pages: int) -> List[Dict]:
    all_stories = []
    for p in range(1, num_pages + 1):
        soup = fetch_page(p)
        if not soup:
            continue
        all_stories.extend(parse_stories_from_soup(soup))
    return all_stories

def filter_and_sort(stories: List[Dict], min_votes: int) -> List[Dict]:
    filtered = [s for s in stories if s.get("votes", 0) >= min_votes]
    return sorted(filtered, key=lambda s: s["votes"], reverse=True)

def print_headline():
    line = "=" * 60
    print(line)
    print("Hacker News — Top Stories".center(60))
    print(f"(Pages: {NUM_PAGES} | Min Votes: {MIN_VOTES})".center(60))
    print(line)

def print_stories(stories: List[Dict]):
    if not stories:
        print("No stories matched your criteria.")
        return
    width = 60
    for i, s in enumerate(stories, 1):
        title = s["title"]
        link = s["link"]
        votes = s["votes"]
        print(f"{i:>2}. [{votes} pts] {title}")
        print(f"    {link}")
        print("-" * width)

def main():
    print_headline()
    stories = collect_stories(NUM_PAGES)
    stories = dedupe_stories(stories)
    stories = filter_and_sort(stories, MIN_VOTES)

    print_stories(stories)

    if EXPORT_JSON:
        out = "hn_top_stories.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(stories, f, ensure_ascii=False, indent=2)
        print(f"\nSaved {len(stories)} stories to {out}")

if __name__ == "__main__":
    main()

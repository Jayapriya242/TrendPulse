"""
TrendPulse - Task 1: Fetch Data from API

Fetches the top 500 trending stories from the HackerNews API, assigns each
story to one of 5 categories using keywords in its title, and saves up to
25 stories per category to a JSON file in the data/ folder.
"""

import json
import os
import re
import time
from datetime import datetime

import requests

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
BASE_URL = "https://hacker-news.firebaseio.com/v0"
HEADERS = {"User-Agent": "TrendPulse/1.0"}   # header required by the brief
NUM_STORIES = 500        # how many top story IDs to fetch
MAX_PER_CATEGORY = 25    # up to 25 stories per category (125 total)
DATA_DIR = "data"

# Keywords for each category, exactly as given in the brief.
# The order matters: "game" appears in both sports and entertainment,
# so a story is given to the first category that matches (sports).
CATEGORIES = {
    "technology": ["AI", "software", "tech", "code", "computer", "data",
                   "cloud", "API", "GPU", "LLM"],
    "worldnews": ["war", "government", "country", "president", "election",
                  "climate", "attack", "global"],
    "sports": ["NFL", "NBA", "FIFA", "sport", "game", "team", "player",
               "league", "championship"],
    "science": ["research", "study", "space", "physics", "biology",
                "discovery", "NASA", "genome"],
    "entertainment": ["movie", "film", "music", "Netflix", "game", "book",
                      "show", "award", "streaming"],
}


# ---------------------------------------------------------------------------
# Step 1 & 2: API calls
# ---------------------------------------------------------------------------
def fetch_json(url):
    """
    Send a GET request and return the parsed JSON.
    If anything goes wrong (network error, bad status code, bad JSON),
    print a message and return None so the script keeps running.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()          # raise an error for 4xx/5xx codes
        return response.json()
    except (requests.RequestException, ValueError) as error:
        print(f"Request failed for {url}: {error}")
        return None


def fetch_top_story_ids():
    """Get the list of top story IDs and keep only the first 500."""
    ids = fetch_json(f"{BASE_URL}/topstories.json")
    if ids is None:
        return []
    return ids[:NUM_STORIES]


def fetch_all_stories(story_ids):
    """Fetch the details of every story ID. Failed or invalid items are skipped."""
    stories = []
    for count, story_id in enumerate(story_ids, start=1):
        item = fetch_json(f"{BASE_URL}/item/{story_id}.json")

        # Skip failed requests, deleted items, and items without a title
        if item is None or not item.get("title"):
            continue
        stories.append(item)

        # Progress update so we know the script is still working
        if count % 100 == 0:
            print(f"Fetched {count}/{len(story_ids)} story details...")
    return stories


# ---------------------------------------------------------------------------
# Categorising
# ---------------------------------------------------------------------------
def title_matches(title, keywords):
    """
    Return True if the title contains any of the keywords.
    Both the title and keyword are lowercased so the check is case-insensitive,
    as the brief requires (e.g. "AI", "ai" and "Ai" all match).
    """
    title_lower = title.lower()
    for keyword in keywords:
        if keyword.lower() in title_lower:
            return True
    return False

# ---------------------------------------------------------------------------
# Extracting fields
# ---------------------------------------------------------------------------
def extract_fields(item, category, collected_at):
    """Keep only the 7 required fields from a HackerNews story."""
    return {
        "post_id": item.get("id"),
        "title": item.get("title"),
        "category": category,
        "score": item.get("score", 0),
        "num_comments": item.get("descendants", 0),   # HN calls comments "descendants"
        "author": item.get("by"),
        "collected_at": collected_at,
    }


def group_by_category(stories):
    """
    Loop over each category, pick up to 25 matching stories,
    and wait 2 seconds after each category (one sleep per category).
    """
    collected = []
    used_ids = set()   # makes sure no story is put in two categories
    collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for category, keywords in CATEGORIES.items():
        count = 0
        for item in stories:
            if count >= MAX_PER_CATEGORY:
                break
            if item["id"] in used_ids:
                continue
            if title_matches(item["title"], keywords):
                collected.append(extract_fields(item, category, collected_at))
                used_ids.add(item["id"])
                count += 1

        print(f"{category}: {count} stories")
        time.sleep(2)   # required pause between categories

    return collected


# ---------------------------------------------------------------------------
# Step 3: Save to JSON
# ---------------------------------------------------------------------------
def save_to_json(stories):
    """Save the stories to data/trends_YYYYMMDD.json and return the file path."""
    os.makedirs(DATA_DIR, exist_ok=True)   # create data/ if it doesn't exist
    filename = f"{DATA_DIR}/trends_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(stories, file, indent=4, ensure_ascii=False)
    return filename


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Fetching top story IDs...")
    top_ids = fetch_top_story_ids()

    if not top_ids:
        print("Could not get the top story list. Please check your connection.")
    else:
        print(f"Got {len(top_ids)} IDs. Fetching story details...")
        all_stories = fetch_all_stories(top_ids)

        print("Assigning categories...")
        results = group_by_category(all_stories)

        output_file = save_to_json(results)
        print(f"Collected {len(results)} stories. Saved to {output_file}")

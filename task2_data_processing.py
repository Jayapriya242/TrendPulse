"""
TrendPulse - Task 2: Clean the Data & Save as CSV

Loads the raw JSON file created in Task 1, cleans it with Pandas
(duplicates, missing values, data types, low scores, whitespace)
and saves the tidy result to data/trends_clean.csv.
"""

import glob
import os

import pandas as pd

DATA_DIR = "data"
OUTPUT_FILE = f"{DATA_DIR}/trends_clean.csv"
MIN_SCORE = 5   # stories with a score below this are treated as low quality


# ---------------------------------------------------------------------------
# 1 - Load the JSON file
# ---------------------------------------------------------------------------
def find_latest_json():
    """
    Find the newest trends_YYYYMMDD.json file in the data/ folder.
    The date in the file name sorts correctly as text, so the last
    file in the sorted list is the most recent one.
    """
    files = sorted(glob.glob(os.path.join(DATA_DIR, "trends_*.json")))
    if not files:
        raise FileNotFoundError("No trends_*.json file found in data/. Run Task 1 first.")
    return files[-1].replace("\\", "/")   # use forward slashes for tidy printing on Windows


def load_data(path):
    """Read the JSON file into a DataFrame and print how many rows were loaded."""
    df = pd.read_json(path)
    print(f"Loaded {len(df)} stories from {path}\n")
    return df


# ---------------------------------------------------------------------------
# 2 - Clean the data
# ---------------------------------------------------------------------------
def clean_data(df):
    # Duplicates: keep only the first row for each post_id
    df = df.drop_duplicates(subset="post_id", keep="first")
    print(f"After removing duplicates: {len(df)}")

    # Missing values: a story is useless without an ID, a title or a score
    df = df.dropna(subset=["post_id", "title", "score"])
    print(f"After removing nulls: {len(df)}")

    # Data types: make sure the number columns are whole numbers.
    # A missing comment count just means no comments, so it becomes 0
    # (otherwise the conversion to int would fail on NaN).
    df["score"] = df["score"].astype(int)
    df["num_comments"] = df["num_comments"].fillna(0).astype(int)

    # Low quality: remove stories with fewer than 5 upvotes
    df = df[df["score"] >= MIN_SCORE]
    print(f"After removing low scores: {len(df)}")

    # Whitespace: remove extra spaces at the start and end of each title
    df["title"] = df["title"].str.strip()

    # Reset the index so rows are numbered 0, 1, 2... after all the removals
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3 - Save as CSV and print a summary
# ---------------------------------------------------------------------------
def save_and_summarise(df):
    df.to_csv(OUTPUT_FILE, index=False)   # index=False: don't save the row numbers
    print(f"\nSaved {len(df)} rows to {OUTPUT_FILE}")

    print("\nStories per category:")
    counts = df["category"].value_counts()
    for category, count in counts.items():
        # :<15 left-aligns the name in a 15-character column so numbers line up
        print(f"  {category:<15} {count}")


if __name__ == "__main__":
    json_path = find_latest_json()
    stories = load_data(json_path)
    clean = clean_data(stories)
    save_and_summarise(clean)

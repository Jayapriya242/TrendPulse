"""
TrendPulse - Task 3: Analysis with Pandas & NumPy

Loads the clean CSV from Task 2, explores it, calculates statistics
with NumPy, adds two new columns (engagement and is_popular) and
saves the result to data/trends_analysed.csv for Task 4.
"""

import numpy as np
import pandas as pd

INPUT_FILE = "data/trends_clean.csv"
OUTPUT_FILE = "data/trends_analysed.csv"


# ---------------------------------------------------------------------------
# 1 - Load and explore
# ---------------------------------------------------------------------------
def load_and_explore(path):
    df = pd.read_csv(path)

    # .shape gives (number of rows, number of columns)
    print(f"Loaded data: {df.shape}\n")

    print("First 5 rows:")
    print(df.head())

    # Pandas .mean() gives the average of a whole column
    print(f"\nAverage score   : {df['score'].mean():,.0f}")
    print(f"Average comments: {df['num_comments'].mean():,.0f}")
    return df


# ---------------------------------------------------------------------------
# 2 - Basic analysis with NumPy
# ---------------------------------------------------------------------------
def numpy_analysis(df):
    # Convert the columns to NumPy arrays so NumPy functions can work on them
    scores = df["score"].to_numpy()
    comments = df["num_comments"].to_numpy()
    categories = df["category"].to_numpy()

    print("\n--- NumPy Stats ---")
    print(f"Mean score   : {np.mean(scores):,.0f}")
    print(f"Median score : {np.median(scores):,.0f}")   # middle value when sorted
    print(f"Std deviation: {np.std(scores):,.0f}")      # how spread out the scores are
    print(f"Max score    : {np.max(scores):,}")
    print(f"Min score    : {np.min(scores):,}")

    # np.unique with return_counts=True gives each category and how often it appears.
    # np.argmax finds the position of the biggest count.
    names, counts = np.unique(categories, return_counts=True)
    top = np.argmax(counts)
    print(f"\nMost stories in: {names[top]} ({counts[top]} stories)")

    # np.argmax on the comments array gives the row number of the most-discussed
    # story; .iloc uses that row number to look up the story's title.
    most_commented = np.argmax(comments)
    title = df["title"].iloc[most_commented]
    print(f'\nMost commented story: "{title}"  — {comments[most_commented]:,} comments')


# ---------------------------------------------------------------------------
# 3 - Add new columns
# ---------------------------------------------------------------------------
def add_columns(df):
    # engagement = comments per upvote. Adding 1 to the score avoids
    # dividing by zero if a story ever has a score of 0.
    df["engagement"] = df["num_comments"] / (df["score"] + 1)

    # is_popular = True when a story scores above the average, otherwise False.
    # Comparing a whole column with a number gives a True/False column.
    average_score = df["score"].mean()
    df["is_popular"] = df["score"] > average_score
    return df


# ---------------------------------------------------------------------------
# 4 - Save the result
# ---------------------------------------------------------------------------
def save_result(df, path):
    df.to_csv(path, index=False)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    data = load_and_explore(INPUT_FILE)
    numpy_analysis(data)
    data = add_columns(data)
    save_result(data, OUTPUT_FILE)

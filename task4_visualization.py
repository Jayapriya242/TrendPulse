"""
TrendPulse - Task 4: Visualizations

Loads the analysed CSV from Task 3 and creates 3 charts with Matplotlib:
  1. Top 10 stories by score (horizontal bar chart)
  2. Stories per category (bar chart)
  3. Score vs comments (scatter plot)
Then combines them into one dashboard. All charts are saved as PNGs in outputs/.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd

INPUT_FILE = "data/trends_analysed.csv"
OUTPUT_DIR = "outputs"

# Set to True to also open each chart in a window after saving it.
# (You must close each window for the script to continue.)
SHOW_CHARTS = False

# One colour per category bar (5 categories, 5 colours)
BAR_COLOURS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"]


# ---------------------------------------------------------------------------
# 1 - Setup
# ---------------------------------------------------------------------------
def setup():
    """Load the analysed data and make sure the outputs/ folder exists."""
    df = pd.read_csv(INPUT_FILE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Loaded {len(df)} stories from {INPUT_FILE}")
    return df


def shorten(title, limit=50):
    """Cut titles longer than 50 characters and add '...' so they fit on the axis."""
    if len(title) > limit:
        return title[:limit - 3] + "..."
    return title


def save_chart(fig, filename):
    """
    Save a figure to outputs/. savefig() is always called BEFORE show(),
    because show() can clear the figure and we would save a blank image.
    """
    path = f"{OUTPUT_DIR}/{filename}"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved {path}")
    if SHOW_CHARTS:
        plt.show()
    plt.close(fig)   # free the memory used by the figure


# ---------------------------------------------------------------------------
# Chart drawing functions. Each one draws onto an "ax" (one chart area),
# so the same code is reused for the single charts and for the dashboard.
# ---------------------------------------------------------------------------
def draw_top_stories(df, ax):
    """Chart 1: horizontal bar chart of the 10 highest-scoring stories."""
    top10 = df.nlargest(10, "score")
    # Reverse the order so the highest score appears at the TOP of the chart
    top10 = top10.iloc[::-1]
    labels = [shorten(title) for title in top10["title"]]

    ax.barh(labels, top10["score"], color="steelblue")
    ax.set_title("Top 10 Stories by Score")
    ax.set_xlabel("Score (upvotes)")
    ax.set_ylabel("Story title")


def draw_categories(df, ax):
    """Chart 2: bar chart of how many stories are in each category."""
    counts = df["category"].value_counts()
    # Take one colour for each category bar
    colours = BAR_COLOURS[:len(counts)]

    ax.bar(counts.index, counts.values, color=colours)
    ax.set_title("Stories per Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of stories")
    ax.tick_params(axis="x", rotation=30)   # tilt names so they don't overlap


def draw_scatter(df, ax):
    """Chart 3: scatter plot of score vs comments, coloured by popularity."""
    # Split the data into two groups using the True/False is_popular column
    popular = df[df["is_popular"] == True]
    not_popular = df[df["is_popular"] == False]

    # Plot each group separately so each gets its own colour and legend label
    ax.scatter(not_popular["score"], not_popular["num_comments"],
               color="grey", alpha=0.6, label="Not popular")
    ax.scatter(popular["score"], popular["num_comments"],
               color="orange", alpha=0.8, label="Popular (above average score)")

    ax.set_title("Score vs Comments")
    ax.set_xlabel("Score (upvotes)")
    ax.set_ylabel("Number of comments")
    ax.legend()


# ---------------------------------------------------------------------------
# 2, 3, 4 - Save each chart on its own
# ---------------------------------------------------------------------------
def make_single_charts(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    draw_top_stories(df, ax)
    save_chart(fig, "chart1_top_stories.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    draw_categories(df, ax)
    save_chart(fig, "chart2_categories.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    draw_scatter(df, ax)
    save_chart(fig, "chart3_scatter.png")


# ---------------------------------------------------------------------------
# Bonus - Dashboard
# ---------------------------------------------------------------------------
def make_dashboard(df):
    """Combine the 3 charts into one 2x2 figure."""
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))

    # The top-10 chart has long titles, so it gets the whole top row:
    # remove the two top axes and add one wide axis in their place.
    axes[0, 0].remove()
    axes[0, 1].remove()
    wide_ax = fig.add_subplot(2, 1, 1)

    draw_top_stories(df, wide_ax)
    draw_categories(df, axes[1, 0])
    draw_scatter(df, axes[1, 1])

    fig.suptitle("TrendPulse Dashboard", fontsize=20, fontweight="bold")
    fig.tight_layout()
    save_chart(fig, "dashboard.png")


if __name__ == "__main__":
    data = setup()
    make_single_charts(data)
    make_dashboard(data)
    print("All charts saved in the outputs/ folder.")

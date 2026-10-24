"""Body-area summaries and plots used by the shark incident notebook."""

import matplotlib.pyplot as plt
import pandas as pd


BODY_PATTERNS = {
    "Feet / ankles": r"\b(?:foot|feet|toes?|heels?|ankles?)\b",
    "Legs": r"\b(?:legs?|calf|calves|thighs?|knees?|shins?)\b",
    "Hands / wrists": r"\b(?:hands?|fingers?|wrists?)\b",
    "Arms / shoulders": r"\b(?:arms?|forearms?|elbows?|shoulders?)\b",
    "Torso": r"\b(?:torso|chest|abdomen|stomach|back|buttocks?)\b",
    "Head / neck": r"\b(?:head|neck|face|scalp)\b"
}


def body_area_tables(data):
    """Count text mentions, excluding records explicitly reporting no injury.

    Returns overall counts, counts by country, and percentages by country.
    Percentages use all selected records in each country as the denominator.
    Areas can overlap. A mention does not establish a clinical diagnosis.
    """
    countries = data["Country"].fillna("Unknown")
    text = data["Injury"].astype("string").str.lower()
    eligible = data["Injury_status"].ne("No injury reported")
    mentions = pd.DataFrame({
        area: text.str.contains(pattern, na=False) & eligible
        for area, pattern in BODY_PATTERNS.items()
    })
    totals = countries.value_counts()
    by_country = (
        mentions.groupby(countries).sum().astype(int).reindex(totals.index)
    )
    percentages = by_country.div(totals, axis=0).mul(100).round(1)
    overall = mentions.sum().astype(int).sort_values(ascending=False)
    overall.name = "records_mentioning_area"
    return overall, by_country, percentages


def plot_country_counts(data, start_year=2006, end_year=2026, top_n=5):
    """Plot selected record counts, rather than population incidence rates."""
    counts = (
        data["Country"].fillna("Unknown").value_counts()
        .head(top_n).sort_values()
    )
    fig, ax = plt.subplots(figsize=(8, 4))
    counts.plot.barh(ax=ax, color="steelblue")
    ax.set_title(f"Selected surfing incidents by country, {start_year}–{end_year}")
    ax.set_xlabel("Number of records")
    ax.set_ylabel("Country")
    ax.bar_label(ax.containers[0], padding=3)
    ax.margins(x=0.15)
    fig.tight_layout()
    return fig, ax


def plot_country_body_comparison(percentages, start_year=2006, end_year=2026):
    """Compare the two focus countries using the original percentage denominator."""
    comparison = percentages.loc[
        ["USA", "Australia"], ["Feet / ankles", "Legs"]
    ]
    fig, ax = plt.subplots(figsize=(8, 4))
    comparison.plot.bar(ax=ax, rot=0, color=["steelblue", "darkorange"])
    ax.set_title(f"Body area mentions by country, {start_year}–{end_year}")
    ax.set_xlabel("Country")
    ax.set_ylabel("Percentage of selected records")
    ax.set_ylim(0, 100)
    ax.legend(title="Body area")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3)
    fig.tight_layout()
    return fig, ax

"""Reusable cleaning functions extracted from the project notebook.

The selection and text-matching rules intentionally preserve the original
analysis. These functions do not infer clinical severity or remove duplicates.
"""

import pandas as pd


ANALYSIS_COLUMNS = [
    "Date", "Year", "Type", "Country", "State", "Activity", "Sex", "Age", "Injury"
]
AGE_BINS = [0, 13, 18, 30, 45, 60, float("inf")]
AGE_LABELS = [
    "Children (0-12)", "Teens (13-17)", "Young adults (18-29)",
    "Adults (30-44)", "Middle-aged adults (45-59)", "Older adults (60+)"
]


def select_analysis_columns(data):
    """Trim column names and keep the nine fields used in the analysis."""
    result = data.copy()
    result.columns = result.columns.str.strip()
    missing = set(ANALYSIS_COLUMNS) - set(result.columns)
    if missing:
        raise ValueError(f"Required columns are missing: {sorted(missing)}")
    return result.loc[:, ANALYSIS_COLUMNS].copy()


def missing_value_summary(data):
    """Count missing values and their percentage in each column."""
    return pd.DataFrame({
        "missing_count": data.isna().sum(),
        "missing_percentage": data.isna().mean().mul(100).round(2)
    }).sort_values("missing_count", ascending=False)


def classify_activities(data):
    """Flag likely board-surfing descriptions using the notebook's rules."""
    result = data.copy()
    activity = result["Activity"].astype("string").str.strip().str.lower()
    surf_match = activity.str.contains(
        r"\bsurfing\b|\bsurfng\b|\bsurfboard\b", na=False
    )
    needs_review = activity.str.contains(
        r"body|boogie|wind|kite|ski|foil|fish|div|swim|carrying|towing|\bor\b|/|\?",
        na=False
    )
    result["Activity_group"] = "Other / review"
    result.loc[surf_match & ~needs_review, "Activity_group"] = "Surfing"
    return result


def filter_surfing(data):
    """Keep records selected by the provisional activity classification."""
    return data.loc[data["Activity_group"].eq("Surfing")].copy().reset_index(drop=True)


def add_age_groups(data):
    """Preserve Age, convert exact numeric values, and create age categories."""
    result = data.copy()
    result["Age_numeric"] = pd.to_numeric(result["Age"], errors="coerce")
    usable_age = result["Age_numeric"].where(result["Age_numeric"].between(0, 120))
    result["Age_group"] = (
        pd.cut(usable_age, bins=AGE_BINS, labels=AGE_LABELS, right=False)
        .cat.add_categories(["Unknown / review"])
        .fillna("Unknown / review")
    )
    return result


def filter_usable_ages(data):
    """Exclude unknown or flagged ages, matching the original study scope."""
    result = data.loc[data["Age_group"].ne("Unknown / review")].copy()
    result = result.reset_index(drop=True)
    result["Age_group"] = result["Age_group"].cat.remove_unused_categories()
    return result


def filter_years(data, start_year=2006, end_year=2026):
    """Select an inclusive calendar-year interval without parsing Date."""
    if start_year > end_year:
        raise ValueError("start_year must not exceed end_year")
    years = pd.to_numeric(data["Year"], errors="coerce")
    result = data.loc[years.between(start_year, end_year)].copy()
    result["Year"] = years.loc[result.index].astype("Int64")
    return result


def standardize_geography(data):
    """Normalize country formatting and the reviewed Australian abbreviations."""
    result = data.copy()
    result["Country"] = (
        result["Country"].astype("string").str.strip().str.title()
        .replace({"Usa": "USA"})
    )
    result["State"] = result["State"].astype("string").str.strip()
    australia = result["Country"].eq("Australia")
    result.loc[australia, "State"] = result.loc[australia, "State"].replace({
        "NSW": "New South Wales", "WA": "Western Australia"
    })
    return result


def correct_hawaii_record(data):
    """Correct the reviewed Hawaii/Maui combination and keep other rows intact."""
    result = data.copy()
    mask = result["Country"].eq("Hawaii") & result["State"].eq("Maui")
    result.loc[mask, ["Country", "State"]] = ["USA", "Hawaii"]
    return result


def standardize_geographic_labels(data):
    """Apply only the country and locality equivalences reviewed in the study."""
    result = data.copy()
    result["Country"] = result["Country"].replace({
        "Reunion Island": "Reunion", "Scotland": "United Kingdom"
    })
    reunion = result["Country"].eq("Reunion")
    result.loc[reunion, "State"] = result.loc[reunion, "State"].replace({
        "Saint Leu": "Saint-Leu", "Saint Gilles": "Saint-Gilles"
    })
    return result


def classify_injury_status(data):
    """Flag exact fatal labels and explicit no-injury text, leaving other cases open.

    Review is not a clinical severity category or a survival classification.
    """
    result = data.copy()
    text = result["Injury"].astype("string").str.strip().str.lower()
    fatal = text.eq("fatal").fillna(False)
    no_injury = text.str.contains(
        r"\bno injur(?:y|ies)\b|\buninjured\b|\bnone sustained\b", na=False
    )
    result["Injury_status"] = "Review"
    result.loc[fatal, "Injury_status"] = "Fatal reported"
    result.loc[no_injury & ~fatal, "Injury_status"] = "No injury reported"
    return result


def clean_data(data, start_year=2006, end_year=2026):
    """Run the complete original selection and cleaning workflow.

    Returns the analytical dataset and an audit table of row and column counts.
    The input is left unchanged. Known selection biases are documented in README.
    """
    audit = [{"stage": "Raw data", "rows": len(data), "columns": len(data.columns)}]

    def record(stage, frame):
        audit.append({"stage": stage, "rows": len(frame), "columns": len(frame.columns)})

    result = select_analysis_columns(data)
    record("Selected analysis columns", result)
    result = filter_surfing(classify_activities(result))
    record("Likely surfing", result)
    result = filter_usable_ages(add_age_groups(result))
    record("Usable age", result)
    result = filter_years(result, start_year, end_year)
    record(f"Period {start_year}-{end_year}", result)
    result = standardize_geographic_labels(
        correct_hawaii_record(standardize_geography(result))
    )
    record("Normalized geography", result)
    result = classify_injury_status(result)
    record("Provisional injury status", result)
    return result, pd.DataFrame(audit)

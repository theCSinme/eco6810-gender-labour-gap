
from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


# ============================================================
# 1. PROJECT PATHS AND SETTINGS
# ============================================================

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"

DATASET_PATH = DATA_DIR / "analysis_dataset.csv"

START_YEAR = 2019
END_YEAR = 2023
THRESHOLD_PP = 5.0

EXPECTED_INCOME_GROUPS = {
    "High income",
    "Upper middle income",
    "Lower middle income",
    "Low income",
}


# ============================================================
# 2. UTILITY FUNCTIONS
# ============================================================

def write_json(path: Path, payload: dict) -> None:
    """Write a JSON file without non-standard NaN values."""
    path.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def country_clustered_se(group_data: pd.DataFrame) -> float:
    """
    Calculate a country-clustered standard error for a group mean.

    Repeated observations within a country are treated as one cluster.
    This allows observations from the same country to be dependent.
    """
    group_data = group_data.dropna(
        subset=["gender_gap_pp", "iso3"]
    )

    n = len(group_data)
    number_of_countries = group_data["iso3"].nunique()

    if n == 0 or number_of_countries < 2:
        return float("nan")

    group_mean = group_data["gender_gap_pp"].mean()
    residuals = group_data["gender_gap_pp"] - group_mean

    cluster_sums = (
        group_data.assign(_residual=residuals)
        .groupby("iso3")["_residual"]
        .sum()
    )

    variance = (
        number_of_countries / (number_of_countries - 1)
    ) * cluster_sums.pow(2).sum() / (n ** 2)

    return float(max(variance, 0.0) ** 0.5)


def validate_required_columns(data: pd.DataFrame) -> None:
    """Check that the input dataset has the required columns."""
    required_columns = {
        "Country Code",
        "Year",
        "male_lfp",
        "female_lfp",
        "income_group",
    }

    missing = required_columns - set(data.columns)

    if missing:
        raise ValueError(
            "The dataset is missing required columns: "
            + ", ".join(sorted(missing))
        )


# ============================================================
# 3. LOAD AND VALIDATE THE PREPARED DATASET
# ============================================================

def load_dataset() -> pd.DataFrame:
    """Load, clean, and validate the prepared analysis dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}\n"
            "Ensure data/analysis_dataset.csv is committed."
        )

    data = pd.read_csv(DATASET_PATH)
    validate_required_columns(data)

    # Standardise country identifiers.
    if "iso3" in data.columns:
        data["iso3"] = data["iso3"].fillna(
            data["Country Code"]
        )
    else:
        data["iso3"] = data["Country Code"]

    data["iso3"] = data["iso3"].astype("string").str.strip()

    # Preserve country names when available.
    if "country_name" in data.columns:
        if "Country Name" in data.columns:
            data["country"] = data["country_name"].fillna(
                data["Country Name"]
            )
        else:
            data["country"] = data["country_name"]
    elif "Country Name" in data.columns:
        data["country"] = data["Country Name"]
    else:
        data["country"] = data["iso3"]

    # Convert numeric variables safely.
    data["year"] = pd.to_numeric(
        data["Year"], errors="coerce"
    )
    data["male_lfp"] = pd.to_numeric(
        data["male_lfp"], errors="coerce"
    )
    data["female_lfp"] = pd.to_numeric(
        data["female_lfp"], errors="coerce"
    )

    data["income_group"] = (
        data["income_group"].astype("string").str.strip()
    )

    # Remove observations missing variables required for analysis.
    data = data.dropna(
        subset=[
            "iso3",
            "year",
            "male_lfp",
            "female_lfp",
            "income_group",
        ]
    ).copy()

    # Restrict the study period.
    data = data[
        data["year"].between(START_YEAR, END_YEAR)
    ].copy()

    if data.empty:
        raise ValueError(
            "No usable observations remain for the study period."
        )

    # Validate years before converting to integers.
    if not (data["year"] % 1 == 0).all():
        raise ValueError("Non-integer year values were found.")

    data["year"] = data["year"].astype(int)

    # Check for empty identifiers and income groups.
    if data["iso3"].eq("").any():
        raise ValueError("Empty country identifiers were found.")

    if data["income_group"].eq("").any():
        raise ValueError("Empty income-group values were found.")

    # Validate participation rates.
    invalid_rates = (
        ~data["male_lfp"].between(0, 100)
        | ~data["female_lfp"].between(0, 100)
    )

    if invalid_rates.any():
        examples = data.loc[
            invalid_rates,
            ["country", "iso3", "year", "male_lfp", "female_lfp"],
        ].head(10)

        raise ValueError(
            f"Found {invalid_rates.sum()} observations with "
            "participation rates outside 0–100.\n"
            + examples.to_string(index=False)
        )

    # Flag possible regional aggregates for review.
    # Do not automatically remove them based on names alone.
    aggregate_names = {
        "world",
        "south asia",
        "sub-saharan africa",
        "europe & central asia",
        "europe and central asia",
        "east asia & pacific",
        "east asia and pacific",
        "latin america & caribbean",
        "latin america and caribbean",
        "middle east & north africa",
        "middle east and north africa",
        "north america",
    }

    names_lower = data["country"].astype(str).str.strip().str.lower()
    possible_aggregates = names_lower.isin(aggregate_names)

    if possible_aggregates.any():
        found = sorted(
            data.loc[possible_aggregates, "country"]
            .astype(str)
            .unique()
        )
        warnings.warn(
            "Possible regional aggregates require review: "
            + ", ".join(found)
            + ". Check the source metadata before deciding whether "
              "to exclude these observations.",
            stacklevel=2,
        )

    # Recalculate the outcome from the two input indicators.
    data["gender_gap_pp"] = (
        data["male_lfp"] - data["female_lfp"]
    )

    # Reject duplicate country-year observations.
    duplicates = data.duplicated(
        ["iso3", "year"], keep=False
    )

    if duplicates.any():
        examples = data.loc[
            duplicates, ["iso3", "country", "year"]
        ].head(10)

        raise ValueError(
            "Duplicate country-year observations found. "
            "Check the prepared dataset.\n"
            + examples.to_string(index=False)
        )

    # Verify income-group coverage.
    observed_groups = set(data["income_group"].dropna().unique())
    unexpected_groups = observed_groups - EXPECTED_INCOME_GROUPS

    if unexpected_groups:
        warnings.warn(
            "Income-group labels differ from the expected labels: "
            + ", ".join(sorted(unexpected_groups))
            + ". Verify the source metadata and group names.",
            stacklevel=2,
        )

    return data.sort_values(
        ["iso3", "year"]
    ).reset_index(drop=True)


# ============================================================
# 4. MAIN ANALYSIS
# ============================================================

def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading prepared dataset...")
    data = load_dataset()

    number_of_observations = len(data)
    number_of_countries = data["iso3"].nunique()

    print(f"Study period: {START_YEAR}–{END_YEAR}")
    print(f"Country-year observations: {number_of_observations}")
    print(f"Unique country identifiers: {number_of_countries}")

    # Save the processed country-year dataset.
    data.to_csv(
        DATA_DIR / "country_year_gender_gap.csv",
        index=False,
    )

    # --------------------------------------------------------
    # Overall baseline
    # --------------------------------------------------------

    baseline = float(data["gender_gap_pp"].mean())

    # --------------------------------------------------------
    # Income-group descriptive statistics
    # --------------------------------------------------------

    summary = (
        data.groupby("income_group")
        .agg(
            observations=("gender_gap_pp", "count"),
            mean_gap_pp=("gender_gap_pp", "mean"),
            sd_country_year=("gender_gap_pp", "std"),
            countries=("iso3", "nunique"),
        )
        .reset_index()
    )

    summary["standard_error_country_year"] = (
        summary["sd_country_year"]
        / summary["observations"].pow(0.5)
    )

    clustered_results = []

    for group_name, group_data in data.groupby(
        "income_group", sort=True
    ):
        clustered_results.append({
            "income_group": group_name,
            "standard_error_clustered": country_clustered_se(
                group_data
            ),
        })

    clustered_df = pd.DataFrame(clustered_results)

    summary = summary.merge(
        clustered_df,
        on="income_group",
        how="left",
        validate="one_to_one",
    )

    summary = summary.sort_values(
        "mean_gap_pp", ascending=False
    ).reset_index(drop=True)

    summary.to_csv(
        OUTPUTS_DIR / "income_group_summary.csv",
        index=False,
    )

    # --------------------------------------------------------
    # Overall annual trend
    # --------------------------------------------------------

    annual_trend = (
        data.groupby("year")["gender_gap_pp"]
        .agg(
            mean_gap_pp="mean",
            observations="count",
        )
        .reset_index()
    )

    annual_trend.to_csv(
        OUTPUTS_DIR / "annual_trend.csv",
        index=False,
    )

    # --------------------------------------------------------
    # Annual trends by income group
    # --------------------------------------------------------

    annual_groups = (
        data.groupby(["year", "income_group"])["gender_gap_pp"]
        .agg(
            mean_gap_pp="mean",
            observations="count",
        )
        .reset_index()
    )

    annual_groups.to_csv(
        OUTPUTS_DIR / "annual_income_group_trends.csv",
        index=False,
    )

    # --------------------------------------------------------
    # Robustness: equal weight for every country
    # --------------------------------------------------------

    country_means = (
        data.groupby(["iso3", "country", "income_group"])[
            "gender_gap_pp"
        ]
        .mean()
        .reset_index(name="country_mean_gap_pp")
    )

    country_summary = (
        country_means.groupby("income_group")
        .agg(
            countries=("iso3", "nunique"),
            equal_country_mean_gap_pp=(
                "country_mean_gap_pp", "mean"
            ),
            country_sd=("country_mean_gap_pp", "std"),
        )
        .reset_index()
    )

    country_summary["country_level_standard_error"] = (
        country_summary["country_sd"]
        / country_summary["countries"].pow(0.5)
    )

    country_summary.to_csv(
        OUTPUTS_DIR / "country_level_robustness.csv",
        index=False,
    )

    # --------------------------------------------------------
    # Primary metric and threshold
    # --------------------------------------------------------

    primary_value = float(
        summary["mean_gap_pp"].max()
        - summary["mean_gap_pp"].min()
    )

    passed = bool(primary_value >= THRESHOLD_PP)

    # --------------------------------------------------------
    # Figure 1: gender gap by income group
    # --------------------------------------------------------

    ordered = summary.sort_values("mean_gap_pp")

    plt.figure(figsize=(10, 6))

    plt.bar(
        ordered["income_group"],
        ordered["mean_gap_pp"],
        yerr=1.96 * ordered["standard_error_clustered"],
        capsize=4,
    )

    plt.axhline(
        baseline,
        linestyle="--",
        label=f"Overall mean ({baseline:.2f} pp)",
    )

    plt.ylabel(
        "Male minus female participation rate (percentage points)"
    )
    plt.xlabel("World Bank income group")
    plt.title(
        "Gender Gap in Labour-Force Participation, 2019–2023"
    )
    plt.xticks(rotation=20, ha="right")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        OUTPUTS_DIR / "gender_gap_by_income_group.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    # --------------------------------------------------------
    # Figure 2: annual trends by income group
    # --------------------------------------------------------

    plt.figure(figsize=(10, 6))

    for group_name, group_data in annual_groups.groupby(
        "income_group"
    ):
        group_data = group_data.sort_values("year")

        plt.plot(
            group_data["year"],
            group_data["mean_gap_pp"],
            marker="o",
            label=group_name,
        )

    plt.xlabel("Year")
    plt.ylabel("Mean gender gap (percentage points)")
    plt.title("Gender Gap Trends by World Bank Income Group")
    plt.xticks(list(range(START_YEAR, END_YEAR + 1)))
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        OUTPUTS_DIR / "gender_gap_trends_2019_2023.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    # --------------------------------------------------------
    # Baseline metric JSON
    # --------------------------------------------------------

    write_json(
        OUTPUTS_DIR / "baseline_metric.json",
        {
            "metric_name": "overall_mean_gender_gap_pp",
            "value": baseline,
            "unit": "percentage points",
            "observations": number_of_observations,
            "countries": number_of_countries,
            "notes": (
                "Mean male-minus-female labour-force "
                "participation gap across available "
                "country-year observations, 2019–2023."
            ),
            "is_template": False,
        },
    )

    # --------------------------------------------------------
    # Primary metric JSON
    # --------------------------------------------------------

    write_json(
        OUTPUTS_DIR / "primary_metric.json",
        {
            "metric_name": (
                "range_between_income_group_mean_gaps_pp"
            ),
            "value": primary_value,
            "threshold": THRESHOLD_PP,
            "passed": passed,
            "unit": "percentage points",
            "notes": (
                "Difference between the largest and smallest "
                "income-group mean gender gaps across available "
                "country-year observations."
            ),
            "is_template": False,
        },
    )

    # --------------------------------------------------------
    # Milestone manifest
    # --------------------------------------------------------

    write_json(
        OUTPUTS_DIR / "milestone_manifest.json",
        {
            "charter_locked": False,
            "sources": [
                {
                    "name": "Prepared World Bank indicator dataset",
                    "status": "local_file",
                    "probe_artifact": (
                        "artifacts/probes/world_bank_data_access.md"
                    ),
                    "note": (
                        "The analysis uses the committed prepared "
                        "dataset and does not make live API requests."
                    ),
                }
            ],
            "baseline_ready": True,
            "primary_metric_schema_ready": True,
            "run_command": "uv run main.py",
            "template_warning": (
                "Instructor approval of the charter and permission "
                "for individual submission must be confirmed separately."
            ),
        },
    )

    # --------------------------------------------------------
    # Print verification results
    # --------------------------------------------------------

    print("\n" + "=" * 55)
    print("ANALYSIS COMPLETED")
    print("=" * 55)

    print(f"Country-year observations: {number_of_observations}")
    print(f"Unique countries: {number_of_countries}")
    print(f"Overall mean gap: {baseline:.3f} percentage points")
    print(
        "Range between income-group means: "
        f"{primary_value:.3f} percentage points"
    )
    print(f"Success threshold: {THRESHOLD_PP:.1f} percentage points")
    print(f"Threshold passed: {passed}")

    print("\nIncome-group results:")
    print(
        summary[
            [
                "income_group",
                "observations",
                "countries",
                "mean_gap_pp",
                "standard_error_clustered",
            ]
        ].to_string(index=False)
    )

    print("\nFiles generated:")
    print("- data/country_year_gender_gap.csv")
    print("- outputs/income_group_summary.csv")
    print("- outputs/annual_trend.csv")
    print("- outputs/annual_income_group_trends.csv")
    print("- outputs/country_level_robustness.csv")
    print("- outputs/gender_gap_by_income_group.png")
    print("- outputs/gender_gap_trends_2019_2023.png")
    print("- outputs/baseline_metric.json")
    print("- outputs/primary_metric.json")
    print("- outputs/milestone_manifest.json")

    print("\nreport.md was not modified.")
    print("Check the printed results against the final report.")


if __name__ == "__main__":
    main()

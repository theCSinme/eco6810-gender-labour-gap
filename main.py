
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"

START_YEAR = 2019
END_YEAR = 2023
THRESHOLD_PP = 5.0

DATASET_PATH = DATA_DIR / "analysis_dataset.csv"


def write_json(path: Path, payload: dict) -> None:
    """Write JSON output, converting only valid Python values."""
    path.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def country_clustered_se(
    data: pd.DataFrame,
    group_column: str = "income_group",
) -> pd.DataFrame:
    """
    Calculate country-clustered standard errors for income-group means.

    Each country is treated as a cluster. This allows observations from
    the same country to be correlated across years.
    """
    results = []

    for group_name, group_data in data.groupby(group_column, sort=True):
        group_data = group_data.dropna(subset=["gender_gap_pp", "iso3"])
        n = len(group_data)
        country_count = group_data["iso3"].nunique()
        mean_value = group_data["gender_gap_pp"].mean()

        if country_count < 2 or n == 0:
            standard_error = float("nan")
        else:
            residuals = group_data["gender_gap_pp"] - mean_value
            cluster_sums = (
                group_data.assign(_residual=residuals)
                .groupby("iso3")["_residual"]
                .sum()
            )

            variance = (
                country_count / (country_count - 1)
            ) * (cluster_sums.pow(2).sum() / (n ** 2))

            standard_error = float(max(variance, 0.0) ** 0.5)

        results.append({
            "income_group": group_name,
            "standard_error_clustered": standard_error,
            "country_clusters": country_count,
        })

    return pd.DataFrame(results)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load the prepared dataset; no live API connection is required.
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Required dataset not found: {DATASET_PATH}\n"
            "Ensure data/analysis_dataset.csv is committed to GitHub."
        )

    data = pd.read_csv(DATASET_PATH)

    required_columns = {
        "Country Code",
        "Year",
        "male_lfp",
        "female_lfp",
        "country_name",
        "income_group",
    }

    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        raise ValueError(
            "The prepared dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    # Standardise column names used throughout the analysis.
    data = data.rename(columns={
        "Country Code": "iso3",
        "Year": "year",
        "male_lfp": "male_lfp",
        "female_lfp": "female_lfp",
        "country_name": "country",
        "income_group": "income_group",
    })

    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    data["male_lfp"] = pd.to_numeric(data["male_lfp"], errors="coerce")
    data["female_lfp"] = pd.to_numeric(data["female_lfp"], errors="coerce")

    data = data.loc[
        data["year"].between(START_YEAR, END_YEAR)
    ].copy()

    data["year"] = data["year"].astype(int)

    data = data.dropna(subset=[
        "iso3",
        "year",
        "male_lfp",
        "female_lfp",
        "income_group",
    ])

    if data.duplicated(["iso3", "year"]).any():
        raise ValueError(
            "Duplicate country-year observations found in the prepared dataset."
        )

    data["gender_gap_pp"] = data["male_lfp"] - data["female_lfp"]

    data = data.sort_values(["iso3", "year"]).reset_index(drop=True)

    if data.empty:
        raise ValueError("No usable observations remain after data cleaning.")

    # Save the analysis dataset used by the script.
    data.to_csv(DATA_DIR / "country_year_gender_gap.csv", index=False)

    # Overall baseline.
    baseline = float(data["gender_gap_pp"].mean())

    # Descriptive statistics by income group.
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

    # Country-clustered standard errors for income-group means.
    clustered = country_clustered_se(data)

    summary = summary.merge(
        clustered,
        on="income_group",
        how="left",
        validate="one_to_one",
    )

    summary["standard_error_country_year"] = (
        summary["sd_country_year"]
        / summary["observations"].pow(0.5)
    )

    summary = summary.sort_values(
        "mean_gap_pp", ascending=False
    ).reset_index(drop=True)

    summary.to_csv(
        OUTPUTS_DIR / "income_group_summary.csv",
        index=False,
    )

    # Overall annual trend.
    annual_trend = (
        data.groupby("year")["gender_gap_pp"]
        .agg(mean_gap_pp="mean", observations="count")
        .reset_index()
    )

    annual_trend.to_csv(
        OUTPUTS_DIR / "annual_trend.csv",
        index=False,
    )

    # Annual trends by income group.
    annual_groups = (
        data.groupby(["year", "income_group"])["gender_gap_pp"]
        .agg(mean_gap_pp="mean", observations="count")
        .reset_index()
    )

    annual_groups.to_csv(
        OUTPUTS_DIR / "annual_income_group_trends.csv",
        index=False,
    )

    # Robustness check: average years within each country first,
    # then give every country equal weight within its income group.
    country_means = (
        data.groupby(["iso3", "country", "income_group"])["gender_gap_pp"]
        .mean()
        .reset_index(name="country_mean_gap_pp")
    )

    country_summary = (
        country_means.groupby("income_group")
        .agg(
            countries=("iso3", "nunique"),
            equal_country_mean_gap_pp=("country_mean_gap_pp", "mean"),
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

    # Primary metric: range between income-group mean gaps.
    primary_value = float(
        summary["mean_gap_pp"].max()
        - summary["mean_gap_pp"].min()
    )
    passed = bool(primary_value >= THRESHOLD_PP)

    # Figure 1: income-group comparison with country-clustered SEs.
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
    plt.ylabel("Male minus female participation rate (percentage points)")
    plt.xlabel("World Bank income group")
    plt.title("Gender Gap in Labour-Force Participation, 2019–2023")
    plt.xticks(rotation=20, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        OUTPUTS_DIR / "gender_gap_by_income_group.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    # Figure 2: annual trends by income group.
    plt.figure(figsize=(10, 6))

    for group_name, group_data in annual_groups.groupby("income_group"):
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

    # Required baseline metric.
    write_json(OUTPUTS_DIR / "baseline_metric.json", {
        "metric_name": "overall_mean_gender_gap_pp",
        "value": baseline,
        "unit": "percentage points",
        "notes": (
            "Mean male-minus-female labour-force participation gap "
            "across available country-year observations, 2019–2023."
        ),
        "is_template": False,
    })

    # Required primary metric.
    write_json(OUTPUTS_DIR / "primary_metric.json", {
        "metric_name": "range_between_income_group_mean_gaps_pp",
        "value": primary_value,
        "threshold": THRESHOLD_PP,
        "passed": passed,
        "unit": "percentage points",
        "notes": (
            "Difference between the largest and smallest income-group "
            "mean gender gaps across available country-year observations."
        ),
        "is_template": False,
    })

    # Keep the milestone manifest aligned with the local-data workflow.
    write_json(OUTPUTS_DIR / "milestone_manifest.json", {
        "charter_locked": False,
        "sources": [
            {
                "name": "Prepared World Bank indicator dataset",
                "status": "local_file",
                "probe_artifact": "artifacts/probes/world_bank_data_access.md",
                "note": (
                    "The analysis uses the committed prepared dataset; "
                    "the script does not make live API requests."
                ),
            }
        ],
        "baseline_ready": True,
        "primary_metric_schema_ready": True,
        "run_command": "uv run main.py",
        "template_warning": (
            "Instructor approval of the charter and permission for "
            "individual submission must be confirmed separately."
        ),
    })

    # Do not overwrite report.md: it is maintained separately on GitHub.
    print(f"Observations: {len(data)}")
    print(f"Countries: {data['iso3'].nunique()}")
    print(f"Overall mean gap: {baseline:.3f} percentage points")
    print(f"Range between income-group means: {primary_value:.3f} pp")
    print(f"Threshold: {THRESHOLD_PP:.1f} pp")
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
    print("\nAnalysis outputs regenerated successfully.")
    print("report.md was not modified.")


if __name__ == "__main__":
    main()


from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"
PROBES_DIR = ROOT / "artifacts" / "probes"

BASE_URL = "https://api.worldbank.org/v2"
START_YEAR = 2019
END_YEAR = 2023
THRESHOLD_PP = 5.0

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
PROBES_DIR.mkdir(parents=True, exist_ok=True)


def get_json(url: str, params: dict, retries: int = 4) -> dict | list:
    """Fetch JSON from the World Bank API with retries."""
    last_error = None

    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=(10, 60),
                headers={"User-Agent": "ECO6810-student-project/1.0"},
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))

    raise RuntimeError(f"API request failed after {retries} attempts: {last_error}")


def fetch_indicator(indicator: str) -> pd.DataFrame:
    """Fetch all pages of one indicator for the selected years."""
    url = f"{BASE_URL}/country/all/indicator/{indicator}"
    params = {
        "date": f"{START_YEAR}:{END_YEAR}",
        "format": "json",
        "per_page": 1000,
        "page": 1,
    }

    first_page = get_json(url, params)

    if not isinstance(first_page, list) or len(first_page) < 2:
        raise RuntimeError(f"Unexpected API response for {indicator}")

    metadata = first_page[0] or {}
    all_rows = list(first_page[1] or [])
    total_pages = int(metadata.get("pages", 1))

    for page_number in range(2, total_pages + 1):
        page_params = {**params, "page": page_number}
        payload = get_json(url, page_params)

        if isinstance(payload, list) and len(payload) > 1:
            all_rows.extend(payload[1] or [])

    records = []
    for row in all_rows:
        value = row.get("value")
        country_code = row.get("countryiso3code")
        year = row.get("date")

        if value is None or not country_code or not year:
            continue

        records.append({
            "iso3": country_code,
            "year": int(year),
            indicator: float(value),
        })

    result = pd.DataFrame(records)

    if result.empty:
        raise RuntimeError(f"No observations returned for {indicator}")

    if result.duplicated(["iso3", "year"]).any():
        raise RuntimeError(f"Duplicate country-year records for {indicator}")

    return result


def fetch_countries() -> pd.DataFrame:
    """Retrieve country metadata and exclude regional aggregates."""
    url = f"{BASE_URL}/country"
    params = {"format": "json", "per_page": 400, "page": 1}

    first_page = get_json(url, params)

    if not isinstance(first_page, list) or len(first_page) < 2:
        raise RuntimeError("Unexpected response from the Countries API")

    metadata = first_page[0] or {}
    rows = list(first_page[1] or [])

    for page_number in range(2, int(metadata.get("pages", 1)) + 1):
        payload = get_json(url, {**params, "page": page_number})
        if isinstance(payload, list) and len(payload) > 1:
            rows.extend(payload[1] or [])

    records = []
    for row in rows:
        region = (row.get("region") or {}).get("value")
        income = (row.get("incomeLevel") or {}).get("value")
        iso3 = row.get("id")

        if (
            iso3
            and region
            and region != "Aggregates"
            and income
            and income != "Aggregates"
        ):
            records.append({
                "iso3": iso3,
                "country": row.get("name", iso3),
                "region": region,
                "income_group": income,
            })

    result = pd.DataFrame(records).drop_duplicates("iso3")

    if result.empty:
        raise RuntimeError("No usable country metadata returned")

    return result


def write_json(path: Path, payload: dict) -> None:
    """Write a JSON object to disk."""
    path.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    print("Retrieving World Bank data...")

    male = fetch_indicator("SL.TLF.CACT.MA.ZS")
    female = fetch_indicator("SL.TLF.CACT.FE.ZS")
    countries = fetch_countries()

    # Merge on country code and year, then attach current income groups.
    data = male.merge(
        female,
        on=["iso3", "year"],
        how="inner",
        validate="one_to_one",
    )

    data = data.merge(
        countries,
        on="iso3",
        how="inner",
        validate="many_to_one",
    )

    data["gender_gap_pp"] = (
        data["SL.TLF.CACT.MA.ZS"] - data["SL.TLF.CACT.FE.ZS"]
    )

    data = (
        data.dropna(subset=["gender_gap_pp", "income_group"])
        .sort_values(["iso3", "year"])
        .reset_index(drop=True)
    )

    if data.empty:
        raise RuntimeError("No valid country-year observations remain")

    # Save the country-year dataset.
    data.to_csv(DATA_DIR / "country_year_gender_gap.csv", index=False)

    # Main descriptive results by income group.
    summary = (
        data.groupby("income_group")
        .agg(
            observations=("gender_gap_pp", "count"),
            mean_gap_pp=("gender_gap_pp", "mean"),
            sd_country_year=("gender_gap_pp", "std"),
            countries=("iso3", "nunique"),
        )
        .reset_index()
        .sort_values("mean_gap_pp", ascending=False)
        .reset_index(drop=True)
    )

    summary["standard_error_country_year"] = (
        summary["sd_country_year"] / summary["observations"].pow(0.5)
    )

    summary.to_csv(OUTPUTS_DIR / "income_group_summary.csv", index=False)

    # Annual trends by income group.
    annual = (
        data.groupby(["year", "income_group"])["gender_gap_pp"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={
            "mean": "mean_gap_pp",
            "count": "observations",
        })
    )

    annual.to_csv(OUTPUTS_DIR / "annual_income_group_trends.csv", index=False)

    # Robustness check: first average years within each country,
    # then give each country equal weight within its current income group.
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
        country_summary["country_sd"] /
        country_summary["countries"].pow(0.5)
    )

    country_summary.to_csv(
        OUTPUTS_DIR / "country_level_robustness.csv",
        index=False,
    )

    # The charter's primary metric: range between income-group means.
    baseline = float(data["gender_gap_pp"].mean())
    primary_value = float(
        summary["mean_gap_pp"].max() - summary["mean_gap_pp"].min()
    )
    passed = bool(primary_value >= THRESHOLD_PP)

    # Figure 1: mean gender gap by income group.
    ordered = summary.sort_values("mean_gap_pp")

    plt.figure(figsize=(9, 5))
    plt.bar(
        ordered["income_group"],
        ordered["mean_gap_pp"],
        yerr=1.96 * ordered["standard_error_country_year"],
        capsize=4,
    )
    plt.axhline(
        baseline,
        linestyle="--",
        label=f"Overall country-year mean ({baseline:.2f} pp)",
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
    plt.figure(figsize=(9, 5))
    for group, group_data in annual.groupby("income_group"):
        group_data = group_data.sort_values("year")
        plt.plot(
            group_data["year"],
            group_data["mean_gap_pp"],
            marker="o",
            label=group,
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

    # Required baseline JSON: preserve the professor's minimum schema.
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

    # Required primary JSON: the key field is named 'passed'.
    write_json(OUTPUTS_DIR / "primary_metric.json", {
        "metric_name": "range_between_income_group_mean_gaps_pp",
        "value": primary_value,
        "threshold": THRESHOLD_PP,
        "passed": passed,
        "unit": "percentage points",
        "notes": (
            "Difference between the largest and smallest income-group "
            "means across available country-year observations."
        ),
        "is_template": False,
    })

    # A probe artifact records the successful data-access check.
    probe_text = f"""# World Bank data access probe

Date generated by project run: see the Git commit history.

The project retrieves the following indicators through the World Bank API:

- Male labour-force participation: SL.TLF.CACT.MA.ZS
- Female labour-force participation: SL.TLF.CACT.FE.ZS
- Country metadata and current income groups: World Bank Countries API

The main script retrieves the 2019–2023 observations and stops with an
error if a required API response cannot be parsed or no usable data remain.

This file documents the source and method; the actual retrieval is performed
by `main.py`.
"""
    (PROBES_DIR / "world_bank_data_access.md").write_text(
        probe_text, encoding="utf-8"
    )

    # Required milestone manifest: preserve the starter template's fields.
    write_json(OUTPUTS_DIR / "milestone_manifest.json", {
        "charter_locked": False,
        "sources": [
            {
                "name": "World Bank World Development Indicators API",
                "status": "ok",
                "probe_artifact": "artifacts/probes/world_bank_data_access.md",
                "note": (
                    "The main script retrieves both labour-force "
                    "participation indicators for 2019–2023."
                ),
            },
            {
                "name": "World Bank Countries API",
                "status": "ok",
                "probe_artifact": "artifacts/probes/world_bank_data_access.md",
                "note": "Provides country names, regions, and current income groups.",
            },
        ],
        "baseline_ready": True,
        "primary_metric_schema_ready": True,
        "run_command": "uv run main.py",
        "template_warning": (
            "The code now generates real analysis outputs. Instructor "
            "approval of the charter and individual-submission permission "
            "remain pending."
        ),
    })

    # Build the Markdown results table as a separate string.
    table_rows = "\n".join(
        f"| {row['income_group']} | "
        f"{int(row['observations'])} | "
        f"{int(row['countries'])} | "
        f"{row['mean_gap_pp']:.2f} |"
        for _, row in summary.iterrows()
    )

    country_table_rows = "\n".join(
        f"| {row['income_group']} | "
        f"{int(row['countries'])} | "
        f"{row['equal_country_mean_gap_pp']:.2f} |"
        for _, row in country_summary.iterrows()
    )

    report = f"""# Gender Gaps in Labour-Force Participation

## Research question

How does the gender gap in labour-force participation vary across World
Bank income groups, and how did the pattern change from 2019 to 2023?

## Why this question matters

Labour-force participation is one dimension of access to economic activity.
Comparing participation rates can help identify where male and female
participation differs. The analysis describes these differences; it does
not establish their causes.

## Data and measurement

The analysis uses World Bank World Development Indicators for male
(`SL.TLF.CACT.MA.ZS`) and female (`SL.TLF.CACT.FE.ZS`) labour-force
participation rates among people aged 15 and above. The period is
{START_YEAR}–{END_YEAR}. The gender gap is calculated as the male rate
minus the female rate and is measured in percentage points.

The merged dataset contains {len(data)} country-year observations from
{data['iso3'].nunique()} countries. Income groups are taken from the
World Bank Countries API at the time the data are retrieved.

## Main result

The overall mean gender gap is **{baseline:.2f} percentage points**.
The range between the largest and smallest income-group mean gaps is
**{primary_value:.2f} percentage points**. The pre-specified threshold
of {THRESHOLD_PP:.1f} percentage points is
**{"met" if passed else "not met"}**.

| Income group | Country-year observations | Countries | Mean gap (pp) |
|---|---:|---:|---:|
{table_rows}

See `outputs/gender_gap_by_income_group.png` for the group comparison.

## Changes over time

The annual group means are saved in
`outputs/annual_income_group_trends.csv` and visualised in
`outputs/gender_gap_trends_2019_2023.png`. These trends are descriptive:
differences between years can reflect changing participation, data revisions,
or changes in the set of countries with available observations.

## Robustness check: equal country weights

The main summary averages available country-year observations, so a country
with more observed years can contribute more to the mean. As a robustness
check, the analysis first averages the gender gap within each country and
then gives each country equal weight within its current income group.

| Income group | Countries | Equal-country mean gap (pp) |
|---|---:|---:|
{country_table_rows}

The equal-country results are saved in
`outputs/country_level_robustness.csv`. Comparing these values with the
main table shows whether the broad pattern is sensitive to country weighting.

## Interpretation

The results describe differences in observed labour-force participation
gaps across income groups. They do not show that national income levels
cause those differences. Factors such as labour-market structure, education,
care responsibilities, institutions, and measurement may matter, but this
project does not identify their separate contributions.

## Limitations

First, the income-group classification returned by the API is applied to
all years rather than using historical income classifications. Second,
the country-year sample is unbalanced because some indicators are missing
for some years. Third, repeated observations from the same country are not
independent. The standard errors in the first figure are simple descriptive
standard errors, not country-clustered confidence intervals. Finally,
country-level averages cannot explain individual participation decisions.

## Reproducibility

Run `uv sync` and then `uv run main.py`. The script retrieves the data and
regenerates the dataset, summary tables, figures, metric JSON files,
milestone manifest, and this report.
"""

    (ROOT / "report.md").write_text(report, encoding="utf-8")

    print(f"Country-year observations: {len(data)}")
    print(f"Unique countries: {data['iso3'].nunique()}")
    print(f"Overall baseline: {baseline:.3f} percentage points")
    print(f"Range between group means: {primary_value:.3f} percentage points")
    print(f"Threshold met: {passed}")
    print(f"Income groups meeting n >= 10: {int((summary['observations'] >= 10).sum())}")
    print("Generated data/, outputs/, and report.md")


if __name__ == "__main__":
    main()

# Gender Gaps in Labour-Force Participation Across Income Groups

## 1. Question

This project examines how the gender gap in labour-force participation varies across World Bank income groups and how it changed between 2019 and 2023. The question matters because differences in participation can reflect unequal access to economic opportunities. The descriptive findings can help identify income groups where the gap is relatively large, although they do not establish why these differences occur.

## 2. Charter Summary

- **Project type:** Descriptive empirical analysis.
- **Main metric:** Range between the highest and lowest income-group mean gender gaps, measured in percentage points.
- **Success threshold:** At least 5 percentage points.
- **Baseline:** Overall mean gender gap of 19.092 percentage points.

The primary metric measures the spread in average gender gaps across income groups. It does not measure the causal effect of income on gender inequality.

## 3. Data

The analysis uses World Bank labour-force participation indicators for males and females aged 15 and above:

- Male labour-force participation rate: `SL.TLF.CACT.MA.ZS`.
- Female labour-force participation rate: `SL.TLF.CACT.FE.ZS`.
- Country names, regions, and income classifications: World Bank country metadata.

The indicator data were obtained from DataHub's World Development Indicators datasets, while country metadata were obtained from the World Bank country information source. The prepared files were brought into the project as CSV files and combined in the existing Colab workflow. The final analysis script reads the committed `data/analysis_dataset.csv` file, so rerunning the analysis does not require a live API connection.

The analysis covers 2019–2023 and contains 931 country-year observations across 187 countries. The dataset is unbalanced because some countries have missing indicator observations in particular years. The income-group classification in the prepared dataset is used consistently throughout the analysis; it should not be interpreted as a historical classification for every year.

Source and access notes are documented in `data/README.md` and `artifacts/probes/world_bank_data_access.md`.

## 4. Method

The outcome variable is the gender gap in labour-force participation:

**Gender gap = Male participation rate − Female participation rate.**

The measure is expressed in percentage points. A positive value indicates that male participation exceeds female participation.

The baseline is the mean gender gap across all available country-year observations. The main analysis calculates the mean gap separately for each of the four World Bank income groups: high income, upper-middle income, lower-middle income, and low income. The primary metric is the difference between the largest and smallest of these four means.

Country-clustered standard errors are calculated for the income-group means to account for potential dependence between repeated observations from the same country. A further robustness check first averages the gap within each country and then gives each country equal weight within its income group. Annual means are also calculated to describe changes over time.

This is a descriptive design, not a causal one. No treatment effect or causal relationship is estimated.

## 5. Result

- **Main metric value:** 7.097 percentage points.
- **Threshold:** 5 percentage points.
- **Passed:** Yes.

The difference between the largest and smallest income-group mean gaps is approximately 7.10 percentage points, exceeding the pre-specified threshold by approximately 2.10 percentage points.

The overall mean gender gap is 19.092 percentage points. The largest group mean is observed in upper-middle-income countries, at approximately 22.735 percentage points, while the smallest is observed in high-income countries, at approximately 15.638 percentage points.

| Income group | Country-year observations | Countries | Mean gap (pp) | Country-clustered SE |
|---|---:|---:|---:|---:|
| Upper-middle income | 263 | 53 | 22.735 | 1.758 |
| Lower-middle income | 229 | 46 | 20.304 | 2.268 |
| Low income | 124 | 25 | 17.902 | 3.314 |
| High income | 315 | 63 | 15.638 | 1.278 |

The results show descriptive differences across income groups. They do not establish that a country's income level causes its gender gap to be larger or smaller.

## 6. Evidence

The following outputs support the findings:

- `outputs/baseline_metric.json` records the overall mean gender gap.
- `outputs/primary_metric.json` records the primary metric, the 5-percentage-point threshold, and the threshold result.
- `outputs/income_group_summary.csv` contains income-group means, observation counts, country counts, and standard errors.
- `outputs/gender_gap_by_income_group.png` visualises the income-group comparison, including country-clustered standard errors.
- `outputs/annual_trend.csv` records the overall annual means.
- `outputs/annual_income_group_trends.csv` and `outputs/gender_gap_trends_2019_2023.png` show annual patterns by income group.
- `outputs/country_level_robustness.csv` reports the equal-country-weight robustness check.

The annual overall mean gap was approximately 19.454 percentage points in 2019, 19.144 in 2020, 18.939 in 2021, 19.219 in 2022, and 18.698 in 2023. The overall gap therefore declined between the beginning and end of the period, although the movement was not monotonic.

## 7. Limits

First, the analysis is descriptive and cannot identify causal effects. Second, the country-year sample is unbalanced, so the countries contributing to the annual averages are not identical in every year. Third, the income classifications are taken from the prepared dataset and are not reconstructed historically for each year. Fourth, the analysis uses country-level participation rates and cannot explain individual labour-market decisions.

The clustered standard errors allow for within-country dependence in repeated observations, but they do not remove confounding or resolve every issue associated with the sample. Differences across income groups may reflect many factors, including education, labour-market structure, care responsibilities, institutions, and measurement. This project does not separately identify those mechanisms.

## 8. If the Result Was Null or Weak

The primary result is not null under the pre-specified threshold: the range of income-group mean gaps is 7.097 percentage points, above the 5-point threshold. However, passing this threshold establishes only that the observed group means differ by the specified amount. It does not establish statistical significance for every pairwise comparison or a causal explanation for the differences.

The result should therefore be interpreted as evidence of descriptive variation across income groups, rather than proof that income classification itself determines gender inequality.

## 9. Reproducibility

- **Run command:** `uv sync` followed by `uv run main.py`.
- **Runtime:** Approximately 15 seconds for the analysis job and 20 seconds for the complete GitHub Actions run in the verified execution.
- **Input dataset:** `data/analysis_dataset.csv`.
- **Output files:** `data/country_year_gender_gap.csv`; `outputs/baseline_metric.json`; `outputs/primary_metric.json`; `outputs/income_group_summary.csv`; `outputs/annual_trend.csv`; `outputs/annual_income_group_trends.csv`; `outputs/country_level_robustness.csv`; `outputs/gender_gap_by_income_group.png`; `outputs/gender_gap_trends_2019_2023.png`; and `outputs/milestone_manifest.json`.

The GitHub Actions workflow successfully ran the analysis and uploaded its generated outputs as an artifact. The analysis script does not overwrite this report.

## 10. AI Usage

AI assistance was used to help structure and debug the Python analysis, prepare the GitHub Actions workflow, interpret execution errors, and organise the report. The analysis results were checked against the successful GitHub Actions logs, including the observation count, country count, overall mean gap, primary metric, threshold, and income-group results.

The detailed record of AI assistance and manual checks is provided in [AI_USAGE_LOG.md](./AI_USAGE_LOG.md). The project team should ensure this section accurately reflects all assistance used and all checks actually performed.

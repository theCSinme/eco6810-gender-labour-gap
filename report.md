# Gender Gaps in Labour-Force Participation Across Income Groups

## 1. Research Question

This project examines how the gender gap in labour-force participation varies across World Bank income groups and how it changed between 2019 and 2023. Differences in participation can reflect unequal access to economic opportunities, differences in labour-market structures, and other social and institutional factors.

The objective is to document differences in the gender gap across income groups and describe changes over time. The analysis is descriptive and does not attempt to identify the causal effect of income on gender inequality.

## 2. Project Charter Summary

- **Project type:** Descriptive empirical analysis.
- **Main metric:** Range between the highest and lowest income-group mean gender gaps, measured in percentage points.
- **Success threshold:** At least 5 percentage points.
- **Baseline metric:** Overall mean gender gap of 19.092 percentage points.
- **Study period:** 2019–2023.

The primary metric measures the spread in average gender gaps across the four income groups. Passing the threshold indicates that the observed range meets the project's pre-specified benchmark. It does not establish statistical significance or causality.

## 3. Data

### 3.1 Data Sources

The analysis uses World Bank World Development Indicators on labour-force participation among males and females aged 15 and above.

The principal indicators are:

- Male labour-force participation rate: `SL.TLF.CACT.MA.ZS`
- Female labour-force participation rate: `SL.TLF.CACT.FE.ZS`

Country names and income-group classifications are obtained from World Bank country metadata. The indicator datasets were accessed through DataHub's World Development Indicators datasets, while country metadata were obtained from the World Bank country information source.

The prepared dataset is stored in `data/analysis_dataset.csv`. Raw indicator and metadata files are stored in `data/raw/`. Source and access information is documented in `data/README.md` and `artifacts/probes/world_bank_data_access.md`.

### 3.2 Sample and Coverage

The prepared dataset contains 931 country-year observations across 187 unique country identifiers for 2019–2023. The panel is unbalanced because some countries have missing observations in particular years.

The analysis uses the income-group classifications contained in the prepared dataset. These classifications are held constant throughout the study period and should not be interpreted as historical classifications reconstructed separately for every year.

Searches were conducted for several common aggregate labels, including `World`, `European Union`, `Sub-Saharan Africa`, and `WLD`. These searches returned no matches. However, these checks were not exhaustive, and the dataset has not been comprehensively validated against all possible regional or aggregate entries. The reported sample therefore reflects the prepared dataset used by the analysis script.

### 3.3 Data Preparation

The analysis script reads `data/analysis_dataset.csv`, converts the year and participation-rate variables to numeric values, removes observations with missing values in required analysis variables, and restricts the sample to 2019–2023. It calculates the gender gap as the difference between male and female participation rates and checks for duplicate country-year identifiers.

The script also validates that participation rates fall between 0 and 100. The analysis can be reproduced from the committed prepared dataset without requiring a live API connection.

## 4. Methodology

### 4.1 Outcome Variable

The outcome variable is the gender gap in labour-force participation:

**Gender gap = Male labour-force participation rate − Female labour-force participation rate**

The measure is expressed in percentage points. A positive value indicates that male labour-force participation exceeds female labour-force participation. A larger positive value indicates a wider gap in favour of male participation.

### 4.2 Baseline and Primary Metric

The baseline is the mean gender gap across all available country-year observations.

The main analysis calculates the mean gender gap separately for the four World Bank income groups:

1. High income
2. Upper-middle income
3. Lower-middle income
4. Low income

The primary metric is the difference between the largest and smallest income-group means:

**Primary metric = Maximum income-group mean − Minimum income-group mean**

The project's success threshold is 5 percentage points. The threshold is passed if the primary metric is at least 5 percentage points.

### 4.3 Standard Errors and Robustness

Country-clustered standard errors are calculated for the income-group means to account for potential dependence between repeated observations from the same country.

The analysis also calculates a robustness measure that first averages the gender gap within each country and then gives each country equal weight within its income group. Annual means are calculated to describe changes over time and differences in trends across income groups.

This is a descriptive design. It does not estimate a treatment effect, identify a causal mechanism, or control for all potential confounding factors.

## 5. Results

### 5.1 Primary Result

The primary metric is **7.097 percentage points**, exceeding the pre-specified threshold of 5 percentage points by approximately 2.097 percentage points.

The overall mean gender gap is **19.092 percentage points**.

The largest income-group mean is observed in upper-middle-income countries, at approximately 22.735 percentage points. The smallest is observed in high-income countries, at approximately 15.638 percentage points.

The primary threshold is therefore passed. This indicates that the range between the observed income-group means exceeds the project's chosen benchmark. It does not establish that every pairwise difference is statistically significant.

### 5.2 Income-Group Comparison

| Income group | Country-year observations | Countries | Mean gender gap (pp) | Country-clustered SE |
|---|---:|---:|---:|---:|
| Upper-middle income | 263 | 53 | 22.735 | 1.758 |
| Lower-middle income | 229 | 46 | 20.304 | 2.268 |
| Low income | 124 | 25 | 17.902 | 3.314 |
| High income | 315 | 63 | 15.638 | 1.278 |

The results show descriptive variation across income groups. Upper-middle-income countries have the largest mean gap, followed by lower-middle-income countries and low-income countries. High-income countries have the smallest mean gap in this sample.

These patterns should not be interpreted as evidence that moving to a higher income group necessarily reduces the gender gap. The analysis does not isolate the influence of income from other differences across countries.

### 5.3 Changes Over Time

The overall annual mean gender gap was approximately:

| Year | Mean gender gap (pp) | Country-year observations |
|---|---:|---:|
| 2019 | 19.454 | 187 |
| 2020 | 19.144 | 187 |
| 2021 | 18.939 | 187 |
| 2022 | 19.219 | 186 |
| 2023 | 18.698 | 184 |

The overall mean gap declined between 2019 and 2023, from approximately 19.454 to 18.698 percentage points. The change was not monotonic: the mean gap increased between 2021 and 2022 before declining again in 2023.

Because the panel is unbalanced, the countries contributing to annual averages are not identical in every year. Income-group classifications are also held constant across the study period. Consequently, the annual patterns are descriptive and should not be interpreted as a causal trend.

## 6. Evidence and Outputs

The following generated files support the findings:

- `outputs/baseline_metric.json` records the overall mean gender gap.
- `outputs/primary_metric.json` records the primary metric, success threshold, and threshold result.
- `outputs/income_group_summary.csv` contains income-group means, observation counts, country counts, and standard errors.
- `outputs/gender_gap_by_income_group.png` compares mean gender gaps across income groups.
- `outputs/annual_trend.csv` records annual overall mean gaps.
- `outputs/annual_income_group_trends.csv` contains annual patterns by income group.
- `outputs/gender_gap_trends_2019_2023.png` visualises annual trends.
- `outputs/country_level_robustness.csv` reports the equal-country-weight robustness check.
- `outputs/milestone_manifest.json` records analysis milestone information.

The income-group figure displays error bars calculated as the mean plus or minus 1.96 country-clustered standard errors. These are approximate intervals and should not automatically be interpreted as exact small-sample 95% confidence intervals, particularly for groups with fewer country clusters.

## 7. Limitations

Several limitations qualify the findings.

First, the analysis is descriptive and cannot identify causal effects. Differences across income groups may reflect education, labour-market structure, care responsibilities, institutions, social norms, and other factors that are not separately examined.

Second, the country-year panel is unbalanced. The countries contributing to annual averages are not identical in every year, which may affect comparisons over time.

Third, income-group classifications are taken from the prepared dataset and are held constant across the study period rather than reconstructed historically for each year.

Fourth, the outcome is a country-level participation-rate difference. It does not explain individual labour-market decisions or differences among demographic groups within countries.

Fifth, country-clustered standard errors account for potential dependence between observations from the same country, but they do not remove confounding. Their precision should also be interpreted cautiously given the number of country clusters within each income group.

Finally, the aggregate-label searches covered several common labels but did not constitute a comprehensive validation against the full source metadata. Further validation would provide stronger assurance that all retained observations correspond to the intended country-level units.

## 8. If the Result Were Null or Weak

The primary result is not null under the project's pre-specified threshold: the range of income-group mean gender gaps is 7.097 percentage points, exceeding the 5-percentage-point benchmark.

However, passing this threshold establishes only that the observed range meets the chosen descriptive criterion. It does not establish statistical significance for every pairwise comparison, identify the mechanisms behind the differences, or demonstrate that income classification causes gender inequality.

If the observed range had fallen below the threshold, the project would not have met its pre-specified descriptive success criterion. That outcome would not necessarily imply that the true gaps were identical; it would mean only that the chosen metric did not reach the specified benchmark in the available sample.

## 9. Reproducibility

The analysis can be reproduced from the repository using the following commands:

```bash
uv sync
uv run main.py
```

The script reads `data/analysis_dataset.csv` and generates the analysis tables, figures, JSON metrics, and milestone manifest. It also writes `data/country_year_gender_gap.csv`.

The expected outputs include:

- `data/country_year_gender_gap.csv`
- `outputs/baseline_metric.json`
- `outputs/primary_metric.json`
- `outputs/income_group_summary.csv`
- `outputs/annual_trend.csv`
- `outputs/annual_income_group_trends.csv`
- `outputs/country_level_robustness.csv`
- `outputs/gender_gap_by_income_group.png`
- `outputs/gender_gap_trends_2019_2023.png`
- `outputs/milestone_manifest.json`

Additional output documentation is available in `outputs/README.md`.

The GitHub Actions workflow completed successfully and uploaded the generated analysis outputs as an artifact. The generated outputs were subsequently committed to the repository. The report is maintained separately and is not automatically overwritten by the analysis script.

The workflow's displayed runtime varies by execution. The most recent successful run completed in approximately 12 seconds overall.

## 10. AI Usage and Research Responsibility

AI assistance was used to help structure and debug the Python analysis, prepare the GitHub Actions workflow, interpret execution errors, and organise the report. The reported results were checked against the successful GitHub Actions logs, including the observation count, country count, overall mean gender gap, primary metric, success threshold, and income-group summaries.

The detailed record of AI assistance and verification activities is provided in `AI_USAGE_LOG.md`. The author remains responsible for the data, code, interpretation, source attribution, and final presentation of the analysis. Remaining validation limitations should be resolved or disclosed before submission.

## Conclusion

This project documents differences in labour-force participation gender gaps across World Bank income groups from 2019 to 2023. The overall mean gap is 19.092 percentage points, while the range between income-group means is 7.097 percentage points, exceeding the project's 5-percentage-point success threshold. Upper-middle-income countries have the largest observed mean gap, and high-income countries have the smallest.

The annual overall mean gap declines between 2019 and 2023, although the path is not monotonic. These findings provide a descriptive account of cross-group differences and changes over time. They do not establish that income causes differences in gender inequality. The results should be interpreted alongside the limitations of the unbalanced panel, fixed income-group classifications, country-level outcome measure, and remaining need for comprehensive aggregate validation.

# Project Charter: Gender Gaps in Labour-Force Participation

## 1. Project overview

**Project title:** Gender Gaps in Labour-Force Participation Across Income Groups

**Course:** ECO6810

**Study period:** 2019–2023

**Geographical coverage:** Countries with usable World Bank indicator observations and country metadata.

**Project status:** Analysis completed; instructor approval of the charter and permission for individual submission remain pending.

## 2. Research question

How does the gender gap in labour-force participation vary across World Bank income groups, and how did the pattern change from 2019 to 2023?

## 3. Motivation

Labour-force participation is an important dimension of economic activity. Differences between male and female participation rates provide a descriptive measure of gender inequality in participation.

Comparing these gaps across income groups can establish whether the observed differences are small or substantial. Examining annual patterns can also show whether the gaps changed over the study period.

The project does not assume that national income causes these differences.

## 4. Data sources

The project uses World Bank World Development Indicators:

- Male labour-force participation rate, ages 15 and above: `SL.TLF.CACT.MA.ZS`
- Female labour-force participation rate, ages 15 and above: `SL.TLF.CACT.FE.ZS`

Country names, regions, and income groups are obtained from World Bank country metadata.

The study period is 2019–2023. The prepared dataset, `data/analysis_dataset.csv`, is retained in the repository and used as the input to the final analysis script. Source files and data-access documentation are also retained in the repository.

## 5. Variables and measurement

The main outcome is the gender gap in labour-force participation, measured in percentage points.

**Gender gap = Male participation rate − Female participation rate.**

A positive value indicates higher male participation.

The main grouping variable is the World Bank income group. Year is used to describe changes over time.

## 6. Primary metric

The primary metric is the range between the largest and smallest income-group mean gender gaps.

**Primary metric = Maximum income-group mean gap − Minimum income-group mean gap.**

The pre-specified threshold is 5 percentage points.

The threshold is a project comparison benchmark, not a statistical significance test.

## 7. Empirical strategy

The analysis will:

1. Load the prepared country-year dataset containing male and female participation indicators.
2. Validate country identifiers, years, indicator values, and income-group classifications.
3. Calculate the male-minus-female participation gap.
4. Report the overall mean gap.
5. Compare mean gaps across income groups.
6. Describe annual changes from 2019 to 2023.
7. Conduct an equal-country-weight robustness check by first averaging observations within each country.
8. Save tables, figures, and machine-readable metric outputs.

Country-clustered standard errors are calculated for income-group means to allow for dependence between repeated observations from the same country. The equal-country-weight robustness check provides a separate descriptive comparison and does not establish causality.

## 8. Main results

The prepared analysis dataset contains 931 country-year observations from 187 countries.

The overall mean gender gap is approximately 19.092 percentage points.

The mean gap is approximately 22.735 percentage points in the upper-middle-income group and 15.638 percentage points in the high-income group.

The difference between the largest and smallest group means is approximately 7.097 percentage points, above the 5-percentage-point threshold.

The threshold is therefore met. These values are descriptive and should be interpreted alongside the generated tables and figures.

## 9. Limitations

- The country-year panel is unbalanced.
- Current income-group classifications are applied to historical observations.
- Repeated observations within countries may be dependent.
- Country-clustered standard errors account for within-country dependence but do not resolve confounding or identify causal effects.
- Aggregate country-level data cannot explain individual decisions or within-country differences.
- Differences between income groups may reflect several factors that this project does not separately identify.

## 10. Reproducibility

The intended run commands are:

`uv sync`

`uv run main.py`

The repository should contain the prepared input data, source documentation, analysis script, generated outputs, and final report. The GitHub Actions workflow has successfully executed the analysis using the committed dataset.

## 11. Submission and approval status

The analysis has been prepared as an individual project. Permission to submit individually and approval of the project charter must be obtained from the instructor.

No approval is claimed until it has been received.

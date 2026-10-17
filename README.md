
# Gender Gaps in Labour-Force Participation

## Project overview

This project examines how the gender gap in labour-force participation varies across World Bank income groups and how the gap changed between 2019 and 2023.

The analysis uses World Bank World Development Indicators (WDI) data for male and female labour-force participation rates among people aged 15 and above.

## Research question

How does the gender gap in labour-force participation vary across World Bank income groups, and how did the pattern change from 2019 to 2023?

## Measurement

The gender gap is defined as:

Gender gap (percentage points) = Male labour-force participation rate − Female labour-force participation rate.

A positive value indicates that the male participation rate exceeds the female participation rate.

The primary metric is the difference between the highest and lowest income-group mean gender gaps. The pre-specified comparison threshold is 5 percentage points.

## Main findings

The analysis dataset contains 931 country-year observations from 187 countries over 2019–2023.

- Overall mean gender gap: 19.09 percentage points.
- Highest income-group mean: Upper middle income, approximately 22.73 percentage points.
- Lowest income-group mean: High income, approximately 15.64 percentage points.
- Range between the highest and lowest income-group means: approximately 7.10 percentage points.
- The primary metric exceeds the 5-percentage-point threshold.

These are descriptive results. They do not establish that income levels cause differences in gender gaps.

## Repository structure

- `main.py`: Main analysis script.
- `data/`: Analysis dataset, raw source files, and data documentation.
- `outputs/`: Summary tables, annual trends, robustness checks, figures, and metric JSON files.
- `artifacts/probes/`: Data-source documentation.
- `CHARTER.md`: Research plan and project status.
- `report.md`: Written research report.
- `AI_USAGE_LOG.md`: Record of AI assistance.

## Data sources

The analysis uses the following World Bank indicators:

- Male labour-force participation rate: `SL.TLF.CACT.MA.ZS`
- Female labour-force participation rate: `SL.TLF.CACT.FE.ZS`

The World Bank Countries API provides country metadata and income-group classifications.

The source data and documentation are retained in `data/`.

## Reproducibility

The intended command is:

```bash
uv sync
uv run main.py
```

The script should regenerate the analysis outputs from the committed input data. Verify the command in a clean environment before submission.

## Limitations

- The panel is unbalanced because indicator observations are not available for every country and year.
- Current income-group classifications are used for the historical period.
- Country-year observations from the same country may be correlated.
- The results are descriptive and do not establish causal relationships.
- Country-level averages cannot explain individual labour-force participation decisions.

## Project status

The charter and permission for individual submission require instructor confirmation. These approvals must not be represented as complete until they have been granted.

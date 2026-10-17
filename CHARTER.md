# Project Charter — Gender Gaps in Labour-Force Participation

## Header

| Field | Value |
|---|---|
| Team members | Jaishree Tomar — individual submission, pending instructor approval |
| Project type | Descriptive |
| Estimated hours per person | To be updated based on actual hours worked |
| Charter version | v1 — proposed |
| Date | 2026-10-01 |

## 1. Problem and stakeholder

This project examines how the gender gap in labour-force participation differs across World Bank income groups. The findings may be useful to researchers and organisations working on gender equality and labour-market inclusion. The analysis will identify differences across countries without claiming to establish their causes.

## 2. Main outcome variable

The main outcome is the gender gap in labour-force participation, measured in percentage points. For each country-year observation, it is calculated as the male participation rate minus the female participation rate among people aged 15 and above. The planned indicators are World Bank WDI series `SL.TLF.CACT.MA.ZS` and `SL.TLF.CACT.FE.ZS`. The proposed sample covers 2019–2023, subject to data availability, with countries classified by World Bank income group.

## 3. Main quantitative success threshold

The project will aim to report mean gender-gap estimates and standard errors for at least three income groups, with at least 10 valid country-year observations per included group. The sample sizes and uncertainty measures will be reported alongside the estimates. This threshold assesses analytical completeness, not whether the hypothesis is supported.

## 4. Baseline to beat

The baseline is the overall mean gender gap across all valid country-year observations in the sample. The income-group estimates will be compared with this overall mean.

## 5. Falsifiable hypothesis

The mean gender gap differs across World Bank income groups, with a difference of at least five percentage points between the group with the largest mean gap and the group with the smallest mean gap.

## 6. Data sources and access plan

The project will use the World Bank World Development Indicators API for male and female labour-force participation rates and the World Bank Countries API for income-group classifications. Python will be used to retrieve and process the data. The analysis will document the data sources, indicator definitions, retrieval date, and missing observations. The proposed indicators and sample will be verified before finalising the analysis.

## 7. Scope limits

- The project is descriptive and does not estimate causal effects.
- It does not establish why gender gaps arise.
- Missing observations and differences in data coverage may affect comparisons.
- Income-group classifications may not reflect historical classifications for every year.
- Country-level results cannot establish patterns for individual workers.

## 8. Risks and fallback

The main risk is insufficient data coverage for some countries or income groups. If fewer than three groups meet the sample-size threshold, the project will document this limitation and reconsider the sample period or scope. Missing values will not be replaced with invented observations.

## 9. Reproducibility checklist

- [ ] `uv run main.py` runs the analysis end-to-end.
- [ ] `outputs/primary_metric.json` contains the computed primary metric and threshold status.
- [ ] `outputs/baseline_metric.json` contains the computed baseline.
- [ ] `outputs/milestone_manifest.json` records the actual project status.
- [ ] `README.md` contains reproducible setup and run instructions.
- [ ] The data retrieval process and source information are documented.

## Sign-off

Status: Proposed. Instructor approval and permission for an individual submission are pending.

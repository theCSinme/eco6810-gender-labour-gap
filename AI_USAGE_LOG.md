# AI Usage Log

## Project

Gender Gaps in Labour-Force Participation Across Income Groups

## Purpose of AI Assistance

ChatGPT was used as a supplementary tool during project development to support coding, debugging, interpretation, documentation, and reproducibility.

## Tasks for Which AI Assistance Was Used

- Clarifying the research question, descriptive analysis structure, and primary metric.
- Discussing the construction and interpretation of the male-minus-female labour-force participation gap in percentage points.
- Assisting with the organization and debugging of the Python analysis script.
- Implementing country-clustered standard errors for income-group mean comparisons.
- Reviewing descriptive statistics, annual trends, and the equal-country-weight robustness check.
- Interpreting execution errors and configuring a GitHub Actions workflow to run the analysis.
- Improving the organization and clarity of the project report, charter, and data documentation.
- Identifying limitations and avoiding unsupported causal claims.

## Verification and Human Responsibility

The analysis was executed through GitHub Actions using the committed prepared dataset. The execution logs were checked for the number of country-year observations, number of countries, overall mean gender gap, range between income-group means, threshold result, and income-group summary statistics.

The successful run reported 931 country-year observations across 187 countries, an overall mean gap of approximately 19.092 percentage points, and a range between income-group mean gaps of approximately 7.097 percentage points. The pre-specified threshold of 5 percentage points was met.

AI assistance does not replace responsibility for understanding the methodology, verifying calculations and source documentation, checking the generated files, and being able to explain the results independently.

## Limitations

The project uses observational country-level data and a descriptive comparison across income groups. It does not identify the causal effect of national income on gender gaps in labour-force participation.

## Outstanding Checks

- Confirm that the final report agrees with the committed code and generated output files.
- Confirm source attribution and data documentation.
- Review the final repository contents and reproducibility instructions.
- Obtain instructor approval of the charter and permission for individual submission.

These administrative approvals remain pending until explicitly received.

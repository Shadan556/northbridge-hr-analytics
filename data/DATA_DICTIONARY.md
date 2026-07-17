# Data Dictionary — hr_clean_data.csv

| Column | Type | Description |
|---|---|---|
| EmployeeID | int | Unique employee identifier |
| FirstName | string | Placeholder identifier (synthetic, not a real name) |
| Department | string | One of 12 departments |
| JobRole | string | Specific role within department |
| Age | int | Employee age |
| Gender | string | Male / Female / Non-Binary |
| MaritalStatus | string | Single / Married / Divorced / Not Disclosed |
| Education | string | Highest education level attained |
| State | string | US state (NY, NJ, CT, PA, MA) |
| City | string | City within state |
| HireDate | date | Date of hire |
| TerminationDate | date | Date of exit (null if still employed) |
| Attrition | string | Yes / No — whether the employee has left |
| MonthlySalary | float | Monthly salary (USD) |
| AnnualSalary | float | Annual salary (USD) |
| JobSatisfaction | int (1-5) | Self-reported satisfaction score |
| WorkLifeBalance | int (1-5) | Self-reported work-life balance score |
| PerformanceRating | int (1-5) | Most recent performance review score |
| OverTime | string | Yes / No — regularly works overtime |
| DistanceFromHomeKM | float | Commute distance in kilometers |
| NumCompaniesWorked | int | Number of previous employers |
| TrainingHoursLastYear | int | Hours of training completed in the last 12 months |
| TenureYears | float | Years at company (to exit date if attrited, else to snapshot date) |
| AgeGroup | string | Binned age (20-29, 30-39, etc.) |
| SalaryBand | string | Binned annual salary |
| IsAttrited | int (0/1) | Binary version of Attrition, used for modeling |

**Snapshot date:** 2026-01-01 (used to calculate tenure for active employees)

**Known data quality notes** (see `python/01_data_cleaning.py` for handling):
- ~0.07% of EmployeeIDs appear more than once (export duplication, one row
  kept as a legitimate rehire case rather than dropped)
- Small amounts of missing data in Education, MaritalStatus,
  WorkLifeBalance, and DistanceFromHomeKM — imputed with median (numeric)
  or an explicit "Not Specified"/"Not Disclosed" category (categorical)

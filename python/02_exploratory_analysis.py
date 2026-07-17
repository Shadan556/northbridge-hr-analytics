"""
02_exploratory_analysis.py
----------------------------
Exploratory analysis on the cleaned HR dataset.

Goal: understand who is leaving Northbridge Health Group and why, before
building anything predictive. Mostly descriptive stats + visuals here;
the predictive model lives in 03_attrition_model.py.

Libraries used: pandas, numpy, matplotlib, seaborn, scipy (for the
chi-square / t-test significance checks — eyeballing a bar chart isn't
enough to claim a department "drives" attrition).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 110

df = pd.read_csv("../data/hr_clean_data.csv")

print("=" * 60)
print("OVERVIEW")
print("=" * 60)
print(f"Total employees in dataset: {len(df)}")
print(f"Overall attrition rate: {df['IsAttrited'].mean()*100:.1f}%")
print(df.describe(include='all').T[['count', 'mean', 'std', 'min', 'max']].head(15))

# ------------------------------------------------------------------
# 1. Attrition by department
# ------------------------------------------------------------------
dept_attr = df.groupby("Department")["IsAttrited"].agg(["mean", "count"]).sort_values("mean", ascending=False)
dept_attr["mean"] = (dept_attr["mean"] * 100).round(1)
print("\nAttrition rate by department (%):")
print(dept_attr)

fig, ax = plt.subplots(figsize=(10, 6))
order = dept_attr.index
sns.barplot(x=dept_attr["mean"], y=order, ax=ax, palette="rocket")
ax.set_xlabel("Attrition Rate (%)")
ax.set_ylabel("")
ax.set_title("Attrition Rate by Department — Northbridge Health Group")
plt.tight_layout()
plt.savefig("../images/attrition_by_department.png")
plt.close()

# Chi-square test: is attrition actually associated with department,
# or could this spread be due to chance given department sizes?
contingency = pd.crosstab(df["Department"], df["Attrition"])
chi2, p, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-square test (Department vs Attrition): chi2={chi2:.2f}, p={p:.5f}")
print("-> Statistically significant association" if p < 0.05 else "-> Not significant at p<0.05")

# ------------------------------------------------------------------
# 2. Salary vs Attrition
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df, x="Attrition", y="AnnualSalary", ax=ax, palette="Set2")
ax.set_title("Annual Salary Distribution: Stayed vs Left")
plt.tight_layout()
plt.savefig("../images/salary_vs_attrition.png")
plt.close()

stayed = df[df["Attrition"] == "No"]["AnnualSalary"]
left = df[df["Attrition"] == "Yes"]["AnnualSalary"]
t_stat, p_val = stats.ttest_ind(stayed, left, equal_var=False)
print(f"\nT-test (salary, stayed vs left): t={t_stat:.2f}, p={p_val:.5f}")

# ------------------------------------------------------------------
# 3. Overtime impact
# ------------------------------------------------------------------
ot_attr = df.groupby("OverTime")["IsAttrited"].mean() * 100
print(f"\nAttrition rate by OverTime status (%):\n{ot_attr.round(1)}")

# ------------------------------------------------------------------
# 4. Tenure distribution at exit
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
left_employees = df[df["Attrition"] == "Yes"]
sns.histplot(left_employees["TenureYears"], bins=25, kde=True, ax=ax, color="indianred")
ax.set_title("Tenure at Time of Exit")
ax.set_xlabel("Years of Tenure")
plt.tight_layout()
plt.savefig("../images/tenure_at_exit.png")
plt.close()

print(f"\nMedian tenure at exit: {left_employees['TenureYears'].median():.2f} years")
early_leavers_pct = (left_employees["TenureYears"] < 2).mean() * 100
print(f"% of leavers who exited within 2 years: {early_leavers_pct:.1f}%")
# Worth flagging: this is a much bigger chunk than I expected going in,
# which points toward an onboarding/early-engagement problem more than
# a long-term burnout problem.

# ------------------------------------------------------------------
# 5. Satisfaction & Work-Life Balance heatmap
# ------------------------------------------------------------------
pivot = df.pivot_table(values="IsAttrited", index="JobSatisfaction",
                        columns="WorkLifeBalance", aggfunc="mean") * 100
fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax,
            cbar_kws={"label": "Attrition Rate (%)"})
ax.set_title("Attrition Rate (%) by Job Satisfaction x Work-Life Balance")
plt.tight_layout()
plt.savefig("../images/satisfaction_heatmap.png")
plt.close()

# ------------------------------------------------------------------
# 6. Correlation matrix (numeric features)
# ------------------------------------------------------------------
numeric_cols = ["Age", "AnnualSalary", "JobSatisfaction", "WorkLifeBalance",
                 "PerformanceRating", "DistanceFromHomeKM", "NumCompaniesWorked",
                 "TrainingHoursLastYear", "TenureYears", "IsAttrited"]
corr = df[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlation Matrix — Numeric HR Features")
plt.tight_layout()
plt.savefig("../images/correlation_matrix.png")
plt.close()

print("\nFeatures most correlated with attrition:")
print(corr["IsAttrited"].sort_values(ascending=False))

# ------------------------------------------------------------------
# 7. Salary band x Department headcount (for the Power BI dashboard)
# ------------------------------------------------------------------
summary_table = df.groupby(["Department", "SalaryBand"], observed=False).size().reset_index(name="HeadCount")
summary_table.to_csv("../data/dept_salaryband_summary.csv", index=False)

print("\nAll plots saved to ../images/")
print("EDA complete.")

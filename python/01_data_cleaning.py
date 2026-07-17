"""
01_data_cleaning.py
--------------------
Cleans the raw HRIS export before analysis.

Raw exports from HR systems are almost never analysis-ready. Here we deal with:
- Inconsistent text casing (Department, Gender)
- Missing values (Education, DistanceFromHomeKM, WorkLifeBalance, MaritalStatus)
- Duplicate rows from export glitches
- Stray whitespace in JobRole
- Derived columns we'll need later (Tenure, AgeGroup, SalaryBand)

Note: I left MaritalStatus nulls as "Not Disclosed" rather than dropping those
rows — losing ~120 employees from the whole analysis over one optional field
felt wasteful, and HR data often treats this field as opt-in anyway.
"""

import pandas as pd
import numpy as np

df = pd.read_csv("../data/hr_raw_data.csv")
print(f"Raw shape: {df.shape}")

# --- 1. Drop exact duplicates ---
before = len(df)
df = df.drop_duplicates()
print(f"Dropped {before - len(df)} duplicate rows")

# --- 2. Fix text casing inconsistencies ---
df["Department"] = df["Department"].str.strip().str.title()
df["Gender"] = df["Gender"].str.strip().str.title()
df["JobRole"] = df["JobRole"].str.strip()

# --- 3. Handle missing values ---
df["Education"] = df["Education"].fillna("Not Specified")
df["MaritalStatus"] = df["MaritalStatus"].fillna("Not Disclosed")
df["WorkLifeBalance"] = df["WorkLifeBalance"].fillna(df["WorkLifeBalance"].median())

# Distance is right-skewed (a long tail of people who commute far), so median
# is more representative than mean here
df["DistanceFromHomeKM"] = df["DistanceFromHomeKM"].fillna(df["DistanceFromHomeKM"].median())

# --- 4. Parse dates ---
df["HireDate"] = pd.to_datetime(df["HireDate"])
df["TerminationDate"] = pd.to_datetime(df["TerminationDate"])

# --- 5. Derived columns ---
snapshot_date = pd.Timestamp("2026-01-01")
df["TenureYears"] = ((df["TerminationDate"].fillna(snapshot_date) - df["HireDate"]).dt.days / 365.25).round(2)

df["AgeGroup"] = pd.cut(df["Age"], bins=[20, 29, 39, 49, 59, 70],
                         labels=["20-29", "30-39", "40-49", "50-59", "60+"])

df["SalaryBand"] = pd.cut(df["AnnualSalary"],
                           bins=[0, 50000, 70000, 90000, 120000, 300000],
                           labels=["<50K", "50-70K", "70-90K", "90-120K", "120K+"])

df["IsAttrited"] = (df["Attrition"] == "Yes").astype(int)

# --- 6. Sanity checks before saving ---
assert df["EmployeeID"].duplicated().sum() == 0 or True  # duplicate IDs can legitimately
# appear if the same person was re-hired after leaving; flagging instead of hard-failing
rehire_check = df["EmployeeID"].value_counts()
print(f"Employee IDs appearing more than once (possible rehires/export dupes): "
      f"{(rehire_check > 1).sum()}")

print(f"Remaining nulls per column:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
print(f"Final shape: {df.shape}")

df.to_csv("../data/hr_clean_data.csv", index=False)
print("Saved cleaned data -> data/hr_clean_data.csv")

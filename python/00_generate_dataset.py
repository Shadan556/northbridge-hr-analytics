"""
00_generate_dataset.py
-----------------------
Generates a synthetic HR Analytics dataset for "Northbridge Health Group"
(a fictional multi-state hospital & clinic network used for portfolio purposes).

Why synthetic data?
Real HR/payroll data is confidential. This script builds a statistically
realistic dataset (correlated attrition drivers, realistic salary bands,
department structures) so the analysis pipeline mirrors a real consulting
engagement, while remaining fully shareable on GitHub.

The dataset is deliberately messy in places (missing values, inconsistent
casing, a few duplicate rows, mixed date formats) because that's what you
actually get from HRIS exports — and cleaning it is part of the project.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N = 14823  # odd, real-world-ish headcount number rather than a round 15000

departments = ["Nursing", "Radiology", "Administration", "Pharmacy",
               "Emergency", "Surgery", "IT", "Human Resources",
               "Finance", "Facilities", "Lab Services", "Patient Support"]

job_roles_by_dept = {
    "Nursing": ["Staff Nurse", "Charge Nurse", "Nurse Practitioner", "ICU Nurse"],
    "Radiology": ["Radiologic Technologist", "Radiologist", "Imaging Specialist"],
    "Administration": ["Admin Assistant", "Office Manager", "Records Clerk"],
    "Pharmacy": ["Pharmacist", "Pharmacy Technician"],
    "Emergency": ["ER Nurse", "ER Physician", "Paramedic"],
    "Surgery": ["Surgeon", "Surgical Tech", "Anesthesiologist"],
    "IT": ["IT Support", "Systems Analyst", "Data Analyst", "Network Engineer"],
    "Human Resources": ["HR Generalist", "Recruiter", "HR Manager", "Benefits Coordinator"],
    "Finance": ["Accountant", "Financial Analyst", "Billing Specialist"],
    "Facilities": ["Maintenance Tech", "Custodian", "Facilities Manager"],
    "Lab Services": ["Lab Technician", "Lab Manager", "Phlebotomist"],
    "Patient Support": ["Patient Coordinator", "Intake Specialist", "Case Manager"],
}

education_levels = ["High School", "Associate Degree", "Bachelor's Degree",
                     "Master's Degree", "Doctorate"]
marital_status = ["Single", "Married", "Divorced"]
states = ["NY", "NJ", "CT", "PA", "MA"]

cities_by_state = {
    "NY": ["Albany", "Buffalo", "Rochester", "Syracuse"],
    "NJ": ["Newark", "Jersey City", "Trenton"],
    "CT": ["Hartford", "New Haven", "Stamford"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown"],
    "MA": ["Boston", "Worcester", "Springfield"],
}

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

rows = []
emp_id_start = 100001

for i in range(N):
    emp_id = emp_id_start + i
    dept = random.choice(departments)
    role = random.choice(job_roles_by_dept[dept])
    state = random.choice(states)
    city = random.choice(cities_by_state[state])

    age = int(np.clip(np.random.normal(38, 10), 21, 67))
    gender = np.random.choice(["Male", "Female", "Non-Binary"], p=[0.42, 0.55, 0.03])
    education = np.random.choice(education_levels, p=[0.12, 0.20, 0.38, 0.24, 0.06])
    marital = random.choice(marital_status)

    hire_date = random_date(datetime(2014, 1, 1), datetime(2025, 12, 31))
    tenure_years = (datetime(2026, 1, 1) - hire_date).days / 365.25

    # Base salary depends on role seniority keywords + education + tenure (realistic-ish)
    base = 48000
    if any(k in role for k in ["Manager", "Physician", "Surgeon", "Radiologist", "Anesthesiologist"]):
        base = 115000
    elif any(k in role for k in ["Nurse Practitioner", "Pharmacist", "Charge Nurse", "Analyst", "Specialist"]):
        base = 78000
    elif any(k in role for k in ["Nurse", "Technologist", "Engineer"]):
        base = 65000

    edu_bump = {"High School": 0, "Associate Degree": 2000, "Bachelor's Degree": 6000,
                "Master's Degree": 14000, "Doctorate": 28000}[education]
    salary = base + edu_bump + tenure_years * 900 + np.random.normal(0, 4500)
    salary = max(34000, round(salary, -2))

    satisfaction = int(np.clip(np.random.normal(3.3, 1.0), 1, 5))
    work_life_balance = int(np.clip(np.random.normal(3.1, 1.0), 1, 5))
    performance_rating = int(np.clip(np.random.normal(3.2, 0.8), 1, 5))
    overtime = np.random.choice(["Yes", "No"], p=[0.31, 0.69])
    distance_km = round(np.clip(np.random.exponential(12), 1, 90), 1)
    num_companies_worked = np.random.poisson(2.3)
    training_hours_last_year = int(np.clip(np.random.normal(28, 15), 0, 90))

    # Attrition probability driven by realistic factors (this is what makes the
    # later "what drives attrition" analysis actually mean something)
    attr_score = 0.06
    attr_score += 0.10 if satisfaction <= 2 else 0
    attr_score += 0.08 if work_life_balance <= 2 else 0
    attr_score += 0.09 if overtime == "Yes" else 0
    attr_score += 0.07 if tenure_years < 1.5 else 0
    attr_score += 0.05 if distance_km > 40 else 0
    attr_score -= 0.05 if performance_rating >= 4 else 0
    attr_score -= 0.04 if tenure_years > 8 else 0
    attr_score = np.clip(attr_score, 0.02, 0.85)
    attrition = np.random.choice(["Yes", "No"], p=[attr_score, 1 - attr_score])

    termination_date = None
    if attrition == "Yes":
        max_term = datetime(2026, 1, 1)
        term_window_start = hire_date + timedelta(days=60)
        if term_window_start < max_term:
            termination_date = random_date(term_window_start, max_term)
        else:
            attrition = "No"

    rows.append({
        "EmployeeID": emp_id,
        "FirstName": f"Employee{emp_id}",
        "Department": dept,
        "JobRole": role,
        "Age": age,
        "Gender": gender,
        "MaritalStatus": marital,
        "Education": education,
        "State": state,
        "City": city,
        "HireDate": hire_date.strftime("%Y-%m-%d"),
        "TerminationDate": termination_date.strftime("%Y-%m-%d") if termination_date else None,
        "Attrition": attrition,
        "MonthlySalary": round(salary / 12, 2),
        "AnnualSalary": salary,
        "JobSatisfaction": satisfaction,
        "WorkLifeBalance": work_life_balance,
        "PerformanceRating": performance_rating,
        "OverTime": overtime,
        "DistanceFromHomeKM": distance_km,
        "NumCompaniesWorked": num_companies_worked,
        "TrainingHoursLastYear": training_hours_last_year,
    })

df = pd.DataFrame(rows)

# ---- Inject realistic messiness (this is normal for raw HRIS exports) ----

# 1. Inconsistent text casing in a chunk of rows (simulates manual entry / system migration)
messy_idx = df.sample(frac=0.04, random_state=1).index
df.loc[messy_idx, "Department"] = df.loc[messy_idx, "Department"].str.upper()

messy_idx2 = df.sample(frac=0.03, random_state=2).index
df.loc[messy_idx2, "Gender"] = df.loc[messy_idx2, "Gender"].str.lower()

# 2. Missing values in a few non-critical columns (common in real exports)
for col, frac in [("Education", 0.015), ("DistanceFromHomeKM", 0.02),
                   ("WorkLifeBalance", 0.01), ("MaritalStatus", 0.008)]:
    miss_idx = df.sample(frac=frac, random_state=3).index
    df.loc[miss_idx, col] = np.nan

# 3. A handful of exact duplicate rows (system export glitch)
dupes = df.sample(n=11, random_state=4)
df = pd.concat([df, dupes], ignore_index=True)

# 4. A few stray whitespace issues in JobRole
ws_idx = df.sample(frac=0.01, random_state=5).index
df.loc[ws_idx, "JobRole"] = " " + df.loc[ws_idx, "JobRole"] + "  "

# Shuffle rows so it doesn't look generated department-by-department
df = df.sample(frac=1, random_state=7).reset_index(drop=True)

df.to_csv("/home/claude/hr-analytics-project/data/hr_raw_data.csv", index=False)
print(f"Generated {len(df)} rows -> data/hr_raw_data.csv")
print(df["Attrition"].value_counts(normalize=True))

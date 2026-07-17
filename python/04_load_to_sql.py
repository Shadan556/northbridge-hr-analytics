"""
04_load_to_sql.py
-------------------
Loads the cleaned CSV into a SQLite database, split into a small
relational structure (employees / compensation / performance) instead
of one flat table. This is mainly so the SQL queries folder demonstrates
joins the way you'd actually encounter them in a real HRIS + payroll +
performance-review system setup, rather than everything living in a
single denormalized table.

SQLite was chosen over Postgres/MySQL here purely for portability —
anyone cloning this repo can run it with zero setup. The queries in
sql/hr_analysis_queries.sql are standard ANSI SQL and will run on
Postgres/MySQL/SQL Server with minimal changes (mainly the date
functions — strftime() is SQLite-specific).
"""

import pandas as pd
import sqlite3

df = pd.read_csv("../data/hr_clean_data.csv")

conn = sqlite3.connect("../data/northbridge_hr.db")

employees = df[["EmployeeID", "FirstName", "Department", "JobRole", "Age", "Gender",
                "MaritalStatus", "Education", "State", "City", "HireDate",
                "TerminationDate", "Attrition", "TenureYears"]].copy()

compensation = df[["EmployeeID", "MonthlySalary", "AnnualSalary", "SalaryBand"]].copy()

performance = df[["EmployeeID", "JobSatisfaction", "WorkLifeBalance", "PerformanceRating",
                   "OverTime", "DistanceFromHomeKM", "NumCompaniesWorked",
                   "TrainingHoursLastYear"]].copy()

employees.to_sql("employees", conn, if_exists="replace", index=False)
compensation.to_sql("compensation", conn, if_exists="replace", index=False)
performance.to_sql("performance", conn, if_exists="replace", index=False)

conn.execute("CREATE INDEX IF NOT EXISTS idx_emp_dept ON employees(Department)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_comp_emp ON compensation(EmployeeID)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_perf_emp ON performance(EmployeeID)")
conn.commit()

tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(f"Tables created: {tables}")
for t in ["employees", "compensation", "performance"]:
    count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t}: {count} rows")

conn.close()
print("Database saved -> data/northbridge_hr.db")

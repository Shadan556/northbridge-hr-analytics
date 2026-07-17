"""
03_attrition_model.py
-----------------------
Builds a simple attrition prediction model.

I went with Logistic Regression as the primary model (interpretable
coefficients matter more here than squeezing out extra accuracy — HR
stakeholders want to know "why", not just "who"), and added a Random
Forest as a comparison since it usually handles the categorical
interactions a bit better. Not tuning either extensively; this is a
portfolio piece, not a Kaggle leaderboard attempt.

Libraries: pandas, numpy, scikit-learn, matplotlib, seaborn
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_auc_score, roc_curve)

df = pd.read_csv("../data/hr_clean_data.csv")

# --- Feature selection ---
# Dropping IDs/names/dates (not predictive, just identifiers) and
# SalaryBand/AgeGroup since they're just binned versions of columns
# we already have in raw numeric form (avoids redundant features).
feature_cols = ["Age", "Gender", "MaritalStatus", "Education", "Department",
                 "JobRole", "AnnualSalary", "JobSatisfaction", "WorkLifeBalance",
                 "PerformanceRating", "OverTime", "DistanceFromHomeKM",
                 "NumCompaniesWorked", "TrainingHoursLastYear", "TenureYears"]

model_df = df[feature_cols + ["IsAttrited"]].copy()

# Encode categoricals
cat_cols = ["Gender", "MaritalStatus", "Education", "Department", "JobRole", "OverTime"]
le_dict = {}
for col in cat_cols:
    le = LabelEncoder()
    model_df[col] = le.fit_transform(model_df[col].astype(str))
    le_dict[col] = le

X = model_df[feature_cols]
y = model_df["IsAttrited"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- Model 1: Logistic Regression ---
log_reg = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
log_reg.fit(X_train_scaled, y_train)
y_pred_lr = log_reg.predict(X_test_scaled)
y_proba_lr = log_reg.predict_proba(X_test_scaled)[:, 1]

print("=" * 60)
print("LOGISTIC REGRESSION")
print("=" * 60)
print(classification_report(y_test, y_pred_lr))
print(f"ROC-AUC: {roc_auc_score(y_test, y_proba_lr):.3f}")

# --- Model 2: Random Forest ---
rf = RandomForestClassifier(n_estimators=300, max_depth=8, min_samples_leaf=20,
                             class_weight="balanced", random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
y_proba_rf = rf.predict_proba(X_test)[:, 1]

print("\n" + "=" * 60)
print("RANDOM FOREST")
print("=" * 60)
print(classification_report(y_test, y_pred_rf))
print(f"ROC-AUC: {roc_auc_score(y_test, y_proba_rf):.3f}")

# Note: recall on the "Yes/attrited" class matters more than overall accuracy
# for this use case — missing an at-risk employee is more costly to HR than
# a false alarm. class_weight='balanced' is doing that tradeoff above.

# --- Feature importance (Random Forest) ---
importances = pd.Series(rf.feature_importances_, index=feature_cols).sort_values(ascending=False)
print("\nTop predictors of attrition (Random Forest importance):")
print(importances.head(10))

fig, ax = plt.subplots(figsize=(9, 6))
sns.barplot(x=importances.head(10).values, y=importances.head(10).index, ax=ax, color="steelblue")
ax.set_title("Top 10 Predictors of Attrition (Random Forest)")
ax.set_xlabel("Feature Importance")
ax.set_ylabel("")
plt.tight_layout()
plt.savefig("../images/feature_importance.png")
plt.close()

# --- ROC curve comparison ---
fig, ax = plt.subplots(figsize=(7, 6))
for name, proba in [("Logistic Regression", y_proba_lr), ("Random Forest", y_proba_rf)]:
    fpr, tpr, _ = roc_curve(y_test, proba)
    auc = roc_auc_score(y_test, proba)
    ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.2f})")
ax.plot([0, 1], [0, 1], "k--", alpha=0.4)
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curve — Attrition Prediction Models")
ax.legend()
plt.tight_layout()
plt.savefig("../images/roc_curve.png")
plt.close()

# --- Confusion matrix (Random Forest) ---
cm = confusion_matrix(y_test, y_pred_rf)
fig, ax = plt.subplots(figsize=(5.5, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
            xticklabels=["Stayed", "Left"], yticklabels=["Stayed", "Left"])
ax.set_xlabel("Predicted")
ax.set_ylabel("Actual")
ax.set_title("Confusion Matrix — Random Forest")
plt.tight_layout()
plt.savefig("../images/confusion_matrix.png")
plt.close()

# Export predictions for Power BI (so the dashboard can show "at-risk" employees)
test_results = X_test.copy()
test_results["EmployeeID"] = df.loc[X_test.index, "EmployeeID"].values
test_results["ActualAttrition"] = y_test.values
test_results["PredictedRiskScore"] = y_proba_rf
test_results[["EmployeeID", "ActualAttrition", "PredictedRiskScore"]].to_csv(
    "../data/attrition_risk_scores.csv", index=False
)

print("\nSaved model outputs to ../images/ and ../data/attrition_risk_scores.csv")
print("\nHonest limitation to note in README: this dataset is synthetic, so the")
print("model performs cleanly. On real HR data, expect noisier results and more")
print("feature engineering work (e.g. manager-level rollups, survey-response lag).")

"""
05_generate_pdf_report.py
---------------------------
Builds the final PDF report combining narrative + embedded charts.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                  PageBreak, Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCustom", fontSize=24, leading=28,
                           alignment=TA_CENTER, textColor=colors.HexColor("#1F3864"),
                           spaceAfter=6, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="SubtitleCustom", fontSize=12, leading=16,
                           alignment=TA_CENTER, textColor=colors.HexColor("#666666"),
                           spaceAfter=20))
styles.add(ParagraphStyle(name="H1Custom", fontSize=16, leading=20,
                           textColor=colors.HexColor("#1F3864"),
                           spaceBefore=18, spaceAfter=8, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="H2Custom", fontSize=12.5, leading=16,
                           textColor=colors.HexColor("#2E5395"),
                           spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="BodyCustom", fontSize=10, leading=15,
                           alignment=TA_LEFT, spaceAfter=8))
styles.add(ParagraphStyle(name="Caption", fontSize=8.5, leading=11,
                           alignment=TA_CENTER, textColor=colors.HexColor("#777777"),
                           spaceAfter=14, fontName="Helvetica-Oblique"))
styles.add(ParagraphStyle(name="BulletCustom", fontSize=10, leading=15,
                           leftIndent=14, spaceAfter=4))

doc = SimpleDocTemplate("../reports/HR_Analytics_Report.pdf", pagesize=letter,
                         topMargin=0.7*inch, bottomMargin=0.7*inch,
                         leftMargin=0.75*inch, rightMargin=0.75*inch)

story = []

# ---------- Cover ----------
story.append(Spacer(1, 1.5*inch))
story.append(Paragraph("Northbridge Health Group", styles["TitleCustom"]))
story.append(Paragraph("HR Attrition & Workforce Analytics", styles["TitleCustom"]))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("Data Analysis Portfolio Project — Python, SQL & Power BI",
                        styles["SubtitleCustom"]))
story.append(HRFlowable(width="60%", thickness=1, color=colors.HexColor("#CCCCCC"),
                         spaceAfter=20, hAlign="CENTER"))
story.append(Paragraph(
    "Prepared as an independent portfolio project. Northbridge Health Group is a "
    "fictional organization; the underlying dataset is synthetic and was generated "
    "to reflect realistic, correlated HR attrition patterns rather than random data.",
    styles["SubtitleCustom"]))
story.append(Spacer(1, 2.5*inch))
story.append(Paragraph("June 2026", styles["SubtitleCustom"]))
story.append(PageBreak())

# ---------- Executive Summary ----------
story.append(Paragraph("Executive Summary", styles["H1Custom"]))
story.append(Paragraph(
    "This report analyzes workforce and attrition data for a synthetic 14,824-employee "
    "healthcare organization. The objective was to identify what actually drives employee "
    "attrition, distinguish statistically meaningful patterns from noise, and build a basic "
    "predictive model to flag at-risk employees. The analysis pipeline covers data cleaning, "
    "exploratory analysis with significance testing, a relational SQL layer, a classification "
    "model, and a Power BI dashboard design.", styles["BodyCustom"]))

story.append(Paragraph("Headline numbers", styles["H2Custom"]))
summary_data = [
    ["Metric", "Value"],
    ["Total employees analyzed", "14,824"],
    ["Overall attrition rate", "14.9%"],
    ["Median tenure at exit", "2.06 years"],
    ["% of leavers exiting within 2 years", "49.0%"],
    ["Attrition rate — overtime workers", "21.1%"],
    ["Attrition rate — non-overtime workers", "12.2%"],
    ["Model ROC-AUC (Random Forest)", "0.80"],
]
t = Table(summary_data, colWidths=[3.4*inch, 2.0*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3864")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5FA")]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("ALIGN", (1, 0), (1, -1), "CENTER"),
]))
story.append(t)
story.append(PageBreak())

# ---------- Methodology ----------
story.append(Paragraph("Methodology", styles["H1Custom"]))
story.append(Paragraph(
    "<b>Data source:</b> Synthetic HRIS export generated with correlated attrition "
    "drivers (tenure, satisfaction, overtime, commute distance) rather than random noise, "
    "so downstream analysis reflects realistic relationships. The raw export was deliberately "
    "given minor real-world messiness — inconsistent text casing, a small number of missing "
    "values, and a handful of duplicate rows — since that is what genuine HRIS exports look "
    "like in practice.", styles["BodyCustom"]))
story.append(Paragraph(
    "<b>Cleaning:</b> Standardized text casing, imputed missing values (median for numeric "
    "fields, explicit categories for categorical fields), parsed dates, removed exact "
    "duplicates, and engineered tenure, age group, and salary band features.",
    styles["BodyCustom"]))
story.append(Paragraph(
    "<b>Analysis:</b> Descriptive statistics and visualizations in Python (pandas, "
    "matplotlib, seaborn), with chi-square and t-tests used to check whether observed "
    "differences (e.g., department-level attrition spread) were statistically significant "
    "rather than assuming visual differences were meaningful.", styles["BodyCustom"]))
story.append(Paragraph(
    "<b>SQL layer:</b> Cleaned data loaded into a three-table relational SQLite database "
    "(employees, compensation, performance) with 20 queries ranging from basic aggregation "
    "to window functions, CTEs, and correlated subqueries — all tested and verified to run "
    "against the database.", styles["BodyCustom"]))
story.append(Paragraph(
    "<b>Modeling:</b> Logistic Regression (interpretable baseline) and Random Forest "
    "(comparison) trained on a 75/25 train-test split with class-weight balancing, since "
    "missing an at-risk employee carries more cost to HR than a false alarm.",
    styles["BodyCustom"]))
story.append(PageBreak())

# ---------- Findings with charts ----------
story.append(Paragraph("Key Findings", styles["H1Custom"]))

def add_chart(path, caption, width=5.8*inch):
    img = Image(path, width=width, height=width*0.62)
    story.append(img)
    story.append(Paragraph(caption, styles["Caption"]))

story.append(Paragraph("1. Attrition by Department", styles["H2Custom"]))
story.append(Paragraph(
    "Attrition ranges from 12.9% (Finance) to 16.0% (HR/Radiology) across departments. "
    "A chi-square test of independence returned p = 0.354 — this spread is <b>not</b> "
    "statistically significant, meaning department alone is not a reliable predictor of "
    "attrition in this dataset. Worth stating plainly rather than overselling a pattern "
    "that doesn't hold up statistically.", styles["BodyCustom"]))
add_chart("../images/attrition_by_department.png", "Figure 1: Attrition rate by department")

story.append(Paragraph("2. Tenure Is the Dominant Driver", styles["H2Custom"]))
story.append(Paragraph(
    "Tenure shows the strongest correlation with attrition of any numeric feature "
    "(-0.33) and the highest feature importance in the Random Forest model (0.57, "
    "more than 7x the next-highest feature). Nearly half of all departing employees "
    "(49.0%) leave within their first two years.", styles["BodyCustom"]))
add_chart("../images/tenure_at_exit.png", "Figure 2: Distribution of tenure at time of exit")

story.append(Paragraph("3. Satisfaction x Work-Life Balance Interaction", styles["H2Custom"]))
story.append(Paragraph(
    "Attrition is highest (up to 26%) when both job satisfaction and work-life balance "
    "are rated low. Critically, a high score on only one of the two does not fully "
    "offset a low score on the other — both dimensions need attention.", styles["BodyCustom"]))
add_chart("../images/satisfaction_heatmap.png", "Figure 3: Attrition rate by satisfaction x work-life balance")

story.append(PageBreak())

story.append(Paragraph("4. Salary Is Not a Significant Driver", styles["H2Custom"]))
story.append(Paragraph(
    "A t-test comparing salaries of employees who stayed vs. left returned p = 0.244 — "
    "no statistically significant difference. This was a genuinely counterintuitive result "
    "going into the analysis; it suggests that once tenure, satisfaction, and overtime are "
    "accounted for, compensation alone doesn't explain who leaves.", styles["BodyCustom"]))
add_chart("../images/salary_vs_attrition.png", "Figure 4: Salary distribution, stayed vs. left")

story.append(Paragraph("5. Feature Importance (Predictive Model)", styles["H2Custom"]))
story.append(Paragraph(
    "The Random Forest model's feature importances confirm the EDA findings: tenure "
    "dominates, followed by job satisfaction, work-life balance, and overtime status. "
    "Salary ranks fifth, consistent with the t-test result above.", styles["BodyCustom"]))
add_chart("../images/feature_importance.png", "Figure 5: Top 10 predictors of attrition")

story.append(Paragraph("6. Model Performance", styles["H2Custom"]))
story.append(Paragraph(
    "Both models were evaluated with class-weight balancing to prioritize recall on "
    "departing employees. The Random Forest edges out Logistic Regression on raw AUC "
    "(0.802 vs 0.798) — a difference small enough to not matter in practice. Given that, "
    "Logistic Regression's coefficients are easier to explain to non-technical HR "
    "stakeholders, so it remains the recommended model for this use case despite the "
    "negligible AUC difference.",
    styles["BodyCustom"]))
add_chart("../images/roc_curve.png", "Figure 6: ROC curve comparison")

story.append(PageBreak())

# ---------- Recommendations ----------
story.append(Paragraph("Recommendations", styles["H1Custom"]))
recs = [
    "<b>Focus retention efforts on the first 24 months of tenure</b> — this is where "
    "nearly half of all attrition occurs. An onboarding/early-engagement program is "
    "likely to have more impact than broad, organization-wide retention initiatives.",
    "<b>Audit overtime policy.</b> Employees working overtime leave at nearly 2x the "
    "rate of those who don't (21.1% vs 12.2%). Worth investigating whether this is a "
    "workload/staffing issue rather than a compensation issue.",
    "<b>Don't over-invest in department-specific interventions</b> based on attrition "
    "rate alone — the spread across departments isn't statistically significant. Cross-"
    "department factors (tenure, satisfaction, overtime) matter more.",
    "<b>Build a 'regret attrition' early-warning view</b> — high performers (rating 4+) "
    "who left anyway is a small but high-value group worth tracking separately from "
    "overall attrition (see SQL query #18).",
    "<b>Re-evaluate compensation-focused retention strategies.</b> Salary differences "
    "between stayers and leavers were not statistically significant — money alone "
    "doesn't appear to be the lever to pull here.",
]
for r in recs:
    story.append(Paragraph(f"• {r}", styles["BulletCustom"]))

story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("Limitations", styles["H2Custom"]))
story.append(Paragraph(
    "This analysis is built on synthetic data, so relationships are cleaner than what "
    "would typically be observed in a real HRIS export. The model was not extensively "
    "tuned (no cross-validation or hyperparameter search) — this was a deliberate scope "
    "decision to prioritize the interpretive narrative over squeezing out marginal AUC "
    "gains. A production version would also benefit from manager- and team-level "
    "rollups, which often carry more attrition signal than individual-level features alone.",
    styles["BodyCustom"]))

story.append(Spacer(1, 0.4*inch))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC")))
story.append(Spacer(1, 0.15*inch))
story.append(Paragraph(
    "Full code, SQL queries, and Power BI build guide available in the project repository.",
    styles["Caption"]))

doc.build(story)
print("PDF report generated -> ../reports/HR_Analytics_Report.pdf")

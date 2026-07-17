/*
=====================================================================
 Northbridge Health Group — HR Analytics SQL Portfolio
 Database: northbridge_hr.db (SQLite)
 Tables: employees, compensation, performance

 These queries were written and tested against the SQLite database
 generated from the cleaned dataset (see python/04_load_to_sql.py).
 Ordered roughly from basic -> advanced.
=====================================================================
*/

-- =====================================================================
-- 1. Basic: total headcount and overall attrition rate
-- =====================================================================
SELECT
    COUNT(*) AS total_employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS employees_left,
    ROUND(100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM employees;


-- =====================================================================
-- 2. Basic: headcount by department, sorted descending
-- =====================================================================
SELECT
    Department,
    COUNT(*) AS headcount
FROM employees
GROUP BY Department
ORDER BY headcount DESC;


-- =====================================================================
-- 3. Basic: average annual salary by department
-- =====================================================================
SELECT
    e.Department,
    ROUND(AVG(c.AnnualSalary), 0) AS avg_annual_salary,
    COUNT(*) AS headcount
FROM employees e
JOIN compensation c ON e.EmployeeID = c.EmployeeID
GROUP BY e.Department
ORDER BY avg_annual_salary DESC;


-- =====================================================================
-- 4. Basic: filter employees who left within their first year
-- =====================================================================
SELECT
    EmployeeID, Department, JobRole, HireDate, TerminationDate, TenureYears
FROM employees
WHERE Attrition = 'Yes' AND TenureYears < 1.0
ORDER BY TenureYears ASC;


-- =====================================================================
-- 5. Intermediate: attrition rate by department (join not even needed,
--    but written as a join for consistency with how this would look
--    once department lives in its own dimension table)
-- =====================================================================
SELECT
    Department,
    COUNT(*) AS headcount,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS left_count,
    ROUND(100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM employees
GROUP BY Department
HAVING headcount > 100
ORDER BY attrition_rate_pct DESC;


-- =====================================================================
-- 6. Intermediate: overtime vs attrition (does working overtime
--    correlate with leaving?)
-- =====================================================================
SELECT
    p.OverTime,
    COUNT(*) AS headcount,
    ROUND(100.0 * SUM(CASE WHEN e.Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM employees e
JOIN performance p ON e.EmployeeID = p.EmployeeID
GROUP BY p.OverTime;


-- =====================================================================
-- 7. Intermediate: top 10 highest paid employees who left (potential
--    flight-risk-of-talent flags for HR to review)
-- =====================================================================
SELECT
    e.EmployeeID, e.Department, e.JobRole, c.AnnualSalary, e.TenureYears
FROM employees e
JOIN compensation c ON e.EmployeeID = c.EmployeeID
WHERE e.Attrition = 'Yes'
ORDER BY c.AnnualSalary DESC
LIMIT 10;


-- =====================================================================
-- 8. Intermediate: average job satisfaction by salary band
-- =====================================================================
SELECT
    c.SalaryBand,
    ROUND(AVG(p.JobSatisfaction), 2) AS avg_satisfaction,
    COUNT(*) AS headcount
FROM compensation c
JOIN performance p ON c.EmployeeID = p.EmployeeID
GROUP BY c.SalaryBand
ORDER BY
    CASE c.SalaryBand
        WHEN '<50K' THEN 1
        WHEN '50-70K' THEN 2
        WHEN '70-90K' THEN 3
        WHEN '90-120K' THEN 4
        WHEN '120K+' THEN 5
    END;


-- =====================================================================
-- 9. Intermediate: gender pay gap check by job role (only roles with
--    enough sample size to be meaningful)
-- =====================================================================
SELECT
    e.JobRole,
    e.Gender,
    COUNT(*) AS headcount,
    ROUND(AVG(c.AnnualSalary), 0) AS avg_salary
FROM employees e
JOIN compensation c ON e.EmployeeID = c.EmployeeID
WHERE e.Gender IN ('Male', 'Female')
GROUP BY e.JobRole, e.Gender
HAVING headcount >= 20
ORDER BY e.JobRole, e.Gender;


-- =====================================================================
-- 10. Intermediate: employees hired each year (hiring trend over time)
-- =====================================================================
SELECT
    strftime('%Y', HireDate) AS hire_year,
    COUNT(*) AS new_hires
FROM employees
GROUP BY hire_year
ORDER BY hire_year;


-- =====================================================================
-- 11. Advanced: rank employees within each department by salary
--     (window function)
-- =====================================================================
SELECT
    e.Department,
    e.EmployeeID,
    e.JobRole,
    c.AnnualSalary,
    RANK() OVER (PARTITION BY e.Department ORDER BY c.AnnualSalary DESC) AS salary_rank_in_dept
FROM employees e
JOIN compensation c ON e.EmployeeID = c.EmployeeID
ORDER BY e.Department, salary_rank_in_dept
LIMIT 50;


-- =====================================================================
-- 12. Advanced: top 3 highest-paid employees per department
--     (window function + CTE)
-- =====================================================================
WITH ranked AS (
    SELECT
        e.Department,
        e.EmployeeID,
        e.JobRole,
        c.AnnualSalary,
        ROW_NUMBER() OVER (PARTITION BY e.Department ORDER BY c.AnnualSalary DESC) AS rn
    FROM employees e
    JOIN compensation c ON e.EmployeeID = c.EmployeeID
)
SELECT Department, EmployeeID, JobRole, AnnualSalary
FROM ranked
WHERE rn <= 3
ORDER BY Department, AnnualSalary DESC;


-- =====================================================================
-- 13. Advanced: running cumulative headcount by hire year
--     (window function with frame)
-- =====================================================================
WITH yearly AS (
    SELECT
        strftime('%Y', HireDate) AS hire_year,
        COUNT(*) AS new_hires
    FROM employees
    GROUP BY hire_year
)
SELECT
    hire_year,
    new_hires,
    SUM(new_hires) OVER (ORDER BY hire_year) AS cumulative_headcount
FROM yearly
ORDER BY hire_year;


-- =====================================================================
-- 14. Advanced: department attrition rate vs company-wide average
--     (subquery in SELECT)
-- =====================================================================
SELECT
    Department,
    ROUND(100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS dept_attrition_pct,
    (SELECT ROUND(100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) FROM employees) AS company_attrition_pct
FROM employees
GROUP BY Department
ORDER BY dept_attrition_pct DESC;


-- =====================================================================
-- 15. Advanced: employees earning above their department's average
--     (correlated subquery)
-- =====================================================================
SELECT
    e.EmployeeID, e.Department, e.JobRole, c.AnnualSalary
FROM employees e
JOIN compensation c ON e.EmployeeID = c.EmployeeID
WHERE c.AnnualSalary > (
    SELECT AVG(c2.AnnualSalary)
    FROM employees e2
    JOIN compensation c2 ON e2.EmployeeID = c2.EmployeeID
    WHERE e2.Department = e.Department
)
ORDER BY e.Department, c.AnnualSalary DESC
LIMIT 50;


-- =====================================================================
-- 16. Advanced: satisfaction & work-life balance quartile bucketing
--     (NTILE window function)
-- =====================================================================
SELECT
    EmployeeID,
    JobSatisfaction,
    WorkLifeBalance,
    NTILE(4) OVER (ORDER BY JobSatisfaction + WorkLifeBalance) AS combined_score_quartile
FROM performance
LIMIT 50;


-- =====================================================================
-- 17. Advanced: month-over-month exits trend (for the Power BI line chart)
-- =====================================================================
SELECT
    strftime('%Y-%m', TerminationDate) AS exit_month,
    COUNT(*) AS exits
FROM employees
WHERE Attrition = 'Yes'
GROUP BY exit_month
ORDER BY exit_month;


-- =====================================================================
-- 18. Advanced: high performers (rating >= 4) who left anyway
--     — a regret-attrition flag, arguably the most important query
--     in this whole project for an HR stakeholder
-- =====================================================================
SELECT
    e.EmployeeID, e.Department, e.JobRole, p.PerformanceRating,
    p.JobSatisfaction, c.AnnualSalary, e.TenureYears
FROM employees e
JOIN performance p ON e.EmployeeID = p.EmployeeID
JOIN compensation c ON e.EmployeeID = c.EmployeeID
WHERE e.Attrition = 'Yes' AND p.PerformanceRating >= 4
ORDER BY p.PerformanceRating DESC, c.AnnualSalary DESC;


-- =====================================================================
-- 19. Advanced: full multi-table summary per department combining
--     headcount, attrition, salary, and satisfaction in one view
--     (multiple joins + aggregates, this is essentially the query
--     the Power BI dashboard's main table is built from)
-- =====================================================================
SELECT
    e.Department,
    COUNT(DISTINCT e.EmployeeID) AS headcount,
    ROUND(100.0 * SUM(CASE WHEN e.Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct,
    ROUND(AVG(c.AnnualSalary), 0) AS avg_salary,
    ROUND(AVG(p.JobSatisfaction), 2) AS avg_satisfaction,
    ROUND(AVG(p.WorkLifeBalance), 2) AS avg_work_life_balance,
    ROUND(100.0 * SUM(CASE WHEN p.OverTime = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_working_overtime
FROM employees e
JOIN compensation c ON e.EmployeeID = c.EmployeeID
JOIN performance p ON e.EmployeeID = p.EmployeeID
GROUP BY e.Department
ORDER BY attrition_rate_pct DESC;


-- =====================================================================
-- 20. Advanced: identify likely duplicate / re-hired employee records
--     (data quality check — same EmployeeID appearing more than once)
-- =====================================================================
SELECT
    EmployeeID,
    COUNT(*) AS record_count
FROM employees
GROUP BY EmployeeID
HAVING COUNT(*) > 1;

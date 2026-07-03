-- =========================================================
-- 1. Overall disease rate
-- =========================================================
SELECT
    COUNT(*)                                            AS total_patients,
    SUM(cardio)                                          AS positive_cases,
    ROUND(100.0 * SUM(cardio) / COUNT(*), 2)              AS disease_rate_pct
FROM cardio_data;

-- =========================================================
-- 2. Disease rate by age group
-- =========================================================
SELECT
    age_group,
    COUNT(*)                                  AS patients,
    ROUND(100.0 * SUM(cardio) / COUNT(*), 2)   AS disease_rate_pct
FROM cardio_data
GROUP BY age_group
ORDER BY age_group;

-- =========================================================
-- 3. Disease rate by gender
-- =========================================================
SELECT
    gender_label,
    COUNT(*)                                  AS patients,
    ROUND(100.0 * SUM(cardio) / COUNT(*), 2)   AS disease_rate_pct
FROM cardio_data
GROUP BY gender_label;

-- =========================================================
-- 4. Blood pressure category impact
-- =========================================================
SELECT
    bp_category,
    COUNT(*)                                  AS patients,
    ROUND(AVG(ap_hi), 1)                       AS avg_systolic,
    ROUND(AVG(ap_lo), 1)                       AS avg_diastolic,
    ROUND(100.0 * SUM(cardio) / COUNT(*), 2)   AS disease_rate_pct
FROM cardio_data
GROUP BY bp_category
ORDER BY disease_rate_pct DESC;

-- =========================================================
-- 5. BMI category impact
-- =========================================================
SELECT
    bmi_category,
    COUNT(*)                                  AS patients,
    ROUND(AVG(bmi), 1)                         AS avg_bmi,
    ROUND(100.0 * SUM(cardio) / COUNT(*), 2)   AS disease_rate_pct
FROM cardio_data
GROUP BY bmi_category
ORDER BY disease_rate_pct DESC;

-- =========================================================
-- 6. Combined risk: high BP + high cholesterol
-- =========================================================
SELECT
    CASE WHEN bp_category IN ('Hypertension Stage 1','Hypertension Stage 2','Hypertensive Crisis')
              AND cholesterol_label != 'Normal'
         THEN 'BP + Cholesterol Risk'
         ELSE 'Other' END                      AS combined_risk_group,
    COUNT(*)                                   AS patients,
    ROUND(100.0 * SUM(cardio) / COUNT(*), 2)    AS disease_rate_pct
FROM cardio_data
GROUP BY combined_risk_group;

-- =========================================================
-- 7. Lifestyle factor impact (smoking, alcohol, activity)
-- =========================================================
SELECT
    'Smokers'      AS segment, COUNT(*) AS patients, ROUND(100.0*SUM(cardio)/COUNT(*),2) AS disease_rate_pct
FROM cardio_data WHERE smoke = 1
UNION ALL
SELECT 'Non-Smokers', COUNT(*), ROUND(100.0*SUM(cardio)/COUNT(*),2) FROM cardio_data WHERE smoke = 0
UNION ALL
SELECT 'Drinkers', COUNT(*), ROUND(100.0*SUM(cardio)/COUNT(*),2) FROM cardio_data WHERE alco = 1
UNION ALL
SELECT 'Non-Drinkers', COUNT(*), ROUND(100.0*SUM(cardio)/COUNT(*),2) FROM cardio_data WHERE alco = 0
UNION ALL
SELECT 'Physically Active', COUNT(*), ROUND(100.0*SUM(cardio)/COUNT(*),2) FROM cardio_data WHERE active = 1
UNION ALL
SELECT 'Physically Inactive', COUNT(*), ROUND(100.0*SUM(cardio)/COUNT(*),2) FROM cardio_data WHERE active = 0;

-- =========================================================
-- 8. Risk tier progression (Low -> Critical)
-- =========================================================
SELECT
    risk_tier,
    COUNT(*)                                  AS patients,
    ROUND(AVG(risk_score), 1)                  AS avg_risk_score,
    ROUND(100.0 * SUM(cardio) / COUNT(*), 2)   AS disease_rate_pct
FROM cardio_data
GROUP BY risk_tier
ORDER BY avg_risk_score;

-- =========================================================
-- 9. Blood pressure quartile analysis
-- =========================================================
WITH quartiles AS (
    SELECT *, NTILE(4) OVER (ORDER BY ap_hi) AS bp_quartile
    FROM cardio_data
)
SELECT
    bp_quartile,
    MIN(ap_hi) AS min_systolic,
    MAX(ap_hi) AS max_systolic,
    COUNT(*)   AS patients,
    ROUND(100.0 * SUM(cardio) / COUNT(*), 2) AS disease_rate_pct
FROM quartiles
GROUP BY bp_quartile
ORDER BY bp_quartile;

-- =========================================================
-- 10. Top 5% highest-risk patients (for targeted outreach)
-- =========================================================
SELECT id, age, gender_label, bmi, ap_hi, ap_lo, cholesterol_label, risk_score, risk_tier
FROM cardio_data
ORDER BY risk_score DESC
LIMIT (SELECT CAST(COUNT(*) * 0.05 AS INT) FROM cardio_data);

-- =========================================================
-- 11. Reusable view for BI tools / dashboards
-- =========================================================
CREATE OR REPLACE VIEW v_cardio_summary AS
SELECT
    age_group, gender_label, bp_category, bmi_category, risk_tier,
    COUNT(*)                                  AS patients,
    ROUND(100.0 * SUM(cardio) / COUNT(*), 2)   AS disease_rate_pct,
    ROUND(AVG(risk_score), 1)                  AS avg_risk_score
FROM cardio_data
GROUP BY age_group, gender_label, bp_category, bmi_category, risk_tier;

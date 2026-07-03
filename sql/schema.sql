-- =========================================================
-- Cardiovascular Risk Analysis - Schema
-- =========================================================
CREATE TABLE cardio_data (
    id                INTEGER PRIMARY KEY,
    age               NUMERIC(4,1),
    gender            SMALLINT,
    gender_label      VARCHAR(10),
    height            NUMERIC(5,1),
    weight            NUMERIC(5,1),
    bmi               NUMERIC(5,1),
    bmi_category      VARCHAR(20),
    ap_hi             SMALLINT,
    ap_lo             SMALLINT,
    pulse_pressure    SMALLINT,
    bp_category       VARCHAR(30),
    cholesterol       SMALLINT,
    cholesterol_label VARCHAR(20),
    gluc              SMALLINT,
    gluc_label        VARCHAR(20),
    smoke             SMALLINT,
    alco              SMALLINT,
    active            SMALLINT,
    age_group         VARCHAR(10),
    risk_score        NUMERIC(5,1),
    risk_tier         VARCHAR(10),
    cardio            SMALLINT
);

-- Load with (Postgres example):
-- \copy cardio_data FROM 'excel_cleaned_cardio_data.csv' WITH (FORMAT csv, HEADER true);

CREATE INDEX idx_cardio_age_group   ON cardio_data (age_group);
CREATE INDEX idx_cardio_risk_tier   ON cardio_data (risk_tier);
CREATE INDEX idx_cardio_bp_category ON cardio_data (bp_category);

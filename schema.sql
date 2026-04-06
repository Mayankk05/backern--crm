-- Database schema for CRM Analysis Platform

-- Table 1: users
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR,
    phone VARCHAR,
    address TEXT,
    account_status VARCHAR DEFAULT 'active',
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Table 2: health_data
CREATE TABLE IF NOT EXISTS health_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    blood_pressure_systolic FLOAT,
    blood_pressure_diastolic FLOAT,
    heart_rate INTEGER,
    chest_pain_type VARCHAR,
    creatinine FLOAT,
    urea FLOAT,
    eGFR FLOAT,
    urine_protein FLOAT,
    fasting_glucose FLOAT,
    HbA1c FLOAT,
    total_cholesterol FLOAT,
    ldl_cholesterol FLOAT,
    hdl_cholesterol FLOAT,
    triglycerides FLOAT,
    bmi FLOAT,
    smoking_status VARCHAR,
    physical_activity VARCHAR,
    family_history TEXT,
    medications JSONB,
    allergies JSONB,
    comorbidities JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_health_data_user_id ON health_data(user_id);
CREATE INDEX IF NOT EXISTS idx_health_data_created_at ON health_data(created_at);

-- Table 3: analysis_results
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    health_data_id UUID REFERENCES health_data(id),
    status VARCHAR DEFAULT 'processing',
    error_message TEXT,
    
    -- Cardiac Results
    cardiac_risk_level VARCHAR,
    cardiac_risk_score FLOAT,
    cardiac_probability FLOAT,
    cardiac_key_factors JSONB,
    
    -- Renal Results
    renal_risk_level VARCHAR,
    renal_risk_score FLOAT,
    renal_probability FLOAT,
    ckd_stage INTEGER,
    egfr_decline_rate VARCHAR,
    renal_key_factors JSONB,
    
    -- Metabolic Results
    metabolic_risk_level VARCHAR,
    metabolic_risk_score FLOAT,
    metabolic_probability FLOAT,
    diabetes_risk FLOAT,
    metabolic_syndrome_probability FLOAT,
    metabolic_key_factors JSONB,
    
    -- Aggregate Results
    crm_patterns_identified JSONB,
    overall_risk_level VARCHAR,
    cardiac_recommendations JSONB,
    renal_recommendations JSONB,
    metabolic_recommendations JSONB,
    lifestyle_recommendations JSONB,
    
    model_version VARCHAR,
    confidence_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analysis_results_user_id ON analysis_results(user_id);

-- Table 4: reports
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    analysis_id UUID REFERENCES analysis_results(id),
    report_title VARCHAR,
    report_type VARCHAR,
    pdf_path VARCHAR,
    html_path VARCHAR,
    file_size_bytes INTEGER,
    includes_charts BOOLEAN DEFAULT false,
    includes_trends BOOLEAN DEFAULT false,
    is_shareable BOOLEAN DEFAULT false,
    share_token VARCHAR UNIQUE,
    share_expiry TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    download_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);

-- Table 5: file_uploads
CREATE TABLE IF NOT EXISTS file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    original_filename VARCHAR NOT NULL,
    file_type VARCHAR NOT NULL,
    file_size_bytes INTEGER,
    mime_type VARCHAR,
    storage_path VARCHAR,
    status VARCHAR DEFAULT 'pending',
    extracted_data JSONB,
    extraction_status VARCHAR,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_file_uploads_user_id ON file_uploads(user_id);

-- Table 6: audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR NOT NULL, -- Unified with code
    resource VARCHAR,        -- Unified with code
    resource_id UUID,
    http_method VARCHAR,
    endpoint VARCHAR,
    request_params JSONB,
    status_code INTEGER,     -- Unified with code (response_status vs status_code)
    status VARCHAR,          -- Added to match some code usage
    success BOOLEAN,
    error_message TEXT,
    ip_address VARCHAR,
    user_agent VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    duration_ms INTEGER
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

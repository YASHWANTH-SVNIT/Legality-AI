-- Store all analyses
CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_chunks INTEGER,
    risky_clauses_found INTEGER,
    avg_risk_score REAL,
    overall_risk_level TEXT,
    processing_time_seconds REAL,
    compound_risks_found INTEGER
);

-- Store user feedback
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    category TEXT NOT NULL,
    feedback_type TEXT NOT NULL, -- 'false-positive', 'false-negative', 'approve-fix'
    approved BOOLEAN,            -- NULL for false-pos/neg, TRUE/FALSE for fix approval
    clause_text TEXT,
    system_risk_score REAL,
    suggested_fix TEXT,
    user_comment TEXT,           -- Added missing column
    pessimist_analysis TEXT,     -- Added missing column
    optimist_analysis TEXT,      -- Added missing column
    arbiter_reasoning TEXT,      -- Added missing column
    user_id TEXT DEFAULT 'anonymous',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);

-- Track category threshold adjustments
CREATE TABLE IF NOT EXISTS threshold_adjustments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    original_threshold REAL NOT NULL,
    adjusted_threshold REAL NOT NULL,
    adjustment_reason TEXT,
    feedback_count INTEGER,      -- How many feedbacks triggered this
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Store verified clauses from feedback
CREATE TABLE IF NOT EXISTS verified_clauses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clause_text TEXT NOT NULL,
    category TEXT NOT NULL,
    is_safe BOOLEAN NOT NULL,    -- TRUE = safe, FALSE = risky
    source TEXT,                  -- 'user-feedback', 'manual', 'cuad'
    confidence_score REAL,        -- Based on user agreement
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- System metrics for analytics
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,
    total_analyses INTEGER DEFAULT 0,
    avg_processing_time REAL,
    total_feedback_received INTEGER DEFAULT 0,
    false_positive_rate REAL,
    avg_user_satisfaction REAL,
    llm_api_calls INTEGER DEFAULT 0,
    llm_cost_usd REAL DEFAULT 0
);

-- Create indices for better query performance
CREATE INDEX IF NOT EXISTS idx_feedback_analysis ON feedback(analysis_id);
CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback(category);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_threshold_category ON threshold_adjustments(category);
CREATE INDEX IF NOT EXISTS idx_verified_category ON verified_clauses(category);
CREATE INDEX IF NOT EXISTS idx_metrics_date ON system_metrics(metric_date);

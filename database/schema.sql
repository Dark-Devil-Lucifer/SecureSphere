CREATE DATABASE IF NOT EXISTS securesphere
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE securesphere;


-- ============================================
-- USERS
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('ADMIN', 'SECURITY_ANALYST', 'VIEWER') NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);


-- ============================================
-- ASSETS
-- ============================================

CREATE TABLE IF NOT EXISTS assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_name VARCHAR(150) NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    operating_system VARCHAR(100),
    ip_address VARCHAR(45),
    hostname VARCHAR(150),
    owner VARCHAR(150),
    criticality ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
        NOT NULL DEFAULT 'MEDIUM',
    environment ENUM('DEVELOPMENT', 'TEST', 'PRODUCTION_SIMULATION')
        NOT NULL DEFAULT 'TEST',
    status ENUM('ACTIVE', 'INACTIVE', 'RETIRED')
        NOT NULL DEFAULT 'ACTIVE',
    last_assessment_date DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_asset_status (status),
    INDEX idx_asset_criticality (criticality)
);


-- ============================================
-- ASSESSMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    assessment_type VARCHAR(100) NOT NULL,
    performed_by INT NOT NULL,
    assessment_date DATETIME NOT NULL,
    status ENUM('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')
        NOT NULL DEFAULT 'PLANNED',
    summary TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_assessment_asset
        FOREIGN KEY (asset_id)
        REFERENCES assets(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_assessment_user
        FOREIGN KEY (performed_by)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    INDEX idx_assessment_asset (asset_id),
    INDEX idx_assessment_status (status)
);


-- ============================================
-- VULNERABILITIES
-- ============================================

CREATE TABLE IF NOT EXISTS vulnerabilities (
    id INT AUTO_INCREMENT PRIMARY KEY,

    vulnerability_id VARCHAR(30) NOT NULL UNIQUE,

    assessment_id INT,
    asset_id INT NOT NULL,

    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,

    severity ENUM(
        'INFORMATIONAL',
        'LOW',
        'MEDIUM',
        'HIGH',
        'CRITICAL'
    ) NOT NULL,

    risk_level ENUM(
        'LOW',
        'MEDIUM',
        'HIGH',
        'CRITICAL'
    ) NOT NULL,

    date_identified DATETIME NOT NULL,

    identified_by INT NOT NULL,

    evidence TEXT,
    remediation TEXT,

    status ENUM(
        'OPEN',
        'IN_PROGRESS',
        'RESOLVED',
        'CLOSED',
        'ACCEPTED_RISK'
    ) NOT NULL DEFAULT 'OPEN',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_vulnerability_assessment
        FOREIGN KEY (assessment_id)
        REFERENCES assessments(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_vulnerability_asset
        FOREIGN KEY (asset_id)
        REFERENCES assets(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_vulnerability_user
        FOREIGN KEY (identified_by)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    INDEX idx_vulnerability_severity (severity),
    INDEX idx_vulnerability_status (status),
    INDEX idx_vulnerability_asset (asset_id)
);


-- ============================================
-- SECURITY EVENTS
-- ============================================

CREATE TABLE IF NOT EXISTS security_events (
    id INT AUTO_INCREMENT PRIMARY KEY,

    event_id VARCHAR(30) NOT NULL UNIQUE,

    asset_id INT NOT NULL,

    event_timestamp DATETIME NOT NULL,

    source VARCHAR(150),

    event_type VARCHAR(100) NOT NULL,

    category ENUM(
        'AUTHENTICATION',
        'SYSTEM',
        'APPLICATION',
        'NETWORK',
        'PERMISSION',
        'SECURITY_ALERT'
    ) NOT NULL,

    severity ENUM(
        'INFORMATIONAL',
        'LOW',
        'MEDIUM',
        'HIGH',
        'CRITICAL'
    ) NOT NULL,

    description TEXT,

    status ENUM(
        'NEW',
        'REVIEWED',
        'RESOLVED'
    ) NOT NULL DEFAULT 'NEW',

    raw_data TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_event_asset
        FOREIGN KEY (asset_id)
        REFERENCES assets(id)
        ON DELETE CASCADE,

    INDEX idx_event_asset (asset_id),
    INDEX idx_event_category (category),
    INDEX idx_event_severity (severity),
    INDEX idx_event_timestamp (event_timestamp)
);


-- ============================================
-- ALERTS
-- ============================================

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,

    alert_id VARCHAR(30) NOT NULL UNIQUE,

    event_id INT,
    asset_id INT NOT NULL,

    rule_name VARCHAR(150) NOT NULL,
    title VARCHAR(255) NOT NULL,

    severity ENUM(
        'INFORMATIONAL',
        'LOW',
        'MEDIUM',
        'HIGH',
        'CRITICAL'
    ) NOT NULL,

    trigger_time DATETIME NOT NULL,

    description TEXT,

    status ENUM(
        'NEW',
        'INVESTIGATING',
        'RESOLVED',
        'CLOSED'
    ) NOT NULL DEFAULT 'NEW',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_alert_event
        FOREIGN KEY (event_id)
        REFERENCES security_events(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_alert_asset
        FOREIGN KEY (asset_id)
        REFERENCES assets(id)
        ON DELETE CASCADE,

    INDEX idx_alert_status (status),
    INDEX idx_alert_severity (severity),
    INDEX idx_alert_asset (asset_id)
);


-- ============================================
-- INCIDENTS
-- ============================================

CREATE TABLE IF NOT EXISTS incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,

    incident_id VARCHAR(30) NOT NULL UNIQUE,

    alert_id INT UNIQUE,
    asset_id INT NOT NULL,

    title VARCHAR(255) NOT NULL,

    severity ENUM(
        'INFORMATIONAL',
        'LOW',
        'MEDIUM',
        'HIGH',
        'CRITICAL'
    ) NOT NULL,

    detection_time DATETIME NOT NULL,

    assigned_analyst INT,

    status ENUM(
        'OPEN',
        'INVESTIGATING',
        'CONTAINED',
        'RESOLVED',
        'CLOSED'
    ) NOT NULL DEFAULT 'OPEN',

    investigation_notes TEXT,
    evidence TEXT,
    root_cause TEXT,
    containment_action TEXT,
    resolution TEXT,
    preventive_action TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_incident_alert
        FOREIGN KEY (alert_id)
        REFERENCES alerts(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_incident_asset
        FOREIGN KEY (asset_id)
        REFERENCES assets(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_incident_analyst
        FOREIGN KEY (assigned_analyst)
        REFERENCES users(id)
        ON DELETE SET NULL,

    INDEX idx_incident_status (status),
    INDEX idx_incident_severity (severity)
);


-- ============================================
-- INCIDENT TIMELINE
-- ============================================

CREATE TABLE IF NOT EXISTS incident_timeline (
    id INT AUTO_INCREMENT PRIMARY KEY,

    incident_id INT NOT NULL,

    event_time DATETIME NOT NULL,

    action VARCHAR(150) NOT NULL,

    description TEXT,

    performed_by INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_timeline_incident
        FOREIGN KEY (incident_id)
        REFERENCES incidents(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_timeline_user
        FOREIGN KEY (performed_by)
        REFERENCES users(id)
        ON DELETE SET NULL,

    INDEX idx_timeline_incident (incident_id)
);


-- ============================================
-- RISKS
-- ============================================

CREATE TABLE IF NOT EXISTS risks (
    id INT AUTO_INCREMENT PRIMARY KEY,

    risk_id VARCHAR(30) NOT NULL UNIQUE,

    asset_id INT NOT NULL,
    vulnerability_id INT,

    threat VARCHAR(255) NOT NULL,
    vulnerability TEXT,

    likelihood INT NOT NULL,
    impact INT NOT NULL,

    risk_score INT NOT NULL,

    risk_level ENUM(
        'LOW',
        'MEDIUM',
        'HIGH',
        'CRITICAL'
    ) NOT NULL,

    mitigation TEXT,

    status ENUM(
        'OPEN',
        'MITIGATED',
        'ACCEPTED',
        'CLOSED'
    ) NOT NULL DEFAULT 'OPEN',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_risk_asset
        FOREIGN KEY (asset_id)
        REFERENCES assets(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_risk_vulnerability
        FOREIGN KEY (vulnerability_id)
        REFERENCES vulnerabilities(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_likelihood
        CHECK (likelihood BETWEEN 1 AND 5),

    CONSTRAINT chk_impact
        CHECK (impact BETWEEN 1 AND 5),

    INDEX idx_risk_level (risk_level),
    INDEX idx_risk_status (status)
);


-- ============================================
-- MONITORING DATA
-- ============================================

CREATE TABLE IF NOT EXISTS monitoring_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    asset_id INT NOT NULL,

    timestamp DATETIME NOT NULL,

    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_usage DECIMAL(5,2),

    uptime_seconds BIGINT,

    running_services TEXT,

    security_status VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_monitoring_asset
        FOREIGN KEY (asset_id)
        REFERENCES assets(id)
        ON DELETE CASCADE,

    INDEX idx_monitoring_asset_time (asset_id, timestamp)
);


-- ============================================
-- AUTOMATION LOGS
-- ============================================

CREATE TABLE IF NOT EXISTS automation_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    automation_name VARCHAR(150) NOT NULL,

    execution_time DATETIME NOT NULL,

    status ENUM(
        'SUCCESS',
        'FAILED',
        'WARNING'
    ) NOT NULL,

    input_source VARCHAR(255),

    output_summary TEXT,

    output_data LONGTEXT,

    error_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_automation_name (automation_name),
    INDEX idx_automation_execution (execution_time)
);


-- ============================================
-- REPORTS
-- ============================================

CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,

    report_id VARCHAR(30) NOT NULL UNIQUE,

    report_type VARCHAR(100) NOT NULL,

    generated_by INT,

    generated_at DATETIME NOT NULL,

    file_name VARCHAR(255),

    file_path VARCHAR(500),

    status ENUM(
        'GENERATED',
        'FAILED'
    ) NOT NULL DEFAULT 'GENERATED',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_report_user
        FOREIGN KEY (generated_by)
        REFERENCES users(id)
        ON DELETE SET NULL,

    INDEX idx_report_type (report_type)
);

# SecureSphere

### Security Operations & Security Posture Management Platform

SecureSphere is a security operations platform designed to centralize security monitoring, vulnerability management, risk assessment, incident response, automated security analysis, and security reporting in a single interface.

It combines a web-based security dashboard with a FastAPI backend, MySQL database, security detection engine, automation services, and PDF reporting.

---

## Features

### 🔐 Authentication & Authorization
- JWT/Bearer-token authentication
- Role-based access control (RBAC)
- Admin, Security Analyst, and Viewer roles
- Protected API endpoints
- Role-restricted security operations

### 🖥️ Asset Management
- Centralized asset inventory
- Asset status tracking
- Asset criticality classification
- Security context for monitored assets

### 🛡️ Vulnerability Management
- Vulnerability tracking
- Severity classification
- Status management
- Risk relationship tracking
- Vulnerability-based alert generation

### 📡 Security Event Monitoring
- Security event collection
- Event classification
- Severity tracking
- Event-to-alert correlation
- Security event analysis

Supported detection scenarios include:

- Failed login attempts
- Authentication bypass attempts
- Malware signatures
- Network port scans
- Privileged commands
- Permission changes
- Service failures
- Suspicious system activity
- Critical security events

### 🚨 Alert Management
SecureSphere uses rule-based detection to generate alerts from security events.

Implemented rules include:

- Critical Security Event
- Unauthorized Access Attempt
- Failed Login Attempt
- Failed Login Spike / Brute Force
- Network Scan Detection
- Privileged Activity
- Service Failure
- Suspicious System Activity
- High Severity Vulnerability

### 🚑 Incident Response
- Automatic incident generation from qualifying alerts
- Incident severity and status tracking
- Incident ownership
- Incident timelines
- Incident investigation workflow

### ⚠️ Risk Assessment
- Risk identification
- Risk severity classification
- Risk status tracking
- Vulnerability-to-risk relationships
- Risk scoring and prioritization

### 🤖 Security Automation
SecureSphere provides automated security analysis and monitoring:

- Security Health Check
- Failed Login Analyzer
- System Resource Monitor
- Integrity Check

System monitoring includes:

- CPU utilization
- Memory utilization
- Disk utilization
- System uptime
- Monitored service status

### 📊 Security Posture
The dashboard provides an aggregated security posture view using:

- Critical alerts
- High alerts
- Open incidents
- Critical incidents
- High vulnerabilities
- Open high-risk findings
- Asset health

### 📄 Security Reporting
SecureSphere generates downloadable PDF reports including:

- Security Posture Report
- Vulnerability Assessment
- Security Incident Report
- Risk Assessment Report
- Asset Security Report

Reports are stored with metadata and can be downloaded through authenticated API endpoints.

---
Installation
1. Clone the repository
git clone git@github.com:Dark-Devil-Lucifer/SecureSphere.git
cd SecureSphere
2. Create a virtual environment
python -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables

Copy the example configuration:

cp .env.example .env

Configure the following values:

DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=securesphere
DB_USER=
DB_PASSWORD=

SECURESPHERE_USERNAME=admin

SECURESPHERE_ADMIN_PASSWORD=
SECURESPHERE_ANALYST_PASSWORD=
SECURESPHERE_VIEWER_PASSWORD=

JWT_SECRET_KEY=

ACCESS_TOKEN_EXPIRE_MINUTES=60

Never commit .env or real credentials to GitHub.

5. Prepare the database

Create the MySQL database and apply:

database/schema.sql
6. Start SecureSphere
uvicorn backend.main:app \
    --host 127.0.0.1 \
    --port 8000

## Architecture

```text
                         ┌──────────────────────┐
                         │      Web Browser      │
                         │ HTML / CSS / JavaScript│
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     FastAPI API      │
                         │ Authentication/RBAC  │
                         │ REST Endpoints       │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
      │ Security     │      │ Automation   │      │ Reporting    │
      │ Detection    │      │ Services     │      │ Engine       │
      │ Engine       │      │              │      │              │
      └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │      SQLAlchemy      │
                         │        ORM           │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │        MySQL         │
                         │   SecureSphere DB    │
                         └──────────────────────┘

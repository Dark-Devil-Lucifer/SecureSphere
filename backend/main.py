from fastapi import FastAPI
from sqlalchemy import text

from backend.config.database import engine
from backend.routes.auth import router as auth_router
from backend.routes.test_protected import router as test_router
from backend.routes.assets import router as assets_router
from fastapi.staticfiles import StaticFiles
from backend.routes.dashboard import router as dashboard_router
from backend.routes.vulnerabilities import (
    router as vulnerabilities_router
)
from backend.routes.security_events import (
    router as security_events_router
)
from backend.routes.alerts import (
    router as alerts_router
)
from backend.routes.incidents import (
    router as incidents_router
)
from backend.routes.risks import router as risks_router
from backend.routes.assessments import router as assessments_router
from backend.routes.automation import router as automation_router
from backend.routes.reports import router as reports_router

app = FastAPI(
    title="SecureSphere",
    description=(
        "Automated Vulnerability Assessment, "
        "Security Monitoring & Incident Response Platform"
    ),
    version="1.0.0"
)

app.mount(
    "/app",
    StaticFiles(
        directory="frontend",
        html=True
    ),
    name="frontend"
)

# Authentication routes
app.include_router(auth_router)
app.include_router(test_router)
app.include_router(assets_router)
app.include_router(dashboard_router)
app.include_router(vulnerabilities_router)
app.include_router(security_events_router)
app.include_router(alerts_router)
app.include_router(incidents_router)
app.include_router(risks_router)
app.include_router(assessments_router)
app.include_router(automation_router)
app.include_router(reports_router)

@app.get("/")
def root():

    return {
        "application": "SecureSphere",
        "status": "running",
        "message": "SecureSphere backend is operational"
    }


@app.get("/api/health")
def health_check():

    try:

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as error:

        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(error)
        }

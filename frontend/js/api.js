const API_BASE_URL = "http://127.0.0.1:8000";


function getToken() {
    return localStorage.getItem("access_token");
}


function getAuthHeaders() {
    const token = getToken();

    const headers = {
        "Content-Type": "application/json"
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    return headers;
}


async function apiRequest(
    endpoint,
    options = {}
) {
    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers: {
                ...getAuthHeaders(),
                ...(options.headers || {})
            }
        }
    );

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {

        const message =
            data?.detail ||
            `Request failed with status ${response.status}`;

        throw new Error(message);
    }

    return data;
}


async function loginUser(
    username,
    password
) {

    return apiRequest(
        "/api/auth/login",
        {
            method: "POST",
            body: JSON.stringify({
                username,
                password
            })
        }
    );
}


async function getAssets(
    query = ""
) {

    return apiRequest(
        `/api/assets${query}`
    );
}


async function getAsset(
    assetId
) {

    return apiRequest(
        `/api/assets/${assetId}`
    );
}


async function createAsset(
    asset
) {

    return apiRequest(
        "/api/assets",
        {
            method: "POST",
            body: JSON.stringify(asset)
        }
    );
}


async function updateAsset(
    assetId,
    asset
) {

    return apiRequest(
        `/api/assets/${assetId}`,
        {
            method: "PUT",
            body: JSON.stringify(asset)
        }
    );
}


async function updateAssetStatus(
    assetId,
    status
) {

    return apiRequest(
        `/api/assets/${assetId}/status`,
        {
            method: "PATCH",
            body: JSON.stringify({
                status
            })
        }
    );
}


async function archiveAsset(
    assetId
) {

    return apiRequest(
        `/api/assets/${assetId}`,
        {
            method: "DELETE"
        }
    );
}

async function getVulnerabilities(
    query = ""
) {

    return apiRequest(
        `/api/vulnerabilities${query}`
    );
}


async function getVulnerability(
    vulnerabilityId
) {

    return apiRequest(
        `/api/vulnerabilities/${vulnerabilityId}`
    );
}


async function createVulnerability(
    vulnerability
) {

    return apiRequest(
        "/api/vulnerabilities",
        {
            method: "POST",
            body: JSON.stringify(
                vulnerability
            )
        }
    );
}


async function updateVulnerabilityStatus(
    vulnerabilityId,
    status
) {

    return apiRequest(
        `/api/vulnerabilities/${vulnerabilityId}/status`,
        {
            method: "PATCH",
            body: JSON.stringify({
                status
            })
        }
    );
}

async function getAlerts(query = "") {

    return apiRequest(
        `/api/alerts${query}`
    );

}


async function updateAlert(
    alertId,
    status
) {

    return apiRequest(
        `/api/alerts/${alertId}/status`,
        {
            method: "PATCH",

            body: JSON.stringify({
                status: status
            })
        }
    );

}

async function getSecurityEvents(query = "") {

    return apiRequest(
        `/api/security-events${query}`
    );

}


async function updateSecurityEventStatus(
    eventId,
    status
) {

    return apiRequest(
        `/api/security-events/${eventId}/status`,
        {
            method: "PATCH",

            body: JSON.stringify({
                status: status
            })
        }
    );

}

// ============================================================
// INCIDENT API
// ============================================================

async function getIncidents() {

    return apiRequest(
        "/api/incidents"
    );

}


async function getIncident(
    incidentId
) {

    return apiRequest(
        `/api/incidents/${incidentId}`
    );

}


async function updateIncident(
    incidentId,
    incident
) {

    return apiRequest(
        `/api/incidents/${incidentId}`,
        {
            method: "PUT",
            body: JSON.stringify(
                incident
            )
        }
    );

}


async function getIncidentTimeline(
    incidentId
) {

    return apiRequest(
        `/api/incidents/${incidentId}/timeline`
    );

}


async function createIncidentTimeline(
    incidentId,
    timeline
) {

    return apiRequest(
        `/api/incidents/${incidentId}/timeline`,
        {
            method: "POST",
            body: JSON.stringify(
                timeline
            )
        }
    );

}

async function getRisks(
    query = ""
) {

    return apiRequest(
        `/api/risks${query}`
    );

}


async function getRisk(
    riskId
) {

    return apiRequest(
        `/api/risks/${riskId}`
    );

}


async function updateRiskStatus(
    riskId,
    status
) {

    return apiRequest(
        `/api/risks/${riskId}/status`,
        {
            method: "PATCH",

            body: JSON.stringify({
                status: status
            })
        }
    );

}

async function getAssessments(
    query = ""
) {

    return apiRequest(
        `/api/assessments${query}`
    );

}


async function getAssessment(
    assessmentId
) {

    return apiRequest(
        `/api/assessments/${assessmentId}`
    );

}


async function updateAssessmentStatus(
    assessmentId,
    status
) {

    return apiRequest(
        `/api/assessments/${assessmentId}/status`,
        {
            method: "PATCH",

            body: JSON.stringify({
                status: status
            })
        }
    );

}
async function getReports() {
    return apiRequest(
        "/api/reports"
    );
}


async function getReport(
    reportId
) {
    return apiRequest(
        `/api/reports/${reportId}`
    );
}


async function generateSecurityPostureReport() {
    return apiRequest(
        "/api/reports/security-posture",
        {
            method: "POST"
        }
    );
}


function getReportDownloadUrl(
    reportId
) {
    return `${API_BASE_URL}/api/reports/${reportId}/download`;
}

async function getLatestHealthCheck() {
    return apiRequest(
        "/api/automation/health"
    );
}


async function getLatestIntegrityCheck() {
    return apiRequest(
        "/api/automation/integrity"
    );
}
async function runFailedLoginAnalyzer() {
    return apiRequest(
        "/api/automation/failed-logins",
        {
            method: "POST"
        }
    );
}


async function getLatestFailedLoginAnalysis() {
    return apiRequest(
        "/api/automation/failed-logins"
    );
}

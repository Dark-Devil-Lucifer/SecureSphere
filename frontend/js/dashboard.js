if (!requireLogin()) {
    throw new Error("Authentication required");
}


document.addEventListener(
    "DOMContentLoaded",
    async function() {

        const user =
            getCurrentUser();


        if (!user) {
            logout();
            return;
        }


        document.getElementById(
            "userName"
        ).textContent =
            user.full_name;


        document.getElementById(
            "userRole"
        ).textContent =
            user.role;


        document.getElementById(
            "welcomeText"
        ).textContent =
            `Welcome back, ${user.full_name}`;


        document.getElementById(
            "logoutButton"
        ).addEventListener(
            "click",
            logout
        );


        await loadDashboard();

	await loadAttentionItems();

	await loadAutomationStatus();

    }
);


async function loadDashboard() {

    const platformStatus =
        document.getElementById(
            "platformStatus"
        );


    try {

        const data =
            await apiRequest(
                "/api/dashboard/summary"
            );


        document.getElementById(
            "totalAssets"
        ).textContent =
            data.assets.total;


        document.getElementById(
            "activeAssets"
        ).textContent =
            data.assets.active;


        document.getElementById(
            "criticalAssets"
        ).textContent =
            data.criticality.critical;


        document.getElementById(
            "highAssets"
        ).textContent =
            data.criticality.high;


        document.getElementById(
            "activeStatus"
        ).textContent =
            data.assets.active;


        document.getElementById(
            "inactiveStatus"
        ).textContent =
            data.assets.inactive;


        document.getElementById(
            "retiredStatus"
        ).textContent =
            data.assets.retired;


        document.getElementById(
            "criticalCount"
        ).textContent =
            data.criticality.critical;


        document.getElementById(
            "highCount"
        ).textContent =
            data.criticality.high;


        document.getElementById(
            "mediumCount"
        ).textContent =
            data.criticality.medium;


        document.getElementById(
            "lowCount"
        ).textContent =
            data.criticality.low;


        platformStatus.textContent =
            "SecureSphere backend is online and connected to the database.";

	// Vulnerabilities

	document.getElementById(
    	    "totalVulnerabilities"
	).textContent =
    	    data.vulnerabilities.total;


	document.getElementById(
            "criticalVulnerabilities"
	).textContent =
            data.vulnerabilities.critical;


	document.getElementById(
            "highVulnerabilities"
	).textContent =
            data.vulnerabilities.high;


	// Security Events

	document.getElementById(
            "totalSecurityEvents"
	).textContent =
            data.security_events.total;


	document.getElementById(
            "criticalSecurityEvents"
	).textContent =
    	    data.security_events.critical;


	document.getElementById(
    	    "openSecurityEvents"
	).textContent =
    	    data.security_events.open;


	// Alerts

	document.getElementById(
    	    "totalAlerts"
	).textContent =
    	    data.alerts.total;


	document.getElementById(
    	    "criticalAlerts"
	).textContent =
    	    data.alerts.critical;


	document.getElementById(
    	    "newAlerts"
	).textContent =
    	    data.alerts.new;


	// Incidents

	document.getElementById(
    	    "totalIncidents"
	).textContent =
    	    data.incidents.total;


	document.getElementById(
    	    "openIncidents"
	).textContent =
    	    data.incidents.open;


	document.getElementById(
    	    "criticalIncidents"
	).textContent =
    	    data.incidents.critical;


	// Risks

	document.getElementById(
    	    "totalRisks"
	).textContent =
    	    data.risks.total;


	document.getElementById(
    	    "criticalRisks"
	).textContent =
    	    data.risks.critical;


	document.getElementById(
    	    "openRisks"
	).textContent =
    	    data.risks.open;


	// Assessments

	document.getElementById(
    	    "totalAssessments"
	).textContent =
    	    data.assessments.total;


	document.getElementById(
    	    "inProgressAssessments"
	).textContent =
    	    data.assessments.in_progress;


	document.getElementById(
    	    "completedAssessments"
	).textContent =
    	    data.assessments.completed;

    } catch (error) {

        platformStatus.textContent =
            `Unable to load dashboard: ${error.message}`;

    }

}
async function loadAttentionItems() {

    const container =
        document.getElementById(
            "attentionList"
        );

    const countElement =
        document.getElementById(
            "attentionCount"
        );


    if (!container || !countElement) {
        return;
    }


    container.innerHTML = `
        <div class="attention-empty">
            Loading security items...
        </div>
    `;


    try {

        const [
            alerts,
            incidents,
            risks
        ] = await Promise.all([
            getAlerts(),
            getIncidents(),
            getRisks()
        ]);


        const items = [];


        /*
         * CRITICAL / NEW ALERTS
         */

        alerts
            .filter(
                alert =>
                    (
                        alert.severity === "CRITICAL" ||
                        alert.severity === "HIGH"
                    ) &&
                    (
                        alert.status === "NEW" ||
                        alert.status === "INVESTIGATING"
                    )
            )
            .forEach(
                alert => {

                    items.push({
                        type: "ALERT",
                        severity: alert.severity,
                        title: alert.title,
                        status: alert.status,
                        id: alert.alert_id,
                        action: "View Alerts",
                        url: "alerts.html"
                    });

                }
            );


        /*
         * OPEN / INVESTIGATING INCIDENTS
         */

        incidents
            .filter(
                incident =>
                    (
                        incident.status === "OPEN" ||
                        incident.status === "INVESTIGATING"
                    )
            )
            .forEach(
                incident => {

                    items.push({
                        type: "INCIDENT",
                        severity: incident.severity,
                        title: incident.title,
                        status: incident.status,
                        id: incident.incident_id,
                        action: "View Incidents",
                        url: "incidents.html"
                    });

                }
            );


        /*
         * OPEN CRITICAL / HIGH RISKS
         */

        risks
            .filter(
                risk =>
                    (
                        risk.risk_level === "CRITICAL" ||
                        risk.risk_level === "HIGH"
                    ) &&
                    (
                        risk.status === "OPEN"
                    )
            )
            .forEach(
                risk => {

                    items.push({
                        type: "RISK",
                        severity: risk.risk_level,
                        title: risk.threat,
                        status: risk.status,
                        id: risk.risk_id,
                        action: "Review Risks",
                        url: "risk-assessment.html"
                    });

                }
            );


        /*
         * Sort CRITICAL before HIGH
         */

        items.sort(
            (a, b) => {

                const priority = {
                    CRITICAL: 1,
                    HIGH: 2,
                    MEDIUM: 3,
                    LOW: 4
                };

                return (
                    (priority[a.severity] || 99) -
                    (priority[b.severity] || 99)
                );

            }
        );


        /*
         * Limit dashboard display
         */

        const visibleItems =
            items.slice(0, 6);


        countElement.textContent =
            items.length;


        if (!visibleItems.length) {

            container.innerHTML = `
                <div class="attention-empty">
                    No critical security items require attention.
                </div>
            `;

            return;
        }


        container.innerHTML =
            visibleItems
                .map(
                    item =>
                        createAttentionItem(item)
                )
                .join("");


        document
            .querySelectorAll(
                ".attention-action"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        function () {

                            window.location.href =
                                this.dataset.url;

                        }
                    );

                }
            );


    } catch (error) {

        countElement.textContent = "—";

        container.innerHTML = `
            <div class="attention-error">
                Unable to load security items:
                ${escapeHtml(error.message)}
            </div>
        `;

    }

}


function createAttentionItem(
    item
) {

    const severityClass =
        String(
            item.severity || ""
        ).toLowerCase();


    const statusClass =
        String(
            item.status || ""
        ).toLowerCase();


    return `
        <div class="attention-item">

            <div
                class="attention-severity ${severityClass}"
            >
                ${escapeHtml(
                    item.severity
                )}
            </div>


            <div class="attention-main">

                <div class="attention-title">
                    ${escapeHtml(
                        item.title
                    )}
                </div>


                <div class="attention-meta">

                    <span>
                        ${escapeHtml(
                            item.type
                        )}
                    </span>

                    <span>
                        ${escapeHtml(
                            item.id
                        )}
                    </span>

                    <span
                        class="attention-status ${statusClass}"
                    >
                        ${escapeHtml(
                            item.status
                        )}
                    </span>

                </div>

            </div>


            <button
                class="attention-action"
                data-url="${escapeHtml(
                    item.url
                )}"
            >
                ${escapeHtml(
                    item.action
                )}
            </button>

        </div>
    `;
}
function escapeHtml(value) {

    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}
async function loadAutomationStatus() {

    try {

        const [
            health,
            integrity,
	    failedLogin
        ] = await Promise.all([
            getLatestHealthCheck(),
            getLatestIntegrityCheck(),
	    getLatestFailedLoginAnalysis()
        ]);


        // SECURITY HEALTH

        const healthData =
            health.output_data;

        const healthMetrics =
            healthData.metrics;

	const postureScore =
	    document.getElementById(
	        "securityPostureScore"
	    );

	if (postureScore) {

	    postureScore.textContent =
	        healthData.security_score ?? "—";
	}

        const healthStatus =
            document.getElementById(
                "securityHealthStatus"
            );

        if (healthStatus) {

            healthStatus.textContent =
                healthData.status;

            healthStatus.className =
                `automation-status status-${String(
                    healthData.status
                ).toLowerCase()}`;
        }


        document.getElementById(
            "healthAssets"
        ).textContent =
            `${healthMetrics.active_assets}/${healthMetrics.total_assets}`;


        document.getElementById(
            "healthCriticalAlerts"
        ).textContent =
            healthMetrics.critical_alerts;


        document.getElementById(
            "healthHighAlerts"
        ).textContent =
            healthMetrics.high_alerts;


        document.getElementById(
            "healthOpenIncidents"
        ).textContent =
            healthMetrics.open_incidents;


        document.getElementById(
            "healthCriticalIncidents"
        ).textContent =
            healthMetrics.critical_incidents;


        document.getElementById(
            "healthHighVulnerabilities"
        ).textContent =
            healthMetrics.high_vulnerabilities;


        const findingsContainer =
            document.getElementById(
                "healthFindings"
            );


        if (
            healthData.findings &&
            healthData.findings.length > 0
        ) {

            findingsContainer.innerHTML = `
                <strong>Findings</strong>

                <ul>
                    ${healthData.findings
                        .map(
                            finding =>
                                `<li>${escapeHtml(
                                    finding
                                )}</li>`
                        )
                        .join("")}
                </ul>
            `;

        } else {

            findingsContainer.innerHTML = `
                <span>
                    No security findings reported.
                </span>
            `;
        }


        // INTEGRITY

        const integrityData =
            integrity.output_data;

        const integrityMetrics =
            integrityData.metrics;


        document.getElementById(
            "healthExecutionStatus"
        ).textContent =
            health.status;


        document.getElementById(
            "integrityStatus"
        ).textContent =
            integrityData.status;


        document.getElementById(
            "integrityFileCount"
        ).textContent =
            integrityMetrics.current_files;


        document.getElementById(
            "integrityModifiedFiles"
        ).textContent =
            integrityMetrics.modified_files;


        document.getElementById(
            "integrityMissingFiles"
        ).textContent =
            integrityMetrics.missing_files;

	        // FAILED LOGIN ANALYZER

        const failedLoginData =
            failedLogin.output_data;

        const failedLoginMetrics =
            failedLoginData.metrics;


        const failedLoginStatus =
            document.getElementById(
                "failedLoginStatus"
            );

        if (failedLoginStatus) {

            failedLoginStatus.textContent =
                failedLoginData.status;

            failedLoginStatus.className =
                `automation-status status-${String(
                    failedLoginData.status
                ).toLowerCase()}`;
        }


        document.getElementById(
            "failedLoginAttempts"
        ).textContent =
            failedLoginMetrics.total_failed_logins;


        document.getElementById(
            "failedLoginAssets"
        ).textContent =
            failedLoginMetrics.affected_assets;


        document.getElementById(
            "failedLoginRepeatedSources"
        ).textContent =
            failedLoginMetrics.repeated_sources;


        document.getElementById(
            "failedLoginSpikes"
        ).textContent =
            failedLoginMetrics.suspicious_spikes;


        const failedLoginFindings =
            document.getElementById(
                "failedLoginFindings"
            );


        if (
            failedLoginFindings &&
            failedLoginData.findings &&
            failedLoginData.findings.length > 0
        ) {

            failedLoginFindings.innerHTML = `
                <strong>Findings</strong>

                <ul>
                    ${failedLoginData.findings
                        .map(
                            finding =>
                                `<li>${escapeHtml(
                                    finding
                                )}</li>`
                        )
                        .join("")}
                </ul>
            `;

        } else if (failedLoginFindings) {

            failedLoginFindings.innerHTML = `
                <span>
                    No suspicious failed-login activity detected.
                </span>
            `;
        }

    } catch (error) {

        console.error(
            "Failed to load automation status:",
            error
        );

        const healthStatus =
            document.getElementById(
                "securityHealthStatus"
            );

        if (healthStatus) {

            healthStatus.textContent =
                "UNAVAILABLE";
        }
    }
}



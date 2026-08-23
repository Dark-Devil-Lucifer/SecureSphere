if (!requireLogin()) {
    throw new Error("Authentication required");
}


let currentIncidentId = null;

let allIncidents = [];


document.addEventListener(
    "DOMContentLoaded",
    async function () {

        const user = getCurrentUser();

        if (!user) {
            logout();
            return;
        }


        document.getElementById(
            "userName"
        ).textContent = user.full_name;


        document.getElementById(
            "userRole"
        ).textContent = user.role;


        document.getElementById(
            "logoutButton"
        ).addEventListener(
            "click",
            logout
        );


        document.getElementById(
            "searchInput"
        ).addEventListener(
            "input",
            filterIncidents
        );


        document.getElementById(
            "severityFilter"
        ).addEventListener(
            "change",
            filterIncidents
        );


        document.getElementById(
            "statusFilter"
        ).addEventListener(
            "change",
            filterIncidents
        );


        document.getElementById(
            "closeDetailsButton"
        ).addEventListener(
            "click",
            closeDetails
        );


        document.getElementById(
            "saveIncidentButton"
        ).addEventListener(
            "click",
            saveIncident
        );


        document.getElementById(
            "addTimelineButton"
        ).addEventListener(
            "click",
            addTimelineEntry
        );


        await loadIncidents();

    }
);


async function loadIncidents() {

    const tbody =
        document.getElementById(
            "incidentTableBody"
        );


    try {

        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    Loading incidents...
                </td>
            </tr>
        `;


        allIncidents =
            await getIncidents();


        filterIncidents();

    } catch (error) {

        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    ${escapeHtml(error.message)}
                </td>
            </tr>
        `;

    }

}


function filterIncidents() {

    const search =
        document.getElementById(
            "searchInput"
        ).value
            .trim()
            .toLowerCase();


    const severity =
        document.getElementById(
            "severityFilter"
        ).value;


    const status =
        document.getElementById(
            "statusFilter"
        ).value;


    const filtered =
        allIncidents.filter(
            incident => {

                const matchesSearch =
                    !search ||
                    incident.incident_id
                        .toLowerCase()
                        .includes(search) ||
                    incident.title
                        .toLowerCase()
                        .includes(search);


                const matchesSeverity =
                    !severity ||
                    incident.severity === severity;


                const matchesStatus =
                    !status ||
                    incident.status === status;


                return (
                    matchesSearch &&
                    matchesSeverity &&
                    matchesStatus
                );

            }
        );


    renderIncidents(filtered);

}


function renderIncidents(
    incidents
) {

    const tbody =
        document.getElementById(
            "incidentTableBody"
        );


    document.getElementById(
        "incidentCount"
    ).textContent =
        `${incidents.length} incident(s)`;


    if (!incidents.length) {

        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    No incidents found.
                </td>
            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        incidents
            .map(
                incident =>
                    createIncidentRow(
                        incident
                    )
            )
            .join("");


    document
        .querySelectorAll(
            ".view-button"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    function () {

                        openIncident(
                            Number(
                                this.dataset.id
                            )
                        );

                    }
                );

            }
        );

}


function createIncidentRow(
    incident
) {

    const severityClass =
        `severity-${incident.severity.toLowerCase()}`;


    const statusClass =
        `status-${incident.status.toLowerCase()}`;


    return `
        <tr>

            <td class="incident-id">
                ${escapeHtml(
                    incident.incident_id
                )}
            </td>

            <td>
                ${escapeHtml(
                    incident.title
                )}
            </td>

            <td>
                <span
                    class="severity-badge ${severityClass}"
                >
                    ${escapeHtml(
                        incident.severity
                    )}
                </span>
            </td>

            <td>
                <span
                    class="status-badge ${statusClass}"
                >
                    ${escapeHtml(
                        incident.status
                    )}
                </span>
            </td>

            <td>
                #${incident.asset_id}
            </td>

            <td>
                ${formatDate(
                    incident.detection_time
                )}
            </td>

            <td>
                ${
                    incident.assigned_analyst
                        ? "#" +
                          incident.assigned_analyst
                        : "Unassigned"
                }
            </td>

            <td>
                <button
                    class="view-button"
                    data-id="${incident.id}"
                >
                    Investigate
                </button>
            </td>

        </tr>
    `;

}


async function openIncident(
    incidentId
) {

    try {

        currentIncidentId =
            incidentId;


        const incident =
            await getIncident(
                incidentId
            );


        document.getElementById(
            "incidentDetails"
        ).classList.remove(
            "hidden"
        );


        document.getElementById(
            "detailsTitle"
        ).textContent =
            incident.title;


        document.getElementById(
            "detailsIncidentId"
        ).textContent =
            incident.incident_id;


        document.getElementById(
            "detailsSeverity"
        ).textContent =
            incident.severity;


        document.getElementById(
            "detailsStatus"
        ).textContent =
            incident.status;


        document.getElementById(
            "detailsAsset"
        ).textContent =
            `#${incident.asset_id}`;


        document.getElementById(
            "detailsAlert"
        ).textContent =
            incident.alert_id
                ? `#${incident.alert_id}`
                : "None";


        document.getElementById(
            "detailsAnalyst"
        ).textContent =
            incident.assigned_analyst
                ? `#${incident.assigned_analyst}`
                : "Unassigned";


        document.getElementById(
            "detailsDetection"
        ).textContent =
            formatDate(
                incident.detection_time
            );


        document.getElementById(
            "investigationNotes"
        ).value =
            incident.investigation_notes || "";


        document.getElementById(
            "evidence"
        ).value =
            incident.evidence || "";


        document.getElementById(
            "rootCause"
        ).value =
            incident.root_cause || "";


        document.getElementById(
            "containmentAction"
        ).value =
            incident.containment_action || "";


        document.getElementById(
            "resolution"
        ).value =
            incident.resolution || "";


        document.getElementById(
            "preventiveAction"
        ).value =
            incident.preventive_action || "";


        document.getElementById(
            "incidentStatus"
        ).value =
            incident.status;


        await loadTimeline(
            incidentId
        );


        document
            .getElementById(
                "incidentDetails"
            )
            .scrollIntoView({
                behavior: "smooth"
            });

    } catch (error) {

        alert(
            error.message
        );

    }

}


async function loadTimeline(
    incidentId
) {

    const container =
        document.getElementById(
            "timelineContainer"
        );


    try {

        const timeline =
            await getIncidentTimeline(
                incidentId
            );


        if (!timeline.length) {

            container.innerHTML = `
                <div class="empty-state">
                    No timeline entries yet.
                </div>
            `;

            return;

        }


        container.innerHTML =
            timeline
                .map(
                    entry => `
                        <div class="timeline-item">

                            <span class="timeline-dot"></span>

                            <h5>
                                ${escapeHtml(
                                    entry.action
                                )}
                            </h5>

                            <p>
                                ${escapeHtml(
                                    entry.description ||
                                    ""
                                )}
                            </p>

                            <span class="timeline-time">
                                ${formatDate(
                                    entry.event_time
                                )}
                            </span>

                        </div>
                    `
                )
                .join("");

    } catch (error) {

        container.innerHTML = `
            <div class="empty-state">
                ${escapeHtml(
                    error.message
                )}
            </div>
        `;

    }

}


async function saveIncident() {

    if (!currentIncidentId) {
        return;
    }


    const payload = {

        status:
            document.getElementById(
                "incidentStatus"
            ).value,

        investigation_notes:
            document.getElementById(
                "investigationNotes"
            ).value.trim(),

        evidence:
            document.getElementById(
                "evidence"
            ).value.trim(),

        root_cause:
            document.getElementById(
                "rootCause"
            ).value.trim(),

        containment_action:
            document.getElementById(
                "containmentAction"
            ).value.trim(),

        resolution:
            document.getElementById(
                "resolution"
            ).value.trim(),

        preventive_action:
            document.getElementById(
                "preventiveAction"
            ).value.trim()

    };


    try {

        await updateIncident(
            currentIncidentId,
            payload
        );


        alert(
            "Incident updated successfully."
        );


        await loadIncidents();


        await openIncident(
            currentIncidentId
        );

    } catch (error) {

        alert(
            error.message
        );

    }

}


async function addTimelineEntry() {

    if (!currentIncidentId) {
        return;
    }


    const action =
        document.getElementById(
            "timelineAction"
        ).value.trim();


    const description =
        document.getElementById(
            "timelineDescription"
        ).value.trim();


    if (!action) {

        alert(
            "Please enter a timeline action."
        );

        return;

    }


    try {

        await createIncidentTimeline(
            currentIncidentId,
            {
                event_time:
                    new Date().toISOString(),
                action: action,
                description: description
            }
        );


        document.getElementById(
            "timelineAction"
        ).value = "";


        document.getElementById(
            "timelineDescription"
        ).value = "";


        await loadTimeline(
            currentIncidentId
        );

    } catch (error) {

        alert(
            error.message
        );

    }

}


function closeDetails() {

    currentIncidentId = null;


    document.getElementById(
        "incidentDetails"
    ).classList.add(
        "hidden"
    );

}


function formatDate(
    value
) {

    if (!value) {
        return "-";
    }


    const date =
        new Date(value);


    if (Number.isNaN(
        date.getTime()
    )) {

        return value;

    }


    return date.toLocaleString();

}


function escapeHtml(
    value
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value ?? "";


    return div.innerHTML;

}

if (!requireLogin()) {
    throw new Error("Authentication required");
}


let currentAlertId = null;


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
            "logoutButton"
        ).addEventListener(
            "click",
            logout
        );


        document.getElementById(
            "searchInput"
        ).addEventListener(
            "input",
            loadAlerts
        );


        document.getElementById(
            "severityFilter"
        ).addEventListener(
            "change",
            loadAlerts
        );


        document.getElementById(
            "statusFilter"
        ).addEventListener(
            "change",
            loadAlerts
        );


        document.getElementById(
            "closeModalButton"
        ).addEventListener(
            "click",
            closeModal
        );


        document.getElementById(
            "updateStatusButton"
        ).addEventListener(
            "click",
            updateAlertStatus
        );


        await loadAlerts();

    }
);


async function loadAlerts() {

    const search =
        document.getElementById(
            "searchInput"
        ).value.trim();


    const severity =
        document.getElementById(
            "severityFilter"
        ).value;


    const status =
        document.getElementById(
            "statusFilter"
        ).value;


    const params =
        new URLSearchParams();


    if (search) {

        params.set(
            "search",
            search
        );

    }


    if (severity) {

        params.set(
            "severity",
            severity
        );

    }


    if (status) {

        params.set(
            "status",
            status
        );

    }


    const query =
        params.toString()
            ? `?${params.toString()}`
            : "";


    const tbody =
        document.getElementById(
            "alertTableBody"
        );


    try {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="7"
                    class="empty-state"
                >
                    Loading alerts...
                </td>
            </tr>
        `;


        const alerts =
            await getAlerts(query);


        renderAlerts(alerts);


    } catch (error) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="7"
                    class="empty-state"
                >
                    ${escapeHtml(error.message)}
                </td>
            </tr>
        `;

    }

}


function renderAlerts(alerts) {

    const tbody =
        document.getElementById(
            "alertTableBody"
        );


    updateSummary(alerts);


    document.getElementById(
        "alertCount"
    ).textContent =
        `${alerts.length} alert(s) found`;


    if (!alerts.length) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="7"
                    class="empty-state"
                >
                    No alerts found.
                </td>
            </tr>
        `;

        return;
    }


    tbody.innerHTML =
        alerts.map(
            alert => createAlertRow(alert)
        ).join("");


    document.querySelectorAll(
        ".view-button"
    ).forEach(
        button => {

            button.addEventListener(
                "click",
                function() {

                    const id =
                        Number(
                            this.dataset.id
                        );

                    const alert =
                        alerts.find(
                            item =>
                                item.id === id
                        );

                    if (alert) {

                        openAlertModal(
                            alert
                        );

                    }

                }
            );

        }
    );

}


function createAlertRow(alert) {

    const severity =
        String(
            alert.severity
        ).toLowerCase();


    const status =
        String(
            alert.status
        ).toLowerCase();


    const triggerTime =
        formatDate(
            alert.trigger_time
        );


    return `

        <tr>

            <td>
                <span class="alert-id">
                    ${escapeHtml(alert.alert_id)}
                </span>
            </td>


            <td>
                ${escapeHtml(alert.title)}
            </td>


            <td>
                <span class="rule-name">
                    ${escapeHtml(alert.rule_name)}
                </span>
            </td>


            <td>

                <span
                    class="
                        severity-badge
                        severity-${severity}
                    "
                >
                    ${escapeHtml(alert.severity)}
                </span>

            </td>


            <td>

                <span
                    class="
                        status-badge
                        status-${status}
                    "
                >
                    ${escapeHtml(alert.status)}
                </span>

            </td>


            <td>
                ${escapeHtml(triggerTime)}
            </td>


            <td>

                <button
                    class="view-button"
                    data-id="${alert.id}"
                >
                    View
                </button>

            </td>

        </tr>

    `;
}


function updateSummary(alerts) {

    const total =
        alerts.length;


    const critical =
        alerts.filter(
            alert =>
                alert.severity === "CRITICAL"
        ).length;


    const high =
        alerts.filter(
            alert =>
                alert.severity === "HIGH"
        ).length;


    const newAlerts =
        alerts.filter(
            alert =>
                alert.status === "NEW"
        ).length;


    document.getElementById(
        "totalAlerts"
    ).textContent =
        total;


    document.getElementById(
        "criticalAlerts"
    ).textContent =
        critical;


    document.getElementById(
        "highAlerts"
    ).textContent =
        high;


    document.getElementById(
        "newAlerts"
    ).textContent =
        newAlerts;

}


function openAlertModal(alert) {

    currentAlertId =
        alert.id;


    const details =
        document.getElementById(
            "alertDetails"
        );


    details.innerHTML = `

        <div class="detail-grid">

            <div class="detail-item">

                <span class="detail-label">
                    Alert ID
                </span>

                <span class="detail-value">
                    ${escapeHtml(alert.alert_id)}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Event ID
                </span>

                <span class="detail-value">
                    ${escapeHtml(String(alert.event_id))}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Asset ID
                </span>

                <span class="detail-value">
                    ${escapeHtml(String(alert.asset_id))}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Rule
                </span>

                <span class="detail-value">
                    ${escapeHtml(alert.rule_name)}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Severity
                </span>

                <span class="detail-value">
                    ${escapeHtml(alert.severity)}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Trigger Time
                </span>

                <span class="detail-value">
                    ${escapeHtml(
                        formatDate(alert.trigger_time)
                    )}
                </span>

            </div>


            <div class="detail-item full">

                <span class="detail-label">
                    Description
                </span>

                <span class="detail-value">
                    ${escapeHtml(
                        alert.description || "No description"
                    )}
                </span>

            </div>

        </div>

    `;


    document.getElementById(
        "alertStatusSelect"
    ).value =
        alert.status;


    document.getElementById(
        "alertModal"
    ).classList.remove(
        "hidden"
    );

}


function closeModal() {

    currentAlertId =
        null;


    document.getElementById(
        "alertModal"
    ).classList.add(
        "hidden"
    );

}


async function updateAlertStatus() {

    if (!currentAlertId) {

        return;
    }


    const status =
        document.getElementById(
            "alertStatusSelect"
        ).value;


    try {

        await updateAlert(
            currentAlertId,
            status
        );


        closeModal();

        await loadAlerts();


    } catch (error) {

        alert(
            error.message
        );

    }

}


function formatDate(value) {

    if (!value) {

        return "N/A";

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


function escapeHtml(value) {

    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );

}

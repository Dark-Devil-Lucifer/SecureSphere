if (!requireLogin()) {
    throw new Error("Authentication required");
}


let selectedEvent = null;


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
            "closeModalButton"
        ).addEventListener(
            "click",
            closeEventModal
        );


        document.getElementById(
            "cancelButton"
        ).addEventListener(
            "click",
            closeEventModal
        );


        document.getElementById(
            "reviewButton"
        ).addEventListener(
            "click",
            function () {
                updateSelectedEventStatus("REVIEWED");
            }
        );


        document.getElementById(
            "resolveButton"
        ).addEventListener(
            "click",
            function () {
                updateSelectedEventStatus("RESOLVED");
            }
        );


        document.getElementById(
            "searchInput"
        ).addEventListener(
            "input",
            loadSecurityEvents
        );


        document.getElementById(
            "severityFilter"
        ).addEventListener(
            "change",
            loadSecurityEvents
        );


        document.getElementById(
            "categoryFilter"
        ).addEventListener(
            "change",
            loadSecurityEvents
        );


        document.getElementById(
            "statusFilter"
        ).addEventListener(
            "change",
            loadSecurityEvents
        );


        await loadSecurityEvents();

    }
);


/* =========================
   LOAD EVENTS
========================= */

async function loadSecurityEvents() {

    const search =
        document.getElementById(
            "searchInput"
        ).value.trim();


    const severity =
        document.getElementById(
            "severityFilter"
        ).value;


    const category =
        document.getElementById(
            "categoryFilter"
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


    if (category) {
        params.set(
            "category",
            category
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
            "eventTableBody"
        );


    try {

        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    Loading security events...
                </td>
            </tr>
        `;


        const events =
            await getSecurityEvents(query);


        renderSecurityEvents(events);


    } catch (error) {

        console.error(
            "Failed to load security events:",
            error
        );


        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    ${escapeHtml(error.message)}
                </td>
            </tr>
        `;

    }

}


/* =========================
   RENDER EVENTS
========================= */

function renderSecurityEvents(events) {

    const tbody =
        document.getElementById(
            "eventTableBody"
        );


    document.getElementById(
        "eventCount"
    ).textContent =
        `${events.length} event(s) found`;


    if (!events.length) {

        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    No security events found.
                </td>
            </tr>
        `;

        return;
    }


    tbody.innerHTML =
        events
            .map(
                event =>
                    createEventRow(event)
            )
            .join("");


    attachEventActions();

}


/* =========================
   CREATE TABLE ROW
========================= */

function createEventRow(event) {

    const severityClass =
        getSeverityClass(
            event.severity
        );


    const statusClass =
        getStatusClass(
            event.status
        );


    return `
        <tr>

            <td>
                <span class="event-id">
                    ${escapeHtml(event.event_id)}
                </span>
            </td>


            <td>
                <span class="event-type">
                    ${escapeHtml(event.event_type)}
                </span>
            </td>


            <td>
                <span class="category-badge">
                    ${escapeHtml(formatLabel(event.category))}
                </span>
            </td>


            <td>
                <span class="severity-badge ${severityClass}">
                    ${escapeHtml(event.severity)}
                </span>
            </td>


            <td>
                ${escapeHtml(event.source || "-")}
            </td>


            <td>
                ${escapeHtml(formatDate(event.event_timestamp))}
            </td>


            <td>
                <span class="status-badge ${statusClass}">
                    ${escapeHtml(event.status)}
                </span>
            </td>


            <td>

                <button
                    class="view-button"
                    data-event-id="${event.id}"
                >
                    View
                </button>

            </td>

        </tr>
    `;
}


/* =========================
   ROW ACTIONS
========================= */

function attachEventActions() {

    const buttons =
        document.querySelectorAll(
            ".view-button"
        );


    buttons.forEach(
        button => {

            button.addEventListener(
                "click",
                function () {

                    const eventId =
                        Number(
                            this.dataset.eventId
                        );


                    openEventDetails(
                        eventId
                    );

                }
            );

        }
    );

}


/* =========================
   OPEN EVENT DETAILS
========================= */

async function openEventDetails(eventId) {

    try {

        const events =
            await getSecurityEvents(
                `?id=${eventId}`
            );


        if (!events.length) {

            alert(
                "Security event not found."
            );

            return;
        }


        selectedEvent =
            events[0];


        renderEventDetails(
            selectedEvent
        );


        document.getElementById(
            "eventModal"
        ).classList.add(
            "show"
        );


        updateActionButtons(
            selectedEvent.status
        );


    } catch (error) {

        console.error(
            "Failed to load event details:",
            error
        );


        alert(
            error.message
        );

    }

}


/* =========================
   EVENT DETAILS
========================= */

function renderEventDetails(event) {

    const container =
        document.getElementById(
            "eventDetails"
        );


    container.innerHTML = `

        <div class="detail-grid">


            <div class="detail-item">

                <span class="detail-label">
                    Event ID
                </span>

                <span class="detail-value">
                    ${escapeHtml(event.event_id)}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Database ID
                </span>

                <span class="detail-value">
                    ${escapeHtml(event.id)}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Event Type
                </span>

                <span class="detail-value">
                    ${escapeHtml(event.event_type)}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Category
                </span>

                <span class="detail-value">
                    ${escapeHtml(
                        formatLabel(event.category)
                    )}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Severity
                </span>

                <span class="detail-value">
                    ${escapeHtml(event.severity)}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Status
                </span>

                <span class="detail-value">
                    ${escapeHtml(event.status)}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Asset ID
                </span>

                <span class="detail-value">
                    ${escapeHtml(event.asset_id)}
                </span>

            </div>


            <div class="detail-item">

                <span class="detail-label">
                    Source
                </span>

                <span class="detail-value">
                    ${escapeHtml(event.source || "-")}
                </span>

            </div>


            <div class="detail-item full-width">

                <span class="detail-label">
                    Event Timestamp
                </span>

                <span class="detail-value">
                    ${escapeHtml(
                        formatDate(event.event_timestamp)
                    )}
                </span>

            </div>


            <div class="detail-item full-width">

                <span class="detail-label">
                    Description
                </span>

                <span class="detail-value">
                    ${escapeHtml(
                        event.description || "-"
                    )}
                </span>

            </div>


            <div class="detail-item full-width">

                <span class="detail-label">
                    Raw Event Data
                </span>

                <span class="detail-value raw-data">
                    ${escapeHtml(
                        event.raw_data || "-"
                    )}
                </span>

            </div>


        </div>

    `;

}


/* =========================
   UPDATE EVENT STATUS
========================= */

async function updateSelectedEventStatus(
    newStatus
) {

    if (!selectedEvent) {
        return;
    }


    if (
        selectedEvent.status ===
        newStatus
    ) {

        return;

    }


    try {

        const updated =
            await updateSecurityEventStatus(
                selectedEvent.id,
                newStatus
            );


        selectedEvent =
            updated;


        renderEventDetails(
            selectedEvent
        );


        updateActionButtons(
            selectedEvent.status
        );


        await loadSecurityEvents();


        alert(
            `Event status updated to ${newStatus}.`
        );


    } catch (error) {

        console.error(
            "Failed to update event:",
            error
        );


        alert(
            error.message
        );

    }

}


/* =========================
   MODAL BUTTONS
========================= */

function updateActionButtons(status) {

    const reviewButton =
        document.getElementById(
            "reviewButton"
        );


    const resolveButton =
        document.getElementById(
            "resolveButton"
        );


    reviewButton.disabled =
        status !== "NEW";


    resolveButton.disabled =
        status === "RESOLVED";

}


function closeEventModal() {

    selectedEvent = null;


    document.getElementById(
        "eventModal"
    ).classList.remove(
        "show"
    );

}


/* =========================
   HELPERS
========================= */

function getSeverityClass(
    severity
) {

    return `severity-${String(
        severity || ""
    ).toLowerCase()}`;

}


function getStatusClass(
    status
) {

    return `status-${String(
        status || ""
    ).toLowerCase()}`;

}


function formatLabel(value) {

    if (!value) {
        return "-";
    }


    return String(value)
        .toLowerCase()
        .split("_")
        .map(
            word =>
                word.charAt(0).toUpperCase() +
                word.slice(1)
        )
        .join(" ");

}


function formatDate(value) {

    if (!value) {
        return "-";
    }


    const date =
        new Date(value);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return value;

    }


    return date.toLocaleString();

}


function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}

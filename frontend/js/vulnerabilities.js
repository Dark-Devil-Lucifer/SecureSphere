if (!requireLogin()) {
    throw new Error("Authentication required");
}


let vulnerabilities = [];
let assets = [];


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
            "addVulnerabilityButton"
        ).addEventListener(
            "click",
            openCreateModal
        );


        document.getElementById(
            "closeDetailsButton"
        ).addEventListener(
            "click",
            closeDetailsModal
        );


        document.getElementById(
            "closeCreateButton"
        ).addEventListener(
            "click",
            closeCreateModal
        );


        document.getElementById(
            "cancelButton"
        ).addEventListener(
            "click",
            closeCreateModal
        );


        document.getElementById(
            "vulnerabilityForm"
        ).addEventListener(
            "submit",
            handleVulnerabilitySubmit
        );


        document.getElementById(
            "searchInput"
        ).addEventListener(
            "input",
            loadVulnerabilities
        );


        document.getElementById(
            "severityFilter"
        ).addEventListener(
            "change",
            loadVulnerabilities
        );


        document.getElementById(
            "statusFilter"
        ).addEventListener(
            "change",
            loadVulnerabilities
        );


        document.getElementById(
            "assetFilter"
        ).addEventListener(
            "change",
            loadVulnerabilities
        );


        applyRoleVisibility();

        await loadAssets();

        await loadVulnerabilities();

    }
);


/* =========================================
   ASSETS
   ========================================= */

async function loadAssets() {

    try {

        assets =
            await getAssets();

        populateAssetFilters();

    } catch (error) {

        console.error(
            "Failed to load assets:",
            error.message
        );

    }

}


function populateAssetFilters() {

    const assetFilter =
        document.getElementById(
            "assetFilter"
        );


    const vulnerabilityAsset =
        document.getElementById(
            "vulnerabilityAsset"
        );


    assets.forEach(
        asset => {

            const filterOption =
                document.createElement(
                    "option"
                );

            filterOption.value =
                asset.id;

            filterOption.textContent =
                asset.asset_name;

            assetFilter.appendChild(
                filterOption
            );


            const formOption =
                document.createElement(
                    "option"
                );

            formOption.value =
                asset.id;

            formOption.textContent =
                `${asset.asset_name} (${asset.ip_address || "N/A"})`;

            vulnerabilityAsset.appendChild(
                formOption
            );

        }
    );

}


/* =========================================
   LOAD VULNERABILITIES
   ========================================= */

async function loadVulnerabilities() {

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


    const assetId =
        document.getElementById(
            "assetFilter"
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


    if (assetId) {

        params.set(
            "asset_id",
            assetId
        );

    }


    const query =
        params.toString()
            ? `?${params.toString()}`
            : "";


    const tbody =
        document.getElementById(
            "vulnerabilityTableBody"
        );


    try {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="8"
                    class="empty-state"
                >
                    Loading vulnerabilities...
                </td>
            </tr>
        `;


        vulnerabilities =
            await getVulnerabilities(
                query
            );


        renderVulnerabilities(
            vulnerabilities
        );


        updateSummary(
            vulnerabilities
        );


    } catch (error) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="8"
                    class="empty-state"
                >
                    ${escapeHtml(
                        error.message
                    )}
                </td>
            </tr>
        `;

    }

}


/* =========================================
   TABLE
   ========================================= */

function renderVulnerabilities(
    vulnerabilityList
) {

    const tbody =
        document.getElementById(
            "vulnerabilityTableBody"
        );


    document.getElementById(
        "vulnerabilityCount"
    ).textContent =
        `${vulnerabilityList.length} vulnerability(s) found`;


    if (!vulnerabilityList.length) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="8"
                    class="empty-state"
                >
                    No vulnerabilities found.
                </td>
            </tr>
        `;

        return;
    }


    tbody.innerHTML =
        vulnerabilityList
            .map(
                vulnerability =>
                    createVulnerabilityRow(
                        vulnerability
                    )
            )
            .join("");


    attachRowActions();

}


/* =========================================
   ROW
   ========================================= */

function createVulnerabilityRow(
    vulnerability
) {

    const asset =
        assets.find(
            item =>
                item.id ===
                vulnerability.asset_id
        );


    const canModify =
        hasRole(
            "ADMIN",
            "SECURITY_ANALYST"
        );


    return `
        <tr>

            <td>
                ${escapeHtml(
                    vulnerability.vulnerability_id
                )}
            </td>


            <td>
                <strong>
                    ${escapeHtml(
                        vulnerability.title
                    )}
                </strong>
            </td>


            <td>
                ${escapeHtml(
                    asset
                        ? asset.asset_name
                        : `Asset #${vulnerability.asset_id}`
                )}
            </td>


            <td>
                ${escapeHtml(
                    vulnerability.category
                )}
            </td>


            <td>

                <span
                    class="vulnerability-badge severity-${vulnerability.severity.toLowerCase()}"
                >
                    ${vulnerability.severity}
                </span>

            </td>


            <td>

                <span
                    class="vulnerability-badge severity-${vulnerability.risk_level.toLowerCase()}"
                >
                    ${vulnerability.risk_level}
                </span>

            </td>


            <td>

                <span
                    class="vulnerability-badge status-${vulnerability.status.toLowerCase().replaceAll("_", "-")}"
                >
                    ${formatLabel(
                        vulnerability.status
                    )}
                </span>

            </td>


            <td>

                <div class="action-group">

                    <button
                        class="view-button view-vulnerability-button"
                        data-id="${vulnerability.id}"
                    >
                        View
                    </button>


                    ${
                        canModify
                        ? `
                        <button
                            class="action-button status-vulnerability-button"
                            data-id="${vulnerability.id}"
                            data-status="${vulnerability.status}"
                        >
                            Status
                        </button>
                        `
                        : ""
                    }

                </div>

            </td>

        </tr>
    `;

}


/* =========================================
   ROW ACTIONS
   ========================================= */

function attachRowActions() {

    document
        .querySelectorAll(
            ".view-vulnerability-button"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    function() {

                        showVulnerability(
                            Number(
                                this.dataset.id
                            )
                        );

                    }
                );

            }
        );


    document
        .querySelectorAll(
            ".status-vulnerability-button"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    function() {

                        changeVulnerabilityStatus(
                            Number(
                                this.dataset.id
                            ),
                            this.dataset.status
                        );

                    }
                );

            }
        );

}


/* =========================================
   DETAILS
   ========================================= */

function showVulnerability(
    vulnerabilityId
) {

    const vulnerability =
        vulnerabilities.find(
            item =>
                item.id ===
                vulnerabilityId
        );


    if (!vulnerability) {

        return;

    }


    const asset =
        assets.find(
            item =>
                item.id ===
                vulnerability.asset_id
        );


    document.getElementById(
        "detailsTitle"
    ).textContent =
        vulnerability.title;


    document.getElementById(
        "detailsVulnerabilityId"
    ).textContent =
        vulnerability.vulnerability_id;


    document.getElementById(
        "detailsContent"
    ).innerHTML = `

        <div class="details-grid">

            <div class="details-item">

                <span class="details-label">
                    Asset
                </span>

                <span class="details-value">
                    ${escapeHtml(
                        asset
                            ? asset.asset_name
                            : `Asset #${vulnerability.asset_id}`
                    )}
                </span>

            </div>


            <div class="details-item">

                <span class="details-label">
                    Category
                </span>

                <span class="details-value">
                    ${escapeHtml(
                        vulnerability.category
                    )}
                </span>

            </div>


            <div class="details-item">

                <span class="details-label">
                    Severity
                </span>

                <span class="details-value">
                    ${vulnerability.severity}
                </span>

            </div>


            <div class="details-item">

                <span class="details-label">
                    Risk Level
                </span>

                <span class="details-value">
                    ${vulnerability.risk_level}
                </span>

            </div>


            <div class="details-item">

                <span class="details-label">
                    Status
                </span>

                <span class="details-value">
                    ${formatLabel(
                        vulnerability.status
                    )}
                </span>

            </div>


            <div class="details-item">

                <span class="details-label">
                    Identified By
                </span>

                <span class="details-value">
                    User #${vulnerability.identified_by}
                </span>

            </div>


            <div class="details-item">

                <span class="details-label">
                    Date Identified
                </span>

                <span class="details-value">
                    ${formatDate(
                        vulnerability.date_identified
                    )}
                </span>

            </div>


            <div class="details-item">

                <span class="details-label">
                    Assessment
                </span>

                <span class="details-value">
                    ${
                        vulnerability.assessment_id
                        ? `Assessment #${vulnerability.assessment_id}`
                        : "Not linked"
                    }
                </span>

            </div>


            <div class="details-item details-full">

                <span class="details-label">
                    Description
                </span>

                <span class="details-value">
                    ${escapeHtml(
                        vulnerability.description ||
                        "No description provided."
                    )}
                </span>

            </div>


            <div class="details-item details-full">

                <span class="details-label">
                    Evidence
                </span>

                <span class="details-value">
                    ${escapeHtml(
                        vulnerability.evidence ||
                        "No evidence provided."
                    )}
                </span>

            </div>


            <div class="details-item details-full">

                <span class="details-label">
                    Remediation
                </span>

                <span class="details-value">
                    ${escapeHtml(
                        vulnerability.remediation ||
                        "No remediation provided."
                    )}
                </span>

            </div>

        </div>

    `;


    document.getElementById(
        "detailsModal"
    ).classList.remove(
        "hidden"
    );

}


function closeDetailsModal() {

    document.getElementById(
        "detailsModal"
    ).classList.add(
        "hidden"
    );

}


/* =========================================
   STATUS
   ========================================= */

async function changeVulnerabilityStatus(
    vulnerabilityId,
    currentStatus
) {

    const nextStatus =
        prompt(
            `Current status: ${formatLabel(currentStatus)}

Enter new status:
OPEN
IN_PROGRESS
RESOLVED
CLOSED
ACCEPTED_RISK`
        );


    if (!nextStatus) {

        return;

    }


    const normalizedStatus =
        nextStatus
            .trim()
            .toUpperCase()
            .replaceAll(" ", "_");


    const validStatuses = [
        "OPEN",
        "IN_PROGRESS",
        "RESOLVED",
        "CLOSED",
        "ACCEPTED_RISK"
    ];


    if (
        !validStatuses.includes(
            normalizedStatus
        )
    ) {

        alert(
            "Invalid status."
        );

        return;

    }


    try {

        await updateVulnerabilityStatus(
            vulnerabilityId,
            normalizedStatus
        );


        await loadVulnerabilities();


    } catch (error) {

        alert(
            error.message
        );

    }

}


/* =========================================
   CREATE
   ========================================= */

function openCreateModal() {

    if (
        !hasRole(
            "ADMIN",
            "SECURITY_ANALYST"
        )
    ) {

        alert(
            "You do not have permission to create vulnerabilities."
        );

        return;

    }


    document.getElementById(
        "vulnerabilityForm"
    ).reset();


    document.getElementById(
        "formError"
    ).classList.add(
        "hidden"
    );


    document.getElementById(
        "createModal"
    ).classList.remove(
        "hidden"
    );

}


function closeCreateModal() {

    document.getElementById(
        "createModal"
    ).classList.add(
        "hidden"
    );

}


async function handleVulnerabilitySubmit(
    event
) {

    event.preventDefault();


    const formError =
        document.getElementById(
            "formError"
        );


    formError.classList.add(
        "hidden"
    );


    const payload = {

        vulnerability_id:
            document.getElementById(
                "vulnerabilityId"
            ).value.trim(),


        asset_id:
            Number(
                document.getElementById(
                    "vulnerabilityAsset"
                ).value
            ),


        title:
            document.getElementById(
                "vulnerabilityTitle"
            ).value.trim(),


        category:
            document.getElementById(
                "vulnerabilityCategory"
            ).value.trim(),


        severity:
            document.getElementById(
                "vulnerabilitySeverity"
            ).value,


        risk_level:
            document.getElementById(
                "vulnerabilityRisk"
            ).value,


        date_identified:
            new Date().toISOString(),


        description:
            document.getElementById(
                "vulnerabilityDescription"
            ).value.trim(),


        evidence:
            document.getElementById(
                "vulnerabilityEvidence"
            ).value.trim(),


        remediation:
            document.getElementById(
                "vulnerabilityRemediation"
            ).value.trim()

    };


    try {

        await createVulnerability(
            payload
        );


        closeCreateModal();


        await loadVulnerabilities();


    } catch (error) {

        formError.textContent =
            error.message;


        formError.classList.remove(
            "hidden"
        );

    }

}


/* =========================================
   HELPERS
   ========================================= */

function formatLabel(
    value
) {

    return value
        .toLowerCase()
        .replaceAll(
            "_",
            " "
        )
        .replace(
            /\b\w/g,
            character =>
                character.toUpperCase()
        );

}


function formatDate(
    value
) {

    if (!value) {

        return "-";

    }


    return new Date(
        value
    ).toLocaleString();

}


function updateSummary(
    vulnerabilityList
) {

    const counts = {

        total:
            vulnerabilityList.length,

        critical: 0,

        high: 0,

        medium: 0,

        low: 0

    };


    vulnerabilityList.forEach(
        vulnerability => {

            switch (
                vulnerability.severity
            ) {

                case "CRITICAL":
                    counts.critical++;
                    break;

                case "HIGH":
                    counts.high++;
                    break;

                case "MEDIUM":
                    counts.medium++;
                    break;

                case "LOW":
                    counts.low++;
                    break;

            }

        }
    );


    document.getElementById(
        "totalCount"
    ).textContent =
        counts.total;


    document.getElementById(
        "criticalCount"
    ).textContent =
        counts.critical;


    document.getElementById(
        "highCount"
    ).textContent =
        counts.high;


    document.getElementById(
        "mediumCount"
    ).textContent =
        counts.medium;


    document.getElementById(
        "lowCount"
    ).textContent =
        counts.low;

}


function escapeHtml(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


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


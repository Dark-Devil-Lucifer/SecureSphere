if (!requireLogin()) {
    throw new Error("Authentication required");
}


let selectedAssessmentId = null;
let allAssessments = [];


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
            renderFilteredAssessments
        );


        document.getElementById(
            "statusFilter"
        ).addEventListener(
            "change",
            renderFilteredAssessments
        );


        document.getElementById(
            "closeDetailsButton"
        ).addEventListener(
            "click",
            closeAssessmentDetails
        );
        document.getElementById(
            "closeFindingDetailsButton"
        ).addEventListener(
            "click",
            closeFindingDetails
        );
function closeFindingDetails() {

    document.getElementById(
        "findingDetailsModal"
    ).classList.add(
        "hidden"
    );

}
        document.getElementById(
            "updateStatusButton"
        ).addEventListener(
            "click",
            updateSelectedAssessmentStatus
        );


        await loadAssessments();

    }
);


async function loadAssessments() {

    const tbody =
        document.getElementById(
            "assessmentTableBody"
        );


    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="empty-state">
                Loading assessments...
            </td>
        </tr>
    `;


    try {

        allAssessments =
            await getAssessments();


        renderFilteredAssessments();


    } catch (error) {

        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    ${escapeHtml(error.message)}
                </td>
            </tr>
        `;

    }

}


function renderFilteredAssessments() {

    const search =
        document.getElementById(
            "searchInput"
        ).value
            .trim()
            .toLowerCase();


    const status =
        document.getElementById(
            "statusFilter"
        ).value;


    const filtered =
        allAssessments.filter(
            assessment => {

                const matchesSearch =
                    !search ||
                    String(
                        assessment.assessment_type || ""
                    )
                        .toLowerCase()
                        .includes(search) ||
                    String(
                        assessment.id || ""
                    )
                        .toLowerCase()
                        .includes(search) ||
                    String(
                        assessment.asset_id || ""
                    )
                        .toLowerCase()
                        .includes(search);


                const matchesStatus =
                    !status ||
                    assessment.status === status;


                return (
                    matchesSearch &&
                    matchesStatus
                );

            }
        );


    document.getElementById(
        "assessmentCount"
    ).textContent =
        `${filtered.length} assessment(s) found`;


    renderAssessments(
        filtered
    );

}


function renderAssessments(
    assessments
) {

    const tbody =
        document.getElementById(
            "assessmentTableBody"
        );


    if (!assessments.length) {

        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    No assessments found.
                </td>
            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        assessments
            .map(
                assessment =>
                    createAssessmentRow(
                        assessment
                    )
            )
            .join("");


    document
        .querySelectorAll(
            ".view-assessment-button"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    function () {

                        const id =
                            Number(
                                this.dataset.id
                            );

                        openAssessmentDetails(
                            id
                        );

                    }
                );

            }
        );

}


function createAssessmentRow(
    assessment
) {

    const statusClass =
        String(
            assessment.status || ""
        ).toLowerCase();


    const assessmentDate =
        formatDate(
            assessment.assessment_date
        );


    return `
        <tr>

            <td>
                <strong>
                    #${escapeHtml(
                        String(
                            assessment.id
                        )
                    )}
                </strong>
            </td>


            <td>
                Asset #${escapeHtml(
                    String(
                        assessment.asset_id
                    )
                )}
            </td>


            <td>
                ${escapeHtml(
                    assessment.assessment_type
                )}
            </td>


            <td>
                User #${escapeHtml(
                    String(
                        assessment.performed_by
                    )
                )}
            </td>


            <td>
                ${escapeHtml(
                    assessmentDate
                )}
            </td>


            <td>

                <span
                    class="status-badge status-${statusClass}"
                >
                    ${escapeHtml(
                        assessment.status
                    )}
                </span>

            </td>


            <td>

                <button
                    class="view-assessment-button"
                    data-id="${assessment.id}"
                >
                    View
                </button>

            </td>

        </tr>
    `;

}


async function openAssessmentDetails(
    assessmentId
) {

    try {

        const assessment =
            await getAssessment(
                assessmentId
            );


        selectedAssessmentId =
            assessment.id;


        document.getElementById(
            "detailsTitle"
        ).textContent =
            assessment.assessment_type;


        document.getElementById(
            "detailsAssessmentId"
        ).textContent =
            `Assessment #${assessment.id}`;


        document.getElementById(
            "detailsAsset"
        ).textContent =
            `Asset #${assessment.asset_id}`;


        document.getElementById(
            "detailsType"
        ).textContent =
            assessment.assessment_type;


        document.getElementById(
            "detailsPerformedBy"
        ).textContent =
            `User #${assessment.performed_by}`;


        document.getElementById(
            "detailsDate"
        ).textContent =
            formatDate(
                assessment.assessment_date
            );


        document.getElementById(
            "detailsSummary"
        ).textContent =
            assessment.summary || "-";


        document.getElementById(
            "detailsStatus"
        ).value =
            assessment.status;

        await loadAssessmentFindings(
            assessment.id
        );

        document.getElementById(
            "assessmentDetails"
        ).classList.remove(
            "hidden"
        );


        document.getElementById(
            "assessmentDetails"
        ).scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


    } catch (error) {

        alert(
            error.message
        );

    }

}

async function loadAssessmentFindings(
    assessmentId
) {

    const container =
        document.getElementById(
            "detailsFindings"
        );

    const countElement =
        document.getElementById(
            "detailsFindingsCount"
        );


    container.innerHTML = `
        <div class="findings-empty">
            Loading findings...
        </div>
    `;


    try {

        const vulnerabilities =
            await getVulnerabilities();


        const findings =
            vulnerabilities.filter(
                vulnerability =>
                    Number(
                        vulnerability.assessment_id
                    ) === Number(
                        assessmentId
                    )
            );


        countElement.textContent =
            `${findings.length} finding${
                findings.length === 1
                    ? ""
                    : "s"
            }`;


        if (!findings.length) {

            container.innerHTML = `
                <div class="findings-empty">
                    No findings linked to this assessment.
                </div>
            `;

            return;

        }


        container.innerHTML =
            findings
                .map(
                    finding =>
                        createFindingItem(
                            finding
                        )
                )
                .join("");
        container
            .querySelectorAll(
                ".finding-view-button"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        function () {

                            const vulnerabilityId =
                                Number(
                                    this.dataset.id
                                );

                            openAssessmentFinding(
                                vulnerabilityId
                            );

                        }
                    );

                }
            );

    } catch (error) {

        countElement.textContent =
            "—";


        container.innerHTML = `
            <div class="findings-error">
                Unable to load findings:
                ${escapeHtml(
                    error.message
                )}
            </div>
        `;

    }

}
async function openAssessmentFinding(
    vulnerabilityId
) {

    try {

        const vulnerability =
            await getVulnerability(
                vulnerabilityId
            );


        document.getElementById(
            "findingDetailsTitle"
        ).textContent =
            vulnerability.title;


        document.getElementById(
            "findingDetailsId"
        ).textContent =
            vulnerability.vulnerability_id;


        document.getElementById(
            "findingDetailsContent"
        ).innerHTML = `

            <div class="finding-details-grid">

                <div class="finding-detail-item">

                    <span>
                        Asset
                    </span>

                    <strong>
                        Asset #${escapeHtml(
                            String(
                                vulnerability.asset_id
                            )
                        )}
                    </strong>

                </div>


                <div class="finding-detail-item">

                    <span>
                        Category
                    </span>

                    <strong>
                        ${escapeHtml(
                            vulnerability.category
                        )}
                    </strong>

                </div>


                <div class="finding-detail-item">

                    <span>
                        Severity
                    </span>

                    <strong
                        class="severity-text ${String(
                            vulnerability.severity || ""
                        ).toLowerCase()}"
                    >
                        ${escapeHtml(
                            vulnerability.severity
                        )}
                    </strong>

                </div>


                <div class="finding-detail-item">

                    <span>
                        Risk Level
                    </span>

                    <strong>
                        ${escapeHtml(
                            vulnerability.risk_level
                        )}
                    </strong>

                </div>


                <div class="finding-detail-item">

                    <span>
                        Status
                    </span>

                    <strong>
                        ${escapeHtml(
                            vulnerability.status
                        )}
                    </strong>

                </div>


                <div class="finding-detail-item">

                    <span>
                        Assessment
                    </span>

                    <strong>
                        Assessment #${escapeHtml(
                            String(
                                vulnerability.assessment_id
                            )
                        )}
                    </strong>

                </div>


                <div class="finding-detail-full">

                    <span>
                        Description
                    </span>

                    <p>
                        ${escapeHtml(
                            vulnerability.description ||
                            "No description provided."
                        )}
                    </p>

                </div>


                <div class="finding-detail-full">

                    <span>
                        Evidence
                    </span>

                    <p>
                        ${escapeHtml(
                            vulnerability.evidence ||
                            "No evidence provided."
                        )}
                    </p>

                </div>


                <div class="finding-detail-full">

                    <span>
                        Remediation
                    </span>

                    <p>
                        ${escapeHtml(
                            vulnerability.remediation ||
                            "No remediation provided."
                        )}
                    </p>

                </div>

            </div>

        `;


        document.getElementById(
            "findingDetailsModal"
        ).classList.remove(
            "hidden"
        );


    } catch (error) {

        alert(
            error.message
        );

    }

}

function createFindingItem(
    finding
) {

    const severityClass =
        String(
            finding.severity || ""
        ).toLowerCase();


    const statusClass =
        String(
            finding.status || ""
        ).toLowerCase();


    return `
        <div class="finding-item">

            <div class="finding-main">

                <strong class="finding-title">
                    ${escapeHtml(
                        finding.vulnerability_id
                    )}
                </strong>

                <span class="finding-description">
                    ${escapeHtml(
                        finding.title
                    )}
                </span>

            </div>


            <div class="finding-meta">

                <span
                    class="severity-badge ${severityClass}"
                >
                    ${escapeHtml(
                        finding.severity
                    )}
                </span>

                <span
                    class="status-badge status-${statusClass}"
                >
                    ${escapeHtml(
                        finding.status
                    )}
                </span>

                <button
                    type="button"
                    class="finding-view-button"
                    data-id="${finding.id}"
                >
                    View
                </button>

            </div>

        </div>
    `;
}

function closeAssessmentDetails() {

    selectedAssessmentId = null;


    document.getElementById(
        "assessmentDetails"
    ).classList.add(
        "hidden"
    );

}


async function updateSelectedAssessmentStatus() {

    if (!selectedAssessmentId) {
        return;
    }


    const status =
        document.getElementById(
            "detailsStatus"
        ).value;


    try {

        await updateAssessmentStatus(
            selectedAssessmentId,
            status
        );


        await loadAssessments();


        await openAssessmentDetails(
            selectedAssessmentId
        );


    } catch (error) {

        alert(
            error.message
        );

    }

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

        return String(value);

    }


    return date.toLocaleString();

}


function escapeHtml(
    value
) {

    return String(
        value ?? ""
    )
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

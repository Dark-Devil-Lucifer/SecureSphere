if (!requireLogin()) {
    throw new Error("Authentication required");
}


let selectedRiskId = null;
let allRisks = [];


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
            renderFilteredRisks
        );


        document.getElementById(
            "riskLevelFilter"
        ).addEventListener(
            "change",
            renderFilteredRisks
        );


        document.getElementById(
            "statusFilter"
        ).addEventListener(
            "change",
            renderFilteredRisks
        );


        document.getElementById(
            "closeDetailsButton"
        ).addEventListener(
            "click",
            closeRiskDetails
        );


        document.getElementById(
            "updateStatusButton"
        ).addEventListener(
            "click",
            updateSelectedRiskStatus
        );


        await loadRisks();

    }
);


async function loadRisks() {

    const tbody =
        document.getElementById(
            "riskTableBody"
        );


    tbody.innerHTML = `
        <tr>
            <td colspan="9" class="empty-state">
                Loading risks...
            </td>
        </tr>
    `;


    try {

        allRisks =
            await getRisks();


        updateSummary(
            allRisks
        );


        renderFilteredRisks();


    } catch (error) {

        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">
                    ${escapeHtml(error.message)}
                </td>
            </tr>
        `;

    }

}


function updateSummary(
    risks
) {

    document.getElementById(
        "totalRisks"
    ).textContent =
        risks.length;


    document.getElementById(
        "criticalRisks"
    ).textContent =
        risks.filter(
            r => r.risk_level === "CRITICAL"
        ).length;


    document.getElementById(
        "highRisks"
    ).textContent =
        risks.filter(
            r => r.risk_level === "HIGH"
        ).length;


    document.getElementById(
        "mediumRisks"
    ).textContent =
        risks.filter(
            r => r.risk_level === "MEDIUM"
        ).length;


    document.getElementById(
        "lowRisks"
    ).textContent =
        risks.filter(
            r => r.risk_level === "LOW"
        ).length;

}


function renderFilteredRisks() {

    const search =
        document.getElementById(
            "searchInput"
        ).value
            .trim()
            .toLowerCase();


    const level =
        document.getElementById(
            "riskLevelFilter"
        ).value;


    const status =
        document.getElementById(
            "statusFilter"
        ).value;


    const filtered =
        allRisks.filter(
            risk => {

                const matchesSearch =
                    !search ||
                    String(
                        risk.risk_id || ""
                    )
                        .toLowerCase()
                        .includes(search) ||
                    String(
                        risk.threat || ""
                    )
                        .toLowerCase()
                        .includes(search) ||
                    String(
                        risk.vulnerability || ""
                    )
                        .toLowerCase()
                        .includes(search);


                const matchesLevel =
                    !level ||
                    risk.risk_level === level;


                const matchesStatus =
                    !status ||
                    risk.status === status;


                return (
                    matchesSearch &&
                    matchesLevel &&
                    matchesStatus
                );

            }
        );


    document.getElementById(
        "riskCount"
    ).textContent =
        `${filtered.length} risk(s) found`;


    renderRisks(
        filtered
    );

}


function renderRisks(
    risks
) {

    const tbody =
        document.getElementById(
            "riskTableBody"
        );


    if (!risks.length) {

        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">
                    No risks found.
                </td>
            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        risks
            .map(
                risk => createRiskRow(risk)
            )
            .join("");


    document
        .querySelectorAll(".view-risk-button")
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    function () {

                        const id =
                            Number(
                                this.dataset.id
                            );

                        openRiskDetails(id);

                    }
                );

            }
        );

}


function createRiskRow(
    risk
) {

    const levelClass =
        String(
            risk.risk_level || ""
        ).toLowerCase();


    const statusClass =
        String(
            risk.status || ""
        ).toLowerCase();


    const scoreClass =
        `score-${levelClass}`;


    return `
        <tr>

            <td>
                <strong>
                    ${escapeHtml(
                        risk.risk_id
                    )}
                </strong>
            </td>


            <td>
                ${escapeHtml(
                    risk.threat
                )}
            </td>


            <td>
                Asset #${escapeHtml(
                    String(
                        risk.asset_id
                    )
                )}
            </td>


            <td>
                ${escapeHtml(
                    String(
                        risk.likelihood
                    )
                )}
                / 5
            </td>


            <td>
                ${escapeHtml(
                    String(
                        risk.impact
                    )
                )}
                / 5
            </td>


            <td>

                <span
                    class="risk-score ${scoreClass}"
                >
                    ${escapeHtml(
                        String(
                            risk.risk_score
                        )
                    )}
                </span>

            </td>


            <td>

                <span
                    class="risk-badge ${levelClass}"
                >
                    ${escapeHtml(
                        risk.risk_level
                    )}
                </span>

            </td>


            <td>

                <span
                    class="status-badge status-${statusClass}"
                >
                    ${escapeHtml(
                        risk.status
                    )}
                </span>

            </td>


            <td>

                <button
                    class="view-risk-button"
                    data-id="${risk.id}"
                >
                    View
                </button>

            </td>

        </tr>
    `;

}


async function openRiskDetails(
    riskId
) {

    try {

        const risk =
            await getRisk(
                riskId
            );


        selectedRiskId =
            risk.id;


        document.getElementById(
            "detailsTitle"
        ).textContent =
            risk.threat;


        document.getElementById(
            "detailsRiskId"
        ).textContent =
            risk.risk_id;


        document.getElementById(
            "detailsRiskLevel"
        ).textContent =
            risk.risk_level;


        document.getElementById(
            "detailsRiskScore"
        ).textContent =
            risk.risk_score;


        document.getElementById(
            "detailsLikelihood"
        ).textContent =
            `${risk.likelihood} / 5`;


        document.getElementById(
            "detailsImpact"
        ).textContent =
            `${risk.impact} / 5`;


        document.getElementById(
            "detailsAsset"
        ).textContent =
            `Asset #${risk.asset_id}`;


        document.getElementById(
            "detailsVulnerability"
        ).textContent =
            risk.vulnerability_id
                ? `Vulnerability #${risk.vulnerability_id}`
                : "None";


        document.getElementById(
            "detailsThreat"
        ).textContent =
            risk.threat || "-";


        document.getElementById(
            "detailsVulnerabilityText"
        ).textContent =
            risk.vulnerability || "-";


        document.getElementById(
            "detailsMitigation"
        ).textContent =
            risk.mitigation || "-";


        document.getElementById(
            "detailsStatus"
        ).value =
            risk.status;


        document.getElementById(
            "riskDetails"
        ).classList.remove(
            "hidden"
        );


        document.getElementById(
            "riskDetails"
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


function closeRiskDetails() {

    selectedRiskId = null;

    document.getElementById(
        "riskDetails"
    ).classList.add(
        "hidden"
    );

}


async function updateSelectedRiskStatus() {

    if (!selectedRiskId) {
        return;
    }


    const status =
        document.getElementById(
            "detailsStatus"
        ).value;


    try {

        await updateRiskStatus(
            selectedRiskId,
            status
        );


        await loadRisks();


        await openRiskDetails(
            selectedRiskId
        );


    } catch (error) {

        alert(
            error.message
        );

    }

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

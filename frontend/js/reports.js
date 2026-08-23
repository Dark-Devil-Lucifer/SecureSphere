document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!requireLogin()) {
            return;
        }

        const user = getCurrentUser();

        const userName =
            document.getElementById(
                "userName"
            );

        const userRole =
            document.getElementById(
                "userRole"
            );

        const logoutButton =
            document.getElementById(
                "logoutButton"
            );

        if (user) {

            userName.textContent =
                user.full_name ||
                user.username;

            userRole.textContent =
                user.role;
        }

        logoutButton.addEventListener(
            "click",
            logout
        );

        applyRoleVisibility();

        await loadReports();

        const generateButton =
            document.getElementById(
                "generateReportButton"
            );

        if (generateButton) {

            generateButton.addEventListener(
                "click",
                generateReport
            );
        }
    }
);


async function loadReports() {

    const tableBody =
        document.getElementById(
            "reportsTableBody"
        );

    try {

        const reports =
            await getReports();

        if (!reports.length) {

            tableBody.innerHTML = `
                <tr>
                    <td
                        colspan="7"
                        class="empty-cell"
                    >
                        No reports generated yet.
                    </td>
                </tr>
            `;

            return;
        }

        tableBody.innerHTML =
            reports.map(
                report => {

                    const generatedAt =
                        report.generated_at
                            ? new Date(
                                report.generated_at
                            ).toLocaleString()
                            : "—";

                    const statusClass =
                        report.status === "GENERATED"
                            ? "status-generated"
                            : "status-failed";

                    return `
                        <tr>

                            <td>
                                <strong>
                                    ${escapeHtml(
                                        report.report_id
                                    )}
                                </strong>
                            </td>

                            <td>
                                ${escapeHtml(
                                    report.report_type
                                )}
                            </td>

                            <td>
                                <span
                                    class="status-badge ${statusClass}"
                                >
                                    ${escapeHtml(
                                        report.status
                                    )}
                                </span>
                            </td>

                            <td>
                                ${report.generated_by ?? "—"}
                            </td>

                            <td>
                                ${generatedAt}
                            </td>

                            <td>
                                ${escapeHtml(
                                    report.file_name ||
                                    "—"
                                )}
                            </td>

                            <td>

                                <button
                                    class="action-button"
                                    onclick="downloadReport(
                                        ${report.id}
                                    )"
                                >
                                    Download
                                </button>

                            </td>

                        </tr>
                    `;
                }
            ).join("");

    } catch (error) {

        tableBody.innerHTML = `
            <tr>
                <td
                    colspan="7"
                    class="empty-cell"
                >
                    Failed to load reports:
                    ${escapeHtml(error.message)}
                </td>
            </tr>
        `;
    }
}


async function generateReport() {

    const button =
        document.getElementById(
            "generateReportButton"
        );

    const message =
        document.getElementById(
            "reportMessage"
        );

    button.disabled = true;

    button.textContent =
        "Generating...";

    message.className =
        "report-message";

    message.textContent = "";

    try {

        const report =
            await generateSecurityPostureReport();

        message.className =
            "report-message success";

        message.textContent =
            `Report ${report.report_id} generated successfully.`;

        await loadReports();

    } catch (error) {

        message.className =
            "report-message error";

        message.textContent =
            `Report generation failed: ${error.message}`;

    } finally {

        button.disabled = false;

        button.textContent =
            "Generate Security Posture Report";
    }
}


async function downloadReport(
    reportId
) {

    const token =
        getToken();

    if (!token) {

        window.location.href =
            "login.html";

        return;
    }

    try {

        const response =
            await fetch(
                getReportDownloadUrl(
                    reportId
                ),
                {
                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );

        if (!response.ok) {

            let message =
                `Download failed (${response.status})`;

            try {

                const data =
                    await response.json();

                message =
                    data.detail ||
                    message;

            } catch {
                // Ignore non-JSON error response.
            }

            throw new Error(message);
        }

        const blob =
            await response.blob();

        const url =
            window.URL.createObjectURL(
                blob
            );

        const link =
            document.createElement(
                "a"
            );

        link.href = url;

        link.download =
            `SecureSphere_Report_${reportId}.pdf`;

        document.body.appendChild(
            link
        );

        link.click();

        link.remove();

        window.URL.revokeObjectURL(
            url
        );

    } catch (error) {

        const message =
            document.getElementById(
                "reportMessage"
            );

        message.className =
            "report-message error";

        message.textContent =
            error.message;
    }
}


function escapeHtml(
    value
) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

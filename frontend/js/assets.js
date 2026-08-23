if (!requireLogin()) {
    throw new Error("Authentication required");
}


let editingAssetId = null;


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
            "addAssetButton"
        ).addEventListener(
            "click",
            openAddModal
        );


        document.getElementById(
            "closeModalButton"
        ).addEventListener(
            "click",
            closeModal
        );


        document.getElementById(
            "cancelButton"
        ).addEventListener(
            "click",
            closeModal
        );


        document.getElementById(
            "assetForm"
        ).addEventListener(
            "submit",
            handleAssetSubmit
        );


        document.getElementById(
            "searchInput"
        ).addEventListener(
            "input",
            loadAssets
        );


        document.getElementById(
            "criticalityFilter"
        ).addEventListener(
            "change",
            loadAssets
        );


        document.getElementById(
            "statusFilter"
        ).addEventListener(
            "change",
            loadAssets
        );


        document.getElementById(
            "environmentFilter"
        ).addEventListener(
            "change",
            loadAssets
        );


        applyRoleVisibility();

        await loadAssets();

    }
);


async function loadAssets() {

    const search =
        document.getElementById(
            "searchInput"
        ).value.trim();


    const criticality =
        document.getElementById(
            "criticalityFilter"
        ).value;


    const assetStatus =
        document.getElementById(
            "statusFilter"
        ).value;


    const environment =
        document.getElementById(
            "environmentFilter"
        ).value;


    const params =
        new URLSearchParams();


    if (search) {
        params.set(
            "search",
            search
        );
    }


    if (criticality) {
        params.set(
            "criticality",
            criticality
        );
    }


    if (assetStatus) {
        params.set(
            "status",
            assetStatus
        );
    }


    if (environment) {
        params.set(
            "environment",
            environment
        );
    }


    const query =
        params.toString()
            ? `?${params.toString()}`
            : "";


    const tbody =
        document.getElementById(
            "assetTableBody"
        );


    try {

        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">
                    Loading assets...
                </td>
            </tr>
        `;


        const assets =
            await getAssets(query);


        renderAssets(assets);


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


function renderAssets(
    assets
) {

    const tbody =
        document.getElementById(
            "assetTableBody"
        );


    document.getElementById(
        "assetCount"
    ).textContent =
        `${assets.length} asset(s) found`;


    if (!assets.length) {

        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">
                    No assets found.
                </td>
            </tr>
        `;

        return;
    }


    tbody.innerHTML =
        assets.map(
            asset =>
                createAssetRow(asset)
        ).join("");


    attachRowActions();
}


function createAssetRow(
    asset
) {

    const criticalityClass =
        asset.criticality
            .toLowerCase();


    const statusClass =
        asset.status
            .toLowerCase();


    const canModify =
        hasRole(
            "ADMIN",
            "SECURITY_ANALYST"
        );


    const canArchive =
        hasRole("ADMIN");


    return `
        <tr>

            <td>
                ${asset.id}
            </td>


            <td class="asset-name-cell">
                ${escapeHtml(
                    asset.asset_name
                )}
            </td>


            <td>
                ${escapeHtml(
                    asset.asset_type
                )}
            </td>


            <td>
                ${
                    escapeHtml(
                        asset.ip_address ||
                        "-"
                    )
                }
                <br>
                <small>
                    ${
                        escapeHtml(
                            asset.hostname ||
                            "-"
                        )
                    }
                </small>
            </td>


            <td>
                ${
                    escapeHtml(
                        asset.owner ||
                        "-"
                    )
                }
            </td>


            <td>

                <span
                    class="badge badge-${criticalityClass}"
                >
                    ${asset.criticality}
                </span>

            </td>


            <td>
                ${formatEnvironment(
                    asset.environment
                )}
            </td>


            <td>

                <span
                    class="badge badge-${statusClass}"
                >
                    ${asset.status}
                </span>

            </td>


            <td>

                <div class="action-group">

                    ${
                        canModify
                        ? `
                        <button
                            class="action-button edit-button"
                            data-id="${asset.id}"
                        >
                            Edit
                        </button>
                        `
                        : ""
                    }


                    ${
                        canModify
                        ? `
                        <button
                            class="action-button status-button"
                            data-id="${asset.id}"
                            data-status="${asset.status}"
                        >
                            Status
                        </button>
                        `
                        : ""
                    }


                    ${
                        canArchive
                        ? `
                        <button
                            class="action-button danger archive-button"
                            data-id="${asset.id}"
                        >
                            Archive
                        </button>
                        `
                        : ""
                    }

                </div>

            </td>

        </tr>
    `;
}


function attachRowActions() {

    document
        .querySelectorAll(
            ".edit-button"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                function() {

                    openEditModal(
                        Number(
                            this.dataset.id
                        )
                    );

                }
            );

        });


    document
        .querySelectorAll(
            ".status-button"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                function() {

                    changeAssetStatus(
                        Number(
                            this.dataset.id
                        ),
                        this.dataset.status
                    );

                }
            );

        });


    document
        .querySelectorAll(
            ".archive-button"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                function() {

                    archiveSelectedAsset(
                        Number(
                            this.dataset.id
                        )
                    );

                }
            );

        });

}


function openAddModal() {

    editingAssetId = null;


    document.getElementById(
        "modalTitle"
    ).textContent =
        "Add Asset";


    document.getElementById(
        "assetForm"
    ).reset();


    document.getElementById(
        "assetId"
    ).value = "";


    document.getElementById(
        "assetModal"
    ).classList.remove(
        "hidden"
    );
}


async function openEditModal(
    assetId
) {

    try {

        const asset =
            await getAsset(
                assetId
            );


        editingAssetId =
            assetId;


        document.getElementById(
            "modalTitle"
        ).textContent =
            "Edit Asset";


        document.getElementById(
            "assetId"
        ).value =
            asset.id;


        document.getElementById(
            "assetName"
        ).value =
            asset.asset_name;


        document.getElementById(
            "assetType"
        ).value =
            asset.asset_type;


        document.getElementById(
            "operatingSystem"
        ).value =
            asset.operating_system || "";


        document.getElementById(
            "ipAddress"
        ).value =
            asset.ip_address || "";


        document.getElementById(
            "hostname"
        ).value =
            asset.hostname || "";


        document.getElementById(
            "owner"
        ).value =
            asset.owner || "";


        document.getElementById(
            "criticality"
        ).value =
            asset.criticality;


        document.getElementById(
            "environment"
        ).value =
            asset.environment;


        document.getElementById(
            "assetModal"
        ).classList.remove(
            "hidden"
        );


    } catch (error) {

        showMessage(
            error.message,
            true
        );

    }

}


function closeModal() {

    document.getElementById(
        "assetModal"
    ).classList.add(
        "hidden"
    );

}


async function handleAssetSubmit(
    event
) {

    event.preventDefault();


    const asset = {

        asset_name:
            document.getElementById(
                "assetName"
            ).value.trim(),

        asset_type:
            document.getElementById(
                "assetType"
            ).value.trim(),

        operating_system:
            document.getElementById(
                "operatingSystem"
            ).value.trim() || null,

        ip_address:
            document.getElementById(
                "ipAddress"
            ).value.trim() || null,

        hostname:
            document.getElementById(
                "hostname"
            ).value.trim() || null,

        owner:
            document.getElementById(
                "owner"
            ).value.trim() || null,

        criticality:
            document.getElementById(
                "criticality"
            ).value,

        environment:
            document.getElementById(
                "environment"
            ).value

    };


    try {

        if (editingAssetId) {

            await updateAsset(
                editingAssetId,
                asset
            );


            showMessage(
                "Asset updated successfully."
            );

        } else {

            await createAsset(
                asset
            );


            showMessage(
                "Asset created successfully."
            );

        }


        closeModal();

        await loadAssets();


    } catch (error) {

        showMessage(
            error.message,
            true
        );

    }

}


async function changeAssetStatus(
    assetId,
    currentStatus
) {

    let newStatus;


    if (currentStatus === "ACTIVE") {

        newStatus = "INACTIVE";

    } else if (
        currentStatus === "INACTIVE"
    ) {

        newStatus = "ACTIVE";

    } else {

        newStatus = "ACTIVE";

    }


    const confirmed =
        confirm(
            `Change asset status to ${newStatus}?`
        );


    if (!confirmed) {
        return;
    }


    try {

        await updateAssetStatus(
            assetId,
            newStatus
        );


        showMessage(
            "Asset status updated."
        );


        await loadAssets();


    } catch (error) {

        showMessage(
            error.message,
            true
        );

    }

}


async function archiveSelectedAsset(
    assetId
) {

    const confirmed =
        confirm(
            "Archive this asset?"
        );


    if (!confirmed) {
        return;
    }


    try {

        await archiveAsset(
            assetId
        );


        showMessage(
            "Asset archived successfully."
        );


        await loadAssets();


    } catch (error) {

        showMessage(
            error.message,
            true
        );

    }

}


function formatEnvironment(
    environment
) {

    return environment
        .replaceAll(
            "_",
            " "
        )
        .replace(
            "PRODUCTION SIMULATION",
            "Production Simulation"
        )
        .replace(
            "DEVELOPMENT",
            "Development"
        )
        .replace(
            "TEST",
            "Test"
        );

}


function showMessage(
    message,
    isError = false
) {

    const element =
        document.getElementById(
            "assetMessage"
        );


    element.textContent =
        message;


    element.style.color =
        isError
        ? "#f87171"
        : "#86efac";


    setTimeout(
        () => {
            element.textContent = "";
        },
        4000
    );

}


function escapeHtml(
    value
) {

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

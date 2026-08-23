function saveLoginSession(data) {

    localStorage.setItem(
        "access_token",
        data.access_token
    );

    localStorage.setItem(
        "user",
        JSON.stringify(data.user)
    );
}


function getCurrentUser() {

    const user = localStorage.getItem("user");

    if (!user) {
        return null;
    }

    try {
        return JSON.parse(user);
    } catch {
        return null;
    }
}


function logout() {

    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "user"
    );

    window.location.href =
        "login.html";
}


function requireLogin() {

    const token =
        localStorage.getItem(
            "access_token"
        );

    if (!token) {

        window.location.href =
            "login.html";

        return false;
    }

    return true;
}


function hasRole(
    ...allowedRoles
) {

    const user =
        getCurrentUser();

    if (!user) {
        return false;
    }

    return allowedRoles.includes(
        user.role
    );
}


function applyRoleVisibility() {

    const user =
        getCurrentUser();

    if (!user) {
        return;
    }

    document
        .querySelectorAll(
            "[data-roles]"
        )
        .forEach(element => {

            const allowedRoles =
                element.dataset.roles
                    .split(",")
                    .map(role =>
                        role.trim()
                    );

            if (
                !allowedRoles.includes(
                    user.role
                )
            ) {
                element.style.display =
                    "none";
            }
        });
}

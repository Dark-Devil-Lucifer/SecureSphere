from fastapi import APIRouter, Depends

from backend.models.user import User
from backend.utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/test",
    tags=["RBAC Test"]
)


@router.get("/authenticated")
def authenticated_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "Authentication successful",
        "username": current_user.username,
        "role": current_user.role
    }


@router.get("/admin-only")
def admin_only_endpoint(
    current_user: User = Depends(
        require_roles("ADMIN")
    )
):
    return {
        "message": "Administrator access granted",
        "username": current_user.username,
        "role": current_user.role
    }


@router.get("/analyst-only")
def analyst_only_endpoint(
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST"
        )
    )
):
    return {
        "message": "Security Analyst access granted",
        "username": current_user.username,
        "role": current_user.role
    }

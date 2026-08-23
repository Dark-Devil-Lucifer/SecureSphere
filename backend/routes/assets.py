from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.asset import Asset
from backend.models.asset_schema import (
    AssetCreate,
    AssetResponse,
    AssetStatusUpdate,
    AssetUpdate
)
from backend.models.user import User
from backend.utils.asset_validation import (
    validate_criticality,
    validate_environment,
    validate_status
)
from backend.utils.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/api/assets",
    tags=["Assets"]
)


# ============================================
# CREATE ASSET
# ADMIN + SECURITY ANALYST
# ============================================

@router.post(
    "",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED
)
def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST"
        )
    )
):

    try:

        criticality = validate_criticality(
            asset_data.criticality
        )

        environment = validate_environment(
            asset_data.environment
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    asset = Asset(
        asset_name=asset_data.asset_name,
        asset_type=asset_data.asset_type,
        operating_system=asset_data.operating_system,
        ip_address=asset_data.ip_address,
        hostname=asset_data.hostname,
        owner=asset_data.owner,
        criticality=criticality,
        environment=environment,
        status="ACTIVE"
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset


# ============================================
# LIST / SEARCH / FILTER ASSETS
# ALL AUTHENTICATED USERS
# ============================================

@router.get(
    "",
    response_model=list[AssetResponse]
)
def list_assets(
    search: Optional[str] = Query(
        default=None
    ),

    criticality: Optional[str] = Query(
        default=None
    ),

    asset_type: Optional[str] = Query(
        default=None
    ),

    environment: Optional[str] = Query(
        default=None
    ),

    asset_status: Optional[str] = Query(
        default=None,
        alias="status"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    query = db.query(Asset)

    if search:

        search_value = f"%{search}%"

        query = query.filter(
            (Asset.asset_name.ilike(search_value))
            |
            (Asset.hostname.ilike(search_value))
            |
            (Asset.ip_address.ilike(search_value))
            |
            (Asset.owner.ilike(search_value))
        )

    if criticality:

        try:
            criticality = validate_criticality(
                criticality
            )

        except ValueError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        query = query.filter(
            Asset.criticality == criticality
        )

    if asset_type:

        query = query.filter(
            Asset.asset_type.ilike(
                asset_type
            )
        )

    if environment:

        try:
            environment = validate_environment(
                environment
            )

        except ValueError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        query = query.filter(
            Asset.environment == environment
        )

    if asset_status:

        try:
            asset_status = validate_status(
                asset_status
            )

        except ValueError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        query = query.filter(
            Asset.status == asset_status
        )

    return (
        query
        .order_by(Asset.id.desc())
        .all()
    )


# ============================================
# GET SINGLE ASSET
# ALL AUTHENTICATED USERS
# ============================================

@router.get(
    "/{asset_id}",
    response_model=AssetResponse
)
def get_asset(
    asset_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id)
        .first()
    )

    if not asset:

        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    return asset


# ============================================
# UPDATE ASSET
# ADMIN + SECURITY ANALYST
# ============================================

@router.put(
    "/{asset_id}",
    response_model=AssetResponse
)
def update_asset(
    asset_id: int,

    asset_data: AssetUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST"
        )
    )
):

    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id)
        .first()
    )

    if not asset:

        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    update_data = asset_data.model_dump(
        exclude_unset=True
    )

    if "criticality" in update_data:

        try:
            update_data["criticality"] = (
                validate_criticality(
                    update_data["criticality"]
                )
            )

        except ValueError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

    if "environment" in update_data:

        try:
            update_data["environment"] = (
                validate_environment(
                    update_data["environment"]
                )
            )

        except ValueError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

    for field, value in update_data.items():

        setattr(
            asset,
            field,
            value
        )

    db.commit()
    db.refresh(asset)

    return asset


# ============================================
# UPDATE STATUS
# ADMIN + SECURITY ANALYST
# ============================================

@router.patch(
    "/{asset_id}/status",
    response_model=AssetResponse
)
def update_asset_status(
    asset_id: int,

    status_data: AssetStatusUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST"
        )
    )
):

    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id)
        .first()
    )

    if not asset:

        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    try:

        new_status = validate_status(
            status_data.status
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    asset.status = new_status

    db.commit()
    db.refresh(asset)

    return asset


# ============================================
# ARCHIVE ASSET
# ADMIN ONLY
# ============================================

@router.delete(
    "/{asset_id}"
)
def archive_asset(
    asset_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles("ADMIN")
    )
):

    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id)
        .first()
    )

    if not asset:

        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    asset.status = "RETIRED"

    db.commit()

    return {
        "message": "Asset archived successfully",
        "asset_id": asset.id,
        "status": asset.status
    }

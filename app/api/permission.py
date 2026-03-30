from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud.permission import (
    get_permission_by_id, get_permission_by_name, get_permissions,
    create_permission, update_permission, delete_permission,
    assign_permissions_to_role, get_role_permissions, remove_permission_from_role,
)
from app.crud.role import get_role_by_id
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionResponse
from app.models.user import User

router = APIRouter()


# ── Permission CRUD ────────────────────────────────────────────────────────────

@router.get("/", response_model=List[PermissionResponse])
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all permissions"""
    return get_permissions(db, skip=skip, limit=limit)


@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get permission details"""
    perm = get_permission_by_id(db, permission_id)
    if not perm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return perm


@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new permission"""
    if get_permission_by_name(db, permission.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission name already exists",
        )
    try:
        return create_permission(db, permission)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_existing_permission(
    permission_id: int,
    permission_update: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a permission"""
    perm = get_permission_by_id(db, permission_id)
    if not perm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    if permission_update.name and permission_update.name != perm.name:
        if get_permission_by_name(db, permission_update.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission name already exists",
            )
    try:
        return update_permission(db, permission_id, permission_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{permission_id}")
async def delete_existing_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a permission"""
    perm = get_permission_by_id(db, permission_id)
    if not perm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    delete_permission(db, permission_id)
    return {"message": "Permission deleted successfully"}


# ── Role ↔ Permission management ──────────────────────────────────────────────

@router.get("/roles/{role_id}/permissions", response_model=List[PermissionResponse])
async def list_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all permissions assigned to a role"""
    if not get_role_by_id(db, role_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return get_role_permissions(db, role_id)


@router.post("/roles/{role_id}/permissions")
async def assign_permissions(
    role_id: int,
    permission_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Assign (replace) the full permission set for a role"""
    if not get_role_by_id(db, role_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    try:
        assign_permissions_to_role(db, role_id, permission_ids)
        return {"message": "Permissions assigned successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/roles/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role_endpoint(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove a single permission from a role"""
    if not get_role_by_id(db, role_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if not get_permission_by_id(db, permission_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    try:
        remove_permission_from_role(db, role_id, permission_id)
        return {"message": "Permission removed from role successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

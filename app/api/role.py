from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud.role import (
    get_role_by_id, get_role_by_name, get_roles, create_role, 
    update_role, delete_role, get_role_users, count_users_by_role
)
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleWithUsers, RoleWithDetails
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[RoleWithDetails])
async def get_roles_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get role list with users and permissions"""
    roles = get_roles(db, skip=skip, limit=limit, include_inactive=include_inactive)
    return roles


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role_details(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get role details"""
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.get("/{role_id}/users", response_model=List[RoleWithUsers])
async def get_role_users_list(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user list under role"""
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    users = get_role_users(db, role_id)
    return users


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_new_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new role"""
    # Check if role name already exists
    if get_role_by_name(db, role.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )
    
    try:
        return create_role(db, role)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{role_id}", response_model=RoleResponse)
async def update_existing_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update role"""
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # If updating role name, check for conflicts with other roles
    if role_update.name and role_update.name != role.name:
        existing_role = get_role_by_name(db, role_update.name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists"
            )
    
    try:
        updated_role = update_role(db, role_id, role_update)
        return updated_role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{role_id}")
async def delete_existing_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete role"""
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Check if any users are using this role
    user_count = count_users_by_role(db, role_id)
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role, {user_count} users are still using this role"
        )
    
    try:
        delete_role(db, role_id)
        return {"message": "Role deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{role_id}/stats")
async def get_role_statistics(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get role statistics"""
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    user_count = count_users_by_role(db, role_id)
    
    return {
        "role": role,
        "user_count": user_count,
        "is_deletable": user_count == 0
    }
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud.user import (
    get_user_by_id, get_user_by_username, get_user_by_email, get_users, count_users,
    create_user, update_user, delete_user, assign_roles_to_user, remove_roles_from_user
)
from app.crud.role import get_role_by_id
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserWithRole, PaginatedResponse
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[UserWithRole])
async def get_users_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[bool] = Query(None),
    role_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user list. status=null returns all, status=true/false filters by is_active."""
    total = count_users(db, status=status, role_id=role_id)
    users = get_users(db, skip=skip, limit=limit, status=status, role_id=role_id)
    return PaginatedResponse(total=total, skip=skip, limit=limit, items=users)


@router.get("/stats/overview")
async def get_users_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user statistics overview"""
    total_users = count_users(db)
    active_users = count_users(db, status=True)
    inactive_users = count_users(db, status=False)
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users
    }


@router.get("/{user_id}", response_model=UserWithRole)
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user details"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new user"""
    # Check if username already exists
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # If role is specified, check if role exists
    if user.role_ids:
        for rid in user.role_ids:
            role = get_role_by_id(db, rid)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role {rid} not found"
                )
    
    try:
        return create_user(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_existing_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # If updating username, check for conflicts with other users
    if user_update.username and user_update.username != user.username:
        existing_user = get_user_by_username(db, user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
    
    # If updating email, check for conflicts with other users
    if user_update.email and user_update.email != user.email:
        existing_user = get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    # If updating role, check if roles exist
    if user_update.role_ids is not None:
        for rid in user_update.role_ids:
            role = get_role_by_id(db, rid)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role {rid} not found"
                )
    
    try:
        updated_user = update_user(db, user_id, user_update)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}")
async def delete_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete user"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    delete_user(db, user_id)
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/assign-role/{role_id}", response_model=UserResponse)
async def assign_role_to_user_endpoint(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a role to user"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    current_ids = [r.id for r in user.roles]
    if role_id not in current_ids:
        current_ids.append(role_id)
    
    try:
        updated_user = assign_roles_to_user(db, user_id, current_ids)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{user_id}/remove-role", response_model=UserResponse)
async def remove_user_role(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove all roles from user"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    updated_user = remove_roles_from_user(db, user_id)
    return updated_user


@router.post("/{user_id}/toggle-status", response_model=UserResponse)
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Toggle user status (active/inactive)"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent disabling yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account"
        )
    
    user_update = UserUpdate(is_active=not user.is_active)
    updated_user = update_user(db, user_id, user_update)
    return updated_user
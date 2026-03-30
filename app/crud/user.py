from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def count_users(db: Session, status: Optional[bool] = None, role_id: Optional[int] = None) -> int:
    """Count users with optional filters"""
    query = db.query(User)
    if status is not None:
        query = query.filter(User.is_active == status)
    if role_id is not None:
        query = query.filter(User.roles.any(Role.id == role_id))
    return query.count()


def get_users(db: Session, skip: int = 0, limit: int = 100, status: Optional[bool] = None,
              role_id: Optional[int] = None) -> List[User]:
    """Get user list"""
    query = db.query(User)
    if status is not None:
        query = query.filter(User.is_active == status)
    if role_id is not None:
        query = query.filter(User.roles.any(Role.id == role_id))
    return query.offset(skip).limit(limit).all()


def _resolve_roles(db: Session, role_ids: List[int]) -> List[Role]:
    """Fetch Role objects for given IDs, raise if any not found"""
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    if len(roles) != len(role_ids):
        found = {r.id for r in roles}
        missing = set(role_ids) - found
        raise ValueError(f"Roles not found: {missing}")
    return roles


def create_user(db: Session, user: UserCreate) -> User:
    """Create new user"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
    )
    if user.role_ids:
        db_user.roles = _resolve_roles(db, user.role_ids)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("Username or email already exists")


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    # Handle password hashing
    if 'password' in update_data and update_data['password']:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))

    # Handle roles separately
    if 'role_ids' in update_data:
        role_ids = update_data.pop('role_ids')
        db_user.roles = _resolve_roles(db, role_ids) if role_ids else []

    for field, value in update_data.items():
        setattr(db_user, field, value)

    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("Username or email already exists")


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_refresh_token(db: Session, user: User, refresh_token: str) -> User:
    """Update user's refresh token"""
    user.refresh_token = refresh_token
    db.commit()
    db.refresh(user)
    return user


def get_user_by_refresh_token(db: Session, refresh_token: str) -> Optional[User]:
    """Get user by refresh token"""
    return db.query(User).filter(User.refresh_token == refresh_token).first()


def clear_user_refresh_token(db: Session, user: User) -> None:
    """Clear user's refresh token"""
    user.refresh_token = None
    db.commit()


def assign_roles_to_user(db: Session, user_id: int, role_ids: List[int]) -> Optional[User]:
    """Assign roles to user (replaces existing roles)"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    db_user.roles = _resolve_roles(db, role_ids)
    db.commit()
    db.refresh(db_user)
    return db_user


def remove_roles_from_user(db: Session, user_id: int) -> Optional[User]:
    """Remove all roles from user"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    db_user.roles = []
    db.commit()
    db.refresh(db_user)
    return db_user
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100, include_inactive: bool = False, 
              role_id: Optional[int] = None) -> List[User]:
    """获取用户列表"""
    query = db.query(User).join(Role, User.role_id == Role.id, isouter=True)
    
    if not include_inactive:
        query = query.filter(User.is_active == True)
    
    if role_id is not None:
        query = query.filter(User.role_id == role_id)
    
    return query.offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """创建新用户"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
        role_id=user.role_id
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("用户名或邮箱已存在")


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """更新用户"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # 如果更新密码，需要加密
    if 'password' in update_data and update_data['password']:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("用户名或邮箱已存在")


def delete_user(db: Session, user_id: int) -> bool:
    """删除用户"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_refresh_token(db: Session, user: User, refresh_token: str) -> User:
    """更新用户的刷新令牌"""
    user.refresh_token = refresh_token
    db.commit()
    db.refresh(user)
    return user


def get_user_by_refresh_token(db: Session, refresh_token: str) -> Optional[User]:
    """根据刷新令牌获取用户"""
    return db.query(User).filter(User.refresh_token == refresh_token).first()


def clear_user_refresh_token(db: Session, user: User) -> None:
    """清除用户的刷新令牌"""
    user.refresh_token = None
    db.commit()


def assign_role_to_user(db: Session, user_id: int, role_id: int) -> Optional[User]:
    """为用户分配角色"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # 检查角色是否存在
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise ValueError("角色不存在")
    
    db_user.role_id = role_id
    db.commit()
    db.refresh(db_user)
    return db_user


def remove_role_from_user(db: Session, user_id: int) -> Optional[User]:
    """移除用户的角色"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.role_id = None
    db.commit()
    db.refresh(db_user)
    return db_user
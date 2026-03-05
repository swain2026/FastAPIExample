#!/usr/bin/env python3
"""创建管理员用户的简单脚本"""
from app.db.database import SessionLocal, create_tables
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.orm import Session


def create_admin():
    """创建管理员用户"""
    create_tables()
    
    db = SessionLocal()
    try:
        # 检查并创建角色
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="管理员")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("✅ 创建 admin 角色")
        
        user_role = db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            user_role = Role(name="user", description="普通用户")
            db.add(user_role)
            db.commit()
            print("✅ 创建 user 角色")
        
        # 创建管理员用户
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                role_id=admin_role.id
            )
            db.add(admin_user)
            db.commit()
            print("✅ 创建管理员用户")
        else:
            print("ℹ️ 管理员用户已存在")
        
        print("\n🎉 初始化完成！")
        print("管理员账号信息:")
        print("  用户名: admin")
        print("  密码: admin123")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
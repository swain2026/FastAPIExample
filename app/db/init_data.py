"""初始化数据库数据"""
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, create_tables
from app.models.role import Role
from app.models.user import User
from app.crud.user import create_user
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


def init_roles(db: Session):
    """初始化默认角色"""
    default_roles = [
        {"name": "admin", "description": "管理员，拥有所有权限"},
        {"name": "user", "description": "普通用户，拥有基本权限"},
        {"name": "guest", "description": "访客，只有查看权限"},
    ]
    
    for role_data in default_roles:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
    
    db.commit()
    print("✅ 默认角色初始化完成")


def init_admin_user(db: Session):
    """初始化管理员用户"""
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        print("❌ 管理员角色不存在，无法创建管理员用户")
        return
    
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if not existing_admin:
        admin_user_data = UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin123",  # 生产环境应该使用更强的密码
            is_active=True,
            role_id=admin_role.id
        )
        
        admin_user = create_user(db, admin_user_data)
        print(f"✅ 管理员用户创建完成: {admin_user.username}")
    else:
        print("ℹ️ 管理员用户已存在")


def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    # 创建表
    create_tables()
    print("✅ 数据库表创建完成")
    
    db = SessionLocal()
    try:
        # 初始化角色
        init_roles(db)
        
        # 初始化管理员用户
        init_admin_user(db)
        
        print("🎉 数据库初始化完成！")
        print("📝 默认管理员账号:")
        print("   用户名: admin")
        print("   密码: admin123")
        print("   邮箱: admin@example.com")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
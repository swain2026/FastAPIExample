"""Initialize database data"""
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, create_tables
from app.models.role import Role
from app.models.user import User
from app.crud.user import create_user
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


def init_roles(db: Session):
    """Initialize default roles"""
    default_roles = [
        {"name": "admin", "description": "Administrator with all permissions"},
        {"name": "user", "description": "Regular user with basic permissions"},
        {"name": "guest", "description": "Guest with view-only permissions"},
    ]
    
    for role_data in default_roles:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
    
    db.commit()
    print("✅ Default roles initialized")


def init_admin_user(db: Session):
    """Initialize admin user"""
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        print("❌ Admin role does not exist, cannot create admin user")
        return
    
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if not existing_admin:
        admin_user_data = UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin123",  # Use a stronger password in production
            is_active=True,
            role_id=admin_role.id
        )
        
        admin_user = create_user(db, admin_user_data)
        print(f"✅ Admin user created: {admin_user.username}")
    else:
        print("ℹ️ Admin user already exists")


def init_database():
    """Initialize database"""
    print("🚀 Starting database initialization...")
    
    # Create tables
    create_tables()
    print("✅ Database tables created")
    
    db = SessionLocal()
    try:
        # Initialize roles
        init_roles(db)
        
        # Initialize admin user
        init_admin_user(db)
        
        print("🎉 Database initialization complete!")
        print("📝 Default admin account:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@example.com")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
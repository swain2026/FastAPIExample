#!/usr/bin/env python3
"""Simple script to create admin user"""
from app.db.database import SessionLocal, create_tables
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.orm import Session


def create_admin():
    """Create admin user"""
    create_tables()
    
    db = SessionLocal()
    try:
        # Check and create roles
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("✅ Created admin role")
        
        user_role = db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            user_role = Role(name="user", description="Regular user")
            db.add(user_role)
            db.commit()
            print("✅ Created user role")
        
        # Create admin user
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
            print("✅ Created admin user")
        else:
            print("ℹ️ Admin user already exists")
        
        print("\n🎉 Initialization complete!")
        print("Admin account info:")
        print("  Username: admin")
        print("  Password: admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
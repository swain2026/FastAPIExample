"""Initialize database data"""
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, create_tables
from app.models.role import Role
from app.models.user import User
from app.models.permission import Permission, PermissionType
from app.crud.user import create_user
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


def init_permissions(db: Session):
    """Initialize default permissions"""
    default_permissions = [
        # User management
        {"name": "user.list",   "display_name": "List Users",       "type": PermissionType.api, "path": "/api/users",            "method": "GET",    "parent_id": 0, "sort_order": 1},
        {"name": "user.create", "display_name": "Create User",      "type": PermissionType.api, "path": "/api/users",            "method": "POST",   "parent_id": 0, "sort_order": 2},
        {"name": "user.update", "display_name": "Update User",      "type": PermissionType.api, "path": "/api/users/{id}",       "method": "PUT",    "parent_id": 0, "sort_order": 3},
        {"name": "user.delete", "display_name": "Delete User",      "type": PermissionType.api, "path": "/api/users/{id}",       "method": "DELETE", "parent_id": 0, "sort_order": 4},
        # Role management
        {"name": "role.list",   "display_name": "List Roles",       "type": PermissionType.api, "path": "/api/roles",            "method": "GET",    "parent_id": 0, "sort_order": 5},
        {"name": "role.create", "display_name": "Create Role",      "type": PermissionType.api, "path": "/api/roles",            "method": "POST",   "parent_id": 0, "sort_order": 6},
        {"name": "role.update", "display_name": "Update Role",      "type": PermissionType.api, "path": "/api/roles/{id}",       "method": "PUT",    "parent_id": 0, "sort_order": 7},
        {"name": "role.delete", "display_name": "Delete Role",      "type": PermissionType.api, "path": "/api/roles/{id}",       "method": "DELETE", "parent_id": 0, "sort_order": 8},
        # Permission management
        {"name": "perm.list",   "display_name": "List Permissions",  "type": PermissionType.api, "path": "/api/permissions",      "method": "GET",    "parent_id": 0, "sort_order": 9},
        {"name": "perm.create", "display_name": "Create Permission", "type": PermissionType.api, "path": "/api/permissions",      "method": "POST",   "parent_id": 0, "sort_order": 10},
        {"name": "perm.update", "display_name": "Update Permission", "type": PermissionType.api, "path": "/api/permissions/{id}", "method": "PUT",    "parent_id": 0, "sort_order": 11},
        {"name": "perm.delete", "display_name": "Delete Permission", "type": PermissionType.api, "path": "/api/permissions/{id}", "method": "DELETE", "parent_id": 0, "sort_order": 12},
    ]

    for perm_data in default_permissions:
        if not db.query(Permission).filter(Permission.name == perm_data["name"]).first():
            db.add(Permission(**perm_data))

    db.commit()
    print("✅ Default permissions initialized")


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
        
        # Initialize permissions
        init_permissions(db)
        
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
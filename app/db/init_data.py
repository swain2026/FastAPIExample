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

    def get_or_create(perm_data: dict) -> Permission:
        perm = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not perm:
            perm = Permission(**perm_data)
            db.add(perm)
            db.flush()  # populate perm.id without full commit
        return perm

    # ── Menu: Dashboard ──────────────────────────────────────────────────────
    menu_dashboard = get_or_create({
        "name": "menu.dashboard", "display_name": "Dashboard",
        "type": PermissionType.menu, "path": "/dashboard",
        "method": None, "parent_id": 0, "sort_order": 1,
    })

    # ── Menu: Auth (parent) ───────────────────────────────────────────────────
    menu_auth = get_or_create({
        "name": "menu.auth", "display_name": "Auth",
        "type": PermissionType.menu, "path": "",
        "method": None, "parent_id": 0, "sort_order": 2,
    })

    # ── Menu: Auth > Users ────────────────────────────────────────────────────
    menu_users = get_or_create({
        "name": "menu.auth.users", "display_name": "Users",
        "type": PermissionType.menu, "path": "/auth/users",
        "method": None, "parent_id": menu_auth.id, "sort_order": 1,
    })

    # ── Menu: Auth > Roles ────────────────────────────────────────────────────
    menu_roles = get_or_create({
        "name": "menu.auth.roles", "display_name": "Roles",
        "type": PermissionType.menu, "path": "/auth/roles",
        "method": None, "parent_id": menu_auth.id, "sort_order": 2,
    })

    # ── Menu: Auth > Permissions ──────────────────────────────────────────────
    menu_perms = get_or_create({
        "name": "menu.auth.permissions", "display_name": "Permissions",
        "type": PermissionType.menu, "path": "/auth/permissions",
        "method": None, "parent_id": menu_auth.id, "sort_order": 3,
    })

    # ── API: User management (parent → menu.auth.users) ───────────────────────
    for perm_data in [
        {"name": "user.list",   "display_name": "List Users",   "method": "GET",    "path": "/api/users",        "sort_order": 1},
        {"name": "user.create", "display_name": "Create User",  "method": "POST",   "path": "/api/users",        "sort_order": 2},
        {"name": "user.update", "display_name": "Update User",  "method": "PUT",    "path": "/api/users/{id}",   "sort_order": 3},
        {"name": "user.delete", "display_name": "Delete User",  "method": "DELETE", "path": "/api/users/{id}",   "sort_order": 4},
    ]:
        get_or_create({**perm_data, "type": PermissionType.api, "parent_id": menu_users.id})

    # ── API: Role management (parent → menu.auth.roles) ───────────────────────
    for perm_data in [
        {"name": "role.list",   "display_name": "List Roles",   "method": "GET",    "path": "/api/roles",        "sort_order": 1},
        {"name": "role.create", "display_name": "Create Role",  "method": "POST",   "path": "/api/roles",        "sort_order": 2},
        {"name": "role.update", "display_name": "Update Role",  "method": "PUT",    "path": "/api/roles/{id}",   "sort_order": 3},
        {"name": "role.delete", "display_name": "Delete Role",  "method": "DELETE", "path": "/api/roles/{id}",   "sort_order": 4},
    ]:
        get_or_create({**perm_data, "type": PermissionType.api, "parent_id": menu_roles.id})

    # ── API: Permission management (parent → menu.auth.permissions) ───────────
    for perm_data in [
        {"name": "perm.list",   "display_name": "List Permissions",   "method": "GET",    "path": "/api/permissions",        "sort_order": 1},
        {"name": "perm.create", "display_name": "Create Permission",  "method": "POST",   "path": "/api/permissions",        "sort_order": 2},
        {"name": "perm.update", "display_name": "Update Permission",  "method": "PUT",    "path": "/api/permissions/{id}",   "sort_order": 3},
        {"name": "perm.delete", "display_name": "Delete Permission",  "method": "DELETE", "path": "/api/permissions/{id}",   "sort_order": 4},
    ]:
        get_or_create({**perm_data, "type": PermissionType.api, "parent_id": menu_perms.id})

    # ── Menu: Logs ────────────────────────────────────────────────────────────
    menu_logs = get_or_create({
        "name": "menu.logs", "display_name": "Logs",
        "type": PermissionType.menu, "path": "/auth/logs",
        "method": None, "parent_id": menu_auth.id, "sort_order": 3,
    })

    # ── API: Log management (parent → menu.logs) ──────────────────────────────
    for perm_data in [
        {"name": "log.list",   "display_name": "List Logs",   "method": "GET",    "path": "/api/logs",       "sort_order": 1}
    ]:
        get_or_create({**perm_data, "type": PermissionType.api, "parent_id": menu_logs.id})

    db.commit()
    print("✅ Default permissions initialized")


def init_roles(db: Session):
    """Initialize default roles"""
    default_roles = [
        {"name": "admin", "description": "Administrator with all permissions"},
        {"name": "user", "description": "Regular user with basic permissions"}
    ]

    for role_data in default_roles:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)

    db.commit()

    # Assign all permissions to the admin role
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if admin_role is not None:
        all_permissions = db.query(Permission).all()
        admin_role.permissions = all_permissions
        db.commit()
        print(f"✅ Admin role assigned {len(all_permissions)} permissions")

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
            role_ids=[admin_role.id]
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
        # Initialize permissions
        init_permissions(db)

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
import re
from fnmatch import fnmatch

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.security import verify_token

# Routes that bypass both auth and permission checks
_PUBLIC_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/health", "/api/auth/")

# Routes that only need a valid token (no permission check needed)
_TOKEN_ONLY_PATHS = ()


def _path_matches(request_path: str, permission_path: str) -> bool:
    """
    Match a request path against a permission path pattern.
    Converts FastAPI-style path params like {id} into wildcards.
    e.g. /api/users/{id}  →  /api/users/*
    """
    pattern = re.sub(r"\{[^}]+\}", "*", permission_path)
    return fnmatch(request_path, pattern)


class ApiAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Skips /auth/* routes entirely.
    2. Requires a valid Bearer token for all other routes.
    3. Checks the user's role permissions (api type) against the request
       path + method, unless the user has the admin role.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 1. Public routes — no auth needed
        if any(path.startswith(p) for p in _PUBLIC_PREFIXES):
            return await call_next(request)

        # 2. Validate Bearer token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = verify_token(auth_header[7:])
        except Exception:
            return JSONResponse(
                status_code=401,
                content={"detail": "Could not validate credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. Token-only paths (docs, health, etc.) — skip permission check
        if any(path == p or path.startswith(p + "/") for p in _TOKEN_ONLY_PATHS):
            return await call_next(request)

        # 4. Load user + permissions from DB
        username = payload.get("sub")
        from app.db.database import SessionLocal
        from app.crud.user import get_user_by_username
        from app.models.permission import PermissionType

        db = SessionLocal()
        try:
            user = get_user_by_username(db, username)
            if not user or not user.is_active:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "User not found or inactive"},
                )

            # 5. Collect all api-type permissions across all roles
            seen = set()
            api_permissions = []
            for role in user.roles:
                for perm in role.permissions:
                    if perm.id not in seen and perm.type == PermissionType.api:
                        seen.add(perm.id)
                        api_permissions.append(perm)
            
            # print([{"id": p.id, "name": p.name, "path": p.path, "method": p.method} for p in api_permissions])

            # 6. Check if any permission matches this request
            method = request.method.upper()
            path = path.rstrip("/")

            # print(path)
            # print(method)

            allowed = any(
                perm.path
                and perm.method
                and perm.method.upper() == method
                and _path_matches(path, perm.path)
                for perm in api_permissions
            )

            if not allowed:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Permission denied"},
                )

        finally:
            db.close()

        return await call_next(request)

import json
import time
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.security import verify_token

_SENSITIVE_FIELDS = {"password", "confirm_password", "old_password", "new_password", "secret"}


def _sanitize(data: dict) -> dict:
    """Recursively remove sensitive keys from a dict."""
    return {
        k: "***" if k.lower() in _SENSITIVE_FIELDS else (
            _sanitize(v) if isinstance(v, dict) else v
        )
        for k, v in data.items()
    }


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _extract_username(request: Request) -> Optional[str]:
    """Best-effort username extraction from Bearer token."""
    try:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            payload = verify_token(auth[7:])
            return payload.get("sub")
    except Exception:
        pass
    return None


class ApiLogMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every non-GET API request to the database."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.method.upper() == "GET":
            return await call_next(request)

        start = time.time()
        params: dict = {}

        if request.query_params:
            params["query"] = _sanitize(dict(request.query_params))

        try:
            body_bytes = await request.body()
            if body_bytes:
                body = json.loads(body_bytes)
                if isinstance(body, dict):
                    params["body"] = _sanitize(body)
                else:
                    params["body"] = body
        except Exception:
            pass

        response: Response = await call_next(request)
        elapsed_ms = int((time.time() - start) * 1000)

        from app.db.database import SessionLocal
        from app.crud.log import create_log
        db = SessionLocal()
        try:
            create_log(
                db,
                method=request.method.upper(),
                path=str(request.url.path),
                status_code=response.status_code,
                user_ip=_get_client_ip(request),
                username=_extract_username(request),
                request_params=json.dumps(params, ensure_ascii=False) if params else None,
                process_time_ms=elapsed_ms,
            )
        except Exception:
            pass
        finally:
            db.close()

        return response

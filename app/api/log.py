from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud.log import delete_log, get_log_by_id, get_logs
from app.models.user import User
from app.schemas.log import ApiLogResponse

router = APIRouter()

# ── API routes ────────────────────────────────────────────────────────────────

@router.get("/", response_model=dict)
async def list_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    path: Optional[str] = Query(None, description="Filter by path (partial match)"),
    username: Optional[str] = Query(None, description="Filter by username"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List API logs with optional filters (paginated)."""
    total, items = get_logs(
        db, skip=skip, limit=limit,
        method=method, path=path,
        username=username, status_code=status_code,
    )
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [ApiLogResponse.model_validate(i) for i in items],
    }
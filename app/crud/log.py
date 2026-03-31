from typing import Optional
from sqlalchemy.orm import Session
from app.models.log import ApiLog


def create_log(db: Session, **kwargs) -> ApiLog:
    log = ApiLog(**kwargs)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    method: Optional[str] = None,
    path: Optional[str] = None,
    username: Optional[str] = None,
    status_code: Optional[int] = None,
):
    query = db.query(ApiLog)
    if method:
        query = query.filter(ApiLog.method == method.upper())
    if path:
        query = query.filter(ApiLog.path.contains(path))
    if username:
        query = query.filter(ApiLog.username == username)
    if status_code:
        query = query.filter(ApiLog.status_code == status_code)
    total = query.count()
    items = query.order_by(ApiLog.created_at.desc()).offset(skip).limit(limit).all()
    return total, items


def get_log_by_id(db: Session, log_id: int) -> Optional[ApiLog]:
    return db.query(ApiLog).filter(ApiLog.id == log_id).first()


def delete_log(db: Session, log_id: int) -> bool:
    log = get_log_by_id(db, log_id)
    if not log:
        return False
    db.delete(log)
    db.commit()
    return True

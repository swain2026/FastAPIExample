from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base
from datetime import datetime


class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    status_code = Column(Integer, nullable=True)
    user_ip = Column(String(50), nullable=True)
    username = Column(String(100), nullable=True)   # from JWT if available
    request_params = Column(Text, nullable=True)    # sanitized body/query params
    process_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ApiLogResponse(BaseModel):
    id: int
    method: str
    path: str
    status_code: Optional[int]
    user_ip: Optional[str]
    username: Optional[str]
    request_params: Optional[str]
    process_time_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

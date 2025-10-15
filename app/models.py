from __future__ import annotations
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Plan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    goal: str
    due_days: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    data: str  # JSON string of the plan

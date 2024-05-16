from datetime import datetime

from sqlmodel import SQLModel, Field
from typing import Optional


class Diseases(SQLModel, table=True):
    __tablename__ = 'diseases'
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str
    description: str
    healing_steps: str
    created_at: datetime = Field(nullable=False, default=datetime.now())
    updated_at: datetime = Field(nullable=False, default=datetime.now())

class CreateDisease(SQLModel):
    name: str
    description: str
    healing_steps: str


class DiseasesOut(SQLModel):
    data: list[Diseases]
    count: int
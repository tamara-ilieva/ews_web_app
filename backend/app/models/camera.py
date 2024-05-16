from datetime import date
from typing import Optional

from sqlmodel import SQLModel, Field


class Camera(SQLModel, table=True):
    __tablename__ = 'cameras'
    id: int = Field(primary_key=True, index=True)
    type: str
    camera_name: str

from datetime import date
from typing import Optional

from sqlmodel import SQLModel, Field


class ApplicationSetting(SQLModel, table=True):
    __tablename__ = 'application_settings'
    id: int = Field(primary_key=True, index=True)
    num_pictures_drone: int = Field(default=20)

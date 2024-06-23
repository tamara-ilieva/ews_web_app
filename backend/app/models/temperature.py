from datetime import datetime

from sqlmodel import SQLModel, Field


class Temperature(SQLModel, table=True):
    __tablename__ = 'temperatures'
    id: int = Field(primary_key=True, index=True)
    average: float
    min: float
    max: float
    image_id: int = Field(foreign_key="dynamic_images.id")
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)


class TemperatureData(SQLModel):
    max_temperature: float
    min_temperature: float
    average_temperature: float
    image_id: int

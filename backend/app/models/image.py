from datetime import datetime

from sqlmodel import SQLModel, Field


class Image(SQLModel, table=True):
    __tablename__ = 'images'
    id: int = Field(primary_key=True, index=True)
    predicted_disease: int = Field(foreign_key="diseases.id", nullable=True)
    is_sick: bool = Field(nullable=True)
    predicted_disease_human_input: int = Field(foreign_key="diseases.id", nullable=True)
    is_sick_human_input: bool = Field(nullable=True)
    file_url: str
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)

class ImageOut(SQLModel):
    id: int
    predicted_disease: int
    is_sick: bool
    predicted_disease_human_input: int
    is_sick_human_input: bool
    file_url: str
    created_at: datetime
    updated_at: datetime

class ImagesOut(SQLModel):
    data: list[ImageOut]
    count: int

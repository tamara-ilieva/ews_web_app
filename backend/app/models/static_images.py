from datetime import datetime

from sqlmodel import SQLModel, Field


class StaticImages(SQLModel, table=True):
    __tablename__ = 'static_images'
    id: int = Field(primary_key=True, index=True)
    predicted_disease: int = Field(foreign_key="diseases.id", nullable=True)
    is_sick: bool = Field(nullable=True)
    predicted_disease_human_input: int = Field(foreign_key="diseases.id", nullable=True)
    is_sick_human_input: bool = Field(nullable=True)
    file_url: str
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)
class StaticImageOut(SQLModel):
    id: int
    predicted_disease: int
    is_sick: bool
    predicted_disease_human_input: str
    is_sick_human_input: bool
    file_url: str
    created_at: datetime
    updated_at: datetime

class StaticImagesOut(SQLModel):
    data: list[StaticImageOut]
    count: int

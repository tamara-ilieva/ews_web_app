from datetime import datetime

from sqlmodel import SQLModel, Field


class StaticImages(SQLModel, table=True):
    __tablename__ = 'static_images'
    id: int = Field(primary_key=True, index=True)
    disease: int = Field(foreign_key="diseases.id", nullable=True)
    file_url: str
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)
    is_sick: bool = False
    is_sick_confirmed: bool = False
    predicted_disease: str
    confirmed_disease: str
class ImageOut(SQLModel):
    id: int
    disease: str
    file_url: str
    created_at: datetime
    updated_at: datetime
    is_sick: bool
    is_sick_confirmed: bool = False
    predicted_disease: str
    confirmed_disease: str

class ImagesOut(SQLModel):
    data: list[ImageOut]
    count: int

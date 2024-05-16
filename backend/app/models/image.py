from datetime import datetime

from sqlmodel import SQLModel, Field


class Image(SQLModel, table=True):
    __tablename__ = 'images'
    id: int = Field(primary_key=True, index=True)
    disease: int = Field(foreign_key="diseases.id", nullable=True)
    file_url: str
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)
    # is_sick: bool = False
    # confirmed: bool = False

class ImageOut(SQLModel):
    id: int
    disease: str
    file_url: str
    created_at: datetime
    updated_at: datetime

class ImagesOut(SQLModel):
    data: list[ImageOut]
    count: int

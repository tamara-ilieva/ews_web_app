from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from app.models.application_settings import ApplicationSetting


from app.api.deps import get_db, SessionDep

router = APIRouter()


class UpdateNumber(BaseModel):
    number: int

@router.get("/num-pictures")
def get_number_of_drone_pictures(session: Session = Depends(get_db)):
    settings = session.exec(select(ApplicationSetting)).first()
    if not settings:
        settings = ApplicationSetting(num_pictures_drone=20)
        session.add(settings)
        session.commit()
    return {"number": settings.num_pictures_drone}


@router.put("/num-pictures")
def update_number_of_drone_pictures(update: UpdateNumber, session: Session = Depends(get_db)):
    settings = session.exec(select(ApplicationSetting)).first()
    settings.num_pictures_drone = update.number
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return settings
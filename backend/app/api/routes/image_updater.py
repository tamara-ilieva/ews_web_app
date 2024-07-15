import datetime
import random
from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from apscheduler.schedulers.background import BackgroundScheduler
from app.api.src.main import predict
from app.core.disease_prediction import is_plant_sick
from app.api.deps import get_db, SessionDep
from app.models.static_images import StaticImages
from app.models.uploaded_images import UploadedImages
from app.models.dynamic_images import DynamicImage

from app.models.diseases import Diseases

from app.models.temperature import Temperature

router = APIRouter()


#
# def extract_temperatures(image_url):
#     """
#     Extracts temperature readings from a thermal image.
#
#     :param image_url: URL of the thermal image.
#     :return: List of temperatures extracted from the image.
#     """
#     image = Image.open(image_url)
#     text = pytesseract.image_to_string(image)
#     temperatures = []
#     for word in text.split():
#         try:
#             temperatures.append(float(word))
#         except ValueError:
#             continue
#     return temperatures
def get_or_create_disease(session: Session, disease_name: str, remedy: str = '/'):
    disease = session.exec(select(Diseases).where(Diseases.name == disease_name)).first()
    if not disease:
        disease = Diseases(name=disease_name, description="", healing_steps=remedy)
        session.add(disease)
        session.commit()
        session.refresh(disease)
    return disease.id


def update_static_images(session: Session):
    statement = select(StaticImages).where(StaticImages.predicted_disease == None)
    images = session.exec(statement).all()

    for image in images:
        print(image)
        result, remedy = predict(image.file_url)
        if result:
            disease_id = get_or_create_disease(session, result)
            image.predicted_disease = disease_id
            session.add(image)

    session.commit()


def get_temperatures(session: Session, image_id: int) -> Optional[Temperature]:
    statement = select(Temperature).where(Temperature.image_id == image_id)
    result = session.execute(statement).scalars().first()
    return result


def update_dynamic_images(session: Session):
    statement = select(DynamicImage).where(DynamicImage.labeled == False)
    images = session.execute(statement).scalars().all()

    # Iterate through images in pairs (assuming pairs are sequential)
    for i in range(0, len(images), 2):
        if i + 1 < len(images):
            thermal_image = images[i]
            optical_image = images[i + 1]
            temperature_current = get_temperatures(session, thermal_image.id)
            temperature_previous = get_temperatures(session,
                                                    thermal_image.id - 1)
            is_sick, disease = is_plant_sick(thermal_image.file_url, optical_image.file_url,
                                             temperature_current, temperature_previous)
            if disease:
                disease = disease[0]
                disease_id = get_or_create_disease(session, disease)
                thermal_image.predicted_disease = disease_id
                optical_image.predicted_disease = disease_id

            thermal_image.is_sick = is_sick
            optical_image.is_sick = is_sick
            thermal_image.labeled = True
            optical_image.labeled = True

            session.add(thermal_image)
            session.add(optical_image)

        session.commit()


def update_uploaded_images(session: Session):
    statement = select(UploadedImages).where(UploadedImages.predicted_disease == None)
    images = session.exec(statement).all()

    for image in images:
        result, remedy = predict(image.file_url)
        if result:
            disease_id = get_or_create_disease(session, result)
            image.predicted_disease = disease_id
            session.add(image)

    session.commit()


def schedule_updates():
    '''
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: update_static_images(next(get_db())), 'interval', hours=1)
    scheduler.add_job(lambda: update_dynamic_images(next(get_db())), 'interval', hours=1)
    scheduler.add_job(lambda: update_uploaded_images(next(get_db())), 'interval', hours=1)
    scheduler.start()
    '''
    update_dynamic_images(session=get_db())


# schedule_updates()


@router.get("/update_dynamic_now")
def update_dynamic_images_endpoint(session: Session = Depends(get_db)):
    update_dynamic_images(session)
    return {"message": "All images updated"}


@router.get("/update_offline_now")
def update_offline_images_endpoint(session: Session = Depends(get_db)):
    update_uploaded_images(session)
    return {"message": "All images updated"}


@router.get("/update_static_now")
def update_static_images_endpoint(session: Session = Depends(get_db)):
    update_static_images(session)
    return {"message": "All images updated"}

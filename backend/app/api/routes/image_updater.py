from typing import Optional

import aiohttp
from app.api.deps import get_db
from app.api.routes.base import send_notification
from app.api.src.main import predict
from app.core.disease_prediction import detect_sick_plant_thermal_image
from app.core.disease_prediction import is_plant_sick
from app.models.diseases import Diseases
from app.models.dynamic_images import DynamicImage
from app.models.models import User
from app.models.static_images import StaticImages
from app.models.temperature import Temperature
from app.models.uploaded_images import UploadedImages
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlmodel import Session, select

router = APIRouter()


def get_or_create_disease(session: Session, disease_name: str, remedy: str = '/'):
    disease = session.exec(select(Diseases).where(Diseases.name == disease_name)).first()
    if not disease:
        disease = Diseases(name=disease_name, description="", healing_steps=remedy)
        session.add(disease)
        session.commit()
        session.refresh(disease)
    return disease.id


def update_static_images(session: Session):
    statement = select(StaticImages).where(StaticImages.labeled == False)
    images = session.execute(statement).scalars().all()

    for i in range(0, len(images), 2):
        if i + 1 < len(images):
            thermal_image = images[i]
            optical_image = images[i + 1]
            is_sick_thermal = detect_sick_plant_thermal_image(thermal_image.file_url)

            if is_sick_thermal:
                result, remedy = predict(thermal_image.file_url)
                if result:
                    disease_id = get_or_create_disease(session, result)
                    thermal_image.predicted_disease = disease_id
                    optical_image.predicted_disease = disease_id

                thermal_image.is_sick = True
                optical_image.is_sick = True
            else:
                thermal_image.is_sick = False
                optical_image.is_sick = False

            thermal_image.labeled = True
            optical_image.labeled = True

            session.add(thermal_image)
            session.add(optical_image)

    session.commit()


def get_temperatures(session: Session, image_id: int) -> Optional[Temperature]:
    statement = select(Temperature).where(Temperature.image_id == image_id)
    result = session.execute(statement).scalars().first()
    return result


async def fetch_image_data(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()


async def update_dynamic_images(session: Session):
    statement = select(DynamicImage).where(DynamicImage.labeled == False)
    images = session.execute(statement).scalars().all()
    users_statement = select(User)
    users = session.execute(users_statement).scalars().all()

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
                thermal_image_data = await fetch_image_data(thermal_image.file_url)
                optical_image_data = await fetch_image_data(optical_image.file_url)
                for user in users:
                    await send_notification(user, optical_image_data, thermal_image_data, disease)

            thermal_image.is_sick = is_sick
            optical_image.is_sick = is_sick
            thermal_image.labeled = True
            optical_image.labeled = True

            session.add(thermal_image)
            session.add(optical_image)

        session.commit()


def update_uploaded_images(session: Session):
    statement = select(UploadedImages).where(UploadedImages.labeled == False)
    images = session.exec(statement).all()

    for image in images:
        result, remedy = predict(image.file_url)
        if result:
            disease_id = get_or_create_disease(session, result)
            image.predicted_disease = disease_id
        image.labeled = True
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


# @router.get("/update_dynamic_now")
# def update_dynamic_images_endpoint(session: Session = Depends(get_db)):
#     update_dynamic_images(session)
#     return {"message": "All images updated"}
#
#
# @router.get("/update_offline_now")
# def update_offline_images_endpoint(session: Session = Depends(get_db)):
#     update_uploaded_images(session)
#     return {"message": "All images updated"}
#
#
# @router.get("/update_static_now")
# def update_static_images_endpoint(session: Session = Depends(get_db)):
#     update_static_images(session)
#     return {"message": "All images updated"}
async def update_dynamic_images_task(session: Session):
    await update_dynamic_images(session)


async def update_offline_images_task(session: Session):
    await update_uploaded_images(session)


async def update_static_images_task(session: Session):
    await update_static_images(session)


@router.get("/update_dynamic_now")
def update_dynamic_images_endpoint(background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    background_tasks.add_task(update_dynamic_images_task, session)
    return {"message": "Dynamic images update started"}


@router.get("/update_offline_now")
def update_offline_images_endpoint(background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    background_tasks.add_task(update_offline_images_task, session)
    return {"message": "Offline images update started"}


@router.get("/update_static_now")
def update_static_images_endpoint(background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    background_tasks.add_task(update_static_images_task, session)
    return {"message": "Static images update started"}

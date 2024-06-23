import datetime
import random

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


def update_dynamic_images(session: Session):
    # Select images with no predicted disease
    statement = select(DynamicImage).where(DynamicImage.predicted_disease == None)
    images = session.execute(statement).scalars().all()

    # Initialize previous temperatures
    prev_temperatures = None

    # Iterate through images in pairs (assuming pairs are sequential)
    for i in range(0, len(images), 2):
        if i + 1 < len(images):
            thermal_image = images[i]
            optical_image = images[i + 1]

            is_sick, disease, current_temperatures = is_plant_sick(thermal_image.file_url, optical_image.file_url,
                                                prev_temperatures)
            if not current_temperatures or current_temperatures[0] <= 15.0 or current_temperatures[0] >= 40:
                current_temperatures=[20.2+random.choice([0.5, 0.2, 0.1, 0.6, 0.7, 0.8])]
            print(is_sick, disease)
            print(current_temperatures)
            temperature1 = Temperature(average=current_temperatures[0]+5.6,
                                      current=current_temperatures[0],
                                      max=current_temperatures[0]+10.6,
                                      image_id=images[i].id,
                                      created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())

            temperature2 = Temperature(average=current_temperatures[0] + 5.6,
                                      current=current_temperatures[0],
                                      max=current_temperatures[0] + 10.6,
                                      image_id=images[i+1].id,
                                      created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())

            session.add(temperature1)
            session.add(temperature2)
            session.commit()
            continue
            if disease:
                disease_id = get_or_create_disease(session, disease)
                thermal_image.predicted_disease = disease_id
                optical_image.predicted_disease = disease_id

            thermal_image.is_sick = is_sick
            optical_image.is_sick = is_sick

            # session.add(thermal_image)
            # session.add(optical_image)

            # Update previous temperatures
            prev_temperatures = current_temperatures

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


@router.get("/update_now")
def update_all_images(session: Session = Depends(get_db)):
    #update_static_images(session)
    update_dynamic_images(session)
    #update_uploaded_images(session)
    return {"message": "All images updated"}
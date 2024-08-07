# from app.db.session import get_db
import base64
import math
import os
from contextlib import asynccontextmanager
from datetime import datetime
from email.mime.image import MIMEImage

from app.models.models import User
from app.api.deps import SessionDep
from app.api.deps import get_db
from app.api.src.main import predict
from app.core.disease_prediction import is_plant_sick
from app.models.diseases import Diseases, CreateDisease, DiseasesOut
from app.models.dynamic_images import DynamicImage, DynamicImageOut
from app.models.image import Image, ImageOut, ImagesOut
from app.models.static_images import StaticImages, StaticImageOut, StaticImagesOut
from app.models.temperature import TemperatureData, Temperature
from app.models.uploaded_images import UploadedImages, UploadedImageOut, UploadedImagesOut
from fastapi import APIRouter
from fastapi import Depends, Query
from fastapi import File, UploadFile
from fastapi.responses import RedirectResponse
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

router = APIRouter()
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

URL = os.getenv("DB_URL", "mysql+aiomysql://root:admin@localhost:3306/ews")
engine = create_engine(URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

URL = os.getenv("DB_URL", "mysql+aiomysql://root:admin@localhost:3306/ews")
engine = create_engine(URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base routes
@router.get('/', include_in_schema=False)
async def landing_page():
    return RedirectResponse(url='/docs')


@router.get('/health')
async def health_check():
    return 'OK'


@router.get('/data')
async def get_data():
    return 'Test'


@asynccontextmanager
async def get_session():
    async with SessionLocal() as session:
        yield session


@router.get("/diseases/{name}")
async def get_disease(session: SessionDep,
                      name: str = None,
                      # db: Optional[AsyncSession] = Depends(get_db)
                      ):
    stmt = select(Diseases).where(Diseases.name == name)

    query = session.execute(stmt)
    result = query.first()
    return result[0]


@router.get("/diseases")
async def get_all_diseases(session: SessionDep,
                           # db: Optional[AsyncSession] = Depends(get_db)
                           ):
    stmt = select(Diseases)
    query = session.execute(stmt)
    diseases = query.scalars().all()
    return DiseasesOut(data=diseases, count=len(diseases))


class ChangeIsSickRequest(BaseModel):
    type: str
    image_id: int
    is_sick_human_input: bool


@router.post("/change-is-sick")
async def change_is_sick(request: ChangeIsSickRequest, session: SessionDep):
    stmt = None
    if request.type == "dynamic":
        stmt = select(DynamicImage).where(DynamicImage.id == request.image_id)
    elif request.type == "uploaded":
        stmt = select(UploadedImages).where(UploadedImages.id == request.image_id)
    elif request.type == "static":
        stmt = select(StaticImages).where(StaticImages.id == request.image_id)

    if stmt is None:
        return {"message": "error"}

    query = session.execute(stmt)
    image = query.scalars().one()

    if image:
        image.is_sick_human_input = request.is_sick_human_input
        session.commit()
        return {"message": f"Updated image {request.image_id} successfully."}
    else:
        return {"error": "Image not found."}, 404


class ChangeDiseaseRequest(BaseModel):
    type: str
    image_id: int
    disease_id: int


@router.post("/change-disease")
async def change_disease(request: ChangeDiseaseRequest, session: SessionDep):
    if request.type == "dynamic":
        stmt = select(DynamicImage).where(DynamicImage.id == request.image_id)
    elif request.type == "uploaded":
        stmt = select(UploadedImages).where(UploadedImages.id == request.image_id)
    elif request.type == "static":
        stmt = select(StaticImages).where(StaticImages.id == request.image_id)
    query = session.execute(stmt)
    image = query.scalars().one()
    if image:
        image.predicted_disease_human_input = request.disease_id
        session.commit()
        return {"message": f"Updated image {request.image_id} successfully."}
    else:
        return {"error": "Image not found."}, 404


@router.get("/dashboard")
async def get_dashboard_images(session: SessionDep,
                               # db: Optional[AsyncSession] = Depends(get_db)
                               ):
    stmt = select(DynamicImage).order_by(DynamicImage.created_at.desc()).limit(4)
    query = session.execute(stmt)
    images = query.scalars().all()
    images_data = []
    for image in images:
        image_disease = session.execute(
            select(Diseases).where(Diseases.id == image.predicted_disease)).scalars().first()
        human_image_disease = session.execute(
            select(Diseases).where(Diseases.id == image.predicted_disease_human_input)).scalars().first()

        images_data.append(ImageOut(id=image.id,
                                    created_at=image.created_at,
                                    updated_at=image.updated_at,
                                    predicted_disease=image_disease.name if image_disease else "",
                                    is_sick=image.is_sick if image.is_sick is not None else False,
                                    predicted_disease_human_input=human_image_disease.name if human_image_disease else "",
                                    is_sick_human_input=image.is_sick_human_input if image.is_sick_human_input is not None else False,
                                    file_url=image.file_url,
                                    ))
    return ImagesOut(data=images_data, count=len(images))


@router.get("/dashboard")
async def get_dashboard_images(session: SessionDep,
                               # db: Optional[AsyncSession] = Depends(get_db)
                               ):
    stmt = select(Image).order_by(Image.created_at.desc()).limit(4)
    query = session.execute(stmt)
    images = query.scalars().all()
    images_data = []
    for image in images:
        image_disease = session.execute(select(Diseases).where(Diseases.id == image.disease)).scalars().first()
        images_data.append(ImageOut(id=image.id,
                                    created_at=image.created_at,
                                    updated_at=image.updated_at,
                                    predicted_disease=image_disease.name if image_disease else "",
                                    predicted_disease_human_input=image_disease.name if image_disease else "",
                                    is_sick_human_input=image.is_sick_human_input if image.is_sick_human_input is not None else False,
                                    is_sick=image.is_sick if image.is_sick is not None else False,
                                    file_url=image.file_url,
                                    ))
    return ImagesOut(data=images_data, count=len(images))


@router.get("/images")
async def get_all_images(session: SessionDep,
                         # db: Optional[AsyncSession] = Depends(get_db)
                         ):
    stmt = select(Image)
    query = session.execute(stmt)
    images = query.scalars().all()
    images_data = []
    for image in images:
        image_disease = session.execute(
            select(Diseases).where(Diseases.id == image.predicted_disease)).scalars().first()
        human_image_disease = session.execute(
            select(Diseases).where(Diseases.id == image.predicted_disease_human_input)).scalars().first()
        images_data.append(ImageOut(id=image.id,
                                    created_at=image.created_at,
                                    updated_at=image.updated_at,
                                    predicted_disease=image_disease.name if image_disease else "",
                                    predicted_disease_human_input=human_image_disease.name if image_disease else "",
                                    is_sick_human_input=image.is_sick_human_input if image.is_sick_human_input is not None else False,
                                    is_sick=image.is_sick if image.is_sick is not None else False,
                                    file_url=image.file_url,
                                    ))
    return ImagesOut(data=images_data, count=len(images))


@router.get("/static-images", response_model=StaticImagesOut)
async def get_static_images(session: SessionDep):
    stmt = select(StaticImages)
    query = session.execute(stmt)
    images = query.scalars().all()
    images_data = []
    for image in images:
        image_disease = session.execute(
            select(Diseases).where(Diseases.id == image.predicted_disease)).scalars().first()
        human_image_disease = session.execute(
            select(Diseases).where(Diseases.id == image.predicted_disease_human_input)).scalars().first()
        images_data.append(StaticImageOut(
            id=image.id,
            created_at=image.created_at,
            updated_at=image.updated_at,
            predicted_disease=image_disease.name if image_disease else "",
            predicted_disease_human_input=human_image_disease.name if human_image_disease else "",
            is_sick_human_input=image.is_sick_human_input if image.is_sick_human_input is not None else False,
            is_sick=image.is_sick if image.is_sick is not None else False,
            file_url=image.file_url,
            labeled=image.labeled,
        ))
    return StaticImagesOut(data=images_data, count=len(images))


@router.get("/dynamic-images")
async def get_dynamic_images(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        session: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * page_size

    stmt = select(DynamicImage).offset(offset).limit(page_size)
    result = session.execute(stmt)
    images = result.scalars().all()

    total_stmt = select(func.count(DynamicImage.id))
    total_result = session.execute(total_stmt)
    total_images_count = total_result.scalar()

    total_pages = math.ceil(total_images_count / page_size)

    images_data = []
    for image in images:
        image_disease_result = session.execute(
            select(Diseases).where(Diseases.id == image.predicted_disease)
        )
        image_disease = image_disease_result.scalars().first()

        human_image_disease_result = session.execute(
            select(Diseases).where(Diseases.id == image.predicted_disease_human_input)
        )
        human_image_disease = human_image_disease_result.scalars().first()
        temperature = session.execute(
            select(Temperature).where(Temperature.image_id == image.id)
        ).scalars().first()

        images_data.append(DynamicImageOut(
            id=image.id,
            average_temperature=temperature.average if temperature else 30.4,
            created_at=image.created_at,
            updated_at=image.updated_at,
            predicted_disease=image_disease.name if image_disease else "",
            predicted_disease_human_input=human_image_disease.name if human_image_disease else "",
            is_sick_human_input=image.is_sick_human_input if image.is_sick_human_input is not None else False,
            is_sick=image.is_sick if image.is_sick is not None else False,
            file_url=image.file_url,
            labeled=image.labeled,
        ))
    return {
        "data": images_data,
        "count": len(images),
        "total": total_images_count,
        "total_pages": total_pages,
        "page": page,
        "page_size": page_size
    }


@router.get("/uploaded-images")
async def get_uploaded_images(session: SessionDep,
                              # db: Optional[AsyncSession] = Depends(get_db)
                              ):
    stmt = select(UploadedImages)
    query = session.execute(stmt)
    images = query.scalars().all()
    images_data = []
    for image in images:
        image_disease = session.execute(
            select(Diseases).where(Diseases.id == image.predicted_disease)).scalars().first()
        human_image_disease = session.execute(
            select(Diseases).where(Diseases.id == image.predicted_disease_human_input)).scalars().first()
        images_data.append(UploadedImageOut(id=image.id,
                                            created_at=image.created_at,
                                            updated_at=image.updated_at,
                                            predicted_disease=image_disease.name if image_disease else "",
                                            predicted_disease_human_input=human_image_disease.name if human_image_disease else "",
                                            is_sick_human_input=image.is_sick_human_input if image.is_sick_human_input is not None else False,
                                            is_sick=image.is_sick if image.is_sick is not None else False,
                                            file_url=image.file_url,
                                            labeled=image.labeled
                                            ))
    return UploadedImagesOut(data=images_data, count=len(images))


@router.post("/diseases")
async def create_disease(disease: CreateDisease, session: SessionDep):
    disease = Diseases.model_validate(disease)
    session.add(disease)
    session.commit()
    session.refresh(disease)
    return disease


# @router.get("/diseases/{d_name}")
# async def read_diseases(d_name: str, db: Optional[AsyncSession] = Depends(get_db)):
#     stmnt = select(Diseases).filter(Diseases.d_name == d_name)
#     query = await db.execute(stmnt)
#     results = query.all()
#     return results


@router.get('/data')
async def get_data():
    return 'Test'


# @router.post('/test-disease')
# async def test_api(image: UploadFile):
#     """
#     OVA E PREKU API
#     """


#     image_data = await image.read()
#     base64_string = base64.b64encode(image_data).decode('utf-8')
#     url = "https://susya.onrender.com"
#     r = requests.post(url, json={"image": base64_string})
#     response_text = r.json()
#     return {"response": response_text}


@router.post('/get-disease-prediction')
async def get_disease_prediction(image: UploadFile):
    image_data = await image.read()
    base64_string = base64.b64encode(image_data).decode('utf-8')
    response = predict(base64_string)

    # if response.get('prediction') != 'Tomato_healthy':
    #     mailto = 'tamarailieva@live.com'
    #     await send_notification(mailto, image_data)

    return {"response": response}


async def send_notification(user: User, optical_image_data: bytes, thermal_image_data: bytes = None,
                            disease: str = None):
    email_sender = 'ews_webapi@outlook.com'
    email_password = 'Ews_Api_Web'

    subject = 'Известување за болно растение!'
    body = (
        f'Здраво {user.full_name}.\nПостои сомневање дека вашето растение е болно, ве молиме преземете соодветни акции. '
        f'Потенцијална болест: {disease}')

    # Create a MIMEText object to represent the email content
    message = MIMEMultipart()
    message['From'] = email_sender
    message['To'] = user.email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Attach the image to the email
    thermal_image = MIMEImage(thermal_image_data, name='thermal_sick_plant_image.png')
    optical_image = MIMEImage(optical_image_data, name='optical_sick_plant_image.png')
    message.attach(thermal_image)
    message.attach(optical_image)

    # Connect to the Outlook SMTP server
    smtp_server = 'smtp.office365.com'  # For Outlook/Office 365
    smtp_port = 587  # For TLS

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable encryption
        server.login(email_sender, email_password)
        text = message.as_string()
        server.sendmail(email_sender, user.email, text)
    except Exception as e:
        print(f'Failed to send email. Error: {str(e)}')
    finally:
        server.quit()  # Close the connection


@router.post("/upload-image")
async def upload_image(session: SessionDep, image: UploadFile = File(...)):
    image_data = await image.read()
    base_64_str = base64.b64encode(image_data).decode('utf-8')
    image_url = await upload_image_to_imagekit(base_64_str)
    new_image = DynamicImage(file_url=image_url, created_at=datetime.now(), updated_at=datetime.now())

    session.add(new_image)
    session.commit()
    session.refresh(new_image)

    return {"image_id": new_image.id}


@router.post("/temperatures")
async def add_temperatures(session: SessionDep, temperatures_data: TemperatureData):
    new_temperatures = Temperature(
        average=temperatures_data.average_temperature,
        min=temperatures_data.min_temperature,
        max=temperatures_data.max_temperature,
        image_id=temperatures_data.image_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(new_temperatures)
    session.commit()


@router.post("/upload-image-uploaded/")
async def upload_image_uploaded(session: SessionDep, image: UploadFile = File(...)):
    image_data = await image.read()
    base_64_str = base64.b64encode(image_data).decode('utf-8')
    image_url = await upload_image_to_imagekit(base_64_str)
    new_image = UploadedImages(file_url=image_url, created_at=datetime.now(), updated_at=datetime.now())

    session.add(new_image)
    session.commit()
    session.refresh(new_image)


@router.post("/upload-image-static/")
async def upload_image_static(session: SessionDep, image: UploadFile = File(...)):
    image_data = await image.read()
    base_64_str = base64.b64encode(image_data).decode('utf-8')
    image_url = await upload_image_to_imagekit(base_64_str)
    new_image = StaticImages(file_url=image_url, created_at=datetime.now(), updated_at=datetime.now())

    session.add(new_image)
    session.commit()
    session.refresh(new_image)

    return {"id": new_image.id, "file_url": new_image.file_url}


@router.get("/detect-sick-plants")
async def detect_sick_plants(session: SessionDep):
    stmt = select(Image).where(Image.disease == None)
    images = session.execute(stmt).scalars().all()
    for image in images:
        is_sick = is_plant_sick(image.file_url)


async def upload_image_to_imagekit(image_data: bytes) -> str:
    """
    Uploads an image to ImageKit and returns the URL of the uploaded image.

    :param image_data: Byte data of the image to upload.
    :return: URL of the uploaded image.
    """

    file_name = f"uploaded_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"

    imagekit = ImageKit(
        private_key='private_VsSJjaYJ2gnAC2marFLqt5FE/3g=',
        public_key='public_m0+lDAqfD5XPJipY5PpNOLrwfGM=',
        url_endpoint='https://ik.imagekit.io/EwsGroup'
    )
    imagekit_url = imagekit.url({
        "path": "/Sliki/",
        "url_endpoint": "https://ik.imagekit.io/EwsGroup",
    })

    options = UploadFileRequestOptions(
        use_unique_file_name=False,
        tags=['thermal', 'optical', 'uploaded'],
        folder='/Sliki/',
        is_private_file=False,
        custom_coordinates='10,10,20,20',
        response_fields=['tags', 'custom_coordinates', 'is_private_file', 'custom_metadata'],
        webhook_url=imagekit_url,
        overwrite_file=True,
        overwrite_ai_tags=False,
        overwrite_tags=False,
        overwrite_custom_metadata=True
    )

    result = imagekit.upload_file(
        file=image_data,
        file_name=file_name,
        options=options
    )
    if result.response_metadata:
        return result.response_metadata.raw["url"]
    else:
        return "Upload failed, no URL returned"


@router.post('/predict-disease')
async def predict_disease_from_image(session: SessionDep):
    return predict("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTAsyN9JjHJmhptDHCWAkqt0FAKbD72UqxmaQ&s")

# from app.db.session import get_db
import base64
import os
from contextlib import asynccontextmanager
from datetime import datetime
from email.mime.image import MIMEImage
from io import BytesIO

from app.api.deps import SessionDep
from app.api.src.main import predict
from app.models.diseases import Diseases, CreateDisease, DiseasesOut
from app.models.image import Image, ImagesOut
from app.models.image import ImageOut
from fastapi import APIRouter
from fastapi import File, UploadFile
from fastapi.responses import RedirectResponse
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.disease_prediction import detect_sick_plant_thermal_image

from app.core.disease_prediction import is_plant_sick

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
                                    disease=image_disease.name if image_disease else "",
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
        image_disease = session.execute(select(Diseases).where(Diseases.id == image.disease)).scalars().first()
        images_data.append(ImageOut(id=image.id,
                                    created_at=image.created_at,
                                    updated_at=image.updated_at,
                                    disease=image_disease.name if image_disease else "",
                                    file_url=image.file_url,
                                    ))
    return ImagesOut(data=images_data, count=len(images))


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

    # Assuming response['prediction'] contains the predicted disease
    if response.get('prediction') != 'Tomato_healthy':
        mailto = 'tamarailieva@live.com'  # Email address to send the notification
        await send_notification(mailto, image_data)
    #     mailto = 'ivan.trifunov@outlook.com'  # Email address to send the notification
    #     await send_notification(mailto, image_data)

    return {"response": response}


async def send_notification(email_receiver: str, image_data: bytes):
    email_sender = 'ews_webapi@outlook.com'
    email_password = 'Ews_Api_Web'

    subject = 'Известување за болно растение!!!'
    body = 'Your plant appears to be sick. Please take necessary action.'

    # Create a MIMEText object to represent the email content
    message = MIMEMultipart()
    message['From'] = email_sender
    message['To'] = email_receiver
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Attach the image to the email
    image = MIMEImage(image_data, name='sick_plant_image.png')
    message.attach(image)

    # Connect to the Outlook SMTP server
    smtp_server = 'smtp.office365.com'  # For Outlook/Office 365
    smtp_port = 587  # For TLS

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable encryption
        server.login(email_sender, email_password)
        text = message.as_string()
        server.sendmail(email_sender, email_receiver, text)
        print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email. Error: {str(e)}')
    finally:
        server.quit()  # Close the connection


@router.post("/upload-image")
async def upload_image(session: SessionDep, image: UploadFile = File(...)):
    image_data = await image.read()
    base_64_str = base64.b64encode(image_data).decode('utf-8')
    image_url = await upload_image_to_imagekit(base_64_str)
    print(image_url)
    new_image = Image(file_url=image_url, created_at=datetime.now(), updated_at=datetime.now())

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
        print(image.file_url, is_sick)

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

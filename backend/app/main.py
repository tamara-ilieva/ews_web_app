from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
# if settings.BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[
#             str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
#         ],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.API_V1_STR)


def dev_start():
    import uvicorn

    uvicorn.run('app.main:app', host="127.0.0.1", port=8008)


def dev_watch():
    import uvicorn

    uvicorn.run('app.main:app', host="127.0.0.1", port=8008, reload=True)

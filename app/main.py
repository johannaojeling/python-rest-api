from fastapi import FastAPI
from google.cloud.firestore_v1 import AsyncClient

from app.api.router import api_router
from app.config.settings import Settings
from app.database.firestore import FirestoreDatabase
from app.repositories.firestore_user_repository import FirestoreUserRepository

app = FastAPI()
app.include_router(api_router)


@app.on_event("startup")
async def startup() -> None:
    settings = Settings()
    firestore_client = AsyncClient()
    firestore_db = FirestoreDatabase(firestore_client)
    user_repository = FirestoreUserRepository(
        firestore_db=firestore_db, collection=settings.collection
    )
    app.state.user_repository = user_repository

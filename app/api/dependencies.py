from functools import lru_cache

from google.cloud.firestore_v1 import AsyncClient

from app.config.settings import Settings
from app.utils.firestore import FirestoreClient


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_firestore_client() -> FirestoreClient:
    client = AsyncClient()
    return FirestoreClient(client)

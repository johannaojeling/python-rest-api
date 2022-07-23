from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from app import schemas
from app.database.firestore import FirestoreDatabase
from app.repositories.user_repository import UserNotFound, UserRepository


class FirestoreUserRepository(UserRepository):
    def __init__(self, firestore_db: FirestoreDatabase, collection: str) -> None:
        self._firestore_db: FirestoreDatabase = firestore_db
        self._collection: str = collection

    async def create_user(
        self, user: schemas.UserCreate, user_id: Optional[str] = None
    ) -> schemas.User:
        user_id = await self._firestore_db.create(
            collection=self._collection,
            data=jsonable_encoder(user),
            document_id=user_id,
        )
        return await self.get_user(user_id)

    async def get_user(self, user_id: str) -> schemas.User:
        user_doc = await self._firestore_db.get(self._collection, user_id)
        if not user_doc:
            raise UserNotFound(f"user with id {user_id!r} not found")
        return schemas.User.parse_obj({"id": user_id, **user_doc})

    async def get_all_users(self) -> List[schemas.User]:
        return [
            schemas.User.parse_obj({"id": user_id, **user_doc})
            async for user_id, user_doc in self._firestore_db.get_all(self._collection)
        ]

    async def update_user(self, user: schemas.UserUpdate, user_id: str) -> schemas.User:
        await self._firestore_db.update(
            collection=self._collection,
            document_id=user_id,
            data=jsonable_encoder(user),
        )
        return await self.get_user(user_id)

    async def delete_user(self, user_id: str) -> None:
        user_doc = await self._firestore_db.get(self._collection, user_id)
        if not user_doc:
            raise UserNotFound(f"user with id {user_id!r} not found")
        await self._firestore_db.delete(self._collection, user_id)
        return None

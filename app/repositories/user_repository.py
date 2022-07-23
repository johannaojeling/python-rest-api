from abc import ABC, abstractmethod
from typing import List, Optional

from app import schemas


class UserRepository(ABC):
    @abstractmethod
    async def create_user(
        self, user: schemas.UserCreate, user_id: Optional[str] = None
    ) -> schemas.User:
        pass

    @abstractmethod
    async def get_user(self, user_id) -> schemas.User:
        pass

    @abstractmethod
    async def get_all_users(self) -> List[schemas.User]:
        pass

    @abstractmethod
    async def update_user(self, user: schemas.UserUpdate, user_id: str) -> schemas.User:
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> None:
        pass


class UserNotFound(Exception):
    pass

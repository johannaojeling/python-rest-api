from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.api.dependencies.repository import get_user_repository
from app.repositories.user_repository import UserNotFound, UserRepository
from app.schemas.user import User, UserCreate, UserUpdate

api_router = APIRouter()


@api_router.post("/", response_model=User, status_code=201)
async def create_user(
    user_create: UserCreate,
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    return await user_repository.create_user(user_create)


@api_router.get("/{user_id}", response_model=User, status_code=200)
async def get_user(
    user_id: str,
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    try:
        return await user_repository.get_user(user_id)
    except UserNotFound:
        raise HTTPException(
            status_code=404, detail=f"No user with id {user_id!r} exists"
        )


@api_router.get("/", response_model=List[User], status_code=200)
async def get_all_users(
    user_repository: UserRepository = Depends(get_user_repository),
) -> List[User]:
    return await user_repository.get_all_users()


@api_router.put("/{user_id}", response_model=User, status_code=200)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    user_repository: UserRepository = Depends(get_user_repository),
) -> Union[User, JSONResponse]:
    try:
        await user_repository.get_user(user_id)
        return await user_repository.update_user(user_update, user_id)
    except UserNotFound:
        user_create = UserCreate(
            first_name=user_update.first_name,
            last_name=user_update.last_name,
            email=user_update.email,
        )
        user = await user_repository.create_user(user_create, user_id)
        return JSONResponse(status_code=201, content=jsonable_encoder(user))


@api_router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    user_repository: UserRepository = Depends(get_user_repository),
) -> None:
    try:
        await user_repository.delete_user(user_id)
    except UserNotFound:
        raise HTTPException(
            status_code=404, detail=f"No user with id {user_id!r} exists"
        )

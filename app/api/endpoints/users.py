from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
)

from app.api.dependencies import get_firestore_client, get_settings
from app.config.settings import Settings
from app.schemas.users import UserRequest, UserResponse
from app.utils.firestore import FirestoreClient

api_router = APIRouter()


@api_router.post("/", response_model=UserResponse, status_code=HTTP_201_CREATED)
async def create_user(
    user_request: UserRequest,
    firestore_client: FirestoreClient = Depends(get_firestore_client),
    settings: Settings = Depends(get_settings),
) -> UserResponse:
    user_id = await firestore_client.create(
        collection=settings.collection, data=jsonable_encoder(user_request)
    )
    return UserResponse(
        id=user_id,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        email=user_request.email,
    )


@api_router.get("/{user_id}", response_model=UserResponse, status_code=HTTP_200_OK)
async def get_user(
    user_id: str,
    firestore_client: FirestoreClient = Depends(get_firestore_client),
    settings: Settings = Depends(get_settings),
) -> UserResponse:
    entry = await firestore_client.get(settings.collection, user_id)
    if not entry:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"No user with id {user_id!r} exists"
        )
    return UserResponse.parse_obj({"id": user_id, **entry})


@api_router.get("/", response_model=List[UserResponse], status_code=HTTP_200_OK)
async def get_all_users(
    firestore_client: FirestoreClient = Depends(get_firestore_client),
    settings: Settings = Depends(get_settings),
) -> List[UserResponse]:
    return [
        UserResponse.parse_obj({"id": user_id, **entry})
        async for user_id, entry in firestore_client.get_all(settings.collection)
    ]


@api_router.put("/{user_id}", response_model=UserResponse, status_code=HTTP_200_OK)
async def update_user(
    user_id: str,
    user_request: UserRequest,
    firestore_client: FirestoreClient = Depends(get_firestore_client),
    settings: Settings = Depends(get_settings),
) -> Union[UserResponse, JSONResponse]:
    user_exists = await firestore_client.exists(settings.collection, user_id)
    user_response = UserResponse(
        id=user_id,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        email=user_request.email,
    )
    if user_exists:
        await firestore_client.update(
            collection=settings.collection,
            document_id=user_id,
            data=jsonable_encoder(user_request),
        )
        return user_response

    await firestore_client.create(
        collection=settings.collection,
        data=jsonable_encoder(user_request),
        document_id=user_id,
    )
    return JSONResponse(
        status_code=HTTP_201_CREATED, content=jsonable_encoder(user_response)
    )


@api_router.delete("/{user_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    firestore_client: FirestoreClient = Depends(get_firestore_client),
    settings: Settings = Depends(get_settings),
) -> None:
    user_exists = await firestore_client.exists(settings.collection, user_id)
    if not user_exists:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"No user with id {user_id!r} exists"
        )
    await firestore_client.delete(settings.collection, user_id)

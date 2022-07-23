from typing import AsyncIterator, Iterable

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app.api.endpoints.users import api_router
from app.repositories.firestore_user_repository import FirestoreUserRepository

test_collection = "test_collection"
test_url = "http://test"
test_user_id = "uid123"
test_data = {
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@mail.com",
}


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router)
    return app


@pytest.mark.asyncio
async def test_create_user(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_db = mocker.AsyncMock()
    user_repository = FirestoreUserRepository(
        firestore_db=firestore_db, collection=test_collection
    )
    app.state.user_repository = user_repository

    firestore_db.create.return_value = test_user_id
    firestore_db.get.return_value = test_data

    async with AsyncClient(app=app, base_url=test_url) as test_client:
        response = await test_client.post("/", json=test_data)

    expected_status = 201
    expected_json = {
        "id": test_user_id,
        **test_data,
    }
    assert response.status_code == expected_status, "Should return status 201"
    assert (
        response.json() == expected_json
    ), "Should return json representing the created user object"


@pytest.mark.asyncio
async def test_get_user(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_db = mocker.AsyncMock()
    user_repository = FirestoreUserRepository(
        firestore_db=firestore_db, collection=test_collection
    )
    app.state.user_repository = user_repository

    firestore_db.get.return_value = test_data

    async with AsyncClient(app=app, base_url=test_url) as test_client:
        response = await test_client.get(f"/{test_user_id}")

    expected_status = 200
    expected_json = {
        "id": test_user_id,
        **test_data,
    }
    assert response.status_code == expected_status, "Should return status 200"
    assert (
        response.json() == expected_json
    ), "Should return json representing the retrieved user object"


@pytest.mark.asyncio
async def test_get_user_not_found(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_db = mocker.AsyncMock()
    user_repository = FirestoreUserRepository(
        firestore_db=firestore_db, collection=test_collection
    )
    app.state.user_repository = user_repository

    firestore_db.get.return_value = None

    async with AsyncClient(app=app, base_url=test_url) as test_client:
        response = await test_client.get(f"/{test_user_id}")

    expected_status = 404
    assert response.status_code == expected_status, "Should return status 404"


@pytest.mark.asyncio
async def test_get_all_users(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_db = mocker.AsyncMock()
    user_repository = FirestoreUserRepository(
        firestore_db=firestore_db, collection=test_collection
    )
    app.state.user_repository = user_repository

    users = [
        (
            "uid123",
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@mail.com",
            },
        ),
        (
            "uid124",
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@mail.com",
            },
        ),
    ]

    get_all = mocker.MagicMock()
    get_all.return_value = async_iter(users)
    firestore_db.get_all = get_all

    async with AsyncClient(app=app, base_url=test_url) as test_client:
        response = await test_client.get("/")

    expected_status = 200
    expected_json = [
        {
            "id": "uid123",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@mail.com",
        },
        {
            "id": "uid124",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@mail.com",
        },
    ]
    assert response.status_code == expected_status, "Should return status 200"
    assert (
        response.json() == expected_json
    ), "Should return json representing the retrieved user objects"


@pytest.mark.asyncio
async def test_update_user(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_db = mocker.AsyncMock()
    user_repository = FirestoreUserRepository(
        firestore_db=firestore_db, collection=test_collection
    )
    app.state.user_repository = user_repository

    existing_data = {
        "first_name": "old_first_name",
        "last_name": "old_last_name",
        "email": "old@email.com",
    }
    firestore_db.get.side_effect = (existing_data, test_data)
    firestore_db.update.side_effect = None

    async with AsyncClient(app=app, base_url=test_url) as test_client:
        response = await test_client.put(f"/{test_user_id}", json=test_data)

    expected_status = 200
    expected_json = {
        "id": test_user_id,
        **test_data,
    }
    assert response.status_code == expected_status, "Should return status 200"
    assert (
        response.json() == expected_json
    ), "Should return json representing the updated user object"


@pytest.mark.asyncio
async def test_update_user_not_found(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_db = mocker.AsyncMock()
    user_repository = FirestoreUserRepository(
        firestore_db=firestore_db, collection=test_collection
    )
    app.state.user_repository = user_repository

    firestore_db.get.side_effect = (None, test_data)
    firestore_db.create.return_value = test_user_id

    async with AsyncClient(app=app, base_url=test_url) as test_client:
        response = await test_client.put(f"/{test_user_id}", json=test_data)

    expected_status = 201
    expected_json = {
        "id": test_user_id,
        **test_data,
    }
    assert response.status_code == expected_status, "Should return status 201"
    assert (
        response.json() == expected_json
    ), "Should return json representing the created user object"


@pytest.mark.asyncio
async def test_delete_user(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_db = mocker.AsyncMock()
    user_repository = FirestoreUserRepository(
        firestore_db=firestore_db, collection=test_collection
    )
    app.state.user_repository = user_repository

    existing_data = {
        "first_name": "old_first_name",
        "last_name": "old_last_name",
        "email": "old@email.com",
    }
    firestore_db.get.return_value = existing_data

    async with AsyncClient(app=app, base_url=test_url) as test_client:
        response = await test_client.delete(f"/{test_user_id}")

    expected_status = 204
    assert response.status_code == expected_status, "Should return status 204"


@pytest.mark.asyncio
async def test_delete_user_not_found(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_db = mocker.AsyncMock()
    user_repository = FirestoreUserRepository(
        firestore_db=firestore_db, collection=test_collection
    )
    app.state.user_repository = user_repository

    firestore_db.get.return_value = None

    async with AsyncClient(app=app, base_url=test_url) as test_client:
        response = await test_client.delete(f"/{test_user_id}")

    expected_status = 404
    assert response.status_code == expected_status, "Should return status 404"


async def async_iter(items: Iterable) -> AsyncIterator:
    for item in items:
        yield item


if __name__ == "__main__":
    pytest.main()

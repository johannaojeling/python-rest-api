from typing import AsyncIterator, Iterable

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app.api.dependencies import get_firestore_client, get_settings
from app.api.endpoints.users import api_router
from app.config.settings import Settings

base_url = "http://test"
settings = Settings(collection="test_collection")
user_id = "uid123"
data = {
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@mail.com",
}


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_settings] = lambda: settings
    return app


@pytest.mark.asyncio
async def test_create_user(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_client = mocker.AsyncMock()
    app.dependency_overrides[get_firestore_client] = lambda: firestore_client

    firestore_client.create.return_value = user_id

    async with AsyncClient(app=app, base_url=base_url) as test_client:
        response = await test_client.post("/", json=data)

    expected_status = 201
    expected_json = {
        "id": user_id,
        **data,
    }
    assert response.status_code == expected_status, "Should return status 201"
    assert (
        response.json() == expected_json
    ), "Should return json representing the created user object"


@pytest.mark.asyncio
async def test_get_user(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_client = mocker.AsyncMock()
    app.dependency_overrides[get_firestore_client] = lambda: firestore_client

    firestore_client.get.return_value = data

    async with AsyncClient(app=app, base_url=base_url) as test_client:
        response = await test_client.get(f"/{user_id}")

    expected_status = 200
    expected_json = {
        "id": user_id,
        **data,
    }
    assert response.status_code == expected_status, "Should return status 200"
    assert (
        response.json() == expected_json
    ), "Should return json representing the retrieved user object"


@pytest.mark.asyncio
async def test_get_user_not_found(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_client = mocker.AsyncMock()
    app.dependency_overrides[get_firestore_client] = lambda: firestore_client

    firestore_client.get.return_value = None

    async with AsyncClient(app=app, base_url=base_url) as test_client:
        response = await test_client.get(f"/{user_id}")

    expected_status = 404
    assert response.status_code == expected_status, "Should return status 404"


@pytest.mark.asyncio
async def test_get_all_users(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_client = mocker.AsyncMock()
    app.dependency_overrides[get_firestore_client] = lambda: firestore_client

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
    firestore_client.get_all = get_all

    async with AsyncClient(app=app, base_url=base_url) as test_client:
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
    firestore_client = mocker.AsyncMock()
    app.dependency_overrides[get_firestore_client] = lambda: firestore_client

    firestore_client.exists.return_value = True
    firestore_client.update.side_effect = None

    async with AsyncClient(app=app, base_url=base_url) as test_client:
        response = await test_client.put(f"/{user_id}", json=data)

    expected_status = 200
    expected_json = {
        "id": user_id,
        **data,
    }
    assert response.status_code == expected_status, "Should return status 200"
    assert (
        response.json() == expected_json
    ), "Should return json representing the updated user object"


@pytest.mark.asyncio
async def test_update_user_not_found(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_client = mocker.AsyncMock()
    app.dependency_overrides[get_firestore_client] = lambda: firestore_client

    firestore_client.exists.return_value = False

    async with AsyncClient(app=app, base_url=base_url) as test_client:
        response = await test_client.put(f"/{user_id}", json=data)

    expected_status = 201
    expected_json = {
        "id": user_id,
        **data,
    }
    assert response.status_code == expected_status, "Should return status 201"
    assert (
        response.json() == expected_json
    ), "Should return json representing the created user object"


@pytest.mark.asyncio
async def test_delete_user(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_client = mocker.AsyncMock()
    app.dependency_overrides[get_firestore_client] = lambda: firestore_client

    firestore_client.exists.return_value = True
    firestore_client.document.side_effect = None

    async with AsyncClient(app=app, base_url=base_url) as test_client:
        response = await test_client.delete(f"/{user_id}")

    expected_status = 204
    assert response.status_code == expected_status, "Should return status 204"


@pytest.mark.asyncio
async def test_delete_user_not_found(mocker: MockerFixture, app: FastAPI) -> None:
    firestore_client = mocker.AsyncMock()
    app.dependency_overrides[get_firestore_client] = lambda: firestore_client

    firestore_client.exists.return_value = False

    async with AsyncClient(app=app, base_url=base_url) as test_client:
        response = await test_client.delete(f"/{user_id}")

    expected_status = 404
    assert response.status_code == expected_status, "Should return status 404"


async def async_iter(items: Iterable) -> AsyncIterator:
    for item in items:
        yield item


if __name__ == "__main__":
    pytest.main()

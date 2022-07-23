from starlette.requests import Request

from app.repositories.user_repository import UserRepository


def get_user_repository(request: Request) -> UserRepository:
    return request.app.state.user_repository

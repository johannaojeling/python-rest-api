from pydantic import BaseSettings


class Settings(BaseSettings):
    collection: str

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserRequest(UserBase):
    pass


class UserResponse(UserBase):
    id: str

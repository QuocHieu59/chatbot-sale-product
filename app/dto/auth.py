from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    age: int
    repeat_password: str

class UserInformation(BaseModel):
    name: str | None = None
    age: int | None = None
    role: str | None = None
    password: str | None = None
    email: str | None = None

class UserId(BaseModel):
    user_id: str

class UserUpdate(BaseModel):
    id: str
    name: str | None = None
    age: int | None = None
    password: str | None = None
    email: str | None = None
    role: str | None = None
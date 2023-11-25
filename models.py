from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel
from enum import Enum

class Gender(str, Enum):
    male = 'male'
    female = 'female'

class Role(str, Enum):
    admin = 'admin'
    user = 'user'
    student = 'student'

class User(BaseModel):
    id: Optional[UUID] = uuid4()
    first_name: str
    middle_name: Optional[str] = 'Mayak'
    last_name: str
    gender: Gender
    roles: list[Role]

class UpdateUser(BaseModel):
    id: Optional[UUID] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    roles: Optional[list[Role]] = None

class TestUser(BaseModel):
    gender: Gender
    roles: list[Role]
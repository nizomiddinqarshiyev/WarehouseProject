from datetime import datetime, date

from pydantic import BaseModel, Field


class RegisterScheme(BaseModel):
    firstname: str
    lastname: str
    login: str
    email: str
    phone_number: str
    password1: str = Field(min_length=8)
    password2: str = Field(min_length=8)


class UserInfoScheme(BaseModel):
    login: str
    firstname: str
    lastname: str
    email: str
    phone: str
    last_updated: datetime


class LoginScheme(BaseModel):
    login: str
    password: str = Field(min_length=8)


class CostumerAddScheme(BaseModel):
    firstname: str
    lastname: str
    phone: str
    email: str

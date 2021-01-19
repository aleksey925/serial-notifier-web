import typing as t

from pydantic import Field
from pydantic.main import BaseModel

from models import Sex


class LoginReqSchema(BaseModel):
    email: str = Field(regex='.*@.*', description='email пользователя')
    password: str = Field(min_length=3, description='пароль пользователя')


class TokenRespSchema(BaseModel):
    access_token: str
    token_type: str


class RegistrationReqSchema(BaseModel):
    email: str = Field(regex='.*@.*', description='email пользователя')
    password: str = Field(min_length=3, description='пароль пользователя')
    sex: t.Optional[Sex]
    nick: str = Field(min_length=3, max_length=50)
    name: t.Optional[str] = Field(max_length=50)
    surname: t.Optional[str] = Field(max_length=50)


class RegistrationRespSchema(BaseModel):
    id: int
    email: str = Field(description='email пользователя')
    sex: t.Optional[Sex]
    nick: str = Field(min_length=3, max_length=50)
    name: t.Optional[str] = Field(max_length=50)
    surname: t.Optional[str] = Field(max_length=50)

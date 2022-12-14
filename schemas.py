from datetime import datetime
import uuid

from pydantic import BaseModel, EmailStr, constr


class UserBaseSchema(BaseModel):
    first_name: str
    last_name: str
    username:str
    mobile_number: str
    email: EmailStr
    country: str
    class Config:
        orm_mode = True


class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    password_confirm: str


class ForgotPassword(BaseModel):
    email: EmailStr


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UpdatePassword(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    passwordConfirm: str


class UserResponse(UserBaseSchema):
    id: uuid.UUID
    created_at: datetime


class UpdateUser(UserBaseSchema):
    role: str


class CreateNewPrice(BaseModel):
    price: int
    currency: str
    country: str


class CreateNewTransaction(BaseModel):
    account_name:str
    account_number:int
    amount: int
    base_price: int
    currency: str

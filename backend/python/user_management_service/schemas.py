from pydantic import BaseModel, Field


class SignupPayload(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)


class LoginPayload(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)

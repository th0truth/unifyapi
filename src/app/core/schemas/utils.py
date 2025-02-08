from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    edbo_id: int
    scopes: list

class UpdatePassword(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=16)
    new_password: str = Field(..., min_length=8, max_length=16)

class PasswordRecovery(BaseModel):
    email: str
    new_password: str

class SetGrade(BaseModel):
    subject: str
    edbo_id: int
    grade: int
    date: str | None = None
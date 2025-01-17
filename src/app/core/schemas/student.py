from pydantic import BaseModel, Field, EmailStr

class StudentCreate(BaseModel):
    edbo_id: int
    name: str
    email: EmailStr | None = None
    password: str = Field(..., min_length=8, max_length=16)

class StudentPublic(BaseModel):
    role: str | None = None
    edbo_id: int
    name: str
    # password: str

class StudentPrivate(BaseModel):
    edbo_id: int
    name: str
    email: EmailStr | None = None
    password: str
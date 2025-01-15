from pydantic import BaseModel, Field, EmailStr
from typing import Any

from core.db.database import MongoDB

class AdminDB(MongoDB):
    DATABASE_NAME = "admin"
    COLLECTION_NAME = "admin"
from pydantic import BaseModel
from uuid import UUID

class MessageCreate(BaseModel):
    content: str

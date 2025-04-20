from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class TicketCreate(BaseModel):
    title: str
    description: str

class MessageOut(BaseModel):
    id: UUID
    content: str
    is_ai: bool
    created_at: datetime

class TicketOut(BaseModel):
    id: UUID
    title: str
    description: str
    status: str
    created_at: datetime
    user_id: UUID

    class Config:
        orm_mode = True
        from_attributes = True

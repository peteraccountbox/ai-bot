from pydantic import BaseModel
from typing import Optional

class UserQuery(BaseModel):
    question: str
    user_id: Optional[int] = None

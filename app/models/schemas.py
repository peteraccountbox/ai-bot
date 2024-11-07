from typing import Optional
from pydantic import BaseModel
from enum import Enum

class ContentType(Enum):
    URL = "URL"
    TEXT = "TEXT"
    PDF = "PDF"

class TrainRequest(BaseModel):
    type: ContentType
    content: str
    id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "URL",
                "content": "https://example.com",
                "id": "My Document ID"
            }
        }

class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is EngageBay CRM?",
                "conversation_id": "optional-uuid-here"
            }
        }
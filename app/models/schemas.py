from pydantic import BaseModel, HttpUrl
from typing import Literal, Union, Optional
from enum import Enum

class ContentType(str, Enum):
    URL = "URL"
    RAW_CONTENT = "RAW_CONTENT"
    FILE = "FILE"

class QueryRequest(BaseModel):
    query: str

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

class StructuredQueryRequest(BaseModel):
    query: str
    memory_id: Optional[str] = None
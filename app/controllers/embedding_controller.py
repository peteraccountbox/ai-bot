# controllers/embedding_controller.py

from fastapi import APIRouter, HTTPException
from app.models.schemas import URLRequest, QueryRequest
from app.services.embedding_service import EmbeddingService

router = APIRouter()
embedding_service = EmbeddingService()

@router.get("/")
def read_root():
    return {"message": "Welcome to AI Bot API!"}

@router.post("/train")
async def store_url(request: URLRequest):
    try:
        embedding_service.store_url_content(request.url)
        return {"message": "URL content stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer")
async def retrieve_answer(request: QueryRequest):
    try:
        answer = embedding_service.retrieve_answer(request.query)
        if answer:
            return {"answer": answer}
        return {"message": "No relevant content found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
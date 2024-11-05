# controllers/embedding_controller.py

from fastapi import APIRouter, HTTPException
from app.models.schemas import TrainRequest, QueryRequest
from app.services.embedding_service import EmbeddingService

router = APIRouter()
embedding_service = EmbeddingService()

@router.get("/")
def read_root():
    return {"message": "Welcome to AI Bot API!"}

@router.post("/train")
async def store_url(request: TrainRequest):
    try:
        await embedding_service.process_payload(request)
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

@router.delete("/reset/collection/{collection_name}")
async def delete_collection(collection_name: str):
    try:
        success = embedding_service.delete_collection(collection_name)
        if success:
            return {"message": f"Collection '{collection_name}' deleted successfully"}
        return {"message": f"Collection '{collection_name}' not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
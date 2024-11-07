# controllers/embedding_controller.py

from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import TrainRequest, QueryRequest, StructuredQueryRequest
from app.services.embedding_service import EmbeddingService
from app.utils.context import set_index_name, clear_index_name
from app.services.chained_ai_service import ChainedAIService

router = APIRouter()
embedding_service = EmbeddingService()
ai_service = ChainedAIService()

@router.get("/")
def read_root():
    return {"message": "Welcome to AI Bot API!"}

async def set_index_context(index_name: str):
    set_index_name(index_name)
    try:
        yield
    finally:
        clear_index_name()

@router.post("/{index_name}/train")
async def store_url(
    index_name: str,
    request: TrainRequest,
    _: None = Depends(set_index_context)
):
    try:
        await embedding_service.process_payload(request)
        return {"message": "URL content stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{index_name}/answer")
async def retrieve_answer(
    index_name: str,
    request: QueryRequest,
    _: None = Depends(set_index_context)
):
    try:
        answer = embedding_service.retrieve_answer(request.query)
        if answer:
            return {"answer": answer}
        return {"message": "No relevant content found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{index_name}/reset")
async def reset_database(
    index_name: str,
    _: None = Depends(set_index_context)
):
    try:
        success = embedding_service.delete_collection(index_name)
        if success:
            return {"message": f"Database {index_name} cleared successfully"}
        return {"message": "Failed to clear database"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{index_name}/document")
async def delete_document(
    index_name: str,
    request: TrainRequest,
    _: None = Depends(set_index_context)
):
    try:
        success = embedding_service.delete_document(request.id)
        if success:
            return {"message": f"Document {request.id} deleted successfully from {index_name}"}
        return {"message": f"Document {request.id} not found in {index_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{index_name}/structured-answer")
def retrieve_chained_ai_answer(
    index_name: str,
    request: StructuredQueryRequest,
    _: None = Depends(set_index_context)
):
    try:
        answer = ai_service.get_structured_answer(
            query=request.query,
            memory_id=request.memory_id
        )
        if answer:
            return {"answer": answer}
        return {"message": "No relevant content found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
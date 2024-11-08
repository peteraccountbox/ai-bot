# controllers/embedding_controller.py

from fastapi import APIRouter, HTTPException, Depends, Header
from app.models.schemas import TrainRequest, QueryRequest
from app.services.embedding_service import EmbeddingService
from app.utils.context import set_index_name, clear_index_name, set_bot_role, clear_bot_role
from typing import Optional

router = APIRouter()
embedding_service = EmbeddingService()

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
    bot_role: Optional[str] = Header(default="",  alias="bot-role"),
    _: None = Depends(set_index_context)
):
    try:
        set_bot_role(bot_role)
        answer = embedding_service.retrieve_answer(
            user_input=request.query,
            conversation_id=request.conversation_id
        )
        return answer
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

@router.delete("/{index_name}/clear-history")
async def clear_chat_history(
    index_name: str,
    request: QueryRequest,
    _: None = Depends(set_index_context)
):
    try:
        if not request.conversation_id:
            raise HTTPException(status_code=400, detail="conversation_id is required")
            
        embedding_service.clear_memory(request.conversation_id)
        return {
            "message": "Chat history cleared successfully",
            "conversation_id": request.conversation_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
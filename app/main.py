# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from app.models import UserQuery
from app.services import BotService

app = FastAPI()

# Initialize BotService
bot_service = BotService()

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Bot API!"}

@app.post("/ask/")
async def ask_bot(query: UserQuery):
    if not query.question:
        raise HTTPException(status_code=400, detail="Question is required.")
    
    # Use the BotService to get the response
    response_text = bot_service.get_response(query.question)
    return {"user_id": query.user_id, "question": query.question, "response": response_text}
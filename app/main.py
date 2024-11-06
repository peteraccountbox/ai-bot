
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.controllers.embedding_controller import router as embedding_router

app = FastAPI()
app.include_router(embedding_router, prefix="/api/v1")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/chat-ui")
async def chat_ui(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8181)
from fastapi import FastAPI

from app.routers.chat import router as chat_router
from app.routers.update import router as update_router


app = FastAPI(title="GigWork Chatbot API")


app.include_router(chat_router, prefix="/chat", tags=["Chatbot"])
app.include_router(update_router, prefix="/update", tags=["Update"])
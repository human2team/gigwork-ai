from fastapi import FastAPI
from app.routers.chat import router as chat_router

app = FastAPI(title="GigWork Chatbot API")

app.include_router(chat_router, prefix="/chat", tags=["Chatbot"])
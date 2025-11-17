from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.route.chat import router as chat_router
from app.route.update import router as update_router

origins = ["http://localhost:5173", "http://localhost:8000"]

app = FastAPI(title="GigWork Chatbot API")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(update_router, prefix="/update", tags=["update_router"])
app.include_router(chat_router, prefix="/chat", tags=["chat_router"])
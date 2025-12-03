from fastapi import FastAPI

from app.routers.chat import router as chat_router
from app.routers.update_conditions import router as condition_update_router
from app.routers.chatbot_page import router as chatbot_page_router

app = FastAPI(title="GigWork Chatbot API")

app.include_router(chat_router, prefix="/chat", tags=["Chatbot"])
app.include_router(chatbot_page_router, tags=["Pages"])

app.include_router(condition_update_router, prefix="/conditions", tags=["Conditions"])

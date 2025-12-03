from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGE_PATH = os.path.join(BASE_DIR, "..", "pages", "chatbot.html")


@router.get("/test")
def serve_chatbot_page():
    return FileResponse(PAGE_PATH)

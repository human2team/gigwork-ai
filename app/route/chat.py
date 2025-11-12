from fastapi import APIRouter, HTTPException

from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.graph.chat_graph import workflow, ChatState

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    text: str
    condition: Optional[Dict[str, Any]] = {}
    search: bool = False

@router.post("/", summary="Chat Endpoint", description="LangGraph 챗봇 엔드포인트")
def chat_endpoint(payload: ChatRequest):
    try:
        state = ChatState(
            user_id=payload.user_id,
            text=payload.text,
            condition=payload.condition or {},
            search=payload.search,
        )

        result_state = workflow.invoke(state)

        return {
            "success": True,
            "response": result_state.get("response"),
            "result": result_state.get("result"),
            "state": result_state,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

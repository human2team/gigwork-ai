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
        # search가 true이고 text가 있으면 condition.requirements에 text 값 추가
        if payload.search and payload.text:
            if payload.condition is None:
                payload.condition = {}
            payload.condition['requirements'] = payload.text

        state = ChatState(
            user_id=payload.user_id,
            text=payload.text,
            condition=payload.condition or {},
            search=payload.search,
        )
        
        # # search가 true이고 text가 있으면 condition.requirements에 text 값 추가
        # if payload.search and payload.text:
        #     if payload.condition is None:
        #         payload.condition = {}
        #     payload.condition['requirements'] = payload.text
        #     state['condition'] = payload.condition
        
        print(f'payload========={payload}')
        result_state = workflow.invoke(state)

        return {
            "success": True,
            "response": result_state.get("response"),
            "result": result_state.get("result"),
            "state": result_state,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

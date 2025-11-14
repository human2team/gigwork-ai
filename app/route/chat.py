from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List, Union

from app.graph.chat_graph import workflow, ChatState

router = APIRouter()

class ConditionModel(BaseModel):
    gender: Optional[str] = None
    age: Optional[int] = None
    place: Optional[str] = None
    work_days: Optional[Union[List[str], str]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    hourly_wage: Optional[int] = None
    requirements: Optional[str] = None
    category: Optional[str] = None
    
    @field_validator('work_days', mode='before')
    @classmethod
    def convert_work_days(cls, v):
        # 빈 문자열이나 None이면 빈 리스트 반환
        if not v or v == "":
            return []
        # 문자열이면 리스트로 변환
        if isinstance(v, str):
            return [v] if v else []
        # 이미 리스트면 그대로 반환
        return v

class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    text: str
    condition: Optional[ConditionModel] = None
    search: bool = False

@router.post("/", summary="Chat Endpoint", description="LangGraph 챗봇 엔드포인트")
async def chat_endpoint(payload: ChatRequest):
    try:
        print(f"[DEBUG] Received ChatRequest")
        print(f"[DEBUG] - user_id: {payload.user_id}")
        print(f"[DEBUG] - text: {payload.text}")
        print(f"[DEBUG] - search: {payload.search}")
        print(f"[DEBUG] - condition type: {type(payload.condition)}")
        print(f"[DEBUG] - condition value: {payload.condition}")
        
        # ConditionModel을 dict로 변환
        condition_dict = payload.condition.dict(exclude_none=True) if payload.condition else {}
        print(f"[DEBUG] - condition_dict: {condition_dict}")
        
        state = ChatState(
            user_id=payload.user_id,
            text=payload.text,
            condition=condition_dict,
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
        print(f"[ERROR] Exception in chat_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

from fastapi import APIRouter, HTTPException

from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.graph.graph import workflow, ChatState  # workflow가 반드시 함수/런너 객체여야 함

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

        # workflow가 함수/런너 객체일 때만 정상 동작
        result_state = workflow.invoke(state)

        return {
            "success": True,
            "response": result_state.get("response"),
            "result": result_state.get("result"),
            "state": result_state,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")


"""
{
  "condition": {
    "place": [ 
      { "region1": "서울", "region2": "강남구" }
    ],
    "category": [
      { "category1": "병원·간호·연구", "category2": "생동성·임상시험" }
    ],
    "work_days": ["2025-12-03"],
    "start_time": "09:00",
    "end_time": "18:00",
    "hourly_wage": 15000,
    "job_text": null,
    "person_text": null
  },
  "llm_response": "조건을 업데이트했습니다.",
  "result": [
    {
      "title": "강남 생동성 시험 보조",
      "location": "서울 강남구",
      "description": "임상 시험 보조 업무이며...",
      "id": 32
    }
  ]
}
"""

"""

{
  "text": "강남에서 주 5일 서빙 알바 찾아줘",
  "condition": {
    "gender": null,
    "age": null,
    "place": null,
    "work_days": null,
    "start_time": null,
    "end_time": null,
    "hourly_wage": null,
    "requirements": null,
    "category": null,
    "categories": null,
    "job_text": null,
    "person_text": null
  },
  "search": false
}
"""
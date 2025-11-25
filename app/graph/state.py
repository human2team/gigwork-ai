# app/graph/state.py
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PendingTask(BaseModel):
    condition_type: str
    condition_value: Optional[str] = None
    operation_type: str  # "replace" | "add" | "remove"
    question: str


class ChatState(BaseModel):
    # 모드 관리
    mode: str = "normal"   # "normal" | "clarification"

    # 사용자 입력값
    user_input_text: str

    # 수집할 핵심 조건
    conditions: Dict[str, Any] = Field(
        default_factory=lambda: {
            "regions": [],     # [{ "region1": "...", "region2": "..." }]
            "categories": [],  # [{ "category1": "...", "category2": "..." }]
            "dates": [],       # ["2025-11-24", ...]
            "start_time": None,
            "end_time": None,
            "wage_min": None,
            "gender": None,
            "age": None,
            "job_text": None,
            "person_text": None,
        }
    )

    # 인텐트 판단 결과 (classifier가 채움)
    intent_in_condition_related: bool = False
    intent_has_condition_text: bool = False
    intent_has_modify_request: bool = False
    intent_want_search: bool = False
    intent_is_answer_to_question: bool = False

    # Clarification 관련
    pending_question: Optional[str] = None
    pending_tasks: List[PendingTask] = Field(default_factory=list)
    error: List[str] = Field(default_factory=list)

    # 검색 결과
    search_result: Optional[List[Dict[str, Any]]] = None

    # 사용자에게 보낼 최종 메시지
    response_text: Optional[str] = None

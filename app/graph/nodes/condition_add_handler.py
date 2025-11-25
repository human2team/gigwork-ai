# app/graph/nodes/condition_add_handler.py
import json
from app.graph.state import ChatState
from app.llm.openai_client import LLMClient

llm = LLMClient()

CONDITION_SCHEMA = {
    "type": "object",
    "properties": {
        "regions": {"type": "array", "items": {"type": "object"}},
        "categories": {"type": "array", "items": {"type": "object"}},
        "dates": {"type": "array", "items": {"type": "string"}},
        "start_time": {"type": ["string", "null"]},
        "end_time": {"type": ["string", "null"]},
        "wage_min": {"type": ["number", "null"]},
        "gender": {"type": ["string", "null"]},
        "age": {"type": ["number", "null"]},
        "job_text": {"type": ["string", "null"]},
        "person_text": {"type": ["string", "null"]}
    },
    "required": ["regions", "categories", "dates"]
}

def condition_add_handler(state: ChatState) -> ChatState:
    system_prompt = """
조건추출기 역할을 수행한다.
사용자 발화에서 알바 조건(지역, 분류, 날짜, 시급, 시간대 등)을 추출하여 JSON Schema에 맞게 반환하라.
JSON만 반환하고 설명하지 마라.
"""
    user_prompt = f"사용자 입력: {state.user_input_text}"

    result = llm.chat_json(
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt}],
        schema=CONDITION_SCHEMA,
        model="gpt-5-mini"
    )

    if result:
        for k, v in result.items():
            if v:
                state.conditions[k] = v
        state.response_text = "조건이 추가되었습니다."
    else:
        state.error.append("condition_add_failed")

    return state

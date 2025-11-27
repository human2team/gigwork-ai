# app/graph/nodes/condition_modify_handler.py
import json
from app.graph.state import ChatState
from app.llm.openai_client import LLMClient

llm = LLMClient()

MODIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "updates": {
            "type": "object",
            "additionalProperties": True
        },
        "errors": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["updates", "errors"]
}

def condition_modify_handler(state: ChatState) -> ChatState:
    system_prompt = """
조건 수정 도우미 역할을 한다.
기존 conditions를 보고, 사용자의 발화대로 수정할 필드를 JSON으로 반환하라.

반환 형식:
{
  "updates": { "wage_min": 12000, "start_time": "14:00" },
  "errors": ["어떤 지역을 삭제할지 명확하지 않습니다"]
}
"""
    user_prompt = f"""
[현재 조건]
{json.dumps(state.conditions, ensure_ascii=False)}

[사용자 발화]
{state.user_input_text}
"""

    result = llm.chat_json(
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt}],
        schema=MODIFY_SCHEMA,
        model="gpt-5-mini"
    )

    if result:
        for k, v in result["updates"].items():
            state.conditions[k] = v

        for e in result["errors"]:
            state.error.append(e)

        state.response_text = "조건을 수정했습니다." if not state.error else "일부 조건 처리에 문제가 있습니다."
    else:
        state.error.append("condition_modify_failed")

    return state

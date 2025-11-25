# app/graph/nodes/intent_classifier_normal.py
from app.graph.state import ChatState
from app.llm.openai_client import LLMClient

llm = LLMClient()

INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "intent_in_condition_related": {"type": "boolean"},
        "intent_has_condition_text": {"type": "boolean"},
        "intent_has_modify_request": {"type": "boolean"},
        "intent_want_search": {"type": "boolean"}
    },
    "required": [
        "intent_in_condition_related",
        "intent_has_condition_text",
        "intent_has_modify_request",
        "intent_want_search"
    ]
}

def intent_classifier_normal(state: ChatState) -> ChatState:
    system_prompt = """
다음 사용자 발화가 단기 알바 조건 수집 또는 검색과 관련된 것인지 판단하라.
항상 JSON 형식으로 반환하라.

판단 기준:
intent_in_condition_related:
  - 단기 알바, 시급, 지역, 요일, 업종, 아르바이트 조건 관련 대화인가?
intent_has_condition_text:
  - 발화에 조건 정보(시급, 지역, 요일, 직무)가 포함되어 있는가?
intent_has_modify_request:
  - 이미 저장된 조건을 수정, 변경, 삭제하려는 의도가 있는가?
intent_want_search:
  - 지금 조건으로 실제 아르바이트 검색을 요청했는가?

출력은 반드시 다음 JSON 형식만 가능:
{
  "intent_in_condition_related": true/false,
  "intent_has_condition_text": true/false,
  "intent_has_modify_request": true/false,
  "intent_want_search": true/false
}
"""
    user_prompt = f"사용자 발화: {state.user_input_text}"

    result = llm.chat_json(
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt}],
        schema=INTENT_SCHEMA,
        model="gpt-5-nano"
    )

    if result:
        state.intent_in_condition_related = result["intent_in_condition_related"]
        state.intent_has_condition_text = result["intent_has_condition_text"]
        state.intent_has_modify_request = result["intent_has_modify_request"]
        state.intent_want_search = result["intent_want_search"]
    else:
        state.error.append("intent_classifier_normal_failed")

    return state

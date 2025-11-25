# app/graph/nodes/intent_classifier_clarification.py
from app.graph.state import ChatState
from app.llm.openai_client import LLMClient

llm = LLMClient()

CLARIFICATION_INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "intent_is_answer_to_question": {"type": "boolean"},
        "intent_in_condition_related": {"type": "boolean"},
        "intent_has_condition_text": {"type": "boolean"},
        "intent_has_modify_request": {"type": "boolean"},
        "intent_want_search": {"type": "boolean"}
    },
    "required": [
        "intent_is_answer_to_question",
        "intent_in_condition_related",
        "intent_has_condition_text",
        "intent_has_modify_request",
        "intent_want_search"
    ]
}

def intent_classifier_clarification(state: ChatState) -> ChatState:
    system_prompt = """
당신은 Clarification 모드의 인텐트 분류기이다.
이전 질문(pending_question)에 대한 답인지 판단하고, 필요한 인텐트 값을 추출하라.

판단 기준:
intent_is_answer_to_question:
  - 사용자가 이전에 봇이 질문한 내용에 답변을 하고 있는가
intent_in_condition_related:
  - 단기 알바, 시급, 지역, 요일, 업종, 아르바이트 조건 관련 대화인가?
intent_has_condition_text:
  - 발화에 조건 정보(시급, 지역, 요일, 직무)가 포함되어 있는가?
intent_has_modify_request:
  - 이미 저장된 조건을 수정, 변경, 삭제하려는 의도가 있는가?
intent_want_search:
  - 지금 조건으로 실제 아르바이트 검색을 요청했는가?

JSON 형식으로 다음 다섯 값만 반환하라:
{
  "intent_is_answer_to_question": true/false,
  "intent_in_condition_related": true/false,
  "intent_has_condition_text": true/false,
  "intent_has_modify_request": true/false,
  "intent_want_search": true/false
}
"""
    user_prompt = f"""
[봇이 이전에 질문한 내용]
{state.pending_question}

[사용자의 이번 입력]
{state.user_input_text}
"""

    result = llm.chat_json(
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt}],
        schema=CLARIFICATION_INTENT_SCHEMA,
        model="gpt-5-nano"
    )

    if result:
        state.intent_is_answer_to_question = result["intent_is_answer_to_question"]
        state.intent_in_condition_related = result["intent_in_condition_related"]
        state.intent_has_condition_text = result["intent_has_condition_text"]
        state.intent_has_modify_request = result["intent_has_modify_request"]
        state.intent_want_search = result["intent_want_search"]
    else:
        state.error.append("intent_classifier_clarification_failed")

    return state

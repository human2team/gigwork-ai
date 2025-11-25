# app/graph/nodes/postprocess_router.py
import json
from app.graph.state import ChatState
from app.llm.openai_client import LLMClient

llm = LLMClient()

CLARIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {"type": "string"}
    },
    "required": ["question"]
}

def postprocess_router(state: ChatState) -> ChatState:
    """
    오류가 존재하면 -> error 배열을 기반으로 LLM으로 clarification 질문 생성
    오류가 없으면 -> mode를 normal로 유지하고 그대로 반환
    """

    if not state.error:
        state.mode = "normal"
        return state

    # 🔹 LLM에 넘겨줄 에러 정보 정리 (JSON 문자열로 변환)
    error_json = json.dumps(state.error, ensure_ascii=False, indent=2)

    system_prompt = """
당신은 조건 기반 알바 챗봇의 Clarification 질문 생성기입니다.

아래는 조건 수정 또는 추출 도중 발생한 오류 목록입니다.
각 오류는 condition_type, condition_value, operation_type, content로 구성됩니다.

사용자가 무엇을 정확히 입력해야 하는지, 어떤 정보가 필요한지를
알기 쉽고 자연스러운 한국어 질문 형태로 만들어 주세요.

반드시 JSON 형식으로만 출력:
{
  "question": "..."
}
"""
    user_prompt = f"오류 목록:\n{error_json}\n\n사용자에게 다시 어떤 내용을 물어보면 좋을까요?"

    result = llm.chat_json(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        schema=CLARIFICATION_SCHEMA,
        model="gpt-5-mini"
    )

    if result:
        state.pending_question = result["question"]
        state.response_text = result["question"]
        state.mode = "clarification"
    else:
        # LLM 실패 시 fallback
        state.pending_question = "확실하지 않은 부분이 있어요. 다시 정확히 말씀해 주세요."
        state.response_text = state.pending_question
        state.mode = "clarification"

    return state

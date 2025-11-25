from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from openai import OpenAI
import json

router = APIRouter()


class LLMClient:
    """
    OpenAI LLM 호출용 아주 얇은 래퍼.
    - response_format=json_object 로 강제
    - JSON 문자열을 파싱해 dict 로 반환
    """

    def __init__(self):
        # OPENAI_API_KEY 는 환경변수로 설정되어 있다고 가정
        self.client = OpenAI()

    def chat_json(self, *, messages: List[Dict[str, str]], model: str = "gpt-5-mini") -> Dict[str, Any]:
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
            )
        except Exception as e:
            raise RuntimeError(f"LLM 호출 실패: {e}")

        content = completion.choices[0].message.content
        if not content:
            raise RuntimeError("LLM 응답이 비어 있습니다.")

        # content 는 JSON 문자열이므로 파싱해서 dict 로 반환
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"LLM가 유효한 JSON 을 반환하지 않았습니다: {e}\n원본: {content}")


llm = LLMClient()


class ConditionUpdateRequest(BaseModel):
    history: List[Dict[str, Any]]
    user_input: str
    conditions: Dict[str, Any]


class ConditionUpdateResponse(BaseModel):
    updated_conditions: Dict[str, Any]
    llm_response: str
    missing_fields: Optional[List[str]] = None
    errors: Optional[List[str]] = None


@router.post("/update_conditions", response_model=ConditionUpdateResponse)
def update_conditions(request: ConditionUpdateRequest) -> ConditionUpdateResponse:
    system_prompt = """
너는 단기 알바 조건 수집 챗봇이다. 간결하고 정중하게 응답한다. 사용자의 알바 조건을 수집하면서 사용자의 입력에 대한 자연스러운 응답을 생성한다.
대화가 알바 조건 수집과 관련이 없으면, 정중하게 알바 조건에 대해 물어봐라.

목적
- 사용자의 입력과 기존 조건을 참고하여 최종 업데이트된 condition을 생성한다.
- 자연어 응답은 llm_response에 넣고, JSON 외 텍스트는 절대 포함하지 마라.

반드시 아래 JSON 구조만 반환하라. 키 이름 변경 금지.
{
  "updated_conditions": {
        "regions": "근무하고 싶은 지역 (예: 강남구, 송파구). 여러 개 가능.",
        "categories": "알바 업종이나 직무 (예: 카페, 주방보조, 택배). 여러 개 가능.",
        "dates": "근무 가능한 날짜 배열 (예: 2025-01-10). 여러 개 가능.",
        "start_time": "근무 시작 시간 (예: 09:00).",
        "end_time": "근무 종료 시간 (예: 18:00).",
        "wage_min": "희망하는 최소 시급. 숫자값.",
        "gender": "성별 제한이 있는 경우 (M,F,N). 대부분 null.",
        "age": "나이 또는 연령대 (예: 25, 20대).",
        "job_text": "하고 싶은 일 또는 희망형태에 대한 자연어 설명.",
        "person_text": "본인의 성격, 특성, 경험 등 자기 소개 문장."
    },
  "llm_response": "...",
}

설명 문장 포함 금지. JSON만 반환.
"""

    user_prompt = f"""
[대화 히스토리]
{json.dumps(request.history, ensure_ascii=False, indent=2)}

[기존 Conditions]
{json.dumps(request.conditions, ensure_ascii=False, indent=2)}

[사용자 입력]
{request.user_input}
"""

    try:
        result = llm.chat_json(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model="gpt-5-mini",
        )
    except RuntimeError as e:
        # LLM 호출/파싱 실패 시 HTTP 500
        raise HTTPException(status_code=500, detail=str(e))

    print("\n🔎 LLM RAW RESULT:\n", result, "\n")

    # LLM 이 반환한 JSON에서 필드 꺼내기
    updated_conditions = result.get("updated_conditions", {}) or {}
    llm_response_text = result.get("llm_response", "")

    # missing_fields 는 간단히 값이 비어있는 키들로 구성 (필요 없으면 이 부분 삭제해도 됨)
    expected_keys = [
        "regions",
        "categories",
        "dates",
        "start_time",
        "end_time",
        "wage_min",
        "gender",
        "age",
        "job_text",
        "person_text",
    ]
    missing_fields = [
        key
        for key in expected_keys
        if key not in updated_conditions
        or updated_conditions.get(key) in (None, "", [], {})
    ]

    return ConditionUpdateResponse(
        updated_conditions=updated_conditions,
        llm_response=llm_response_text,
        missing_fields=missing_fields or None,
        errors=None,
    )

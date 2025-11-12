from app.llm.openai_client import LLMClient

llm = LLMClient()

def classify_input(state):
    text = state.text
    messages = [
        {"role": "system", "content": "입력이 사용자 입장에서 아르바이트 관련 조건을 서술하는지 true/false로 판단하라."},
        {"role": "user", "content": text}
    ]
    res = llm.chat(messages)
    state.is_job_related = "true" in res.lower()
    if not state.is_job_related:
        state.response = "아르바이트 관련 조건을 설명해주세요."
    else:
        state.response = "원하시는 조건이 있으면 추가해 주세요. 검색을 누르시면 조건에 맞는 공고를 찾아드리겠습니다."
    print(f"[classify_input] is_job_related={state.is_job_related}")
    return state

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """OpenAI LLM 연결 관리 클래스"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OPENAI_API_KEY가 .env에 없습니다.")
        self.client = OpenAI(api_key=self.api_key)

    def chat(self, messages: list, model="gpt-4o-mini"):
        """Chat 모델 호출 (LangGraph 노드 등에서 공용으로 사용)"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ LLM 호출 오류: {e}")
            return None

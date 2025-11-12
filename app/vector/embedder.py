import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class Embedder:
    """텍스트를 임베딩 벡터로 변환"""

    def __init__(self, model="text-embedding-3-small"):
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY가 .env에 없습니다.")
        self.client = OpenAI(api_key=api_key)

    def create_embedding(self, text: str):
        """문자열 하나 → 벡터 반환"""
        try:
            res = self.client.embeddings.create(model=self.model, input=text)
            return res.data[0].embedding
        except Exception as e:
            print(f"❌ 임베딩 생성 실패: {e}")
            return []

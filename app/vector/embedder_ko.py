from sentence_transformers import SentenceTransformer

class EmbedderKo:
    """한국어 특화 임베딩 모델을 사용한 텍스트 벡터 변환"""

    def __init__(self, model="jhgan/ko-sroberta-multitask"):
        """
        한국어 임베딩 모델 초기화
        
        Args:
            model: Hugging Face 모델 이름 (기본: jhgan/ko-sroberta-multitask)
                   - 768차원 벡터 생성
                   - 한국어 동의어/유사어 처리에 강함
        """
        self.model_name = model
        print(f"📥 한국어 임베딩 모델 로딩 중: {model}")
        print("⏳ 첫 실행 시 모델 다운로드에 시간이 걸릴 수 있습니다 (~500MB)")
        self.model = SentenceTransformer(model)
        print("✅ 모델 로딩 완료")

    def create_embedding(self, text: str):
        """
        문자열 하나 → 벡터 반환 (로컬 실행, API 비용 없음)
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            list: 768차원 임베딩 벡터 (OpenAI는 1536차원)
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()  # numpy array → list 변환
        except Exception as e:
            print(f"❌ 임베딩 생성 실패: {e}")
            return []
    
    def create_embeddings_batch(self, texts: list[str]):
        """
        여러 문자열 → 벡터 리스트 반환 (배치 처리로 빠름)
        
        Args:
            texts: 임베딩할 텍스트 리스트
            
        Returns:
            list[list]: 각 텍스트에 대한 768차원 벡터 리스트
        """
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            print(f"❌ 배치 임베딩 생성 실패: {e}")
            return []

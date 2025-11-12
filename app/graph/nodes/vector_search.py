'''
from app.vector.embedder import Embedder
from app.db.database import PostgresDB

embedder = Embedder()
db = PostgresDB()

def vector_search(state):
    # 입력 텍스트를 벡터 임베딩으로 변환
    text = state.condition.get("requirements")
    embedding = embedder.get_embedding(text)

    # 벡터 임베딩을 사용해 유사도 검색 수행 및 결과 반환
    # 작성 예정
    return state
'''

# 더미 데이터 사용
# 폐기 예정
def vector_search(state):
    print("[vector_search] 실행됨")

    dummy_results = [
        {"id": 10, "title": "커피 전문점 바리스타", "similarity": 0.94},
        {"id": 11, "title": "디저트 카페 알바", "similarity": 0.91},
        {"id": 12, "title": "브런치 카페 홀서빙", "similarity": 0.88},
    ]

    state.result = dummy_results
    state.response = f"벡터 검색으로 {len(dummy_results)}개의 유사한 공고를 찾았습니다."
    return state

from app.vector.embedder import Embedder
from app.db.database import PostgresDB

embedder = Embedder()
db = PostgresDB()

# 테스트 테이블에서 벡터 유사도 기반으로 검색
# 실제 테이블로 수정 필요

def vector_search(state):
    print("[vector_search] 실행됨")

    text = state.condition.get("requirements")
    embedding = embedder.create_embedding(text)
    
    query = """
        SELECT 
            id,
            title,
            content,
            1 - (embedding <=> %s::vector) AS similarity,
            metadata,
            created_at
        FROM docs
        ORDER BY similarity DESC
        LIMIT 5;
    """
    params = (embedding,)

    try:
        rows = db.execute_query(query, params)
    except Exception as e:
        state.response = f"DB 검색 중 오류 발생: {e}"
        state.result = []
        return state

    state.result = rows
    state.response = f"벡터 유사도 기반으로 {len(rows)}개의 알바를 찾았습니다."

    return state

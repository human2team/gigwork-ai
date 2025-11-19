from app.vector.embedder import Embedder
from app.db.database import PostgresDB

embedder = Embedder()
db = PostgresDB()

def vector_search(state):
    print("[vector_search] 실행됨")

    text = state.condition.get("requirements")
    embedding = embedder.create_embedding(text)
    
    # embedding을 문자열로 변환 (pgvector 호환)
    if isinstance(embedding, list):
        embedding_str = str(embedding)
    else:
        embedding_str = embedding
    
    # query = """
    #     SELECT 
    #         id,
    #         title,
    #         content,
    #         1 - (embedding <=> %s::vector) AS similarity,
    #         metadata,
    #         created_at
    #     FROM docs
    #     ORDER BY similarity DESC
    #     LIMIT 5;
    # """
    
    limit = 5  # 검색 결과 개수
    similarity_threshold = 0.5  # 유사도 임계값
    # 1 - (embedding <=> %s::vector) AS similarity
    # AND (1 - (embedding <=> %s::vector)) >= %s
    # ORDER BY (1 - (embedding <=> %s::vector)) DESC
    query = """
        SELECT id, company, description, location, salary, status, title, work_days, work_hours, end_time, 
               other_requirement, qualifications, requirements, salary_type, start_time, category, age, education, gender,
               (1 - (embedding <=> '""" + embedding_str + """'::vector)) AS similarity
        FROM jobs
        WHERE embedding IS NOT NULL
          AND (1 - (embedding <=> '""" + embedding_str + """'::vector)) >= %s
        ORDER BY (1 - (embedding <=> '""" + embedding_str + """'::vector)) DESC
        LIMIT %s
    """

    params = (similarity_threshold, limit)

    try:
        print(f'@@@@@@@@@@@@@@@@@@@@@@@@')
        rows = db.execute_query(query, params)
        print(f'rows######################{rows}')
    except Exception as e:
        print(f'e$$$$$$$$$$$$$$$$$$$$$$$$$$${e}')
        state.response = f"DB 검색 중 오류 발생: {e}"
        state.result = []
        return state
    finally:
        db.close()

    state.result = rows
    state.response = f"벡터 유사도 기반으로 {len(rows)}개의 알바를 찾았습니다."

    return state

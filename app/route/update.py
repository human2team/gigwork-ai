from fastapi import APIRouter, HTTPException

from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.vector.embedder import Embedder
from app.db.database import PostgresDB

embedder = Embedder()
db = PostgresDB()

router = APIRouter()

class UpdateRequest(BaseModel):
    user_id: Optional[str] = None
    id: str

@router.post("/", summary="update Endpoint", description="사업자 정보 데이터 임베딩")
def chat_endpoint(payload: UpdateRequest):
    try:        
        print(f'payload========={payload}')
        id = payload.id
        code = '0'
        msg = ''
        
        query = """
            SELECT description
            FROM jobs
            WHERE id = %s
        """
        params = (id,)

        try:
            rows = db.execute_query(query, params)
            print(f'rows@@@@@{rows}')
            
            if rows and len(rows) > 0:
                row = rows[0]  # 첫 번째 row 가져오기
                desc = row['description']  # RealDictCursor이므로 딕셔너리처럼 접근
                print(f'{id}desc@@@@@{desc}')
                embedding = embedder.create_embedding(desc)
                print(f'embedding type: {type(embedding)}, length: {len(embedding) if isinstance(embedding, list) else "N/A"}')
                
                # pgvector는 리스트를 문자열 형태로 변환 필요
                # embedding이 리스트일 경우 문자열로 변환. pgvector는 '[0.1, 0.2, ...]' 형태의 문자열을 받음
                if isinstance(embedding, list):
                    embedding_str = str(embedding)
                else:
                    embedding_str = embedding
                
                query = """
                    UPDATE jobs SET embedding = %s WHERE id = %s
                """
                params = (embedding_str, id)
                db.execute_non_query(query, params)
                print(f'✅ ID {id} 업데이트 완료')
            else:
                msg = "해당 ID의 데이터를 찾을 수 없거나 업데이트 오류 발생"
                code = "-1"

        except Exception as e:
            msg = f"DB 검색 중 오류 발생: {e}"
            code = "-1"
        finally:
            return {
                "code": code,
                "msg": msg
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

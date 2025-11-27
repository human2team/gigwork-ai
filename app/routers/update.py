from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import logging
import numpy as np
from typing import List
import psycopg2
from psycopg2.extras import execute_values
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. 모델 로드 ---
MODEL_NAME = 'jhgan/ko-sroberta-multitask'
try:
    model = SentenceTransformer(MODEL_NAME)
    logger.info(f"✅ Embedding Model loaded successfully: {MODEL_NAME}")
except Exception as e:
    logger.error(f"❌ Failed to load embedding model {MODEL_NAME}: {e}")
    raise

router = APIRouter()

# --- 2. 데이터베이스 연결 설정 ---


# Neon PostgreSQL 연결 (임베딩 저장용)
def get_neon_connection():
    """Neon PostgreSQL 데이터베이스 연결 (임베딩 저장)"""
    try:
        # .env의 DB_URL에서 정보 파싱
        db_url = os.getenv('DB_URL')
        if not db_url:
            raise Exception('DB_URL 환경변수가 없습니다.')
        import re
        from urllib.parse import urlparse, parse_qs
        url = urlparse(db_url)
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port
        database = url.path[1:]  # /neondb -> neondb
        sslmode = parse_qs(url.query).get('sslmode', ['require'])[0]
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            sslmode=sslmode
        )
        logger.info("✅ Neon PostgreSQL connection successful")
        return connection
    except Exception as e:
        logger.error(f"❌ Neon connection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Neon connection failed: {str(e)}")

# --- 3. Request/Response 모델 ---
class JobUpdateRequest(BaseModel):
    job_id: int

class EmbeddingResponse(BaseModel):
    job_id: int
    status: str
    message: str

# --- 4. 핵심 로직 ---

def fetch_job_description(job_id: int) -> str:
    """
    PostgreSQL(Neon)에서 Job ID에 해당하는 description만 조회
    """
    connection = None
    try:
        connection = get_neon_connection()
        cursor = connection.cursor()
        query = "SELECT description FROM jobs WHERE id = %s"
        cursor.execute(query, (job_id,))
        result = cursor.fetchone()
        if not result or not result[0]:
            raise ValueError(f"Job ID {job_id}에 해당하는 데이터를 찾을 수 없습니다.")
        description = result[0]
        if not description or len(description.strip()) == 0:
            raise ValueError(f"Job ID {job_id}의 description이 비어있습니다.")
        logger.info(f"🔍 Fetched description for job_id {job_id}: {description[:100]}...")
        return description
    except Exception as e:
        logger.error(f"❌ PostgreSQL query error: {e}")
        raise
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("🔒 PostgreSQL connection closed")

def generate_embedding(text: str) -> np.ndarray:
    """
    텍스트를 임베딩 벡터로 변환
    """

    try:
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding
    except Exception as e:
        logger.error(f"❌ Embedding generation failed: {e}")
        raise


# --- 임베딩을 jobs 테이블에 저장하는 함수만 남김 ---
def save_embedding_to_jobs_table(job_id: int, embedding_vector: np.ndarray):
    # 임베딩 벡터를 Neon DB의 jobs 테이블의 embedding 컬럼에 저장
    connection = None
    try:
        connection = get_neon_connection()
        cursor = connection.cursor()
        embedding_list = embedding_vector.tolist()
        embedding_str = '[' + ','.join(map(str, embedding_list)) + ']'
        query = """
            UPDATE jobs 
            SET embedding = %s::vector
            WHERE id = %s
        """
        cursor.execute(query, (embedding_str, job_id))
        if cursor.rowcount == 0:
            raise ValueError(f"Job ID {job_id}가 jobs 테이블에 존재하지 않습니다.")
        connection.commit()
        logger.info(f"✅ Embedding saved to jobs.embedding for job_id: {job_id}")
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"❌ Failed to save embedding to Neon jobs table: {e}")
        raise
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("🔒 Neon connection closed")

# --- FastAPI 엔드포인트 추가 ---
@router.post("/")
def update_embedding(request: JobUpdateRequest):
    try:
        # 1. MySQL에서 description 조회
        description = fetch_job_description(request.job_id)
        # 2. 임베딩 생성
        embedding = generate_embedding(description)
        # 3. Neon jobs 테이블에 저장
        save_embedding_to_jobs_table(request.job_id, embedding)
        return EmbeddingResponse(job_id=request.job_id, status="success", message="Embedding updated")
    except Exception as e:
        logger.error(f"❌ Embedding update failed: {e}")
        return EmbeddingResponse(job_id=request.job_id, status="error", message=str(e))
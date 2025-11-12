import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class PostgresDB:
    """PostgreSQL 연결 및 쿼리 실행 클래스"""

    def __init__(self):
        self.db_url = os.getenv("DB_URL")
        self.conn = None

    def connect(self):
        try:
            if self.conn is None or self.conn.closed:
                self.conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
                print("✅ PostgreSQL 데이터베이스 연결 성공")
        except Exception as e:
            print(f"❌ PostgreSQL 데이터베이스 연결 실패: {e}")

    def execute_query(self, query: str, params: tuple = None):
        """SELECT 등 결과 반환 쿼리"""
        self.connect()
        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            result = cur.fetchall()
        return result

    def execute_non_query(self, query: str, params: tuple = None):
        """INSERT, UPDATE, DELETE 등 결과 없는 쿼리"""
        self.connect()
        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            self.conn.commit()

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
            print("🔒 데이터베이스 연결 종료")

    # def test(self):
    #     """현재 데이터베이스 내 모든 테이블 목록 표시"""
    #     self.connect()
    #     query = """
    #     SELECT table_schema, table_name
    #     FROM information_schema.tables
    #     WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    #     ORDER BY table_schema, table_name;
    #     """
    #     with self.conn.cursor() as cur:
    #         cur.execute(query)
    #         tables = cur.fetchall()

    #     if not tables:
    #         print("⚠️ 테이블이 없습니다.")
    #     else:
    #         print("📋 데이터베이스 내 테이블 목록:")
    #         for t in tables:
    #             print(f" - {t['table_schema']}.{t['table_name']}")
    #     return tables
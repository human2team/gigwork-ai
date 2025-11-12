from app.db.database import PostgresDB

# 데이터베이스 연결 및 테스트용 테이블 목록 출력
db = PostgresDB()
db.test()
db.close()
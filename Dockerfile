# 베이스 이미지: Python 3.10
FROM python:3.10-slim

# 환경 변수 설정 (버퍼링 끄고, .pyc 안 만들고, UTF-8)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 작업 디렉토리
WORKDIR /app

# 필요한 시스템 패키지 (빌드/로케일 등 필요하면 여기 추가)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# 파이썬 패키지 설치
# requirements.txt는 프로젝트 루트에 있다고 가정
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사
COPY . .

# FastAPI + Uvicorn 기준
# main.py 안에 `app = FastAPI()` 라는 인스턴스가 있다고 가정
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

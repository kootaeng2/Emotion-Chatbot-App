# 1. 베이스 이미지 선택 (파이썬 3.10 버전)
FROM python:3.10-slim

# 2. 작업 폴더 설정
WORKDIR /app

# 3. 필요한 라이브러리 설치
COPY requirements.txt requirements.txt

# 👇👇👇 이 3줄을 추가해 주세요: 빌드 도구 및 시스템 라이브러리 설치 👇👇👇
RUN apt-get update && \
    apt-get install -y build-essential libblas-dev liblapack-dev && \
    rm -rf /var/lib/apt/lists/*
# 👆👆👆

RUN pip install --no-cache-dir -r requirements.txt

# 4. 캐시 및 데이터베이스 폴더를 미리 만들고 모든 사용자가 쓸 수 있도록 권한을 부여합니다.
RUN mkdir -p /app/.cache /app/src && chmod -R 777 /app/.cache /app/src

# 5. 프로젝트 전체 코드 복사
COPY . .
# 6. Hugging Face 관련 라이브러리들이 사용할 캐시 폴더를 지정합니다.
ENV HF_HOME=/app/.cache
ENV TRANSFORMERS_CACHE=/app/.cache

# 7. Hugging Face Spaces가 사용할 포트 열기
EXPOSE 7860

# 8. 최종 실행 명령어 (gunicorn으로 run.py 안의 app을 실행)
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "run:app"]
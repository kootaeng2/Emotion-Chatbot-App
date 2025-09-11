# 1. 베이스 이미지 선택 (파이썬 3.10 버전)
FROM python:3.10-slim

# 2. 작업 폴더 설정
WORKDIR /app

# 3. 필요한 라이브러리 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# --- 수정/추가 부분 시작 ---
# 4. 프로젝트 전체 코드 복사 (이것을 먼저 수행)
COPY . .

# 5. 데이터베이스가 위치할 src 폴더와 캐시 폴더에 쓰기 권한 부여
RUN chmod -R 777 /app/src
RUN mkdir -p /app/.cache && chmod -R 777 /app/.cache


# Hugging Face 관련 라이브러리들이 사용할 캐시 폴더를
# 권한이 있는 /app 폴더 내부로 지정합니다.
ENV HF_HOME=/app/.cache
ENV TRANSFORMERS_CACHE=/app/.cache

ENV OMP_NUM_THREADS=1

# 6. Hugging Face Spaces가 사용할 포트 열기
EXPOSE 10000

# 7. 최종 실행 명령어 최상위 폴더 run.py실행
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "run:app"]
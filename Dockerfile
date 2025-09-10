# 1. 베이스 이미지 선택 (파이썬 3.10 버전)
FROM python:3.10-slim

# 2. 작업 폴더 설정
WORKDIR /app

# 3. 필요한 라이브러리 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 캐시 폴더 생성 및 사용자에게 권한 제공 
RUN mkdir -p /app/.cache && chmod -R 777 /app/.cache

# 4. 프로젝트 전체 코드 복사
COPY . .

# Hugging Face 관련 라이브러리들이 사용할 캐시 폴더를
# 권한이 있는 /app 폴더 내부로 지정합니다.
ENV HF_HOME=/app/.cache
ENV TRANSFORMERS_CACHE=/app/.cache

# 5. Hugging Face Spaces가 사용할 포트(7860) 열기
EXPOSE 7860

# 6. 최종 실행 명령어 최상위 폴더 run.py실행
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "run:app"]
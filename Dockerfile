# 1. 베이스 이미지 선택 (파이썬 3.10 버전)
FROM python:3.10-slim

# 2. 작업 폴더 설정
WORKDIR /app

# 3. 필요한 빌드 도구 및 시스템 라이브러리 설치
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential libblas-dev liblapack-dev && \
    rm -rf /var/lib/apt/lists/*

# 4. 파이썬 라이브러리 설치 (분리하여 안정성 극대화)

# 4.1. 두 개의 종속성 파일 복사
COPY core_ml_deps.txt core_ml_deps.txt
COPY app_deps.txt app_deps.txt

# 4.2. 대용량 ML 종속성 먼저 설치 (실패 위험을 이 단계에 집중)
RUN pip install -r core_ml_deps.txt

# 4.3. 나머지 App 종속성 설치 (작은 모듈의 설치 성공 보장)
RUN pip install -r app_deps.txt

RUN pip install google-generativeai

# 5. 캐시 및 데이터베이스 폴더를 미리 만들고 권한을 부여합니다.
RUN mkdir -p /app/.cache /app/src && chmod -R 777 /app/.cache /app/src

# 6. 프로젝트 전체 코드 복사 (캐싱 효율을 위해 가장 늦게 배치)
COPY . .

# 7. 환경 변수 설정 (Hugging Face 라이브러리 캐시 경로 지정)
ENV HF_HOME=/app/.cache
ENV TRANSFORMERS_CACHE=/app/.cache

# 8. Hugging Face Spaces가 사용할 포트 열기
EXPOSE 7860

# 9. 최종 실행 명령어 (Gunicorn 워커 수를 2개로 제한)
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "-w", "2", "--preload", "run:app"]

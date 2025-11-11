# 1. 베이스 이미지 선택 (PyTorch와 같은 대용량 ML 앱을 위해 메모리/호환성이 검증된 파이썬 slim 버전을 유지합니다.)
FROM python:3.10-slim

# 2. 작업 폴더 설정
WORKDIR /app

# 3. 필요한 빌드 도구 및 시스템 라이브러리 설치 (가장 먼저 실행하여 컴파일 환경을 준비합니다.)
# DEBIAN_FRONTEND=noninteractive를 사용하여 빌드 중 대화형 프롬프트가 뜨는 것을 방지합니다.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential libblas-dev liblapack-dev && \
    rm -rf /var/lib/apt/lists/*

# 4. 파이썬 라이브러리 설치 (캐싱 효율을 위해 requirements.txt만 먼저 복사합니다.)
COPY requirements.txt requirements.txt

# --no-cache-dir 옵션을 제거하여 캐시를 활용하고 빌드 속도를 높입니다.
RUN pip install -r requirements.txt

# 5. 캐시 및 데이터베이스 폴더를 미리 만들고 권한을 부여합니다.
RUN mkdir -p /app/.cache /app/src && chmod -R 777 /app/.cache /app/src

# 6. 프로젝트 전체 코드 복사 (가장 늦게 배치하여 코드 변경 시에도 이전 단계 캐시를 유지합니다.)
COPY . .

# 7. 환경 변수 설정 (Hugging Face 라이브러리 캐시 경로 지정)
ENV HF_HOME=/app/.cache
ENV TRANSFORMERS_CACHE=/app/.cache

# 8. Hugging Face Spaces가 사용할 포트 열기
EXPOSE 7860

# 9. 최종 실행 명령어 (Gunicorn 워커 수를 2개로 제한하여 메모리 부족(OOM) 오류를 방지합니다.)
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "-w", "2", "run:app"]



# 1. 베이스 이미지 선택 (파이썬 3.10 버전)
FROM python:3.10-slim

# 2. 작업 폴더 설정
WORKDIR /app

# 3. 필요한 라이브러리 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 4. 프로젝트 전체 코드 복사
COPY . .

# 5. Hugging Face Spaces가 사용할 포트(7860) 열기
EXPOSE 7860

# 6. 최종 실행 명령어 최상위 폴더 run.py실행
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "run:app"]
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

MODEL_ID = "taehoon222/diary-emotion-model"
# README.md에 명시된 로컬 모델 저장 경로를 사용합니다.
SAVE_DIRECTORY = "korean-emotion-classifier-final"

if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)

print(f"Downloading model '{MODEL_ID}' to '{SAVE_DIRECTORY}'...")

# 모델과 토크나이저 다운로드
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)

# 로컬 폴더에 저장
tokenizer.save_pretrained(SAVE_DIRECTORY)
model.save_pretrained(SAVE_DIRECTORY)

print("✅ Model download complete.")
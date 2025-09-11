# emotion_engine.py 
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os

def load_emotion_classifier():
    # Hugging Face Hub ID 대신 로컬 폴더 경로를 사용합니다.
    MODEL_PATH = "korean-emotion-classifier-final" #

    print(f"Loading model from local path '{MODEL_PATH}'...")

    try:
        # 로컬 파일만 사용하도록 'local_files_only=True' 옵션 추가
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True)
        print("✅ Local model loading successful!")

    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None
    
    device = 0 if torch.cuda.is_available() else -1
    emotion_classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=device)
    
    return emotion_classifier

# predict_emotion 함수는 그대로 유지
# ...
def predict_emotion(classifier, text):
    if not text or not text.strip(): return "내용 없음"
    if classifier is None: return "오류: 감정 분석 엔진 준비 안됨."
    result = classifier(text)
    return result[0]['label']
# emotion_engine.py 
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os


def load_emotion_classifier():
    # 로컬 경로 대신, Hugging Face Hub의 모델 ID를 사용합니다.
    MODEL_PATH = "taehoon222/diary-emotion-model" # "사용자이름/모델이름" 형식

    print(f"Hugging Face Hub 모델 '{MODEL_PATH}'에서 모델을 불러옵니다...")

    try:
        # local_files_only 옵션을 제거하여 온라인에서 다운로드하도록 합니다.
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, force_download=True)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        print("✅ Hugging Face Hub 모델 로딩 성공!")

    except Exception as e:
        print(f"❌ 모델 로딩 중 오류: {e}")
        return None
    
    device = 0 if torch.cuda.is_available() else -1
    emotion_classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=device)
    
    return emotion_classifier

def predict_emotion(classifier, text):
    if not text or not text.strip(): return "내용 없음"
    if classifier is None: return "오류: 감정 분석 엔진 준비 안됨."
    result = classifier(text)
    return result[0]['label']
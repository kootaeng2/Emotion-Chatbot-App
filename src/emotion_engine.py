import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os

def load_emotion_classifier():
    MODEL_ID = "taehoon222/korean-emotion-classifier-final"

    print(f"Hugging Face Hub 모델 '{MODEL_ID}'에서 모델을 불러옵니다...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
        print("✅ Hugging Face Hub 모델 로딩 성공!")
    except Exception as e:
        print(f"❌ 모델 로딩 중 오류: {e}")
        return None
    
    device = 0 if torch.cuda.is_available() else -1
    if device == 0:
        print("Device set to use cuda (GPU)")
    else:
        print("Device set to use cpu")
    
    emotion_classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=device)
    return emotion_classifier

def predict_emotion(classifier, text):
    if not text or not text.strip(): return "내용 없음"
    if classifier is None: return "오류: 감정 분석 엔진 준비 안됨."
    result = classifier(text)
    return result[0]['label']
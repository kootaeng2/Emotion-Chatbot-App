import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os

def load_emotion_classifier():
    MODEL_PATH = "korean-emotion-classifier-final"
    print(f"Loading model from local path '{MODEL_PATH}'...")
    try:
        # 인터넷 연결을 시도하지 않도록 local_files_only=True 옵션을 추가합니다.
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True)
        print("✅ Local model loading successful!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
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
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os

# 모델을 저장할 전역 변수
_classifier = None

def load_emotion_classifier():
    global _classifier
    # 모델이 이미 로드되었다면, 즉시 반환
    if _classifier is not None:
        return _classifier

    # 모델이 로드되지 않았다면, 로드 시작
    MODEL_ID = "taehoon222/korean-emotion-classifier-final"

    print(f"Hugging Face Hub 모델 '{MODEL_ID}'에서 모델을 불러옵니다...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
        print("Hugging Face Hub 모델 로딩 성공!")
    except Exception as e:
        print(f"모델 로딩 중 오류: {e}")
        return None
    
    device = -1
    if device == 0:
        print("Device set to use cuda (GPU)")
    else:
        print("Device set to use cpu")
    
    # 로드된 모델을 전역 변수에 저장
    _classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=device)
    return _classifier

def predict_emotion(text):
    # 예측 시점에 모델을 로드하거나, 이미 로드된 모델을 가져옴
    classifier = load_emotion_classifier()
    if not text or not text.strip(): return "내용 없음"
    if classifier is None: return "오류: 감정 분석 엔진 준비 안됨."
    result = classifier(text)
    return result[0]['label']

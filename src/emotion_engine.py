# emotion_engine.py

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os

def load_emotion_classifier():
    # 현재 스크립트 파일의 디렉터리 경로를 가져옵니다.
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 모델 폴더의 절대 경로를 만듭니다.
    MODEL_PATH = os.path.join(base_path, "korean-emotion-classifier-final")
    
    # 경로가 로컬 디렉터리인지 확인
    if not os.path.isdir(MODEL_PATH):
        print(f"❌ 오류: 지정된 경로 '{MODEL_PATH}'에 모델 폴더가 존재하지 않습니다.")
        return None
        
    print(f"--- 최종 모델 경로 확인: [{MODEL_PATH}] ---")
    print(f"로컬 절대 경로 '{MODEL_PATH}'에서 모델을 직접 불러옵니다...")
    
    try:
        # 1. from_pretrained()에 절대 경로를 직접 전달합니다.
        # 2. `local_files_only=True`는 제거합니다. 라이브러리가 자동으로 인식합니다.
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        
        print("✅ 로컬 모델 파일 직접 로딩 성공!")

    except Exception as e:
        print(f"❌ 모델 로딩 중 오류: {e}")
        # 오류가 발생한 원인을 정확히 출력합니다.
        print(f"상세 오류 메시지: {e}")
        return None
    
    device = 0 if torch.cuda.is_available() else -1
    emotion_classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=device)
    
    return emotion_classifier

# predict_emotion 함수는 그대로 둡니다.
def predict_emotion(classifier, text):
    if not text or not text.strip(): return "내용 없음"
    if classifier is None: return "오류: 감정 분석 엔진 준비 안됨."
    result = classifier(text)
    return result[0]['label']
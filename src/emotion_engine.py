# emotion_engine.py (수정 후 최종 버전)

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os

def load_emotion_classifier():
    # --- 이 부분을 수정합니다 ---
    # 현재 스크립트 파일의 절대 경로를 찾습니다. (예: /app/src/emotion_engine.py)
    script_path = os.path.abspath(__file__)
    # 스크립트가 있는 디렉터리를 찾습니다. (예: /app/src)
    src_dir = os.path.dirname(script_path)
    # 그 상위 디렉터리, 즉 프로젝트 루트를 찾습니다. (예: /app)
    base_dir = os.path.dirname(src_dir)
    # 프로젝트 루트와 모델 폴더 이름을 합쳐 정확한 경로를 만듭니다.
    MODEL_PATH = os.path.join(base_dir, "korean-emotion-classifier-final")
    
    print(f"--- 배포 환경 모델 경로 확인: [{MODEL_PATH}] ---")
    
    try:
        # local_files_only 옵션은 로컬 경로를 명시할 때 안전을 위해 유지하는 것이 좋습니다.
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True)
        print("✅ 로컬 모델 파일 직접 로딩 성공!")

    except Exception as e:
        print(f"❌ 모델 로딩 중 오류: {e}")
        return None
    # --- 여기까지 수정 ---
    
    device = 0 if torch.cuda.is_available() else -1
    emotion_classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=device)
    
    return emotion_classifier

# predict_emotion 함수는 그대로 둡니다.
def predict_emotion(classifier, text):
    if not text or not text.strip(): return "내용 없음"
    if classifier is None: return "오류: 감정 분석 엔진 준비 안됨."
    result = classifier(text)
    return result[0]['label']
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os
import logging

# 모델을 저장할 전역 변수
_classifier = None

def load_emotion_classifier():
    global _classifier
    # 모델이 이미 로드되었다면, 즉시 반환
    if _classifier is not None:
        return _classifier

    # 모델이 로드되지 않았다면, 로드 시작
    MODEL_ID = "taehoon222/korean-emotion-classifier-final"

    logging.info(f"Hugging Face Hub 모델 '{MODEL_ID}'에서 모델을 불러옵니다...")
    try:
        logging.info("토크나이저 로딩 중...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        logging.info("모델 로딩 중...")
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
        logging.info("Hugging Face Hub 모델 로딩 성공!")
    except Exception as e:
        logging.error(f"모델 로딩 중 오류: {e}")
        return None
    
    device = 0 if torch.cuda.is_available() else -1
    if device == 0:
        logging.info("Device set to use cuda (GPU)")
    else:
        logging.info("Device set to use cpu")
    
    # 로드된 모델을 전역 변수에 저장
    _classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=device)
    return _classifier

def predict_emotion(text):
    logging.info(f"predict_emotion 함수 호출됨. 텍스트 길이: {len(text) if text else 0}")
    classifier = load_emotion_classifier()
    if not text or not text.strip():
        logging.warning("분석할 텍스트가 비어있거나 공백입니다.")
        return "내용 없음"
    if classifier is None:
        logging.error("감정 분석 엔진이 준비되지 않았습니다.")
        return "오류: 감정 분석 엔진 준비 안됨."
    
    try:
        logging.info(f"분류기 실행 중... 텍스트: {text[:50]}...") 
        result = classifier(text)
        logging.info(f"분류 결과: {result[0]['label']}")
        return result[0]['label']
    except Exception as e:
        logging.error(f"감정 분류 중 오류 발생: {e}")
        return "오류: 감정 분류 실패"

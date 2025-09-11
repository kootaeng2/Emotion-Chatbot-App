from transformers import AutoConfig

# 훈련된 모델 파일이 저장된 로컬 폴더 경로를 정확하게 입력하세요.
# 예: "korean-emotion-classifier-final" 또는 "results/checkpoint-500" 등
LOCAL_MODEL_PATH = "korean-emotion-classifier-final" 

try:
    config = AutoConfig.from_pretrained(LOCAL_MODEL_PATH)
    
    # 로컬 모델의 레이블 개수와 목록을 직접 출력해봅니다.
    num_labels = len(config.id2label)
    labels = list(config.id2label.values())
    
    print(f"✅ 로컬 모델 확인 성공!")
    print(f"   - 레이블 개수: {num_labels}개")
    print(f"   - 레이블 목록: {labels}")

except Exception as e:
    print(f"❌ 로컬 모델 확인 중 오류 발생: {e}")
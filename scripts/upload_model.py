# upload_model.py
# 배포용 모델을 Hugging Face Hub에 업로드

from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ---!!! 1. 이 부분을 최종적으로 결정한 정보로 수정해주세요 !!!---
YOUR_HF_ID = "taehoon222"  # 사용자님의 Hugging Face ID
YOUR_MODEL_NAME = "korean-emotion-classifier" # 추천 모델 이름 (원하는 이름으로 변경 가능)
# ----------------------------------------------------

# 2. 내 컴퓨터에 저장된, 훈련이 완료된 모델의 경로
LOCAL_MODEL_PATH = 'E:/sentiment_analysis_project/results/checkpoint-9681'

print(f"'{LOCAL_MODEL_PATH}'에서 모델을 불러옵니다...")
try:
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(LOCAL_MODEL_PATH)
    print("✅ 로컬 모델 로딩 성공!")
except Exception as e:
    print(f"❌ 로컬 모델을 불러오는 데 실패했습니다: {e}")
    exit()

# 3. Hugging Face Hub에 업로드합니다.
NEW_REPO_ID = f"{YOUR_HF_ID}/{YOUR_MODEL_NAME}"
print(f"'{NEW_REPO_ID}' 이름으로 Hub에 업로드를 시작합니다...")
try:
    tokenizer.push_to_hub(NEW_REPO_ID)
    model.push_to_hub(NEW_REPO_ID)
    print("\n🎉🎉🎉 모델 업로드에 성공했습니다! 🎉🎉🎉")
except Exception as e:
    print(f"\n❌ 업로드 중 오류가 발생했습니다: {e}")
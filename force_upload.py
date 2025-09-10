# force_upload.py
from huggingface_hub import HfApi
import os

# --- 설정 ---
# PC에 있는, 올바르게 수정된 모델 폴더 경로
LOCAL_MODEL_DIR = "./korean-emotion-classifier-final" 
# 덮어쓰기 할 Hub의 모델 ID
REPO_ID = "koons/korean-emotion-classifier-final" 
# --- --- ---

# Hugging Face API 클라이언트 생성
api = HfApi()

# 폴더 업로드
print(f"'{LOCAL_MODEL_DIR}' 폴더의 내용을 '{REPO_ID}'에 업로드합니다...")
try:
    # folder_path에 있는 모든 파일을 repo_id에 올립니다. (기존 파일은 덮어씀)
    api.upload_folder(
        folder_path=LOCAL_MODEL_DIR,
        repo_id=REPO_ID,
        repo_type="model"
    )
    print("✅ 업로드 완료!")
except Exception as e:
    print(f"\n❌ 업로드 중 오류가 발생했습니다: {e}")
    print("huggingface-cli login이 정상적으로 되었는지, REPO_ID가 정확한지 확인해주세요.")
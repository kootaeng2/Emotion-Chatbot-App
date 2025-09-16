import os
from huggingface_hub import HfApi, create_repo, HfFolder

def upload_with_huggingface_hub():
    """
    huggingface_hub 라이브러리를 사용해 로컬 폴더를 직접 Hub에 업로드합니다.
    이 방법은 파일을 메모리에 미리 로드하지 않아 윈도우 파일 잠금 오류를 피할 수 있습니다.
    """
    # --- 설정 부분 (사용자 정보에 맞게 수정해주세요) ---
    HF_USERNAME = "taehoon222" # 본인의 Hugging Face 사용자 이름
    MODEL_NAME = "korean-emotion-classifier-final" # Hub에 올릴 모델 이름
    LOCAL_MODEL_PATH = "./korean-emotion-classifier-final" # 로컬 모델 폴더 경로
    # ----------------------------------------------------

    HF_REPO_ID = f"{HF_USERNAME}/{MODEL_NAME}"

    print("="*50)
    print(f"로컬 폴더 경로: {os.path.abspath(LOCAL_MODEL_PATH)}")
    print(f"Hugging Face Hub 저장소: {HF_REPO_ID}")
    print("="*50)

    # 로컬 경로에 모델 폴더가 있는지 확인
    if not os.path.isdir(LOCAL_MODEL_PATH):
        print(f"오류: '{LOCAL_MODEL_PATH}' 폴더를 찾을 수 없습니다.")
        return

    try:
        # 1. Hugging Face Hub에 저장소(repository) 생성
        # exist_ok=True: 이미 저장소가 있다면 생성하지 않고 넘어감
        print(f"\n[1/2] '{HF_REPO_ID}' 저장소를 생성하거나 확인합니다...")
        create_repo(
            repo_id=HF_REPO_ID,
            exist_ok=True,
            token=HfFolder.get_token() # 로컬에 저장된 로그인 토큰 사용
        )
        print("✅ 저장소 준비 완료")

        # 2. 지정된 로컬 폴더의 모든 내용을 Hub 저장소에 업로드
        api = HfApi()
        print(f"\n[2/2] '{LOCAL_MODEL_PATH}' 폴더의 내용을 업로드합니다...")
        print("이 작업은 모델 크기와 인터넷 속도에 따라 몇 분 정도 소요될 수 있습니다.")
        api.upload_folder(
            folder_path=LOCAL_MODEL_PATH,
            repo_id=HF_REPO_ID,
            repo_type="model",
            commit_message="Upload trained Korean emotion classification model"
        )
        print("✅ 업로드 완료!")
        print(f"\n다음 주소에서 모델을 확인할 수 있습니다: https://huggingface.co/{HF_REPO_ID}")

    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")
        print("Hugging Face 로그인 상태와 파일 경로, 네트워크 연결을 다시 한번 확인해주세요.")

if __name__ == "__main__":
    upload_with_huggingface_hub()
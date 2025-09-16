from huggingface_hub import login
import os

# --- 중요 ---
# 아래 따옴표 안에 Hugging Face 웹사이트에서 복사한 토큰을 붙여넣어 주세요.
# 토큰은 'hf_' 로 시작하는 긴 문자열입니다.
# 예시: hf_token = "hf_abcdefg123456"
hf_token = "YOUR_TOKEN_HERE"
# ------------

# 혹시 모르니 다시 한번 확인: 토큰에 'write' 권한이 있는지 확인해주세요.

# 환경 변수 설정
os.environ["HF_TOKEN"] = hf_token

print("Python 스크립트를 통해 Hugging Face 로그인을 시도합니다...")
try:
    # git credential(자격 증명)에도 토큰을 추가합니다.
    login(token=hf_token, add_to_git_credential=True)
    print("\n✅ 성공적으로 로그인되었습니다!")
    print("이제 터미널에서 'python upload_model.py'를 실행하여 모델을 업로드하세요.")
except Exception as e:
    print(f"\n❌ 로그인 실패: {e}")
    print("\n토큰이 올바른지 다시 한번 확인해주세요.")
    print("만약 계속 실패한다면, 네트워크 방화벽 문제일 수 있습니다.")
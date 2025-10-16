# check_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env 파일에서 API 키를 불러옵니다
load_dotenv()

try:
    # API 키 설정
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("🔥🔥🔥 GEMINI_API_KEY 환경 변수를 찾을 수 없습니다. .env 파일을 확인해주세요. 🔥🔥🔥")
    else:
        genai.configure(api_key=api_key)

        print("✅ API 키가 설정되었습니다. 사용 가능한 모델 목록을 조회합니다...")
        print("---------------------------------------------------------")

        # 'generateContent'를 지원하는 모델만 필터링하여 출력
        for m in genai.list_models():
          if 'generateContent' in m.supported_generation_methods:
            print(m.name)

        print("---------------------------------------------------------")
        print("✅ 위에 나열된 모델 중 하나를 'src/main.py' 파일에 사용하세요.")

except Exception as e:
    print(f"🔥🔥🔥 모델 목록을 가져오는 중 오류 발생: {e} 🔥🔥🔥")
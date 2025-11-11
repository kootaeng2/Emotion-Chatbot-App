import json
import re
import os

# 1. 텍스트 정제 함수 정의 (train_final.py의 로직)
def clean_text(text: str) -> str:
    """한글, 영어, 숫자, 공백을 제외한 모든 특수문자를 제거합니다."""
    return re.sub(r'[^가-힣a-zA-Z0-9 ]', '', str(text))

# 2. 파일 경로 설정 및 데이터 로드 (파일 경로가 data/에 있다고 가정)
file_path = './data/training-label.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        training_data_raw = json.load(f)

    print(f"✅ '{file_path}' 파일 로딩 성공. 총 {len(training_data_raw)}개 데이터 중 10개만 추출합니다.")
    print("---------------------------------------------------\n")

    # 3. 첫 10개 데이터에 대해 처리 및 비교
    comparison_data = []
    
    # training_data_raw는 대화 단위의 리스트입니다.
    for i, data in enumerate(training_data_raw[:5]):
        # 대화의 모든 문장을 공백으로 연결하여 원본 텍스트를 만듭니다. (explore_data.py 로직)
        raw_text = " ".join(data['talk']['content'].values())
        
        cleaned_text = clean_text(raw_text)
        
        # 원본 데이터의 E코드 감정 추출 (참고용)
        emotion_type = data['profile']['emotion']['type']
        
        comparison_data.append({
            'ID': i + 1,
            'Emotion': emotion_type,
            'Raw Text': raw_text,
            'Cleaned Text': cleaned_text
        })
    
    # 4. 결과 출력
    for item in comparison_data:
        print(f"--- ID: {item['ID']} (감정 코드: {item['Emotion']}) ---")
        print(f"  원본 (Raw) : {item['Raw Text']}")
        print(f"  정제 (Clean): {item['Cleaned Text']}")
        print("-" * 30)

except FileNotFoundError:
    print(f"❌ 오류: 데이터 파일을 찾을 수 없습니다. 경로를 확인하세요: {os.path.abspath(file_path)}")
except Exception as e:
    print(f"❌ 데이터 처리 중 오류 발생: {e}")
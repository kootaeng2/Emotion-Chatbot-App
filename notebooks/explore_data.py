# 데이터셋의 사용 조사 보고 그래프

import pandas as pd
import json
import re

# 파일 경로 설정
file_path = './data/'

# 훈련 라벨 JSON 파일 불러오기
with open(training_data_path, 'r', encoding='cp949') as file:
    training_data_raw = json.load(file)

# 필요한 데이터만 추출하여 리스트에 저장
extracted_data = []

# 데이터는 리스트이므로 바로 순회합니다.
for dialogue in training_data_raw:
    try:
        # 1. 감정 라벨 추출 (emotion 키는 profile 안에 있습니다)
        emotion_type = dialogue['profile']['emotion']['type']
        
        # 2. 대화 텍스트 추출 (talk 키 안에 content가 있습니다)
        dialogue_content = dialogue['talk']['content']
        
        # 3. 딕셔너리의 value들(텍스트)만 추출합니다.
        texts = list(dialogue_content.values())
        
        # 4. 모든 텍스트를 하나의 문자열로 합칩니다.
        # 빈 문자열을 제거하고 합치는 것이 좋습니다.
        full_text = " ".join([text for text in texts if text.strip()])
        
        # 5. 합쳐진 텍스트와 감정 라벨이 모두 유효할 경우에만 추가합니다.
        if full_text and emotion_type:
            extracted_data.append({'text': full_text, 'emotion': emotion_type})
            
    except KeyError:
        # 'profile', 'emotion', 'talk', 'content' 등의 키가 없는 항목은 건너뜁니다.
        continue

# 새로운 데이터프레임 생성
df_train = pd.DataFrame(extracted_data)

# 6. 합쳐진 데이터 확인
print("--- 추출된 훈련 데이터프레임의 첫 5줄 ---")
print(df_train.head())

print("\n--- 데이터프레임 크기 ---")
print(f"훈련 데이터: {df_train.shape}")

# 기존 훈련 데이터 로드 코드 아래에 이어서 작성해 주세요.
# ------------------------------------------------------------------

# 1. 검증 라벨 JSON 파일 불러오기
with open(file_path + 'validation-label.json', 'r', encoding='utf-8') as file:
    validation_data_raw = json.load(file)

# 2. 검증 데이터 추출
extracted_val_data = []

for dialogue in validation_data_raw:
    try:
        emotion_type = dialogue['profile']['emotion']['type']
        dialogue_content = dialogue['talk']['content']
        texts = list(dialogue_content.values())
        full_text = " ".join([text for text in texts if text.strip()])

        if full_text and emotion_type:
            extracted_val_data.append({'text': full_text, 'emotion': emotion_type})
            
    except KeyError:
        continue

# 3. 새로운 데이터프레임 생성
df_val = pd.DataFrame(extracted_val_data)

# 4. 검증 데이터 확인
print("\n--- 추출된 검증 데이터프레임의 첫 5줄 ---")
print(df_val.head())

print("\n--- 검증 데이터프레임 크기 ---")
print(f"검증 데이터: {df_val.shape}")

# main.py의 기존 코드 맨 아래에 이어서 작성합니다.
# -----------------------------------------------------------
# --- [Phase 1] 데이터 탐색 및 전처리 ---
# -----------------------------------------------------------
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 데이터 탐색 및 시각화
print("\n--- [Phase 1-1] 데이터 탐색 및 시각화 시작 ---")

# 한글 폰트 설정 (Windows: Malgun Gothic, Mac: AppleGothic)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

# 훈련 데이터의 감정 분포 확인
print("\n--- 훈련 데이터 감정 분포 ---")
print(df_train['emotion'].value_counts())

# 감정 분포 시각화
plt.figure(figsize=(10, 6))
sns.countplot(data=df_train, y='emotion', order=df_train['emotion'].value_counts().index)
plt.title('훈련 데이터 감정 분포 시각화', fontsize=15)
plt.xlabel('개수', fontsize=12)
plt.ylabel('감정', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.show() # 그래프 창 보여주기

print("\n시각화 완료. 그래프 창을 닫으면 다음 단계가 진행됩니다.")

# 2. 텍스트 정제
print("\n--- [Phase 1-2] 텍스트 정제 시작 ---")
# 이미 re 모듈은 위에서 import 했습니다.

def clean_text(text):
    # 정규표현식을 사용하여 한글, 영어, 숫자, 공백을 제외한 모든 문자 제거
    return re.sub(r'[^가-힣a-zA-Z0-9 ]', '', text)

# 훈련/검증 데이터에 정제 함수 적용
df_train['cleaned_text'] = df_train['text'].apply(clean_text)
df_val['cleaned_text'] = df_val['text'].apply(clean_text)

print("텍스트 정제 완료.")
print(df_train[['text', 'cleaned_text']].head())
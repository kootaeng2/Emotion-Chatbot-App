import pandas as pd
import json
import re
import matplotlib.pyplot as plt
import seaborn as sns

# --- [Phase 1] 데이터 로딩 및 병합 ---
print("---" + "[Phase 1] 데이터 로딩 및 병합 시작" + "---")

# 파일 경로 설정
data_path = 'data/' # 현재 위치(notebooks)에서 상위 폴더(root)의 data 폴더로 이동
train_text_path = data_path + 'training-origin.xlsx'
train_label_path = data_path + 'training-label.json'
val_text_path = data_path + 'validation-origin.xlsx' # 파일 이름 오타 'vaklidation' 주의
val_label_path = data_path + 'validation-label.json'

# 1. 데이터 불러오기
try:
    # 텍스트 데이터(xlsx)와 라벨 데이터(json)를 각각 불러옵니다.
    df_train_text = pd.read_excel(train_text_path, header=0)
    df_val_text = pd.read_excel(val_text_path, header=0)

    # JSON 파일은 감정 라벨만 추출하기 위해 json.load()를 사용합니다.
    with open(train_label_path, 'r', encoding='utf-8') as f:
        train_labels_raw = json.load(f)
    with open(val_label_path, 'r', encoding='utf-8') as f:
        val_labels_raw = json.load(f)

    print("파일 로딩 성공!")

except FileNotFoundError as e:
    print(f"파일을 찾을 수 없습니다: {e}")
    print("파일 경로와 파일 이름을 다시 확인해주세요. 특히 'validation-origin.xlsx'의 오타를 확인하세요.")
    # 파일이 없으면 더 이상 진행할 수 없으므로 여기서 중단합니다.
    exit()


# 2. 라벨 데이터 정제 및 추출
# 기존 코드의 로직을 활용하여 감정 라벨만 추출합니다.
def extract_emotions(raw_labels):
    emotions = []
    for dialogue in raw_labels:
        try:
            emotions.append(dialogue['profile']['emotion']['type'])
        except KeyError:
            emotions.append(None) # 해당 구조가 없는 경우 None으로 추가
    return emotions

df_train_labels = pd.DataFrame({'emotion': extract_emotions(train_labels_raw)})
df_val_labels = pd.DataFrame({'emotion': extract_emotions(val_labels_raw)})

# 3. 텍스트 데이터와 라벨 데이터 병합
# 두 데이터프레임의 순서가 동일하다고 가정하고 옆으로 합칩니다.
df_train = pd.concat([df_train_text, df_train_labels], axis=1)
df_val = pd.concat([df_val_text, df_val_labels], axis=1)

def combine_dialogues(df):
    dialogue_cols = [col for col in df.columns if '문장' in str(col)]
    for col in dialogue_cols:
        df[col] = df[col].astype(str).fillna('')
    df['text'] = df[dialogue_cols].apply(lambda row: ' '.join(row), axis=1)
    return df

df_train = combine_dialogues(df_train)
df_val = combine_dialogues(df_val)

print("\n--- 통합된 훈련 데이터프레임의 첫 5줄 ---")
print(df_train[['text', 'emotion']].head())
print("\n--- 통합된 검증 데이터프레임의 첫 5줄 ---")
print(df_val[['text', 'emotion']].head())

print("\n---" + "데이터프레임 크기" + "---")
print(f"훈련 데이터: {df_train.shape}")
print(f"검증 데이터: {df_val.shape}")
print("--- [Phase 1] 완료 ---")


# --- [Phase 2] 데이터 탐색 및 전처리 ---
print("\n---" + "[Phase 2] 데이터 탐색 및 전처리 시작" + "---")

# 1. 데이터 탐색 및 시각화
# 한글 폰트 설정 (Windows: Malgun Gothic)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

# 훈련 데이터의 감정 분포 확인
print("\n---" + "훈련 데이터 감정 분포" + "---")
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
print("\n---" + "텍스트 정제 시작" + "---")

def clean_text(text):
    # 텍스트가 문자열이 아닌 경우(결측치 등) 빈 문자열로 변환
    if not isinstance(text, str):
        return ""
    # 정규표현식을 사용하여 한글, 영어, 숫자, 공백을 제외한 모든 문자 제거
    return re.sub(r'[^가-힣a-zA-Z0-9 ]', '', text)

# 훈련/검증 데이터에 정제 함수 적용
df_train['cleaned_text'] = df_train['text'].apply(clean_text)
df_val['cleaned_text'] = df_val['text'].apply(clean_text)

print("텍스트 정제 완료.")
print(df_train[['text', 'cleaned_text']].head())
print("--- [Phase 2] 완료 ---")

print("\n모든 과정이 완료되었습니다. 이제 이 데이터프레임(df_train, df_val)으로 분석을 계속 진행할 수 있습니다.")

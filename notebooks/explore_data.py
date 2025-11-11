import pandas as pd
import json
import re
import matplotlib.pyplot as plt
import seaborn as sns

# --- Matplotlib 한글 폰트 설정 (Windows: Malgun Gothic) ---
try:
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False 
except:
    print("한글 폰트 설정에 실패했습니다. 그래프의 라벨이 깨질 수 있습니다.")

# 👇👇👇 사용자 요청에 따라 E코드를 대분류 감정으로 매핑하는 함수 추가 👇👇👇
def map_emotion_code(ecode):
    """
    E코드 문자열을 대분류 감정 문자열로 매핑합니다. (예: 'E11' -> '분노')
    """
    # E코드 문자열이 아니거나 형식이 맞지 않으면 None 반환
    if not isinstance(ecode, str) or len(ecode) < 2 or ecode[0] != 'E':
        return None

    try:
        # 'E'를 제거하고 숫자 부분만 추출
        code_num = int(ecode[1:])
    except ValueError:
        return None 

    if 10 <= code_num <= 19:
        return '분노'
    elif 20 <= code_num <= 29:
        return '슬픔'
    elif 30 <= code_num <= 39:
        return '불안'
    elif 40 <= code_num <= 49:
        return '상처'
    elif 50 <= code_num <= 59:
        return '당황'
    elif 60 <= code_num <= 69:
        return '기쁨'
    else:
        return None
# 👆👆👆 함수 추가 완료 👆👆👆


# --- [Phase 1] 데이터 로딩 및 병합 ---
print("---" + "[Phase 1] 데이터 로딩 및 병합 시작" + "---")

# 파일 경로 설정
data_path = 'data/'
train_text_path = data_path + 'training-origin.xlsx'
train_label_path = data_path + 'training-label.json'
val_text_path = data_path + 'validation-origin.xlsx' 
val_label_path = data_path + 'test.json'

# 1. 데이터 불러오기
try:
    df_train_text = pd.read_excel(train_text_path, header=0)
    df_val_text = pd.read_excel(val_text_path, header=0)

    with open(train_label_path, 'r', encoding='utf-8') as f:
        train_labels_raw = json.load(f)
    with open(val_label_path, 'r', encoding='utf-8') as f:
        val_labels_raw = json.load(f)

    print("파일 로딩 성공!")

except FileNotFoundError as e:
    print(f"파일을 찾을 수 없습니다: {e}")
    print("파일 경로와 파일 이름을 다시 확인해주세요.")
    exit()


# 2. 라벨 데이터 정제 및 추출
def extract_emotions(raw_labels):
    # 'emotion' 컬럼에 원본 E코드를 저장합니다.
    emotions = []
    for dialogue in raw_labels:
        try:
            emotions.append(dialogue['profile']['emotion']['type'])
        except KeyError:
            emotions.append(None)
    return emotions

df_train_labels = pd.DataFrame({'emotion': extract_emotions(train_labels_raw)})
df_val_labels = pd.DataFrame({'emotion': extract_emotions(val_labels_raw)})

# 3. 텍스트 데이터와 라벨 데이터 병합
def combine_dialogues(df):
    dialogue_cols = [col for col in df.columns if '문장' in str(col)]
    for col in dialogue_cols:
        df[col] = df[col].astype(str).fillna('')
    df['text'] = df[dialogue_cols].apply(lambda row: ' '.join(row), axis=1)
    return df

df_train = pd.concat([df_train_text, df_train_labels], axis=1)
df_val = pd.concat([df_val_text, df_val_labels], axis=1)
df_train = combine_dialogues(df_train)
df_val = combine_dialogues(df_val)


# 👇👇👇 매핑 함수 적용 👇👇👇
# 원본 E코드(emotion)를 대분류 감정(major_emotion)으로 매핑하고, 매핑되지 않은 데이터는 제거합니다.
df_train['major_emotion'] = df_train['emotion'].apply(map_emotion_code)
df_val['major_emotion'] = df_val['emotion'].apply(map_emotion_code)

df_train.dropna(subset=['major_emotion'], inplace=True)
df_val.dropna(subset=['major_emotion'], inplace=True)
# 👆👆👆 매핑 함수 적용 완료 👆👆👆


# ⭐️ 훈련 데이터와 검증 데이터를 하나로 합칩니다.
# 이제 합칠 때 'major_emotion' 컬럼이 포함됩니다.
df_combined = pd.concat([df_train, df_val], ignore_index=True)


print("\n--- 통합 데이터프레임의 첫 5줄 (매핑 후) ---")
# 'emotion' (E코드)와 'major_emotion' (대분류 감정) 모두 출력하여 확인
print(df_combined[['text', 'emotion', 'major_emotion']].head())
print("\n--- 통합 데이터프레임 크기 ---")
print(f"통합 데이터: {df_combined.shape}")
print("--- [Phase 1] 완료 ---")


# --- [Phase 2] 데이터 탐색 및 전처리 ---
print("\n---" + "[Phase 2] 데이터 탐색 및 전처리 시작" + "---")

# 1. 데이터 탐색 및 시각화
# ⭐️ 통합 데이터의 대분류 감정 분포 확인
print("\n---" + "통합 데이터 (훈련 + 검증) 감정 분포" + "---")
# ⭐️ 'major_emotion' 컬럼을 사용합니다.
emotion_counts = df_combined['major_emotion'].value_counts() 
print(emotion_counts)
print("-------------------------------------------\n")


# 감정 분포 시각화
plt.figure(figsize=(10, 6))

# value_counts() 결과를 직접 Bar Plot으로 그립니다.
sns.barplot(x=emotion_counts.values, y=emotion_counts.index, color='#2c7bb6') 

# 수량 (개수)을 막대 끝에 추가
for index, value in enumerate(emotion_counts.values):
    # 막대 끝에 텍스트 추가 (쉼표 포함)
    plt.text(x=value + 100, y=index, s=f'{value:,}', va='center', ha='left', fontsize=12, color='black')

plt.title('훈련 + 검증 데이터 통합 감정 분포 시각화', fontsize=15)
plt.xlabel('개수', fontsize=12)
plt.ylabel('감정', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.7)

# X축 범위를 수량 텍스트가 잘리지 않도록 확장 (약 15000개로 설정)
plt.xlim(0, 15000)
# 과학적 표기법 해제
plt.ticklabel_format(style='plain', axis='x')

plt.show() 

print("\n시각화 완료. 그래프 창을 닫으면 다음 단계가 진행됩니다.")

# 2. 텍스트 정제
print("\n---" + "텍스트 정제 시작" + "---")

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # 정규표현식을 사용하여 한글, 영어, 숫자, 공백을 제외한 모든 문자 제거
    return re.sub(r'[^가-힣a-zA-Z0-9 ]', '', text)

# ⭐️ 통합 데이터에 정제 함수 적용
df_combined['cleaned_text'] = df_combined['text'].apply(clean_text)

print("텍스트 정제 완료.")
print(df_combined[['text', 'cleaned_text', 'major_emotion']].head())
print("--- [Phase 2] 완료 ---")

print("\n모든 과정이 완료되었습니다. 이제 이 데이터프레임(df_combined)으로 분석을 계속 진행할 수 있습니다.")
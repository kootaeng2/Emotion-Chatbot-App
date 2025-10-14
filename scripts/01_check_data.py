import pandas as pd
import json
import os

def load_and_process_data(base_path="."):
    """
    데이터를 로드하고 전처리하여 통합 데이터프레임을 반환합니다.
    """
    data_path = os.path.join(base_path, 'data')
    
    # 파일 경로 설정
    train_text_path = os.path.join(data_path, 'training-origin.xlsx')
    train_label_path = os.path.join(data_path, 'training-label.json')
    val_text_path = os.path.join(data_path, 'validation-origin.xlsx')
    val_label_path = os.path.join(data_path, 'validation-label.json')

    # 1. 데이터 불러오기
    try:
        df_train_text = pd.read_excel(train_text_path, header=0)
        df_val_text = pd.read_excel(val_text_path, header=0)
        with open(train_label_path, 'r', encoding='utf-8') as f:
            train_labels_raw = json.load(f)
        with open(val_label_path, 'r', encoding='utf-8') as f:
            val_labels_raw = json.load(f)
        print("✅ 파일 로딩 성공")
    except FileNotFoundError as e:
        print(f"❌ 파일을 찾을 수 없습니다: {e}")
        return None, None

    # 2. 라벨 데이터 정제
    def extract_emotions(raw_labels):
        emotions = [dialogue['profile']['emotion']['type'] for dialogue in raw_labels]
        return emotions

    df_train_labels = pd.DataFrame({'emotion': extract_emotions(train_labels_raw)})
    df_val_labels = pd.DataFrame({'emotion': extract_emotions(val_labels_raw)})

    # 3. 텍스트와 라벨 데이터 병합
    df_train = pd.concat([df_train_text, df_train_labels], axis=1)
    df_val = pd.concat([df_val_text, df_val_labels], axis=1)

    # 4. 대화 문장 병합
    def combine_dialogues(df):
        dialogue_cols = [col for col in df.columns if '문장' in str(col)]
        for col in dialogue_cols:
            df[col] = df[col].astype(str).fillna('')
        df['text'] = df[dialogue_cols].apply(lambda row: ' '.join(row), axis=1)
        # 원본 문장 컬럼과 text, emotion만 남김
        keep_cols = dialogue_cols + ['text', 'emotion']
        return df[keep_cols]

    df_train = combine_dialogues(df_train)
    df_val = combine_dialogues(df_val)
    
    print("✅ 데이터 병합 및 전처리 완료")
    return df_train, df_val

if __name__ == "__main__":
    df_train, df_val = load_and_process_data()

    if df_train is not None:
        print("\n--- [데이터 구성 확인] ---")
        
        # 데이터셋 크기 확인
        print("\n1. 데이터셋 크기:")
        print(f"  - 훈련 데이터: {df_train.shape[0]}개")
        print(f"  - 검증 데이터: {df_val.shape[0]}개")

        # 결측치 확인
        print("\n2. 주요 컬럼 결측치 확인 (훈련 데이터):")
        print(df_train[['text', 'emotion']].isnull().sum())

        # 감정 클래스 분포 확인
        print("\n3. 훈련 데이터의 감정 분포:")
        print(df_train['emotion'].value_counts())
